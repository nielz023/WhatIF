"""OR6 · What if you never needed sleep again? · nieuwe stijl: speelgoedslaapkamer 's nachts.

1  hook: jij, klaarwakker op je bed om 03:00; achter je in de hoek staat iets.
2  NIGHT 1: acht uur extra: je zit fris en vrolijk aan je bureau (lamp aan).
3  WEEK 1: vijftig boeken uit: de stapel naast je bureau groeit.
4  MONTH 1: drie nieuwe talen: briefjes op de muur (HOLA, BONJOUR, CIAO).
5  MONTH 6: donker; jij op je bed. In de hoek beweegt iets: een zwarte schaduw van jou, met witte ogen.
6  "Your brain needs dreams." Close: je wijd open ogen.
7  "And now... they come while you're awake." De schaduw staat vlak achter je.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or6")
b = S.bram
END = S.total
r, e, Wd = S.r, S.e, S.W
r2, r3, r4, r5, r6, r7 = (r(n) for n in (2, 3, 4, 5, 6, 7))

# ------------------------------------------------------------------------------------------------ schaduw (kopie, zwart)
sh = S.clone(b, "schaduw")
black = mat("Schaduw_zwart", (4, 4, 6), rough=0.9, coat=0)
eye_w = glow("Schaduw_ogen", (255, 255, 255), 6.0)
eye_objs = set()
for s in (-1, 1):
    eye_objs |= set(sh.eyes[s].children_recursive)
for o in sh.objs:
    if o.type != "MESH":
        continue
    o.visible_shadow = False
    for i in range(len(o.data.materials)):
        o.data.materials[i] = eye_w if o in eye_objs else black
    if o.name.startswith(("Bram_Mond", "Bram_Blos")) or any(o in sh.brows[s].children for s in (-1, 1)):
        o.hide_render = True
sh.breath = True
shadow_meshes = [o for o in sh.objs if o.type == "MESH" and not o.hide_render]
for o in shadow_meshes:
    for t, on in ((0.0, True), (e(1), False), (r5, True)):
        visible(o, t, on)

# ------------------------------------------------------------------------------------------------ kamer
room("Kamer6", (0, 0, 0), 4.4, 4.0, 2.6, open_side="-y", wall=(120, 150, 210), floor=(170, 120, 80),
     window=("-x", 0.4, 1.5, 1.1, 1.0))
box("Bed6", (-1.2, 0.6, 0.25), (1.1, 2.1, 0.5), mat("Deken6", (240, 150, 120), rough=0.8, sheen=0.6), bev=0.08)
box("Bedframe6", (-1.2, 1.7, 0.45), (1.2, 0.08, 0.9), mat("Bedhout", (180, 120, 70), rough=0.5, coat=0.3), bev=0.03)
box("Kussen6", (-1.2, 1.35, 0.57), (0.75, 0.35, 0.14), mat("Kussen", (250, 250, 245), rough=0.8, sheen=0.5), bev=0.06)
desk_m = mat("Bureau", (235, 225, 205), rough=0.4, coat=0.3)
DX, DY = 1.85, 0.2
box("Bureau6", (DX, DY, 0.74), (0.65, 1.4, 0.05), desk_m, bev=0.02)
for sx in (-1, 1):
    for sy in (-1, 1):
        box(f"Bureaupoot6_{sx}_{sy}", (DX + sx * 0.28, DY + sy * 0.65, 0.36), (0.05, 0.05, 0.72), desk_m, bev=0.01)
box("Laptop6", (DX - 0.05, DY - 0.1, 0.775), (0.3, 0.4, 0.02), mat("Laptop", (190, 195, 205), rough=0.3, coat=0.5), bev=0.01)
scr = box("Laptopscherm6", (DX + 0.1, DY - 0.1, 0.92), (0.02, 0.4, 0.27), glow("Laptopgloed", (150, 200, 255), 1.5), bev=0.005)
scr.rotation_euler = (0, R(-12), 0)
cyl("Lampvoet6", (DX + 0.1, DY + 0.5, 0.765), 0.08, 0.03, mat("Lamp6", (250, 200, 60), rough=0.3, coat=0.6))
cyl("Lamparm6", (DX + 0.1, DY + 0.5, 0.79), 0.015, 0.4, mat("Lamp6", (250, 200, 60), rough=0.3, coat=0.6))
lamp_m = glow("Lampkap6", (255, 220, 160), 0.0)
cyl("Lampkap6", (DX + 0.02, DY + 0.5, 1.12), 0.12, 0.14, lamp_m, r2=0.06)
CH = V(1.15, 0.2, 0)
chair_m = mat("Stoel", (90, 150, 220), rough=0.4, coat=0.4)
box("Stoelzitting6", CH + V(0, 0, 0.47), (0.48, 0.48, 0.06), chair_m, bev=0.02)
box("Stoelleuning6", CH + V(-0.25, 0, 0.8), (0.05, 0.46, 0.55), chair_m, bev=0.02)
cyl("Stoelpoot6", CH, 0.04, 0.45, mat("Paal", (60, 70, 80), rough=0.4, coat=0.3))
box("Kleed6", (0, -0.2, 0.005), (1.6, 1.2, 0.02), mat("Kleed6", (230, 200, 120), rough=0.9, sheen=0.6), bev=0.01)
box("Kast6", (0.3, 1.75, 0.9), (0.9, 0.45, 1.8), mat("Kast6", (240, 240, 235), rough=0.4, coat=0.3), bev=0.03)

desk_l = point("Bureaulamp6", (DX - 0.05, DY + 0.45, 1.05), 0, (1.0, 0.78, 0.5), 0.08)
key_energy(desk_l, [(0, 0), (r2 - 0.034, 0), (r2, 40), (r5 - 0.034, 40), (r5, 0)])
key_value(lamp_m.node_tree.nodes["Emission"].inputs["Strength"], [(0, 0.2), (r2 - 0.034, 0.2), (r2, 5.0), (r5 - 0.034, 5.0), (r5, 0.2)])
for idb in (desk_l.data, lamp_m.node_tree):
    for fc in fcurves(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
moon = area("Maanlicht6", (-3.2, 0.4, 1.9), (-0.5, 0.6, 0.8), 1.2, 130, (0.55, 0.65, 1.0))
fill = area("Vul6", (0.5, -3.0, 2.0), (0, 0.5, 1.0), 2.5, 25, (0.6, 0.7, 1.0))
warm = area("Warm6", (0.6, -1.2, 1.9), (CH.x, CH.y, 1.2), 1.2, 0, (1.0, 0.85, 0.65))
area("Gezicht6", (0.5, 0.1, 1.7), (-0.9, 0.55, 1.3), 0.6, 30, (0.7, 0.8, 1.0))
key_energy(warm, [(0, 0), (r2 - 0.034, 0), (r2, 70), (r5 - 0.034, 70), (r5, 0)])

# ------------------------------------------------------------------------------------------------ jij
BED = V(-0.9, 0.55, 0)
SITB = dict(dz=-0.18, lean=-2)
SITC = dict(dz=-0.19, lean=6)
S.place(b, 0.0, BED, 90)
S.beat(b, 0.0, face="bang", amt=0.6, body=SITB, legs=85, head=dict(up=0))
S.beat(b, e(1), face="bang", amt=0.7, body=SITB, legs=85, head=dict(turn=10))
S.teleport(b, r2, CH, 90)
S.beat(b, r2, face="blij", amt=0.8, body=SITC, legs=85)
S.beat(b, Wd(2, 3), face="heel_blij", arms="juichen", body=dict(dz=-0.19, lean=-2), legs=85, head=dict(up=8))
S.beat(b, Wd(2, 3) + 0.5, face="heel_blij", arms="omhoog", body=dict(dz=-0.19, lean=-2), legs=85, head=dict(up=8, tilt=6))
S.beat(b, e(2) - 0.3, face="blij", body=SITC, legs=85, head=dict(turn=-15))
# regel 3: boek in je handen, de stapel groeit
book = box("Leesboek6", (0, 0, 0), (0.22, 0.04, 0.16), mat("Boek6", (60, 120, 210), rough=0.5, coat=0.3), bev=0.008)
attach(book, b.el[1], hand_offset(b, 1) + V(-0.12, -0.04, 0.02), (0, 0, 0))
show(book, r3, r4)
READ = ((-45, 6, 26), (-80, 0, 0))
S.beat(b, r3, face="blij", amt=0.7, arms=READ, body=SITC, legs=85, head=dict(up=-14, turn=-6))
S.beat(b, e(3), face="trots", amt=0.8, arms=READ, body=SITC, legs=85, head=dict(up=-14, turn=-6))
rnd = random.Random(5)
STACK = V(0.85, -0.75, 0.0)
cols = [(220, 60, 50), (60, 130, 220), (250, 200, 60), (80, 180, 110), (160, 90, 200), (240, 240, 230)]
z = 0.0
for k in range(24):
    h = rnd.uniform(0.035, 0.06)
    for c in range(2):
        o = box(f"Stapelboek_{k}_{c}", (STACK.x + c * 0.32, STACK.y + rnd.uniform(-0.02, 0.02), z + h / 2), (0.2, 0.28, h),
                mat(f"Boekkaft_{(k + c) % 6}", cols[(k + c) % 6], rough=0.5, coat=0.3), bev=0.005, rot=(0, 0, rnd.uniform(-10, 10)))
        show(o, r3 + 0.1 + (Wd(3, 4) - r3) * (k * 2 + c) / 48)
    z += h
# regel 4: briefjes op de muur boven het bureau
WALLX = 2.19
note_m = mat("Briefje", (255, 230, 90), rough=0.7)
ink = mat("Inkt", (25, 25, 40), rough=0.6)
for k, (word, y, zz) in enumerate((("HOLA", -0.1, 1.55), ("BONJOUR", 0.35, 1.32), ("CIAO", 0.75, 1.6))):
    n = box(f"Briefje_{k}", (WALLX, y, zz), (0.01, 0.36, 0.24), note_m, bev=0, rot=(rnd.uniform(-6, 6), 0, 0))
    t_ = text3d(f"Briefje_tekst_{k}", word, (WALLX - 0.008, y, zz), 0.075 if len(word) < 6 else 0.055, ink, rot=(90, 0, -90), extrude=0.0)
    show(n, Wd(4, 2) + 0.25 * k)
    show(t_, Wd(4, 2) + 0.25 * k)
S.beat(b, r4, face="trots", arms="rust", r_arm=((-70, 30, 0), (-8, 0, 0)), body=SITC, legs=85, head=dict(up=6, turn=-10))
S.beat(b, e(4), face="trots", arms="rust", r_arm=((-75, 34, 0), (-8, 0, 0)), body=SITC, legs=85, head=dict(up=8, turn=-14))
# regel 5-7: weer op bed, in het donker
S.teleport(b, r5, BED, 90)
HUG = ((-38, 16, 30), (-100, 0, 0))
S.beat(b, r5, face="nerveus", amt=0.7, arms=HUG, body=SITB, legs=85)
S.beat(b, Wd(5, 3) + 0.2, face="bang", amt=0.9, arms=HUG, body=SITB, legs=85, head=dict(turn=30, up=2))
S.beat(b, r6, face="bang", arms=HUG, body=SITB, legs=85, head=dict(turn=8))
S.beat(b, r7 + 0.5, face="bang", arms=HUG, body=SITB, legs=85, head=dict(turn=0))
S.beat(b, END, face="geschrokken", arms=HUG, body=SITB, legs=85, head=dict(turn=0, up=2))
S.face(b, r6 + 0.3, "bang", eyes=1.32)
S.blink(b, r5 + 0.3)

CORNER = V(1.7, 1.45, 0)
S.place(sh, 0.0, CORNER, -70)
S.beat(sh, 0.0, face="leeg")
S.beat(sh, r5, face="leeg")
S.beat(sh, Wd(5, 3), face="leeg", head=dict(tilt=18))
S.beat(sh, Wd(5, 3) + 0.8, face="leeg", head=dict(tilt=22, turn=-10))
BEHIND = V(-1.55, 0.75, 0.5)
S.teleport(sh, r7, BEHIND, 90)
S.beat(sh, r7, face="leeg", head=dict(up=-12), body=dict(lean=10))
S.beat(sh, Wd(7, 4), face="leeg", r_arm=((-70, -10, 10), (-20, 0, 0)), head=dict(up=-14, tilt=10), body=dict(lean=16))
S.beat(sh, END, face="leeg", r_arm=((-72, -12, 12), (-22, 0, 0)), head=dict(up=-14, tilt=12), body=dict(lean=18))
sh.blink_at = [FR(r7 + 0.8)]

# ------------------------------------------------------------------------------------------------ camera's
HB = BED + V(0, 0, 1.47 - 0.18)
HC = CH + V(0, 0, 1.47 - 0.19)
WIDE = (((0.4, -2.4, 1.5), (0.2, 0.9, 1.0), 14), ((0.4, -2.25, 1.48), (0.2, 0.9, 1.0), 14.5))
S.shot(0.0, *WIDE, focus=HB)
S.shot(1.15, ((HB.x + 1.0, HB.y - 0.5, HB.z), tuple(HB + V(0, 0, -0.06)), 28),
       ((HB.x + 0.85, HB.y - 0.42, HB.z), tuple(HB + V(0, 0, -0.06)), 32))
S.shot(r2, ((CH.x + 0.85, CH.y - 1.05, 1.38), tuple(HC + V(0.1, 0, -0.25)), 24), ((CH.x + 0.8, CH.y - 0.95, 1.36), tuple(HC + V(0.1, 0, -0.22)), 26))
S.shot(r3, ((CH.x - 0.6, CH.y - 1.9, 1.15), (STACK.x + 0.2, -0.3, 0.75), 22), ((CH.x - 0.55, CH.y - 1.8, 1.2), (STACK.x + 0.2, -0.3, 0.85), 24))
S.shot(r4, ((CH.x + 0.1, CH.y - 1.5, 1.6), (1.85, 0.3, 1.4), 20), ((CH.x + 0.15, CH.y - 1.4, 1.6), (1.9, 0.3, 1.45), 22), focus=V(WALLX, 0.3, 1.4))
S.shot(r5, *WIDE, focus=HB)
S.shot(r6, ((HB.x + 0.9, HB.y - 0.25, HB.z), tuple(HB + V(0, 0, -0.04)), 30), ((HB.x + 0.62, HB.y - 0.18, HB.z), tuple(HB + V(0, 0, -0.04)), 34))
S.shot(r7, ((HB.x + 1.7, HB.y - 0.7, HB.z + 0.12), tuple(HB + V(-0.35, 0.12, 0.08)), 24),
       ((HB.x + 1.45, HB.y - 0.6, HB.z + 0.12), tuple(HB + V(-0.35, 0.12, 0.08)), 28))


def world():
    sky("nacht", strength=0.3)


S.world_fn = world
S.done()
