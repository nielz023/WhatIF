"""S22 · Dag 22 · alleen in de bunker. Muren van twee meter beton, hij slaapt op de vloer. De vriend belt elke
avond ('You still there?'), het T-shirt van de Anchor. De telefoon ligt op de grond, omdat hij hem niet durft vast te houden.

    blender -b -P anim/scenes/s22_bunker.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s22", "woestijn", "bunker")

LIE = V(-1.4, -1.12, 0.24)                     # op zijn rug op de matras, voeten bij -y, hoofd op het kussen
PH = V(-0.72, 0.18, 0.012)                     # telefoon op de vloer, naast zijn hoofd

for n in ("Telefoon_vloer", "Telefoon_scherm"):
    if S.obj(n):
        S.obj(n).hide_render = True
phone = prop_phone(S, "Telefoon_bunker", PH, screen=(0.3, 0.85, 0.45))
phone.rotation_euler = (math.radians(-90), 0, math.radians(-20))
phone.scale = (1.7, 1.7, 1.7)
wit = S.mat("scherm_wit", (1, 1, 1), 3.0)
T.text("Telefoon_naam", "BEST FRIEND", (0, -0.0075, 0.045), 0.011, wit, extrude=0.0).parent = phone
T.text("Telefoon_tijd", "2:14:08", (0, -0.0075, 0.025), 0.013, wit, extrude=0.0).parent = phone
T.text("Telefoon_speaker", "SPEAKER ON", (0, -0.0075, -0.04), 0.008, wit, extrude=0.0).parent = phone
T.point_light("Telefoon_gloed", tuple(PH + V(0, 0, 0.12)), color=(0.4, 1.0, 0.55), energy=2.5, radius=0.05)

held = S.actor("hoofdpersonage", LIE, 0)
key(held.rig, 0.0, loc=LIE, rot=(-90, 0, 0), interp="CONSTANT")

# ---------------------------------------------------------------- tijdlijn
S.hud(22, "4,194,304x STRONGER", t0=0.5)
S.ambience("sfx_bunker", 0.0, 60, vol=0.12)
S.music("gitaar", 0.6, 60, vol=0.2, fade_in=1.6, fade_out=1.6)
l1 = S.say("S22-01", gap=0.8)
THICK = l1[0] + 3.62                           # 'Your new home is a concrete bunker...'
FLOOR = l1[0] + 7.31                           # 'You still sleep on the floor.'
l2 = S.say("S22-02", who=None, gap=0.6, gain=1.0)
l3 = S.say("S22-03", gap=0.5)
ALONE = l3[0] + 2.09
l4 = S.say("S22-04", gap=0.5, gain=1.0)
SOLD = l4[0] + 2.75                            # 'Sold forty.'
KEEP = l4[0] + 6.38                            # 'I'm keeping the money, obviously.'
l5 = S.say("S22-05", gap=0.4)
l6 = S.say("S22-06", gap=0.9)
SCARED = l6[0] + 2.94                          # 'Because you're scared to hold it.'
S.wait(1.8)
END = S.t
S.real(THICK + 0.1, FLOOR - 0.1)
S.text("WALLS: 2 M CONCRETE", THICK + 1.4, FLOOR - 0.1, loc=(0.965, 0.22), size=52, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("\"THE ANCHOR\" T-SHIRTS SOLD: 40", SOLD + 0.2, KEEP + 1.5, loc=(0.965, 0.22), size=50, color=GOLD, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- hij: op zijn rug, hoofd naar de telefoon
TO_PHONE = {"head": (0, 48, 0), "neck": (0, 18, 0)}      # + = gezicht naar +x, naar de telefoon
HOVER = arm("L", (0.85, 0.35, 0.25), (0.8, 0.45, 0.4))
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.6, look=(0, 0), body={"head": (0, 10, 0)})
S.beat(held, FLOOR - 0.2, "staan", face="verdrietig", face_amt=0.5, look=(0, 0))
S.beat(held, l2[0] + 0.4, "staan", face="neutraal", face_amt=0.6, look=(0.6, -0.2), body=TO_PHONE)
S.beat(held, l3[0] + 0.5, "staan", face="blij", face_amt=0.3, look=(0.6, -0.2), body=TO_PHONE, mond_verdrietig=0.3)
S.beat(held, ALONE + 1.0, "staan", face="verdrietig", face_amt=0.5, look=(0.6, -0.2), body=TO_PHONE)
S.beat(held, l4[0] + 0.4, "staan", face="blij", face_amt=0.4, look=(0.6, -0.2), body=TO_PHONE)
S.beat(held, KEEP + 0.4, "staan", face="lach", face_amt=0.5, look=(0.6, -0.2), body=TO_PHONE)
S.beat(held, l5[0] + 0.1, "staan", face="lach", face_amt=0.7, look=(0.5, 0.0), body={"head": (0, 30, 0)}, ogen_knijp=0.4)
S.beat(held, l5[1] + 0.3, "staan", face="blij", face_amt=0.5, look=(0.2, 0.0), body={"head": (0, 15, 0)})
S.beat(held, l6[0] + 0.3, "staan", face="verdrietig", face_amt=0.5, look=(0.6, -0.2), body=TO_PHONE)
S.beat(held, SCARED - 0.6, "staan", face="verdrietig", face_amt=0.6, look=(0.6, -0.3), body=TO_PHONE, arms=HOVER)
S.beat(held, SCARED + 0.6, "staan", face="nerveus", face_amt=0.7, look=(0.6, -0.3), body=TO_PHONE,
       arms=arm("L", (0.85, 0.3, 0.2), (0.85, 0.35, 0.35)))
S.beat(held, END - 0.6, "staan", face="verdrietig", face_amt=0.8, look=(0.6, -0.3), body=TO_PHONE, arms=HOVER, mond_verdrietig=0.6)
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.8, -2.9, 1.7), (-0.9, 0.4, 0.5), 20), ((1.5, -2.6, 1.6), (-0.9, 0.4, 0.5), 22))
S.cam(FLOOR - 0.15, ((-1.25, -0.6, 2.55), (-1.3, -0.4, 0.2), 22), ((-1.25, -0.55, 2.45), (-1.3, -0.35, 0.2), 24))
S.cam(l2[0] - 0.2, (PH + V(0.38, -0.3, 0.22), PH + V(0, 0, 0.0), 38), (PH + V(0.33, -0.26, 0.2), PH + V(0, 0, 0.0), 42))
HH = S.headpos(held, l3[0] + 0.5)
S.cam(l3[0] - 0.1, (HH + V(1.0, 0.35, 0.3), HH + V(0, 0, 0.0), 34), (HH + V(0.9, 0.3, 0.27), HH + V(0, 0, 0.0), 38))
S.cam(l4[0] - 0.1, (PH + V(0.65, 0.05, 0.14), HH + V(0, 0, -0.05), 30), (PH + V(0.58, 0.05, 0.13), HH + V(0, 0, -0.05), 33))
S.cam(l5[0] - 0.2, (HH + V(0.15, -0.35, 1.0), HH + V(0, 0, 0), 34), (HH + V(0.13, -0.3, 0.9), HH + V(0, 0, 0), 38))
S.cam(l6[0] - 0.1, ((0.9, 1.6, 2.4), (-1.1, -0.4, 0.15), 24), ((0.8, 1.5, 2.3), (-1.1, -0.4, 0.15), 26))
S.cam(SCARED - 0.4, (PH + V(0.55, -0.5, 0.35), PH + V(-0.25, 0.0, 0.2), 32), (PH + V(0.5, -0.45, 0.32), PH + V(-0.25, 0.0, 0.2), 36))

S.finish(length=END)
