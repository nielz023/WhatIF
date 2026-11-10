"""OR3 · What if you could rewind time ten seconds? · nieuwe stijl: zonnig speelgoedstadje, zebrapad.

1  hook: een auto raast door rood op je af... en spoelt terug (<< REWIND).
2  REWIND 1: je laat je telefoon vallen. Terugspoelen: hij vliegt terug in je hand. Hij valt weer: gevangen.
3  REWIND 2: je stapt het zebrapad op, de auto rijdt door rood. Terugspoelen. Je stapt terug; de auto raast voorbij.
4  Je tikt op je horloge... en dezelfde tien seconden beginnen opnieuw (de telefoon valt weer). LOOP.
5-6 "And again." Steeds weer hetzelfde stukje, jij steeds banger.
De tijden van de terugspoel-momenten zijn gelijk aan de eerste versie (de << REWIND-teksten staan in tekst/or3.json).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or3")
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W
sc = bpy.context.scene

T_ = town(0, 0, half=60, seed=3, lights_on=False)
tl_state(T_, 0.0, "rood")
CURB = V(-4.1, -5.3, 0.15)                     # stoeprand bij het zebrapad (zuidkant), kijkt naar +x
S.place(b, 0.0, CURB, 90)

# telefoon in je hand (hangt aan de elleboog-empty van de rechterarm s=+1) en een losse telefoon
ph_m = mat("Telefoon", (35, 35, 45), rough=0.3, coat=0.6)
scr_m = glow("Telefoonscherm", (120, 190, 255), 2.5)


def phone(name):
    o = box(name, (0, 0, 0), (0.075, 0.15, 0.014), ph_m, bev=0.006)
    s_ = box(name + "_scherm", (0, 0, 0.0075), (0.064, 0.13, 0.002), scr_m, bev=0)
    s_.parent = o
    return o


ph_hand = phone("Telefoon_hand")
attach(ph_hand, b.el[1], hand_offset(b, 1) + V(0.0, -0.04, 0.02), (60, 0, 0))
ph_free = phone("Telefoon_los")

# auto
AUTO = car("Auto_rijdt", -1.75, 60, -90, (230, 50, 45))
LANE_X = -1.75


def car_at(t, y):
    key(AUTO, "location", FR(t), V(LANE_X, y, 0))


HOLD_ARM = "telefoon"

# ------------------------------------------------------------------------------------------------ regel 3 (bron)
r3 = r(3)
STEP = V(-2.4, -5.3, 0.0)
t_hit = Wd(3, 6) - 0.08
S.beat(b, r3, face="neutraal", r_arm="rust", head=dict(turn=0))
S.walk(b, r3 + 0.25, Wd(3, 5) + 0.15, [CURB, V(-3.3, -5.3, 0.0), STEP])
S.face(b, Wd(3, 5), "neutraal")
S.head(b, Wd(3, 5), turn=0)
S.head(b, t_hit - 0.3, turn=-50, up=0)
S.face(b, t_hit - 0.25, "geschrokken")
S.beat(b, t_hit - 0.2, face="geschrokken", arms="afweer", head=dict(turn=-55), body=dict(lean=-6))
S.beat(b, t_hit, face="geschrokken", arms="afweer", head=dict(turn=-60), body=dict(lean=-8))
car_at(r3, 60.0)
car_at(r3 + 0.6, 42.0)
car_at(t_hit, STEP.y + 2.9)                   # neus vlak voor je
RW1, RW2 = Wd(3, 6), Wd(3, 7) - 0.15
copy_anim(rig_objs(b) + [AUTO], t_hit, r3 + 0.3, RW1, RW2)
S.place(b, RW2 + 0.02, CURB, 90)
S.beat(b, RW2 + 0.02, face="nerveus", amt=0.7, head=dict(turn=-40))
S.walk(b, Wd(3, 8) - 0.1, Wd(3, 9) + 0.35, [CURB, CURB + V(-0.6, 0, 0)], back=True)
S.face(b, Wd(3, 8), "nerveus")
S.head(b, Wd(3, 9) + 0.36, turn=-30)
S.beat(b, Wd(3, 9) + 0.4, face="geschrokken", amt=0.8, arms="schrik", head=dict(turn=-25), body=dict(lean=-4))
S.beat(b, Wd(3, 10) + 0.2, face="blij", arms="rust", head=dict(turn=0, up=4), body=dict(lean=-2))
S.beat(b, e(3), face="heel_blij", arms="rust", head=dict(turn=0, up=4))
car_at(RW2 + 0.01, 42.0)
car_at(Wd(3, 9) - 0.4, 14.0)
car_at(Wd(3, 9) + 0.25, -5.0)
car_at(Wd(3, 9) + 1.0, -40.0)
car_at(Wd(3, 9) + 1.05, -300.0)

# ------------------------------------------------------------------------------------------------ hook (regel 1)
H_HIT = 1.05
copy_anim(rig_objs(b) + [AUTO], r3 + 0.3, t_hit, 0.0, H_HIT)
copy_anim(rig_objs(b) + [AUTO], t_hit, r3 + 0.3, H_HIT + 0.08, e(1))
S.face(b, 0.0, "nerveus", 0.6)
S.face(b, H_HIT - 0.3, "geschrokken")
S.face(b, e(1), "geschrokken", 0.7)

# ------------------------------------------------------------------------------------------------ regel 2: telefoon
r2 = r(2)
S.place(b, r2, CURB, 90)
car_at(r2, -300.0)
S.beat(b, r2, face="neutraal", r_arm=HOLD_ARM, head=dict(up=-14))
drop, land = Wd(2, 1) + 0.05, Wd(2, 1) + 0.5
S.beat(b, drop, face="neutraal", r_arm=HOLD_ARM, head=dict(up=-14))
S.beat(b, drop + 0.15, face="geschrokken", r_arm=((-30, 6, 10), (-40, 0, 0)), head=dict(up=-22))
S.beat(b, drop + 0.25, face="geschrokken", r_arm=((-25, 6, 8), (-35, 0, 0)), head=dict(up=-24), body=dict(lean=6))
sc.frame_set(FR(drop))
M_HOLD = ph_hand.matrix_world.copy()
FLOOR = V(M_HOLD.translation.x + 0.15, M_HOLD.translation.y - 0.05, 0.157)
key(ph_free, "location", FR(drop - 0.01), M_HOLD.translation)
key(ph_free, "rotation_euler", FR(drop - 0.01), M_HOLD.to_euler())
key(ph_free, "location", FR(land), FLOOR)
key(ph_free, "rotation_euler", FR(land), (0, 0, R(30)))
key(ph_free, "location", FR(land + 0.15), FLOOR + V(0.05, 0.03, 0))
key(ph_free, "rotation_euler", FR(land + 0.15), (0, 0, R(40)))
RA, RB = Wd(2, 4) - 0.05, Wd(2, 4) + 0.55
copy_anim([ph_free], land, drop - 0.01, RA, RB)
copy_anim(rig_objs(b), drop + 0.25, r2 + 0.1, RA, RB)
d2b = Wd(2, 5) - 0.45
S.beat(b, RB + 0.02, face="trots", amt=0.7, r_arm=HOLD_ARM, head=dict(up=-14))
S.beat(b, d2b, face="trots", amt=0.7, r_arm=HOLD_ARM, head=dict(up=-14))
CATCH_ARM = ((-20, 4, 12), (-70, 0, 0))
S.beat(b, d2b + 0.2, face="heel_blij", r_arm=CATCH_ARM, head=dict(up=-20), body=dict(lean=4, dz=-0.02))
key(ph_free, "location", FR(RB + 0.01), M_HOLD.translation)
key(ph_free, "rotation_euler", FR(RB + 0.01), M_HOLD.to_euler())
S.beat(b, Wd(2, 6) + 0.4, face="heel_blij", r_arm=HOLD_ARM, head=dict(up=-10, tilt=6))
S.beat(b, e(2), face="blij", r_arm=HOLD_ARM, head=dict(up=-4, tilt=4))
for t, on in ((0.0, False), (drop, True), (RB, False)):
    visible(ph_free, t, on)
for t, on in ((0.0, False), (r2, True), (drop, False), (RB, True), (r3, False)):
    visible(ph_hand, t, on)

# ------------------------------------------------------------------------------------------------ regel 4: horloge
r4 = r(4)
watch = box("Horloge", (0, 0, 0), (0.07, 0.06, 0.025), mat("Horloge", (40, 40, 50), rough=0.3, coat=0.6), bev=0.008)
wg = box("Horloge_gloed", (0, 0, 0.013), (0.05, 0.04, 0.002), glow("Horloge_scherm", (90, 230, 255), 5.0), bev=0)
wg.parent = watch
attach(watch, b.el[-1], V(-0.0, -0.04, -0.12), (0, 0, 0))
S.place(b, r4, CURB, 90)
WATCH_L = ((-35, 8, 22), (-95, 0, 0))
S.beat(b, r4, face="neutraal", arms="rust", head=dict(up=-12))
S.beat(b, r4 + 0.3, face="nieuwsgierig", arms=WATCH_L, r_arm=((-45, 4, 20), (-70, 0, 0)), head=dict(up=-18, turn=-8))
S.beat(b, Wd(4, 4) - 0.1, face="nieuwsgierig", arms=WATCH_L, r_arm=((-45, 4, 20), (-70, 0, 0)), head=dict(up=-18, turn=-8))
S.beat(b, Wd(4, 4) + 0.05, face="nieuwsgierig", arms=WATCH_L, r_arm=((-50, 2, 30), (-85, 0, 0)), head=dict(up=-18, turn=-8))
S.beat(b, Wd(4, 5) + 0.2, face="verbaasd", arms=WATCH_L, r_arm="rust", head=dict(up=-16, turn=-8))
for t, on in ((0.0, False), (r4, True)):
    visible(watch, t, on)
key_value(wg.data.materials[0].node_tree.nodes["Emission"].inputs["Strength"],
          [(0, 2.0), (Wd(4, 4), 2.0), (Wd(4, 4) + 0.05, 12.0), (Wd(4, 4) + 0.4, 3.0)])
LOOP1 = Wd(4, 6) - 0.05
LOOP_SRC = (r2, RB + 0.3)


def loop(a, b_, scared):
    """Speel het begin van regel 2 opnieuw af in [a, b_]."""
    dur = min(b_ - a, LOOP_SRC[1] - LOOP_SRC[0])
    copy_anim(rig_objs(b) + [ph_free], LOOP_SRC[0], LOOP_SRC[0] + dur, a, a + dur)
    off = a - LOOP_SRC[0]
    visible(ph_hand, a, True)
    visible(ph_hand, drop + off, False)
    visible(ph_free, a, False)
    visible(ph_free, drop + off, True)
    if RB + off < b_:
        visible(ph_free, RB + off, False)
        visible(ph_hand, RB + off, True)
    S.face(b, a, "nerveus" if scared < 1 else "bang", 0.6 + 0.4 * min(1, scared))
    S.face(b, drop + off + 0.15, "geschrokken" if scared < 1 else "bang", 1.0)
    if a + dur < b_ - 0.05:
        S.face(b, b_ - 0.05, "bang", 1.0)


loop(LOOP1, r(5) - 0.02, 0.0)
loop(r(5) - 0.02, r(6) - 0.02, 1.0)
loop(r(6) - 0.02, END, 2.0)
S.face(b, e(6) - 0.2, "bang", 1.0)
S.face(b, END, "bang", 1.0)
visible(watch, LOOP1 + 0.01, True)

# ------------------------------------------------------------------------------------------------ camera's
HEAD = CURB + V(0, 0, 1.47)
LOWROAD = ((2.2, -12.8, 0.85), (-3.0, -3.2, 1.2), 26)
LOWROAD2 = ((2.1, -12.4, 0.85), (-3.0, -3.2, 1.25), 27)
S.shot(0.0, LOWROAD, LOWROAD2, focus=CURB + V(1.0, 0, 1.4))
PH = ((CURB.x + 2.0, CURB.y - 1.1, 1.15), tuple(CURB + V(0.15, -0.05, 1.05)), 26)
PH2 = ((CURB.x + 1.85, CURB.y - 1.0, 1.12), tuple(CURB + V(0.15, -0.05, 0.98)), 26)
S.shot(r2, PH, PH2)
S.shot(r3, LOWROAD, LOWROAD2, focus=CURB + V(1.0, 0, 1.4))
S.shot(RW2, ((0.4, -7.2, 1.05), (-3.6, -5.2, 1.05), 30), ((0.3, -7.1, 1.05), (-3.7, -5.2, 1.08), 32))
S.shot(r4, ((CURB.x + 1.45, CURB.y - 0.8, 1.3), tuple(CURB + V(0.2, -0.05, 1.2)), 26),
       ((CURB.x + 1.3, CURB.y - 0.72, 1.28), tuple(CURB + V(0.2, -0.05, 1.18)), 28))
S.shot(LOOP1, PH, PH2)
S.shot(r(5) - 0.02, ((CURB.x + 1.6, CURB.y - 0.95, 1.2), tuple(CURB + V(0.15, -0.05, 1.08)), 28),
       ((CURB.x + 1.45, CURB.y - 0.85, 1.2), tuple(CURB + V(0.15, -0.05, 1.12)), 30))
S.shot(r(6) - 0.02, ((CURB.x + 1.15, CURB.y - 0.55, 1.4), tuple(HEAD + V(0, 0, -0.08)), 30),
       ((CURB.x + 0.95, CURB.y - 0.45, 1.4), tuple(HEAD + V(0, 0, -0.08)), 38))


def world():
    sky("dag")
    sun(4.2, d=(-0.6, -0.35, 0.72))
    three_point("Zebra", CURB, 90, scale=1.6)


S.world_fn = world
S.done()
