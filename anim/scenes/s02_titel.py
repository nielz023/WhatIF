"""S02 · Titel en spelregels (dag 1, 2x) · slaapkamer, ochtend.

Hij zit op de rand van zijn bed en staart naar zijn tintelende handen. Titelkaart,
de spelregels, en 'you still weigh seventy-five kilos'.

    blender -b -P anim/scenes/s02_titel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s02", "slaapkamer", "ochtend")

BED_EDGE = V(-0.93, 0.55, 0)          # rand van het bed (matras tot x = -1.02)
SIT = dict(pose="ontspannen", crouch=(0.13, -4.0), feet=((0.02, 0.30, 0.17), (-0.02, 0.30, 0.17)))
STAND = V(0.15, 0.25, 0)

held = S.actor("hoofdpersonage", BED_EDGE, 90)
hands = lambda t: S.head(held) + V(0.42, 0, -0.62)

# ---------------------------------------------------------------- tijdlijn
S.hud(1, "2x STRONGER", t0=0.6)
S.music("ochtend", 0.0, 13.6, vol=0.32)
S.ambience("sfx_straat_sfeer", 0.0, 13.6, vol=0.10)

l1 = S.say("S02-01", gap=1.0)
l2 = S.say("S02-02", gap=0.4)
l3 = S.say("S02-03", gap=0.5)
S.wait(0.3)
CARD = S.t + 0.1
S.sfx("sfx_whoosh_titel", CARD - 0.25, 0.9)
S.card("WHAT IF YOU GOT\n2x STRONGER\nEVERY DAY?", CARD, CARD + 3.4, size=120)
l4 = S.say("S02-04", gap=1.2)
S.music("speels", CARD + 1.0, l4[1] + 30, vol=0.30, fade_in=1.5)
l5 = S.say("S02-05", gap=0.4)
S.gauge("WEIGHT: 75 KG", l5[0] + 1.6, None, color=WHITE, size=56)
l6 = S.say("S02-06", gap=0.5)

# ---------------------------------------------------------------- acteren
# wakker, suf op de bedrand; dan de handen
S.beat(held, 0.0, **SIT, face="neutraal", look=(0, -0.5), body={"head": (18, 0, 0), "chest": (6, 0, 0)})
S.beat(held, 1.4, **SIT, face="twijfel", face_amt=0.5, look=(0.2, -0.3), body={"head": (12, -8, 0), "chest": (6, 0, 0)})
S.beat(held, l1[1] - 0.2, **{**SIT, "pose": "staan"}, face="verbaasd", face_amt=0.4, at=hands(0), arms=LOOK_HANDS)
S.beat(held, l2[0] + 1.0, **{**SIT, "pose": "staan"}, face="verbaasd", face_amt=0.9, at=hands(0), arms=LOOK_HANDS)
for k, t in enumerate((l2[0] + 2.6, l2[0] + 3.4, l2[0] + 4.2)):     # handen draaien en schudden
    tw = 18 if k % 2 == 0 else -14
    S.beat(held, t, **{**SIT, "pose": "staan"}, face="verbaasd", face_amt=0.8, at=hands(0),
           arms=arms(arm("L", (0.25, 0.55, -0.75), (-0.25 + tw / 200, 0.75, 0.55)), arm("R", (0.25, 0.55, -0.75), (-0.25 - tw / 200, 0.75, 0.55))))
S.beat(held, l2[1] - 0.6, **{**SIT, "pose": "vuisten"}, face="grijns", face_amt=0.6, at=hands(0) + V(0, 0, 0.1))
# 'what if...' hij kijkt op, naar de camera
S.beat(held, l3[0] + 0.5, **{**SIT, "pose": "vuisten"}, face="verbaasd", face_amt=0.7, look=(0.0, 0.1), body={"head": (-4, -10, 0)})
S.beat(held, l3[1], **{**SIT, "pose": "vuisten"}, face="zelfverzekerd", face_amt=0.5, look=(0.0, 0.1), body={"head": (-6, -10, 0)})
# staat op (titelkaart), rekt zich uit
S.hold(held, CARD + 0.5)
S.beat(held, CARD + 1.4, "staan", crouch=(0.2, 20), feet=((0.02, 0.18, 0), (-0.02, 0.18, 0)), face="neutraal", body={"chest": (12, 0, 0)})
S.place(held, CARD + 0.5, BED_EDGE, 90)
S.place(held, CARD + 2.0, BED_EDGE + V(0.35, 0, 0), 90)
S.beat(held, CARD + 2.2, "staan", face="blij", face_amt=0.4)
S.walk(held, CARD + 2.6, CARD + 4.6, [BED_EDGE + V(0.35, 0, 0), STAND], end_rot=heading(STAND, (0.9, -1.9, 0)))
S.beat(held, CARD + 5.3, "armen_omhoog", face="lach", face_amt=0.6, body={"chest": (-10, 0, 0), "head": (-14, 0, 0)})
S.beat(held, CARD + 6.6, "juichen", amount=0.6, face="blij", body={"chest": (-6, 0, 0)})
S.beat(held, l4[0] + 7.5, "vuisten", face="zelfverzekerd", look=(0, 0))
S.beat(held, l4[1] - 0.6, "vuisten", face="zelfverzekerd", face_amt=0.8, look=(0.2, 0), body={"head": (-4, 10, 0)})
# 75 kilo: kijkt naar zichzelf omlaag
S.beat(held, l5[0] + 1.5, "handen_zij", face="twijfel", body={"head": (24, 0, 0), "neck": (8, 0, 0)}, look=(0, -0.7))
S.beat(held, l5[1] - 0.8, "handen_zij", face="nerveus", face_amt=0.6, body={"head": (4, 0, 0)}, look=(0, 0))
# 'you barely notice': schouders op, loopt naar de deur
S.beat(held, l6[0] + 2.4, "schouders_op", face="twijfel", face_amt=0.8, look=(0, 0))
S.beat(held, l6[1] - 0.3, "ontspannen", face="blij", face_amt=0.5)
S.walk(held, l6[1] + 0.1, l6[1] + 2.4, [STAND, V(1.1, -0.35, 0), V(1.9, 0.6, 0)])

# zoemende handen: kleine lichtvonkjes rond de handen tijdens regel 2
glim = S.mat("tintel", (0.6, 0.95, 1.0), 6)
for k in range(10):
    side = "hand.L" if k % 2 else "hand.R"
    o = T.sphere(f"Tinteling_{k}", (0, 0, 0), 0.006, glim, seg=6, ol=0)
    attach(o, held, side, ((k % 3 - 1) * 0.035, -0.02 * (k % 2), 0.03 * (k % 4 - 1.5)))
    for j in range(16):
        tt = l2[0] + 0.3 + j * 0.28 + k * 0.03
        key(o, tt, scale=1.0 if j % 2 == 0 else 0.15)
    key(o, l2[0] + 0.2, scale=0.0)
    key(o, l2[1] + 0.4, scale=0.0)

# ---------------------------------------------------------------- camera
HEAD = S.head(held)
HANDS = (S.bone_world(held, "hand.L", l2[0] + 1.5) + S.bone_world(held, "hand.R", l2[0] + 1.5)) / 2
FWD = V(1, 0, 0)                      # hij kijkt naar +x
S.cam(0.0, ((0.9, -3.3, 1.55), (-0.8, 0.6, 0.85), 20), ((0.6, -2.6, 1.45), (-0.8, 0.6, 0.9), 24))
S.cam(l1[1] - 0.4, (HANDS + V(0.75, -0.35, -0.12), HANDS + V(0, 0, 0.05), 34), (HANDS + V(0.6, -0.28, -0.1), HANDS + V(0, 0, 0.05), 38), dof=2.4)
S.cam(l3[0] - 0.1, (HEAD + V(1.6, -0.2, -0.05), HEAD + V(0, 0, -0.1), 38), (HEAD + V(1.3, -0.15, -0.05), HEAD + V(0, 0, -0.1), 42))
S.cam(CARD, ((1.6, -2.2, 0.6), (-0.3, 0.6, 1.0), 22), ((1.4, -2.0, 0.9), (0.1, 0.3, 1.2), 24))
S.cam(l4[0] + 7.0, ((0.9, -1.9, 1.25), STAND + V(0, 0, 1.25), 32), ((0.7, -1.6, 1.3), STAND + V(0, 0, 1.3), 36))
TOCAM = (V(0.9, -1.9, 0) - STAND).normalized()
S.cam(l5[0], (STAND + TOCAM * 1.3 + V(0, 0, 2.1), STAND + V(0, 0, 0.7), 24), (STAND + TOCAM * 1.5 + V(0, 0, 2.2), STAND + V(0, 0, 0.75), 22))
S.cam(l6[0], ((0.15, -2.2, 1.35), STAND + V(0, 0, 1.3), 30), ((0.4, -2.6, 1.4), STAND + V(0.5, 0, 1.2), 26))

S.finish(tail=2.0)
