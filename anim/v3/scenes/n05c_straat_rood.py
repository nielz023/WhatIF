"""N05c · Drone over de straat om middernacht (script scène 5c, 3 s).
In elk huis springen de ramen tegelijk rood aan (de telefoons), daarna gaan hier en daar gewone lampen aan.

    blender -b -P anim/v3/scenes/n05c_straat_rood.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n05c", "straat", "avond", exposure=-0.6, night=True)
sh = S.cuts([3.0])
END = sh[-1][1]
T_RED = 0.3

# rommel van video 1 (boodschappen) weg
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
    key(e, 0.0, DARK, 0.1)
    key(e, T_RED - 1 / 24, DARK, 0.1)
    key(e, T_RED, RED, 3.5 + rnd.uniform(-0.6, 0.6))          # alles tegelijk rood
    if rnd.random() < 0.4:                                    # daarna gaat er een gewone lamp aan
        t_lamp = rnd.uniform(1.5, 2.7)
        key(e, t_lamp - 1 / 24, RED, 3.2)
        key(e, t_lamp, WARM, 1.6)
        key(e, END, WARM, 1.6)
    else:
        key(e, END, RED, 3.2)
    for fc in A._fcurves(m.node_tree):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    for s in slots:
        s.material = m
    n_house += 1
print("ramen per huis:", n_house)
# veranda- en straatlampen gaan pas na het alarm aan: veranda uit tot 1,6 s
vl = bpy.data.objects.get("Verandalicht")
if vl:
    light_key(vl, 0.0, 0)
    light_key(vl, 1.6, 60)
emission_key("veranda_lamp", 0.0, 0.0)
emission_key("veranda_lamp", 1.6, 6.0)
# rode gloed op de straat zodra het alarm afgaat
for k, x in enumerate((-24.0, -12.0, 0.0, 12.0)):
    for y in (9.0, -9.0):
        g = T.point_light(f"Alarmgloed_{k}_{'n' if y > 0 else 'z'}", (x, y, 3.5), color=RED, energy=0, radius=1.5, shadow=False)
        light_key(g, 0.0, 0)
        light_key(g, T_RED, 900)
        light_key(g, END, 700)

# ---------------------------------------------------------------- drone: trage glijvlucht langs de straat
S.cam(0.0, ((-34.0, -20.0, 26.0), (-6.0, 4.0, 2.0), 30), ((-27.0, -18.5, 23.5), (-1.0, 4.5, 2.0), 30), shake=S.shake(0.25),
      handheld=0.15)

S.sfx("sfx_alarm_nucleair", 0.0, 0.32, loop_to=END)
S.sfx("sfx_alarm_piep", T_RED, 0.35)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.15)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
