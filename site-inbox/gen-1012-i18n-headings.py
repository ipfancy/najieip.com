#!/usr/bin/env python3
# 给 EN/FR 译文插入描述性 <h2> 路标；断言去掉 h2 后正文逐字不变
import json, os, re, urllib.request

ENV = os.path.expanduser("~/.hermes/.env")
KEY = None
for line in open(ENV):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

P = "/Users/ziganghe/.hermes/cache/scratch/i18n_1012.json"
D = json.load(open(P, encoding="utf-8"))

PROMPT = """You are a senior legal editor. The HTML article below is a finished, publication-ready English text.

Task: insert 4 to 5 descriptive <h2> section headings into it so readers can scan it. The headings must be SHORT (4-8 words) and purely descriptive signposts derived from the text that follows them.

STRICT RULES
- Do NOT change, add, delete, reorder or reword a single character of any existing text, tag, number or attribute.
- Only INSERT `<h2>...</h2>` immediately before a chosen `<p>` (never inside a tag, never after `</table>`).
- Keep the heading text in the SAME LANGUAGE as the article.
- Return a JSON object with exactly two keys: "published_title" (the headline itself) and "html_body" (the full modified HTML).

Current title: @@TITLE@@

HTML:
@@BODY@@"""


def call(prompt):
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2, "max_tokens": 9000,
            "response_format": {"type": "json_object"},
        }).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"},
    )
    return json.loads(urllib.request.urlopen(req, timeout=300).read())["choices"][0]["message"]["content"]


for lang in ("en", "fr"):
    old = D[lang]["html_body"]
    pr = PROMPT.replace("@@TITLE@@", D[lang]["title"]).replace("@@BODY@@", old)
    txt = re.sub(r"^```(?:json)?|```$", "", call(pr).strip(), flags=re.M).strip()
    try:
        d = json.loads(txt)
        new = d.get("html_body", "")
    except Exception as e:
        print(lang, "JSON FAIL", e); continue
    stripped = re.sub(r"\s*<h2>.*?</h2>", "", new, flags=re.S)
    ok = stripped == old
    print(f"[{lang}] h2_count={new.count('<h2>')} | text_unchanged={ok}")
    if not ok:
        # 找出首个差异位置
        for i, (a, b) in enumerate(zip(stripped, old)):
            if a != b:
                print("   first diff @", i, repr(stripped[i-80:i+80]), "VS", repr(old[i-80:i+80]))
                break
        print("   lengths:", len(stripped), len(old))
        continue
    assert "<h1" not in new and "**" not in new
    D[lang]["html_body"] = new
    print("   headings:", re.findall(r"<h2>(.*?)</h2>", new))

json.dump(D, open(P, "w"), ensure_ascii=False, indent=1)
print("SAVED")
