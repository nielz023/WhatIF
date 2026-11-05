"""N18a · Jaar 1: het park vol moestuinen (script scène 18a-18c).
18a  WIDE trage crane: tijdsprongkaart 1 YEAR LATER, dan het park vol moestuinen. Mensen wieden en gieten, kinderen
     klimmen weer op het klimrek uit scène 3.
18b  MEDIUM: het hondje uit scène 3 wordt weer uitgelaten, nu door het broertje. Het hondje trekt, hij loopt erachteraan.
18c  DETAIL push-in: het broertje zet het oude bordje KEEP OFF THE GRASS weer rechtop (krijt eronder: ...EXCEPT TO GROW
     FOOD), duwt het paaltje met twee handen de grond in en klopt het aan.

    blender -b -P anim/v3/scenes/n18a_park.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n18a", "park", "jaar1", exposure=0.3)
CARD = 1.3
sh = S.cuts([CARD, 4.0, 3.6, 3.6])
END = sh[-1][1]
t_a, t_b, t_c = [s[0] for s in sh[1:]]
rnd = random.Random(18)
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- tuinders bij de moestuinbakken
GREEN = S.mat("gieter_groen", (0.2, 0.55, 0.3))


def gieter(name):
    g = T.cyl(name, (0, 0, 0), 0.09, 0.2, GREEN, seg=16, ol=0.003)
    T.to_mesh(T.tube(name + "_tuit", [(0, -0.06, 0.06), (0, -0.26, 0.2)], 0.015, GREEN)).parent = g
    T.to_mesh(T.tube(name + "_hengsel", [(0, 0.07, 0.18), (0, 0.0, 0.3), (0, -0.07, 0.18)], 0.012, GREEN)).parent = g
    return g


GARDENERS = [("figurant_a", V(-14.0, -10.95, 0), 0, "wied"), ("figurant_e", V(-10.0, -11.25, 0), 180, "giet"),
             ("opa", V(-6.0, -13.85, 0), 180, "wied"), ("figurant_f", V(-18.0, -11.25, 0), 180, "giet"),
             ("mama", V(-10.0, -13.85, 0), 0, "wied"), ("figurant_b", V(-14.0, -16.15, 0), 0, "giet")]
for k, (n, p, rot, act) in enumerate(GARDENERS):
    ch = S.actor(n, p, rot, label=f"tuinder_{k}")
    M = S._root_matrix(ch, 0.0)
    fwd = (M.to_3x3() @ V(0, -1, 0)).normalized()
    if act == "wied":
        # gebukt met gebogen knieën, handen in de aarde, plukt om de beurt
        for j, t in enumerate(frange(0.0, END, 0.55)):
            S.beat(ch, t, "staan", face="blij", face_amt=0.5, look=(0.0, -0.7), crouch=(0.22, 30),
                   body={"spine": (24, 0, 0), "head": (14, 0, 0)})
            side = "L" if j % 2 else "R"
            other = "R" if side == "L" else "L"
            lat = (M.to_3x3() @ V(0.14 if side == "L" else -0.14, 0, 0))
            S.reach(ch, t, side, p + fwd * 0.62 + lat + V(0, 0, 0.32))
            S.reach(ch, t, other, p + fwd * 0.55 - lat + V(0, 0, 0.45))
    else:
        g = gieter(f"Gieter_{k}")
        S.beat(ch, 0.0, "staan", face="blij", face_amt=0.5, look=(0.0, -0.5), body={"spine": (10, 0, 0), "head": (10, 0, 0)})
        S.hold(ch, END)
        grab(S, g, ch, 0.0, "hand.R", loc=(0.0, 0.0, -0.06), rot=(0, 0, 0))
        tilt = 0
        for j, t in enumerate(frange(0.0, END, 0.6)):
            hp = p + fwd * 0.38 + (M.to_3x3() @ V(-0.22, 0, 0)) + V(0, 0, 0.8 if j % 2 else 0.86)
            S.reach(ch, t, "R", hp, rot=(0, 0, 0))
        S.reach(ch, 0.0, "L", inf=0.0)

# ---------------------------------------------------------------- kinderen weer op het klimrek
KC = V(-7.0, 7.0, 0)
u = V(0.81, 0.58, 0)
kidA = S.actor("kind_a", KC + u * 1.68 + V(0, 0, 0.67), -54)
S.beat(kidA, 0.0, "armen_omhoog", amount=0.8, face="lach", face_amt=0.7, crouch=(0.05, 10))
ring = lambda ang, z, r: KC + V(math.cos(ang) * r, math.sin(ang) * r, z)     # noqa: E731
a0 = math.atan2(u.y, u.x)
for k, t in enumerate(frange(0.0, END, 0.7)):
    hi = k % 2
    # buizen vlak bij de schouders (korte kinderarmen): om de beurt een hand hoger
    S.reach(kidA, t, "L", ring(a0 - 0.12, 1.45 if hi else 1.1, 1.4 if hi else 1.5))
    S.reach(kidA, t, "R", ring(a0 + 0.12, 1.1 if hi else 1.45, 1.5 if hi else 1.4))
    A.crouch(kidA, F(t), 0.05 - 0.04 * hi, 10)
S.hold(kidA, END)
kidB = S.actor("kind_b", KC + V(-0.75, -2.35, 0), 20)
for k, t in enumerate(frange(0.0, END, 0.8)):
    S.beat(kidB, t, "juichen" if k % 2 else "staan", amount=0.8, face="lach", face_amt=0.8, at=S.head(kidA),
           crouch=(0.06 if k % 2 else 0.0, 4))
S.hold(kidB, END)

# ---------------------------------------------------------------- 18b: het broertje laat het hondje uit
bro = S.actor("broertje", V(8.2, -1.2, 0), 125)
hond = animal(S, "hondje", V(7.2, -1.9, 0), 125)
B_PATH = [V(8.2, -1.2, 0), V(6.2, -2.4, 0), V(4.6, -3.2, 0)]
H_PATH = [V(7.0, -2.0, 0), V(5.4, -3.4, 0), V(4.3, -4.7, 0)]
animal_path(hond, t_a - 0.6, t_b + 2.6, H_PATH, action="hond_loop", speed=1.3)
S.walk(bro, t_a - 0.6, t_b + 2.8, B_PATH, stride=0.42)
S.beat(bro, t_a, "staan", face="lach", face_amt=0.6, at=V(4.0, -3.6, 0.3), feet="keep", body={"spine": (-8, 0, 0)})
S.beat(bro, t_b + 0.6, "staan", face="inspanning", face_amt=0.5, at=V(4.0, -3.6, 0.3), feet="keep", body={"spine": (-10, 0, 0)})
S.beat(bro, t_b + 2.8, "staan", face="blij", face_amt=0.6, at=V(2.8, -4.2, 0.6))
animal_place(hond, t_b + 2.65, H_PATH[-1], 140)
animal_act(hond, t_b + 2.65, END, "hond_snuffel")
leash(S, bro, hond, 0.0, END)

# ---------------------------------------------------------------- 18c: het bordje weer rechtop
bord = S.obj("Bord_KEEP_OFF_THE_GRASS")
ROOT = bord.location.copy()
bord.rotation_mode = "XYZ"
T_PUSH0, T_PUSH1 = t_c + 0.5, t_c + 1.3
for t, a in ((0.0, -24), (T_PUSH0, -24), (T_PUSH1, 0)):
    bord.rotation_euler.x = math.radians(a)
    bord.keyframe_insert("rotation_euler", index=0, frame=F(t))
for k, t in enumerate((t_c + 1.8, t_c + 2.25, t_c + 2.7)):        # aankloppen: telkens een paar mm de grond in
    bord.location.z = -0.012 * k
    bord.keyframe_insert("location", index=2, frame=F(t - 0.05))
    bord.location.z = -0.012 * (k + 1)
    bord.keyframe_insert("location", index=2, frame=F(t + 0.03))
bord.location.z = 0.0
bord.keyframe_insert("location", index=2, frame=F(0.0))
bpy.context.view_layer.update()
B_C = ROOT + V(0.68, 0.41, 0)       # naast het scheve plankje; schuifelt mee als het rechtop komt
B_C2 = ROOT + V(0.68, 0.10, 0)
S.teleport(bro, t_c, B_C, face_dir := math.degrees(math.atan2(ROOT.x - B_C.x, -(ROOT.y - B_C.y))))
bro.rig.location = tuple(B_C)
bro.rig.keyframe_insert("location", frame=F(t_c))
S.turn(bro, T_PUSH0, T_PUSH1, math.degrees(math.atan2(ROOT.x - B_C2.x, -(ROOT.y - B_C2.y))), loc=B_C2)
S.beat(bro, t_c, "staan", face="vastberaden", face_amt=0.6, at=ROOT + V(0, 0, 0.6), crouch=(0.08, 12))
S.beat(bro, T_PUSH0 + 0.2, "staan", face="inspanning", face_amt=0.8, at=ROOT + V(0, 0, 0.6), crouch=(0.1, 14),
       body={"spine": (5, 0, 0)})
S.beat(bro, T_PUSH1 + 0.2, "staan", face="vastberaden", face_amt=0.7, at=ROOT + V(0, 0, 0.7), crouch=(0.06, 8))
S.beat(bro, t_c + 2.9, "staan", face="blij", face_amt=0.8, at=ROOT + V(0, 0, 0.75))
for t in frange(t_c, T_PUSH1 + 0.3, 0.1):
    S.sc.frame_set(F(t))
    Mb = bord.matrix_world
    # korte armen: hij duwt aan het uiteinde van het krijtplankje (de paal is buiten bereik)
    # (onderkant, onder zijn grote hoofd door)
    S.reach(bro, t, "L", Mb @ V(0.42, -0.04, 0.70))
    S.reach(bro, t, "R", Mb @ V(0.42, 0.04, 0.68))
# aankloppen met de linkerhand (camerakant) tegen het uiteinde van het krijtplankje
for t in (t_c + 1.8, t_c + 2.25, t_c + 2.7):
    S.reach(bro, t - 0.15, "L", ROOT + V(0.48, -0.08, 0.70))
    S.reach(bro, t, "L", ROOT + V(0.43, -0.05, 0.72))
S.reach(bro, t_c + 2.9, "L", inf=0.0)
S.reach(bro, T_PUSH1 + 0.34, "R", inf=0.0)
S.reach(bro, 0.0, "L", inf=0.0)
S.reach(bro, 0.0, "R", inf=0.0)
S.reach(bro, t_c - 0.05, "L", inf=0.0)
S.reach(bro, t_c - 0.05, "R", inf=0.0)
S.hold(bro, END)

# ---------------------------------------------------------------- camera's
S.black(0.0, CARD, "1 YEAR LATER")
# 18a WIDE trage crane omlaag over de moestuinen, het klimrek achterin
S.cam(0.0, ((2.0, -24.0, 7.5), (-9.0, -10.0, 0.5), 26))
S.cam(t_a, ((2.0, -24.0, 7.5), (-9.0, -10.0, 0.5), 26), ((0.5, -21.5, 3.6), (-9.0, -9.5, 0.9), 26))
# 18b MEDIUM het broertje met het hondje, schuin van voren meelopend
S.cam(t_b, None, fn=S.follow(bro, (-2.2, -2.6, 0.9), lens=30, look_offset=(0.3, 0.2, -0.25)), shake=S.shake(0.2))
# 18c DETAIL push-in op het bordje
S.cam(t_c, ((3.9, -6.5, 1.0), ROOT + V(0.35, 0, 0.72), 32), ((3.8, -6.2, 0.98), ROOT + V(0.35, 0, 0.72), 35))

# ---------------------------------------------------------------- HUD, geluid
S.counter("YEAR 1", 212, t0=t_a)
S.ambience("sfx_park_ochtend", t_a, END, vol=0.22)
S.ambience("sfx_kinderen_spelen", t_a, END, vol=0.06)
S.sfx("sfx_whoosh", 0.0, 0.3)
S.sfx("sfx_hond_blaf", t_b + 1.0, 0.2)
S.sfx("sfx_hout_klop", t_c + 1.8, 0.35)
S.sfx("sfx_hout_klop", t_c + 2.25, 0.35)
S.sfx("sfx_hout_klop", t_c + 2.7, 0.35)
S.music("strijkers_warm", t_a, END, vol=0.18, fade_in=0.6, fade_out=0.6)
S.finish(length=END, tail=0.0)
