"""D04 · De val (script scène 4a-4h). Achtertuin met schuur, zonnige ochtend.
4a WIDE 6,5 s: broertje wijst naar het schuurdak, bal in de dakgoot; hij staat al op het dak bij de rand.
   VO: "Twenty minutes after you wake up, you get the first real test."  BROERTJE: "Get it! Get it!"
4b MEDIUM 3 s: hij buigt zich naar de bal, zijn voet glijdt over het mos, armen maaien.
4c LOW WIDE 3 s (slow motion): hij valt; we snijden weg vlak voor de klap. Geen muziek, alleen wind.
4d CLOSE 2 s: broertje gilt, handen voor zijn mond; de klap valt NA de gil, gedempt.
4e MEDIUM 5 s: hij ligt op de tegels, arm in een rare hoek. 2 s stilte. Knak, arm terug, hij gaat zitten. "...ow?"
4f MEDIUM 3 s: mama bij de achterdeur laat de wasmand vallen.  MAMA: "Don't. Move."
4g CLOSE 5 s: VO "A three-meter fall onto concrete. You should be in hospital. Instead..." Hij gooit de bal.
4h CLOSE 2,3 s: broertje vangt de bal, mond open.  BROERTJE: "Do it again!"

    python3 anim/v4/scenes/d04_schuur.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d04", "kleine_nd", "schuur", exposure=0.2)
sh = S.cuts([5.9, 3.0, 3.0, 2.0, 5.0, 3.0, 5.0, 2.3])
END = sh[-1][1]
t_b, t_c, t_d, t_e, t_f, t_g, t_h = (s[0] for s in sh[1:])


def roof_z(y):
    """Bovenkant van het voorste dakvlak (helling 28°, rand bij y -0,19)."""
    return 2.595 + 0.532 * (y - 0.52)


# ---------------------------------------------------------------- het broertje in de tuin
BRO = V(1.4, -3.3, 0.0)
bro = S.actor("broertje", BRO, 149)                 # kijkt naar het dak
ROOF_HEAD = V(3.4, 0.0, 3.6)
S.beat(bro, 0.0, "wijzen", face="lach", face_amt=0.8, at=ROOF_HEAD)
S.beat(bro, 2.0, "wijzen", face="blij", face_amt=1.0, at=ROOF_HEAD + V(0.2, -0.2, -0.6))
for k, t in enumerate(frange(3.9, 5.7, 0.26)):           # "Get it! Get it!": springt op en neer
    S.place(bro, t, BRO + V(0, 0, 0.08 if k % 2 == 0 else 0.0), 149)
    S.beat(bro, t, "juichen" if k % 2 == 0 else "wijzen", amount=0.8, face="schreeuw", face_amt=0.8,
           crouch=(0.0 if k % 2 == 0 else 0.05, 0), at=ROOF_HEAD)
S.place(bro, 5.8, BRO, 149)
S.beat(bro, 5.8, "staan", face="blij", face_amt=0.9, at=ROOF_HEAD)
S.beat(bro, t_c - 0.2, "schrik", face="geschrokken", face_amt=0.9, at=ROOF_HEAD + V(0, -0.4, -0.6))
# 4d: hij gilt, handen voor zijn mond (handen ~0,3 m voor zijn gezicht)
MOUTH = arms(arm("L", (0.30, 0.65, -0.70), (-0.45, 0.70, 0.55)), arm("R", (0.30, 0.65, -0.70), (-0.45, 0.70, 0.55)))
S.beat(bro, t_d, "staan", arms=MOUTH, face="schreeuw", face_amt=1.0, at=V(3.4, -2.0, 0.4), crouch=(0.03, 6))
S.beat(bro, t_d + 1.2, "staan", arms=MOUTH, face="bang", face_amt=1.0, at=V(3.4, -2.1, 0.2), crouch=(0.04, 8))
# vanaf 4e kijkt hij naar zijn grote broer op de tegels (draait naar hem toe)
S.place(bro, t_e - 0.1, BRO, 149)
S.place(bro, t_e + 0.4, BRO, 119)
S.beat(bro, t_e + 0.4, "staan", arms=MOUTH, face="bang", face_amt=0.9, at=V(3.4, -2.1, 0.3))
S.beat(bro, t_e + 3.0, "staan", face="verbaasd", face_amt=0.9, at=V(3.4, -2.2, 0.6))
CATCH = arms(arm("L", (0.20, 0.85, -0.45), (-0.20, 0.95, 0.15)), arm("R", (0.20, 0.85, -0.45), (-0.20, 0.95, 0.15)))
S.beat(bro, t_h - 0.2, "staan", arms=CATCH, face="verbaasd", face_amt=0.9, at=V(3.0, -2.5, 0.8))
S.beat(bro, t_h + 0.5, "staan", arms=CATCH, face="geschrokken", face_amt=0.9, at=V(2.6, -2.7, 0.9), crouch=(0.05, 6))
S.beat(bro, t_h + 1.1, "staan", arms=CATCH, face="lach", face_amt=1.0, at=V(3.0, -2.5, 0.7), crouch=(0.03, 2))
A.blink_at(bro, F(2.7))
A.blink_at(bro, F(t_e + 2.2))
S.hold(bro, END)

# ---------------------------------------------------------------- de bal
bal = S.obj("Voetbal")
_c = sum((bal.matrix_world @ V(c) for c in bal.bound_box), V((0, 0, 0))) / 8   # oorsprong naar het midden van de bal
bal.data.transform(Matrix.Translation(bal.matrix_world.inverted() @ _c).inverted())
bal.location = _c
BAL0 = V(_c)
BAL_GROUND = V(3.10, -2.30, 0.11)      # naast hem op de tegels
for t, p in ((0.0, BAL0), (8.25, BAL0), (8.5, BAL0 + V(-0.05, -0.30, 0.10)), (9.5, BAL0 + V(-0.15, -0.75, -0.55)),
             (11.0, V(3.1, -1.6, 1.0)), (12.3, BAL_GROUND + V(0.05, 0.25, 0.0)), (12.9, BAL_GROUND + V(0, 0.05, 0.35)),
             (13.4, BAL_GROUND), (t_g + 3.0, BAL_GROUND)):
    key(bal, t, loc=tuple(p))

# ---------------------------------------------------------------- hij, op het dak en vallend (kantelt om de heup)
held = S.actor("hoofdpersonage_kind", (3.4, 0.0, roof_z(0.0)), 0)
hb = Body(S, held, (3.4, 0.05, roof_z(0.05) + held.J["pelvis"].z), 0)
P_ = held.J["pelvis"].z
ROOF_FEET = ((0, 0.10, -0.05), (0, -0.08, 0.04))       # voeten volgen de helling (voorste voet lager)
hb.key(0.0, (3.4, 0.05, roof_z(0.05) + P_))
S.beat(held, 0.0, "staan", face="zelfverzekerd", face_amt=0.8, feet=ROOF_FEET, body={"head": (14, -8, 0), "spine": (6, 0, 0)})
S.beat(held, 2.2, "schouders_op", amount=0.5, face="grijns", face_amt=0.9, feet=ROOF_FEET, body={"head": (18, 10, 0), "spine": (8, 0, 0)})
S.beat(held, 4.0, "staan", face="grijns", face_amt=1.0, feet=ROOF_FEET, body={"head": (24, -12, 0), "spine": (10, 0, 0)})
hb.key(t_b - 0.1, (3.4, 0.0, roof_z(0.0) + P_))
# 4b: hij buigt naar de bal (linkerhand wijst ernaar, reikt niet tot de goot), dan glijdt zijn voet weg
REACH_L = arms(arm("L", (0.35, 0.80, -0.50), (0.25, 0.75, -0.62)), arm("R", (0.70, -0.10, -0.70), (0.80, 0.20, -0.55)))
S.beat(held, t_b + 0.2, "staan", arms=REACH_L, face="inspanning", face_amt=0.6, feet=ROOF_FEET, crouch=(0.10, 28),
       body={"head": (10, -12, 0)})
hb.key(t_b + 1.0, (3.4, -0.06, roof_z(-0.06) + P_ - 0.02))
S.beat(held, t_b + 1.2, "staan", arms=REACH_L, face="inspanning", face_amt=0.8, feet=ROOF_FEET, crouch=(0.08, 22),
       body={"head": (12, -14, 0)})
T_SLIP = t_b + 1.5
S.beat(held, T_SLIP - 0.15, "staan", arms=REACH_L, face="inspanning", face_amt=0.6, feet=ROOF_FEET, crouch=(0.12, 6),
       body={"head": (4, -6, 0)})                    # anticipatie: gewicht naar achter
hb.key(T_SLIP, (3.4, -0.08, roof_z(-0.08) + P_ - 0.05), tilt=-4)
FLAIL_A = arms(arm("L", (0.80, 0.30, 0.50), (0.40, 0.30, 0.86)), arm("R", (0.80, 0.10, 0.20), (0.80, -0.20, 0.55)))
FLAIL_B = arms(arm("L", (0.80, 0.10, 0.20), (0.80, -0.20, 0.55)), arm("R", (0.80, 0.30, 0.50), (0.40, 0.30, 0.86)))
hb.key(T_SLIP + 0.35, (3.4, -0.12, roof_z(-0.12) + 0.45), tilt=28)
hb.key(t_c, (3.4, -0.32, roof_z(-0.19) + 0.30), tilt=48)
fl = list(frange(T_SLIP + 0.05, t_d + 0.05, 0.17))
for k, t in enumerate(fl):
    lt = 0.0 if t < T_SLIP + 0.3 else (28 if t < t_c else 55)
    S.beat(held, t, "staan", arms=FLAIL_A if k % 2 else FLAIL_B, face="geschrokken", face_amt=1.0,
           body={"head": (-12, 0, 6 if k % 2 else -6)}, **hb.legs(lt, spread=0.25, bend=0.9, lift=-20 if k % 2 else -32))
# 4c: vrije val in slow motion, kantelt verder achterover; snijden weg vlak voor de tegels
hb.key(t_c + 0.9, (3.4, -0.85, 1.95), tilt=58)
hb.key(t_c + 2.1, (3.4, -1.55, 1.05), tilt=68)
hb.key(t_d + 0.02, (3.4, -1.85, 0.62), tilt=74)
show(held.rig, 0.0, t_d)
S.qc_skip.add(held.name)       # gekanteld rig: de hoofdregels van QC rekenen zonder ouder

# ---------------------------------------------------------------- hij op de tegels (4e-4g)
lig = S.actor("hoofdpersonage_kind", (3.4, -2.2, 0.0), 0)
lb = Body(S, lig, (3.4, -2.2, 0.14), 0)
show(lig.rig, t_d)
S.qc_skip.add(lig.name)
LIE_T = 78
WEIRD = arm("L", (0.95, -0.05, 0.30), (0.35, 0.80, -0.50))          # arm in een rare hoek (zonder bloed)
REST_L = arm("L", (0.30, 0.05, -0.95), (0.25, 0.20, -0.95))
REST_R = arm("R", (0.30, 0.05, -0.95), (0.25, 0.20, -0.95))
lb.key(t_d, (3.4, -2.2, 0.14), tilt=LIE_T)
S.beat(lig, t_d, "staan", arms=arms(WEIRD, REST_R), face="neutraal", face_amt=0.0, body={"head": (12, 0, 0)},
       **lb.legs(LIE_T, spread=0.30))
S.eyes_closed(lig, t_d, t_e + 1.1)
S.beat(lig, t_e + 1.0, "staan", arms=arms(WEIRD, REST_R), face="twijfel", face_amt=0.3, body={"head": (12, 0, 0)},
       **lb.legs(LIE_T, spread=0.30))
T_KNAK = t_e + 2.0
S.beat(lig, T_KNAK - 0.05, "staan", arms=arms(WEIRD, REST_R), face="verbaasd", face_amt=0.5, body={"head": (10, 6, 0)},
       **lb.legs(LIE_T, spread=0.30))
S.beat(lig, T_KNAK + 0.06, "staan", arms=arms(REST_L, REST_R), face="geschrokken", face_amt=0.8, body={"head": (10, 6, 0)},
       **lb.legs(LIE_T, spread=0.30))
# rechtop zitten
lb.key(t_e + 2.35, (3.4, -2.2, 0.14), tilt=LIE_T)
lb.key(t_e + 3.15, (3.4, -2.2, 0.13), tilt=6)
SIT_ARMS = arms(arm("L", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97)), arm("R", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97)))
S.beat(lig, t_e + 2.35, "staan", arms=arms(REST_L, REST_R), face="verbaasd", face_amt=0.6, body={"head": (8, 0, 0)},
       **lb.legs(LIE_T, spread=0.30))
S.beat(lig, t_e + 2.8, "staan", arms=SIT_ARMS, face="twijfel", face_amt=0.6, body={"head": (2, 0, 0)},
       **lb.legs(40, spread=0.28))
S.beat(lig, t_e + 3.15, "staan", arms=SIT_ARMS, face="twijfel", face_amt=0.8, body={"head": (-4, 0, 6)},
       **lb.legs(6, spread=0.26))
A.blink_at(lig, F(t_e + 3.6))
S.beat(lig, t_e + 4.2, "staan", arms=SIT_ARMS, face="verbaasd", face_amt=0.7, body={"head": (4, 0, -6)},
       **lb.legs(6, spread=0.26))
# 4g: hij kijkt naar de bal, pakt hem (rechterhand) en gooit hem naar zijn broertje
LOOK_BALL = {"head": (14, -30, 0), "neck": (6, -12, 0)}
S.beat(lig, t_g, "staan", arms=SIT_ARMS, face="twijfel", face_amt=0.6, body={"head": (4, -10, 0)}, **lb.legs(6, spread=0.26))
S.beat(lig, t_g + 1.4, "staan", arms=SIT_ARMS, face="blij", face_amt=0.5, body=LOOK_BALL, **lb.legs(6, spread=0.26))
T_PICK = t_g + 2.6
S.reach(lig, t_g + 1.9, "R", None, 0.0)
S.reach(lig, T_PICK, "R", BAL_GROUND + V(0.06, 0.02, 0.12))
S.beat(lig, T_PICK, "staan", arms=arms(arm("L", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97))), face="blij", face_amt=0.6,
       body={"head": (16, -30, 0), "neck": (6, -12, 0), "spine": (22, -14, -12)}, **lb.legs(6, spread=0.26))
S.reach(lig, T_PICK + 0.35, "R", None, 0.0)
WIND = arm("R", (0.55, -0.30, 0.78), (0.20, -0.45, 0.87))              # uithalen boven de schouder
THROW = arm("R", (0.40, 0.85, 0.35), (0.10, 0.95, 0.30))
T_REL = t_g + 4.55
TO_BRO = {"head": (-4, -40, 0), "neck": (0, -16, 0), "spine": (0, -12, 0)}
S.beat(lig, T_PICK + 0.45, "staan", arms=arms(arm("L", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97)), HOLD_FRONT_R),
       face="grijns", face_amt=0.8, body=TO_BRO, **lb.legs(6, spread=0.26))
S.beat(lig, T_REL - 0.35, "staan", arms=arms(arm("L", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97)), WIND),
       face="grijns", face_amt=1.0, body=dict(TO_BRO, chest=(-6, 10, 0)), **lb.legs(6, spread=0.26))
S.beat(lig, T_REL, "staan", arms=arms(arm("L", (0.30, -0.25, -0.92), (0.20, 0.10, -0.97)), THROW),
       face="lach", face_amt=1.0, body=dict(TO_BRO, chest=(8, -14, 0)), **lb.legs(6, spread=0.26))
S.beat(lig, T_REL + 0.5, "staan", arms=SIT_ARMS, face="grijns", face_amt=1.0, body=TO_BRO, **lb.legs(6, spread=0.26))
S.hold(lig, END)

# bal in zijn hand, gegooid, gevangen
grab(S, bal, lig, T_PICK, "hand.R", loc=(0, 0.07, -0.08), release=T_REL, mode="loc")
P_REL = S.bone_world(lig, "hand.R", T_REL) + V(0, 0, 0.05)
T_CATCH = t_h + 0.45
BRO_HANDS = S.bone_world(bro, "hand.R", T_CATCH) * 0.5 + S.bone_world(bro, "hand.L", T_CATCH) * 0.5 + V(0, 0, 0.06)
for k in range(7):
    u = k / 6
    p = P_REL.lerp(BRO_HANDS, u) + V(0, 0, 0.9 * 4 * u * (1 - u))
    key(bal, T_REL + (T_CATCH - T_REL) * u, loc=tuple(p))
grab(S, bal, bro, T_CATCH, "hand.R", mode="loc", target=None, offset=None, loc=(0, 0.04, 0))
key(bal, END, loc=tuple(BRO_HANDS))

# ---------------------------------------------------------------- mama bij de achterdeur, de wasmand valt
MAM = V(-2.0, -5.25, 0.0)
mam = S.actor("mama", MAM, 180)
show(mam.rig, t_f - 0.2)
mand = S.obj("Wasmand")
was = S.obj("Wasgoed")
was.parent = mand
was.matrix_parent_inverse = mand.matrix_world.inverted()
HOLD_M = arms(arm("L", (0.30, 0.35, -0.89), (0.05, 0.75, -0.66)), arm("R", (0.30, 0.35, -0.89), (0.05, 0.75, -0.66)))
STOP_M = arms(arm("L", (0.30, 0.85, -0.35), (0.10, 0.75, 0.65)), arm("R", (0.30, 0.85, -0.35), (0.10, 0.75, 0.65)))
HELD_AT = MAM + V(0.0, 0.36, 0.42)
T_DROP = t_f + 0.55
key(mand, 0.0, loc=tuple(mand.location), rot=(0, 0, 0))
key(mand, t_f - 0.3, loc=tuple(mand.location), rot=(0, 0, 0))
for t, p, r in ((t_f - 0.25, HELD_AT, 0), (T_DROP, HELD_AT, 0), (T_DROP + 0.28, MAM + V(0.05, 0.55, 0.0), 0),
                (T_DROP + 0.40, MAM + V(0.06, 0.58, 0.04), 8), (T_DROP + 0.55, MAM + V(0.06, 0.60, 0.0), 6)):
    key(mand, t, loc=tuple(p), rot=(r, 0, 0))
S.beat(mam, 0.0, "staan", arms=HOLD_M, face="blij", face_amt=0.4, look=(0, 0))
S.beat(mam, t_f, "staan", arms=HOLD_M, face="geschrokken", face_amt=0.8, body={"head": (-4, 0, 0)})
S.beat(mam, T_DROP - 0.05, "staan", arms=HOLD_M, face="geschrokken", face_amt=1.0)
S.beat(mam, T_DROP + 0.15, "schrik", face="geschrokken", face_amt=1.0, crouch=(0.03, -4))
S.beat(mam, t_f + 1.1, "staan", arms=STOP_M, face="bang", face_amt=1.0, crouch=(0.04, 8))
S.beat(mam, t_f + 2.4, "staan", arms=STOP_M, face="bang", face_amt=0.8, crouch=(0.04, 10))
S.hold(mam, END)
S.qc_skip.add(mand.name)
# wasgoed glijdt uit de mand over de tegels
wmat = was.active_material
for k, (dx, dy, rz) in enumerate(((-0.45, 0.35, 20), (0.40, 0.45, -35), (0.05, 0.85, 60), (-0.15, 0.65, -10))):
    w = T.box(f"Wasgoed_los_{k}", (0, 0, 0), (0.32, 0.26, 0.03), wmat, bevel=0.012, ol=0)
    A0 = MAM + V(0.05, 0.58, 0.25)
    key(w, 0.0, loc=tuple(A0), scale=0.001)
    key(w, T_DROP + 0.28, loc=tuple(A0), scale=0.001)
    key(w, T_DROP + 0.32, loc=tuple(A0), scale=1.0, rot=(0, 0, 0))
    key(w, T_DROP + 0.75, loc=tuple(MAM + V(dx, dy, 0.02)), scale=1.0, rot=(0, 0, rz))

# ---------------------------------------------------------------- camera's
# 4a WIDE: trage pan van het broertje omhoog naar het dak
S.cam(0.0, (V(-3.5, -4.0, 1.8), V(1.6, -1.6, 1.4), 22), (V(-3.3, -4.1, 1.9), V(2.8, -0.4, 2.3), 22))
# 4b MEDIUM op het dak, iets van voren en lager
S.cam(t_b, (V(2.1, -1.9, 3.45), V(3.4, -0.05, 3.35), 28), (V(2.15, -1.95, 3.35), V(3.4, -0.2, 3.1), 28))
# 4c LOW WIDE (camera van de set)
S.cam(t_c, (V(-0.2, -2.3, 0.3), V(3.2, -0.6, 1.7), 20), (V(-0.15, -2.35, 0.3), V(3.2, -0.9, 1.4), 20))
# 4d CLOSE broertje
S.cam(t_d, S.shot(bro, t_d + 0.8, size="mcu", az=5, lens=35), S.shot(bro, t_d + 0.8, size=0.85, az=5, lens=35))
# 4e MEDIUM statisch van opzij
S.cam(t_e, (V(5.3, -2.35, 0.80), V(3.4, -2.05, 0.38), 28), None, handheld=0.1)
# 4f MEDIUM mama bij de achterdeur
S.cam(t_f, (V(-1.1, -2.6, 1.3), V(-2.0, -5.0, 0.95), 26))
# 4g CLOSE: hij zit op de tegels, gooit de bal
S.cam(t_g, (V(2.55, -3.75, 0.95), V(3.2, -2.3, 0.45), 26), (V(2.6, -3.65, 0.92), V(3.2, -2.3, 0.45), 26))
# 4h CLOSE broertje vangt
S.cam(t_h, S.shot(bro, t_h + 0.6, size="mcu", az=-15, lens=35), S.shot(bro, t_h + 0.6, size=0.85, az=-12, lens=35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D04-01", at=0.3)
S.say("D04-02", who=bro, at=3.9)
S.sfx("sfx_struikelen", T_SLIP, 0.35)
S.sfx("sfx_slowmo", t_c - 0.05, 0.25)
S.sfx("sfx_vrije_val", t_c, 0.3)
S.sfx("sfx_val_klap", t_d + 1.05, 0.4)
S.sfx("sfx_bot_knak", T_KNAK, 0.5)
S.say("D04-03", who=lig, at=t_e + 2.75)
S.sfx("sfx_wasmand", T_DROP + 0.25, 0.4)
S.say("D04-04", who=mam, at=t_f + 1.05)
S.say("D04-05", at=t_g + 0.1)
S.sfx("sfx_whoosh", T_REL - 0.1, 0.15)
S.say("D04-06", who=bro, at=t_h + 0.75)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.08)
S.music("speels", 0.0, t_c, vol=0.2, fade_in=0.2, fade_out=0.3)
S.music("speels", t_g + 0.3, END, vol=0.16, fade_in=1.2, fade_out=0.3)
S.finish(length=END, tail=0.0)
