# PDF MCP Server

一个基于 FastMCP 的 PDF 操作服务器，提供 PDF 合并、拆分、转图片、加水印、加密等功能。

## 功能特性

- ✅ **PDF 合并** - 将多个 PDF 文件合并为一个
- ✅ **PDF 拆分** - 按页面或页面范围拆分 PDF
- ✅ **PDF 转图片** - 将 PDF 页面转换为 JPEG/PNG 图片
- ✅ **添加水印** - 支持文字和图片水印，可自定义位置、透明度、旋转角度
- ✅ **PDF 加密** - 支持密码保护和权限控制
- ✅ **创建水印图片** - 生成文字水印图片文件
- ✅ **中文支持** - 完整支持中文文字和字体
- ✅ **智能透明度处理** - 水印透明度在图片生成阶段处理，兼容所有 PyMuPDF 版本

## 安装

```bash
# 使用 uv 安装
uv pip install -e .

# 或使用 pip 安装
pip install -e .
```

## 配置 MCP

在 Kiro 的 MCP 配置文件中添加：

### Workspace 配置 (`.kiro/settings/mcp.json`)

```json
{
  "mcpServers": {
    "pdf-operations": {
      "command": "uv",
      "args": ["run", "pdf-mcp-server"],
      "disabled": false
    }
  }
}
```

### 或使用 uvx 运行

```json
{
  "mcpServers": {
    "pdf-operations": {
      "command": "uvx",
      "args": ["--from", ".", "pdf-mcp-server"],
      "disabled": false
    }
  }
}
```

## 可用工具（共 8 个）

### 1. merge_pdfs
合并多个 PDF 文件

**参数：**
- `input_paths` (list[str]) - 输入 PDF 文件路径列表
- `output_path` (str) - 输出 PDF 文件路径
- `title` (str, 可选) - PDF 标题

### 2. split_pdf_file
拆分 PDF 文件

**参数：**
- `input_path` (str) - 输入 PDF 文件路径
- `output_dir` (str) - 输出目录路径
- `split_mode` (str) - 拆分模式："pages" 或 "ranges"
- `ranges` (list[str], 可选) - 页面范围，如 ["1-3", "5", "7-10"]
- `prefix` (str, 可选) - 输出文件名前缀

### 3. convert_pdf_to_images
将 PDF 转换为图片

**参数：**
- `input_path` (str) - 输入 PDF 文件路径
- `output_dir` (str) - 输出目录路径
- `format` (str) - 图片格式："jpeg" 或 "png"
- `quality` (int) - JPEG 质量 (1-100)
- `dpi` (int) - 图片分辨率
- `pages` (str, 可选) - 页面范围，如 "1-3,5,7-10"
- `prefix` (str, 可选) - 输出文件名前缀

### 4. add_pdf_watermark
为 PDF 添加水印（图片方式，支持完整透明度）

**参数：**
- `input_path` (str) - 输入 PDF 文件路径
- `output_path` (str) - 输出 PDF 文件路径
- `watermark_text` (str, 可选) - 水印文字
- `watermark_image_path` (str, 可选) - 水印图片路径
- `opacity` (float) - 不透明度 (0.0-1.0)
- `font_size` (int) - 字体大小
- `position` (str) - 位置："center", "top-left", "top-right", "bottom-left", "bottom-right"
- `rotation` (float) - 旋转角度

**特点：** 文字转为图片后添加，透明度效果好，但文字不可选择

### 4.5. add_text_watermark_direct
直接在 PDF 上添加文字水印（文字可选择、可复制）

**参数：**
- `input_path` (str) - 输入 PDF 文件路径
- `output_path` (str) - 输出 PDF 文件路径
- `watermark_text` (str) - 水印文字内容
- `opacity` (float) - 不透明度 (0.0-1.0)，建议 0.1-0.3 实现若隐若现效果
- `font_size` (int) - 字体大小
- `position` (str) - 位置："center", "top-left", "top-right", "bottom-left", "bottom-right"
- `rotation` (float) - 旋转角度（支持任意角度 0-360），建议 45 度
- `color_r` (float) - 红色分量 (0.0-1.0)
- `color_g` (float) - 绿色分量 (0.0-1.0)
- `color_b` (float) - 蓝色分量 (0.0-1.0)
- `layout` (str) - 布局模式："single"(单个), "corners"(四角), "tile"(平铺)

**特点：** 
- 直接文字，可选择复制，文件更小
- 支持三种布局：单个位置、四角、整页平铺
- 通过颜色亮度调整实现若隐若现的透明效果

### 5. encrypt_pdf_file
加密 PDF 文件

**参数：**
- `input_path` (str) - 输入 PDF 文件路径
- `output_path` (str) - 输出 PDF 文件路径
- `user_password` (str) - 用户密码
- `owner_password` (str, 可选) - 所有者密码
- `allow_printing` (bool) - 允许打印
- `allow_modifying` (bool) - 允许修改
- `allow_copying` (bool) - 允许复制
- `allow_annotating` (bool) - 允许注释
- `allow_filling_forms` (bool) - 允许填写表单
- `mode` (str) - 加密模式："basic" 或 "rasterize"

### 6. create_watermark_image
创建水印图片

**参数：**
- `text` (str) - 水印文字
- `output_path` (str, 可选) - 输出路径
- `font_size` (int) - 字体大小
- `color` (str) - 文字颜色
- `background_color` (str) - 背景颜色

## 使用示例

配置完成后，在 Kiro 中可以直接调用这些工具：

```
请帮我合并 doc1.pdf 和 doc2.pdf 到 merged.pdf
```

```
把 document.pdf 的第1-5页拆分出来
```

```
给 report.pdf 添加"机密文件"水印
```

## 依赖项

- fastmcp - MCP 框架
- pikepdf - PDF 操作库
- pymupdf (fitz) - PDF 渲染库
- pillow - 图片处理库

## 开发

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 运行服务器
uv run pdf-mcp-server
```

## License

MIT
