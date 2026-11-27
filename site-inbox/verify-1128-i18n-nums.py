#!/usr/bin/env python3
"""i18n 数字保真核对 — ART-2026-0137 EN/FR"""
import json, re

EN = json.load(open("/Users/ziganghe/wiki/digital-employees/reports/_i18n_en_1128.json"))
FR = json.load(open("/Users/ziganghe/wiki/digital-employees/reports/_i18n_fr_1128.json"))

checks = {
    "en": ["1471", "505", "1.8 billion", "331", "35", "10.6%", "5.3%", "18.2%", "41.2%", "24.3%",
           "May 1, 2026", "2026] No. 7", "1972", "Article 12", "five times"],
    "fr": ["1471", "505", "1,8 milliard", "331", "35", "10,6", "5,3", "18,2", "41,2", "24,3",
           "1er mai 2026", "1972", "Article 12", "cinq fois"],
}
for tag, obj in (("en", EN), ("fr", FR)):
    body = obj["html_body"]
    print("=" * 70)
    print(tag.upper(), "TITLE:", obj["title"])
    print("DESC:", obj["description"][:200])
    print("KW:", obj["keywords"])
    print("h2:", re.findall(r"<h2>(.*?)</h2>", body))
    print("strong:", len(re.findall(r"<strong>", body)), "p:", len(re.findall(r"<p>", body)))
    miss = [c for c in checks[tag] if c not in body]
    print("MISSING:", miss)
    print("FIRST 600:", re.sub(r"<[^>]+>", "", body)[:600])
