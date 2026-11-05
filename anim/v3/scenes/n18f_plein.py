"""N18f · Jaar 1: het stadsplein met het grote regelbord (script scène 18f).
18f  WIDE trage pull-back: een enorm houten bord vol handgeschreven regels. Een man klimt op een ladder en schrijft er
     nog één bij (13. SWAP, DON'T STEAL.). Mensen lezen mee. VO N18-02. De teller tikt van 212 naar 213.

    blender -b -P anim/v3/scenes/n18f_plein.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402

S = Scene3("n18f", "stadsplein", "jaar1", exposure=0.3)
sh = S.cuts([6.8])
END = sh[-1][1]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de ladder: in de set prikt hij door het bord, dus iets naar voren
LAD = S.obj("Ladder_regelbord")
LEAN = math.radians(14)
LAD.location = (2.2, 11.1, 0.0)
LROOT = V(2.2, 11.1, 0.0)


def lad(zl, x=0.0):
    """Punt op de ladder: lokale hoogte zl langs de bomen."""
    return LROOT + V(x, zl * math.sin(LEAN), zl * math.cos(LEAN))


# ---------------------------------------------------------------- de man klimt naar boven
man = S.actor("figurant_c", V(2.2, 10.9, 0), 180)
S.beat(man, 0.0, "staan", face="vastberaden", face_amt=0.5, at=V(1.8, 12.0, 3.0))
RUNG = lambda k: 0.25 + 0.28 * k                                   # noqa: E731
T_CL = [0.5 + 0.34 * k for k in range(8)]                          # elke 0,34 s een sport hoger, tot vlak bij het bord
S.place(man, 0.4, V(2.2, 10.9, 0), 180)
for k, t in enumerate(T_CL):
    zl = RUNG(k)
    p = lad(zl) + V(0, -0.1, 0.0)                                  # voeten op de sporten, dicht bij het bord
    S.place(man, t, p, 180)
    side = "L" if k % 2 else "R"
    # zijn rechterhand aan de rechterboom (+x), anders kruisen de armen
    S.reach(man, t - 0.1, side, lad(zl + 1.05, 0.22 if side == "R" else -0.22) + V(0, -0.05, 0))
    S.reach(man, t + 0.15, side, lad(zl + 1.05, 0.22 if side == "R" else -0.22) + V(0, -0.05, 0))
    A.foot(man, F(t - 0.15), "L" if k % 2 else "R", (0, 0, 0.12))
    A.foot(man, F(t), "L" if k % 2 else "R", (0, 0, 0))
TOP = T_CL[-1]
S.reach(man, 0.0, "L", inf=0.0)
S.reach(man, 0.0, "R", inf=0.0)
S.reach(man, 0.35, "L", inf=0.0)
S.reach(man, 0.35, "R", inf=0.0)
# boven: linkerhand aan de ladder, rechterhand schrijft
S.reach(man, END, "L", lad(RUNG(7) + 1.05, -0.22) + V(0, -0.05, 0))
S.beat(man, TOP + 0.2, "staan", face="vastberaden", face_amt=0.7, at=V(2.3, 12.0, 3.2), body={"spine": (18, 0, 0)})
S.hold(man, END)

# ---------------------------------------------------------------- de nieuwe regel, woord voor woord
WORDS = ["13.", "SWAP,", "DON'T", "STEAL."]
# kleine letters recht voor zijn rechterschouder: verder reiken kan hij niet vanaf de ladder
X0, Z = 1.9, lad(RUNG(7)).z + 1.1
objs, x = [], X0
for i, w in enumerate(WORDS):
    o = HU.marker_text(f"Nieuwe_regel_{i}", w, (x, 11.965, Z), 0.1, "blauw", align="LEFT")
    bpy.context.view_layer.update()
    xs = [(o.matrix_world @ V(c)).x for c in o.bound_box]
    objs.append((o, x, max(xs)))
    x = max(xs) + 0.06
T_W0 = TOP + 0.5
T_W1 = END - 0.9
dt = (T_W1 - T_W0) / len(objs)
pen = T.cyl("Stift_man", (0, 0, 0), 0.012, 0.13, S.mat("stift_blauw_huls", (0.15, 0.3, 0.8)), seg=8, ol=0.002)
grab(S, pen, man, 0.0, "hand.R", loc=(0.0, 0.0, -0.05), rot=(90, 0, 0))
for i, (o, xa, xb) in enumerate(objs):
    ta = T_W0 + i * dt
    visible(o, 0.0, False)
    visible(o, ta + dt * 0.8, True)
    for k, u in enumerate((0.0, 0.33, 0.66, 0.95)):
        S.reach(man, ta + dt * u, "R", V(xa + (xb - xa) * u, 11.9, Z + (0.03 if k % 2 else -0.02)))
# rechterhand gaat in één beweging van de sport naar het bord (geen IK-overgang die halverwege blijft hangen)
S.reach(man, T_W1 + 0.4, "R", V(xb - 0.15, 11.75, Z - 0.15))

# ---------------------------------------------------------------- mensen lezen mee
for n, p, act in (("figurant_a", V(-1.6, 9.6, 0), "lees"), ("figurant_e", V(-0.4, 9.2, 0), "wijs"),
                  ("kind_b", V(0.7, 9.7, 0), "lees"), ("opa", V(-2.6, 8.7, 0), "lees")):
    ch = S.actor(n, p, 180 + (p.x - 0.5) * -4)
    if act == "wijs":
        S.beat(ch, 0.0, "wijzen", face="blij", face_amt=0.6, at=V(-1.5, 12.0, 3.3))
        S.beat(ch, 2.5, "staan", face="lach", face_amt=0.6, at=V(-1.5, 12.0, 3.0))
    else:
        S.beat(ch, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(p.x * 0.5, 12.0, 3.4))
        S.beat(ch, 3.2, "staan", face="blij", face_amt=0.5, at=V(2.3, 12.0, Z))
    S.hold(ch, END)

# ---------------------------------------------------------------- camera: trage pull-back
S.cam(0.0, ((2.6, 5.5, 2.2), (1.2, 12.0, 2.8), 28), ((4.4, -2.2, 2.6), (0.4, 12.0, 2.8), 26))

# ---------------------------------------------------------------- HUD, geluid, stem
S.counter("YEAR 1", [(0.0, 212), (T_W1 + 0.1, 213)], t0=0.0)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.08)
S.sfx("sfx_stift", T_W0, 0.3)
S.sfx("sfx_metaal_stap", 0.6, 0.15)
S.music("strijkers_warm", 0.0, END, vol=0.16, fade_in=0.3, fade_out=0.8)
S.say("N18-02", at=0.4)
S.finish(length=END, tail=0.0)
