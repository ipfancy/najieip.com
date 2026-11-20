#!/usr/bin/env python3
"""2026-11-21 多语言同步 — 马尔代夫商标法 → EN / FR 翻译（逐语言单独请求）"""
import json, os, re, sys, urllib.request

MD = "/Users/ziganghe/wiki/digital-employees/articles/20261112-maldives-trademark-law.md"
OUT_EN = "/Users/ziganghe/wiki/digital-employees/reports/_i18n_en_1121.json"
OUT_FR = "/Users/ziganghe/wiki/digital-employees/reports/_i18n_fr_1121.json"
MODEL = "deepseek-chat"

def load_md():
    raw = open(MD, encoding="utf-8").read()
    if raw.startswith("---"):
        raw = raw.split("---", 2)[2]
    lines = raw.split("\n")
    title = ""
    body_lines = []
    for ln in lines:
        if not title and ln.startswith("# "):
            title = ln[2:].strip()
            continue
        body_lines.append(ln)
    body = "\n".join(body_lines).strip()
    return title, body

SYSTEM = """You are a professional legal translator for a Chinese IP law firm's bilingual website.
Translate the Chinese article into {lang_name} ({lang_code}). Rules:
1. Legal terminology must be exact. Use these mappings where applicable:
   商标 = trademark / marque ; 注册 = registration / enregistrement ;
   先申请原则 = first-to-file principle / principe du premier déposant ;
   续展 = renewal / renouvellement ; 撤销 = revocation / revocation ;
   在先使用 = prior use / usage antérieur ; 假冒侵权 = counterfeiting / contrefaçon ;
   类别（尼斯分类）= class (Nice Classification) / classe (classification de Nice) ;
   地理标志 = geographical indication / indication géographique ;
   工业品外观设计 = industrial design / dessin ou modèle industriel ;
   过渡期 = transitional period / période transitoire ; 实施细则 = implementing regulations / règlement d'exécution.
2. Keep ALL numbers, dates, law numbers, amounts EXACTLY as in the source (convert 万/亿 only if it reads naturally; never drop a digit).
3. Keep the financial/legal meaning; do not add or remove arguments.
4. Output HTML fragments only: <p>, <h2>, <strong>, <table class="data"> with <thead>/<tbody>/<tr>/<td>/<th>, <ul>/<li>, <ol>/<li>.
5. NEVER output an <h1>. Do not output any Chinese characters (except inside a proper noun that has no translation — avoid even that).
6. Do not include the "关注公众号"/"下一期"/disclaimer/byline lines — the site adds those.
7. Output must be valid JSON with exactly three keys: "title", "description", "keywords", "html_body".
   - title: the translated headline (no site suffix).
   - description: 140-220 characters of plain text summarising the article (do NOT repeat the title verbatim).
   - keywords: 6-8 comma-separated keywords.
   - html_body: the article body as HTML fragments.
Respond with the JSON object only, no markdown fence."""

def call(lang_name, lang_code, title, body):
    key = None
    for ln in open(os.path.expanduser("~/.hermes/.env"), encoding="utf-8"):
        if ln.startswith("DEEPSEEK_API_KEY"):
            key = ln.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("no DEEPSEEK_API_KEY")
    user = f"TITLE:\n{title}\n\nBODY (Chinese markdown):\n{body}"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM.format(lang_name=lang_name, lang_code=lang_code)},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    txt = d["choices"][0]["message"]["content"]
    return json.loads(txt)

def cjk(s):
    return len(re.findall(r"[\u4e00-\u9fff]", s))

if __name__ == "__main__":
    title, body = load_md()
    print("TITLE:", title, "| body chars:", len(body), file=sys.stderr)
    for lang_name, lang_code, out in [("English", "en", OUT_EN), ("French", "fr", OUT_FR)]:
        best = None
        for attempt in range(3):
            try:
                r = call(lang_name, lang_code, title, body)
            except Exception as e:
                print(f"{lang_code} attempt{attempt} EXC {e}", file=sys.stderr)
                continue
            n = cjk(r.get("html_body", "")) + cjk(r.get("title", ""))
            print(f"{lang_code} attempt{attempt}: body={len(r.get('html_body',''))} cjk={n} h1={'<h1' in r.get('html_body','')}", file=sys.stderr)
            if n < 30 and "<h1" not in r.get("html_body", "") and len(r.get("html_body", "")) > 1500:
                best = r
                break
            best = r
        json.dump(best, open(out, "w"), ensure_ascii=False, indent=1)
        print("WROTE", out, file=sys.stderr)
