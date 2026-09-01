"""Base provider for image generation / editing."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ImageResult:
    path: Path
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    extra_paths: Optional[list] = None


class BaseProvider(ABC):
    name: str = ""
    models: list[str] = []
    default_model: str = ""
    default_size: str = "1024x1024"

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        raise NotImplementedError

    @abstractmethod
    def edit(self, image: Path, prompt: str, **kwargs: Any) -> ImageResult:
        raise NotImplementedError


def guard_overwrite(path: Path, force: bool) -> None:
    """Refuse to silently overwrite an existing file unless --force is given.

    Mirrors api2img's writeImages() behaviour: existing outputs are protected
    by default, and the caller must opt in to replacement.
    """
    if path.exists() and not force:
        raise SystemExit(
            f"输出文件已存在，已跳过（避免覆盖）：{path}\n"
            f"如需覆盖请加 --force 参数。"
        )
