"""D10a · De redder, 2066 (script scène 10a-10d). Straat bij nacht, brandende flat.
10a  WIDE handheld 3,3 s: de flat brandt, brandweerwagens, een moeder schreeuwt omhoog naar een raam.
     VO: "So you do the one thing only you can do."
10b  MEDIUM track 2,5 s: hij rent tussen de brandweermannen door het gebouw in.  BRANDWEERMAN: "Hey! Kid!"
10c  WIDE 3,4 s: rook, oranje gloed. Hij komt de deur uit met een klein meisje op zijn rug; zijn hoodie smeult.
     VO: "Being unkillable turns out to be very useful."
10c2 MEDIUM 3,9 s: het meisje rent naar haar moeder; de moeder kijkt over haar schouder naar hem.
     MOEDER: "How old are you?"  JONGEN: "It's complicated."
10d  CLOSE 2,5 s: de pestkop, nu agent van in de vijftig, kijkt toe en schudt langzaam zijn hoofd. Bijna een glimlach.

    python3 anim/v4/scenes/d10a_brand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d10a", "kleine_nd", "brand", exposure=0.25, night=True)
sh = S.cuts([3.3, 2.5, 3.4, 3.9, 2.5])
END = sh[-1][1]
t_b, t_c, t_c2, t_d = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

SW = 0.15                                                 # stoep (y 5..9)
# deuropening van de flat met oranje gloed erachter
T.box("Flat_deuropening", (0.5, 9.46, 0.0), (1.3, 0.08, 2.3), S.mat("deur_gat_donker", (0.05, 0.03, 0.02)), bevel=0, ol=0)
T.box("Flat_deur_gloed", (0.5, 9.42, 0.15), (1.1, 0.02, 1.9), ND.pbr("deur_gloed", (1.0, 0.45, 0.1), emit=(1.0, 0.45, 0.1), strength=4.0),
      bevel=0, ol=0)
T.point_light("Deur_vuurlicht", (0.5, 8.6, 1.6), color=(1.0, 0.45, 0.12), energy=500, radius=0.5)
DOOR = V(0.5, 9.0, SW)

# ---------------------------------------------------------------- de moeder (en later het meisje)
MOM = V(3.0, 6.2, SW)
moeder = S.actor("moeder_meisje", MOM, 160)
WIN = V(-2.5, 9.5, 10.0)
for k, t in enumerate(frange(0.0, t_c2, 0.5)):
    S.beat(moeder, t, "staan", arms=arms(arm("R", (0.35, 0.45, -0.20), (0.15, 0.35, 0.93))) if k % 2 == 0 else None,
           face="schreeuw", face_amt=1.0, at=WIN)
S.beat(moeder, t_c2 + 0.5, "staan", face="geschrokken", face_amt=0.8, at=V(2.2, 6.0, 1.0))
S.hold(moeder, END)

# ---------------------------------------------------------------- brandweermannen
bw1 = S.actor("brandweerman", (-2.4, 6.3, SW), 160)
bw2 = S.actor("brandweerman", (-1.9, 4.5, SW), 200, label="brandweerman_2")
S.beat(bw1, 0.0, "staan", face="nerveus", face_amt=0.7, at=WIN)
S.beat(bw2, 0.0, "staan", face="nerveus", face_amt=0.7, at=WIN)

# ---------------------------------------------------------------- hij rent naar binnen
held = S.actor("hoofdpersonage_kind", (-3.2, 1.2, 0), 160)
show(held.rig, t_b - 0.05)
S.run(held, t_b, t_b + 2.2, [(-3.2, 1.2, 0), (-0.6, 4.2, SW), (0.2, 7.0, SW), DOOR + V(0, 0.55, 0)], stride=0.75)
S.beat(held, t_b, "staan", face="inspanning", face_amt=0.9, at=DOOR + V(0, 0, 1.2))
S.beat(bw1, t_b + 0.7, "staan", arms=arms(arm("R", (0.80, 0.25, -0.20), (0.85, 0.20, 0.10))), face="geschrokken", face_amt=1.0,
       at=DOOR + V(0, -1.0, 1.0))                                                  # "Hey! Kid!"
S.beat(bw1, t_b + 1.8, "staan", arms=arms(arm("R", (0.80, 0.25, -0.20), (0.85, 0.20, 0.10))), face="schreeuw", face_amt=1.0,
       at=DOOR + V(0, 0.5, 1.0))
S.hold(bw1, t_c)
S.beat(bw2, t_b + 1.2, "schrik", face="geschrokken", face_amt=0.8, at=DOOR + V(0, 0, 1.0))
S.hold(bw2, END)

# 10c: komt naar buiten met het meisje op zijn rug (zelfde snede: staat in de deur)
S.teleport(held, t_c, DOOR + V(0, 0.3, 0), 0)
OUT_AT = V(1.4, 6.6, SW)
S.walk(held, t_c + 0.3, t_c + 2.6, [DOOR + V(0, 0.3, 0), V(0.9, 7.6, SW), OUT_AT], stride=0.38, end_rot=-20)
CARRY = arms(arm("L", (0.35, -0.40, -0.85), (0.30, -0.60, -0.75)), arm("R", (0.35, -0.40, -0.85), (0.30, -0.60, -0.75)))
for t in (t_c, t_c + 1.0, t_c + 2.0):
    S.beat(held, t, "staan", arms=CARRY, face="inspanning", face_amt=0.7, crouch=(0.06, 18), at=OUT_AT + V(1.5, -4.0, 1.0))
S.beat(held, t_c2, "staan", face="neutraal", face_amt=0.5, at=MOM + V(0, 0, 1.2))
S.beat(held, t_c2 + 1.7, "staan", face="twijfel", face_amt=0.7, at=MOM + V(0, 0, 1.6), body={"head": (0, 0, 8)})
S.beat(held, t_c2 + 2.4, "schouders_op", amount=0.8, face="grijns", face_amt=0.6, at=MOM + V(0, 0, 1.6))   # "It's complicated"
S.hold(held, END)
for t in frange(t_c + 0.2, END, 0.45):                   # de hoodie smeult
    for sx in (-1, 1):
        S.puff(S.head(held, t) + V(sx * 0.18, 0.05, -0.38), t, n=2, r=(0.03, 0.06), grow=1.8, dur=0.8,
               color=(0.35, 0.33, 0.32), rise=0.5, spread=0.08)

# het meisje: op zijn rug (gekeyd achter zijn borst), daarna rent ze naar haar moeder
meisje = S.actor("meisje_brand", DOOR + V(0, 0.6, 0.6), 0)
show(meisje.rig, t_c)
S.qc_skip.add(meisje.name)
S.qc_skip.add(bw2.name)
PIGGY = arms(arm("L", (0.40, 0.70, -0.30), (-0.45, 0.85, -0.10)), arm("R", (0.40, 0.70, -0.30), (-0.45, 0.85, -0.10)))
for t in frange(t_c, t_c2 - 0.04, 0.1):
    M = S._root_matrix(held, t)
    p = M.translation + M.to_3x3() @ V(0.0, 0.26, 0.52)
    A.place(meisje, F(t), tuple(p), math.degrees(S._rot_now(held, t)))
S.beat(meisje, t_c, "staan", arms=PIGGY, face="nerveus", face_amt=0.8, look=(0.0, -0.2),
       feet=((0.16, 0.30, 0.20), (-0.16, 0.30, 0.20)))
S.hold(meisje, t_c2 - 0.04)
GIRL0 = OUT_AT + V(0.35, 0.1, 0)
S.teleport(meisje, t_c2, GIRL0, 100)
S.run(meisje, t_c2 + 0.1, t_c2 + 1.0, [GIRL0, MOM + V(-0.45, 0.05, 0)], stride=0.45)
S.beat(meisje, t_c2 + 1.0, "staan", arms=arms(arm("L", (0.6, 0.6, 0.2), (-0.2, 0.9, 0.2)), arm("R", (0.6, 0.6, 0.2), (-0.2, 0.9, 0.2))),
       face="verdrietig", face_amt=0.6, at=S.head(moeder))
S.hold(meisje, END)
S.place(moeder, t_c2 + 0.6, MOM, 160)
S.place(moeder, t_c2 + 1.0, MOM, 100)                     # draait naar het meisje
S.beat(moeder, t_c2 + 1.1, "staan", arms=arms(arm("L", (0.5, 0.6, -0.3), (-0.3, 0.9, -0.2)), arm("R", (0.5, 0.6, -0.3), (-0.3, 0.9, -0.2))),
       face="verdrietig", face_amt=0.6, at=S.head(meisje, t_c2 + 1.1))
S.beat(moeder, t_c2 + 1.6, "staan", arms=arms(arm("L", (0.5, 0.6, -0.3), (-0.3, 0.9, -0.2)), arm("R", (0.5, 0.6, -0.3), (-0.3, 0.9, -0.2))),
       face="verbaasd", face_amt=1.0, at=S.head(held, t_c2 + 1.6))           # kijkt over haar schouder naar hem

# ---------------------------------------------------------------- 10d: de pestkop als agent
pk = S.actor("pestkop_agent", (-4.2, 4.6, SW), 150)
S.beat(pk, 0.0, "armen_over", face="neutraal", face_amt=0.6, at=WIN)
S.beat(pk, t_d, "armen_over", face="neutraal", face_amt=0.6, at=S.head(held, t_d))
for k, t in enumerate(frange(t_d + 0.3, t_d + 1.7, 0.45)):
    S.beat(pk, t, "armen_over", face="neutraal", face_amt=0.5, at=S.head(held, t_d), body={"head": (4, 14 if k % 2 else -14, 0)})
S.beat(pk, t_d + 1.95, "armen_over", face="grijns", face_amt=0.35, at=S.head(held, t_d))      # bijna een glimlach
S.hold(pk, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-4.0, -12.0, 2.2), V(0.0, 9.0, 8.0), 22), (V(-3.6, -10.8, 2.15), V(0.0, 9.0, 7.6), 22), handheld=0.18)
S.cam(t_b, None, fn=lambda t: (S._root_matrix(held, t).translation + V(2.3, -1.5, 1.3),
                               S._root_matrix(held, t).translation + V(0, 0.8, 0.9), 30), handheld=0.15)
S.cam(t_c, (V(1.2, 2.2, 1.6), V(0.6, 8.6, 1.3), 28), (V(1.15, 2.6, 1.55), V(0.7, 8.0, 1.2), 28))
S.cam(t_c2, (V(2.0, 2.6, 1.45), V(2.1, 6.5, 1.15), 28), (V(2.05, 2.8, 1.44), V(2.1, 6.5, 1.15), 28))
S.cam(t_d, S.shot(pk, t_d + 1.0, size="mcu", az=-15, lens=35), S.shot(pk, t_d + 1.0, size=0.85, az=-13, lens=35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2066, t0=0.0, big=True)
S.jump(0.0)
S.say("D10-01", at=0.2)
S.say("D10-02", who=bw1, at=t_b + 0.7)
S.say("D10-03", at=t_c + 0.15)
S.say("D10-04", who=moeder, at=t_c2 + 1.5)
S.say("D10-05", who=held, at=t_c2 + 2.05)
S.ambience("sfx_brand", 0.0, END, vol=0.16)
S.ambience("sfx_rook_sirenes", 0.0, t_c, vol=0.06)
S.music("drums_build", 0.0, END, vol=0.16, fade_in=0.2, fade_out=0.4)
S.finish(length=END, tail=0.0)
