#!/usr/bin/env python3
"""FR retry: force French output (previous attempt echoed Chinese)."""
import json, os, re, urllib.request

MD = os.path.expanduser("~/wiki/digital-employees/articles/20261024-mili-personal-safety-protection-order.md")
OUT = "/tmp/i18n_1031.json"

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

PROMPT = """Tu es traducteur juridique professionnel. Traduis intégralement en FRANÇAIS l'article chinois ci-dessous.

TERMINOLOGIE OBLIGATOIRE :
- 人身安全保护令 → ordonnance de protection (personal safety protection order)
- 家庭暴力 → violences conjugales / violences domestiques
- 较大可能性 → seuil de « probabilité » (standard abaissé)
- 高度可能性 → standard de « haute probabilité »
- 证明标准 → standard de preuve
- 告诫书 → lettre d'avertissement de la police
- 行政处罚决定书 → décision de sanction administrative
- 伤情鉴定意见 → expertise médico-légale des blessures
- 妇联 → Fédération des femmes (ligne 12338)
- 拒不执行判决、裁定罪 → refus d'exécution d'un jugement
- 司法拘留 → détention judiciaire
- 反家庭暴力法 → loi contre les violences domestiques
- 法释〔2022〕17号 → interprétation judiciaire n° 17 (2022)
- 民法典 → Code civil

RÈGLES ABSOLUES :
1. La sortie doit être ENTIÈREMENT en français. Aucun caractère chinois (sauf les numéros de texte juridique entre 〔〕 que tu peux conserver tels quels, et les noms propres).
2. Conserve le ton de l'auteur : première personne, direct, phrases courtes et franches.
3. Conserve exactement tous les chiffres, pourcentages, montants, numéros d'articles et délais (72 heures, 24 heures, 6 mois, 5 jours, 1000 yuans, 15 jours, 8 mois, 206, 84, 78, 92,86 %, 3,3 万 = 33 000, etc.).
4. Structure HTML : chaque paragraphe dans <p>, sous-titres dans <h2>, listes numérotées dans <ol><li>. PAS de <h1>, pas de <html>/<body>, pas de commentaires, pas de signature, pas d'avertissement.
5. N'ajoute ni ne retire aucun argument. N'invente aucun fait.
6. Réponds en JSON STRICT (sans balises markdown) avec les clés : title, description, html_body, keywords.
7. description : 180-260 caractères, factuelle, ne répète pas le titre.
8. keywords : tableau de 6-8 expressions en français.

Article source :
""" + body

def call():
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu réponds exclusivement en français, en JSON strict."},
            {"role": "user", "content": PROMPT},
        ],
        "temperature": 0.2,
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

best = None
for attempt in range(3):
    d = call()
    hb = d["html_body"]
    cjk = len(re.findall(r"[\u4e00-\u9fff]", hb))
    print("attempt", attempt, "cjk_in_body:", cjk, "h2:", hb.count("<h2"), "bytes:", len(hb.encode()))
    if cjk < 30:
        best = d
        break
    best = d
if best is None:
    raise SystemExit("FR failed")
data = json.load(open(OUT))
data["fr"] = best
json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
print("TITLE:", best["title"])
print("DESC:", best["description"])
print("KW:", best["keywords"])
print("BODY HEAD:", best["html_body"][:500])
