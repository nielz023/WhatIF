"""N13i · Dag 7: in het lab van de wetenschapper (script scène 13i-13j). De wetenschapper is een MAN (niels 2026-11-04).
13i  MEDIUM push-in: hij pakt een doosje medicijnen uit de kast en houdt het vast.
     WETENSCHAPPER: "This is what he needs. But I want something in return."
13i2 CLOSE: JONGEN: "Anything."
13j  CLOSE: WETENSCHAPPER: "Tell your street to meet me. Tomorrow night. We need to talk."
     Hij legt het doosje in de handen van de jongen en houdt zijn hand er nog even op.
13k  DETAIL: het doosje in zijn handen. VO: "And what he said at that meeting... changed everything."

    blender -b -P anim/v3/scenes/n13i_lab.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n13i", "brug", "lab_binnen", exposure=0.2)
sh = S.cuts([4.6, 1.6, 4.8, 3.9])
END = sh[-1][1]
t_i2, t_j, t_k = [s[0] for s in sh[1:]]

# ---------------------------------------------------------------- het doosje in de kast
box = S.obj("Medicijndoos_kast")
bpy.context.view_layer.update()
BOX0 = box.matrix_world.translation.copy()
box.scale = (1.5, 1.5, 1.5)

# ---------------------------------------------------------------- de wetenschapper (man) en de jongen
W0 = V(2.42, 1.86, 0)
wet = S.actor("wetenschapper", W0, 180)                          # kijkt naar +y, de kast in
male_scientist(S, wet)
H_AT = V(2.2, -1.05, 0)
held = S.actor("hoofdpersonage_kind", H_AT, 180)                 # kijkt naar +y, naar hem
for o in list(bpy.data.objects):
    if o.name.startswith("wetenschapper_klembord"):
        o.hide_render = o.hide_viewport = True

T_GRAB = 0.75
S.beat(wet, 0.0, "staan", face="neutraal", face_amt=0.5, at=BOX0)
S.reach(wet, 0.0, "R", inf=0.0)
S.reach(wet, T_GRAB - 0.35, "R", BOX0 + V(0.0, -0.12, 0.06))
S.reach(wet, T_GRAB, "R", BOX0 + V(0.0, -0.02, 0.03))
grab(S, box, wet, T_GRAB, "hand.R", loc=(0.0, 0.07, 0.0), rot=(0, 0, 90))
S.reach(wet, T_GRAB + 0.3, "R", inf=0.0)
S.reach(wet, 0.0, "L", inf=0.0)
S.turn(wet, T_GRAB + 0.35, T_GRAB + 1.0, 0)                        # draait zich om naar de jongen
W1 = V(2.28, -0.12, 0)
S.walk(wet, T_GRAB + 1.0, T_GRAB + 2.0, [W0, W1], stride=0.4, turn=False)
S.beat(wet, T_GRAB + 2.1, "staan", face="vastberaden", face_amt=0.5, at=S.headpos(held, 0.0), arms=HOLD_FRONT_R, feet="keep")
S.beat(wet, t_i2 - 0.6, "staan", face="twijfel", face_amt=0.5, at=S.headpos(held, 0.0), arms=HOLD_FRONT_R, feet="keep")
S.say("N13-04", who=wet, at=0.3)

S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.5, at=BOX0)
S.beat(held, T_GRAB + 1.6, "staan", face="nerveus", face_amt=0.6, at=S.headpos(wet, 0.0) + V(0, -1.8, -0.1))
S.beat(held, t_i2, "staan", face="vastberaden", face_amt=0.8, at=V(2.3, 0.05, 1.6))
S.say("N13-05", who=held, at=t_i2 + 0.25)

# ---------------------------------------------------------------- 13j: het doosje in zijn handen, zijn hand er nog even op
P = V(2.24, -0.55, 0.92)
T_GIVE, T_REL, T_OFF = t_j + 1.0, t_j + 1.6, t_j + 3.6
S.beat(wet, t_j, "staan", face="vastberaden", face_amt=0.6, at=S.headpos(held, 0.0), arms=HOLD_FRONT_R, feet="keep")
S.reach(wet, t_j + 0.3, "R", P + V(0.0, 0.18, 0.12))
S.reach(wet, T_GIVE, "R", P + V(0.0, 0.05, 0.06))
S.reach(wet, T_REL, "R", P + V(0.0, 0.0, 0.1))                    # hand bovenop het doosje
S.reach(wet, T_OFF, "R", P + V(0.0, 0.0, 0.1))
S.reach(wet, T_OFF + 0.5, "R", inf=0.0)
S.say("N13-06", who=wet, at=t_j + 0.25)
# het doosje: los van zijn hand vanaf T_REL, ligt dan in de handen van de jongen
for c in box.constraints:
    c.keyframe_insert("influence", frame=F(T_REL) - 1)
    c.influence = 0.0
    c.keyframe_insert("influence", frame=F(T_REL))
box.location = BOX0
box.keyframe_insert("location", frame=1)
box.keyframe_insert("location", frame=F(T_REL) - 1)
box.location = P
box.keyframe_insert("location", frame=F(T_REL))
for fc in A._fcurves(box):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
for side, dx in (("L", -0.1), ("R", 0.1)):          # hij kijkt naar +y: zijn rechterhand zit aan +x
    S.reach(held, 0.0, side, inf=0.0)
    S.reach(held, T_GIVE - 0.4, side, inf=0.0)
    S.reach(held, T_GIVE, side, P + V(dx, -0.02, -0.04))
    S.reach(held, END, side, P + V(dx, -0.02, -0.04))
S.beat(held, t_j, "staan", face="nerveus", face_amt=0.5, at=S.headpos(wet, 0.0) + V(0, -1.75, -0.05))
S.beat(held, T_REL + 0.2, "staan", face="vastberaden", face_amt=0.4, at=P)
S.beat(held, t_k, "staan", face="vastberaden", face_amt=0.7, at=P)
A.blink_at(held, F(t_k + 1.2))
S.hold(wet, END)
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 13i MEDIUM push-in: hij bij de medicijnkast, de jongen op de voorgrond
S.cam(0.0, ((0.2, -2.3, 1.6), (2.4, 1.4, 1.2), 26), ((0.6, -1.7, 1.55), (2.4, 1.2, 1.2), 30))
# 13i2 CLOSE de jongen, langs de wetenschapper
HH = S.headpos(held, t_i2 + 0.5)
S.cam(t_i2, (HH + V(-0.75, 1.05, 0.05), HH + V(0, 0, -0.08), 32), (HH + V(-0.7, 0.98, 0.05), HH + V(0, 0, -0.08), 34))
# 13j CLOSE de wetenschapper over de schouder van de jongen
WH = S.headpos(wet, t_j + 1.0)
S.cam(t_j, (WH + V(1.08, -1.75, -0.3), WH + V(-0.15, 0, -0.2), 30), (WH + V(1.02, -1.64, -0.28), WH + V(-0.15, 0, -0.2), 32))
# 13k DETAIL het doosje in zijn handen, trage push
S.cam(t_k, ((P.x - 0.7, P.y + 0.5, P.z + 0.5), P + V(0, 0, 0.03), 36), ((P.x - 0.6, P.y + 0.43, P.z + 0.43), P + V(0, 0, 0.03), 40))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 7", 0, t0=0.0)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.04)
S.sfx("sfx_la_dicht", T_GRAB - 0.05, 0.15)
S.say("N13-07", at=t_k + 0.2)
S.finish(length=END, tail=0.0)
