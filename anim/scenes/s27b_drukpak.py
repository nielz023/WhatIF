"""S27b · Dag 38 · de hangar. De wetenschappers geven hem het enige wat misschien helpt: een drukpak, zuurstof voor
tweeënzeventig uur. 'Up there, nothing breaks. Nobody gets hurt. Just until we figure this out.'

    blender -b -P anim/scenes/s27b_drukpak.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s27b", "ruimte", "hangar")

SUIT = V(0.0, 6.0, 0.0)
GLOVE = SUIT + V(-0.5, -0.02, 0.95)
H0 = V(-3.2, -7.0, 0.0)
H1 = V(-0.68, 5.3, 0.0)                       # een armlengte van de handschoen
PROF_AT = V(1.35, 4.35, 0.0)

held = S.actor("hoofdpersonage", H0, heading(H0, H1))
prof = S.actor("wetenschapper", PROF_AT, heading(PROF_AT, H1), energy=1.1)

# ---------------------------------------------------------------- tijdlijn
S.hud(38, "274,877,906,944x STRONGER", t0=0.5)
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.06)
S.music("cello", 0.2, 0, vol=0.17, fade_in=1.8, fade_out=2.0)
CEL = S.sounds[-1]
l6 = S.say("S27-06", gap=0.8)
PSUIT = l6[0] + 4.55                           # 'A pressure suit.'
OXY = l6[0] + 5.9                              # 'Oxygen for seventy-two hours.'
l7 = S.say("S27-07", who=prof, gap=0.7, gain=1.1)
NOBODY = l7[0] + 2.32                          # 'Nobody gets hurt.'
UNTIL = l7[0] + 5.06                           # 'Just until we figure this out.'
S.wait(2.4)
END = S.t
CEL["loop_to"] = END + 0.5
S.text("PRESSURE SUIT", PSUIT, OXY - 0.05, loc=(0.965, 0.22), size=60, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("OXYGEN: 72 HOURS", OXY, l6[1] + 0.8, loc=(0.965, 0.22), size=60, color=CYAN, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- hij loopt naar het pak, raakt de handschoen aan
S.walk(held, 0.3, PSUIT - 0.3, [H0, V(-1.6, -1.0, 0), H1], stride=0.5, arms=0.35, end_rot=heading(H1, SUIT + V(0, 0, 0)))
S.beat(held, 0.3, "staan", face="neutraal", face_amt=0.5, at=SUIT + V(0, 0, 2.0), face_only=True)
S.beat(held, PSUIT, "staan", face="verbaasd", face_amt=0.4, at=SUIT + V(0, 0, 2.1), feet="keep")
S.beat(held, OXY + 0.5, "staan", face="neutraal", face_amt=0.6, at=SUIT + V(0, 0, 1.6), feet="keep")
S.beat(held, l7[0] + 0.2, "staan", face="neutraal", face_amt=0.6, at=S.head(prof, l7[0]), feet="keep")
S.beat(held, NOBODY, "staan", face="verdrietig", face_amt=0.6, at=S.head(prof, l7[0]), feet="keep", mond_verdrietig=0.4)
S.beat(held, UNTIL + 0.4, "staan", face="verdrietig", face_amt=0.7, at=GLOVE, feet="keep", mond_verdrietig=0.5, body={"head": (6, 0, 0)})
S.hold(held, l7[1] + 0.2)
S.reach(held, l7[1] + 0.2, "L", None, inf=0.0)
S.reach(held, l7[1] + 0.9, "L", GLOVE + V(0.04, -0.09, 0.0), inf=1.0)
S.beat(held, l7[1] + 0.9, "staan", face="verdrietig", face_amt=0.8, at=GLOVE, feet="keep", mond_verdrietig=0.6, ogen_knijp=0.3)
S.hold(held, END)

# ---------------------------------------------------------------- de wetenschapper
S.beat(prof, 0.0, "staan", face="neutraal", face_amt=0.6, at=S.head(held, PSUIT), arms=arm("R", (0.3, 0.3, -0.9), (0.2, 0.6, -0.4)))
S.beat(prof, l7[0] - 0.2, "staan", face="verdrietig", face_amt=0.4, at=S.head(held, l7[0]), arms=HAND_OUT_R)
S.beat(prof, NOBODY + 0.3, "staan", face="verdrietig", face_amt=0.6, at=S.head(held, l7[0]), mond_verdrietig=0.4)
S.beat(prof, UNTIL, "staan", face="neutraal", face_amt=0.7, at=S.head(held, l7[0]), body={"head": (8, 0, 0)}, mond_verdrietig=0.5)
S.beat(prof, END - 0.3, "staan", face="verdrietig", face_amt=0.6, look=(0, -0.5), body={"head": (14, 0, 0)})

# ---------------------------------------------------------------- camera
S.cam(0.0, ((8.0, -12.0, 3.5), (-1.0, 4.0, 1.6), 24), ((7.4, -11.0, 3.2), (-1.0, 4.0, 1.5), 26))
S.cam(PSUIT - 0.15, ((0.6, 3.0, 1.75), (0.0, 6.0, 1.75), 32), ((0.5, 3.4, 1.8), (0.0, 6.0, 1.8), 36))
S.cam(OXY + 0.6, S.shot(held, OXY + 1.2, "mcu", az=-30, lens=34), S.shot(held, l6[1], "mcu", az=-26, lens=37))
S.cam(l7[0] - 0.15, S.shot(prof, l7[0] + 0.5, "mcu", az=20, lens=34), S.shot(prof, NOBODY, "mcu", az=16, lens=37))
S.cam(NOBODY + 0.9, S.shot(held, NOBODY + 1.2, "mcu", az=-25, lens=34), S.shot(held, UNTIL, "mcu", az=-22, lens=37))
S.cam(l7[1] + 0.2, ((-3.2, 3.2, 1.55), (-0.35, 5.3, 1.25), 28), ((-3.0, 3.35, 1.55), (-0.35, 5.3, 1.25), 30))

S.finish(length=END)
