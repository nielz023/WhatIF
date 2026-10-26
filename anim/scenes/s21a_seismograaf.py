"""S21a · Dag 20 · wakker worden in de kelder. 'One million times.' De seismograaf van de universiteit
slaat uit: geen aardbeving, hij, die uit bed stapt.

    blender -b -P anim/scenes/s21a_seismograaf.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s21a", "kleine_interieurs", "kelder")

MAT = V(-1.3, 1.45, 0.0)                       # matras naast de wasmachine (sinds dag 17)
LIE = V(-0.45, 1.45, 0.24)                     # liggend: voeten bij +x, hoofd op het kussen (-x)
SIT_AT = V(-1.45, 1.22, 0.0)
STAND_AT = V(-1.45, 0.82, 0.0)
DK = V(0.0, -230.0, 0.0)                       # de universiteit: een los decor ver weg
RED = (1.0, 0.25, 0.2, 1)

# ---------------------------------------------------------------- de matras
mattress = T.box("Matras", tuple(MAT), (1.9, 0.9, 0.2), S.mat("matras", (0.62, 0.75, 0.92)), bevel=0.06, ol=0.01)
T.box("Matras_streep", (MAT.x, MAT.y, 0.2), (1.92, 0.25, 0.005), S.mat("matras_streep", (0.95, 0.95, 0.97)), bevel=0, ol=0)
T.box("Kussen_matras", (MAT.x - 0.65, MAT.y, 0.2), (0.35, 0.6, 0.12), S.mat("kussen", (0.97, 0.96, 0.93)), bevel=0.04, ol=0.006)
deken = T.box("Deken", (MAT.x + 0.25, MAT.y, 0.2), (1.3, 0.95, 0.06), S.mat("deken", (0.85, 0.45, 0.2)), bevel=0.03, ol=0.008)
mug = prop_mug(S, "Gelijmde_mok", (MAT.x - 0.4, MAT.y - 0.62, 0.0), cracked=True, scale=1.4)
T.point_light("Ochtendlicht_gat", (-0.6, 0.5, 3.2), color=(0.85, 0.9, 1.0), energy=60, radius=0.4)

# ---------------------------------------------------------------- de universiteit: seismograaf
dm = S.mat("lab_muur", (0.80, 0.84, 0.86))
T.box("Uni_vloer", (DK.x, DK.y, -0.1), (7, 6, 0.1), S.mat("lab_vloer", (0.45, 0.48, 0.52)), bevel=0, ol=0)
T.box("Uni_muur", (DK.x, DK.y + 1.6, 0), (7, 0.15, 3.0), dm, bevel=0, ol=0.01)
T.box("Uni_raam", (DK.x + 1.8, DK.y + 1.51, 1.1), (1.6, 0.02, 1.1), S.mat("uni_raam", (0.75, 0.85, 1.0), 1.5), bevel=0, ol=0.006)
T.box("Uni_bord", (DK.x - 1.9, DK.y + 1.51, 1.2), (1.4, 0.02, 0.9), S.mat("uni_bord", (0.15, 0.25, 0.2)), bevel=0, ol=0.006)
T.text("Uni_bord_tekst", "SEISMOLOGY", (DK.x - 1.9, DK.y + 1.49, 1.85), 0.14, S.mat("krijt", (0.95, 0.95, 0.9)), extrude=0.0)
T.box("Uni_tafel", (DK.x, DK.y + 0.9, 0), (2.4, 0.9, 0.78), S.mat("lab_tafel", (0.55, 0.42, 0.30)), bevel=0.01, ol=0.008)
T.box("Seismo_voet", (DK.x - 0.1, DK.y + 0.9, 0.78), (0.8, 0.45, 0.08), S.mat("seismo_metaal", (0.35, 0.37, 0.42)), bevel=0.01, ol=0.005)
drum = T.cyl("Seismo_trommel", (0, 0, 0), 0.13, 0.62, S.mat("seismo_papier", (0.97, 0.96, 0.92)), rot=(0, 90, 0), seg=28, ol=0.004)
drum.location = (DK.x - 0.41, DK.y + 0.9, 1.0)
for x in (-0.47, 0.25):
    T.box(f"Seismo_steun{x}", (DK.x + x, DK.y + 0.9, 0.86), (0.04, 0.1, 0.16), S.mat("seismo_metaal", (0.35, 0.37, 0.42)), bevel=0, ol=0.004)
# papierstrook die van de trommel naar voren loopt, met de lijn erop
PAPER0 = V(DK.x - 0.1, DK.y + 0.6, 0.87)
paper = T.box("Seismo_strook", (0, 0, 0), (0.55, 0.9, 0.003), S.mat("seismo_papier", (0.97, 0.96, 0.92)), base=False, bevel=0, ol=0.003)
paper.location = PAPER0 + V(0, -0.2, 0)
# naald: arm op een scharnier achter de trommel
arm_o = T.box("Seismo_naald", (0, -0.16, 0), (0.012, 0.32, 0.012), S.mat("naald", (0.15, 0.15, 0.18)), base=False, bevel=0, ol=0.003)
tip = T.sphere("Seismo_punt", (0, -0.32, 0), 0.012, S.mat("inkt", (0.85, 0.1, 0.1)), seg=8, ol=0)
tip.parent = arm_o
needle = hinge(arm_o, (DK.x - 0.1, DK.y + 1.05, 0.9))
screen = T.box("Uni_scherm", (DK.x + 0.85, DK.y + 1.15, 0.78), (0.6, 0.05, 0.4), P.m("zwart"), bevel=0.01, ol=0.005)
glow = T.box("Uni_scherm_beeld", (DK.x + 0.85, DK.y + 1.12, 0.81), (0.55, 0.005, 0.34), S.mat("scherm_rood", (1.0, 0.2, 0.15), 3.0), bevel=0, ol=0)
T.text("Uni_scherm_tekst", "ALERT", (DK.x + 0.85, DK.y + 1.115, 0.93), 0.09, S.mat("scherm_wit", (1, 1, 1), 4.0), extrude=0.0)
coffee = prop_mug(S, "Koffiemok_uni", (DK.x + 0.5, DK.y + 0.65, 0.78), scale=1.2)
T.area_light("Uni_licht", (DK.x, DK.y - 0.5, 2.8), (0, 0, 0), size=(4, 3), color=(0.95, 0.97, 1.0), energy=500)
T.point_light("Uni_ochtend", (DK.x + 1.8, DK.y + 1.0, 1.6), color=(1.0, 0.9, 0.75), energy=80, radius=0.3)
prof = S.actor("wetenschapper", DK + V(0.2, -0.05, 0), 0, energy=0.9)
stool = T.cyl("Uni_kruk", (DK.x + 0.2, DK.y + 0.1, 0), 0.2, 0.5, S.mat("kruk", (0.2, 0.2, 0.25)), seg=16, ol=0.006)

# ---------------------------------------------------------------- tijdlijn
S.hud(20, "1,048,576x STRONGER", t0=0.3, color=RED)
for t in (0.35, 1.15, 1.95):                   # de teller knippert rood
    S.card("", t, t + 0.12, bg=(0.75, 0.02, 0.02), dim=0.22, fin=2, fout=8)
S.music("drone", 0.0, 60, vol=0.2, fade_in=0.8, fade_out=1.0)
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.05)
l1 = S.say("S21-01", gap=0.6)
MILLION = l1[0] + 3.2                          # 'One million times.'
l2 = S.say("S21-02", gap=0.7)
WAKE = l2[0] + 0.1
UNI = l2[0] + 1.3                              # 'the seismograph at the university'
NOT_EQ = l2[0] + 3.72                          # 'Not an earthquake.'
YOU = l2[0] + 5.45                             # 'You.'
BED = l2[0] + 6.17                             # 'Getting out of bed.'
STEP = BED + 0.55
S.wait(1.4)
END = S.t
S.sfx("sfx_seismograaf", UNI - 0.2, 0.22)
S.sfx("sfx_grond_kruimelt", STEP - 0.05, 0.28)
S.sfx("sfx_dreun", STEP, 0.18)
S.text("UNIVERSITY SEISMOGRAPH", UNI + 0.1, NOT_EQ - 0.1, loc=(0.965, 0.22), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("MAGNITUDE 1.9", UNI + 0.9, YOU - 0.1, loc=(0.965, 0.14), size=56, color=RED, anchor=("RIGHT", "BOTTOM"))
S.gauge("EPICENTER: YOUR BASEMENT", YOU, END)

# ---------------------------------------------------------------- de seismograaf: trommel draait, naald slaat uit
amp = lambda t: 0.004 + 0.13 * smooth(WAKE - 0.2, WAKE + 0.4, t) * (1 - 0.6 * smooth(NOT_EQ, YOU, t)) + 0.16 * smooth(STEP - 0.1, STEP + 0.1, t)
fr = list(range(1, F(END) + 2))
rnd = random.Random(20)
jit = [rnd.uniform(-1, 1) for _ in fr]
bake(needle, "rotation_euler", fr, [(0, 0, max(-0.5, min(0.5, amp((f - 1) / FPS) * 3.2 * math.sin(f * 2.3) * (0.6 + 0.4 * jit[i]))))
                                     for i, f in enumerate(fr)])
bake(drum, "rotation_euler", fr, [((f - 1) / FPS * 1.2, math.radians(90), 0) for f in fr])
# de getekende lijn op de strook: de strook schuift naar voren, de lijn groeit mee
V_PAPER = 0.035
trace_pts = []
for i, f in enumerate(fr[::2]):
    t = (f - 1) / FPS
    a = amp(t) * 3.2 * math.sin(f * 2.3) * (0.6 + 0.4 * jit[fr.index(f)])
    trace_pts.append((math.sin(max(-0.5, min(0.5, a))) * 0.32, -t * V_PAPER, 0.0025))
trace = T.tube("Seismo_lijn", trace_pts, 0.0018, S.mat("inkt", (0.85, 0.1, 0.1)))
trace.data.bevel_factor_mapping_end = "SPLINE"
trace.location = PAPER0 + V(0, 0.18, 0)
for t in frange(0.0, END + 0.2, 0.2):
    trace.data.bevel_factor_end = min(1.0, t / (END + 0.2))
    trace.data.keyframe_insert("bevel_factor_end", frame=F(t))
    trace.location = PAPER0 + V(0, 0.18 + t * V_PAPER, 0)
    trace.keyframe_insert("location", frame=F(t))
# de koffie trilt
for t in frange(WAKE, NOT_EQ, 0.08):
    key(coffee, t, loc=(DK.x + 0.5 + rnd.uniform(-0.01, 0.01), DK.y + 0.65 + rnd.uniform(-0.01, 0.01), 0.78))
key(coffee, NOT_EQ + 0.1, loc=(DK.x + 0.5, DK.y + 0.65, 0.78))

# de wetenschapper: ingedut op de kruk, schrikt wakker, buigt zich over de strook
SIT_P, zp = sit(prof, seat_top=0.5, lean=10)
S.place(prof, 0, DK + V(0.2, 0.1, zp), 0 + 180)
S.beat(prof, 0.0, **SIT_P, pose="ontspannen", face="neutraal", face_amt=1.0, ogen_knijp=1.0, body={"head": (24, 0, 10)})
S.beat(prof, UNI + 0.5, **SIT_P, pose="ontspannen", face="neutraal", face_amt=1.0, ogen_knijp=1.0, body={"head": (24, 0, 10)})
S.beat(prof, UNI + 0.75, **SIT_P, pose="schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, -0.2))
S.beat(prof, UNI + 1.6, **SIT_P, pose="staan", face="verbaasd", face_amt=1.0, at=PAPER0, body={"spine": (20, 0, 0), "chest": (10, 0, 0)})
S.beat(prof, NOT_EQ + 0.3, **SIT_P, pose="staan", face="verbaasd", face_amt=0.9, at=PAPER0, body={"spine": (24, 0, 0), "chest": (12, 0, 0)},
       arms=HOLD_FRONT_R)
S.hold(prof, END)

# ---------------------------------------------------------------- hij: ligt, ogen open, zit, staat heel voorzichtig op
held = S.actor("hoofdpersonage", LIE, 0)
key(held.rig, 0.0, loc=LIE, rot=(-90, 0, 90), interp="CONSTANT")
S.beat(held, 0.0, "staan", face="neutraal", face_amt=1.0, ogen_knijp=1.0, mond_verdrietig=0.2)
S.beat(held, MILLION - 0.1, "staan", face="neutraal", face_amt=1.0, ogen_knijp=1.0)
S.beat(held, MILLION + 0.3, "staan", face="nerveus", face_amt=0.6, look=(0, 0.3))
SITF, _ = sit(held, seat_top=0.2, lean=6, spread=0.2)
key(held.rig, WAKE - 1 / FPS, loc=LIE, rot=(-90, 0, 90), interp="CONSTANT")
key(held.rig, WAKE, loc=SIT_AT, rot=(0, 0, 0), interp="CONSTANT")
S.beat(held, WAKE, **SITF, pose="staan", face="nerveus", face_amt=0.7, look=(0, -0.5), body={"head": (12, 0, 0)})
S.beat(held, WAKE + 1.0, **SITF, pose="staan", face="verdrietig", face_amt=0.5, look=(0, -0.5), body={"head": (16, 0, 0)}, arms=LOOK_HANDS)
S.hold(held, YOU - 0.3)
S.beat(held, YOU, **SITF, pose="staan", face="nerveus", face_amt=0.8, look=(0, -0.7), body={"head": (22, 0, 0)},
       arms=arms(arm("L", (0.4, 0.3, -0.85), (0.3, 0.2, -0.93)), arm("R", (0.4, 0.3, -0.85), (0.3, 0.2, -0.93))))
S.place(held, BED, SIT_AT)
S.place(held, STEP, STAND_AT)
S.beat(held, STEP, "staan", crouch=(0.08, 14), face="inspanning", face_amt=0.5, look=(0, -0.7), body={"head": (20, 0, 0)},
       arms=arms(arm("L", (0.5, 0.2, -0.8), (0.6, 0.2, -0.7)), arm("R", (0.5, 0.2, -0.8), (0.6, 0.2, -0.7))))
S.beat(held, STEP + 0.6, "staan", face="nerveus", face_amt=0.9, look=(0, -0.8), body={"head": (24, 0, 0)},
       arms=arms(arm("L", (0.5, 0.2, -0.8), (0.6, 0.2, -0.7)), arm("R", (0.5, 0.2, -0.8), (0.6, 0.2, -0.7))))
S.beat(held, END - 0.5, "staan", face="verdrietig", face_amt=0.7, look=(0.3, 0.6), body={"head": (-14, 0, 0)})
S.hold(held, END)

# de betonvloer barst onder zijn voeten, gruis van de balken, de wasmachine springt op
crack_m = S.mat("barst_beton", (0.18, 0.17, 0.16))
rc = random.Random(21)
for k in range(9):
    a = k / 9 * 2 * math.pi + rc.uniform(-0.2, 0.2)
    pts, p = [], STAND_AT + V(0, 0, 0.004)
    for j in range(5):
        pts.append(tuple(p))
        a += rc.uniform(-0.5, 0.5)
        p = p + V(math.cos(a), math.sin(a), 0) * rc.uniform(0.12, 0.3)
    c = T.tube(f"Vloerbarst_{k}", pts, 0.008, crack_m)
    c.data.bevel_factor_end = 0.0
    c.data.keyframe_insert("bevel_factor_end", frame=F(STEP))
    c.data.bevel_factor_end = 1.0
    c.data.keyframe_insert("bevel_factor_end", frame=F(STEP + 0.35))
S.puff(STAND_AT + V(0, 0, 0.05), STEP, n=6, r=(0.08, 0.18), grow=2.0, dur=1.2, rise=0.25, spread=0.5)
for x in (-1.6, -0.4, 0.8):
    S.debris(V(x, 1.5, 2.12), STEP + 0.05, n=6, size=(0.01, 0.025), color=(0.6, 0.5, 0.4), speed=(0.05, 0.3), up=0.0,
             direction=(0, 0, -1), spread=0.5, life=1.8, floor=0.01, name="Gruis_val")
wm = S.obj("Wasmachine")
w0 = wm.location.copy()
key(wm, STEP - 0.02, loc=w0)
key(wm, STEP + 0.08, loc=w0 + V(0.01, 0, 0.05))
key(wm, STEP + 0.2, loc=w0)
bulb = [S.obj(n) for n in ("Peertje", "Peertje_snoer")]
piv = bpy.data.objects.new("Peertje_scharnier", None)
T._link(piv)
piv.location = (0, 0, 2.3)
for o in bulb:
    o.parent = piv
    o.matrix_parent_inverse = Matrix.Translation(piv.location).inverted()
for k, t in enumerate(frange(STEP, END, 0.35)):
    key(piv, t, rot=(10 * math.exp(-(t - STEP) * 0.9) * (1 if k % 2 else -1), 0, 0))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-1.15, 1.2, 2.12), (-1.2, 1.45, 0.3), 22), ((-1.2, 1.25, 2.05), (-1.25, 1.45, 0.3), 26))
S.cam(WAKE - 0.05, ((-0.9, -0.9, 0.95), (-1.45, 1.3, 0.62), 28), ((-0.95, -0.75, 0.95), (-1.45, 1.3, 0.62), 30))
S.cam(UNI - 0.1, ((DK.x + 2.2, DK.y + 1.15, 1.5), (DK.x + 0.1, DK.y + 0.3, 1.05), 28), ((DK.x + 2.0, DK.y + 1.1, 1.45), (DK.x + 0.1, DK.y + 0.3, 1.05), 30),
      shake=lambda t: 0.5 * smooth(WAKE, WAKE + 0.5, t))
S.cam(NOT_EQ - 0.15, ((DK.x + 1.5, DK.y + 1.2, 1.45), (DK.x - 0.05, DK.y + 0.6, 0.95), 32), ((DK.x + 1.35, DK.y + 1.15, 1.4), (DK.x - 0.05, DK.y + 0.6, 0.95), 36),
      shake=lambda t: 0.4)
S.cam(YOU - 0.15, (S.headpos(held, YOU) + V(0.25, -1.1, -0.05), S.headpos(held, YOU) + V(0, 0, -0.12), 34),
      (S.headpos(held, YOU) + V(0.22, -0.95, -0.05), S.headpos(held, YOU) + V(0, 0, -0.1), 38))
S.cam(BED, ((0.6, -1.7, 0.75), (-1.45, 0.9, 0.55), 24), ((0.5, -1.55, 0.8), (-1.45, 0.9, 0.6), 26),
      shake=lambda t: max(0.0, 1.0 - (t - STEP) * 1.3) if t > STEP else 0.0)

S.finish(length=END)
