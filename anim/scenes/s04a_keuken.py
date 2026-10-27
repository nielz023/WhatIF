"""S04a · Dag 2 · keuken: papa's augurkenpot. 'I loosened it for you.' 'Okay, Hercules.'

    blender -b -P anim/scenes/s04a_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s04a", "keuken", "ochtend")

TX, TY, TZ = 0.2, -0.6, 0.76
DAD_AT = V(-0.58, 0.55, 0)                       # achter de tafel, mama zit vooraan met haar rug naar ons
HERO_AT = V(0.22, 0.55, 0)
JAR_P = V(-0.18, 0.55, 0.9)

for n in ("Krant",):
    S.obj(n).hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Krant_kolom"):
        o.hide_render = True

# ---------------------------------------------------------------- figuren
papa = S.actor("papa", DAD_AT, 58, energy=1.1)      # schuin naar de camera gedraaid
held = S.actor("hoofdpersonage", HERO_AT, -58)
mama = S.actor("mama", (TX - 0.38, TY - 0.57, 0), 180, energy=0.8)
SIT_M, zm = sit(mama)
S.place(mama, 0, (TX - 0.38, TY - 0.57, zm), 180)
coffee = S.obj("Koffiemok")
coffee.location = (TX - 0.3, TY - 0.24, TZ)
for n in ("Stoel_3", "Stoel_4"):
    S.obj(n).hide_render = True
S.obj("Ontbijt_bord").location = (TX - 0.38, TY - 0.25, TZ)

jar, lid = prop_jar(S, "Augurkenpot", JAR_P + V(0, 0, -0.07))

# ---------------------------------------------------------------- tijdlijn
S.hud(2, "4x STRONGER", t0=0.35)
S.music("speels", 0.0, 30, vol=0.30, fade_in=0.4, start=4.0)
S.ambience("sfx_straat_sfeer", 0.0, 30, vol=0.05)
l1 = S.say("S04-01", gap=0.6)
l2 = S.say("S04-02", gap=0.5, who=papa)
HAND = l2[1] - 0.3
l3 = S.say("S04-03", gap=0.4)
OPEN = l3[0] + 2.35                           # 'It… comes off.'
S.sfx("sfx_pot_krak", OPEN - 0.1, 0.9)
l4 = S.say("S04-04", gap=0.6, who=mama, gain=1.2)
S.wait(0.8)
S.sfx("sfx_whoosh", S.t - 0.35, 0.6)
END = S.t + 0.1

# ---------------------------------------------------------------- papa worstelt, geeft de pot
DL, DR = JAR_P + V(-0.02, 0.07, 0.02), JAR_P + V(-0.02, -0.07, 0.02)   # papa's handen (zijn links = +y)
S.beat(papa, 0.0, "staan", face="inspanning", at=JAR_P, crouch=(0.03, 8))
S.reach(papa, 0.0, "L", DL)
S.reach(papa, 0.0, "R", DR)
grab(S, jar, papa, 0.0, "hand.L", mode="loc", offset=(0.02, -0.06, -0.08), release=HAND)
grab(S, lid, None, 0.0, target=jar, mode="loc", offset=(0, 0, 0.155), release=OPEN - 0.05)
t = 0.3
while t < l1[1] + 0.2:                        # draait en draait, met trillende armen
    S.reach(papa, t, "R", DR + V(0, 0.01, 0.06))
    S.reach(papa, t + 0.35, "R", DR + V(0.01, -0.02, 0.07))
    S.beat(papa, t + 0.2, "staan", face="inspanning", face_amt=1.0, at=JAR_P, crouch=(0.04, 10), body={"head": (6, 0, 6 if int(t * 3) % 2 else -6)})
    t += 0.7
S.beat(papa, l2[0] - 0.2, "staan", face="neutraal", at=S.head(held), crouch=(0.0, 0))
S.reach(papa, l2[0] + 0.3, "L", JAR_P + V(0.05, 0.06, 0.03))
S.reach(papa, l2[0] + 0.3, "R", JAR_P + V(0.05, -0.06, 0.03))
S.beat(papa, l2[0] + 1.6, "staan", face="zelfverzekerd", face_amt=0.9, at=S.head(held), body={"head": (0, 0, 8)})
A.blink_at(papa, F(l2[1] - 0.6), closed=5)       # knipoog
S.reach(papa, HAND + 0.4, "L", None, 0.0)
S.reach(papa, HAND + 0.4, "R", None, 0.0)
S.beat(papa, HAND + 0.6, "armen_over", face="zelfverzekerd", face_amt=0.7, at=JAR_P + V(0.2, 0, 0.1))
S.beat(papa, OPEN + 0.1, "schrik", face="geschrokken", at=JAR_P + V(0.3, 0, 0.2))
S.beat(papa, OPEN + 1.2, "schrik", amount=0.5, face="verbaasd", at=S.head(held) + V(0, 0, -0.3))
S.beat(papa, l4[0] + 0.5, "staan", face="twijfel", face_amt=0.8, at=S.head(mama, 0))
S.hold(papa, END)

# ---------------------------------------------------------------- hij pakt de pot en opent hem
HL, HR = JAR_P + V(0.03, -0.07, 0.0), JAR_P + V(0.03, 0.07, 0.07)     # zijn links = -y (hij kijkt naar -x)
S.beat(held, 0.0, "ontspannen", face="neutraal", face_amt=0.6, at=JAR_P)
S.beat(held, l1[1], "ontspannen", face="twijfel", face_amt=0.6, at=S.head(papa))
S.beat(held, l2[1] - 0.8, "staan", face="neutraal", at=JAR_P)
S.reach(held, HAND - 0.5, "L", None, 0.0)
S.reach(held, HAND, "L", HL)
grab(S, jar, held, HAND, "hand.L", mode="loc", offset=(-0.02, 0.06, -0.08))
S.reach(held, l3[0] + 0.5, "L", HL + V(0.02, 0, 0.0))
S.reach(held, l3[0] + 0.6, "R", None, 0.0)
S.reach(held, OPEN - 0.5, "R", HR)
S.beat(held, OPEN - 0.5, "staan", face="neutraal", at=JAR_P + V(0, 0, 0.08), crouch=(0.02, 6))
grab(S, lid, held, OPEN - 0.05, "hand.R", mode="loc", offset=(0, 0, -0.01))
# het draaien: één klein rukje, en de deksel met de rand komt omhoog
S.reach(held, OPEN, "R", HR + V(0, 0.0, 0.02))
S.reach(held, OPEN + 0.18, "R", HR + V(0.06, 0.04, 0.22))
S.beat(held, OPEN + 0.15, "schrik", amount=0.3, face="geschrokken", at=HR + V(0, 0, 0.2), crouch=(0.0, -4))
S.reach(held, OPEN + 1.6, "R", HR + V(0.1, 0.0, 0.28))
S.reach(held, OPEN + 1.6, "L", HL + V(0.05, 0.0, 0.0))
S.beat(held, OPEN + 1.0, "staan", face="verbaasd", face_amt=0.9, at=HR + V(0.06, 0.04, 0.25))
S.beat(held, l3[1] - 0.6, "staan", face="twijfel", face_amt=0.8, at=S.head(papa))
S.beat(held, l4[0] + 0.4, "staan", face="nerveus", face_amt=0.6, at=S.head(mama, 0))
S.beat(held, l4[1] - 0.2, "staan", face="blij", face_amt=0.6, at=S.head(mama, 0))
S.hold(held, END)
# glas en pekel
S.debris(HR + V(0, 0, 0.06), OPEN, n=8, size=(0.006, 0.016), color=(0.8, 0.95, 0.85), speed=(0.6, 1.4), up=1.2, floor=0.0, life=1.4, name="Glassplinter")
S.debris(HR + V(0, 0, 0.04), OPEN, n=10, size=(0.006, 0.012), color=(0.85, 0.9, 0.45), speed=(0.4, 1.2), up=1.4, floor=0.0, life=1.2, shape="sphere", name="Pekel")

# ---------------------------------------------------------------- mama
S.beat(mama, 0.0, **SIT_M, pose="ontspannen", face="blij", face_amt=0.3, at=S.head(papa) + V(0, 0, -0.3))
S.reach(mama, 0.0, "R", coffee.location + V(0.07, 0, 0.05))
S.beat(mama, l2[0] + 1.0, **SIT_M, pose="ontspannen", face="twijfel", face_amt=0.5, at=S.head(papa))
S.beat(mama, OPEN + 0.1, **SIT_M, pose="ontspannen", face="verbaasd", face_amt=0.8, at=JAR_P + V(0.1, 0, 0.2))
S.beat(mama, l4[0] - 0.1, **SIT_M, pose="ontspannen", face="lach", face_amt=1.0, at=S.head(held), body={"head": (-6, 0, 4), "chest": (-4, 0, 0)})
S.beat(mama, l4[1] + 0.3, **SIT_M, pose="ontspannen", face="blij", face_amt=0.8, at=S.head(held))
S.hold(mama, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((2.1, -3.6, 1.9), (-0.2, 0.0, 1.05), 24), ((1.9, -3.3, 1.85), (-0.2, 0.0, 1.05), 26))
S.cam(l2[0] - 0.2, ((0.95, -1.55, 1.45), (-0.2, 0.55, 1.12), 28), ((0.85, -1.4, 1.45), (-0.2, 0.55, 1.12), 30))
S.cam(l2[0] + 1.9, S.shot(papa, l2[0] + 2, "cu", az=-22, lens=36), S.shot(papa, l2[1], "cu", az=-18, lens=40))
S.cam(HAND - 0.3, (JAR_P + V(0.02, -0.7, -0.12), JAR_P + V(0.02, 0, 0.02), 34), (JAR_P + V(0.02, -0.6, -0.1), JAR_P + V(0.02, 0, 0.04), 38), dof=2.2)
S.cam(OPEN + 0.9, (HR + V(0.25, -0.5, 0.1), HR + V(0.06, 0.04, 0.22), 40), (HR + V(0.22, -0.42, 0.12), HR + V(0.1, 0.0, 0.26), 46), dof=2.0)
S.cam(l3[1] - 0.8, S.shot(papa, l3[1], "mcu", az=-20, lens=34))
S.cam(l4[0] - 0.2, S.shot(mama, l4[0], "cu", az=30, lens=38, h=0.05), S.shot(mama, l4[1], "cu", az=26, lens=42, h=0.05))
S.wall(l4[0] - 0.2, l4[1] + 0.1)
S.cam(l4[1] + 0.1, ((1.3, -4.0, 1.7), (-0.15, -0.1, 1.05), 25), ((1.2, -3.7, 1.7), (-0.15, -0.1, 1.05), 26))

S.finish(length=END)
