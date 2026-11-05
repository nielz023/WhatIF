"""D08c · De club en de parkeerplaats (script scène 8c-8d2). Ingang club, nacht.
8c  MEDIUM 4,6 s + 8c2 2,6 s, trage dolly: de hele oude klas (volwassen) gaat de club binnen; hij loopt mee. De portier legt zijn
    hand plat voor hem.  VO: "Your whole class goes out to celebrate. You go too. For about four seconds."
    PORTIER: "Nice try, kid."
8d  CLOSE 3 s: hij kijkt de klas na, de deur valt dicht.  VO: "You will never, ever get in."
8d2 MEDIUM handheld 4 s, parkeerplaats (verderop in dezelfde straat): hij zit achter het stuur van de auto van de
    vriend (cabrio), kan net over het stuur kijken. Een agent klopt op het portier.
    AGENT: "License, kid?"  JONGEN: "I'm thirty-two!"

    python3 anim/v4/scenes/d08c_club.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403
from lib import stad as SD  # noqa: E402
from lib import props as PR  # noqa: E402

S = Scene4("d08c", "kleine_nd", "club", exposure=0.25, night=True)
sh = S.cuts([4.6, 2.6, 3.0, 4.0])
END = sh[-1][1]
t_c2, t_d, t_p = sh[1][0], sh[2][0], sh[3][0]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de deur (scharnier links, zwaait naar buiten)
deur = S.obj("Club_deur")
dh = hinge(deur, (-1.0, 5.40, 0.0))
for t, a in ((0.0, 0), (1.5, 0), (1.9, -95), (t_d + 0.6, -95), (t_d + 0.95, 0)):
    key(dh, t, rot=(0, 0, a))

# ---------------------------------------------------------------- de portier
port = S.actor("portier", (1.45, 4.6, 0), -32)
HERO_STOP = V(0.3, 3.5, 0.0)                         # buiten de draaicirkel van de deur (2 m)
S.beat(port, 0.0, "armen_over", face="neutraal", face_amt=0.7, at=V(-2.0, 0.0, 1.6))
S.beat(port, 3.0, "armen_over", face="neutraal", face_amt=0.7, at=V(-0.5, 2.0, 1.5))
S.walk(port, 4.25, 4.75, [(1.45, 4.6, 0), (0.9, 3.95, 0)], stride=0.5, end_rot=-53)
S.beat(port, 4.6, "staan", face="zelfverzekerd", face_amt=0.8, at=HERO_STOP + V(0, 0, 1.3))
S.reach(port, 4.55, "R", None, 0.0)
S.hold(port, t_d - 0.05)
# ---------------------------------------------------------------- de oude klas: volwassen, lopen naar binnen
DOOR = V(0.0, 5.35, 0.0)
klas = [("beste_vriend_20", (-2.4, -1.0), 0.0, 2.3), ("figurant_a", (-1.5, -1.9), 0.0, 2.8),
        ("figurant_b", (-3.0, -2.2), 0.2, 3.3), ("figurant_c", (-2.0, -3.0), 0.3, 3.8), ("figurant_d", (-3.3, -3.4), 0.5, 4.3)]
for name, (x, y), t0, t1 in klas:
    ch = S.actor(name, (x, y, 0), 160)
    S.walk(ch, t0, t1, [(x, y, 0), (-0.45, 3.4, 0), DOOR + V(-0.2, 0.15, 0)], stride=0.62)
    S.beat(ch, t0, "staan", face="lach", face_amt=0.8, at=DOOR + V(0, 0, 1.7))
    show(ch.rig, 0.0, t1 - 0.02)
    S.qc_skip.add(ch.name)

# ---------------------------------------------------------------- hij loopt mee en wordt tegengehouden
held = S.actor("hoofdpersonage_kind", (0.2, -0.2, 0), 180)
S.walk(held, 0.5, 4.75, [(0.2, -0.2, 0), (0.45, 2.4, 0), HERO_STOP], stride=0.45, end_rot=180)
S.beat(held, 0.5, "staan", face="blij", face_amt=0.8, at=DOOR + V(0, 0, 1.6))
S.beat(held, 4.85, "schrik", face="geschrokken", face_amt=0.8, at=HERO_STOP + V(0, -0.4, 1.5), crouch=(0.02, -8))
S.beat(held, 5.6, "staan", face="twijfel", face_amt=0.7, at=V(0.9, 3.95, 2.1))          # kijkt omhoog naar de portier
FACE = S.head(held, 5.0)
S.reach(port, 4.95, "R", FACE + V(0.04, 0.36, 0.0))                                        # hand plat voor zijn gezicht
S.reach(port, t_d - 0.1, "R", FACE + V(0.04, 0.36, 0.0))
S.teleport(port, t_d, (1.6, 3.0, 0), -30)                                                   # terug op zijn post (snede)
S.reach(port, t_d, "R", None, 0.0)
S.beat(port, t_d, "armen_over", face="zelfverzekerd", face_amt=0.6, at=HERO_STOP + V(0, 0, 1.2))
S.hold(port, t_p)
S.beat(held, t_d, "staan", face="twijfel", face_amt=0.7, at=DOOR + V(-0.3, 0.0, 1.4))      # kijkt de klas na
S.beat(held, t_d + 1.2, "staan", face="verdrietig", face_amt=0.5, at=V(1.6, 3.9, 1.0), crouch=(0.0, 4))   # draait weg, naar ons toe
S.beat(held, t_d + 2.2, "staan", face="verdrietig", face_amt=0.6, at=V(1.8, 3.8, 0.7), body={"head": (6, 0, 0)})
A.blink_at(held, F(t_d + 1.5))

# ---------------------------------------------------------------- 8d2: de cabrio van de vriend, verderop
CAR = V(-14.0, -7.4, -0.1)
car = SD.car2("Auto_vriend", tuple(CAR), rot=0.0, color=(0.75, 0.12, 0.10), open_cab=True)
PR.lamp_post("Lantaarn_parkeer", (-12.2, -5.6, 0), on=True)
T.point_light("Lantaarn_parkeer_licht", (-12.6, -6.0, 4.0), color=(1.0, 0.78, 0.5), energy=700, radius=0.3)
SEAT = CAR + V(0.0, 0.4, 0.0)
hs, hz_ = sit(held, seat_top=0.71 - 0.1)
S.teleport(held, t_p, SEAT + V(0, 0, hz_ - 0.1 + 0.1), 90)
WHEEL = CAR + V(0.45, 0.4, 0.98)
S.beat(held, t_p, **hs, face="zelfverzekerd", face_amt=0.7, at=CAR + V(6, 0.4, 1.2))
S.reach(held, t_p - 0.02, "L", None, 0.0)
S.reach(held, t_p - 0.02, "R", None, 0.0)
S.reach(held, t_p, "L", WHEEL + V(-0.04, 0.13, 0.07))
S.reach(held, t_p, "R", WHEEL + V(-0.04, -0.13, 0.07))
S.reach(held, END, "L", WHEEL + V(-0.04, 0.13, 0.07))
S.reach(held, t_p + 1.6, "R", WHEEL + V(-0.04, -0.13, 0.07))
AG = V(-13.85, -6.05, 0.0)
S.beat(held, t_p + 0.9, **hs, face="nerveus", face_amt=0.8, at=AG + V(0, 0, 1.6))            # schrikt van het kloppen
S.reach(held, t_p + 2.0, "R", None, 0.0)
S.beat(held, t_p + 1.9, **hs, arms=arms(arm("R", (0.45, 0.30, -0.84), (0.10, 0.55, 0.83))), face="boos", face_amt=1.0,
       at=AG + V(0, 0, 1.6))                                                                      # "I'm thirty-two!"
S.beat(held, t_p + 3.2, **hs, arms=arms(arm("R", (0.40, 0.35, -0.84), (0.20, 0.75, 0.10))), face="boos", face_amt=0.8,
       at=AG + V(0, 0, 1.6))
S.hold(held, END)

agent = S.actor("agent", AG, 0)
show(agent.rig, t_p)
S.beat(agent, t_p, "staan", face="neutraal", face_amt=0.7, at=SEAT + V(0, 0, 1.3), crouch=(0.04, 14))
KNOCK = CAR + V(0.2, 0.92, 0.82)
for k, t in enumerate((t_p + 0.3, t_p + 0.45, t_p + 0.6, t_p + 0.75)):
    S.reach(agent, t, "R", KNOCK + V(0, 0.08 if k % 2 == 0 else 0.0, 0.0))
S.reach(agent, t_p + 1.1, "R", None, 0.0)
S.beat(agent, t_p + 1.3, "staan", face="twijfel", face_amt=0.6, at=SEAT + V(0, 0, 1.3), crouch=(0.03, 10))
S.beat(agent, t_p + 2.3, "staan", face="verbaasd", face_amt=0.8, at=SEAT + V(0, 0, 1.3), crouch=(0.0, 0))
S.hold(agent, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-3.4, -1.4, 1.65), V(0.0, 4.4, 1.25), 28), (V(-2.6, -0.4, 1.6), V(0.0, 4.5, 1.2), 28))
S.cam(t_c2, (V(2.2, 1.9, 1.5), V(0.5, 3.8, 1.3), 30), (V(2.15, 2.0, 1.48), V(0.5, 3.8, 1.3), 30))
S.cam(t_d, (V(2.2, 4.4, 1.4), V(-0.3, 4.2, 1.3), 26), (V(2.12, 4.38, 1.39), V(-0.3, 4.2, 1.3), 26))   # buiten de deurcirkel
S.cam(t_p, (V(-11.2, -5.8, 1.7), CAR + V(0.1, 0.6, 1.35), 26), (V(-11.5, -5.85, 1.65), CAR + V(0.1, 0.6, 1.35), 26), handheld=0.12)

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2032, t0=0.0, tick=False)
S.say("D08-03", at=0.2)
S.say("D08-04", who=port, at=5.35)
S.say("D08-05", at=t_d + 0.15)
S.sfx("sfx_deur_dicht", t_d + 0.85, 0.35)
S.say("D08-06", who=agent, at=t_p + 0.95)
S.say("D08-07", who=held, at=t_p + 2.3)
S.sfx("sfx_knokkels", t_p + 0.3, 0.4)
S.ambience("sfx_club_buiten", 0.0, t_p, vol=0.12)
S.ambience("sfx_stad_nacht_wind", t_p, END, vol=0.1)
S.music("piano_warm", 0.0, END, vol=0.15, fade_in=0.3, fade_out=0.3)
S.finish(length=END, tail=0.0)
