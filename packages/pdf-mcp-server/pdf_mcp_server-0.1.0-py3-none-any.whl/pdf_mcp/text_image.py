from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .utils import contains_chinese


@dataclass
class RasterImage:
    data: bytes
    width: int
    height: int


_COMMON_FONT_CANDIDATES: tuple[str, ...] = (
    "PingFang.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti.ttf",
    "/Library/Fonts/Songti.ttc",
    "/Library/Fonts/华文黑体.ttf",
    "/System/Library/Fonts/STSong.ttf",
    "/System/Library/Fonts/Hiragino Sans GB W3.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/truetype/arphic/ukai.ttc",
    "SimHei.ttf",
    "msyh.ttc",
    "msyh.ttf",
)


def _iter_font_candidates(explicit: Optional[str], prefer_cjk: bool) -> Iterable[str]:
    if explicit:
        yield explicit

    if prefer_cjk:
        yield from _COMMON_FONT_CANDIDATES

    # Fallback to bundled DejaVu font for Latin scripts
    try:
        font_dir = Path(ImageFont.__file__).resolve().parent / "Fonts"
        yield str(font_dir / "DejaVuSans.ttf")
    except Exception:  # pragma: no cover - very unlikely
        pass


def _load_font(font_size: int, font_path: Optional[str], text: str) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    prefer_cjk = contains_chinese(text)
    for candidate in _iter_font_candidates(font_path, prefer_cjk):
        try:
            return ImageFont.truetype(candidate, font_size)
        except OSError:
            continue

    if prefer_cjk:
        raise RuntimeError(
            "未找到支持中文的字体，请通过 font_path 参数指定可用的中文字体"
        )

    return ImageFont.load_default()


def create_text_image(
    text: str,
    font_size: int = 24,
    color: str = "#808080",
    background_color: str = "transparent",
    font_path: Optional[str] = None,
) -> RasterImage:
    font = _load_font(font_size, font_path, text)

    # Pillow 的 getbbox 支持精确计算文本包围盒
    ascent, descent = font.getmetrics()
    (left, top, right, bottom) = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top

    padding_x = max(int(font_size * 0.4), 8)
    padding_y = max(int(font_size * 0.3), 8)

    width = text_width + padding_x * 2
    height = ascent + descent + padding_y * 2

    mode = "RGBA"
    if background_color.lower() == "transparent":
        background_rgba = (0, 0, 0, 0)
    else:
        background_rgba = ImageColor.getcolor(background_color, mode)

    image = Image.new(mode, (width, height), background_rgba)
    draw = ImageDraw.Draw(image)
    text_color = ImageColor.getcolor(color, mode)

    # 对于 getbbox 产生的偏移进行校正
    baseline_x = padding_x - left
    baseline_y = padding_y

    draw.text((baseline_x, baseline_y), text, fill=text_color, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return RasterImage(data=buffer.getvalue(), width=width, height=height)
