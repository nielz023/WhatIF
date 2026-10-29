"""F07 · Dag 2 · 10x · keuken, 07:50. De natuurkundige filmt hem met een camera die kogels filmt en speelt het traag
af. Dan schrijft ze op het whiteboard: 2.4h + 0.24h + ... = 2h 40min. 06:20 -> 09:00. Zijn dagen worden korter, en
al zijn dagen passen vóór negen uur. Tenzij hij wakker blijft. AWAKE 17:30.

    blender -b -P anim/v2/scenes/f07_natuurkundige.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f07", "keuken", "natuurkundige")

TX, TY, TZ = 0.2, -0.6, 0.76
FX = 4.8 / 2 - 0.42
WB_Y = 4.2 / 2 - 0.73 - 0.008
WB = V(FX + 0.06, WB_Y - 0.03, 0.82)             # midden van het bord (de kant naar de kamer)
TRIPOD = V(-1.35, -1.55, 0)
HERO_AT = V(1.0, 0.12, 0)                        # voor de hogesnelheidscamera
SCI0 = V(-0.3, 0.12, 0)                          # achter de laptop
BOARD_SCI = V(1.5, 0.94, 0)
MOM_AT = V(0.0, 1.0, 0)
DAD_AT = V(-1.3, 0.62, 0)

# de laptop naar de vrije linkerkant van de tafel, met het scherm naar haar toe
lap = S.obj("Laptop")
lap.location = V(-0.3, -0.42, TZ)
lap.rotation_euler.z = math.radians(180)

# ---------------------------------------------------------------- figuren
ROBE = (0.86, 0.62, 0.76)
sci = S.actor("wetenschapper", SCI0, 0)
held = S.actor("hoofdpersonage", HERO_AT, heading(HERO_AT, TRIPOD))
mama = S.actor("mama", MOM_AT, heading(MOM_AT, HERO_AT), outfit=dict(shirt=ROBE, broek=ROBE))
papa = S.actor("papa", DAD_AT, heading(DAD_AT, HERO_AT))
pad = T.box("Notitieblok", (0, 0, 0), (0.15, 0.2, 0.012), S.mat("notitieblok", (0.98, 0.93, 0.55)), bevel=0.002, ol=0)

# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_binnen_sfeer", 0.0, 120, vol=0.05)
l1 = S.say("F07-01", gap=0.5)
CUT = l1[1] + 0.3                                # zij staat bij het bord
l2 = S.say("F07-02", gap=0.6)
l3 = S.say_slow("F07-03", "Wetenschapper", who=sci, gap=0.5, sub="SCIENTIST", subtitle="Your days are getting shorter.", gain=1.0)
l4 = S.say("F07-04", gap=0.6)
l5 = S.say("F07-05", gap=0.6)
l6 = S.say("F07-06", gap=0.5)
NINE = l6[0] + 1.6                               # 'is nine o'clock'
CANDLES = l6[1] - 0.8
l7 = S.say("F07-07", gap=0.8)
l8 = S.say("F07-08", gap=0.8)
AW = l8[0] + 1.6                                 # 'Then she writes one more line': AWAKE verschijnt
l9 = S.say("F07-09", gap=0.6)
END = l9[1] + 1.4
d4 = l4[1] - l4[0]

S.hud2(2, "10x", clock=clock(7 * 3600 + 50 * 60, 0.1, dec=1, day="TUE"), t0=0.4,
       awake=awake(17.5, rate=1 / 3600, t0=AW, secs=True), awake_t0=AW)
S.sfx("sfx_hud_tik", AW, 0.6)
S.gauge2("DAY 1 = 24 h", l4[0] + 0.05 * d4, l5[0], color=GOLD, row=0)
S.gauge2("DAY 2 = 2.4 h", l4[0] + 0.42 * d4, l5[0], color=GOLD, row=1)
S.gauge2("DAY 3 = 15 min", l4[0] + 0.6 * d4, l5[0], color=GOLD, row=2)
S.music("klinisch", l2[0] - 0.4, NINE, vol=0.16, fade_in=1.5, fade_out=0.2)
S.sfx("sfx_klok_motief", CANDLES + 0.6, 0.35)
S.music("strijkers_emo", l7[0] - 0.3, l8[1], vol=0.15, fade_in=2.0, fade_out=1.5)
S.music("strijkers_warm", l9[0] - 0.6, END + 1, vol=0.2, fade_in=1.0, fade_out=1.2)

# ---------------------------------------------------------------- het bord: de som verschijnt regel voor regel
wb = S.obj("Whiteboard")
lines = {k: [o for o in bpy.data.objects if o.name.startswith(f"Whiteboard_achter_regel{k}")] for k in range(1, 7)}
bpy.context.view_layer.update()


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (min(p.x for p in pts) - 0.01, max(p.x for p in pts) + 0.01, min(p.y for p in pts) - 0.0015,
            min(p.z for p in pts) - 0.01, max(p.z for p in pts) + 0.01)


def reveal(k, t0, t1, steps=10):
    """Witte strook over regel k die schokkerig naar rechts wegschuift: zij schrijft (tien keer te langzaam)."""
    x0, x1, yf, z0, z1 = bbox(lines[k])
    me = bpy.data.meshes.new(f"Whiteboard_dekstrook{k}")
    me.from_pydata([(-(x1 - x0), 0, 0), (0, 0, 0), (0, 0, z1 - z0), (-(x1 - x0), 0, z1 - z0)], [], [(0, 1, 2, 3)])
    cv = bpy.data.objects.new(f"Whiteboard_dekstrook{k}", me)
    T._link(cv)
    cv.data.materials.append(S.mat("whiteboard_wit2", (0.97, 0.97, 0.98)))
    cv.location = (x1, yf, z0)
    key(cv, 0.0, scale=(1, 1, 1))
    key(cv, t0, scale=(1, 1, 1))
    for j in range(1, steps + 1):
        u = j / steps
        key(cv, t0 + (t1 - t0) * u, scale=(max(0.0001, 1 - u), 1, 1))
    for fc in A._fcurves(cv):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
    show(cv, 0.0, t1 + 0.05)
    return x0, x1, yf, (z0 + z1) / 2


WRITES = [(1, l2[0] + 0.8, l2[1] + 0.2), (2, l2[1] + 0.3, l3[0] + 1.0),
          (3, l5[0] + 1.0, l5[1] - 0.6), (4, l6[0] - 0.6, NINE - 0.3),
          (5, l8[0] + 0.3, l8[0] + 1.5), (6, l8[0] + 1.6, l8[0] + 3.0)]
spans = {k: reveal(k, a, b, steps=8 if k < 5 else 6) for k, a, b in WRITES}

# een rode cirkel om 09:00
x0b, x1b, yfb, zb = bbox([o for o in lines[4] if o.name.endswith("b")])[0:3] + (spans[4][3],)
RX, RZ = (x1b - x0b) * 0.62, 0.07
ell = [((x0b + x1b) / 2 + RX * math.cos(a), yfb - 0.004, zb + RZ * math.sin(a))
       for a in (2 * math.pi * j / 48 + 0.4 for j in range(52))]          # iets meer dan rond: met de hand getekend
ring = T.to_mesh(T.tube("Whiteboard_cirkel_0900", ell, 0.0045, S.mat("stift_rood_v2", (0.85, 0.1, 0.1))))
CIRCLE = NINE + 0.1
show(ring, CIRCLE)
S.sfx("sfx_stift", CIRCLE - 0.1, 0.3, cut=(0, 0.8))
for k, a, b in WRITES:
    S.sfx("sfx_stift", a, 0.18, cut=(0, min(3.0, b - a)))

# ---------------------------------------------------------------- de natuurkundige
S.reach(sci, 0.0, "L", None, 0.0)
S.reach(sci, 0.0, "R", None, 0.0)
S.beat(sci, 0.0, "staan", face="neutraal", face_amt=0.5, at=lap.location + V(0, 0, 0.12), crouch=(0.06, 14))
S.reach(sci, 0.4, "R", lap.location + V(0.08, -0.05, 0.06))
S.reach(sci, l1[0] + 4.0, "R", lap.location + V(0.08, -0.05, 0.06))
S.beat(sci, l1[0] + 4.4, "staan", face="verbaasd", face_amt=0.6, at=lap.location + V(0, 0.05, 0.15), crouch=(0.08, 18))
S.teleport(sci, CUT, BOARD_SCI, heading(BOARD_SCI, WB))
S.reach(sci, CUT, "R", None, 0.0)
S.beat(sci, CUT, "staan", face="neutraal", face_amt=0.5, at=WB)
for k, a, b in WRITES:                           # haar hand volgt de strook
    x0, x1, yf, zm = spans[k]
    S.reach(sci, a - 0.35, "R", V(x0 + 0.02, yf - 0.03, zm + 0.02))
    n = max(2, int((b - a) / 0.25))
    for j in range(n + 1):
        u = j / n
        S.reach(sci, a + (b - a) * u, "R", V(x0 + 0.02 + (x1 - x0) * u, yf - 0.03, zm + 0.004 * (1 if j % 2 else -1)))
    S.reach(sci, b + 0.4, "R", None, 0.0)
S.reach(sci, CIRCLE - 0.2, "R", V((x0b + x1b) / 2 - 0.04, yfb - 0.03, zb + 0.03))
S.reach(sci, CIRCLE + 0.2, "R", V((x0b + x1b) / 2 + 0.04, yfb - 0.03, zb - 0.03))
S.reach(sci, CIRCLE + 0.6, "R", None, 0.0)
S.beat(sci, l2[1] - 1.2, "staan", face="geschrokken", face_amt=0.6, at=WB)          # 'and her face changes'
S.turn(sci, l3[0] - 0.4, l3[0] + 0.8, heading(BOARD_SCI, HERO_AT))
S.beat(sci, l3[0] + 0.3, "staan", face="verdrietig", face_amt=0.8, at=S.head(held, l3[0]))
S.turn(sci, l3[1] + 0.3, l4[0] + 0.5, heading(BOARD_SCI, WB))
S.beat(sci, l4[0] + 0.6, "staan", face="nerveus", face_amt=0.6, at=WB)
S.beat(sci, l8[0] + 3.4, "staan", face="vastberaden", face_amt=0.6, at=WB)
S.turn(sci, l9[0] - 0.2, l9[0] + 1.0, heading(BOARD_SCI, HERO_AT))
S.beat(sci, l9[0] + 0.6, "staan", face="blij", face_amt=0.4, at=S.head(held, l9[0]))
S.hold(sci, END)

# ---------------------------------------------------------------- hij: schrijft voor de camera, kijkt dan naar het bord
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
grab(S, pad, held, 0.0, "hand.L", loc=(0.0, 0.08, 0.02), rot=(-80, 0, 0), release=CUT)
S.beat(held, 0.0, "staan", face="vastberaden", face_amt=0.6, arms=HOLD_FRONT_L, look=(0, -0.3))
t, k = 0.3, 0
PADP = HERO_AT + (TRIPOD - HERO_AT).normalized() * 0.32 + V(0, 0, 0.98)
while t < l1[0] + 3.0:                           # tien keer zo snel schrijven: zijn hand is een waas
    j = 0.03 * (1 if k % 2 else -1)
    S.reach(held, t, "R", PADP + V(j, -j, 0.04 + 0.015 * (k % 3)))
    t += 0.08
    k += 1
S.reach(held, l1[0] + 3.2, "R", None, 0.0)
S.beat(held, l1[0] + 3.2, "staan", face="blij", face_amt=0.5, arms=HAND_OUT_L, at=TRIPOD + V(0, 0, 1.35))   # laat het zien
S.beat(held, CUT - 0.6, "staan", face="neutraal", face_amt=0.5, at=S.head(sci, CUT - 0.6))
show(pad, 0.0, CUT)
S.turn(held, CUT, CUT + 0.6, heading(HERO_AT, BOARD_SCI))
S.beat(held, CUT + 0.4, "staan", face="neutraal", face_amt=0.5, at=WB)
S.beat(held, l2[1] - 0.6, "staan", face="twijfel", face_amt=0.7, at=S.head(sci, l2[1]))
S.beat(held, l3[1], "staan", face="geschrokken", face_amt=0.6, at=S.head(sci, l3[1]))
S.beat(held, l4[0] + 1.0, "staan", face="twijfel", face_amt=0.8, at=WB)
S.beat(held, NINE, "staan", face="geschrokken", face_amt=0.9, at=WB)
S.beat(held, CANDLES, "staan", face="verdrietig", face_amt=1.0, at=WB + V(0, 0, -0.2), body={"head": (-10, 0, 0)})
S.beat(held, l7[1], "staan", face="verdrietig", face_amt=0.9, at=WB + V(0, 0, -0.1))
S.beat(held, AW, "staan", face="verbaasd", face_amt=0.8, at=WB)
S.beat(held, l9[0] + 0.4, "staan", face="vastberaden", face_amt=1.0, at=S.head(sci, l9[0]))
S.hold(held, END)

# ---------------------------------------------------------------- mama en papa (tien keer te langzaam)
S.beat(mama, 0.0, "staan", face="nerveus", face_amt=0.5, at=S.head(held, 0.0))
S.beat(mama, CUT + 1.0, "staan", face="nerveus", face_amt=0.6, at=WB)
S.beat(mama, NINE + 2.0, "staan", face="bang", face_amt=0.6, at=WB)
S.hold(mama, END)
S.beat(papa, 0.0, "staan", face="grijns", face_amt=0.6, at=S.head(held, 0.0))
t = 0.6
while t < END:                                   # nog steeds de mop over de slak
    A.key_prop(papa.rig, "mond_open", 0.45, F(t))
    A.key_prop(papa.rig, "mond_open", 0.15, F(t + 1.2))
    t += 2.4
S.hold(papa, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-1.15, -2.45, 1.75), (0.5, 0.1, 1.0), 24), ((-1.05, -2.4, 1.72), (0.6, 0.15, 1.0), 26))
fwd0 = (TRIPOD - HERO_AT).normalized()
POV = TRIPOD - fwd0 * 0.3 + V(0, 0, 1.72)        # vlak achter de hogesnelheidscamera: zij filmt hem
S.cam(l1[0] + 2.2, (POV + V(0.25, -0.2, 0), PADP + V(0, 0, 0.18), 46), (POV + V(0.25, -0.2, 0) - fwd0 * 0.1, PADP + V(0, 0, 0.18), 50), dof=2.6)
LP = lap.location + V(0, 0.05, 0.12)
S.cam(l1[0] + 4.4, (LP + V(0.35, -0.75, 0.3), LP + V(0, 0.15, 0.15), 30), (LP + V(0.32, -0.7, 0.28), LP + V(0, 0.2, 0.18), 32), dof=1.2)
S.cam(CUT, ((2.05, -0.6, 1.15), WB + V(-0.15, -0.25, 0.12), 32), ((2.05, -0.5, 1.12), WB + V(-0.15, -0.25, 0.12), 34))
HS = S.headpos(sci, l2[1] - 0.8)
S.cam(l2[1] - 1.4, (HS + V(0.85, -0.12, -0.08), HS, 26), (HS + V(0.82, -0.18, -0.08), HS, 28), dof=1.2)
S.cam(l3[0] + 0.6, S.ots(held, sci, l3[0] + 1.2, lens=36, side=-1, back=1.5, out=1.0, rise=0.12))
S.cam(l4[0] + 0.4, ((2.15, 0.25, 1.2), WB + V(-0.04, 0, 0.06), 34), ((2.15, 0.32, 1.18), WB + V(-0.04, 0, 0.06), 37), dof=1.0)
S.cam(l5[0] + 0.6, ((2.3, -0.75, 1.5), (0.9, 0.7, 1.05), 24), ((2.28, -0.65, 1.48), (0.9, 0.7, 1.05), 26))
S.cam(l6[0] - 0.4, ((2.15, 0.9, 1.55), V((x0b + x1b) / 2, yfb, zb), 40), ((2.14, 0.95, 1.5), V((x0b + x1b) / 2, yfb, zb), 46), dof=0.7)
fwdH = (BOARD_SCI - HERO_AT).normalized()
FRONT = fwdH * 0.9 + V(-fwdH.y, fwdH.x, 0) * 0.4 + V(0, 0, -0.08)   # voor hem, iets links
HH = S.headpos(held, CANDLES)
S.cam(CANDLES - 0.3, (HH + FRONT * 1.3, HH, 32), (HH + FRONT * 1.15, HH, 36), dof=1.2)
S.cam(l8[0] - 0.2, ((2.05, -0.6, 1.15), WB + V(-0.1, -0.25, 0.0), 32), ((2.05, -0.45, 1.1), WB + V(-0.08, -0.2, -0.05), 36))
HH9 = S.headpos(held, l9[0] + 1.0)
S.cam(l9[0] - 0.2, (HH9 + FRONT * 1.15 + V(0, 0, -0.1), HH9, 34), (HH9 + FRONT, HH9, 38), dof=1.4)

S.finish(length=END)
