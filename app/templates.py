from __future__ import annotations

def wifi_payload(*, ssid: str, password: str | None, auth: str = "WPA", hidden: bool = False) -> str:
    # Standard WiFi QR format: WIFI:T:WPA;S:MySSID;P:MyPass;H:false;;
    # Escape special chars: \ ; , : "
    def esc(s: str) -> str:
        return (
            s.replace("\\", "\\\\")
             .replace(";", "\\;")
             .replace(",", "\\,")
             .replace(":", "\\:")
             .replace('"', '\"')
        )

    auth = auth.upper()
    if auth not in ("WPA", "WEP", "NOPASS"):
        raise ValueError("auth must be WPA, WEP, or nopass")

    parts = [
        "WIFI:",
        f"T:{'nopass' if auth=='NOPASS' else auth};",
        f"S:{esc(ssid)};",
    ]
    if auth != "NOPASS":
        parts.append(f"P:{esc(password or '')};")
    parts.append(f"H:{'true' if hidden else 'false'};")
    parts.append(";")
    return "".join(parts)

def vcard_payload(
    *,
    full_name: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    org: str | None = None,
    title: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    url: str | None = None,
    address: str | None = None,
) -> str:
    # Minimal vCard 3.0
    if not full_name:
        full_name = " ".join([p for p in [first_name, last_name] if p]).strip() or "Contact"

    n_last = last_name or ""
    n_first = first_name or ""

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{n_last};{n_first};;;",
        f"FN:{full_name}",
    ]
    if org:
        lines.append(f"ORG:{org}")
    if title:
        lines.append(f"TITLE:{title}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{phone}")
    if email:
        lines.append(f"EMAIL;TYPE=INTERNET:{email}")
    if url:
        lines.append(f"URL:{url}")
    if address:
        # Very lightweight; you can expand later into ADR components
        lines.append(f"ADR;TYPE=HOME:;;{address};;;;")
    lines.append("END:VCARD")
    return "\n".join(lines)
