"""Generic OpenAI-compatible provider.

This is the "universal key" for integrating any image generation vendor that
speaks the OpenAI images protocol (/images/generations, /images/edits).
Switching vendors = changing baseUrl, no code changes.
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config_store import get_api_key, get_base_url
from .base import BaseProvider, ImageResult, guard_overwrite


NAME = "openai"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-image-1"


def _normalize_base_url(url: str) -> str:
    """Mirror api2img's normalizeBaseUrl: ensure the path ends with /v1."""
    trimmed = url.rstrip("/")
    if trimmed.endswith("/v1"):
        return trimmed
    return f"{trimmed}/v1"


def _client():
    try:
        from openai import OpenAI
        import httpx
    except ImportError:
        raise SystemExit(
            "openai provider 需要 openai + httpx 依赖。\n"
            "安装：pip install openai httpx\n"
            "（Seedream provider 无需额外依赖，可先用 --provider seedream）"
        )
    key = get_api_key(NAME)
    if not key:
        raise SystemExit(
            "未配置 openai provider 的 API Key。\n"
            "运行：python scripts/cli.py configure --provider openai "
            "--base-url <vendor-endpoint> --api-key <你的Key>"
        )
    raw_url = get_base_url(NAME) or DEFAULT_BASE_URL
    return OpenAI(
        api_key=key,
        base_url=_normalize_base_url(raw_url),
        http_client=httpx.Client(trust_env=False),
    )


def _resolve_out(out: Optional[str], prefix: str) -> Path:
    if out:
        return Path(out)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("output") / f"{prefix}_{ts}.png"


class OpenAICompatProvider(BaseProvider):
    name = NAME
    models = ["gpt-image-1", "dall-e-3", "dall-e-2"]
    default_model = DEFAULT_MODEL
    default_size = "1024x1024"
    required_packages = ["openai", "httpx"]

    def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        size: str = "1024x1024",
        n: int = 1,
        response_format: str = "b64_json",
        out: Optional[str] = None,
        force: bool = False,
        **_: Any,
    ) -> ImageResult:
        client = _client()
        kwargs: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
        }
        # Some relays only accept url; some only b64_json. Pass through what user asks.
        if response_format:
            kwargs["response_format"] = response_format

        resp = client.images.generate(**kwargs)
        if not resp.data:
            raise SystemExit("provider returned no image data.")

        item = resp.data[0]
        out_path = _resolve_out(out, NAME)
        guard_overwrite(out_path, force)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if getattr(item, "b64_json", None):
            out_path.write_bytes(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            urllib.request.urlretrieve(item.url, out_path)
        else:
            raise SystemExit("No downloadable image URL or b64_json was returned.")

        return ImageResult(
            path=out_path,
            provider=NAME,
            model=model,
            usage=resp.usage.model_dump() if hasattr(resp, "usage") else None,
        )

    def edit(
        self,
        image: Path,
        prompt: str,
        model: str = DEFAULT_MODEL,
        size: str = "1024x1024",
        mask: Optional[Path] = None,
        response_format: str = "b64_json",
        out: Optional[str] = None,
        force: bool = False,
        **_: Any,
    ) -> ImageResult:
        if not image.exists():
            raise SystemExit(f"Source image not found: {image}")

        client = _client()
        files = [image]
        if mask:
            mask_path = Path(mask)
            if not mask_path.exists():
                raise SystemExit(f"Mask image not found: {mask_path}")
            files.append(mask_path)

        handles = [f.open("rb") for f in files]
        try:
            kwargs: Dict[str, Any] = {
                "model": model,
                "image": handles[0],
                "prompt": prompt,
                "size": size,
            }
            if mask:
                kwargs["mask"] = handles[1]
            if response_format:
                kwargs["response_format"] = response_format

            resp = client.images.edit(**kwargs)
        finally:
            for h in handles:
                h.close()

        if not resp.data:
            raise SystemExit("provider returned no image data.")

        item = resp.data[0]
        out_path = _resolve_out(out, f"{NAME}_edit")
        guard_overwrite(out_path, force)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if getattr(item, "b64_json", None):
            out_path.write_bytes(base64.b64decode(item.b64_json))
        elif getattr(item, "url", None):
            urllib.request.urlretrieve(item.url, out_path)
        else:
            raise SystemExit("No downloadable image URL or b64_json was returned.")

        return ImageResult(
            path=out_path,
            provider=NAME,
            model=model,
            usage=resp.usage.model_dump() if hasattr(resp, "usage") else None,
        )
