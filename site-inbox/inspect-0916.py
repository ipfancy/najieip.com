#!/usr/bin/env python3
"""0916 inspect: mili index card metas, JSON-LD dates, deploy-log tail."""
import re, json, os

root = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(root)

t = open('mili/blog/index.html', encoding='utf-8').read()
print("=== mili/blog/index.html top 5 cards ===")
for m in list(re.finditer(r'<div class="article-card">(.*?)\n  </div>', t, flags=re.S))[:5]:
    b = m.group(1)
    h = re.search(r'<h2><a href="([^"]+)">([^<]*)', b)
    meta = re.search(r'<div class="meta">(.*?)</div>', b, flags=re.S)
    print((h.group(1) if h else '?'), '|', (h.group(2)[:34] if h else ''), '|',
          re.sub(r'\s+', ' ', meta.group(1)).strip() if meta else '')

print("\n=== JSON-LD datePublished ===")
for f in ['mili/blog/20260917-livestream-ai-voice-personality-rights.html',
          'mili/blog/20260918-ai-search-rag-liability.html',
          'mili/blog/20260918-personality-rights-injunction.html',
          'najie/blog/20260916-data-asset-four-step.html',
          'mili/blog/20260916-inventor-remuneration-907.html']:
    tt = open(f, encoding='utf-8').read()
    dp = re.findall(r'"datePublished"\s*:\s*"([^"]+)"', tt)
    mod = re.findall(r'"dateModified"\s*:\s*"([^"]+)"', tt)
    print(f, '| datePublished=', dp[:1], '| dateModified=', mod[:1], '| len', len(tt))

print("\n=== deploy-log tail ===")
d = json.load(open('site-inbox/deploy-log.json', encoding='utf-8'))
items = d['deploys'] if isinstance(d, dict) else d
print('type:', type(d).__name__, 'keys:', list(d.keys()) if isinstance(d, dict) else '', 'entries:', len(items))
for e in items[-8:]:
    print(json.dumps(e, ensure_ascii=False)[:300])
