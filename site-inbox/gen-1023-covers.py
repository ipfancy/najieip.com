#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 1023 封面图：纯文字排版（原创排版，无 AI 图像素材），1200x630 OG 卡。"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = "/mnt/c/Users/zigan/najieip-site"
FB = "/mnt/c/Windows/Fonts/msyhbd.ttc"   # 微软雅黑 Bold
FR = "/mnt/c/Windows/Fonts/msyh.ttc"     # 微软雅黑 Regular

CARDS = [
    dict(slug="20261023-najie-trademark-law-70-days",
         kicker="商标法修订 · 2027-01-01 施行",
         lines=["商标新法还剩70天", "现在该做完的三件事"],
         entity="北京纳杰知识产权代理有限公司",
         color=(122, 31, 43)),
    dict(slug="20261023-aipunajie-overseas-patent-fto",
         kicker="出海专利风险 · FTO",
         lines=["出海没查专利", "货被扣"],
         entity="北京爱普纳杰专利代理事务所",
         color=(26, 82, 118)),
]


def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (1, h))
    for y in range(h):
        r = top[0] + (bottom[0] - top[0]) * y // (h - 1)
        g = top[1] + (bottom[1] - top[1]) * y // (h - 1)
        b = top[2] + (bottom[2] - top[2]) * y // (h - 1)
        img.putpixel((0, y), (r, g, b))
    return img.resize((w, h))


def main():
    W, H = 1200, 630
    for c in CARDS:
        base = c["color"]
        top = tuple(min(255, int(v * 1.35)) for v in base)
        img = vgrad(W, H, (28, 28, 34), (12, 12, 16))
        d = ImageDraw.Draw(img)
        # 左侧色块
        d.rectangle([0, 0, 14, H], fill=base)
        # 右上角淡色几何（原创几何，非素材图）
        d.ellipse([W - 300, -160, W + 120, 260], outline=(255, 255, 255, 12), width=2)
        d.ellipse([W - 220, -80, W + 60, 200], outline=(255, 255, 255, 10), width=2)

        f_kicker = ImageFont.truetype(FR, 30)
        f_title = ImageFont.truetype(FB, 74)
        f_ent = ImageFont.truetype(FR, 28)
        f_date = ImageFont.truetype(FR, 26)

        # 金色短线
        d.rectangle([72, 150, 152, 156], fill=(201, 162, 39))
        d.text((176, 132), c["kicker"], font=f_kicker, fill=(201, 162, 39))

        y = 226
        for ln in c["lines"]:
            d.text((72, y), ln, font=f_title, fill=(255, 255, 255))
            y += 96
        # 分隔线
        d.rectangle([72, H - 132, W - 72, H - 131], fill=(255, 255, 255, 30))
        d.text((72, H - 104), c["entity"], font=f_ent, fill=(226, 232, 238))
        dt = "2026-10-23 · najieip.com"
        tw = d.textlength(dt, font=f_date)
        d.text((W - 72 - tw, H - 100), dt, font=f_date, fill=(148, 163, 184))

        out = os.path.join(REPO, "img", c["slug"] + ".png")
        img.save(out, "PNG", optimize=True)
        print("OK", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
