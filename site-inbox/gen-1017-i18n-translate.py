#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-17 第42周 i18n 翻译 — ART-2026-0105 AI短剧 / Token 成本入赔（复用 1003/1012 工厂）"""
import json, os, re, sys, urllib.request

ENV = os.path.expanduser("~/.hermes/.env")
KEY = None
for line in open(ENV):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    sys.exit("no key")

MD = os.path.expanduser("~/wiki/digital-employees/articles/20261009-mili-ai-short-drama-token-evidence.md")
raw = open(MD, encoding="utf-8").read()
body = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S)
body = body.replace("# AI短剧被整部搬走只赔2万，这3样证据你留了吗", "").strip()
body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()

SLUG = "20261009-mili-ai-short-drama-token-evidence"
ZH_URL = f"https://najieip.com/mili/blog/{SLUG}.html"

TERMS = """著作权术语对照（必须严格使用）:
视听作品=audiovisual work / œuvre audiovisuelle
独创性=originality / originalité
著作权=版权=copyright / droit d'auteur
侵权=infringement / contrefaçon
法定赔偿=statutory damages / dommages-intérêts légaux
酌定（赔偿）=(damages) awarded at the court's discretion / fixés à la discrétion du juge
权属=ownership / titularité
词元（Token）=token / token (jeton)
算力成本=compute cost / coût de calcul
商用AI工具授权费=commercial AI tool licence fee / frais de licence d'outils d'IA commerciaux
提示词=prompt / invite de commande (prompt)
分镜提示词=storyboard prompt / invite de storyboard
原始工程文件=source project files / fichiers de projet sources
留痕=evidence retention / conservation des preuves
举证=proving (evidence) / production de la preuve
刑事追诉线=criminal prosecution threshold / seuil de poursuite pénale
盗录=illegal recording / enregistrement illégal
显式+隐式标识=explicit and implicit labelling / marquage explicite et implicite
江岸区法院=Jiang'an District People's Court, Wuhan / tribunal de district de Jiang'an, Wuhan
"""

PROMPT_EN = """You are a senior Chinese-English legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality English suitable for an English-language law firm blog. Keep the author's direct, opinionated, first-person voice.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for the four section headings, <p> for paragraphs. There is no table in this article - do NOT create one.
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**".
4. Keep ALL numbers, dates and amounts EXACTLY: 47 episodes / one hour, RMB 20,000 (2万元 = 20,000 yuan), over 1,700 AI short dramas (1700多部), July 1, Wuhan Jiang'an District People's Court. Do not round or convert.
5. Drop the WeChat-Official-Account call-to-action clause (@纳杰觅理 关注公众号) but keep the invitation to leave comments; keep the "next article" sentence.
6. Keep the author signature line "He Zigang | Intellectual Property Lawyer | Aipunajie · Mili · Najie" and the author's own disclaimer sentence (but not the AI-assistance line).
7. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
8. title: natural English headline (not literal word-for-word).

Chinese article:
""" + body

PROMPT_FR = """You are a senior Chinese-French legal translator for an IP law firm.

Translate the following Chinese article into professional, publication-quality French suitable for a French-language law firm blog. Keep the author's direct, opinionated, first-person voice.

Terminology:
""" + TERMS + """

Hard rules:
1. Return a JSON object with keys: title, description, keywords (array of 6-9 strings), html_body.
2. html_body must be HTML only (no markdown). Start with <p>. Use <h2> for the four section headings, <p> for paragraphs. There is no table in this article - do NOT create one.
3. NEVER include an <h1> in html_body. NEVER include HTML comments. NEVER include markdown asterisks or "**".
4. Keep ALL numbers, dates and amounts EXACTLY: 47 épisodes / une heure, 20 000 yuans RMB (2万元), plus de 1 700 mini-séries générées par IA (1700多部), 1er juillet, tribunal de district de Jiang'an, Wuhan. Do not round.
5. Drop the WeChat-Official-Account call-to-action clause but keep the invitation to leave comments; keep the "next article" sentence.
6. Keep the author signature line "He Zigang | Avocat en propriété intellectuelle | Aipunajie · Mili · Najie" and the author's own disclaimer sentence (but not the AI-assistance line).
7. description: 200-400 characters, plain descriptive summary (NOT a repeat of the title).
8. title: natural French headline.
9. French typography: use &#x27; never a raw apostrophe inside HTML attribute values.

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
    "en": ["47", "20,000", "1,700", "July 1"],
    "fr": ["47", "20 000", "1 700", "1er juillet"],
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
    if missing:
        print(f"  FAILNUM {lang}: {missing}")
    d["html_body"] = hb
    out[lang] = d
    print(f"--- {lang.upper()} ---")
    print("TITLE:", d["title"])
    print("DESC:", d["description"])
    print("KW:", d["keywords"])
    print("HTML_LEN:", len(hb), "| h2:", hb.count("<h2"), "| table:", hb.count("<table"))
    print("SNIP:", hb[:300].replace("\n", " "))

json.dump(out, open(os.path.expanduser("~/.hermes/cache/scratch/i18n_1017.json"), "w"), ensure_ascii=False, indent=1)
print("SAVED")
