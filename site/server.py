#!/usr/bin/env python3
"""Сервер сайта BETULA AQUA: только стандартная библиотека Python.

Отдаёт dist/, считает переходы по QR (/q/<канал>) и принимает заявки (/order).
Данные пишутся в DATA_DIR (на сервере в России): visits.csv и leads.csv.
Адреса: все пути живут под префиксом из base_url (по умолчанию /betula-aqua).
"""
import argparse
import csv
import html
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
CODE_RE = re.compile(r"^[a-z0-9_-]{1,40}$")
EVENT_RE = re.compile(r"^(cta|scroll):[a-z0-9_-]{1,30}$")
EVENTS_PER_MINUTE = 600
MAX_BODY = 4096
LEADS_PER_HOUR = 60

CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
    "form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
)


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def clean_cell(value, limit=80):
    """Убирает управляющие символы и защищает от формул в Excel."""
    value = "".join(ch for ch in value if ch.isprintable()).strip()[:limit]
    if value[:1] in ("=", "+", "-", "@"):
        value = "'" + value
    return value


class App:
    def __init__(self, dist, data_dir, config_path, content_dir):
        self.dist = Path(dist).resolve()
        self.data = Path(data_dir)
        self.data.mkdir(parents=True, exist_ok=True)
        self.cfg = load_json(config_path)
        content = Path(content_dir)
        self.site = load_json(content / "site.ru.json")
        self.channels = {c["code"]: c.get("to", "landing") for c in load_json(content / "channels.json")["channels"]}
        self.base = urlparse(self.cfg["base_url"]).path.rstrip("/")
        self.lock = threading.Lock()
        self.recent = []
        self.events = []

    def row(self, name, header, row):
        path = self.data / name
        with self.lock:
            new = not path.exists()
            with path.open("a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(header)
                w.writerow(row)

    def now(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def too_many(self):
        t = time.time()
        with self.lock:
            self.recent = [x for x in self.recent if t - x < 3600]
            if len(self.recent) >= LEADS_PER_HOUR:
                return True
            self.recent.append(t)
        return False

    def events_full(self):
        t = time.time()
        with self.lock:
            self.events = [x for x in self.events if t - x < 60]
            if len(self.events) >= EVENTS_PER_MINUTE:
                return True
            self.events.append(t)
        return False

    def max_url(self, code):
        link = self.cfg.get("max_bot_link", "")
        if not link:
            return ""
        sep = "&" if "?" in link else "?"
        return f"{link}{sep}{self.cfg.get('max_start_param', 'start')}={code}"

    def error_page(self, key):
        e = self.site["errors"]
        phone = self.cfg["operator"]["phone"]
        msg = html.escape(e[key].replace("{phone}", phone))
        title = html.escape(e["title"])
        back = html.escape(e["back"])
        return (
            f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title>'
            f'<link rel="icon" href="data:,"><link rel="stylesheet" href="{self.base}/static/style.css"></head><body>'
            f'<main id="main"><div class="wrap"><h1>{title}</h1><p>{msg}</p>'
            f'<p><a class="btn" href="{self.base}/#zakaz">{back}</a></p></div></main></body></html>'
        )


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BetulaSite"
        sys_version = ""

        def log_message(self, fmt, *args):  # без IP-адресов
            print(f"{self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}")

        # ---------- ответы ----------
        def _send(self, status, body=b"", ctype="text/html; charset=utf-8", cache="no-cache", extra=None):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache)
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "same-origin")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _redirect(self, url, status=HTTPStatus.FOUND):
            self._send(status, b"", cache="no-store", extra={"Location": url})

        def _rel(self):
            path = urlparse(self.path).path
            b = app.base
            if path == b:
                return None
            if b and not path.startswith(b + "/"):
                return False
            return path[len(b):] or "/"

        def _file(self, rel_path, cache):
            target = (app.dist / rel_path.lstrip("/")).resolve()
            if app.dist not in target.parents and target != app.dist:
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")
            if not target.is_file():
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")
            ctype = {
                ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                ".js": "text/javascript; charset=utf-8", ".pdf": "application/pdf",
                ".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2",
            }.get(target.suffix.lower(), "application/octet-stream")
            self._send(HTTPStatus.OK, target.read_bytes(), ctype, cache)

        # ---------- маршруты ----------
        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            rel = self._rel()
            if rel is None or (rel is False and urlparse(self.path).path == "/"):
                return self._redirect(app.base + "/")
            if rel is False:
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")
            if rel == "/":
                return self._file("index.html", "no-cache")
            if rel == "/kak-prinimat":
                return self._file("kak-prinimat.html", "no-cache")
            if rel == "/policy":
                return self._file("policy.html", "no-cache")
            if rel == "/spasibo":
                return self._file("spasibo.html", "no-cache")
            if rel == "/health":
                return self._send(HTTPStatus.OK, b"ok", "text/plain; charset=utf-8")
            if rel.startswith("/q/"):
                return self._qr(rel[3:])
            if rel.startswith("/static/") or rel.startswith("/docs/"):
                return self._file(rel, "public, max-age=604800" if rel.endswith(".woff2") else "public, max-age=3600")
            return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")

        def _qr(self, code):
            if not CODE_RE.match(code):
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")
            to = app.channels.get(code)
            channel = code if to else "unknown"
            if to == "max" and app.max_url(channel):
                kind, target = "max", app.max_url(channel)
            elif to == "howto":
                kind, target = "howto", f"{app.base}/kak-prinimat?s={channel}"
            else:
                kind, target = "landing", f"{app.base}/?s={channel}"
            app.row("visits.csv", ["ts_utc", "channel", "target"], [app.now(), channel, kind])
            self._redirect(target)

        def do_POST(self):
            rel = self._rel()
            if rel == "/e":
                return self._event()
            if rel != "/order":
                return self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")
            try:
                n = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                n = -1
            if n <= 0 or n > MAX_BODY:
                return self._send(HTTPStatus.BAD_REQUEST, app.error_page("generic").encode("utf-8"))
            form = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode("utf-8", "replace")).items()}
            thanks = f"{app.base}/spasibo"
            if form.get("website", "").strip():  # ловушка для роботов: молча не сохраняем
                return self._redirect(thanks, HTTPStatus.SEE_OTHER)
            if form.get("consent") != "yes":
                return self._send(HTTPStatus.BAD_REQUEST, app.error_page("consent").encode("utf-8"))
            digits = "".join(ch for ch in form.get("phone", "") if ch.isdigit())
            if not 10 <= len(digits) <= 15:
                return self._send(HTTPStatus.BAD_REQUEST, app.error_page("phone").encode("utf-8"))
            if app.too_many():
                return self._send(HTTPStatus.TOO_MANY_REQUESTS, app.error_page("generic").encode("utf-8"))
            source = form.get("source", "")
            source = source if CODE_RE.match(source) else ""
            pack = form.get("pack", "1")
            pack = pack if pack in ("1", "2") else "1"
            via = form.get("via", "call")
            via = via if via in ("call", "max") else "call"
            app.row(
                "leads.csv", ["ts_utc", "name", "phone_digits", "source", "consent", "pack", "via"],
                [app.now(), clean_cell(form.get("name", "")), digits, source, "yes", pack, via],
            )
            self._redirect(thanks, HTTPStatus.SEE_OTHER)

        def _event(self):
            """Счётчик нажатий и прокрутки: только событие и метка канала, без IP и cookie."""
            try:
                n = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                n = -1
            if n <= 0 or n > 300:
                return self._send(HTTPStatus.BAD_REQUEST, b"", "text/plain; charset=utf-8")
            form = {k: v[0] for k, v in parse_qs(self.rfile.read(n).decode("utf-8", "replace")).items()}
            ev, src = form.get("ev", ""), form.get("s", "")
            if not EVENT_RE.match(ev):
                return self._send(HTTPStatus.BAD_REQUEST, b"", "text/plain; charset=utf-8")
            src = src if CODE_RE.match(src) else ""
            if not app.events_full():
                app.row("events.csv", ["ts_utc", "event", "source"], [app.now(), ev, src])
            self._send(HTTPStatus.NO_CONTENT, b"", "text/plain; charset=utf-8")

    return Handler


def make_server(host="127.0.0.1", port=8080, dist=None, data_dir=None, config=None, content=None):
    app = App(
        dist or ROOT / "dist",
        data_dir or os.environ.get("DATA_DIR") or ROOT / "data",
        config or ROOT / "config.json",
        content or ROOT / "content",
    )
    return ThreadingHTTPServer((host, port), make_handler(app)), app


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    srv, app = make_server(args.host, args.port)
    print(f"http://{args.host}:{args.port}{app.base}/  данные: {app.data}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
