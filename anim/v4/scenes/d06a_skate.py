"""D06a · Testen: de skatehelling (script scène 6a-6c). Skatepark, dag.
6a  WIDE 4,7 s, trage push-in: de beste vriend filmt, de pestkop staat boven op de hoogste helling naast hem.
    VO: "Of course, nobody believes you. So your best friend wants proof."
6a2 MEDIUM 3,3 s: de pestkop achter hem.  PESTKOP: "If you're lying, this is gonna hurt."
6b  MEDIUM 2,4 s: de pestkop duwt hem; hij rolt de helling af als een ledenpop en stuitert tegen de rand.
6c1 CLOSE 1,8 s: hij staat op en klopt zijn broek af.
6c2 CLOSE 2,4 s: de vriend, telefoon omhoog.  VRIEND: "Do it again, I wasn't recording."

    python3 anim/v4/scenes/d06a_skate.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d06a", "kleine_nd", "skate", exposure=0.2)
sh = S.cuts([4.7, 3.3, 2.4, 1.8, 2.4])
END = sh[-1][1]
t_a2, t_b, t_c1, t_c2 = (s[0] for s in sh[1:])
PZ = 3.3                                              # bovenkant van het platform (y 5..7)
for o in bpy.data.objects:                            # de markering van de set
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de pestkop en de vriend op het platform
pest = S.actor("pestkop", (0.18, 5.95, PZ), 0)
vriend = S.actor("beste_vriend", (-1.15, 5.45, PZ), 75)
HERO0 = V(0.0, 5.22, PZ)
held = S.actor("hoofdpersonage_kind", HERO0, 0)
P_ = held.J["pelvis"].z
H_HEAD = S.head(held)
phone = prop_phone(S, "Telefoon_vriend")
grab(S, phone, vriend, 0.0, "hand.L", loc=(0, 0.06, 0.0), rot=(0, 0, 0))
S.beat(vriend, 0.0, "filmen", face="lach", face_amt=0.8, at=H_HEAD)
S.beat(vriend, 2.5, "filmen", face="grijns", face_amt=0.9, at=H_HEAD)
S.beat(vriend, t_b + 0.5, "filmen", face="geschrokken", face_amt=0.8, at=V(0, 2.5, 2.0))
S.beat(vriend, t_c1, "filmen", face="verbaasd", face_amt=0.8, at=V(0, -1.0, 1.0))
S.beat(vriend, t_c2 + 0.2, "staan", arms=arms(arm("L", (0.35, 0.40, -0.85), (-0.10, 0.45, 0.89))), face="geschrokken",
       face_amt=0.7, at=V(0, -1.0, 1.0))                       # telefoon omhoog, kijkt geschrokken op zijn scherm
S.beat(vriend, t_c2 + 1.2, "staan", arms=arms(arm("L", (0.35, 0.40, -0.85), (-0.10, 0.45, 0.89))), face="nerveus",
       face_amt=0.9, at=V(0, -1.0, 1.0))
A.blink_at(vriend, F(1.6))
S.hold(vriend, END)

S.beat(pest, 0.0, "armen_over", face="zelfverzekerd", face_amt=0.9, at=H_HEAD)
S.beat(pest, t_a2 + 0.2, "armen_over", face="grijns", face_amt=1.0, at=H_HEAD + V(0, 0, -0.1))
T_PUSH = t_b + 0.35
BACK = V(0.0, 5.42, PZ + 1.0)
S.reach(pest, T_PUSH - 0.35, "L", BACK + V(0.12, 0.10, 0.0))
S.reach(pest, T_PUSH - 0.35, "R", BACK + V(-0.12, 0.10, 0.0))
S.reach(pest, T_PUSH, "L", BACK + V(0.12, -0.10, 0.0))
S.reach(pest, T_PUSH, "R", BACK + V(-0.12, -0.10, 0.0))
S.reach(pest, T_PUSH + 0.3, "L", None, 0.0)
S.reach(pest, T_PUSH + 0.3, "R", None, 0.0)
S.beat(pest, T_PUSH - 0.3, "staan", face="grijns", face_amt=1.0, at=H_HEAD, crouch=(0.04, 4))
S.beat(pest, T_PUSH, "duwen", face="grijns", face_amt=1.0, at=H_HEAD, crouch=(0.06, 6))
S.beat(pest, T_PUSH + 0.5, "armen_over", face="lach", face_amt=1.0, at=V(0, 2.0, 1.5))
S.hold(pest, END)

# ---------------------------------------------------------------- hij: staat aan de rand, wordt geduwd, rolt naar beneden
hb = Body(S, held, HERO0 + V(0, 0, P_), 0)
S.qc_skip.add(held.name)
S.beat(held, 0.0, "schouders_op", amount=0.4, face="zelfverzekerd", face_amt=0.7)
S.beat(held, 2.2, "staan", face="grijns", face_amt=0.8, body={"head": (0, -25, 0)})
S.beat(held, t_a2 + 0.6, "staan", face="twijfel", face_amt=0.6, body={"head": (14, 0, 0)})      # kijkt naar beneden
S.beat(held, t_a2 + 2.2, "staan", face="nerveus", face_amt=0.5, body={"head": (16, 0, -4)})
hb.key(0.0, HERO0 + V(0, 0, P_))
hb.key(T_PUSH, HERO0 + V(0, 0, P_))


def slope(y, up=0.62):
    """Heuppunt boven de helling (45°, van y 4 / z 3,2 tot y 0,8 / z 0)."""
    return V(0.0, y, max(0.0, y - 0.8) + up)


path = [(T_PUSH, HERO0 + V(0, 0, P_), 0), (T_PUSH + 0.18, HERO0 + V(0, -0.35, P_ - 0.05), -30),
        (T_PUSH + 0.40, V(0, 4.2, 3.2 + 0.45), -95), (T_PUSH + 0.65, slope(3.3, 1.0), -185), (T_PUSH + 0.90, slope(2.3), -275),
        (T_PUSH + 1.15, slope(1.3), -365), (T_PUSH + 1.35, slope(0.55, 0.55), -440), (T_PUSH + 1.55, V(0, -0.2, 1.1), -520),
        (T_PUSH + 1.80, V(0, -0.85, 0.16), -282 - 360)]
for t, p, tl in path:
    hb.key(t, p, tilt=tl)
FLAIL_A = arms(arm("L", (0.80, 0.30, 0.50), (0.40, 0.30, 0.86)), arm("R", (0.80, 0.10, 0.20), (0.80, -0.20, 0.55)))
FLAIL_B = arms(arm("L", (0.80, 0.10, 0.20), (0.80, -0.20, 0.55)), arm("R", (0.80, 0.30, 0.50), (0.40, 0.30, 0.86)))
S.beat(held, T_PUSH, "schrik", face="geschrokken", face_amt=1.0)
for k, t in enumerate(frange(T_PUSH + 0.15, T_PUSH + 1.7, 0.16)):
    S.beat(held, t, "staan", arms=FLAIL_A if k % 2 else FLAIL_B, face="schreeuw" if k < 5 else "inspanning", face_amt=1.0,
           body={"head": (-10, 0, 8 if k % 2 else -8), "spine": (0, 0, 6 if k % 2 else -6)},
           **hb.legs(0, spread=0.3, bend=0.9, lift=-30 - 25 * (k % 3)))
T_LAND = T_PUSH + 1.8
REST = arms(arm("L", (0.45, 0.05, -0.90), (0.40, 0.20, -0.90)), arm("R", (0.45, 0.05, -0.90), (0.40, 0.20, -0.90)))
S.beat(held, T_LAND, "staan", arms=REST, face="inspanning", face_amt=0.6, body={"head": (10, 0, 0)}, **hb.legs(78, spread=0.3))
S.beat(held, t_c1, "staan", arms=REST, face="twijfel", face_amt=0.5, body={"head": (12, 0, 0)}, **hb.legs(78, spread=0.3))
# 6c1: hij gaat zitten, staat op, klopt zijn broek af
GROUND = V(0, -0.85, 0)
hb.key(t_c1 + 0.05, GROUND + V(0, 0, 0.16), tilt=-282 - 360)
hb.key(t_c1 + 0.45, GROUND + V(0, 0, 0.14), tilt=-354 - 360)
hb.key(t_c1 + 0.85, GROUND + V(0, -0.25, P_ - 0.18), tilt=-372 - 360)
hb.key(t_c1 + 1.1, GROUND + V(0, -0.30, P_), tilt=-360 - 360)
S.beat(held, t_c1 + 0.45, "staan", arms=REST, face="twijfel", face_amt=0.6, **hb.legs(6, spread=0.3))
S.beat(held, t_c1 + 0.85, "staan", face="twijfel", face_amt=0.6, crouch=(0.18, 10))
PAT_A = arms(arm("L", (0.30, 0.10, -0.95), (0.20, 0.35, -0.90)), arm("R", (0.35, -0.15, -0.92), (0.20, 0.10, -0.97)))
PAT_B = arms(arm("L", (0.35, -0.15, -0.92), (0.20, 0.10, -0.97)), arm("R", (0.30, 0.10, -0.95), (0.20, 0.35, -0.90)))
for k, t in enumerate(frange(t_c1 + 1.1, END, 0.17)):
    S.beat(held, t, "staan", arms=PAT_A if k % 2 else PAT_B, face="zelfverzekerd" if t > t_c2 else "blij", face_amt=0.7,
           crouch=(0.04, 12), body={"head": (8, 0, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(4.6, -2.4, 3.3), V(0.0, 5.2, 3.9), 32), (V(3.7, -1.3, 3.6), V(0.0, 5.3, 4.0), 32))
S.cam(t_a2, (V(1.9, 3.0, 4.9), V(0.0, 5.5, 4.3), 30), (V(1.75, 3.15, 4.9), V(0.05, 5.5, 4.35), 30))
S.cam(t_b, None, fn=lambda t: (V(3.4, hb.at(t).y - 1.4, hb.at(t).z + 0.8), hb.at(t) + V(0, -0.3, 0.2), 30))
S.cam(t_c1, (V(1.0, -3.2, 1.0), V(0.0, -1.1, 0.8), 30), (V(0.95, -3.1, 1.05), V(0.0, -1.15, 0.95), 30))
S.cam(t_c2, S.shot(vriend, t_c2 + 1.0, size="mcu", az=-20, lens=35), S.shot(vriend, t_c2 + 1.0, size=0.85, az=-18, lens=35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D06-01", at=0.2)
S.say("D06-02", who=pest, at=t_a2 + 0.1)
S.sfx("sfx_struikelen", T_PUSH, 0.35)
for t, v in ((T_PUSH + 0.4, 0.25), (T_PUSH + 0.9, 0.2), (T_PUSH + 1.35, 0.25), (T_LAND, 0.3)):
    S.sfx("sfx_val_klap", t, v)
S.say("D06-03", who=vriend, at=t_c2 + 0.15)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.08)
S.music("funky", 0.0, END, vol=0.17, fade_in=0.3, fade_out=0.2)
S.finish(length=END, tail=0.0)
