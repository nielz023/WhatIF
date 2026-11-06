"""
Looproutekaart voor de medewerkers in Driftmark HQ.
Leest office_nav_raw.json (gemaakt door office_build.py) en tekent alle vlakken die in de
weg staan (tussen 10 cm en 1,75 m hoog) op een raster van 5 cm. Daarna worden obstakels
20 cm dikker gemaakt (de breedte van een medewerker). Wit = vrij, zwart = geblokkeerd.

Draaien:  python3 hq/blender/nav_build.py <office_nav_raw.json> <uitmap>
Maakt:    office_nav.png (720x720) en office_nav.json (maten, deuren, koffiehoeken, stoelen)
"""
import json, math, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

src = sys.argv[1]; out = sys.argv[2]
d = json.load(open(src))
HALF, RES = 18.0, 0.05
N = int(2 * HALF / RES)
R_BASE = 17.2

def px(x, z):
    return ((x + HALF) / RES, (z + HALF) / RES)

blk = Image.new('L', (N, N), 0)  # 255 = geblokkeerd
dr = ImageDraw.Draw(blk)
for f in d['faces']:
    q = [px(x, z) for x, z in f]
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    area = 0.0
    for i in range(len(q)):
        x0, y0 = q[i]; x1, y1 = q[(i + 1) % len(q)]
        area += x0 * y1 - x1 * y0
    if abs(area) > 0.5:
        dr.polygon(q, fill=255)
    dr.line(q + [q[0]], fill=255, width=2)

# buiten de achthoek is geen vloer
allow = Image.new('L', (N, N), 0)
oct_ = [px(math.sin(math.pi / 8 + k * math.tau / 8) * (R_BASE - 0.45), math.cos(math.pi / 8 + k * math.tau / 8) * (R_BASE - 0.45)) for k in range(8)]
ImageDraw.Draw(allow).polygon(oct_, fill=255)

free = ImageChops.subtract(allow, blk)  # 255 = vrij
free = free.point(lambda v: 255 if v > 127 else 0)
free = free.filter(ImageFilter.MinFilter(9))  # obstakels 4 px (20 cm) dikker
free.save(os.path.join(out, 'office_nav.png'), optimize=True)

meta = {
    'half': HALF, 'res': RES, 'n': N,
    'doors': {r: {'o': [po[0], po[2]], 'i': [pi[0], pi[2]]} for r, po, pi in d['doors']},
    'coffee': {r: {'p': [st[0], st[2]], 'l': [lk[0], lk[2]]} for r, st, lk in d['coffee']},
}
json.dump(meta, open(os.path.join(out, 'office_nav.json'), 'w'), separators=(',', ':'))
fr = sum(1 for v in free.getdata() if v)
print('nav', N, 'x', N, 'vrij', round(100 * fr / (N * N), 1), '%', 'deuren', len(meta['doors']), 'koffie', len(meta['coffee']))
