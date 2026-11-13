#!/usr/bin/env python3
"""Выполняет обещания из политики обработки данных.

  python3 purge_leads.py            удалить заявки старше retention_months (запускать раз в сутки)
  python3 purge_leads.py --erase 79230001122   удалить все заявки с этим телефоном (отзыв согласия)
"""
import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rewrite(path, keep, header):
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(keep)
    os.replace(tmp, path)


def purge(data_dir, retention_months, erase_phone=None, now=None):
    path = Path(data_dir) / "leads.csv"
    if not path.exists():
        return 0
    now = now or datetime.now(timezone.utc)
    limit = now - timedelta(days=30 * retention_months)
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    keep = []
    for r in body:
        ts = datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if ts < limit:
            continue
        if erase_phone and r[header.index("phone_digits")] == erase_phone:
            continue
        keep.append(r)
    rewrite(path, keep, header)
    return len(body) - len(keep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--erase", help="телефон цифрами, например 79230001122")
    args = ap.parse_args()
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    data = os.environ.get("DATA_DIR") or ROOT / "data"
    removed = purge(data, cfg["retention_months"], args.erase)
    print(f"Удалено заявок: {removed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
