"""S18 · Dag 17 · de kelder: wakker worden twee verdiepingen lager. Papa sleept de matras naar de wasmachine
(geen grap), mama brengt thee in de gelijmde mok en gaat gewoon naast hem zitten.

    blender -b -P anim/scenes/s18_kelder.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s18", "kleine_interieurs", "kelder")

HOLE = V(-0.6, 0.5, 2.3)
LIE = V(-0.6, -0.95, 0.06)                     # liggend: wortel bij de voeten, hoofd onder het gat
SIT_AT = V(-0.6, 0.15, 0.0)
MAT0, MAT1 = V(1.0, 1.45, 0.0), V(-1.3, 1.45, 0.0)
STAIR_TOP, STAIR_BOT = V(-2.5, 0.0, 1.98), V(-2.5, -2.3, 0.0)

# ---------------------------------------------------------------- twee verdiepingen erboven (voor het shot omhoog)
wood = S.mat("vloerhout_boven", (0.55, 0.40, 0.26))
for nm, (x0, x1, y0, y1) in {"links": (-3.0, -1.05, -2.75, 2.75), "rechts": (-0.15, 3.0, -2.75, 2.75),
                             "voor": (-1.05, -0.15, -2.75, 0.05), "achter": (-1.05, -0.15, 0.95, 2.75)}.items():
    T.box(f"Begane_grond_plafond_{nm}", ((x0 + x1) / 2, (y0 + y1) / 2, 4.95), (x1 - x0, y1 - y0, 0.25), wood, bevel=0.01, ol=0.01)
for j in range(6):
    a = j / 6 * 2 * math.pi
    T.box(f"Splinter_boven_{j}", (HOLE.x + 0.48 * math.cos(a), HOLE.y + 0.48 * math.sin(a), 4.9), (0.05, 0.22, 0.03),
          S.mat("splinter_b", (0.75, 0.58, 0.38)), rot=(25, 0, math.degrees(a) + 90), bevel=0, ol=0.003)
T.box("Slaapkamer_plafond", (0, 0, 7.6), (6, 5.5, 0.2), S.mat("plafond_wit", (0.95, 0.94, 0.92)), bevel=0, ol=0)
T.point_light("Licht_begane_grond", (HOLE.x + 0.3, HOLE.y, 4.0), color=(0.75, 0.8, 1.0), energy=25, radius=0.3)
T.point_light("Licht_slaapkamer", (HOLE.x, HOLE.y, 6.6), color=(1.0, 0.85, 0.65), energy=90, radius=0.4)

# ---------------------------------------------------------------- figuren en rekwisieten
held = S.actor("hoofdpersonage", LIE, 0)
papa = S.actor("papa", V(60, 60, 0), 0, energy=0.9)
mama = S.actor("mama", STAIR_TOP, 180, energy=0.9)
mat_m = S.mat("matras", (0.62, 0.75, 0.92))
mattress = T.box("Matras", (0, 0, 0), (1.9, 0.9, 0.2), mat_m, bevel=0.06, ol=0.01)
T.box("Matras_streep", (0, 0, 0.2), (1.92, 0.25, 0.005), S.mat("matras_streep", (0.95, 0.95, 0.97)), bevel=0, ol=0).parent = mattress
T.box("Kussen", (-0.65, 0, 0.2), (0.35, 0.6, 0.12), S.mat("kussen", (0.97, 0.96, 0.93)), bevel=0.04, ol=0.006).parent = mattress
mug = prop_mug(S, "Gelijmde_mok", cracked=True, scale=1.4)

# ---------------------------------------------------------------- tijdlijn
S.hud(17, "131,072x STRONGER", t0=0.6)
S.music("cello", 0.0, 60, vol=0.22, fade_in=1.0, fade_out=1.5)
CELLO = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.06)
l1 = S.say("S18-01", gap=0.8)
WAKE = l1[0] + 1.45
UP = l1[0] + 2.95
FELL = l1[0] + 5.0
S.sfx("sfx_grond_kruimelt", 0.2, 0.25)
l2 = S.say("S18-02", gap=0.5)
FLOOR = l2[0] + 1.5
JACK = l2[0] + 5.7
S.real(l2[0] + 0.1, l2[1] + 0.2)
S.text("WOODEN FLOOR: ~200 KG/M²", FLOOR + 0.2, JACK - 0.1, loc=(0.965, 0.22), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("CAR JACK: ~2,000 KG", JACK + 0.6, l2[1] + 0.2, loc=(0.965, 0.22), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOU, ROLLING OVER: MORE", JACK + 2.4, l2[1] + 0.2, loc=(0.965, 0.14), size=50, color=GOLD, anchor=("RIGHT", "BOTTOM"))
l3 = S.say("S18-03", gap=0.6)
DRAG0, DRAG1 = l3[0] + 0.2, l3[0] + 4.5
JOKE = l3[0] + 8.3
BAD = l3[0] + 9.3
l4 = S.say("S18-04", gap=0.9)
TEA = l4[0] + 0.2
MUG = l4[0] + 2.2                              # 'In the mug.'
GLUED = l4[0] + 3.58                           # 'The glued one.'
GIVE = GLUED - 0.5
SAYS = l4[0] + 5.3
SITS = l4[0] + 6.9
S.wait(2.6)
END = S.t
CELLO["loop_to"] = TEA
S.music("mok_thema", TEA - 0.6, END + 0.3, vol=0.24, fade_in=1.2, fade_out=1.2)

# ---------------------------------------------------------------- wakker worden in het puin
key(held.rig, 0.0, loc=LIE, rot=(-90, 0, 0), interp="CONSTANT")
S.beat(held, 0.0, "staan", face="neutraal", face_amt=1.0, ogen_knijp=1.0, mond_verdrietig=0.2)
S.beat(held, WAKE - 0.1, "staan", face="neutraal", face_amt=1.0, ogen_knijp=1.0)
S.beat(held, WAKE + 0.15, "staan", face="geschrokken", face_amt=0.8, look=(0, 0))
S.beat(held, WAKE + 1.0, "staan", face="verbaasd", face_amt=0.8, look=(0.3, 0.6))
for t in frange(0.3, FELL, 0.9):
    S.debris(HOLE + V(0, 0, -0.05), t, n=4, size=(0.008, 0.02), color=(0.7, 0.6, 0.45), speed=(0.05, 0.2), up=0.0,
             direction=(0, 0, -1), spread=0.4, life=2.4, floor=0.02, name="Gruis_val")
# rechtop zitten (snede op FELL)
SITF, _ = sit(held, seat_top=0.0, lean=6, spread=0.2)
key(held.rig, FELL - 1 / FPS, loc=LIE, rot=(-90, 0, 0), interp="CONSTANT")
key(held.rig, FELL, loc=SIT_AT, rot=(0, 0, 0), interp="CONSTANT")
S.beat(held, FELL, **SITF, pose="staan", face="verbaasd", face_amt=0.7, look=(0, 0.8), body={"head": (-30, 0, 0), "neck": (-10, 0, 0)},
       arms=arm("R", (0.2, 0.3, 0.9), (-0.6, 0.2, 0.75)))
S.beat(held, FELL + 1.4, **SITF, pose="staan", face="verdrietig", face_amt=0.6, look=(0, 0.7), body={"head": (-26, 0, 0)})
S.beat(held, JACK, **SITF, pose="staan", face="nerveus", face_amt=0.7, look=(0, -0.6), body={"head": (16, 0, 0)}, arms=LOOK_HANDS)
S.beat(held, l2[1], **SITF, pose="staan", face="verdrietig", face_amt=0.7, look=(0, -0.6), body={"head": (18, 0, 0)}, arms=LOOK_HANDS)

# ---------------------------------------------------------------- de matras naar de wasmachine
ease = lambda u: smooth(0, 1, u) * 0.5 + u * 0.5
mat_at = lambda t: MAT0.lerp(MAT1, ease(max(0.0, min(1.0, (t - DRAG0) / (DRAG1 - DRAG0)))))
mfr = list(range(F(DRAG0) - 1, F(DRAG1) + 2))
key(mattress, 0.0, loc=MAT0 + V(0, 0, 0.12))
bake(mattress, "location", mfr, [tuple(mat_at((f - 1) / FPS) + V(0, 0, 0.12 if (f - 1) / FPS < DRAG1 else 0.0)) for f in mfr])
key(mattress, DRAG1 + 0.25, loc=MAT1)
P_DAD0, P_DAD1 = MAT0 + V(-1.2, 0, 0), MAT1 + V(-1.2, 0, 0)
P_HERO0, P_HERO1 = MAT0 + V(1.2, 0, 0), MAT1 + V(1.2, 0, 0)
S.teleport(papa, l2[1] + 0.3, P_DAD0, 90)
S.teleport(held, l2[1] + 0.3, P_HERO0, -90)
S.walk(papa, DRAG0, DRAG1, [P_DAD0, P_DAD1], stride=0.3, turn=False, arms=None)
S.walk(held, DRAG0, DRAG1, [P_HERO0, P_HERO1], stride=0.3, turn=False, arms=None)
CARRY = dict(pose="staan", crouch=(0.12, 18.0))
S.beat(papa, l2[1] + 0.3, **CARRY, face="neutraal", face_amt=0.8, look=(0, -0.3), body={"head": (8, 0, 0)})
S.beat(held, l2[1] + 0.3, **CARRY, face="verdrietig", face_amt=0.5, look=(0, -0.3))
for t in frange(l2[1] + 0.3, DRAG1 + 0.4, 0.4):
    c = mat_at(t) + V(0, 0, 0.32)
    for ch, sx in ((papa, -0.95), (held, 0.95)):
        for side, sy in (("L", 0.22), ("R", -0.22)):
            S.reach(ch, t, side, c + V(sx, sy if ch is papa else -sy, 0), inf=1.0)
for ch in (papa, held):
    for side in "LR":
        S.reach(ch, DRAG1 + 0.8, side, None, inf=0.0)
S.beat(papa, DRAG1 + 0.4, **CARRY, face="neutraal", face_amt=0.8, look=(0, -0.3), feet="keep")
S.beat(papa, DRAG1 + 0.9, "staan", face="neutraal", face_amt=1.0, at=S.head(held, DRAG1), mond_verdrietig=0.3)
S.beat(papa, JOKE, "staan", face="neutraal", face_amt=1.0, at=S.head(held, DRAG1), mond_verdrietig=0.4, wenkbrauw_boos=-0.2)
S.hold(papa, l3[1] + 0.3)
S.teleport(papa, l3[1] + 0.4, V(60, 60, 0), 0)
S.beat(held, DRAG1 + 0.9, "staan", face="verdrietig", face_amt=0.6, look=(0, -0.4))
S.beat(held, JOKE + 0.3, "staan", face="verdrietig", face_amt=0.7, at=S.head(papa, JOKE))
S.beat(held, BAD + 0.2, "staan", face="verdrietig", face_amt=0.9, look=(0.2, -0.5), body={"head": (12, 0, 0)})

# ---------------------------------------------------------------- mama brengt thee en gaat naast hem zitten
HERO_SIT = V(-0.95, 1.45, 0.0)
SITM, rz = sit(held, seat_top=0.2, lean=8, spread=0.18)
S.teleport(held, l3[1] + 0.4, HERO_SIT + V(0, 0, rz), 0)
S.beat(held, l3[1] + 0.4, **SITM, pose="staan", face="verdrietig", face_amt=0.7, look=(0, -0.4), body={"head": (14, 0, 0)},
       arms=arms(arm("L", (0.2, 0.55, -0.8), (-0.1, 0.9, -0.2)), arm("R", (0.2, 0.55, -0.8), (-0.1, 0.9, -0.2))))
S.beat(held, TEA + 0.4, **SITM, pose="staan", face="verdrietig", face_amt=0.5, at=S.head(mama, TEA) + V(0, 0, 1.2))
S.hold(held, GIVE - 0.3)
CUP = arms(arm("L", (0.15, 0.6, -0.78), (-0.35, 0.9, 0.2)), arm("R", (0.15, 0.6, -0.78), (-0.35, 0.9, 0.2)))
S.beat(held, GIVE, **SITM, pose="staan", face="neutraal", face_amt=0.6, look=(0, 0.4), arms=CUP)
S.beat(held, GLUED + 0.2, **SITM, pose="staan", face="verdrietig", face_amt=0.5, look=(0, -0.6), arms=CUP, body={"head": (18, 0, 0)})
S.beat(held, SITS, **SITM, pose="staan", face="blij", face_amt=0.25, look=(-0.3, -0.5), arms=CUP, body={"head": (14, 0, -10)},
       mond_verdrietig=0.3)
S.hold(held, END)

S.place(mama, 0.0, STAIR_TOP, 180)
GIVE_AT = HERO_SIT + V(-0.05, -0.75, 0)
S.walk(mama, l3[1] - 0.6, l4[0] + 1.4, [STAIR_TOP, STAIR_BOT], stride=0.25, arms=None)
S.walk(mama, l4[0] + 1.5, GIVE - 0.3, [STAIR_BOT, V(-1.9, -0.6, 0), GIVE_AT], stride=0.45, arms=None, end_rot=180)
TRAY = arm("R", (0.15, 0.55, -0.8), (-0.2, 0.95, 0.2))
S.beat(mama, 0.0, "staan", face="verdrietig", face_amt=0.4, look=(0, -0.6), arms=TRAY, feet="keep")
S.beat(mama, MUG, "staan", face="verdrietig", face_amt=0.4, at=S.head(held, MUG), arms=TRAY, feet="keep")
S.beat(mama, GIVE - 0.2, "staan", crouch=(0.1, 18), face="blij", face_amt=0.25, at=S.head(held, GIVE), arms=HAND_OUT_R, mond_verdrietig=0.3)
S.beat(mama, GIVE + 0.4, "staan", crouch=(0.06, 10), face="blij", face_amt=0.2, at=S.head(held, GIVE), mond_verdrietig=0.3)
MOM_SIT = HERO_SIT + V(-0.68, 0.05, 0)
S.walk(mama, GLUED + 0.3, SAYS - 0.3, [GIVE_AT, MOM_SIT + V(0, -0.35, 0)], stride=0.3, end_rot=0)
SITMM, rzm = sit(mama, seat_top=0.2, lean=10, spread=0.16)
S.teleport(mama, SAYS - 0.05, MOM_SIT + V(0, 0, rzm), 0)
S.beat(mama, SAYS - 0.05, **SITMM, pose="ontspannen", face="verdrietig", face_amt=0.4, look=(0, -0.3))
S.beat(mama, SITS, **SITMM, pose="ontspannen", face="blij", face_amt=0.3, at=S.head(held, SITS), body={"head": (6, 0, 10)},
       mond_verdrietig=0.3, arms=arm("L", (0.6, -0.2, -0.75), (0.75, 0.6, -0.1)))
S.hold(mama, END)
grab(S, mug, mama, 0.0, "hand.R", (0, 0.05, 0.05), (90, 0, 0), release=GIVE)
grab(S, mug, held, GIVE, "hand.R", (0.04, 0.05, 0.05), (90, 0, 20))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-0.3, -1.15, 2.05), (-0.6, -0.15, 0.15), 24), ((-0.35, -1.0, 1.95), (-0.6, -0.1, 0.15), 28))
S.cam(UP - 0.1, ((HOLE.x, HOLE.y - 0.05, 0.4), (HOLE.x - 0.02, HOLE.y + 0.05, 6.5), 18), ((HOLE.x, HOLE.y - 0.05, 0.4), (HOLE.x - 0.02, HOLE.y + 0.05, 6.5), 22))
S.cam(FELL - 0.05, ((-0.25, -1.55, 0.85), (-0.6, 0.3, 0.6), 28), ((-0.3, -1.4, 0.82), (-0.6, 0.3, 0.6), 30))
S.cam(FLOOR - 0.1, ((1.0, -0.6, 1.1), (-0.05, 0.35, 2.3), 20), ((0.85, -0.45, 1.15), (-0.2, 0.4, 2.3), 22))
HC = S.headpos(held, JACK + 0.5)
S.cam(JACK - 0.1, (HC + V(0.5, -1.55, -0.1), HC + V(0, 0, -0.3), 30), (HC + V(0.45, -1.4, -0.1), HC + V(0, 0, -0.28), 32))
S.cam(l3[0] - 0.2, ((0.6, -2.45, 1.5), (0.0, 1.4, 0.5), 22), ((0.2, -2.45, 1.45), (-0.8, 1.4, 0.5), 24))
DH = S.head(papa, JOKE)
S.cam(JOKE - 0.25, (DH + V(1.4, -0.6, -0.12), DH + V(0, 0, -0.22), 32), (DH + V(1.28, -0.55, -0.12), DH + V(0, 0, -0.22), 34))
HH = S.headpos(held, BAD)
S.cam(BAD - 0.1, (HH + V(-1.35, -0.55, -0.4), HH + V(0, 0, -0.22), 32), (HH + V(-1.22, -0.5, -0.38), HH + V(0, 0, -0.22), 35))
S.cam(l3[1] + 0.4, ((-0.9, -2.45, 0.7), (-2.45, -1.0, 1.85), 18), ((-0.95, -2.45, 0.7), (-2.4, -1.3, 1.45), 20))
S.cam(l4[0] + 1.6, ((-0.15, -1.25, 1.1), (-1.05, 1.0, 0.95), 24), ((-0.2, -1.1, 1.08), (-1.0, 1.0, 0.92), 26))
S.cam(GLUED - 0.1, ((-0.3, 0.42, 0.98), (-0.95, 1.2, 0.58), 36), ((-0.33, 0.48, 0.96), (-0.95, 1.2, 0.58), 40))
S.cam(SAYS - 0.1, ((0.7, -1.9, 0.95), (-1.3, 1.4, 0.65), 26), ((0.5, -1.6, 0.9), (-1.3, 1.4, 0.65), 32))

S.finish(length=END)
