"""F09 · Dag 4 · 1.000x · straat in de grijze ochtend. Hij wordt wakker van koplampen: de vuilniswagen, en het
broertje in zijn dinopyjama dat midden over straat rent. Zestien minuten. Hij duwt hem alsof hij van glas is:
MOVED 0.4 m ... 1.2 m ... 2.0 m. De wagen glijdt rakelings langs. Op de stoep: 'I know it's you.'

    blender -b -P anim/v2/scenes/f09_redding.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f09", "straat", "grijs")
rnd = random.Random(9)

CURB = V(-10.0, 6.02, 0.0)                       # waar hij op dag 3 in slaap viel
BRO_AT = V(-1.4, 1.2, 0)                         # midden op de rijbaan, op weg naar de overkant (-y)
BEHIND = V(0.25, 0.85, 0)                        # hij staat achter het broertje (zoals in de cold open)
TRUCK_X = -8.75                                  # neus op ~3 m van het broertje
SIT_BRO = V(-1.55, -3.4, 0)                      # later: samen op de stoeprand aan de overkant
SIT_HERO = V(-0.85, -3.4, 0)

truck = S.obj("Vuilniswagen")
S.obj("Auto_geparkeerd_2").location.x = -21.0
for o in bpy.data.objects:
    if o.name.startswith("Raamtekst"):
        o.hide_render = True
S.obj("Kraai").hide_render = True
crow = G.crow("kraai", (-3.6, 2.6, 3.4), rot_z=-70, wing=38)
bag = S.obj("Plastic_zak")
bag.location = (-2.35, 0.55, 1.55)

# ---------------------------------------------------------------- tijdlijn (en zijn tijd: m = minuten voor hem)
l1 = S.say("F09-01", gap=0.6)
WALK = l1[1] + 0.2                               # snede: hij staat achter het broertje
l2 = S.say("F09-02", at=WALK + 0.6)
l3 = S.say("F09-03", gap=0.4)
d3 = l3[1] - l3[0]
P1, P2 = l3[0] + 0.42 * d3, l3[0] + 0.95 * d3   # 'forty centimeters', 'one meter twenty'
l4 = S.say("F09-04", gap=0.5)
l5 = S.say("F09-05", gap=0.9)
P3 = l5[0] + 1.8                                 # 'two meters'
PASS0, PASS1 = l5[0] + 2.6, l5[1] + 0.6          # de wagen glijdt langs
SIDE = PASS1 + 0.6                               # snede: samen op de stoep
l6 = S.say_slow("F09-06", "Broertje", gap=SIDE + 1.0 - S.t, sub="BROTHER", subtitle="I know it's you.", gain=1.0)
l7 = S.say("F09-07", gap=0.7)
END = l7[1] + 1.8

MINS = [(0.0, 0.0), (WALK - 0.05, 0.6), (WALK, 2.0), (l3[0], 2.0), (P1, 4.0), (P2, 8.0), (l5[0], 11.0),
        (P3, 14.0), (PASS0, 16.0), (PASS1, 30.0), (SIDE - 0.05, 30.0), (SIDE, 55.0), (END + 1, 57.0)]
MOVE = [(0.0, 0.0), (2.0, 0.0), (4.0, 0.4), (8.0, 1.2), (11.0, 1.7), (14.0, 2.0), (99.0, 2.0)]


def interp(tab, x):
    for (a, va), (b, vb) in zip(tab, tab[1:]):
        if x <= b:
            return va + (vb - va) * (0 if b == a else (x - a) / (b - a))
    return tab[-1][1]


def mins(t):
    return interp(MINS, t)


def moved(m):
    return interp(MOVE, m)


START = 8 * 3600 + 58 * 60 + 38.9
S.hud2(4, "1,000x", clock=lambda t: hms(START + mins(t) * 60 / 1000, 2, "TUE"), t0=0.3,
       awake=lambda t: awake(1 / 60, rate=1 / 60)(mins(t)), awake_t0=0.5)
S.gauge2("TRUCK: 16 MIN", l2[0] + 0.6, l3[0] + 0.3, color=(1.0, 0.45, 0.35, 1), row=0)
S.gauge2(lambda t: f"MOVED: {moved(mins(t)):.1f} m", l3[0] + 0.4, PASS0, color=GOLD, row=0)
S.gauge2(lambda t: f"{int(mins(t))} MIN", l3[0] + 0.4, PASS0, color=GOLD, row=1)
S.music("drone", 0.0, PASS0, vol=0.26, fade_in=0.4, fade_out=0.3)
S.music("piano_zacht", l2[0], PASS0 - 0.2, vol=0.14, fade_in=2.0, fade_out=0.3)
S.ambience("sfx_vuilniswagen", 0.0, PASS1, vol=0.12)
for k in range(int(PASS0 / 2.6)):                # de klok tikt veel te langzaam
    S.sfx("sfx_klok_tik", 0.9 + k * 2.6, 0.2, cut=(0, 0.35))
S.sfx("sfx_hartslag", l4[0], 0.22, cut=(0, l4[1] - l4[0]))
S.sfx("sfx_remmen", PASS0 + 0.2, 0.18)
S.music("strijkers_warm", SIDE - 0.3, END + 1, vol=0.17, fade_in=1.5, fade_out=1.5)
S.ambience("sfx_straat_sfeer", SIDE, END + 1, vol=0.05)

# de vuilniswagen, met rokende remmen (in zijn tijd 3 m/s gedeeld door duizend)
for t in frange(0.0, END + 1, 0.25):
    key(truck, t, loc=(TRUCK_X + 3.1 * mins(t) / 16, 1.5, 0))
for fc in A._fcurves(truck):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
sm = bpy.data.materials.new("remrook")
sm.use_nodes = True
b = sm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.78, 0.78, 0.8, 1)
b.inputs["Alpha"].default_value = 0.3
sm.surface_render_method = "BLENDED"
sm.diffuse_color = (0.78, 0.78, 0.8, 0.3)
for k in range(26):                              # hangen stil achter de wielen
    wx = rnd.choice((-2.6, 2.6)) - rnd.uniform(0.1, 0.9)
    wy = rnd.choice((-1.25, 1.25)) + rnd.uniform(-0.15, 0.15)
    puff = T.sphere(f"Remrook_{k}", (wx, wy, rnd.uniform(0.15, 0.6)), rnd.uniform(0.12, 0.3), sm, seg=10, ol=0)
    puff.parent = truck
    show(puff, l2[0])
key(bag, 0.0, loc=bag.location.copy())
key(bag, END + 1, loc=bag.location + V(0.004, 0, -0.01))

# ---------------------------------------------------------------- het broertje: bevroren midden in zijn sprint
bro = S.actor("broertje_dino", BRO_AT, 0, frozen=True)
run_pose(S, bro, 0.0, front="R", amount=0.85, lift=0.14, reach=0.12, back=0.16, face="blij", look=(0.15, 0.1))
A.key_prop(bro.rig, "mond_open", 0.35, F(0.0))
for t in frange(0.0, SIDE - 0.05, 0.25):
    S.place(bro, t, BRO_AT - V(0, moved(mins(t)), 0), 0)
S.hold(bro, SIDE - 0.05)
SIT_B, zb = sit(bro, seat_top=0.13)
S.teleport(bro, SIDE, SIT_BRO + V(0, 0, zb), 180)
S.beat(bro, SIDE, **SIT_B, pose="ontspannen", face="neutraal", face_amt=0.5, look=(0.0, -0.1),
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(bro, l6[0] - 0.2, **SIT_B, pose="ontspannen", face="neutraal", face_amt=0.5, look=(0.0, -0.1),
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.beat(bro, l6[1] + 0.3, **SIT_B, pose="ontspannen", face="blij", face_amt=0.6, at=SIT_HERO + V(0, 0, 0.9),
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.hold(bro, END)

# ---------------------------------------------------------------- hij
held = S.actor("hoofdpersonage", CURB, 0)
SIT_H, zh = sit(held, seat_top=0.13)
S.place(held, 0, CURB + V(0, 0, zh), 0)
SIT_ARMS = arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)))
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, look=(0, -0.4), body={"head": (28, 0, 0), "neck": (10, 0, 0)}, arms=SIT_ARMS)
S.eyes_closed(held, 0.0, 1.1)
S.beat(held, 1.3, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=0.8, at=truck.location + V(4.3, 0, 1.0), arms=SIT_ARMS)
S.beat(held, l1[0] + 5.5, **SIT_H, pose="ontspannen", face="bang", face_amt=1.0, at=S.head(bro, 0), arms=SIT_ARMS)
# achter het broertje; hij schuift mee met elke duw
S.teleport(held, WALK, BRO_AT + BEHIND, 8)
S.beat(held, WALK, "staan", face="bang", face_amt=0.9, at=S.head(bro, WALK))
S.reach(held, WALK, "L", None, 0.0)
S.reach(held, WALK, "R", None, 0.0)
S.beat(held, l2[1] - 0.4, "staan", face="vastberaden", face_amt=0.7, at=S.head(bro, l2[1]), crouch=(0.03, 12))
for t in frange(l3[0], SIDE - 0.05, 0.25):
    S.place(held, t, BRO_AT + BEHIND - V(0, moved(mins(t)), 0), 8)
GAP = V(0, 0.04, 0.0)                            # op zijn rug, net onder de grote dinocapuchon
t, k = l3[0] + 0.3, 0
while t < PASS1:                                 # handen op zijn schouders, ze trillen
    j = V(0.006 * (1 if k % 2 else -1), 0.004 * (1 if k % 3 else -1), 0.005 * (1 if k % 2 else -1)) * (1.6 if l4[0] < t < l4[1] else 1.0)
    BR = S._root_matrix(bro, t).translation
    SL = BR + V(0.15, 0.17, 0.5)
    SR = BR + V(-0.15, 0.17, 0.5)
    S.reach(held, t, "L", SL + GAP + j)
    S.reach(held, t + 0.06, "R", SR + GAP - j)
    t += 0.13
    k += 1
S.reach(held, PASS1 + 0.1, "L", None, 0.0)
S.reach(held, PASS1 + 0.1, "R", None, 0.0)
LOOK = S.head(bro, 0) + V(0.1, -1.2, 0.3)


def look_ahead(t):
    """Over zijn hoofd heen de straat in (schuift mee met het broertje)."""
    return S.head(bro, t) + V(0.1, -1.2, 0.3)


S.beat(held, l3[0] + 0.4, "staan", face="vastberaden", face_amt=0.8, at=look_ahead(l3[0] + 0.4), crouch=(0.04, 8))
S.beat(held, l4[0] + 0.3, "staan", face="inspanning", face_amt=0.8, at=look_ahead(l4[0] + 0.3), crouch=(0.04, 8))
S.beat(held, l4[1], "staan", face="inspanning", face_amt=0.9, at=look_ahead(l4[1]), crouch=(0.04, 8))
S.beat(held, PASS0 - 0.8, "staan", face="vastberaden", face_amt=0.9, at=look_ahead(PASS0 - 0.8), crouch=(0.04, 8))
S.beat(held, PASS0 - 0.3, "staan", face="bang", face_amt=0.8, at=look_ahead(PASS0) + V(-2.0, 0.5, 0), crouch=(0.04, 8))
S.beat(held, PASS1, "staan", face="verbaasd", face_amt=0.8, at=look_ahead(PASS1), crouch=(0.03, 6))
# op de stoep naast hem
S.teleport(held, SIDE, SIT_HERO + V(0, 0, zh), 180)
S.beat(held, SIDE, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, look=(0.0, -0.1), arms=SIT_ARMS)
S.beat(held, l6[0] + 1.0, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.8, at=S.head(bro, l6[0]), arms=SIT_ARMS)
S.beat(held, l7[0] + 0.3, **SIT_H, pose="ontspannen", face="blij", face_amt=0.7, at=S.head(bro, l7[0]) + V(0.3, 0.7, 0.1), arms=SIT_ARMS)
S.hold(held, END)

# ---------------------------------------------------------------- camera
HW = S.headpos(held, 1.0)
S.cam(0.0, (HW + V(0.35, -1.05, -0.08), HW + V(0, 0, -0.05), 28), (HW + V(0.32, -0.95, -0.08), HW + V(0, 0, -0.05), 31), dof=1.6)
S.cam(l1[0] + 2.2, ((-11.8, 8.4, 1.9), (-4.5, 1.3, 1.0), 24), ((-11.6, 8.2, 1.85), (-4.0, 1.3, 1.0), 26))
S.cam(l1[0] + 6.0, S.shot(bro, 0.0, "cu", az=40, lens=40, h=-0.1), S.shot(bro, 0.0, "cu", az=36, lens=44, h=-0.1), dof=2.0)
S.cam(WALK, ((-1.0, -0.9, 0.55), (-8.0, 1.8, 1.7), 24), ((-1.2, -0.8, 0.6), (-8.0, 1.8, 1.8), 25))
S.cam(l3[0] - 0.1, S.shot(held, l3[0] + 0.5, "full", az=-60, lens=30), S.shot(held, l3[0] + 2.0, "med", az=-55, lens=32))


def top(t):
    p = S._root_matrix(bro, t).translation
    return ((p.x + 0.6, p.y - 2.0, 7.5), (p.x - 1.0, p.y + 0.6, 0.4), 28)


S.cam(P1 - 0.6, None, fn=top)
MID = S._root_matrix(bro, l4[0]).translation + V(0, 0.17, 0.5) + GAP
S.cam(l4[0] - 0.05, (MID + V(1.35, -0.55, 0.2), MID + V(0, 0, 0.05), 40), (MID + V(1.15, -0.5, 0.16), MID + V(0, 0, 0.05), 44), dof=1.8)
HH = S.headpos(held, l4[1])
S.cam(l4[0] + 3.2, (HH + V(0.75, -1.5, -0.08), HH + V(0, 0, -0.04), 44), (HH + V(0.65, -1.35, -0.08), HH + V(0, 0, -0.04), 48), dof=2.2)
S.cam(PASS0 - 0.6, ((-0.6, -4.2, 0.55), (-1.6, 0.6, 1.1), 26), ((-0.7, -4.0, 0.6), (-1.4, 0.6, 1.2), 27))
TWO = (SIT_BRO + SIT_HERO) / 2
S.cam(SIDE, ((TWO.x + 0.2, TWO.y + 2.3, 0.85), TWO + V(0, 0, 0.7), 30), ((TWO.x + 0.15, TWO.y + 2.1, 0.85), TWO + V(0, 0, 0.7), 32))
HB = S.bone_world(bro, "head", l6[0] + 1.0, tail=False) + V(0, 0, 0.26)   # headpos klopt niet bij zitten
S.cam(l6[0] + 0.4, (HB + V(0.5, 0.85, -0.05), HB, 34), (HB + V(0.45, 0.78, -0.05), HB, 38), dof=1.4)
HS = S.bone_world(held, "head", l7[0] + 1.0, tail=False) + V(0, 0, 0.12)
S.cam(l7[0] - 0.1, (HS + V(-0.25, 0.95, -0.12), HS, 32), (HS + V(-0.22, 0.86, -0.12), HS, 35), dof=1.4)

S.finish(length=END)
