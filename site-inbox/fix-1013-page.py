#!/usr/bin/env python3
"""SiteOps 1013 — 精修 mili/blog/20261010 部分裸发布页。
六项缺陷：无 JSON-LD / 无 og:image / 无 twitter 标题 / 无 keywords / 无 og:site_name / description 复读标题。
另：正文文本节点 ASCII 直引号 → 中文引号（房屋一致）。
用法: python3 site-inbox/fix-1013-page.py [--apply]
"""
import os, re, sys, json, copy, glob

ROOT = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(ROOT)
APPLY = "--apply" in sys.argv

TARGET = "mili/blog/20261010-mili-aigc-trade-secret-two-leaks.html"
TEMPLATE = "mili/blog/20261009-mili-ai-short-drama-token-evidence.html"
SLUG = TARGET.rsplit("/", 1)[-1]
URL = "https://najieip.com/" + TARGET
DATE = "2026-10-10"
TITLE = "AI团队最容易漏的2个泄密口子：不传文件，防泄露系统也抓不到"

DESC = ("北京市市场监管局 9 月 22 日《AIGC 企业商业秘密保护指引》征求意见稿点出两个最容易被漏掉的泄密口子："
        "一是研发人员用 AI 编程助手、代码补全插件时，工具索引整个代码仓库、每次交互把代码上下文发到云端，"
        "这种外发不体现为文件传输，常规数据防泄露措施难以识别；二是员工图方便把代码和 prompt 粘进公共模型，"
        "很多团队还不觉得这是泄密。本文拆解两个口子的技术路径、指引给出的具体做法，以及今天就能做的三个动作。")

KW = "AIGC,商业秘密保护,AI编程助手,代码外泄,数据防泄露,提示词,北京市市场监管局,企业合规"


def read(p):
    return open(p, encoding="utf-8").read()


t0 = read(TARGET)
tpl = read(TEMPLATE)

# ---- 1. 从模板取房屋 head 组件 ----
def grab(path, pat, label):
    m = re.search(pat, path, re.S)
    if not m:
        raise SystemExit(f"模板缺组件: {label}")
    return m.group(1).strip()

tpl_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S)
tpl_art = None
tpl_bc = None
for s in tpl_ld:
    o = json.loads(s)
    if o.get("@type") == "Article":
        tpl_art = o
    elif o.get("@type") == "BreadcrumbList":
        tpl_bc = o
if tpl_art is None or tpl_bc is None:
    raise SystemExit("模板缺 Article/BreadcrumbList JSON-LD")

tpl_ogimg = grab(tpl, r'<meta property="og:image" content="([^"]+)"', "og:image")
tpl_sitename = grab(tpl, r'<meta property="og:site_name" content="([^"]+)"', "og:site_name")

# 选一张本页未用过、且站内 mili 页已在用的 pexels 图（保证 URL 有效）
def pick_image(exclude_current):
    used = {}
    for f in glob.glob("mili/blog/*.html"):
        for u in re.findall(r'<meta property="og:image" content="(https://images\.pexels\.com/[^"]+)"', read(f)):
            used.setdefault(u, []).append(f)
    same = [u for u, fs in used.items() if all(f == TARGET for f in fs)]
    if same:
        return same[0]
    if exclude_current in used:
        return exclude_current
    return tpl_ogimg

IMG = pick_image(tpl_ogimg)

# ---- 2. JSON-LD 覆写 ----
art = copy.deepcopy(tpl_art)
art["headline"] = TITLE
art["description"] = DESC
art["image"] = IMG
art["datePublished"] = DATE
art["dateModified"] = DATE
art["mainEntityOfPage"] = URL
art["url"] = URL

bc = copy.deepcopy(tpl_bc)
items = bc["itemListElement"]
for it in items:
    if it.get("position") == 2:
        it["item"] = "https://najieip.com/mili/blog/"
    if it.get("position") == 3:
        it["name"] = TITLE
        it["item"] = URL

ld_art = json.dumps(art, ensure_ascii=False)
ld_bc = json.dumps(bc, ensure_ascii=False)

# ---- 3. 组装 head 补件 ----
def esc(v):
    return v.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

head_add = "\n".join([
    '<meta property="og:site_name" content="%s">' % esc(tpl_sitename),
    '<meta property="og:image" content="%s">' % IMG,
    '<meta name="twitter:card" content="summary_large_image">',
    '<meta name="twitter:title" content="%s">' % esc(TITLE),
    '<meta name="twitter:description" content="%s">' % esc(DESC),
    '<meta name="keywords" content="%s">' % esc(KW),
    '<script type="application/ld+json">%s</script>' % ld_art,
    '<script type="application/ld+json">%s</script>' % ld_bc,
])

t = t0

# description / og:description 去标题复读
t = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + esc(DESC) + m.group(2), t)
t = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + esc(DESC) + m.group(2), t)

# 已有 twitter:card（summary）替换为 summary_large_image
if '<meta name="twitter:card"' in t:
    t = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary_large_image">', t)

# JSON-LD 插在 </head> 之前（若尚无 ld+json），始终插 head_add
assert "</head>" in t
t = t.replace("</head>", head_add + "\n</head>", 1)

# ---- 4. 正文文本节点 ASCII 直引号 → 中文引号 ----
def zh_quotes(seg):
    out = []
    toggle = 0
    for ch in seg:
        if ch == '"':
            out.append("\u201c" if toggle == 0 else "\u201d")
            toggle ^= 1
        else:
            out.append(ch)
    return "".join(out)


def convert_text_nodes(html):
    parts = re.split(r"(<[^>]+>)", html)
    head_end = None
    for i, p in enumerate(parts):
        if p == "</head>":
            head_end = i
            break
    for i, p in enumerate(parts):
        if p.startswith("<"):
            continue
        if head_end is not None and i < head_end:
            continue  # 不动 head 内的裸文本
        nq = p.count('"')
        if nq == 1:
            continue  # 落单的引号不动（避免误配）
        if nq:
            parts[i] = zh_quotes(p)
    return "".join(parts)


t2 = convert_text_nodes(t)

# ---- 5. 断言 ----
errs = []
def assert_eq(label, a, b):
    if a != b:
        errs.append(f"{label}: {a} != {b}")

assert_eq("h1", len(re.findall(r"<h1[ >]", t2)), 1)
assert_eq("h2", len(re.findall(r"<h2[ >]", t2)), len(re.findall(r"<h2[ >]", t0)))
assert_eq("p", len(re.findall(r"<p[ >]", t2)), len(re.findall(r"<p[ >]", t0)))


def norm(html):
    """归一化 body 文本（排除 head 的 title/JSON-LD），用于逐字比对。"""
    b = html[html.find("<body"):]
    s = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    return re.sub(r"\s+", " ", s).strip()


n1, n2 = norm(t0), norm(t2)
if n1 != n2:
    import difflib
    d = [x for x in difflib.unified_diff(n1.split(), n2.split(), lineterm="", n=0)][:8]
    errs.append("body 文本不一致: " + " | ".join(d))

# ld+json 全部可解析；schema.org 真实存在
lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S)
if len(lds) != 2:
    errs.append(f"ld+json 块数 = {len(lds)} (期望 2)")
for i, s in enumerate(lds):
    try:
        json.loads(s)
    except Exception as e:
        errs.append(f"ld[{i}] 非法 JSON: {e}")
if t2.count("https://schema.org") < 2:
    errs.append("schema.org 缺失（疑似脱敏字面量）")
if "https://***" in t2:
    errs.append("存在 https://*** 脱敏字面量")
if t2.count("**") != 0:
    errs.append(f"** 泄漏 = {t2.count('**')}")
if len(re.findall(r'<meta name="description" content="([^"]*)"', t2)[0]) < 80:
    errs.append("description 过短")
assert_eq("og:image", len(re.findall(r'<meta property="og:image"', t2)), 1)

print("=== 修复计划 ===")
print(f"  文件: {TARGET}  {len(t0.encode())}B -> {len(t2.encode())}B")
print(f"  og:image = {IMG}")
print(f"  description 长度 = {len(DESC)}")
print(f"  ld+json 块 = {len(lds)}  schema.org 计数 = {t2.count('https://schema.org')}")
print(f"  正文归一后逐字相等 = {norm(t2) == norm(t0)}")
print("  断言:", "PASS" if not errs else "FAIL")
for e in errs:
    print("   -", e)

if not APPLY:
    print("\n(dry-run。加 --apply 写盘)")
    sys.exit(1 if errs else 0)

if errs:
    sys.exit(2)

open(TARGET, "w", encoding="utf-8").write(t2)
print("\n[APPLIED] 已写盘")
