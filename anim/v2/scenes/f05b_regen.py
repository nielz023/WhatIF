"""F05b · Dag 2 · 10x · achtertuin in de regen, vroege ochtend. De druppels dwarrelen als sneeuw; er landt er een
in zijn hand; hij tikt er een aan en die splitst. Hij belt zijn beste vriend: een diep gerommel. '...hello?'
Niemand kan hem nog horen.

    blender -b -P anim/v2/scenes/f05b_regen.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402

S = Scene2("f05b", "tuin", "regen")

FALL = 0.9                                       # m/s: regen (9 m/s) gedeeld door tien
DOOR = V(1.4, 0.45, 0.01)
SPOT = V(0.6, 6.0, 0.0)                          # midden in de dichte druppelwolk

# ---------------------------------------------------------------- tijdlijn
S.hud2(2, "10x", clock=clock(7 * 3600 + 31 * 60 + 4, 0.1, dec=1, day="TUE"), t0=0.4)
l1 = S.say("F05-03", gap=0.6)
FLOAT = l1[0] + 3.0                              # 'the raindrops are... floating'
HAND = l1[0] + 4.4                               # 'you hold out your hand'
LAND = l1[1] - 0.8
l2 = S.say("F05-04", gap=0.5)
TAP = l2[0] + 1.6
l3 = S.say("F05-05", gap=0.5)
CALL = l3[1] - 1.2                               # 'so you call your best friend'
l4 = S.say_slow("F05-06", "Vriend", gap=0.4, sub="FRIEND", subtitle="...hello?", gain=1.0)
l5 = S.say("F05-07", gap=0.4)
l6 = S.say("F05-08", gap=0.5)
l7 = S.say("F05-09", gap=0.7)
END = l7[1] + 2.0
S.ambience("sfx_regen", 0.0, l3[1], vol=0.10)
S.music("strijkers_warm", 0.0, l4[0], vol=0.22, fade_in=1.2, fade_out=1.5)
S.music("drone", l4[0] - 0.5, END + 0.5, vol=0.16, fade_in=2.0, fade_out=2.0)
S.sfx("sfx_telefoon_rommel", l4[0] - 0.2, 0.5)
S.sfx("sfx_glasdeur", 0.2, 0.25)

# ---------------------------------------------------------------- de regen valt, heel langzaam (naadloze lus)
# elke druppelwolk krijgt een gekoppelde kopie één wolkhoogte erboven; beide zakken en springen samen terug
for name, H in (("Regendruppels", 4.95), ("Regendruppels_camera", 1.0)):
    o = S.obj(name)
    cp = o.copy()
    bpy.context.scene.collection.objects.link(cp)
    cp.location = o.location + V(0, 0, H)
    period = H / FALL
    for ob, z0 in ((o, o.location.z), (cp, cp.location.z)):
        t = 0.0
        while t < END + period:
            key(ob, t, loc=V(ob.location.x, ob.location.y, z0))
            key(ob, t + period - 1 / 24, loc=V(ob.location.x, ob.location.y, z0 - FALL * (period - 1 / 24)))
            t += period
        for fc in A._fcurves(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
            for i in range(1, len(fc.keyframe_points), 2):
                fc.keyframe_points[i].interpolation = "CONSTANT"

# ---------------------------------------------------------------- hij
held = S.actor("hoofdpersonage", DOOR, 0)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0, 0.3))
S.walk(held, 0.3, FLOAT - 0.4, [DOOR, DOOR + V(-0.2, 2.0, 0), SPOT], end_rot=200, stride=0.5)
S.beat(held, FLOAT, "staan", face="verbaasd", face_amt=0.9, at=SPOT + V(0.6, 0.6, 2.4))
S.beat(held, FLOAT + 1.2, "staan", face="verbaasd", face_amt=1.0, at=SPOT + V(-0.8, 0.4, 2.0), body={"head": (-12, 0, 0)})
# een druppel landt in zijn hand
PALM = SPOT + V(0.14, 0.4, 0.86)                 # voor hem (hij kijkt naar +y)
drop = T.sphere("Druppel_hand", (0, 0, 0), 0.007, HU.water("regendruppel"), scale=(1, 1, 1.5), seg=10, ol=0)
S.beat(held, HAND, "staan", face="verbaasd", face_amt=0.8, at=PALM, arms=HAND_OUT_R)
S.beat(held, LAND, "staan", face="blij", face_amt=0.9, at=PALM, arms=HAND_OUT_R)
S.beat(held, l1[1] + 0.3, "staan", face="lach", face_amt=0.7, at=PALM, arms=HAND_OUT_R)
HP = S.bone_world(held, "hand.R", LAND, tail=True) + V(0, 0, 0.045)   # de druppel landt echt op zijn hand
key(drop, 0.0, loc=HP + V(0, 0, FALL * LAND))
key(drop, LAND, loc=HP)
key(drop, LAND + 0.4, loc=HP + V(0, 0, -0.01), scale=(1.4, 1.4, 0.6))
for fc in A._fcurves(drop):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
# hij tikt een druppel aan: die splitst in tweeën
TIP = SPOT + V(-0.25, 0.42, 1.18)
tapd = T.sphere("Tikdruppel", (0, 0, 0), 0.008, HU.water("regendruppel"), scale=(1, 1, 1.4), seg=10, ol=0)
key(tapd, 0.0, loc=TIP + V(0, 0, FALL * TAP))
key(tapd, TAP, loc=TIP)
show(tapd, 0.0, TAP + 1 / 24)
halves = [S.obj("Gesplitste_druppel_1"), S.obj("Gesplitste_druppel_2")]
for k, h in enumerate(halves):
    side = -1 if k == 0 else 1
    show(h, TAP)
    key(h, TAP, loc=TIP + V(0.004 * side, 0, 0))
    key(h, TAP + 4.0, loc=TIP + V(0.05 * side, -0.01, -FALL * 4.0 * 0.9))
    for fc in A._fcurves(h):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
S.beat(held, TAP - 0.6, "staan", face="blij", face_amt=0.7, at=TIP)
S.reach(held, TAP - 0.5, "L", None, 0.0)
S.reach(held, TAP - 0.05, "L", TIP + V(0.02, -0.03, -0.01))
S.reach(held, TAP + 0.5, "L", None, 0.0)
S.beat(held, TAP + 0.2, "staan", face="lach", face_amt=0.9, at=TIP + V(0, 0, -0.2))
# de telefoon
phone = prop_phone(S, "Telefoon_held", (0, 0, 0))
grab(S, phone, held, CALL - 0.6, "hand.R", loc=(0.0, 0.07, 0.02), rot=(90, 0, 180))
show(phone, CALL - 0.6)
S.beat(held, CALL - 0.5, "staan", face="blij", face_amt=0.8, look=(0, -0.2), arms=HOLD_FRONT_R)
S.beat(held, CALL + 0.4, "staan", face="blij", face_amt=0.7, look=(0.3, 0.1), arms=PHONE_EAR_R)
S.beat(held, l4[0] + 0.6, "staan", face="twijfel", face_amt=0.8, look=(0.2, 0), arms=PHONE_EAR_R)
S.beat(held, l5[0] + 1.6, "staan", face="nerveus", face_amt=0.8, look=(0.1, -0.1), arms=PHONE_EAR_R)
S.beat(held, l6[0] + 1.2, "staan", face="verdrietig", face_amt=0.6, at=SPOT + V(0, 0.6, 0.6), arms=HOLD_FRONT_R)
S.beat(held, l7[0] + 0.4, "staan", face="verdrietig", face_amt=0.9, look=(0, 0.25), body={"head": (-8, 0, 0)}, arms=HOLD_FRONT_R)
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-1.6, 10.9, 1.9), (0.6, 3.0, 1.4), 22), ((-1.5, 10.6, 1.85), (0.6, 4.0, 1.3), 23))
S.cam(FLOAT - 0.2, ((0.1, 8.1, 1.2), (0.6, 6.0, 1.35), 35), ((0.1, 7.8, 1.22), (0.6, 6.0, 1.4), 38), dof=2.8)
HR = S.bone_world(held, "hand.R", LAND, tail=False)
S.cam(HAND - 0.1, (HR + V(0.3, 0.5, 0.12), HR + V(-0.02, 0.04, 0.02), 40), (HR + V(0.26, 0.44, 0.11), HR + V(-0.02, 0.04, 0.02), 44), dof=0.7)
S.cam(l1[1] + 0.1, S.shot(held, l1[1] + 0.5, "mcu", az=-20, lens=36))
S.cam(TAP - 0.7, (TIP + V(-0.4, 0.35, 0.06), TIP + V(0.05, -0.1, 0.0), 42), (TIP + V(-0.34, 0.3, 0.05), TIP + V(0.05, -0.1, 0.0), 46), dof=0.7)
S.cam(TAP + 1.4, ((-2.4, 3.6, 1.5), (1.0, 8.0, 1.1), 24), ((-2.2, 3.8, 1.5), (0.8, 7.5, 1.1), 26))
S.cam(CALL - 0.4, S.shot(held, CALL, "med", az=-30, lens=30), S.shot(held, l4[1], "mcu", az=-20, lens=38))
S.cam(l5[0] + 2.4, S.shot(held, l5[1], "cu", az=-15, lens=42, h=0.05), S.shot(held, l6[1], "cu", az=-10, lens=48, h=0.05), dof=1.6)
S.cam(l7[0] - 0.2, ((0.9, 8.2, 2.6), (0.6, 6.0, 1.0), 30), ((1.6, 10.8, 6.0), (0.6, 6.0, 0.8), 28))

S.finish(length=END)
