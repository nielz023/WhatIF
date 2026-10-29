"""F04a · Dag 2 · 10x · slaapkamer, 06:20. Wakker vóór de wekker. Hij stoot zijn waterglas om, vangt het,
bekijkt het en schept het water er weer in. Reactietijd: een kwart seconde -> een veertigste.

    blender -b -P anim/v2/scenes/f04a_glas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402

S = Scene2("f04a", "slaapkamer", "dag2")

LIE_AT = V(-1.38, 0.1, 0.4)
SEAT = V(-0.93, 1.1, 0)                          # bedrand, vlak bij het nachtkastje (links van hem)
SIT = dict(pose="ontspannen", crouch=(0.13, -4.0), feet=((0.02, 0.30, 0.17), (-0.02, 0.30, 0.17)))
glass = S.obj("Glas_water")
gwater = S.obj("Glas_water_water")
G0 = Vector(glass.location)
wekker = S.obj("Wekker")
CLOCK_P = wekker.matrix_world.translation + V(0, -0.03, 0.06)
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = True
COVER = T.box("Dekbed_over_hem", (-1.47, 0.36, 0.44), (1.12, 1.6, 0.47), S.obj("Dekbed_blauw").active_material, bevel=0.14, ol=0)

held = S.actor("hoofdpersonage", LIE_AT, 0)

# ---------------------------------------------------------------- tijdlijn
S.hud2(2, "10x", clock=clock(6 * 3600 + 20 * 60, 0.1, dec=1, day="TUE"), t0=0.4)
l1 = S.say("F04-01", gap=0.7)
UP = l1[0] + 3.5                                 # liggen -> zitten (verstopt achter de wekker-close-up)
l2 = S.say("F04-02", gap=0.5)
KNOCK = l2[0] + 0.6
CATCH = l2[0] + 2.2
LOOK = l2[0] + 3.2
SCOOP = l2[0] + 4.3
IN = SCOOP + 0.9
l3 = S.say("F04-03", gap=0.45)
END = l3[1] + 0.8
S.music("ochtend", 0.0, END + 1, vol=0.2, fade_in=0.8, fade_out=1.0)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.05)
S.sfx("sfx_whoosh", KNOCK - 0.1, 0.25)
S.sfx("sfx_hud_tik", CATCH, 0.3)
S.gauge2("REACTION: 0.25 s", l3[0] + 3.2, l3[0] + 6.6, color=HUD_W)
S.gauge2("TODAY: 0.025 s", l3[0] + 6.8, END, color=GOLD)

# ---------------------------------------------------------------- liggen, ogen open, rechtop
COVER_SHOW = show(COVER, 0.0, UP)
held.rig.location, held.rig.rotation_euler = LIE_AT, (math.radians(-75), 0, 0)
for p in ("location", "rotation_euler"):
    held.rig.keyframe_insert(p, frame=F(0))
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.3, look=(0, 0.2))
S.eyes_closed(held, 0.0, l1[0] + 0.5)
S.beat(held, l1[0] + 0.9, "staan", face="verbaasd", face_amt=0.6, look=(0.5, 0.2), body={"head": (0, 25, 0)})
held.rig.location, held.rig.rotation_euler = SEAT, (0, 0, math.radians(90))
for p in ("location", "rotation_euler"):
    held.rig.keyframe_insert(p, frame=F(UP))
for fc in A._fcurves(held.rig):
    if fc.data_path in ("location", "rotation_euler"):
        for kp in fc.keyframe_points:
            if kp.co.x <= F(UP) + 0.5:
                kp.interpolation = "CONSTANT"
S.beat(held, UP, **SIT, face="verbaasd", face_amt=0.7, at=CLOCK_P)
S.beat(held, l1[1] - 0.6, **SIT, face="verbaasd", face_amt=0.9, look=(0, 0.1), body={"head": (-4, -10, 0)})

# ---------------------------------------------------------------- het glas valt (in zijn tijd: heel langzaam)
P1 = G0 + V(0.10, -0.10, 0.06)                   # kantelt over de rand
P2 = G0 + V(0.22, -0.2, -0.13)                   # waar hij het vangt
key(glass, 0.0, loc=G0, rot=(0, 0, 0))
key(glass, KNOCK, loc=G0, rot=(0, 0, 0))
key(glass, KNOCK + 0.5, loc=P1, rot=(-25, 55, 0))
key(glass, CATCH, loc=P2, rot=(-35, 95, 0))
S.reach(held, KNOCK - 0.6, "L", None, 0.0)
S.reach(held, KNOCK - 0.05, "L", G0 + V(-0.05, 0.02, 0.07))     # zijn hand tikt het om
S.reach(held, KNOCK + 0.45, "L", G0 + V(0.0, -0.05, 0.12))
S.reach(held, CATCH - 0.1, "L", P2 + V(0, 0, 0.04))             # en vangt het
S.beat(held, KNOCK + 0.15, **SIT, face="geschrokken", face_amt=0.7, at=P1)
S.beat(held, CATCH + 0.1, **SIT, face="verbaasd", face_amt=0.8, at=P2)
grab(S, glass, held, CATCH, "hand.L", mode="loc", offset=(0.02, 0.0, -0.06))
key(glass, CATCH + 0.5, rot=(0, 0, 0))                          # rechtop in zijn hand
FACE = SEAT + V(0.36, 0.06, 0.95)                               # voor zijn gezicht
S.reach(held, LOOK, "L", FACE + V(0, 0.03, -0.05))
S.beat(held, LOOK + 0.1, **SIT, face="verbaasd", face_amt=1.0, at=FACE)

# het water: een klont die blijft hangen, met een paar losse druppels
W0 = G0 + V(0.06, -0.06, 0.12)
W1 = G0 + V(0.32, -0.22, 0.04)
W2 = W1 + V(0.03, 0.0, -0.02)
blob = T.sphere("Waterklont", (0, 0, 0), 0.035, HU.water("water"), scale=(1.6, 1.0, 0.7), seg=16, ol=0)
drops = [T.sphere(f"Waterdruppel_{k}", (0, 0, 0), 0.008 + 0.003 * (k % 2), HU.water("water"), seg=10, ol=0) for k in range(5)]
show(blob, KNOCK + 0.3, IN)
key(blob, KNOCK + 0.3, loc=W0, rot=(0, 0, 0), scale=(0.4, 0.4, 0.4))
key(blob, CATCH, loc=W1, rot=(0, 20, 10), scale=(1, 1, 1))
key(blob, SCOOP, loc=W2, rot=(0, 35, 20), scale=(1.05, 0.95, 1.0))
for k, d in enumerate(drops):
    off = V(0.05 * math.cos(k * 1.3), 0.05 * math.sin(k * 1.7), 0.03 * math.sin(k * 2.1))
    show(d, KNOCK + 0.35, SCOOP + 0.3)
    key(d, KNOCK + 0.35, loc=W0)
    key(d, SCOOP, loc=W2 + off * 1.6)
show(gwater, 0.0, KNOCK + 0.3)
show(gwater, IN - 0.05)
# hij schept de klont met zijn rechterhand terug in het glas
GL_IN = FACE + V(0, 0.03, -0.05) + V(0.0, 0.05, 0.02)
S.reach(held, SCOOP - 0.5, "R", None, 0.0)
S.reach(held, SCOOP, "R", W2 + V(-0.02, -0.04, -0.02))
S.reach(held, IN - 0.1, "R", GL_IN + V(0.02, -0.06, 0.1))
S.reach(held, IN + 0.5, "R", None, 0.0)
key(blob, IN - 0.15, loc=GL_IN + V(0.02, -0.04, 0.12), rot=(0, 0, 0), scale=(0.7, 0.7, 0.7))
S.beat(held, SCOOP, **SIT, face="blij", face_amt=0.6, at=W2)
S.beat(held, IN + 0.2, **SIT, face="lach", face_amt=0.7, at=FACE)
S.beat(held, l3[0] + 2.4, **SIT, face="blij", face_amt=0.8, look=(0, 0.1), body={"head": (-4, -12, 0)})
S.beat(held, l3[1] - 1.0, **SIT, face="grijns", face_amt=0.8, at=FACE)
S.hold(held, END)

# ---------------------------------------------------------------- camera
HL = LIE_AT + V(0, 1.42, 0.38)
S.cam(0.0, (HL + V(0.45, -0.75, 0.85), HL + V(0, -0.05, 0.05), 38), (HL + V(0.38, -0.62, 0.72), HL + V(0, -0.05, 0.05), 42), dof=1.4)
S.cam(l1[0] + 1.8, (CLOCK_P + V(0.62, -0.62, 0.3), CLOCK_P + V(-0.18, 0, 0.02), 32), (CLOCK_P + V(0.56, -0.56, 0.28), CLOCK_P + V(-0.18, 0, 0.02), 35), dof=1.4)
S.cam(l1[0] + 3.6, S.shot(held, l1[0] + 4, "med", az=-20, lens=30), S.shot(held, l1[1], "mcu", az=-15, lens=34))
S.cam(l2[0] + 0.3, ((0.3, 1.55, 1.2), G0 + V(0.15, -0.2, -0.02), 30), ((0.25, 1.5, 1.15), G0 + V(0.22, -0.25, -0.06), 32), dof=1.5)
S.cam(CATCH + 0.6, ((0.3, 0.45, 1.2), (-0.72, 1.12, 1.08), 28), ((0.2, 0.5, 1.18), (-0.72, 1.12, 1.08), 30))
S.cam(l3[0] - 0.1, S.shot(held, l3[0], "med", az=-45, lens=30), S.shot(held, l3[1], "med", az=-40, lens=33))

S.finish(length=END)
