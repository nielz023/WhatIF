"""N08i · Opa op de veranda (script scène 8i), straat, avondlicht.
8i-1 CLOSE: opa staat op de veranda, leunt op zijn stok en kijkt de straat in.
     OPA: "First they take what they need. Then they take what they want."
8i-2 WIDE vanaf de straat: opa klein op de veranda, de lege straat in de schemering, ver weg een oranje gloed.
     VO: "And on day three... people stop going to work."

    blender -b -P anim/v3/scenes/n08i_opa_veranda.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n08i", "straat", "avond", exposure=-0.4, night=True)
sh = S.cuts([5.4, 3.9])
END = sh[-1][1]
t_w = sh[1][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Boodschappentas", "Appels")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- opa op de veranda, kijkt de straat in (-y)
OPA_AT = V(-0.95, 11.95, 0.0)
opa = S.actor("opa", OPA_AT, 0, cane=True)
FAR = V(-30.0, 1.0, 1.4)                                    # de straat in, naar links
S.beat(opa, 0.0, "staan", face="neutraal", face_amt=0.6, at=FAR)
S.beat(opa, 1.2, "staan", face="boos", face_amt=0.4, at=FAR + V(0, 0, 0.2))
S.beat(opa, 2.8, "staan", face="nerveus", face_amt=0.5, at=V(-8.0, 2.0, 1.2))
S.beat(opa, 4.4, "staan", face="boos", face_amt=0.6, at=FAR)
S.beat(opa, END, "staan", face="neutraal", face_amt=0.5, at=FAR)
S.hold(opa, END)

# ---------------------------------------------------------------- ver weg in de straat: een oranje gloed (iets brandt)
glow = T.point_light("Gloed_ver", (-42.0, 2.0, 2.5), color=(1.0, 0.45, 0.15), energy=2500, radius=1.5)
for t, e in ((0.0, 2200), (1.3, 3000), (2.4, 2000), (3.8, 3200), (5.2, 2300), (6.6, 3100), (END, 2500)):
    light_key(glow, t, e, interp="LINEAR")

# ---------------------------------------------------------------- camera's
HO = S.headpos(opa, 2.5)
# 8i-1 CLOSE: van schuin voor, iets onder ooghoogte, heel trage push-in
S.cam(0.0, (HO + V(-0.9, -1.9, -0.1), HO + V(0, 0, -0.12), 32), (HO + V(-0.8, -1.65, -0.1), HO + V(0, 0, -0.1), 34))
# 8i-2 WIDE vanaf de overkant: opa klein op zijn veranda, de lege straat, trage pull-back
S.cam(t_w, (V(4.5, 3.2, 1.5), V(-3.5, 10.5, 1.6), 24), (V(6.0, 1.8, 1.7), V(-4.0, 10.0, 1.7), 24))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 2", 0, t0=0.0)
S.ambience("sfx_krekels_nacht", 0.0, END, vol=0.05)
S.say("N08-05", who=opa, at=0.3)
S.sfx("sfx_stad_nacht_wind", t_w, 0.06)
S.say("N08-06", at=t_w + 0.3)
S.finish(length=END, tail=0.0)
