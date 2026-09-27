#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 口径对齐（EN/FR + zh 觅理）——修复今日 09-27 zh 口径修复未覆盖的语种页
替换全部走精确字符串 + 计数断言(==1)；备份 .bak-20260927。
"""
import os, shutil, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
APPLY = '--apply' in sys.argv

ZH_DESC = ('北京觅理律师事务所 — 综合型律师事务所（不止于知识产权）：知识产权诉讼、商业秘密、'
           '反不正当竞争与反垄断、行政法与行政复议、刑事辩护与刑事合规、海商法、国际法、'
           '民商事争议解决、企业常年法律顾问。5位资深合伙人，技术+法律双背景团队。')

EN_DESC = ('Mili Law Firm (Beijing Mili Law Offices) — a full-service law firm, not IP-only: IP litigation, '
           'trade secrets, unfair competition & antitrust, administrative law, criminal defense & compliance, '
           'maritime law, international law, civil & commercial disputes, and general corporate counsel. '
           '85% favorable outcome rate; 5 senior partners; tech + law dual background team.')

# 注意 FR 描述内不使用撇号，避免 HTML 属性截断（09-27 实测 og:description 被截成 "Mili Cabinet d"）
FR_DESC = ("Mili Cabinet d&#x27;Avocats (Beijing Mili Law Offices) — cabinet pluridisciplinaire, au-dela de la PI : "
           "contentieux PI, secrets d&#x27;affaires, concurrence deloyale et antitrust, droit administratif, "
           "defense penale et conformite, droit maritime, droit international, litiges civils et commerciaux, "
           "conseil juridique permanent. 85 % de resultats favorables ; 5 associes experimentes.")

EDITS = {
 'mili/index.html': [
  ('<div class="hero-badge">↯ 知识产权专业律所</div>',
   '<div class="hero-badge">↯ 综合型律师事务所 · 知产诉讼专长</div>'),
  ('专注知识产权诉讼与法律保护——专利侵权诉讼、商标争议、<br>反不正当竞争、技术合同纠纷，以专业赢得尊重。',
   '以知产诉讼为专长，覆盖综合法律事务——专利侵权诉讼、商标争议、<br>反不正当竞争与反垄断、行政法与刑事合规、海商法、国际法、民商事争议，以专业赢得尊重。'),
  ('<div class="section-title"><h2>业务领域</h2><p>全维度知识产权法律保护</p></div>',
   '<div class="section-title"><h2>业务领域</h2><p>全维度法律保护 · 知产诉讼为专长</p></div>'),
 ],
 'en/mili/index.html': [
  ('<meta name="description" content="Mili Law Firm — IP Legal Protection。提供Patent Infringement Litigation、Trademark Disputes、Unfair Competition、IP Contracts等法律服务。85% Favorable Outcome Rate，5位资深Partners，Tech + Law Dual Background团队。">',
   '<meta name="description" content="%s">' % EN_DESC),
  ('<title>Mili Law Firm — IP Legal Protection</title>',
   '<title>Mili Law Firm — Full-Service Law Firm · IP Litigation</title>'),
  ('<meta property="og:title" content="Mili Law Firm">',
   '<meta property="og:title" content="Mili Law Firm — Full-Service Law Firm · IP Litigation">'),
  ('<meta property="og:description" content="Mili Law Firm — IP Legal Protection。提供Patent Infringement Litigation、Trademark Disputes、Unfair Competition、IP Contracts等法律服务。85% Favorable Outcome Rate，5位资深Partners，Tech + Law Dual Background团队。">',
   '<meta property="og:description" content="%s">' % EN_DESC),
  ('<p>IP litigation and legal protection — patent infringement, trademark disputes,<br>unfair competition, technology contract disputes. Earning respect through expertise.</p>',
   '<p>IP litigation as our core strength, plus full-service legal support — patent infringement, trademark disputes,<br>unfair competition &amp; antitrust, administrative law, criminal defense &amp; compliance, maritime and international law. Earning respect through expertise.</p>'),
  ('<div class="section-title"><h2>Practice Areas</h2><p>Full-Spectrum IP Legal Protection</p></div>',
   '<div class="section-title"><h2>Practice Areas</h2><p>Full-Spectrum Legal Protection · IP Litigation Focus</p></div>'),
  ('<div class="stat-label">资深Partners</div>',
   '<div class="stat-label">Senior Partners</div>'),
 ],
 'fr/mili/index.html': [
  ('<meta name="description" content="Mili Cabinet d\'Avocats — Protection Juridique PI。提供Contentieux de Contrefaçon、Litiges de Marques、Concurrence Déloyale、Contrats PI等法律服务。85% de Résultats Favorables，5位资深Associés，Double Compétence Tech + Droit团队。">',
   '<meta name="description" content="%s">' % FR_DESC),
  ("<title>Mili Cabinet d'Avocats — Protection Juridique PI</title>",
   "<title>Mili Cabinet d&#x27;Avocats — Cabinet Pluridisciplinaire · Contentieux PI</title>"),
  ('<meta property="og:title" content="Mili Cabinet d&#x27;Avocats">',
   '<meta property="og:title" content="Mili Cabinet d&#x27;Avocats — Cabinet Pluridisciplinaire · Contentieux PI">'),
  ('<meta property="og:description" content="Mili Cabinet d">',
   '<meta property="og:description" content="%s">' % FR_DESC),
  ("<p>Contentieux PI et protection juridique — contrefaçon de brevets, litiges de marques,<br>concurrence déloyale, contrats technologiques. Gagner le respect par l'expertise.</p>",
   "<p>Contentieux PI comme spécialité, et accompagnement juridique complet — contrefaçon de brevets, litiges de marques,<br>concurrence déloyale et antitrust, droit administratif, defense penale et conformite, droit maritime et international. Gagner le respect par l'expertise.</p>"),
  ('<div class="section-title"><h2>Domaines d\'activité</h2><p>Protection Juridique PI Complète</p></div>',
   '<div class="section-title"><h2>Domaines d\'activité</h2><p>Protection Juridique Complète · Spécialité Contentieux PI</p></div>'),
  ('<div class="stat-label">资深Associés</div>',
   '<div class="stat-label">Associés expérimentés</div>'),
 ],
 'en/aipunajie/index.html': [
  ('(Special General Partnership) — Founded 2012 in Chaoyang, Beijing.',
   '(Special General Partnership) — Founded in 2012; registered domicile: Dongcheng District, Beijing.'),
  ('was founded in 2012, headquartered in Chaoyang District, Beijing.',
   'was founded in 2012, with its registered domicile at No. 11 Chongwenmenwai Street, Dongcheng District, Beijing (shared business office: 1502, Baogang Tower, Jianguomenwai Avenue, Chaoyang District).'),
 ],
 'fr/aipunajie/index.html': [
  ('— Fondée en 2012, à Chaoyang, Pékin.',
   '— Fondée en 2012 ; siège social dans le district de Dongcheng, Pékin.'),
  ("a été fondée en 2012, dont le siège est à Chaoyang, Pékin.",
   "a été fondée en 2012 ; son siège social est situé au n° 11, rue Chongwenmenwai, district de Dongcheng, Pékin (bureau partagé : 1502, Baogang Tower, avenue Jianguomenwai, district de Chaoyang)."),
 ],
}

EN_LD = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "@id": "https://najieip.com/#org-mili",
  "name": "Mili Law Firm",
  "legalName": "Beijing Mili Law Offices",
  "alternateName": ["北京觅理律师事务所", "Mili Cabinet d'Avocats"],
  "identifier": "31110000MD0262382F",
  "description": "Full-service law firm, not IP-only: IP litigation, trade secrets, unfair competition & antitrust, administrative law, criminal defense & compliance, maritime law, international law, civil & commercial disputes, and general corporate counsel. A branch office operates in Changping District, Beijing.",
  "url": "https://najieip.com/en/mili/",
  "address": {"@type": "PostalAddress", "streetAddress": "Room 1502, Baogang Tower, No. 12-12 (Bing), Jianguomenwai Avenue", "addressLocality": "Chaoyang District", "addressRegion": "Beijing", "addressCountry": "CN"},
  "areaServed": ["CN"],
  "knowsLanguage": ["zh", "en"],
  "numberOfEmployees": "5",
  "brand": {"@type": "Brand", "name": "Najie IP", "alternateName": "纳杰觅理", "url": "https://najieip.com/"},
  "memberOf": {"@id": "https://najieip.com/#organization"},
  "knowsAbout": ["IP litigation", "trade secrets", "unfair competition", "antitrust", "administrative law", "criminal defense and compliance", "maritime law", "international law", "civil and commercial dispute resolution", "corporate legal counsel"],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "legal consultation",
    "telephone": "+86-10-65150974",
    "email": "collection@najieip.com"
  }
}
</script>'''

FR_LD = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LegalService",
  "@id": "https://najieip.com/#org-mili",
  "name": "Mili Cabinet d&#x27;Avocats",
  "legalName": "Beijing Mili Law Offices",
  "alternateName": ["北京觅理律师事务所", "Mili Law Firm"],
  "identifier": "31110000MD0262382F",
  "description": "Cabinet pluridisciplinaire, au-dela de la PI : contentieux PI, secrets d&#x27;affaires, concurrence deloyale et antitrust, droit administratif, defense penale et conformite, droit maritime, droit international, litiges civils et commerciaux, conseil juridique permanent. Une succursale a Changping, Pekin.",
  "url": "https://najieip.com/fr/mili/",
  "address": {"@type": "PostalAddress", "streetAddress": "Bureau 1502, Baogang Tower, 12-12 (Bing) avenue Jianguomenwai", "addressLocality": "District de Chaoyang", "addressRegion": "Pekin", "addressCountry": "CN"},
  "areaServed": ["CN"],
  "knowsLanguage": ["zh", "fr"],
  "numberOfEmployees": "5",
  "brand": {"@type": "Brand", "name": "Najie IP", "alternateName": "纳杰觅理", "url": "https://najieip.com/"},
  "memberOf": {"@id": "https://najieip.com/#organization"},
  "knowsAbout": ["contentieux PI", "secrets d&#x27;affaires", "concurrence deloyale", "antitrust", "droit administratif", "defense penale et conformite", "droit maritime", "droit international", "litiges civils et commerciaux", "conseil juridique permanent"],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "consultation juridique",
    "telephone": "+86-10-65150974",
    "email": "collection@najieip.com"
  }
}
</script>'''

HREFLANG = ('<link rel="alternate" hreflang="zh-CN" href="https://najieip.com/mili/">\n'
            '<link rel="alternate" hreflang="en" href="https://najieip.com/en/mili/">\n'
            '<link rel="alternate" hreflang="fr" href="https://najieip.com/fr/mili/">\n'
            '<link rel="alternate" hreflang="x-default" href="https://najieip.com/mili/">')

ADDITIONS = {
 'mili/index.html': [
   ('<link rel="canonical" href="https://najieip.com/mili/">',
    '<link rel="canonical" href="https://najieip.com/mili/">\n' + HREFLANG),
 ],
 'en/mili/index.html': [
   ('<link rel="canonical" href="https://najieip.com/en/mili/">',
    '<link rel="canonical" href="https://najieip.com/en/mili/">\n' + HREFLANG),
   ('</head>', EN_LD + '\n</head>'),
 ],
 'fr/mili/index.html': [
   ('<link rel="canonical" href="https://najieip.com/fr/mili/">',
    '<link rel="canonical" href="https://najieip.com/fr/mili/">\n' + HREFLANG),
   ('</head>', FR_LD + '\n</head>'),
 ],
}

ok = True
for f, pairs in EDITS.items():
    t = open(f, encoding='utf-8').read()
    for old, new in pairs:
        c = t.count(old)
        if c != 1:
            print('❌ %-24s 匹配 %d 次（期望 1）: %s' % (f, c, old[:70]))
            ok = False
            continue
        t = t.replace(old, new, 1)
    for old, new in ADDITIONS.get(f, []):
        c = t.count(old)
        if c != 1:
            print('❌ %-24s [ADD] 匹配 %d 次（期望 1）: %s' % (f, c, old[:60]))
            ok = False
            continue
        t = t.replace(old, new, 1)
    if APPLY and ok:
        shutil.copy2(f, f + '.bak-20260927')
        open(f, 'w', encoding='utf-8').write(t)
        print('✅ %s 已写入（%d 处替换 + %d 处插入）' % (f, len(pairs), len(ADDITIONS.get(f, []))))
    else:
        print('… %s 校验通过（%d 处替换 + %d 处插入）%s' % (f, len(pairs), len(ADDITIONS.get(f, [])), '' if APPLY else ' [dry-run]'))

# 残留检查
print('\n=== 残留中文（EN/FR 描述字段） ===')
import re
for f in ['en/mili/index.html', 'fr/mili/index.html', 'en/aipunajie/index.html', 'fr/aipunajie/index.html']:
    t = open(f, encoding='utf-8').read()
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    d = m.group(1) if m else ''
    print('%-24s 中文字=%d 长度=%d' % (f, len(re.findall(r'[\u4e00-\u9fff]', d)), len(d)))
print('\nAPPLY=%s  OK=%s' % (APPLY, ok))
