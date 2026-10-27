"""SH3c · 1 jaar vooruit kijken · tv-studio (visioenen): volgende week de lotto, hij wint. Eén maand: interview met
een reuzencheque. Zes maanden: geld regent neer. Alles is perfect.

    blender -b -P anim/shorts/sh3c_studio.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh3", "c", "tvstudio", "studio", lines=(3, 4))
l3, l4 = S.L[3], S.L[4]
T0, END = S.t0, S.t1
for o in bpy.data.objects:
    if o.name.startswith("Tvcamera_2"):
        o.hide_render = True
S.obj("Showlogo_2").data.body = "JACKPOT"
S.obj("Showlogo_sub").data.body = "LOTTO LIVE"

Z = 0.35
AT = V(-1.1, 2.6, Z)
anchor = S.actor("nieuwslezeres", AT, 0, energy=1.0)
HP = V(1.0, 2.4, Z)
held = S.actor("hoofdpersonage", HP, 10)
WIN = l3[1] - 1.3                                # '... and you win'
GLOW = l4[0] + 0.1
MONTH = l4[0] + 1.6
SIX = l4[0] + 3.3
eye_glow(held, [(T0, 0), (GLOW - 0.05, 0), (GLOW + 0.1, 1), (MONTH - 0.2, 0.6), (MONTH, 0)])

# loterijballen voor het grote scherm
NUMS = ("7", "13", "21", "34", "42")
ball_m = S.mat("lottobal", (0.98, 0.85, 0.15))
num_m = S.mat("lottocijfer", (0.1, 0.1, 0.12))
BALL0 = l3[0] + 1.2
for k, n in enumerate(NUMS):
    c = V(-1.6 + k * 0.8, 6.9, 1.7)
    b = T.sphere(f"Lottobal_{k}", tuple(c), 0.3, ball_m, ol=0.01)
    tx = T.text(f"Lottocijfer_{k}", n, tuple(c + V(0, -0.31, -0.08)), 0.24, num_m, extrude=0.01)
    for o in (b, tx):
        show(o, BALL0 + k * 0.3)
        key(o, BALL0 + k * 0.3, scale=0.01)
        key(o, BALL0 + k * 0.3 + 0.2, scale=1.0)
ticket = T.box("Lot", (0, 0, 0), (0.14, 0.004, 0.08), S.mat("lot", (0.98, 0.95, 0.8)), bevel=0, ol=0.002, base=False)
T.box("Lot_rand", (0, -0.003, 0.025), (0.12, 0.002, 0.012), S.mat("lot_rood", (0.85, 0.12, 0.1)), bevel=0, ol=0, base=False).parent = ticket
# de reuzencheque en de geldregen
chq = T.box("Cheque", (0.0, 2.8, Z + 0.25), (1.7, 0.04, 0.8), S.mat("cheque", (0.97, 0.97, 0.93)), bevel=0.01, ol=0.008)
cht = T.text("Cheque_bedrag", "$10,000,000", (0.0, 2.77, Z + 0.62), 0.22, S.mat("cheque_inkt", (0.1, 0.4, 0.15)), extrude=0.004)
chn = T.text("Cheque_naam", "PAY TO: YOU", (0.0, 2.77, Z + 0.9), 0.1, num_m, extrude=0.003)
for o in (chq, cht, chn):
    show(o, MONTH, SIX)

# ---------------------------------------------------------------- geluid, tellers
S.card("", T0, END, dim=0.12, bg=(0.85, 0.95, 1.0), fin=0, fout=0)
S.card("", T0, T0 + 0.35, dim=1.0, bg=(1, 1, 1), fin=0, fout=8)
S.counter("NEXT WEEK", T0 + 0.1, GLOW, color=(0.75, 0.9, 1.0, 1), sub="THE LOTTERY")
S.counter("1 MONTH", MONTH, SIX, color=(0.75, 0.9, 1.0, 1))
S.counter("6 MONTHS", SIX, None, color=(0.75, 0.9, 1.0, 1), sub="EVERYTHING IS PERFECT")
for k in range(5):
    S.sfx("sfx_hud_tik", BALL0 + k * 0.3, 0.3)
S.sfx("sfx_menigte_juicht", WIN, 0.35)
S.sfx("sfx_visioen", GLOW - 0.1, 0.45)
S.sfx("sfx_publiek", MONTH, 0.25)

# confetti en geld
for k, col in enumerate(((0.95, 0.2, 0.3), (0.2, 0.6, 0.95), (1.0, 0.85, 0.1), (0.3, 0.85, 0.35))):
    S.debris(HP + V(0, 0, 3.0), WIN + 0.05 * k, n=22, size=(0.04, 0.07), color=col, speed=(1.0, 3.0), up=0.4, floor=Z,
             life=3.0, name=f"Confetti_{k}")
for k in range(3):
    S.debris(V(0.3, 2.5, 4.0), SIX + 0.3 * k, n=26, size=(0.12, 0.06), color=(0.35, 0.7, 0.35), speed=(0.5, 1.6), up=0.0,
             floor=Z, life=3.5, name=f"Geld_{k}")

# ---------------------------------------------------------------- acteren
S.beat(anchor, T0, "wijzen", face="lach", face_amt=0.6, at=V(0, 6.9, 1.7))
for k, t in enumerate(frange(T0 + 0.2, l3[0] + 2.8, 0.13)):
    A.key_prop(anchor.rig, "mond_open", (0.1, 0.45, 0.2, 0.55, 0.0)[k % 5], F(t))
S.beat(anchor, WIN, "juichen", face="lach", face_amt=1.0, at=HP + V(0, 0, 1.3), mouth=0.5)
S.beat(held, T0, "staan", face="grijns", face_amt=0.8, at=V(0, 6.9, 1.7))
S.reach(held, T0, "R", HP + V(0.15, -0.3, 1.1))
grab(S, ticket, held, T0, "hand.R", mode="full", rot=(90, 0, 0))
S.beat(held, l3[0] + 2.6, "staan", face="zelfverzekerd", face_amt=1.0, look=(0, 0), mouth=0.0)
S.beat(held, WIN, "juichen", face="lach", face_amt=1.0, look=(0, 0.3), mouth=0.6)
S.reach(held, WIN, "R", None, 0.0)
S.beat(held, WIN + 0.6, "armen_omhoog", face="lach", face_amt=1.0, look=(0, 0.3), mouth=0.5)
show(ticket, T0, MONTH)
S.beat(held, GLOW, "staan", face="verbaasd", face_amt=0.8, look=(0, 0), mouth=0.2)
# 1 maand: naast de cheque, de presentatrice interviewt
S.place(held, MONTH, V(1.3, 2.4, Z), -10)
S.place(anchor, MONTH, V(-1.3, 2.3, Z), 20)
S.beat(held, MONTH, "wijzen", face="zelfverzekerd", face_amt=1.0, at=chq.location + V(0, 0, 0.6), mouth=0.0)
S.beat(anchor, MONTH, "staan", face="blij", face_amt=0.8, at=V(1.3, 2.4, Z + 1.3))
# 6 maanden: zonnebril, geldregen
shades = T.box("Zonnebril", (0, 0, 0), (0.42, 0.03, 0.08), S.mat("zonnebril", (0.03, 0.03, 0.04)), bevel=0.02, ol=0.004, base=False)
S.place(held, SIX, V(0.3, 2.3, Z), 0)
S.place(anchor, SIX, V(-4.0, 2.3, Z), 0)
show(shades, SIX)
hc = S.head(held, SIX)
shades.location = hc + V(0, -0.33, 0.06)
attach_keep(shades, held, "head", SIX)
S.beat(held, SIX, "juichen", face="lach", face_amt=1.0, look=(0, 0.4), mouth=0.4)
S.beat(held, SIX + 1.0, "armen_omhoog", face="grijns", face_amt=1.0, look=(0, 0), mouth=0.0)
S.beat(held, END - 0.6, "wijzen", face="grijns", face_amt=1.0, look=(0, 0), mouth=0.0)
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(T0, ((0.2, -2.6, 2.0), (0.0, 5.8, 1.7), 22), ((0.1, -2.2, 1.95), (0.0, 5.8, 1.7), 24))
S.cam(l3[0] + 2.7, S.shot(held, l3[0] + 3.0, "med", az=-8, lens=30), S.shot(held, WIN, "med", az=-6, lens=32))
S.cam(WIN - 0.1, ((1.2, -2.0, 1.4), (0.6, 2.4, 1.6), 22), ((1.1, -1.8, 1.4), (0.6, 2.4, 1.7), 22))
S.cam(GLOW - 0.1, S.shot(held, GLOW, "cu", az=0, lens=42), S.shot(held, MONTH, "cu", az=0, lens=48))
S.cam(MONTH, ((0.0, -2.4, 1.5), (0.0, 2.5, 1.2), 24), ((0.0, -2.1, 1.5), (0.0, 2.5, 1.2), 26))
S.cam(SIX, ((0.5, -1.4, 0.9), (0.3, 2.3, 1.6), 22), ((0.45, -1.2, 0.85), (0.3, 2.3, 1.6), 24))

S.done()
