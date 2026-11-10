"""OR2 · What if everyone disappeared except you? · nieuwe stijl: speelgoedstadje (ochtend -> avond) + slaapkamer.

1  hook: close, je kijkt om je heen; de camera stijgt op: jij alleen op een leeg kruispunt.
2  HOUR 1: een rij auto's voor rood, motoren lopen (uitlaatwolkjes), niemand achter het stuur. Jij loopt ertussen.
3  DAY 1: jij op het dak van een auto, armen omhoog. De stad is van jou.
4  DAY 3 ('s avonds): de stad gaat blok voor blok op zwart, van de horizon naar jou toe.
5  DAY 7: jij aan je bureau, draaiend aan een oude radio. Ruis... dan een stem.
6  "And it's... your voice." Close op je gezicht, de radio gloeit mee.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or2")
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W

# ------------------------------------------------------------------------------------------------ stad
P4 = V(0.3, 15.0, 0.0)


def blocks(x, y):
    if y > 12:
        return "ABCDEFGH"[min(7, max(0, int((y - 12) / 6)))]
    return "Z"


T_ = town(0, 0, half=60, blocks=blocks, seed=2)
tl_state(T_, 0.0, "rood")
# rij wachtende auto's (rijstrook x = +1.75, rijrichting +y)
CARS = []
for i, col in enumerate(((220, 60, 50), (60, 130, 220), (250, 200, 60), (90, 190, 120))):
    y = -11.0 - i * 5.4
    CARS.append((car(f"Auto_{i}", 1.75, y, 90, col), V(1.75, y, 0)))
car("Auto_geparkeerd_0", -5.0 + 0.0, 22.0, -90, (240, 240, 240))
car("Auto_geparkeerd_1", 9.0, -1.75, 180, (160, 90, 200))

# ------------------------------------------------------------------------------------------------ 1: hook
P1 = V(0.4, 0.4, 0)
S.place(b, 0.0, P1, 0)
S.beat(b, 0.0, face="verbaasd", amt=0.8, head=dict(turn=28, up=2), arms="los")
S.beat(b, Wd(1, 3), face="verbaasd", head=dict(turn=-30, up=2), arms="los")
S.beat(b, Wd(1, 6), face="bang", amt=0.8, head=dict(turn=0, up=6), arms="schrik")
S.beat(b, e(1), face="bang", head=dict(turn=-4, up=8), arms="schrik")
HEAD1 = P1 + V(0, 0, 1.47)
UP = Wd(1, 5) - 0.1
S.shot(0.0, ((P1.x + 0.25, P1.y - 1.35, 1.5), tuple(HEAD1 + V(0, 0, -0.06)), 32),
       ((P1.x + 0.3, P1.y - 1.55, 1.52), tuple(HEAD1 + V(0, 0, -0.06)), 32))
S.shot(UP, ((P1.x + 0.6, P1.y - 2.4, 1.6), tuple(P1 + V(0, 0, 1.0)), 30),
       ((P1.x + 6.0, P1.y - 20.0, 26.0), tuple(P1 + V(0, 3.0, 0.0)), 24), focus="aim")

# ------------------------------------------------------------------------------------------------ 2: auto's
h1 = r(2)
wa, wb = V(-0.2, -9.5, 0), V(-0.2, -17.5, 0)
S.teleport(b, h1, wa, 0)
S.walk(b, h1 + 0.05, r(3) - 0.08, [wa, wb])
S.face(b, h1 + 0.1, "nerveus", 0.7)
S.head(b, h1 + 0.1, turn=0)
S.head(b, h1 + 1.0, turn=-35, up=-2)
S.face(b, Wd(2, 6), "verbaasd", 0.9)
S.head(b, Wd(2, 6), turn=-45, up=-4)
S.head(b, r(3) - 0.1, turn=-30, up=-2)
for i, (root, p) in enumerate(CARS):
    pipe = p + V(0.35, -2.05, 0.3)
    t, k = h1 + 0.07 * i, 0
    while t < r(3):
        puff(f"Uitlaat_{i}_{k}", pipe, t, dur=1.0, r=0.13, rise=0.45, drift=(0.15, -0.35, 0))
        t += 0.4
        k += 1
    # motor loopt: auto trilt een beetje
    for f in range(FR(h1), FR(r(3)) + 1, 2):
        key(root, "location", f, p + V(0, 0, 0.008 * ((f // 2) % 2)))
S.shot(h1, ((-0.9, -23.5, 0.7), (0.4, -13.0, 1.0), 30), ((-0.85, -22.6, 0.75), (0.3, -13.6, 1.05), 32))

# ------------------------------------------------------------------------------------------------ 3: op het autodak
d1 = r(3)
car3, cp = CARS[1]
ROOF = cp + V(0, -0.2, 1.63)
S.teleport(b, d1, ROOF, 27)
S.beat(b, d1, face="heel_blij", arms="juichen", body=dict(dz=0.0))
for k, t in enumerate((d1 + 0.35, d1 + 0.75, d1 + 1.15, d1 + 1.55, d1 + 1.95)):
    S.beat(b, t, face="heel_blij", arms="juichen" if k % 2 == 0 else "omhoog",
           body=dict(dz=0.04 if k % 2 == 0 else 0.0, squash=1.03 if k % 2 == 0 else 0.97), head=dict(up=8, tilt=5 - 10 * (k % 2)))
S.beat(b, e(3), face="heel_blij", arms="juichen", head=dict(up=10))
S.shot(d1, ((ROOF.x + 1.6, ROOF.y - 3.2, 1.2), tuple(ROOF + V(0, 0, 1.15)), 24),
       ((ROOF.x + 2.4, ROOF.y - 4.4, 1.0), tuple(ROOF + V(0, 0, 1.25)), 22))

# ------------------------------------------------------------------------------------------------ 4: de stroom valt uit
d3 = r(4)
S.teleport(b, d3, P4, 0)
t_go = Wd(4, 3) - 0.05
T_A = Wd(4, 5) + 0.05
order = "HGFEDCBA"
for k, blk in enumerate(order):
    t_off = t_go + k * (T_A - 0.25 - t_go) / 7 if blk != "A" else T_A
    for bb in (blk,) + (("Z",) if blk == "A" else ()):
        m_ = T_["win_mats"].get(bb)
        if m_:
            sock = m_.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
            key_value(sock, [(0.0, 0.0), (d3 - 0.04, 0.0), (d3, 3.0), (t_off - 0.034, 3.0), (t_off, 0.0)])
        for post, bulb, li, lb in T_["lamps"]:
            if lb == bb:
                key_energy(li, [(0.0, 0), (d3 - 0.04, 0), (d3, 400), (t_off - 0.034, 400), (t_off, 0)])
        lm = bpy.data.materials.get(f"Lamp_{bb}")
        if lm:
            key_value(lm.node_tree.nodes["Emission"].inputs["Strength"], [(0.0, 0.2), (d3 - 0.04, 0.2), (d3, 6.0), (t_off - 0.034, 6.0), (t_off, 0.1)])
for idb in [m for m in T_["win_mats"].values() if m] + [li.data for _, _, li, _ in T_["lamps"]] + \
        [bpy.data.materials.get(f"Lamp_{x}") for x in order + "Z" if bpy.data.materials.get(f"Lamp_{x}")]:
    tgt = idb.node_tree if hasattr(idb, "node_tree") and idb.node_tree else idb
    for fc in fcurves(tgt):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
S.beat(b, d3, face="nerveus", amt=0.6, head=dict(up=4))
S.beat(b, t_go + 0.3, face="bang", amt=0.7, head=dict(up=6, turn=-6))
S.beat(b, T_A - 0.2, face="bang", head=dict(up=4, turn=10), arms="schrik")
S.beat(b, T_A + 0.1, face="geschrokken", head=dict(up=2, turn=22), arms="schrik", body=dict(lean=-4))
S.beat(b, r(5) - 0.05, face="geschrokken", amt=0.9, head=dict(up=2, turn=26), arms="schrik", body=dict(lean=-4))
S.blink(b, T_A + 0.25)
HEAD4 = P4 + V(0, 0, 1.47)
S.shot(d3, ((P4.x + 2.2, P4.y - 6.5, 1.3), (P4.x - 6.0, P4.y + 22, 4.0), 22),
       ((P4.x + 2.0, P4.y - 5.8, 1.3), (P4.x - 6.0, P4.y + 22, 4.2), 24), focus=HEAD4)
S.shot(T_A - 0.45, ((P4.x + 0.3, P4.y - 1.4, 1.42), tuple(HEAD4 + V(0, 0, -0.06)), 32),
       ((P4.x + 0.26, P4.y - 1.25, 1.42), tuple(HEAD4 + V(0, 0, -0.06)), 34))
moon_l = area("Maan_gezicht", HEAD4 + V(1.5, -3.0, 2.0), HEAD4, 1.5, 0, (0.55, 0.65, 1.0))
key_energy(moon_l, [(0, 0), (d3 - 0.04, 0), (d3, 160), (r(5) - 0.04, 160), (r(5), 0)])
warm4 = area("Lantaarn_gezicht", HEAD4 + V(-2.0, -1.5, 2.5), HEAD4, 1.0, 0, (1.0, 0.75, 0.45))
key_energy(warm4, [(0, 0), (d3 - 0.04, 0), (d3, 120), (T_A - 0.034, 120), (T_A, 0)])
for fc in fcurves(warm4.data):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------------------------------------ 5-6: slaapkamer, radio
KX = 300.0
K = V(KX, 0, 0)
room("Slaapkamer", K, 4.0, 3.6, 2.6, open_side="-y", wall=(170, 190, 225), floor=(190, 140, 95),
     window=("+x", 0.6, 1.5, 1.0, 1.0))
desk_m = mat("Bureau", (235, 225, 205), rough=0.4, coat=0.3)
DX, DY = KX + 1.35, 0.4                          # bureau tegen de rechtermuur (+x)
box("Bureaublad", (DX, DY, 0.74), (0.7, 1.4, 0.05), desk_m, bev=0.02)
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f"Bureaupoot_{sx}_{sy}", (DX + sx * 0.3, DY + sy * 0.65, 0.36), (0.05, 0.05, 0.72), desk_m, bev=0.01)
chair_m = mat("Stoel", (90, 150, 220), rough=0.4, coat=0.4)
CH = V(KX + 0.55, 0.3, 0)
box("Stoelzitting", CH + V(0, 0, 0.47), (0.48, 0.48, 0.06), chair_m, bev=0.02)
box("Stoelleuning", CH + V(-0.25, 0, 0.8), (0.05, 0.46, 0.55), chair_m, bev=0.02)
cyl("Stoelpoot", CH, 0.04, 0.45, mat("Paal", (60, 70, 80), rough=0.4, coat=0.3))
# radio
RX, RY, RZ = DX - 0.05, DY - 0.1, 0.765
wood = mat("Radiohout", (150, 85, 45), rough=0.45, coat=0.5)
radio = box("Radio", (RX, RY, RZ + 0.13), (0.28, 0.46, 0.26), wood, bev=0.04)
box("Radio_doek", (RX - 0.142, RY + 0.08, RZ + 0.14), (0.01, 0.2, 0.17), mat("Radiodoek", (220, 200, 160), rough=0.9, sheen=0.5), bev=0.01)
dial_m = glow("Radio_schaal_gloed", (255, 190, 90), 2.0)
box("Radio_schaal", (RX - 0.143, RY - 0.12, RZ + 0.19), (0.01, 0.16, 0.06), dial_m, bev=0.005)
needle = box("Radio_naald", (RX - 0.148, RY - 0.17, RZ + 0.19), (0.006, 0.008, 0.055), mat("Naald", (220, 40, 30)), bev=0)
knob = cyl("Radio_knop", (RX - 0.14, RY - 0.12, RZ + 0.07), 0.035, 0.04, mat("Knop", (60, 45, 35)), rot=(0, -90, 0))
cyl("Radio_antenne", (RX + 0.05, RY + 0.15, RZ + 0.26), 0.006, 0.4, mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6), rot=(18, 0, 0))
box("Bed", (KX - 1.2, 0.9, 0.25), (1.0, 2.0, 0.5), mat("Bed_deken", (240, 150, 120), rough=0.8, sheen=0.6), bev=0.08)
box("Kussen", (KX - 1.2, 1.65, 0.56), (0.7, 0.35, 0.14), mat("Kussen", (250, 250, 245), rough=0.8, sheen=0.5), bev=0.06)
box("Poster", (KX - 0.3, 1.79, 1.6), (0.6, 0.02, 0.8), mat("Poster", (250, 120, 70), rough=0.6), bev=0.0)
radio_light = point("Radiogloed", (RX - 0.35, RY - 0.12, RZ + 0.25), 8, (1.0, 0.62, 0.3), 0.05)
moon_room = area("Maanlicht_kamer", (KX + 2.6, 0.6, 2.2), (KX + 0.5, 0.3, 0.8), 1.2, 0, (0.55, 0.65, 1.0))
key_energy(moon_room, [(0, 0), (r(5) - 0.04, 0), (r(5), 90)])
fill_room = area("Kamer_vul", (KX - 0.8, -2.5, 1.8), (KX + 0.8, 0.3, 1.0), 2.0, 0, (0.7, 0.75, 1.0))
key_energy(fill_room, [(0, 0), (r(5) - 0.04, 0), (r(5), 30)])
d7 = r(5)
SEAT = V(CH.x, CH.y, 0)
S.teleport(b, d7, SEAT, 90)                     # kijkt naar +x (bureau)
SIT = dict(dz=-0.19, lean=6)
S.beat(b, d7, face="nerveus", amt=0.5, arms="rust", r_arm="radio", body=SIT, head=dict(up=-8), legs=85)
S.beat(b, d7 + 0.5, face="nieuwsgierig", arms="rust", r_arm="radio", body=SIT, head=dict(up=-10, tilt=6), legs=85)
S.beat(b, Wd(5, 2) - 0.1, face="nieuwsgierig", arms="rust", r_arm=("radio"), body=SIT, head=dict(up=-10, tilt=6), legs=85)
S.beat(b, Wd(5, 4), face="blij", arms="rust", r_arm="rust", body=dict(dz=-0.19, lean=10), head=dict(up=-6, tilt=4), legs=85)
S.beat(b, e(5), face="blij", amt=0.8, arms="rust", body=dict(dz=-0.19, lean=10), head=dict(up=-6, tilt=4), legs=85)
d6 = r(6)
S.beat(b, Wd(6, 1), face="verbaasd", amt=0.7, body=dict(dz=-0.19, lean=8), head=dict(up=-6), legs=85)
S.beat(b, Wd(6, 2), face="geschrokken", arms="rust", body=dict(dz=-0.19, lean=-4), head=dict(up=-2), legs=85)
S.beat(b, END, face="bang", arms="rust", body=dict(dz=-0.19, lean=-6), head=dict(up=-2, tilt=-3), legs=85)
S.blink(b, Wd(6, 2) + 0.15)
for t, a in ((d7, 0), (d7 + 0.5, 0), (Wd(5, 2) - 0.1, 220)):
    key(knob, "rotation_euler", FR(t), (R(a), R(-90), 0))
for t, y in ((d7 + 0.5, RY - 0.17), (Wd(5, 2) - 0.1, RY - 0.06)):
    key(needle, "location", FR(t), V(RX - 0.148, y, RZ + 0.19))
for k, t in enumerate(frange(d7, END, 0.1)):
    on = t >= Wd(5, 4)
    ee = 8 * (1.0 + (0.7 * math.sin(t * 23) * math.sin(t * 7.3) if on else 0.15 * math.sin(t * 40)))
    radio_light.data.energy = ee
    radio_light.data.keyframe_insert("energy", frame=FR(t))
    dial_m.node_tree.nodes["Emission"].inputs["Strength"].default_value = 2.0 * ee / 8
    dial_m.node_tree.nodes["Emission"].inputs["Strength"].keyframe_insert("default_value", frame=FR(t))
HEAD7 = SEAT + V(0.05, 0, 1.47 - 0.19)
S.shot(d7, ((KX + 1.68, -0.45, 1.36), tuple(HEAD7 * 0.7 + V(RX, RY, 0.95) * 0.3), 24),
       ((KX + 1.62, -0.38, 1.34), tuple(HEAD7 * 0.75 + V(RX, RY, 0.95) * 0.25), 26))
S.shot(d6 - 0.15, ((HEAD7.x + 1.0, HEAD7.y - 0.42, HEAD7.z + 0.0), tuple(HEAD7 + V(0, 0, -0.05)), 28),
       ((HEAD7.x + 0.9, HEAD7.y - 0.36, HEAD7.z + 0.0), tuple(HEAD7 + V(0, 0, -0.05)), 34))


# ------------------------------------------------------------------------------------------------ licht en lucht
def world():
    fac, strength = sky_blend(("dag", "nacht"))
    key_value(fac, [(0, 0.0), (d3 - 0.04, 0.0), (d3, 0.75), (d7 - 0.04, 0.75), (d7, 1.0)])
    key_value(strength, [(0, 0.85), (d3 - 0.04, 0.85), (d3, 0.35), (d7 - 0.04, 0.35), (d7, 0.12)])
    sn = sun(3.6, (1.0, 0.9, 0.75), d=(-0.5, -0.45, 0.6))
    key_energy(sn, [(0, 3.6), (d3 - 0.04, 3.6), (d3, 0.25), (d7 - 0.04, 0.25), (d7, 0.0)])
    fl = three_point("Stad", (0.4, -6.0, 0), 0, scale=2.2)
    for li in fl:
        key_energy(li, [(0, li.data.energy), (d3 - 0.04, li.data.energy), (d3, 0)])


S.world_fn = world
S.done()
