"""N03c · De laatste normale dag: de stad op de middag (script scène 3e-3f).
Mensen wachten ongeduldig bij een rood voetgangerslicht terwijl er geen auto rijdt; een agent schrijft een
parkeerbon. Het broertje stapt de stoep af, mama trekt hem aan zijn capuchon terug: "Wait for green."

    blender -b -P anim/v3/scenes/n03c_stad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n03c", "stad", "middag", exposure=0.2)
sh = S.cuts([3.0, 3.6])
END = sh[-1][1]
t_f = sh[1][0]
SW = 0.2                                     # hoogte van de stoep

# geparkeerde auto met bon naar de zuidkant van de dwarsstraat, dicht bij de wachtende mensen
CAR = V(-13.5, -4.7, 0)
car = S.obj("Auto_geparkeerd_0")
car.location = CAR
bon = S.obj("Parkeerbon")
bon.location = CAR + V(-1.2, 0, 1.02)
bon.hide_render = True
bon.keyframe_insert("hide_render", frame=1)
bon.hide_render = False
bon.keyframe_insert("hide_render", frame=F(2.35))
bpy.context.view_layer.update()

# ---------------------------------------------------------------- de wachtende mensen op de hoek (kijken naar +x)
crowd = []
SPOTS = [(-7.6, -9.9, 85, "figurant_a"), (-7.9, -8.3, 95, "figurant_c"), (-7.2, -6.9, 92, "figurant_d"),
         (-8.4, -7.4, 80, "figurant_e"), (-8.9, -8.8, 100, "figurant_f")]
for k, (x, y, r, nm) in enumerate(SPOTS):
    e = S.actor(nm, (x, y, SW), r)
    crowd.append(e)
    # ongeduldig wiebelen, op de tenen, van been naar been
    for j, t in enumerate(frange(0.0, END, 0.7 + 0.1 * k)):
        S.beat(e, t, "staan" if j % 2 else "handen_zij", amount=0.6, face="twijfel" if j % 3 else "neutraal", face_amt=0.5,
               at=V(6.5, -7.0, 2.6) if j % 2 else V(0, -30, 1.2), crouch=(0.0, 0), body={"spine": (0, 0, 4 if (j + k) % 2 else -4)})
    S.hold(e, END)
# de vrouw kijkt op haar horloge
w = crowd[2]
WATCH = arm("L", (0.25, 0.55, -0.6), (-0.55, 0.65, 0.35))
S.beat(w, 0.6, "staan", face="nerveus", face_amt=0.5, arms=WATCH, look=(0.3, -0.6), body={"head": (18, 0, -8)})
S.beat(w, 1.9, "staan", face="boos", face_amt=0.4, arms=WATCH, look=(0.3, -0.6), body={"head": (16, 0, -8)})
S.beat(w, 2.6, "handen_zij", face="twijfel", face_amt=0.5, at=V(6.5, -7.0, 2.6))
S.hold(w, END)

# ---------------------------------------------------------------- mama en het broertje vooraan bij de stoeprand
MAMA_AT, BRO_AT = V(-6.95, -9.3, SW), V(-6.4, -8.75, SW)
mama = S.actor("mama", MAMA_AT, 85)
bro = S.actor("broertje", BRO_AT, 90)
S.beat(mama, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(6.5, -7.0, 2.6))
S.beat(bro, 0.0, "handen_zij", face="twijfel", face_amt=0.6, at=V(6.0, -12, 1.0))
S.beat(bro, 1.5, "staan", face="boos", face_amt=0.4, at=V(0, -40, 1.0), body={"head": (0, 0, 0)})
# 3f: anticipatie (zakt door de knieën), stapt van de stoep...
S.beat(bro, t_f + 0.2, "staan", face="zelfverzekerd", face_amt=0.6, at=V(6, -7.8, 1.0), crouch=(0.08, 6))
STEP = V(-5.55, -8.75, 0)
S.walk(bro, t_f + 0.35, t_f + 0.8, [BRO_AT, STEP], stride=0.4)
# ...mama grijpt zijn capuchon en trekt hem terug, hij veert met overshoot tegen haar been
S.reach(mama, t_f + 0.45, "R", inf=0.0)
HOOD = lambda t: S.headpos(bro, t) + V(-0.32, 0, -0.32)
S.reach(mama, t_f + 0.85, "R", HOOD(t_f + 0.85))
S.beat(mama, t_f + 0.85, "staan", face="boos", face_amt=0.5, at=S.headpos(bro, t_f + 0.85) + V(1.6, -0.6, 0), body={"spine": (8, 0, 0)})
S.teleport(bro, t_f + 1.0, STEP, 90)
S.place(bro, t_f + 1.35, BRO_AT + V(-0.12, 0, 0), 90)
S.place(bro, t_f + 1.55, BRO_AT + V(0.04, 0, 0), 90)
S.place(bro, t_f + 1.75, BRO_AT, 90)
S.reach(mama, t_f + 1.35, "R", BRO_AT + V(-0.3, 0, 1.0))
S.reach(mama, t_f + 1.8, "R", inf=0.0)
S.beat(bro, t_f + 1.1, "schrik", amount=0.6, face="verbaasd", face_amt=0.8, crouch=(0.0, -10))
S.beat(mama, t_f + 1.9, "handen_zij", face="zelfverzekerd", face_amt=0.6, at=S.headpos(bro, t_f + 1.9) + V(1.8, -0.9, 0))
line = S.say("N03-03", who=mama, at=t_f + 1.0)
# zucht en kijkt mama aan, gebaart naar de lege straat
S.beat(bro, line[1] + 0.15, "schouders_op", face="twijfel", face_amt=0.8, at=S.headpos(mama, line[1]) + V(2.2, -1.6, 0), crouch=(0.03, -4))
S.beat(bro, line[1] + 1.1, "wijzen", amount=0.7, face="boos", face_amt=0.5, at=V(2.0, -16.0, 0.6))
S.say("N03-04", who=bro, at=line[1] + 0.15)
S.hold(bro, END)
S.hold(mama, END)

# ---------------------------------------------------------------- de agent schrijft een bon
ag = S.actor("agent", CAR + V(-1.0, -2.05, SW), 0)
WRITE = arms(arm("L", (0.25, 0.6, -0.75), (-0.2, 0.9, 0.35)), arm("R", (0.25, 0.55, -0.75), (-0.45, 0.8, 0.35)))
S.beat(ag, 0.0, "staan", arms=WRITE, face="neutraal", face_amt=0.5, look=(0.0, -0.6), body={"head": (18, 0, 0)})
S.beat(ag, 1.3, "staan", arms=WRITE, face="zelfverzekerd", face_amt=0.5, look=(0.0, -0.6), body={"head": (20, 0, 0)})
S.reach(ag, 1.85, "R", inf=0.0)
S.reach(ag, 2.3, "R", bon.location + V(0, -0.12, 0.05))
S.reach(ag, 2.7, "R", inf=0.0)
S.beat(ag, 2.8, "staan", face="zelfverzekerd", face_amt=0.6, at=bon.location)
S.hold(ag, END)

# ---------------------------------------------------------------- camera's
# 3e WIDE handheld op ooghoogte: de wachtende mensen, de lege straat, de agent bij de auto erachter
S.cam(0.0, ((-2.4, -13.6, 1.75), (-10.5, -6.4, 1.15), 26), ((-2.7, -13.2, 1.75), (-10.5, -6.4, 1.15), 27), handheld=0.35)
# 3f MEDIUM push-in vanaf de weg op mama en het broertje
S.cam(t_f, ((-3.4, -11.6, 1.2), (-6.6, -8.9, 1.05), 32), ((-3.85, -11.3, 1.17), (-6.6, -8.9, 1.05), 36), handheld=0.15)

# ---------------------------------------------------------------- HUD en geluid
S.countdown(0, 0.3, END, jumps=[(0.0, 7 * 3600 + 48 * 60 + 20)])
S.ambience("sfx_stad_dag", 0.0, END, vol=0.22)
S.sfx("sfx_klok_tik", 0.0, 0.12, loop_to=END)
S.sfx("sfx_stift", 0.4, 0.2)
S.finish(length=END, tail=0.0)
