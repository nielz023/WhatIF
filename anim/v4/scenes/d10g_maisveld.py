"""D10g · De inslag in het maïsveld (script scène 10g-10h).
10g WIDE 2,2 s: inslag in een maïsveld, een stofwolk. Stilte.
10h MEDIUM 5,3 s: hij kruipt uit de krater en spuugt een maïskorrel uit.
    VO: "You feel every single bone."  JONGEN: "Okay. No more planes."

    python3 anim/v4/scenes/d10g_maisveld.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d10g", "kleine_nd", "maisveld", exposure=0.15)
sh = S.cuts([2.2, 5.3])
END = sh[-1][1]
t_h = sh[1][0]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

CR = V(0.0, 4.0, 0.35)                                   # bovenkant van de kraterwal
T_HIT = 0.45
# stofwolk van de set: groeit bij de inslag
stof = S.obj("Stofwolk")
for t, sc in ((0.0, 0.01), (T_HIT, 0.01), (T_HIT + 0.35, 0.8), (t_h - 0.02, 1.0), (t_h, 0.01)):   # in 10h is het stof gaan liggen
    key(stof, t, scale=sc)
for o in [S.obj("Krater_mais"), S.obj("Kraterwal")]:      # de krater ontstaat bij de inslag
    for t, sc in ((0.0, 0.01), (T_HIT, 0.01), (T_HIT + 0.08, 1.0)):
        key(o, t, scale=sc)
for t in (T_HIT, T_HIT + 0.12):
    S.puff(CR + V(0, 0, 0.3), t, n=10, r=(0.6, 1.4), grow=2.4, dur=1.4, color=(0.62, 0.52, 0.40), rise=2.5, spread=2.2)

# ---------------------------------------------------------------- hij: komt uit de lucht, ligt in de krater, kruipt eruit
held = S.actor("hoofdpersonage_kind", CR, 0)
P_ = held.J["pelvis"].z
hb = Body(S, held, CR + V(0, 0, 40), 0)
S.qc_skip.add(held.name)
hb.key(0.0, CR + V(0, 0.4, 40.0), tilt=-90, interp="LINEAR")
hb.key(T_HIT, CR + V(0, 0, 0.12), tilt=-90)
LIE = CR + V(0, -0.2, 0.14)
hb.key(t_h, LIE, tilt=-88)
hb.key(t_h + 0.9, LIE, tilt=-86)
hb.key(t_h + 1.5, LIE + V(0, -0.05, 0.22), tilt=-58)              # duwt zich op handen en knieën
hb.key(t_h + 2.4, CR + V(0, -1.6, 0.30), tilt=-55)                # kruipt naar de rand (naar ons toe)
hb.key(t_h + 3.0, CR + V(0, -2.0, 0.22), tilt=-8)                 # op zijn knieën
hb.key(END, CR + V(0, -2.0, 0.22), tilt=-6)
FLAT = arms(arm("L", (0.90, 0.30, 0.20), (0.80, 0.50, 0.20)), arm("R", (0.90, 0.30, 0.20), (0.80, 0.50, 0.20)))
CRAWL_A = arms(arm("L", (0.25, 0.80, -0.55), (0.10, 0.75, -0.65)), arm("R", (0.25, 0.70, -0.70), (0.10, 0.55, -0.83)))
CRAWL_B = arms(arm("L", (0.25, 0.70, -0.70), (0.10, 0.55, -0.83)), arm("R", (0.25, 0.80, -0.55), (0.10, 0.75, -0.65)))
KNEES = dict(feet=((0.14, -0.32, 0.42), (-0.14, -0.30, 0.42)), crouch=(0.0, 0.0))
S.beat(held, 0.0, "staan", arms=FLAT, face="schreeuw", face_amt=1.0)
S.beat(held, t_h, "staan", arms=FLAT, face="inspanning", face_amt=0.8, body={"head": (-30, 0, 0)}, **KNEES)
S.eyes_closed(held, t_h, t_h + 0.8)
for k, t in enumerate(frange(t_h + 1.4, t_h + 2.5, 0.28)):
    S.beat(held, t, "staan", arms=CRAWL_A if k % 2 else CRAWL_B, face="inspanning", face_amt=0.9, body={"head": (-35, 0, 0)},
           **KNEES)
S.beat(held, t_h + 3.0, "staan", face="twijfel", face_amt=0.7, body={"head": (0, 0, 0)}, mouth=0.6, **KNEES)
S.beat(held, t_h + 3.3, "staan", face="grijns", face_amt=0.4, mouth=0.9, **KNEES)          # spuugt
S.beat(held, t_h + 3.7, "staan", face="zelfverzekerd", face_amt=0.4, body={"head": (4, 0, 6)}, **KNEES)
S.beat(held, t_h + 4.6, "staan", face="twijfel", face_amt=0.8, body={"head": (4, 0, -6)}, **KNEES)
S.hold(held, END)
# de maïskorrel
korrel = T.sphere("Maiskorrel", (0, 0, 0), 0.025, S.mat("mais_geel", (1.0, 0.82, 0.15)), scale=(1, 0.8, 1.2), seg=8, ol=0)
MOUTH = S.head(held, t_h + 3.3) + V(0, -0.36, -0.16)
key(korrel, 0.0, loc=tuple(MOUTH), scale=0.001)
key(korrel, t_h + 3.3, loc=tuple(MOUTH), scale=0.001)
key(korrel, t_h + 3.33, loc=tuple(MOUTH), scale=1.0)
key(korrel, t_h + 3.6, loc=tuple(MOUTH + V(0.15, -0.55, 0.12)), scale=1.0)
key(korrel, t_h + 3.9, loc=tuple(MOUTH + V(0.25, -0.95, -0.5)), scale=1.0)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-14.0, -14.0, 6.0), V(0.0, 4.0, 1.0), 24), (V(-13.6, -13.6, 5.9), V(0.0, 4.0, 1.0), 24), handheld=0.08)
_hm = (S.headpos(held, t_h + 0.6) + S.headpos(held, END - 0.3)) * 0.5
S.cam(t_h, (_hm + V(2.7, -2.5, 0.15), _hm + V(0, 0, -0.5), 26), (_hm + V(2.5, -2.3, 0.15), _hm + V(0, 0, -0.45), 26))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2066, t0=0.0, tick=False)
S.sfx("sfx_inslag_veld", T_HIT - 0.05, 0.45)
S.say("D10-08", at=t_h + 0.3)
S.say("D10-09", who=held, at=t_h + 3.1)
S.sfx("sfx_blik_plop", t_h + 3.3, 0.2)
S.ambience("sfx_park_ochtend", t_h, END, vol=0.06)
S.finish(length=END, tail=0.0)
