"""S23 · Dag 24 · de woestijnbasis. De wetenschapper rekent het voor (ontsnappingssnelheid, 11,2 km/s), hij probeert
te springen, en de grond geeft het op: hij zakt tot zijn middel in een krater van gruis. 'The planet is.'

    blender -b -P anim/scenes/s23_woestijnbasis.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s23", "woestijn", "basis_dag")

BOARD = V(13.0, 14.0, 0)
A_B = math.radians(20)
N_B = V(math.sin(A_B), -math.cos(A_B), 0)     # voorkant van het bord
T_B = V(math.cos(A_B), math.sin(A_B), 0)
CHAIR = BOARD + N_B * 2.8
PROF_AT = BOARD + T_B * 1.55 + N_B * 0.6
JUMP = V(0.0, 3.0, 0.0)
SINK = -0.92                                   # tot zijn middel in het gruis
RED = (1.0, 0.25, 0.2, 1)

# ---------------------------------------------------------------- whiteboard, stoel
wbo = S.obj("Whiteboard_formules")
ev = T.text("Formule_ontsnapping", "ESCAPE: 11.2 km/s", (0, -0.035, 1.08), 0.13, S.mat("stift_rood", (0.85, 0.12, 0.1)), extrude=0.002)
ev.parent = wbo
rot_hero = heading(CHAIR, BOARD)
I.chair("Klapstoel", tuple(CHAIR), rot=rot_hero, color=(0.30, 0.32, 0.28))

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", CHAIR, rot_hero)
prof = S.actor("wetenschapper", PROF_AT, heading(PROF_AT, CHAIR), energy=1.3)
LABCOAT = dict(shirt=(0.95, 0.95, 0.93), broek=(0.30, 0.32, 0.40))
helpers = [S.actor("wetenschapper", BOARD + N_B * 1.6 + T_B * (-2.0 - k * 0.9), heading(BOARD + N_B * 1.6 + T_B * (-2.0 - k * 0.9), CHAIR),
                   energy=0.7, label=f"onderzoeker_{k}", outfit=dict(LABCOAT, haar=((0.15, 0.1, 0.07), (0.7, 0.55, 0.3))[k]), drop=("bril",))
           for k in range(2)]
SIT_H, zh = sit(held, seat_top=0.46, lean=-2)
S.place(held, 0, CHAIR + V(0, 0, zh), rot_hero)

# ---------------------------------------------------------------- tijdlijn
S.hud(24, "16,777,216x STRONGER", t0=0.4)
S.ambience("sfx_wind_hoog", 0.0, 80, vol=0.08)
S.music("woestijn", 0.0, 0, vol=0.24, fade_in=1.0, fade_out=0.8)
DESERT = S.sounds[-1]
l1 = S.say("S23-01", gap=0.7)
BASE = l1[0] + 3.86
NOBODY = l1[0] + 6.63
l2 = S.say("S23-02", gap=0.6)
l3 = S.say("S23-03", who=prof, gap=0.4, gain=1.15)
ELEVEN = l3[0] + 2.2                           # 'eleven point two kilometers per second'
TODAY = l3[0] + 4.85                           # 'Based on your strength... you could jump that today.'
l4 = S.say("S23-04", gap=1.1)
TRY = l4[0]
KNEES = l4[0] + 1.21
PUSH = l4[0] + 2.32
l5 = S.say("S23-05", gap=0.5)
GIVES = l5[0] + 1.64                           # 'gives up.'
CRUSH = l5[0] + 1.75
l6 = S.say("S23-06", gap=1.6)
GRANITE = l6[0] + 1.62
LEGS = l6[0] + 6.05
PLANET = l6[0] + 10.04                         # 'The planet is.'
l7 = S.say("S23-07", gap=1.2)
CLIMB = l7[0]
STRONGEST = l7[0] + 2.11
CANT = l7[0] + 4.56
S.wait(1.6)
END = S.t
DESERT["loop_to"] = KNEES - 0.6
S.music("drums_build", KNEES - 1.2, CRUSH, vol=0.26, fade_in=0.4, fade_out=0.08)
S.music("subbas", CRUSH, END + 0.3, vol=0.24, fade_in=0.05, fade_out=1.5)
S.music("drone", l6[0] + 0.5, END + 0.3, vol=0.18, fade_in=2.0, fade_out=1.5)
S.sfx("sfx_grond_kruimelt", CRUSH - 0.05, 0.35)
S.sfx("sfx_inslag", CRUSH, 0.3)
S.sfx("sfx_zand_opstijgen", CRUSH + 0.2, 0.22)

S.text("NEAREST TOWN: 200 KM", NOBODY + 0.3, l1[1] + 0.5, loc=(0.965, 0.22), size=52, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.gauge("ESCAPE VELOCITY: 11.2 KM/S", ELEVEN + 0.4, l3[1] + 0.4, color=WHITE)
S.text("YOUR JUMP: ENOUGH", TODAY + 1.2, l3[1] + 0.4, loc=(0.035, 0.68), size=56, color=GOLD, anchor=("LEFT", "TOP"))
S.real(l6[0] + 0.1, l6[1] + 0.2)
S.text("GRANITE CRUMBLES AT ~200 MPa", GRANITE + 0.3, LEGS - 0.1, loc=(0.965, 0.22), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOUR PUSH: THOUSANDS OF TIMES MORE", GRANITE + 2.0, LEGS - 0.1, loc=(0.965, 0.14), size=50, color=RED, anchor=("RIGHT", "BOTTOM"))
S.text("THE LIMIT: THE PLANET", PLANET + 0.2, l6[1] + 0.8, loc=(0.5, 0.16), size=90, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.gauge("STRONGEST THING EVER: YOU", STRONGEST + 0.2, CANT - 0.1, color=GOLD)
S.gauge("JUMP HEIGHT: 0 CM", CANT + 0.4, END, color=RED)

# ---------------------------------------------------------------- het bord: hij zit, de wetenschapper rekent
show(ev, ELEVEN)
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.6, at=BOARD + V(0, 0, 1.7))
S.beat(held, l3[0] + 0.3, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.7, at=S.head(prof, l3[0]))
S.beat(held, ELEVEN + 0.3, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.5, at=BOARD + V(0, 0, 1.2))
S.beat(held, TODAY + 0.4, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.8, at=S.head(prof, TODAY), wenkbrauw_op=0.6)
S.beat(held, l3[1] + 0.2, **SIT_H, pose="ontspannen", face="grijns", face_amt=0.4, at=S.head(prof, TODAY))
S.hold(held, l3[1] + 0.9)
S.beat(prof, 0.0, "staan", face="blij", face_amt=0.6, at=S.head(held, 0))
S.beat(prof, l3[0] + 0.1, "wijzen", face="lach", face_amt=0.6, at=BOARD + V(0, 0, 1.5), body={"chest": (0, 25, 0)})
S.beat(prof, ELEVEN, "wijzen", face="verbaasd", face_amt=0.7, at=BOARD + V(0, 0, 1.2), body={"chest": (0, 30, 0)})
S.beat(prof, TODAY - 0.2, "handen_zij", face="lach", face_amt=0.9, at=S.head(held, TODAY), wenkbrauw_op=0.8)
S.beat(prof, l3[1] - 0.5, "handen_zij", amount=0.6, face="blij", face_amt=1.0, at=S.head(held, TODAY))
S.hold(prof, l3[1] + 0.9)
for k, ch in enumerate(helpers):
    S.beat(ch, 0.0, "armen_over" if k else "staan", face="neutraal", face_amt=0.7, at=BOARD + V(0, 0, 1.5))
    S.beat(ch, TODAY + 0.3, "armen_over" if k else "staan", face="verbaasd", face_amt=0.6, at=S.head(held, TODAY))
    S.hold(ch, l3[1] + 0.9)

# ---------------------------------------------------------------- de sprong: knieën, duwen, de grond geeft het op
CUT = l4[0] - 0.4
S.teleport(held, CUT, JUMP, 180)
OBS = [(prof, V(-2.0, -7.0, 0)), (helpers[0], V(1.6, -7.2, 0)), (helpers[1], V(3.4, -7.0, 0))]
for ch, p in OBS:
    S.teleport(ch, CUT, p, heading(p, JUMP))
    S.beat(ch, CUT, "staan", face="nerveus", face_amt=0.7, at=JUMP + V(0, 0, 1.4))
    S.beat(ch, CRUSH + 0.3, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, at=JUMP + V(0, 0, 0.6))
    S.beat(ch, l6[0] + 1.0, "handen_hoofd" if ch is prof else "staan", amount=0.6, face="verbaasd", face_amt=0.9, at=JUMP + V(0, 0, 0.6))
    S.hold(ch, END)
S.beat(held, CUT, "staan", face="vastberaden", face_amt=0.6, look=(0, 0.6), body={"head": (-18, 0, 0)})
S.beat(held, TRY + 0.6, "staan", face="grijns", face_amt=0.5, look=(0, 0.7), body={"head": (-24, 0, 0)})
S.beat(held, KNEES + 0.1, "schrap", crouch=(0.42, 26), feet=((0.2, 0.0, 0), (-0.2, 0.0, 0)), face="inspanning", face_amt=0.8,
       look=(0, 0.4), body={"head": (-20, 0, 0)}, arms=arms(arm("L", (0.3, -0.6, -0.75), (0.2, -0.5, -0.8)), arm("R", (0.3, -0.6, -0.75), (0.2, -0.5, -0.8))))
S.hold(held, PUSH - 0.05)
S.beat(held, PUSH + 0.15, "armen_omhoog", amount=0.9, crouch=(0.05, -6), face="inspanning", face_amt=1.0, mouth=0.5, look=(0, 0.8),
       body={"head": (-24, 0, 0)})
S.hold(held, CRUSH - 0.05)
S.beat(held, CRUSH + 0.25, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, -0.6), body={"head": (16, 0, 0)})
# zakken: de wortel gaat onder het zand (het zandvlak verbergt zijn benen)
key(held.rig, CRUSH - 0.02, loc=JUMP)
key(held.rig, CRUSH + 0.18, loc=JUMP + V(0, 0, SINK - 0.08))
key(held.rig, CRUSH + 0.4, loc=JUMP + V(0, 0, SINK))
S.beat(held, l6[0] + 0.2, "staan", face="verbaasd", face_amt=0.8, look=(0, -0.6), body={"head": (20, 0, 0)},
       arms=arms(arm("L", (0.7, 0.2, -0.6), (0.8, 0.4, -0.3)), arm("R", (0.7, 0.2, -0.6), (0.8, 0.4, -0.3))))
S.beat(held, LEGS + 0.2, "staan", face="verdrietig", face_amt=0.6, look=(0, 0.2), body={"head": (-4, 0, 0)},
       arms=arms(arm("L", (0.7, 0.2, -0.6), (0.8, 0.4, -0.3)), arm("R", (0.7, 0.2, -0.6), (0.8, 0.4, -0.3))))
S.beat(held, PLANET - 0.6, "staan", face="neutraal", face_amt=0.7, look=(0, 0.6), body={"head": (-20, 0, 0)})
S.hold(held, CLIMB)
# eruit klimmen, op de rand zitten
RIM = JUMP + V(0, -1.95, 0)
for side, dx in (("L", 0.35), ("R", -0.35)):
    S.reach(held, CLIMB, side, None, inf=0.0)
    S.reach(held, CLIMB + 0.4, side, RIM + V(dx, 0.2, 0.25), inf=1.0)
    S.reach(held, CLIMB + 1.3, side, RIM + V(dx, 0.2, 0.25), inf=1.0)
    S.reach(held, CLIMB + 1.6, side, None, inf=0.0)
S.beat(held, CLIMB + 0.4, "staan", crouch=(0.1, 25), face="inspanning", face_amt=0.4, look=(0, -0.3))
key(held.rig, CLIMB + 0.4, loc=JUMP + V(0, 0, SINK), rot=(0, 0, 180))
key(held.rig, CLIMB + 1.3, loc=JUMP + V(0, -1.3, -0.3), rot=(0, 0, 180))
SIT_R, zr = sit(held, seat_top=0.18, lean=6, spread=0.25)
S.place(held, CLIMB + 1.9, RIM + V(0, -0.1, zr), 0)
S.beat(held, CLIMB + 1.9, **SIT_R, pose="ontspannen", face="verdrietig", face_amt=0.6, look=(0, -0.5), body={"head": (14, 0, 0)})
S.beat(held, STRONGEST + 0.4, **SIT_R, pose="ontspannen", face="verdrietig", face_amt=0.7, arms=LOOK_HANDS, look=(0, -0.6), body={"head": (18, 0, 0)})
S.beat(held, CANT + 0.3, **SIT_R, pose="ontspannen", face="verdrietig", face_amt=0.9, look=(0.2, 0.7), body={"head": (-18, 0, 0)}, mond_verdrietig=0.7)
S.hold(held, END)

# de krater: donker gruis, een opgeworpen rand, stof en brokken
grit = S.mat("gruis", (0.48, 0.38, 0.28))
crater = T.cyl("Krater_gruis", tuple(JUMP + V(0, 0, 0.004)), 1.0, 0.01, grit, seg=40, ol=0)
key(crater, CRUSH - 1 / FPS, scale=(0.001, 0.001, 1))
key(crater, CRUSH + 0.25, scale=(1.75, 1.75, 1))
rim = T.torus("Krater_rand", tuple(JUMP), 1.85, 0.32, S.mat("kraterrand", (0.78, 0.60, 0.40)), seg=40, seg2=10, ol=0.02)
key(rim, CRUSH - 1 / FPS, scale=(0.001, 0.001, 0.001))
key(rim, CRUSH + 0.3, scale=(1.0, 1.0, 0.55))
S.ring(JUMP + V(0, 0, 0.1), CRUSH, r0=0.4, r1=12.0, dur=0.7, color=(1.0, 0.92, 0.75), strength=2.0, thick=0.08)
S.puff(JUMP + V(0, 0, 0.2), CRUSH, n=14, r=(0.5, 1.1), grow=3.0, dur=3.0, color=(0.90, 0.75, 0.52), rise=1.8, spread=2.2)
S.debris(JUMP + V(0, 0, 0.1), CRUSH, n=50, size=(0.04, 0.14), color=(0.65, 0.50, 0.35), speed=(3.0, 8.0), up=1.4, floor=0.0, life=2.0)
S.puff(JUMP + V(0, 0, 0.3), CLIMB + 0.5, n=5, r=(0.2, 0.4), grow=2.0, dur=1.6, color=(0.90, 0.75, 0.52), rise=0.6, spread=1.0)

# ---------------------------------------------------------------- camera
# 1 · de basis van boven, dan heel hoog: niemand in de buurt
S.cam(0.0, ((-38, -38, 9), (10, 20, 2), 24), ((-34, -36, 10), (10, 20, 2), 26))
S.cam(NOBODY - 0.2, ((0, -60, 30), (8, 20, 0), 24), ((0, -140, 130), (8, 20, 0), 24))
# 2 · het bord
S.cam(l2[0] - 0.2, (CHAIR + N_B * 2.2 + T_B * 1.2 + V(0, 0, 1.55), BOARD + V(0, 0, 1.45), 28),
      (CHAIR + N_B * 1.9 + T_B * 1.0 + V(0, 0, 1.5), BOARD + V(0, 0, 1.45), 30))
S.cam(l3[0] - 0.1, S.shot(prof, l3[0] + 1.0, "med", az=-25, lens=32), S.shot(prof, ELEVEN, "mcu", az=-22, lens=34))
S.cam(ELEVEN + 0.4, (BOARD + N_B * 1.3 + T_B * 0.3 + V(0, 0, 1.35), BOARD + V(0, 0, 1.25) - N_B * 0.03, 34),
      (BOARD + N_B * 1.1 + T_B * 0.25 + V(0, 0, 1.3), BOARD + V(0, 0, 1.2) - N_B * 0.03, 38))
S.cam(TODAY - 0.1, S.shot(held, TODAY, "mcu", az=-38, lens=34), S.shot(held, l3[1] + 0.6, "mcu", az=-34, lens=38))
# 3 · de sprong: laag en breed, de waarnemers achter de zandzakken
S.cam(CUT, ((5.5, -4.5, 1.0), (0, 3, 1.4), 26), ((5.0, -4.0, 1.0), (0, 3, 1.3), 28))
S.cam(KNEES - 0.1, ((0.9, 0.6, 0.55), (0, 3, 0.9), 26), ((0.8, 0.8, 0.5), (0, 3, 0.85), 28))
S.cam(PUSH - 0.05, ((0.0, -4.0, 0.7), (0, 3, 1.6), 22), ((0.0, -4.2, 0.6), (0, 3, 1.6), 22),
      shake=lambda t: max(0.0, 2.5 - (t - CRUSH) * 1.5) if t > CRUSH else 0.0)
# 4 · 'Even solid granite...' hij tot zijn middel in de krater
S.cam(l6[0] - 0.3, ((4.5, -2.0, 1.6), (0, 3, 0.2), 26), ((4.0, -1.6, 1.5), (0, 3, 0.2), 28))
S.cam(LEGS - 0.2, ((0.9, 4.7, 0.7), (0, 3, 0.55), 32), ((0.8, 4.55, 0.68), (0, 3, 0.55), 36))      # hij kijkt naar +y
S.cam(PLANET - 0.6, ((0.0, 2.4, 6.0), (0, 3, 0), 24), ((0.0, -10, 90), (0, 3, 0), 24))
# 5 · eruit klimmen, op de rand
S.cam(CLIMB - 0.1, ((3.5, -3.0, 1.0), (0, 1.8, 0.4), 28), ((3.2, -2.8, 1.0), (0, 1.5, 0.4), 30))
S.cam(STRONGEST - 0.1, S.shot(held, STRONGEST + 0.3, "mcu", az=20, lens=32), S.shot(held, CANT - 0.2, "mcu", az=18, lens=36))
S.cam(CANT - 0.1, ((-7.0, -9.0, 2.2), (0, 1.0, 0.4), 30), ((-7.5, -10.0, 2.6), (0, 1.0, 0.4), 30))

S.finish(length=END)
