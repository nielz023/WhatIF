"""D17b · De laatste zonsverduistering, 600 miljoen jaar (script scène 17b-a t/m 17b-d). Rode rotsvlakte, middag.
17b-a WIDE LOW drift 4 s: de maan schuift voor de zon, het wordt schemerig.  VO: "Every year, the Moon drifts about four centimeters away from Earth."
17b-b DETAIL 4 s: de maan bedekt de zon nét niet helemaal: een dunne, vurige ring.  VO: "So one day, it's too small to cover the Sun anymore."
17b-c CLOSE push-in 6,5 s (hier 2 shots): zijn gezicht in het schemerlicht.
      VO: "You're watching the last total eclipse there will ever be. And nobody else will ever know."
17b-d WIDE 3 s: het licht komt terug over de vlakte. Alleen muziek.

    python3 anim/v4/scenes/d17b_eclips.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d17b", "heuvel", "super", exposure=0.15)
sh = S.cuts([4.4, 4.0, 3.4, 3.3, 3.2])
END = sh[-1][1]
t_b, t_c, t_c2, t_d = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker")

ZD = V(0.0, math.cos(math.radians(32)), math.sin(math.radians(32)))
SUN = ZD * 2600
maan = bpy.data.objects.get("Maan")
MC = ZD * 1800
SIDE = V(1.0, 0.0, 0.0)
key(maan, 0.0, loc=tuple(MC - SIDE * 95))
key(maan, t_b + 0.6, loc=tuple(MC), interp="BEZIER")
key(maan, t_c2 + 2.0, loc=tuple(MC + SIDE * 6))
key(maan, END, loc=tuple(MC + SIDE * 75))

# ---------------------------------------------------------------- schemer: zon en hemel dimmen tijdens de verduistering
DIM = [(0.0, 1.0), (1.2, 1.0), (t_b + 0.5, 0.12), (t_d - 0.3, 0.12), (t_d + 1.6, 1.0)]
for o in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    e = o.data.energy
    for t, f in DIM:
        o.data.energy = e * f
        o.data.keyframe_insert("energy", frame=F(t))
    o.data.energy = e
wd = bpy.context.scene.world
for n in ([n for n in wd.node_tree.nodes if n.type == "BACKGROUND"] if wd and wd.node_tree else []):
    s0 = n.inputs["Strength"].default_value
    for t, f in DIM:
        n.inputs["Strength"].default_value = s0 * max(0.08, f)
        n.inputs["Strength"].keyframe_insert("default_value", frame=F(t))
    n.inputs["Strength"].default_value = s0

# ---------------------------------------------------------------- hij staat op de vlakte en kijkt omhoog
HP = V(0.0, 0.0, 0.0)
held = S.actor("hoofdpersonage_zwerver", HP, 180)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=SUN)
S.beat(held, t_b, "staan", face="verbaasd", face_amt=0.6, at=SUN)
S.beat(held, t_c, "staan", face="verbaasd", face_amt=0.7, at=SUN)
S.beat(held, t_c2, "staan", face="verdrietig", face_amt=0.4, at=SUN)
S.beat(held, t_c2 + 2.0, "staan", face="blij", face_amt=0.35, at=SUN)
S.beat(held, t_d + 0.4, "staan", face="blij", face_amt=0.5, at=SUN + V(300, 0, -400))
S.hold(held, END)
A.blink_at(held, F(t_c + 1.6))
HD = S.headpos(held, t_c + 1.0)
LOOK = (SUN - HD).normalized()
RS = V(LOOK.y, -LOOK.x, 0).normalized()

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(1.5, -4.0, 0.6), SUN * 0.02 + V(0, 0, 2.5), 24), (V(1.7, -3.8, 0.62), SUN * 0.02 + V(0, 0, 2.5), 24))
S.cam(t_b, (V(1.8, -2.6, 0.9), ZD * 2600, 200), (V(1.8, -2.6, 0.9), ZD * 2600, 210))
S.cam(t_c, (HD + LOOK * 1.3 + RS * 0.35 + V(0, 0, -0.1), HD, 35), (HD + LOOK * 1.15 + RS * 0.3 + V(0, 0, -0.1), HD, 35))
S.cam(t_c2, (HD + LOOK * 1.25 - RS * 0.25 + V(0, 0, -0.05), HD + V(0, 0, -0.08), 32), (HD + LOOK * 1.12 - RS * 0.22 + V(0, 0, -0.05), HD + V(0, 0, -0.08), 32))
S.cam(t_d, (V(-6.0, -14.0, 1.2), V(2.0, 40.0, 6.0), 22), (V(-5.6, -13.4, 1.25), V(2.0, 40.0, 6.0), 22))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(600000000, t0=0.0, big=True)
S.jump(0.0)
S.say("D17b-01", at=0.2)
S.say("D17b-02", at=t_b + 0.2)
S.say("D17b-03", at=t_c + 0.2)
S.ambience("sfx_wind_hoog", 0.0, END, vol=0.06)
S.music("strijkers_emo", 0.0, END, vol=0.17, fade_in=0.6, fade_out=0.8)
S.finish(length=END, tail=0.0)
