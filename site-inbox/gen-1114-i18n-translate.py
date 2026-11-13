import json, os, re, sys, urllib.request

REPO = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261113-byd-netherlands-evidence-seizure"
BRAND = "mili"
ZH = open(f"{REPO}/{BRAND}/blog/{SLUG}.html").read()
art = ZH[ZH.find("<article>") + 9: ZH.rfind("</article>")]
# 去掉 h1 / figure / 尾部（公众号引导 + 落款 + 免责 + footer + CTA）
start = art.find("<p>", art.find("</figure>") + 9)
art = art[start:]
cut = art.find("<p>关注公众号")
if cut == -1:
    cut = art.find("<p>何自刚")
body_src = art[:cut].strip()
print("SRC LEN", len(body_src), "h2", body_src.count("<h2>"), "table", body_src.count("<table"))

KEY = None
for line in open(os.path.expanduser("~/.hermes/.env")):
    if line.startswith("DEEPSEEK_API_KEY"):
        KEY = line.split("=", 1)[1].strip().strip('"')
        break
assert KEY, "no key"

SYS = {
 "en": """You are a senior Chinese-English legal translator working for a Chinese law firm's website.
Translate the Chinese HTML fragment into professional, natural ENGLISH. Rules:
- Output ONLY the translated HTML fragment. No preamble, no markdown fences.
- Keep the exact same HTML tags and structure: <h2>, <p>, <strong>, <em>, <table class="data">, <thead>, <tbody>, <tr>, <td>, <th>.
- Do NOT add, remove, merge or reorder any paragraph or section. Same number of <p> and <h2>.
- Translate h2 headings into short English section titles (investment memo style, no colon-heavy Chinese syntax).
- Preserve all numbers, dates, case/model names exactly: Article 1019, Article 1019h, Article 84, Ti7, JLR, BYD, Land Rover Defender, months/dates as in source. Use English date style (November 11, August, June, October).
- Do NOT write any Chinese characters. No Chinese punctuation; use standard English punctuation and straight or typographic quotes.
- Terminology: 外观设计 design (design patent in CN context); 证据保全 evidence preservation / interim seizure of evidence; 扣押令 seizure order; 民事诉讼法 Code of Civil Procedure; 诉前保全 pre-litigation preservation; 开示 disclosure; 异议 objection; 涉外争议 cross-border disputes.""",
 "fr": """Vous êtes traducteur juridique chinois-français pour le site d'un cabinet chinois.
Traduisez le fragment HTML chinois en FRANÇAIS professionnel et naturel. Règles :
- Renvoyez UNIQUEMENT le fragment HTML traduit. Aucun préambule, aucun bloc markdown.
- Conservez exactement la même structure HTML : <h2>, <p>, <strong>, <em>, <table class="data">, <thead>, <tbody>, <tr>, <td>, <th>.
- N'ajoutez, ne supprimez, ne fusionnez et ne réordonnez aucun paragraphe ni section. Même nombre de <p> et de <h2>.
- Traduisez les titres h2 en titres de section courts en français.
- Conservez tous les chiffres, dates et noms de modèles exactement : article 1019, article 1019h, article 84, Ti7, JLR, BYD, Land Rover Defender ; mois et dates en français (11 novembre, août, juin, octobre).
- N'écrivez AUCUN caractère chinois. Ponctuation française ; apostrophes typographiques &#x27; ou ’.
- Terminologie : 外观设计 dessins et modèles ; 证据保全 saisie-conservat ; 扣押令 ordonnance de saisie ; 民事诉讼法 Code de procédure civile ; 诉前保全 mesures conservatoires avant procès ; 开示 communication des pièces ; 异议 opposition/contestation ; 涉外争议 litiges transfrontaliers.""",
}

def call(lang):
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYS[lang]},
                     {"role": "user", "content": body_src}],
        "temperature": 0.2,
        "max_tokens": 4000,
    }
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json",
        "Authorization": "Bearer " + KEY})
    r = json.loads(urllib.request.urlopen(req, timeout=240).read())
    return r["choices"][0]["message"]["content"].strip()

out = {}
for lang in ("en", "fr"):
    for attempt in range(3):
        txt = call(lang)
        txt = re.sub(r"^```(?:html)?\s*|\s*```$", "", txt).strip()
        cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
        ok = (cjk == 0 and txt.count("<h2>") == body_src.count("<h2>")
              and txt.count("<p>") == body_src.count("<p>"))
        print(lang, "attempt", attempt + 1, "len", len(txt), "cjk", cjk,
              "h2", txt.count("<h2>"), "p", txt.count("<p>"), "ok", ok, flush=True)
        if ok:
            out[lang] = txt
            break
    if lang not in out:
        out[lang] = txt
        print("WARN: validation failed for", lang)

json.dump({"src_len": len(body_src), "en": out.get("en"), "fr": out.get("fr")},
          open("/Users/ziganghe/.hermes/cache/scratch/i18n-1114-translations.json", "w"),
          ensure_ascii=False, indent=1)
print("SAVED")
