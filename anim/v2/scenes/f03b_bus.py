"""F03b · Dag 1 · 1x · zonnige straat. Hij rent de voordeur uit, de bus rijdt net weg.
'You run for the bus. The bus wins. It always wins.'

    blender -b -P anim/v2/scenes/f03b_bus.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import street as STR  # noqa: E402

S = Scene2("f03b", "straat", "zonnig")

DOOR = V(-1.4, 12.0, 0)            # voordeur van zijn huis (pad x = -1.4)
GATE = V(-1.4, 8.3, 0.12)
STOP = V(24.0, 7.0, 0.12)          # bushalte
BUS0 = V(25.5, 3.15, 0)            # noordbaan, rijdt naar -x (deuren aan de stoepkant)
bus = STR.city_bus("Stadsbus", BUS0, rot=180)
for nm in ("Auto_geparkeerd_3", "Auto_geparkeerd_4"):   # stonden in de busbaan (x = 14 en x = 31)
    S.obj(nm).hide_render = True
    for c in S.obj(nm).children_recursive:
        c.hide_render = True

held = S.actor("hoofdpersonage", DOOR, 0)

# ---------------------------------------------------------------- tijdlijn
S.hud2(1, "1x", clock=clock(7 * 3600 + 51 * 60, 1.0, hhmm=True, day="MON"), t0=0.25)
l1 = S.say("F03-07", gap=0.35)
GO = 0.0
CUT = 1.9                          # van de voordeur naar de bushalte
LEAVE = 2.2                        # de bus trekt op
END = l1[1] + 1.4
S.sfx("sfx_glasdeur", 0.05, 0.4)
S.sfx("sfx_bus_vertrekt", LEAVE - 0.6, 0.45)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.18)
S.music("piano_warm", 0.0, END + 1, vol=0.16, fade_in=0.3, fade_out=0.6)

# ---------------------------------------------------------------- hij rent
S.beat(held, 0.0, "staan", face="nerveus", look=(0.3, 0))
S.run(held, 0.1, CUT + 0.2, [DOOR, GATE, GATE + V(1.0, -1.4, 0)], stride=0.9, lift=0.16, ease_out=0.0)
S.teleport(held, CUT, STOP + V(-7.5, 0.2, 0), 90)
S.run(held, CUT, l1[1] - 0.3, [STOP + V(-7.5, 0.2, 0), STOP + V(-1.2, -0.2, 0)], stride=0.9, lift=0.16, ease_in=0.0, ease_out=0.3)
S.beat(held, l1[1] - 0.2, "handen_zij", face="verdrietig", face_amt=0.8, at=BUS0 + V(-18, 0, 1.2), crouch=(0.06, 18))
S.beat(held, END, "handen_zij", face="verdrietig", face_amt=0.9, at=BUS0 + V(-30, 0, 1.2), crouch=(0.08, 22))
A.key_prop(held.rig, "mond_open", 0.4, F(l1[1]))
A.key_prop(held.rig, "mond_open", 0.15, F(l1[1] + 0.4))
A.key_prop(held.rig, "mond_open", 0.4, F(l1[1] + 0.8))

# ---------------------------------------------------------------- de bus trekt op en rijdt weg
key(bus, 0.0, loc=BUS0)
key(bus, LEAVE, loc=BUS0)
for k in range(1, 8):                  # optrekken: x = x0 - a t^2
    tt = LEAVE + k * (END + 0.5 - LEAVE) / 7
    key(bus, tt, loc=BUS0 - V(2.2 * (tt - LEAVE) ** 2, 0, 0))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((2.0, 6.7, 2.2), (-1.4, 10.8, 0.9), 26), ((1.6, 6.8, 2.0), (-1.0, 8.4, 0.9), 26))
# achter hem aan over de stoep, de bus trekt voor zijn neus op
S.cam(CUT, ((12.5, 7.4, 1.5), (24.0, 6.2, 1.3), 28), ((13.5, 7.35, 1.5), (24.0, 5.6, 1.3), 30))
S.cam(l1[1] - 0.6, S.shot(held, l1[1], "mcu", az=-30, lens=36), S.shot(held, END, "mcu", az=-24, lens=40))

S.finish(length=END)
