"""S27a · Dag 37 · de beste vriend komt naar de basis, loopt tot aan de zandzakken. 'So. Space, huh?' Hij houdt zijn
telefoon omhoog: 'Do it again. I wasn't recording.' Ze lachen allebei, tot het niet grappig meer is.

    blender -b -P anim/scenes/s27a_vriend.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s27a", "woestijn", "basis_dag")

SEAT = V(2.5, -56.5, 0.0)                      # zijn plekje, vijftig meter buiten de zandzakken (zie S26)
HERO_AT = SEAT + V(0, 0.6, 0)
FR_AT = V(2.5, -5.42, 0.0)                     # vlak achter de zandzakken
FACE_BASE = 180

# ---------------------------------------------------------------- set: dezelfde paal en zijn kist als in S26
S.obj("Hekpaal_halverwege").location = (2.5, -31.0, 0)
for n in ("Hekdraad_1", "Hekdraad_2"):
    S.obj(n).hide_render = True
metaal = S.mat("hek_metaal", (0.55, 0.56, 0.58))
for z in (0.6, 1.2):
    T.tube(f"Hekdraad_w_{z}", [(-30, -12, z), (2.0, -12, z)], 0.012, metaal)
    T.tube(f"Hekdraad_o_{z}", [(6.0, -12, z), (30, -12, z)], 0.012, metaal)
hout = S.mat("kist_hout", (0.45, 0.33, 0.2))
T.box("Kist_held", tuple(SEAT), (0.7, 0.5, 0.42), hout, bevel=0.02, ol=0.015)

held = S.actor("hoofdpersonage", HERO_AT, FACE_BASE)
F0 = V(-3.5, 6.0, 0)
vriend = S.actor("beste_vriend", F0, heading(F0, FR_AT), energy=1.2)
phone = prop_phone(S, "Telefoon_vriend")
attach(phone, vriend, "hand.L", (0, 0.02, 0.03), (90, 0, 180))

# ---------------------------------------------------------------- tijdlijn
S.hud(37, "137,438,953,472x STRONGER", t0=0.5)
S.ambience("sfx_wind_hoog", 0.0, 60, vol=0.07)
S.music("gitaar", 0.3, 0, vol=0.18, fade_in=1.5, fade_out=2.0)
GIT = S.sounds[-1]
l1 = S.say("S27-01", gap=0.8)
ARRIVE = l1[0] + 3.64                          # 'He walks right up to the sandbags.'
l2 = S.say("S27-02", who=vriend, gap=0.6, gain=1.0)
l3 = S.say("S27-03", gap=0.4)
l4 = S.say("S27-04", who=vriend, gap=0.4, gain=1.0)
AGAIN_END = l4[0] + 2.46
l5 = S.say("S27-05", gap=0.2)
S.wait(2.2)
END = S.t
GIT["loop_to"] = END + 0.4
S.text("DISTANCE: 50 M", ARRIVE + 0.3, l2[1] + 0.4, loc=(0.965, 0.22), size=54, color=WHITE, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- de vriend
S.walk(vriend, 0.0, ARRIVE + 0.4, [F0, V(0.5, -1.5, 0), FR_AT], stride=0.6, arms=0.6, end_rot=heading(FR_AT, HERO_AT))
ON_BAGS = arms(arm("L", (0.25, 0.75, -0.6), (0.0, 0.95, -0.3)), arm("R", (0.25, 0.75, -0.6), (0.0, 0.95, -0.3)))
HH = S.head(held, 0.0) + V(0, 0, 0.6)
S.beat(vriend, 0.0, "staan", face="neutraal", face_amt=0.6, at=HH, feet="keep", face_only=True)
S.beat(vriend, ARRIVE + 0.5, "staan", crouch=(0.04, 10), face="blij", face_amt=0.4, at=HH, arms=ON_BAGS)
S.beat(vriend, l2[0] - 0.1, "staan", crouch=(0.04, 10), face="grijns", face_amt=0.6, at=HH, arms=ON_BAGS, body={"head": (0, 0, 8)})
S.beat(vriend, l2[1] + 0.2, "staan", crouch=(0.04, 10), face="blij", face_amt=0.5, at=HH, arms=ON_BAGS)
S.beat(vriend, l3[0] + 0.3, "filmen", face="grijns", face_amt=0.6, at=HH)
S.beat(vriend, l4[0] + 0.1, "filmen", face="lach", face_amt=0.6, at=HH, body={"head": (-4, 0, 0)})
S.beat(vriend, AGAIN_END, "filmen", face="grijns", face_amt=0.9, at=HH)
S.beat(vriend, l5[0] + 0.1, "filmen", face="lach", face_amt=1.0, at=HH, body={"head": (-10, 0, 0), "chest": (-6, 0, 0)}, ogen_knijp=0.6)
S.beat(vriend, l5[0] + 1.1, "staan", face="lach", face_amt=0.7, at=HH, body={"head": (6, 0, 0)}, ogen_knijp=0.4)
S.beat(vriend, l5[1] + 0.4, "staan", face="verdrietig", face_amt=0.5, at=HH, mond_verdrietig=0.4)
S.beat(vriend, END - 0.3, "staan", face="verdrietig", face_amt=0.7, look=(0, -0.4), body={"head": (12, 0, 0)}, mond_verdrietig=0.6)
visible(phone, 0.0, False)
visible(phone, l3[0] + 0.2, True)

# ---------------------------------------------------------------- hij, vijftig meter verderop
S.beat(held, 0.0, "ontspannen", face="neutraal", face_amt=0.5, look=(0, -0.2), body={"head": (8, 0, 0)})
S.beat(held, ARRIVE, "ontspannen", face="verbaasd", face_amt=0.5, look=(0, 0.1))
S.beat(held, l2[1] + 0.1, "ontspannen", face="blij", face_amt=0.5, look=(0, 0.1))
S.beat(held, AGAIN_END - 0.3, "ontspannen", face="lach", face_amt=0.6, look=(0, 0.1))
S.beat(held, l5[0] + 0.1, "handen_zij", face="lach", face_amt=1.0, look=(0, 0.0), body={"head": (-12, 0, 0), "spine": (-6, 0, 0)}, ogen_knijp=0.7)
S.beat(held, l5[0] + 1.0, "ontspannen", face="lach", face_amt=0.8, look=(0, 0.0), body={"head": (10, 0, 0), "spine": (10, 0, 0)}, ogen_knijp=0.5)
S.beat(held, l5[1] + 0.3, "ontspannen", face="blij", face_amt=0.3, look=(0, 0.1), mond_verdrietig=0.5)
S.beat(held, END - 0.3, "ontspannen", face="verdrietig", face_amt=0.7, look=(0, -0.3), body={"head": (10, 0, 0)}, mond_verdrietig=0.7)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((6.5, -10.5, 1.5), (0.0, -1.0, 1.2), 28), ((6.2, -10.0, 1.5), (1.2, -3.0, 1.15), 30))
S.cam(ARRIVE - 0.1, S.shot(vriend, ARRIVE + 0.6, "med", az=10, lens=30), S.shot(vriend, l2[0], "med", az=8, lens=33))
S.cam(l2[1] + 0.05, S.shot(held, l2[1] + 0.4, "mcu", az=15, lens=34), S.shot(held, l2[1] + 1.4, "mcu", az=12, lens=37))
S.cam(l3[0] + 0.1, S.shot(vriend, l3[0] + 0.6, "mcu", az=20, lens=32), S.shot(vriend, l4[0] + 1.0, "mcu", az=16, lens=36))
S.cam(AGAIN_END + 0.05, ((1.6, -58.8, 1.6), (2.5, -5.4, 1.15), 110), ((1.65, -58.6, 1.6), (2.5, -5.4, 1.2), 125))
S.cam(l5[0] + 0.9, S.shot(held, l5[0] + 1.2, "med", az=18, lens=32), S.shot(held, l5[1], "mcu", az=14, lens=35))
S.cam(l5[1] + 0.2, S.shot(vriend, l5[1] + 0.6, "mcu", az=-18, lens=34), S.shot(vriend, END, "mcu", az=-15, lens=38))

S.finish(length=END)
