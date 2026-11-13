#!/usr/bin/env python3
"""Сборка сайта: content/*.json + config.json -> dist/*.html.

В коде только разметка. Все слова лежат в content/. Утверждения о продукте
проходят через claims.json: сборка падает, если утверждение не опубликовано.
"""
import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


class ClaimError(Exception):
    pass


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(s):
    return html.escape(s, quote=True)


class Builder:
    def __init__(self, content_dir=None, config_path=None, out_dir=None, docs_dir=None):
        self.content_dir = Path(content_dir or ROOT / "content")
        self.cfg = load_json(config_path or ROOT / "config.json")
        self.site = load_json(self.content_dir / "site.ru.json")
        cl = load_json(self.content_dir / "claims.json")
        self.allowed = set(cl["allowed_statuses"])
        self.claims = {c["id"]: c for c in cl["claims"]}
        self.out = Path(out_dir or ROOT / "dist")
        self.docs_dir = Path(docs_dir or ROOT / "docs")
        self.base = urlparse(self.cfg["base_url"]).path.rstrip("/")
        self.used = set()

    # ---------- утверждения ----------
    def _check(self, ids):
        if not ids:
            raise ClaimError("Текст с утверждением без номеров утверждений")
        for i in ids:
            c = self.claims.get(i)
            if c is None:
                raise ClaimError(f"Утверждение {i} не найдено в claims.json")
            if not c.get("publish"):
                raise ClaimError(f"Утверждение {i} не опубликовано: {c.get('reason', 'нет причины')}")
            if c["status"] not in self.allowed:
                raise ClaimError(f"Утверждение {i} со статусом {c['status']}: без источника на сайт нельзя")
            if not c.get("source"):
                raise ClaimError(f"Утверждение {i} без источника")
            self.used.add(i)

    def _subst(self, s):
        op = self.cfg["operator"]
        req = ""
        if op.get("inn"):
            req += f" ИНН {op['inn']}."
        if op.get("ogrn"):
            req += f" ОГРН {op['ogrn']}."
        pairs = {
            "{phone}": op["phone"],
            "{address}": op["address"],
            "{operator_name}": op["name"],
            "{updated}": self.cfg["updated"],
            "{retention}": str(self.cfg["retention_months"]),
            "{requisites}": req,
        }
        for k, v in pairs.items():
            s = s.replace(k, v)
        return s

    def claimed(self, item):
        """Текст с утверждением: объект {t, c}."""
        if not isinstance(item, dict) or "t" not in item or "c" not in item:
            raise ClaimError(f"Ожидался объект с t и c, получено: {item!r}")
        self._check(item["c"])
        return esc(self._subst(item["t"]))

    def ui(self, s):
        """Подпись интерфейса: только строка."""
        if not isinstance(s, str):
            raise ClaimError(f"Ожидалась строка подписи, получено: {s!r}")
        return esc(self._subst(s))

    # ---------- общие куски ----------
    def head(self, title, desc_html=""):
        d = f'<meta name="description" content="{desc_html}">' if desc_html else ""
        return (
            '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{title}</title>{d}"
            '<link rel="icon" href="data:,">'
            f'<link rel="stylesheet" href="{self.base}/static/style.css">'
            "</head>"
        )

    def header(self):
        ui = self.site["ui"]
        links = "".join(f'<a href="{self.base}/#{esc(n["id"])}">{self.ui(n["t"])}</a>' for n in ui["nav"])
        return (
            f'<a class="skip" href="#main">{self.ui(ui["skip"])}</a>'
            f'<header class="top"><div class="wrap"><a class="brand" href="{self.base}/">{self.ui(ui["brand"])}</a>'
            f'<nav aria-label="{self.ui(ui["nav_label"])}">{links}</nav></div></header>'
        )

    def footer(self):
        f = self.site["footer"]
        return (
            '<footer class="foot"><div class="wrap">'
            f'<p class="badge">{self.claimed(f["badge"])}</p>'
            f'<h2 class="small-h">{self.ui(f["maker_h"])}</h2>'
            f'<p>{self.claimed(f["maker"])}</p>'
            f'<p><a href="{self.base}/#dokumenty">{self.ui(f["docs_link"])}</a></p>'
            f'<p><a href="{self.base}/policy">{self.ui(f["policy"])}</a></p>'
            f'<p class="muted">{self.ui(f["updated"])}</p>'
            "</div></footer>"
        )

    # ---------- секции ----------
    def hero(self):
        h = self.site["hero"]
        max_btn = ""
        if self.cfg.get("max_bot_link"):
            max_btn = f'<a class="btn ghost" href="{self.base}/q/site">{self.ui(h["btn_max"])}</a>'
        return (
            '<section class="hero"><div class="wrap">'
            f'<p class="muted">{self.claimed(h["maker"])}</p>'
            f'<h1>{self.ui(h["title"])}</h1>'
            f'<p class="lead">{self.claimed(h["lead"])}</p>'
            f'<p class="badge">{self.claimed(h["badge"])}</p>'
            f'<p class="btns"><a class="btn" href="#kak">{self.ui(h["btn_how"])}</a>'
            f'<a class="btn alt" href="#zakaz">{self.ui(h["btn_order"])}</a>{max_btn}</p>'
            "</div></section>"
        )

    def kak(self):
        k = self.site["kak"]
        steps = "".join(
            f'<li><h3>{self.ui(s["title"])}</h3><p>{self.claimed(s["p"])}</p></li>' for s in k["steps"]
        )
        days = "".join(
            f'<li><label><input type="checkbox" data-day="{n}"><span><span class="vh">{self.ui(k["tracker_day"])} </span>{n}</span></label></li>'
            for n in range(1, 22)
        )
        return (
            '<section id="kak"><div class="wrap">'
            f'<h2>{self.ui(k["h2"])}</h2><ol class="steps">{steps}</ol>'
            f'<p class="note">{self.claimed(k["course"])}</p>'
            f'<h3>{self.ui(k["tracker_h3"])}</h3><p class="muted">{self.ui(k["tracker_note"])}</p>'
            f'<ol class="tracker">{days}</ol>'
            f'<p><button type="button" class="btn ghost" id="tracker-reset">{self.ui(k["tracker_reset"])}</button></p>'
            "</div></section>"
        )

    def nelzya(self):
        n = self.site["nelzya"]
        no = "".join(f"<li>{self.claimed(i)}</li>" for i in n["no_items"])
        dont = "".join(f"<li>{self.claimed(i)}</li>" for i in n["dont_items"])
        return (
            '<section id="nelzya" class="tint"><div class="wrap">'
            f'<h2>{self.ui(n["h2"])}</h2>'
            f'<h3>{self.ui(n["no_h3"])}</h3><ul>{no}</ul>'
            f'<p class="note">{self.claimed(n["doctor"])}</p>'
            f'<h3>{self.ui(n["dont_h3"])}</h3><ul>{dont}</ul>'
            f'<p>{self.claimed(n["storage"])}</p>'
            "</div></section>"
        )

    def chto(self):
        c = self.site["chto"]
        paras = "".join(f"<p>{self.claimed(p)}</p>" for p in c["paras"])
        rows = "".join(
            f'<tr><th scope="row">{self.ui(r["k"])}</th><td>{self.claimed(r["v"])}</td></tr>' for r in c["facts"]
        )
        return (
            '<section id="chto"><div class="wrap">'
            f'<h2>{self.ui(c["h2"])}</h2>{paras}'
            f'<h3>{self.ui(c["facts_h3"])}</h3><table class="facts"><tbody>{rows}</tbody></table>'
            "</div></section>"
        )

    def max_block(self):
        if not self.cfg.get("max_bot_link"):
            return ""
        m = self.site["max"]
        return (
            '<section class="tint"><div class="wrap">'
            f'<h2>{self.ui(m["h2"])}</h2><p>{self.ui(m["p"])}</p>'
            f'<p><a class="btn" href="{self.base}/q/site">{self.ui(m["btn"])}</a></p>'
            "</div></section>"
        )

    def zakaz(self):
        z = self.site["zakaz"]
        has_card = bool(self.cfg.get("order_url"))
        intro = self.claimed(z["p_card"] if has_card else z["p_form"])
        card = ""
        if has_card:
            card = f'<p><a class="btn" rel="noopener" href="{esc(self.cfg["order_url"])}">{self.ui(z["btn_card"])}</a></p>'
        phone = self.cfg["operator"]["phone"]
        tel = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        return (
            '<section id="zakaz" class="tint"><div class="wrap">'
            f'<h2>{self.ui(z["h2"])}</h2><p>{intro}</p>{card}'
            f'<h3>{self.ui(z["form_h3"])}</h3><p class="muted">{self.ui(z["hint"])}</p>'
            f'<form method="post" action="{self.base}/order" class="order">'
            f'<label for="f-name">{self.ui(z["label_name"])}</label>'
            '<input id="f-name" name="name" autocomplete="name" maxlength="80">'
            f'<label for="f-phone">{self.ui(z["label_phone"])}</label>'
            '<input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required maxlength="25">'
            '<input type="hidden" name="source" id="f-source" value="">'
            f'<div class="hp" aria-hidden="true"><label for="f-site">{self.ui(z["hp_label"])}</label>'
            '<input id="f-site" name="website" tabindex="-1" autocomplete="off"></div>'
            '<label class="consent" for="f-consent"><input id="f-consent" type="checkbox" name="consent" value="yes" required>'
            f'<span>{self.ui(z["consent_before"])}<a href="{self.base}/policy">{self.ui(z["consent_link"])}</a></span></label>'
            f'<button class="btn" type="submit">{self.ui(z["btn_send"])}</button>'
            "</form>"
            f'<p>{self.ui(z["call_before"])}<a href="tel:{esc(tel)}">{esc(phone)}</a></p>'
            "</div></section>"
        )

    def faq(self):
        f = self.site["faq"]
        items = "".join(
            f'<details><summary>{self.ui(i["q"])}</summary><p>{self.claimed(i["a"])}</p></details>' for i in f["items"]
        )
        return f'<section id="voprosy"><div class="wrap"><h2>{self.ui(f["h2"])}</h2>{items}</div></section>'

    def dokumenty(self):
        d = self.site["dokumenty"]
        present = [x for x in d["docs"] if (self.docs_dir / Path(x["file"]).name).exists()]
        if present:
            docs = "<ul>" + "".join(
                f'<li><a href="{self.base}/{esc(x["file"])}">{self.ui(x["title"])}</a> ({self.ui(d["docs_open"])})</li>'
                for x in present
            ) + "</ul>"
        else:
            docs = f'<p>{self.ui(d["docs_none"])}</p>'
        refs = ""
        for r in d["refs"]:
            extra = ""
            if r.get("extra"):
                extra = (
                    f' {self.ui(r["extra"])} <a href="https://doi.org/{esc(r["extra_doi"])}" rel="noopener">'
                    f'{self.ui(d["doi_label"])} {esc(r["extra_doi"])}</a>.'
                )
            refs += (
                f'<li>{self.claimed(r)} <a href="https://doi.org/{esc(r["doi"])}" rel="noopener">'
                f'{self.ui(d["doi_label"])} {esc(r["doi"])}</a>.{extra}</li>'
            )
        return (
            '<section id="dokumenty" class="tint"><div class="wrap">'
            f'<h2>{self.ui(d["h2"])}</h2><h3>{self.ui(d["docs_h3"])}</h3>{docs}'
            f'<h3>{self.claimed(d["refs_h3"])}</h3><p class="note">{self.claimed(d["refs_note"])}</p>'
            f"<ul>{refs}</ul></div></section>"
        )

    # ---------- страницы ----------
    def index(self):
        m = self.site["meta"]
        body = (
            self.header() + '<main id="main">'
            + self.hero() + self.kak() + self.nelzya() + self.chto()
            + self.max_block() + self.zakaz() + self.faq() + self.dokumenty()
            + "</main>" + self.footer()
            + f'<script src="{self.base}/static/app.js" defer></script></body></html>'
        )
        return self.head(self.ui(m["title"]), self.claimed(m["description"])) + "<body>" + body

    def policy(self):
        p = self.site["policy"]
        secs = ""
        for s in p["sections"]:
            paras = "".join(f"<p>{self.ui(x)}</p>" for x in s["p"])
            secs += f'<h2>{self.ui(s["h"])}</h2>{paras}'
        return (
            self.head(self.ui(p["title"])) + "<body>" + self.header()
            + f'<main id="main"><div class="wrap"><h1>{self.ui(p["title"])}</h1>{secs}'
            f'<p><a class="btn ghost" href="{self.base}/">{self.ui(p["back"])}</a></p></div></main>'
            + self.footer() + "</body></html>"
        )

    def thanks(self):
        t = self.site["thanks"]
        return (
            self.head(self.ui(t["title"])) + "<body>" + self.header()
            + f'<main id="main"><div class="wrap"><h1>{self.ui(t["h1"])}</h1><p>{self.ui(t["p"])}</p>'
            f'<p><a class="btn" href="{self.base}/">{self.ui(t["back"])}</a></p></div></main>'
            + self.footer() + "</body></html>"
        )

    def build(self):
        pages = {"index.html": self.index(), "policy.html": self.policy(), "spasibo.html": self.thanks()}
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "static").mkdir(parents=True)
        for name, text in pages.items():
            (self.out / name).write_text(text, encoding="utf-8")
        for f in (ROOT / "static").iterdir():
            shutil.copy2(f, self.out / "static" / f.name)
        if self.docs_dir.exists():
            (self.out / "docs").mkdir()
            for f in self.docs_dir.iterdir():
                if f.suffix.lower() == ".pdf":
                    shutil.copy2(f, self.out / "docs" / f.name)
        return sorted(self.used)

    def to_verify(self):
        return [self.claims[i] for i in sorted(self.used) if self.claims[i].get("verify")]


def main():
    b = Builder()
    try:
        used = b.build()
    except ClaimError as e:
        print(f"СБОРКА ОСТАНОВЛЕНА: {e}", file=sys.stderr)
        return 1
    print(f"Собрано в {b.out}. Использовано утверждений: {len(used)}.")
    v = b.to_verify()
    if v:
        print("\nПеред запуском сверить с СГР, протоколом или технологом:")
        for c in v:
            print(f"  {c['id']}: {c['text']}  [{c['source']}]")
    if not b.cfg.get("max_bot_link"):
        print("\nНе задано: max_bot_link (кнопки MAX скрыты, QR ведёт на сайт).")
    if not b.cfg.get("order_url"):
        print("Не задано: order_url (кнопка маркетплейса скрыта, остаётся заявка).")
    if not b.cfg["operator"].get("inn"):
        print("Не задано: operator.inn и operator.ogrn (в политике не указаны).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
