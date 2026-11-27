#!/usr/bin/env python3
"""2026-11-28 多语言同步 — 惩罚性赔偿漏写请求（ART-2026-0137）→ EN / FR（逐语言单独请求）"""
import json, os, re, sys, urllib.request

MD = "/Users/ziganghe/wiki/digital-employees/articles/20261124-mili-punitive-damages-one-shot.md"
TAG = "1128"
OUT_EN = f"/Users/ziganghe/wiki/digital-employees/reports/_i18n_en_{TAG}.json"
OUT_FR = f"/Users/ziganghe/wiki/digital-employees/reports/_i18n_fr_{TAG}.json"
MODEL = "deepseek-chat"


def load_md():
    raw = open(MD, encoding="utf-8").read()
    fm_title = ""
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        fm = parts[1]
        for ln in fm.split("\n"):
            if ln.startswith("title:"):
                fm_title = ln.split(":", 1)[1].strip()
        raw = parts[2]
    title, body_lines = fm_title, []
    for ln in raw.split("\n"):
        if not title and ln.startswith("# "):
            title = ln[2:].strip()
            continue
        body_lines.append(ln)
    return title, "\n".join(body_lines).strip()


SYSTEM = """You are a professional legal translator for a Chinese IP law firm's bilingual website.
Translate the Chinese article into {lang_name} ({lang_code}). Rules:
1. Legal terminology must be exact. Use these mappings:
   惩罚性赔偿 = punitive damages / dommages-intérêts punitifs ;
   补偿性赔偿 = compensatory damages / dommages-intérêts compensatoires ;
   计算基数 = calculation base / base de calcul ; 维权合理开支 = reasonable enforcement costs / frais raisonnables de défense ;
   故意 = intent (willfulness) / intention (faute dolosive) ;
   情节严重 = serious circumstances / circonstances graves ;
   商业秘密 = trade secrets / secrets d'affaires ;
   不正当竞争 = unfair competition / concurrence déloyale ;
   仿冒、混淆 = counterfeiting and confusion / contrefaçon et confusion ;
   释明 = the court's clarification (judicial clarification) / explication par le juge ;
   不予受理 = not accepted (inadmissible) / irrecevable ;
   一审法庭辩论终结 = close of the first-instance hearing / clôture des débats en première instance ;
   诉讼请求 = claims (prayer for relief) / conclusions (demandes) ;
   知识产权法庭 = Intellectual Property Court / tribunal de la propriété intellectuelle ;
   法释〔2026〕7号 = Fa Shi [2026] No. 7 / Fa Shi [2026] n° 7.
2. Keep ALL numbers, dates, judicial-interpretation numbers, percentages and amounts EXACTLY (e.g. 1471, 505, 1.8 billion / 1,8 milliard, 331, 35, 10.6% / 10,6 %, 5.3% / 5,3 %, 18.2% / 18,2 %, 41.2% / 41,2 %, 24.3% / 24,3 %, five times / cinq fois, May 1 2026 / 1er mai 2026).
3. Preserve every argument; do not add or drop any.
4. Output HTML fragments only: <p>, <h2>, <strong>, <table class="data"> with <thead>/<tbody>/<tr>/<td>/<th>, <ul>/<li>, <ol>/<li>.
5. NEVER output an <h1>. Do not output any Chinese characters.
6. Do not include the "关注公众号"/"下一篇"/disclaimer/byline lines — the site adds those.
7. Output valid JSON with exactly four keys: "title", "description", "keywords", "html_body".
   - title: translated headline (no site suffix).
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
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM.format(lang_name=lang_name, lang_code=lang_code)},
            {"role": "user", "content": f"TITLE:\n{title}\n\nBODY (Chinese markdown):\n{body}"},
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
    return json.loads(d["choices"][0]["message"]["content"])


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
            print(f"{lang_code} attempt{attempt}: body={len(r.get('html_body',''))} cjk={n} "
                  f"h1={'<h1' in r.get('html_body','')}", file=sys.stderr)
            best = r
            if n < 30 and "<h1" not in r.get("html_body", "") and len(r.get("html_body", "")) > 1200:
                break
        json.dump(best, open(out, "w"), ensure_ascii=False, indent=1)
        print("WROTE", out, file=sys.stderr)
