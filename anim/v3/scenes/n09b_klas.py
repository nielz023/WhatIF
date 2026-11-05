"""N09b · Dag 3: het lege klaslokaal (script scène 9b-9c).
9b WIDE trage dolly vanaf het bord: het broertje rent op ons af met zijn armen in de lucht het lege lokaal in, springt op een stoel
   (stoel wiebelt) en springt er weer af.
9c MEDIUM push-in: hij schrijft met een stift NO SCHOOL FOREVER!! op het bord, grote armbewegingen,
   draait zich om en lacht: "Best. Day. Ever!"

    blender -b -P anim/v3/scenes/n09b_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n09b", "school", "nr_no_school", exposure=0.0)
sh = S.cuts([4.2, 6.0])
END = sh[-1][1]
t_c = sh[1][0]

UP = arms(arm("L", (0.35, 0.15, 0.92), (0.15, 0.1, 1.0)), arm("R", (0.35, 0.15, 0.92), (0.15, 0.1, 1.0)))
WIDE = arms(arm("L", (0.9, 0.2, 0.3), (0.8, 0.3, 0.5)), arm("R", (0.9, 0.2, 0.3), (0.8, 0.3, 0.5)))

# ---------------------------------------------------------------- 9b: binnenrennen, op de stoel, eraf
CHAIR = S.obj("Schoolstoel_0_1_-0.38")
SEAT = V(-1.12, -0.58, 0.46)
bro = S.actor("broertje", (3.6, -1.3, 0), 90 + 180)
AISLE = [V(3.6, -1.3, 0), V(1.5, -1.3, 0), V(-0.6, -1.3, 0), V(-1.05, -1.25, 0)]
S.run(bro, 0.0, 1.5, AISLE, stride=0.5, lift=0.22, lean=10, arms=0.0, ease_in=0.1, ease_out=0.25)
S.beat(bro, 0.15, "staan", arms=UP, face="blij", face_amt=1.0, feet="keep")
S.beat(bro, 1.3, "staan", arms=UP, face="blij", face_amt=1.0, feet="keep")
# afzet, sprong op de zitting (blijft naar de camera kijken, -x)
S.beat(bro, 1.55, "staan", arms=WIDE, face="grijns", face_amt=0.9, crouch=(0.12, 12), feet="keep")
S.place(bro, 1.55, V(-1.05, -1.25, 0), -90)
S.place(bro, 1.75, V(-1.09, -0.9, 0.62), -80)
S.place(bro, 1.9, SEAT, -90)
S.beat(bro, 1.9, "staan", arms=WIDE, face="grijns", face_amt=1.0, crouch=(0.08, 6), feet="keep")
S.beat(bro, 2.15, "staan", arms=UP, face="blij", face_amt=1.0, feet="keep")
S.beat(bro, 2.55, "staan", arms=WIDE, face="geschrokken", face_amt=0.6, body={"spine": (0, 0, 10)}, feet="keep")   # stoel wiebelt
S.beat(bro, 2.8, "staan", arms=WIDE, face="blij", face_amt=0.9, body={"spine": (0, 0, -8)}, feet="keep")
S.beat(bro, 3.05, "staan", arms=UP, face="blij", face_amt=1.0, crouch=(0.1, 10), feet="keep")
# sprong eraf, terug het gangpad in, landt door de knieën
S.place(bro, 3.1, SEAT, -90)
S.place(bro, 3.3, V(-1.08, -1.05, 0.55), -90)
S.place(bro, 3.45, V(-1.05, -1.45, 0.0), -90)
S.beat(bro, 3.45, "staan", arms=WIDE, face="grijns", face_amt=1.0, crouch=(0.22, 18), feet="keep")
S.beat(bro, 3.85, "staan", arms=UP, face="blij", face_amt=1.0, feet="keep")
for fc in A._fcurves(bro.rig):
    if fc.data_path == "location" and fc.array_index == 2:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
# de stoel wiebelt als hij erop landt en eraf springt
CHAIR.rotation_mode = "XYZ"
r0 = CHAIR.rotation_euler.copy()
for t, a in ((0.0, 0), (1.9, 0), (2.05, 6), (2.25, -5), (2.45, 4), (2.65, -3), (2.85, 2), (3.1, 0), (3.25, -7), (3.45, 4), (3.65, -2), (3.85, 0)):
    CHAIR.rotation_euler = (r0.x + math.radians(a), r0.y, r0.z)
    CHAIR.keyframe_insert("rotation_euler", frame=F(t))

# ---------------------------------------------------------------- 9c: NO SCHOOL FOREVER!! op het bord schrijven
BX = -4.45
from lib import huis as HU  # noqa: E402
for nm in ("Bord_NO_SCHOOL", "Bord_FOREVER"):
    S.obj(nm).hide_render = S.obj(nm).hide_viewport = True
TX = 0.13                                                   # kleiner handschrift: binnen bereik van zijn korte arm
T_W = [(t_c + 0.35, t_c + 1.55), (t_c + 1.75, t_c + 2.95)]
masks = []                                                  # (y0, y1, z, ta, tb) per regel, voor de hand
for k, (txt, z) in enumerate((("NO SCHOOL", 1.26), ("FOREVER!!", 1.07))):
    full = HU.marker_text(f"Bord_regel{k}_vol", txt, (BX + 0.026, 0, z), TX, "rood", rot=(90, 0, 90), align="LEFT")
    bpy.context.view_layer.update()
    ys = [(full.matrix_world @ V(c)).y for c in full.bound_box]
    w = max(ys) - min(ys)
    y0 = -w / 2
    full.location.y = y0
    full.hide_render = full.hide_viewport = True
    ta, tb = T_W[k]
    steps = [i for i in range(1, len(txt) + 1) if txt[i - 1] != " "]
    for j, i in enumerate(steps):
        o = HU.marker_text(f"Bord_regel{k}_{i:02d}", txt[:i], (BX + 0.026, y0, z), TX, "rood", rot=(90, 0, 90), align="LEFT")
        t_on = ta + (tb - ta) * (j + 1) / len(steps)
        t_off = ta + (tb - ta) * (j + 2) / len(steps) if j + 1 < len(steps) else None
        for t, vis in ((0.0, False), (t_on, True)) + (((t_off, False),) if t_off else ()):
            o.hide_render = not vis
            o.hide_viewport = not vis
            o.keyframe_insert("hide_render", frame=F(t))
            o.keyframe_insert("hide_viewport", frame=F(t))
        for fc in A._fcurves(o):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    masks.append((y0, y0 + w, z + TX * 0.35, ta, tb))

# hij staat op een opstapje voor het bord (anders komt hij niet bij het bord)
STEP_H = 0.55
T.box("Opstapje", (-4.06, -0.17, 0), (0.42, 0.4, STEP_H), S.mat("opstapje_hout", (0.55, 0.38, 0.22)), bevel=0.02, ol=0.004)
ST = V(-4.06, -0.17, STEP_H)                                # rechterschouder voor het midden van de tekst
S.teleport(bro, t_c, ST, -90)
S.beat(bro, t_c, "staan", face="grijns", face_amt=0.8, at=V(BX, 0, 1.5), feet="keep")
stift = T.cyl("Stift", (0, 0, 0), 0.012, 0.13, S.mat("stift_rood", (0.85, 0.1, 0.1)), seg=10, ol=0.003)
stift.hide_render = True
stift.keyframe_insert("hide_render", frame=F(0.0))
stift.hide_render = False
stift.keyframe_insert("hide_render", frame=F(t_c))
for fc in A._fcurves(stift):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
grab(S, stift, bro, 0.0, "hand.R", loc=(0, 0.06, 0.02), rot=(90, 0, 0))
S.reach(bro, 0.0, "R", inf=0.0)
S.reach(bro, t_c + 0.15, "R", inf=0.0)
for (y0, y1, zc, ta, tb) in masks:
    n = 6
    for j in range(n + 1):
        u = j / n
        y = y0 + (y1 - y0) * u
        z = zc + (0.07 if j % 2 else -0.06)
        S.reach(bro, ta + (tb - ta) * u, "R", V(BX + 0.18, y, min(z, 1.5)))
S.beat(bro, t_c + 1.6, "staan", face="grijns", face_amt=1.0, at=V(BX, 0.3, 1.25), body={"spine": (4, 0, 0)}, feet="keep")
S.reach(bro, t_c + 3.2, "R", V(BX + 0.3, 0.3, 1.2))
S.reach(bro, t_c + 3.5, "R", inf=0.0)
# draait zich om naar de camera en roept het uit, armen in de lucht
S.turn(bro, t_c + 3.05, t_c + 3.45, 138)
S.beat(bro, t_c + 3.5, "staan", arms=UP, face="blij", face_amt=1.0, look=(0.0, 0.2))
S.beat(bro, END, "staan", arms=UP, face="blij", face_amt=1.0, look=(0.0, 0.1))
S.hold(bro, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, ((-3.95, -1.0, 2.35), (1.0, -1.15, 0.4), 22), ((-3.85, -1.15, 2.3), (0.0, -1.0, 0.45), 23))
S.cam(t_c, ((-2.95, 1.95, 1.3), (-4.25, -0.15, 1.2), 26), ((-3.05, 1.7, 1.3), (-4.25, -0.15, 1.2), 28))

S.counter("DAY 3", 0, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.02)
S.sfx("sfx_tuinhek_rammel", 1.9, 0.15)
S.sfx("sfx_stift", t_c + 0.35, 0.25, loop_to=t_c + 2.95)
S.say("N09-02", who=bro, at=t_c + 3.4)
S.finish(length=END, tail=0.0)
