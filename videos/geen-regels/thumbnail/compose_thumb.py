"""Zet de tekst NO MORE RULES op de thumbnail-renders van video 3 (1280x720, YouTube).

    python3 videos/geen-regels/thumbnail/compose_thumb.py [render_dir] [uit_dir]

Leest out/thumb/render_<variant>.png (uit thumb_no_rules.py) en schrijft thumb_<variant>.png/.jpg plus
thumb_overzicht.jpg (alle varianten onder elkaar, ook op telefoonformaat om leesbaarheid te checken).
Huisstijl: Anton, witte en gele letters met dikke zwarte rand en een donkere 3D-blokschaduw.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "out", "thumb")
DST = sys.argv[2] if len(sys.argv) > 2 else SRC
FONT = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
W, H = 1280, 720
WHITE = (255, 255, 255)
YELLOW = (255, 214, 30)
RED = (255, 40, 30)

# per variant: (regels, linkerrand, onderrand) — tekst links, het gezicht staat rechts
LAYOUT = {
    "groot": dict(x=38, bottom=405),          # boven het grote scherm, dat blijft zichtbaar
    "straat": dict(x=38, bottom=690),
    "omhoog": dict(x=38, bottom=690),
}
LINES = [("NO MORE", 150, WHITE), ("RULES", 250, YELLOW)]


def grade(im):
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.18)
    # rode vignet aan de randen + donkerder linksonder achter de tekst
    w, h = im.size
    vig = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(vig)
    d.ellipse((-w * 0.25, -h * 0.35, w * 1.25, h * 1.35), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGB", (w, h), (40, 0, 0))
    im = Image.composite(im, dark, vig)
    grad = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(int(w * 0.55)):
        a = int(110 * (1 - x / (w * 0.55)) ** 1.6)
        gd.line([(x, int(h * 0.45)), (x, h)], fill=a)
    grad = grad.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), im, grad)
    return im


def block_text(base, x, y, text, size, fill):
    font = ImageFont.truetype(FONT, size)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    depth = max(6, size // 18)
    for k in range(depth, 0, -1):                    # 3D-blokschaduw schuin rechtsonder
        d.text((x + k, y + k), text, font=font, fill=(20, 0, 0, 255), stroke_width=max(4, size // 24),
               stroke_fill=(20, 0, 0, 255))
    d.text((x, y), text, font=font, fill=fill + (255,), stroke_width=max(4, size // 24), stroke_fill=(0, 0, 0, 255))
    # zachte gloed onder alles voor contrast met de achtergrond
    glow = layer.split()[3].filter(ImageFilter.GaussianBlur(14))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow.putalpha(glow.point(lambda a: int(a * 0.7)))
    base.alpha_composite(shadow)
    base.alpha_composite(layer)
    return font.getbbox(text)


def compose(variant):
    src = os.path.join(SRC, f"render_{variant}.png")
    if not os.path.exists(src):
        return None
    im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
    im = grade(im).convert("RGBA")
    lay = LAYOUT.get(variant, LAYOUT["groot"])
    y = lay["bottom"]
    for text, size, col in reversed(LINES):           # van onder naar boven stapelen
        font = ImageFont.truetype(FONT, size)
        top, bot = font.getbbox(text)[1], font.getbbox(text)[3]
        y -= bot
        block_text(im, lay["x"], y, text, size, col)
        y += top - 6
    out = im.convert("RGB")
    os.makedirs(DST, exist_ok=True)
    out.save(os.path.join(DST, f"thumb_{variant}.png"))
    out.save(os.path.join(DST, f"thumb_{variant}.jpg"), quality=92)
    return out


def main():
    done = [(v, compose(v)) for v in LAYOUT]
    done = [(v, im) for v, im in done if im is not None]
    if not done:
        sys.exit("geen renders gevonden in " + SRC)
    # overzicht: groot + klein (zoals in de zoekresultaten op een telefoon, ~168 px breed)
    small_w = 320
    rows = []
    for v, im in done:
        row = Image.new("RGB", (W + small_w + 30, H), (18, 18, 24))
        row.paste(im, (0, 0))
        sm = im.resize((small_w, small_w * 9 // 16), Image.LANCZOS)
        row.paste(sm, (W + 15, (H - sm.height) // 2))
        ImageDraw.Draw(row).text((W + 15, (H - sm.height) // 2 + sm.height + 10), v, fill=(200, 200, 210),
                                 font=ImageFont.truetype(FONT, 36))
        rows.append(row)
    sheet = Image.new("RGB", (rows[0].width, sum(r.height for r in rows) + 12 * (len(rows) - 1)), (8, 8, 12))
    yy = 0
    for r in rows:
        sheet.paste(r, (0, yy))
        yy += r.height + 12
    sheet.save(os.path.join(DST, "thumb_overzicht.jpg"), quality=88)
    print("KLAAR", [v for v, _ in done], "->", DST)


if __name__ == "__main__":
    main()
