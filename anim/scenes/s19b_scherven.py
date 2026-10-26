"""S19b · Dag 18 · na de nies: glas overal. Dit stuk is echt (de knal door de geluidsbarrière),
twaalf huizen, elk raam, autoalarmen zes straten ver. 'Bless you, I guess?'

    blender -b -P anim/scenes/s19b_scherven.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s19b", "straat", "scherven")

AT = V(-3.0, 7.35, 0.12)
FRIEND_AT = V(-5.8, 6.7, 0.12)
held = S.actor("hoofdpersonage", AT, 0)
vriend = S.actor("beste_vriend", FRIEND_AT, heading(FRIEND_AT, AT), energy=1.2)

# ---------------------------------------------------------------- tijdlijn
S.hud(18, "262,144x STRONGER", t0=0.0, tick=False)
S.ambience("sfx_autoalarm", 0.0, 60, vol=0.14)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.05)
l7 = S.say("S19-07", gap=0.5)
NORMAL = l7[0] + 1.47
LUNGS = l7[0] + 4.6
FASTER = l7[0] + 7.5
REPLAY = l7[0] + 11.6                          # de pauze: herhaling van de knal
BOOM_R = REPLAY + 1.3
NOT_SNEEZE = l7[0] + 14.65                     # 'That's not a sneeze anymore. That's a sonic boom.'
S.real(l7[0] + 0.1, NOT_SNEEZE - 0.2)
S.text("NORMAL SNEEZE: ~5 M/S", NORMAL + 0.4, FASTER - 0.1, loc=(0.965, 0.30), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOUR LUNGS: 262,144x STRONGER", LUNGS + 0.2, FASTER - 0.1, loc=(0.965, 0.22), size=50, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("AIR SPEED: > 343 M/S", FASTER + 0.8, NOT_SNEEZE - 0.2, loc=(0.965, 0.30), size=56, color=CYAN, anchor=("RIGHT", "BOTTOM"))
S.text("FASTER THAN SOUND", FASTER + 2.2, NOT_SNEEZE - 0.2, loc=(0.965, 0.22), size=50, color=CYAN, anchor=("RIGHT", "BOTTOM"))
S.text("SONIC BOOM", NOT_SNEEZE + 1.6, l7[1] + 0.2, loc=(0.5, 0.18), size=110, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.sfx("sfx_whoosh", BOOM_R - 0.35, 0.3)
S.sfx("sfx_klap_donder", BOOM_R - 0.02, 0.35)
l8 = S.say("S19-08", gap=0.6)
EVERY = l8[0] + 1.3
ALARMS = l8[0] + 3.6                           # 'Car alarms for six blocks.'
S.gauge("12 HOUSES · EVERY WINDOW", l8[0] + 0.1, l8[1] + 0.3, color=WHITE)
S.gauge("CAR ALARMS: 6 BLOCKS", ALARMS, l8[1] + 0.6, color=(1.0, 0.6, 0.15, 1))
l9 = S.say("S19-09", who=vriend, gap=0.6, gain=1.15)
BLESS = l9[0] + 1.96
S.wait(1.2)
END = S.t

# ---------------------------------------------------------------- hij: schuldig, tussen de scherven
NOSE = arm("R", (0.2, 0.55, -0.5), (-0.7, 0.45, 0.55))
S.beat(held, 0.0, "staan", face="nerveus", face_amt=1.0, look=(0.6, 0.1), body={"head": (0, 25, 0)}, arms=NOSE)
S.beat(held, NORMAL, "staan", face="nerveus", face_amt=0.8, look=(-0.5, 0.3), body={"head": (-6, -30, 0)})
S.beat(held, LUNGS, "staan", face="twijfel", face_amt=0.8, look=(0, -0.5), body={"head": (14, 0, 0)}, arms=LOOK_HANDS)
S.beat(held, FASTER, "staan", face="nerveus", face_amt=0.7, look=(0, 0.1))
# de herhaling (in profiel): inademen, en de nies
S.beat(held, REPLAY, "staan", face="nerveus", face_amt=0.6, look=(0, 0.1))
S.beat(held, BOOM_R - 0.5, "schrik", amount=0.5, face="geschrokken", face_amt=0.6, body={"head": (-26, 0, 0), "chest": (-12, 0, 0)},
       mouth=0.7, ogen_knijp=1.0)
S.beat(held, BOOM_R, "staan", crouch=(0.12, 30), face="inspanning", face_amt=1.0, body={"head": (30, 0, 0), "chest": (18, 0, 0)},
       mouth=0.6, ogen_knijp=1.0)
S.beat(held, BOOM_R + 0.8, "staan", crouch=(0.04, 8), face="verdrietig", face_amt=0.8, look=(0, -0.4), body={"head": (10, 0, 0)})
S.beat(held, l8[0] + 0.3, "staan", face="verdrietig", face_amt=0.8, look=(-0.6, 0.3), body={"head": (-8, -40, 0)})
S.beat(held, ALARMS, "staan", face="nerveus", face_amt=0.9, look=(0.6, 0.2), body={"head": (-4, 35, 0)})
S.beat(held, BLESS + 0.3, "schouders_op", amount=0.7, face="grijns", face_amt=0.5, at=S.head(vriend, BLESS), mond_verdrietig=0.4)
S.hold(held, END)
S.beat(vriend, 0.0, "handen_hoofd", crouch=(0.25, 20), face="geschrokken", face_amt=1.0, at=S.head(held, 0))
S.beat(vriend, l8[0], "handen_hoofd", crouch=(0.1, 8), face="bang", face_amt=0.8, at=S.head(held, 0))
S.beat(vriend, l9[0] - 0.3, "staan", face="nerveus", face_amt=1.0, at=S.head(held, l9[0]), arms=arms(HAND_OUT_R, HAND_OUT_L))
S.beat(vriend, BLESS, "schouders_op", amount=0.8, face="twijfel", face_amt=0.9, at=S.head(held, l9[0]), wenkbrauw_op=0.7)
S.hold(vriend, END)

# de herhaling: kegel van lucht en de schokgolf
FACE = AT + V(0, -0.3, 1.45)
S.ring(FACE, BOOM_R, r0=0.15, r1=6.0, dur=0.7, rot=(90, 0, 0), thick=0.05, strength=3.0, color=(0.6, 0.95, 1.0))
S.ring(FACE + V(0, -1.2, 0), BOOM_R + 0.08, r0=0.3, r1=9.0, dur=0.8, rot=(90, 0, 0), thick=0.05, strength=2.5, color=(0.6, 0.95, 1.0))
air = T.cyl("Luchtkegel", (0, 0, 0), 0.05, 1.0, S.mat("lucht_cyaan", (0.6, 0.95, 1.0), 2.0), r2=0.9, seg=24, ol=0)
air.rotation_euler = (math.radians(90), 0, 0)
key(air, BOOM_R - 1 / FPS, loc=FACE, scale=(0.001, 0.001, 0.001))
key(air, BOOM_R + 0.12, loc=FACE, scale=(1.0, 1.0, 3.5))
key(air, BOOM_R + 0.45, loc=FACE + V(0, -2.5, 0), scale=(1.4, 1.4, 4.5))
key(air, BOOM_R + 0.6, loc=FACE + V(0, -3.5, 0), scale=(0.001, 0.001, 0.001))

# knipperende alarmlichten op de geparkeerde auto's
blink = S.mat("alarm_oranje", (1.0, 0.55, 0.1), 8)
for k in range(6):
    car = S.obj(f"Auto_geparkeerd_{k}")
    ov = S.obj(f"Auto_overkant_{k}") if k < 4 else None
    for c in (car, ov):
        if c is None:
            continue
        for sx in (-1.9, 1.9):
            for sy in (-0.8, 0.8):
                o = T.sphere(S._fxname("Alarmlicht"), tuple(c.location + V(sx, sy, 0.7)), 0.09, blink, seg=10, ol=0)
                for j, t in enumerate(frange(0.0, END, 0.4)):
                    visible(o, t, j % 2 == 0)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-4.0, 6.8, 0.5), (2.0, 9.5, 1.2), 22), ((-4.2, 6.6, 0.55), (0.0, 9.0, 1.2), 24))
HC = S.head(held, NORMAL)
S.cam(NORMAL - 0.1, (HC + V(0.4, -1.3, -0.1), HC + V(0, 0, -0.15), 34), (HC + V(0.3, -1.1, -0.1), HC + V(0, 0, -0.12), 38))
S.cam(FASTER - 0.1, (HC + V(0.25, -0.75, 0.0), HC + V(0, 0, -0.04), 44), (HC + V(0.2, -0.65, 0.0), HC + V(0, 0, -0.04), 50))
S.cam(REPLAY - 0.1, ((AT.x + 6.5, AT.y - 2.2, 1.4), (AT.x + 0.2, AT.y - 2.4, 1.3), 26), ((AT.x + 6.2, AT.y - 2.1, 1.4), (AT.x + 0.2, AT.y - 2.4, 1.3), 28),
      shake=lambda t: max(0.0, 1.6 - (t - BOOM_R) * 2.5) if t > BOOM_R else 0.0)
S.cam(NOT_SNEEZE - 0.1, ((-22, -1.5, 2.0), (2, 7, 3.0), 24), ((-21, -1.2, 2.2), (2, 7, 3.0), 26))
S.cam(l8[0] - 0.2, ((-14.0, 3.6, 2.2), (-10.0, 13.0, 3.0), 24), ((8.0, 3.6, 2.2), (12.0, 13.0, 3.0), 24), ease=False)
S.cam(ALARMS - 0.1, ((-7.0, 0.2, 1.1), (-9.0, 3.4, 0.8), 24), ((-7.2, 0.0, 1.2), (-9.0, 3.4, 0.8), 26))
S.cam(l9[0] - 0.2, S.shot(vriend, l9[0], "mcu", az=-20, lens=34), S.shot(vriend, l9[1], "cu", az=-15, lens=40))
S.cam(BLESS + 0.4, S.shot(held, BLESS, "mcu", az=20, lens=34), S.shot(held, END, "mcu", az=16, lens=38))

S.finish(length=END)
