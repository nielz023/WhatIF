"""S07a · Dag 5 · winkelcentrum: de grijpmachine (41 knuffels) en de roltrap omhoog die naar beneden gaat.

    blender -b -P anim/scenes/s07a_winkelcentrum.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s07a", "winkelcentrum", "winkelcentrum")
rnd = random.Random(7)

AX, AY = -18.0, -9.0                         # grijpmachine (voorkant naar -y)
CLAW_HERO = V(AX - 0.2, AY - 1.15, 0)
CLAW_FRIEND = V(AX - 1.05, AY - 1.7, 0)
STICK = V(AX - 0.2, AY - 0.55, 1.1)
CHUTE = V(AX + 0.15, AY - 0.52, 0.35)
# roltrap 1 (x = -10): as en normaal van het loopvlak
ESC_C = V(-10.0, 2.2, 2.4)
ESC_A = V(0, 0.836, 0.549)
ESC_N = V(0, -0.549, 0.836)


def esc_pt(s):
    return ESC_C + ESC_A * s + ESC_N * 0.345


for k in range(4):                           # arcadekasten iets opzij, zodat de camera naast de grijpmachine past
    S.obj(f"Arcadekast_{k + 1}").location.x += 2.2
held = S.actor("hoofdpersonage", (-2.0, -4.6, 0), 60)
vriend = S.actor("beste_vriend", (-1.6, -5.5, 0), 60)
extras = [S.extra(0, (3.6, -2.4, 0), 200), S.extra(1, (4.4, -3.1, 0), 20), S.extra(3, (-5.6, 3.2, 0), 160),
          S.extra(4, (8.0, 1.5, 0), -90), S.extra(6, (-14.0, 2.5, 0), 90), S.extra(7, (6.5, -6.0, 0), 120)]

# ---------------------------------------------------------------- tijdlijn
S.hud(5, "32x STRONGER", t0=0.4)
S.music("mall", 0.0, 60, vol=0.3, fade_in=0.5)
S.ambience("sfx_klas_geroezemoes", 0.0, 60, vol=0.15)
l1 = S.say("S07-01", gap=0.6)
l2 = S.say("S07-02", gap=0.6)
HOLD = l2[0] + 2.15                          # 'You hold the claw, gently'
EMPTY = l2[0] + 3.45                         # 'and empty the whole box'
N41 = l2[0] + 4.96                           # 'Forty-one plushies.'
S.sfx("sfx_grijpmachine", HOLD - 0.1, 0.8)
S.wait(0.6)
ESC0 = S.t                                   # de roltrap
STOP = ESC0 + 2.1
S.sfx("sfx_roltrap", STOP - 0.45, 1.0)
S.wait(4.2)
END = S.t

# ---------------------------------------------------------------- l1: ze lopen door de drukke hal
WALK_H = [V(-2.0, -4.6, 0), V(-6.0, -5.8, 0), V(-10.5, -7.0, 0)]
WALK_V = [V(-1.6, -5.5, 0), V(-5.6, -6.7, 0), V(-10.0, -7.9, 0)]
S.beat(held, 0.0, "ontspannen", face="blij", face_amt=0.6, at=S.head(vriend, 0))
S.beat(vriend, 0.0, "ontspannen", face="lach", face_amt=0.6, at=S.head(held, 0))
S.walk(held, 0.2, l1[1] + 0.3, WALK_H)
S.walk(vriend, 0.2, l1[1] + 0.3, WALK_V)
S.beat(held, l1[0] + 3.0, "ontspannen", face="lach", face_amt=0.7, look=(0.5, 0.1), body={"head": (0, 25, 0)})
S.beat(vriend, l1[0] + 3.2, "ontspannen", face="lach", look=(-0.5, 0.1), body={"head": (0, -25, 0)})
# figuranten: drie lopen, drie staan
S.walk(extras[0], 0.0, 9.0, [V(3.6, -2.4, 0), V(1.0, -5.0, 0), V(-4.0, -9.0, 0)])
S.walk(extras[2], 0.0, 9.0, [V(-5.6, 3.2, 0), V(-2.0, 5.0, 0), V(3.0, 6.0, 0)])
S.walk(extras[5], 0.0, 9.0, [V(6.5, -6.0, 0), V(2.0, -8.0, 0), V(-3.0, -10.5, 0)])
for k, e in enumerate(extras):
    S.beat(e, 0.0, "ontspannen" if k % 2 else "staan", face="blij" if k % 3 else "neutraal", face_amt=0.4, look=(0.2 * (k % 3 - 1), 0))
S.beat(extras[1], 0.0, "filmen", amount=0.7, face="blij", face_amt=0.4)          # maakt een foto van de fontein
S.beat(extras[3], 0.0, "armen_over", face="neutraal", face_amt=0.4)

# ---------------------------------------------------------------- l2: de grijpmachine
S.teleport(held, l2[0] - 0.05, CLAW_HERO, 180)
S.teleport(vriend, l2[0] - 0.05, CLAW_FRIEND, 215)
S.beat(held, l2[0] - 0.05, "staan", face="vastberaden", face_amt=0.6, at=V(AX, AY, 1.4))
S.beat(vriend, l2[0] - 0.05, "armen_over", face="twijfel", face_amt=0.6, at=V(AX, AY, 1.4))
S.reach(held, l2[0] + 0.3, "R", None, 0.0)
S.reach(held, l2[0] + 0.9, "R", STICK + V(0, -0.04, -0.03))
S.beat(held, l2[0] + 1.0, "staan", face="zelfverzekerd", face_amt=0.7, at=V(AX + 0.1, AY + 0.1, 1.35), crouch=(0.03, 6))
# heel zachtjes... hij houdt de grijper vast
S.reach(held, HOLD, "R", STICK + V(0.0, -0.035, -0.03))
S.reach(held, HOLD + 0.6, "R", STICK + V(0.02, -0.03, -0.035))
S.beat(held, HOLD + 0.2, "staan", face="inspanning", face_amt=0.3, at=V(AX + 0.1, AY + 0.1, 1.3), crouch=(0.04, 8), ogen_knijp=0.5)
S.reach(held, EMPTY, "R", STICK + V(0.03, -0.02, -0.04))
S.beat(held, EMPTY + 0.2, "staan", face="verbaasd", face_amt=0.7, at=CHUTE, crouch=(0.06, 12))
S.reach(held, EMPTY + 0.8, "R", None, 0.0)
S.beat(held, N41 - 0.2, "juichen", amount=0.7, face="lach", look=(0.4, 0.2), body={"head": (0, 20, 0)})
S.hold(held, l2[1] + 0.4)
S.beat(vriend, EMPTY + 0.3, "schrik", amount=0.6, face="verbaasd", at=CHUTE + V(0, -0.5, 0))
S.beat(vriend, N41 - 0.3, "staan", face="lach", face_amt=0.9, at=S.head(held, l2[0]) + V(-0.1, 0, 0), arms=arms(HOLD_FRONT_L, HOLD_FRONT_R))
S.hold(vriend, l2[1] + 0.4)

# de knuffels: de kast loopt leeg, alles rolt de bak uit
PCOL = [(0.95, 0.6, 0.75), (0.5, 0.75, 1.0), (1.0, 0.85, 0.3), (0.55, 0.85, 0.5), (0.8, 0.6, 0.95), (1.0, 0.6, 0.35)]
inside = S.obj("Knuffels")
key(inside, EMPTY, scale=(1, 1, 1))
key(inside, EMPTY + 1.3, scale=(1, 1, 0.05))
pile = []
for k in range(41):
    c = PCOL[k % 6]
    r = rnd.uniform(0.07, 0.1)
    p = T.sphere(f"Knuffel_{k}", (0, 0, 0), r, S.mat(f"knuffel_{k % 6}", c), seg=12, ol=0.004)
    for sx in (-1, 1):
        ear = T.sphere(f"Knuffel_{k}_oor{sx}", (sx * r * 0.6, 0, r * 0.85), r * 0.35, S.mat(f"knuffel_{k % 6}", c), seg=8, ol=0.003)
        ear.parent = p
    for sx in (-1, 1):
        eye = T.sphere(f"Knuffel_{k}_oog{sx}", (sx * r * 0.35, -r * 0.88, r * 0.2), r * 0.12, P.m("zwart"), seg=6, ol=0)
        eye.parent = p
    t0 = EMPTY + k * 0.035
    a = rnd.uniform(-1.2, 1.2)
    d = rnd.uniform(0.25, 0.9)
    land = V(AX + 0.15 + d * math.sin(a), AY - 0.75 - d * abs(math.cos(a)) * 0.9, r * 0.8 + 0.06 * (k % 4))
    mid = (CHUTE + land) * 0.5 + V(0, -0.15, 0.35)
    key(p, 0, loc=CHUTE, scale=0.001)
    key(p, t0 - 1 / FPS, loc=CHUTE, scale=0.001)
    key(p, t0, loc=CHUTE, scale=1.0, rot=(0, 0, 0))
    key(p, t0 + 0.18, loc=mid, rot=(rnd.uniform(-90, 90), rnd.uniform(-90, 90), 0))
    key(p, t0 + 0.36, loc=land, rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(-180, 180)))
    pile.append(p)
for k in range(9):
    n = min(41, 5 * (k + 1))
    t0 = EMPTY + 0.1 + k * 0.16
    t1 = EMPTY + 0.1 + (k + 1) * 0.16
    if n >= 41:
        t0, t1 = N41, None
    S.gauge(f"PLUSHIES: {n}", t0, t1, color=GOLD if n >= 41 else WHITE)
# de vriend draagt een armvol knuffels
for k in range(5):
    q = T.sphere(f"Armvol_{k}", (0, 0, 0), 0.085, S.mat(f"knuffel_{k % 6}", PCOL[k % 6]), seg=12, ol=0.004)
    attach(q, vriend, "chest", ((k % 3 - 1) * 0.12, -0.2 + (k // 3) * 0.12, 0.2 + (k // 3) * 0.04))   # bot-assen: y = op, z = voor
    show(q, N41 - 0.3)

# ---------------------------------------------------------------- de roltrap (omhoog lopen op de roltrap naar beneden)
S.teleport(held, ESC0, (-10.0, -3.3, 0), 180)
S.teleport(vriend, ESC0, (-8.9, -3.6, 0), 145)
S.beat(held, ESC0, "staan", face="zelfverzekerd", face_amt=0.6, look=(0, 0.2))
S.beat(vriend, ESC0, "staan", face="twijfel", face_amt=0.6, at=esc_pt(0) + V(0, 0, 1.0))
TOP = esc_pt(-0.6)
S.walk(held, ESC0 + 0.05, STOP + 0.1, [V(-10.0, -3.3, 0), V(-10.0, -1.95, 0.1), esc_pt(-3.6), TOP], stride=0.5)
S.beat(held, STOP + 0.3, "schrik", amount=0.4, face="geschrokken", face_amt=0.7, at=esc_pt(-4.5))
S.beat(held, STOP + 1.2, "schouders_op", face="nerveus", face_amt=0.8, at=S.head(vriend, ESC0))
S.hold(held, END)
S.beat(vriend, STOP + 0.2, "schrik", amount=0.5, face="verbaasd", at=esc_pt(-4.5))
S.beat(vriend, STOP + 1.0, "handen_hoofd", face="nerveus", face_amt=0.7, at=S.head(held, STOP + 0.1))
S.hold(vriend, END)
# gele tredelijnen die naar beneden lopen, tot de roltrap kreunend stopt
ymat = S.mat("tredelijn", (0.98, 0.8, 0.1))
v = 0.55
frames = list(range(F(ESC0) - 1, F(END) + 1))
for k in range(20):
    o = T.box(f"Tredelijn_{k}", (0, 0, 0), (1.05, 0.05, 0.012), ymat, base=False, bevel=0, ol=0)
    o.rotation_euler = (math.radians(33.3), 0, 0)
    rows = []
    for f in frames:
        t = min((f - 1) / FPS, STOP) - ESC0
        s = ((k * 0.45 - v * t) % 9.0) - 4.5
        rows.append(tuple(esc_pt(s) + ESC_N * 0.01))
    bake(o, "location", frames, rows)
    show(o, ESC0)
S.debris(esc_pt(-4.3), STOP, n=14, size=(0.008, 0.02), color=(1.0, 0.8, 0.3), speed=(1.0, 2.4), up=1.0, floor=0.0, life=0.8, name="Vonk")
S.puff(esc_pt(-4.4), STOP, n=4, r=(0.1, 0.2), grow=2.0, dur=1.0, color=(0.5, 0.5, 0.52), rise=0.4, spread=0.3)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-12.2, -7.6, 1.5), (-4.5, -5.4, 1.3), 28), ((-12.4, -7.7, 1.5), (-6.5, -6.0, 1.25), 30))
S.cam(l1[0] + 3.6, S.shot(held, l1[0] + 4.0, "med", az=-30, lens=28, lr=-0.45), S.shot(held, l1[1], "med", az=-30, lens=30, lr=-0.45))
S.cam(l2[0] - 0.05, ((AX + 1.5, AY - 0.55, 1.6), (AX - 0.45, AY - 1.3, 1.3), 26), ((AX + 1.45, AY - 0.6, 1.58), (AX - 0.4, AY - 1.25, 1.3), 28))
S.cam(HOLD - 0.2, (STICK + V(0.62, -0.25, 0.12), STICK + V(-0.05, -0.04, -0.02), 30), (STICK + V(0.56, -0.24, 0.11), STICK + V(-0.05, -0.04, -0.02), 36))
S.cam(EMPTY, ((AX + 1.3, AY - 1.9, 0.75), (AX - 0.1, AY - 0.8, 0.45), 22), ((AX + 1.2, AY - 1.85, 0.75), (AX - 0.1, AY - 0.8, 0.45), 24))
S.cam(N41 - 0.4, ((AX + 2.7, AY - 2.5, 1.5), (AX - 0.4, AY - 1.25, 0.8), 22), ((AX + 2.6, AY - 2.45, 1.5), (AX - 0.4, AY - 1.25, 0.85), 24))
S.cam(ESC0, ((-5.8, -3.0, 4.4), (-10.0, 0.0, 1.6), 22), ((-5.9, -2.8, 4.5), (-10.0, 0.4, 1.9), 22),
      shake=lambda t: max(0.0, 0.8 - (t - STOP) * 2) if t > STOP else 0.0)
S.cam(STOP + 1.0, ((-8.2, 2.4, 4.6), TOP + V(0, 0, 1.2), 30), ((-8.25, 2.35, 4.6), TOP + V(0, 0, 1.2), 34))

S.finish(length=END)
