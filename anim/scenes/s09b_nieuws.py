"""S09b · Dag 7 · tv-studio: de nieuwslezeres over de 'bewerkte' video.

    blender -b -P anim/scenes/s09b_nieuws.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s09b", "tvstudio", "studio")

AT = V(-0.9, 2.6, 0.35)                      # voor het decor, naar de camera
anchor = S.actor("nieuwslezeres", AT, 0, energy=1.1)
S.obj("Showlogo_2").data.body = "VIRAL"
S.obj("Showlogo_sub").data.body = "FAKE?"
for o in bpy.data.objects:
    if o.name.startswith("Tvcamera_2"):
        o.hide_render = True

# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_binnen_sfeer", 0.0, 30, vol=0.08)
S.music("lofi", 0.0, 30, vol=0.18, fade_in=0.1, start=12.0)
l3 = S.say("S09-03", who=anchor, gap=0.4, gain=1.2)
EXPERTS = l3[0] + 4.39
S.wait(0.4)
END = S.t
S.text("BREAKING NEWS", l3[0] + 0.1, END, loc=(0.05, 0.215), size=40, color=(1.0, 0.3, 0.25, 1), anchor=("LEFT", "BOTTOM"))
S.text("LOCAL TEEN LIFTS CAR WITH BARE HANDS", l3[0] + 0.25, EXPERTS - 0.1, loc=(0.05, 0.13), size=58, color=WHITE, anchor=("LEFT", "BOTTOM"))
S.text("EXPERTS: \"ALMOST CERTAINLY EDITED\"", EXPERTS, END, loc=(0.05, 0.13), size=58, color=WHITE, anchor=("LEFT", "BOTTOM"))

# ---------------------------------------------------------------- acteren
S.beat(anchor, 0.0, "staan", face="neutraal", face_amt=0.6, look=(0, 0))
S.beat(anchor, l3[0] + 0.5, "staan", face="zelfverzekerd", face_amt=0.5, look=(0, 0), body={"head": (0, 0, 4)})
S.beat(anchor, l3[0] + 2.2, "staan", face="verbaasd", face_amt=0.5, look=(0, 0), body={"head": (-4, 0, -3)})
S.beat(anchor, EXPERTS - 0.3, "armen_over", amount=0.6, face="twijfel", face_amt=0.7, look=(0, 0), body={"head": (0, 0, 8)})
S.beat(anchor, l3[1] - 0.6, "armen_over", amount=0.6, face="zelfverzekerd", face_amt=0.6, look=(0, 0), body={"head": (3, 0, 0)}, wenkbrauw_op=0.6)
S.hold(anchor, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((AT.x + 1.6, -5.5, 2.6), (AT.x + 0.4, 4.0, 1.6), 26), ((AT.x + 1.2, -4.5, 2.4), (AT.x + 0.4, 4.0, 1.6), 30))
S.cam(l3[0] + 1.6, S.shot(anchor, l3[0] + 2.0, "mcu", az=0, lens=34, lr=-0.35), S.shot(anchor, END, "mcu", az=0, lens=38, lr=-0.35))

S.finish(length=END)
