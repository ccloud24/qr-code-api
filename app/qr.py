from __future__ import annotations
import io
import re
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

try:
    from PIL import Image
except Exception as e:
    Image = None  # type: ignore

from qrcode.image.svg import SvgPathImage

_HEX_RE = re.compile(r"^[0-9a-fA-F]{6}$")

def _validate_hex(hex_rgb: str) -> str:
    h = hex_rgb.strip().lstrip("#")
    if not _HEX_RE.match(h):
        raise ValueError("Invalid hex color. Use 6 hex chars, e.g. 000000 or ffffff.")
    return h.lower()

def _ec_map(level: str):
    level = level.upper()
    if level == "L":
        return ERROR_CORRECT_L
    if level == "M":
        return ERROR_CORRECT_M
    if level == "Q":
        return ERROR_CORRECT_Q
    if level == "H":
        return ERROR_CORRECT_H
    raise ValueError("Invalid ec level. Use one of L, M, Q, H.")

def render_qr_png(*, data: str, size: int = 256, margin: int = 4, ec: str = "M", fg: str = "000000", bg: str = "ffffff") -> bytes:
    if Image is None:
        raise RuntimeError("Pillow is required for PNG rendering. Install with: pip install pillow")

    fg = _validate_hex(fg)
    bg = _validate_hex(bg)
    ec_const = _ec_map(ec)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_const,
        box_size=10,  # temporary; we'll resize after
        border=margin,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=f"#{fg}", back_color=f"#{bg}").convert("RGB")

    # Resize to requested size (square). NEAREST preserves crisp edges.
    img = img.resize((size, size), resample=Image.NEAREST)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def render_qr_svg(*, data: str, size: int = 256, margin: int = 4, ec: str = "M") -> bytes:
    # For SVG, we use qrcode's SvgPathImage. The 'size' is a scaling hint (module size).
    ec_const = _ec_map(ec)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_const,
        box_size=max(1, size // 64),  # heuristic scaling; SVG remains vector anyway
        border=margin,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(image_factory=SvgPathImage)
    # qrcode's SVG image writes to a file-like handle
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue()
