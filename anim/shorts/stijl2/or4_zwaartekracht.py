"""OR4 · What if gravity switched off for one second? · nieuwe stijl: zonnige speelgoedwoonstraat.

1  hook: de hele straat zweeft al: auto's, bomen, mensen en jij, langzaam omhoog.
2  0.1 s: je voeten komen los van de stoep.
3  0.4 s: het water klimt in bolletjes uit je glas.
4  0.7 s: auto's, bomen, mensen... alles drijft omhoog.
5  0.9 s: je hangt hoog boven de daken; de straat ligt ver onder je.
6  "And then... gravity comes back." Je valt.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or4", cast=("hoofdpersonage", "mama", "papa", "opa"))
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W
r2, r3, r4, r5, r6 = (r(n) for n in (2, 3, 4, 5, 6))
HIGH = 40.0
fall0 = Wd(6, 4) + 0.05


def ease(u, p=1.7):
    return max(0.0, min(1.0, u)) ** p


T_ = town(0, 0, half=60, cross=False, seed=4, lamps=True)
P = V(-5.0, 6.0, 0.15)
S.place(b, 0.0, P, 0)

# glas water in je hand
gm = bpy.data.materials.new("Waterglas")
pb = gm.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = (0.92, 0.97, 1.0, 1)
pb.inputs["Roughness"].default_value = 0.03
L.set_in(pb, "Transmission Weight", 1.0)
pb.inputs["IOR"].default_value = 1.45
glass = cyl("Waterglas", (0, 0, 0), 0.045, 0.13, gm)
attach(glass, b.el[1], hand_offset(b, 1) + V(0.0, -0.06, -0.03))
water_m = mat("Water", (70, 160, 250), rough=0.05, coat=0.8)
water = cyl("Water_in_glas", (0, 0, 0.006), 0.04, 0.09, water_m)
water.parent = glass
HOLD = ((-45, 4, 18), (-70, 0, 0))


def hero_z(t):
    if t < r2 + 0.9:
        return 0.0
    if t < r3:
        return 0.3 * ease((t - r2 - 0.9) / (r3 - r2 - 0.9), 1.4)
    if t < r4:
        return 0.3 + 0.6 * (t - r3) / (r4 - r3)
    if t < r5:
        return 0.9 + 3.2 * ease((t - r4) / (r5 - r4), 1.3)
    return 0.0


for t in frange(r2, r5 - 0.04, 0.1):
    S.place(b, t, P + V(0, 0, hero_z(t)), 0)
S.place(b, r5 - 0.034, P + V(0, 0, hero_z(r5 - 0.04)), 0)
S.teleport(b, r5, P + V(0, 0, HIGH), 0)
for t in frange(r5, fall0, 0.2):
    S.place(b, t, P + V(0, 0, HIGH + 1.2 * (t - r5) / (fall0 - r5)), 0)
for t in frange(fall0, END + 0.1, 0.05):
    dt = t - fall0
    S.place(b, t, P + V(0, 0, HIGH + 1.2 - 0.5 * 9.81 * dt * dt), 0)

S.beat(b, r2, face="neutraal", r_arm=HOLD, head=dict(up=-8))
S.beat(b, r2 + 0.9, face="verbaasd", amt=0.7, r_arm=HOLD, head=dict(up=-25))
S.beat(b, r3 - 0.1, face="verbaasd", arms="zweven", r_arm=HOLD, head=dict(up=-25), legs=(8, -6))
S.beat(b, Wd(3, 4), face="verbaasd", arms="zweven", r_arm=HOLD, head=dict(up=-12, turn=-10), legs=(10, -8))
S.beat(b, r4 - 0.05, face="verbaasd", arms="zweven", r_arm=HOLD, head=dict(up=-10, turn=-10), legs=(10, -8))
S.beat(b, r4 + 0.3, face="geschrokken", arms="schrik", head=dict(up=6, turn=20), body=dict(lean=-6, side=6), legs=(16, -10))
S.beat(b, Wd(4, 6), face="bang", arms="omhoog", head=dict(up=8, turn=-20), body=dict(lean=-8, side=-6), legs=(-6, 14))
S.beat(b, r5, face="bang", arms="zweven", head=dict(up=-30), body=dict(lean=14), legs=(12, -6))
S.beat(b, Wd(5, 5), face="bang", arms="zweven", head=dict(up=-34), body=dict(lean=16), legs=(14, -8))
S.beat(b, fall0, face="geschrokken", arms="juichen", head=dict(up=10), body=dict(lean=-14), legs=(20, -15))
S.beat(b, END, face="geschrokken", arms="omhoog", head=dict(up=12), body=dict(lean=-14), legs=(24, -18), mouth=dict(Schreeuw=0.6, E=0.3))
for t, on in ((0.0, False), (r2, True), (r4 + 0.25, False)):
    visible(glass, t, on)

rnd = random.Random(4)
for k in range(9):
    bb = ball(f"Waterbol_{k}", (0, 0, 0), 1.0, water_m)
    bb.parent = glass
    t0 = Wd(3, 4) - 0.1 + k * 0.07
    x, y = rnd.uniform(-0.02, 0.02), rnd.uniform(-0.02, 0.02)
    rr = rnd.uniform(0.022, 0.04)
    for t, loc, sc_ in ((0.0, (x, y, 0.08), 0.001), (t0, (x, y, 0.08), 0.001), (t0 + 0.15, (x, y, 0.12), rr),
                        (r4 + 0.2, (x * 4 + rnd.uniform(-0.06, 0.06), y * 4 + rnd.uniform(-0.06, 0.06), 0.28 + 0.45 * rnd.random()), rr * 1.2)):
        key(bb, "location", FR(t), V(loc))
        key(bb, "scale", FR(t), Vector((sc_,) * 3))
for t, z in ((0.0, 1.0), (Wd(3, 4) - 0.1, 1.0), (r4, 0.08)):
    key(water, "scale", FR(t), Vector((1, 1, z)))

# ------------------------------------------------------------------------------------------------ alles zweeft
FLOAT = []
L4A = r2 + 0.9


def drift(obj, h, spin, seed):
    rr = random.Random(seed)
    p0 = obj.location.copy()
    r0 = V(*obj.rotation_euler)
    sp = V(rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1)) * spin
    for t in frange(L4A, fall0 + 0.01, 0.2):
        u = (t - L4A) / (fall0 - L4A)
        ee = ease(u, 1.6)
        key(obj, "location", FR(t), p0 + V(0, 0, h * ee))
        key(obj, "rotation_euler", FR(t), tuple(r0[i] + R(sp[i] * ee) for i in range(3)))
    FLOAT.append(obj)


cars = [car("Auto_park_0", -2.6, 12.0, 90, (230, 70, 60)), car("Auto_park_1", 2.6, 10.0, -90, (70, 140, 230)),
        car("Auto_park_2", -2.6, 16.0, 90, (250, 200, 60)), car("Auto_park_3", 2.6, 1.0, -90, (120, 200, 130))]
for k, c in enumerate(cars):
    drift(c, 3.5 + k * 0.6, 25 + 5 * k, k)
for k, o in enumerate([o for o in bpy.data.objects if o.name.startswith("Boom_4_") and o.name.endswith("_stam")]):
    cr = bpy.data.objects[o.name.replace("_stam", "_kruin")]
    cr.parent = o
    cr.matrix_parent_inverse = o.matrix_world.inverted()
    drift(o, 2.5 + 0.4 * (k % 3), 10, 20 + k)
for k, (post, bulb, li, blk) in enumerate(T_["lamps"][:6]):
    for o in (bulb, li):
        o.parent = post
        o.matrix_parent_inverse = post.matrix_world.inverted()
    arm_ = bpy.data.objects.get(post.name.replace("paal", "arm"))
    if arm_:
        arm_.parent = post
        arm_.matrix_parent_inverse = post.matrix_world.inverted()
    drift(post, 1.6 + 0.3 * k, 18, 40 + k)
people = []
for k, (cn, loc, yaw) in enumerate((("mama", (-6.2, 9.5, 0.15), 30), ("papa", (-4.6, 1.5, 0.15), -20),
                                     ("opa", (5.2, 4.0, 0.15), -60))):
    ex = S.extra(cn)
    people.append(ex)
    S.beat(ex, 0.0, face="neutraal")
    S.beat(ex, r4 + 0.2, face="neutraal", arms="schrik", body=dict(lean=-8))
    S.beat(ex, END, face="neutraal", arms="omhoog", body=dict(lean=-10))
    for t in frange(0.0, L4A, 1.0):
        S.place(ex, t, loc, yaw)
    for t in frange(L4A, fall0 + 0.01, 0.2):
        u = (t - L4A) / (fall0 - L4A)
        S.place(ex, t, V(loc) + V(0, 0, 4.5 * ease(u, 1.6)), yaw + 40 * u * (1 if k % 2 else -1))

# hook: het stuk van regel 4 (alles zweeft) alvast laten zien
copy_anim(rig_objs(b) + FLOAT + sum((rig_objs(p) for p in people), []), r4 + 0.5, e(4), 0.0, e(1))
S.face(b, 0.0, "bang", 0.9)
S.face(b, e(1), "bang", 1.0)
S.place(b, r2 - 0.034, P + V(0, 0, hero_z(e(4))), 0)
S.place(b, r2, P, 0)
S.beat(b, r2 - 0.034, face="bang", arms="omhoog", head=dict(up=8))
for fc in fcurves(b.char):
    for kp in fc.keyframe_points:
        if abs(kp.co[0] - FR(r2 - 0.034)) < 0.5:
            kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------------------------------------ camera's
S.shot(0.0, ((-0.4, -4.5, 1.0), (-4.8, 6.0, 3.6), 32), ((-0.5, -4.0, 1.4), (-4.8, 6.0, 4.0), 34), focus=P + V(0, 0, 3.6))
S.shot(r2, ((P.x + 0.9, P.y - 1.7, 0.4), (P.x, P.y, 0.45), 26), ((P.x + 0.85, P.y - 1.6, 0.45), (P.x, P.y, 0.6), 28), focus="aim")
S.shot(r3, ((P.x + 1.2, P.y - 2.0, 1.75), (P.x + 0.1, P.y, 1.55), 26),
       ((P.x + 1.2, P.y - 2.0, 2.35), (P.x + 0.1, P.y, 2.15), 28))
S.shot(r4, ((-0.2, -5.5, 0.8), (-4.2, 6.0, 2.8), 28), ((-0.3, -5.0, 1.6), (-4.2, 6.0, 4.4), 30), focus=P + V(0, 0, 3.0))
HC = P + V(0, 0, HIGH + 0.9)
C5a, C5b, C6b = P + V(1.2, -2.6, HIGH + 3.4), P + V(1.1, -2.4, HIGH + 3.8), P + V(1.0, -2.2, HIGH + 4.2)
S.shot(r5, (tuple(C5a), tuple(HC + V(0, 0, -1.5)), 22), (tuple(C5b), tuple(HC + V(0, 0, -1.2)), 24), focus=HC)
S.shot(r6, (tuple(C5b), tuple(HC + V(0, 0, -1.2)), 24), (tuple(C6b), tuple(HC + V(0, 0, -2.4)), 26), focus=HC)


def world():
    sky("dag")
    sun(4.2, d=(-0.6, -0.35, 0.72))
    three_point("Straat", P, 0, scale=1.6)
    three_point("Hoog", P + V(0, 0, HIGH), 0, scale=1.6)


S.world_fn = world
S.done()
