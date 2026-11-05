"""N03b · De laatste normale dag: het strand (script scène 3c-3d).
Opa leest de krant, oma smeert zonnebrand op zijn neus, de strandwacht fluit en wijst naar het bord
NO SWIMMING BEYOND THE FLAGS. Detail: opa klikt het vakje SAT van zijn pillendoosje open en pakt een pil.

    blender -b -P anim/v3/scenes/n03b_strand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n03b", "strand", "middag", exposure=0.2)
sh = S.cuts([3.0, 2.5])
END = sh[-1][1]
t_d = sh[1][0]

# strandtas met het pillendoosje tussen de twee stoelen, binnen opa's bereik (links van hem)
BAG = V(-4.06, -1.95, 0)
S.obj("Strandtas").location = BAG
S.obj("Pillendoosje_opa").location = BAG + V(0, 0.0, 0.355)
S.obj("Pillendoosje_opa").rotation_euler.z = math.radians(-20)
S.obj("Pillendoosje_opa").scale = (2.4, 2.4, 2.4)        # op maat van de grote stripfiguurhanden
bpy.context.view_layer.update()

# ---------------------------------------------------------------- opa en oma in hun strandstoelen
OPA_AT, OMA_AT = V(-4.6, -1.95, 0), V(-3.82, -2.02, 0)
_st = S.obj("Strandstoel_oma")
if _st is not None:
    _st.location.x, _st.location.y = -3.82, -2.07         # stoel schuift mee: oma zit dichter bij opa
opa = S.actor("opa", OPA_AT, -5, drop=("wandelstok",))        # stok laat hij bij het strand liggen
oma = S.actor("oma", OMA_AT, 5)
SEAT = {}
for ch, at, r in ((opa, OPA_AT, -5), (oma, OMA_AT, 5)):
    spec, z = sit(ch, seat_top=0.30, lean=-14)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0.04, z), r)

# krant in opa's handen (licht gebogen vel), hij slaat een bladzijde om
krant = T.box("Krant_opa", (0, 0, 0), (0.46, 0.012, 0.32), S.mat("krantenpapier", (0.93, 0.92, 0.86)), bevel=0.003, ol=0.002)
attach(krant, opa, "hand.R", (0.22, 0.05, 0.02), (90, 0, 0))
READ = arms(arm("L", (0.30, 0.75, -0.55), (-0.35, 0.85, 0.35)), arm("R", (0.30, 0.75, -0.55), (-0.35, 0.85, 0.35)))
S.beat(opa, 0.0, **SEAT[opa], arms=READ, face="neutraal", face_amt=0.5, at=krant.matrix_world.translation + V(0, -0.4, 0.1))
S.beat(opa, 0.7, **SEAT[opa], arms=READ, face="twijfel", face_amt=0.4, look=(0.0, -0.3), body={"head": (14, 0, 0)})
# oma smeert zonnebrand op zijn neus: hij trekt een gezicht en leunt weg
NOSE = S.headpos(opa, 0.9) + V(0.05, -0.32, -0.05)
S.beat(oma, 0.0, **SEAT[oma], face="blij", face_amt=0.6, at=S.head(opa))
# pols net naast de neus (vingers raken hem); oma leunt opzij naar opa, armen zijn kort
S.reach(oma, 0.6, "R", inf=0.0)
S.reach(oma, 0.9, "R", NOSE + V(0.2, -0.05, -0.03))
S.reach(oma, 1.3, "R", NOSE + V(0.12, 0, -0.02))
S.reach(oma, 1.6, "R", NOSE + V(0.12, 0, -0.05))
S.reach(oma, 1.9, "R", NOSE + V(0.12, 0, -0.02))
S.reach(oma, 2.05, "R", inf=0.0)
S.beat(oma, 1.0, **SEAT[oma], face="lach", face_amt=0.7, at=S.head(opa), body={"spine": (4, 0, 24)})
S.beat(oma, 1.9, **SEAT[oma], face="lach", face_amt=0.7, at=S.head(opa), body={"spine": (4, 0, 24)})
S.beat(oma, 2.4, **SEAT[oma], face="blij", face_amt=0.6, at=S.head(opa))
S.beat(opa, 1.25, **SEAT[opa], arms=READ, face="boos", face_amt=0.6, look=(0.6, 0.1), body={"head": (6, 0, 14)})
S.beat(opa, 2.1, **SEAT[opa], arms=READ, face="twijfel", face_amt=0.6, look=(0.0, -0.3), body={"head": (12, 0, 0)})
A.blink_at(opa, F(1.35), closed=5)
S.hold(oma, END)

# ---------------------------------------------------------------- 3d: het pillendoosje
box = S.obj("Pillendoosje_opa")
SAT = box.matrix_world.translation + Matrix.Rotation(math.radians(-20), 3, "Z") @ V((-0.081 + 5 * 0.027) * 2.4, 0, 0.07)
S.beat(opa, t_d, **SEAT[opa], arms=arm("R", (0.30, 0.75, -0.55), (-0.35, 0.85, 0.35)), face="neutraal", face_amt=0.5,
       at=SAT, body={"head": (18, 0, -10), "spine": (8, 0, -18)})             # leunt opzij naar de tas
S.reach(opa, 0.0, "L", inf=0.0)                                  # shot 1: linkerhand houdt de krant (FK)
S.reach(opa, t_d - 0.05, "L", inf=0.0)
S.reach(opa, t_d, "L", SAT + V(0.05, -0.25, 0.25))
S.reach(opa, t_d + 0.45, "L", SAT + V(0.0, -0.10, 0.14))        # duim op het klepje
S.reach(opa, t_d + 0.75, "L", SAT + V(0.0, -0.07, 0.11))        # klik
S.reach(opa, t_d + 1.25, "L", SAT + V(0.0, -0.02, 0.13))          # vingers in het vakje
S.reach(opa, t_d + 1.6, "L", SAT + V(0.0, -0.02, 0.12))
S.reach(opa, END, "L", SAT + V(0.04, -0.14, 0.24))               # pil omhoog
lid = S.obj("Pillendoosje_opa_deksel_SAT")
for t, a in ((t_d + 0.6, 0), (t_d + 0.75, -60), (t_d + 0.85, -120), (t_d + 0.95, -110)):
    lid.rotation_euler.x = math.radians(a)
    lid.keyframe_insert("rotation_euler", index=0, frame=F(t))
pil = S.obj("Pillendoosje_opa_pil_SAT1")
if pil is not None:
    grab(S, pil, opa, t_d + 1.55, bone="hand.L", loc=(0.0, 0.07, 0.02), mode="loc")
S.hold(opa, END)

# ---------------------------------------------------------------- strandwacht: fluit en wijst naar de vlaggen
wacht = S.actor("strandwacht", (6.0, -7.95, 0), 0)
spec, z = sit(wacht, seat_top=2.04, lean=-6, bent=True)
S.place(wacht, 0, V(6.0, -7.95, z), 0)
FLAG = V(-6.0, -19.5, 1.5)
S.beat(wacht, 0.0, **spec, face="neutraal", face_amt=0.5, at=V(2.0, -22.0, 0.5))
S.beat(wacht, 0.5, **spec, face="vastberaden", face_amt=0.6, at=V(1.0, -22.0, 0.5),
       arms=arm("R", (0.35, 0.55, 0.2), (-0.55, 0.45, 0.65)))                 # fluitje naar de mond
A.key_prop(wacht.rig, "mond_open", 0.0, F(0.5))
S.beat(wacht, 1.2, **spec, pose="wijzen", face="boos", face_amt=0.6, at=FLAG)
S.beat(wacht, 2.6, **spec, pose="wijzen", amount=0.8, face="vastberaden", face_amt=0.6, at=FLAG)
S.hold(wacht, END)

# zwemmers in de verte (voorbij de vlaggen)
for k, (x, y, r) in enumerate(((-2.0, -21.0, 160), (3.5, -22.0, 200), (8.0, -20.5, 180))):
    e = S.extra(k + 2, (x, y, 0), r)
    S.beat(e, 0.0, "staan", face="blij", face_amt=0.5)
    S.walk(e, 0.2, 2.8, [V(x, y, 0), V(x + 0.6, y + 1.6, 0)], stride=0.45)
    S.hold(e, END)

# ---------------------------------------------------------------- camera's
# 3c WIDE: opa en oma en profil, de strandwacht en het bord op de achtergrond, langzame drift
S.cam(0.0, ((-8.6, -5.9, 1.35), (-0.6, -3.6, 1.15), 24), ((-8.2, -6.0, 1.32), (-0.6, -3.8, 1.15), 25), handheld=0.06)
# 3d DETAIL push-in op het pillendoosje
S.cam(t_d, (SAT + V(-0.22, -1.05, 0.5), SAT + V(-0.03, 0, 0.08), 60), (SAT + V(-0.19, -0.9, 0.43), SAT + V(-0.03, 0, 0.08), 64),
      dof=0.6)

# ---------------------------------------------------------------- HUD en geluid
S.countdown(0, 0.3, END, jumps=[(0.0, 9 * 3600 + 12 * 60 + 44)])
S.ambience("sfx_strand_sfeer", 0.0, END, vol=0.25)
S.sfx("sfx_klok_tik", 0.0, 0.12, loop_to=END)
S.sfx("sfx_fluitje", 0.55, 0.35)
S.sfx("sfx_papier_vouwen", 0.7, 0.2)
S.sfx("sfx_pillendoosje", t_d + 0.7, 0.45)
S.finish(length=END, tail=0.0)
