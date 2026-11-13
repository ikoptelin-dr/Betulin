"""Автотесты сайта. Запуск: python3 -m unittest discover -s tests -v (из папки site/)."""
import copy
import csv
import http.client
import json
import re
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import server  # noqa: E402


def copy_content(tmp):
    dst = Path(tmp) / "content"
    shutil.copytree(ROOT / "content", dst)
    return dst


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def builder(self, content=None, cfg=None):
        cfg_path = Path(self.tmp) / "config.json"
        cfg_path.write_text(json.dumps(cfg or json.loads((ROOT / "config.json").read_text(encoding="utf-8")), ensure_ascii=False), encoding="utf-8")
        return build.Builder(content or ROOT / "content", cfg_path, Path(self.tmp) / "dist", Path(self.tmp) / "docs")

    def test_builds_and_uses_only_published_claims(self):
        b = self.builder()
        used = b.build()
        self.assertTrue(used)
        for i in used:
            c = b.claims[i]
            self.assertTrue(c["publish"], i)
            self.assertIn(c["status"], b.allowed, i)
            self.assertTrue(c["source"], i)
        for name in ("index.html", "kak-prinimat.html", "policy.html", "spasibo.html"):
            self.assertTrue((Path(self.tmp) / "dist" / name).exists(), name)

    def test_build_fails_on_unpublished_claim(self):
        content = copy_content(self.tmp)
        site = json.loads((content / "site.ru.json").read_text(encoding="utf-8"))
        site["hero"]["lead"] = {"t": "Впервые его можно просто выпить", "c": ["X03"]}
        (content / "site.ru.json").write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(build.ClaimError):
            self.builder(content).build()

    def test_build_fails_on_claim_text_without_numbers(self):
        content = copy_content(self.tmp)
        site = json.loads((content / "site.ru.json").read_text(encoding="utf-8"))
        site["hero"]["lead"] = "Сильное утверждение без источника"
        (content / "site.ru.json").write_text(json.dumps(site, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(build.ClaimError):
            self.builder(content).build()

    def test_build_fails_on_unknown_status(self):
        content = copy_content(self.tmp)
        cl = json.loads((content / "claims.json").read_text(encoding="utf-8"))
        for c in cl["claims"]:
            if c["id"] == "C01":
                c["status"] = "НЕТ"
        (content / "claims.json").write_text(json.dumps(cl, ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(build.ClaimError):
            self.builder(content).build()

    def test_every_product_text_in_page_carries_claims(self):
        """Строки интерфейса не содержат слов о действии продукта."""
        site = json.loads((ROOT / "content" / "site.ru.json").read_text(encoding="utf-8"))
        ui_texts = []

        def walk(o, key=""):
            if isinstance(o, dict):
                if "t" in o and "c" in o:
                    return
                for k, v in o.items():
                    walk(v, k)
            elif isinstance(o, list):
                for v in o:
                    walk(v, key)
            elif isinstance(o, str) and not key.startswith("_"):
                ui_texts.append(o)

        walk(site)
        walk(json.loads((ROOT / "content" / "landing.ru.json").read_text(encoding="utf-8")))
        banned = re.compile(r"исцел|лечит|излеч|помога|восстанов|очищ|ДНК|впервые|единственн|100\s?%", re.I)
        # политика и ошибки содержат слова про лекарства и удаление данных, проверяем остальное
        bad = [t for t in ui_texts if banned.search(t) and "лекарств" not in t]
        self.assertEqual(bad, [])

    def test_no_external_resources_or_trackers(self):
        b = self.builder()
        b.build()
        for page in (Path(self.tmp) / "dist").glob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotRegex(text, r'<script[^>]+src="https?://')
            self.assertNotRegex(text, r'<link[^>]+href="https?://')
            self.assertNotRegex(text, r'<img[^>]+src="https?://')
            self.assertNotIn("metrika", text.lower())
            self.assertNotIn("google", text.lower())
            for url in re.findall(r'href="(https?://[^"]+)"', text):
                self.assertTrue(url.startswith("https://doi.org/"), url)

    def test_font_size_is_at_least_18px(self):
        css = (ROOT / "static" / "style.css").read_text(encoding="utf-8")
        base = int(re.search(r"--base:\s*(\d+)px", css).group(1))
        self.assertGreaterEqual(base, 18)
        sizes = [float(x) for x in re.findall(r"font-size:\s*([\d.]+)rem", css)]
        self.assertGreaterEqual(min(sizes) * base, 16)  # самая мелкая подпись не меньше 16px

    def test_required_disclaimer_present_on_every_page(self):
        b = self.builder()
        b.build()
        for name in ("index.html", "kak-prinimat.html", "policy.html", "spasibo.html"):
            text = (Path(self.tmp) / "dist" / name).read_text(encoding="utf-8")
            self.assertIn("Не является лекарственным средством", text, name)

    def test_max_and_order_blocks_follow_config(self):
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        text = self.builder(cfg=cfg).index()
        self.assertNotIn("/q/site", text)
        self.assertNotIn("Заказать на маркетплейсе", text)
        cfg["max_bot_link"] = "https://max.example/bot"
        cfg["order_url"] = "https://market.example/card"
        text = self.builder(cfg=cfg).index()
        self.assertIn("/q/site", text)
        self.assertIn("https://market.example/card", text)

    def test_documents_listed_only_when_files_exist(self):
        b = self.builder()
        self.assertNotIn("sgr.pdf", b.index())
        docs = Path(self.tmp) / "docs"
        docs.mkdir()
        (docs / "sgr.pdf").write_bytes(b"%PDF-1.4")
        self.assertIn("docs/sgr.pdf", self.builder().index())

    def test_landing_has_form_research_caveat_and_no_fake_proof(self):
        text = self.builder().landing()
        self.assertEqual(text.count('name="consent"'), 1)
        self.assertNotRegex(text, r'name="consent"[^>]*checked')
        self.assertIn("не переносятся на человека напрямую", text)
        self.assertIn("не обещаем", text)
        self.assertNotRegex(text, r"отзыв|рейтинг|покупател[ейя] уже|гарантир", )
        self.assertNotIn("style=", text)

    def test_fonts_are_self_hosted_and_update_badge_removed(self):
        css = (ROOT / "static" / "style.css").read_text(encoding="utf-8")
        self.assertNotIn("googleapis", css)
        self.assertNotIn("gstatic", css)
        for f in re.findall(r"url\(fonts/([^)]+)\)", css):
            self.assertTrue((ROOT / "static" / "fonts" / f).exists(), f)
        for page in (self.builder().landing(), self.builder().index()):
            self.assertNotIn("обновлён", page)
            self.assertNotIn("13.11.2026", page)

    def test_landing_sells_with_offer_and_many_ctas(self):
        text = self.builder().landing()
        self.assertGreaterEqual(text.count('href="#zayavka"'), 8)
        for must in ("2 190 ₽", "3 504 ₽", "−20%", "Бесплатная доставка", "за 3 минуты", "RU.77.99.11.003.R.003611.10.20",
                     'name="pack"', 'name="via"', 'class="bar"', "leaf.webp", "Не является лекарственным средством"):
            self.assertIn(must, text, must)
        self.assertEqual(text.count('name="consent"'), 1)
        self.assertNotRegex(text, r'name="consent"[^>]*checked')

    def test_landing_typography_single_family_max_700(self):
        for name in ("landing.css", "style.css"):
            css = (ROOT / "static" / name).read_text(encoding="utf-8")
            self.assertNotIn("Golos", css, name)
            weights = [int(w) for w in re.findall(r"font-weight:\s*(\d{3})", css)]
            weights += [int(w) for w in re.findall(r"font:\s*(\d{3})\s", css)]
            self.assertTrue(weights and max(weights) <= 700, (name, weights))
            self.assertNotRegex(css, r"letter-spacing:\s*-", name)
            for f in re.findall(r"url\((?:fonts|img)/([^)]+)\)", css):
                self.assertTrue(list((ROOT / "static").rglob(f)), f)
        self.assertIn("img/label-front.webp", (ROOT / "static" / "landing.css").read_text(encoding="utf-8"))

    def test_consent_checkbox_is_not_prechecked(self):
        text = self.builder().index()
        self.assertRegex(text, r'name="consent"[^>]*required')
        self.assertNotRegex(text, r'name="consent"[^>]*checked')


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        cls.cfg_path = Path(cls.tmp) / "config.json"
        cls.cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        cls.dist = Path(cls.tmp) / "dist"
        build.Builder(ROOT / "content", cls.cfg_path, cls.dist, Path(cls.tmp) / "docs").build()
        cls.data = Path(cls.tmp) / "data"
        cls.start()

    @classmethod
    def start(cls):
        cls.srv, cls.app = server.make_server("127.0.0.1", 0, cls.dist, cls.data, cls.cfg_path, ROOT / "content")
        cls.port = cls.srv.server_address[1]
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.tmp, True)

    def req(self, method, path, body=None, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        c.request(method, path, body=body, headers=headers or {})
        r = c.getresponse()
        data = r.read()
        c.close()
        return r, data

    def post_order(self, fields):
        from urllib.parse import urlencode
        body = urlencode(fields)
        return self.req("POST", "/betula-aqua/order", body, {"Content-Type": "application/x-www-form-urlencoded"})

    def rows(self, name):
        p = self.data / name
        if not p.exists():
            return []
        with p.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_pages_open(self):
        for path in ("/betula-aqua/", "/betula-aqua/kak-prinimat", "/betula-aqua/policy", "/betula-aqua/spasibo", "/betula-aqua/static/style.css", "/betula-aqua/health"):
            r, _ = self.req("GET", path)
            self.assertEqual(r.status, 200, path)

    def test_root_and_bare_prefix_redirect(self):
        r, _ = self.req("GET", "/")
        self.assertEqual(r.status, 302)
        self.assertEqual(r.getheader("Location"), "/betula-aqua/")
        r, _ = self.req("GET", "/betula-aqua")
        self.assertEqual(r.status, 302)

    def test_security_headers(self):
        r, _ = self.req("GET", "/betula-aqua/")
        self.assertIn("default-src 'self'", r.getheader("Content-Security-Policy"))
        self.assertEqual(r.getheader("X-Content-Type-Options"), "nosniff")

    def test_path_traversal_blocked(self):
        for path in ("/betula-aqua/static/../../config.json", "/betula-aqua/static/%2e%2e/%2e%2e/config.json", "/betula-aqua/docs/../../server.py"):
            r, data = self.req("GET", path)
            self.assertEqual(r.status, 404, path)
            self.assertNotIn(b"base_url", data)

    def test_qr_redirect_to_site_with_source_mark(self):
        before = len(self.rows("visits.csv"))
        r, _ = self.req("GET", "/betula-aqua/q/trifold")
        self.assertEqual(r.status, 302)
        self.assertEqual(r.getheader("Location"), "/betula-aqua/?s=trifold")
        rows = self.rows("visits.csv")
        self.assertEqual(len(rows), before + 1)
        self.assertEqual(rows[-1]["channel"], "trifold")
        self.assertEqual(rows[-1]["target"], "landing")

    def test_label_qr_goes_to_howto_page(self):
        r, _ = self.req("GET", "/betula-aqua/q/label")
        self.assertEqual(r.getheader("Location"), "/betula-aqua/kak-prinimat?s=label")
        r, _ = self.req("GET", "/betula-aqua/q/site")
        self.assertEqual(r.getheader("Location"), "/betula-aqua/?s=site")

    def test_qr_unknown_and_invalid_codes(self):
        r, _ = self.req("GET", "/betula-aqua/q/typo-code")
        self.assertEqual(r.status, 302)
        self.assertEqual(r.getheader("Location"), "/betula-aqua/?s=unknown")
        r, _ = self.req("GET", "/betula-aqua/q/BAD%20CODE")
        self.assertEqual(r.status, 404)
        r, _ = self.req("GET", "/betula-aqua/q/" + "a" * 60)
        self.assertEqual(r.status, 404)

    def test_visit_log_has_no_personal_data(self):
        self.req("GET", "/betula-aqua/q/label", headers={"User-Agent": "TestAgent/1.0", "X-Forwarded-For": "203.0.113.9"})
        text = (self.data / "visits.csv").read_text(encoding="utf-8")
        self.assertNotIn("TestAgent", text)
        self.assertNotIn("203.0.113.9", text)
        self.assertNotIn("127.0.0.1", text)

    def test_qr_goes_to_max_when_configured(self):
        self.app.cfg["max_bot_link"] = "https://max.example/bot"
        self.app.cfg["max_start_param"] = "start"
        try:
            r, _ = self.req("GET", "/betula-aqua/q/site")
            self.assertEqual(r.status, 302)
            self.assertEqual(r.getheader("Location"), "https://max.example/bot?start=site")
            self.app.cfg["max_bot_link"] = "https://max.example/bot?x=1"
            r, _ = self.req("GET", "/betula-aqua/q/site")
            self.assertEqual(r.getheader("Location"), "https://max.example/bot?x=1&start=site")
            r, _ = self.req("GET", "/betula-aqua/q/trifold")
            self.assertEqual(r.getheader("Location"), "/betula-aqua/?s=trifold")
        finally:
            self.app.cfg["max_bot_link"] = ""

    def test_order_requires_consent(self):
        before = len(self.rows("leads.csv"))
        r, data = self.post_order({"name": "Анна", "phone": "+7 923 000 11 22"})
        self.assertEqual(r.status, 400)
        self.assertIn("согласие".encode("utf-8"), data)
        self.assertEqual(len(self.rows("leads.csv")), before)

    def test_order_rejects_bad_phone(self):
        before = len(self.rows("leads.csv"))
        r, _ = self.post_order({"name": "Анна", "phone": "123", "consent": "yes"})
        self.assertEqual(r.status, 400)
        self.assertEqual(len(self.rows("leads.csv")), before)

    def test_order_saved_with_consent_and_source(self):
        r, _ = self.post_order({"name": "Анна", "phone": "+7 (923) 000-11-22", "consent": "yes", "source": "label"})
        self.assertEqual(r.status, 303)
        self.assertEqual(r.getheader("Location"), "/betula-aqua/spasibo")
        last = self.rows("leads.csv")[-1]
        self.assertEqual(last["phone_digits"], "79230001122")
        self.assertEqual(last["source"], "label")
        self.assertEqual(last["consent"], "yes")

    def test_order_saves_pack_and_contact_method(self):
        self.post_order({"name": "Олег", "phone": "79230001133", "consent": "yes", "pack": "2", "via": "max"})
        last = self.rows("leads.csv")[-1]
        self.assertEqual((last["pack"], last["via"]), ("2", "max"))
        self.post_order({"name": "Олег", "phone": "79230001134", "consent": "yes", "pack": "99", "via": "fax"})
        last = self.rows("leads.csv")[-1]
        self.assertEqual((last["pack"], last["via"]), ("1", "call"))

    def test_events_counted_without_personal_data(self):
        from urllib.parse import urlencode
        h = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Spy/1.0"}
        r, _ = self.req("POST", "/betula-aqua/e", urlencode({"ev": "cta:hero", "s": "trifold"}), h)
        self.assertEqual(r.status, 204)
        r, _ = self.req("POST", "/betula-aqua/e", urlencode({"ev": "scroll:50", "s": "<x>"}), h)
        self.assertEqual(r.status, 204)
        rows = self.rows("events.csv")
        self.assertEqual((rows[-2]["event"], rows[-2]["source"]), ("cta:hero", "trifold"))
        self.assertEqual((rows[-1]["event"], rows[-1]["source"]), ("scroll:50", ""))
        text = (self.data / "events.csv").read_text(encoding="utf-8")
        self.assertNotIn("Spy", text)
        self.assertNotIn("127.0.0.1", text)
        for bad in ("evil:1", "cta:<script>", "cta:" + "a" * 50):
            r, _ = self.req("POST", "/betula-aqua/e", urlencode({"ev": bad}), h)
            self.assertEqual(r.status, 400, bad)

    def test_order_honeypot_not_saved(self):
        before = len(self.rows("leads.csv"))
        r, _ = self.post_order({"name": "Бот", "phone": "79230001122", "consent": "yes", "website": "http://spam"})
        self.assertEqual(r.status, 303)
        self.assertEqual(len(self.rows("leads.csv")), before)

    def test_order_csv_injection_neutralised(self):
        self.post_order({"name": "=HYPERLINK(\"http://x\")", "phone": "79230001122", "consent": "yes", "source": "<script>"})
        last = self.rows("leads.csv")[-1]
        self.assertTrue(last["name"].startswith("'="))
        self.assertEqual(last["source"], "")

    def test_order_oversized_body_rejected(self):
        r, _ = self.post_order({"name": "x" * 5000, "phone": "79230001122", "consent": "yes"})
        self.assertEqual(r.status, 400)

    def test_get_order_not_allowed(self):
        r, _ = self.req("GET", "/betula-aqua/order")
        self.assertEqual(r.status, 404)


class QrFilesTests(unittest.TestCase):
    def test_every_channel_has_qr_pointing_to_its_code(self):
        try:
            import cv2
        except ImportError:
            self.skipTest("opencv не установлен")
        cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        channels = json.loads((ROOT / "content" / "channels.json").read_text(encoding="utf-8"))["channels"]
        det = cv2.QRCodeDetector()
        for c in channels:
            img = cv2.imread(str(ROOT / "qr" / f"{c['code']}.png"))
            self.assertIsNotNone(img, c["code"])
            text, _, _ = det.detectAndDecode(img)
            self.assertEqual(text, f"{cfg['base_url'].rstrip('/')}/q/{c['code']}")

    def test_channel_codes_unique_and_valid(self):
        channels = json.loads((ROOT / "content" / "channels.json").read_text(encoding="utf-8"))["channels"]
        codes = [c["code"] for c in channels]
        self.assertEqual(len(codes), len(set(codes)))
        for code in codes:
            self.assertRegex(code, r"^[a-z0-9_-]{1,40}$")


class PurgeTests(unittest.TestCase):
    def test_old_rows_and_erased_phone_are_removed(self):
        from datetime import datetime, timedelta, timezone
        import purge_leads
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        now = datetime(2026, 11, 13, tzinfo=timezone.utc)
        fmt = "%Y-%m-%dT%H:%M:%SZ"
        rows = [
            [(now - timedelta(days=400)).strftime(fmt), "Старая", "79230000001", "label", "yes"],
            [(now - timedelta(days=10)).strftime(fmt), "Свежая", "79230000002", "label", "yes"],
            [(now - timedelta(days=5)).strftime(fmt), "Отозвала", "79230000003", "trifold", "yes"],
        ]
        with (tmp / "leads.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts_utc", "name", "phone_digits", "source", "consent"])
            w.writerows(rows)
        removed = purge_leads.purge(tmp, 12, erase_phone="79230000003", now=now)
        self.assertEqual(removed, 2)
        with (tmp / "leads.csv").open(encoding="utf-8") as f:
            left = list(csv.DictReader(f))
        self.assertEqual([r["name"] for r in left], ["Свежая"])

    def test_missing_file_is_fine(self):
        import purge_leads
        self.assertEqual(purge_leads.purge(tempfile.mkdtemp(), 12), 0)


if __name__ == "__main__":
    unittest.main()
