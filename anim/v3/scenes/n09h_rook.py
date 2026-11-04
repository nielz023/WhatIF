"""N09h · Dag 3: avond, rook in de verte (script scène 9h), straat in de schemering.
9h-1 WIDE trage push: de straat in, achter de daken stijgen rookkolommen op, oranje gloed. Geen politie.
     VO: "This part is real: in 1977, New York lost power for just one night. More than a thousand fires were started."
9h-2 MEDIUM: een geparkeerde auto met loeiend alarm, knipperlichten, rook op de achtergrond.
9h-3 LOW push-in op het huis van de jongen, warme ramen. De lantaarn ervoor flakkert één keer.
     Mini-cliffhanger VO: "And on day four... the power went out here too."

    blender -b -P anim/v3/scenes/n09h_rook.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n09h", "straat", "avond", exposure=-0.3, night=True)
sh = S.cuts([5.6, 3.0, 4.6])
END = sh[-1][1]
t_2, t_3 = sh[1][0], sh[2][0]
rnd = random.Random(19)

for o in list(bpy.data.objects):
    if o.name.startswith(("Boodschappentas", "Appels")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- rookkolommen achter de daken (loopen over de hele scène)
SMOKE = [S.mat("rook_donker", (0.16, 0.15, 0.15)), S.mat("rook_grijs", (0.30, 0.28, 0.27))]
EMBER = S.mat("vuurgloed", (1.0, 0.42, 0.10), 6.0)
COLS = [(V(-62.0, 26.0, 0), 46.0, 9.0), (V(-44.0, -28.0, 0), 38.0, 7.5), (V(-110.0, 24.0, 0), 55.0, 12.0), (V(-20.0, 40.0, 0), 40.0, 8.0)]
for c, (base, hgt, wid) in enumerate(COLS):
    T.sphere(f"Vuur_gloed_{c}", tuple(base + V(0, 0, 2.0)), wid * 0.45, EMBER, scale=(1.4, 1.4, 0.7), seg=14, ol=0)
    lt = T.point_light(f"Vuur_licht_{c}", tuple(base + V(0, 0, 4.0)), color=(1.0, 0.45, 0.15), energy=40000, radius=3.0, shadow=False)
    for t, e in ((0.0, 30000), (0.7, 48000), (1.5, 26000), (2.6, 52000), (3.4, 30000), (4.7, 46000), (6.0, 28000), (7.5, 50000),
                 (9.0, 32000), (10.6, 47000), (END, 36000)):
        light_key(lt, t, e * (0.7 + 0.15 * c), interp="LINEAR")
    P_PER = 4.5
    N = 16
    for i in range(N):
        o = T.sphere(f"Rook_{c}_{i}", (0, 0, 0), 1.0, SMOKE[i % 2], seg=12, ol=0)
        drift = V(rnd.uniform(2, 6), rnd.uniform(-1, 1), 0)
        jit = V(rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0) * wid * 0.2
        phase = i / N * P_PER
        t = -phase
        while t < END + 0.1:
            for u, z, s in ((0.0, 2.0, 0.35), (0.5, hgt * 0.5, 0.9), (1.0, hgt, 1.25)):
                tt = t + u * P_PER
                o.location = base + jit + drift * u + V(0, 0, z)
                o.scale = [wid * s * (0.8 + 0.4 * ((i * 7) % 5) / 4)] * 3
                o.keyframe_insert("location", frame=F(tt))
                o.keyframe_insert("scale", frame=F(tt))
            t += P_PER
        for fc in A._fcurves(o):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

# ---------------------------------------------------------------- de auto met alarm: oranje knipperlichten
car = S.obj("Auto_geparkeerd_2")
bpy.context.view_layer.update()
pts = [car.matrix_world @ V(cc) for cc in car.bound_box]
lo = V([min(p[i] for p in pts) for i in range(3)])
hi = V([max(p[i] for p in pts) for i in range(3)])
BLINK = S.mat("knipperlicht", (1.0, 0.55, 0.05), 8.0)
blinkers = []
for x in (lo.x - 0.01, hi.x + 0.01):
    for y in (lo.y + 0.22, hi.y - 0.22):
        blinkers.append(T.box(f"Knipperlicht_{x:.0f}_{y:.0f}", (x, y, lo.z + 0.62), (0.03, 0.18, 0.08), BLINK, base=False, bevel=0, ol=0))
blt = T.point_light("Knipper_licht", tuple((lo + hi) / 2 + V(0, 0, 0.8)), color=(1.0, 0.55, 0.1), energy=0, radius=0.5, shadow=False)
on = True
for k, t in enumerate(frange(0.0, END, 0.35)):
    for b in blinkers:
        b.hide_render = not on
        b.keyframe_insert("hide_render", frame=F(t))
    light_key(blt, t, 600 if on else 0)
    on = not on
for b in blinkers:
    for fc in A._fcurves(b):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"

# ---------------------------------------------------------------- de lantaarn voor het huis flakkert één keer (vooruitblik op dag 4)
lamp_mats = {ms.material for o in bpy.data.objects if o.name.startswith("Lantaarn_n_0") for c in [o] + list(o.children_recursive)
             for ms in getattr(c, "material_slots", []) if ms.material and ms.material.node_tree
             and any(n.type == "EMISSION" for n in ms.material.node_tree.nodes)}
T_FL = t_3 + 3.2
for m in lamp_mats:
    for t, s in ((0.0, 1.0), (T_FL, 1.0), (T_FL + 0.08, 0.05), (T_FL + 0.16, 0.9), (T_FL + 0.26, 0.0), (T_FL + 0.4, 0.8), (END, 0.8)):
        for n in m.node_tree.nodes:
            if n.type == "EMISSION":
                if not hasattr(n, "_base"):
                    pass
                sock = n.inputs["Strength"]
                if t == 0.0:
                    m["_base"] = sock.default_value
                sock.default_value = m["_base"] * s
                sock.keyframe_insert("default_value", frame=F(t))
    if m.node_tree.animation_data and m.node_tree.animation_data.action:
        for fc in A._fcurves(m.node_tree):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
print("LANTAARN-MATERIALEN:", [m.name for m in lamp_mats])

# ---------------------------------------------------------------- camera's
# 9h-1 WIDE de straat in (naar -x), rook boven de daken
S.cam(0.0, ((14.0, 1.2, 1.7), (-40.0, 4.5, 7.5), 24), ((11.5, 1.3, 1.65), (-40.0, 4.5, 7.5), 25), handheld=0.08)
# 9h-2 MEDIUM de auto met alarm, van schuin voor, rook erachter
CC = (lo + hi) / 2
S.cam(t_2, (CC + V(4.6, -3.2, 0.35), CC + V(-3.5, 1.2, 1.6), 26), (CC + V(4.2, -3.0, 0.35), CC + V(-3.5, 1.2, 1.7), 27), handheld=0.2)
# 9h-3 LOW push-in op het huis van de jongen
S.cam(t_3, ((4.6, 0.6, 0.7), (-1.0, 12.9, 4.2), 24), ((4.0, 2.4, 0.75), (-1.0, 12.9, 4.4), 26))

# ---------------------------------------------------------------- HUD, geluid en stemmen
S.counter("DAY 3", 0, t0=0.0)
S.ambience("sfx_rook_sirenes", 0.0, END, vol=0.05)
S.sfx("sfx_autoalarm", t_2 - 0.6, 0.12, loop_to=t_3 + 0.8)
S.sfx("sfx_stad_nacht_wind", t_3, 0.06, loop_to=END)
S.say("N09-07", at=0.3)
S.say("N09-08", at=t_3 + 0.3)
S.finish(length=END, tail=0.0)
