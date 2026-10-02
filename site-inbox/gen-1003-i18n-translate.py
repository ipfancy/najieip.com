#!/usr/bin/env python3
# 2026-10-03 第39周 i18n 生成 — ART-2026-0097 德国实用新型
import json, os, re, sys, urllib.request

ENV = os.path.expanduser("~/.hermes/.env")
KEY = None
for line in open(ENV):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("no key")

MD = os.path.expanduser("~/wiki/digital-employees/articles/20260928-german-utility-model-offense.md")
raw = open(MD, encoding="utf-8").read()
# 去 frontmatter
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
body = body.replace("# 30欧、1个月拿证：长江存储拿下德国禁令的出海快刀", "").strip()
# 去合集/检索词注释块
body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()

SLUG = "20260928-german-utility-model-offense"
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"

TERMS = """专利术语对照（必须严格使用）:
实用新型=utility model / modèle d'utilité
分离程序=separation procedure (Abzweigung, German Utility Model Act Sec. 5(1)) / procédure de séparation (Abzweigung)
禁令=injunction / injonction
慕尼黑第一地区法院=Munich Regional Court I (Landgericht München I) / Tribunal régional de Munich I
德国专利商标局=German Patent and Trade Mark Office (DPMA) / Office allemand des brevets et des marques (DPMA)
联邦专利法院=Federal Patent Court / Tribunal fédéral des brevets
现有技术=prior art / état de la technique
创造性=inventive step / activité inventive
权利要求=claims / revendications
宣告无效=invalidation / nullité
欧洲专利=European patent / brevet européen
PCT申请=PCT application / demande PCT
优先权日=priority date / date de priorité
申请日=filing date / date de dépôt
宽限期=grace period / délai de grâce
担保金=security bond / caution
交叉许可=cross-licence / licence croisée
商业秘密=trade secret / secret d'affaires
保护客体=subject matter / objet de protection
实质审查=substantive examination / examen quant au fond
形式审查=formal examination / examen formel
注册制=registration-based system / système d'enregistrement
出海企业=Chinese companies going global / entreprises chinoises à l'international
一审判决=first-instance judgment / jugement de première instance
二审=appeal / appel
一审/第一审=first instance / première instance"""

PROMPT_EN = """You are a senior Chinese-English legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality English suitable for an English-language law firm blog.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for section headings, <h3> if needed, <p> for paragraphs, <ul>/<li> and <ol>/<li> for lists, <blockquote> for pull quotes, and a properly formed <table> (with <thead><tr><th> and <tbody>) for the two markdown tables in the source.
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**". NEVER include the 合集/检索词 trailing comment lines.
4. Keep ALL numbers, currency, dates, patent/application numbers and proper names EXACTLY as in the source (30 EUR, 250 EUR, 2025-10, 5 cases, 4 utility models, 1 European patent, 8-10 months, 13 months, 2 months, 10 years, Sec. 5(1)). Do not round or convert.
5. Keep the author's direct, opinionated voice ("I would put my position plainly here", "let me make this clear").
6. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
7. title: natural English headline (not a literal word-for-word rendering).

Chinese article:
"""

PROMPT_FR = """You are a senior Chinese-French legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality French suitable for a French-language law firm blog.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for section headings, <h3> if needed, <p> for paragraphs, <ul>/<li> and <ol>/<li> for lists, <blockquote> for pull quotes, and a properly formed <table> (with <thead><tr><th> and <tbody>) for the two markdown tables in the source.
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**". NEVER include the 合集/检索词 trailing comment lines.
4. Keep ALL numbers, currency, dates, patent/application numbers and proper names EXACTLY as in the source (30 EUR, 250 EUR, 2025-10, 5 cases, 4 utility models, 1 European patent, 8-10 months, 13 months, 2 months, 10 years, Sec. 5(1)). Use French spacing for large numbers only if the source has them. Do not round.
5. Keep the author's direct, opinionated voice.
6. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
7. title: natural French headline.
8. French typography: use &#x27; never a raw apostrophe inside HTML attribute values if any; use proper French punctuation spacing.

Chinese article:
"""


def call(prompt):
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt + body}],
            "temperature": 0.3,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"},
        }).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"},
    )
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    return r["choices"][0]["message"]["content"]


out = {}
for lang, prompt in (("en", PROMPT_EN), ("fr", PROMPT_FR)):
    txt = call(prompt)
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    d = json.loads(txt)
    hb = d["html_body"]
    assert "<h1" not in hb, f"{lang}: h1 leaked"
    assert "**" not in hb, f"{lang}: markdown leaked"
    assert "<!--" not in hb, f"{lang}: comment leaked"
    for token in ["30", "250", "2025", "8-10"]:
        assert token in hb, f"{lang}: lost token {token}"
    for token in ["Sec. 5(1)", "5(1)", "art. 5", "Article 5", "Abs. 1"]:
        if token in hb:
            break
    else:
        print(f"  WARN {lang}: separation-procedure citation phrasing not literal (manual check)")
    d["html_body"] = hb
    out[lang] = d
    z = json.loads(json.dumps(d, ensure_ascii=False))
    print(f"--- {lang.upper()} ---")
    print("TITLE:", z["title"])
    print("DESC:", z["description"])
    print("KW:", z["keywords"])
    print("HTML_LEN:", len(hb), "| h2:", hb.count("<h2"), "| table:", hb.count("<table"))
    print("SNIP:", hb[:600].replace("\n", " "))

json.dump(out, open("/Users/ziganghe/.hermes/cache/scratch/i18n_1003.json", "w"), ensure_ascii=False, indent=1)
print("SAVED")
