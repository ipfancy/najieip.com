#!/usr/bin/env python3
# 2026-10-12 第41周 i18n 生成 — ART-2026-0101 拓竹 / Stratasys（复用 1003 工厂）
import json, os, re, sys, urllib.request

ENV = os.path.expanduser("~/.hermes/.env")
KEY = None
for line in open(ENV):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("no key")

MD = os.path.expanduser("~/wiki/digital-employees/articles/bambu-stratasys-fto-decision-tree-20261004.md")
raw = open(MD, encoding="utf-8").read()
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
body = body.replace("# 同一专利族，美国判赔2760万美元，欧洲驳回禁令", "").strip()
body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()

SLUG = "bambu-stratasys-fto-decision-tree-20261004"
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"

TERMS = """专利术语对照（必须严格使用）:
专利族=patent family / famille de brevets
故意侵权=willful infringement / contrefaçon délibérée
临时禁令=preliminary injunction / injonction provisoire
永久禁售令=permanent injunction (sales ban) / injonction permanente (interdiction de vente)
统一专利法院(UPC)=Unified Patent Court (UPC) / Tribunal unifié du brevet (TUP)
海牙地方分院=Hague Local Division / division locale de La Haye
自由实施检索(FTO)=freedom to operate (FTO) / liberté d'exploitation (FTO)
无效宣告=invalidation / annulation (nullité)
权利要求=claims / revendications
权利要求解释=claim construction / interprétation des revendications
三倍赔偿=treble damages / dommages-intérêts triplés
保护范围=scope of protection / portée de la protection
地域性=territoriality / territorialité
上诉=appeal / appel
管辖权抗辩=jurisdictional challenge / exception d'incompétence
专利检索=patent search / recherche de brevets
出海企业=Chinese companies going global / entreprises chinoises à l'international
海关/CBP 等不涉及
模型社区=model-sharing community / communauté de partage de modèles
版权连带=copyright exposure / risque de contrefaçon de droit d'auteur
母子公司架构=parent-subsidiary structure / structure mère-filiale
"""

PROMPT_EN = """You are a senior Chinese-English legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality English suitable for an English-language law firm blog.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for section headings, <p> for paragraphs, and a properly formed <table> (with <thead><tr><th> and <tbody>) for the single markdown table in the source (3 columns: jurisdiction / outcome / tools available).
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**". NEVER include the trailing 合集 comment lines.
4. Keep ALL numbers, currency, dates, patent numbers and proper names EXACTLY as in the source: 2760 (万美元 = USD 27.6 million), 8280, US 9,421,713, US 7,555,357, EP2964450, 14.2 million / 10.6 million / 2.8 million USD split, March 2027, 3.62 million units and RMB 9.6 billion exports in H1 2026, 337 (USITC Section 337), September 17, April 2026. Do not round or convert.
5. Keep the author's direct, opinionated voice.
6. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
7. title: natural English headline (not literal word-for-word).

Chinese article:
""" + body

PROMPT_FR = """You are a senior Chinese-French legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality French suitable for a French-language law firm blog.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for section headings, <p> for paragraphs, and a properly formed <table> (with <thead><tr><th> and <tbody>) for the single markdown table in the source (3 columns).
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**".
4. Keep ALL numbers, currency, dates, patent numbers and proper names EXACTLY as in the source: 2760 (万美元 = 27,6 millions USD), 8280, US 9,421,713, US 7,555,357, EP2964450, 14,2 / 10,6 / 2,8 millions USD, mars 2027, 3,62 millions d'unités et 9,6 milliards RMB d'exportations au 1er semestre 2026, 337 (article 337 de l'USITC), 17 septembre, avril 2026. Do not round.
5. Keep the author's direct, opinionated voice.
6. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
7. title: natural French headline.
8. French typography: use &#x27; never a raw apostrophe inside HTML attribute values; use proper French punctuation spacing.

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


out = {}
TOKENS = ["2760", "9,421,713", "7,555,357", "EP2964450", "337", "2027"]
for lang, prompt in (("en", PROMPT_EN), ("fr", PROMPT_FR)):
    txt = call(prompt)
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    d = json.loads(txt)
    hb = d["html_body"]
    assert "<h1" not in hb, f"{lang}: h1 leaked"
    assert "**" not in hb, f"{lang}: markdown leaked"
    assert "<!--" not in hb, f"{lang}: comment leaked"
    missing = [t for t in TOKENS if t not in hb]
    if missing:
        print(f"  WARN {lang}: tokens not literal -> {missing}")
    d["html_body"] = hb
    out[lang] = d
    print(f"--- {lang.upper()} ---")
    print("TITLE:", d["title"])
    print("DESC:", d["description"])
    print("KW:", d["keywords"])
    print("HTML_LEN:", len(hb), "| h2:", hb.count("<h2"), "| table:", hb.count("<table"))
    print("SNIP:", hb[:400].replace("\n", " "))

json.dump(out, open("/Users/ziganghe/.hermes/cache/scratch/i18n_1012.json", "w"), ensure_ascii=False, indent=1)
print("SAVED")
