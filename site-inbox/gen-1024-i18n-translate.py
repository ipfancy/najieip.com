#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-24 第43周 i18n 翻译 — ART-2026-0103 腾冲燃气案·六条清单（复用 1003/1012/1017 工厂）"""
import json, os, re, sys, urllib.request

ENV = os.path.expanduser("~/.hermes/.env")
KEY = None
for line in open(ENV):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("no key")

MD = os.path.expanduser("~/wiki/digital-employees/articles/20261006-mili-gas-post-judgment-six-checklist.md")
raw = open(MD, encoding="utf-8").read()
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
body = body.replace("# 赢了官司还被点名6条：这份合规清单抄了就能用", "").strip()
body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()

SLUG = "20261006-mili-gas-post-judgment-six-checklist"
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"

TERMS = """反垄断=antitrust / droit de la concurrence
滥用市场支配地位=abuse of dominant market position / abus de position dominante
附加不合理交易条件=imposing unreasonable trading conditions / imposition de conditions commerciales déraisonnables
拒绝交易=refusal to deal / refus de contracter
不公平高价=unfair pricing / prix injustement élevés
偏差结算款=deviation settlement payment / paiement de règlement des écarts
提前申报用气计划=advance declaration of gas consumption plans / déclaration préalable des plans de consommation de gaz
停供=suspension of supply / suspension de la fourniture
公用事业=public utility / service public
判项=operative part of the judgment (the order) / dispositif du jugement
说理部分=reasoning section / motifs
司法建议=judicial suggestion / suggestion judiciaire
强制执行力=enforceability / force exécutoire
既判力=res judicata / autorité de la chose jugée
留痕=evidence retention / conservation des preuves
台账=ledger / registre
对账=reconciliation / rapprochement comptable
应激整改=reactive remediation under litigation pressure / mise en conformité réactive sous la pression du litige
合规建设=proactive compliance building / construction proactive de la conformité
最高人民法院=Supreme People's Court (SPC) / Cour populaire suprême
案号=(2025) 最高法知民终950号 = (2025) SPC Zhi Min Zhong No. 950 / (2025) SPC Zhi Min Zhong n° 950
腾冲=Tengchong, Yunnan / Tengchong (Yunnan)
"""

NUM_EN = """Keep ALL numbers, dates and amounts EXACTLY, converting 万 (10,000) to the full figure:
- (2025) SPC Zhi Min Zhong No. 950
- six items (六条)
- RMB 390,000 (39万元) and RMB 13,000 (1.3万元)
- 22 October 2024, 8:40 am, 9:30 am, 50 minutes
- 30 December 2024, 12 industrial enterprises
- 15 days, 3 consecutive months, three and a half years, three volume adjustments
Do not round or omit."""

NUM_FR = """Keep ALL numbers, dates and amounts EXACTLY, converting 万 (10,000) to the full figure:
- (2025) SPC Zhi Min Zhong n° 950
- six items (六条)
- 390 000 yuans RMB (39万元) and 13 000 yuans (1,3万元 → 13 000)
- 22 octobre 2024, 8 h 40, 9 h 30, 50 minutes
- 30 décembre 2024, 12 entreprises industrielles
- 15 jours, 3 mois consécutifs, trois ans et demi, trois ajustements de volume
Do not round or omit."""

PROMPT_EN = """You are a senior Chinese-English legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality English suitable for an English-language law firm blog. Keep the author's direct, opinionated, first-person voice.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>.
3. Use <h2> for the FIVE section headings (the five sections starting with 一、二、三、四、五). Use <p> for paragraphs and <ul>/<li> for the six checklist bullets.
4. The article contains ONE table (6 rows: # / SPC requirement / action / evidence carrier). Render it as <table> with <thead><tr><th>...</th></tr></thead> and <tbody>. Preserve all six rows and all columns.
5. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**".
6. """ + NUM_EN + """
7. Drop the WeChat-Official-Account call-to-action and the contact-info block (phone/email/WeChat). Keep the sentence referring to the tool on the Mili website (deviation settlement exposure calculator) and the invitation to leave comments.
8. Keep the author's core-opinion blockquote as <blockquote><p>...</p></blockquote>, with the signature "He Zigang | Intellectual Property Lawyer | Aipunajie · Mili · Najie (20 years in practice, AI-native hybrid organisation practitioner)".
9. Keep the author's own disclaimer sentence (but not the AI-assistance line).
10. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
11. title: natural English headline (not literal word-for-word).

Chinese article:
""" + body

PROMPT_FR = """You are a senior Chinese-French legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality French suitable for a French-language law firm blog. Keep the author's direct, opinionated, first-person voice.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>.
3. Use <h2> for the FIVE section headings (the five sections starting with 一、二、三、四、五). Use <p> for paragraphs and <ul>/<li> for the six checklist bullets.
4. The article contains ONE table (6 rows: # / SPC requirement / action / evidence carrier). Render it as <table> with <thead><tr><th>...</th></tr></thead> and <tbody>. Preserve all six rows and all columns.
5. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**".
6. """ + NUM_FR + """
7. Drop the WeChat-Official-Account call-to-action and the contact-info block. Keep the sentence referring to the tool on the Mili website and the invitation to leave comments.
8. Keep the author's core-opinion blockquote as <blockquote><p>...</p></blockquote>, with the signature "He Zigang | Avocat en propriété intellectuelle | Aipunajie · Mili · Najie (20 ans de pratique, praticien d'organisation hybride native de l'IA)".
9. Keep the author's own disclaimer sentence (but not the AI-assistance line).
10. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
11. title: natural French headline.
12. French typography: use &#x27; never a raw apostrophe inside HTML attribute values.

Chinese article:
""" + body


def call(prompt):
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"},
        }).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"},
    )
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    return r["choices"][0]["message"]["content"]


TOKENS = {
    "en": ["950", "390,000", "13,000", "22 October 2024", "12"],
    "fr": ["950", "390 000", "13 000", "22 octobre 2024", "12"],
}

out = {}
for lang, prompt in (("en", PROMPT_EN), ("fr", PROMPT_FR)):
    txt = call(prompt)
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    d = json.loads(txt)
    hb = d["html_body"]
    assert "<h1" not in hb, f"{lang}: h1 leaked"
    assert "**" not in hb, f"{lang}: markdown leaked"
    assert "<!--" not in hb, f"{lang}: comment leaked"
    missing = [t for t in TOKENS[lang] if t not in hb]
    print(f"  NUMCHECK {lang}: missing={missing}")
    d["html_body"] = hb
    out[lang] = d
    print(f"--- {lang.upper()} ---")
    print("TITLE:", d["title"])
    print("DESC:", d["description"])
    print("KW:", d["keywords"])
    print("HTML_LEN:", len(hb), "| h2:", hb.count("<h2"), "| table:", hb.count("<table"), "| tr:", hb.count("<tr"))

os.makedirs(os.path.expanduser("~/.hermes/cache/scratch"), exist_ok=True)
json.dump(out, open(os.path.expanduser("~/.hermes/cache/scratch/i18n_1024.json"), "w"), ensure_ascii=False, indent=1)
print("SAVED")
