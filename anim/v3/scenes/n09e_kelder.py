"""N09e · Dag 3: mama verstopt het eten (script scène 9e), keuken met planken voor het raam.
Mama zet het laatste blik in een doos, tilt hem met gebogen knieën op (zwaar, ze leunt achterover) en loopt
er voorzichtig mee richting de kelderdeur.

    blender -b -P anim/v3/scenes/n09e_kelder.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n09e", "keuken", "nr_kaarsen", exposure=0.6)
sh = S.cuts([3.6])
END = sh[-1][1]

for o in list(bpy.data.objects):
    if o.name.startswith(("Kaars_tafel", "Lucifers", "Kaarsvlam", "Kaars_licht")):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# ---------------------------------------------------------------- de doos met blikken
BOX0 = V(-0.2, -0.6, 0.76)
BW, BD, BH = 0.46, 0.34, 0.28
CARD = S.mat("karton", (0.72, 0.55, 0.36))
doos = T.box("Doos_blikken", (0, 0, 0), (BW, BD, BH), CARD, bevel=0.01, ol=0.004)
CANS = [S.mat("blik_rood", (0.85, 0.12, 0.10)), S.mat("blik_geel", (0.9, 0.75, 0.15)), S.mat("blik_groen", (0.2, 0.55, 0.25))]
for k in range(6):
    c = T.cyl(f"Doos_blik_{k}", (-0.14 + (k % 3) * 0.14, -0.07 + (k // 3) * 0.14, BH - 0.09), 0.045, 0.12, CANS[k % 3], seg=14, ol=0.003)
    c.parent = doos
doos.location = BOX0

# het laatste blik in haar rechterhand gaat de doos in
blik = T.cyl("Blik_laatste", (0, 0, 0), 0.045, 0.12, CANS[0], seg=14, ol=0.003)

# ---------------------------------------------------------------- mama
M_AT = V(-0.95, -0.6, 0)
mama = S.actor("mama", M_AT, 90)
S.beat(mama, 0.0, "staan", face="vastberaden", face_amt=0.6, at=BOX0 + V(0, 0, 0.1))
T_DROP, T_GRIP, T_LIFT, T_TURN, T_WALK = 0.7, 1.05, 1.45, 1.6, 2.0
S.reach(mama, 0.0, "R", BOX0 + V(-0.05, 0.25, 0.42))
S.reach(mama, T_DROP, "R", BOX0 + V(0.0, 0.05, 0.36))
S.reach(mama, 0.0, "L", inf=0.0)
S.reach(mama, T_DROP, "L", inf=0.0)
grab(S, blik, mama, 0.0, "hand.R", loc=(0, 0.06, 0.0))
visible(blik, T_DROP, False)                               # zit nu tussen de andere blikken in de doos
# tillen: door de knieën, dan achterover leunen
S.beat(mama, T_GRIP, "staan", face="inspanning", face_amt=0.7, at=BOX0, crouch=(0.18, 16), feet="keep")
S.beat(mama, T_LIFT, "staan", face="inspanning", face_amt=0.9, at=BOX0 + V(0, 0, 0.6), body={"spine": (-9, 0, 0)}, feet="keep")
S.turn(mama, T_TURN, T_WALK, 221)
DOOR = V(-1.45, -0.1, 0)
S.walk(mama, T_WALK, END, [M_AT, DOOR], stride=0.36, turn=False)
for t in frange(T_WALK, END, 0.4):
    S.beat(mama, t, "staan", face="inspanning", face_amt=0.7, at=DOOR + V(-0.6, 0.6, 1.3), body={"spine": (-10, 0, 0)}, feet="keep")
S.hold(mama, END)

# de doos: ligt op tafel tot het optillen, daarna vast voor haar buik (per frame uit de stand van haar wortel)
CARRY = V(0.0, -0.38, 0.6)                                 # lokaal: voor haar (-y), op buikhoogte
doos.rotation_mode = "XYZ"
for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    M = S._root_matrix(mama, t)
    yaw = M.to_euler().z
    held = M @ CARRY
    if t <= T_GRIP:
        loc, rz = BOX0, 0.0
    elif t <= T_LIFT:
        u = (t - T_GRIP) / (T_LIFT - T_GRIP)
        loc, rz = BOX0.lerp(held, u * u * (3 - 2 * u)), yaw * u
    else:
        loc, rz = held, yaw
    doos.location = loc
    doos.rotation_euler = (0, 0, rz)
    doos.keyframe_insert("location", frame=f)
    doos.keyframe_insert("rotation_euler", frame=f)
# handen aan de zijkanten van de doos
for t in frange(T_GRIP, END + 0.01, 0.15):
    M = S._root_matrix(mama, t)
    S.sc.frame_set(F(t))
    c = doos.matrix_world.translation
    side = (M.to_3x3() @ V(1, 0, 0)).normalized()
    S.reach(mama, t, "L", c + side * (BW / 2 + 0.02) + V(0, 0, 0.02))
    S.reach(mama, t, "R", c - side * (BW / 2 + 0.02) + V(0, 0, 0.02))

# ---------------------------------------------------------------- camera: statisch vanuit de hoek bij de deur
S.wall(0.0, END + 1, "front")                            # tegenshot: de voormuur moet dicht zijn
S.cam(0.0, ((-2.1, 1.75, 1.4), (-0.8, -0.55, 0.9), 22), ((-2.1, 1.72, 1.38), (-0.95, -0.45, 0.9), 23))

S.counter("DAY 3", 0, t0=0.0)
S.sfx("sfx_blik_plop", T_DROP, 0.3)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.02)
S.finish(length=END, tail=0.0)
