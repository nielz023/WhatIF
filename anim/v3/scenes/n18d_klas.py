"""N18d · Jaar 1: de school is weer open (script scène 18d-18e).
18d  WIDE: oma en de wetenschapper geven les, de klas zit weer vol. Op het bord: HOW TO GROW BEANS.
18e  CLOSE: het broertje zit weer in de klas, hoofd op zijn hand. Achter hem op het bord, half uitgeveegd: NO SCHOOL FOR...
     Hij zucht diep, schouders zakken, zijn hoofd glijdt verder van zijn hand. "Worst. Day. Ever."

    blender -b -P anim/v3/scenes/n18d_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n18d", "school", "nr_jaar1", exposure=0.3)
sh = S.cuts([3.2, 4.6])
END = sh[-1][1]
t_e = sh[1][0]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

BOARD = V(-4.42, 0.4, 1.3)
WIN = V(0.3, 4.0, 1.5)                  # het broertje kijkt verveeld naar het raam

# ---------------------------------------------------------------- de klas (kijkt naar het bord, -x)
SEATS = {"broertje": (-1.12, -0.58), "kind_b": (0.38, -2.02), "zusje_pestkop": (0.38, 1.62), "figurant_d": (1.88, -0.58),
         "kind_a": (1.88, 0.18), "volgeling_c": (3.38, -2.02)}
K = {}
for n, (x, y) in SEATS.items():
    ch = S.actor(n, V(x + 0.05, y, 0), -90)
    spec, z = sit(ch, seat_top=0.46)
    ch.rig.location.z = z
    ch.rig.keyframe_insert("location", frame=1)
    ch.spec = spec
    K[n] = ch
for i, (n, ch) in enumerate(K.items()):
    if n == "broertje":
        continue
    for j, t in enumerate(frange(0.0, END, 1.3 + 0.15 * i)):
        S.beat(ch, t, face="blij" if (i + j) % 3 else "neutraal", face_amt=0.4, at=BOARD + V(0, 0, 0.2 * (j % 2)), **ch.spec)
    S.hold(ch, END)

# ---------------------------------------------------------------- oma en de wetenschapper voor de klas
oma = S.actor("oma", V(-3.65, 0.9, 0), 90)
wet = S.actor("wetenschapper", V(-3.45, -1.35, 0), 75)
male_scientist(S, wet)
S.beat(oma, 0.0, "wijzen", face="blij", face_amt=0.6, at=V(0.4, 0.0, 1.0))
S.reach(oma, 0.0, "R", BOARD + V(0.12, 0.3, 0.05))
S.reach(oma, 1.4, "R", BOARD + V(0.12, -0.2, -0.2))
S.reach(oma, 2.4, "R", BOARD + V(0.12, 0.6, -0.2))
S.beat(oma, 1.6, "staan", face="lach", face_amt=0.6, at=S.headpos(K["kind_b"], 0.0))
S.hold(oma, END)
# de wetenschapper houdt een potje met een boonplantje omhoog
pot = T.cyl("Potje_boon", (0, 0, 0), 0.07, 0.11, S.mat("terracotta", (0.78, 0.42, 0.25)), seg=14, ol=0.003)
for k in range(3):
    T.sphere(f"Boonblad_{k}", (0.02 * (k - 1), 0.0, 0.18 + 0.03 * k), 0.035, S.mat("blad_boon", (0.3, 0.7, 0.25)),
             scale=(1.4, 0.4, 0.8), seg=8, ol=0.002).parent = pot
T.cyl("Boonsteel", (0, 0, 0.1), 0.006, 0.12, S.mat("blad_boon", (0.3, 0.7, 0.25)), seg=6, ol=0).parent = pot
S.beat(wet, 0.0, "staan", face="blij", face_amt=0.6, at=S.headpos(K["broertje"], 0.0))
POT = S.headpos(wet, 0.0) + V(0.45, 0.12, -0.25)
S.reach(wet, 0.0, "R", POT)
S.reach(wet, 1.8, "R", POT + V(0.0, 0.25, 0.08))
S.reach(wet, END, "R", POT + V(0.0, 0.25, 0.08))
grab(S, pot, wet, 0.0, "hand.R", loc=(0.0, 0.0, -0.08), rot=(0, 0, 0))
S.hold(wet, END)

# ---------------------------------------------------------------- het broertje: hoofd op zijn hand, zucht, glijdt weg
bro = K["broertje"]
S.beat(bro, 0.0, face="verdrietig", face_amt=0.5, at=WIN, body={"spine": (10, 0, 0), "head": (6, 0, -8)}, **bro.spec)
HB = S.headpos(bro, 0.0)
RIGHT = V(0, 1, 0)                 # hij kijkt naar -x, zijn rechterkant is +y
CHIN = HB + RIGHT * 0.1 + V(-0.12, 0, -0.2)
S.reach(bro, 0.0, "R", CHIN)
S.reach(bro, t_e + 0.6, "R", CHIN)
# zucht: borst omhoog, dan zakt alles
S.beat(bro, t_e + 0.2, face="verdrietig", face_amt=0.6, at=WIN, body={"spine": (4, 0, 0), "head": (2, 0, -6)}, **bro.spec)
S.beat(bro, t_e + 0.9, face="verdrietig", face_amt=0.9, at=WIN, body={"spine": (16, 0, 0), "head": (10, 0, -16)}, **bro.spec)
S.reach(bro, t_e + 1.2, "R", CHIN + V(0, 0.03, -0.06))
S.say("N18-01", who=bro, at=t_e + 0.9)
S.beat(bro, t_e + 2.6, face="verdrietig", face_amt=1.0, at=WIN, body={"spine": (20, 0, 0), "head": (14, 0, -26)}, **bro.spec)
S.reach(bro, t_e + 3.0, "R", CHIN + V(0, 0.08, -0.12))
A.blink_at(bro, F(t_e + 3.4))
S.hold(bro, END)
S.reach(bro, 0.0, "L", inf=0.0)
S.sfx("sfx_adem_hijgen", t_e + 0.3, 0.12)

# ---------------------------------------------------------------- camera's
# 18d WIDE vanuit de hoek achterin: de klas, oma en de wetenschapper bij het bord
S.cam(0.0, ((3.6, -3.6, 1.9), (-2.8, 0.2, 1.0), 20), ((3.4, -3.45, 1.85), (-2.8, 0.2, 1.0), 21))
# 18e CLOSE het broertje van opzij, het half uitgeveegde bord achter hem
S.cam(t_e, ((-0.25, 0.85, 1.25), (-1.8, -0.8, 1.12), 28), ((-0.4, 0.7, 1.22), (-1.8, -0.8, 1.12), 30))

# ---------------------------------------------------------------- HUD, geluid
S.counter("YEAR 1", 212, t0=0.0)
S.ambience("sfx_klas_geroezemoes", 0.0, END, vol=0.05)
S.music("strijkers_warm", 0.0, END, vol=0.14, fade_in=0.3, fade_out=0.6)
S.finish(length=END, tail=0.0)
