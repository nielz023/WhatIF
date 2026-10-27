"""SH4 · What if you turned into whatever you touched? · keuken: hout (tafel), staal (koelkast), glas (deurraam).
Daarna het trapgat (los gebouwd naast de keuken): boven aan de trap glijdt zijn voet weg. Hij valt... einde.

    blender -b -P anim/shorts/sh4_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh4", "a", "keuken", "ochtend", lines=(1, 2, 3, 4, 5, 6, 7, 8))
l1, l2, l3, l4, l5, l6, l7, l8 = (S.L[n] for n in range(1, 9))
END = S.t1

for n in ("Krant", "Stoel_4", "Ontbijt_broertje", "Ontbijt_bord"):
    o = S.obj(n)
    if o:
        o.hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Krant_kolom"):
        o.hide_render = True
for n in ("Cornflakes_doos", "Cornflakes_label", "Melkpak", "Melkpak_band"):
    S.obj(n).hide_render = True               # niet voor hem

TZ = 0.77
TABLE_EDGE = V(0.58, -0.13, TZ)
P0 = V(0.58, 0.22, 0)                          # aan tafel, gezicht naar de camera (-y)
FRIDGE_AT = V(1.72, 0.92, 0)                   # voor de koelkast
FRIDGE_TOUCH = V(1.80, 1.33, 1.05)
DOOR_AT = V(-1.86, 0.88, 0)                    # voor de achterdeur (raampje erin)
PANE = V(-2.29, 0.95, 1.05)
PANE_TOUCH = V(-2.28, 0.86, 1.3)

# een raampje in de keukendeur
glass = T.glass("deurraam", (0.7, 0.85, 0.95), 0.4)
T.box("Deurraam", tuple(PANE), (0.02, 0.5, 0.6), glass, bevel=0, ol=0.006)
T.box("Deurraam_lijst", tuple(PANE + V(0.005, 0, -0.03)), (0.02, 0.58, 0.66), P.m("wit"), bevel=0.005, ol=0.006)

# ---------------------------------------------------------------- het trapgat (los, x = 12 ... 17)
HX = 12.0
ZS = 40.0                                       # hoog boven de tuin (geen gras door het trapgat)
_before = set(bpy.data.objects)
STEP_N, RISE, RUN = 13, 0.19, 0.26
TOP_X = HX + 2.0                                # rand van de bovenste tree
wall_m = S.mat("trapgat_muur", (0.86, 0.80, 0.68))
wood_m = S.mat("trap_hout", (0.55, 0.36, 0.2))
run_m = S.mat("traploper", (0.55, 0.15, 0.16))
T.box("Overloop", (HX + 1.0, 0, -0.1), (2.0, 1.4, 0.1), wood_m, bevel=0, ol=0.01)
for k in range(STEP_N):
    x = TOP_X + RUN * (k + 0.5)
    z = -RISE * (k + 1)
    T.box(f"Tree_{k}", (x, 0, z - 0.06), (RUN + 0.02, 1.0, 0.06), wood_m, bevel=0.01, ol=0.01)
    T.box(f"Tree_loper_{k}", (x - 0.02, 0, z), (RUN - 0.02, 0.6, 0.012), run_m, bevel=0, ol=0.004)
    T.box(f"Stootbord_{k}", (TOP_X + RUN * k + 0.005, 0, z), (0.02, 1.0, RISE), P.m("wit"), bevel=0, ol=0.004)
BOT_Z = -RISE * STEP_N
T.box("Gang_beneden", (TOP_X + RUN * STEP_N + 1.5, 0, BOT_Z - 0.1), (3.0, 1.6, 0.1), wood_m, bevel=0, ol=0.01)
for s in (-1, 1):
    T.box(f"Trapmuur_{s}", (HX + 3.6, s * 0.75, BOT_Z), (8.0, 0.1, 2.6 - BOT_Z), wall_m, bevel=0, ol=0.01)
    if s == -1:
        continue
    # leuning
    for k in range(0, STEP_N, 2):
        x = TOP_X + RUN * (k + 0.5)
        T.cyl(f"Spijl_{k}", (x, 0.45, -RISE * (k + 1)), 0.012, 0.9, P.m("wit"), seg=8, ol=0.004)
    ln = T.cyl("Leuning", (0, 0, 0), 0.025, math.hypot(RUN * STEP_N, RISE * STEP_N) + 0.4, wood_m, seg=10, ol=0.006)
    ln.location = (TOP_X - 0.15, 0.45, 0.9)
    ln.rotation_euler = (0, math.radians(90) + math.atan2(RISE, RUN), 0)
T.box("Trapgat_achter", (HX - 0.05, 0, -0.1), (0.1, 1.6, 2.7), wall_m, bevel=0, ol=0.01)
T.box("Trapgat_eind", (TOP_X + RUN * STEP_N + 3.0, 0, BOT_Z), (0.1, 1.6, 2.7 - BOT_Z), wall_m, bevel=0, ol=0.01)
T.box("Trapgat_plafond", (HX + 3.6, 0, 2.55), (8.0, 1.6, 0.1), P.m("wit"), bevel=0, ol=0)
T.box("Schilderij", (HX + 4.0, 0.69, 0.6), (0.6, 0.02, 0.45), S.mat("schilderij", (0.3, 0.55, 0.75)), bevel=0, ol=0.008)
T.point_light("Trap_lamp", (HX + 1.2, 0, 2.3), color=(1.0, 0.82, 0.6), energy=110, radius=0.1)
T.point_light("Trap_lamp_beneden", (TOP_X + 2.6, 0, BOT_Z + 2.2), color=(1.0, 0.8, 0.55), energy=60, radius=0.1)
for o in set(bpy.data.objects) - _before:
    if o.parent is None:
        o.location.z += ZS

# ---------------------------------------------------------------- figuur en materialen
held = S.actor("hoofdpersonage", P0, 0)
HP0 = S.head(held)                             # hoofd aan tafel (rustpose)
T_HAND = l1[0] + 2.4                             # zijn hand wordt hout
T_FRIDGE = l3[0] + 0.9
T_PANE = l4[0] + 1.0
e_hout = spreader(S, held, "Hout_bron", T_HAND, l2[0] + 1.6, r1=2.6)
key(e_hout, T_HAND + 0.9, scale=0.16)
key(e_hout, l2[0] + 0.1, scale=0.18)
key(e_hout, l2[0] + 0.7, scale=0.55)
e_staal = spreader(S, held, "Staal_bron", T_FRIDGE + 0.15, T_FRIDGE + 1.6, r1=2.6)
e_glas = spreader(S, held, "Glas_bron", T_PANE + 0.15, T_PANE + 1.5, r1=2.6)
material_spread(held, [("hout", e_hout), ("staal", e_staal), ("glas", e_glas)])

# ---------------------------------------------------------------- muziek, geluid, tellers
S.music_all("pizz_spanning", vol=0.24)
S.music("strijk_noot", l6[0] - 0.3, END, vol=0.2, fade_in=1.2)
S.ambience("sfx_binnen_sfeer", 0.0, l6[0], vol=0.12)
S.sfx("sfx_hout_klop", T_HAND + 0.1, 0.35)
S.sfx("sfx_hout_klop", l2[1] - 0.75, 0.55)
S.sfx("sfx_hout_klop", l2[1] - 0.4, 0.55)
S.sfx("sfx_staal", T_FRIDGE + 0.2, 0.4)
S.sfx("sfx_glas_klink", T_PANE + 0.2, 0.4)
S.counter("WOOD", T_HAND + 0.3, T_FRIDGE + 0.2, color=(0.85, 0.6, 0.3, 1))
S.counter("STEEL", T_FRIDGE + 0.4, T_PANE + 0.2, color=(0.78, 0.84, 0.92, 1))
S.counter("GLASS", T_PANE + 0.4, l8[0], color=(0.6, 0.9, 1.0, 1))

# ---------------------------------------------------------------- 1 · hout
S.beat(held, 0.0, "staan", face="neutraal", look=(0, -0.4), at=TABLE_EDGE)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, l2[1] - 1.3, "L", None, 0.0)
S.reach(held, 0.0, "R", TABLE_EDGE + V(0, 0.02, 0.06))
S.beat(held, T_HAND + 0.4, "staan", face="verbaasd", face_amt=0.9, at=TABLE_EDGE, mouth=0.25)
S.reach(held, T_HAND + 0.3, "R", TABLE_EDGE + V(0, 0.02, 0.06))
S.reach(held, l1[1] - 0.6, "R", HP0 + V(0.15, -0.3, -0.2))       # hij tilt zijn houten hand op
S.beat(held, l1[1] - 0.4, "staan", face="geschrokken", face_amt=0.9, at=HP0 + V(0.15, -0.4, -0.2), mouth=0.4)
S.beat(held, l2[0] + 0.6, "staan", face="bang", face_amt=0.8, look=(0, -0.5), mouth=0.2,
       body={"head": (14, 0, 0)})
S.reach(held, l2[0] + 0.6, "R", None, 0.0)
# knock knock: linkerhand klopt op zijn eigen hoofd
S.beat(held, l2[1] - 1.1, "staan", face="twijfel", face_amt=1.0, look=(0, 0), mouth=0.0)
for k, t in enumerate((l2[1] - 0.85, l2[1] - 0.5)):
    S.reach(held, t - 0.12, "L", HP0 + V(-0.05, -0.05, 0.42))
    S.reach(held, t, "L", HP0 + V(-0.04, -0.02, 0.33))
S.reach(held, l2[1] + 0.2, "L", None, 0.0)

# ---------------------------------------------------------------- 2 · staal
S.walk(held, l2[1] + 0.3, T_FRIDGE - 0.3, [P0, V(1.2, 0.6, 0), FRIDGE_AT], stride=0.45, end_rot=180)
S.beat(held, l2[1] + 0.3, "staan", face="nerveus", face_amt=0.6, look=(0.3, 0), feet="keep", mouth=0.0)
S.turn(held, T_FRIDGE - 0.3, T_FRIDGE - 0.05, 180)
S.reach(held, T_FRIDGE - 0.1, "R", FRIDGE_TOUCH + V(0, -0.08, 0))
S.reach(held, T_FRIDGE + 0.05, "R", FRIDGE_TOUCH)
S.beat(held, T_FRIDGE + 0.1, "staan", face="verbaasd", face_amt=0.8, at=FRIDGE_TOUCH, mouth=0.2)
S.reach(held, T_FRIDGE + 1.4, "R", None, 0.0)
# zwaar en koud: hij zakt door zijn knieën en rilt
HEAVY = T_FRIDGE + 1.6
S.turn(held, HEAVY, HEAVY + 0.5, 270)
S.beat(held, HEAVY + 0.5, "handen_zij", face="inspanning", face_amt=0.9, look=(0, -0.3), crouch=(0.08, 6), mouth=0.1)
S.beat(held, HEAVY + 1.2, "armen_over", face="nerveus", face_amt=1.0, look=(0, -0.4), crouch=(0.08, 6), mouth=0.05)
for k, t in enumerate(frange(HEAVY + 1.3, HEAVY + 2.2, 0.12)):
    S.beat(held, t, "armen_over", face="nerveus", face_amt=1.0, crouch=(0.08, 6), mouth=0.05,
           body={"chest": (0, 0, 3 if k % 2 else -3)})
# elke stap een deuk: van de koelkast naar de achterdeur
STEP0, STEP1 = l3[1] - 2.2, l4[0] + 0.6
path = [V(1.65, 0.75, 0), V(0.4, 0.55, 0), DOOR_AT]
S.walk(held, STEP0, STEP1, path, stride=0.32, arms=0.25, end_rot=270)
S.beat(held, STEP0, "staan", face="inspanning", face_amt=1.0, look=(0, -0.5), feet="keep", mouth=0.1,
       body={"chest": (10, 0, 0)})
dent_m = S.mat("deuk", (0.32, 0.3, 0.3))
crack_m = S.mat("barst", (0.12, 0.1, 0.1))
nst = 10
segs = [(path[i + 1] - path[i]) for i in range(len(path) - 1)]
tot = sum(s.length for s in segs)
for k in range(1, nst):
    u = k / nst
    d = tot * (smooth(0, 1, u) * 0.5 + u * 0.5)
    for s_, a in zip(segs, path):
        if d <= s_.length:
            p = a + s_.normalized() * d
            side = s_.normalized().cross(V(0, 0, 1)) * (0.09 if k % 2 else -0.09)
            break
        d -= s_.length
    t = STEP0 + (STEP1 - STEP0) * u
    dz = T.cyl(f"Deuk_{k}", tuple(p + side + V(0, 0, -0.012)), 0.11, 0.014, dent_m, seg=14, ol=0.003)
    dz.scale = (1.25, 0.85, 1)
    dz.rotation_euler.z = math.atan2(s_.y, s_.x)
    show(dz, t)
    for j in range(3):
        c = T.box(f"Deuk_barst_{k}_{j}", tuple(p + side + V(0, 0, 0.001)), (0.22 + j * 0.05, 0.008, 0.003), crack_m,
                  bevel=0, ol=0)
        c.rotation_euler.z = j * 1.05 + k
        show(c, t)
    S.sfx("sfx_metaal_stap", t - 0.03, 0.42)

# ---------------------------------------------------------------- 3 · glas
S.reach(held, T_PANE - 0.15, "R", PANE_TOUCH + V(0.08, 0, 0))
S.reach(held, T_PANE, "R", PANE_TOUCH)
S.beat(held, T_PANE, "staan", face="neutraal", look=(0, 0.1), at=PANE_TOUCH, mouth=0.0)
S.beat(held, T_PANE + 0.6, "staan", face="verbaasd", face_amt=0.8, at=PANE_TOUCH + V(0.5, -0.4, -0.3), mouth=0.2)
S.reach(held, T_PANE + 1.0, "R", HP0 - P0 + DOOR_AT + V(-0.35, -0.1, -0.25))
S.beat(held, l4[1] - 0.2, "staan", face="bang", face_amt=0.9, at=HP0 - P0 + DOOR_AT + V(-0.5, -0.2, -0.3), mouth=0.3)
S.reach(held, l4[1], "R", None, 0.0)
# voorzichtig, op zijn tenen: klink, klink. Dan stoot hij tegen de stoel: een barstje
TIP0, TIP1 = l5[0] + 0.1, l5[0] + 2.9
S.walk(held, TIP0, TIP1, [DOOR_AT, V(-1.0, 0.55, 0), V(-0.42, 0.42, 0)], stride=0.18, arms=0.2, end_rot=90)
S.beat(held, TIP0, "handen_zij", face="nerveus", face_amt=1.0, look=(0, -0.4), feet="keep", mouth=0.05)
for t in frange(TIP0 + 0.25, TIP1, 0.42):
    S.sfx("sfx_glas_klink", t, 0.32)
BUMP = TIP1 + 0.05
S.beat(held, BUMP, "schrik", amount=0.5, face="geschrokken", face_amt=1.0, look=(0.2, -0.3), mouth=0.5)
S.sfx("sfx_glas_klink", BUMP, 0.55)
chair3 = S.obj("Stoel_3")
key(chair3, BUMP - 0.02, loc=tuple(chair3.location), rot=(0, 0, 0))
key(chair3, BUMP + 0.2, loc=tuple(chair3.location + V(0.05, -0.08, 0)), rot=(0, 0, -6))
cracks = []
for j in range(5):
    c = T.box(f"Glasbarst_{j}", (0, 0, 0), (0.006, 0.09 + j * 0.02, 0.004), P.m("wit"), bevel=0, ol=0)
    attach(c, held, "upper_arm.R", loc=(0.05, -0.1 + j * 0.01, 0.06), rot=(0, j * 35 - 70, 0))
    c.visible_shadow = False
    cracks.append(c)
    show(c, BUMP + 0.04 * j)
S.beat(held, BUMP + 0.6, "staan", face="bang", face_amt=1.0, look=(0.7, -0.2), mouth=0.35, body={"head": (6, 0, 25)})
S.hold(held, l6[0] - 0.05)

# ---------------------------------------------------------------- 4 · boven aan de trap
TOP = V(TOP_X - 0.22, 0, ZS)
S.teleport(held, l6[0], TOP, 90)
S.beat(held, l6[0], "handen_zij", face="bang", face_amt=1.0, look=(0.3, -0.8), mouth=0.2, body={"head": (18, 0, 0)})
S.beat(held, l6[1] - 0.6, "handen_zij", face="nerveus", face_amt=1.0, look=(0.4, -0.9), mouth=0.1,
       body={"head": (24, 0, 0), "chest": (6, 0, 0)})
S.hold(held, l7[0] + 0.1)
SLIP = l7[0] + 0.35
S.beat(held, SLIP + 0.2, "armen_omhoog", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, -0.6), mouth=0.8)
S.beat(held, SLIP + 1.2, "armen_omhoog", amount=1.0, face="schreeuw", face_amt=1.0, look=(0, -0.8), mouth=1.0)
S.hold(held, END)
S.sfx("sfx_struikelen", SLIP - 0.05, 0.6)
S.sfx("sfx_slowmo", SLIP + 0.15, 0.4)
S.sfx("sfx_cliffhanger", l7[1] - 0.3, 0.75)
# kantelen om zijn voeten, dan zweeft hij (slow motion) boven de treden
rig = held.rig
fr = list(range(F(SLIP), F(END) + 1))


def fall(t):
    u = max(0.0, t - SLIP)
    tip = min(1.0, u / 0.7)
    slow = max(0.0, u - 0.7)
    ang = 32 * smooth(0, 1, tip) + 9 * slow
    fwd = 0.25 * smooth(0, 1, tip) + 0.22 * slow
    down = 0.05 * tip + 0.12 * slow * slow
    return ang, fwd, down


bake(rig, "location", fr, [(TOP.x + fall((f - 1) / FPS)[1], TOP.y, TOP.z - fall((f - 1) / FPS)[2]) for f in fr])
for f in fr:
    rig.rotation_euler = (math.radians(fall((f - 1) / FPS)[0]), 0, math.radians(90))
    rig.keyframe_insert("rotation_euler", frame=f)
# zijn rechtervoet glijdt van de rand
key(rig, SLIP - 0.04, rot=(0, 0, 90))

# ---------------------------------------------------------------- camera (staand)
S.cam(0.0, S.shot(held, 0.3, "med", az=8, lens=30, h=0.15), S.shot(held, T_HAND, "med", az=4, lens=33, h=0.1))
S.cam(T_HAND, (TABLE_EDGE + V(0.5, -0.75, 0.45), TABLE_EDGE + V(0, 0.05, 0.12), 36),
      (TABLE_EDGE + V(0.45, -0.68, 0.42), TABLE_EDGE + V(0, 0.05, 0.12), 40))
S.cam(l1[1] - 0.7, S.shot(held, l1[1], "mcu", az=10, lens=36), S.shot(held, l2[0] + 1.0, "mcu", az=6, lens=38))
S.cam(l2[0] + 1.0, S.shot(held, l2[0] + 1.2, "med", az=-10, lens=30, h=0.1), S.shot(held, l2[1], "med", az=-6, lens=32, h=0.1))
S.cam(l2[1] + 0.2, ((0.3, -1.6, 1.4), (1.5, 1.1, 1.0), 24), ((0.45, -1.5, 1.4), (1.6, 1.2, 1.0), 26))
S.cam(T_FRIDGE + 0.1, ((0.35, 0.15, 1.5), (1.75, 1.2, 1.1), 28), ((0.4, 0.2, 1.48), (1.75, 1.2, 1.1), 30))
S.cam(HEAVY + 0.3, S.shot(held, HEAVY + 0.6, "mcu", az=12, lens=34), S.shot(held, STEP0, "mcu", az=8, lens=38))
S.cam(STEP0, ((-1.5, 0.95, 0.35), (0.8, 0.6, 0.3), 22), ((-1.45, 0.95, 0.37), (0.4, 0.6, 0.35), 22))
S.cam(l4[0] - 0.2, ((-1.0, 0.0, 1.35), (-2.2, 0.9, 1.2), 26), ((-1.05, 0.05, 1.3), (-2.2, 0.9, 1.2), 28))
S.cam(T_PANE + 0.8, ((-1.2, 0.2, 1.35), (-1.95, 0.85, 1.25), 32), ((-1.25, 0.24, 1.33), (-1.95, 0.85, 1.25), 36))
S.cam(l5[0], ((-0.2, -1.2, 0.9), (-1.2, 0.6, 0.6), 24), ((-0.1, -1.0, 0.9), (-0.8, 0.5, 0.6), 24))
S.cam(BUMP - 0.1, ((0.8, -0.8, 1.3), (-0.42, 0.42, 1.0), 28), ((0.75, -0.75, 1.3), (-0.42, 0.42, 1.0), 30),
      shake=lambda t: 0.8 * max(0, 1 - (t - BUMP) / 0.4))
# trap: van beneden omhoog, dan over zijn schouder naar beneden
Z_ = V(0, 0, ZS)
S.cam(l6[0], (V(TOP_X + 2.6, 0.2, BOT_Z + 0.8) + Z_, V(TOP_X - 0.2, 0, 0.9) + Z_, 22), (V(TOP_X + 2.4, 0.2, BOT_Z + 0.8) + Z_, V(TOP_X - 0.2, 0, 0.85) + Z_, 24))
S.cam(l6[0] + 1.9, (V(TOP_X - 1.2, -0.35, 1.75) + Z_, V(TOP_X + 2.5, 0.1, BOT_Z + 0.3) + Z_, 22),
      (V(TOP_X - 1.1, -0.32, 1.7) + Z_, V(TOP_X + 2.5, 0.1, BOT_Z + 0.2) + Z_, 22))
S.cam(SLIP - 0.1, None, fn=lambda t: (TOP + V(1.6 + fall(t)[1], -0.55, 0.3 - fall(t)[2]),
                                      TOP + V(0.15 + fall(t)[1], 0, 0.7 - fall(t)[2] * 1.3), 21),
      shake=lambda t: 0.5 + 0.8 * smooth(SLIP, SLIP + 0.5, t))

S.done()
