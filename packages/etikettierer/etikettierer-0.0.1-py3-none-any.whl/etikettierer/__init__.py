"""
etikettierer - core label and QR code utilities (non-GUI)
"""
__version__ = "0.0.1"

from .labels import (
    ERROR_CORRECTION_MAP,
    estimate_version,
    generate_qr_code,
    create_label_image,
)
from .printers import (
    print_brother_ql_label,
    print_image_to_zpl,
    print_zpl_via_windows,
)

__all__ = [
    "ERROR_CORRECTION_MAP",
    "estimate_version",
    "generate_qr_code",
    "create_label_image",
    "print_brother_ql_label",
    "print_image_to_zpl",
    "print_zpl_via_windows",
]
