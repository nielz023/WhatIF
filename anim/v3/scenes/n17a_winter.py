"""N17a · Dag 100: winter (script scène 17a-17i). Straat onder de sneeuw, slagboom met vuurkorf.
17a  WIDE drone: de straat onder de sneeuw, rook uit de schoorstenen, bij de slagboom brandt een vuurkorf. VO N17-01.
17b  MEDIUM: de agent bij de slagboom wrijft zijn handen, adem dampt, hij stopt en tuurt de sneeuw in.
17c  WIDE trage push: uit de sneeuwstorm komen vier figuren aan, de pestkop en zijn volgelingen, rillend.
17d  MEDIUM: de straat verzamelt zich achter de slagboom, papa zet zich schrap. BUURMAN N17-02.
17e  CLOSE push-in: de pestkop rillend, zonder kroon. N17-03. Zijn zusje komt achter hem vandaan.
17f  CLOSE: de vriend kijkt naar de rode fiets die de pestkop aan de hand meedraagt.
17g  WIDE: stilte, iedereen kijkt naar oma.
17h  MEDIUM push-in: oma loopt naar de slagboom en tilt hem op. OMA N17-04. RULES: 15 licht op.
17i  CLOSE: de pestkop geeft de rode fiets terug, de vriend pakt hem aan en knikt één keer. VO N17-05.

    blender -b -P anim/v3/scenes/n17a_winter.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402
import bmesh  # noqa: E402

S = Scene3("n17a", "straat", "nr_sneeuw", exposure=0.05)
sh = S.cuts([3.5, 3.0, 4.0, 3.5, 5.8, 2.5, 3.0, 6.6, 4.4])
END = sh[-1][1]
t_b, t_c, t_d, t_e, t_f, t_g, t_h, t_i = [s[0] for s in sh[1:]]
rnd = random.Random(17)

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True
# de geparkeerde auto's bij de slagboom staan in de weg van de bende en de buren
for o in list(bpy.data.objects):
    if o.name.startswith(("Auto_geparkeerd_0", "Auto_geparkeerd_1")):
        o.hide_render = o.hide_viewport = True


def face_to(p, q):
    d = q - p
    return math.degrees(math.atan2(d.x, -d.y))


def hide_until(ch, t):
    for c in ch.rig.children_recursive:
        if c.type == "MESH":
            visible(c, 0.0, False)
            visible(c, t, True)


# ---------------------------------------------------------------- vallende sneeuw (schuin door de wind)
SNOW_MAT = S.mat("sneeuwvlok", (0.95, 0.97, 1.0), glow=0.6)


def snowfall(name, lo, hi, n, size=0.022, period=4.0, tilt=18):
    """Twee gestapelde blokken vlokken die in een lus omlaag schuiven (naadloos), schuin gekanteld voor wind."""
    H = hi[2] - lo[2]
    piv = bpy.data.objects.new(name, None)
    S.sc.collection.objects.link(piv)
    piv.location = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2])
    piv.rotation_euler = (0, math.radians(tilt), 0)
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    for k in range(2):
        for _ in range(n):
            c = V(rnd.uniform(lo[0], hi[0]) - piv.location.x, rnd.uniform(lo[1], hi[1]) - piv.location.y, rnd.uniform(0, H) + k * H)
            s = size * rnd.uniform(0.6, 1.4)
            vs = [bm.verts.new(c + V(*d) * s) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
            for a, b, cc in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
                bm.faces.new((vs[a], vs[b], vs[cc]))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(SNOW_MAT)
    ob = bpy.data.objects.new(name + "_vlokken", me)
    S.sc.collection.objects.link(ob)
    ob.parent = piv
    for t, z in ((0.0, 0.0), (period, -H)):
        ob.location = (0, 0, z)
        ob.keyframe_insert("location", index=2, frame=F(t))
    for fc in A._fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.modifiers.new("CYCLES")
    return ob


snowfall("Sneeuwval_slagboom", (-44.0, -5.0, -1.0), (-19.0, 9.0, 7.0), 2600, period=5.0)
snowfall("Sneeuwval_ver", (-70.0, -14.0, -1.0), (-10.0, 14.0, 13.0), 2200, size=0.05, period=6.0, tilt=22)

# rook uit de schoorstenen (een paar trage bollen per schoorsteen)
SMOKE = S.mat("rook_schoorsteen", (0.55, 0.57, 0.62))
for ci, (cx, cy) in enumerate(((-36, 17.0), (-30, 17.0), (-24, 17.0), (-18, 17.0), (-30, -15.0), (-24, -15.0), (-12, 17.0))):
    for k in range(4):
        b = T.sphere(f"Rook_{ci}_{k}", (cx, cy, 10.2), 0.35, SMOKE, seg=10, ol=0)
        ph = k * 1.1
        for t in frange(0.0, END, 0.5):
            u = ((t + ph) % 4.4) / 4.4
            b.location = (cx + 1.6 * u, cy, 10.2 + 3.0 * u)
            s = 0.4 + 1.6 * u if u < 0.92 else 0.0
            b.scale = (s, s, s)
            b.keyframe_insert("location", frame=F(t))
            b.keyframe_insert("scale", frame=F(t))


# ---------------------------------------------------------------- adem die dampt
BREATH = T.glass("adem_damp", (0.95, 0.97, 1.0), alpha=0.35)
_nb = [0]


def puff(ch, t):
    M = S._root_matrix(ch, t)
    fwd = (M.to_3x3() @ V(0, -1, 0)).normalized()
    p0 = S.headpos(ch, t) + fwd * 0.34 + V(0, 0, -0.2)
    _nb[0] += 1
    b = T.sphere(f"Adem_{_nb[0]}", tuple(p0), 0.1, BREATH, seg=10, ol=0)
    for dt, s, d in ((-0.05, 0.0, 0.0), (0.0, 0.1, 0.0), (0.35, 0.45, 0.2), (0.8, 0.7, 0.38), (0.85, 0.0, 0.4)):
        b.scale = (s, s, s * 0.8)
        b.location = p0 + fwd * d + V(0, 0, d * 0.4)
        b.keyframe_insert("scale", frame=F(t + dt))
        b.keyframe_insert("location", frame=F(t + dt))


# ---------------------------------------------------------------- de slagboom en de agent
ARM = S.obj("Slagboom_arm")
ARM.rotation_mode = "XYZ"
T_LIFT0, T_LIFT1 = t_h + 2.4, t_h + 3.6
for t, a in ((0.0, 0), (T_LIFT0, 0), (T_LIFT1, -75)):
    ARM.rotation_euler.y = math.radians(a)
    ARM.keyframe_insert("rotation_euler", index=1, frame=F(t))
for fc in A._fcurves(ARM):
    for kp in fc.keyframe_points:
        kp.interpolation = "BEZIER"
        kp.easing = "EASE_IN_OUT"

AG = V(-28.6, 4.6, 0)
ag = S.actor("agent", AG, -90, drop=("agent_badge",))
S.beat(ag, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0.0, -0.1))
# 17b: handen wrijven voor de borst, adem dampt, dan stopt hij en tuurt
HC = S.headpos(ag, 0.0) + V(-0.32, 0.0, -0.42)
for i, t in enumerate(frange(t_b - 0.4, t_b + 1.6, 0.18)):
    o = 0.05 if i % 2 else -0.05
    S.reach(ag, t, "L", HC + V(0, 0.07 + o, 0))
    S.reach(ag, t, "R", HC + V(0, -0.07 + o, 0))
S.reach(ag, t_b + 1.75, "L", inf=0.0)
S.reach(ag, t_b + 1.75, "R", inf=0.0)
S.reach(ag, 0.0, "L", inf=0.0)
S.reach(ag, 0.0, "R", inf=0.0)
S.reach(ag, t_b - 0.45, "L", inf=0.0)
S.reach(ag, t_b - 0.45, "R", inf=0.0)
S.beat(ag, t_b, "staan", face="neutraal", face_amt=0.6, look=(0.0, -0.2), body={"head": (-8, 0, 0)})
puff(ag, t_b + 0.3)
puff(ag, t_b + 1.2)
S.beat(ag, t_b + 1.9, "staan", face="geschrokken", face_amt=0.5, at=V(-42.0, 2.2, 1.0))
S.beat(ag, t_b + 2.5, "staan", face="nerveus", face_amt=0.7, at=V(-42.0, 2.2, 1.0))
puff(ag, t_b + 2.4)

# ---------------------------------------------------------------- de bende uit de sneeuwstorm (kijkt naar +x)
P_STOP = V(-31.8, 2.6, 0)
GANG = {"pestkop": V(0, 0, 0), "volgeling_a": V(-0.9, 1.0, 0), "volgeling_b": V(-1.1, -1.3, 0), "volgeling_c": V(-1.7, 0.2, 0)}
WALK0 = V(-41.6, 0, 0)          # 17c: van x -41.6 naar -37.9 (de rest gebeurt buiten beeld)
WALK1 = V(-37.9, 0, 0)
gang = {}
for n, off in GANG.items():
    p0 = V(WALK0.x, P_STOP.y, 0) + off
    gang[n] = S.actor(n, p0, 90)
    hide_until(gang[n], t_c)
pest = gang["pestkop"]
zus = S.actor("zusje_pestkop", V(WALK0.x - 0.55, P_STOP.y + 0.05, 0), 90)
hide_until(zus, t_c)
for n, ch in gang.items():
    off = GANG[n]
    a = V(WALK0.x, P_STOP.y, 0) + off
    b = V(WALK1.x, P_STOP.y, 0) + off
    S.walk(ch, t_c - 0.4, t_d, [a, b], stride=0.26, turn=False, arms=0.0)
    S.beat(ch, t_c - 0.4, "armen_over", face="verdrietig", face_amt=0.7, look=(0.0, -0.4), body={"head": (-16, 0, 0)}, feet="keep")
    S.hold(ch, t_d)
    # 17e: op hun plek voor de slagboom
    S.teleport(ch, t_e, P_STOP + off, 90)
    ch.rig.location = tuple(P_STOP + off)
    ch.rig.keyframe_insert("location", frame=F(t_e))
za, zb = V(WALK0.x - 0.55, P_STOP.y + 0.05, 0), V(WALK1.x - 0.55, P_STOP.y + 0.05, 0)
S.walk(zus, t_c - 0.4, t_d, [za, zb], stride=0.2, turn=False, arms=0.0)
S.beat(zus, t_c - 0.4, "armen_over", face="bang", face_amt=0.6, look=(0.0, -0.3), feet="keep")
S.hold(zus, t_d)
Z_HIDE = P_STOP + V(-0.6, 0.05, 0)
Z_OUT = P_STOP + V(-0.3, 0.68, 0)
S.teleport(zus, t_e, Z_HIDE, 90)
zus.rig.location = tuple(Z_HIDE)
zus.rig.keyframe_insert("location", frame=F(t_e))

# ---------------------------------------------------------------- de rode fiets aan de hand van de pestkop
fv = ST3.fiets2("Fiets_vriend_rood", (WALK0.x + 0.4, P_STOP.y - 0.55, 0), rot=90, color=(0.85, 0.12, 0.10), sticker=True)
visible(fv, 0.0, False)
visible(fv, t_c, True)
for c in fv.children_recursive:
    visible(c, 0.0, False)
    visible(c, t_c, True)
bpy.context.view_layer.update()


def grip(b, side):
    return S.obj(b.name + "_stuurdeel").matrix_world @ V(0, 0.24 if side == "L" else -0.24, 0.1)


# ---------------------------------------------------------------- de straat achter de slagboom (kijkt naar -x)
CROWD = {"papa": (-27.7, 2.2), "mama": (-26.9, 3.0), "buurman": (-27.3, 0.2), "oma": (-26.7, 1.1), "opa": (-25.9, 0.4),
         "beste_vriend": (-27.6, 3.7), "hoofdpersonage_kind": (-26.8, 4.1), "wetenschapper": (-25.9, 2.2),
         "broertje": (-26.1, 3.6)}
GC = P_STOP + V(-0.6, 0.1, 0)
C = {}
for n, (x, y) in CROWD.items():
    p = V(x, y, 0)
    C[n] = S.actor(n, p + V(2.2, 0, 0), face_to(p, GC))
    hide_until(C[n], t_d)
male_scientist(S, C["wetenschapper"])
no_phone(C["beste_vriend"])
for i, (n, ch) in enumerate(C.items()):
    p = V(*CROWD[n], 0)
    t0 = t_d + 0.05 + 0.12 * (i % 4)
    S.walk(ch, t0, t0 + 1.3, [p + V(2.2, 0, 0), p], stride=0.4, turn=False)
    S.beat(ch, t0, "staan", face="nerveus", face_amt=0.5, at=S.headpos(pest, t_e) + V(0, 0, -0.1), feet="keep")
    S.hold(ch, t0 + 1.3)
oma, papa, buur, vr = C["oma"], C["papa"], C["buurman"], C["beste_vriend"]
held = C["hoofdpersonage_kind"]
HP = S.headpos(pest, t_e + 0.2)
# 17d: papa zet zich schrap, de buurman wijst
S.beat(papa, t_d + 1.5, "handen_zij", face="vastberaden", face_amt=0.9, at=HP, crouch=(0.06, 8))
S.beat(papa, t_d + 3.0, "handen_zij", face="vastberaden", face_amt=0.9, at=HP, crouch=(0.06, 8))
S.beat(buur, t_d + 1.2, "wijzen", face="boos", face_amt=0.9, at=HP, feet="keep")
S.say("N17-02", who=buur, at=t_d + 1.1)
S.beat(buur, t_d + 3.3, "staan", face="boos", face_amt=0.6, at=HP)
S.beat(ag, t_d + 0.6, "staan", face="vastberaden", face_amt=0.7, at=HP)

# 17e: de pestkop rillend, tanden klapperen, kijkt naar de grond en dan op
S.beat(pest, t_e, "armen_over", face="verdrietig", face_amt=0.8, look=(0.0, -0.6), body={"head": (-20, 0, 0)})
for k, t in enumerate(frange(t_e, t_e + 1.6, 1.0 / 12)):
    A.key_prop(pest.rig, "mond_open", 0.18 if k % 2 else 0.02, F(t))
puff(pest, t_e + 0.2)
S.beat(pest, t_e + 1.0, "armen_over", face="verdrietig", face_amt=0.9, look=(0.0, -0.6), body={"head": (-20, 0, 0)})
S.beat(pest, t_e + 1.7, "armen_over", face="nerveus", face_amt=0.9, at=S.headpos(papa, t_e))
S.say("N17-03", who=pest, at=t_e + 0.45)
puff(pest, t_e + 4.2)
# het zusje komt achter hem vandaan
S.beat(zus, t_e, "staan", face="bang", face_amt=0.6, look=(0.0, -0.2))
S.walk(zus, t_e + 3.4, t_e + 4.3, [Z_HIDE, Z_OUT], stride=0.18, turn=False)
S.beat(zus, t_e + 4.3, "staan", face="bang", face_amt=0.7, at=S.headpos(papa, t_e), feet="keep")
S.reach(zus, t_e + 4.3, "R", S.bone_world(pest, "upper_arm.L", t_e + 4.3, tail=True) + V(0.0, -0.05, -0.12))
S.reach(zus, t_e + 3.9, "R", inf=0.0)
S.reach(zus, 0.0, "R", inf=0.0)
for ch in (pest, zus):
    S.hold(ch, END)
for n in ("volgeling_a", "volgeling_b", "volgeling_c"):
    S.beat(gang[n], t_e, "armen_over", face="verdrietig", face_amt=0.7, look=(0.0, -0.5), body={"head": (-14, 0, 0)})
    S.hold(gang[n], END)

# fiets: in 17c rechts voor de pestkop, daarna staat hij naast hem; in 17i duwt hij hem naar de vriend
P_I = P_STOP + V(0.9, 0, 0)                # 17i: na de slagboom stapt hij een meter naar voren
T_PUSH0, T_PUSH1 = t_i + 0.5, t_i + 1.4
PUSH = V(0.7, 0, 0)
S.walk(pest, t_i - 0.9, t_i + 0.2, [P_STOP, P_I], stride=0.3, turn=False)
WR = 0.33
wv, wa = S.obj(fv.name + "_wiel_v"), S.obj(fv.name + "_wiel_a")
fv.rotation_mode = "XYZ"
prev, roll = None, 0.0
for f in range(F(t_c - 0.4), F(END) + 1):
    t = (f - 1) / FPS
    M = S._root_matrix(pest, t)
    yaw = math.degrees(M.to_euler().z) - 90.0
    loc = M @ V(-0.55, -0.4, 0)
    if t > T_PUSH0:
        u = min(1.0, (t - T_PUSH0) / (T_PUSH1 - T_PUSH0))
        u = u * u * (3 - 2 * u)
        loc = (S._root_matrix(pest, T_PUSH0) @ V(-0.55, -0.4, 0)) + PUSH * u
    if prev is not None and (loc - prev).length < 0.5:
        roll += (loc - prev).length / WR
    prev = loc.copy()
    fv.location = loc
    fv.rotation_euler = (0, 0, math.radians(yaw))
    fv.keyframe_insert("location", frame=f)
    fv.keyframe_insert("rotation_euler", frame=f)
    for w in (wv, wa):
        w.rotation_euler.y = roll
        w.keyframe_insert("rotation_euler", index=1, frame=f)
T_REL = T_PUSH0 + 0.15
for t in frange(t_c - 0.4, T_REL, 0.2):
    S.sc.frame_set(F(t))
    S.reach(pest, t, "L", grip(fv, "L"))
S.sc.frame_set(F(T_REL))
S.reach(pest, T_REL, "L", grip(fv, "L"))
S.reach(pest, T_REL + 0.3, "L", inf=0.0)
S.reach(pest, 0.0, "L", inf=0.0)

# ---------------------------------------------------------------- 17f: de vriend kijkt naar de fiets
BIKE_E = S._root_matrix(pest, t_f) @ V(-0.55, -0.4, 0) + V(0, 0, 0.6)
S.beat(vr, t_f, "staan", face="verdrietig", face_amt=0.6, at=BIKE_E)
A.blink_at(vr, F(t_f + 1.2))
S.beat(vr, t_f + 1.6, "staan", face="twijfel", face_amt=0.7, at=BIKE_E)

# ---------------------------------------------------------------- 17g: stilte, iedereen kijkt naar oma
OMA_H = S.headpos(oma, t_g)
for n, ch in list(C.items()) + [("agent", ag)]:
    if n == "oma":
        continue
    S.beat(ch, t_g + 0.2 + rnd.uniform(0, 0.6), "staan", face="twijfel", face_amt=0.5, at=OMA_H, feet="keep")
S.beat(pest, t_g + 0.6, "armen_over", face="nerveus", face_amt=0.8, at=OMA_H)
S.beat(oma, t_g, "staan", face="neutraal", face_amt=0.6, at=HP)
S.beat(oma, t_g + 1.4, "staan", face="vastberaden", face_amt=0.5, at=HP)
S.beat(oma, t_g + 2.4, "staan", face="blij", face_amt=0.3, at=HP)

# ---------------------------------------------------------------- 17h: oma loopt naar de slagboom en tilt hem op
O0, O1 = V(*CROWD["oma"], 0), V(-29.38, 2.0, 0)
S.walk(oma, t_h + 0.2, t_h + 1.9, [O0, O1], stride=0.32, turn=False)
S.turn(oma, t_h + 1.9, t_h + 2.2, -90)
S.beat(oma, t_h + 0.2, "staan", face="vastberaden", face_amt=0.6, at=HP, feet="keep")
bpy.context.view_layer.update()
S.sc.frame_set(F(t_h))
Minv = ARM.matrix_world.inverted()
GRIP_L = Minv @ V(-30.0, 2.22, 1.1)
GRIP_R = Minv @ V(-30.0, 1.77, 1.1)
S.reach(oma, 0.0, "L", inf=0.0)
S.reach(oma, 0.0, "R", inf=0.0)
S.reach(oma, t_h + 1.7, "L", inf=0.0)
S.reach(oma, t_h + 1.7, "R", inf=0.0)
for t in frange(t_h + 2.1, T_LIFT0 + 0.75, 0.1):
    S.sc.frame_set(F(t))
    S.reach(oma, t, "L", ARM.matrix_world @ GRIP_L)
    S.reach(oma, t, "R", ARM.matrix_world @ GRIP_R)
S.reach(oma, T_LIFT0 + 1.1, "L", inf=0.0)
S.reach(oma, T_LIFT0 + 1.1, "R", inf=0.0)
S.beat(oma, t_h + 2.2, "staan", face="inspanning", face_amt=0.6, look=(0.0, 0.1), feet="keep")
S.beat(oma, T_LIFT1 + 0.1, "staan", face="blij", face_amt=0.6, at=HP, feet="keep")
S.say("N17-04", who=oma, at=t_h + 2.1)
S.sfx("sfx_slagboom", T_LIFT0, 0.5)
S.hold(oma, t_i - 0.6)
# 17i: oma stapt opzij, uit de weg van de fiets
S.walk(oma, t_i - 0.6, t_i + 0.6, [O1, V(-28.9, 0.85, 0)], stride=0.3)
S.beat(oma, t_i + 0.7, "staan", face="blij", face_amt=0.5, at=V(-29.6, 2.1, 0.9), feet="keep")
S.hold(oma, END)
S.beat(pest, T_LIFT1 + 0.5, "staan", face="verbaasd", face_amt=0.7, at=S.headpos(oma, T_LIFT1))
S.beat(pest, T_LIFT1 + 2.3, "staan", face="verdrietig", face_amt=0.4, at=S.headpos(oma, T_LIFT1))
S.beat(zus, T_LIFT1 + 0.8, "staan", face="blij", face_amt=0.5, at=S.headpos(oma, T_LIFT1))

# ---------------------------------------------------------------- 17i: de fiets terug
V_I = V(-28.55, 2.1, 0)
S.walk(vr, t_i - 1.0, t_i + 0.3, [V(*CROWD["beste_vriend"], 0), V_I], stride=0.32, turn=False)
S.turn(vr, t_i + 0.3, t_i + 0.5, -90)
S.beat(pest, t_i, "staan", face="verdrietig", face_amt=0.5, look=(0.0, -0.5), body={"head": (-14, 0, 0)}, feet="keep")
S.beat(pest, T_PUSH1 + 0.4, "staan", face="verdrietig", face_amt=0.4, look=(0.3, -0.5), body={"head": (-14, 0, 0)}, feet="keep")
S.hold(pest, END)
S.beat(vr, t_i, "staan", face="twijfel", face_amt=0.6, look=(0.0, -0.4), body={"head": (-12, 0, 0)}, feet="keep")
for t in frange(T_PUSH1 - 0.2, END, 0.2):
    S.sc.frame_set(F(t))
    S.reach(vr, t, "L", grip(fv, "L"))
    S.reach(vr, t, "R", grip(fv, "R"))
S.reach(vr, T_PUSH1 - 0.5, "L", inf=0.0)
S.reach(vr, T_PUSH1 - 0.5, "R", inf=0.0)
S.reach(vr, 0.0, "L", inf=0.0)
S.reach(vr, 0.0, "R", inf=0.0)
# ze kijken elkaar niet aan, dan knikt de vriend één keer
T_NOD = t_i + 2.6
S.beat(vr, T_NOD - 0.4, "staan", face="neutraal", face_amt=0.5, at=S.headpos(pest, T_NOD), feet="keep")
S.beat(vr, T_NOD, "staan", face="neutraal", face_amt=0.5, at=S.headpos(pest, T_NOD), body={"head": (-14, 0, 0)}, feet="keep")
S.beat(vr, T_NOD + 0.3, "staan", face="blij", face_amt=0.3, at=S.headpos(pest, T_NOD), feet="keep")
S.hold(vr, END)
S.beat(pest, T_NOD + 0.4, "staan", face="blij", face_amt=0.25, at=S.headpos(vr, T_NOD), feet="keep")

# ---------------------------------------------------------------- camera's
# 17a WIDE drone over de besneeuwde straat
S.cam(0.0, ((-55.0, -14.0, 18.0), (-22.0, 4.0, 0.0), 26), ((-51.0, -11.5, 15.5), (-24.0, 4.0, 0.0), 26))
# 17b MEDIUM de agent, over de slagboom
HA = S.headpos(ag, t_b)
S.cam(t_b, ((-30.7, 3.35, 1.45), HA + V(0, 0, -0.12), 32), ((-30.55, 3.45, 1.42), HA + V(0, 0, -0.12), 34))
# 17c WIDE trage push vanaf de straatkant de sneeuw in
S.cam(t_c, ((-24.6, 1.3, 1.7), (-40.0, 2.2, 0.9), 30), ((-25.9, 1.5, 1.6), (-40.0, 2.2, 0.9), 32))
# 17d MEDIUM de straat achter de slagboom, van buiten
S.cam(t_d, ((-33.0, 3.6, 1.5), (-27.2, 1.8, 1.0), 28), ((-32.7, 3.5, 1.5), (-27.2, 1.8, 1.0), 29))
# 17e CLOSE push-in de pestkop
S.cam(t_e, (HP + V(1.4, -0.3, -0.04), HP + V(0, 0.08, -0.08), 30), (HP + V(1.12, -0.24, -0.04), HP + V(0, 0.1, -0.08), 32))
# 17f CLOSE de vriend
HV = S.headpos(vr, t_f)
S.cam(t_f, (HV + V(-1.25, -0.35, 0.0), HV + V(0, 0, -0.06), 32), (HV + V(-1.18, -0.33, 0.0), HV + V(0, 0, -0.06), 33))
# 17g WIDE hoog van buiten, over de bende heen
S.cam(t_g, ((-37.0, -2.0, 3.4), (-27.6, 2.4, 0.8), 26), ((-36.5, -1.7, 3.3), (-27.6, 2.4, 0.8), 27))
# 17h MEDIUM push-in oma bij de slagboom
HO = S.headpos(oma, T_LIFT0)
S.cam(t_h, ((-32.4, 0.0, 1.45), HO + V(0.3, 0.0, -0.1), 28), ((-31.8, 0.35, 1.4), HO + V(0.0, 0.0, -0.05), 30))
# 17i CLOSE de fiets terug, van opzij
S.cam(t_i, ((-29.75, 5.4, 1.3), (-29.75, 2.25, 0.85), 30), ((-29.75, 5.2, 1.28), (-29.75, 2.25, 0.85), 31))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 100", [(0.0, 15), (T_LIFT1 + 0.6, 15)], t0=0.0, big=True)
S.ambience("sfx_sneeuwstorm", 0.0, END, vol=0.05)
S.ambience("sfx_vuur", t_b, t_c, vol=0.03)
S.music("m_winter", 0.0, T_LIFT1, vol=0.14, fade_in=0.6, fade_out=0.6)
S.music("strijkers_warm", T_LIFT1 - 0.2, END, vol=0.2, fade_in=0.6, fade_out=0.6)
S.say("N17-01", at=0.3)
S.say("N17-05", at=t_i + 0.6)
S.finish(length=END, tail=0.0)
