"""S17d · Dag 16 · het avondnieuws: 'Tonight, questions about whether this teenager is a hero… or a threat.'

    blender -b -P anim/scenes/s17d_nieuws.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s17d", "tvstudio", "studio")

AT = V(-0.9, 2.6, 0.35)                      # voor het decor, naar de camera
anchor = S.actor("nieuwslezeres", AT, 0, energy=1.0)
S.obj("Showlogo_2").data.body = "HERO?"
S.obj("Showlogo_sub").data.body = "OR THREAT?"
for o in bpy.data.objects:
    if o.name.startswith("Tvcamera_2"):
        o.hide_render = True

# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_binnen_sfeer", 0.0, 30, vol=0.06)
S.music("drone", 0.0, 30, vol=0.24, fade_in=0.2, fade_out=1.2)
l13 = S.say("S17-13", who=anchor, gap=0.5, gain=1.2)
THREAT = l13[0] + 3.83                       # '...or a threat.'
S.wait(1.2)
END = S.t
S.text("BREAKING NEWS", l13[0] + 0.1, END, loc=(0.05, 0.215), size=40, color=(1.0, 0.3, 0.25, 1), anchor=("LEFT", "BOTTOM"))
S.text("TEEN STOPS ROLLER COASTER WITH STEEL RAIL", l13[0] + 0.25, THREAT - 0.1, loc=(0.05, 0.13), size=56, color=WHITE,
       anchor=("LEFT", "BOTTOM"))
S.text("HERO... OR THREAT?", THREAT, END, loc=(0.05, 0.13), size=64, color=WHITE, anchor=("LEFT", "BOTTOM"))

# ---------------------------------------------------------------- acteren
S.beat(anchor, 0.0, "staan", face="neutraal", face_amt=0.7, look=(0, 0))
S.beat(anchor, l13[0] + 0.4, "staan", face="neutraal", face_amt=0.9, look=(0, 0), body={"head": (-3, 0, 0)}, wenkbrauw_op=0.3)
S.beat(anchor, THREAT - 0.4, "staan", face="twijfel", face_amt=0.6, look=(0, 0), body={"head": (4, 0, 5)})
S.beat(anchor, THREAT + 0.6, "staan", face="nerveus", face_amt=0.5, look=(0, 0), body={"head": (6, 0, 4)})
S.hold(anchor, END)

# ---------------------------------------------------------------- camera: langzame push-in, serieus
S.cam(0.0, S.shot(anchor, 0.0, "med", az=0, lens=32, lr=-0.35), S.shot(anchor, END, "mcu", az=0, lens=40, lr=-0.35))

S.finish(length=END)
