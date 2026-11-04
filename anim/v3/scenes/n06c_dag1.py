"""N06c · De teller verschijnt (script scène 6c, 5 s).
WIDE van buiten op het huis, trage pull-back. HUD rechtsboven verschijnt voor het eerst: DAY 1 · RULES: 0.
VO: "Day one." Daarna 1 s stilte (muziek stopt hard in de eindmontage).

    blender -b -P anim/v3/scenes/n06c_dag1.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n06c", "straat", "avond", exposure=-0.6, night=True)
sh = S.cuts([5.0])
END = sh[-1][1]

for o in list(bpy.data.objects):
    if o.name.startswith(("Boodschappentas", "Appels")):
        o.hide_render = o.hide_viewport = True

DARK, RED, WARM = (0.04, 0.05, 0.09), (1.0, 0.07, 0.04), (1.0, 0.74, 0.40)


def win_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N = m.node_tree.nodes
    N.clear()
    e = N.new("ShaderNodeEmission")
    o = N.new("ShaderNodeOutputMaterial")
    m.node_tree.links.new(e.outputs[0], o.inputs[0])
    return m, e


def key(e, t, col, strength):
    e.inputs["Color"].default_value = (*col, 1)
    e.inputs["Strength"].default_value = strength
    e.inputs["Color"].keyframe_insert("default_value", frame=F(t))
    e.inputs["Strength"].keyframe_insert("default_value", frame=F(t))


rnd = random.Random(5)
n_house = 0
for ob in list(bpy.data.objects):
    if ob.type != "MESH" or not ob.name.startswith("Huis_"):
        continue
    slots = [s for s in ob.material_slots if s.material and s.material.name.split(".")[0] in ("raamglas", "raam_warm")]
    if not slots:
        continue
    m, e = win_mat(f"raam_alarm_{n_house}")
    r = rnd.random()
    if ob.name == "Huis_hoofdpersonage":
        key(e, 0.0, WARM, 1.4)
    elif r < 0.55:
        key(e, 0.0, WARM, 1.6)
    elif r < 0.8:
        key(e, 0.0, RED, 3.0)
    else:
        key(e, 0.0, DARK, 0.1)
    for fc in A._fcurves(m.node_tree):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    for s in slots:
        s.material = m
    n_house += 1

# oranje knipperlicht van het kruispunt verderop valt over de straat
ORANJE = (1.0, 0.55, 0.08)
kn = T.point_light("Knipperlicht_straat", (14.0, 2.0, 4.0), color=ORANJE, energy=0, radius=1.0, shadow=False)
t, on = 0.0, True
while t <= END + 0.01:
    light_key(kn, t, 1800 if on else 0)
    t += 0.5
    on = not on

# trage pull-back van het slaapkamerraam naar het hele huis in de straat
S.cam(0.0, ((1.6, 4.8, 4.7), (0.8, 13.0, 4.1), 30), ((3.0, -5.5, 6.2), (0.6, 13.0, 3.6), 26), handheld=0.1)

S.counter("DAY 1", 0, t0=0.9)
S.say("N06-02", at=1.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.12)
S.sfx("sfx_alarm_nucleair", 0.0, 0.05, loop_to=2.5)
S.finish(length=END, tail=0.0)
