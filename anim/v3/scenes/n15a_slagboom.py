"""N15a · Dag 14: wijken worden landjes (script scène 15a-15d). Straat met de slagboom en de ruilmarkt.
15a  WIDE: de slagboom van winkelkar, planken en verkeersbord. De agent (fluitje in plaats van badge) fluit, steekt zijn
     hand op en laat een buurvrouw met een kruiwagen door.
15b  WIDE stijlbreuk: papieren stadskaart van bovenaf, gekleurde vlekken verschijnen een voor een (twee shots).
     VO: "Within two weeks, every neighborhood in the city had become its own little country..."
15c  DETAIL: een hand legt batterijen op tafel, een andere hand schuift er een kaars voor terug. VO: "Batteries were the new cash."
15d  MEDIUM: de jongen ruilt een stapel strips voor drie kaarsen en een fles water. De verkoper bladert met een likkende vinger, knikt.

    blender -b -P anim/v3/scenes/n15a_slagboom.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n15a", "straat", "nr_slagboom", exposure=0.05)
sh = S.cuts([3.6, 3.6, 3.4, 2.6, 3.8])
END = sh[-1][1]
t_b1, t_b2, t_c, t_d = [s[0] for s in sh[1:]]
rnd = random.Random(15)

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- 15a: de slagboom, de agent en de buurvrouw met de kruiwagen
ARM = S.obj("Slagboom_arm")
ARM.rotation_mode = "XYZ"
T_OPEN0, T_OPEN1 = 1.5, 2.2
for t, a in ((0.0, 0), (T_OPEN0, 0), (T_OPEN1, -75), (t_b1 + 0.1, -75)):
    ARM.rotation_euler.y = math.radians(a)
    ARM.keyframe_insert("rotation_euler", index=1, frame=F(t))

AG = V(-28.6, 4.6, 0)
ag = S.actor("agent", AG, -90, drop=("agent_badge",))            # kijkt naar -x, de straat uit
S.beat(ag, 0.0, "staan", face="vastberaden", face_amt=0.6, look=(0.0, 0.0))
WH = S.bone_world(ag, "head", 0.0, tail=False) + V(-0.15, 0.0, -0.05)   # fluitje aan de mond
S.reach(ag, 0.0, "R", inf=0.0)
S.reach(ag, 0.15, "R", WH)
S.reach(ag, 0.75, "R", WH)
S.reach(ag, 0.95, "R", inf=0.0)
S.beat(ag, 0.95, "staan", face="vastberaden", face_amt=0.8, look=(0.0, 0.0), arms=arm("L", (0.3, 0.6, 0.5), (0.0, 0.3, 0.95)))
S.beat(ag, T_OPEN0, "staan", face="blij", face_amt=0.4, look=(0.2, 0.0), arms=WAVE_SMALL_R)
S.beat(ag, T_OPEN0 + 0.35, "staan", face="blij", face_amt=0.4, look=(0.3, 0.0), arms=WAVE_SMALL_R2)
S.beat(ag, T_OPEN0 + 0.7, "staan", face="blij", face_amt=0.4, look=(0.4, 0.0), arms=WAVE_SMALL_R)
S.beat(ag, T_OPEN0 + 1.3, "staan", face="neutraal", face_amt=0.5, look=(0.4, 0.0))
S.hold(ag, t_b1)

# buurvrouw met kruiwagen: komt van buiten (-x), wacht, en loopt dan door de slagboom de straat in
BV0, BV1, BV2 = V(-35.0, 2.6, 0), V(-31.8, 2.6, 0), V(-27.6, 2.6, 0)
bv = S.actor("figurant_b", BV0, 90)                              # kijkt naar +x
S.walk(bv, 0.0, 1.0, [BV0, BV1], stride=0.32, turn=False)
S.walk(bv, T_OPEN1 - 0.3, t_b1 + 0.3, [BV1, BV2], stride=0.32, turn=False)
S.beat(bv, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0.0, 0.0))
S.beat(bv, 1.1, "staan", face="blij", face_amt=0.5, at=S.headpos(ag, 0.0))
WB = S.mat("kruiwagen_groen", (0.25, 0.45, 0.3))
kw = T.box("Kruiwagen", (0, 0, 0), (0.62, 0.9, 0.32), WB, base=False, bevel=0.06, ol=0.004)     # bak (lokaal: lengte langs y)
for sx in (-1, 1):
    T.to_mesh(T.tube(f"Kruiwagen_hand{sx}", [(sx * 0.22, 0.4, 0.05), (sx * 0.26, 0.95, 0.25)], 0.02, S.mat("staal_zwart", (0.08, 0.08, 0.09)))).parent = kw
    T.to_mesh(T.tube(f"Kruiwagen_poot{sx}", [(sx * 0.2, 0.3, -0.12), (sx * 0.2, 0.32, -0.42)], 0.018, S.mat("staal_zwart", (0.08, 0.08, 0.09)))).parent = kw
wheel = T.cyl("Kruiwagen_wiel", (0, 0, 0), 0.18, 0.08, S.mat("rubber_zwart", (0.05, 0.05, 0.05)), rot=(0, 90, 0), seg=18, ol=0.003)
wheel.parent = kw
wheel.location = (0, -0.5, -0.3)
wheel.rotation_mode = "XYZ"
for k in range(5):
    T.box(f"Kruiwagen_pot{k}", (rnd.uniform(-0.18, 0.18), rnd.uniform(-0.25, 0.25), 0.16), (0.14, 0.14, 0.16),
          S.mat(f"pot_{k % 3}", [(0.75, 0.45, 0.25), (0.9, 0.85, 0.7), (0.35, 0.55, 0.3)][k % 3]), base=False, bevel=0.03, ol=0.003).parent = kw
kw.rotation_mode = "XYZ"
roll = 0.0
prev = None
for f in range(F(0.0), F(t_b1) + 1):
    t = (f - 1) / FPS
    M = S._root_matrix(bv, t)
    p = M @ V(0, -1.0, 0.48)                       # voor haar uit (zij kijkt naar -y lokaal)
    yaw = M.to_euler().z
    if prev is not None:
        roll += (p - prev).length / 0.18
    prev = p.copy()
    kw.location = p
    kw.rotation_euler = (math.radians(-8), 0, yaw)
    kw.keyframe_insert("location", frame=f)
    kw.keyframe_insert("rotation_euler", frame=f)
    wheel.rotation_euler.x = roll
    wheel.keyframe_insert("rotation_euler", index=0, frame=f)
for t in frange(0.0, t_b1, 0.2):
    S.sc.frame_set(F(t))
    for s, sx in (("L", 1), ("R", -1)):
        S.reach(bv, t, s, kw.matrix_world @ V(sx * 0.26, 0.95, 0.25))

# ---------------------------------------------------------------- 15b: de papieren stadskaart (ver weg in de scène)
MP = V(300.0, 300.0, 0.0)
PAPER = S.mat("kaart_papier", (0.93, 0.89, 0.78))
INK = S.mat("kaart_inkt", (0.35, 0.32, 0.30))
WATER = S.mat("kaart_rivier", (0.55, 0.72, 0.85))
T.box("Kaart_tafel", tuple(MP + V(0, 0, -0.06)), (3.2, 2.2, 0.06), S.mat("tafel_hout_donker", (0.35, 0.22, 0.14)), bevel=0.01, ol=0)
T.box("Kaart", tuple(MP), (2.4, 1.6, 0.004), PAPER, bevel=0, ol=0)
T.to_mesh(T.tube("Kaart_rivier", [MP + V(-1.2, -0.2, 0.006), MP + V(-0.4, 0.05, 0.006), MP + V(0.3, -0.1, 0.006), MP + V(1.2, 0.25, 0.006)], 0.04, WATER))
for i in range(-5, 6):
    T.box(f"Kaart_straat_x{i}", tuple(MP + V(i * 0.2 + rnd.uniform(-0.03, 0.03), 0, 0.0045)), (0.006, 1.6, 0.001), INK, bevel=0, ol=0)
for j in range(-3, 4):
    T.box(f"Kaart_straat_y{j}", tuple(MP + V(0, j * 0.2 + rnd.uniform(-0.03, 0.03), 0.0045)), (2.4, 0.006, 0.001), INK, bevel=0, ol=0)
COLS = [(0.90, 0.35, 0.30), (0.30, 0.55, 0.85), (0.95, 0.75, 0.25), (0.40, 0.70, 0.40), (0.70, 0.45, 0.80), (0.95, 0.55, 0.20)]
blobs = []
for k in range(26):
    c = COLS[k % len(COLS)]
    p = MP + V(rnd.uniform(-1.05, 1.05), rnd.uniform(-0.68, 0.68), 0.006 + k * 0.0002)
    b = T.cyl(f"Landje_{k}", tuple(p), rnd.uniform(0.09, 0.16), 0.001, S.mat(f"landje_{k % len(COLS)}", c), seg=7 + k % 4, ol=0)
    b.rotation_euler.z = rnd.uniform(0, 6.3)
    b.scale = (rnd.uniform(0.8, 1.3), rnd.uniform(0.7, 1.1), 1)
    sc0 = tuple(b.scale)
    t0 = t_b1 + 0.25 + k * 0.2
    b.scale = (0.001, 0.001, 1)
    b.keyframe_insert("scale", frame=1)
    b.keyframe_insert("scale", frame=F(t0))
    b.scale = (sc0[0] * 1.15, sc0[1] * 1.15, 1)
    b.keyframe_insert("scale", frame=F(t0 + 0.12))
    b.scale = sc0
    b.keyframe_insert("scale", frame=F(t0 + 0.22))
    blobs.append(b)
# grenslijntjes (gestippeld) en vlaggetjes in shot 2
FL = S.mat("vlag_rood", (0.9, 0.2, 0.15))
for k in range(4):
    p = blobs[k * 3].location + V(0.05, 0.04, 0)
    T.cyl(f"Kaart_vlagstok_{k}", tuple(p), 0.003, 0.08, INK, seg=6, ol=0)
    T.box(f"Kaart_vlag_{k}", tuple(p + V(0.018, 0, 0.065)), (0.035, 0.002, 0.022), S.mat(f"vlag_{k}", COLS[(k * 2) % 6]), base=False, bevel=0, ol=0)

# ---------------------------------------------------------------- 15c: batterijen op tafel, een kaars terug
TB = V(-16.0, 7.3, 0.9)
koper = S.actor("figurant_a", V(-16.25, 6.45, 0.12), 180)            # kijkt naar +y, naar de tafel
verk1 = S.actor("figurant_c", V(-15.75, 8.15, 0.12), 0)              # achter de tafel, kijkt naar -y
for ch in (koper, verk1):
    S.beat(ch, 0.0, "staan", face="neutraal", face_amt=0.5, at=TB)
bat = ST3.batterijen("Batterijen_koper", (0, 0, 0), n=6, seed=9)
T_PUT = t_c + 0.9
S.reach(koper, t_c, "R", TB + V(-0.25, -0.35, 0.18))
S.reach(koper, T_PUT, "R", TB + V(-0.18, -0.2, 0.06))
S.reach(koper, T_PUT + 0.4, "R", TB + V(-0.25, -0.45, 0.1))
S.reach(koper, T_PUT + 0.8, "R", inf=0.0)
grab(S, bat, koper, 0.0, "hand.R", loc=(0, 0.04, -0.02), release=T_PUT)
bat.location = TB + V(-0.2, -0.18, 0.0)
bat.keyframe_insert("location", frame=F(T_PUT))
# de kaars: de verkoper schuift hem naar de koper
kaars = S.obj("Marktkaars_1")
K0 = kaars.location.copy()
K1 = V(-15.75, 7.0, K0.z)
T_PUSH0, T_PUSH1 = t_c + 1.3, t_c + 2.1
for t, p in ((0.0, K0), (T_PUSH0, K0), (T_PUSH1, K1)):
    kaars.location = p
    kaars.keyframe_insert("location", frame=F(t))
S.reach(verk1, t_c, "L", inf=0.0)
S.reach(verk1, T_PUSH0 - 0.3, "L", K0 + V(0, 0.08, 0.12))
S.reach(verk1, T_PUSH0, "L", K0 + V(0, 0.06, 0.08))
S.reach(verk1, T_PUSH1, "L", K1 + V(0, 0.06, 0.08))
S.reach(verk1, T_PUSH1 + 0.4, "L", inf=0.0)
S.beat(verk1, t_c + 0.4, "staan", face="neutraal", face_amt=0.6, at=bat.location + V(0, 0, 0))
S.beat(koper, t_c + 1.6, "staan", face="blij", face_amt=0.4, at=K1)

# ---------------------------------------------------------------- 15d: de jongen ruilt strips voor kaarsen en water
TS = V(-12.0, 7.3, 0.9)
held = S.actor("hoofdpersonage_kind", V(-12.48, 6.45, 0.12), 180)    # (lantaarnpaal staat op x -12)
ruil = S.actor("ruilmarktverkoper", V(-11.85, 8.15, 0.12), 0)
strips = ST3.stripboeken("Strips_jongen", (0, 0, 0), n=7, seed=11)
T_LAY = t_d + 0.6
grab(S, strips, held, 0.0, "hand.R", loc=(0.0, 0.08, 0.0), rot=(90, 0, 0), release=T_LAY)
strips.rotation_mode = "XYZ"
LAY = TS + V(-0.4, -0.15, 0.0)
strips.location, strips.rotation_euler = LAY, (0, 0, math.radians(8))
strips.keyframe_insert("location", frame=F(T_LAY))
strips.keyframe_insert("rotation_euler", frame=F(T_LAY))
S.reach(held, t_d, "R", LAY + V(0.0, -0.18, 0.16))
S.reach(held, T_LAY, "R", LAY + V(0.0, -0.06, 0.06))
S.reach(held, T_LAY + 0.35, "R", inf=0.0)
S.reach(held, t_d, "L", inf=0.0)
S.beat(held, t_d, "staan", face="nerveus", face_amt=0.4, at=S.headpos(ruil, 0.0))
S.beat(held, t_d + 1.0, "staan", face="nerveus", face_amt=0.5, at=LAY)
# verkoper: likt aan zijn vinger, bladert, knikt, schuift de kaarsen en de fles terug
MOUTH = S.bone_world(ruil, "head", t_d, tail=False) + V(0, -0.14, 0.05)
for t, p in ((t_d + 0.6, MOUTH), (t_d + 0.85, MOUTH), (t_d + 1.15, LAY + V(0.06, 0.05, 0.06)), (t_d + 1.4, LAY + V(-0.04, 0.05, 0.07)),
             (t_d + 1.65, LAY + V(0.06, 0.05, 0.06)), (t_d + 1.9, LAY + V(-0.04, 0.05, 0.07))):
    S.reach(ruil, t, "R", p)
S.reach(ruil, t_d, "R", inf=0.0)
S.beat(ruil, t_d, "staan", face="twijfel", face_amt=0.5, at=LAY)
for t, a in ((t_d + 2.1, 0), (t_d + 2.3, 14), (t_d + 2.5, 0), (t_d + 2.7, 12), (t_d + 2.9, 0)):
    A.bone_rot(ruil, F(t), "head", (a, 0, 0))
S.beat(ruil, t_d + 2.1, "staan", face="blij", face_amt=0.6, at=S.headpos(held, 0.0))
ITEMS = []
for k in range(3):
    ITEMS.append(ST3.kaars(f"Ruilkaars_{k}", (TS.x + 0.2 + k * 0.07, TS.y + 0.22, TS.z), lit=False))
fles = T.cyl("Ruilfles", (TS.x + 0.42, TS.y + 0.2, TS.z), 0.04, 0.3, T.glass("fles_water", (0.75, 0.9, 1.0), alpha=0.5), seg=12, ol=0)
ITEMS.append(fles)
T_GIVE0, T_GIVE1 = t_d + 2.3, t_d + 3.1
for o in ITEMS:
    p0 = o.location.copy()
    for t, p in ((0.0, p0), (T_GIVE0, p0), (T_GIVE1, p0 + V(0, -0.3, 0))):
        o.location = p
        o.keyframe_insert("location", frame=F(t))
S.reach(ruil, T_GIVE0 - 0.2, "R", TS + V(0.3, 0.32, 0.1))
S.reach(ruil, T_GIVE1, "R", TS + V(0.3, 0.02, 0.1))
S.reach(ruil, T_GIVE1 + 0.4, "R", inf=0.0)
S.beat(held, t_d + 2.6, "staan", face="blij", face_amt=0.6, at=TS + V(0.3, -0.1, 0))
for ch in (held, ruil, koper, verk1, bv):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 15a WIDE van opzij: de slagboom, de agent, de buurvrouw met de kruiwagen
S.cam(0.0, ((-26.2, -2.6, 1.7), (-31.0, 2.8, 1.2), 24), ((-26.4, -2.2, 1.7), (-31.0, 2.8, 1.2), 25), handheld=0.15)
# 15b WIDE de kaart van bovenaf, vlekken verschijnen; dan dichterbij met de vlaggetjes
S.cam(t_b1, ((MP.x, MP.y - 0.35, 2.6), MP, 28), ((MP.x, MP.y - 0.3, 2.3), MP, 28))
S.cam(t_b2, ((MP.x - 0.2, MP.y - 0.9, 0.75), MP + V(-0.1, 0.0, 0), 30), ((MP.x - 0.15, MP.y - 0.8, 0.65), MP + V(-0.1, 0.05, 0), 32))
# 15c DETAIL de tafel met batterijen en kaars
S.cam(t_c, ((TB.x - 0.95, TB.y - 0.35, 2.0), TB + V(0.05, -0.08, 0.0), 30), ((TB.x - 0.88, TB.y - 0.32, 1.92), TB + V(0.05, -0.08, 0.0), 31))
# 15d MEDIUM de ruil, van opzij langs de tafel
S.cam(t_d, ((TS.x - 1.95, TS.y - 1.25, 1.45), TS + V(-0.05, 0.05, 0.3), 30), ((TS.x - 1.85, TS.y - 1.18, 1.45), TS + V(-0.05, 0.05, 0.3), 31))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 14", 6, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, t_b1, vol=0.04)
S.ambience("sfx_menigte_mompel", t_c, END, vol=0.04)
S.sfx("sfx_fluitje", 0.2, 0.2)
S.sfx("sfx_papier_vouwen", t_b1, 0.25)
S.music("m_reis", t_b1, END, vol=0.16, fade_in=0.4, fade_out=0.4)
S.say("N15-01", at=1.6)
S.say("N15-02", at=t_c + 0.2)
S.finish(length=END, tail=0.0)
