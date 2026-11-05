"""N19d · Jaar 5: het strand is weer vol (script scène 19d-19f). Spiegelt scène 3c, maar trager.
19d  WIDE push-in: het strand vol, de strandwacht op zijn stoel blaast op zijn fluitje (zelfde beweging als scène 3) en
     wijst naar de vlaggen. Het bord NO SWIMMING BEYOND THE FLAGS staat er weer (handgeschilderd).
19e  MEDIUM: opa en oma op dezelfde strandstoelen. Oma smeert zonnebrand op opa's neus, opa trekt hetzelfde gezicht.
     VO N19-03 begint.
19f  CLOSE: de tiener-jongen naast hen kijkt naar het bord. Daarna over zijn schouder naar het bord. VO N19-04.

    blender -b -P anim/v3/scenes/n19d_strand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n19d", "strand", "jaar5", exposure=0.3)
sh = S.cuts([4.0, 3.6, 3.6, 3.8])
END = sh[-1][1]
t_e, t_f, t_f2 = [s[0] for s in sh[1:]]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

SIGN = V(1.0, -14.5, 1.65)

# ---------------------------------------------------------------- opa en oma in hun strandstoelen (zoals scène 3c)
OPA_AT, OMA_AT = V(-4.6, -1.95, 0), V(-3.86, -2.02, 0)
_st = S.obj("Strandstoel_oma")
if _st is not None:
    _st.location.x, _st.location.y = -3.86, -2.07         # stoel schuift mee: oma zit dicht tegen opa aan (korte armen)
opa = S.actor("opa", OPA_AT, -5, drop=("wandelstok",))        # stok laat hij bij het strand liggen
oma = S.actor("oma", OMA_AT, 5)
SEAT = {}
for ch, at, r in ((opa, OPA_AT, -5), (oma, OMA_AT, 5)):
    spec, z = sit(ch, seat_top=0.30, lean=-14)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0.04, z), r)
krant = T.box("Krant_opa", (0, 0, 0), (0.46, 0.012, 0.32), S.mat("krantenpapier", (0.93, 0.92, 0.86)), bevel=0.003, ol=0.002)
attach(krant, opa, "hand.R", (0.22, 0.05, 0.02), (90, 0, 0))
READ = arms(arm("L", (0.30, 0.75, -0.55), (-0.35, 0.85, 0.35)), arm("R", (0.30, 0.75, -0.55), (-0.35, 0.85, 0.35)))
S.beat(opa, 0.0, **SEAT[opa], arms=READ, face="neutraal", face_amt=0.5, at=krant.matrix_world.translation + V(0, -0.4, 0.1))
# opa buigt een beetje naar oma toe, zodat ze bij zijn neus kan
S.beat(opa, t_e + 0.3, **SEAT[opa], arms=READ, face="twijfel", face_amt=0.4, look=(0.0, -0.3), body={"head": (14, 0, 0), "spine": (0, 0, -12)})
NOSE = S.headpos(opa, t_e + 0.6) + V(0.05, -0.32, -0.05)
S.beat(oma, 0.0, **SEAT[oma], face="blij", face_amt=0.6, at=S.head(opa))
k = 1.4                                                  # trager dan in scène 3
S.reach(oma, 0.0, "R", inf=0.0)
S.reach(oma, t_e + 0.2 + 0.2 * k, "R", inf=0.0)
S.reach(oma, t_e + 0.2 + 0.4 * k, "R", NOSE + V(0.15, -0.05, 0))
S.reach(oma, t_e + 0.2 + 0.8 * k, "R", NOSE + V(0.08, 0, 0.02))
S.reach(oma, t_e + 0.2 + 1.1 * k, "R", NOSE + V(0.08, 0, -0.02))
S.reach(oma, t_e + 0.2 + 1.4 * k, "R", NOSE + V(0.08, 0, 0.02))
S.reach(oma, t_e + 0.2 + 1.5 * k, "R", NOSE + V(0.12, -0.04, 0.0))
S.reach(oma, t_e + 0.2 + 1.62 * k, "R", inf=0.0)
S.beat(oma, t_e + 0.2 + 0.3 * k, **SEAT[oma], face="lach", face_amt=0.7, at=S.head(opa), body={"spine": (6, 0, -28)})
S.beat(oma, t_e + 0.2 + 1.9 * k, **SEAT[oma], face="blij", face_amt=0.6, at=S.head(opa))
S.beat(opa, t_e + 0.2 + 0.75 * k, **SEAT[opa], arms=READ, face="boos", face_amt=0.6, look=(0.6, 0.1), body={"head": (6, 0, 14), "spine": (0, 0, -12)})
S.beat(opa, t_e + 0.2 + 1.6 * k, **SEAT[opa], arms=READ, face="twijfel", face_amt=0.6, look=(0.0, -0.3), body={"head": (12, 0, 0), "spine": (0, 0, -12)})
A.blink_at(opa, F(t_e + 0.2 + 0.85 * k), closed=5)
# en dan lacht hij toch even (anders dan in scène 3)
S.beat(opa, t_f, **SEAT[opa], arms=READ, face="blij", face_amt=0.6, at=S.head(oma))
S.hold(opa, END)
S.hold(oma, END)

# ---------------------------------------------------------------- de strandwacht: fluit en wijst (zoals scène 3c)
wacht = S.actor("strandwacht", (6.0, -7.95, 0), 0)
spec, z = sit(wacht, seat_top=2.04, lean=-6, bent=True)
S.place(wacht, 0, V(6.0, -7.95, z), 0)
FLAG = V(-6.0, -19.5, 1.5)
S.beat(wacht, 0.0, **spec, face="neutraal", face_amt=0.5, at=V(2.0, -22.0, 0.5))
S.beat(wacht, 0.7, **spec, face="vastberaden", face_amt=0.6, at=V(1.0, -22.0, 0.5),
       arms=arm("R", (0.35, 0.55, 0.2), (-0.55, 0.45, 0.65)))
S.beat(wacht, 1.9, **spec, pose="wijzen", face="boos", face_amt=0.6, at=FLAG)
S.beat(wacht, 3.4, **spec, pose="wijzen", amount=0.8, face="vastberaden", face_amt=0.6, at=FLAG)
S.beat(wacht, t_e + 0.5, **spec, face="blij", face_amt=0.5, at=V(2.0, -22.0, 0.5))
S.hold(wacht, END)

# ---------------------------------------------------------------- zwemmers en strandgasten
for kx, (x, y, r) in enumerate(((-2.0, -21.0, 160), (3.5, -22.0, 200), (8.0, -20.5, 180), (-7.5, -9.5, 30), (9.5, -4.0, -40))):
    e = S.extra(kx + 2, (x, y, 0), r)
    S.beat(e, 0.0, "staan", face="blij", face_amt=0.5)
    if kx < 3:
        S.walk(e, 0.4, 3.8, [V(x, y, 0), V(x + 0.6, y + 1.6, 0)], stride=0.45)
    S.hold(e, END)

# ---------------------------------------------------------------- de tiener-jongen naast hen, kijkt naar het bord
TP = V(-1.7, -2.4, 0)
d = SIGN - TP
held = S.actor("hoofdpersonage_tiener", TP, math.degrees(math.atan2(d.x, -d.y)))
S.beat(held, 0.0, "staan", face="blij", face_amt=0.4, at=S.head(oma))
S.beat(held, t_f - 0.4, "staan", face="neutraal", face_amt=0.5, at=SIGN)
S.beat(held, t_f + 1.6, "staan", face="blij", face_amt=0.5, at=SIGN)
A.blink_at(held, F(t_f + 2.4))
S.beat(held, t_f2 + 1.5, "staan", face="zelfverzekerd", face_amt=0.5, at=SIGN)
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 19d WIDE push-in: het volle strand, de strandwacht, het bord
S.cam(0.0, ((-9.0, 7.0, 2.3), (3.0, -10.0, 1.2), 26), ((-7.6, 4.6, 2.0), (3.0, -10.0, 1.4), 28))
# 19e MEDIUM: opa en oma (spiegelt 3c)
S.cam(t_e, ((-8.6, -5.9, 1.35), (-1.0, -3.6, 1.0), 26), ((-8.4, -6.0, 1.32), (-1.0, -3.8, 1.0), 27), handheld=0.06)
# 19f CLOSE: de jongen van voren (in zijn kijkrichting)
HT = S.headpos(held, t_f)
dn = V(d.x, d.y, 0).normalized()
side = V(dn.y, -dn.x, 0)
S.cam(t_f, (HT + dn * 1.4 + side * 0.25 + V(0, 0, -0.05), HT + V(0, 0, -0.06), 34), (HT + dn * 1.25 + side * 0.22 + V(0, 0, -0.05), HT + V(0, 0, -0.06), 36))
# 19f2 over zijn schouder naar het bord, trage push
S.cam(t_f2, (HT - dn * 0.7 - side * 0.6 + V(0, 0, 0.1), SIGN, 50), (HT - dn * 0.6 - side * 0.55 + V(0, 0, 0.1), SIGN, 68))

# ---------------------------------------------------------------- HUD, geluid, stem
S.counter("YEAR 5", 6300, t0=0.0)
S.ambience("sfx_strand_sfeer", 0.0, END, vol=0.22)
S.sfx("sfx_fluitje", 0.75, 0.3)
S.music("strijkers_emo", t_e, END, vol=0.16, fade_in=0.8, fade_out=0.6)
S.say("N19-03", at=t_e + 0.3)
S.say("N19-04", at=t_f2 + 0.4)
S.finish(length=END, tail=0.0)
