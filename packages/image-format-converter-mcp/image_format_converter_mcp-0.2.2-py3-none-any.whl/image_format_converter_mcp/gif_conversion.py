#!/usr/bin/env python3
"""
GIF Creation Module - Convert Multiple Images to GIF Format
"""

from pathlib import Path
from PIL import Image, ImageColor
import gc
from typing import Tuple, List

# Import Supported Formats and Utility Functions From the Main Conversion Module
from .general_conversion import SUPPORTED_OUT_FORMATS, generate_unique_filename


def analyze_image_sizes(images: List[Image.Image]) -> dict:
    """
    分析图片尺寸，返回统计信息
    
    Args:
        images: PIL图片对象列表
        
    Returns:
        dict: 包含最小、最大、平均尺寸等统计信息
    """
    if not images:
        return {}
    
    sizes = [img.size for img in images]
    widths = [size[0] for size in sizes]
    heights = [size[1] for size in sizes]
    
    min_width, max_width = min(widths), max(widths)
    min_height, max_height = min(heights), max(heights)
    
    # 找到最小和最大面积的图片索引
    areas = [w * h for w, h in sizes]
    min_area_idx = areas.index(min(areas))
    max_area_idx = areas.index(max(areas))
    
    return {
        'sizes': sizes,
        'min_size': (min_width, min_height),
        'max_size': (max_width, max_height),
        'min_area_size': sizes[min_area_idx],
        'max_area_size': sizes[max_area_idx],
        'total_images': len(images),
        'uniform_size': len(set(sizes)) == 1
    }


def determine_target_size(size_stats: dict, size_strategy: str, target_width: int = None, target_height: int = None) -> Tuple[int, int]:
    """
    根据策略确定目标尺寸
    
    Args:
        size_stats: 尺寸统计信息
        size_strategy: 尺寸策略
        target_width: 自定义宽度
        target_height: 自定义高度
        
    Returns:
        Tuple[int, int]: 目标宽度和高度
    """
    if size_strategy == "min_size":
        return size_stats['min_area_size']
    elif size_strategy == "max_size":
        return size_stats['max_area_size']
    elif size_strategy == "custom":
        if target_width is None or target_height is None:
            raise ValueError("Custom size strategy requires both target_width and target_height")
        return (target_width, target_height)
    else:  # auto
        # 保持原有逻辑，返回第一张图片的尺寸
        return size_stats['sizes'][0] if size_stats['sizes'] else (800, 600)


def resize_image_with_mode(img: Image.Image, target_size: Tuple[int, int], resize_mode: str, alignment: str, background_color: str) -> Image.Image:
    """
    按指定模式调整图片尺寸
    
    Args:
        img: 源图片
        target_size: 目标尺寸 (width, height)
        resize_mode: 缩放模式 fit/fill/stretch
        alignment: 对齐方式 center/top_left/top_right/bottom_left/bottom_right
        background_color: 背景色
        
    Returns:
        Image.Image: 处理后的图片
    """
    target_width, target_height = target_size
    
    if resize_mode == "stretch":
        # 拉伸模式：直接调整到目标尺寸
        return img.resize(target_size, Image.LANCZOS)
    
    elif resize_mode == "fill":
        # 填充模式：等比缩放后裁剪，填满目标尺寸
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # 图片更宽，以高度为准缩放
            new_height = target_height
            new_width = int(img.width * target_height / img.height)
        else:
            # 图片更高，以宽度为准缩放
            new_width = target_width
            new_height = int(img.height * target_width / img.width)
        
        # 缩放图片
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 计算裁剪位置
        if alignment == "center":
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
        elif alignment == "top_left":
            left, top = 0, 0
        elif alignment == "top_right":
            left = new_width - target_width
            top = 0
        elif alignment == "bottom_left":
            left = 0
            top = new_height - target_height
        elif alignment == "bottom_right":
            left = new_width - target_width
            top = new_height - target_height
        else:  # 默认居中
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
        
        # 裁剪到目标尺寸
        return resized_img.crop((left, top, left + target_width, top + target_height))
    
    else:  # fit模式
        # 适应模式：等比缩放，保持完整图片，可能有背景填充
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # 图片更宽，以宽度为准缩放
            new_width = target_width
            new_height = int(img.height * target_width / img.width)
        else:
            # 图片更高，以高度为准缩放
            new_height = target_height
            new_width = int(img.width * target_height / img.height)
        
        # 缩放图片
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 如果已经是目标尺寸，直接返回
        if (new_width, new_height) == target_size:
            return resized_img
        
        # 创建目标尺寸的背景画布
        try:
            bg_color = ImageColor.getrgb(background_color)
        except ValueError:
            bg_color = (0, 0, 0)  # 默认黑色
        
        # 根据图片模式创建背景
        if resized_img.mode in ('RGBA', 'LA'):
            background = Image.new('RGBA', target_size, bg_color + (255,))
        else:
            background = Image.new('RGB', target_size, bg_color)
        
        # 计算粘贴位置
        if alignment == "center":
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
        elif alignment == "top_left":
            paste_x, paste_y = 0, 0
        elif alignment == "top_right":
            paste_x = target_width - new_width
            paste_y = 0
        elif alignment == "bottom_left":
            paste_x = 0
            paste_y = target_height - new_height
        elif alignment == "bottom_right":
            paste_x = target_width - new_width
            paste_y = target_height - new_height
        else:  # 默认居中
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
        
        # 粘贴图片到背景
        if resized_img.mode == 'RGBA':
            background.paste(resized_img, (paste_x, paste_y), resized_img)
        else:
            background.paste(resized_img, (paste_x, paste_y))
        
        return background


def calculate_easing_durations(num_frames: int, base_duration: int, easing: str, easing_strength: float = 1.0) -> list:
    """
    Calculate frame durations based on easing curve.
    
    Args:
        num_frames (int): Number of frames in the animation
        base_duration (int): Base duration in milliseconds
        easing (str): Easing type: "ease-in", "ease-out", "ease-in-out"
        easing_strength (float): Strength of easing effect (0.5 = subtle, 1.0 = normal, 2.0 = extreme)
        
    Returns:
        list: List of frame durations in milliseconds
    """
    if num_frames <= 1:
        return [base_duration]
    
    durations = []
    
    if easing == "ease-in":
        # Start Slow, End Fast
        for i in range(num_frames):
            # Quadratic Ease-in: t²
            progress = (i / (num_frames - 1)) ** 2
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    elif easing == "ease-out":
        # Start Fast, End Slow
        for i in range(num_frames):
            # Quadratic Ease-out: 1 - (1-t)²
            progress = i / (num_frames - 1)
            ease_progress = 1 - (1 - progress) ** 2
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * ease_progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    elif easing == "ease-in-out":
        # Start Slow, Middle Fast, End Slow
        for i in range(num_frames):
            progress = i / (num_frames - 1)
            if progress < 0.5:
                # First Half: Ease-in
                ease_progress = 2 * progress ** 2
            else:
                # Second Half: Ease-out
                ease_progress = 1 - 2 * (1 - progress) ** 2
            
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * ease_progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    else:
        # No Easing: Uniform Duration
        durations = [base_duration] * num_frames
    
    return durations


def convert_images_to_gif(
    input_files: list,
    file_name: str = None,
    output_dir: str = None,
    duration: int = 100,
    loop: int = 0,
    color_mode: str = "RGB",
    color_count: int = 256,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    ping_pong: bool = False,
    easing: str = "none",
    easing_strength: float = 1.0,
    # 新增尺寸控制参数
    size_strategy: str = "auto",
    resize_mode: str = "fit", 
    alignment: str = "center",
    target_width: int = None,
    target_height: int = None,
    background_color: str = "black"
) -> str:
    """
    Create a GIF from a list of image files.
    
    Args:
        input_files (list): List of image file paths
        file_name (str, optional): Custom name for the GIF file (without extension). If None, uses automatic naming.
        output_dir (str, optional): Output directory path. If None or invalid, uses first file's directory.
        duration (int): Duration per frame in milliseconds (default: 100)
        loop (int): Number of loops (0 = infinite, default: 0)
        color_mode (str): Color mode for GIF conversion. Options: "RGB" (default), "P" (Indexed), "L" (Grayscale)
        color_count (int): Number of colors for P and L modes. Range: 2-256. RGB mode ignores this parameter.
        brightness (float): Brightness multiplier (0.0 = black, 1.0 = normal, 2.0 = twice as bright, default: 1.0)
        contrast (float): Contrast multiplier (0.0 = no contrast, 1.0 = normal, 2.0 = high contrast, default: 1.0)
        saturation (float): Saturation multiplier (0.0 = grayscale, 1.0 = normal, 2.0 = oversaturated, default: 1.0)
        ping_pong (bool): Enable ping-pong loop (forward→backward→forward, default: False)
        easing (str): Easing curve for timing. Options: "none" (default), "ease-in", "ease-out", "ease-in-out"
        easing_strength (float): Strength of easing effect (0.5 = subtle, 1.0 = normal, 2.0 = extreme, default: 1.0)
        size_strategy (str): Size unification strategy. Options: "auto" (default), "min_size", "max_size", "custom"
        resize_mode (str): Resize mode. Options: "fit" (default), "fill", "stretch"
        alignment (str): Alignment for fit/fill modes. Options: "center" (default), "top_left", "top_right", "bottom_left", "bottom_right"
        target_width (int, optional): Target width for custom size strategy
        target_height (int, optional): Target height for custom size strategy  
        background_color (str): Background color for fit mode (default: "black")
        
    Returns:
        str: Path to the created GIF file
    """
    # Validate Input Files
    if not input_files or not isinstance(input_files, list):
        raise ValueError("input_files must be a non-empty list of file paths")
    
    # Convert to Path objects and validate
    image_paths = []
    for file_path in input_files:
        path_obj = Path(file_path)
        if not path_obj.exists():
            print(f"(WARNING) File does not exist: {file_path}")
            continue
        if not path_obj.is_file():
            print(f"(WARNING) Not a file: {file_path}")
            continue
        image_paths.append(path_obj)
    
    if not image_paths:
        raise ValueError("No valid image files provided")
    
    # Set Output Directory with Fallback Logic
    if output_dir is None:
        output_dir_path = image_paths[0].parent
    else:
        try:
            output_dir_path = Path(output_dir)
            # Try to create directory if it doesn't exist
            if not output_dir_path.exists():
                output_dir_path.mkdir(parents=True, exist_ok=True)
            # Validate it's actually a directory and accessible
            if not output_dir_path.is_dir():
                print(f"(WARNING) Invalid output_dir '{output_dir}', using first file's directory")
                output_dir_path = image_paths[0].parent
            else:
                # Test if we can actually write to this directory
                try:
                    test_file = output_dir_path / ".test_write_access"
                    test_file.touch()
                    test_file.unlink()
                except Exception:
                    print(f"(WARNING) Cannot write to output_dir '{output_dir}', using first file's directory")
                    output_dir_path = image_paths[0].parent
        except Exception as e:
            print(f"(WARNING) Invalid output_dir '{output_dir}', using first file's directory")
            output_dir_path = image_paths[0].parent
    
    print(f"OUTPUT: Output directory: {output_dir_path}")
    
    # Validate Color Mode
    valid_color_modes = ["RGB", "P", "L"]
    if color_mode.upper() not in valid_color_modes:
        raise ValueError(f"Invalid color_mode: {color_mode}. Must be one of: {', '.join(valid_color_modes)}")
    
    color_mode = color_mode.upper()  # Normalize to Uppercase
    
    # Validate Size Strategy Parameter
    valid_size_strategies = ["auto", "min_size", "max_size", "custom"]
    if size_strategy.lower() not in valid_size_strategies:
        raise ValueError(f"Invalid size_strategy: {size_strategy}. Must be one of: {', '.join(valid_size_strategies)}")
    
    size_strategy = size_strategy.lower()  # Normalize to Lowercase
    
    # Validate Resize Mode Parameter
    valid_resize_modes = ["fit", "fill", "stretch"]
    if resize_mode.lower() not in valid_resize_modes:
        raise ValueError(f"Invalid resize_mode: {resize_mode}. Must be one of: {', '.join(valid_resize_modes)}")
    
    resize_mode = resize_mode.lower()  # Normalize to Lowercase
    
    # Validate Alignment Parameter
    valid_alignments = ["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    if alignment.lower() not in valid_alignments:
        raise ValueError(f"Invalid alignment: {alignment}. Must be one of: {', '.join(valid_alignments)}")
    
    alignment = alignment.lower()  # Normalize to Lowercase
    
    # Validate Custom Size Parameters
    if size_strategy == "custom":
        if target_width is None or target_height is None:
            raise ValueError("Custom size strategy requires both target_width and target_height")
        if target_width <= 0 or target_height <= 0:
            raise ValueError("target_width and target_height must be positive integers")
        if target_width > 8000 or target_height > 8000:
            raise ValueError("target_width and target_height must be <= 8000")
    
    # Validate Easing Parameter
    valid_easing = ["none", "ease-in", "ease-out", "ease-in-out"]
    if easing.lower() not in valid_easing:
        raise ValueError(f"Invalid easing: {easing}. Must be one of: {', '.join(valid_easing)}")
    
    easing = easing.lower()  # Normalize to Lowercase
    
    # Validate and Auto-Correct Duration Parameter
    original_duration = duration
    if duration < 1 or duration > 10000:
        duration = 100  # Default Value
        print(f"(WARNING) Invalid duration {original_duration}ms. Setting to default {duration}ms and continuing.")
    
    # Validate and Auto-Correct Loop Parameter
    original_loop = loop
    if loop < 0:
        loop = 0  # Default Value (Infinite)
        print(f"(WARNING) Invalid loop {original_loop}. Setting to default {loop} (infinite) and continuing.")
    
    # Validate and Auto-Correct file_name Parameter
    original_file_name = file_name
    if file_name is not None and (not isinstance(file_name, str) or file_name.strip() == ""):
        file_name = None  # Default Value (Automatic Naming)
        print(f"(WARNING) Invalid file_name '{original_file_name}'. Using automatic naming instead.")
    
    # Validate and Auto-Correct Easing Strength Parameter
    original_easing_strength = easing_strength
    if easing_strength < 0.1 or easing_strength > 5.0:
        easing_strength = 1.0  # Default Value
        print(f"(WARNING) Invalid easing_strength {original_easing_strength}. Setting to default {easing_strength}x and continuing.")
    
    # Validate and Auto-Correct Effect Parameters
    original_brightness = brightness
    if brightness < 0.0 or brightness > 5.0:
        brightness = 1.0  # Default Value
        print(f"(WARNING) Invalid brightness {original_brightness}. Setting to default {brightness}x and continuing.")
    
    original_contrast = contrast
    if contrast < 0.0 or contrast > 5.0:
        contrast = 1.0  # Default value
        print(f"(WARNING) Invalid contrast {original_contrast}. Setting to default {contrast}x and continuing.")
    
    original_saturation = saturation
    if saturation < 0.0 or saturation > 5.0:
        saturation = 1.0  # Default Value
        print(f"(WARNING) Invalid saturation {original_saturation}. Setting to default {saturation}x and continuing.")
    
    # Show Effect Settings if Any Are Modified
    effects_applied = []
    if brightness != 1.0:
        effects_applied.append(f"Brightness: {brightness}x")
    if contrast != 1.0:
        effects_applied.append(f"Contrast: {contrast}x")
    if saturation != 1.0:
        effects_applied.append(f"Saturation: {saturation}x")
    
    if effects_applied:
        print(f"EFFECTS: {', '.join(effects_applied)}")
    
    # Show Animation Settings if Any Are Modified
    animation_settings = []
    if ping_pong:
        animation_settings.append("Ping-pong loop")
    if easing != "none":
        strength_text = f" (strength: {easing_strength}x)"
        animation_settings.append(f"Easing: {easing}{strength_text}")
    
    if animation_settings:
        print(f"ANIMATION: {', '.join(animation_settings)}")
    
    # Smart Color Count Handling With Fallback Logic
    if color_mode == "RGB":
        # RGB Mode Ignores Color_count - Always Use Full Color
        print(f"COLOR: Color mode: {color_mode} (ignoring color_count parameter)")
    else:
        # P and L Modes Validate and Use Color_count
        original_color_count = color_count
        if color_count < 2 or color_count > 256:
            color_count = 256  # Default Value
            print(f"(WARNING) Invalid color_count {original_color_count}. Setting to default {color_count} and continuing.")
        
        print(f"COLOR: Color mode: {color_mode}, Color count: {color_count}")
    
    # Generate Output Path Based on file_name or Automatic Naming
    if file_name is not None:
        # Use file_name with .gif Extension (check if extension already exists)
        file_name_clean = Path(file_name).stem  # Remove any existing extension
        base_output_path = output_dir_path / f"{file_name_clean}.gif"
        output_path = generate_unique_filename(base_output_path)
        print(f"INFO: Custom name output path: {output_path}")
    else:
        # Use Automatic Naming (Animation.gif, Animation 01.gif, etc.)
        base_output_path = output_dir_path / "Animation.gif"
        output_path = generate_unique_filename(base_output_path)
        print(f"INFO: Auto-generated output path: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get All Supported Image Extensions From the Main Conversion Module
    supported_extensions = set()
    for format_exts in SUPPORTED_OUT_FORMATS.values():
        supported_extensions.update(ext.lower() for ext in format_exts)
    
    # Filter and validate image files
    image_files = []
    skipped_files = []
    
    for file_path in image_paths:
        file_ext = file_path.suffix.lower()
        
        # Skip if Not an Image File
        if file_ext not in supported_extensions:
            skipped_files.append(f"Unsupported format: {file_path.name}")
            continue
        
        # Skip Existing GIF Files
        if file_ext == '.gif':
            skipped_files.append(f"GIF file: {file_path.name}")
            continue
        
        image_files.append(file_path)
    
    if not image_files:
        raise RuntimeError("No supported images found in input list")
    
    print(f"PROCESSING: Found {len(image_files)} images to combine into GIF")
    if skipped_files:
        print(f"SKIPPED: {len(skipped_files)} files")
        for skipped in skipped_files:
            print(f"   - {skipped}")
    
    # Load All Images
    images = []
    failed_images = []
    
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                # Convert to Specified Color Mode
                if img.mode != color_mode:
                    if color_mode == "RGB":
                        # For RGB, Convert RGBA/LA to RGB, Others as-is
                        if img.mode in ('RGBA', 'LA'):
                            img = img.convert('RGB')
                        elif img.mode in ('P', 'L'):
                            img = img.convert('RGB')
                    elif color_mode == "L":
                        # For Grayscale, Convert Any Mode to L
                        img = img.convert('L')
                    elif color_mode == "P":
                        # For Indexed, Convert to P
                        img = img.convert('P', palette=Image.ADAPTIVE)
                
                # Apply Brightness, Contrast, and Saturation Effects
                if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
                    # Convert to RGB for Color Processing
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    
                    # Apply Brightness
                    if brightness != 1.0:
                        img = img.point(lambda p: int(p * brightness))
                    
                    # Apply Contrast
                    if contrast != 1.0:
                        img = img.point(lambda p: int(128 + (p - 128) * contrast))
                    
                    # Apply Saturation
                    if saturation != 1.0:
                        hsv_img = img.convert('HSV')
                        h, s, v = hsv_img.split()
                        s = s.point(lambda p: int(p * saturation))
                        img = Image.merge('HSV', (h, s, v)).convert('RGB')
                
                # Apply Color Count Reduction for P and L Modes
                if color_mode == "L" and color_count < 256:
                    img = img.quantize(colors=color_count)
                elif color_mode == "P" and color_count < 256:
                    img = img.quantize(colors=color_count)
                
                images.append(img.copy())
                print(f"SUCCESS: Loaded: {img_path.name} (converted to {color_mode})")
        except Exception as e:
            print(f"(WARNING) Could not load {img_path.name}: {e}")
            failed_images.append(str(img_path))
    
    if not images:
        raise RuntimeError("No valid images could be loaded")
    
    if failed_images:
        print(f"(WARNING) Failed to load {len(failed_images)} images")
    
    # 处理尺寸统一
    if size_strategy != "auto":
        print(f"SIZE: Analyzing image sizes for {size_strategy} strategy...")
        
        # 分析图片尺寸
        size_stats = analyze_image_sizes(images)
        
        if size_stats['uniform_size']:
            print(f"SIZE: All images already have uniform size: {size_stats['sizes'][0]}")
        else:
            print(f"SIZE: Found {size_stats['total_images']} images with different sizes")
            print(f"SIZE: Size range: {size_stats['min_size']} to {size_stats['max_size']}")
            
            # 确定目标尺寸
            try:
                target_size = determine_target_size(size_stats, size_strategy, target_width, target_height)
                print(f"SIZE: Target size: {target_size[0]}x{target_size[1]} (strategy: {size_strategy})")
                print(f"SIZE: Resize mode: {resize_mode}, Alignment: {alignment}")
                
                # 调整所有图片到目标尺寸
                resized_images = []
                for i, img in enumerate(images):
                    if img.size == target_size:
                        resized_images.append(img)
                    else:
                        resized_img = resize_image_with_mode(
                            img, target_size, resize_mode, alignment, background_color
                        )
                        resized_images.append(resized_img)
                
                images = resized_images
                print(f"SUCCESS: All images resized to {target_size[0]}x{target_size[1]}")
                
            except Exception as e:
                print(f"(WARNING) Size processing failed: {e}, continuing with original sizes")
    else:
        print(f"SIZE: Using auto strategy - keeping original image sizes")
    
    # Save as GIF
    try:
        # Create a Copy of Images List to Avoid Modifying the Original
        gif_images = images.copy()
        
        # Apply Ping-pong Effect if Requested
        if ping_pong and len(gif_images) > 1:
            # Create Ping-pong Sequence: Forward → Backward → Forward
            # Example: [1,2,3,4] Becomes [1,2,3,4,3,2,1,2,3,4,3,2,1...]
            forward_frames = gif_images
            backward_frames = gif_images[-2:0:-1]  # Reverse, excluding first and last
            
            # Combine: Forward + Backward + Forward (for Smooth Loop)
            gif_images = forward_frames + backward_frames + forward_frames
            print(f"PROCESSING: Ping-pong: {len(images)} frames → {len(gif_images)} frames")
        
        # Calculate Easing-Based Frame Durations if Requested
        frame_durations = []
        if easing != "none" and len(gif_images) > 1:
            frame_durations = calculate_easing_durations(len(gif_images), duration, easing, easing_strength)
            print(f"TIMING: Easing: {easing} timing applied")
        else:
            # Use Uniform Duration for All Frames
            frame_durations = [duration] * len(gif_images)
        
        # Use Simple PIL Method for All Loop Scenarios
        save_kwargs = {
            'format': 'GIF',
            'save_all': True,
            'append_images': gif_images[1:],
            'duration': frame_durations,
            'loop': loop,
            'optimize': True
        }
        
        images[0].save(output_path, **save_kwargs)
        
        print(f"SUCCESS: GIF created successfully: {output_path}")
        print(f"SUMMARY: Frames: {len(gif_images)}, Duration: {duration}ms, Loop: {'infinite' if loop == 0 else loop}")
        return str(output_path)
    
    except Exception as e:
        raise RuntimeError(f"Failed to create GIF: {e}")
    finally:
        # Simple Memory Cleanup
        gc.collect()
