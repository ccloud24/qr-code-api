from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional

QrFormat = Literal["png", "svg"]
EcLevel = Literal["L", "M", "Q", "H"]

class BatchItem(BaseModel):
    data: str = Field(..., max_length=2953, description="Text to encode (max QR capacity depends on mode and EC).")
    format: QrFormat = "png"
    size: int = Field(256, ge=64, le=2048, description="Target image size in pixels (PNG) or module scaling hint (SVG).")
    margin: int = Field(4, ge=0, le=32, description="Quiet zone in modules (border).")
    ec: EcLevel = "M"
    fg: str = Field("000000", description="Foreground hex RGB without '#', e.g. 000000")
    bg: str = Field("ffffff", description="Background hex RGB without '#', e.g. ffffff")

    filename: Optional[str] = Field(None, description="Optional filename to use in ZIP (otherwise auto-generated).")

class BatchRequest(BaseModel):
    items: list[BatchItem] = Field(..., min_length=1, max_length=200)

class TemplateWifiParams(BaseModel):
    ssid: str
    password: str | None = None
    auth: Literal["WPA", "WEP", "nopass"] = "WPA"
    hidden: bool = False

class TemplateVCardParams(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    org: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    url: str | None = None
    address: str | None = None
