"""OR2c · What if everyone disappeared except you? · slaapkamer 's nachts, regel 5-6.

5  DAY 7: jij zit aan je bureau en draait aan een oude radio. Ruis... en dan eindelijk een stem.
6  "And it's... your voice." De camera schuift vanaf de radio naar je gezicht; de gloed van de radio pulseert mee.

    python3 anim/shorts/or2c_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or2", "c", "slaapkamer", "nacht", lines=(5, 6))
L = S.L
T0, END = S.t0, S.t1
W = lambda n, i: L[n][0] + S.words[f"OR2-{n:02d}"][i]["s"]

for nm in ("Laptop", "Laptop_beeld", "Schoolboek_open"):
    o = S.obj(nm)
    if o:
        o.hide_render = o.hide_viewport = True

# -- de radio op het bureau --------------------------------------------------------------------------
RX, RY, RZ = 1.72, 0.22, 0.75
body_m = S.mat("radio_hout", (0.45, 0.25, 0.12))
radio = T.box("Radio", (RX, RY, RZ), (0.2, 0.36, 0.2), body_m, bevel=0.02, ol=0.004)
T.box("Radio_luidspreker", (RX - 0.101, RY + 0.08, RZ + 0.03), (0.004, 0.16, 0.14), S.mat("radio_doek", (0.2, 0.17, 0.14)), bevel=0, ol=0)
dial_m = S.mat("radio_schaal", (1.0, 0.7, 0.3), 3.0)
dial = T.box("Radio_schaal", (RX - 0.102, RY - 0.09, RZ + 0.11), (0.004, 0.13, 0.05), dial_m, bevel=0, ol=0)
needle = T.box("Radio_naald", (RX - 0.105, RY - 0.14, RZ + 0.105), (0.003, 0.006, 0.05), S.mat("radio_naald", (0.8, 0.1, 0.05)), bevel=0, ol=0)
knob = T.cyl("Radio_knop", (RX - 0.1, RY - 0.09, RZ + 0.045), 0.025, 0.03, S.mat("radio_knop", (0.12, 0.1, 0.08)), rot=(0, -90, 0), seg=16, ol=0.003)
ant = T.cyl("Radio_antenne", (RX + 0.04, RY + 0.12, RZ + 0.2), 0.004, 0.35, S.mat("chroom_ant", (0.8, 0.8, 0.82)), rot=(18, 0, 0), seg=6, ol=0)
glow = T.point_light("Radio_gloed", (RX - 0.25, RY - 0.09, RZ + 0.13), color=(1.0, 0.65, 0.3), energy=6, radius=0.05)

# -- jij aan het bureau ------------------------------------------------------------------------------
CH = S.obj("Bureaustoel")
SEAT = V(CH.location.x, CH.location.y, 0) if CH else V(1.14, 0.2, 0)
held = S.actor("hoofdpersonage", SEAT, 90)
spec, rz = sit(held, seat_top=0.5, lean=6)
if rz:
    A.place(held, F(T0), (SEAT.x, SEAT.y, rz), 90)
d7 = L[5][0]
S.beat(held, T0, "staan", face="nerveus", face_amt=0.4, look=(0, -0.2), body={"head": (8, 0, 0)}, **spec)
S.reach(held, T0, "R", None, 0.0)
KN = V(RX - 0.14, RY - 0.09, RZ + 0.045)
S.reach(held, d7 + 0.2, "R", KN + V(-0.1, -0.05, 0.02))
S.reach(held, d7 + 0.5, "R", KN)
S.reach(held, W(5, 2) - 0.1, "R", KN)
S.reach(held, W(5, 4), "R", KN + V(-0.12, -0.08, -0.05))
S.reach(held, W(5, 4) + 0.35, "R", None, 0.0)
for k, tt in enumerate((d7 + 0.5, W(5, 2) - 0.1)):
    key(knob, tt, rot=(0, -90, 0) if k == 0 else (200, -90, 0))
key(needle, d7 + 0.5, loc=(RX - 0.105, RY - 0.14, RZ + 0.105))
key(needle, W(5, 2) - 0.1, loc=(RX - 0.105, RY - 0.05, RZ + 0.105))
S.beat(held, W(5, 2), "staan", face="verbaasd", face_amt=0.8, look=(0, -0.2), body={"head": (10, 0, 0), "spine": (3, 0, 0)}, **spec)
S.beat(held, W(5, 4), "staan", face="blij", face_amt=0.7, look=(0, -0.2), body={"head": (12, 0, 0), "spine": (5, 0, 0)}, **spec)
S.beat(held, L[5][1], "staan", face="blij", face_amt=0.8, look=(0, -0.2), body={"head": (12, 0, 0), "spine": (5, 0, 0)}, **spec)
# regel 6: het is jouw stem
d6 = L[6][0]
S.beat(held, W(6, 1), "staan", face="verbaasd", face_amt=0.7, look=(0, -0.2), body={"head": (10, 0, 0), "spine": (4, 0, 0)}, **spec)
S.beat(held, W(6, 2), "staan", face="geschrokken", face_amt=1.0, look=(0, -0.2), body={"head": (4, 0, 0), "spine": (0, 0, 0)}, **spec)
S.beat(held, END, "staan", face="bang", face_amt=1.0, look=(0, -0.2), body={"head": (2, 0, 0), "spine": (-4, 0, 0)}, **spec)
held.frozen = W(6, 2) + 0.4                # verstijfd: geen ademen/knipperen meer

# gloed: rustig bij ruis, pulseert op de stem
e = 6
for t in frange(T0, END, 0.12):
    on = t >= W(5, 4)
    glow.data.energy = e * (1.0 + (0.6 * math.sin(t * 23) * math.sin(t * 7.3) if on else 0.15 * math.sin(t * 40)))
    glow.data.keyframe_insert("energy", frame=F(t))

# -- camera's ----------------------------------------------------------------------------------------
HEAD = S.head(held, W(5, 4)) + V(0.08, 0, 0)
# driekwart van voren, tussen jou en de muur: je gezicht in de gloed, de radio rechts in beeld
S.cam(T0, ((1.97, -0.42, 1.18), tuple(HEAD * 0.6 + V(RX, RY, 0.95) * 0.4), 22),
      ((1.97, -0.32, 1.16), tuple(HEAD * 0.65 + V(RX, RY, 0.95) * 0.35), 24))
# vanachter de radio naar je gezicht
S.cam(d6 - 0.15, ((1.98, 0.12, 1.02), tuple(HEAD + V(0, 0, -0.04)), 20),
      ((1.96, 0.14, 1.05), tuple(HEAD + V(0, 0, -0.04)), 30))

S.counter("DAY 7", d7, L[5][1])
S.sfx("sfx_radio_ruis", d7 + 0.4, 0.22, cut=W(5, 4) + 0.3)
S.sfx("sfx_cliffhanger", W(6, 2) - 0.05, 0.35)
S.ambience("sfx_krekels_nacht", T0, END, vol=0.05)
S.done()
