"""N08g · Dag 2: het park (script scène 8g-8h).
8g WIDE push-in: KEEP OFF THE GRASS ligt plat in het gras, ernaast een kampvuur met mensen op het gras. Een man stapt
   over het bordje heen. Het hondje uit scène 3 snuffelt eraan, zonder baasje, de lijn sleept achter hem aan.
8h DETAIL: het broertje bukt (knieën buigen), pakt het bordje met beide handen en klemt het onder zijn arm
   (plant: het bordje komt terug in scène 19).

    blender -b -P anim/v3/scenes/n08g_park_bordje.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n08g", "park", "dag2", exposure=0.0)
sh = S.cuts([3.5, 3.4])
END = sh[-1][1]
t_h = sh[1][0]

bord = S.obj("Bord_KEEP_OFF_THE_GRASS")
ROOT = bord.location.copy()
YAW0 = math.radians(15)
DIR = V(-math.sin(YAW0), math.cos(YAW0), 0)            # het bord ligt vanaf de paalvoet in deze richting
PERP = V(DIR.y, -DIR.x, 0)
MIDP = ROOT + DIR * 0.75 + V(0, 0, 0.05)               # waar je het vastpakt (bovenste deel van de paal)
PLATE = ROOT + DIR * 1.12

# ---------------------------------------------------------------- mensen op het gras rond het kampvuur
FIRE = V(5.5, -9.5, 0)
for k, (nm, p) in enumerate((("figurant_a", V(3.6, -10.9, 0)), ("figurant_e", V(7.7, -11.2, 0)), ("figurant_f", V(8.0, -8.2, 0)))):
    d = FIRE - p
    rot = math.degrees(math.atan2(d.x, -d.y))
    e = S.actor(nm, p, rot, label=f"kampvuur_{k}")
    spec, rz = sit(e, seat_top=0.02, lean=-8)
    e.rig.location.z = rz
    e.rig.keyframe_insert("location", frame=F(0.0))
    for j, t in enumerate(frange(0.0, END, 1.1 + 0.2 * k)):
        S.beat(e, t, "staan", face="blij" if (j + k) % 2 else "neutraal", face_amt=0.6, at=FIRE + V(0, 0, 0.5) if j % 2 else None,
               look=(0.3 if j % 2 else -0.3, 0.0), **spec)
    S.hold(e, END)

# ---------------------------------------------------------------- de man stapt over het bordje
man = S.actor("figurant_b", (1.2, -6.4, 0), 0)
S.walk(man, 0.2, 3.4, [V(1.2, -6.4, 0), V(2.45, -3.7, 0), V(3.0, -1.4, 0)], stride=0.7)
S.beat(man, 1.4, "staan", face="neutraal", face_amt=0.5, at=PLATE, feet="keep")
S.beat(man, 2.4, "staan", face="neutraal", face_amt=0.4, look=(0.0, 0.0), feet="keep")
S.hold(man, END)
visible(man.body, 0.0, True)
visible(man.body, t_h, False)

# ---------------------------------------------------------------- het hondje zonder baasje, lijn sleept mee
hond = animal(S, "hondje", (6.0, -4.5, 0), 120)
animal_path(hond, 0.0, 1.8, [V(6.0, -4.5, 0), V(4.4, -3.6, 0), PLATE + V(0.55, 0.15, -PLATE.z)], action="hond_loop")
animal_place(hond, 1.85, PLATE + V(0.55, 0.15, -PLATE.z), 105)
animal_act(hond, 1.85, END, "hond_snuffel")
lijn = T.box("Hondenlijn_sleept", (0, 0, 0), (0.014, 1.3, 0.014), S.mat("lijn_rood", (0.75, 0.12, 0.1)), base=False, bevel=0, ol=0.003)
lijn.parent = hond.rig
lijn.location = (0.0, 0.7, 0.14)                            # achter de halsband langs de grond (lokaal +y = achter)
lijn.rotation_euler = (math.radians(-11), 0, 0)

# ---------------------------------------------------------------- 8h: het broertje raapt het bordje op
FACE = -PERP                                                # hij staat naast het bord en kijkt ernaar
BRO_AT = MIDP + PERP * 0.3                                 # dicht bij de paal: korte kinderarmen
BRO_AT.z = 0.0
rot_bro = math.degrees(math.atan2(FACE.x, -FACE.y))
bro = S.actor("broertje", BRO_AT, rot_bro)
visible(bro.body, 0.0, False)
visible(bro.body, t_h - 0.05, True)
S.beat(bro, t_h, "staan", face="neutraal", face_amt=0.6, at=MIDP)
S.reach(bro, 0.0, "L", inf=0.0)
S.reach(bro, 0.0, "R", inf=0.0)
S.reach(bro, t_h + 0.2, "L", inf=0.0)
S.reach(bro, t_h + 0.2, "R", inf=0.0)
S.beat(bro, t_h + 0.85, "staan", face="vastberaden", face_amt=0.7, at=MIDP, crouch=(0.32, 22))
S.reach(bro, t_h + 0.85, "L", MIDP - DIR * 0.15 + V(0, 0, 0.04))       # rechterhand aan de +DIR-kant (= zijn rechts)
S.reach(bro, t_h + 0.85, "R", MIDP + DIR * 0.15 + V(0, 0, 0.04))
T_GRAB = t_h + 0.95
S.reach(bro, t_h + 1.5, "L", inf=0.0)
# hij komt overeind en houdt het bordje rechtop naast zich, als een vlag: rechterhand om de paal, tekst naar de camera
from mathutils import Matrix  # noqa: E402
RIGHT = V(FACE.y, -FACE.x, 0)
T_UP = t_h + 1.7
GRIP = BRO_AT + RIGHT * 0.42 + FACE * 0.10 + V(0, 0, 0.62)
S.reach(bro, T_UP, "R", GRIP)
S.reach(bro, END, "R", GRIP + V(0, 0, 0.03))
S.beat(bro, T_UP, "staan", face="vastberaden", face_amt=0.8, look=(0.0, 0.1))
S.beat(bro, END, "staan", face="blij", face_amt=0.5, look=(0.3, 0.0))
S.hold(bro, END)
CAMDIR = FACE * 1.7 - DIR * 1.6
CAMDIR.z = 0
CAMDIR.normalize()
YAW_UP = math.atan2(CAMDIR.x, -CAMDIR.y)
TILT = math.radians(-24)                                   # bovenkant iets van hem af
HOLD = 0.62
UP_AT = GRIP - (Matrix.Rotation(YAW_UP, 3, 'Z') @ Matrix.Rotation(TILT, 3, 'Y') @ V(0, 0, HOLD))
ROT_UP = (Matrix.Rotation(YAW_UP, 3, 'Z') @ Matrix.Rotation(TILT, 3, 'Y')).to_euler()
LIFT_MID = (MIDP + UP_AT) / 2 + V(0, 0, 0.35)
for t, loc, rot in ((0.0, ROOT, (math.radians(-88), 0, YAW0)), (T_GRAB, ROOT, (math.radians(-88), 0, YAW0)),
                    (T_GRAB + 0.4, LIFT_MID, (math.radians(-45), 0, (YAW0 + YAW_UP) / 2)),
                    (T_UP, UP_AT, tuple(ROT_UP)), (END, UP_AT, tuple(ROT_UP))):
    bord.location = loc
    bord.rotation_euler = rot
    bord.keyframe_insert("location", frame=F(t))
    bord.keyframe_insert("rotation_euler", frame=F(t))
grab(S, bord, bro, T_UP, "hand.R", loc=(0, 0.05, 0.0), mode="loc", offset=tuple(UP_AT - GRIP))
# het hondje loopt in 8h naar de andere kant van het bord
animal_place(hond, t_h, PLATE - PERP * 0.9 + V(0, 0, -PLATE.z), math.degrees(math.atan2(PERP.x, -PERP.y)))

# ---------------------------------------------------------------- camera's
S.cam(0.0, ((-1.2, -0.6, 1.5), (4.0, -6.8, 0.35), 24), ((-0.6, -1.3, 1.35), (4.0, -7.0, 0.3), 25))
HB = S.headpos(bro, t_h + 1.9)
S.cam(t_h, (HB + FACE * 1.7 + DIR * -1.6 + V(0, 0, -0.3), HB + V(0, 0, -0.32), 27),
      (HB + FACE * 1.55 + DIR * -1.45 + V(0, 0, -0.3), HB + V(0, 0, -0.3), 28))

# ---------------------------------------------------------------- HUD en geluid
S.counter("DAY 2", 0, t0=0.0)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.08)
S.sfx("sfx_vuur", 0.0, 0.18, loop_to=END)
S.sfx("sfx_hond_blaf", 2.6, 0.12)
S.finish(length=END, tail=0.0)
