"""OR2b · What if everyone disappeared except you? · de laan 's avonds, regel 4.

4  DAY 3: jij staat midden op de lege laan. "The power goes out": de stad gaat blok voor blok op zwart, van de
   horizon naar jou toe; het laatste blok (waar jij staat) gaat uit in de close-up.

    python3 anim/shorts/or2b_stad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or2", "b", "stad", "stroom", lines=(4,))
L = S.L
T0, END = S.t0, S.t1
W = lambda n, i: L[n][0] + S.words[f"OR2-{n:02d}"][i]["s"]
S.clip = (0.05, 3000)
S.sc.view_settings.exposure = -0.6

for o in list(bpy.data.objects):
    if o.name.startswith("Fiets_held"):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True
for o in bpy.data.objects:          # skyline aan de horizon hoort bij blok H (golf begint daar)
    if o.name.startswith("Skyline") and o.type == "MESH":
        for ms in o.material_slots:
            if ms.material and ms.material.name in ("ramen_A", "ramen_B", "ramen_C"):
                ms.material = bpy.data.materials.get("ramen_H")


def light_key(o, t, e):
    o.data.energy = e
    o.data.keyframe_insert("energy", frame=F(t))


def blackout(blk, t):
    for nm in (f"ramen_{blk}", f"lantaarn_{blk}"):
        m = bpy.data.materials.get(nm)
        if m is None or not m.node_tree:
            continue
        for n in m.node_tree.nodes:
            if n.type == "EMISSION" or "Emission Strength" in n.inputs:
                sock = n.inputs["Strength"] if n.type == "EMISSION" else n.inputs["Emission Strength"]
                base = sock.default_value
                for tt, s in ((0.0, base), (t - 1 / 24, base), (t, base * 0.02)):
                    sock.default_value = s
                    sock.keyframe_insert("default_value", frame=F(tt))
        if m.node_tree.animation_data and m.node_tree.animation_data.action:
            for fc in A._fcurves(m.node_tree):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"
    col = bpy.data.collections.get(f"Lantaarnlicht_{blk}")
    if col:
        for o in col.all_objects:
            if o.type == "LIGHT":
                e = o.data.energy
                light_key(o, 0.0, e)
                light_key(o, t - 1 / 24, e)
                light_key(o, t, 0.0)
                for fc in A._fcurves(o.data):
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"
    S.sfx("sfx_dreun", t, 0.18 + 0.03 * ("HGFEDCBA".index(blk)))


d3 = L[4][0]
P = V(0.9, 4.0, 0)
held = S.actor("hoofdpersonage", P, 180)
HEAD = S.head(held, 0.0)
t_go = W(4, 3) - 0.05                 # "power"
T_A = W(4, 5) + 0.05                  # "out": jouw blok
for k, blk in enumerate("HGFEDCB"):
    blackout(blk, t_go + k * (T_A - 0.25 - t_go) / 6)
blackout("A", T_A)
S.sfx("sfx_stroom_thunk", T_A, 0.35)

S.beat(held, T0, "staan", face="nerveus", face_amt=0.5, look=(0, 0.3), body={"head": (-6, 0, 0)})
S.beat(held, t_go + 0.3, "staan", face="bang", face_amt=0.7, look=(0, 0.3), body={"head": (-8, 0, 0)})
S.beat(held, T_A - 0.2, "staan", face="bang", face_amt=1.0, look=(0.2, 0.2), body={"head": (-4, 0, 8)})
S.beat(held, T_A + 0.1, "staan", face="geschrokken", face_amt=1.0, look=(0.5, 0.1), body={"head": (-2, 0, 14)})
S.beat(held, END, "staan", face="geschrokken", face_amt=0.9, look=(0.6, 0.1), body={"head": (-2, 0, 16)})
# zwak blauw maanlicht van voren: na de uitval blijft je gezicht net leesbaar
mf = T.area_light("Maan_gezicht", tuple(HEAD + V(0.8, 2.5, 1.4)), tuple(HEAD), size=(1.0, 1.0), color=(0.5, 0.6, 1.0), energy=14)
mf.visible_camera = False
# wijd van achter je: de laan en de skyline die uitgaat
S.cam(T0, ((P.x - 0.9, P.y - 4.5, 1.0), (P.x + 0.3, P.y + 60, 7.0), 26), ((P.x - 0.8, P.y - 3.8, 0.95), (P.x + 0.3, P.y + 60, 7.5), 28))
# close: je gezicht, het licht om je heen gaat uit
S.cam(T_A - 0.45, ((HEAD.x + 0.25, HEAD.y + 1.3, HEAD.z - 0.05), tuple(HEAD + V(0, 0, -0.05)), 32),
      ((HEAD.x + 0.22, HEAD.y + 1.15, HEAD.z - 0.05), tuple(HEAD + V(0, 0, -0.05)), 34))
S.counter("DAY 3", d3, L[4][1] + 0.2)
S.done()
