"""N16f · Dag 30, later: op het dak onder de Melkweg (script scène 16f-16h). Dak van het huis aan de tuinkant, nacht.
16f  WIDE trage crane omhoog: de jongen en opa liggen op het dak en kijken omhoog. Opa wijst, zijn arm zakt langzaam.
16g  CLOSE opa: "Haven't seen that since I was a kid."
16g2 de Melkweg, scherp en helder. VO: "This part is real. In 1994, an earthquake knocked out the power in Los Angeles..."
16g3 WIDE vanaf de nok: de twee op het dak, de donkere tuinen.
16h  CLOSE: de jongen kijkt opzij naar opa en glimlacht.
16h2 WIDE pull-back hoog boven het dak: de donkere stad. VO: "But winter was coming..." Het rustige motief breekt af.

    blender -b -P anim/v3/scenes/n16f_melkweg.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n16f", "tuin", "nacht", exposure=0.35, night=True)
sh = S.cuts([5.0, 4.2, 5.0, 4.6, 4.0, 4.4])
END = sh[-1][1]
t_g, t_g2, t_g3, t_h, t_h2 = [s[0] for s in sh[1:]]

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True
night_sky(stars=1.0, milky=1.2)

# ---------------------------------------------------------------- het dakvlak aan de tuinkant opmeten
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()


def roof_z(x, y):
    hit, loc, nrm, *_ = S.sc.ray_cast(dg, V(x, y, 30.0), V(0, 0, -1))
    return (loc, nrm) if hit else (None, None)


pa, na = roof_z(0.0, -2.6)
pb, nb = roof_z(0.0, -0.6)
UP = (pa - pb).normalized()                       # langs het dak omhoog (naar de nok, -y)
NRM = na.normalized() if na.z > 0 else -na.normalized()
print("DAK", pa, pb, "helling", round(math.degrees(math.asin(max(-1, min(1, UP.z)))), 1))


def lie(ch, x, feet_y, back=0.16):
    """Leg een figuur op zijn rug op het dak, voeten naar de goot, hoofd naar de nok."""
    p, n = roof_z(x, feet_y)
    n = n if n.z > 0 else -n
    Z = UP
    Y = -n                                          # zijn voorkant (-y lokaal) wijst naar de lucht
    X = Y.cross(Z).normalized()
    Y = Z.cross(X).normalized()
    M = Matrix((X, Y, Z)).transposed()
    ch.rig.rotation_mode = "XYZ"
    ch.rig.location = p + n * back
    ch.rig.rotation_euler = M.to_euler()
    for f in (1, F(END) + 1):
        ch.rig.keyframe_insert("location", frame=f)
        ch.rig.keyframe_insert("rotation_euler", frame=f)
    return p


held = S.actor("hoofdpersonage_kind", (0.55, -0.8, 7.0), 0)
opa = S.actor("opa", (-0.55, -0.8, 7.0), 0, drop=("wandelstok",))
lie(held, 0.55, -0.55)
lie(opa, -0.55, -0.15)
bpy.context.view_layer.update()
SKY = lambda ch: S.headpos(ch, 0.0) + NRM * 6.0 + UP * 2.5        # noqa: E731
S.face(held, 0.0, "verbaasd", 0.5, look=(0.0, 0.3))
S.face(opa, 0.0, "blij", 0.4, look=(0.0, 0.3))
# opa wijst naar de sterren, zijn arm zakt langzaam
SP = S.bone_world(opa, "upper_arm.R", 0.5, tail=False)
S.reach(opa, 0.0, "R", inf=0.0)
S.reach(opa, 0.6, "R", SP + (NRM * 0.9 + UP * 0.35).normalized() * 0.44)     # gestrekte arm (armlengte)
S.reach(opa, 2.4, "R", SP + (NRM * 0.85 + UP * 0.45 + V(0.2, 0, 0)).normalized() * 0.44)
S.reach(opa, 4.3, "R", SP + (NRM * 0.45 + UP * 0.1).normalized() * 0.42)
S.reach(opa, 4.6, "R", SP + (NRM * 0.45 + UP * 0.1).normalized() * 0.42)
S.reach(opa, 4.85, "R", inf=0.0)
# 16g: opa praat zacht, verwonderd
S.face(opa, t_g, "blij", 0.6, look=(0.1, 0.35))
S.say("N16-03", who=opa, at=t_g + 0.3)
A.blink_at(opa, F(t_g + 2.9))
# 16h: de jongen kijkt opzij naar opa en glimlacht
S.face(held, t_h, "verbaasd", 0.3, look=(0.0, 0.3))
S.face(held, t_h + 1.0, "blij", 0.7, look=(0.8, 0.0))
A.bone_rot(held, F(t_h + 0.6), "head", (0, 0, 0))
A.bone_rot(held, F(t_h + 1.2), "head", (0, -35, 0))
A.bone_rot(held, F(t_h2 + 0.5), "head", (0, -35, 0))
A.bone_rot(held, F(t_h2 + 1.2), "head", (0, 0, 0))
S.face(opa, t_h + 1.4, "blij", 0.7, look=(-0.8, 0.0))
A.bone_rot(opa, F(t_h + 1.0), "head", (0, 0, 0))
A.bone_rot(opa, F(t_h + 1.6), "head", (0, 30, 0))
A.blink_at(held, F(t_h + 2.6))
S.face(held, t_h2 + 1.2, "blij", 0.5, look=(0.0, 0.3))

# zacht maanlicht op de gezichten
T.point_light("Maan_vul_gezichten", tuple((S.headpos(held, 0.0) + S.headpos(opa, 0.0)) / 2 + NRM * 2.5 + V(0, 2.0, 0)),
              color=(0.6, 0.7, 1.0), energy=60, radius=1.0)

# ---------------------------------------------------------------- camera's
HO, HH = S.headpos(opa, 0.0), S.headpos(held, 0.0)
MID = (HO + HH) / 2
# 16f WIDE trage crane omhoog vanuit de tuin
S.cam(0.0, ((3.8, 7.0, 1.5), MID + V(0, 0.4, 0.4), 26), ((2.0, 3.2, 8.7), MID + V(0, 0.1, 0.1), 28))
# 16g CLOSE opa, van boven
S.cam(t_g, (HO + NRM * 1.15 + UP * 0.25 + V(-0.15, 0, 0), HO + V(0, 0, 0.02), 32), (HO + NRM * 1.05 + UP * 0.22 + V(-0.14, 0, 0), HO + V(0, 0, 0.02), 34))
# 16g2 de Melkweg: vanaf hun hoofden omhoog
S.cam(t_g2, (MID + NRM * 0.6 + UP * 0.6, MID + NRM * 6.0 + UP * 9.0 + V(1.0, 0, 0), 18), (MID + NRM * 0.6 + UP * 0.6, MID + NRM * 6.0 + UP * 9.0 + V(2.6, 0, 0), 18))
# 16g3 WIDE vanaf de nok, over hun hoofden de tuin in
S.cam(t_g3, (MID + UP * 3.0 + NRM * 2.6, MID - UP * 1.6, 24), (MID + UP * 2.8 + NRM * 2.5, MID - UP * 1.6, 25))
# 16h CLOSE de jongen
S.cam(t_h, (HH + NRM * 1.1 + UP * 0.25 + V(0.2, 0, 0), HH + V(0, 0, 0.02), 32), (HH + NRM * 1.0 + UP * 0.22 + V(0.18, 0, 0), HH + V(0, 0, 0.02), 34))
# 16h2 WIDE pull-back omhoog: het dak, de donkere stad
S.cam(t_h2, (MID + NRM * 3.0 + V(0, 3.0, 2.0), MID, 26), (MID + V(4.0, 22.0, 26.0), MID + V(0, -6.0, 0), 26))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 30", 14, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.03)
S.music("piano_zacht", 0.0, t_h + 2.5, vol=0.18, fade_in=0.6, fade_out=0.25)
S.music("m_winter", t_h + 2.5, END, vol=0.14, fade_in=0.3, fade_out=0.5)
S.say("N16-04", at=t_g + 3.2)
S.say("N16-05", at=t_h + 2.6)
S.finish(length=END, tail=0.0)
