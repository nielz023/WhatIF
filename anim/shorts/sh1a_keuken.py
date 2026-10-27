"""SH1a · What if you got 10x faster every day? · keuken: één knipper en de kom is leeg. Dag 1, en weg is hij.

    blender -b -P anim/shorts/sh1a_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh1", "a", "keuken", "ochtend", lines=(1, 2))
l1, l2 = S.L[1], S.L[2]

TZ = 0.76
SEAT = V(0.58, 0.02, 0)
BOWL = V(0.58, -0.36, TZ)
for n in ("Krant", "Stoel_1", "Stoel_2", "Ontbijt_broertje", "Ontbijt_bord"):
    S.obj(n).hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Krant_kolom"):
        o.hide_render = True
chair = S.obj("Stoel_4")
for n, dx in (("Cornflakes_doos", -0.95), ("Cornflakes_label", -0.95), ("Melkpak", -0.6), ("Melkpak_band", -0.6)):
    S.obj(n).location.x += dx                 # niet voor zijn gezicht

# ---------------------------------------------------------------- kom met ontbijtgranen
bowl = T.cyl("Kom", tuple(BOWL), 0.055, 0.07, S.mat("kom", (0.25, 0.55, 0.9)), r2=0.085, seg=32, ol=0.004, cap=False)
T.cyl("Kom_bodem", tuple(BOWL + V(0, 0, 0.002)), 0.054, 0.004, S.mat("kom", (0.25, 0.55, 0.9)), seg=32, ol=0)
milk = T.cyl("Melk", tuple(BOWL + V(0, 0, 0.055)), 0.078, 0.004, S.mat("melk", (0.97, 0.97, 0.94)), seg=32, ol=0)
rnd = random.Random(3)
pts = []
for k in range(40):
    a, r = rnd.uniform(0, 6.283), 0.07 * math.sqrt(rnd.random())
    pts.append(BOWL + V(r * math.cos(a), r * math.sin(a), 0.064 + rnd.uniform(0, 0.012)))
cereal = P.points_mesh("Ontbijtgranen", pts, 0.011, S.mat("granen", (0.95, 0.7, 0.25)))
spoon = T.box("Lepel", (0, 0, 0), (0.02, 0.15, 0.006), P.m("metaal"), bevel=0.003, ol=0.002)
EMPTY = 0.82                                   # de knipper: daarna is alles op
show(milk, 0, EMPTY)
show(cereal, 0, EMPTY)
milk2 = T.cyl("Melk_restje", tuple(BOWL + V(0, 0, 0.012)), 0.05, 0.003, S.mat("melk", (0.97, 0.97, 0.94)), seg=32, ol=0)
show(milk2, EMPTY)

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", SEAT, 0)
SIT, zs = sit(held)
S.place(held, 0, (SEAT.x, SEAT.y, zs), 0)
mama = S.actor("mama", (-0.9, 1.25, 0), 180, energy=0.7)        # bij het aanrecht, rug naar ons
coffee = S.obj("Koffiemok")
coffee.location = (-0.75, 1.55, 0.9)

# ---------------------------------------------------------------- muziek en geluid
S.music_all("subbas", vol=0.26)
S.music("drums_build", l2[0] - 0.2, S.total, vol=0.22, fade_in=1.5)
S.ambience("sfx_binnen_sfeer", 0.0, S.t1, vol=0.12)
S.sfx("sfx_whoosh", EMPTY - 0.05, 0.5)
S.sfx("sfx_slowmo", EMPTY + 0.3, 0.25)
VANISH = l2[0] + 3.0
S.sfx("sfx_whoosh_titel", VANISH - 0.05, 0.7)
S.sfx("sfx_schuiven", VANISH, 0.4)
S.counter("DAY 1", l2[0] + 0.1, sub="10x FASTER")

# ---------------------------------------------------------------- hij eet, knippert, alles is op
S.beat(held, 0.0, **SIT, pose="ontspannen", face="blij", face_amt=0.4, at=BOWL + V(0, 0, 0.05))
S.reach(held, 0.0, "R", BOWL + V(0.05, -0.02, 0.1))
grab(S, spoon, held, 0.0, "hand.R", mode="full", offset=(0, 0.05, 0))
A.blink_at(held, F(EMPTY - 0.1), closed=3)
# na de knipper: lepel in de lucht, wangen bol, verbaasd
S.reach(held, EMPTY, "R", S.head(held) + V(0.08, -0.22, -0.12))
S.beat(held, EMPTY, **SIT, pose="staan", face="verbaasd", face_amt=0.9, at=BOWL, mouth=0.0)
S.beat(held, EMPTY + 1.0, **SIT, pose="staan", face="verbaasd", face_amt=1.0, at=BOWL, body={"head": (10, 0, 0)})
S.beat(held, l1[0] + 3.3, **SIT, pose="staan", face="geschrokken", face_amt=0.9, at=S.head(held) + V(0, -0.5, -0.2))
S.reach(held, l1[0] + 3.3, "L", S.head(held) + V(-0.12, -0.32, -0.25))
S.reach(held, l1[0] + 3.3, "R", S.head(held) + V(0.12, -0.32, -0.25))
S.beat(held, l1[1] - 0.6, **SIT, pose="staan", face="nerveus", face_amt=0.8, look=(0, 0))
S.reach(held, l1[1] - 0.4, "L", None, 0.0)
S.reach(held, l1[1] - 0.4, "R", None, 0.0)
# dag 1: hij staat op en kijkt naar de deur, grijns
S.beat(held, l2[0] + 0.4, **SIT, pose="vuisten", face="vastberaden", face_amt=0.7, look=(0.6, 0))
S.place(held, l2[0] + 0.9, (SEAT.x, SEAT.y + 0.25, 0), 0)
S.beat(held, l2[0] + 1.0, "vuisten", face="grijns", face_amt=0.9, look=(0.7, 0), body={"head": (0, 0, -20)})
S.beat(held, VANISH - 0.3, "schrap", face="grijns", face_amt=1.0, look=(0.8, 0), crouch=(0.08, 6), body={"head": (-6, 0, -30)})
show(held.rig, 0, VANISH)
show(spoon, 0, VANISH)
# wat hij achterlaat: stofwolk, een tollende stoel, servetjes
S.puff(SEAT + V(0, 0.2, 0.4), VANISH, n=10, r=(0.15, 0.35), grow=2.2, dur=1.0, rise=0.3, spread=0.7)
S.debris(SEAT + V(0, -0.3, 0.8), VANISH, n=14, size=(0.04, 0.09), color=(0.97, 0.97, 0.95), speed=(1.5, 3.0), up=0.8,
         floor=0.0, life=2.5, name="Servet")
key(chair, VANISH - 0.02, rot=(0, 0, 0))
key(chair, VANISH + 1.6, rot=(0, 0, 540))
for fc in A._fcurves(chair):
    for kp in fc.keyframe_points:
        kp.interpolation = "QUAD"
        kp.easing = "EASE_OUT"

# mama: koffie, de luchtstroom, ze draait zich om
S.beat(mama, 0.0, "ontspannen", face="neutraal", at=coffee.location + V(0, 0, 0.1))
S.reach(mama, 0.0, "R", coffee.location + V(0.06, 0, 0.05))
S.hold(mama, VANISH)
S.beat(mama, VANISH + 0.15, "schrik", amount=0.6, face="geschrokken", at=SEAT + V(0, 0, 1.0))
S.turn(mama, VANISH + 0.3, VANISH + 0.9, 20, V(-0.9, 1.25, 0))
S.beat(mama, VANISH + 1.0, "schrik", amount=0.4, face="verbaasd", at=SEAT + V(0, 0, 0.9))
S.hold(mama, S.t1)

# ---------------------------------------------------------------- camera (staand)
S.cam(0.0, S.shot(held, 0.3, "med", az=6, lens=30, h=0.2), S.shot(held, EMPTY, "med", az=4, lens=32, h=0.2))
S.cam(EMPTY, S.shot(held, EMPTY + 0.5, "mcu", az=6, lens=34, h=0.1), S.shot(held, l1[0] + 2.0, "mcu", az=4, lens=38, h=0.1))
S.cam(l1[0] + 2.0, (BOWL + V(0.02, -0.22, 0.45), BOWL + V(0, 0, 0.02), 32), (BOWL + V(0.02, -0.18, 0.4), BOWL + V(0, 0, 0.02), 34), dof=2.0)
S.cam(l1[0] + 3.2, S.shot(held, l1[0] + 3.5, "mcu", az=10, lens=36), S.shot(held, l1[1], "mcu", az=6, lens=40))
S.cam(l2[0], ((1.9, -1.9, 1.55), (0.45, 0.0, 0.95), 24), ((1.8, -1.75, 1.5), (0.45, 0.1, 0.95), 26))
S.cam(l2[0] + 1.9, S.shot(held, l2[0] + 2.4, "mcu", az=30, lens=34, h=0.05),
      S.shot(held, VANISH - 0.1, "mcu", az=26, lens=38, h=0.0))
S.cam(VANISH, ((1.6, -2.0, 1.35), (0.2, 0.4, 0.75), 22), ((1.5, -1.85, 1.35), (0.2, 0.4, 0.8), 24), shake=lambda t: 1.5 * max(0, 1 - (t - VANISH) / 0.6))

S.done()
