from io import BytesIO
from PIL import Image
from typing import Union, BinaryIO, Tuple
import base64
import requests
import os
import logging

logger = logging.getLogger(__name__)

def get_image_data(image: Union[str, BinaryIO]) -> bytes:
    """
    从各种输入类型获取图像数据 (统一的图像数据获取函数)
    
    Args:
        image: 图像路径、URL或二进制数据
        
    Returns:
        bytes: 原始图像数据
    """
    try:
        if isinstance(image, str):
            if image.startswith(('http://', 'https://')):
                # 从URL下载
                response = requests.get(image)
                response.raise_for_status()
                return response.content
            elif image.startswith('data:'):
                # Data URL格式 (如 data:image/png;base64,...)
                if 'base64,' in image:
                    base64_data = image.split('base64,')[1]
                    return base64.b64decode(base64_data)
                else:
                    raise ValueError("Unsupported data URL format")
            elif len(image) > 100 and not os.path.exists(image):
                # 纯base64字符串 (没有data URL前缀)
                try:
                    return base64.b64decode(image)
                except Exception:
                    # 如果base64解码失败，则当作文件路径处理
                    pass
            
            # 本地文件路径
            with open(image, 'rb') as f:
                return f.read()
        elif hasattr(image, 'read'):
            # 文件类对象
            data = image.read()
            if isinstance(data, bytes):
                return data
            else:
                raise ValueError("File-like object did not return bytes")
        else:
            # 假设是bytes
            return bytes(image) if not isinstance(image, bytes) else image
    except Exception as e:
        logger.error(f"Error getting image data: {e}")
        raise

def compress_image(image_data: Union[bytes, BytesIO], max_size: int = 1024) -> bytes:
    """压缩图片以减小大小

    Args:
        image_data: 图片数据，可以是 bytes 或 BytesIO
        max_size: 最大尺寸（像素）

    Returns:
        bytes: 压缩后的图片数据
    """
    try:
        # Ensure max_size is int (type safety)
        max_size = int(max_size)

        # 如果输入是 bytes，转换为 BytesIO
        if isinstance(image_data, bytes):
            image_data = BytesIO(image_data)

        img = Image.open(image_data)

        # 转换为 RGB 模式（如果需要）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 计算新尺寸，保持宽高比
        ratio = max_size / max(img.size)
        if ratio < 1:
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 保存压缩后的图片
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        raise

def encode_image_to_base64(image_data: bytes) -> str:
    """将图片数据编码为 base64 字符串
    
    Args:
        image_data: 图片二进制数据
        
    Returns:
        str: base64 编码的字符串
    """
    try:
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        raise 

def prepare_image_base64(image: Union[str, BinaryIO], compress: bool = False, max_size: int = 1024) -> str:
    """
    将图像准备为base64格式 (统一的base64编码函数)
    
    Args:
        image: 图像输入
        compress: 是否压缩图像
        max_size: 压缩时的最大尺寸
        
    Returns:
        str: Base64编码的图像字符串
    """
    try:
        image_data = get_image_data(image)
        
        if compress:
            image_data = compress_image(image_data, max_size)
        
        return encode_image_to_base64(image_data)
    except Exception as e:
        logger.error(f"Error preparing image base64: {e}")
        raise

def prepare_image_data_url(image: Union[str, BinaryIO], compress: bool = False, max_size: int = 1024) -> str:
    """
    将图像准备为data URL格式 (统一的data URL生成函数)
    
    Args:
        image: 图像输入
        compress: 是否压缩图像
        max_size: 压缩时的最大尺寸
        
    Returns:
        str: data URL格式的图像字符串
    """
    try:
        base64_data = prepare_image_base64(image, compress, max_size)
        mime_type = get_image_mime_type(image)
        return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        logger.error(f"Error preparing image data URL: {e}")
        raise

def get_image_mime_type(image: Union[str, BinaryIO]) -> str:
    """
    获取图像的MIME类型 (统一的MIME类型检测函数)
    
    Args:
        image: 图像输入
        
    Returns:
        str: MIME类型
    """
    try:
        if isinstance(image, str):
            # 文件路径 - 检查扩展名
            ext = os.path.splitext(image)[1].lower()
            mime_mapping = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff'
            }
            return mime_mapping.get(ext, 'image/jpeg')
        else:
            # 尝试从图像数据检测
            image_data = get_image_data(image)
            img = Image.open(BytesIO(image_data))
            format_mapping = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'GIF': 'image/gif',
                'WEBP': 'image/webp',
                'BMP': 'image/bmp',
                'TIFF': 'image/tiff'
            }
            return format_mapping.get(img.format, 'image/jpeg')
    except Exception:
        # 默认回退
        return 'image/jpeg'

def get_image_dimensions(image: Union[str, BinaryIO]) -> Tuple[int, int]:
    """
    获取图像尺寸 (统一的尺寸获取函数)
    
    Args:
        image: 图像输入
        
    Returns:
        tuple: (width, height)
    """
    try:
        image_data = get_image_data(image)
        img = Image.open(BytesIO(image_data))
        return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {e}")
        return (0, 0)

def validate_image_format(image: Union[str, BinaryIO], supported_formats: list = None) -> bool:
    """
    验证图像格式是否受支持 (统一的格式验证函数)
    
    Args:
        image: 图像输入
        supported_formats: 支持的格式列表，默认为常见格式
        
    Returns:
        bool: 如果支持则为True
    """
    if supported_formats is None:
        supported_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
    
    try:
        if isinstance(image, str):
            ext = os.path.splitext(image)[1].lower().lstrip('.')
            return ext in supported_formats
        else:
            # 检查实际图像格式
            image_data = get_image_data(image)
            img = Image.open(BytesIO(image_data))
            return img.format.lower() in [fmt.upper() for fmt in supported_formats]
    except Exception as e:
        logger.warning(f"Could not validate image format: {e}")
        return True  # 默认允许

def parse_coordinates_from_text(text: str) -> list:
    """
    从文本响应中解析对象坐标 (统一的解析逻辑)
    
    Args:
        text: 包含坐标信息的文本响应
        
    Returns:
        list: 解析出的对象列表，每个对象包含label, confidence, coordinates, description
    """
    objects = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if line and ':' in line and ('x=' in line or 'width=' in line):
            try:
                # 提取对象名称和详细信息
                parts = line.split(':', 1)
                if len(parts) == 2:
                    object_name = parts[0].strip()
                    details = parts[1].strip()
                    
                    # 使用类似正则表达式的解析提取坐标
                    coords = {}
                    for param in ['x', 'y', 'width', 'height']:
                        param_pattern = f"{param}="
                        if param_pattern in details:
                            start_idx = details.find(param_pattern) + len(param_pattern)
                            end_idx = details.find('%', start_idx)
                            if end_idx > start_idx:
                                try:
                                    value = float(details[start_idx:end_idx])
                                    coords[param] = value
                                except ValueError:
                                    continue
                    
                    # 提取描述（坐标之后）
                    desc_start = details.find(' - ')
                    description = details[desc_start + 3:] if desc_start != -1 else details
                    
                    objects.append({
                        "label": object_name,
                        "confidence": 1.0,
                        "coordinates": coords,
                        "description": description
                    })
                    
            except Exception:
                # 对于不匹配预期格式的对象的回退
                objects.append({
                    "label": line,
                    "confidence": 1.0,
                    "coordinates": {},
                    "description": line
                })
    
    return objects

def parse_center_coordinates_from_text(text: str) -> tuple:
    """
    从结构化文本响应中解析中心坐标 (统一的解析逻辑)
    
    Args:
        text: 包含FOUND/CENTER/DESCRIPTION格式的文本响应
        
    Returns:
        tuple: (found: bool, center_coords: List[int] | None, description: str)
    """
    found = False
    center_coords = None
    description = ""
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('FOUND:'):
            found = 'YES' in line.upper()
        elif line.startswith('CENTER:') and found:
            # 提取中心坐标 [x, y]
            coords_text = line.replace('CENTER:', '').strip()
            try:
                # 移除括号并分割
                coords_text = coords_text.replace('[', '').replace(']', '')
                if ',' in coords_text:
                    x_str, y_str = coords_text.split(',')
                    x = int(float(x_str.strip()))
                    y = int(float(y_str.strip()))
                    center_coords = [x, y]
            except (ValueError, IndexError):
                pass
        elif line.startswith('DESCRIPTION:'):
            description = line.replace('DESCRIPTION:', '').strip()
    
    return found, center_coords, description