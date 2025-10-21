"""PDF MCP Server using FastMCP."""

from __future__ import annotations

import logging
from typing import Optional

from fastmcp import FastMCP

from .pdf_tools import (
    add_text_watermark,
    add_watermark,
    create_text_image_file,
    encrypt_pdf,
    merge_pdf,
    pdf_to_image,
    split_pdf,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("PDF Operations")


@mcp.tool()
def merge_pdfs(
    input_paths: list[str],
    output_path: str,
    title: Optional[str] = None,
) -> str:
    """合并多个PDF文件为一个PDF。
    
    Args:
        input_paths: 输入PDF文件路径列表
        output_path: 输出PDF文件路径
        title: 可选的PDF标题
    
    Returns:
        合并结果的详细信息
    """

    try:
        result = merge_pdf(input_paths, output_path, title)
        files_info = "\n".join([
            f"  - {f.name}: {f.pages}页, {f.formatted_size}"
            for f in result.files
        ])
        return (
            f"✅ PDF合并成功\n"
            f"输出文件: {result.output_path}\n"
            f"总页数: {result.total_pages}\n"
            f"输出大小: {result.output_stats.formatted_size}\n"
            f"合并的文件:\n{files_info}"
        )
    except Exception as e:
        logger.error(f"合并PDF失败: {e}")
        raise


@mcp.tool()
def split_pdf_file(
    input_path: str,
    output_dir: str,
    split_mode: str = "pages",
    ranges: Optional[list[str]] = None,
    prefix: Optional[str] = None,
) -> str:
    """拆分PDF文件。
    
    Args:
        input_path: 输入PDF文件路径
        output_dir: 输出目录路径
        split_mode: 拆分模式，"pages"(每页一个文件) 或 "ranges"(按范围拆分)
        ranges: 页面范围列表，如 ["1-3", "5", "7-10"]，仅在 ranges 模式下使用
        prefix: 输出文件名前缀
    
    Returns:
        拆分结果的详细信息
    """
    
    try:
        result = split_pdf(input_path, output_dir, split_mode, ranges, prefix)
        items_info = "\n".join([
            f"  - {item.name}: {item.pages}页, {item.formatted_size}"
            for item in result.items
        ])
        return (
            f"✅ PDF拆分成功\n"
            f"输出目录: {result.output_dir}\n"
            f"生成文件数: {len(result.items)}\n"
            f"原始总页数: {result.total_pages}\n"
            f"拆分文件:\n{items_info}"
        )
    
    except Exception as e:
        logger.error(f"拆分PDF失败: {e}")
        raise
        


@mcp.tool()
def convert_pdf_to_images(
    input_path: str,
    output_dir: str,
    format: str = "jpeg",
    quality: int = 80,
    dpi: int = 150,
    pages: Optional[str] = None,
    prefix: Optional[str] = None,
) -> str:
    """将PDF页面转换为图片。
    
    Args:
        input_path: 输入PDF文件路径
        output_dir: 输出目录路径
        format: 图片格式，"jpeg" 或 "png"
        quality: JPEG质量 (1-100)
        dpi: 图片分辨率
        pages: 页面范围，如 "1-3,5,7-10" 或 "all"
        prefix: 输出文件名前缀
    
    Returns:
        转换结果的详细信息
    """
    
    try:
        result = pdf_to_image(input_path, output_dir, format, quality, dpi, pages, prefix)
        total_size = sum(f.size for f in result.files)
        from .utils import format_file_size
        
        return (
            f"✅ PDF转图片成功\n"
            f"输出目录: {result.output_dir}\n"
            f"格式: {result.format.upper()}\n"
            f"DPI: {result.dpi}\n"
            f"质量: {result.quality}\n"
            f"转换页数: {len(result.page_numbers)}\n"
            f"生成文件数: {len(result.files)}\n"
            f"总大小: {format_file_size(total_size)}"
        )
    
    except Exception as e:
        logger.error(f"转换PDF失败: {e}")
        raise


@mcp.tool()
def add_pdf_watermark(
    input_path: str,
    output_path: str,
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
    opacity: float = 0.5,
    font_size: int = 24,
    position: str = "center",
    rotation: float = 0.0,
    layout: str = "tile",
) -> str:
    """为PDF添加水印。
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        watermark_text: 水印文字内容
        watermark_image_path: 水印图片路径
        opacity: 不透明度 (0.0-1.0)
        font_size: 文字大小
        position: 位置，可选 "center", "top-left", "top-right", "bottom-left", "bottom-right"
        rotation: 旋转角度
        layout: 布局模式，可选 "single"(单个), "corners"(四角), "tile"(平铺)
    
    Returns:
        添加水印结果的详细信息
    """
    
    try:
        result = add_watermark(
            input_path,
            output_path,
            watermark_text,
            watermark_image_path,
            opacity,
            font_size,
            position,
            rotation,
            layout,
        )
        return (
            f"✅ 添加水印成功\n"
            f"输出文件: {result.output_path}\n"
            f"页数: {result.page_count}\n"
            f"水印类型: {result.watermark_type}\n"
            f"水印描述: {result.watermark_description}"
        )
    
    except Exception as e:
        logger.error(f"添加失败: {e}")
        raise


@mcp.tool()
def add_text_watermark_direct(
    input_path: str,
    output_path: str,
    watermark_text: str,
    opacity: float = 0.4,
    font_size: int = 24,
    position: str = "center",
    color_r: float = 0.5,
    color_g: float = 0.5,
    color_b: float = 0.5,
    layout: str = "tile",
) -> str:
    """直接在PDF上添加文字水印（文字可选择、可复制）。
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        watermark_text: 水印文字内容
        opacity: 不透明度 (0.0-1.0)，通过调整颜色亮度实现，建议 0.1-0.3
        font_size: 字体大小
        position: 位置，可选 "center", "top-left", "top-right", "bottom-left", "bottom-right"
        color_r: 红色分量 (0.0-1.0)
        color_g: 绿色分量 (0.0-1.0)
        color_b: 蓝色分量 (0.0-1.0)
        layout: 布局模式，可选 "single"(单个), "corners"(四角), "tile"(平铺)
    
    Returns:
        添加文字水印结果的详细信息
    """

    
    try:
        result = add_text_watermark(
            input_path,
            output_path,
            watermark_text,
            opacity,
            font_size,
            position,
            0.0,
            (color_r, color_g, color_b),
            layout,
        )
        
        layout_tips = {
            "single": "单个位置",
            "corners": "四个角落",
            "tile": "整页平铺"
        }.get(layout, "单个位置")
        
        return (
            f"✅ 添加文字水印成功\n"
            f"输出文件: {result.output_path}\n"
            f"页数: {result.page_count}\n"
            f"水印类型: {result.watermark_type}\n"
            f"水印内容: {result.watermark_text}\n"
            f"布局方式: {layout_tips}\n"
            f"特点: 文字可选择、可复制"
        )
    
    except Exception as e:
        logger.error(f"添加添加文字水印失败: {e}")
        raise e

@mcp.tool()
def encrypt_pdf_file(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None,
    allow_printing: bool = False,
    allow_modifying: bool = False,
    allow_copying: bool = False,
    allow_annotating: bool = False,
    allow_filling_forms: bool = False,
    mode: str = "basic",
    dpi: int = 144,
    image_format: str = "png",
    quality: int = 85,
) -> str:
    """加密PDF文件并设置权限。
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        user_password: 用户密码（打开密码）
        owner_password: 所有者密码（权限密码）
        allow_printing: 允许打印
        allow_modifying: 允许修改
        allow_copying: 允许复制
        allow_annotating: 允许注释
        allow_filling_forms: 允许填写表单
        mode: 加密模式，"basic"(标准加密) 或 "rasterize"(光栅化加密)
        dpi: 光栅化DPI（仅在rasterize模式下使用）
        image_format: 光栅化图片格式（仅在rasterize模式下使用）
        quality: 光栅化质量（仅在rasterize模式下使用）
    
    Returns:
        加密结果的详细信息
    """
    
    try:
        permissions = {
            "printing": allow_printing,
            "modifying": allow_modifying,
            "copying": allow_copying,
            "annotating": allow_annotating,
            "fillingForms": allow_filling_forms,
        }
        result = encrypt_pdf(
            input_path,
            output_path,
            user_password,
            owner_password,
            permissions,
            mode,
            dpi,
            image_format,
            quality,
        )
        perms_info = "\n".join([
            f"  - {k}: {'✓' if v else '✗'}"
            for k, v in result.permissions.items()
        ])
        return (
            f"✅ PDF加密成功\n"
            f"输出文件: {result.output_path}\n"
            f"页数: {result.page_count}\n"
            f"加密模式: {result.mode}\n"
            f"权限设置:\n{perms_info}"
        )
    
    except Exception as e:
        logger.error(f"加密失败: {e}")
        raise e


@mcp.tool()
def create_watermark_image(
    text: str,
    output_path: Optional[str] = None,
    font_size: int = 24,
    color: str = "#808080",
    background_color: str = "transparent",
) -> str:
    """创建文字水印图片。
    
    Args:
        text: 水印文字内容
        output_path: 输出图片路径（可选，默认在当前目录）
        font_size: 字体大小
        color: 文字颜色（十六进制或颜色名）
        background_color: 背景颜色（十六进制、颜色名或"transparent"）
    
    Returns:
        创建结果的详细信息
    """
    
    try:
        result = create_text_image_file(text, output_path, font_size, color, background_color)
        return (
            f"✅ 水印图片创建成功\n"
            f"输出文件: {result.output_path}\n"
            f"文字内容: {result.text}\n"
            f"尺寸: {result.width}x{result.height}\n"
            f"字体大小: {result.font_size}\n"
            f"文件大小: {result.file_stats.formatted_size}"
        )
    except Exception as e:
        raise e


def main():
    """启动MCP服务器。"""
    mcp.run()


if __name__ == "__main__":
    main()
