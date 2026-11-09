"""OR2a · What if everyone disappeared except you? · lege stad (ochtend), regel 1-3.

1  hook: dichtbij je gezicht, je kijkt om je heen; de camera schiet omhoog: jij alleen op een leeg kruispunt.
2  HOUR 1: een rij auto's voor rood, motoren lopen nog (uitlaatwolkjes), niemand achter het stuur. Jij loopt ertussen.
3  DAY 1: jij staat op het dak van een auto met je armen omhoog. De stad is van jou.

    python3 anim/shorts/or2a_stad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or2", "a", "stad", "ochtend", lines=(1, 2, 3))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR2-{n:02d}"][i]["s"]
S.clip = (0.05, 3000)

# geen bestuurders: de auto's staan er verlaten bij (ook de open cabine van de rode auto blijft leeg)
for o in list(bpy.data.objects):
    if o.name.startswith(("Bestuurder", "Chauffeur")):
        o.hide_render = o.hide_viewport = True

P1 = V(0.8, -2.5, 0)
held = S.actor("hoofdpersonage", P1, 180)
HEAD1 = S.head(held, 0.0)

# -- regel 1: wakker, alleen ------------------------------------------------------------------------
S.beat(held, 0.0, "staan", face="verbaasd", face_amt=0.7, look=(0.4, 0.1), body={"head": (0, 0, 25), "neck": (0, 0, 10)})
S.beat(held, W(1, 3), "staan", face="verbaasd", face_amt=0.8, look=(-0.4, 0.1), body={"head": (0, 0, -25), "neck": (0, 0, -10)})
S.beat(held, W(1, 6), "staan", face="bang", face_amt=0.8, look=(0, 0.3), body={"head": (-8, 0, 0)})
S.beat(held, L[1][1], "staan", face="bang", face_amt=0.9, look=(0, 0.3), body={"head": (-10, 0, 0)})
S.cam(0.0, ((HEAD1.x + 0.35, HEAD1.y + 1.5, HEAD1.z + 0.05), tuple(HEAD1 + V(0, 0, -0.05)), 30),
      ((HEAD1.x + 0.35, HEAD1.y + 1.7, HEAD1.z + 0.1), tuple(HEAD1 + V(0, 0, -0.05)), 30))
UP = W(1, 5) - 0.1
S.cam(UP, ((P1.x + 0.6, P1.y + 2.2, 1.6), tuple(P1 + V(0, 0, 0.9)), 24),
      ((P1.x + 3.0, P1.y + 16.0, 22.0), tuple(P1 + V(0, -6.0, 0.0)), 22))
S.sfx("sfx_whoosh", UP - 0.05, 0.35)

# -- regel 2: HOUR 1, de rij auto's ------------------------------------------------------------------
h1 = L[2][0]
wa, wb = V(1.3, -11.0, 0), V(1.3, -17.2, 0)
S.teleport(held, h1, wa, 0)
S.walk(held, h1 + 0.05, L[3][0] - 0.06, [wa, wb], stride=0.42, arms=0.4)
S.beat(held, h1 + 0.1, "staan", face="nerveus", face_amt=0.7, look=(0.6, 0.0), feet="keep")
S.beat(held, W(2, 6), "staan", face="verbaasd", face_amt=0.8, look=(0.8, -0.1), feet="keep", body={"head": (0, 0, 35), "neck": (0, 0, 15)})
S.beat(held, L[3][0] - 0.06, "staan", face="verbaasd", face_amt=0.8, look=(0.8, -0.1), feet="keep", body={"head": (0, 0, 30)})
# uitlaatwolkjes achter elke auto (de auto's kijken naar +y; uitlaat achteraan rechts)
CARS = [V(3.0, -12.6 - i * 5.6, 0) for i in range(4)]
for i, c in enumerate(CARS):
    pipe = c + V(0.55, -2.15, 0.28)
    t = h1 + 0.07 * i
    while t < L[3][0]:
        S.puff(pipe, t, n=3, r=(0.16, 0.26), grow=2.2, dur=1.2, color=(0.86, 0.87, 0.9), rise=0.4, spread=0.3)
        t += 0.45
S.cam(h1, ((0.1, -22.5, 0.55), (2.0, -12.5, 0.85), 26), ((0.2, -21.6, 0.6), (1.8, -13.0, 0.9), 28))
S.sfx("sfx_konvooi", h1, 0.12, cut=L[3][0] + 0.2)
S.counter("HOUR 1", h1, L[2][1])

# -- regel 3: DAY 1, op het dak van een auto ---------------------------------------------------------
d1 = L[3][0]
ROOF = V(3.0, -18.0, 1.24)
S.teleport(held, d1, ROOF, 120)
S.beat(held, d1, "juichen", face="lach", face_amt=1.0, look=(0, 0.4))
S.beat(held, d1 + 0.5, "juichen", amount=0.9, face="lach", face_amt=1.0, look=(0, 0.5), body={"spine": (-4, 0, 6)})
S.beat(held, d1 + 1.1, "juichen", face="lach", face_amt=1.0, look=(0, 0.5), body={"spine": (-4, 0, -6)})
S.beat(held, END, "juichen", face="lach", face_amt=1.0, look=(0, 0.5), body={"spine": (-4, 0, 0)})
S.cam(d1, ((6.6, -14.0, 0.5), tuple(ROOF + V(0, 0, 0.9)), 20), ((6.4, -22.0, 0.55), tuple(ROOF + V(0, 0, 0.9)), 20))
S.counter("DAY 1", d1, L[3][1])

# -- geluid ------------------------------------------------------------------------------------------
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.12)
S.music_all("m_nacht_angst", vol=0.24)
S.done()
