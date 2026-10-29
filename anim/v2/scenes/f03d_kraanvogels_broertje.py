"""F03d · Dag 1 · 1x · kamer van het broertje, 's avonds. Hij vouwt een kraanvogel die op een zielige duif lijkt.
Broertje: 'If you fold a thousand paper cranes, you get one wish.' VO: 'He's folded four...'

    blender -b -P anim/v2/scenes/f03d_kraanvogels_broertje.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f03d", "slaapkamer", "broertje")

DX, DY = 1.76, 0.25                          # bureau (lengte langs y)
CHAIR = V(DX - 0.62, DY - 0.05, 0)
BRO_AT = V(DX - 0.66, DY - 0.05, 0)
HERO_AT = V(1.35, -1.05, 0)                  # net binnen, bij de deur
DESK = V(DX - 0.22, DY - 0.02, 0.78)         # waar hij vouwt
CRANES = V(DX + 0.14, DY + 0.34, 0.8)        # de vier kraanvogels

# ---------------------------------------------------------------- figuren en rekwisieten
bro = S.actor("broertje_dino", BRO_AT, 90)
SIT_B, zb = sit(bro, seat_top=0.5)
S.place(bro, 0, BRO_AT + V(0, 0, zb), 90)
held = S.actor("hoofdpersonage", HERO_AT, heading(HERO_AT, BRO_AT))
duif = S.obj("Kraanvogel_zielige_duif")
SHOW_R = arm("R", (0.45, 0.6, -0.55), (0.55, 0.7, 0.45))       # de duif omhoog, naar zijn broer
paper = T.box("Vouwblaadje", (0, 0, 0), (0.15, 0.15, 0.004), S.mat("vouwblaadje", (0.95, 0.35, 0.45)), bevel=0, ol=0)

# ---------------------------------------------------------------- tijdlijn
S.hud2(1, "1x", clock=clock(19 * 3600 + 42 * 60, 1.0, hhmm=True, day="MON"), t0=0.3)
l1 = S.say("F03-12", gap=3.4, who=bro, gain=1.2)
l2 = S.say("F03-13", gap=0.5)
END = l2[1] + 0.8
S.music("piano_warm", 0.0, END + 1.5, vol=0.2, fade_in=0.8, fade_out=1.0, start=20.0)
S.sfx("sfx_papier_vouwen", 0.15, 0.35, cut=(0, 1.2))
S.sfx("sfx_papier_vouwen", l1[1] + 0.3, 0.25, cut=(2.0, 3.5))
A.lipsync(bro, voice_file("F03-12"), F(l1[0]), gain=1.2)

# ---------------------------------------------------------------- het broertje vouwt
grab(S, paper, bro, 0.0, "hand.R", loc=(0.0, 0.07, 0.02), rot=(90, 0, 0), release=l1[0] - 0.4)
S.beat(bro, 0.0, **SIT_B, pose="staan", face="inspanning", face_amt=0.5, at=DESK, body={"head": (14, 0, 0)})
t = 0.2
k = 0
while t < l1[0] - 0.6:                        # vouwen: handen naar elkaar, het blaadje draait
    S.reach(bro, t, "R", DESK + V(0, -0.04 + 0.03 * (k % 2), 0.06 + 0.02 * (k % 3)))
    S.reach(bro, t + 0.12, "L", DESK + V(0, 0.07 - 0.03 * (k % 2), 0.05))
    t += 0.45
    k += 1
# hij legt het blaadje neer, pakt de 'duif' en houdt hem omhoog naar zijn grote broer
paper_rest = DESK + V(0.05, -0.12, -0.02)
key(paper, l1[0] - 0.4, loc=paper_rest, rot=(0, 0, 20))
grab(S, duif, bro, l1[0] - 0.2, "hand.R", loc=(0.0, 0.08, 0.03), rot=(90, 0, 160))
S.reach(bro, l1[0] - 0.3, "R", Vector(duif.location) + V(0, 0, 0.04))
S.reach(bro, l1[0] - 0.3, "L", None, 0.0)
S.reach(bro, l1[0] + 0.3, "R", None, 0.0)
S.beat(bro, l1[0] + 0.1, **SIT_B, pose="staan", face="blij", face_amt=0.8, at=S.head(held), body={"head": (0, 0, -10), "chest": (0, -20, 0)},
       arms=SHOW_R)
S.beat(bro, l1[1] + 0.2, **SIT_B, pose="staan", face="lach", face_amt=0.7, at=S.head(held), body={"head": (0, 0, -6), "chest": (0, -15, 0)},
       arms=SHOW_R)
S.beat(bro, l2[0] + 2.4, **SIT_B, pose="staan", face="blij", face_amt=0.5, at=DESK, body={"head": (12, 0, 0)}, arms=HOLD_FRONT_R)
S.hold(bro, END)

# ---------------------------------------------------------------- hij, in de deuropening
S.beat(held, 0.0, "staan", face="blij", face_amt=0.4, at=S.head(bro), body={"chest": (0, 0, 0)})
S.beat(held, l1[0] + 0.5, "handen_zij", face="blij", face_amt=0.6, at=S.head(bro))
S.beat(held, l1[1] + 0.3, "staan", face="lach", face_amt=0.5, at=CRANES)
S.beat(held, l2[0] + 1.6, "staan", face="nerveus", face_amt=0.6, at=CRANES, body={"head": (8, 0, 0)})
S.beat(held, l2[0] + 3.4, "ontspannen", face="twijfel", face_amt=0.8, look=(0.2, -0.3), body={"head": (6, 12, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- camera
HB = S.head(bro)
S.cam(0.0, ((-1.3, -0.7, 1.5), (1.3, -0.35, 0.85), 24), ((-1.1, -0.65, 1.45), (1.3, -0.3, 0.85), 26))
S.cam(1.7, (DESK + V(0.2, -0.75, 0.25), DESK + V(-0.08, 0.0, 0.02), 40), (DESK + V(0.18, -0.65, 0.22), DESK + V(-0.08, 0, 0.02), 44), dof=1.2)
S.cam(l1[0] - 0.3, (HB + V(0.95, -1.15, -0.1), HB + V(-0.05, -0.1, -0.25), 28), (HB + V(0.85, -1.05, -0.1), HB + V(-0.05, -0.1, -0.22), 32), dof=1.8)
S.cam(l2[0] - 0.1, (CRANES + V(-0.2, -0.7, 0.3), CRANES + V(-0.05, -0.05, 0), 36), (CRANES + V(-0.17, -0.6, 0.26), CRANES + V(-0.05, -0.05, 0), 40), dof=1.0)
S.cam(l2[0] + 2.2, S.shot(held, l2[0] + 3, "mcu", az=-20, lens=36), S.shot(held, l2[1], "cu", az=-15, lens=42))
S.wall(l2[0] + 2.2, END + 1)

S.finish(length=END)
