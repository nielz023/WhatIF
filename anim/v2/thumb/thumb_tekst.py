"""Tekst op de thumbnails van video 2 (PIL): grote Anton-letters met een donkere 3D-blokschaduw
(huisstijl Driftmark), plus de HUD rechtsboven zoals in de video (DAY 4 · 1,000x).

    python3 anim/v2/thumb/thumb_tekst.py <render.png> <uit.png> "<regel 1>" ["<regel 2>"] [--pos links|rechts]
        [--hud "DAY 4  ·  1,000x"] [--kleur geel|wit]
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ANTON = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
W, H = 1280, 720
KLEUR = {"geel": (255, 214, 10), "wit": (255, 255, 255), "oranje": (255, 140, 30)}


def block_text(img, xy, text, size, fill, depth=10, shadow=(20, 16, 40), anchor="la", stroke=6):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(ANTON, size)
    x, y = xy
    # zachte gloed eronder zodat het op elke achtergrond leest
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((x + depth, y + depth), text, font=f, fill=(0, 0, 0, 200), anchor=anchor,
                              stroke_width=stroke + 8, stroke_fill=(0, 0, 0, 200))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    for k in range(depth, 0, -1):               # 3D-blok naar rechtsonder
        d.text((x + k, y + k), text, font=f, fill=shadow, anchor=anchor, stroke_width=stroke, stroke_fill=shadow)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(20, 16, 40))
    return d.textbbox((x, y), text, font=f, anchor=anchor, stroke_width=stroke)


def hud(img, text):
    """Zoals de HUD in de video: wit, rechtsboven, met een donkere pil erachter."""
    f = ImageFont.truetype(ANTON, 44)
    d = ImageDraw.Draw(img)
    x1, y0 = W - 28, 26
    bb = d.textbbox((x1, y0), text, font=f, anchor="ra")
    pill = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((bb[0] - 22, bb[1] - 12, bb[2] + 22, bb[3] + 14), 18, fill=(10, 14, 40, 170))
    img.alpha_composite(pill)
    d.text((x1, y0), text, font=f, fill=(255, 255, 255), anchor="ra")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("lines", nargs="+")
    ap.add_argument("--pos", default="links")
    ap.add_argument("--hud", default="DAY 4  ·  1,000x")
    ap.add_argument("--kleur", default="geel")
    ap.add_argument("--size", type=int, default=150)
    ap.add_argument("--y", type=int, default=None)
    ap.add_argument("--pop", type=float, default=1.12, help="extra contrast/verzadiging")
    a = ap.parse_args()

    img = Image.open(a.src).convert("RGB").resize((W, H), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(a.pop)
    img = ImageEnhance.Color(img).enhance(a.pop)
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    img = img.convert("RGBA")
    # licht vignet: oog naar het midden
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.15, -H * 0.25, W * 1.15, H * 1.25), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGBA", (W, H), (5, 8, 25, 150))
    dark.putalpha(Image.eval(vig, lambda v: int((255 - v) * 0.6)))
    img.alpha_composite(dark)

    if a.hud:
        hud(img, a.hud)
    y = a.y if a.y is not None else (110 if a.hud else 40)
    fill = KLEUR.get(a.kleur, KLEUR["geel"])
    for i, line in enumerate(a.lines):
        size = a.size if i == 0 else int(a.size * 0.62)
        col = fill if i == 0 else (255, 255, 255)
        if a.pos == "rechts":
            bb = block_text(img, (W - 50, y), line, size, col, anchor="ra")
        else:
            bb = block_text(img, (44, y), line, size, col, anchor="la")
        y = bb[3] + 6
    img.convert("RGB").save(a.dst, quality=95)
    print("OK", a.dst)


if __name__ == "__main__":
    main()
