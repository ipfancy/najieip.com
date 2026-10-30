#!/usr/bin/env python3
"""GEO/i18n 2026-10-31: ART-2026-0114 人身安全保护令 → EN + FR"""
import json, os, re, urllib.request

MD = os.path.expanduser("~/wiki/digital-employees/articles/20261024-mili-personal-safety-protection-order.md")
OUT = "/tmp/i18n_1031.json"
SLUG = "20261024-mili-personal-safety-protection-order"

def env(key):
    for line in open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

KEY = env("DEEPSEEK_API_KEY")

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

TERMS = (
    "术语对照表（必须严格使用）：\n"
    "人身安全保护令 → personal safety protection order\n"
    "家庭暴力 → domestic violence (DV)\n"
    "较大可能性 → lower \"probability\" threshold\n"
    "高度可能性 → \"high probability\" standard\n"
    "证明标准 → standard of proof\n"
    "告诫书 → police admonition letter\n"
    "行政处罚决定书 → administrative penalty decision\n"
    "伤情鉴定意见 → forensic injury assessment\n"
    "妇联 → Women's Federation (12338 hotline)\n"
    "拒不执行判决、裁定罪 → crime of refusing to execute a judgment or ruling\n"
    "司法拘留 → judicial detention\n"
    "反家庭暴力法 → Anti-Domestic Violence Law\n"
    "法释〔2022〕17号 → Judicial Interpretation No. 17 (2022)\n"
    "民法典 → Civil Code\n"
)

RULES = (
    "Rules:\n"
    "- Keep the author's voice: first person, direct, plain-spoken, occasional short punchy sentences. Do NOT flatten it into corporate tone.\n"
    "- Preserve every number, statute number, case reference, percentage and monetary amount exactly.\n"
    "- Preserve structure with HTML: each paragraph in <p>, subheads in <h2>, numbered lists in <ol><li>. "
    "NO <h1>, NO <html>/<body>, NO comments, NO signature lines, NO disclaimer.\n"
    "- Do not add or remove arguments. Do not invent facts.\n"
    "- Output STRICT JSON only, no markdown fences, with keys: title, description, html_body, keywords.\n"
    "- description: 180-260 characters, factual, NOT a repeat of the title.\n"
)

def translate(langname):
    prompt = "You are a professional legal translator. Translate a Chinese legal-practice article into " + langname + ".\n" \
             + TERMS + RULES + "\nSource article:\n" + body
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
    d = translate(name)
    hb = d["html_body"]
    assert "<h1" not in hb.lower(), "model returned h1"
    out[lang] = d
    print(lang, "title:", d["title"][:100])
    print(lang, "desc_len:", len(d["description"]), "|", d["description"][:100])
    print(lang, "h2:", hb.count("<h2"), "p:", hb.count("<p>"), "ol:", hb.count("<ol>"),
          "table:", hb.count("<table"), "bytes:", len(hb.encode()))
    print("-" * 50)
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print("saved", OUT)
