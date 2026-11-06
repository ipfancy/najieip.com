#!/usr/bin/env python3
"""GEO/i18n 2026-11-07: ART-2026-0118 专利出海第二道闸 → EN + FR"""
import json, os, re, urllib.request

MD = os.path.expanduser("~/wiki/digital-employees/articles/20261101-najie-ip-foreign-transfer-review.md")
OUT = "/Users/ziganghe/.hermes/cache/scratch/i18n_1107.json"


def env(key):
    for line in open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


KEY = env("DEEPSEEK_API_KEY")
assert KEY, "no DEEPSEEK_API_KEY"

raw = open(MD, encoding="utf-8").read()
body = raw.split("---", 2)[2].strip()
body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()
lines = body.split("\n")
cut = None
for i, l in enumerate(lines):
    if l.startswith("何自刚 |") or l.startswith("*本文由 AI"):
        cut = i
        break
if cut:
    lines = lines[:cut]
body = "\n".join(lines).strip()
body = re.sub(r"^#\s+.*\n", "", body, count=1).strip()

TERMS = (
    "术语对照表（必须严格使用，英文 / 法文）：\n"
    "知识产权对外转让 → outbound transfer of intellectual property / transfert à l'étranger de propriété intellectuelle\n"
    "《知识产权对外转让有关工作办法（试行）》→ the (Trial) Measures for the Administration of Outbound Transfers of Intellectual Property (Guo Ban Fa [2018] No. 19) / les Mesures (à l'essai) relatives au transfert à l'étranger de propriété intellectuelle (Guo Ban Fa [2018] n° 19)\n"
    "对外转让 → outbound transfer / transfert à l'étranger\n"
    "权利人变更 → change of the rights holder / changement de titulaire des droits\n"
    "实际控制人变更 → change of actual controller / changement de contrôleur effectif\n"
    "独占实施许可 → exclusive exploitation licence / licence d'exploitation exclusive\n"
    "先证后约 → licence-before-contract / licence avant contrat\n"
    "《技术出口许可意向书》→ Letter of Intent for Technology Export Licence / lettre d'intention de licence d'exportation de technologies\n"
    "《技术出口许可证》→ Technology Export Licence / licence d'exportation de technologies\n"
    "集成电路布图设计专有权 → layout-design right of integrated circuits / droit sur le schéma de configuration de circuits intégrés\n"
    "植物新品种权 → new plant variety right / droit sur une nouvelle variété végétale\n"
    "《中国禁止出口限制出口技术目录》→ Catalogue of Technologies Prohibited or Restricted from Export / Catalogue des technologies interdites ou restreintes à l'exportation\n"
    "临时登记 → interim registration / enregistrement provisoire\n"
    "商务部 → Ministry of Commerce (MOFCOM) / ministère du Commerce\n"
    "保密审查 → confidentiality review / contrôle de confidentialité\n"
    "外资并购安全审查 → national security review of foreign investment M&A / contrôle de sécurité des investissements étrangers\n"
    "VIE重组 → VIE restructuring / restructuration VIE\n"
    "红筹回流 → red-chip redomiciliation / retournement de structure red-chip\n"
    "技术出口 → technology export / exportation de technologies\n"
)

RULES = (
    "Rules:\n"
    "- Keep the author's voice: first person, direct, plain-spoken, occasional short punchy sentences. Do NOT flatten it into corporate tone.\n"
    "- Preserve every number, statute number, document number (e.g. 国办发〔2018〕19号, 第48号公告), percentage and monetary amount exactly.\n"
    "- Output structure with HTML only: each paragraph in <p>. Numbered lists in <ol><li>. Bold emphasis in <strong>.\n"
    "- Do NOT output <h1> and do NOT output <h2> — headings will be added separately. No <html>/<body>, no comments, no signature lines, no disclaimer.\n"
    "- Do not add or remove arguments. Do not invent facts.\n"
    "- Output STRICT JSON only, no markdown fences, with keys: title, description, html_body, keywords (list of 5-8 English/French SEO terms).\n"
    "- description: 180-260 characters, factual, NOT a repeat of the title.\n"
)


def translate(langname):
    prompt = ("You are a professional legal translator. Translate a Chinese legal-practice article into " + langname
              + ". Translate only into " + langname + "; never output Chinese characters in html_body.\n"
              + TERMS + RULES + "\nSource article:\n" + body)
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY},
    )
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    txt = r["choices"][0]["message"]["content"]
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    return json.loads(txt)


out = {}
for lang, name in (("en", "English"), ("fr", "French")):
    d = None
    for attempt in range(3):
        d = translate(name)
        hb = d["html_body"]
        cjk = len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", hb)))
        if cjk < 30 and "<h1" not in hb.lower() and "<h2" not in hb.lower():
            break
        print(lang, "retry", attempt, "cjk=", cjk, "h2=", hb.count("<h2"))
    out[lang] = d
    hb = d["html_body"]
    print(lang, "title:", d["title"][:110])
    print(lang, "desc_len:", len(d["description"]), "|", d["description"][:110])
    print(lang, "cjk_in_body:", len(re.findall(r"[\u4e00-\u9fff]", re.sub(r"<[^>]+>", "", hb))),
          "| p:", hb.count("<p>"), "| ol:", hb.count("<ol>"), "| table:", hb.count("<table"),
          "| bytes:", len(hb.encode()))
    print("-" * 50)
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print("saved", OUT)
