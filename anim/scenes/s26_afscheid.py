"""S26 · Dag 35 · afscheid van het gezin. De woestijnbasis in de schemering: hij zit alleen, vijftig meter buiten de
zandzakken, en hoort zijn eigen hart. Het gezin komt op bezoek (achter de zandzakken), het broertje roept, opa zegt dat
zwaaien mag. Mama zet de gelijmde mok op de paal halverwege en loopt terug. Hij pakt hem op. Hij breekt niet.

    blender -b -P anim/scenes/s26_afscheid.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s26", "woestijn", "basis_schemer")

WALL_Y = -6.0                                  # zandzakken (x -12..12), het gezin erachter
POST = V(2.5, -31.0, 0.0)                      # paal halverwege
POST_TOP = POST + V(0, 0, 1.6)
SEAT = V(2.5, -56.5, 0.0)                      # zijn kist, vijftig meter van de zandzakken
FACE_BASE = 180                                # rot 180 = kijkt naar +y (de basis)

# ---------------------------------------------------------------- set: paal verzetten, gat in het hek, zijn plekje
S.obj("Hekpaal_halverwege").location = tuple(POST)
for n in ("Hekdraad_1", "Hekdraad_2"):
    S.obj(n).hide_render = True
metaal = S.mat("hek_metaal", (0.55, 0.56, 0.58))
for z in (0.6, 1.2):
    T.tube(f"Hekdraad_w_{z}", [(-30, -12, z), (2.0, -12, z)], 0.012, metaal)
    T.tube(f"Hekdraad_o_{z}", [(6.0, -12, z), (30, -12, z)], 0.012, metaal)
hout = S.mat("kist_hout", (0.45, 0.33, 0.2))
T.box("Kist_held", tuple(SEAT), (0.7, 0.5, 0.42), hout, bevel=0.02, ol=0.015)
T.box("Kist_broertje", (9.9, -4.95, 0), (0.6, 0.45, 0.32), hout, bevel=0.02, ol=0.015)
T.cyl("Lantaarn_held", tuple(SEAT + V(0.9, 0.3, 0)), 0.07, 0.24, S.mat("lantaarn", (1.0, 0.8, 0.45), 4.0), seg=12, ol=0.01)
T.point_light("Lantaarn_licht", tuple(SEAT + V(0.9, 0.3, 0.35)), color=(1.0, 0.75, 0.45), energy=60, radius=0.1)
mug = prop_mug(S, "Mok_gelijmd", POST_TOP, handle=False, cracked=True)

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", SEAT, FACE_BASE)
SIT_H, zh = sit(held, seat_top=0.42, lean=14, spread=0.2)
S.place(held, 0.0, SEAT + V(0, 0.08, zh), FACE_BASE)
FAM = dict(opa=V(6.1, -4.9, 0), oma=V(7.0, -4.85, 0), papa=V(8.0, -4.95, 0), mama=V(8.95, -4.9, 0), broertje=V(9.9, -4.95, 0.32))
fam = {}
for k, (name, p) in enumerate(FAM.items()):
    fam[name] = S.actor(name, V(p.x, p.y + 60, p.z), heading(p, SEAT), energy=0.9)
mama, papa, bro, opa, oma = fam["mama"], fam["papa"], fam["broertje"], fam["opa"], fam["oma"]

# ---------------------------------------------------------------- tijdlijn
S.hud(35, "34,359,738,368x STRONGER", t0=0.5)
S.ambience("sfx_wind_hoog", 0.0, 90, vol=0.06)
S.music("piano_zacht", 0.4, 0, vol=0.18, fade_in=2.0, fade_out=1.6)
PIANO = S.sounds[-1]
l1 = S.say("S26-01", gap=0.9)
l2 = S.say("S26-02", gap=0.7)
HEART = l2[0] + 4.61                           # 'Your own heart.'
l3 = S.say("S26-03", gap=0.6)
STRONGER = l3[0] + 3.71                        # 'And every night it gets stronger.'
SOFAR = l3[0] + 8.11                           # 'So far.'
l4 = S.say("S26-04", gap=1.0)
VISIT = l4[0]
SANDBAGS = l4[0] + 4.3
l5 = S.say("S26-05", who=bro, gap=0.5, gain=1.0)
l6 = S.say("S26-06", gap=0.7)
l7 = S.say("S26-07", who=opa, gap=0.5, gain=1.0)
l8 = S.say("S26-08", gap=0.5)
WAVE = l8[0] + 0.2
WAVE_BACK = l8[0] + 2.68                       # 'And all five of them wave back.'
l9 = S.say("S26-09", who=mama, gap=1.0, gain=1.0)
l10 = S.say("S26-10", gap=3.4)
PLACE = l10[0] + 1.0                           # 'The mug.'
CRACK = l10[0] + 3.06                          # 'The crack still running right through the middle.'
l11 = S.say("S26-11", who=mama, gap=0.8, gain=1.0)
TOO = l11[0] + 3.92                            # 'You don't have to hold this together too.'
l12 = S.say("S26-12", gap=1.4)
PICK = l12[0] + 0.2                            # 'You pick up the mug.'
GRAB = l12[0] + 1.6
LIFTED = l12[0] + 5.3
NOBREAK = l12[0] + 5.61                        # 'It doesn't break.'
l13 = S.say("S26-13", gap=1.0)
EGGS, MUGS, DAYS, TIRED = l13[0], l13[0] + 1.56, l13[0] + 3.23, l13[0] + 6.14
S.wait(2.6)
END = S.t

# muziek: piano, bijna stil onder de vraag van het broertje, de mok in strijkers (geen speeldoos)
PIANO["loop_to"] = l9[0] + 0.5
PIANO["keys"] = [(l5[0] - 0.4, 0.18), (l5[0] - 0.1, 0.06), (l6[1], 0.06), (l7[1] + 0.2, 0.18)]
S.music("strijkers_emo", l9[0] + 0.2, END + 0.6, vol=0.2, fade_in=2.0, fade_out=2.0)
# het hart: alleen in de stiltes, nooit boven de stem
S.sfx("sfx_hartslag", l2[0] + 2.62, vol=0.42, loop_to=l3[1] + 0.4)
S.sfx("sfx_hartslag", TIRED + 1.2, vol=0.22, loop_to=END)

S.gauge("♥ HEART: STRONGER EVERY NIGHT", STRONGER, SOFAR + 1.0, color=RED)
S.text("50 M", SANDBAGS - 0.4, l4[1] + 0.8, loc=(0.965, 0.22), size=60, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("EGGS BROKEN: 0", EGGS, END, loc=(0.035, 0.76), size=58, color=WHITE)
S.text("MUGS BROKEN: 0", MUGS, END, loc=(0.035, 0.69), size=58, color=WHITE)
S.text("DAYS OF BEING CAREFUL: 35", DAYS, END, loc=(0.035, 0.62), size=58, color=GOLD)

# ---------------------------------------------------------------- hij: alleen op zijn kist
ARMS_KNEES = arms(arm("L", (0.25, 0.6, -0.75), (-0.2, 0.9, -0.1)), arm("R", (0.25, 0.6, -0.75), (-0.2, 0.9, -0.1)))
HAND_CHEST = arm("L", (0.3, 0.5, -0.75), (-0.75, 0.55, 0.35))
S.beat(held, 0.0, **SIT_H, face="verdrietig", face_amt=0.4, look=(0, -0.4), body={"head": (16, 0, 0)}, arms=ARMS_KNEES)
S.beat(held, l2[0] + 2.3, **SIT_H, face="neutraal", face_amt=0.6, look=(0, -0.2), body={"head": (6, 0, 0)}, arms=ARMS_KNEES)
S.beat(held, HEART - 0.3, **SIT_H, face="nerveus", face_amt=0.5, look=(0, -0.5), body={"head": (18, 0, 0)}, arms=HAND_CHEST)
S.beat(held, SOFAR, **SIT_H, face="bang", face_amt=0.45, look=(0, -0.5), body={"head": (16, 0, 0)}, arms=HAND_CHEST)
S.beat(held, VISIT + 0.5, **SIT_H, face="verbaasd", face_amt=0.5, look=(0, 0.2), body={"head": (-4, 0, 0)}, arms=ARMS_KNEES)
# hij staat op als ze er zijn
S.teleport(held, SANDBAGS + 0.2, SEAT + V(0, 0.6, 0), FACE_BASE)
S.beat(held, SANDBAGS + 0.2, "ontspannen", face="blij", face_amt=0.4, look=(0, 0.1), mond_verdrietig=0.3)
S.beat(held, l5[1] + 0.2, "ontspannen", face="verdrietig", face_amt=0.7, look=(0, -0.1), body={"head": (6, 0, 0)}, mond_verdrietig=0.5)
S.beat(held, l6[1], "ontspannen", face="verdrietig", face_amt=0.8, look=(0, -0.4), body={"head": (12, 0, 0)}, mond_verdrietig=0.6)
S.beat(held, l7[1] - 0.6, "ontspannen", face="verbaasd", face_amt=0.4, look=(0, 0.1), mond_verdrietig=0.2)
# het rare kleine zwaaitje
for k, t in enumerate(frange(WAVE, WAVE + 1.8, 0.32)):
    S.beat(held, t, "zwaaien_a" if k % 2 == 0 else "zwaaien_b", amount=0.45, face="blij", face_amt=0.35, look=(0, 0.1),
           mond_verdrietig=0.3, crouch=(0.03, 4))
S.beat(held, WAVE + 2.2, "ontspannen", face="lach", face_amt=0.4, look=(0, 0.1), mond_verdrietig=0.2)
S.beat(held, l9[0] + 0.6, "ontspannen", face="verbaasd", face_amt=0.4, look=(0.1, 0.1))
S.beat(held, l11[0] + 0.4, "ontspannen", face="verdrietig", face_amt=0.6, look=(0, 0.1), mond_verdrietig=0.5)
S.beat(held, TOO, "ontspannen", face="verdrietig", face_amt=0.9, look=(0, -0.1), mond_verdrietig=0.9, ogen_knijp=0.3)
S.hold(held, l11[1] + 0.5)
# naar de paal (op een snede) en de mok heel voorzichtig oppakken
STAND = POST + V(0, -0.62, 0)
S.teleport(held, l12[0] - 0.25, STAND + V(0, -1.6, 0), FACE_BASE)
S.walk(held, l12[0] - 0.25, PICK + 0.9, [STAND + V(0, -1.6, 0), STAND], stride=0.3, arms=0.15, end_rot=FACE_BASE)
S.beat(held, PICK + 0.9, "ontspannen", face="nerveus", face_amt=0.5, at=POST_TOP, feet="keep")
S.beat(held, GRAB, "ontspannen", crouch=(0.02, 10), face="inspanning", face_amt=0.25, at=POST_TOP, feet="keep", ogen_knijp=0.2)
S.reach(held, PICK + 0.9, "R", None, inf=0.0)
S.reach(held, GRAB - 0.3, "R", POST_TOP + V(0.03, -0.1, 0.07), inf=1.0)
S.reach(held, GRAB + 0.4, "R", POST_TOP + V(0.03, -0.1, 0.09), inf=1.0)
S.reach(held, LIFTED - 0.4, "R", STAND + V(-0.05, 0.3, 0.95), inf=1.0)
S.reach(held, LIFTED + 0.3, "R", None, inf=0.0)
CUP = arms(arm("L", (0.15, 0.6, -0.78), (-0.35, 0.9, 0.2)), arm("R", (0.15, 0.6, -0.78), (-0.35, 0.9, 0.2)))
S.beat(held, LIFTED + 0.3, "ontspannen", face="neutraal", face_amt=0.5, look=(0, -0.6), arms=CUP, body={"head": (16, 0, 0)}, feet="keep")
S.beat(held, NOBREAK + 0.3, "ontspannen", face="blij", face_amt=0.3, look=(0, -0.6), arms=CUP, body={"head": (18, 0, 0)},
       mond_verdrietig=0.4, feet="keep")
S.beat(held, TIRED - 0.3, "ontspannen", crouch=(0.06, 6), face="verdrietig", face_amt=0.6, look=(0, -0.6), arms=CUP,
       body={"head": (22, 0, 0), "spine": (8, 0, 0)}, ogen_knijp=0.5, mond_verdrietig=0.5, feet="keep")
S.beat(held, END - 0.4, "ontspannen", crouch=(0.07, 7), face="verdrietig", face_amt=0.7, look=(0, -0.6), arms=CUP,
       body={"head": (24, 0, 0), "spine": (10, 0, 0)}, ogen_knijp=0.6, mond_verdrietig=0.5, feet="keep")
grab(S, mug, held, GRAB, "hand.R", (0.04, 0.05, 0.05), (90, 0, 20))

# ---------------------------------------------------------------- het gezin achter de zandzakken
for name, ch in fam.items():
    p = FAM[name]
    S.teleport(ch, VISIT - 0.1, p, heading(p, SEAT))
    S.beat(ch, VISIT - 0.1, "staan", face="blij" if name != "mama" else "verdrietig", face_amt=0.4,
           at=S.head(held, SANDBAGS + 0.5) + V(0, 0, 0.6), feet="keep", arms=None)
# broertje roept, handen bij de mond (met zijn handen op de zandzakken)
S.beat(bro, l5[0] - 0.2, "staan", face="schreeuw", face_amt=0.7, at=S.head(held, l5[0]) + V(0, 0, 0.6), arms=arms(HAND_OUT_R, HAND_OUT_L))
S.beat(bro, l5[1] + 0.3, "staan", face="verdrietig", face_amt=0.5, at=S.head(held, l5[0]) + V(0, 0, 0.6))
S.beat(opa, l7[0] - 0.15, "wijzen", face="boos", face_amt=0.25, at=S.head(held, l7[0]) + V(0, 0, 0.6))
S.beat(opa, l7[1] + 0.1, "staan", face="blij", face_amt=0.5, at=S.head(held, l7[0]) + V(0, 0, 0.6))
S.beat(oma, l7[1], "staan", face="blij", face_amt=0.6, at=S.head(held, l7[0]) + V(0, 0, 0.6), arms=arm("R", (0.3, 0.5, 0.2), (-0.4, 0.4, 0.85)))
for n, (name, ch) in enumerate(fam.items()):
    t0 = WAVE_BACK + 0.08 * n
    for k, t in enumerate(frange(t0, t0 + 2.4, 0.34)):
        S.beat(ch, t, "zwaaien_a" if (k + n) % 2 == 0 else "zwaaien_b", amount=1.0 if name == "broertje" else 0.75,
               face="lach" if name in ("broertje", "opa") else "blij", face_amt=0.7, at=S.head(held, WAVE_BACK) + V(0, 0, 0.6))
    S.beat(ch, t0 + 2.7, "staan", face="blij" if name != "mama" else "verdrietig", face_amt=0.5,
           at=S.head(held, WAVE_BACK) + V(0, 0, 0.6))

# mama: met de mok om de zandzakken heen, naar de paal, zet hem neer en loopt terug
TRAY = arm("R", (0.15, 0.55, -0.8), (-0.2, 0.95, 0.2))
M0 = FAM["mama"]
M_AROUND = [M0, V(12.7, -4.9, 0), V(13.0, -7.2, 0), V(11.0, -8.6, 0)]
S.beat(mama, l9[0] - 0.4, "staan", face="verdrietig", face_amt=0.5, at=S.head(held, l9[0]) + V(0, 0, 0.6), arms=TRAY, feet="keep")
S.walk(mama, l9[0] + 0.3, l10[0] - 0.3, M_AROUND, stride=0.5, arms=None)
M_NEAR = POST + V(0.4, 3.0, 0)
M_AT = POST + V(0.0, 0.55, 0)
S.teleport(mama, l10[0] - 0.25, M_NEAR, heading(M_NEAR, M_AT))
S.walk(mama, l10[0] - 0.25, PLACE - 0.45, [M_NEAR, M_AT], stride=0.45, arms=None, end_rot=heading(M_AT, POST))
S.beat(mama, PLACE - 0.45, "staan", crouch=(0.04, 12), face="verdrietig", face_amt=0.5, at=POST_TOP, arms=HAND_OUT_R, feet="keep")
S.beat(mama, PLACE + 0.4, "staan", face="verdrietig", face_amt=0.6, at=POST_TOP, feet="keep")
S.beat(mama, CRACK, "staan", face="verdrietig", face_amt=0.6, at=S.head(held, l11[0]) + V(0, 0, 0.6), feet="keep")
S.beat(mama, l11[0] + 0.2, "staan", face="verdrietig", face_amt=0.85, at=S.head(held, l11[0]) + V(0, 0, 0.6), mond_verdrietig=0.8,
       arms=arm("L", (0.3, 0.5, -0.5), (-0.6, 0.5, 0.4)), feet="keep")
S.beat(mama, TOO, "staan", face="verdrietig", face_amt=1.0, at=S.head(held, l11[0]) + V(0, 0, 0.6), mond_verdrietig=1.0, ogen_knijp=0.4,
       feet="keep")
S.hold(mama, l11[1] + 0.3)
M_BACK = [M_AT, M_AT + V(1.5, 6.0, 0), V(4.0, -12.0, 0), V(4.4, -14.0, 0)]
S.walk(mama, l11[1] + 0.3, l11[1] + 6.0, M_BACK[:2], stride=0.4, arms=0.2)
S.teleport(mama, l12[0] - 0.25, M0, heading(M0, STAND))
S.beat(mama, l12[0] - 0.25, "staan", face="verdrietig", face_amt=0.6, at=S.head(held, GRAB) + V(0, 0, 0.6), arms=HAND_CHEST, feet="keep")
S.beat(mama, NOBREAK + 0.2, "staan", face="blij", face_amt=0.4, at=S.head(held, GRAB) + V(0, 0, 0.6), arms=HAND_CHEST,
       mond_verdrietig=0.6, feet="keep")
S.hold(mama, END)
grab(S, mug, mama, 0.0, "hand.R", (0, 0.05, 0.05), (90, 0, 0), release=PLACE)
for ch in (papa, bro, opa, oma):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
BASE_LOOK = V(8.0, -5.0, 1.0)
S.cam(0.0, ((-4.8, -64.8, 1.35), (3.4, -52.0, 1.7), 26), ((-4.2, -64.0, 1.35), (3.4, -52.0, 1.7), 28))
S.cam(l2[0] + 2.3, S.shot(held, HEART, "med", az=22, lens=32), S.shot(held, HEART, "mcu", az=18, lens=34))
S.cam(STRONGER - 0.2, S.shot(held, STRONGER, "mcu", az=-35, lens=34), S.shot(held, SOFAR, "mcu", az=-30, lens=37))
S.cam(VISIT - 0.1, ((1.4, -58.6, 1.55), BASE_LOOK, 110), ((1.45, -58.4, 1.55), BASE_LOOK + V(0, 0, 0.1), 120))
S.cam(SANDBAGS - 0.1, ((8.4, -11.5, 1.35), (8.0, -4.9, 1.05), 28), ((8.3, -11.0, 1.35), (8.0, -4.9, 1.05), 30))
S.cam(l5[0] - 0.15, S.shot(bro, l5[0] + 0.5, "med", az=35, lens=32), S.shot(bro, l5[0] + 1.5, "med", az=32, lens=35))
S.cam(l6[0] - 0.1, S.shot(held, l6[0] + 1.0, "mcu", az=20, lens=34), S.shot(held, l6[1], "mcu", az=18, lens=38))
S.cam(l7[0] - 0.1, S.shot(opa, l7[0] + 0.5, "med", az=-15, lens=30), S.shot(opa, l7[1], "med", az=-12, lens=33))
S.cam(WAVE - 0.15, S.shot(held, WAVE + 0.5, "full", az=12, lens=30), S.shot(held, WAVE + 1.5, "full", az=10, lens=32))
S.cam(WAVE_BACK - 0.1, ((7.9, -13.0, 1.4), (7.9, -4.9, 1.15), 26), ((7.9, -12.4, 1.4), (7.9, -4.9, 1.15), 28))
S.cam(l9[0] - 0.15, S.shot(mama, l9[0] + 0.5, "med", az=15, lens=32), ((15.5, -14.0, 1.9), (11.5, -6.5, 1.0), 26))
S.cam(l10[0] - 0.3, ((9.0, -35.5, 1.5), (2.4, -30.4, 1.1), 30), ((8.5, -35.0, 1.5), (2.4, -30.4, 1.1), 32))
# de mok op de paal en mama erachter, schuin van opzij zodat haar hoofd naast de mok staat
MID = (POST_TOP + V(0, 0, 0.07) + S.head(mama, PLACE + 1.0)) * 0.5
S.cam(PLACE + 0.25, (MID + V(-1.15, -1.15, 0.05), MID, 32), (MID + V(-1.0, -1.0, 0.04), MID, 35))
S.cam(l11[0] - 0.15, S.shot(mama, l11[0] + 0.5, "mcu", az=72, lens=34), S.shot(mama, TOO, "mcu", az=70, lens=38))
S.cam(TOO + 0.2, S.shot(held, TOO + 0.6, "mcu", az=-20, lens=34), S.shot(held, l11[1], "mcu", az=-18, lens=38))
S.cam(l12[0] - 0.25, ((-0.7, -33.6, 1.35), (2.5, -31.7, 1.15), 28), ((-0.55, -33.4, 1.35), (2.5, -31.6, 1.2), 30))
S.cam(GRAB - 0.5, (POST_TOP + V(1.05, 0.45, 0.0), POST_TOP + V(0, -0.25, -0.05), 36),
      (POST_TOP + V(1.1, 0.35, -0.12), POST_TOP + V(0, -0.4, -0.2), 34))
S.cam(NOBREAK - 0.15, S.shot(held, NOBREAK + 0.5, "mcu", az=58, lens=34, up=-0.1), S.shot(held, TIRED, "mcu", az=55, lens=37, up=-0.1))
S.cam(TIRED - 0.2, ((0.4, -36.5, 1.9), (3.6, -22.0, 1.1), 24), ((0.6, -35.8, 2.1), (3.6, -22.0, 1.2), 26))

S.finish(length=END)
