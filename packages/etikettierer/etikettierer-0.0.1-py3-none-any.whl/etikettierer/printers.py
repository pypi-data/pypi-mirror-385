from typing import Optional
from PIL import Image
import io
import zpl

def print_brother_ql_label(
    pil_image: Image.Image,
    label_size: str = "62",
    printer_model: str = "QL-800",
    printer_usb: str = "usb://0x04f9:0x209b",
    red: bool = False,
):
    """
    Send the PIL image to a Brother QL printer using brother_ql.
    Note: brother_ql is an optional dependency. Import error is raised if it's not installed.
    """
    try:
        from brother_ql.backends.helpers import send
        from brother_ql.conversion import convert
        from brother_ql.raster import BrotherQLRaster
    except Exception as exc:
        raise RuntimeError("brother_ql package is required for Brother printing") from exc

    # Resize to printer internal size (heuristic from old GUI)
    print_image = pil_image.resize((696, 771), Image.LANCZOS)

    qlr = BrotherQLRaster(printer_model)
    qlr.exception_on_warning = True

    instructions = convert(
        qlr=qlr,
        images=[print_image],
        label=label_size,
        rotate="auto",
        threshold=70.0,
        dither=False,
        compress=False,
        red=red,
        dpi_600=False,
        hq=True,
        cut=True,
    )

    send(
        instructions=instructions,
        printer_identifier=printer_usb,
        backend_identifier="pyusb",
        blocking=True,
    )

def print_image_to_zpl(image: Image.Image) -> str:
    """
    Convert a PIL image to ZPL using the `zpl` library and return the ZPL string.
    """
    # rotate the image same as original GUI
    rot_preview_image = image.rotate(90, expand=True)
    label = zpl.Label(76, 100)
    label.origin(3, 0)
    image_width = 69
    label.write_graphic(rot_preview_image, image_width)
    label.endorigin()
    return label.dumpZPL()

def print_zpl_via_windows(zpl_string: str, printer_name: str):
    """
    Send ZPL string directly to a Windows printer (requires pywin32).
    """
    try:
        import win32print
    except Exception as exc:
        raise RuntimeError("pywin32 is required for Windows printing") from exc

    hprinter = win32print.OpenPrinter(printer_name)
    try:
        hjob = win32print.StartDocPrinter(hprinter, 1, ("ZPL Label", None, "RAW"))
        win32print.StartPagePrinter(hprinter)
        win32print.WritePrinter(hprinter, zpl_string.encode("utf-8"))
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
    finally:
        win32print.ClosePrinter(hprinter)
