"""S14 · Dag 13 · huisartsenpraktijk: de naald buigt, de tweede knapt. Niemand kan er nog in.

    blender -b -P anim/scenes/s14_dokter.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s14", "kleine_interieurs", "dokter")

TABLE = V(-0.85, 0.5, 0)                        # op de rand van de onderzoekstafel, kijkt naar +x
NURSE_AT = V(-0.02, 0.62, 0)
MOM_AT = V(0.45, -0.55, 0)
held = S.actor("hoofdpersonage", TABLE, 90)
nurse = S.actor("nieuwslezeres", NURSE_AT, -90, energy=1.0, label="verpleegster", drop=("microfoon", "oorbel"),
                outfit=dict(shirt=(0.55, 0.82, 0.85), broek=(0.55, 0.82, 0.85), haar=(0.30, 0.18, 0.10)))
mama = S.actor("mama", MOM_AT, heading(MOM_AT, TABLE), energy=0.9)
SIT, zh = sit(held, seat_top=0.83, lean=-4)
S.place(held, 0, (TABLE.x, TABLE.y, zh), 90)

# de kromme naalden in het bakje liggen er pas aan het eind
bent_tray = [o for o in bpy.data.objects if o.name.startswith("Kromme_naald")]

# ---------------------------------------------------------------- spuiten
def syringe(name):
    body = T.cyl(name, (0, 0, 0), 0.011, 0.085, S.mat("spuit", (0.92, 0.95, 0.98)), seg=12, ol=0.0015)
    T.cyl(name + "_vloeistof", (0, 0, 0.01), 0.0095, 0.03, S.mat("spuit_vocht", (0.85, 0.3, 0.3)), seg=10, ol=0).parent = body
    T.cyl(name + "_zuiger", (0, 0, -0.03), 0.004, 0.035, S.mat("spuit_zuiger", (0.25, 0.25, 0.3)), seg=8, ol=0.001).parent = body
    straight = T.cyl(name + "_naald", (0, 0, 0.085), 0.0016, 0.055, P.m("metaal"), seg=6, ol=0.0008)
    straight.parent = body
    bent = T.to_mesh(T.tube(name + "_naald_krom", [(0, 0, 0.085), (0, 0, 0.11), (0.006, 0, 0.122), (0.03, 0, 0.128)], 0.0016, P.m("metaal")))
    bent.parent = body
    stub = T.cyl(name + "_naald_stomp", (0, 0, 0.085), 0.0016, 0.012, P.m("metaal"), seg=6, ol=0.0008)
    stub.parent = body
    return body, straight, bent, stub


sy1, n1, b1, s1 = syringe("Spuit_1")
sy2, n2, b2, s2 = syringe("Spuit_2")
for o in (sy1, sy2):
    attach(o, nurse, "hand.R", (0.0, 0.06, 0.03), (0, 0, 0))     # bot-assen: y = langs de vingers, z = voor

# ---------------------------------------------------------------- tijdlijn
S.hud(13, "8,192x STRONGER", t0=0.4)
S.music("klinisch", 0.0, 60, vol=0.24, fade_in=0.6, fade_out=0.8)
CLIN = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.06)
l1 = S.say("S14-01", gap=0.6)
l2 = S.say("S14-02", gap=0.4)
PUSH = l2[0] + 2.3                              # 'She pushes the needle in.'
BEND = l2[0] + 4.85                             # 'The needle bends.'
SWAP = l2[0] + 6.0                              # 'She tries another one.'
SNAP = l2[0] + 9.05                             # 'It snaps.'
S.sfx("sfx_metaal_buigt", BEND - 0.05, 0.35)
S.sfx("sfx_naald", SNAP - 0.03, 0.6)
l3 = S.say("S14-03", gap=0.6)
FABRIC = l3[0] + 1.7
X8K = l3[0] + 6.1
NOODLE = l3[0] + 9.2
l4 = S.say("S14-04", gap=0.6)
GOOD = l4[0] + 0.3
BAD = l4[0] + 3.7
CLIN["loop_to"] = BAD - 0.2
S.music("drone", BAD - 0.6, 60, vol=0.26, fade_in=1.0, fade_out=1.0)
S.wait(1.3)
END = S.t

S.real(l3[0] + 0.05, l3[1] + 0.2)
S.text("SKIN = COLLAGEN, WOVEN LIKE FABRIC", FABRIC, l3[1] + 0.2, loc=(0.965, 0.30), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("x 8,192", X8K, l3[1] + 0.2, loc=(0.965, 0.22), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("NEEDLE = COOKED NOODLE  vs  CAR TIRE", NOODLE, l3[1] + 0.2, loc=(0.965, 0.14), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("GOOD NEWS", GOOD, BAD - 0.2, loc=(0.035, 0.30), size=60, color=(0.45, 1.0, 0.5, 1), anchor=("LEFT", "BOTTOM"))
S.text("BAD NEWS", BAD, END, loc=(0.035, 0.30), size=60, color=(1.0, 0.35, 0.3, 1), anchor=("LEFT", "BOTTOM"))

# naald 1: recht -> krom; spuit 2: recht -> stompje (punt vliegt weg)
show(sy1, 0.0, SWAP)                           # (zet ook alle kinderen; daarna per naald bijstellen)
show(sy2, SWAP)
for o, on in ((n1, True), (b1, False), (s1, False), (n2, False), (b2, False), (s2, False)):
    visible(o, 0.0, on)
visible(n1, BEND, False)
visible(b1, BEND, True)
visible(b1, SWAP, False)
visible(n2, SWAP, True)
visible(b2, SWAP, False)
visible(s2, SWAP, False)
visible(n2, SNAP, False)
visible(s2, SNAP, True)
for o in bent_tray:
    show(o, GOOD - 0.2)

# ---------------------------------------------------------------- hij: arm uit, kijkt weg
ARM_OUT = arm("L", (0.3, 0.85, -0.42), (0.15, 0.98, -0.05))
S.beat(held, 0.0, **SIT, pose="ontspannen", face="nerveus", face_amt=0.5, at=S.head(nurse, 0))
S.beat(held, l1[0] + 3.0, **SIT, pose="ontspannen", face="nerveus", face_amt=0.7, at=S.head(nurse, 0) + V(0, -0.2, -0.45))
S.beat(held, PUSH - 1.0, **SIT, pose="ontspannen", face="bang", face_amt=0.6, look=(-0.6, 0.2), body={"head": (0, 0, 35)}, arms=ARM_OUT, ogen_knijp=0.9)
S.hold(held, BEND - 0.2)
S.beat(held, BEND + 0.2, **SIT, pose="ontspannen", face="verbaasd", face_amt=0.6, at=S.head(held, 0) + V(0.45, 0.25, -0.35), arms=ARM_OUT)
S.beat(held, SWAP + 0.4, **SIT, pose="ontspannen", face="bang", face_amt=0.5, look=(-0.6, 0.2), body={"head": (0, 0, 35)}, arms=ARM_OUT, ogen_knijp=0.9)
S.hold(held, SNAP - 0.1)
S.beat(held, SNAP + 0.2, **SIT, pose="ontspannen", face="verbaasd", face_amt=0.9, at=S.head(held, 0) + V(0.45, 0.25, -0.35), arms=ARM_OUT, wenkbrauw_op=0.8)
S.beat(held, l3[0] + 1.0, **SIT, pose="ontspannen", face="twijfel", face_amt=0.6, look=(0.2, -0.4))
S.beat(held, GOOD, **SIT, pose="ontspannen", face="grijns", face_amt=0.8, at=S.head(mama, GOOD))
S.beat(held, BAD + 0.4, **SIT, pose="ontspannen", face="nerveus", face_amt=0.6, look=(0.1, -0.3))
S.beat(held, l4[1] - 1.6, **SIT, pose="ontspannen", face="bang", face_amt=0.6, look=(0, -0.5), body={"head": (10, 0, 0)},
       arms=arms(arm("L", (0.1, 0.4, -0.9), (-0.6, 0.7, 0.2)), arm("R", (0.1, 0.4, -0.9), (-0.6, 0.7, 0.2))))
S.hold(held, END)

# ---------------------------------------------------------------- verpleegster
ARM_PT = S.head(held, 0) + V(0.45, 0.22, -0.38)   # binnenkant van zijn elleboog
S.beat(nurse, 0.0, "staan", face="blij", face_amt=0.6, at=S.head(held, 0), arms=HOLD_FRONT_R)
S.beat(nurse, l1[1], "staan", face="zelfverzekerd", face_amt=0.6, at=ARM_PT, arms=HOLD_FRONT_R)
S.reach(nurse, PUSH - 0.4, "R", ARM_PT + V(0.2, 0.0, 0.03))
S.reach(nurse, PUSH, "R", ARM_PT + V(0.16, 0.0, 0.02))
S.reach(nurse, PUSH + 1.6, "R", ARM_PT + V(0.12, 0.0, 0.02))
S.beat(nurse, PUSH, "staan", face="inspanning", face_amt=0.4, at=ARM_PT, crouch=(0.04, 10))
S.beat(nurse, BEND + 0.1, "staan", face="verbaasd", face_amt=0.9, at=ARM_PT + V(0.12, 0, 0.05), crouch=(0.04, 10))
S.reach(nurse, BEND + 0.5, "R", ARM_PT + V(0.28, -0.05, 0.12))
S.reach(nurse, SWAP + 0.3, "R", ARM_PT + V(0.2, 0.0, 0.03))
S.reach(nurse, SWAP + 1.4, "R", ARM_PT + V(0.15, 0.0, 0.02))
S.beat(nurse, SWAP + 0.3, "staan", face="vastberaden", face_amt=0.9, at=ARM_PT, crouch=(0.05, 12))
S.beat(nurse, SNAP - 0.6, "staan", face="inspanning", face_amt=0.8, at=ARM_PT, crouch=(0.06, 14))
S.beat(nurse, SNAP + 0.1, "schrik", amount=0.6, face="geschrokken", face_amt=1.0, at=ARM_PT)
S.reach(nurse, SNAP + 0.1, "R", None, 0.0)
S.beat(nurse, l3[0] + 1.0, "staan", face="verbaasd", face_amt=0.7, at=S.head(held, 0))
S.beat(nurse, l4[0] + 0.5, "armen_over", face="twijfel", face_amt=0.7, at=S.head(held, 0))
S.hold(nurse, END)
S.debris(ARM_PT + V(0.06, 0, 0.02), SNAP, n=1, size=(0.012, 0.016), color=(0.8, 0.82, 0.85), speed=(1.0, 1.4), up=1.5, floor=0.0, life=1.2, name="Naaldpunt")

# ---------------------------------------------------------------- mama
S.beat(mama, 0.0, "armen_over", face="neutraal", face_amt=0.5, at=S.head(held, 0))
S.beat(mama, BEND + 0.3, "armen_over", face="verbaasd", face_amt=0.8, at=ARM_PT, wenkbrauw_op=0.7)
S.beat(mama, SNAP + 0.3, "handen_hoofd", amount=0.5, face="geschrokken", face_amt=0.8, at=ARM_PT)
S.beat(mama, GOOD + 0.3, "staan", face="blij", face_amt=0.5, at=S.head(held, GOOD))
S.beat(mama, BAD + 0.6, "armen_over", face="verdrietig", face_amt=0.7, at=S.head(held, BAD))
S.hold(mama, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.9, -3.7, 1.6), (-0.6, 0.6, 1.0), 20), ((0.7, -3.2, 1.55), (-0.6, 0.6, 1.0), 22))
S.cam(l2[0] - 0.1, ((0.25, -1.3, 1.4), (-0.5, 0.6, 1.15), 30), ((0.2, -1.1, 1.38), (-0.5, 0.6, 1.15), 34))
S.cam(BEND - 0.35, (ARM_PT + V(0.12, -0.55, 0.22), ARM_PT + V(0.08, 0, 0), 45), (ARM_PT + V(0.1, -0.5, 0.2), ARM_PT + V(0.08, 0, 0), 50))
S.cam(SWAP - 0.1, S.shot(held, SWAP, "cu", az=-40, lens=34), S.shot(held, SNAP - 0.5, "cu", az=-36, lens=38))
S.cam(SNAP - 0.4, (ARM_PT + V(0.12, -0.55, 0.22), ARM_PT + V(0.08, 0, 0), 45), (ARM_PT + V(0.12, -0.6, 0.24), ARM_PT + V(0.08, 0, 0.02), 42),
      shake=lambda t: max(0.0, 0.6 - (t - SNAP) * 1.5) if t > SNAP else 0.0)
S.cam(l3[0] - 0.1, ((-0.1, -0.7, 1.45), S.head(held, 0) + V(0, 0, -0.15), 30), ((-0.15, -0.55, 1.45), S.head(held, 0) + V(0, 0, -0.15), 34))
S.cam(GOOD - 0.25, ((0.55, 1.15, 1.25), (0.55, 1.65, 0.93), 45), ((0.55, 1.2, 1.2), (0.55, 1.65, 0.93), 50))
S.cam(BAD - 0.1, S.shot(held, BAD, "cu", az=-40, lens=34), S.shot(held, END, "ecu", az=-35, lens=42))

S.finish(length=END)
