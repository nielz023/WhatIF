"""F13 · Outro · de keukentafel van bovenaf: de taart, de negen vlammetjes, de kring van duizend kraanvogels.
Langzaam inzoomen. 'Could YOU stay awake?' De teaser voor de volgende video (2x SMALLER) en het eindscherm
(12 seconden, ruimte voor de YouTube-elementen).

    blender -b -P anim/v2/scenes/f13_outro.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from feest import party_set  # noqa: E402

S = Scene2("f13", "keuken", "verjaardag")

TX, TY, TZ = 0.2, -0.6, 0.76
BRO_SEAT = S.obj("Stoel_4").location.copy()
CAKE = V(0.5, -0.6, TZ)
LAST_AT = V(0.5, -0.88, TZ)

O = party_set(S, ring=True)
O["cake"].location = CAKE
S.obj("Glas_water").location = (TX - 0.25, TY - 0.3, TZ)
last = S.obj("Kraanvogel_de_laatste")
last.location = LAST_AT
last.rotation_euler = (0, 0, math.radians(180))
for o in bpy.data.objects:
    if o.name.startswith("Kraanvogel_tafelrand_") and (o.location.xy - LAST_AT.xy).length < 0.15:
        o.hide_render = True
        o.hide_viewport = True
O["lighter"].location = CAKE + V(0.32, 0.22, 0.02)
O["lighter"].rotation_euler = (0, 0, math.radians(150))
O["plates"].hide_render = True                   # papa houdt ze vast, buiten beeld
for o in O["wb5"] + O["wb6"]:
    o.hide_render = False

# het broertje, bevroren, naar de kaarsjes geleund (zijn handen op tafel komen in beeld)
bro = S.actor("broertje_dino", BRO_SEAT, 0)
SIT_B, zb = sit(bro)
S.reach(bro, 0.0, "L", CAKE + V(-0.3, 0.3, 0.02))
S.reach(bro, 0.0, "R", CAKE + V(0.0, 0.32, 0.02))
S.place(bro, 0.0, BRO_SEAT + V(0, -0.06, zb), 0)
S.beat(bro, 0.0, **SIT_B, pose="ontspannen", face="blij", face_amt=0.8, at=CAKE + V(0, 0, 0.3),
       body={"spine": (16, 0, 0), "head": (6, 0, 0)}, mouth=0.0, mond_O=0.35)

# ---------------------------------------------------------------- tijdlijn
S.music("reprise", 0.0, 0, vol=0.18, fade_in=2.0, fade_out=3.0)
REP = S.sounds[-1]
l1 = S.say("F13-01", gap=1.2)
d1 = l1[1] - l1[0]
COMMENTS = l1[0] + 0.68 * d1                     # 'Tell us in the comments.'
l2 = S.say("F13-02", gap=1.0)
d2 = l2[1] - l2[0]
SMALLER = l2[0] + 0.36 * d2                      # 'What if every day... you got two times SMALLER?'
l3 = S.say("F13-03", gap=0.9)
d3 = l3[1] - l3[0]
CAREFUL = l3[0] + 0.5 * d3                       # 'be careful what you wish for.'
ENDSCREEN = l3[1] + 0.8
END = ENDSCREEN + 12.0
REP["loop_to"] = END
S.music("pizz_spanning", SMALLER - 0.2, l2[1] + 0.8, vol=0.07, fade_in=0.3, fade_out=0.8)
S.sfx("sfx_klok_tik", 0.6, 0.15, cut=(0, 0.35))

S.text("STAY AWAKE  ·  OR  ·  CLOSE YOUR EYES?", l1[0] + 0.3, l1[1] + 0.6, loc=(0.5, 0.14), size=64, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("TELL US IN THE COMMENTS", COMMENTS, l1[1] + 0.6, loc=(0.5, 0.07), size=48, color=GOLD, anchor=("CENTER", "BOTTOM"))
S.card("NEXT TIME", SMALLER - 0.3, l2[1] + 0.6, size=90, dim=0.45, sub="WHAT IF YOU GOT 2x SMALLER EVERY DAY?")
S.text("BE CAREFUL WHAT YOU WISH FOR", CAREFUL - 0.2, ENDSCREEN - 0.1, loc=(0.5, 0.14), size=60, color=WHITE, anchor=("CENTER", "BOTTOM"))
# eindscherm: links de volgende video, rechts abonneren (YouTube legt er zijn eigen knoppen overheen)
S.card("", ENDSCREEN, END + 0.5, dim=0.35, fin=20, fout=1)
S.text("WATCH NEXT", ENDSCREEN + 0.3, END, loc=(0.27, 0.78), size=60, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("SUBSCRIBE", ENDSCREEN + 0.5, END, loc=(0.75, 0.78), size=60, color=RED, anchor=("CENTER", "BOTTOM"))

# ---------------------------------------------------------------- camera: recht van boven, heel langzaam erin
S.cam(0.0, ((0.5, -0.78, 2.25), CAKE + V(0, 0, 0.05), 30), ((0.5, -0.68, 1.75), CAKE + V(0, 0, 0.05), 30), handheld=0.0)
S.cam(l2[0] - 0.2, ((0.5, -0.68, 1.75), CAKE + V(0, 0, 0.05), 30), ((0.5, -0.66, 1.5), CAKE + V(0, 0, 0.05), 32), handheld=0.0)
S.cam(ENDSCREEN - 0.3, ((0.55, -0.85, 1.85), CAKE + V(0.05, 0, 0.05), 24), ((0.55, -0.87, 1.92), CAKE + V(0.05, 0, 0.05), 24), handheld=0.0)

S.finish(length=END)
