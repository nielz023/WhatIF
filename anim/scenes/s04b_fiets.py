"""S04b · Dag 2 · straat: naar school fietsen, een bus inhalen, 58 km/h.

    blender -b -P anim/scenes/s04b_fiets.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s04b", "straat", "zonnig")

LANE = 5.25                 # fietspad
BUS_Y = 2.6
V_HERO = 16.0               # 58 km/h
V_BUS = 8.3                 # 30 km/h

held = S.actor("hoofdpersonage", (-60, LANE, 0), 90, energy=0.5)
bike, crank = prop_bike(S, held)
bus = prop_bus(S)

# ---------------------------------------------------------------- tijdlijn
S.hud(2, "4x STRONGER", t0=0.15, tick=False)
S.music("fiets", 0.0, 30, vol=0.32, fade_in=0.3)
S.ambience("sfx_straat_sfeer", 0.0, 30, vol=0.12)
l5 = S.say("S04-05", gap=0.5)
PASS = l5[0] + 5.3                         # 'You pass a bus.'
S.sfx("sfx_fiets_bus", PASS - 2.2, 0.75)
l6 = S.say("S04-06", gap=0.6)
S.real(l6[0], l6[0] + 9.6)
S.wait(1.2)
END = S.t

# snelheidsmeter telt op tot 58 km/h
for k, v in enumerate((19, 31, 44, 52, 58)):
    S.gauge(f"{v} km/h", l5[0] + 2.0 + k * 0.25, l5[0] + 2.25 + k * 0.25 if v != 58 else None, color=WHITE if v < 58 else GOLD)
S.text("FIT CYCLIST: 250 W", l6[0] + 1.4, l6[0] + 9.6, loc=(0.965, 0.30), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOU: 1,000 W", l6[0] + 4.0, l6[0] + 9.6, loc=(0.965, 0.22), size=56, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("= TOUR DE FRANCE SPRINT", l6[0] + 6.3, l6[0] + 9.6, loc=(0.965, 0.155), size=40, color=CYAN, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- shots en posities
# Elk shot heeft zijn eigen stuk straat (160 m), zodat hij nooit van de straat af rijdt.
SEGS = [  # (t0, x0)
    (0.0, -66.0),          # A: rijdt weg, zijwaarts meegereden
    (l5[0] + 2.9, -48.0),  # B: haalt de bus in
    (l6[0] - 0.3, -70.0),  # C: van voren, ontspannen gezicht
    (l6[0] + 3.9, -40.0),  # D: trappers en wielen laag
    (l6[0] + 6.4, -62.0),  # E: hoog en breed, schiet langs auto's
    (l6[0] + 10.2, -55.0), # F: 'on the way to math class'
]


def seg_of(t):
    k = 0
    for i, (t0, _) in enumerate(SEGS):
        if t >= t0:
            k = i
    return k


def hero_x(t):
    t0, x0 = SEGS[seg_of(t)]
    return x0 + V_HERO * (t - t0)


frames = list(range(1, F(END) + 2))
bake(held.rig, "location", frames, [(hero_x((f - 1) / FPS), LANE, 0.0) for f in frames], interp="LINEAR")
# hard snijden tussen de segmenten
for fc in A._fcurves(held.rig):
    if fc.data_path == "location":
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

# de bus rijdt alleen in shot B; daarbuiten staat hij ver weg
tB = SEGS[1][0]
bus_x = lambda t: -40.0 + V_BUS * (t - tB)
bfr = list(range(F(tB), F(SEGS[2][0]) + 1))
bus.rotation_euler.z = 0
bake(bus, "location", bfr, [(bus_x((f - 1) / FPS), BUS_Y, 0.0) for f in bfr], interp="LINEAR")
key(bus, tB - 1 / FPS, loc=(500, BUS_Y, 0), interp="CONSTANT")
key(bus, SEGS[2][0] + 1 / FPS, loc=(500, BUS_Y, 0), interp="CONSTANT")
key(bus, SEGS[2][0], loc=(bus_x(SEGS[2][0]), BUS_Y, 0), interp="CONSTANT")

# een paar rijdende auto's in shot E (hij haalt ze in)
for k, (x0, y, c) in enumerate(((-48, 1.2, (0.85, 0.2, 0.15)), (-36, -1.5, (0.2, 0.55, 0.85)), (-25, 1.2, (0.95, 0.95, 0.95)))):
    car = P.car(f"Rijdende_auto_{k}", (500, y, 0), rot=0 if y > 0 else 180, color=c)
    tE, tF = SEGS[4][0], SEGS[5][0]
    v = 11.0 if y > 0 else -12.0
    cf = list(range(F(tE), F(tF) + 1))
    bake(car, "location", cf, [(x0 + v * ((f - 1) / FPS - tE), y, 0.0) for f in cf], interp="LINEAR")
    key(car, tE - 1 / FPS, loc=(500, y, 0), interp="CONSTANT")
    key(car, tF + 1 / FPS, loc=(500, y, 0), interp="CONSTANT")

# ---------------------------------------------------------------- acteren: fietsen
ride(S, held, crank, 0.0, END, cadence=2.3)
S.beat(held, 0.0, "staan", face="blij", face_amt=0.5, look=(0, 0.1), body={"chest": (-10, 0, 0), "head": (-14, 0, 0)}, crouch=(0.07, 24))
S.beat(held, l5[0] + 2.0, "staan", face="neutraal", face_amt=0.6, look=(0, 0.1), body={"chest": (-10, 0, 0), "head": (-14, 0, 0)}, crouch=(0.07, 24))
# langs de bus: kijkt even opzij, knikt naar de buschauffeur
S.beat(held, PASS - 0.6, "staan", face="blij", face_amt=0.6, look=(-0.5, 0.1), body={"chest": (-10, 0, 0), "head": (-14, -35, 0)}, crouch=(0.07, 24))
S.beat(held, PASS + 0.6, "staan", face="zelfverzekerd", face_amt=0.5, look=(0, 0.1), body={"chest": (-10, 0, 0), "head": (-10, 0, 0)}, crouch=(0.07, 24))
S.beat(held, l6[0] + 1.0, "staan", face="blij", face_amt=0.7, look=(0, 0.1), body={"chest": (-10, 0, 0), "head": (-14, 0, 0)}, crouch=(0.07, 24))
# fluit een deuntje (mondje in O-vorm)
S.beat(held, l6[0] + 7.0, "staan", face="blij", face_amt=0.3, mouth=0.1, mond_O=0.8, look=(0.2, 0.3), body={"chest": (-10, 0, 0), "head": (-18, 8, 0)}, crouch=(0.07, 24))
S.beat(held, l6[1] - 1.5, "staan", face="blij", face_amt=0.6, look=(0, 0.1), body={"chest": (-10, 0, 0), "head": (-14, 0, 0)}, crouch=(0.07, 24))
S.hold(held, END)
# ride() zette de voeten en handen; beat() zette de voeten terug op nul: opnieuw de trapbeweging erover
ride(S, held, crank, 0.0, END, cadence=2.3)

# snelheidsstrepen in de close shots
streak = S.mat("snelheidsstreep", (1, 1, 1), 1.5)
for k in range(10):
    o = T.box(f"Streep_{k}", (0, 0, 0), (1.6 + (k % 3) * 0.6, 0.012, 0.012), streak, base=False, bevel=0, ol=0)
    o.parent = held.rig
    o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = (((k * 7) % 5 - 2) * 0.3, 1.2 + (k % 4) * 0.5, 0.3 + ((k * 3) % 7) * 0.22)
    o.rotation_euler.z = math.radians(90)
    show(o, SEGS[2][0], SEGS[3][0])

# ---------------------------------------------------------------- camera
H = lambda dx=0.0, dy=0.0, dz=0.0: (lambda t: (hero_x(t) + dx, LANE + dy, dz))
# A: zijwaarts meerijden (camera op de rijbaan, kijkt naar het noorden)
S.cam(0.0, None, fn=lambda t: (V((hero_x(t) + 1.4, LANE + 2.5, 1.1)), V((hero_x(t) - 0.1, LANE, 0.9)), 28))
# B: achter hem op het fietspad, de bus links voor hem
S.cam(SEGS[1][0], None, fn=lambda t: (V((hero_x(t) - 3.0 - (t - SEGS[1][0]) * 1.4, LANE - 0.6, 1.5)), V((hero_x(t) + 4.0, LANE - 1.2, 1.1)), 24))
# C: van voren, meerijdend
S.cam(SEGS[2][0], None, fn=lambda t: (V((hero_x(t) + 2.2, LANE - 0.6, 1.45)), V((hero_x(t), LANE, 1.2)), 32))
# D: laag bij de trappers
S.cam(SEGS[3][0], None, fn=lambda t: (V((hero_x(t) + 0.2, LANE - 1.1, 0.3)), V((hero_x(t) - 0.05, LANE, 0.32)), 30))
# E: hoog, breed
S.cam(SEGS[4][0], None, fn=lambda t: (V((hero_x(t) - 12 + (t - SEGS[4][0]) * 3, 0.8, 6.5)), V((hero_x(t) + 3, LANE - 1, 0.5)), 26))
# F: van voren, iets breder, hij zwaait
S.cam(SEGS[5][0], None, fn=lambda t: (V((hero_x(t) + 3.2 + (t - SEGS[5][0]) * 0.8, LANE - 1.6, 1.3)), V((hero_x(t), LANE, 1.0)), 28))

S.finish(length=END)
