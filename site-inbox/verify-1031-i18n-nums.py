import re, os, json
REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261024-mili-personal-safety-protection-order"
en = open(f"{REPO}/en/blog/{SLUG}-en.html", encoding="utf-8").read()
fr = open(f"{REPO}/fr/blog/{SLUG}-fr.html", encoding="utf-8").read()

def body(t):
    i = t.find("<article>")
    return t[i:]

EN_TOKENS = ["33,000", "3,000", "84", "78", "92.86%", "206", "March 30, 2026", "11 items", "72 hours",
             "24 hours", "6 months", "5 days", "1,000 yuan", "15 days", "eight months", "Article 9",
             "Article 6", "Article 28", "Article 29", "Article 34", "Article 19", "12338"]
FR_TOKENS = ["33 000", "84", "78", "92,86 %", "206", "30 mars 2026", "11 éléments", "72 heures",
             "24 heures", "6 mois", "5 jours", "1 000 yuans", "15 jours", "huit mois", "article 9",
             "article 6", "article 28", "article 29", "article 34", "article 19", "12338"]
fails = []
for name, txt, toks in (("EN", body(en), EN_TOKENS), ("FR", body(fr), FR_TOKENS)):
    miss = [x for x in toks if x.lower() not in txt.lower()]
    print(name, "missing:", miss)
    if miss:
        fails.append((name, miss))
print("FAILS:", fails)
print("EN bytes", len(en.encode()), "FR bytes", len(fr.encode()))
print("EN h1", len(re.findall(r"<h1", en)), "h2", en.count("<h2>"), "ld", en.count("application/ld+json"))
print("FR h1", len(re.findall(r"<h1", fr)), "h2", fr.count("<h2>"), "ld", fr.count("application/ld+json"))
# 英文页不得出现中文
print("EN cjk body:", len(re.findall(r"[\u4e00-\u9fff]", body(en))))
print("FR cjk body:", len(re.findall(r"[\u4e00-\u9fff]", body(fr))))
