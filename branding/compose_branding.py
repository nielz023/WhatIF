"""Zet logo en banner voor "Way Too Far" in elkaar uit de renders van render_branding.py.

    python3 branding/compose_branding.py <map met renders> <uitmap> <fontmap>

Fonts (Google Fonts, OFL): Anton-Regular.ttf en Montserrat[wght].ttf in <fontmap>.
Uit: logo_800.png (YouTube-profielfoto, wordt rond bijgesneden) en banner_2560x1440.png
(alles wat belangrijk is staat in de veilige zone van 1546x423 in het midden).
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT, FONTS = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
MONT = os.path.join(FONTS, "Montserrat[wght].ttf")
if not os.path.exists(MONT):
    MONT = os.path.join(FONTS, "Montserrat%5Bwght%5D.ttf")

ORANJE = (245, 128, 37)
GEEL = (255, 214, 64)
NACHT = (20, 16, 52)
PAARS = (68, 44, 150)
WIT = (255, 255, 255)
INKT = (26, 22, 48)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def radial(size, inner, outer, center=None, radius=None):
    w, h = size
    cx, cy = center or (w / 2, h / 2)
    radius = radius or math.hypot(w, h) / 2
    small = Image.new("RGB", (w // 4, h // 4))
    px = small.load()
    for y in range(h // 4):
        for x in range(w // 4):
            d = min(1.0, math.hypot(x * 4 - cx, y * 4 - cy) / radius)
            px[x, y] = lerp(inner, outer, d ** 1.3)
    return small.resize(size, Image.BICUBIC)


def rays(size, center, color, n=18, alpha=40):
    """Stripboek-stralen vanuit het midden."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    R = math.hypot(w, h)
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = a0 + math.pi / n
        pts = [center, (center[0] + R * math.cos(a0), center[1] + R * math.sin(a0)),
               (center[0] + R * math.cos(a1), center[1] + R * math.sin(a1))]
        d.polygon(pts, fill=(*color, alpha))
    return layer


def stars(img, box, n, seed=7):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice((1, 1, 1.5, 2, 3))
        a = rnd.randint(120, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))


def shadow(sprite, offset, blur, color=(0, 0, 0), alpha=110):
    a = sprite.split()[3].point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", sprite.size, (*color, 0))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (sprite.width + abs(offset[0]), sprite.height + abs(offset[1])), (0, 0, 0, 0))
    out.alpha_composite(sh, (max(0, offset[0]), max(0, offset[1])))
    out.alpha_composite(sprite, (max(0, -offset[0]), max(0, -offset[1])))
    return out


def outline_sprite(sprite, width, color):
    """Dikke witte rand rond het personage, zodat het loskomt van de achtergrond."""
    a = sprite.split()[3].filter(ImageFilter.MaxFilter(width * 2 + 1))
    ring = Image.new("RGBA", sprite.size, (*color, 0))
    ring.putalpha(a)
    ring.alpha_composite(sprite)
    return ring


def block_text(draw, xy, text, f, fill, depth, depth_color, stroke=0, stroke_fill=INKT, anchor="ls"):
    """Tekst met een 3D-blokschaduw (schuin naar rechtsonder)."""
    x, y = xy
    for k in range(depth, 0, -1):
        draw.text((x + k, y + k), text, font=f, fill=depth_color, anchor=anchor,
                  stroke_width=stroke, stroke_fill=depth_color)
    draw.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


# ------------------------------------------------------------------- logo
def make_logo():
    S = 1600
    bg = radial((S, S), PAARS, NACHT).convert("RGBA")
    bg.alpha_composite(rays((S, S), (S / 2, S * 0.46), GEEL, n=20, alpha=26))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((S * 0.18, S * 0.12, S * 0.82, S * 0.78), fill=(*ORANJE, 120))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(140)))
    held = Image.open(os.path.join(SRC, "logo_held.png")).convert("RGBA")
    held = outline_sprite(held, 10, WIT)
    scale = 1.06
    held = held.resize((int(held.width * scale), int(held.height * scale)), Image.LANCZOS)
    held = shadow(held, (0, 18), 26, alpha=120)
    bg.alpha_composite(held, ((S - held.width) // 2, S - held.height + 70))
    logo = bg.resize((800, 800), Image.LANCZOS).convert("RGB")
    logo.save(os.path.join(OUT, "logo_800.png"))
    # voorbeeld zoals YouTube hem toont (rond)
    prev = Image.new("RGBA", (800, 800), (255, 255, 255, 255))
    mask = Image.new("L", (800, 800), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 799, 799), fill=255)
    prev.paste(logo, (0, 0), mask)
    prev.convert("RGB").save(os.path.join(OUT, "voorbeeld_logo_rond.png"))


# ----------------------------------------------------------------- banner
def make_banner():
    W, H = 2560, 1440
    SX0, SY0, SX1, SY1 = 507, 508, 2053, 931          # veilige zone (alle apparaten)
    # links gewone blauwe lucht, naar rechts zonsondergang en dan de ruimte in: het loopt uit de hand
    stops = [(0.0, (110, 185, 245)), (0.30, (255, 170, 90)), (0.52, (220, 70, 80)), (0.72, PAARS), (1.0, NACHT)]
    small = Image.new("RGB", (W // 4, H // 4))
    px = small.load()
    for x in range(W // 4):
        t = x * 4 / W
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                col = lerp(c0, c1, (t - p0) / (p1 - p0))
                break
        for y in range(H // 4):
            v = 1.0 - 0.18 * abs(y * 4 - H / 2) / (H / 2)
            px[x, y] = tuple(int(c * v) for c in col)
    bg = small.resize((W, H), Image.BICUBIC).convert("RGBA")
    stars(bg, (W * 0.55, 0, W, H), 420)
    # planeet rechtsboven, voor wie de hele banner ziet (tv)
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pl)
    d.ellipse((W - 330, 60, W + 130, 520), fill=(120, 170, 255, 255))
    d.ellipse((W - 300, 50, W + 160, 510), fill=(0, 0, 0, 0))
    bg.alpha_composite(pl.filter(ImageFilter.GaussianBlur(2)))
    # stripboekstralen achter het personage
    hx = SX0 + 230
    bg.alpha_composite(rays((W, H), (hx, (SY0 + SY1) / 2), (255, 255, 255), n=26, alpha=12))

    # personage: hoofd en romp binnen de veilige zone, benen lopen eronder door (zichtbaar op tv)
    held = Image.open(os.path.join(SRC, "banner_held.png")).convert("RGBA")
    held = held.crop(held.getbbox())
    target_h = 740
    held = held.resize((int(held.width * target_h / held.height), target_h), Image.LANCZOS)
    held = outline_sprite(held, 8, WIT)
    held = shadow(held, (10, 16), 18, alpha=110)
    top = SY0 + 12
    feet = top + target_h
    vloer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(vloer).ellipse((hx - 150, feet - 22, hx + 150, feet + 22), fill=(0, 0, 0, 90))
    bg.alpha_composite(vloer.filter(ImageFilter.GaussianBlur(12)))
    bg.alpha_composite(held, (int(hx - held.width / 2), top))

    # tekst: WAY TOO FAR, elk woord groter (escalatie)
    d = ImageDraw.Draw(bg)
    x = SX0 + 500
    base = SY0 + 300
    f1, f2, f3 = font(ANTON, 150), font(ANTON, 205), font(ANTON, 270)
    words = [("WAY", f1, WIT), ("TOO", f2, WIT), ("FAR", f3, GEEL)]
    for word, f, col in words:
        block_text(d, (x, base), word, f, col, depth=12, depth_color=INKT, stroke=6)
        x += d.textlength(word, font=f) + 38
    sub = font(MONT, 46, weight=800)
    tag = "A NEW 3D WHAT IF EVERY WEEK"
    tx = SX0 + 505
    ty = base + 80
    tw = d.textlength(tag, font=sub)
    d.rounded_rectangle((tx - 22, ty - 46, tx + tw + 22, ty + 18), radius=14, fill=(*INKT, 230))
    d.text((tx, ty), tag, font=sub, fill=WIT, anchor="ls")
    bg.convert("RGB").save(os.path.join(OUT, "banner_2560x1440.png"))

    # controlebeeld met de veilige zones
    chk = bg.copy()
    dc = ImageDraw.Draw(chk)
    dc.rectangle((SX0, SY0, SX1, SY1), outline=(0, 255, 120, 255), width=6)
    dc.rectangle((0, SY0, W - 1, SY1), outline=(255, 255, 0, 255), width=4)
    chk.convert("RGB").resize((1280, 720)).save(os.path.join(OUT, "controle_veilige_zone.jpg"), quality=90)
    # voorbeeld zoals op mobiel (alleen de veilige zone)
    bg.crop((SX0, SY0, SX1, SY1)).convert("RGB").save(os.path.join(OUT, "voorbeeld_banner_mobiel.png"))


make_logo()
make_banner()
print("KLAAR", OUT)
