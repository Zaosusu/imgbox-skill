"""StepFun provider (OpenAI-compatible images API)."""
from __future__ import annotations

import base64
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config_store import get_api_key
from .base import BaseProvider, ImageResult, guard_overwrite


NAME = "stepfun"
MODELS = [
    "step-image-edit-2",
    "step-2x-large",
    "step-1x-medium",
]
DEFAULT_MODEL = "step-image-edit-2"
BASE_URL = "https://api.stepfun.com/step_plan/v1"


def _disable_proxy() -> None:
    for key in ["ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY"]:
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "*"


_disable_proxy()


def _api_key() -> str:
    key = get_api_key(NAME)
    if not key:
        raise SystemExit(
            "未配置 StepFun API Key（或仍是占位符）。\n"
            "运行：python scripts/cli.py configure --provider stepfun --api-key <你的Key>"
        )
    return key


def _client() -> "OpenAI":
    try:
        from openai import OpenAI
        import httpx
    except ImportError:
        raise SystemExit(
            "StepFun provider 需要 openai + httpx 依赖。\n"
            "安装：pip install openai httpx\n"
            "（Seedream provider 无需额外依赖，可先用 --provider seedream）"
        )
    return OpenAI(
        api_key=_api_key(),
        base_url=BASE_URL,
        http_client=httpx.Client(trust_env=False),
    )


def _resolve_out(out: Optional[str], prefix: str, suffix: str) -> Path:
    if out:
        return Path(out)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("output") / f"{prefix}_{ts}{suffix}"


class StepFunProvider(BaseProvider):
    name = NAME
    models = MODELS
    default_model = DEFAULT_MODEL
    default_size = "1024x1024"
    required_packages = ["openai", "httpx"]
    BASE_URL = BASE_URL

    def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        size: str = "1024x1024",
        steps: Optional[int] = None,
        seed: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        neg_prompt: Optional[str] = None,
        text_mode: bool = False,
        n: int = 1,
        response_format: str = "url",
        style_reference: Optional[Dict[str, Any]] = None,
        out: Optional[str] = None,
        force: bool = False,
        **_: Any,
    ) -> ImageResult:
        if steps is None:
            steps = 8 if model == "step-image-edit-2" else 50
        if cfg_scale is None:
            cfg_scale = 1.0 if model == "step-image-edit-2" else (6.0 if model == "step-2x-large" else 7.5)

        extra: Dict[str, Any] = {
            "steps": steps,
            "cfg_scale": cfg_scale,
        }
        if seed is not None:
            extra["seed"] = seed
        if neg_prompt:
            extra["negative_prompt"] = neg_prompt
        if text_mode:
            extra["text_mode"] = True
        if style_reference is not None:
            extra["style_reference"] = style_reference

        client = _client()
        resp = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=n,
            response_format=response_format,
            extra_body=extra,
        )
        if not resp.data:
            raise SystemExit("StepFun returned no image data.")

        item = resp.data[0]
        out_path = _resolve_out(out, "stepfun", ".png")
        guard_overwrite(out_path, force)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if response_format == "b64_json" and item.b64_json:
            out_path.write_bytes(base64.b64decode(item.b64_json))
        elif item.url:
            urllib.request.urlretrieve(item.url, out_path)
        else:
            raise SystemExit("No downloadable image URL or b64_json was returned.")

        return ImageResult(
            path=out_path,
            provider=NAME,
            model=model,
            usage=resp.usage.model_dump() if getattr(resp, "usage", None) is not None else None,
        )

    def edit(
        self,
        image: Path,
        prompt: str,
        model: str = DEFAULT_MODEL,
        steps: int = 8,
        seed: Optional[int] = None,
        cfg_scale: float = 1.0,
        neg_prompt: str = "",
        text_mode: bool = False,
        response_format: str = "b64_json",
        out: Optional[str] = None,
        force: bool = False,
        **_: Any,
    ) -> ImageResult:
        if not image.exists():
            raise SystemExit(f"Source image not found: {image}")

        extra: Dict[str, Any] = {
            "steps": steps,
            "cfg_scale": cfg_scale,
        }
        if seed is not None:
            extra["seed"] = seed
        if neg_prompt:
            extra["negative_prompt"] = neg_prompt
        if text_mode:
            extra["text_mode"] = True

        client = _client()
        with image.open("rb") as f:
            resp = client.images.edit(
                model=model,
                image=f,
                prompt=prompt,
                response_format=response_format,
                extra_body=extra,
            )
        if not resp.data:
            raise SystemExit("StepFun returned no image data.")

        item = resp.data[0]
        suffix = image.suffix or ".png"
        out_path = _resolve_out(out, f"stepfun_edit_{image.stem}", suffix)
        guard_overwrite(out_path, force)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if response_format == "b64_json" and item.b64_json:
            out_path.write_bytes(base64.b64decode(item.b64_json))
        elif item.url:
            urllib.request.urlretrieve(item.url, out_path)
        else:
            raise SystemExit("No downloadable image URL or b64_json was returned.")

        return ImageResult(
            path=out_path,
            provider=NAME,
            model=model,
            usage=resp.usage.model_dump() if getattr(resp, "usage", None) is not None else None,
        )
