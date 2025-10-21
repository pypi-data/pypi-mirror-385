from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import fitz  # type: ignore
import pikepdf

from .text_image import RasterImage, create_text_image
from .utils import (
    FileStats,
    add_pdf_extension,
    contains_chinese,
    ensure_directory,
    ensure_parent_dir,
    format_file_size,
    get_file_stats,
    parse_page_range,
    resolve_output_dir,
    resolve_output_path,
    slugify_for_filename,
)


@dataclass
class ProcessedFile:
    path: Path
    name: str
    pages: int
    formatted_size: str


@dataclass
class MergeResult:
    output_path: Path
    files: List[ProcessedFile]
    total_pages: int
    total_input_size: int
    output_stats: FileStats


@dataclass
class SplitItem:
    path: Path
    name: str
    pages: int
    formatted_size: str


@dataclass
class SplitResult:
    output_dir: Path
    items: List[SplitItem]
    total_pages: int
    input_stats: FileStats


@dataclass
class ImageFile:
    path: Path
    size: int


@dataclass
class PDFToImageResult:
    input_path: Path
    output_dir: Path
    format: str
    quality: int
    dpi: int
    page_numbers: List[int]
    files: List[ImageFile]


@dataclass
class WatermarkResult:
    output_path: Path
    page_count: int
    watermark_description: str
    watermark_type: str


@dataclass
class EncryptResult:
    output_path: Path
    page_count: int
    mode: str
    permissions: dict[str, bool]


@dataclass
class TextImageResult:
    output_path: Path
    text: str
    font_size: int
    color: str
    background_color: str
    width: int
    height: int
    file_stats: FileStats


def _to_path(path_like: str) -> Path:
    return Path(path_like).expanduser().resolve()


def merge_pdf(input_paths: Sequence[str], output_path: str, title: Optional[str] = None) -> MergeResult:
    if not input_paths:
        raise ValueError("必须提供至少一个输入PDF文件")

    processed_files: list[ProcessedFile] = []
    total_input_size = 0
    total_pages = 0

    resolved_output_path = add_pdf_extension(resolve_output_path(_to_path(input_paths[0]), output_path))
    ensure_parent_dir(resolved_output_path)

    with pikepdf.Pdf.new() as merged_pdf:
        if title:
            merged_pdf.docinfo["/Title"] = title
        merged_pdf.docinfo["/Producer"] = "PDF Operation MCP (Python)"

        for input_path in input_paths:
            source_path = _to_path(input_path)
            if not source_path.exists():
                raise FileNotFoundError(f"文件不存在: {source_path}")

            stats = get_file_stats(source_path)
            total_input_size += stats.size

            with pikepdf.Pdf.open(source_path) as pdf:
                page_count = len(pdf.pages)
                if page_count == 0:
                    continue
                merged_pdf.pages.extend(pdf.pages)
                total_pages += page_count
                processed_files.append(
                    ProcessedFile(
                        path=source_path,
                        name=source_path.name,
                        pages=page_count,
                        formatted_size=stats.formatted_size,
                    )
                )

        if total_pages == 0:
            raise ValueError("所有PDF均为空，无法合并")

        merged_pdf.save(resolved_output_path)

    output_stats = get_file_stats(resolved_output_path)
    return MergeResult(
        output_path=resolved_output_path,
        files=processed_files,
        total_pages=total_pages,
        total_input_size=total_input_size,
        output_stats=output_stats,
    )


def split_pdf(
    input_path: str,
    output_dir: str,
    split_mode: str = "pages",
    ranges: Optional[Sequence[str]] = None,
    prefix: Optional[str] = None,
) -> SplitResult:
    source_path = _to_path(input_path)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须为PDF")

    resolved_output_dir = resolve_output_dir(source_path, output_dir)
    ensure_directory(resolved_output_dir)

    with pikepdf.Pdf.open(source_path) as pdf:
        total_pages = len(pdf.pages)
        if total_pages == 0:
            raise ValueError("输入PDF为空")

        base_name = prefix or source_path.stem
        items: list[SplitItem] = []

        if split_mode == "pages":
            for page_index, page in enumerate(pdf.pages, start=1):
                output_path = resolved_output_dir / f"{base_name}_page_{page_index:03d}.pdf"
                new_pdf = pikepdf.Pdf.new()
                new_pdf.pages.append(page)
                new_pdf.save(output_path)
                new_pdf.close()
                stats = get_file_stats(output_path)
                items.append(
                    SplitItem(
                        path=output_path,
                        name=output_path.name,
                        pages=1,
                        formatted_size=stats.formatted_size,
                    )
                )
        elif split_mode == "ranges" and ranges:
            for range_expression in ranges:
                page_numbers = parse_page_range(range_expression, total_pages)
                if not page_numbers:
                    continue

                new_pdf = pikepdf.Pdf.new()
                for page_number in page_numbers:
                    new_pdf.pages.append(pdf.pages[page_number - 1])

                start = min(page_numbers)
                end = max(page_numbers)
                if start == end:
                    file_name = f"{base_name}_page_{start:03d}.pdf"
                else:
                    file_name = f"{base_name}_pages_{start:03d}-{end:03d}.pdf"

                output_path = resolved_output_dir / file_name
                new_pdf.save(output_path)
                new_pdf.close()
                stats = get_file_stats(output_path)
                items.append(
                    SplitItem(
                        path=output_path,
                        name=file_name,
                        pages=len(page_numbers),
                        formatted_size=stats.formatted_size,
                    )
                )
        else:
            raise ValueError("使用 ranges 模式时必须提供 ranges 参数")

    if not items:
        raise ValueError("未生成任何拆分结果")

    return SplitResult(
        output_dir=resolved_output_dir,
        items=items,
        total_pages=total_pages,
        input_stats=get_file_stats(source_path),
    )


def _render_page_to_image(
    page: fitz.Page,
    image_format: str,
    dpi: int,
    quality: int,
) -> bytes:
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, alpha=image_format == "png")
    if image_format == "png":
        return pix.tobytes("png")
    return pix.tobytes("jpg", jpg_quality=quality)


def pdf_to_image(
    input_path: str,
    output_dir: str,
    format: str = "jpeg",
    quality: int = 80,
    dpi: int = 150,
    pages: Optional[str] = None,
    prefix: Optional[str] = None,
) -> PDFToImageResult:
    image_format = format.lower()
    if image_format not in {"jpeg", "jpg", "png"}:
        raise ValueError("图片格式仅支持 jpeg 或 png")
    if image_format == "jpg":
        image_format = "jpeg"

    source_path = _to_path(input_path)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须为PDF")

    doc = fitz.open(source_path)
    total_pages = doc.page_count
    if total_pages == 0:
        raise ValueError("输入PDF为空")

    page_numbers = parse_page_range(pages, total_pages)
    resolved_output_dir = resolve_output_dir(source_path, output_dir)
    ensure_directory(resolved_output_dir)
    base_name = prefix or source_path.stem

    files: list[ImageFile] = []
    for page_number in page_numbers:
        page = doc.load_page(page_number - 1)
        image_bytes = _render_page_to_image(page, image_format, dpi, quality)
        output_name = f"{base_name}_{page_number:03d}.{ 'jpg' if image_format == 'jpeg' else 'png'}"
        output_path = resolved_output_dir / output_name
        ensure_parent_dir(output_path)
        output_path.write_bytes(image_bytes)
        stats = get_file_stats(output_path)
        files.append(ImageFile(path=output_path, size=stats.size))

    doc.close()

    return PDFToImageResult(
        input_path=source_path,
        output_dir=resolved_output_dir,
        format=image_format,
        quality=quality,
        dpi=dpi,
        page_numbers=page_numbers,
        files=files,
    )


def _scale_dimensions(width: float, height: float, max_width: float, max_height: float) -> tuple[float, float]:
    scale = min(max_width / width, max_height / height, 1.0)
    return width * scale, height * scale


def _compute_position(position: str, page_rect: fitz.Rect, width: float, height: float) -> fitz.Rect:
    pos_map = {
        "center": (page_rect.width / 2 - width / 2, page_rect.height / 2 - height / 2),
        "top-left": (36, page_rect.height - height - 36),
        "top-right": (page_rect.width - width - 36, page_rect.height - height - 36),
        "bottom-left": (36, 36),
        "bottom-right": (page_rect.width - width - 36, 36),
    }

    x, y = pos_map.get(position, pos_map["center"])
    return fitz.Rect(x, y, x + width, y + height)


def _prepare_watermark_image(
    watermark_text: Optional[str],
    watermark_image_path: Optional[str],
    font_size: int,
    color: str,
    background_color: str,
    opacity: float = 1.0,
) -> tuple[RasterImage, str, str]:
    from io import BytesIO
    from PIL import Image

    if watermark_image_path:
        image_path = _to_path(watermark_image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"水印图片不存在: {image_path}")

        with Image.open(image_path) as img:
            rgba = img.convert("RGBA")
            # 应用透明度
            if opacity < 1.0:
                alpha = rgba.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                rgba.putalpha(alpha)
            buffer = BytesIO()
            rgba.save(buffer, format="PNG")
            return (
                RasterImage(data=buffer.getvalue(), width=rgba.width, height=rgba.height),
                f"图片水印: {image_path.name}",
                "image",
            )

    if not watermark_text:
        raise ValueError("必须提供文字或图片水印")

    raster = create_text_image(
        text=watermark_text,
        font_size=font_size,
        color=color,
        background_color=background_color,
    )

    # 应用透明度到文字水印
    if opacity < 1.0:
        img = Image.open(BytesIO(raster.data))
        rgba = img.convert("RGBA")
        alpha = rgba.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        rgba.putalpha(alpha)
        buffer = BytesIO()
        rgba.save(buffer, format="PNG")
        raster = RasterImage(data=buffer.getvalue(), width=rgba.width, height=rgba.height)

    watermark_type = "中文图片水印" if contains_chinese(watermark_text) else "文字水印"
    description = f"{watermark_type}: \"{watermark_text}\""
    return raster, description, "image"


def add_watermark(
    input_path: str,
    output_path: str,
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
    opacity: float = 0.3,
    font_size: int = 24,
    position: str = "center",
    rotation: float = 0.0,
    layout: str = "single",
) -> WatermarkResult:
    source_path = _to_path(input_path)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须为PDF")

    raster, description, watermark_type = _prepare_watermark_image(
        watermark_text,
        watermark_image_path,
        font_size,
        "#808080",
        "transparent",
        opacity=max(0.0, min(opacity, 1.0)),
    )

    doc = fitz.open(source_path)
    page_count = doc.page_count
    if page_count == 0:
        raise ValueError("输入PDF为空")

    for page in doc:
        rect = page.rect
        max_width = rect.width * 0.4
        max_height = rect.height * 0.4
        width, height = _scale_dimensions(raster.width, raster.height, max_width, max_height)
        
        if layout == "corners":
            # 四角模式
            positions = [
                _compute_position("top-left", rect, width, height),
                _compute_position("top-right", rect, width, height),
                _compute_position("bottom-left", rect, width, height),
                _compute_position("bottom-right", rect, width, height),
            ]
            for target_rect in positions:
                page.insert_image(
                    target_rect,
                    stream=raster.data,
                    overlay=True,
                    keep_proportion=True,
                    rotate=rotation,
                )
        
        elif layout == "tile":
            # 平铺模式
            spacing_x = width * 1.5
            spacing_y = height * 1.5
            
            cols = int(rect.width / spacing_x) + 1
            rows = int(rect.height / spacing_y) + 1
            
            for row in range(rows):
                for col in range(cols):
                    x = col * spacing_x
                    y = row * spacing_y
                    
                    if x + width <= rect.width and y + height <= rect.height:
                        target_rect = fitz.Rect(x, y, x + width, y + height)
                        page.insert_image(
                            target_rect,
                            stream=raster.data,
                            overlay=True,
                            keep_proportion=True,
                            rotate=rotation,
                        )
        
        else:
            # 单个位置模式
            target_rect = _compute_position(position, rect, width, height)
            page.insert_image(
                target_rect,
                stream=raster.data,
                overlay=True,
                keep_proportion=True,
                rotate=rotation,
            )

    resolved_output_path = add_pdf_extension(resolve_output_path(source_path, output_path))
    ensure_parent_dir(resolved_output_path)
    doc.save(resolved_output_path)
    doc.close()
    
    layout_desc = {
        "single": "",
        "corners": "(四角)",
        "tile": "(平铺)"
    }.get(layout, "")
    
    return WatermarkResult(
        output_path=resolved_output_path,
        page_count=page_count,
        watermark_description=f"{description}{layout_desc}",
        watermark_type=watermark_type,
    )


def _permissions_dict(permissions: Optional[dict]) -> dict[str, bool]:
    return {
        "printing": bool(permissions.get("printing")) if permissions else False,
        "modifying": bool(permissions.get("modifying")) if permissions else False,
        "copying": bool(permissions.get("copying")) if permissions else False,
        "annotating": bool(permissions.get("annotating")) if permissions else False,
        "fillingForms": bool(permissions.get("fillingForms")) if permissions else False,
    }


def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None,
    permissions: Optional[dict] = None,
    mode: str = "basic",
    dpi: int = 144,
    image_format: str = "png",
    quality: int = 85,
) -> EncryptResult:
    if not user_password:
        raise ValueError("必须提供用户密码")

    source_path = _to_path(input_path)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须为PDF")

    perms = _permissions_dict(permissions)

    if mode == "rasterize":
        doc = fitz.open(source_path)
        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("输入PDF为空")

        new_doc = fitz.open()
        scale = dpi / 72.0
        matrix = fitz.Matrix(scale, scale)

        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=image_format == "png")
            img_bytes = pix.tobytes("png" if image_format == "png" else "jpg", jpg_quality=quality)
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=img_bytes)

        resolved_output_path = add_pdf_extension(resolve_output_path(source_path, output_path))
        ensure_parent_dir(resolved_output_path)

        permission_bits = 0
        if perms["printing"]:
            permission_bits |= fitz.PDF_PERM_PRINT
        if perms["modifying"]:
            permission_bits |= fitz.PDF_PERM_MODIFY
        if perms["copying"]:
            permission_bits |= fitz.PDF_PERM_COPY
        if perms["annotating"]:
            permission_bits |= fitz.PDF_PERM_ANNOTATE
        if perms["fillingForms"]:
            permission_bits |= fitz.PDF_PERM_FILL_FORM

        new_doc.save(
            resolved_output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw=owner_password or user_password,
            user_pw=user_password,
            permissions=permission_bits,
        )
        doc.close()
        new_doc.close()

        return EncryptResult(
            output_path=resolved_output_path,
            page_count=page_count,
            mode="rasterize",
            permissions=perms,
        )

    with pikepdf.Pdf.open(source_path) as pdf:
        page_count = len(pdf.pages)
        if page_count == 0:
            raise ValueError("输入PDF为空")

        resolved_output_path = add_pdf_extension(resolve_output_path(source_path, output_path))
        ensure_parent_dir(resolved_output_path)

        allow = pikepdf.Permissions(
            print=perms["printing"],
            modify=perms["modifying"],
            copy=perms["copying"],
            annotate=perms["annotating"],
            form=perms["fillingForms"],
        )

        pdf.save(
            resolved_output_path,
            encryption=pikepdf.Encryption(
                owner=owner_password or user_password,
                user=user_password,
                allow=allow,
                R=6,
            ),
        )

    return EncryptResult(
        output_path=resolved_output_path,
        page_count=page_count,
        mode="basic",
        permissions=perms,
    )


def create_text_image_file(
    text: str,
    output_path: Optional[str] = None,
    font_size: int = 24,
    color: str = "#808080",
    background_color: str = "transparent",
) -> TextImageResult:
    if not text.strip():
        raise ValueError("文字内容不能为空")

    slug = slugify_for_filename(text)
    if output_path:
        target = Path(output_path).expanduser()
        if target.is_dir():
            target = target / f"watermark_{slug}.png"
    else:
        target = Path.cwd() / f"watermark_{slug}.png"

    target = target.with_suffix(".png")
    ensure_parent_dir(target)

    raster = create_text_image(
        text=text,
        font_size=font_size,
        color=color,
        background_color=background_color,
    )

    target.write_bytes(raster.data)
    stats = get_file_stats(target)

    return TextImageResult(
        output_path=target,
        text=text,
        font_size=font_size,
        color=color,
        background_color=background_color,
        width=raster.width,
        height=raster.height,
        file_stats=stats,
    )


@dataclass
class TextWatermarkResult:
    output_path: Path
    page_count: int
    watermark_text: str
    watermark_type: str


def add_text_watermark(
    input_path: str,
    output_path: str,
    watermark_text: str,
    opacity: float = 0.3,
    font_size: int = 24,
    position: str = "center",
    rotation: float = 0.0,
    color: tuple[float, float, float] = (0.5, 0.5, 0.5),
    layout: str = "single",
) -> TextWatermarkResult:
    """直接在PDF上添加文字水印（文字可选择、可复制）。
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        watermark_text: 水印文字内容
        opacity: 不透明度 (0.0-1.0)，通过调整颜色亮度实现
        font_size: 字体大小
        position: 位置："center", "top-left", "top-right", "bottom-left", "bottom-right"
        rotation: 旋转角度
        color: RGB颜色元组 (0.0-1.0)
        layout: 布局模式："single"(单个), "corners"(四角), "tile"(平铺)
    
    Returns:
        TextWatermarkResult: 添加水印的结果
    """
    source_path = _to_path(input_path)
    if not source_path.exists():
        raise FileNotFoundError(f"文件不存在: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须为PDF")
    
    if not watermark_text.strip():
        raise ValueError("水印文字不能为空")
    
    doc = fitz.open(source_path)
    page_count = doc.page_count
    if page_count == 0:
        raise ValueError("输入PDF为空")
    
    # 限制透明度和颜色值范围，通过提高颜色亮度来模拟透明度
    opacity = max(0.0, min(opacity, 1.0))
    # 将颜色调亮以模拟透明效果：越透明，颜色越接近白色
    adjusted_color = tuple(
        min(1.0, c + (1.0 - c) * (1.0 - opacity))
        for c in color
    )
    
    # PyMuPDF 的 insert_text 只支持 0, 90, 180, 270 度旋转
    # 对于其他角度，需要使用 TextWriter
    use_textwriter = rotation not in [0, 90, 180, 270]
    
    for page in doc:
        rect = page.rect
        text_width = fitz.get_text_length(watermark_text, fontsize=font_size)
        text_height = font_size
        
        if use_textwriter:
            # 使用 TextWriter 支持任意角度旋转
            tw = fitz.TextWriter(rect)
            
        if layout == "corners":
            # 四角模式
            positions = [
                (50, rect.height - 50),  # 左上
                (rect.width - text_width - 50, rect.height - 50),  # 右上
                (50, 50 + text_height),  # 左下
                (rect.width - text_width - 50, 50 + text_height),  # 右下
            ]
            for x, y in positions:
                if use_textwriter:
                    tw.append(
                        fitz.Point(x, y),
                        watermark_text,
                        fontsize=font_size,
                    )
                else:
                    page.insert_text(
                        fitz.Point(x, y),
                        watermark_text,
                        fontsize=font_size,
                        color=adjusted_color,
                        rotate=int(rotation),
                        overlay=True,
                    )
        
        elif layout == "tile":
            # 平铺模式
            spacing_x = text_width * 2.5
            spacing_y = text_height * 4
            
            # 计算需要多少行和列
            cols = int(rect.width / spacing_x) + 2
            rows = int(rect.height / spacing_y) + 2
            
            for row in range(rows):
                for col in range(cols):
                    x = col * spacing_x
                    y = row * spacing_y + text_height
                    
                    # 确保在页面范围内
                    if x < rect.width and y < rect.height:
                        if use_textwriter:
                            tw.append(
                                fitz.Point(x, y),
                                watermark_text,
                                fontsize=font_size,
                            )
                        else:
                            page.insert_text(
                                fitz.Point(x, y),
                                watermark_text,
                                fontsize=font_size,
                                color=adjusted_color,
                                rotate=int(rotation),
                                overlay=True,
                            )
        
        else:
            # 单个位置模式
            pos_map = {
                "center": (rect.width / 2 - text_width / 2, rect.height / 2),
                "top-left": (50, rect.height - 50),
                "top-right": (rect.width - text_width - 50, rect.height - 50),
                "bottom-left": (50, 50 + text_height),
                "bottom-right": (rect.width - text_width - 50, 50 + text_height),
            }
            
            x, y = pos_map.get(position, pos_map["center"])
            if use_textwriter:
                tw.append(
                    fitz.Point(x, y),
                    watermark_text,
                    fontsize=font_size,
                )
            else:
                page.insert_text(
                    fitz.Point(x, y),
                    watermark_text,
                    fontsize=font_size,
                    color=adjusted_color,
                    rotate=int(rotation),
                    overlay=True,
                )
        
        # 如果使用 TextWriter，应用颜色、旋转并写入页面
        if use_textwriter:
            tw.write_text(page, color=adjusted_color, overlay=True, rotate=rotation)
    
    resolved_output_path = add_pdf_extension(resolve_output_path(source_path, output_path))
    ensure_parent_dir(resolved_output_path)
    doc.save(resolved_output_path)
    doc.close()
    
    layout_desc = {
        "single": "单个位置",
        "corners": "四角",
        "tile": "平铺"
    }.get(layout, "单个位置")
    
    watermark_type = f"{'中文' if contains_chinese(watermark_text) else ''}文字水印({layout_desc})"
    
    return TextWatermarkResult(
        output_path=resolved_output_path,
        page_count=page_count,
        watermark_text=watermark_text,
        watermark_type=watermark_type,
    )
