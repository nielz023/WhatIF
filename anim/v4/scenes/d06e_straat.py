"""D06e · De vuilniswagen en de Hayflick-grens (script scène 6e-6i). Straat, zonnig.
6e  WIDE 3 s, handheld: hij stapt van de stoep zonder te kijken; de vuilniswagen raakt hem; hij maakt een radslag door
    de lucht en landt op zijn voeten. Deuk in de vorm van een jongen.
6f  CLOSE 2,6 s: de vuilnisman kijkt naar de deuk, dan naar de jongen.  "...I'm gonna need a form for this."
6g  DETAIL 3 s: het filmpje op de telefoon van de vriend: 4.2M, 11M, 38M views.
6h  CLOSE 3,3 + 3,2 s: hij zit op de stoeprand, kijkt naar zijn hand.
    VO: "This part is real. Your cells can only copy themselves about fifty times. Then they stop."
6h2 DETAIL 5 s: microscoop: een cel deelt, en nog eens, wordt grijs en stopt; zijn cel blijft delen.
    VO: "Scientists call it the Hayflick limit. It's the reason everybody gets old."
6i  CLOSE 2,5 s: VO "Everybody... except you."

    python3 anim/v4/scenes/d06e_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403
from lib import street as STR  # noqa: E402

S = Scene4("d06e", "straat", "zonnig", exposure=0.2)
sh = S.cuts([3.0, 2.6, 3.0, 3.3, 3.2, 5.0, 2.5])
END = sh[-1][1]
t_f, t_g, t_h, t_h1, t_m, t_i = (s[0] for s in sh[1:])

# ---------------------------------------------------------------- de vuilniswagen
S.hide("Auto_overkant_2")                     # geparkeerde auto precies waar hij op de stoeprand zit
STR.garbage_truck("Vuilniswagen", (0, 0, 0), rot=0, lights=False)
truck = S.obj("Vuilniswagen")
TY_ = -1.3
HX = 0.3                                              # hier wordt hij geraakt
T_HIT = 1.3
X_HIT = HX - 4.25 - 0.12
X_STOP = X_HIT + 3.6
for t, x in ((0.0, X_HIT - 9.0 * T_HIT), (T_HIT, X_HIT), (T_HIT + 0.9, X_STOP), (END, X_STOP)):
    key(truck, t, loc=(x, TY_, 0.0))
for fc in A._fcurves(truck):
    fc.keyframe_points[0].interpolation = "LINEAR"
# chauffeur in de cabine (rijdt mee via Child Of; stapt "uit" als de vuilnisman in 6f naast de wagen staat)
drv = S.actor("vuilnisman", (3.45, 0.55, 0.0), 90, label="vuilnisman_cabine")
ds, dz = sit(drv, seat_top=1.25)
S.place(drv, 0, V(3.45, 0.55, dz), 90)
S.beat(drv, 0.0, **ds, face="neutraal", face_amt=0.4, look=(0.0, 0.0))
S.beat(drv, T_HIT - 0.15, **ds, face="geschrokken", face_amt=0.9, look=(0.0, -0.2))
S.hold(drv, END)
_co = drv.rig.constraints.new("CHILD_OF")
_co.target = truck
_co.set_inverse_pending = False
_co.inverse_matrix = Matrix.Identity(4)
S.qc_skip.add(drv.name)
show(drv.rig, 0.0, t_f - 0.05)
# deuk in de vorm van een jongen (vanaf de klap)
dm = S.mat("deuk_donker", (0.55, 0.56, 0.58))
deuk = [T.sphere("Deuk_hoofd", (4.29, -1.45, 1.55), 0.24, dm, scale=(0.08, 1, 1), seg=16, ol=0),
        T.box("Deuk_lijf", (4.29, -1.45, 0.72), (0.03, 0.34, 0.6), dm, bevel=0.06, ol=0)]
for o in deuk:                                    # lokaal t.o.v. de wagen: voorkant x 4,25, waar hij stond
    o.parent = truck
    show(o, T_HIT)

# ---------------------------------------------------------------- de vriend filmt vanaf de stoep
vriend = S.actor("beste_vriend", (-2.6, -5.0, 0.12), 140)
phone = prop_phone(S, "Telefoon_vriend")
grab(S, phone, vriend, 0.0, "hand.L", loc=(0, 0.06, 0.0))
S.beat(vriend, 0.0, "filmen", face="lach", face_amt=0.8, at=V(HX, -3.0, 1.2))
S.beat(vriend, T_HIT + 0.1, "filmen", face="geschrokken", face_amt=1.0, at=V(HX + 3, -2.4, 1.8))
S.beat(vriend, T_HIT + 1.2, "filmen", face="verbaasd", face_amt=1.0, at=V(HX + 6.5, -2.4, 1.2))
S.hold(vriend, END)

# ---------------------------------------------------------------- hij: van de stoep, geraakt, radslag, landt op zijn voeten
held = S.actor("hoofdpersonage_kind", (HX, -4.7, 0.12), 180)
P_ = held.J["pelvis"].z
hb = Body(S, held, (HX, -4.7, 0.12 + P_), 180)
S.qc_skip.add(held.name)
STEP_A = dict(crouch=(0.03, 4), feet=((0, 0.16, 0.06), (0, -0.12, 0.0)))
STEP_B = dict(crouch=(0.03, 4), feet=((0, -0.12, 0.0), (0, 0.16, 0.06)))
LOOK_BACK = {"head": (0, 0, 0), "neck": (0, 0, 0)}
pts = [(0.0, V(HX, -4.7, 0.12 + P_)), (0.6, V(HX, -3.9, 0.12 + P_)), (0.95, V(HX, -3.35, P_ + 0.02)), (T_HIT, V(HX, -2.75, P_))]
for t, p in pts:
    hb.key(t, p)
for k, t in enumerate(frange(0.0, T_HIT, 0.22)):
    S.beat(held, t, "staan", face="lach", face_amt=0.9, look=(-0.8, 0.0),
           body={"head": (0, -45, 0), "neck": (0, -20, 0)}, **(STEP_A if k % 2 else STEP_B))     # kijkt achterom naar de vriend
FLY = [(T_HIT + 0.02, V(HX + 0.3, -2.75, P_ + 0.1), 0), (T_HIT + 0.35, V(HX + 2.6, -2.6, 2.3), -150),
       (T_HIT + 0.7, V(HX + 4.6, -2.5, 2.4), -290), (T_HIT + 1.05, V(HX + 6.2, -2.4, P_ + 0.25), -360),
       (T_HIT + 1.25, V(HX + 6.4, -2.4, P_ - 0.12), -360), (T_HIT + 1.6, V(HX + 6.45, -2.4, P_), -360)]
for t, p, r in FLY:
    hb.key(t, p, roll=r)
SPREAD = arms(arm("L", (0.95, 0.05, 0.25), (0.95, 0.05, 0.3)), arm("R", (0.95, 0.05, 0.25), (0.95, 0.05, 0.3)))
S.beat(held, T_HIT + 0.02, "schrik", face="geschrokken", face_amt=1.0, crouch=(0.05, -10))
S.beat(held, T_HIT + 0.3, "staan", arms=SPREAD, face="geschrokken", face_amt=1.0,
       feet=((0.25, 0.0, 0.10), (-0.25, 0.0, 0.10)))                                       # radslag: armen en benen wijd
S.beat(held, T_HIT + 0.9, "staan", arms=SPREAD, face="schreeuw", face_amt=1.0, feet=((0.22, 0.0, 0.10), (-0.22, 0.0, 0.10)))
S.beat(held, T_HIT + 1.25, "armen_omhoog", amount=0.7, face="verbaasd", face_amt=1.0, crouch=(0.22, 10))
S.beat(held, T_HIT + 1.6, "armen_omhoog", amount=0.9, face="verbaasd", face_amt=1.0, crouch=(0.02, 0))   # ta-da
S.beat(held, t_g, "staan", face="twijfel", face_amt=0.7, body={"head": (0, 30, 0)})
S.hold(held, t_h)
show(held.rig, 0.0, t_h)

# ---------------------------------------------------------------- 6f: de vuilnisman bij de deuk
DENT = V(X_STOP + 4.29, -2.25, 1.15)
vman = S.actor("vuilnisman", (X_STOP + 4.95, -3.05, 0.0), -140)
show(vman.rig, t_f - 0.05)
S.beat(vman, t_f, "staan", face="neutraal", face_amt=0.6, at=DENT)
S.beat(vman, t_f + 0.9, "staan", face="twijfel", face_amt=0.7, at=DENT + V(0, 0, -0.2))
S.beat(vman, t_f + 1.4, "staan", face="neutraal", face_amt=0.9, at=S.head(held, T_HIT + 1.6))
A.blink_at(vman, F(t_f + 2.0))
S.hold(vman, END)

# ---------------------------------------------------------------- 6g: het filmpje op een telefoon (los, groot in beeld)
PH = V(-14.0, -5.6, 1.2)                           # ergens buiten beeld van de andere shots
ph = T.box("Telefoon_detail", tuple(PH), (0.075, 0.009, 0.155), S.mat("telefoon_zwart", (0.06, 0.06, 0.07)), base=False, bevel=0.007, ol=0)
scr = T.box("Telefoon_detail_scherm", tuple(PH + V(0, -0.0052, 0)), (0.067, 0.001, 0.142), S.mat("scherm_app", (0.08, 0.08, 0.1), 1.0),
            base=False, bevel=0, ol=0)
vid = T.box("Telefoon_detail_video", tuple(PH + V(0, -0.0065, 0.03)), (0.064, 0.001, 0.036), S.mat("video_oranje", (0.95, 0.5, 0.15), 1.2),
            base=False, bevel=0, ol=0)
T.sphere("Telefoon_detail_play", tuple(PH + V(0, -0.0075, 0.03)), 0.008, S.mat("play_wit", (1, 1, 1), 2.0), scale=(1, 0.2, 1), seg=10, ol=0)
for k, (txt, t0) in enumerate((("4.2M views", t_g), ("11M views", t_g + 1.0), ("38M views", t_g + 2.0))):
    o = T.text(f"Telefoon_views_{k}", txt, tuple(PH + V(0, -0.0075, -0.02)), 0.011 if k < 2 else 0.013,
               S.mat("views_wit" if k < 2 else "views_geel", (1, 1, 1) if k < 2 else (1.0, 0.85, 0.1), 2.5), extrude=0.0005)
    show(o, 0.0 if k == 0 else t0, None if k == 2 else t0 + 1.0)
    if k:
        key(o, t0, scale=1.35)
        key(o, t0 + 0.15, scale=1.0)
T.text("Telefoon_titel", "kid vs garbage truck", tuple(PH + V(0, -0.0075, -0.006)), 0.0068, S.mat("titel_grijs", (0.8, 0.8, 0.85), 1.5),
       extrude=0.0005)

# ---------------------------------------------------------------- 6h/6i: hij zit op de stoeprand en kijkt naar zijn hand
SIT_AT = V(HX + 6.2, -3.82, 0.0)
zit = S.actor("hoofdpersonage_kind", SIT_AT, 180)
spec, rz = sit(zit, seat_top=0.12)
S.place(zit, 0, SIT_AT + V(0, 0, rz), 180)
show(zit.rig, t_h)
LOOKH_A = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 0, 0))
LOOKH_B = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 150, 0))
REST = arms(arm("L", (0.25, 0.35, -0.90), (0.05, 0.80, -0.60)))
S.beat(zit, t_h, **spec, arms=arms(REST, LOOKH_A), face="twijfel", face_amt=0.5, look=(0.0, -0.8), body={"head": (16, 0, 0)})
S.beat(zit, t_h + 1.4, **spec, arms=arms(REST, LOOKH_B), face="twijfel", face_amt=0.6, look=(0.0, -0.8), body={"head": (18, 0, 4)})
S.beat(zit, t_h1 + 0.3, **spec, arms=arms(REST, LOOKH_A), face="neutraal", face_amt=0.6, look=(0.0, -0.8), body={"head": (16, 0, -3)})
S.beat(zit, t_h1 + 2.0, **spec, arms=arms(REST, LOOKH_B), face="twijfel", face_amt=0.5, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.beat(zit, t_m + 2.5, **spec, arms=arms(REST, LOOKH_A), face="twijfel", face_amt=0.5, look=(0.0, -0.8), body={"head": (16, 0, 0)})
S.beat(zit, t_i + 0.4, **spec, arms=REST, face="neutraal", face_amt=0.7, look=(0.0, 0.0), body={"head": (-2, 0, 0)})  # kijkt op
A.blink_at(zit, F(t_h1 + 1.0))
A.blink_at(zit, F(t_i + 1.4))
S.hold(zit, END)

# ---------------------------------------------------------------- 6h2: microscoop (een eigen ruimte ver onder de straat)
M = V(0.0, 0.0, -300.0)
bg = T.sphere("Microscoop_achtergrond", tuple(M), 30.0, S.mat("microscoop_bg", (0.02, 0.05, 0.12), 0.4), seg=24, ol=0)
bg.scale = (-1, 1, 1)
rim = T.torus("Microscoop_rand", tuple(M + V(0, -2.2, 0)), 1.45, 0.6, S.mat("microscoop_rand", (0.0, 0.0, 0.0)), seg=48, seg2=12, ol=0,
              rot=(90, 0, 0))
rnd = random.Random(4)
m_cel = S.mat("cel_groen", (0.35, 0.85, 0.75), 0.8)
m_kern = S.mat("cel_kern", (0.15, 0.45, 0.55), 0.6)
m_grijs = S.mat("cel_grijs", (0.42, 0.42, 0.45), 0.15)
m_held = S.mat("cel_goud", (1.0, 0.68, 0.30), 1.2)


def cell(name, mat, r):
    o = T.sphere(name, (0, 0, 0), r, mat, seg=20, ol=0)
    k = T.sphere(name + "_kern", (0, 0, 0), r * 0.4, m_kern if mat is not m_held else S.mat("cel_kern_goud", (0.8, 0.35, 0.1), 0.8),
                 seg=12, ol=0)
    k.parent = o
    k.location = (0, -r * 0.5, 0)
    return o


def lineage(tag, c, r, t0, divs, mat, grey_at=None, gen=0, dirn=None):
    """Een cel op c die op divs[0] deelt (twee kinderen schuiven uit elkaar), enz."""
    o = cell(f"Cel_{tag}", mat, r)
    t_end = divs[0] if divs else None
    vis_end = t_end + 0.02 if t_end is not None else None
    key(o, t0 - 0.02, loc=tuple(c), scale=0.001)
    key(o, t0, loc=tuple(c), scale=0.85)
    key(o, t0 + 0.25, loc=tuple(c), scale=1.0)
    show(o, t0 - 0.02, vis_end)
    for ch in o.children:
        show(ch, t0 - 0.02, vis_end)
    if t_end is None:
        if grey_at is not None:
            g = cell(f"Cel_{tag}_grijs", m_grijs, r * 0.92)
            g.location = c
            show(g, grey_at)
            for ch in g.children:
                show(ch, grey_at)
            show(o, t0 - 0.02, grey_at)
            for ch in o.children:
                show(ch, t0 - 0.02, grey_at)
        else:
            for k_, t in enumerate(frange(t0 + 0.3, t0 + 6, 0.5)):
                key(o, t, loc=tuple(c), scale=1.0 + 0.04 * (k_ % 2))
        return
    a = rnd.uniform(0, math.pi) if dirn is None else dirn + math.pi / 2
    d = V(math.cos(a), 0, math.sin(a)) * r * 0.95
    key(o, t_end - 0.3, loc=tuple(c), scale=1.0)
    key(o, t_end, loc=tuple(c), scale=1.12)
    for s_, sgn in enumerate((1, -1)):
        lineage(f"{tag}{s_}", c + d * sgn, r * 0.78, t_end, divs[1:], mat, grey_at, gen + 1, a)


LG, RG = M + V(-0.75, 0, 0.05), M + V(0.75, 0, 0.05)
lineage("gewoon", LG, 0.24, t_m + 0.1, [t_m + 0.9, t_m + 1.9], m_cel, grey_at=t_m + 2.9)
lineage("hem", RG, 0.24, t_m + 0.1, [t_m + 0.9, t_m + 1.9, t_m + 2.9, t_m + 3.9], m_held)
lbl_m = S.mat("label_wit", (1, 1, 1), 2.0)
T.text("Label_normaal", "NORMAL CELL", tuple(M + V(-0.75, -0.05, -0.95)), 0.11, lbl_m, extrude=0.002)
T.text("Label_jij", "YOUR CELL", tuple(M + V(0.75, -0.05, -0.95)), 0.11, S.mat("label_goud", (1.0, 0.75, 0.3), 2.0), extrude=0.002)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(HX + 1.2, 5.6, 1.7), V(HX + 0.8, -2.8, 1.1), 24), (V(HX + 2.6, 5.4, 1.75), V(HX + 3.2, -2.6, 1.2), 24), handheld=0.6)
VH = S.head(vman)
S.cam(t_f, (VH + V(0.05, 1.35, -0.05), VH + V(-0.1, 0.0, -0.18), 32), (VH + V(0.04, 1.2, -0.05), VH + V(-0.1, 0.0, -0.15), 32))
S.cam(t_g, (PH + V(0.0, -0.30, 0.0), PH, 35), (PH + V(0.0, -0.23, 0.0), PH + V(0, 0, -0.005), 35), handheld=0.2)
ZH = SIT_AT + V(0, 0, 0.95)
S.cam(t_h, (ZH + V(0.55, 1.45, 0.05), ZH + V(0, 0, -0.15), 35), (ZH + V(0.48, 1.25, 0.05), ZH + V(0, 0, -0.12), 35))
S.cam(t_h1, (V(SIT_AT.x - 0.75, SIT_AT.y + 0.55, 0.95), V(SIT_AT.x, SIT_AT.y + 0.30, 0.55), 35),
      (V(SIT_AT.x - 0.68, SIT_AT.y + 0.5, 0.92), V(SIT_AT.x, SIT_AT.y + 0.30, 0.55), 35))
S.cam(t_m, (M + V(0, -3.4, 0.1), M + V(0, 0, -0.1), 35), (M + V(0, -2.9, 0.1), M + V(0, 0, -0.1), 35), handheld=0.0)
S.cam(t_i, (ZH + V(0.05, 1.05, 0.0), ZH + V(0, 0, 0.0), 40), (ZH + V(0.04, 0.9, 0.0), ZH + V(0, 0, 0.0), 40))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.sfx("sfx_vuilniswagen", 0.0, 0.25)
S.sfx("sfx_remmen", T_HIT - 0.05, 0.3)
S.sfx("sfx_dreun", T_HIT, 0.45)
S.sfx("sfx_whoosh", T_HIT + 0.2, 0.2)
S.sfx("sfx_val_klap", T_HIT + 1.1, 0.2)
S.say("D06-05", who=vman, at=t_f + 0.35)
S.sfx("sfx_meldingen", t_g + 0.9, 0.2)
S.say("D06-06", at=t_h + 0.15)
S.say("D06-07", at=t_m + 0.15)
S.say("D06-08", at=t_i + 0.1)
S.tick(END - 0.15, 0.4)
S.ambience("sfx_straat_sfeer", 0.0, t_m, vol=0.08)
S.music("funky", 0.0, t_h, vol=0.17, fade_in=0.1, fade_out=0.8)
S.music("piano_zacht", t_h, END, vol=0.14, fade_in=1.0, fade_out=0.3)
S.finish(length=END, tail=0.0)
