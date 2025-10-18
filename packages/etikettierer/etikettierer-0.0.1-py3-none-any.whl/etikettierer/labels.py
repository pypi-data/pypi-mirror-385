import os
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import qrcode
import importlib.resources as resources

from .utils import scale_and_center

# Public error correction map (same keys as original GUI)
ERROR_CORRECTION_MAP = {
    "L (7%) - High Capacity": qrcode.constants.ERROR_CORRECT_L,
    "M (15%) - Standard": qrcode.constants.ERROR_CORRECT_M,
    "Q (25%) - Higher Security": qrcode.constants.ERROR_CORRECT_Q,
    "H (30%) - Very Robust": qrcode.constants.ERROR_CORRECT_H,
}

def estimate_version(text: str) -> int:
    """
    Estimate QR code version based on text length (simple heuristic).
    """
    length = len(text or "")
    if length <= 25:
        return 1
    elif length <= 50:
        return 2
    elif length <= 100:
        return 3
    elif length <= 200:
        return 5
    elif length <= 500:
        return 10
    else:
        return 15

def generate_qr_code(data: str, error_level: int, version: Optional[int] = None) -> Image.Image:
    """
    Generate a QR code PIL image for `data`.
    :param data: string to encode
    :param error_level: qrcode.ERROR_CORRECT_*
    :param version: optional version override
    :return: PIL.Image (RGB)
    """
    if version is None:
        version = estimate_version(data)

    qr = qrcode.QRCode(
        version=version,
        error_correction=error_level,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def _draw_sample_text(draw: ImageDraw.ImageDraw, sample_name: str, qr_eln_area: int, sample_text_area: int, fixed_width: int) -> Optional[ImageFont.ImageFont]:
    """
    Pick a font size that fits `sample_name` into the center area and draw it.
    Returns the font used, or None if a truetype font couldn't be loaded.
    """
    try:
        max_font_size = 40
        for font_size in range(max_font_size, 6, -1):
            font = ImageFont.truetype("arial.ttf", font_size)
            bbox = font.getbbox(sample_name)
            text_width = bbox[2] - bbox[0]
            if text_width <= fixed_width - 20:
                break
    except OSError:
        # Could not load arial.ttf; caller will handle fallback (return None)
        return None

    sample_text_center_y = qr_eln_area + sample_text_area // 2
    text_height = bbox[3] - bbox[1]
    text_x = (fixed_width - text_width) // 2
    text_y = sample_text_center_y - text_height // 2
    draw.text((text_x, text_y), sample_name, font=font, fill="black")
    return font

def _draw_rotated_label_text(label_img: Image.Image, text: str, top_y: int, box_height: int) -> None:
    """
    Draw vertical/rotated label text on the left edge.
    """
    try:
        label_font = ImageFont.truetype("arial.ttf", 32)
    except OSError:
        label_font = ImageFont.load_default()

    padding = 10
    bbox = label_font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_img = Image.new(
        "RGBA", (text_w + 2 * padding, text_h + 2 * padding), (255, 255, 255, 0)
    )
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((padding, padding), text, font=label_font, fill="black")

    rotated = text_img.rotate(90, expand=True)
    x = 10
    y = top_y + (box_height - rotated.height) // 2
    label_img.paste(rotated, (x, y), rotated)

# def create_label_image(eln_link: str, sample_name: str, error_level: int, logo_path: Optional[str] = None) -> Optional[Image.Image]:
#     """
#     Create the label image composed of:
#       - ELN QR at top
#       - sample name centered text in the middle stripe
#       - sample QR at bottom
#     Returns PIL.Image (RGB) or None if some unrecoverable error occurred (e.g. fonts missing and text can't be rendered).
#     """
#     # Constants
#     fixed_width = 762
#     fixed_height = 1000

#     # generate qrs
#     qr_eln_img = generate_qr_code(eln_link, error_level, estimate_version(eln_link))
#     qr_sample_img = generate_qr_code(sample_name, error_level, estimate_version(sample_name))

#     # try load logo if provided
#     logo = None
#     if not logo_path:
#         try:
#             from importlib import resources
#             with resources.open_binary("etikettierer", "ipf-logo.ico") as f:
#                 logo = Image.open(f).convert("RGBA")
#                 logo_size = 100
#                 logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
#         except Exception:
#             logo = None

#     if logo_path:
#         try:
#             logo = Image.open(logo_path).convert("RGBA")
#             logo_size = 100
#             logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
#         except Exception:
#             logo = None

#     # layout areas
#     qr_eln_area = int(fixed_height * 0.45)
#     sample_text_area = int(fixed_height * 0.12)
#     qr_sample_area = fixed_height - qr_eln_area - sample_text_area

#     qr_eln_resized = scale_and_center(qr_eln_img, fixed_width, qr_eln_area)

#     if logo:
#         qr_w, qr_h = qr_eln_resized.size
#         logo_w, logo_h = logo.size
#         position = (qr_w - logo_w - 20, 20)
#         qr_eln_resized.paste(logo, position, mask=logo)

#     qr_sample_resized = scale_and_center(qr_sample_img, fixed_width, qr_sample_area)

#     label_img = Image.new("RGB", (fixed_width, fixed_height), "white")
#     label_img.paste(qr_eln_resized, (0, 0))
#     label_img.paste(qr_sample_resized, (0, qr_eln_area + sample_text_area))

#     draw = ImageDraw.Draw(label_img)
#     draw.line([(0, qr_eln_area), (fixed_width, qr_eln_area)], fill="black", width=3)
#     draw.line([(0, qr_eln_area + sample_text_area), (fixed_width, qr_eln_area + sample_text_area)], fill="black", width=3)
#     draw.rectangle([(0, 0), (fixed_width - 1, fixed_height - 1)], outline="black", width=3)

#     font = _draw_sample_text(draw, sample_name, qr_eln_area, sample_text_area, fixed_width)
#     if font is None:
#         # If truetype fonts are missing, fallback to default: draw with load_default() but fit may look different.
#         try:
#             default_font = ImageFont.load_default()
#             # draw without fit attempt
#             sample_text_center_y = qr_eln_area + sample_text_area // 2
#             bbox = default_font.getbbox(sample_name)
#             text_width = bbox[2] - bbox[0]
#             text_height = bbox[3] - bbox[1]
#             text_x = (fixed_width - text_width) // 2
#             text_y = sample_text_center_y - text_height // 2
#             draw.text((text_x, text_y), sample_name, font=default_font, fill="black")
#         except Exception:
#             return None

#     _draw_rotated_label_text(label_img, "ELN link", 0, qr_eln_area)
#     _draw_rotated_label_text(label_img, "sample name", qr_eln_area + sample_text_area, qr_sample_area)

#     return label_img

def create_label_image(eln_link: str, sample_name: str, error_level: int) -> Optional[Image.Image]:
    """
    Create the label image composed of:
      - ELN QR at top (with IPF logo overlay)
      - sample name text in the middle stripe
      - sample QR at bottom
    Returns a PIL Image (RGB) or None if an unrecoverable error occurs.
    """
    fixed_width, fixed_height = 762, 1000

    # Generate QR codes
    qr_eln_img = generate_qr_code(eln_link, error_level, estimate_version(eln_link))
    qr_sample_img = generate_qr_code(sample_name, error_level, estimate_version(sample_name))

    # Load logo from within the package
    logo = None
    try:
        with resources.path("etikettierer", "ipf-logo.ico") as p:
            logo = Image.open(p).convert("RGBA")
            logo_size = 100
            logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
    except Exception as e:
        print(f"Could not load logo: {e}")
        logo = None

    # Layout areas
    qr_eln_area = int(fixed_height * 0.45)
    sample_text_area = int(fixed_height * 0.12)
    qr_sample_area = fixed_height - qr_eln_area - sample_text_area

    qr_eln_resized = scale_and_center(qr_eln_img, fixed_width, qr_eln_area)

    # Paste logo on top-right of ELN QR
    if logo:
        qr_w, qr_h = qr_eln_resized.size
        logo_w, logo_h = logo.size
        position = (qr_w - logo_w - 20, 20)
        qr_eln_resized.paste(logo, position, mask=logo)

    qr_sample_resized = scale_and_center(qr_sample_img, fixed_width, qr_sample_area)

    # Create final label layout
    label_img = Image.new("RGB", (fixed_width, fixed_height), "white")
    label_img.paste(qr_eln_resized, (0, 0))
    label_img.paste(qr_sample_resized, (0, qr_eln_area + sample_text_area))

    draw = ImageDraw.Draw(label_img)
    draw.line([(0, qr_eln_area), (fixed_width, qr_eln_area)], fill="black", width=3)
    draw.line([(0, qr_eln_area + sample_text_area), (fixed_width, qr_eln_area + sample_text_area)], fill="black", width=3)
    draw.rectangle([(0, 0), (fixed_width - 1, fixed_height - 1)], outline="black", width=3)

    font = _draw_sample_text(draw, sample_name, qr_eln_area, sample_text_area, fixed_width)
    if font is None:
        default_font = ImageFont.load_default()
        sample_text_center_y = qr_eln_area + sample_text_area // 2
        bbox = default_font.getbbox(sample_name)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (fixed_width - text_width) // 2
        text_y = sample_text_center_y - text_height // 2
        draw.text((text_x, text_y), sample_name, font=default_font, fill="black")

    _draw_rotated_label_text(label_img, "ELN link", 0, qr_eln_area)
    _draw_rotated_label_text(label_img, "sample name", qr_eln_area + sample_text_area, qr_sample_area)

    return label_img