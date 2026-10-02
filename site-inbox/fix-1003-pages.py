#!/usr/bin/env python3
# 2026-10-03 修复 3 篇新页的 Markdown 残留 / 缺 h1
import os, re, sys

R = os.path.expanduser("~/wiki/najieip-verify")
APPLY = "--apply" in sys.argv

PAGES = {
 "mili/blog/20260928-german-utility-model-offense.html": ("30欧、1个月拿证：长江存储拿下德国禁令的出海快刀", 2),
 "mili/blog/20261001-ai-voice-clone-shanghai-first-case-evidence-shift.html": ("上海首例AI声音案判5万，北京首例25万！差在举证", 1),
 "najie/blog/20261002-ai-patent-reply-evidence.html": ("用AI写专利答复被驳！国知局划下这3条红线", 0),
}

ROW = re.compile(r"^<p>\|(.*)\|</p>$")

def to_table(rows):
    cells = [[c.strip() for c in r.split("|")] for r in rows]
    # 去掉首尾空列（若存在）
    hdr = cells[0]
    body = [c for c in cells[1:] if not all(re.fullmatch(r":?-{2,}:?", x or "-") for x in c)]
    out = ['<table>', '<thead><tr>' + "".join(f"<th>{h}</th>" for h in hdr) + '</tr></thead>', '<tbody>']
    for c in body:
        while len(c) < len(hdr):
            c.append("")
        out.append('<tr>' + "".join(f"<td>{x}</td>" for x in c[:len(hdr)]) + '</tr>')
    out += ['</tbody>', '</table>']
    return out

for rel, (title, exp_tables) in PAGES.items():
    p = os.path.join(R, rel)
    t = open(p, encoding="utf-8").read()
    lines = t.split("\n")
    out, i, made = [], 0, 0
    while i < len(lines):
        m = ROW.match(lines[i])
        if m:
            blk = []
            j = i
            while j < len(lines) and ROW.match(lines[j]):
                blk.append(ROW.match(lines[j]).group(1))
                j += 1
            if len(blk) >= 3:
                out.extend(to_table(blk))
                made += 1
                i = j
                continue
        out.append(lines[i])
        i += 1
    t2 = "\n".join(out)
    t2 = t2.replace('\\"', "&#34;")
    t2 = t2.replace("|---", "&#124;---") if False else t2
    # **bold** -> <strong>
    t2 = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t2)
    # 缺 h1 则补
    if "<h1>" not in t2:
        assert t2.count("<article>") == 1
        t2 = t2.replace("<article>\n", f"<article>\n<h1>{title}</h1>\n<br>\n", 1)
    print(f"{rel}\n  tables_made={made} (expect {exp_tables}) h1={t2.count('<h1>')} "
          f"md_residue={t2.count('|---')} star={t2.count('**')} <table>={t2.count('<table>')}")
    assert made == exp_tables, f"{rel}: table count {made} != {exp_tables}"
    assert "<h1>" in t2 and t2.count("<h1>") == 1
    assert "|---" not in t2 and "**" not in t2
    # 文本保全断言
    PROBES = {
      "20260928-german-utility-model-offense.html": ["分离窗口2个月", "UPC口头审理约13个月", "保护客体"],
      "20261001-ai-voice-clone-shanghai-first-case-evidence-shift.html": ["殷某桢", "0491", "洗声"],
      "20261002-ai-patent-reply-evidence.html": ["202010182089.3", "1927206"],
    }
    key = os.path.basename(rel)
    for probe in PROBES[key]:
        assert probe in t2, f"{rel}: lost '{probe}'"
    if APPLY:
        open(p, "w", encoding="utf-8").write(t2)
print("APPLY" if APPLY else "DRY-RUN")
