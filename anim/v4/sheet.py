"""Contactvel met tijd + shotnaam per still: python3 anim/v4/sheet.py <code>"""
import sys, glob, os, re
from PIL import Image, ImageDraw
code = sys.argv[1]
log = open(f"out/stillscheck/{code}.log", errors="ignore").read()
cams = {float(t): c.split("_")[-1] for t, c in re.findall(r"STILL ([0-9.]+) frame \d+ camera (\S+)", log)}
fs = sorted(glob.glob(f"out/{code}/stills/*.png"))
if not fs: sys.exit()
ims = [Image.open(f).convert("RGB") for f in fs]
w, h = ims[0].size; C = 6; R = (len(ims) + C - 1) // C
sheet = Image.new("RGB", (C * w, R * h), (0, 0, 0)); d = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(zip(fs, ims)):
    x, y = (i % C) * w, (i // C) * h; sheet.paste(im, (x, y))
    t = float(re.search(r"_t([0-9.]+)\.png", f).group(1))
    lab = f"{code} {t:.2f}s shot {cams.get(t, '?')}"
    d.rectangle([x, y, x + 8 * len(lab) + 6, y + 16], fill=(0, 0, 0)); d.text((x + 3, y + 2), lab, fill=(255, 230, 0))
sheet.save(f"out/stillscheck/{code}.jpg", quality=82)
