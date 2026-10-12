#!/usr/bin/env python3
# FR 版差异定位 + 归一化判定
import json, re, urllib.request, os, difflib

ENV = os.path.expanduser("~/.hermes/.env")
KEY = [l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(ENV) if l.startswith("DEEPSEEK_API_KEY")][0]
P = "/Users/ziganghe/.hermes/cache/scratch/i18n_1012.json"
D = json.load(open(P, encoding="utf-8"))

PROMPT = """You are a senior legal editor. The HTML article below is a finished, publication-ready French text.

Task: insert 4 to 5 descriptive <h2> section headings into it so readers can scan it. The headings must be SHORT (4-8 words), in French, purely descriptive signposts derived from the text that follows them.

STRICT RULES
- Do NOT change, add, delete, reorder or reword a single character of any existing text, tag, number or attribute. Do not normalise spacing or punctuation either.
- Only INSERT `<h2>...</h2>` immediately before a chosen `<p>` (never inside a tag, never after `</table>`).
- Return a JSON object with exactly two keys: "published_title" and "html_body" (the full modified HTML, unchanged except for the inserted headings).

Current title: @@TITLE@@

HTML:
@@BODY@@"""


def call(prompt):
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps({"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
                         "temperature": 0.0, "max_tokens": 9000,
                         "response_format": {"type": "json_object"}}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())["choices"][0]["message"]["content"]


def norm(s):
    s = re.sub(r"\s*<h2>.*?</h2>", "", s, flags=re.S)
    return re.sub(r"\s+", " ", s).strip()


old = D["fr"]["html_body"]
for attempt in range(3):
    txt = re.sub(r"^```(?:json)?|```$", "", call(PROMPT.replace("@@TITLE@@", D["fr"]["title"]).replace("@@BODY@@", old)).strip(), flags=re.M).strip()
    d = json.loads(txt)
    new = d.get("html_body", "")
    raw_ok = re.sub(r"\s*<h2>.*?</h2>", "", new, flags=re.S) == old
    n_ok = norm(new) == norm(old)
    print(f"attempt {attempt+1}: h2={new.count('<h2>')} raw_equal={raw_ok} norm_equal={n_ok} len={len(new)}/{len(old)}")
    if raw_ok or n_ok:
        if "**" not in new and "<h1" not in new:
            D["fr"]["html_body"] = new
            print("   headings:", re.findall(r"<h2>(.*?)</h2>", new))
            break
if norm(D["fr"]["html_body"]) != norm(old):
    print("FR STILL MISMATCH — keeping original (no h2 in FR)")
else:
    json.dump(D, open(P, "w"), ensure_ascii=False, indent=1)
    print("SAVED fr")
