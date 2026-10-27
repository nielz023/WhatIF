"""Zet de oude close-ups en de glans-close-ups naast elkaar (voor/na-blad).
Gebruik: python cast/voor_na.py <renders-map> <glans-map> <uitvoer.png> [figuur,figuur,...]"""
import sys
from PIL import Image, ImageDraw, ImageFont

oud, nieuw, uit = sys.argv[1:4]
keys = (sys.argv[4] if len(sys.argv) > 4 else "papa,oma,beste_vriend,pestkop").split(",")
import glob, os
S = 520
pad = 20
font = None
for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
    if os.path.exists(f):
        font = ImageFont.truetype(f, 34)
font = font or ImageFont.load_default()
W = pad + len(keys) * (S + pad)
H = 70 + 2 * (S + pad) + pad
sheet = Image.new("RGB", (W, H), (14, 18, 32))
d = ImageDraw.Draw(sheet)
for row, label in enumerate(("VOOR", "NA (glans)")):
    d.text((pad, 18 + row * 0), "", fill="white")
for k, key in enumerate(keys):
    a = glob.glob(os.path.join(oud, f"*_{key}_close-up.png"))
    b = os.path.join(nieuw, f"glans_{key}.png")
    x = pad + k * (S + pad)
    for row, path in enumerate((a[0] if a else None, b)):
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGB").resize((S, S), Image.LANCZOS)
            sheet.paste(im, (x, 70 + row * (S + pad)))
d.text((pad, 18), "VOOR (boven)  ·  NA, glans-look (onder)", fill=(235, 240, 255), font=font)
sheet.save(uit)
print(uit)
