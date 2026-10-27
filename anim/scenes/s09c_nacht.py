"""S09c · Dag 7 · slaapkamer: de vriend ('I can't even edit'), samen lachen, en dan de nacht dat hij de som maakt.

    blender -b -P anim/scenes/s09c_nacht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s09c", "slaapkamer", "nacht")

for n in ("Telefoon", "Telefoon_scherm"):
    S.obj(n).hide_render = True
glow = S.obj("Telefoon_gloed")
BX, BY = -1.52, 0.86
EDGE = V(-1.38, 0.95, 0.6)                   # op het bed, benen gestrekt, schuin naar de vriend en de camera
CHAIR = V(0.1, 0.45, 0)                      # vriend op de bureaustoel
LIE = V(BX, 0.1, 0.74)                       # liggend: wortel bij het voeteneind, hoofd op het kussen

held = S.actor("hoofdpersonage", EDGE, 40, energy=1.0)
vriend = S.actor("beste_vriend", CHAIR, -60, energy=1.0)
chair = S.obj("Bureaustoel")
chair.location = (CHAIR.x, CHAIR.y, 0)
chair.rotation_euler.z = math.radians(-90)
SIT_H, _ = sit(held, seat_top=0.0, lean=-6, spread=0.1)
zh = EDGE.z
SIT_V, zv = sit(vriend, seat_top=0.53, lean=4)
S.place(held, 0, (EDGE.x, EDGE.y, zh), 40)
S.place(vriend, 0, (CHAIR.x, CHAIR.y, zv), -60)
fphone = prop_phone(S, "Vriend_telefoon", (0, 0, 0), screen=(0.9, 0.95, 1.0))
fphone.scale = (1.7,) * 3
attach(fphone, vriend, "hand.R", (0, 0.06, 0.0), (90, 0, 0))
PHN = S.head(vriend, 0) + V(-0.25, -0.35, -0.45)
# extra dekbed over hem heen als hij ligt
duvet = T.box("Dekbed_over_hem", (BX, 0.55, 0.62), (1.05, 1.15, 0.24), S.mat("dekbed_blauw", (0.12, 0.32, 0.78)), bevel=0.08, ol=0.01)

# ---------------------------------------------------------------- tijdlijn
S.music("lofi", 0.0, 0.0, vol=0.26, fade_in=0.2, start=20.0)
LOFI = S.sounds[-1]
l4 = S.say("S09-04", who=vriend, gap=0.3, gain=1.2)
l5 = S.say("S09-05", gap=0.5)
NIGHT = l5[0] + 2.3                          # 'But that night...'
MATH = l5[0] + 4.7
LOFI["loop_to"] = MATH - 0.1
S.music("drone", MATH - 0.6, 0.0, vol=0.3, fade_in=0.8, fade_out=0.05)
DRONE = S.sounds[-1]
l6 = S.say("S09-06", gap=0.5)
D7, D10, D20 = l6[0], l6[0] + 2.46, l6[0] + 4.84
MILLION = l6[0] + 6.55
l7 = S.say("S09-07", gap=0.7)
DRONE["loop_to"] = l7[1] + 0.15
BLACK = l7[1] + 0.25                         # patroononderbreking: 1 s zwart en stilte
S.t = BLACK + 1.0
TICK = S.t
S.sfx("sfx_hud_tik", TICK, 0.8)
S.wait(1.0)
END = S.t

S.hud(7, "128x STRONGER", t0=0.0, t1=BLACK, tick=False)
S.hud(8, "256x STRONGER", t0=TICK, tick=False)
S.card("DAY 7:  128x", D7 + 0.2, D10, size=100, dim=0.25)
S.card("DAY 10:  1,024x", D10 + 0.1, MILLION - 0.6, size=110, dim=0.3, color=GOLD)
S.card("DAY 20:  1,048,576x", MILLION, l6[1] + 0.4, size=120, dim=0.4, color=(1.0, 0.3, 0.25, 1))
S.card(" ", BLACK, TICK, dim=1.0)

# ---------------------------------------------------------------- vriend en hij, lachen
S.beat(vriend, 0.0, **SIT_V, pose="filmen", amount=0.6, face="lach", face_amt=0.5, at=PHN)
S.beat(vriend, l4[0] + 0.1, **SIT_V, pose="filmen", amount=0.6, face="lach", face_amt=0.8, at=S.head(held, 0))
S.beat(vriend, l4[0] + 1.5, **SIT_V, pose="schouders_op", face="lach", face_amt=1.0, at=S.head(held, 0))
S.beat(vriend, l5[0] + 0.3, **SIT_V, pose="ontspannen", face="lach", face_amt=1.0, at=S.head(held, 0), body={"chest": (-8, 0, 0), "head": (-10, 0, 0)})
S.hold(vriend, NIGHT - 1 / FPS)
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="blij", face_amt=0.4, at=PHN)
S.beat(held, l4[0] + 0.6, **SIT_H, pose="ontspannen", face="grijns", face_amt=0.7, at=S.head(vriend, 0))
S.beat(held, l5[0] + 0.2, **SIT_H, pose="ontspannen", face="lach", face_amt=1.0, at=S.head(vriend, 0), body={"chest": (-6, 0, 0), "head": (-8, 0, 0)})
S.beat(held, l5[0] + 1.3, **SIT_H, pose="ontspannen", face="lach", face_amt=0.6, at=S.head(vriend, 0))
S.hold(held, NIGHT - 1 / FPS)
# 's nachts: vriend weg, laptop dicht, hij ligt wakker
S.teleport(vriend, NIGHT, (30, 30, 0))
show(duvet, NIGHT)
key(held.rig, NIGHT - 1 / FPS, loc=(EDGE.x, EDGE.y, zh), rot=(0, 0, 40), interp="CONSTANT")
key(held.rig, NIGHT, loc=LIE, rot=(-90, 0, 0), interp="CONSTANT")
key(chair, NIGHT - 1 / FPS, loc=(CHAIR.x, CHAIR.y, 0), interp="CONSTANT")
key(chair, NIGHT, loc=(1.14, 0.2, 0), interp="CONSTANT")
key(chair, 0, loc=(CHAIR.x, CHAIR.y, 0), interp="CONSTANT")
S.beat(held, NIGHT, "staan", face="neutraal", face_amt=0.5, look=(0, 0.1), arms=arms(arm("L", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0)), arm("R", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0))))
S.beat(held, MATH, "staan", face="nerveus", face_amt=0.5, look=(0.2, 0.2), arms=arms(arm("L", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0)), arm("R", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0))))
S.beat(held, D10, "staan", face="bang", face_amt=0.5, look=(0, 0.3), arms=arms(arm("L", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0)), arm("R", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0))))
S.beat(held, MILLION, "staan", face="bang", face_amt=1.0, look=(0, 0.0), arms=arms(arm("L", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0)), arm("R", (0.2, 0.0, -1.0), (0.1, 0.1, -1.0))))
S.hold(held, END)
# nachtlicht: het lampje is uit, alleen maan en de rode wekker
glow.data.energy = 4
key(glow, 0, loc=(-0.4, 0.0, 0.95))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-0.75, 0.05, 1.4), S.head(vriend, 0) + V(0, 0, -0.1), 30), ((-0.72, 0.08, 1.4), S.head(vriend, 0) + V(0, 0, -0.1), 34))
S.cam(l5[0] - 0.1, ((0.9, -1.4, 1.5), (-0.4, 0.6, 0.95), 24), ((0.8, -1.25, 1.45), (-0.4, 0.6, 0.95), 26))
S.cam(NIGHT, ((-0.2, -0.9, 2.1), (BX, 1.1, 0.8), 26), ((-0.35, -0.7, 2.05), (BX, 1.2, 0.85), 28))
HEAD_L = S.head(held, MATH)                  # zijn hoofd op het kussen (gezicht naar boven)
S.cam(MATH - 0.2, (HEAD_L + V(0.12, -0.55, 0.95), HEAD_L, 30), (HEAD_L + V(0.08, -0.45, 0.9), HEAD_L, 36))
S.cam(D10, (HEAD_L + V(-0.12, -0.4, 0.9), HEAD_L, 36), (HEAD_L + V(-0.04, -0.3, 0.8), HEAD_L, 40))
S.cam(l7[0] - 0.2, (HEAD_L + V(0, -0.25, 0.8), HEAD_L + V(0, -0.02, 0.2), 42), (HEAD_L + V(0, -0.25, 0.8), HEAD_L + V(0, -0.02, 0.2), 50))

S.finish(length=END)
