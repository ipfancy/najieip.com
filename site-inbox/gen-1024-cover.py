#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门丞 1024 封面图：纯文字排版（原创排版，无 AI 图像素材），1200x630 OG 卡。"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = "/mnt/c/Users/zigan/najieip-site"
FB = "/mnt/c/Windows/Fonts/msyhbd.ttc"   # 微软雅黑 Bold
FR = "/mnt/c/Windows/Fonts/msyh.ttc"     # 微软雅黑 Regular

CARDS = [
    dict(slug="20261024-mili-personal-safety-protection-order",
         kicker="人身安全保护令 · 反家庭暴力法",
         lines=["保护令拿到了，", "不等于家暴已认定"],
         entity="北京觅理律师事务所",
         date="2026-10-24 · najieip.com",
         color=(18, 70, 114)),
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
        img = vgrad(W, H, (28, 28, 34), (12, 12, 16))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 14, H], fill=base)
        d.ellipse([W - 300, -160, W + 120, 260], outline=(255, 255, 255, 12), width=2)
        d.ellipse([W - 220, -80, W + 60, 200], outline=(255, 255, 255, 10), width=2)

        f_kicker = ImageFont.truetype(FR, 30)
        f_title = ImageFont.truetype(FB, 74)
        f_ent = ImageFont.truetype(FR, 28)
        f_date = ImageFont.truetype(FR, 26)

        d.rectangle([72, 150, 152, 156], fill=(201, 162, 39))
        d.text((176, 132), c["kicker"], font=f_kicker, fill=(201, 162, 39))

        y = 226
        for ln in c["lines"]:
            d.text((72, y), ln, font=f_title, fill=(255, 255, 255))
            y += 96

        d.rectangle([72, H - 132, W - 72, H - 131], fill=(255, 255, 255, 30))
        d.text((72, H - 104), c["entity"], font=f_ent, fill=(226, 232, 238))
        tw = d.textlength(c["date"], font=f_date)
        d.text((W - 72 - tw, H - 100), c["date"], font=f_date, fill=(148, 163, 184))

        out = os.path.join(REPO, "img", c["slug"] + ".png")
        img.save(out, "PNG", optimize=True)
        print("OK", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
