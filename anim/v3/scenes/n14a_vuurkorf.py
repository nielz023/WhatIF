"""N14a · Dag 9: de eerste regel (script scène 14a-14j). Straat 's nachts, de hele straat in een kring rond een vuurkorf.
14a  WIDE trage crane omlaag: de kring, handen wrijven, vonken stijgen op.
14b  MEDIUM: opa staat er weer rechtop bij, tikt de jongen op zijn schouder en knikt.
14c  MEDIUM push-in: de wetenschapper op een kratje. "Nobody is coming to save us..." (twee shots: hij, dan de luisterende kring)
14d  CLOSE: de buurman, armen over elkaar. "And who decides those rules? You?"
14e  WIDE: stilte, iedereen kijkt naar elkaar.
14f  MEDIUM push-in: oma staat op uit haar tuinstoel. "Rule number one. Nobody in this street goes hungry."
14g  WIDE trage pull-back: één hand, nog één, dan de hele straat. RULES: 0 -> 1. Strijkers.
14h  CLOSE: de jongen kijkt naar oma. VO (echt gebeurd: Tonga, 1965)
14i  stijlbreuk: zes silhouetten rond een vuurtje op een eiland in de schemering (drie shots).
14j  CLOSE: terug bij de jongen. VO "Humans don't need someone to give them rules..."
14k  WIDE drone omhoog: het ene vuurtje in de donkere stad, verderop andere vuren. VO "But other streets were making rules too..."

    blender -b -P anim/v3/scenes/n14a_vuurkorf.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n14a", "straat", "nr_vuurkorf", exposure=0.15, night=True)
sh = S.cuts([4.0, 3.5, 4.6, 4.8, 3.3, 3.0, 5.6, 4.6, 4.4, 4.2, 5.0, 4.6, 4.8, 4.8])
END = sh[-1][1]
t_b, t_c, t_c2, t_d, t_e, t_f, t_g, t_h, t_i1, t_i2, t_i3, t_j, t_k = [s[0] for s in sh[1:]]
rnd = random.Random(14)

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

FIRE = V(-1.0, 1.0, 0)


def ring(a, r):
    return FIRE + V(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0)


def face_to(p, q):
    d = q - p
    return math.degrees(math.atan2(d.x, -d.y))


def local(p, rot, lx, ly, lz=0.0):
    """Punt in het lokale assenstelsel van een figuur (kijkt naar -y, +x is zijn linkerkant)."""
    return p + (Matrix.Rotation(math.radians(rot), 3, "Z") @ V(lx, ly, lz))


# ---------------------------------------------------------------- de kring
RING = [  # naam, hoek, straal
    ("hoofdpersonage_kind", 155, 2.7), ("opa", 141, 2.95), ("oma", 118, 3.3), ("broertje", 100, 2.6),
    ("mama", 80, 3.0), ("papa", 63, 3.2), ("buurman", 32, 3.2), ("figurant_d", 8, 3.4),
    ("figurant_e", -37, 3.3), ("agent", -60, 3.0), ("kind_a", -78, 2.5), ("figurant_a", -97, 3.2),
    ("kind_b", -112, 2.5), ("figurant_b", -128, 3.3), ("figurant_c", -155, 3.3), ("beste_vriend", 176, 2.8),
]
POS, ROT, C = {}, {}, {}
for n, a, r in RING:
    p = ring(a, r)
    POS[n], ROT[n] = p, face_to(p, FIRE)
    kw = dict(drop=("agent_pet",)) if n == "agent" else {}
    C[n] = S.actor(n, p, ROT[n], **kw)
no_phone(C["beste_vriend"])
held, opa, oma, broer = C["hoofdpersonage_kind"], C["opa"], C["oma"], C["broertje"]
buur, vr = C["buurman"], C["beste_vriend"]
# de wetenschapper op het kratje (in de kring, aan de oostkant)
WET_AT = V(2.2, 0.2, 0.32)
wet = S.actor("wetenschapper", WET_AT, face_to(WET_AT, FIRE))
male_scientist(S, wet)
for o in list(bpy.data.objects):
    if o.name.startswith("wetenschapper_klembord"):
        o.hide_render = o.hide_viewport = True
POS["wetenschapper"], ROT["wetenschapper"], C["wetenschapper"] = WET_AT, face_to(WET_AT, FIRE), wet
ALL = list(C.values())

# ---------------------------------------------------------------- oma's tuinstoel (ze zit tot 14f)
OP, OR = POS["oma"], ROT["oma"]
CH = S.mat("tuinstoel_groen", (0.25, 0.42, 0.30))
chair = []
chair.append(T.box("Tuinstoel_zitting", tuple(local(OP, OR, 0, 0.02, 0.38)), (0.52, 0.48, 0.05), CH, rot=(0, 0, OR), base=False, bevel=0.01, ol=0.004))
chair.append(T.box("Tuinstoel_rug", tuple(local(OP, OR, 0, 0.26, 0.72)), (0.52, 0.05, 0.62), CH, rot=(-8, 0, OR), base=False, bevel=0.01, ol=0.004))
for sx in (-1, 1):
    chair.append(T.box(f"Tuinstoel_leuning_{sx}", tuple(local(OP, OR, sx * 0.28, 0.02, 0.62)), (0.05, 0.46, 0.04), CH, rot=(0, 0, OR), base=False, bevel=0.01, ol=0.004))
    for sy in (-1, 1):
        chair.append(T.box(f"Tuinstoel_poot_{sx}_{sy}", tuple(local(OP, OR, sx * 0.25, sy * 0.21 + 0.02, 0.0)), (0.04, 0.04, 0.62), CH,
                           rot=(0, 0, OR), bevel=0.005, ol=0.003))
spec_sit, z_sit = sit(oma, seat_top=0.405, lean=-6)
S.place(oma, 0.0, OP + V(0, 0, z_sit), OR)
ARMREST = {s: local(OP, OR, (0.28 if s == "L" else -0.28), 0.0, 0.66) for s in ("L", "R")}

# ---------------------------------------------------------------- vuur: flakkerende vlammen, gloed en vonken
flames = [o for o in bpy.data.objects if o.name.startswith("Vuurkorf_vlam")]
glow = next((o for o in bpy.data.objects if o.name.startswith("Vuurkorf_gloed")), None)
for f in range(F(0.0), F(t_i1) + 2, 2):
    t = (f - 1) / FPS
    for k, o in enumerate(flames):
        s = 1.0 + 0.25 * math.sin(t * 9.0 + k * 1.7) + 0.15 * math.sin(t * 23.0 + k)
        o.scale = (1.0, 1.0, s)
        o.keyframe_insert("scale", frame=f)
    if glow:
        glow.data.energy = 900 * (1.0 + 0.18 * math.sin(t * 11.0) + 0.1 * math.sin(t * 29.0))
        glow.data.keyframe_insert("energy", frame=f)
SPARK = S.mat("vonk", (1.0, 0.55, 0.15), 18.0)
for k in range(16):
    sp = T.sphere(f"Vonk_{k}", (0, 0, 0), 0.012, SPARK, seg=6, ol=0)
    ph, spd, a0 = rnd.uniform(0, 3), rnd.uniform(0.6, 1.1), rnd.uniform(0, 6.3)
    for f in range(F(0.0), F(t_i1) + 2, 2):
        t = (f - 1) / FPS
        u = ((t * spd + ph) % 3.0) / 3.0
        r = 0.15 + 0.5 * u
        sp.location = FIRE + V(r * math.cos(a0 + 2 * u), r * math.sin(a0 + 2 * u), 1.0 + 3.0 * u)
        sp.scale = (1 - u,) * 3
        sp.keyframe_insert("location", frame=f)
        sp.keyframe_insert("scale", frame=f)

# ---------------------------------------------------------------- acteren: iedereen kijkt naar het vuur, wrijft in de handen, fluistert
FH = FIRE + V(0, 0, 0.9)
for n, ch in C.items():
    if ch is oma:
        S.beat(oma, 0.0, **spec_sit, face="neutraal", face_amt=0.5, at=FH)
        continue
    S.beat(ch, 0.0, "staan", face="neutraal", face_amt=0.5, at=FH + V(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0))
RUB = ["mama", "figurant_a", "figurant_c", "agent", "papa", "figurant_e"]
for n in RUB:
    ch, p, r = C[n], POS[n], ROT[n]
    hz = S.headpos(ch, 0.0).z - 0.75 * (S.headpos(ch, 0.0).z - p.z) / 1.0 * 0.6
    for i, t in enumerate(frange(0.0, t_b + 0.01, 0.22)):
        w = 0.035 * (1 if i % 2 else -1)
        S.reach(ch, t, "L", local(p, r, 0.02 + w, -0.28, 0) + V(0, 0, hz))
        S.reach(ch, t, "R", local(p, r, -0.02 + w, -0.28, 0) + V(0, 0, hz))
    S.reach(ch, t_b + 0.5, "L", inf=0.0)
    S.reach(ch, t_b + 0.5, "R", inf=0.0)
# fluisteren: twee figuranten kijken naar elkaar
S.beat(C["figurant_a"], 0.6, "staan", face="nerveus", face_amt=0.5, at=S.headpos(C["kind_b"], 0.0))
S.beat(C["figurant_b"], 0.9, "staan", face="twijfel", face_amt=0.5, at=S.headpos(C["figurant_a"], 0.0))
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.4, at=FH)

# 14b: opa staat rechtop, tikt de jongen op zijn schouder en knikt
S.beat(opa, t_b, "staan", face="blij", face_amt=0.5, at=S.headpos(held, 0.0), feet="keep")
SH = S.bone_world(held, "upper_arm.L", t_b + 0.6, tail=False) + V(0, 0, 0.05)   # de schouder aan opa's kant
S.reach(opa, t_b + 0.3, "R", inf=0.0)
for t, dz in ((t_b + 0.8, 0.06), (t_b + 1.0, 0.0), (t_b + 1.2, 0.05), (t_b + 1.4, 0.0), (t_b + 2.2, 0.0)):
    S.reach(opa, t, "R", SH + V(0, 0, dz))
S.reach(opa, t_b + 2.7, "R", inf=0.0)
A.bone_rot(opa, F(t_b + 1.6), "head", (0, 0, 0))
A.bone_rot(opa, F(t_b + 1.85), "head", (12, 0, 0))
A.bone_rot(opa, F(t_b + 2.15), "head", (0, 0, 0))
S.beat(held, t_b + 1.0, "staan", face="blij", face_amt=0.5, at=(S.headpos(opa, t_b) + FH) / 2, feet="keep")

# 14c: de wetenschapper spreekt, iedereen kijkt naar hem
S.beat(wet, 0.0, "staan", face="neutraal", face_amt=0.5, at=FH)
S.beat(wet, t_c, "staan", face="vastberaden", face_amt=0.6, at=S.headpos(oma, 0.0) + V(0, 0, 0.3))
S.beat(wet, t_c + 2.6, "wijzen", amount=0.6, face="vastberaden", face_amt=0.7, at=S.headpos(held, 0.0) + V(0, 0, 0.3))
S.beat(wet, t_c2 + 1.0, "handen_zij", amount=0.7, face="vastberaden", face_amt=0.8, at=S.headpos(C["mama"], 0.0) + V(0, 0, 0.3))
S.beat(wet, t_c2 + 3.0, "staan", face="vastberaden", face_amt=0.9, at=S.headpos(held, 0.0) + V(0, 0, 0.3))
S.say("N14-01", who=wet, at=t_c + 0.3)
WH = S.headpos(wet, t_c)
for n, ch in C.items():
    if ch in (wet,):
        continue
    if ch is oma:
        S.beat(oma, t_c + rnd.uniform(0.0, 0.5), **spec_sit, face="neutraal", face_amt=0.5, at=WH)
    else:
        S.beat(ch, t_c + rnd.uniform(0.0, 0.6), "staan", face="neutraal", face_amt=0.5, at=WH, feet="keep")
S.beat(held, t_c2 + 0.5, "staan", face="vastberaden", face_amt=0.5, at=WH, feet="keep")

# 14d: de buurman, armen over elkaar, sceptisch
S.beat(buur, t_d - 0.4, "armen_over", face="twijfel", face_amt=0.8, at=WH, feet="keep")
S.say("N14-02", who=buur, at=t_d + 0.2)
BH = S.headpos(buur, t_d)
for ch in (C["papa"], C["mama"], C["figurant_d"], wet):
    S.beat(ch, t_d + 0.6, "staan", face="twijfel", face_amt=0.5, at=BH, feet="keep")

# 14e: stilte, iedereen kijkt naar elkaar, niemand stapt naar voren
names = [n for n in C if C[n] not in (oma, wet)]
for i, n in enumerate(names):
    other = C[names[(i + 3) % len(names)]]
    S.beat(C[n], t_e + rnd.uniform(0.0, 0.8), "staan", face=rnd.choice(["twijfel", "nerveus", "neutraal"]), face_amt=0.5,
           at=S.headpos(other, 0.0), feet="keep")
S.beat(oma, t_e, **spec_sit, face="neutraal", face_amt=0.4, at=FH)
S.beat(wet, t_e + 0.3, "staan", face="twijfel", face_amt=0.5, at=FH + V(0, 0, 0.6), feet="keep")
S.beat(oma, t_e + 1.6, **spec_sit, face="vastberaden", face_amt=0.4, at=S.headpos(held, 0.0))

# 14f: oma staat op: handen op de leuningen, voorover, omhoog, vest recht trekken
T_PUSH, T_UP = t_f + 0.3, t_f + 1.1
for s in ("L", "R"):
    S.reach(oma, t_f, s, ARMREST[s] + V(0, 0, 0.02))
    S.reach(oma, T_UP - 0.1, s, ARMREST[s] + V(0, 0, 0.02))
    S.reach(oma, T_UP + 0.35, s, inf=0.0)
lean = dict(spec_sit)
lean["crouch"] = (spec_sit["crouch"][0], 28.0)
S.beat(oma, T_PUSH, **lean, face="inspanning", face_amt=0.4, look=(0.0, -0.3))
S.place(oma, T_PUSH + 0.15, OP + V(0, 0, z_sit), OR)
S.place(oma, T_UP, OP + V(0, 0, 0), OR)
S.beat(oma, T_UP, "staan", face="vastberaden", face_amt=0.6, at=FH + V(0, 0, 0.7))
for t, dz in ((T_UP + 0.4, 0.0), (T_UP + 0.6, -0.06), (T_UP + 0.8, 0.0)):         # trekt haar vest recht
    for s, lx in (("L", 0.12), ("R", -0.12)):
        S.reach(oma, t, s, local(OP, OR, lx, -0.2, 0.75 + dz))
for s in ("L", "R"):
    S.reach(oma, T_UP + 1.1, s, inf=0.0)
S.beat(oma, t_f + 1.6, "staan", face="vastberaden", face_amt=0.8, at=WH)
S.beat(oma, t_f + 3.4, "staan", face="blij", face_amt=0.5, at=S.headpos(C["papa"], 0.0) + V(0, 0, 0.1))
S.say("N14-03", who=oma, at=t_f + 1.3)
OH = S.headpos(oma, t_f + 1.5)
for n, ch in C.items():
    if ch is not oma:
        S.beat(ch, t_f + 0.4 + rnd.uniform(0, 0.5), "staan", face="verbaasd", face_amt=0.4, at=OH, feet="keep")

# 14g: handen omhoog, eerst één, dan nog één, dan iedereen; het broertje springt met twee handen
ORDER = ["papa", "mama", "agent", "figurant_d", "kind_a", "figurant_a", "beste_vriend", "figurant_e", "figurant_b", "kind_b",
         "figurant_c", "hoofdpersonage_kind", "opa", "wetenschapper", "buurman"]
T_HANDS = [t_g + 0.2, t_g + 0.9] + [t_g + 1.4 + 0.12 * k + rnd.uniform(0, 0.15) for k in range(len(ORDER) - 2)]
T_HANDS[-1] = t_g + 3.0                          # de buurman als laatste
for n, t in zip(ORDER, T_HANDS):
    ch = C[n]
    side = "R" if n not in ("mama", "kind_b") else "L"
    S.beat(ch, t, "staan", face="blij", face_amt=0.6, at=OH, feet="keep")
    # hand omhoog vanaf de schouder: schuin naar buiten en iets naar voren, langs het grote hoofd (arm rekt niet)
    sh_ = S.bone_world(ch, f"upper_arm.{side}", t + 0.3, tail=False)
    arm = ((ch.J[f"elbow.{side}"] - ch.J[f"shoulder.{side}"]).length + (ch.J[f"wrist.{side}"] - ch.J[f"elbow.{side}"]).length) * ch.rig.scale.z
    d = local(V(0, 0, 0), ROT[n], (-0.5 if side == "R" else 0.5), -0.25, 0.83).normalized()
    up = sh_ + d * arm * 0.9
    wr = S.bone_world(ch, f"hand.{side}", t - 0.25, tail=False)     # IK eerst aan op de hangende hand, dan omhoog
    S.reach(ch, t - 0.25, side, wr, inf=0.0)
    S.reach(ch, t - 0.1, side, wr)
    S.reach(ch, t + 0.3, side, up)
    S.reach(ch, t_h - 0.05, side, up)
    S.reach(ch, t_h, side, inf=0.0)
S.beat(broer, t_g + 1.2, "juichen", face="lach", face_amt=0.9, at=OH, feet="keep")
for t, dz in ((t_g + 1.5, 0.0), (t_g + 1.75, 0.28), (t_g + 2.0, 0.0), (t_g + 2.3, 0.0), (t_g + 2.55, 0.25), (t_g + 2.8, 0.0)):
    S.place(broer, t, POS["broertje"] + V(0, 0, dz))
S.beat(oma, t_g + 1.0, "staan", face="blij", face_amt=0.8, at=S.headpos(held, 0.0) + V(0, 0, 0.4))

# 14h + 14j: de jongen kijkt naar oma, ogen glanzend
S.beat(held, t_h, "staan", face="blij", face_amt=0.45, at=OH, feet="keep")
A.blink_at(held, F(t_h + 2.6))
S.beat(held, t_j, "staan", face="vastberaden", face_amt=0.3, at=OH + V(0, 0, -0.1), feet="keep")
S.beat(held, t_j + 2.4, "staan", face="blij", face_amt=0.6, at=FH + V(0, 0, 0.5), feet="keep")
for ch in ALL:
    S.hold(ch, END)

# ---------------------------------------------------------------- 14k: andere vuren in de stad (niet allemaal vriendelijk)
for i, (x, y, col) in enumerate(((-70, 60, (1.0, 0.45, 0.1)), (60, -55, (1.0, 0.25, 0.08)), (95, 40, (1.0, 0.5, 0.15)),
                                   (-95, -45, (1.0, 0.2, 0.06)), (30, 95, (1.0, 0.4, 0.1)))):
    T.sphere(f"Ver_vuur_{i}", (x, y, 1.0), 0.8, S.mat(f"ver_vuur_{i}", col, 20.0), scale=(1, 1, 1.6), seg=10, ol=0)
    T.point_light(f"Ver_vuur_licht_{i}", (x, y, 3.0), color=col, energy=6000, radius=1.0)

# ---------------------------------------------------------------- 14i: het eiland (stijlbreuk: silhouetten tegen de schemerlucht)
ISL = V(400.0, 400.0, 0.0)
sky = bpy.data.materials.new("eiland_schemerlucht")
sky.use_nodes = True
nt = sky.node_tree
for n_ in list(nt.nodes):
    nt.nodes.remove(n_)
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
em = nt.nodes.new("ShaderNodeEmission")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tc.outputs["Generated"], sep.inputs[0])
nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
nt.links.new(em.outputs[0], out.inputs[0])
ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (1.0, 0.42, 0.12, 1)
ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.7, (0.10, 0.06, 0.22, 1)
mid = ramp.color_ramp.elements.new(0.25)
mid.color = (0.85, 0.25, 0.30, 1)
em.inputs["Strength"].default_value = 1.6
T.box("Eiland_lucht", tuple(ISL + V(0, 60, -2)), (260, 0.5, 60), sky, base=True, bevel=0, ol=0)
SIL = S.mat("silhouet", (0.015, 0.012, 0.02))
T.plane("Eiland_zee", tuple(ISL + V(0, 20, -0.25)), (400, 120), S.mat("zee_schemer", (0.10, 0.06, 0.14)))
T.box("Eiland_glinster", tuple(ISL + V(-4, 45, -0.24)), (40, 3, 0.01), S.mat("zee_glinster", (1.0, 0.5, 0.2), 1.5), bevel=0, ol=0)
T.sphere("Eiland_heuvel", tuple(ISL + V(0, 6, -2.2)), 9.0, S.mat("eiland_zand", (0.06, 0.04, 0.05)), scale=(1.6, 1.0, 0.3), seg=32, ol=0)
T.sphere("Eiland_rots", tuple(ISL + V(9, 12, -0.6)), 3.0, SIL, scale=(1.2, 1.0, 0.9), seg=16, ol=0)
for k, (dx, dy, h, lean) in enumerate(((-6.0, 7.0, 6.5, 12), (-7.5, 9.0, 5.0, -8), (6.0, 9.5, 5.6, -14))):
    top = ISL + V(dx + lean * 0.08, dy, h)
    T.to_mesh(T.tube(f"Palm_stam_{k}", [ISL + V(dx, dy, 0), ISL + V(dx + lean * 0.03, dy, h * 0.5), top], 0.14, SIL))
    for j in range(7):
        a = 2 * math.pi * j / 7
        T.to_mesh(T.tube(f"Palm_blad_{k}_{j}", [top, top + V(1.4 * math.cos(a), 0.6 * math.sin(a), 0.5), top + V(2.4 * math.cos(a), 1.0 * math.sin(a), -0.6)],
                         0.07, SIL))
camp = ST3.kampvuur("Eiland_vuur", tuple(ISL + V(0, 1.0, 0)), lit=True)
ilights = [o for o in camp.children_recursive if o.type == "LIGHT"]
for o in ilights:
    o.data.energy = 600
pot = T.cyl("Eiland_pot", tuple(ISL + V(0, 1.0, 0.5)), 0.18, 0.22, SIL, seg=14, ol=0)
T.to_mesh(T.tube("Eiland_potstok", [ISL + V(-0.6, 1.0, 0), ISL + V(-0.5, 1.0, 1.0), ISL + V(0, 1.0, 0.95)], 0.02, SIL))


def boy(name, at, rot, sitting=True, scale=1.0):
    """Eenvoudig silhouet van een jongen. Geeft (wortel, arm-scharnier rechts, arm-scharnier links)."""
    root = bpy.data.objects.new(name, None)
    T._link(root)
    parts = []
    hz = 0.82 if sitting else 1.25
    bz0, bz1 = (0.22, 0.62) if sitting else (0.55, 1.05)
    parts.append(T.sphere(name + "_hoofd", (0, 0, hz), 0.15, SIL, seg=14, ol=0))
    parts.append(T.to_mesh(T.tube(name + "_lijf", [(0, 0, bz0), (0, 0, bz1)], 0.15, SIL)))
    if sitting:
        for sx in (-1, 1):
            parts.append(T.to_mesh(T.tube(f"{name}_been{sx}", [(sx * 0.08, 0, 0.22), (sx * 0.1, -0.35, 0.35), (sx * 0.1, -0.45, 0.02)], 0.06, SIL)))
    else:
        for sx in (-1, 1):
            parts.append(T.to_mesh(T.tube(f"{name}_been{sx}", [(sx * 0.08, 0, 0.6), (sx * 0.1, 0, 0.0)], 0.065, SIL)))
    for p_ in parts:
        p_.parent = root
    arms_ = []
    for sx in (-1, 1):
        sh_ = bpy.data.objects.new(f"{name}_schouder{sx}", None)
        T._link(sh_)
        sh_.parent = root
        sh_.location = (sx * 0.17, 0, bz1 - 0.05)
        a_ = T.to_mesh(T.tube(f"{name}_arm{sx}", [(0, 0, 0), (0, 0, -0.42)], 0.05, SIL))
        a_.parent = sh_
        sh_.rotation_mode = "XYZ"
        sh_.rotation_euler = (math.radians(-35), 0, 0)
        arms_.append(sh_)
    root.location = tuple(at)
    root.rotation_euler = (0, 0, math.radians(rot))
    root.scale = (scale,) * 3
    return root, arms_[0], arms_[1]


BOYS = []
for k in range(6):
    a = math.radians(200 + k * 28 - (0 if k < 3 else 0))
    at = ISL + V(0, 1.0, 0) + V(1.25 * math.cos(a) * 1.3, 1.25 * math.sin(a), 0)
    BOYS.append(boy(f"Eilandjongen_{k}", at, face_to(at, ISL + V(0, 1.0, 0)), sitting=(k not in (1, 4)), scale=rnd.uniform(0.9, 1.05)))
# i2: de kok roert in de pot, de vuurwachter legt een tak op het vuur
cook_arm = BOYS[1][1]
for t, ax in ((t_i2, -60), (t_i2 + 0.6, -95), (t_i2 + 1.2, -60), (t_i2 + 1.8, -95), (t_i2 + 2.4, -60), (t_i2 + 3.0, -95), (t_i2 + 3.6, -60)):
    cook_arm.rotation_euler.x = math.radians(ax)
    cook_arm.keyframe_insert("rotation_euler", index=0, frame=F(t))
stick = T.to_mesh(T.tube("Eiland_tak", [(0, 0, 0), (0, -0.6, 0)], 0.025, SIL))
keeper_root, k_arm, _ = BOYS[4]
stick.parent = k_arm
stick.location = (0, 0, -0.42)
for t, ax in ((t_i2 + 0.8, -20), (t_i2 + 1.8, -75), (t_i2 + 2.4, -75), (t_i2 + 3.2, -20)):
    k_arm.rotation_euler.x = math.radians(ax)
    k_arm.keyframe_insert("rotation_euler", index=0, frame=F(t))
visible(stick, 0.0, True)
visible(stick, t_i2 + 2.4, False)
# i3: twee jongens geven elkaar een hand (goedmaken), de anderen leggen een hand op hun schouder
for (root_, ar, al), ax in ((BOYS[0], -80), (BOYS[2], -80)):
    for t, a_ in ((t_i3, -35), (t_i3 + 0.8, ax), (t_i3 + 3.0, ax)):
        ar.rotation_euler.x = math.radians(a_)
        ar.keyframe_insert("rotation_euler", index=0, frame=F(t))
for k, (root_, ar, al) in enumerate(BOYS):
    for t in frange(t_i1, t_j, 0.5):                       # ademen/schommelen
        root_.rotation_euler.y = math.radians(2.0 * math.sin(t * 1.7 + k))
        root_.keyframe_insert("rotation_euler", index=1, frame=F(t))

# ---------------------------------------------------------------- camera's
FC = FIRE + V(0, 0, 1.0)


def close(ch, t, target, dist=1.35, side=0.0, lens=32, push=0.1, dz=-0.05):
    """Close-up van voren: camera in de richting waar hij naar kijkt (tussen zijn blik en het vuur in)."""
    h = S.headpos(ch, t)
    a = target - h
    a.z = 0
    b = FC - h
    b.z = 0
    d = (a.normalized() + 0.5 * b.normalized()).normalized()
    sd = V(d.y, -d.x, 0) * side
    p0 = h + d * dist + sd + V(0, 0, dz)
    p1 = h + d * (dist - push) + sd + V(0, 0, dz)
    return (p0, h + V(0, 0, -0.06), lens), (p1, h + V(0, 0, -0.06), lens + 2)


# 14a WIDE trage crane omlaag over de kring
S.cam(0.0, ((6.5, -7.5, 6.5), FC, 24), ((4.2, -5.2, 2.6), FC + V(0, 0, 0.1), 24))
# 14b MEDIUM opa en de jongen, vanaf het vuur
mid_b = (POS["opa"] + POS["hoofdpersonage_kind"]) / 2 + V(0, 0, 1.15)
cb = FIRE + (mid_b - FIRE).normalized() * 0.6 + V(0.2, 0.35, 0)
cb.z = 1.42
S.cam(t_b, (cb, mid_b, 27), (cb + (mid_b - cb).normalized() * 0.15, mid_b, 28))
# 14c MEDIUM push-in de wetenschapper op zijn kratje (vuur achter de camera)
WH2 = S.headpos(wet, t_c + 1.0)
dw = (WH2 - FC)
dw.z = 0
dw.normalize()
S.cam(t_c, (WH2 - dw * 2.6 + V(0.3, 0, -0.35), WH2 + V(0, 0, -0.15), 30), (WH2 - dw * 1.9 + V(0.25, 0, -0.3), WH2 + V(0, 0, -0.12), 32))
# 14c2 de luisterende kring, over het vuur heen (vanaf achter de wetenschapper)
S.cam(t_c2, ((3.6, -1.4, 3.2), (-2.4, 3.0, 0.9), 30), ((3.5, -1.3, 3.15), (-2.4, 3.0, 0.9), 31))
# 14d CLOSE de buurman
S.cam(t_d, *close(buur, t_d + 0.8, WH, dist=1.45))
# 14e WIDE stilte, laag vanaf de straatkant
S.cam(t_e, ((2.5, -6.4, 1.6), (-1.2, 1.6, 1.0), 22), ((2.45, -6.2, 1.6), (-1.2, 1.6, 1.0), 22), handheld=0.15)
# 14f MEDIUM push-in oma
OH2 = S.headpos(oma, t_f + 2.0)
do = (FC - OH2)
do.z = 0
do.normalize()
S.cam(t_f, (OH2 + do * 2.6 + V(0, 0, -0.35), OH2 + V(0, 0, -0.35), 30), (OH2 + do * 2.0 + V(0, 0, -0.25), OH2 + V(0, 0, -0.15), 32))
# 14g WIDE trage pull-back, hoog
S.cam(t_g, ((3.4, -4.2, 2.6), FC, 24), ((6.2, -7.8, 4.8), FC, 24))
# 14h CLOSE de jongen, vanaf het vuur
AZH = 35.0   # 3/4 van voren aan de kant weg van opa
_c = S.shot(held, t_h + 1.0, "mcu", az=AZH, lens=32)
S.cam(t_h, _c, (_c[0], _c[1], 34))
# 14i1 WIDE het eiland, 14i2 bij het vuurtje, 14i3 twee jongens maken het goed
IC = ISL + V(0, 1.0, 0)
S.cam(t_i1, ((IC.x - 2.0, IC.y - 11.0, 1.4), IC + V(0, 4.0, 1.4), 28), ((IC.x - 1.6, IC.y - 10.0, 1.35), IC + V(0, 4.0, 1.4), 28))
S.cam(t_i2, ((IC.x + 1.2, IC.y - 4.2, 0.9), IC + V(0, 0.4, 0.6), 30), ((IC.x + 1.0, IC.y - 3.7, 0.9), IC + V(0, 0.4, 0.6), 32))
S.cam(t_i3, ((IC.x - 3.2, IC.y - 3.6, 1.0), IC + V(-0.6, 0.0, 0.6), 30), ((IC.x - 3.0, IC.y - 3.3, 1.0), IC + V(-0.6, 0.0, 0.6), 31))
# 14j CLOSE de jongen, iets van opzij
_c = S.shot(held, t_j + 1.0, "mcu", az=AZH, lens=34)
S.cam(t_j, _c, (_c[0], _c[1], 36))
# 14k WIDE drone omhoog: één vuurtje in de donkere stad, verderop andere vuren
S.cam(t_k, ((-8.0, -10.0, 9.0), FC, 26), ((-45.0, -8.0, 42.0), FC + V(4, 0, 0), 26))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 9", [(0.0, 0), (t_g + 1.6, 1)], t0=0.0)
S.no_hud.append((t_i1, t_j))
S.ambience("sfx_vuur", 0.0, t_i1, vol=0.06)
S.ambience("sfx_menigte_mompel", 0.0, t_c, vol=0.04)
S.ambience("sfx_stad_nacht_wind", t_j, END, vol=0.04)
S.music("strijkers_warm", t_g, t_k + 1.0, vol=0.22, fade_in=0.4, fade_out=1.0)
S.music("m_nacht_angst", t_k, END, vol=0.16, fade_in=0.8, fade_out=0.4)
S.sfx("sfx_menigte_juicht", t_g + 1.8, 0.12)
S.say("N14-04", at=t_h + 0.4)
S.say("N14-05", at=t_i1 + 3.9)
S.say("N14-06", at=t_j + 0.5)
S.say("N14-07", at=t_k + 0.2)
S.finish(length=END, tail=0.0)
