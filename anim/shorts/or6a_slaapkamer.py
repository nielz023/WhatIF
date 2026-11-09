"""OR6a · What if you never needed sleep again? · slaapkamer 's nachts, één deel.

1  hook: jij, klaarwakker op je bed om 03:00; achter je in de hoek staat iets.
2  NIGHT 1: acht uur extra: je zit fris en vrolijk aan je bureau (laptop, lamp).
3  WEEK 1: vijftig boeken uit: de stapel naast je bureau groeit.
4  MONTH 1: drie nieuwe talen: briefjes op de muur (HOLA, BONJOUR, CIAO).
5  MONTH 6: het is donker; jij op je bed. In de hoek beweegt iets: een zwarte schaduw van jou, met witte ogen.
6  "Your brain needs dreams." Close: je wijd open ogen.
7  "And now... they come while you're awake." De schaduw staat vlak achter je.

    python3 anim/shorts/or6a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or6", "a", "slaapkamer", "nacht", lines=(1, 2, 3, 4, 5, 6, 7))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR6-{n:02d}"][i]["s"]
r2, r3, r4, r5, r6, r7 = (L[n][0] for n in (2, 3, 4, 5, 6, 7))

# -- licht: bureaulamp aan tijdens regel 2-4 -----------------------------------------------------------
desk_l = T.point_light("Bureau_licht_or6", (1.6, -0.1, 1.35), color=(1.0, 0.78, 0.5), energy=0, radius=0.08)
for t, e in ((0, 0), (r2 - 0.02, 0), (r2, 45), (r5 - 0.02, 45), (r5, 0)):
    desk_l.data.energy = e
    desk_l.data.keyframe_insert("energy", frame=F(t))
for fc in A._fcurves(desk_l.data):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
moon = S.obj("Maanlicht_raam")

# -- jij ---------------------------------------------------------------------------------------------
BED = V(-0.92, 0.55, 0)
CHAIR = S.obj("Bureaustoel")
SEAT = V(CHAIR.location.x, CHAIR.location.y, 0) if CHAIR else V(1.14, 0.2, 0)
held = S.actor("hoofdpersonage", BED, 90)
spec_bed, rz_bed = sit(held, seat_top=0.52, lean=-2)
spec_ch, rz_ch = sit(held, seat_top=0.5, lean=6)


def on_bed(t):
    S.place(held, t, BED + V(0, 0, rz_bed), 90)


def on_chair(t):
    S.place(held, t, SEAT + V(0, 0, rz_ch), 90)


on_bed(0.0)
S.beat(held, 0.0, "staan", face="bang", face_amt=0.6, look=(0, 0.1), mouth=0.0, **spec_bed)
S.beat(held, L[1][1], "staan", face="bang", face_amt=0.7, look=(-0.3, 0.1), mouth=0.0, **spec_bed)
# regel 2-4 aan het bureau
S.teleport(held, r2, SEAT + V(0, 0, rz_ch), 90)
S.beat(held, r2, "staan", face="lach", face_amt=0.8, look=(0, -0.2), **spec_ch)
S.beat(held, W(2, 3), "juichen", amount=0.5, face="lach", face_amt=1.0, look=(-0.3, 0.1), **spec_ch)
S.beat(held, L[2][1] - 0.3, "staan", face="blij", face_amt=0.9, look=(0, -0.2), **spec_ch)
# boek in je handen (regel 3)
book_m = S.mat("boek_or6", (0.2, 0.45, 0.8))
HEADc = S.head(held, r3)
BOOK = HEADc + V(0.42, 0.0, -0.32)
book = T.box("Leesboek", tuple(BOOK), (0.04, 0.22, 0.16), book_m, base=False, bevel=0.006, ol=0.003)
book.rotation_euler = (0, math.radians(-30), 0)
show(book, r3, r4)
S.reach(held, r3, "L", BOOK + V(0, 0.12, -0.04))
S.reach(held, r3, "R", BOOK + V(0, -0.12, -0.04))
S.reach(held, r4, "L", None, 0.0)
S.reach(held, r4, "R", None, 0.0)
S.beat(held, r3, "staan", face="blij", face_amt=0.7, look=(0, -0.5), body={"head": (14, 0, 0)}, **spec_ch)
S.beat(held, L[3][1], "staan", face="zelfverzekerd", face_amt=0.8, look=(0, -0.5), body={"head": (14, 0, 0)}, **spec_ch)
# de stapel boeken
rnd = random.Random(5)
STACK = V(1.0, -0.85, 0.0)
cols = [(0.8, 0.2, 0.15), (0.2, 0.5, 0.8), (0.95, 0.75, 0.2), (0.25, 0.6, 0.35), (0.6, 0.3, 0.7), (0.9, 0.9, 0.85)]
z = 0.0
for k in range(24):
    h = rnd.uniform(0.035, 0.06)
    for col in range(2):
        o = T.box(f"Stapelboek_{k}_{col}", (STACK.x + col * 0.3, STACK.y + rnd.uniform(-0.02, 0.02), z), (0.2, 0.28, h),
                  S.mat(f"boekkaft_{(k + col) % 6}", cols[(k + col) % 6]), rot=(0, 0, rnd.uniform(-10, 10)), bevel=0.004, ol=0.003)
        show(o, r3 + 0.1 + (W(3, 4) - r3) * (k * 2 + col) / 48)
    z += h
S.sfx("sfx_papier_vouwen", r3 + 0.2, 0.25)
# regel 4: briefjes op de muur
WALLX = 2.08
note_m = S.mat("briefje_geel", (1.0, 0.9, 0.35))
ink = S.mat("briefje_inkt", (0.1, 0.1, 0.15))
for k, (word, y, zz) in enumerate((("HOLA", -0.1, 1.55), ("BONJOUR", 0.35, 1.35), ("CIAO", 0.75, 1.6))):
    n = T.box(f"Briefje_{k}", (WALLX, y, zz), (0.01, 0.34, 0.22), note_m, base=False, bevel=0, ol=0.002)
    n.rotation_euler = (math.radians(rnd.uniform(-6, 6)), 0, 0)
    t_ = T.text(f"Briefje_tekst_{k}", word, (WALLX - 0.007, y, zz - 0.025), 0.06 if len(word) < 6 else 0.05, ink, rot=(90, 0, -90), extrude=0.0)
    t_.rotation_euler = (math.radians(90), 0, math.radians(-90))
    show(n, W(4, 2) + 0.25 * k)
    show(t_, W(4, 2) + 0.25 * k)
    S.sfx("sfx_stift", W(4, 2) + 0.25 * k, 0.2)
S.beat(held, r4, "wijzen", face="zelfverzekerd", face_amt=0.9, look=(0.3, 0.3), body={"head": (-6, 0, 0)}, **spec_ch)
S.beat(held, L[4][1], "wijzen", face="zelfverzekerd", face_amt=0.9, look=(0.3, 0.3), body={"head": (-6, 0, 0)}, **spec_ch)
# regel 5-7: weer op je bed, het is donker
S.teleport(held, r5, BED + V(0, 0, rz_bed), 90)
S.beat(held, r5, "armen_over", face="nerveus", face_amt=0.7, look=(0, 0.0), **spec_bed)
S.beat(held, W(5, 3) + 0.2, "armen_over", face="bang", face_amt=0.9, look=(0.9, 0.2), body={"head": (0, 0, -30), "neck": (0, 0, -15)}, **spec_bed)
S.beat(held, r6, "armen_over", face="bang", face_amt=1.0, look=(0.2, 0.0), body={"head": (0, 0, -8)}, **spec_bed)
S.beat(held, r7 + 0.5, "armen_over", face="bang", face_amt=1.0, look=(0.0, 0.0), body={"head": (0, 0, 0)}, **spec_bed)
S.beat(held, END, "armen_over", face="bang", face_amt=1.0, look=(0.0, 0.0), body={"head": (0, 0, 0)}, **spec_bed)
held.frozen = r7 + 0.6

# -- de schaduw: een zwarte kopie van jou met witte ogen ----------------------------------------------
CORNER = V(1.72, 1.5, 0)
shadow = S.actor("hoofdpersonage", CORNER, -125, label="Schaduw")
black = S.mat("schaduw_zwart", (0.004, 0.004, 0.006))
white = S.mat("schaduw_ogen", (1.0, 1.0, 1.0), 6.0)
for o in shadow.rig.children_recursive:
    if o.type != "MESH":
        continue
    for slot in o.material_slots:
        nm = slot.material.name if slot.material else ""
        m_ = re.search(r"Material_(\d+)\.", nm)
        eye = "_vlak" in nm and m_ is not None and 8 <= int(m_.group(1)) <= 21
        slot.link = "OBJECT"
        slot.material = white if eye else black
    o.visible_shadow = False
visible(shadow.rig, 0.0, True)
visible(shadow.rig, L[1][1], False)
visible(shadow.rig, r5, True)
shadow.frozen = 0.0
S.beat(shadow, 0.0, "staan", face="neutraal", look=(0, 0), mouth=0.0)
S.beat(shadow, r5, "staan", face="neutraal", look=(0, 0), mouth=0.0)
S.beat(shadow, W(5, 3), "staan", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (0, 18, 0)})
S.beat(shadow, W(5, 3) + 0.8, "staan", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (0, 22, -10)})
BEHIND = BED + V(-0.75, 0.35, 0.52)
S.teleport(shadow, r7, BEHIND, 90)
S.beat(shadow, r7, "staan", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (10, 0, 0)})
S.beat(shadow, END, "staan", face="neutraal", look=(0, 0), mouth=0.0, body={"head": (14, 10, 0)})
S.reach(shadow, r7, "R", None, 0.0)
S.reach(shadow, W(7, 4), "R", S.head(held, r7) + V(-0.25, -0.12, -0.22))
S.reach(shadow, END, "R", S.head(held, r7) + V(-0.2, -0.12, -0.25))

# -- tellers, geluid -----------------------------------------------------------------------------------
S.counter("NIGHT 1", r2, L[2][1])
S.counter("WEEK 1", r3, L[3][1])
S.counter("MONTH 1", r4, L[4][1])
S.counter("MONTH 6", r5, L[5][1], color=RED)
S.text("03:00", 0.2, L[1][1], loc=(0.5, 0.79), size=150, color=(1.0, 0.3, 0.2, 1), anchor=("CENTER", "CENTER"), pop=True)
S.texts[-1]["box"] = True
S.music_all("m_nacht_angst", vol=0.24)
S.ambience("sfx_krekels_nacht", 0.0, END, vol=0.05)
S.sfx("sfx_klok_tik", 0.0, 0.2, cut=L[1][1])
S.sfx("sfx_vloer_kraak", W(5, 3), 0.45)
S.sfx("sfx_hartslag", r6, 0.3, cut=END)
S.sfx("sfx_brass_hit", r7 + 0.5, 0.35)

# -- camera's ------------------------------------------------------------------------------------------
HB = S.head(held, 0.0)
# hook: dichtbij je gezicht, de schaduw achter in de hoek (onscherp)
S.cam(0.0, ((HB.x - 0.55, HB.y - 0.6, HB.z + 0.15), (CORNER.x, CORNER.y, 1.2), 24),
      ((HB.x - 0.45, HB.y - 0.55, HB.z + 0.12), (CORNER.x, CORNER.y, 1.25), 28))
S.cam(1.15, ((HB.x + 1.0, HB.y - 0.55, HB.z), tuple(HB + V(0, 0.05, -0.05)), 28),
      ((HB.x + 0.85, HB.y - 0.45, HB.z), tuple(HB + V(0, 0.05, -0.05)), 30))
HC = S.head(held, r2)
S.cam(r2, ((SEAT.x + 0.55, SEAT.y - 1.25, 1.35), (SEAT.x + 0.4, SEAT.y, 0.95), 22), ((SEAT.x + 0.5, SEAT.y - 1.15, 1.3), (SEAT.x + 0.4, SEAT.y, 0.95), 24))
S.cam(r3, ((SEAT.x - 0.1, SEAT.y - 1.55, 1.1), (STACK.x + 0.2, -0.3, 0.7), 20), ((SEAT.x - 0.05, SEAT.y - 1.45, 1.15), (STACK.x + 0.2, -0.3, 0.8), 22))
S.cam(r4, ((SEAT.x - 0.4, SEAT.y - 0.9, 1.45), (WALLX, 0.3, 1.4), 20), ((SEAT.x - 0.3, SEAT.y - 0.85, 1.45), (WALLX, 0.3, 1.45), 22))
S.cam(r5, ((0.45, -1.7, 1.25), (0.35, 0.95, 0.95), 16), ((0.4, -1.6, 1.25), (0.4, 1.0, 1.0), 17))
HD = S.head(held, r6)
S.cam(r6, ((HD.x + 0.9, HD.y - 0.25, HD.z), tuple(HD + V(0, 0, -0.04)), 30), ((HD.x + 0.6, HD.y - 0.18, HD.z), tuple(HD + V(0, 0, -0.04)), 34))
S.cam(r7, ((HD.x + 1.6, HD.y - 0.6, HD.z + 0.1), tuple(HD + V(-0.35, 0.15, 0.05)), 24),
      ((HD.x + 1.35, HD.y - 0.5, HD.z + 0.1), tuple(HD + V(-0.35, 0.15, 0.05)), 28))
S.done()
