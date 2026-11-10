"""OR5 · What if you turned invisible? · nieuwe stijl: slaapkamer (ochtend), zonnig zebrapad, bankkluis.

1  hook: je lichaam flikkert: het wordt doorzichtig als glas en komt weer terug.
2  SECOND 1: je houdt je handen voor je gezicht. Ze vervagen.
3  MINUTE 1: je loopt (als glas) over een vol zebrapad; niemand kijkt naar je.
4  HOUR 1: je wandelt de open bankkluis in, tussen de goudstaven. Je grijnst.
5  "Then... everything goes black." Zwart beeld (kaart in tekst/or5.json).
6  Licht schiet dwars door je doorzichtige hoofd (en je ogen) heen.
7  "You're invisible. And completely blind." In de kluis: jij, tastend, bang.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

CROWD = ("beste_vriend", "pestkop", "mama", "papa", "opa", "oma", "gymleraar", "wetenschapper")
S = Kort("or5", cast=("hoofdpersonage",) + CROWD)
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W
r2, r3, r4, r5, r6, r7 = (r(n) for n in (2, 3, 4, 5, 6, 7))

# ------------------------------------------------------------------------------------------------ glas-materialen
hands = set()
for s in (-1, 1):
    hands |= {o for o in b.el[s].children_recursive if o.type == "MESH"}
body = {o for o in b.char.children_recursive if o.type == "MESH"} - hands
socks = {"hand": [], "body": []}


def to_glass(objs, tag):
    def fn(m):
        nt = m.node_tree
        if nt and any(n.type == "LIGHT_PATH" for n in nt.nodes):
            return m                                    # ogen/wenkbrauwen/mond blijven zichtbaar
        n, sock = fade_material(m, tag, "glass")
        socks[tag].append(sock)
        return n
    material_swap(objs, fn)


to_glass(hands, "hand")
to_glass(body, "body")
flick = [(0.0, 0), (0.25, 0), (0.3, 1), (0.55, 1), (0.6, 0), (0.8, 0), (0.85, 1), (1.35, 1), (1.42, 0), (r2, 0), (r3 - 0.04, 0), (r3, 1)]
for sk in socks["body"]:
    key_value(sk, flick)
hf = Wd(2, 3)
for sk in socks["hand"]:
    key_value(sk, flick[:-3] + [(r2, 0), (hf, 0), (hf + 0.6, 0.6), (e(2), 1.0), (r3, 1.0)])
for sk in socks["body"] + socks["hand"]:
    pass

# ------------------------------------------------------------------------------------------------ 1-2 slaapkamer
KX = 300.0
K = V(KX, 0, 0)
room("Kamer5", K, 4.0, 3.6, 2.6, open_side="-y", wall=(250, 225, 170), floor=(200, 150, 100),
     window=("+y", -0.6, 1.5, 1.2, 1.0))
box("Bed5", (KX + 1.2, 0.7, 0.25), (1.0, 2.0, 0.5), mat("Deken5", (110, 170, 230), rough=0.8, sheen=0.6), bev=0.08)
box("Kussen5", (KX + 1.2, 1.45, 0.56), (0.7, 0.35, 0.14), mat("Kussen", (250, 250, 245), rough=0.8, sheen=0.5), bev=0.06)
box("Kast5", (KX - 1.5, 1.4, 0.9), (0.8, 0.6, 1.8), mat("Kast5", (240, 240, 235), rough=0.4, coat=0.3), bev=0.03)
box("Kleed5", (KX, -0.3, 0.005), (1.8, 1.3, 0.02), mat("Kleed5", (240, 120, 100), rough=0.9, sheen=0.6), bev=0.01)
P1 = V(KX + 0.1, -0.4, 0)
S.place(b, 0.0, P1, 15)
S.beat(b, 0.0, face="verbaasd", amt=0.8, head=dict(up=-12), arms="los")
S.beat(b, 0.6, face="geschrokken", arms="schrik", head=dict(up=-8), body=dict(lean=-4))
S.beat(b, e(1), face="geschrokken", amt=0.8, arms="schrik", head=dict(up=0))
S.beat(b, r2, face="verbaasd", arms="rust")
S.beat(b, r2 + 0.45, face="verbaasd", amt=0.8, arms="gezicht", head=dict(up=-6))
S.beat(b, Wd(2, 4), face="geschrokken", arms="gezicht", head=dict(up=-8))
S.beat(b, r3 - 0.05, face="geschrokken", arms="gezicht", head=dict(up=-8))
HEAD1 = P1 + V(0, 0, 1.47)
FR1 = V(math.sin(R(15)), -math.cos(R(15)), 0)
S.shot(0.0, ((P1.x + 0.7, P1.y - 2.6, 1.25), (P1.x, P1.y, 1.05), 28), ((P1.x + 0.6, P1.y - 2.3, 1.25), (P1.x, P1.y, 1.1), 30))
S.shot(r2, (tuple(HEAD1 + FR1 * 1.15 + V(0.3, 0, -0.1)), tuple(HEAD1 + FR1 * 0.35 + V(0, 0, -0.2)), 28),
       (tuple(HEAD1 + FR1 * 1.0 + V(0.25, 0, -0.1)), tuple(HEAD1 + FR1 * 0.38 + V(0, 0, -0.2)), 32))

# ------------------------------------------------------------------------------------------------ 3 zebrapad vol mensen
T_ = town(0, 0, half=60, seed=5)
tl_state(T_, 0.0, "groen")
A0, A1 = V(-6.0, -5.3, 0.15), V(5.5, -5.3, 0.15)
S.teleport(b, r3, A0, 90)
S.walk(b, r3 + 0.05, e(3) + 0.1, [A0, V(-3.6, -5.3, 0.0), V(3.6, -5.3, 0.0), A1])
S.face(b, r3 + 0.1, "blij", 0.7)
S.face(b, Wd(3, 6), "grijns")
S.head(b, Wd(3, 6), turn=-25)
S.head(b, e(3), turn=0)
rnd = random.Random(7)
for k, cn in enumerate(CROWD):
    ex = S.extra(cn)
    y = -6.5 + 0.55 * (k % 5) + (0.25 if k % 2 else 0)
    if abs(y + 5.3) < 0.35:
        y += 0.7
    east = k % 2 == 0
    x0, x1 = (-6.0, 6.0) if east else (6.0, -6.0)
    off = rnd.uniform(-2.5, 2.5)
    a, bb = V(x0 + off * 0.5 * (1 if east else -1), y, 0.0), V(x1, y, 0.0)
    S.place(ex, 0.0, a, 90 if east else -90)
    S.walk(ex, r3 - 0.3 - rnd.uniform(0, 0.6), e(3) + 1.0, [a, a.lerp(bb, 0.75)])
    S.face(ex, r3, "neutraal")
    S.head(ex, r3, turn=rnd.uniform(-10, 10))
    S.place(ex, r4, V(0, -300 - 3 * k, -50), 0)       # daarna uit beeld
S.shot(r3, ((5.0, -9.6, 1.3), (-1.0, -5.3, 1.0), 26), ((4.8, -9.3, 1.3), (1.0, -5.3, 1.0), 28))

# ------------------------------------------------------------------------------------------------ 4-7 kluis
VX = -300.0
steel = mat("Kluisstaal", (150, 160, 175), rough=0.3, coat=0.6)
wallm = mat("Kluismuur", (70, 80, 100), rough=0.6, coat=0.2)
gold = mat("Goud", (255, 190, 50), rough=0.2, coat=0.8)
room("Kluis", (VX, 0, 0), 6.0, 7.0, 3.0, open_side="-y", wall_m=wallm, floor_m=mat("Kluisvloer", (110, 115, 125), rough=0.4, coat=0.4))
for nm, x0, x1 in (("vl", -3.15, -0.9), ("vr", 0.9, 3.15)):
    box(f"Kluis_voor_{nm}", (VX + (x0 + x1) / 2, -3.6, 1.5), (x1 - x0, 0.3, 3.0), steel, bev=0.03)
box("Kluis_voor_boven", (VX, -3.6, 2.6), (1.8, 0.3, 0.8), steel, bev=0.03)
door = cyl("Kluisdeur", (0, 0, 0), 1.1, 0.4, steel, rot=(90, 0, 0), bev=0.03)
door.location = (VX - 1.95, -4.4, 1.15)
door.rotation_euler = (R(90), 0, R(-70))
wheel_m = mat("Kluiswiel", (220, 225, 235), rough=0.2, coat=0.8)
for k in range(4):
    sp = box(f"Kluiswiel_{k}", (0, 0, 0.42), (0.9, 0.06, 0.06), wheel_m, bev=0.02)
    sp.parent = door
    sp.rotation_euler = (0, 0, R(45 * k))
for side in (-1, 1):
    for lvl in range(3):
        box(f"Kluisrek_{side}_{lvl}", (VX + side * 2.5, 0.8, 0.45 + lvl * 0.7), (0.8, 4.0, 0.05), steel, bev=0.01)
        for j in range(10):
            for q in range(2):
                box(f"Goud_{side}_{lvl}_{j}_{q}", (VX + side * 2.5 + (q - 0.5) * 0.3, -0.9 + j * 0.38, 0.52 + lvl * 0.7),
                    (0.24, 0.12, 0.09), gold, bev=0.015)
for j in range(6):
    box(f"Goudstapel_{j}", (VX + 0.6 + (j % 3) * 0.28, 2.3, 0.045 + (j // 3) * 0.09), (0.24, 0.12, 0.09), gold, bev=0.015)
VLIGHTS = [area("Kluis_licht", (VX, 0.5, 2.9), (VX, 0.5, 0), 3.0, 260, (1.0, 0.86, 0.66)),
           point("Goudgloed_l", (VX - 2.0, 0.8, 1.2), 30, (1.0, 0.75, 0.3), 0.3),
           point("Goudgloed_r", (VX + 2.0, 0.8, 1.2), 30, (1.0, 0.75, 0.3), 0.3),
           # vullicht schuin van boven/opzij, niet achter de camera (anders gloeit het glazen hoofd wit)
           area("Kluis_vul", (VX + 2.7, 1.6, 2.7), (VX, 0.4, 1.2), 1.2, 90, (1.0, 0.92, 0.8)),
           area("Kluis_vul2", (VX - 1.0, -2.5, 2.2), (VX, 0.6, 1.2), 1.5, 90, (0.8, 0.88, 1.0))]
# regel 5-6: alles wordt zwart; alleen de lichtstralen; regel 7 schemer
for li in VLIGHTS:
    li.visible_transmission = False                 # geen witte lichtvlek door de glazen bol van je hoofd
    e0 = li.data.energy
    key_energy(li, [(0.0, e0), (r5 + 0.5, e0), (r5 + 0.6, e0 * 0.06), (r7 - 0.05, e0 * 0.06), (r7 + 0.25, e0 * 0.45)])

IN0, IN1 = V(VX - 0.2, -5.6, 0), V(VX + 0.1, 0.6, 0)
S.teleport(b, r4, IN0, 180)
S.walk(b, r4 + 0.05, e(4) - 0.2, [IN0, V(VX, -3.0, 0), IN1])
S.face(b, r4 + 0.1, "grijns")
S.head(b, r4 + 0.1, turn=0)
S.head(b, Wd(4, 7), turn=20, up=4)
S.face(b, Wd(4, 7), "heel_blij")
S.beat(b, e(4) - 0.15, face="heel_blij", arms="juichen", head=dict(up=8))
S.beat(b, r5 + 0.3, face="heel_blij", arms="omhoog", head=dict(up=8), body=dict(dz=0.03))
S.beat(b, r5 + 0.6, face="heel_blij", arms="juichen", head=dict(up=8))
S.beat(b, Wd(5, 1), face="verbaasd", arms="rust", head=dict(up=0))
S.shot(r4, ((VX + 1.3, 2.8, 1.35), (VX - 0.3, -3.6, 1.0), 24), ((VX + 1.1, 2.6, 1.3), (VX, -1.0, 1.0), 26))
S.shot(r5, ((VX + 0.9, 2.2, 1.3), (VX + 0.05, 0.6, 1.2), 28), ((VX + 0.8, 2.0, 1.3), (VX + 0.05, 0.6, 1.25), 32))

# regel 6: lichtstralen dwars door je hoofd (je kijkt naar +y)
HEAD = IN1 + V(0, 0, 1.47)
beam_m = glow("Lichtstraal", (255, 245, 200), 14.0)
beams = []
for k, dx in enumerate((-0.075, 0.075, 0.0)):
    bm = cyl(f"Lichtstraal_{k}", (0, 0, 0), 0.014 if k < 2 else 0.006, 3.4, beam_m, rot=(90, 0, 0))
    bm.location = HEAD + V(dx, 1.7, 0.035 if k < 2 else 0.1)
    key(bm, "scale", FR(0.0), Vector((1, 1, 0.001)))
    key(bm, "scale", FR(Wd(6, 1) - 0.02 + 0.06 * k), Vector((1, 1, 0.001)))
    key(bm, "scale", FR(Wd(6, 3) + 0.06 * k), Vector((1, 1, 1)))
    show(bm, r6 - 0.04, r7)
    beams.append(bm)
S.beat(b, r6 - 0.02, face="leeg", arms="rust", head=dict(up=0))
S.beat(b, r6 + 0.1, face="leeg", arms="rust", head=dict(up=0))
S.shot(r6, ((HEAD.x + 2.1, HEAD.y + 0.5, HEAD.z + 0.15), (HEAD.x, HEAD.y + 0.1, HEAD.z - 0.1), 40),
       ((HEAD.x + 1.9, HEAD.y + 0.45, HEAD.z + 0.12), (HEAD.x, HEAD.y + 0.1, HEAD.z - 0.08), 44), focus=HEAD)

# regel 7: tastend in de kluis
S.beat(b, r7, face="bang", arms="tasten", head=dict(turn=20))
S.beat(b, Wd(7, 2) + 0.2, face="bang", arms="tasten", r_arm=((-70, 26, -10), (-10, 0, 0)), head=dict(turn=-5), body=dict(lean=4))
S.beat(b, Wd(7, 3), face="bang", arms=((-82, 10, -4), (-16, 0, 0)), r_arm="tasten", head=dict(turn=-25), body=dict(lean=5))
S.beat(b, END, face="bang", arms="tasten", head=dict(turn=20), body=dict(lean=5))
S.blink(b, r7 + 0.4)
S.shot(r7, ((VX - 0.9, 2.5, 1.6), (VX + 0.1, 0.6, 1.2), 26), ((VX - 0.7, 2.2, 1.55), (VX + 0.1, 0.6, 1.25), 30))


def world():
    sky("dag")
    sun(4.2, d=(-0.6, -0.35, 0.72))
    three_point("Kamer", P1, 15, scale=0.9)
    three_point("Zebra", A0 + V(5, 0, 0), 0, scale=2.0)


S.world_fn = world
S.done()
