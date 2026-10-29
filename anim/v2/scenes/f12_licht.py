"""F12 · Dag 8, 9, 10 · 1.000.000.000x · de bevroren verjaardagskeuken om 08:59:59.9999. Hij ziet licht bewegen:
een golf van licht kruipt van de kaarsvlammen over de tafel naar het gezicht van zijn broertje (0,3 m/s voor hem).
Iedereen van wie hij houdt staat in deze keuken. Hij legt de laatste kraanvogel naast de taart. Zwart: 'So... can you
stay awake?', de HUD tikt door: AWAKE 20:00:01.

    blender -b -P anim/v2/scenes/f12_licht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402
from feest import party_set  # noqa: E402

S = Scene2("f12", "keuken", "verjaardag")
rnd = random.Random(12)

TX, TY, TZ = 0.2, -0.6, 0.76
SEAT = S.obj("Stoel_2").location.copy()
BRO_SEAT = S.obj("Stoel_4").location.copy()
CAKE = V(0.5, -0.6, TZ)
FLAME = CAKE + V(0, 0, 0.326)
WB = V(2.04, 1.362, 0.78)
GATE = V(-0.2, 8.4, 0)
ROBE = (0.86, 0.62, 0.76)
LIGHT = 0.3                                      # m/s: licht op een miljard keer zijn snelheid

O = party_set(S, ring=True)
cake, plates, lighter, gift = O["cake"], O["plates"], O["lighter"], O["gift"]
cake.location = CAKE
S.obj("Glas_water").location = (TX - 0.25, TY - 0.3, TZ)        # uit het shot van de laatste kraanvogel
ring = sorted([o for o in bpy.data.objects if o.name.startswith("Kraanvogel_tafelrand_")], key=lambda o: o.name)
last = S.obj("Kraanvogel_de_laatste")
LAST_AT = V(0.5, -0.88, TZ)                      # vlak naast de taart, aan zijn kant: het gat in de kring
last.location = LAST_AT
last.rotation_euler = (0, 0, math.radians(180))
for o in bpy.data.objects:
    if o.name.startswith("Kraanvogel_tafelrand_") and (o.location.xy - LAST_AT.xy).length < 0.15:
        o.hide_render = True
        o.hide_viewport = True
ring = [o for o in ring if not o.hide_render]

# ---------------------------------------------------------------- tijdlijn
l1 = S.say("F12-01", gap=0.6)
d1 = l1[1] - l1[0]
D8, D9, D10 = 0.0, l1[0] + 0.16 * d1, l1[0] + 0.33 * d1
l2 = S.say("F12-02", gap=0.8)
d2 = l2[1] - l2[0]
MOVING = l2[0] + 0.62 * d2                       # 'Light. Moving.'
l3 = S.say("F12-03", gap=0.6)
d3 = l3[1] - l3[0]
l4 = S.say("F12-04", gap=0.8)
d4 = l4[1] - l4[0]
MOM_T, DAD_T, BRO_T = l4[0] + 0.24 * d4, l4[0] + 0.45 * d4, l4[0] + 0.7 * d4
l5 = S.say("F12-05", gap=0.8)
l6 = S.say("F12-06", gap=0.8)
d6 = l6[1] - l6[0]
l7 = S.say("F12-07", gap=0.8)
PLACE0, PLACE1 = l7[0] - 0.6, l7[0] + 1.8
l8 = S.say("F12-08", gap=1.0)
BLACK = l8[1] + 0.25
END = BLACK + 3.2

DAY10_WAKE = 8 * 3600 + 59 * 60 + 59.9999


def awake10(t):
    """Zijn uren op dag 10: precies 20:00:01 een seconde nadat het zwart wordt."""
    return 20.0 + (t - BLACK - 1.0) / 3600


S.hud2(8, "10,000,000x", clock="TUE 08:59:59.990", t0=D8 + 0.3, t1=D9)
S.hud2(9, "100,000,000x", clock="TUE 08:59:59.9990", t0=D9, t1=D10)
S.hud2(10, "1,000,000,000x", clock=lambda t: hms(DAY10_WAKE + awake10(t) * 3600 / 1e9, 5, "TUE"), t0=D10,
       awake=lambda t: awake(awake10(t), rate=0, secs=True)(t), awake_t0=D10 + 0.1)
S.gauge2("1 SECOND = 32 YEARS", l1[0] + 0.62 * d1, l1[1] + 0.3, color=GOLD, row=0)
S.real(l3[0], l3[1])
S.gauge2("LIGHT: 300,000 km/s", l3[0] + 0.3, l3[1], color=GOLD, row=0)
S.gauge2("FOR YOU: 0.3 m/s", l3[0] + 0.3 * d3, l3[1], color=GOLD, row=1)
S.gauge2("CRANES: 999", l7[0] - 0.4, PLACE1, color=GOLD, row=0)
S.gauge2("CRANES: 1,000", PLACE1, BLACK, color=GOLD, row=0)
S.card("", BLACK, END + 0.5, dim=1.0, fin=3, fout=1)
S.music("strijk_noot", 0.0, l8[0] - 0.3, vol=0.12, fade_in=2.0, fade_out=0.2)
S.sfx("sfx_klok_motief", D10 + 0.2, 0.12)
S.sfx("sfx_klok_motief", l5[0] + 2.5, 0.1)
for k in range(int((END - BLACK) / 1.0) + 1):     # alleen de HUD tikt nog
    S.sfx("sfx_klok_tik", BLACK + 0.9 + k * 1.0, 0.25, cut=(0, 0.35))

# ---------------------------------------------------------------- de kring kraanvogels (dag 8 half, dag 9 rond) en de laatste
for i, o in enumerate(ring):
    show(o, 0.0 if i % 2 == 0 else D9)
show(last, PLACE0)

# ---------------------------------------------------------------- iedereen, bevroren zoals op dag 7
held = S.actor("hoofdpersonage", SEAT, 180)
SIT_H, zh = sit(held)
bro = S.actor("broertje_dino", BRO_SEAT, 0)
SIT_B, zb = sit(bro)
MF = V(1.35, 0.72, 0)
mama = S.actor("mama", MF, heading(MF, SEAT), outfit=dict(shirt=ROBE, broek=ROBE))
P2 = V(-0.39, -0.62, 0)
papa = S.actor("papa", P2, 93)
opa = S.actor("opa", V(-2.0, 1.2, 0), heading(V(-2.05, 1.22, 0), CAKE) - 4)
OMA = V(-2.36, 0.77, 0)
oma = S.actor("oma", OMA, heading(V(-2.4, 0.78, 0), CAKE))
friend = S.actor("beste_vriend", GATE, 0)
for ch in (held, bro, mama, papa, opa, oma, friend):
    S.reach(ch, 0.0, "L", None, 0.0)
    S.reach(ch, 0.0, "R", None, 0.0)

S.place(bro, 0.0, BRO_SEAT + V(0, -0.06, zb), 0)
S.beat(bro, 0.0, **SIT_B, pose="ontspannen", face="blij", face_amt=0.8, at=CAKE + V(0, 0, 0.3),
       body={"spine": (16, 0, 0), "head": (6, 0, 0)}, mouth=0.0, mond_O=0.35)
S.reach(bro, 0.0, "L", CAKE + V(-0.3, 0.3, 0.02))
S.reach(bro, 0.0, "R", CAKE + V(0.0, 0.32, 0.02))
S.beat(mama, 0.0, "staan", face="verdrietig", face_amt=0.9, at=S.head(held, 0) + V(0, 0, 0.1))
S.reach(mama, 0.0, "L", MF + V(-0.12, -0.18, 1.18))
S.reach(mama, 0.0, "R", MF + V(-0.08, -0.32, 1.05))
marker = T.cyl("Stift_mama", (0, 0, 0), 0.012, 0.13, S.mat("stift_rood", (0.85, 0.12, 0.1)), rot=(90, 0, 0), seg=10, ol=0)
grab(S, marker, mama, 0.0, "hand.R", mode="loc", offset=(0, 0.02, 0))
PL = P2 + V(0.32, 0.0, 0.95)
S.beat(papa, 0.0, "staan", face="lach", face_amt=1.0, at=S.head(held, 0) + V(0, 0, 0.2), mouth=0.6,
       body={"spine": (-6, 0, 0), "head": (-10, 0, 4)})
S.reach(papa, 0.0, "L", PL + V(0.0, 0.12, -0.02))
S.reach(papa, 0.0, "R", PL + V(0.0, -0.12, -0.02))
plates.location = PL + V(0, 0, -0.05)
lighter.location = CAKE + V(0.32, 0.22, 0.02)
lighter.rotation_euler = (0, 0, math.radians(150))
OG = V(-2.4, 0.78, 0) + V(0.28, -0.08, 0.85)
S.beat(oma, 0.0, "staan", face="blij", face_amt=0.8, at=S.head(held, 0))
S.reach(oma, 0.0, "L", OG + V(0.0, 0.17, 0.05))
S.reach(oma, 0.0, "R", OG + V(0.08, -0.17, 0.05))
gift.location = OG + V(0.04, -0.01, -0.04)
gift.rotation_euler = (0, 0, math.radians(heading(V(-2.4, 0.78, 0), CAKE)))
TALK = arms(arm("R", (0.35, 0.55, -0.55), (0.1, 0.75, 0.65)))
S.beat(opa, 0.0, "staan", face="lach", face_amt=0.8, at=S.head(held, 0) + V(0, 0, 0.3), mouth=0.7, arms=TALK)
run_pose(S, friend, 0.0, front="L", look=(0, 0))
phone = T.box("Telefoon_vriend", (0, 0, 0), (0.035, 0.008, 0.07), S.mat("telefoon_zwart", (0.08, 0.08, 0.1)), bevel=0.004, ol=0)
grab(S, phone, friend, 0.0, "hand.R", loc=(0.0, 0.07, 0.02), rot=(90, 0, 180))
for ch in (bro, mama, papa, opa, oma):
    S.hold(ch, END)
run_pose(S, friend, END, front="L", look=(0, 0))

# de traan (zelfde plek als in F11)
bpy.context.scene.frame_set(F(0.5))
dg = bpy.context.evaluated_depsgraph_get()
MH = S.headpos(mama, 0.5)
pos, fwd, left = S.frame_of(mama, 0.5)
hit, loc, nrm, _, ob, _ = bpy.context.scene.ray_cast(dg, MH + fwd * 1.0 + left * 0.11 + V(0, 0, -0.06), -fwd)
tear_at = loc + nrm * 0.006 if hit else MH + fwd * 0.3 + left * 0.11 + V(0, 0, -0.06)
T.sphere("Traan_mama", tear_at, 0.011, HU.water("traan"), scale=(1, 1, 1.5), seg=12, ol=0)

# ---------------------------------------------------------------- hij
A8 = V(1.05, -1.05, 0)
crane_hand = HU.kraanvogel("Kraanvogel_dag8", (0, 0, 0), 3, rot=(0, 0, 0))
S.place(held, 0.0, A8, heading(A8, CAKE))
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=CAKE + V(0.15, -0.2, 0.0), body={"spine": (14, 0, 0)})
S.reach(held, 0.0, "R", CAKE + V(0.25, -0.32, 0.06))
grab(S, crane_hand, held, 0.0, "hand.R", mode="loc", offset=(0, 0, -0.04), release=D9)
show(crane_hand, 0.0, D9)
S.reach(held, D9 - 1.0 / FPS, "R", CAKE + V(0.25, -0.32, 0.06))
S.reach(held, D9, "R", None, 0.0)
S.teleport(held, D9, SEAT + V(0, 0, zh), 180)
CHIN = arms(arm("L", (0.2, 0.7, -0.5), (-0.3, 0.55, 0.75)), arm("R", (0.2, 0.7, -0.5), (-0.3, 0.55, 0.75)))
S.beat(held, D9, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.4, at=CAKE + V(0, 0, 0.1), arms=CHIN)
S.beat(held, D10, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=FLAME)
S.beat(held, l2[0] + 1.0, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.7, at=FLAME)
S.beat(held, MOVING, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=1.0, at=FLAME + V(0, 0.15, -0.1))
S.beat(held, l3[0] + 0.6 * d3, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.8, at=S.head(bro, 0))
S.beat(held, l4[0] + 0.5, **SIT_H, pose="ontspannen", face="blij", face_amt=0.4, at=S.head(mama, 0))
S.beat(held, DAD_T, **SIT_H, pose="ontspannen", face="blij", face_amt=0.5, at=S.head(papa, 0))
S.beat(held, BRO_T, **SIT_H, pose="ontspannen", face="blij", face_amt=0.6, at=S.head(bro, 0))
S.beat(held, l5[0] + 0.5, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.4, at=FLAME)
S.beat(held, l5[1] - 1.5, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=FLAME + V(0, 0, 0.1))
S.beat(held, l6[0] + 0.55 * d6, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.7, at=FLAME + V(0, 0, -0.1), body={"head": (8, 0, 0)})
for k, tb in enumerate((l6[0] + 0.62 * d6, l6[0] + 0.85 * d6, l6[1] + 0.3)):   # zware oogleden
    S.eyes_closed(held, tb, tb + 0.35 + 0.15 * k)
# de laatste kraanvogel
S.reach(held, PLACE0 - 0.3, "R", None, 0.0)
S.reach(held, PLACE0, "R", SEAT + V(0.12, 0.3, 0.72))
S.reach(held, PLACE1 - 0.4, "R", LAST_AT + V(0.02, -0.08, 0.07))
S.reach(held, PLACE1 + 0.5, "R", LAST_AT + V(0.04, -0.14, 0.12))
S.reach(held, PLACE1 + 1.2, "R", None, 0.0)
grab(S, last, held, PLACE0, "hand.R", mode="loc", offset=(0, 0, -0.05), release=PLACE1)
S.beat(held, PLACE0, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=LAST_AT)
S.beat(held, PLACE1 + 0.6, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.6, at=FLAME)
S.beat(held, l8[0] - 0.3, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.3, at=FLAME, body={"head": (10, 0, 0)})
S.eyes_closed(held, l8[1] - 0.2, END + 1)
S.hold(held, END)

# ---------------------------------------------------------------- de lichtgolf: bolschillen vanuit de vlammen, 0,3 m/s
wave = bpy.data.materials.new("lichtgolf")
wave.use_nodes = True
N, L = wave.node_tree.nodes, wave.node_tree.links
N.clear()
out = N.new("ShaderNodeOutputMaterial")
em = N.new("ShaderNodeEmission")
em.inputs["Color"].default_value = (1.0, 0.72, 0.38, 1)
em.inputs["Strength"].default_value = 2.2
tr = N.new("ShaderNodeBsdfTransparent")
lw = N.new("ShaderNodeLayerWeight")
lw.inputs["Blend"].default_value = 0.12
mx = N.new("ShaderNodeMixShader")
pw = N.new("ShaderNodeMath")
pw.operation = "POWER"
pw.inputs[1].default_value = 2.0
L.new(lw.outputs["Facing"], pw.inputs[0])
L.new(pw.outputs[0], mx.inputs[0])
L.new(tr.outputs[0], mx.inputs[1])
L.new(em.outputs[0], mx.inputs[2])
L.new(mx.outputs[0], out.inputs["Surface"])
wave.surface_render_method = "BLENDED"
wave.diffuse_color = (1.0, 0.72, 0.38, 0.1)
W_T = [MOVING - 1.2 + 1.5 * k for k in range(int((l4[0] - MOVING + 1.2) / 1.5) + 1)]
for k, w0 in enumerate(W_T):
    life = 1.6 / LIGHT
    shell = T.sphere(f"Lichtgolf_{k}", (0, 0, 0), 1.0, wave, seg=48, ol=0)
    shell.location = FLAME
    show(shell, w0, w0 + life)
    key(shell, w0, scale=0.002)
    key(shell, w0 + life, scale=LIGHT * life)
    for fc in A._fcurves(shell):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
# zacht warm licht op zijn gezicht als de golf hem bereikt
pl = bpy.data.lights.new("Lichtgolf_gezicht", "POINT")
pl.color = (1.0, 0.7, 0.4)
pl.shadow_soft_size = 0.3
plo = bpy.data.objects.new("Lichtgolf_gezicht", pl)
plo.location = FLAME + V(0, -0.2, 0.05)
T._link(plo)
for t, e in ((0.0, 0.0), (MOVING - 1.2, 0.0), (MOVING - 1.2 + 0.7 / LIGHT, 6.0), (l4[0], 6.0)):
    pl.energy = e
    pl.keyframe_insert("energy", frame=F(t))

# ---------------------------------------------------------------- camera
S.wall(0.0, END + 1)
S.cam(0.0, ((1.95, -0.55, 1.45), (0.85, -0.95, 1.05), 28), ((1.92, -0.58, 1.43), (0.85, -0.95, 1.05), 30))
S.cam(D9, ((2.25, -1.95, 2.3), CAKE + V(0, -0.1, 0.1), 26), ((2.2, -1.9, 2.28), CAKE + V(0, -0.1, 0.1), 27))
S.cam(D10, ((-2.2, -1.95, 2.4), (0.4, -0.1, 0.8), 21), ((-2.1, -1.85, 2.3), (0.45, -0.2, 0.85), 23))
HD = S.bone_world(held, "head", l2[0] + 0.5, tail=False) + V(0, 0, 0.18)
S.cam(l2[0] - 0.3, ((0.9, -0.3, 1.4), HD, 26), ((0.88, -0.34, 1.38), HD, 30), dof=1.0)
S.cam(MOVING - 0.6, (FLAME + V(0.55, -0.15, 0.06), FLAME + V(0, 0, -0.05), 32), (FLAME + V(0.5, -0.12, 0.04), FLAME + V(0, 0, -0.05), 36), dof=0.6)
# de golf over de tafel naar het broertje
BH = S.headpos(bro, 0.5)
S.cam(l3[0] - 0.2, ((1.35, -0.75, 0.95), (0.45, -0.2, 0.95), 28), ((1.3, -0.7, 0.95), (0.45, -0.15, 1.0), 30))
S.cam(l3[0] + 0.42 * d3, ((1.75, -0.95, 1.3), BH + V(0, 0, -0.15), 24), ((1.7, -0.92, 1.3), BH + V(0, 0, -0.15), 27), dof=1.2)
S.cam(l3[0] + 0.72 * d3, ((-0.2, -1.4, 1.35), (0.6, -0.3, 1.0), 26), ((-0.15, -1.35, 1.35), (0.6, -0.25, 1.0), 28))
# iedereen van wie hij houdt
S.cam(l4[0] - 0.3, ((-2.2, -1.95, 2.4), (0.4, -0.1, 0.8), 21), ((-2.15, -1.9, 2.38), (0.4, -0.1, 0.8), 22))
MH2 = S.headpos(mama, 0.5)
S.cam(MOM_T - 0.2, ((2.2, -0.95, 1.75), MH2 + V(0, 0, -0.25), 30), ((2.15, -0.85, 1.75), MH2 + V(0, 0, -0.2), 34))
PH = S.headpos(papa, 0.5)
S.cam(DAD_T - 0.2, ((1.05, -0.5, 1.6), PH + V(0, 0, -0.1), 34), ((1.0, -0.5, 1.6), PH + V(0, 0, -0.1), 37), dof=1.2)
S.cam(BRO_T - 0.2, ((0.95, -0.75, 1.05), BH + V(0, 0, -0.18), 32), ((0.92, -0.7, 1.05), BH + V(0, 0, -0.18), 36), dof=1.0)
# hij: te laat, te vroeg, zo moe
HD5 = S.bone_world(held, "head", l5[0] + 1.0, tail=False) + V(0, 0, 0.18)
S.cam(l5[0] - 0.3, ((0.9, -0.28, 1.42), HD5, 22), ((0.85, -0.4, 1.4), HD5, 30), dof=1.0)
S.cam(l6[0] - 0.3, ((-0.3, -0.5, 1.3), HD5, 28), ((-0.2, -0.6, 1.3), HD5, 34), dof=1.0)
S.cam(PLACE0 - 0.2, ((0.98, -0.52, 1.22), LAST_AT + V(0.0, -0.05, 0.05), 34), ((0.95, -0.54, 1.2), LAST_AT + V(0.0, -0.05, 0.04), 40), dof=0.6)
HD8 = S.bone_world(held, "head", l8[0], tail=False) + V(0, 0, 0.16)
S.cam(l8[0] - 0.6, ((0.88, -0.5, 1.12), HD8 + V(0, 0, -0.08), 28), ((0.84, -0.56, 1.12), HD8 + V(0, 0, -0.08), 34), dof=0.8)

S.finish(length=END)
