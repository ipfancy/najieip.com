#!/usr/bin/env python3
# -*- coding: utf-8 -*-
with open('/Users/ziganghe/wiki/najieip-verify/sitemap.xml', encoding='utf-8') as f:
    xml = f.read()

assert 'trademark-compliance-selfcheck' not in xml, "sitemap 已有该文章"

new_urls = '''  <url>
    <loc>https://najieip.com/blog/trademark-compliance-selfcheck-20260810.html</loc>
    <lastmod>2026-08-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://najieip.com/najie/blog/trademark-compliance-selfcheck-20260810.html</loc>
    <lastmod>2026-08-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''

assert '</urlset>' in xml
xml = xml.replace('</urlset>', new_urls + '</urlset>', 1)
with open('/Users/ziganghe/wiki/najieip-verify/sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(xml)
print("sitemap.xml updated")
