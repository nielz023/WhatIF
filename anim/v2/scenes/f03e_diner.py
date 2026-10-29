"""F03e · Dag 1 · 1x · maandagavond, diner. Opa vertelt zijn visverhaal (veertig minuten), oma knikt,
de rest staart naar zijn bord. 'Monday dinner. Grandpa tells his fishing story...'

    blender -b -P anim/v2/scenes/f03e_diner.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f03e", "keuken", "zondagsdiner")

TX, TY, TZ = 0.2, -0.6, 0.76
OPA_AT = V(TX - 0.7, TY + 0.62, 0)            # achter de tafel (kijken naar -y)
OMA_AT = V(TX + 0.0, TY + 0.62, 0)
HERO_AT = V(TX + 0.7, TY + 0.62, 0)           # achter de tafel rechts: zijn verveelde gezicht naar ons
PAPA_AT = V(TX - 1.72, TY, 0)                 # kopse kant links
BRO_AT = V(TX + 1.72, TY, 0)                  # kopse kant rechts
MAMA_AT = V(TX + 0.7, TY - 0.62, 0)           # vooraan rechts, rug naar ons

# de stoelen vooraan links en midden weg (open voor de camera), de kopse stoelen naar de tafel
for k in (1, 2):
    S.obj(f"Stoel_{k}").hide_render = True
    for o in bpy.data.objects:
        if o.name.startswith(f"Bord_{k}_"):
            o.hide_render = True
S.obj("Stoel_kop_1").rotation_euler.z = math.radians(90)
S.obj("Stoel_kop_2").rotation_euler.z = math.radians(-90)

# ---------------------------------------------------------------- figuren
opa = S.actor("opa", OPA_AT, 0)
oma = S.actor("oma", OMA_AT, 0)
mama = S.actor("mama", MAMA_AT, 180)
papa = S.actor("papa", PAPA_AT, 90)
bro = S.actor("broertje", BRO_AT, -90)
held = S.actor("hoofdpersonage", HERO_AT, 0)
SEAT = {}
for ch, at, r in ((opa, OPA_AT, 0), (oma, OMA_AT, 0), (mama, MAMA_AT, 180), (papa, PAPA_AT, 90), (bro, BRO_AT, -90), (held, HERO_AT, 0)):
    spec, z = sit(ch)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0, z), r)

# ---------------------------------------------------------------- tijdlijn: de klok vliegt, het verhaal niet
S.hud2(1, "1x", clock=clock(18 * 3600 + 32 * 60, 420.0, hhmm=True, day="MON"), t0=0.3)
S.ambience("sfx_diner_sfeer", 0.0, 12, vol=0.14)
l1 = S.say("F03-14", gap=0.6)
END = l1[1] + 1.3
S.music("piano_warm", 0.0, END + 1, vol=0.16, fade_in=0.6, fade_out=0.8, start=40.0)
S.gauge2("STORY: 40 MIN", l1[0] + 3.4, END)

# ---------------------------------------------------------------- opa vertelt (met handen: 'zó groot!')
BIG = arms(arm("L", (0.75, 0.55, -0.2), (0.85, 0.45, 0.25)), arm("R", (0.75, 0.55, -0.2), (0.85, 0.45, 0.25)))
SMALL = arms(arm("L", (0.3, 0.8, -0.4), (0.25, 0.9, 0.3)), arm("R", (0.3, 0.8, -0.4), (0.25, 0.9, 0.3)))
TABLE_MID = V(TX, TY - 0.2, 1.0)
seq = [("wijzen", None, "lach"), ("staan", BIG, "verbaasd"), ("schouders_op", None, "grijns"), ("staan", SMALL, "zelfverzekerd"),
       ("staan", BIG, "lach"), ("wijzen", None, "verbaasd"), ("staan", BIG, "grijns")]
t = 0.0
k = 0
while t < END:
    pose, arm_fn, face = seq[k % len(seq)]
    kw = dict(arms=arm_fn) if arm_fn else {}
    S.beat(opa, t, **SEAT[opa], pose=pose, amount=0.7, face=face, face_amt=0.8, at=TABLE_MID + V(-0.6 + 0.4 * (k % 3), 0, 0), **kw)
    t += 1.15
    k += 1
S.hold(opa, END)
t = 0.15
while t < END:                                   # opa praat aan één stuk door
    A.key_prop(opa.rig, "mond_open", 0.45, F(t))
    A.key_prop(opa.rig, "mond_open", 0.1, F(t + 0.12))
    t += 0.26 + 0.06 * math.sin(t * 3)
# oma knikt, de rest staart naar zijn bord
S.beat(oma, 0.0, **SEAT[oma], pose="ontspannen", face="blij", face_amt=0.5, at=S.head(opa))
for k, t in enumerate(frange(0.6, END, 1.4)):
    S.beat(oma, t, **SEAT[oma], pose="ontspannen", face="blij", face_amt=0.5, at=S.head(opa), body={"head": (10 if k % 2 else -2, 0, 0)})
S.hold(oma, END)
PLATE = {mama: V(MAMA_AT.x, TY - 0.28, TZ), papa: V(TX - 1.5, TY, TZ), bro: V(TX + 1.5, TY, TZ), held: V(HERO_AT.x, TY + 0.28, TZ)}
for ch in (mama, papa, bro, held):
    S.beat(ch, 0.0, **SEAT[ch], pose="ontspannen", face="neutraal", face_amt=0.6, at=PLATE[ch], body={"head": (16, 0, 0)})
    S.beat(ch, END * 0.5, **SEAT[ch], pose="ontspannen", face="twijfel", face_amt=0.5, at=PLATE[ch] + V(0.05, 0, 0), body={"head": (20, 0, 0)})
    S.hold(ch, END)
S.beat(held, l1[0] + 2.6, **SEAT[held], pose="ontspannen", face="twijfel", face_amt=0.7, at=S.head(opa), body={"head": (-4, 0, 0)})
S.beat(held, l1[0] + 4.4, **SEAT[held], pose="ontspannen", face="verdrietig", face_amt=0.5, look=(0.3, -0.4), body={"head": (6, 0, 0)})
S.beat(held, l1[1] - 0.6, **SEAT[held], pose="ontspannen", face="verdrietig", face_amt=0.4, at=PLATE[held], body={"head": (12, 0, 0)})
S.hold(held, END)
S.beat(bro, l1[0] + 4.0, **SEAT[bro], pose="ontspannen", face="neutraal", face_amt=0.5, at=PLATE[bro], body={"head": (24, 0, 10)})

# ---------------------------------------------------------------- camera
HO = S.head(opa)
S.cam(0.0, ((-0.6, -3.3, 2.25), (0.3, -0.3, 0.85), 24), ((-0.55, -3.0, 2.2), (0.25, -0.3, 0.85), 26))
S.cam(l1[0] + 1.6, (HO + V(-0.2, -1.9, -0.1), HO + V(0.15, 0, -0.25), 30), (HO + V(-0.18, -1.75, -0.1), HO + V(0.15, 0, -0.25), 33), dof=2.0)
HH = V(HERO_AT.x, HERO_AT.y - 0.2, 1.12)         # zijn hoofd (zittend, iets voorover); camera tussen hem en het broertje
S.cam(l1[0] + 3.8, (HH + V(0.7, -0.7, 0.2), HH + V(-0.12, 0, 0.1), 26), (HH + V(0.64, -0.64, 0.18), HH + V(-0.12, 0, 0.1), 28), dof=1.5)
S.cam(l1[1] - 0.5, ((-1.9, -2.6, 1.5), (0.4, -0.4, 0.9), 24), ((-1.8, -2.45, 1.48), (0.4, -0.4, 0.9), 25))

S.finish(length=END)
