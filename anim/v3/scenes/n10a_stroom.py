"""N10a · Dag 4: het licht gaat uit (script scène 10a-10c2). Stad, de lange laan, 21:12. Ook bron voor de teaser (0a-0c).
10a  WIDE track naast de fiets: de jongen fietst met een jerrycan water aan zijn stuur naar huis, overal brandt licht.
     VO: "Power plants don't run themselves. They need people watching them, every second of every day."
10b  DETAIL: lege controlekamer, een rood lampje knippert, een meter tikt naar het rode vlak.
10c  WIDE drone statisch: 21:13, de stad gaat blok voor blok op zwart, van de horizon naar de camera. Thunk per blok.
10c2 LOW WIDE (camera rijdt achteruit voor de fiets uit) + CLOSE: hij sprint staand op de pedalen voor de golf uit,
     de lantaarns achter hem vallen uit, het licht op zijn gezicht verdwijnt.

    blender -b -P anim/v3/scenes/n10a_stroom.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n10a", "stad", "stroom", exposure=-0.6, night=True)
sh = S.cuts([4.2, 2.0, 5.0, 2.5, 1.6])
END = sh[-1][1]
t_b, t_c, t_c2, t_c3 = sh[1][0], sh[2][0], sh[3][0], sh[4][0]

for o in list(bpy.data.objects):
    if o.name.startswith("Fiets_held"):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# de skyline aan de horizon gebruikt de raammaterialen van blok A-C; zet ze op blok H zodat de golf echt bij de horizon begint
for o in bpy.data.objects:
    if o.name.startswith("Skyline") and o.type == "MESH":
        for ms in o.material_slots:
            if ms.material and ms.material.name in ("ramen_A", "ramen_B", "ramen_C"):
                ms.material = bpy.data.materials.get("ramen_H")

# ---------------------------------------------------------------- stroomuitval per blok (ramen, lantaarns, hun lichten)
BLOCK_T = {}


def blackout(blk, t):
    BLOCK_T[blk] = t
    for nm in (f"ramen_{blk}", f"lantaarn_{blk}"):
        m = bpy.data.materials.get(nm)
        if m is None or not m.node_tree:
            print("LET OP: materiaal ontbreekt", nm)
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
    S.sfx("sfx_dreun", t, 0.22 + 0.04 * ("HGFEDCBA".index(blk)))


for k, blk in enumerate("HGFEDCB"):
    blackout(blk, t_c + 0.4 + k * 0.55)
T_A = t_c3 + 0.55                                           # het laatste blok (waar hij is) gaat uit in de close-up
blackout("A", T_A)

# ---------------------------------------------------------------- de jongen op de fiets met jerrycan en lamp
held = S.actor("hoofdpersonage_kind", (1.6, 72.0, 0), 180)
_, crank = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen", lamp=True, jerrycan=True)
ride_path(S, held, crank, 0.0, t_c + 2.2, [V(1.6, 72.0, 0), V(1.8, 50.0, 0), V(1.7, 38.0, 0)], cadence=1.0, lean=10, sway=2)
ride_path(S, held, crank, t_c + 2.2, END, [V(1.7, 38.0, 0), V(1.5, 20.0, 0), V(1.6, -2.0, 0)], cadence=2.4, lean=24, stand=True, sway=7)
S.face(held, 0.0, "neutraal", 0.5, look=(0.2, 0.5))
S.face(held, 2.4, "twijfel", 0.6, look=(0.0, 0.6))                    # kijkt naar de lucht
S.face(held, t_c2, "bang", 1.0, look=(0.0, 0.1))
S.face(held, t_c3, "geschrokken", 1.0, look=(0.5, 0.0))
A.bone_rot(held, F(t_c3), "head", (0, 0, 0))
A.bone_rot(held, F(t_c3 + 0.4), "head", (0, 50, 0))                   # kijkt over zijn schouder
A.bone_rot(held, F(END), "head", (0, 45, 0))
A.blink_at(held, F(t_c3 + 0.9))

# ---------------------------------------------------------------- 10b: de lege controlekamer (los decor buiten de stad)
CR = V(400.0, -400.0, 0.0)
PANEL = S.mat("paneel_grijs", (0.42, 0.45, 0.48))
T.box("Centrale_paneel", tuple(CR), (2.4, 0.5, 1.6), PANEL, bevel=0.03, ol=0.006)
T.box("Centrale_muur", tuple(CR + V(0, 0.6, 0)), (6.0, 0.2, 3.0), S.mat("centrale_muur", (0.30, 0.33, 0.36)), bevel=0, ol=0)
T.box("Centrale_vloer", tuple(CR + V(0, 0, -0.02)), (6.0, 6.0, 0.02), S.mat("centrale_vloer", (0.22, 0.23, 0.25)), bevel=0, ol=0)
for k in range(6):
    T.box(f"Centrale_knop_{k}", tuple(CR + V(-0.9 + k * 0.18, -0.26, 0.95)), (0.1, 0.03, 0.06), S.mat(f"knop_{k % 3}", [(0.2, 0.6, 0.3), (0.85, 0.75, 0.2), (0.25, 0.4, 0.8)][k % 3], 1.5), bevel=0.005, ol=0)
red = T.sphere("Centrale_rood_lampje", tuple(CR + V(0.75, -0.27, 1.38)), 0.045, S.mat("lampje_rood", (1.0, 0.05, 0.03), 9.0), seg=12, ol=0)
on = True
for t in frange(0.0, END, 0.25):
    red.hide_render = not on
    red.keyframe_insert("hide_render", frame=F(t))
    on = not on
for fc in A._fcurves(red):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
# meter: wit vlak met een rood vlak rechts, wijzer draait naar rood
G = CR + V(0.0, -0.265, 1.3)
T.cyl("Meter_plaat", tuple(G), 0.2, 0.01, S.mat("meter_wit", (0.95, 0.95, 0.92)), rot=(90, 0, 0), seg=32, ol=0.003)
T.box("Meter_rood_vlak", tuple(G + V(0.11, -0.012, 0.06)), (0.12, 0.003, 0.1), S.mat("meter_rood", (0.9, 0.1, 0.08)), rot=(0, -35, 0), base=False, bevel=0, ol=0)
naald = T.box("Meter_naald", (0, 0, 0), (0.006, 0.004, 0.17), S.mat("naald_zwart", (0.05, 0.05, 0.05)), base=True, bevel=0, ol=0)
naald.location = G + V(0, -0.016, 0)
for t, a in ((0.0, -40), (t_b, -40), (t_b + 0.6, 10), (t_b + 0.9, 5), (t_b + 1.4, 58), (t_b + 1.6, 52), (t_b + 1.8, 62)):
    naald.rotation_euler = (0, math.radians(a), 0)
    naald.keyframe_insert("rotation_euler", frame=F(t))
lc = T.point_light("Centrale_licht", tuple(CR + V(0.3, -1.2, 2.2)), color=(0.7, 0.8, 1.0), energy=120, radius=0.5)

# ---------------------------------------------------------------- camera's
# 10a WIDE track naast de fiets (links, iets voor hem), de laan met alle lichten erachter
S.cam(0.0, None, fn=S.follow(held, (-3.4, -2.4, 0.9), lens=26, look_offset=(0.8, 3.0, 0.6)), shake=S.shake(0.15))
# 10b DETAIL de meter en het rode lampje
S.cam(t_b, (G + V(-0.35, -0.9, 0.2), G + V(0.25, 0, 0.02), 40), (G + V(-0.3, -0.75, 0.18), G + V(0.25, 0, 0.02), 44))
# 10c WIDE drone statisch, hoog boven de laan; de golf rolt van de horizon naar ons
S.cam(t_c, ((0.0, -40.0, 55.0), (0.0, 120.0, 0.0), 28), ((0.0, -38.0, 54.0), (0.0, 118.0, 0.0), 28))
# 10c2 LOW WIDE: camera rijdt laag achteruit voor de fiets uit
S.cam(t_c2, None, fn=S.follow(held, (0.3, -4.9, 0.55), lens=24, look_offset=(0.0, 14.0, 1.6)), shake=S.shake(0.35))
# 10c2 CLOSE handheld: zijn gezicht, de lantaarn achter hem valt uit
S.cam(t_c3, None, fn=S.follow(held, (1.0, -1.9, 1.15), lens=34, look_offset=(0.0, 0.0, 0.0)), shake=S.shake(0.6))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 4", 0, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.05)
S.sfx("sfx_alarm_piep", t_b + 0.1, 0.1, loop_to=t_c)
S.say("N10-01", at=0.2)
S.finish(length=END, tail=0.0)
