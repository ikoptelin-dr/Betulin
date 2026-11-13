#!/usr/bin/env python3
"""QR-коды для каждого канала: <base_url>/q/<код>. Нужен пакет segno (pip install segno).

Файлы qr/<код>.svg для печати и qr/<код>.png для проверки. Запускать после
любого изменения base_url или списка каналов в content/channels.json.
"""
import json
import sys
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    channels = json.loads((ROOT / "content" / "channels.json").read_text(encoding="utf-8"))["channels"]
    base = cfg["base_url"].rstrip("/")
    out = ROOT / "qr"
    out.mkdir(exist_ok=True)
    for c in channels:
        url = f"{base}/q/{c['code']}"
        qr = segno.make(url, error="m")
        qr.save(out / f"{c['code']}.svg", scale=10, border=4, dark="#000000", light="#ffffff")
        qr.save(out / f"{c['code']}.png", scale=10, border=4, dark="#000000", light="#ffffff")
        print(f"{c['code']:10} {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
