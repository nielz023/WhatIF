"""N15e · Dag 14: het winkelcentrum als koninkrijk (script scène 15e).
15e-1 WIDE push-in: de ingang, barricade van winkelkarren, twee volgelingen op wacht, de rode fiets van de vriend bij de deur.
15e-2 MEDIUM: het grote bord 20 RULES, bovenaan 1. THE BOSS IS ALWAYS RIGHT.
      VO: "And the boy who wanted no rules at all?"

    blender -b -P anim/v3/scenes/n15e_ingang.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n15e", "koninkrijk", "ingang", exposure=0.0)
sh = S.cuts([2.6, 2.4])
END = sh[-1][1]
t_2 = sh[1][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# twee volgelingen op wacht voor de ingang, armen over elkaar
wa = S.actor("volgeling_b", V(-1.6, -3.3, 0), 0)
wb = S.actor("volgeling_c", V(1.9, -3.1, 0), -10)
for ch in (wa, wb):
    S.beat(ch, 0.0, "armen_over", face="zelfverzekerd", face_amt=0.7, look=(0.0, 0.0))
A.bone_rot(wa, F(1.2), "head", (0, 0, 0))
A.bone_rot(wa, F(1.8), "head", (0, 20, 0))
for ch in (wa, wb):
    S.hold(ch, END)

# vlaggen wapperen een beetje
for n in ("Vlag_koninkrijk_l", "Vlag_koninkrijk_r"):
    o = S.obj(n)
    for c in o.children_recursive:
        if c.type == "MESH" and "doek" in c.name.lower():
            c.rotation_mode = "XYZ"
            for f in range(F(0.0), F(END) + 1, 3):
                t = (f - 1) / FPS
                c.rotation_euler.z = math.radians(6 * math.sin(t * 3.1 + len(n)))
                c.keyframe_insert("rotation_euler", index=2, frame=f)

# ---------------------------------------------------------------- camera's
S.cam(0.0, ((-3.5, -20.0, 2.0), (-4.5, 0.0, 2.6), 24), ((-3.2, -14.5, 1.9), (-4.2, 0.0, 2.6), 24))
S.cam(t_2, ((-10.6, -6.6, 1.8), (-12.5, -1.6, 2.3), 30), ((-10.8, -6.0, 1.85), (-12.5, -1.6, 2.4), 32))

S.counter("DAY 14", 6, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.04)
S.music("m_spanning_puls", 0.0, END, vol=0.16, fade_in=0.2, fade_out=0.2)
S.say("N15-03", at=0.6)
S.finish(length=END, tail=0.0)
