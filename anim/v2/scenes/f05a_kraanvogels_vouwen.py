"""F05a · Dag 2 · 10x · keukentafel bij dageraad. 'Then you remember. The present.' Hij vouwt, zijn handen een waas,
de hoop groeit. Teller CRANES: 1 ... 214 ... 640 ... 1,000.

    blender -b -P anim/v2/scenes/f05a_kraanvogels_vouwen.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402

S = Scene2("f05a", "keuken", "dageraad")

TX, TY, TZ = 0.2, -0.6, 0.76
SEAT_AT = V(TX - 0.38, TY - 0.62, 0)             # Stoel_1, kijkt naar +y (de tafel)
WORK = V(TX - 0.3, TY - 0.28, TZ + 0.07)         # waar zijn handen vouwen

# de hoop uit de set plus extra kraanvogels: samen wordt het er duizend (de onderste eerst zichtbaar)
cranes = [o for o in bpy.data.objects if o.name.startswith("Kraanvogel_") and o.name[11:].isdigit()]
cranes += HU.kraanvogels_hoop("Kraanvogel_extra", (TX + 0.25, TY - 0.0), (1.0, 0.75), 560, height=0.3, seed=21, z0=TZ)
cranes += HU.kraanvogels_hoop("Kraanvogel_stoel", (TX + 0.38, TY + 0.62), (0.45, 0.4), 110, height=0.25, seed=22, z0=0.47)
cranes += HU.kraanvogels_hoop("Kraanvogel_vloer", (TX + 0.6, TY + 1.0), (1.4, 0.6), 160, height=0.02, seed=23, z0=0.0)
cranes.sort(key=lambda o: (o.location.z, o.location.x))
S.obj("Kraanvogel_in_wording").hide_render = True

held = S.actor("hoofdpersonage", SEAT_AT, 180)
SIT_H, zh = sit(held)
S.place(held, 0, SEAT_AT + V(0, 0, zh), 180)
sheet = T.box("Vouwblaadje", (0, 0, 0), (0.15, 0.15, 0.004), HU.paper("origamipapier2", HU.PAPIER[2]), bevel=0, ol=0)

# ---------------------------------------------------------------- tijdlijn
l1 = S.say("F05-01", gap=0.6)
GO = l1[1] + 0.3
l2 = S.say("F05-02", gap=0.6)
END = l2[1] + 1.4
N0, N1 = GO + 0.4, l2[1] - 0.2                   # de teller loopt van 1 naar 1.000


def count(t):
    u = smooth(N0, N1, t) if t < N1 else 1.0
    return max(1, int(round(1 + 999 * (u ** 1.4))))


START = 6 * 3600 + 58 * 60 + 20
SPAN = 30 * 60 + 40                              # buiten: een half uur; voor hem: vijf uur


def clk(t):
    s = START + 0.1 * t + SPAN * (smooth(N0, N1, t) if t < N1 else 1.0)
    return hms(s, 0, "TUE")


S.hud2(2, "10x", clock=clk, t0=0.4)
S.gauge2(lambda t: f"CRANES: {count(t):,}", N0, END, color=GOLD)
S.music("strijkers_warm", 0.0, END + 1, vol=0.2, fade_in=1.0, fade_out=1.2)
S.ambience("sfx_dageraad_straat", 0.0, END, vol=0.05)
S.sfx("sfx_papier_vouwen", GO, 0.45, cut=(0, 6.0))
S.sfx("sfx_papier_vouwen", GO + 6.0, 0.4, cut=(0, 6.0))
S.sfx("sfx_hud_tik", N1, 0.5)

for k, o in enumerate(cranes):                   # de hoop groeit mee met de teller
    n_at = (k + 1) * 1000 / len(cranes)
    u = ((n_at - 1) / 999) ** (1 / 1.4)
    t = N0 + u * (N1 - N0)
    show(o, t)

# ---------------------------------------------------------------- hij: denkt, dan vouwen (handen als een waas)
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=WORK + V(0.3, 0.3, 0))
S.beat(held, l1[0] + 0.9, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=0.6, look=(0, 0.2), body={"head": (-6, 0, 0)})
S.beat(held, GO, **SIT_H, pose="ontspannen", face="vastberaden", face_amt=0.8, at=WORK, body={"head": (14, 0, 0)})
grab(S, sheet, held, GO, "hand.R", loc=(0.0, 0.06, 0.02), rot=(90, 0, 0))
t = GO + 0.1
k = 0
while t < N1:                                    # tien keer zo snel: de handen trillen tot een waas
    j = 0.035 * (1 if k % 2 else -1)
    S.reach(held, t, "R", WORK + V(0.06 + j, -0.02, 0.05 + 0.02 * (k % 3)))
    S.reach(held, t + 0.04, "L", WORK + V(-0.06 - j, 0.02, 0.06 - 0.02 * (k % 2)))
    t += 0.08
    k += 1
S.reach(held, N1 + 0.1, "R", WORK + V(0.05, 0.05, 0.12))
S.reach(held, N1 + 0.1, "L", None, 0.0)
S.beat(held, N1 + 0.2, **SIT_H, pose="ontspannen", face="blij", face_amt=0.8, at=WORK + V(0.5, 0.4, 0.2), body={"head": (0, 10, 0)})
S.beat(held, END - 0.6, **SIT_H, pose="ontspannen", face="lach", face_amt=0.6, at=WORK + V(0.5, 0.4, 0.2))
S.hold(held, END)

# ---------------------------------------------------------------- camera
HH = S.headpos(held, 0.5)
S.cam(0.0, ((1.8, -2.4, 1.7), (TX - 0.2, TY + 0.1, 0.9), 26), ((1.6, -2.2, 1.65), (TX - 0.2, TY + 0.1, 0.9), 28))
S.cam(l1[0] + 0.7, ((TX + 0.25, TY + 0.4, 1.12), HH + V(0, 0, -0.08), 36), ((TX + 0.22, TY + 0.35, 1.1), HH + V(0, 0, -0.08), 40), dof=1.6)
S.cam(GO, (WORK + V(0.6, 0.55, 0.42), WORK + V(0, -0.05, 0.06), 32), (WORK + V(0.52, 0.48, 0.38), WORK + V(0, -0.05, 0.06), 35), dof=1.2)
S.cam(GO + 2.6, ((TX + 1.9, TY - 1.9, 2.3), (TX + 0.15, TY, 0.85), 28), ((TX + 1.7, TY - 1.7, 2.2), (TX + 0.15, TY, 0.85), 30))
S.cam(N1 - 0.6, ((TX + 0.8, TY + 0.55, 1.15), HH + V(0, 0, -0.08), 32), ((TX + 0.7, TY + 0.5, 1.15), HH + V(0, 0, -0.08), 36), dof=1.8)

S.wall(l1[0] + 0.7, GO)                          # tegenshots op zijn gezicht: de voormuur achter hem
S.wall(N1 - 0.6, END + 1)
S.finish(length=END)
