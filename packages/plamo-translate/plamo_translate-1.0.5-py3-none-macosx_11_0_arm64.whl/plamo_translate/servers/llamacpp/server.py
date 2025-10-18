import asyncio
import contextlib
import importlib.resources
import json
import logging
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import socket
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from mcp.server.fastmcp import Context, FastMCP

from plamo_translate.servers.utils import (
    INSTRUCTION,
    PLAMO_MAX_TOKENS,
    PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE,
    PLAMO_TRANSLATE_CLI_REPETITION_PENALTY,
    PLAMO_TRANSLATE_CLI_TEMP,
    PLAMO_TRANSLATE_CLI_TOP_K,
    PLAMO_TRANSLATE_CLI_TOP_P,
    TranslateRequest,
    construct_llm_input,
    find_free_port,
    update_config,
)

logger = logging.getLogger(__name__)


def _http_get(url: str) -> bytes:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "plamo-translate-cli"})
    with urllib.request.urlopen(req) as r:  # nosec - controlled URL
        return r.read()


def _download_to(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = _http_get(url)
    with dest.open("wb") as f:
        f.write(data)


def _extract_zip(zip_path: Path, out_dir: Path) -> None:
    import zipfile

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)


def _make_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _find_llama_binary(search_dir: Path) -> Optional[Path]:
    candidates = []
    exe_names = ["llama-server", "llama-server.exe"]
    for root, _dirs, files in os.walk(search_dir):
        for name in files:
            if name in exe_names:
                p = Path(root) / name
                candidates.append(p)
    # Prefer entries under 'bin/' if present
    for c in candidates:
        if "/bin/" in str(c).replace("\\", "/"):
            return c
    return candidates[0] if candidates else None


def _find_free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _detect_asset_name(tag: str) -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Accelerator preferences (windows/linux)
    accel = os.environ.get("PLAMO_TRANSLATE_CLI_LLAMA_CPP_ACCELERATOR", "").lower()
    prefer_vulkan = os.environ.get("PLAMO_TRANSLATE_CLI_LLAMA_CPP_PREFER_VULKAN", "0") in {"1", "true", "yes"}

    # Examples from latest release as of implementation:
    # - llama-b{tag}-bin-macos-arm64.zip
    # - llama-b{tag}-bin-macos-x64.zip
    # - llama-b{tag}-bin-ubuntu-x64.zip
    # - llama-b{tag}-bin-ubuntu-vulkan-x64.zip
    # - llama-b{tag}-bin-win-cpu-x64.zip
    # - llama-b{tag}-bin-win-cpu-arm64.zip
    # - llama-b{tag}-bin-win-cuda-12.4-x64.zip
    # - llama-b{tag}-bin-win-vulkan-x64.zip
    # - llama-b{tag}-bin-win-opencl-adreno-arm64.zip
    # - llama-b{tag}-bin-win-hip-radeon-x64.zip
    # - llama-b{tag}-bin-win-sycl-x64.zip

    # Normalize CPU arches
    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = machine

    if system == "darwin":
        if arch == "arm64":
            return f"llama-{tag}-bin-macos-arm64.zip"
        else:
            return f"llama-{tag}-bin-macos-x64.zip"

    if system == "linux":
        # Use ubuntu-x64 prebuilt; optionally select vulkan
        if prefer_vulkan:
            return f"llama-{tag}-bin-ubuntu-vulkan-x64.zip"
        return f"llama-{tag}-bin-ubuntu-x64.zip"

    if system == "windows":
        # Default to CPU runtime; allow override
        if accel in {"cuda", "hip", "vulkan", "opencl", "sycl"}:
            if accel == "cuda":
                # Freeze to CUDA 12.4 artifact family as of latest release
                return f"llama-{tag}-bin-win-cuda-12.4-{arch}.zip"
            if accel == "hip":
                return f"llama-{tag}-bin-win-hip-radeon-{arch}.zip"
            if accel == "opencl":
                # arm64 Adreno variant exists; try best-matching naming
                suffix = "adreno-arm64" if arch == "arm64" else arch
                return f"llama-{tag}-bin-win-opencl-{suffix}.zip"
            if accel == "vulkan":
                return f"llama-{tag}-bin-win-vulkan-{arch}.zip"
            if accel == "sycl":
                return f"llama-{tag}-bin-win-sycl-{arch}.zip"
        return f"llama-{tag}-bin-win-cpu-{arch}.zip"

    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def _ensure_llama_binary() -> Path:
    # Cache under ~/.cache/plamo-translate/llama.cpp/{tag}/
    cache_dir = Path.home() / ".cache" / "plamo-translate" / "llama.cpp"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Query latest release
    release_api = "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"
    data = json.loads(_http_get(release_api).decode("utf-8"))
    tag: str = data.get("tag_name")
    if not tag:
        raise RuntimeError("Failed to get llama.cpp release tag")

    # Already downloaded for this tag?
    tag_dir = cache_dir / tag
    bin_marker = tag_dir / "BIN_PATH"
    if bin_marker.exists():
        p = Path(bin_marker.read_text().strip())
        if p.exists():
            return p

    asset_name = _detect_asset_name(tag)
    assets: List[dict] = data.get("assets", [])
    asset = None
    for a in assets:
        if a.get("name") == asset_name:
            asset = a
            break
    if asset is None:
        available = [a.get("name") for a in assets]
        raise RuntimeError(
            f"Could not find a suitable llama.cpp binary asset ({asset_name}). Available: {available}"
        )

    url = asset.get("browser_download_url")
    if not url:
        raise RuntimeError("Asset has no download URL")

    # Download + extract
    tag_dir.mkdir(parents=True, exist_ok=True)
    tmp_zip = tag_dir / asset_name
    _download_to(url, tmp_zip)

    extract_dir = tag_dir / "extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    _extract_zip(tmp_zip, extract_dir)

    llama_bin = _find_llama_binary(extract_dir)
    if not llama_bin:
        raise RuntimeError("llama binary not found in the extracted archive")
    _make_executable(llama_bin)

    bin_marker.write_text(str(llama_bin))
    return llama_bin


def _read_chat_template() -> Optional[str]:
    try:
        ref = importlib.resources.files("plamo_translate.assets").joinpath("chat_template.jinja2")
        return ref.read_text(encoding="utf-8")
    except Exception:
        return None


def _build_prompt(messages: List[object]) -> str:
    # Minimal prompt construction: concatenate contents in order.
    # The MLX backend uses a tokenizer chat_template; here we avoid that
    # and emit the plain message contents, which matches the model's
    # training format (input/output lines) for PLaMo Translate.
    parts: List[str] = []
    for m in messages:
        # Support pydantic models or dict-like
        content = getattr(m, "content", None)
        if content is None and isinstance(m, dict):
            content = m.get("content", "")
        if content is None:
            content = ""
        parts.append(content.rstrip("\n"))
    return "\n".join(parts) + "\n"


def _prefer_gguf_filename(files: Sequence[str]) -> Optional[str]:
    # Try to find a GGUF file matching preferred quantizations
    preferred = [
        "q4_k_m",
        "q4_k_s",
        "q4_0",
        "q5_k_m",
        "q5_0",
        "q8_0",
    ]
    ggufs = [f for f in files if f.lower().endswith(".gguf")]
    if not ggufs:
        return None
    low = [f.lower() for f in ggufs]
    for pref in preferred:
        for i, name in enumerate(low):
            if pref in name:
                return ggufs[i]
    return ggufs[0]


def _download_model_via_hf() -> Path:
    """Download GGUF model from Hugging Face if not provided via env.

    Environment variables supported:
    - PLAMO_TRANSLATE_CLI_HF_REPO: repo id like "mmnga/plamo-2-translate-gguf"
    - PLAMO_TRANSLATE_CLI_HF_FILE: specific filename within the repo
    - PLAMO_TRANSLATE_CLI_HF_REVISION: branch/tag/commit
    - PLAMO_TRANSLATE_CLI_QUANT: hint like "q4_k_m" to filter file selection
    """
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
    except Exception as e:
        raise RuntimeError(
            "huggingface_hub is required to auto-download GGUF model. "
            "Please install it or set PLAMO_TRANSLATE_CLI_LLAMA_CPP_MODEL to a local .gguf file."
        ) from e

    repo_id = os.environ.get("PLAMO_TRANSLATE_CLI_HF_REPO", "mmnga/plamo-2-translate-gguf")
    hf_file = os.environ.get("PLAMO_TRANSLATE_CLI_HF_FILE")
    revision = os.environ.get("PLAMO_TRANSLATE_CLI_HF_REVISION")

    if hf_file is None:
        # Try to resolve a file from repo listing, optionally using quant hint
        try:
            files = list_repo_files(repo_id, revision=revision)
        except Exception as e:
            raise RuntimeError(f"Failed to list files for {repo_id}: {e}") from e

        quant_hint = os.environ.get("PLAMO_TRANSLATE_CLI_QUANT", "").lower()
        if quant_hint:
            cand = [f for f in files if f.lower().endswith(".gguf") and quant_hint in f.lower()]
            if cand:
                hf_file = cand[0]
        if hf_file is None:
            hf_file = _prefer_gguf_filename(files)
        if hf_file is None:
            raise RuntimeError(f"No .gguf files found in repo {repo_id}")

    local_path = hf_hub_download(repo_id=repo_id, filename=hf_file, revision=revision)
    p = Path(local_path)
    update_config(model_path=str(p))
    return p


class PLaMoTranslateServer(FastMCP):
    """PLaMo Translate Server using llama.cpp binary."""

    def __init__(self, log_level: str, show_progress: bool = False) -> None:
        super().__init__(
            name="plamo-translate",
            instructions=INSTRUCTION,
            log_level=log_level,
            stateless_http=False,
            host="127.0.0.1",
            port=find_free_port(),
            lifespan=self.lifespan,
        )

        self.show_progress = show_progress

        # Ensure llama.cpp binary is available
        self.llama_bin = _ensure_llama_binary()

        # Resolve model path (.gguf)
        self.model_path = self._resolve_model_path()
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"GGUF model file not found at: {self.model_path}. "
                "Set PLAMO_TRANSLATE_CLI_LLAMA_CPP_MODEL to a .gguf path."
            )

        # Start llama-server
        self.llama_server_port = _find_free_tcp_port()
        self._start_llama_server()

        # Register tool
        self.add_tool(
            fn=self.translate,
            name="plamo-translate",
            description=INSTRUCTION,
        )

    def _resolve_model_path(self) -> Path:
        # Priority 1: PLAMO_TRANSLATE_CLI_LLAMA_CPP_MODEL (explicit .gguf path)
        # Priority 2: PLAMO_TRANSLATE_CLI_MODEL_NAME if it looks like a path to .gguf
        # Priority 3: config file model_path
        # Fallback: auto-download via huggingface_hub
        mp = os.environ.get("PLAMO_TRANSLATE_CLI_LLAMA_CPP_MODEL")
        if mp:
            p = Path(mp).expanduser()
            update_config(model_path=str(p))
            return p

        name = os.environ.get("PLAMO_TRANSLATE_CLI_MODEL_NAME", "")
        if name.endswith(".gguf") or "/" in name or name.startswith("."):
            p = Path(name).expanduser()
            update_config(model_path=str(p))
            return p

        # As a last resort, look in config file
        cfg = update_config()
        if "model_path" in cfg:
            p = Path(cfg["model_path"]).expanduser()
            if p.exists():
                return p

        # Auto-download from Hugging Face
        return _download_model_via_hf()

    @contextlib.asynccontextmanager
    async def lifespan(self, server: FastMCP):
        try:
            async with contextlib.AsyncExitStack() as stack:
                yield
        except Exception as e:
            logger.error(f"Error during lifespan: {str(e)} {e}")
            await stack.aclose()
        finally:
            # Cleanup llama-server process if running
            proc = getattr(self, "llama_proc", None)
            if proc and isinstance(proc, subprocess.Popen):
                with contextlib.suppress(Exception):
                    proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    with contextlib.suppress(Exception):
                        proc.kill()

    def _start_llama_server(self) -> None:
        cmd: List[str] = [
            str(self.llama_bin),
            "-m",
            str(self.model_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.llama_server_port),
            "--no-webui",
        ]

        threads = os.environ.get("PLAMO_TRANSLATE_CLI_THREADS")
        if threads:
            cmd += ["-t", str(int(threads))]
        ngl = os.environ.get("PLAMO_TRANSLATE_CLI_LLAMA_CPP_NGL")
        if ngl:
            cmd += ["-ngl", str(int(ngl))]

        # Reduce logging noise
        env = os.environ.copy()
        env.setdefault("LLAMA_LOG_COLORS", "0")
        env.setdefault("LLAMA_LOG_TIMESTAMPS", "0")
        env.setdefault("LLAMA_LOG_PREFIX", "0")

        self.llama_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
        )

        # Wait until server is ready
        self._wait_for_llama_server_ready(timeout_s=60)

    def _wait_for_llama_server_ready(self, timeout_s: int = 60) -> None:
        import time
        start = time.time()
        url_base = f"http://127.0.0.1:{self.llama_server_port}"
        last_err: Optional[Exception] = None
        while time.time() - start < timeout_s:
            try:
                # Try health endpoint if available
                data = _http_get(url_base + "/health")
                if data:
                    return
            except Exception as e:
                last_err = e
            try:
                # Fallback to root path
                data = _http_get(url_base + "/")
                if data:
                    return
            except Exception as e:
                last_err = e
            time.sleep(0.2)
        raise RuntimeError(f"llama-server did not become ready: {last_err}")

    def _request_completion(self, prompt: str, stream: bool) -> tuple[Optional[str], Optional[object]]:
        import urllib.request
        import urllib.error

        url = f"http://127.0.0.1:{self.llama_server_port}/completion"
        body: Dict[str, object] = {
            "prompt": prompt,
            "n_predict": int(PLAMO_MAX_TOKENS) if str(PLAMO_MAX_TOKENS).isdigit() else 32768,
            "temperature": float(PLAMO_TRANSLATE_CLI_TEMP),
            "top_p": float(PLAMO_TRANSLATE_CLI_TOP_P),
            "top_k": int(PLAMO_TRANSLATE_CLI_TOP_K),
            "stream": stream,
        }
        if PLAMO_TRANSLATE_CLI_REPETITION_PENALTY is not None:
            body["repeat_penalty"] = float(PLAMO_TRANSLATE_CLI_REPETITION_PENALTY)
        if PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE is not None:
            body["repeat_last_n"] = int(PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE)

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            resp = urllib.request.urlopen(req)  # nosec - local trusted
            if stream:
                return None, resp
            else:
                data = resp.read()
                return data.decode("utf-8", errors="ignore"), None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"llama-server HTTP error: {e.status} {e.reason}")
        except Exception as e:
            raise RuntimeError(f"llama-server request error: {e}")

    async def translate(self, request: TranslateRequest, stream: bool, context: Context) -> str:
        logger.info(f"Received translation request: {context.request_id}")

        try:
            # Build prompt text
            messages = construct_llm_input(request)
            prompt = _build_prompt(messages)

            # Proxy to llama-server
            text_resp, stream_resp = self._request_completion(prompt, stream=stream)

            if not stream:
                # Parse JSON and extract text
                try:
                    obj = json.loads(text_resp or "{}")
                except json.JSONDecodeError:
                    # Some versions return plaintext; return as-is
                    return text_resp or ""
                # Common fields across llama-server versions
                for key in ("content", "response", "text"):
                    if key in obj:
                        return str(obj[key])
                # OpenAI-compatible responses under choices[0].text
                try:
                    return obj["choices"][0]["text"]
                except Exception:
                    return text_resp or ""

            # Stream via SSE-like events
            assert stream_resp is not None
            translation = ""
            segments_count = 0
            # The HTTPResponse object behaves like a file
            for raw_line in stream_resp:
                try:
                    line = raw_line.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                if not line:
                    continue
                # Handle SSE: lines prefixed with "data: " contain JSON
                if line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    if data in ("[DONE]", "DONE"):
                        break
                    try:
                        evt = json.loads(data)
                    except Exception:
                        # Sometimes a single char token is sent directly
                        token = data
                    else:
                        token = (
                            evt.get("content")
                            or evt.get("token")
                            or evt.get("delta")
                            or evt.get("response")
                            or evt.get("text")
                            or ""
                        )
                    if token:
                        translation += str(token)
                        segments_count += 1
                        await context.report_progress(progress=segments_count, total=None, message=str(token))
                        await asyncio.sleep(0)

            return ""

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise e
