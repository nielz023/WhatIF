"""S09a · Dag 7 · slaapkamer, nacht: twaalf miljoen views, de reacties vliegen voorbij.

    blender -b -P anim/scenes/s09a_internet.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s09a", "slaapkamer", "nacht")

BED = V(-1.52, 1.25, 0.6)                    # rechtop in bed, rug tegen het kussen, kijkt naar -y
PH = V(-1.52, 0.9, 1.0)
for n in ("Telefoon", "Telefoon_scherm", "Laptop"):
    S.obj(n).hide_render = True
for o in S.obj("Laptop").children_recursive:
    o.hide_render = True

held = S.actor("hoofdpersonage", BED, 0, energy=1.0)
SIT, _ = sit(held, seat_top=0.0, lean=-8, spread=0.12)
phone = prop_phone(S, "Zijn_telefoon", PH, screen=(0.5, 0.75, 1.0))
phone.rotation_euler = (math.radians(-55), 0, math.radians(180))
phone.scale = (1.7,) * 3
glow = S.obj("Telefoon_gloed")
glow.location = PH + V(0, 0.15, 0.25)
glow.data.energy = 18

# ---------------------------------------------------------------- tijdlijn
S.hud(7, "128x STRONGER", t0=0.4)
S.music("lofi", 0.0, 60, vol=0.3, fade_in=0.6)
l1 = S.say("S09-01", gap=0.6)
l2 = S.say("S09-02", gap=0.4)
GYM = l2[0] + 1.8
S.wait(0.6)
END = S.t

# views tellen op
for k, (txt, t0) in enumerate((("VIEWS: 1,204", 0.5), ("VIEWS: 88,512", 1.0), ("VIEWS: 1,350,000", 1.5), ("VIEWS: 12,000,000", 2.3))):
    t1 = (0.5, 1.0, 1.5, 2.3, None)[k + 1]
    S.gauge(txt, l1[0] + t0, l1[0] + t1 if t1 else END, color=GOLD if k == 3 else WHITE)
    if k in (1, 3):
        S.sfx("sfx_meldingen", l1[0] + t0, 0.35)
# reacties vliegen voorbij (eerst 'fake', dan de gym-vragen)
FAKE = ['"CGI"', '"fake"', '"edited lol"', '"FAKE 100%"', '"green screen"']
GYMQ = ['"bro is HIM"', '"what gym??"', '"teach me"', '"HOW"', '"workout plan pls"']
spots = [(0.62, 0.70), (0.70, 0.58), (0.60, 0.46), (0.72, 0.36), (0.63, 0.24)]
for k, c in enumerate(FAKE):
    t0 = l2[0] + 0.1 + k * 0.28
    S.text(c, t0, GYM - 0.05, loc=spots[k], size=46, color=(1.0, 0.4, 0.4, 1), anchor=("LEFT", "CENTER"))
for k, c in enumerate(GYMQ):
    t0 = GYM + k * 0.3
    S.text(c, t0, END, loc=spots[k], size=46, color=(0.55, 1.0, 0.6, 1), anchor=("LEFT", "CENTER"))
for k in range(5):
    S.sfx("sfx_hud_tik", l2[0] + 0.1 + k * 0.28, 0.25)
    S.sfx("sfx_hud_tik", GYM + k * 0.3, 0.25)

# ---------------------------------------------------------------- acteren
PL = PH + V(0.085, 0.04, -0.04)
PR = PH + V(-0.085, 0.04, -0.04)
S.beat(held, 0.0, **SIT, pose="ontspannen", face="verbaasd", face_amt=0.6, at=PH)
S.reach(held, 0.0, "L", PL)
S.reach(held, 0.0, "R", PR)
t = 0.5
while t < END - 0.3:                          # scrollen met de duim
    S.reach(held, t, "R", PR + V(0.01, -0.01, 0.02))
    S.reach(held, t + 0.18, "R", PR + V(0.01, -0.01, -0.01))
    t += 0.55
S.beat(held, l1[0] + 2.4, **SIT, pose="ontspannen", face="verbaasd", face_amt=1.0, at=PH, wenkbrauw_op=0.8)
S.beat(held, l2[0] + 0.4, **SIT, pose="ontspannen", face="twijfel", face_amt=0.7, at=PH)
S.beat(held, GYM + 0.2, **SIT, pose="ontspannen", face="grijns", face_amt=0.9, at=PH)
S.beat(held, l2[1], **SIT, pose="ontspannen", face="lach", face_amt=0.6, at=PH)
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.3, -1.1, 1.5), (-1.52, 1.1, 1.0), 26), ((0.05, -0.8, 1.45), (-1.52, 1.1, 1.0), 30))
S.cam(l1[0] + 2.0, S.shot(held, l1[0] + 2.2, "mcu", az=12, lens=32, h=-0.1), S.shot(held, l1[1], "mcu", az=10, lens=36, h=-0.1))
S.cam(l2[0] - 0.1, ((-1.2, 0.25, 1.1), (-1.52, 1.15, 1.3), 28), ((-1.25, 0.35, 1.12), (-1.52, 1.15, 1.32), 32))
S.cam(GYM + 0.6, S.shot(held, GYM + 1.0, "mcu", az=-15, lens=30, h=0.0), S.shot(held, END, "mcu", az=-12, lens=34, h=0.0))

S.finish(length=END)
