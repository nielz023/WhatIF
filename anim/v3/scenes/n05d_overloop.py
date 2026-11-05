"""N05d · De overloop om middernacht (script scène 5d-5h).
5d papa leest zijn telefoon op armlengte ("It's a hack."), mama vindt de mouw van haar ochtendjas pas de tweede keer.
5e het broertje stormt zijn kamer uit, remt af aan de deurpost ("Does that mean no school?").
5f opa in zijn deuropening, schuift zijn bril recht ("It means nobody knows what happens next.").
5g het hele gezin, rood verlicht, stilte; mama legt haar hand op de schouder van het broertje.
5h close op de jongen. VO: "Here's the thing. A rule only works... if everyone believes in it."

    blender -b -P anim/v3/scenes/n05d_overloop.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n05d", "overloop", "nacht", exposure=0.3, night=True)
sh = S.cuts([3.5, 3.0, 4.3, 3.0, 5.4])
END = sh[-1][1]
t_e, t_f, t_g, t_h = (s[0] for s in sh[1:])
RED = (1.0, 0.08, 0.05)

PYJ = dict(papa=dict(shirt=(0.30, 0.42, 0.68), broek=(0.30, 0.42, 0.68)),
           mama=dict(shirt=(0.72, 0.42, 0.58), broek=(0.85, 0.75, 0.80)),
           broertje=dict(shirt=(0.95, 0.72, 0.25), broek=(0.95, 0.72, 0.25)),
           opa=dict(shirt=(0.55, 0.62, 0.52), broek=(0.55, 0.62, 0.52)))


def door_open(name, t0, t1, angle):
    leaf = S.obj(name + "_blad")
    rz = leaf.rotation_euler.z
    for t, a in ((t0, 0.0), (t1, angle)):
        leaf.rotation_euler.z = rz + math.radians(a)
        leaf.keyframe_insert("rotation_euler", index=2, frame=F(t))
    return leaf


def phone_for(ch, nm, t=0.0, side="R"):
    ph = prop_phone(S, nm, screen=RED)
    grab(S, ph, ch, t, f"hand.{side}", loc=(0, 0.07, 0.02), rot=(90, 0, 180))
    return ph


def face_light(ch, nm, t_on=0.0, energy=35, off=(0.0, -0.45, -0.25)):
    """Rood schermlicht onder het gezicht (volgt de figuur via een kind van de rig)."""
    li = T.point_light(nm, (0, 0, 0), color=RED, energy=energy, radius=0.08, shadow=False)
    li.parent = ch.rig
    li.location = V(0, 0, ch.J["head_c"].z) + V(*off)
    if t_on > 0:
        light_key(li, 0.0, 0)
        light_key(li, t_on, energy)
    return li


HOLD = arms(arm("R", (0.25, 0.45, -0.85), (-0.25, 0.9, 0.3)), arm("L", (0.25, 0.45, -0.85), (-0.35, 0.85, 0.25)))
HOLD1 = arms(arm("R", (0.25, 0.45, -0.85), (-0.25, 0.9, 0.3)))

# ---------------------------------------------------------------- de cast
papa = S.actor("papa", (1.85, -0.15, 0), -15, outfit=PYJ["papa"])
mama = S.actor("mama", (2.45, -0.45, 0), -55, outfit=PYJ["mama"])
bro = S.actor("broertje", (-0.2, 2.05, 0), 0, outfit=PYJ["broertje"])
opa = S.actor("opa", (1.6, 1.12, 0), -25, outfit=PYJ["opa"])
held = S.actor("hoofdpersonage_pyjama", (-1.9, 2.3, 0), 0)
visible(held.body, 0.0, False)
visible(held.body, t_g - 0.1, True)
door_open("Deur_ouders", 0.0, 0.01, 100)
door_open("Deur_jongen", t_g - 0.3, t_g - 0.1, 95)
door_open("Deur_opa", 0.0, 0.01, 95)
door_open("Deur_broertje", t_e - 0.05, t_e + 0.25, 100)

# ---------------------------------------------------------------- 5d papa en mama
p_ph = phone_for(papa, "Telefoon_papa")
face_light(papa, "Schermlicht_papa", energy=30, off=(0.0, -0.6, -0.15))
FAR = arms(arm("R", (0.2, 0.85, -0.35), (0.0, 1.0, 0.25)))
S.beat(papa, 0.0, "staan", arms=HOLD1, face="nerveus", face_amt=0.6, look=(0.0, -0.3))
S.beat(papa, 0.45, "staan", arms=FAR, face="twijfel", face_amt=0.9, look=(0.0, -0.15), body={"head": (-10, 0, 0)}, ogen_knijp=0.7)
S.beat(papa, 1.3, "staan", arms=FAR, face="twijfel", face_amt=1.0, look=(0.0, -0.15), body={"head": (-12, 0, 4)}, ogen_knijp=0.8)
S.beat(papa, 2.3, "staan", arms=FAR, face="nerveus", face_amt=0.9, look=(0.0, -0.1), body={"head": (-8, 0, -3)}, ogen_knijp=0.5)
S.beat(papa, 3.0, "staan", arms=HOLD1, face="nerveus", face_amt=0.8, look=(-0.4, 0.0))
S.say("N05-01", who=papa, at=0.55)
# mama: arm zoekt achter haar de mouw (mis), tweede keer raak, dan ochtendjas dicht
BACK = arm("L", (0.35, -0.55, -0.75), (0.1, -0.85, -0.5))
S.beat(mama, 0.0, "staan", face="nerveus", face_amt=0.5, at=S.head(papa, 0.0))
S.beat(mama, 0.5, "staan", arms=arms(BACK), face="nerveus", face_amt=0.6, body={"chest": (0, 0, 14)}, at=S.head(papa, 0.5))
S.beat(mama, 0.95, "staan", arms=arms(arm("L", (0.45, -0.3, -0.85), (0.3, -0.5, -0.8))), face="twijfel", face_amt=0.7,
       body={"chest": (0, 0, 8)}, look=(0.5, -0.4))
S.beat(mama, 1.45, "staan", arms=arms(BACK), face="nerveus", face_amt=0.6, body={"chest": (0, 0, 16)}, look=(0.5, -0.4))
S.beat(mama, 2.05, "armen_over", amount=0.9, face="nerveus", face_amt=0.7, at=S.head(papa, 2.05))
S.beat(mama, 2.9, "armen_over", amount=1.0, face="bang", face_amt=0.5, at=S.head(papa, 2.9))

# ---------------------------------------------------------------- 5e het broertje stormt naar buiten
b_ph = phone_for(bro, "Telefoon_broertje", side="R")    # rechts: links grijpt hij de deurpost
face_light(bro, "Schermlicht_broertje", energy=22)
S.beat(bro, 0.0, "staan", face="verbaasd", face_amt=0.6)
S.run(bro, t_e + 0.05, t_e + 0.85, [V(-0.2, 2.05, 0), V(-0.15, 1.45, 0), V(-0.05, 0.95, 0)], stride=0.42, lean=10, ease_out=0.3)
POST = V(0.25, 1.12, 0.72)                       # deurpost aan zijn linkerkant, op schouderhoogte van een kind
S.reach(bro, 0.0, "L", inf=0.0)
S.reach(bro, t_e + 0.7, "L", inf=0.0)
S.reach(bro, t_e + 0.85, "L", POST)
S.reach(bro, t_e + 1.35, "L", POST)
S.reach(bro, t_e + 1.65, "L", inf=0.0)
S.turn(bro, t_e + 0.9, t_e + 1.4, 40, loc=V(0.05, 0.85, 0))
S.beat(bro, t_e + 0.95, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="verbaasd", face_amt=1.0, at=S.head(papa, t_e + 0.95),
       body={"spine": (8, 0, 0)}, feet="keep")
S.beat(bro, t_e + 1.5, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="blij", face_amt=0.8, at=S.head(papa, t_e + 1.5),
       feet="keep")
S.say("N05-02", who=bro, at=t_e + 1.0)
S.beat(bro, t_e + 2.6, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="lach", face_amt=0.6, at=S.head(papa, t_e + 2.6),
       feet="keep")
# papa en mama kijken naar hem
S.beat(papa, t_e + 0.9, "staan", arms=HOLD1, face="verbaasd", face_amt=0.5, at=S.head(bro, t_e + 0.9))
S.beat(mama, t_e + 0.9, "armen_over", amount=1.0, face="verbaasd", face_amt=0.5, at=S.head(bro, t_e + 0.9))

# ---------------------------------------------------------------- 5f opa schuift zijn bril recht
S.beat(opa, 0.0, "staan", face="neutraal", face_amt=0.5, at=S.head(bro, 0.0))
# één hand (rechts) schuift de bril recht, VÓÓR het grote hoofd langs (niet erdoor); links blijft omlaag
FWD = V(math.sin(math.radians(-25)), -math.cos(math.radians(-25)), 0)
SIDE_R = V(-FWD.y, FWD.x, 0) * -1                       # rechterkant van opa
GL = S.headpos(opa, t_f) + FWD * 0.36 + V(0, 0, -0.08)          # pols vlak onder de bril: de vingers duwen hem omhoog
S.reach(opa, 0.0, "R", inf=0.0)
S.reach(opa, 0.0, "L", inf=0.0)
S.reach(opa, t_f + 0.1, "R", inf=0.0)
S.reach(opa, t_f + 0.55, "R", GL + SIDE_R * 0.06)
S.reach(opa, t_f + 1.0, "R", GL + SIDE_R * 0.03 + V(0, 0, 0.03))
S.reach(opa, t_f + 1.4, "R", inf=0.0)
S.reach(opa, END, "L", inf=0.0)
S.beat(opa, t_f + 0.5, "staan", face="neutraal", face_amt=0.4, look=(0.0, 0.0), body={"head": (-4, 0, 0)})
S.beat(opa, t_f + 1.3, "staan", face="vastberaden", face_amt=0.4, at=S.head(bro, t_f + 1.3))
S.say("N05-03", who=opa, at=t_f + 0.4)
S.beat(opa, t_f + 3.6, "staan", face="verdrietig", face_amt=0.4, at=S.head(bro, t_f + 3.6))
S.beat(bro, t_f + 0.8, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="twijfel", face_amt=0.6, at=S.head(opa, t_f + 0.8),
       feet="keep")
S.beat(bro, t_f + 3.0, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="nerveus", face_amt=0.7, at=S.head(opa, t_f + 3.0),
       feet="keep")
S.beat(papa, t_f + 0.3, "staan", arms=HOLD1, face="nerveus", face_amt=0.6, at=S.head(opa, t_f + 0.3))
S.beat(mama, t_f + 0.3, "armen_over", amount=1.0, face="bang", face_amt=0.5, at=S.head(opa, t_f + 0.3))

# ---------------------------------------------------------------- 5g het hele gezin, stilte
S.teleport(mama, t_g, V(0.55, 0.55, 0), -30)
S.teleport(papa, t_g, V(1.15, 0.05, 0), -35)
S.teleport(held, t_g, V(-1.35, 0.55, 0), 55)
h_ph = phone_for(held, "Telefoon_jongen")
face_light(held, "Schermlicht_jongen", t_on=t_g, energy=28)
m_ph = phone_for(mama, "Telefoon_mama", side="L")
face_light(mama, "Schermlicht_mama", t_on=t_g, energy=22)
S.beat(held, 0.0, "staan", arms=HOLD1, face="neutraal", face_amt=0.4)
S.beat(held, t_g, "staan", arms=HOLD1, face="nerveus", face_amt=0.7, look=(0.0, -0.4), feet="keep")
S.beat(held, t_g + 1.5, "staan", arms=HOLD1, face="nerveus", face_amt=0.8, look=(0.3, -0.2), feet="keep")
S.beat(mama, t_g, "staan", arms=arms(arm("L", (0.25, 0.45, -0.85), (-0.35, 0.85, 0.25))), face="bang", face_amt=0.5,
       look=(0.0, -0.4), feet="keep")
# mama legt haar hand op zijn hoofd (zijn schouder zit te laag voor haar korte arm)
SHOULDER = S.headpos(bro, t_g + 1.0) + V(0.12, -0.05, 0.27)
S.reach(mama, t_g, "R", inf=0.0)
S.reach(mama, t_g + 1.1, "R", inf=0.0)
S.reach(mama, t_g + 1.4, "R", SHOULDER)
S.reach(mama, END, "R", SHOULDER)
S.beat(mama, t_g + 1.4, "staan", arms=arms(arm("L", (0.25, 0.45, -0.85), (-0.35, 0.85, 0.25))), face="verdrietig", face_amt=0.4,
       at=S.head(bro, t_g + 1.4), feet="keep")
S.beat(papa, t_g, "staan", arms=HOLD1, face="nerveus", face_amt=0.7, look=(0.0, -0.4), feet="keep")
S.beat(papa, t_g + 1.8, "staan", arms=HOLD1, face="nerveus", face_amt=0.7, at=S.head(held, t_g + 1.8), feet="keep")
S.beat(bro, t_g, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="nerveus", face_amt=0.6,
       look=(0.0, -0.4), feet="keep")
S.beat(bro, t_g + 1.5, "staan", arms=arms(arm("R", (0.3, 0.5, -0.8), (-0.2, 0.9, 0.3))), face="verdrietig", face_amt=0.4,
       at=S.head(mama, t_g + 1.5), feet="keep")
S.beat(opa, t_g, "staan", face="verdrietig", face_amt=0.4, at=S.head(held, t_g))

# ---------------------------------------------------------------- 5h de jongen kijkt naar zijn telefoon
S.beat(held, t_h, "staan", arms=HOLD1, face="neutraal", face_amt=0.5, look=(0.0, -0.5), feet="keep")
S.beat(held, t_h + 2.4, "staan", arms=HOLD1, face="nerveus", face_amt=0.6, look=(0.0, -0.5), feet="keep")
S.beat(held, t_h + 4.3, "staan", arms=HOLD1, face="vastberaden", face_amt=0.4, look=(0.0, -0.35), feet="keep")
A.blink_at(held, F(t_h + 3.2), closed=5)
for ch in (papa, mama, bro, opa, held):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
HP = S.headpos(papa, 1.2)
HM = S.headpos(mama, 1.2)
MID = (HP + HM) / 2
S.cam(0.0, (MID + V(-1.0, -2.9, 0.0), MID + V(-0.1, 0, -0.3), 27), (MID + V(-0.85, -2.65, 0.0), MID + V(-0.1, 0, -0.3), 28),
      handheld=0.5)
S.cam(t_e, ((-0.45, -2.4, 1.25), (-0.05, 1.0, 0.8), 30), ((-0.35, -2.0, 1.2), (0.0, 0.9, 0.8), 32))
HO = S.headpos(opa, t_f + 1.5)
S.cam(t_f, (HO + V(-1.3, -1.95, -0.1), HO + V(0, 0, -0.2), 34), (HO + V(-1.2, -1.8, -0.1), HO + V(0, 0, -0.2), 35))
S.cam(t_g, ((-0.1, -2.75, 1.75), (0.1, 0.6, 0.85), 22), ((0.05, -2.65, 1.72), (0.1, 0.6, 0.85), 22))
HH = S.headpos(held, t_h + 2.0)
S.cam(t_h, (HH + V(0.75, -1.7, 0.0), HH + V(0, 0, -0.1), 32), (HH + V(0.55, -1.45, 0.0), HH + V(0, 0, -0.08), 33))

# ---------------------------------------------------------------- geluid
S.sfx("sfx_alarm_nucleair", 0.0, 0.3, keys=[(0.0, 0.3), (t_g, 0.3), (t_g + 0.3, 0.12), (END, 0.1)], loop_to=END)
S.sfx("sfx_deurklink", t_e - 0.05, 0.4)
S.sfx("sfx_vloer_kraak", t_e + 0.05, 0.35, cut=(0.0, 0.9))
S.say("N05-04", at=t_h + 0.2)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
