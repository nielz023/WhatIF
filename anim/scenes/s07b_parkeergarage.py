"""S07b · Dag 5 · parkeergarage: een kat achter het wiel, hij tilt de auto op, de vriend filmt alles.

    blender -b -P anim/scenes/s07b_parkeergarage.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s07b", "winkelcentrum", "parkeergarage")

CX, CY = -3.0, -13.5                         # de auto met de kat (neus naar +y)
PIVOT = V(CX, CY - 1.3, 0.0)                 # achterwielen
BUMPER = V(0, 3.35, 0.38)                    # onderkant voorbumper t.o.v. het scharnier
CAT0 = V(CX + 0.4, CY + 0.95, 0)             # achter het linkervoorwiel
LIFT_DEG = 20.0

# lege plek maken en de eigen auto neerzetten
for o in list(bpy.data.objects):
    if o.name.startswith("Auto_") and (o.location.xy - V(CX, CY).xy).length < 1.6:
        bpy.data.objects.remove(o, do_unlink=True)
car = P.car("Auto_kat", (CX, CY, 0), rot=90, color=(0.85, 0.15, 0.12), kind="hatch")
lifter = hinge(car, PIVOT)


def bumper_at(deg, dx=0.0):
    a = math.radians(deg)
    return PIVOT + V(dx, BUMPER.y * math.cos(a) - BUMPER.z * math.sin(a), BUMPER.y * math.sin(a) + BUMPER.z * math.cos(a))


def make_cat(name):
    fur = S.mat("kat_rood", (0.95, 0.55, 0.2))
    light = S.mat("kat_licht", (1.0, 0.85, 0.65))
    root = bpy.data.objects.new(name, None)
    T._link(root)
    parts = [T.sphere(name + "_lijf", (0, 0, 0.14), 0.1, fur, scale=(0.85, 1.7, 0.85), seg=14, ol=0.004),
             T.sphere(name + "_kop", (0, -0.19, 0.22), 0.078, fur, seg=14, ol=0.004),
             T.sphere(name + "_snuit", (0, -0.255, 0.205), 0.035, light, scale=(1.2, 0.8, 0.8), seg=10, ol=0.002),
             T.to_mesh(T.tube(name + "_staart", [(0, 0.15, 0.15), (0, 0.24, 0.26), (0.03, 0.22, 0.38), (0.05, 0.17, 0.42)], 0.018, fur))]
    for sx in (-1, 1):
        parts.append(T.sphere(f"{name}_oor{sx}", (sx * 0.045, -0.18, 0.29), 0.03, fur, scale=(0.6, 0.35, 1.2), rot=(0, sx * 15, 0), seg=8, ol=0.002))
        parts.append(T.sphere(f"{name}_oog{sx}", (sx * 0.03, -0.248, 0.235), 0.014, S.mat("kat_oog", (0.5, 0.95, 0.3), 1.5), seg=8, ol=0.001))
        for sy in (-1, 1):
            parts.append(T.cyl(f"{name}_poot{sx}{sy}", (sx * 0.05, sy * 0.1, 0.0), 0.022, 0.12, light if sy < 0 else fur, seg=8, ol=0.002))
    for o in parts:
        o.parent = root
    return root


cat = make_cat("Kat")
cat.location = CAT0
cat.rotation_euler.z = math.radians(160)

held = S.actor("hoofdpersonage", (-11.0, -6.8, 0), -110)
vriend = S.actor("beste_vriend", (-11.6, -7.7, 0), -110)
phone = prop_phone(S, "Vriend_telefoon", (0, 0, 0), screen=(0.9, 0.95, 1.0))
phone.scale = (1.7,) * 3
attach(phone, vriend, "hand.R", (0, 0.06, 0.0), (90, 0, 0))

# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.15)
S.music("pizz_spanning", 0.0, 0.0, vol=0.28, fade_in=0.5, fade_out=0.4)
PIZZ = S.sounds[-1]
l3 = S.say("S07-03", gap=0.5)
MEOW = l3[0] + 2.6
S.sfx("sfx_kat", MEOW - 0.25, 0.7)
l4 = S.say("S07-04", who=vriend, gap=0.35, gain=1.2)
l5 = S.say("S07-05", gap=0.35)
CROUCH = l5[0] + 1.6
GRAB = l5[0] + 3.0
LIFT = l5[0] + 3.85
UP = LIFT + 0.9
S.sfx("sfx_auto_tillen", LIFT + 0.4 - 1.15, 0.9)
PIZZ["loop_to"] = LIFT - 0.2
l6 = S.say("S07-06", gap=0.5)
l7 = S.say("S07-07", gap=0.4)
OUT = l7[0] + 0.05
LOOK = l7[0] + 1.45
AWAY = l7[0] + 2.75
S.music("orkest_held", LIFT - 0.4, l7[1] + 0.1, vol=0.3, fade_in=0.4, fade_out=0.15)
S.sfx("sfx_blik_plop", l7[1] + 0.12, 0.6)          # het komische 'plink'
l8 = S.say("S07-08", gap=0.5)
DOWN = l8[0] + 0.1
S.wait(1.2)
END = S.t
S.music("mall", l8[0] - 0.2, END + 0.2, vol=0.18, fade_in=0.6, fade_out=0.6, start=20.0)

S.real(l6[0] + 0.1, l6[1] + 0.2)
S.text("UNTRAINED DEADLIFT: 60 kg", l6[0] + 1.6, l6[1] + 0.2, loc=(0.965, 0.30), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("x 32 = 1,920 kg", l6[0] + 5.65, l6[1] + 0.2, loc=(0.965, 0.22), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("SMALL CAR: 1,450 kg", l6[0] + 9.1, l6[1] + 0.2, loc=(0.965, 0.14), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.gauge("1,450 kg", l6[0] + 9.1, l7[1])
S.text("● REC", l8[0], END, loc=(0.965, 0.94), size=56, color=(1.0, 0.25, 0.2, 1), anchor=("RIGHT", "TOP"))

# ---------------------------------------------------------------- ze lopen binnen, horen de kat
H_STOP = V(-4.3, -9.7, 0)
V_STOP = V(-5.3, -8.9, 0)
S.beat(held, 0.0, "ontspannen", face="blij", face_amt=0.5, at=S.head(vriend, 0))
S.beat(vriend, 0.0, "ontspannen", face="lach", face_amt=0.6, at=S.head(held, 0))
S.walk(held, 0.1, l3[0] + 2.3, [V(-11.0, -6.8, 0), V(-7.0, -8.4, 0), H_STOP])
S.walk(vriend, 0.1, l3[0] + 2.3, [V(-11.6, -7.7, 0), V(-8.0, -8.6, 0), V_STOP])
S.beat(held, MEOW, "staan", face="verbaasd", face_amt=0.7, at=CAT0 + V(0, 0, 0.3))
S.turn(held, MEOW + 0.1, MEOW + 0.6, heading(H_STOP, CAT0), H_STOP)
S.beat(vriend, MEOW + 0.1, "staan", face="verbaasd", face_amt=0.6, at=CAT0 + V(0, 0, 0.3))
S.turn(vriend, MEOW + 0.2, MEOW + 0.7, heading(V_STOP, CAT0), V_STOP)
S.beat(held, l3[1] - 0.6, "staan", face="verdrietig", face_amt=0.5, at=CAT0 + V(0, 0, 0.2))
# vriend: 'Just wait for the owner'
S.beat(vriend, l4[0], "handen_zij", amount=0.5, face="nerveus", face_amt=0.9, at=S.head(held, l4[0]),
       arms=arms(arm("L", (0.4, 0.5, -0.3), (0.2, 0.6, 0.6)), arm("R", (0.4, 0.5, -0.3), (0.2, 0.6, 0.6))))
S.beat(vriend, l4[1], "staan", face="nerveus", face_amt=0.7, at=S.head(held, l4[1]))
# hij loopt naar de bumper
STAND = V(CX, CY + 2.55, 0)                  # vlak voor de bumper, kijkt naar -y
S.walk(held, l4[0] + 0.3, l5[0] + 0.6, [H_STOP, V(CX + 0.2, CY + 3.3, 0), STAND], end_rot=0)
S.beat(held, l5[0] + 0.1, "staan", face="twijfel", face_amt=0.6, look=(-0.6, 0), body={"head": (0, -35, 0)})
S.beat(held, l5[0] + 0.8, "staan", face="twijfel", face_amt=0.6, look=(0.6, 0), body={"head": (0, 35, 0)})
S.beat(held, CROUCH, "staan", face="vastberaden", at=bumper_at(0) + V(0, 0, 0.2), crouch=(0.3, 30), feet=((0.08, 0.05, 0), (-0.08, 0.1, 0)))
S.reach(held, CROUCH, "L", None, 0.0)
S.reach(held, CROUCH, "R", None, 0.0)
S.reach(held, GRAB, "L", bumper_at(0, 0.35) + V(0, 0.03, 0.0))
S.reach(held, GRAB, "R", bumper_at(0, -0.35) + V(0, 0.03, 0.0))
S.beat(held, GRAB, "staan", face="inspanning", face_amt=0.5, at=bumper_at(0) + V(0, -0.5, 0.4), crouch=(0.34, 32), feet=((0.08, 0.05, 0), (-0.08, 0.1, 0)))
S.hold(held, LIFT)
# ...en tillen: de auto draait om de achterwielen omhoog, hij komt overeind
for k in range(7):
    t = LIFT + (UP - LIFT) * k / 6
    deg = LIFT_DEG * smooth(0, 1, k / 6)
    S.reach(held, t, "L", bumper_at(deg, 0.35) + V(0, 0.02, 0.0))
    S.reach(held, t, "R", bumper_at(deg, -0.35) + V(0, 0.02, 0.0))
key(lifter, 0, rot=(0, 0, 0))
key(lifter, LIFT, rot=(0, 0, 0))
key(lifter, UP, rot=(LIFT_DEG, 0, 0))
S.place(held, LIFT, STAND, 0)
S.place(held, UP, STAND + V(0, -0.22, 0), 0)
S.beat(held, LIFT + 0.3, "staan", face="inspanning", face_amt=0.8, at=bumper_at(10) + V(0, 0, 0.3), crouch=(0.15, 8))
S.beat(held, UP, "staan", face="zelfverzekerd", face_amt=0.7, look=(0.3, 0.2), crouch=(0.02, -10), body={"head": (0, 12, 0)})
# vasthouden tijdens de uitleg (een beetje te makkelijk)
for k in range(int((l7[1] - UP) / 0.9)):
    t = UP + 0.45 + k * 0.9
    S.reach(held, t, "L", bumper_at(LIFT_DEG + 0.4 * (k % 2), 0.35) + V(0, 0.02, 0.0))
    S.reach(held, t, "R", bumper_at(LIFT_DEG + 0.4 * (k % 2), -0.35) + V(0, 0.02, 0.0))
key(lifter, UP + 1.0, rot=(LIFT_DEG + 0.4, 0, 0))
key(lifter, l7[1] + 0.4, rot=(LIFT_DEG, 0, 0))
S.beat(held, l6[0] + 2.0, "staan", face="blij", face_amt=0.6, at=S.head(vriend, UP), crouch=(0.02, -10))
S.beat(held, l6[0] + 6.0, "staan", face="grijns", face_amt=0.7, look=(0.5, 0.2), crouch=(0.02, -10))
S.beat(held, OUT, "staan", face="blij", face_amt=0.6, at=CAT0 + V(0.5, 1.0, 0.2), crouch=(0.02, -8))
S.beat(held, LOOK + 0.2, "staan", face="blij", face_amt=0.9, at=CAT0 + V(1.2, 1.6, 0.2), crouch=(0.02, -8))
S.beat(held, AWAY + 0.3, "staan", face="twijfel", face_amt=0.8, at=CAT0 + V(3.5, 3.0, 0.2), crouch=(0.02, -8))
S.hold(held, DOWN)
# voorzichtig neerzetten
key(lifter, DOWN, rot=(LIFT_DEG, 0, 0))
key(lifter, DOWN + 1.2, rot=(0, 0, 0))
for k in range(5):
    t = DOWN + 1.2 * k / 4
    deg = LIFT_DEG * (1 - smooth(0, 1, k / 4))
    S.reach(held, t, "L", bumper_at(deg, 0.35) + V(0, 0.02, 0.0))
    S.reach(held, t, "R", bumper_at(deg, -0.35) + V(0, 0.02, 0.0))
S.place(held, DOWN, STAND + V(0, -0.22, 0), 0)
S.place(held, DOWN + 1.2, STAND, 0)
S.beat(held, DOWN + 1.2, "staan", face="blij", face_amt=0.5, at=bumper_at(0), crouch=(0.3, 28))
S.reach(held, DOWN + 1.5, "L", None, 0.0)
S.reach(held, DOWN + 1.5, "R", None, 0.0)
S.beat(held, DOWN + 1.8, "staan", face="grijns", face_amt=0.7, at=S.head(vriend, DOWN))
S.hold(held, END)
S.sfx("sfx_dreun", DOWN + 1.15, 0.25)

# vriend filmt
S.beat(vriend, LIFT - 0.3, "schrik", amount=0.6, face="geschrokken", at=bumper_at(15))
S.beat(vriend, UP + 0.5, "filmen", face="verbaasd", face_amt=0.8, at=S.head(held, UP))
S.beat(vriend, l6[0] + 4.0, "filmen", face="lach", face_amt=0.7, at=S.head(held, UP))
S.hold(vriend, END)
show(phone, UP + 0.4)

# de kat: zit vast, loopt naar buiten, kijkt even om, loopt weg
c_pts = [CAT0, CAT0 + V(0.35, 0.9, 0), CAT0 + V(1.4, 2.0, 0)]
c_pts2 = [c_pts[-1], c_pts[-1] + V(1.8, 1.4, 0), c_pts[-1] + V(6.0, 3.0, 0)]
key(cat, 0, loc=CAT0, rot=(0, 0, 160))
key(cat, OUT, loc=CAT0, rot=(0, 0, 160))


def cat_walk(t0, t1, pts, step=0.16):
    n = max(2, int((t1 - t0) / (1 / 12)))
    segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(segs)
    for i in range(n + 1):
        u = i / n
        d = total * u
        for j, L in enumerate(segs):
            if d <= L or j == len(segs) - 1:
                p = pts[j].lerp(pts[j + 1], min(1.0, d / L))
                dirv = pts[j + 1] - pts[j]
                break
            d -= L
        t = t0 + (t1 - t0) * u
        key(cat, t, loc=p + V(0, 0, 0.012 * abs(math.sin(u * 30))), rot=(0, 0, heading((0, 0), (dirv.x, dirv.y))))


cat_walk(OUT, LOOK, c_pts)
key(cat, LOOK + 0.25, loc=c_pts[-1], rot=(0, 0, heading(c_pts[-1], S.head(held, LOOK))))
key(cat, AWAY - 0.1, loc=c_pts[-1], rot=(0, 0, heading(c_pts[-1], S.head(held, LOOK))))
cat_walk(AWAY, AWAY + 2.6, c_pts2)
S.sfx("sfx_kat", LOOK - 0.1, 0.35)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((2.0, -7.6, 1.5), (-6.0, -8.4, 1.1), 26), ((1.6, -7.8, 1.5), (-5.0, -9.0, 1.0), 28))
S.cam(l3[0] + 3.3, ((CX + 0.7, CY + 3.3, 0.2), CAT0 + V(0, 0, 0.16), 34), ((CX + 0.65, CY + 3.1, 0.19), CAT0 + V(0, 0, 0.16), 40))
S.cam(l4[0] - 0.1, S.shot(vriend, l4[0], "mcu", az=20, lens=30), S.shot(vriend, l4[1], "mcu", az=16, lens=34))
S.cam(l5[0] - 0.1, ((0.8, -10.6, 1.3), (CX, CY + 2.0, 0.8), 24), ((0.7, -10.7, 1.2), (CX, CY + 2.0, 0.75), 26))
S.cam(GRAB - 0.3, ((CX + 1.8, CY + 3.9, 0.35), (CX - 0.2, CY + 1.9, 1.1), 20), ((CX + 1.8, CY + 3.9, 0.35), (CX - 0.2, CY + 1.9, 1.35), 20),
      shake=lambda t: max(0.0, 1.0 - (t - LIFT) * 1.2) if t > LIFT else 0.0)
S.cam(UP + 0.6, ((4.0, -7.0, 1.9), (CX + 0.2, CY + 1.0, 0.9), 22), ((3.6, -7.3, 1.9), (CX + 0.2, CY + 1.0, 0.9), 24))
S.cam(l6[0] + 5.5, S.shot(held, l6[0] + 6, "med", az=70, lens=28, h=0.5), S.shot(held, l6[1], "med", az=64, lens=30, h=0.5))
S.cam(OUT - 0.1, ((CX + 2.6, CY + 3.6, 0.3), CAT0 + V(0.8, 1.2, 0.15), 26), ((CX + 2.6, CY + 3.6, 0.3), CAT0 + V(1.3, 1.9, 0.15), 28))
S.cam(LOOK, (c_pts[-1] + V(-0.85, 0.1, 0.24), c_pts[-1] + V(0, 0, 0.2), 32), (c_pts[-1] + V(-0.8, 0.12, 0.24), c_pts[-1] + V(0, 0, 0.2), 38))
S.cam(AWAY + 0.2, ((CX + 1.2, CY + 3.9, 0.6), c_pts2[1] + V(0, 0, 0.2), 26), ((CX + 1.2, CY + 3.9, 0.6), c_pts2[2] + V(0, 0, 0.2), 26))
S.cam(l8[0] - 0.1, S.shot(vriend, l8[0], "med", az=-12, lens=28), S.shot(vriend, END, "mcu", az=-8, lens=32))

S.finish(length=END)
