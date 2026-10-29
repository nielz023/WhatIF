"""F01 · Cold open · dag 4 · 1.000x · straat in de grijze ochtend.
Het broertje (dinopyjama) staat bevroren midden in een sprint, drie meter voor de vuilniswagen.
Alles staat stil, behalve hij. Smash cut naar zwart, '3 DAYS EARLIER'.

    blender -b -P anim/v2/scenes/f01_cold_open.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f01", "straat", "grijs")

# ---------------------------------------------------------------- set
BRO_AT = V(-1.4, 1.2, 0)                     # midden op de rijbaan, op weg naar de overkant (-y)
HERO_AT = V(-1.15, 2.05, 0)                  # vlak achter hem
TRUCK_X = -8.75                               # neus van de wagen op ~3 m van het broertje
truck = S.obj("Vuilniswagen")
truck.location.x = TRUCK_X
S.obj("Auto_geparkeerd_2").location.x = -21.0     # stond naast de wagen
for o in bpy.data.objects:
    if o.name.startswith("Raamtekst"):         # mama schrijft pas na de redding op het raam
        o.hide_render = True
S.obj("Kraai").hide_render = True              # vervangen door de glans-kraai
crow = G.crow("kraai", (-3.6, 2.6, 3.4), rot_z=-70, wing=38)
bag = S.obj("Plastic_zak")
bag.location = (-2.35, 0.55, 1.55)

# 1.000x: in 25 s van hem schuift de wagen ~0,2 m op en zakt de zak een paar millimeter
key(truck, 0.0, loc=(TRUCK_X, 1.5, 0))
key(truck, 26.0, loc=(TRUCK_X + 0.2, 1.5, 0))
key(bag, 0.0, loc=bag.location.copy())
key(bag, 26.0, loc=bag.location + V(0.004, 0, -0.006))
for o in (truck, bag):
    for fc in A._fcurves(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

# ---------------------------------------------------------------- figuren
bro = S.actor("broertje_dino", BRO_AT, 0, frozen=True)
START = V(0.55, 2.7, 0)                       # eerst staat hij een paar meter verderop
held = S.actor("hoofdpersonage", START, heading(START, BRO_AT))

# ---------------------------------------------------------------- tijdlijn
CLK = clock(8 * 3600 + 58 * 60 + 40, 1 / 1000, dec=2)
S.hud2(4, "1,000x", clock=CLK, t0=0.25)
l1 = S.say("F01-01", gap=0.5)
l2 = S.say("F01-02", gap=0.35)
l3 = S.say("F01-03", gap=0.3)
l4 = S.say("F01-04", gap=0.3)
l5 = S.say("F01-05", gap=0.35)
CUT = l5[1] + 0.5                              # smash cut naar zwart
l6 = S.say("F01-06", at=CUT + 0.45)
CARD = l6[1] + 0.35
END = CARD + 1.1

S.music("drone", 0.0, CUT, vol=0.30, fade_in=0.3, fade_out=0.02)
S.music("strijkers_emo", l2[0], CUT, vol=0.20, fade_in=2.5, fade_out=0.02)
S.ambience("sfx_vuilniswagen", 0.0, CUT, vol=0.16)
for k in range(int(CUT / 2.6)):                # de klok tikt veel te langzaam
    S.sfx("sfx_klok_tik", 0.9 + k * 2.6, 0.22, cut=(0, 0.35))
S.sfx("sfx_hartslag", l4[0], 0.25, cut=(0, l5[1] - l4[0]))
S.sfx("sfx_whoosh", CUT - 0.25, 0.35)
S.card("", CUT, CARD, dim=1.0, fin=1, fout=1)
S.card("3 DAYS EARLIER", CARD, END, size=96, dim=1.0, fin=1, fout=4)
S.sfx("sfx_hud_tik", CARD, 0.5)

# ---------------------------------------------------------------- het broertje: bevroren sprint
run_pose(S, bro, 0.0, front="R", amount=0.85, lift=0.14, reach=0.12, back=0.16, face="blij", look=(0.15, 0.1))
A.key_prop(bro.rig, "mond_open", 0.35, F(0.0))
S.hold(bro, END)

# ---------------------------------------------------------------- hij
SH_L = S.bone_world(bro, "upper_arm.L", 0.0, tail=False) + V(0, 0.04, 0.06)
SH_R = S.bone_world(bro, "upper_arm.R", 0.0, tail=False) + V(0, 0.04, 0.06)
GAP = V(0, 0.07, 0.03)                         # handen blijven een paar centimeter van zijn schouders
S.beat(held, 0.0, "staan", face="bang", at=S.head(bro, 0) + V(-1.0, 0, 0))
S.beat(held, l1[1] - 0.6, "staan", face="nerveus", at=S.head(bro, 0))
S.beat(held, l2[0] + 1.2, "staan", face="bang", at=truck.location + V(4.3, 0, 1.2))
S.walk(held, l2[1] - 1.3, l3[0] + 0.35, [START, HERO_AT], end_rot=8, stride=0.5)
S.beat(held, l3[0] + 0.4, "staan", face="vastberaden", face_amt=0.7, at=S.head(bro, 0), crouch=(0.03, 12))
S.reach(held, l3[0] + 0.4, "L", None, 0.0)
S.reach(held, l3[0] + 0.4, "R", None, 0.0)
S.reach(held, l3[0] + 0.8, "L", SH_L + GAP * 3)
S.reach(held, l3[0] + 0.8, "R", SH_R + GAP * 3)
S.reach(held, l3[1] + 0.2, "L", SH_L + GAP)
S.reach(held, l3[1] + 0.2, "R", SH_R + GAP)
t = l4[0]
k = 0
while t < l5[1]:                               # zijn handen trillen
    j = V(0.006 * (1 if k % 2 else -1), 0.004 * (1 if k % 3 else -1), 0.005 * (1 if k % 2 else -1))
    S.reach(held, t, "L", SH_L + GAP + j)
    S.reach(held, t + 0.06, "R", SH_R + GAP - j)
    t += 0.13
    k += 1
LOOK = S.head(bro, 0) + V(0.1, -1.2, 0.3)        # over zijn hoofd heen, de straat in: kin omhoog, gezicht zichtbaar
S.beat(held, l4[0] + 0.3, "staan", face="bang", face_amt=0.9, at=LOOK, crouch=(0.04, 8))
S.beat(held, l5[0], "staan", face="vastberaden", face_amt=0.8, at=LOOK + V(-0.3, 0, 0), crouch=(0.04, 8), pupil_klein=0.3)
S.hold(held, CUT)

# ---------------------------------------------------------------- camera
HB = S.head(bro, 0)
# 1. zijn gezicht, koplampen op zijn wang
S.cam(0.0, S.shot(bro, 0.0, "cu", az=40, lens=40, h=-0.1), S.shot(bro, 0.0, "cu", az=36, lens=44, h=-0.1), dof=2.0)
# 2. breed: drie meter tot de wagen
S.cam(l1[0] + 2.4, ((2.6, -3.4, 1.15), (-4.2, 1.6, 1.25), 26), ((2.3, -3.1, 1.15), (-4.2, 1.6, 1.25), 27))
# 3. koplampen laag, de kraai en de zak hangen stil
S.cam(l2[0] - 0.1, ((-1.0, -0.9, 0.55), (-8.0, 1.8, 1.7), 24), ((-1.2, -0.8, 0.6), (-8.0, 1.8, 1.8), 25))
S.cam(l2[0] + 2.6, ((-1.9, -0.6, 2.4), (-3.4, 2.4, 3.2), 30), ((-2.0, -0.5, 2.35), (-3.0, 2.0, 2.4), 32), dof=4.0)
# 4. hij stapt erbij: 'just grab him and run'
S.cam(l3[0] - 0.1, S.shot(held, l3[0], "full", az=-60, lens=30), S.shot(held, l3[1], "med", az=-55, lens=32))
# 5. de handen, een paar centimeter van zijn schouders
MID = (SH_L + SH_R) / 2 + GAP
S.cam(l4[0] - 0.05, (MID + V(1.35, -0.55, 0.2), MID + V(0, 0, 0.05), 40), (MID + V(1.15, -0.5, 0.16), MID + V(0, 0, 0.05), 44), dof=1.8)
# 6. zijn gezicht: 'the only way to save him... is slowly'
HH = S.headpos(held, l4[1])                      # hij staat achter het broertje: van voren, schuin over hem heen
S.cam(l4[0] + 3.0, (HH + V(0.75, -1.5, -0.08), HH + V(0, 0, -0.04), 44), (HH + V(0.65, -1.35, -0.08), HH + V(0, 0, -0.04), 48), dof=2.2)
S.cam(l5[0] + 2.6, ((3.4, -4.6, 1.5), (-3.0, 1.6, 1.2), 28), ((2.6, -3.6, 1.4), (-2.6, 1.6, 1.2), 30))

S.finish(length=END, picture_end=CUT)
