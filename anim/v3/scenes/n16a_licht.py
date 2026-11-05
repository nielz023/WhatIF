"""N16a · Dag 30: het eerste licht (script scène 16a-16e). Straat in de schemering, lantaarn met zonnepaneel.
16a MEDIUM handheld: de jongen en de wetenschapper sjouwen een zonnepaneel naar de straatlantaarn (de jongen achteruit).
16b DETAIL: de handen van de wetenschapper verbinden twee draden in een kroonsteentje, de schroevendraaier draait echt.
16c WIDE: de hele straat staat te kijken, kinderen op schouders.
16d CLOSE: WETENSCHAPPER: "Okay. Now." De jongen duwt met zijn duim de schakelaar om.
16e LOW WIDE trage push: de lantaarn flikkert... en blijft branden. De straat juicht, de agent fluit.
    VO: "The first light in thirty days."

    blender -b -P anim/v3/scenes/n16a_licht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n16a", "straat", "nr_eerste_licht", exposure=0.15)
sh = S.cuts([3.5, 3.0, 3.0, 2.6, 4.6])
END = sh[-1][1]
t_b, t_c, t_d, t_e = [s[0] for s in sh[1:]]
rnd = random.Random(16)

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

LAMP = V(8.0, 6.5, 0.12)
HEAD = V(8.0, 5.0, 5.7)                         # lampkop (arm wijst naar -y)

# ---------------------------------------------------------------- de lantaarn: uit, flikkert, aan
T_ON0 = t_e + 0.25
FLICK = [(0.0, 0.0), (T_ON0, 0.0), (T_ON0 + 0.08, 1.0), (T_ON0 + 0.16, 0.0), (T_ON0 + 0.5, 0.0), (T_ON0 + 0.56, 0.8),
         (T_ON0 + 0.62, 0.1), (T_ON0 + 0.7, 1.0), (T_ON0 + 0.78, 0.2), (T_ON0 + 1.15, 0.2), (T_ON0 + 1.3, 1.0), (END, 1.0)]
lights = [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("Lantaarn_zonnepaneel")]
bulb = S.obj("Lantaarn_zonnepaneel_lamp")
emis = []
for m in bulb.data.materials:
    if m and m.node_tree:
        for n in m.node_tree.nodes:
            if "Strength" in n.inputs and n.type in ("EMISSION", "BSDF_PRINCIPLED"):
                emis.append((n.inputs["Strength"] if n.type == "EMISSION" else n.inputs["Emission Strength"], n.inputs["Strength"].default_value
                             if n.type == "EMISSION" else n.inputs["Emission Strength"].default_value, m))
E0 = {lo.name: lo.data.energy for lo in lights}
for t, v in FLICK:
    f = F(t)
    for lo in lights:
        lo.data.energy = E0[lo.name] * v * 1.3
        lo.data.keyframe_insert("energy", frame=f)
    for sock, s0, m in emis:
        sock.default_value = max(s0, 12.0) * v
        sock.keyframe_insert("default_value", frame=f)
for lo in lights:
    if lo.data.animation_data and lo.data.animation_data.action:
        for fc in A._fcurves(lo.data):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
# zachte lichtbundel in de mist (kegel, doorschijnend)
cone_m = bpy.data.materials.new("lichtbundel_mist")
cone_m.use_nodes = True
nt = cone_m.node_tree
nt.nodes.clear()
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
mx = nt.nodes.new("ShaderNodeMixShader")
tr = nt.nodes.new("ShaderNodeBsdfTransparent")
em = nt.nodes.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.78, 0.5, 1)
em.inputs["Strength"].default_value = 1.0
mx.inputs[0].default_value = 0.08
nt.links.new(tr.outputs[0], mx.inputs[1])
nt.links.new(em.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], o_.inputs[0])
try:
    cone_m.surface_render_method = "BLENDED"
except Exception:
    cone_m.blend_method = "BLEND"
for t, v in FLICK:
    mx.inputs[0].default_value = 0.08 * v
    mx.inputs[0].keyframe_insert("default_value", frame=F(t))
cone = T.cyl("Lichtbundel", tuple(HEAD - V(0, 0, 5.6)), 1.7, 5.55, cone_m, r2=0.15, seg=32, ol=0)
cone.visible_shadow = False
if os.environ.get("WHATIF_ENGINE") == "WORKBENCH":          # (workbench kent geen doorschijnend licht)
    cone.hide_render = True

# ---------------------------------------------------------------- 16a: zonnepaneel sjouwen (de jongen loopt achteruit voorop)
set_panel = [o for o in bpy.data.objects if o.name.startswith("Zonnepaneel_lantaarn")]
for o in set_panel:
    if o.type == "MESH":
        o.hide_render = False
        visible(o, 0.0, False)
        visible(o, t_b, True)
FRAME = S.mat("aluminium_paneel_dragen", (0.75, 0.77, 0.8))
CELL = S.mat("zonnecel_dragen", (0.05, 0.10, 0.25))
pan = T.box("Paneel_gedragen", (0, 0, 0), (1.6, 1.0, 0.04), FRAME, base=False, bevel=0.005, ol=0.003)
T.box("Paneel_gedragen_cellen", (0, 0, 0.022), (1.52, 0.92, 0.004), CELL, base=False, bevel=0, ol=0).parent = pan
for i in range(1, 4):
    T.box(f"Paneel_gedragen_lijn{i}", (-0.76 + i * 0.38, 0, 0.025), (0.008, 0.92, 0.002), FRAME, base=False, bevel=0, ol=0).parent = pan
A0, A1 = V(3.8, 5.3, 0), V(8.6, 5.3, 0)
held = S.actor("hoofdpersonage_kind", A0 + V(0.9, 0, 0), -90)           # kijkt naar -x, loopt achteruit (+x)
wet = S.actor("wetenschapper", A0 - V(0.9, 0, 0), -90 + 180)            # kijkt naar +x
male_scientist(S, wet)
for o in list(bpy.data.objects):
    if o.name.startswith("wetenschapper_klembord"):
        o.hide_render = o.hide_viewport = True
S.walk(held, 0.0, t_b, [A0 + V(0.9, 0, 0), A1 + V(0.9, 0, 0)], stride=0.26, turn=False)
S.walk(wet, 0.0, t_b, [A0 - V(0.9, 0, 0), A1 - V(0.9, 0, 0)], stride=0.36, turn=False)
for f in range(F(0.0), F(t_b) + 1):
    t = (f - 1) / FPS
    a = S._root_matrix(held, t).translation
    b = S._root_matrix(wet, t).translation
    pan.location = (a + b) / 2 + V(0, 0, 0.72 + 0.015 * math.sin(t * 9))
    pan.rotation_euler = (0, math.radians(2.0 * math.sin(t * 4.5)), 0)
    pan.keyframe_insert("location", frame=f)
    pan.keyframe_insert("rotation_euler", frame=f)
visible(pan, 0.0, True)
visible(pan, t_b, False)
for t in frange(0.0, t_b, 0.2):
    S.sc.frame_set(F(t))
    for ch, sx in ((held, 0.78), (wet, -0.78)):
        for side, sy in (("L", 1), ("R", -1)):
            yy = sy * (0.42 if ch is wet else -0.42)
            S.reach(ch, t, side, pan.matrix_world @ V(sx, yy, 0.03))
S.beat(held, 0.0, "staan", face="inspanning", face_amt=0.5, look=(0.7, 0.0), crouch=(0.04, 8))
S.beat(held, 1.4, "staan", face="inspanning", face_amt=0.6, at=S.headpos(wet, 1.4), crouch=(0.05, 8))
S.beat(wet, 0.0, "staan", face="inspanning", face_amt=0.4, at=pan.location + V(-0.4, 0, 0), crouch=(0.04, 10))
S.beat(wet, 1.8, "staan", face="vastberaden", face_amt=0.5, at=S.headpos(held, 1.8), crouch=(0.04, 10))
for ch in (held, wet):
    for side in ("L", "R"):
        S.reach(ch, t_b - 0.01, side, inf=0.0)

# ---------------------------------------------------------------- 16b: draden in het kroonsteentje (kastje aan de paal)
BOX = V(8.0, 6.36, 1.02)
GREY = S.mat("kastje_grijs", (0.55, 0.57, 0.58))
T.box("Paal_kastje", tuple(BOX), (0.22, 0.12, 0.3), GREY, base=False, bevel=0.012, ol=0.004)
kroon = T.box("Kroonsteentje", tuple(BOX + V(0, -0.075, -0.02)), (0.09, 0.03, 0.035), S.mat("kroonsteen_wit", (0.95, 0.95, 0.93)), base=False, bevel=0.004, ol=0.002)
RED, BLK = S.mat("draad_rood", (0.85, 0.1, 0.08)), S.mat("draad_zwart", (0.05, 0.05, 0.06))
for k, (dx, m) in enumerate(((-0.03, RED), (0.03, BLK))):
    T.to_mesh(T.tube(f"Draad_{k}", [BOX + V(dx * 3, -0.12, -0.6), BOX + V(dx * 2, -0.14, -0.25), BOX + V(dx, -0.09, -0.02)], 0.006, m))
switch = T.box("Schakelaar", tuple(BOX + V(0.05, -0.065, 0.08)), (0.04, 0.02, 0.06), S.mat("schakelaar_zwart", (0.06, 0.06, 0.07)), base=False, bevel=0.004, ol=0.002)
lever = T.box("Schakelaar_hendel", (0, 0, 0), (0.012, 0.015, 0.035), S.mat("schakelaar_rood", (0.9, 0.12, 0.08)), base=False, bevel=0.003, ol=0.001)
lever.location = BOX + V(0.05, -0.08, 0.08)
lever.rotation_mode = "XYZ"
W_B = V(8.0, 5.72, 0.12)
S.teleport(wet, t_b, W_B, 180)
wet.rig.location = tuple(W_B)
wet.rig.keyframe_insert("location", frame=F(t_b))
sd = T.cyl("Schroevendraaier", (0, 0, 0), 0.006, 0.09, S.mat("staal", (0.8, 0.8, 0.82)), seg=8, ol=0)
T.cyl("Schroevendraaier_heft", (0, 0, -0.1), 0.014, 0.1, S.mat("heft_geel", (0.95, 0.75, 0.1)), seg=10, ol=0.002).parent = sd
sd.rotation_mode = "XYZ"
for f in range(F(t_b), F(t_c) + 1):
    t = (f - 1) / FPS
    sd.location = BOX + V(0.035, -0.2 + 0.01 * math.sin(t * 6), -0.02)
    sd.rotation_euler = (math.radians(-90), (t - t_b) * 7.0, 0)
    sd.keyframe_insert("location", frame=f)
    sd.keyframe_insert("rotation_euler", frame=f)
visible(sd, 0.0, False)
visible(sd, t_b, True)
visible(sd, t_c, False)
S.reach(wet, t_b, "R", BOX + V(0.035, -0.25, -0.04))
S.reach(wet, t_c - 0.05, "R", BOX + V(0.035, -0.25, -0.04))
S.reach(wet, t_b, "L", BOX + V(-0.05, -0.14, -0.06))
S.reach(wet, t_c - 0.05, "L", BOX + V(-0.04, -0.14, -0.05))
S.beat(wet, t_b, "staan", face="vastberaden", face_amt=0.6, at=BOX, feet="keep", crouch=(0.12, 18))
S.reach(wet, t_c, "R", inf=0.0)
S.reach(wet, t_c, "L", inf=0.0)

# ---------------------------------------------------------------- 16c-16e: de straat kijkt
CROWD = [("papa", (5.4, 2.6), None), ("mama", (6.3, 2.0), None), ("opa", (9.6, 2.3), None), ("oma", (10.4, 2.9), None),
         ("agent", (11.4, 3.7), None), ("beste_vriend", (4.6, 3.6), None), ("buurman", (12.0, 2.4), None),
         ("figurant_a", (7.4, 1.4), None), ("figurant_b", (8.6, 1.6), None), ("figurant_d", (3.8, 2.2), None),
         ("figurant_e", (10.9, 1.2), None), ("kind_b", (6.9, 3.4), None)]
C = {}
for n, (x, y), _ in CROWD:
    p = V(x, y, 0)
    d = HEAD - p
    C[n] = S.actor(n, p, math.degrees(math.atan2(d.x, -d.y)), **({"drop": ("agent_badge",)} if n == "agent" else {}))
no_phone(C["beste_vriend"])
# kinderen staan op kratjes naast hun ouders om over de hoofden te kijken
SHOULD = {}
for kid, carrier, off in (("broertje", "papa", V(0.75, 0.25, 0)), ("kind_a", "figurant_d", V(-0.7, 0.3, 0))):
    cp = C[carrier]
    base = V(cp.rig.location.x, cp.rig.location.y, 0) + off
    T.box(f"Kratje_{kid}", tuple(base), (0.5, 0.4, 0.4), S.mat("plastic_krat_blauw", (0.15, 0.35, 0.75)), bevel=0.03, ol=0.004)
    d = HEAD - base
    k = S.actor(kid, base + V(0, 0, 0.4), math.degrees(math.atan2(d.x, -d.y)))
    SHOULD[kid] = (k, base + V(0, 0, 0.4))
    C[kid] = k
for n, ch in C.items():
    S.beat(ch, 0.0, "staan", face="nerveus" if n not in SHOULD else "verbaasd", face_amt=0.4, at=HEAD + V(0, 0, -2.5))
# de toeschouwers komen pas in beeld vanaf 16c (in 16a staan ze nog niet langs de stoep)
for ch in C.values():
    for c in ch.rig.children_recursive:
        if c.type == "MESH":
            visible(c, 0.0, False)
            visible(c, t_c, True)
for n in ("mama", "opa", "oma", "figurant_b"):
    S.beat(C[n], t_c + rnd.uniform(0, 0.8), "staan", face="nerveus", face_amt=0.5, at=BOX + V(0, 0, 0.3))

# 16d: de jongen bij de schakelaar, de wetenschapper ernaast
H_D, W_D = V(7.55, 5.95, 0.12), V(6.85, 5.25, 0.12)
S.teleport(held, t_c, H_D, 132)
held.rig.location = tuple(H_D)
held.rig.keyframe_insert("location", frame=F(t_c))
S.teleport(wet, t_c, W_D, 140)
wet.rig.location = tuple(W_D)
wet.rig.keyframe_insert("location", frame=F(t_c))
S.beat(wet, t_c, "staan", face="vastberaden", face_amt=0.6, at=S.headpos(held, t_c + 0.1), feet="keep")
S.say("N16-01", who=wet, at=t_d + 0.3)
SW = lever.location.copy()
S.beat(held, t_c, "staan", face="nerveus", face_amt=0.5, at=SW, feet="keep")
S.reach(held, t_c - 0.05, "R", inf=0.0)                          # arm blijft hangen tot de snede (niet 3 s langzaam heffen)
S.reach(held, t_c, "R", SW + V(0.0, -0.09, 0.0))
S.reach(held, t_d + 1.5, "R", SW + V(0.0, -0.09, 0.01))
S.reach(held, t_d + 1.75, "R", SW + V(0.0, -0.1, 0.03))          # duim trekt even terug (anticipatie)
S.reach(held, t_d + 2.05, "R", SW + V(0.0, -0.085, -0.03))         # en duwt de schakelaar om
S.reach(held, t_e + 0.6, "R", SW + V(0.0, -0.085, -0.03))
S.reach(held, t_e + 1.0, "R", inf=0.0)
S.beat(held, t_d + 0.3, "staan", face="vastberaden", face_amt=0.6, at=S.headpos(wet, t_d), feet="keep")
S.beat(held, t_d + 1.4, "staan", face="vastberaden", face_amt=0.8, at=SW, feet="keep")
for t, a in ((0.0, 25), (t_d + 2.0, 25), (t_d + 2.08, -25)):
    lever.rotation_euler.x = math.radians(a)
    lever.keyframe_insert("rotation_euler", index=0, frame=F(t))

# 16e: hij brandt! juichen, handen omhoog, de agent fluit, het broertje stuitert op papa's schouders
T_YAY = T_ON0 + 1.4
for n, ch in C.items():
    if n == "agent":
        continue
    t = T_YAY + rnd.uniform(0.0, 0.5)
    S.beat(ch, t, "juichen" if (n in SHOULD or rnd.random() < 0.6) else "armen_omhoog", face="lach", face_amt=0.8, at=HEAD, feet="keep")
bk, bpos = SHOULD["broertje"]
for i, t in enumerate(frange(T_YAY, END, 0.24)):
    S.place(bk, t, bpos + V(0, 0, 0.16 if i % 2 else 0.0))
ag = C["agent"]
WH = S.bone_world(ag, "head", 0.0, tail=False) + V(0, -0.15, -0.05)
S.reach(ag, T_YAY, "R", WH)
S.reach(ag, END, "R", WH)
S.beat(ag, T_YAY, "staan", face="blij", face_amt=0.7, at=HEAD, feet="keep", arms=arm("L", (0.3, 0.2, 0.9), (0.2, 0.1, 0.95)))
S.beat(held, T_ON0 + 0.2, "staan", face="verbaasd", face_amt=0.8, at=HEAD, feet="keep")
S.beat(held, T_YAY + 0.2, "juichen", face="lach", face_amt=0.9, at=HEAD, feet="keep")
S.beat(wet, T_ON0 + 0.3, "staan", face="verbaasd", face_amt=0.7, at=HEAD, feet="keep")
S.beat(wet, T_YAY + 0.4, "staan", face="blij", face_amt=0.9, at=S.headpos(held, T_YAY), feet="keep")
for ch in list(C.values()) + [held, wet]:
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 16a MEDIUM handheld, meelopend langs de straatkant
S.cam(0.0, None, fn=S.follow(held, (-0.6, -3.4, 1.5), lens=26, look_offset=(-0.6, 3.2, -0.6)), shake=S.shake(0.3))
# 16b DETAIL de draden en de schroevendraaier
S.cam(t_b, ((BOX.x + 0.8, BOX.y - 0.1, BOX.z + 0.3), BOX + V(0.0, -0.12, -0.04), 46), ((BOX.x + 0.74, BOX.y - 0.09, BOX.z + 0.27), BOX + V(0.0, -0.12, -0.04), 50))
# 16c WIDE de straat kijkt, vanaf de overkant
S.cam(t_c, ((8.6, -3.2, 2.6), (8.0, 6.0, 3.0), 22), ((8.6, -2.9, 2.6), (8.0, 6.0, 3.2), 22))
# 16d CLOSE de jongen bij de schakelaar
HH = S.headpos(held, t_d + 1.0)
S.cam(t_d, (HH + V(2.1, -0.55, 0.0), HH + V(0.2, 0.1, -0.15), 36), (HH + V(1.95, -0.5, 0.0), HH + V(0.2, 0.1, -0.15), 38))
# 16e LOW WIDE trage push: van laag tussen de mensen omhoog naar de lantaarn
S.cam(t_e, ((5.2, 7.7, 0.8), (8.2, 2.6, 2.0), 20), ((5.35, 7.5, 0.9), (8.2, 2.8, 2.6), 20))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 30", 14, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.04)
S.ambience("sfx_menigte_mompel", t_c, t_e + 1.4, vol=0.05)
S.sfx("sfx_menigte_juicht", T_YAY - 0.1, 0.16)
S.sfx("sfx_fluitje", T_YAY + 0.3, 0.12)
S.music("strijkers_warm", t_e + 1.3, END, vol=0.2, fade_in=0.5, fade_out=0.6)
S.say("N16-02", at=t_e + 1.9)
S.finish(length=END, tail=0.0)
