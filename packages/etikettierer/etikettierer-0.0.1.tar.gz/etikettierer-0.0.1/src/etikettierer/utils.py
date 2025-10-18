from typing import Tuple
from PIL import Image

def scale_and_center(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Scale `img` to fit inside (target_width, target_height) preserving aspect ratio,
    and return a new Image of exact target size with the scaled image centered on white background.
    """
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * img_ratio)

    resized = img.resize((new_width, new_height), Image.LANCZOS)
    result = Image.new("RGB", (target_width, target_height), "white")
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    result.paste(resized, (x, y))
    return result
