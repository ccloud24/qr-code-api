from __future__ import annotations
import io
import zipfile
from datetime import datetime
from fastapi import FastAPI, Query, Body
from fastapi.responses import Response, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .security import ApiKeyMiddleware
from .qr import render_qr_png, render_qr_svg
from .models import BatchRequest
from .templates import wifi_payload, vcard_payload

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Generate QR codes as PNG or SVG, plus WiFi and vCard helpers.",
)

# Middleware
app.add_middleware(ApiKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins if settings.cors_allow_origins else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "service": settings.app_name, "time_utc": datetime.utcnow().isoformat() + "Z"}

@app.get("/v1/qr")
def qr(
    data: str = Query(..., min_length=1, max_length=2953),
    format: str = Query("png", pattern="^(png|svg)$"),
    size: int = Query(256, ge=64, le=2048),
    margin: int = Query(4, ge=0, le=32),
    ec: str = Query("M", pattern="^(L|M|Q|H)$"),
    fg: str = Query("000000", min_length=3, max_length=7),
    bg: str = Query("ffffff", min_length=3, max_length=7),
    download: bool = Query(False, description="If true, sets Content-Disposition to attachment."),
):
    try:
        if format == "png":
            payload = render_qr_png(data=data, size=size, margin=margin, ec=ec, fg=fg, bg=bg)
            headers = {}
            if download:
                headers["Content-Disposition"] = 'attachment; filename="qr.png"'
            return Response(content=payload, media_type="image/png", headers=headers)
        else:
            payload = render_qr_svg(data=data, size=size, margin=margin, ec=ec)
            headers = {}
            if download:
                headers["Content-Disposition"] = 'attachment; filename="qr.svg"'
            return Response(content=payload, media_type="image/svg+xml", headers=headers)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": "bad_request", "message": str(e)})

@app.post("/v1/qr/batch")
def qr_batch(req: BatchRequest = Body(...)):
    """Return a ZIP containing multiple QR images."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        for i, item in enumerate(req.items, start=1):
            # Auto filename
            ext = item.format
            name = item.filename or f"qr_{i:03d}.{ext}"
            try:
                if item.format == "png":
                    b = render_qr_png(
                        data=item.data,
                        size=item.size,
                        margin=item.margin,
                        ec=item.ec,
                        fg=item.fg,
                        bg=item.bg,
                    )
                else:
                    b = render_qr_svg(
                        data=item.data,
                        size=item.size,
                        margin=item.margin,
                        ec=item.ec,
                    )
            except ValueError as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": "bad_request", "message": f"Item {i}: {str(e)}"},
                )
            z.writestr(name, b)

    buf.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="qr_batch.zip"'}
    return StreamingResponse(buf, media_type="application/zip", headers=headers)

@app.get("/v1/templates/wifi")
def template_wifi(
    ssid: str = Query(..., min_length=1, max_length=64),
    password: str | None = Query(None, max_length=128),
    auth: str = Query("WPA", pattern="^(WPA|WEP|nopass)$"),
    hidden: bool = Query(False),
    render: bool = Query(False, description="If true, return PNG QR code instead of payload JSON."),
    size: int = Query(256, ge=64, le=2048),
    margin: int = Query(4, ge=0, le=32),
    ec: str = Query("M", pattern="^(L|M|Q|H)$"),
    fg: str = Query("000000"),
    bg: str = Query("ffffff"),
):
    try:
        payload = wifi_payload(ssid=ssid, password=password, auth=auth, hidden=hidden)
        if not render:
            return {"type": "wifi", "payload": payload}
        img = render_qr_png(data=payload, size=size, margin=margin, ec=ec, fg=fg, bg=bg)
        return Response(content=img, media_type="image/png")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": "bad_request", "message": str(e)})

@app.get("/v1/templates/vcard")
def template_vcard(
    full_name: str | None = Query(None, max_length=128),
    first_name: str | None = Query(None, max_length=64),
    last_name: str | None = Query(None, max_length=64),
    org: str | None = Query(None, max_length=128),
    title: str | None = Query(None, max_length=128),
    phone: str | None = Query(None, max_length=64),
    email: str | None = Query(None, max_length=128),
    url: str | None = Query(None, max_length=256),
    address: str | None = Query(None, max_length=256),
    render: bool = Query(False),
    size: int = Query(256, ge=64, le=2048),
    margin: int = Query(4, ge=0, le=32),
    ec: str = Query("M", pattern="^(L|M|Q|H)$"),
    fg: str = Query("000000"),
    bg: str = Query("ffffff"),
):
    payload = vcard_payload(
        full_name=full_name,
        first_name=first_name,
        last_name=last_name,
        org=org,
        title=title,
        phone=phone,
        email=email,
        url=url,
        address=address,
    )
    if not render:
        return {"type": "vcard", "payload": payload}
    img = render_qr_png(data=payload, size=size, margin=margin, ec=ec, fg=fg, bg=bg)
    return Response(content=img, media_type="image/png")
