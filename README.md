# QR Code Generator API (FastAPI)

A lightweight QR code API you can publish on marketplaces (RapidAPI, APILayer, etc.).
- Generate **PNG** or **SVG** QR codes
- WiFi and vCard helpers
- Batch endpoint that returns a ZIP

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open docs:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Authentication (optional)
By default, the API is public.

To require an API key:
- Set `REQUIRE_API_KEY=true`
- Set `API_KEYS` to a comma-separated list

Example:
```bash
export REQUIRE_API_KEY=true
export API_KEYS="my-key-1,my-key-2"
```

Then send:
- `X-API-Key: my-key-1`

## Endpoints

### GET /v1/qr
Generate a QR code.

Example (PNG):
```bash
curl -G "http://127.0.0.1:8000/v1/qr" \
  --data-urlencode "data=https://example.com" \
  --data-urlencode "format=png" \
  --output qr.png
```

Example (SVG):
```bash
curl -G "http://127.0.0.1:8000/v1/qr" \
  --data-urlencode "data=hello world" \
  --data-urlencode "format=svg" \
  --output qr.svg
```

Supported query params:
- `data` (required)
- `format` = `png` | `svg`
- `size` (64..2048)
- `margin` (0..32)
- `ec` = `L|M|Q|H`
- `fg`, `bg` (PNG only) as hex RGB without `#` (e.g. `000000`)

### POST /v1/qr/batch
Returns a ZIP file of multiple QR codes.

```bash
curl -X POST "http://127.0.0.1:8000/v1/qr/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"data": "https://example.com", "format": "png", "size": 256},
      {"data": "hello", "format": "svg", "margin": 2}
    ]
  }' \
  --output qr_batch.zip
```

### GET /v1/templates/wifi
Returns WiFi payload JSON, or render a PNG QR with `render=true`.

```bash
curl -G "http://127.0.0.1:8000/v1/templates/wifi" \
  --data-urlencode "ssid=MyWifi" \
  --data-urlencode "password=MyPass123" \
  --data-urlencode "auth=WPA"
```

Render:
```bash
curl -G "http://127.0.0.1:8000/v1/templates/wifi" \
  --data-urlencode "ssid=MyWifi" \
  --data-urlencode "password=MyPass123" \
  --data-urlencode "auth=WPA" \
  --data-urlencode "render=true" \
  --output wifi.png
```

### GET /v1/templates/vcard
Returns vCard payload JSON, or render a PNG QR with `render=true`.

```bash
curl -G "http://127.0.0.1:8000/v1/templates/vcard" \
  --data-urlencode "full_name=Jane Doe" \
  --data-urlencode "phone=+15551234567" \
  --data-urlencode "email=jane@example.com"
```

## Docker

```bash
docker build -t qr-api .
docker run -p 8000:8000 qr-api
```

## Notes for marketplace listings
- Import `openapi.json` into the marketplace (RapidAPI / Postman / etc.)
- Use `X-API-Key` for auth
- Start with a Free tier limited by requests/month, then charge for batch + higher limits
