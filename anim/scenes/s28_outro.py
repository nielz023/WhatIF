"""S28 · Outro · de aarde vanuit de ruimte, de gelijmde mok zweeft ervoor. 'What would YOU do?' De teaser voor de
volgende video (2x SMALLER) en het eindscherm (12 seconden, ruimte voor de YouTube-elementen).

    blender -b -P anim/scenes/s28_outro.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s28", "ruimte", "ruimte")
S.clip = (0.01, 30000)

MUG = V(0.0, -0.6, 400.0)
mug = S.obj("Mok_gelijmd")

# ---------------------------------------------------------------- tijdlijn
S.music("strijkers_warm", 0.0, 0, vol=0.2, fade_in=2.0, fade_out=3.0)
WARM = S.sounds[-1]
l1 = S.say("S28-01", gap=1.2)
GO_HOME = l1[0] + 2.0
STAY = l1[0] + 3.4
COMMENTS = l1[0] + 5.5                         # 'Tell us in the comments.'
l2 = S.say("S28-02", gap=1.0)
SMALLER = l2[0] + 2.82                         # 'What if every day... you got two times SMALLER?'
DAY1 = l2[0] + 7.14
DAY30 = l2[0] + 9.59
l3 = S.say("S28-03", gap=0.9)
CAREFUL = l3[0] + 4.27                         # 'be careful what you wish for.'
ENDSCREEN = l3[1] + 0.8
END = ENDSCREEN + 12.0
WARM["loop_to"] = l2[0] - 0.2
S.music("piano_zacht", l2[0] - 0.6, 0, vol=0.16, fade_in=1.5, fade_out=3.0)
PIANO = S.sounds[-1]
PIANO["loop_to"] = END
S.sfx("sfx_whoosh", SMALLER - 0.2, 0.18)

S.text("THROW IT  ·  OR  ·  STAY UP THERE?", COMMENTS - 1.6, l1[1] + 0.6, loc=(0.5, 0.14), size=64, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("TELL US IN THE COMMENTS", COMMENTS, l1[1] + 0.6, loc=(0.5, 0.07), size=48, color=GOLD, anchor=("CENTER", "BOTTOM"))
S.card("NEXT WEEK", SMALLER - 0.3, DAY1 - 0.2, size=90, dim=0.45, sub="WHAT IF YOU GOT 2x SMALLER EVERY DAY?")
S.text("DAY 1: THE TOP SHELF IS TOO HIGH", DAY1, DAY30 - 0.1, loc=(0.5, 0.14), size=56, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("DAY 30: SMALLER THAN AN ATOM", DAY30, l2[1] + 0.8, loc=(0.5, 0.14), size=56, color=CYAN, anchor=("CENTER", "BOTTOM"))
S.text("BE CAREFUL WHAT YOU WISH FOR", CAREFUL - 0.2, ENDSCREEN - 0.1, loc=(0.5, 0.14), size=60, color=WHITE, anchor=("CENTER", "BOTTOM"))
# eindscherm: links de volgende video, rechts abonneren (YouTube legt er zijn eigen knoppen overheen)
S.text("WATCH NEXT", ENDSCREEN + 0.3, END, loc=(0.27, 0.78), size=60, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("SUBSCRIBE", ENDSCREEN + 0.5, END, loc=(0.75, 0.78), size=60, color=RED, anchor=("CENTER", "BOTTOM"))

# ---------------------------------------------------------------- de mok draait heel langzaam
if mug:
    r0 = V(*[math.degrees(a) for a in mug.rotation_euler])
    key(mug, 0.0, loc=MUG, rot=tuple(r0))
    key(mug, END, loc=MUG + V(0.0, 0.0, 0.01), rot=tuple(r0 + V(6, -4, 40)))

# ---------------------------------------------------------------- camera: langzaam naar de mok, dan wijd voor het eindscherm
S.cam(0.0, ((0.9, -4.2, 400.9), (0.0, -0.6, 400.05), 24), ((0.25, -1.9, 400.25), (0.0, -0.6, 400.05), 30))
S.cam(GO_HOME, ((0.25, -1.9, 400.25), (0.0, -0.6, 400.05), 30), ((0.06, -1.0, 400.09), (0.0, -0.6, 400.04), 50))
S.cam(l2[0] - 0.2, ((-1.0, -6.0, 401.2), (0.0, 40.0, 385.0), 24), ((-0.8, -5.2, 401.0), (0.0, 40.0, 385.0), 24))
S.cam(l3[0] - 0.2, ((3.0, -4.0, 399.5), (2000, 300, -900), 28), ((3.1, -4.1, 399.6), (2000, 300, -900), 30))
S.cam(ENDSCREEN - 0.3, ((0.4, -5.5, 401.6), (0.0, -0.6, 399.6), 26), ((0.5, -6.5, 401.9), (0.0, -0.6, 399.6), 26))

S.finish(length=END)
