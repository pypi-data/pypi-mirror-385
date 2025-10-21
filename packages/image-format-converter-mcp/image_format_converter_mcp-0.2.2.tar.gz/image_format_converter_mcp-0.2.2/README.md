# 图片转换器 MCP

一个提供全面图片转换和处理工具的模型上下文协议（MCP）服务器。

## 功能特性

- **通用图片转换**：在各种图片格式之间转换（JPEG、PNG、BMP、TIFF、ICO、WEBP、HEIC/HEIF、AVIF、GIF）
- **批量处理**：将整个文件夹的图片转换为目标格式
- **GIF 创建**：将多张图片转换为自定义选项的动画 GIF
- **PDF 生成**：将多张图片合并为单个 PDF 文档
- **智能命名**：自动文件命名，防止重复
- **格式检测**：自动检测输入图片格式
- **质量控制**：优化 ICO 文件的多分辨率

## 安装

### 从 PyPI 安装
```bash
pip install image-format-converter-mcp
```

### 开发安装
```bash
git clone https://github.com/beta/image-format-converter-mcp
cd image-format-converter-mcp
pip install -e .
```

## 配置

无需特殊配置。服务器使用默认设置运行。

### MCP 配置示例

```json
{
  "mcpServers": {
    "Image Convertor MCP": {
      "command": "uvx",
      "args": ["image-format-converter-mcp"],
      "env": {}
    }
  }
}
```

## 可用工具

### 通用图片转换
- `auto_convert_image(input_path:str, target_format:str, output_dir:str=None, file_name:str=None)` - 将单张图片转换为目标格式
- `auto_convert_folder(input_folder:str, target_format:str, output_dir:str=None)` - 将文件夹中的所有图片转换为目标格式

### GIF 创建
- `convert_images_to_gif(input_folder:str, custom_name:str=None, duration:int=100, loop:int=0, color_mode:str="RGB", color_count:int=256, brightness:float=1.0, contrast:float=1.0, saturation:float=1.0, ping_pong:bool=False, easing:str="none", easing_strength:float=1.0)` - 将多张图片转换为动画 GIF

### PDF 生成
- `convert_images_to_pdf(input_folder:str, output_dir:str=None, output_name:str=None, sort_order:str="alphabetical", page_size:str="A4", dpi:int=300, fit_to_page:bool=True, center_image:bool=True, background_color:str="white")` - 将多张图片合并为 PDF

## 支持的格式

### 输入格式
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tif, .tiff)
- ICO (.ico)
- WEBP (.webp)
- HEIC/HEIF (.heic, .heif)
- AVIF (.avif)
- GIF (.gif)

### 输出格式
- JPEG (.jpg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tif)
- ICO (.ico)
- WEBP (.webp)
- HEIC/HEIF (.heic)
- AVIF (.avif)
- GIF (.gif)
- PDF (.pdf)

## 使用方法

### 命令行
```bash
image-format-converter-mcp
```

### 作为 MCP 服务器
服务器通过标准输入输出运行，可以与任何 MCP 兼容的客户端集成。

## 系统要求

- Python 3.9+
- Pillow (PIL) 用于图片处理
- pillow-heif 用于 HEIC/HEIF 支持
- reportlab 用于 PDF 生成
- 网络连接（用于某些格式转换）

## 更新日志

### 版本 0.1.7
- **错误修复**：修复了 MCP 服务器在 Windows 操作系统上的兼容性问题

### 版本 0.1.6
- **错误修复**：修复了 MCP 服务器完成问题，工具不再显示为"卡住"的处理状态
- **错误修复**：修复了 MCP 工具执行中的参数错误，该错误阻止了工具运行
- **性能优化**：通过垃圾回收优化内存使用和资源管理
- **性能优化**：为具有可选参数的 MCP 工具添加了全面的警告捕获和报告

### 版本 0.1.1
- 具有核心图片转换功能的初始版本

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。