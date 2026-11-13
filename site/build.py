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
        self.lp = load_json(self.content_dir / "landing.ru.json")
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
    def head(self, title, desc_html="", css="style.css"):
        d = f'<meta name="description" content="{desc_html}">' if desc_html else ""
        return (
            '<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f"<title>{title}</title>{d}"
            '<link rel="icon" href="data:,">'
            f'<link rel="preload" href="{self.base}/static/fonts/manrope-cyrillic.woff2" as="font" type="font/woff2" crossorigin>'
            f'<link rel="stylesheet" href="{self.base}/static/{css}">'
            "</head>"
        )

    def header(self, nav=None, prefix=None, cta=None, cls="top"):
        ui = self.site["ui"]
        nav = self.lp["nav"] if nav is None else nav
        prefix = f"{self.base}/" if prefix is None else prefix
        links = "".join(f'<a href="{prefix}#{esc(n["id"])}">{self.ui(n["t"])}</a>' for n in nav)
        btn = f'<a class="btn small" href="{prefix}#zayavka">{self.ui(cta)}</a>' if cta else ""
        return (
            f'<a class="skip" href="#main">{self.ui(ui["skip"])}</a>'
            f'<header class="{cls}"><div class="wrap wide"><a class="brand" href="{self.base}/">{self.ui(ui["brand"])}</a>'
            f'<nav aria-label="{self.ui(ui["nav_label"])}">{links}</nav>{btn}</div></header>'
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

    def order_form(self):
        z = self.site["zakaz"]
        return (
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
        )

    def phone_link(self):
        phone = self.cfg["operator"]["phone"]
        tel = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        return f'<a href="tel:{esc(tel)}">{esc(phone)}</a>'

    def zakaz(self):
        z = self.site["zakaz"]
        has_card = bool(self.cfg.get("order_url"))
        intro = self.claimed(z["p_card"] if has_card else z["p_form"])
        card = ""
        if has_card:
            card = f'<p><a class="btn" rel="noopener" href="{esc(self.cfg["order_url"])}">{self.ui(z["btn_card"])}</a></p>'
        return (
            '<section id="zakaz" class="tint"><div class="wrap">'
            f'<h2>{self.ui(z["h2"])}</h2><p>{intro}</p>{card}'
            f'<h3>{self.ui(z["form_h3"])}</h3><p class="muted">{self.ui(z["hint"])}</p>'
            + self.order_form()
            + f'<p>{self.ui(z["call_before"])}{self.phone_link()}</p>'
            "</div></section>"
        )

    def faq(self, ids=None):
        f = self.site["faq"]
        chosen = f["items"] if ids is None else [f["items"][k] for k in ids]
        items = "".join(
            f'<details><summary>{self.ui(i["q"])}</summary><p>{self.claimed(i["a"])}</p></details>' for i in chosen
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
            self.header(self.site["ui"]["nav"], "") + '<main id="main">'
            + self.hero() + self.kak() + self.nelzya() + self.chto()
            + self.max_block() + self.zakaz() + self.faq() + self.dokumenty()
            + "</main>" + self.footer()
            + f'<script src="{self.base}/static/app.js" defer></script></body></html>'
        )
        return self.head(self.ui(m["title"]), self.claimed(m["description"])) + "<body>" + body

    # ---------- продающая страница ----------
    TICK = (
        '<svg class="tick" width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="11" fill="#115060"/>'
        '<path d="M6.5 11.5l3 3 6-6.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
    ICONS = {
        "doc": "M8 5h6l3 3v11H8z M14 5v3h3 M10 12h5 M10 15h5",
        "factory": "M5 19V11l4 2V11l4 2V8l6 3v8z M5 19h14",
        "book": "M6 6h5a2 2 0 0 1 2 2v10a2 2 0 0 0-2-2H6z M18 6h-5 M18 6v10h-5",
        "truck": "M4 8h9v8H4z M13 11h4l3 3v2h-7z M7 18a1.5 1.5 0 1 0 0-.01 M17 18a1.5 1.5 0 1 0 0-.01",
    }

    def tx(self, x):
        """Строка подписи или объект с утверждением."""
        return self.claimed(x) if isinstance(x, dict) else self.ui(x)

    def icon(self, name):
        return (
            '<svg class="ico" width="40" height="40" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="8" fill="#ade2e1"/>'
            f'<path d="{self.ICONS[name]}" fill="none" stroke="#115060" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )

    def cta(self, cid, label=None, cls="btn"):
        L = self.lp
        text = self.tx(label) if label is not None else self.claimed(L["cta_price"])
        return f'<a class="{cls}" href="#zayavka" data-cta="{esc(cid)}">{text}</a>'

    def cta_row(self, cid, label=None):
        return f'<div class="cta-row">{self.cta(cid, label)}<p>{self.claimed(self.lp["callback"])}</p></div>'

    def sec(self, sid, kicker, h2, inner, cls=""):
        sid_attr = f' id="{esc(sid)}"' if sid else ""
        return (
            f'<section class="block gut {cls}"{sid_attr} data-sec="{esc(sid or cls)}"><div class="wrap">'
            f'<p class="kicker">{self.ui(kicker)}</p><h2>{self.ui(h2)}</h2>{inner}</div></section>'
        )

    def lp_form(self):
        z, o = self.site["zakaz"], self.lp["offer"]
        packs = "".join(
            f'<label class="opt"><input type="radio" name="pack" value="{esc(p["id"])}"{" checked" if p["id"] == "1" else ""}>'
            f'<span><b>{self.ui(p["name"])}</b> · {self.claimed(p["price"])}</span></label>'
            for p in o["packs"]
        )
        return (
            f'<form method="post" action="{self.base}/order" class="form" id="order-form">'
            f'<h3>{self.ui(o["form_h3"])}</h3>'
            f'<fieldset class="seg"><legend>{self.ui(o["pack_label"])}</legend>{packs}</fieldset>'
            f'<label for="f-name">{self.ui(z["label_name"])}</label>'
            '<input id="f-name" name="name" type="text" autocomplete="name" maxlength="80">'
            f'<label for="f-phone">{self.ui(z["label_phone"])}</label>'
            '<input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required maxlength="25" placeholder="+7">'
            f'<fieldset class="seg"><legend>{self.ui(o["via_label"])}</legend>'
            f'<label class="opt"><input type="radio" name="via" value="call" checked><span>{self.ui(o["via_call"])}</span></label>'
            f'<label class="opt"><input type="radio" name="via" value="max"><span>{self.ui(o["via_max"])}</span></label></fieldset>'
            '<input type="hidden" name="source" id="f-source" value="">'
            f'<div class="hp" aria-hidden="true"><label for="f-site">{self.ui(z["hp_label"])}</label>'
            '<input id="f-site" name="website" tabindex="-1" autocomplete="off"></div>'
            '<label class="consent" for="f-consent"><input id="f-consent" type="checkbox" name="consent" value="yes" required>'
            f'<span>{self.ui(z["consent_before"])}<a href="{self.base}/policy">{self.ui(z["consent_link"])}</a></span></label>'
            f'<button class="btn" type="submit" data-cta="form-submit">{self.ui(o["send"])}</button>'
            f'<p class="after">{self.claimed(o["after_btn"])}</p>'
            "</form>"
        )

    def landing(self):
        L, base = self.lp, self.base
        h = L["hero"]
        ticks = "".join(f"<li>{self.TICK}<span>{self.claimed(t)}</span></li>" for t in h["ticks"])
        chips = "".join(f'<span class="chip">{self.claimed(c)}</span>' for c in h["chips"])
        stickers = "".join(
            f'<div class="sticker"><b>{self.claimed(s["b"])}</b><span>{self.ui(s["s"])}</span></div>' for s in h["stickers"]
        )
        hero = (
            '<section class="hero gut" data-sec="hero"><div class="wrap">'
            f'<div class="h-top"><span class="eyebrow"><i></i>{self.claimed(h["pill"])}</span>'
            f'<h1>{self.ui(h["h1_a"])} <span>{self.ui(h["h1_b"])}</span></h1></div>'
            f'<div class="stage"><img class="leaf" alt="" src="{base}/static/img/leaf.webp" width="324" height="672">'
            f'<div class="bwrap"><div class="bottle" role="img" aria-label="{self.ui(h["bottle_alt"])}">'
            '<div class="cap"></div><div class="neck"></div><div class="body"></div></div><div class="floor"></div></div>'
            f'<div class="stickers">{stickers}</div></div>'
            f'<div class="h-rest"><p class="lead">{self.claimed(h["lead"])}</p><ul class="ticks">{ticks}</ul>'
            '<div class="buy">'
            f'<div class="row"><span class="price">{self.claimed(h["price"])}</span><span class="per">{self.claimed(h["per"])}</span></div>'
            f'<p class="set">{self.claimed(h["set"])}</p>'
            + self.cta("hero")
            + f'<p class="callback"><span class="dot" aria-hidden="true"></span><b>{self.claimed(L["callback"])}</b></p>'
            f'<div class="delivery">{chips}</div></div>'
            f'<p class="legal">{self.claimed(h["legal"])}</p></div>'
            "</div></section>"
        )
        trust = (
            '<div class="trust gut"><div class="wrap"><ul>'
            + "".join(
                f'<li>{self.icon(t["icon"])}<span><b>{self.ui(t["b"])}</b><small>{self.claimed(t["s"])}</small></span></li>'
                for t in L["trust"]
            )
            + "</ul></div></div>"
        )
        u = L["utro"]
        scenes = "".join(
            f'<li class="scene"><span class="time">{self.ui(s["n"])}</span><p>{self.ui(s["t"])}</p></li>' for s in u["scenes"]
        )
        utro = self.sec(
            "utro", u["kicker"], u["h2"],
            f'<ul class="scenes">{scenes}</ul><p class="lead turn">{self.ui(u["turn"])}</p>' + self.cta_row("utro"),
        )
        f = L["forma"]
        was = "".join(f'<li><span class="x" aria-hidden="true">×</span><span>{self.tx(w)}</span></li>' for w in f["was"])
        nums = "".join(
            f'<div class="num"><b>{self.claimed(n["b"])}</b><span>{self.ui(n["s"])}</span></div>' for n in f["nums"]
        )
        forma = self.sec(
            "forma", f["kicker"], f["h2"],
            f'<p class="lead">{self.ui(f["lead"])}</p><div class="split"><ul class="was">{was}</ul>'
            f'<div><div class="nums">{nums}</div><p class="note">{self.claimed(f["note"])}</p></div></div>'
            + self.cta_row("forma"),
        )
        k = L["kletki"]
        props = "".join(f'<li>{self.TICK}<span>{self.claimed(p)}</span></li>' for p in k["props"])
        kletki = self.sec(
            "kletki", k["kicker"], k["h2"],
            f'<div class="split"><div><p class="lead">{self.claimed(k["p1"])}</p><p class="p2">{self.claimed(k["p2"])}</p></div>'
            f'<div class="propcard"><ul class="props">{props}</ul><p class="small">{self.claimed(k["props_note"])}</p></div></div>',
            "tintband",
        )
        n = L["nauka"]
        d = self.site["dokumenty"]
        cards = "".join(
            f'<li class="card"><p class="tagrow"><span class="tag">{self.ui(c["tag"])}</span><span class="where">{self.ui(c["where"])}</span></p>'
            f'<p>{self.claimed(c["p"])}</p><p class="ref">{self.ui(c["ref"])}. '
            f'<a href="https://doi.org/{esc(c["doi"])}" rel="noopener">{self.ui(d["doi_label"])} {esc(c["doi"])}</a></p></li>'
            for c in n["cards"]
        )
        nauka = self.sec(
            "nauka", n["kicker"], n["h2"],
            f'<p class="lead">{self.claimed(n["lead"])}</p><ul class="cards">{cards}</ul>'
            f'<div class="honest"><h3>{self.ui(n["honest_h3"])}</h3><p>{self.claimed(n["honest"])}</p></div>'
            + self.cta_row("nauka", self.lp["cta_course"]),
        )
        r, ks = L["ritual"], self.site["kak"]
        steps = "".join(
            f'<li><b>{self.ui(s["title"])}</b><span>{self.claimed(s["p"])}</span></li>' for s in ks["steps"]
        )
        ritual = self.sec(
            "ritual", r["kicker"], r["h2"],
            f'<ol class="steps4">{steps}</ol><p class="note">{self.claimed(r["course"])}</p>'
            f'<p><a href="{base}/kak-prinimat" data-cta="howto-link">{self.ui(r["more"])}</a></p>' + self.cta_row("ritual"),
            "tintband",
        )
        pr = L["proof"]
        items = "".join(
            f'<li><b>{self.ui(i["b"])}</b><span>{self.claimed(i["s"])}</span></li>' for i in pr["items"]
        )
        proof = self.sec("dokumenty", pr["kicker"], pr["h2"], f'<ul class="prooflist">{items}</ul>')
        o = L["offer"]
        packs = ""
        for p in o["packs"]:
            old = f'<s>{self.ui(p["old"])}</s>' if p.get("old") else ""
            badge = f'<span class="disc">{self.ui(p["badge"])}</span>' if p.get("badge") else ""
            packs += (
                f'<div class="pack{" best" if badge else ""}">{badge}<p class="pname">{self.ui(p["name"])}</p>'
                f'<p class="pprice">{self.claimed(p["price"])} {old}</p><p class="pnote">{self.claimed(p["note"])}</p>'
                f'<a class="btn pick" href="#order-form" data-pack="{esc(p["id"])}" data-cta="pack-{esc(p["id"])}">{self.ui(o["pick"])}</a></div>'
            )
        incl = "".join(f"<li>{self.TICK}<span>{self.claimed(i)}</span></li>" for i in o["incl"])
        after = "".join(f"<li>{self.claimed(a)}</li>" for a in o["after"])
        offer = (
            '<section class="block gut offer" id="zayavka" data-sec="zayavka"><div class="wrap">'
            f'<p class="kicker">{self.ui(o["kicker"])}</p><h2>{self.ui(o["h2"])}</h2>'
            f'<div class="packs">{packs}</div>'
            '<div class="offer-card"><div>'
            f'<h3>{self.ui(o["incl_h3"])}</h3><ul class="incl">{incl}</ul>'
            f'<h3>{self.ui(o["after_h3"])}</h3><ol class="steps3">{after}</ol></div>'
            + self.lp_form()
            + "</div></div></section>"
        )
        b = L["blizkim"]
        blizkim = self.sec(
            "blizkim", b["kicker"], b["h2"],
            f'<p class="lead">{self.claimed(b["p"])}</p><div class="cta-row">{self.cta("blizkim", b["btn"])}</div>',
        )
        faq = "".join(
            f'<details><summary>{self.ui(q["q"])}</summary><p>{self.claimed(q["a"])}</p></details>' for q in L["faq"]
        )
        faqsec = self.sec("voprosy", L["faq_kicker"], L["faq_h2"], f'<div class="faq">{faq}</div>' + self.cta_row("faq"), "tintband")
        fi = L["final"]
        final = (
            '<section class="block gut final" data-sec="final"><div class="wrap">'
            f'<h2>{self.ui(fi["h2"])}</h2><p class="lead">{self.claimed(fi["p"])}</p>'
            f'<div class="cta-row center">{self.cta("final")}</div>'
            f'<p class="call">{self.ui(fi["or_call"])}{self.phone_link()}</p></div></section>'
        )
        bar = (
            f'<div class="bar"><div><b>{self.claimed(h["price"])}</b><span>{self.claimed(L["bar_sub"])}</span></div>'
            f'{self.cta("bar", L["cta"])}</div>'
        )
        ui = self.site["ui"]
        links = "".join(f'<a href="#{esc(x["id"])}">{self.ui(x["t"])}</a>' for x in L["nav"])
        header = (
            f'<a class="skip" href="#main">{self.ui(ui["skip"])}</a>'
            f'<header class="top gut"><div class="wrap"><a class="brand" href="{base}/">{self.ui(ui["brand"])}</a>'
            f'<nav aria-label="{self.ui(ui["nav_label"])}">{links}</nav>{self.cta("header", L["cta"])}</div></header>'
        )
        body = (
            header + '<main id="main">' + hero + trust + utro + forma + kletki + nauka + ritual + proof + offer
            + blizkim + faqsec + final + "</main>" + self.footer() + bar
            + f'<script src="{base}/static/app.js" defer></script></body></html>'
        )
        m = L["meta"]
        return self.head(self.ui(m["title"]), self.claimed(m["description"]), "landing.css") + '<body class="lp">' + body

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
        pages = {"index.html": self.landing(), "kak-prinimat.html": self.index(), "policy.html": self.policy(), "spasibo.html": self.thanks()}
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "static").mkdir(parents=True)
        for name, text in pages.items():
            (self.out / name).write_text(text, encoding="utf-8")
        shutil.copytree(ROOT / "static", self.out / "static", dirs_exist_ok=True)
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
    if not b.cfg.get("price_text"):
        print("Не задано: price_text (цена на странице не показана).")
    if not b.cfg["operator"].get("inn"):
        print("Не задано: operator.inn и operator.ogrn (в политике не указаны).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
