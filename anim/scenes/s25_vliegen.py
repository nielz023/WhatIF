"""S25 · Dag 26-30 · 's nachts in de woestijn. Zijn klappen klinken als donder; dat geeft hem een idee. Hij duwt
op de lucht, het zand spat in een ring weg, en hij zwemt omhoog de sterrenhemel in. Van boven ziet hij zijn stad, 200 km verderop.

    blender -b -P anim/scenes/s25_vliegen.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s25", "woestijn", "nachtlucht")

LAUNCH = V(6.0, -25.0, 0.0)
CITY = V(-600.0, 2600.0, 10.0)
SAND = (0.90, 0.80, 0.62)

held = S.actor("hoofdpersonage", LAUNCH, 180, energy=1.4)
T.point_light("Maanlicht_held", tuple(LAUNCH + V(-3, 2, 4)), color=(0.7, 0.8, 1.0), energy=60, radius=1.0)

# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_wind_hoog", 0.0, 80, vol=0.06)
S.music("piano_zacht", 0.0, 0, vol=0.18, fade_in=1.0, fade_out=1.5)
PIANO = S.sounds[-1]
l1 = S.say("S25-01", gap=0.6)
D26, D28 = l1[0] + 1.72, l1[0] + 3.11
CLAP = l1[0] + 4.6                             # 'Your claps sound like thunder.'
l2 = S.say("S25-02", gap=0.4)
l3 = S.say("S25-03", gap=0.7)
D30 = l3[0]
l4 = S.say("S25-04", gap=0.7)
RAISE = l4[0] + 1.6
PUSH = l4[0] + 3.13                            # 'and push down.'
l5 = S.say("S25-05", gap=0.5)
THICK = l5[0] + 3.84
SWIM = l5[0] + 10.49                           # 'You swim.'
l6 = S.say("S25-06", gap=0.9)
HELI = l6[0] + 1.86
l7 = S.say("S25-07", gap=0.7)
FLYING = l7[0] + 4.03                          # 'You're flying.'
l8 = S.say("S25-08", gap=1.6)
FAR = l8[0] + 3.69
SMALL = l8[0] + 7.6
S.wait(2.0)
END = S.t
PIANO["loop_to"] = RAISE
S.music("opbouw_vliegen", RAISE - 0.5, 0, vol=0.24, fade_in=1.5, fade_out=1.5)
BUILD = S.sounds[-1]
BUILD["loop_to"] = FLYING - 0.2
S.music("orkest_held", FLYING - 0.6, l8[0] + 2.0, vol=0.26, fade_in=0.8, fade_out=3.0)
S.music("piano_zacht", l8[0] + 1.0, END + 0.4, vol=0.18, fade_in=2.0, fade_out=1.5, start=8.0)
S.sfx("sfx_klap_donder", CLAP, 0.3)
S.sfx("sfx_zand_opstijgen", PUSH, 0.3)
S.sfx("sfx_whoosh", SWIM - 0.1, 0.25)

S.hud(26, None, t0=D26, t1=D28)
S.hud(28, None, t0=D28, t1=D30 - 0.1)
S.hud(30, "1,073,741,824x STRONGER", t0=D30)
S.real(l6[0] + 0.1, l6[1] + 0.3)
S.text("HELICOPTER: AIR DOWN = LIFT UP", HELI + 0.2, l6[1] + 0.3, loc=(0.965, 0.22), size=50, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOUR ARMS: FASTER THAN ANY ROTOR", l6[0] + 4.2, l6[1] + 0.3, loc=(0.965, 0.14), size=50, color=GOLD, anchor=("RIGHT", "BOTTOM"))
for k, (t, alt) in enumerate(((SWIM + 0.4, "ALTITUDE: 10 M"), (l6[0] + 3.0, "ALTITUDE: 40 M"), (l7[0], "ALTITUDE: 90 M"), (FLYING, "ALTITUDE: 120 M"))):
    nxt = [l6[0] + 3.0, l7[0], FLYING, l8[0] + 0.5][k]
    S.gauge(alt, t, nxt - 0.05 if k < 3 else nxt, color=WHITE, size=56)
S.text("YOUR CITY: 200 KM", FAR + 0.2, SMALL - 0.2, loc=(0.965, 0.22), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- de klap als donder, het idee
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.6, look=(0, 0.3), body={"head": (-8, 0, 0)})
S.beat(held, CLAP - 0.35, "staan", face="neutraal", face_amt=0.6, arms=CLAP_A, look=(0, -0.2))
S.beat(held, CLAP, "staan", face="geschrokken", face_amt=0.6, arms=CLAP_B, look=(0, -0.2))
S.beat(held, CLAP + 0.5, "schrik", amount=0.4, face="verbaasd", face_amt=0.9, look=(0, 0))
S.beat(held, l2[0] + 0.2, "staan", face="twijfel", face_amt=0.6, arms=LOOK_HANDS, look=(0, -0.5), body={"head": (14, 0, 0)})
S.beat(held, l2[1] - 0.2, "staan", face="grijns", face_amt=0.7, look=(0, 0.6), body={"head": (-24, 0, 0)})
S.ring(LAUNCH + V(0, -0.35, 1.25), CLAP, r0=0.1, r1=9.0, dur=0.6, rot=(90, 0, 0), color=(0.8, 0.9, 1.0), strength=2.5)
S.flash(LAUNCH + V(0, -0.35, 1.25), CLAP, size=0.25, color=(0.85, 0.92, 1.0), strength=6)
S.puff(LAUNCH + V(0, 0, 0.05), CLAP, n=6, r=(0.2, 0.4), grow=2.0, dur=1.4, color=SAND, rise=0.3, spread=1.5)

# ---------------------------------------------------------------- duwen op de lucht, opstijgen
S.beat(held, D30 + 0.2, "staan", face="vastberaden", face_amt=0.6, look=(0, 0.2))
S.beat(held, RAISE, "armen_omhoog", amount=1.0, face="vastberaden", face_amt=0.8, look=(0, 0.5), body={"head": (-14, 0, 0)})
S.hold(held, PUSH - 0.08)
DOWN = arms(arm("L", (0.45, 0.1, -0.88), (0.35, 0.1, -0.93)), arm("R", (0.45, 0.1, -0.88), (0.35, 0.1, -0.93)))
UP = arms(arm("L", (0.6, 0.1, 0.78), (0.4, 0.1, 0.9)), arm("R", (0.6, 0.1, 0.78), (0.4, 0.1, 0.9)))
S.beat(held, PUSH, "staan", face="inspanning", face_amt=1.0, arms=DOWN, look=(0, -0.3), crouch=(0.06, 0))


def sand_ring(t, r, n=12, big=1.0):
    S.ring(LAUNCH + V(0, 0, 0.15), t, r0=0.5, r1=r, dur=0.9, color=(1.0, 0.92, 0.75), strength=1.6, thick=0.12)
    for k in range(n):
        a = k / n * 2 * math.pi
        S.puff(LAUNCH + V(math.cos(a), math.sin(a), 0) * 1.4, t, n=3, r=(0.3 * big, 0.6 * big), grow=2.5, dur=2.2, color=SAND,
               rise=0.6 * big, spread=1.0)
    S.debris(LAUNCH + V(0, 0, 0.1), t, n=int(30 * big), size=(0.03, 0.08), color=SAND, speed=(3.0, 8.0), up=0.6, floor=0.0, life=1.8)


sand_ring(PUSH, 14.0, big=1.2)
# zweven met korte stoten omlaag, telkens wat hoger
hover = [(PUSH, 0.0), (PUSH + 0.35, 0.35), (THICK, 0.6), (THICK + 0.6, 1.1), (l5[0] + 7.0, 1.4), (SWIM - 0.3, 2.2)]
for k, (t, z) in enumerate(hover):
    key(held.rig, t, loc=LAUNCH + V(0, 0, z), rot=(0, 0, 180))
    if k:
        S.beat(held, t - 0.25, "staan", face="verbaasd" if k < 3 else "grijns", face_amt=0.8, arms=UP, look=(0, -0.4), feet=((0.1, 0.0, 0.1), (-0.1, 0.0, 0.0)))
        S.beat(held, t, "staan", face="inspanning", face_amt=0.6, arms=DOWN, look=(0, -0.4), feet=((0.1, 0.0, 0.0), (-0.1, 0.0, 0.1)))
for t in (THICK + 0.6, l5[0] + 7.0):
    sand_ring(t, 8.0, n=8, big=0.6)

# ---------------------------------------------------------------- zwemmen door de nacht
PATH = [(SWIM, V(6, -25, 2.6)), (SWIM + 1.5, V(6, -20, 8)), (l6[0] + 3.0, V(6, 0, 40)), (l7[0], V(5, 50, 90)),
        (FLYING, V(3, 110, 118)), (l8[0] + 0.5, V(1, 160, 122)), (l8[0] + 2.0, V(0, 172, 122)), (END, V(0, 175, 122.4))]
for t, p in PATH:
    pitch = 90 if t < l8[0] + 1.5 else 0
    if t in (SWIM, SWIM + 1.5):
        pitch = 55 if t == SWIM else 70
    key(held.rig, t, loc=p, rot=(pitch, 0, 180))
A_FWD = arms(arm("L", (0.2, 0.15, 0.96), (0.1, 0.1, 0.99)), arm("R", (0.2, 0.15, 0.96), (0.1, 0.1, 0.99)))
A_OUT = arms(arm("L", (0.95, 0.15, 0.25), (0.85, 0.35, -0.3)), arm("R", (0.95, 0.15, 0.25), (0.85, 0.35, -0.3)))
A_IN = arms(arm("L", (0.5, 0.6, -0.55), (-0.45, 0.8, 0.35)), arm("R", (0.5, 0.6, -0.55), (-0.45, 0.8, 0.35)))
faces = lambda t: ("blij", 0.6) if t < l7[0] else (("lach", 0.9) if t < l8[0] else ("verbaasd", 0.5))
for k, t in enumerate(frange(SWIM, l8[0] + 1.2, 0.45)):
    f, a = faces(t)
    st = k % 3
    S.beat(held, t, "staan", face=f, face_amt=a, arms=(A_FWD, A_OUT, A_IN)[st], look=(0, 0.6), body={"head": (-30, 0, 0), "spine": (-6, 0, 0)},
           feet=(((0.12, 0.0, 0.0), (-0.12, -0.25, 0.1)), ((0.12, -0.25, 0.1), (-0.12, 0.0, 0.0)), ((0.12, 0.0, 0.0), (-0.12, 0.0, 0.0)))[st])
# boven: rechtop watertrappelen, kijken naar de stad
TREAD_A = arms(arm("L", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)), arm("R", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)))
TREAD_B = arms(arm("L", (0.8, 0.45, -0.35), (0.5, 0.8, -0.2)), arm("R", (0.8, 0.45, -0.35), (0.5, 0.8, -0.2)))
for k, t in enumerate(frange(l8[0] + 1.6, END, 0.6)):
    S.beat(held, t, "staan", face="verbaasd" if t < SMALL else "verdrietig", face_amt=0.6 if t < SMALL else 0.7,
           arms=TREAD_A if k % 2 else TREAD_B, at=CITY, feet=((0.12, 0.05, 0.06), (-0.12, -0.05, 0.0)) if k % 2 else ((0.12, -0.05, 0.0), (-0.12, 0.05, 0.06)))
# lucht die hij omlaag duwt: kegels onder hem bij elke slag
air = S.mat("lucht_wit", (0.75, 0.88, 1.0), 1.2)
for k, t in enumerate(frange(SWIM + 0.3, l7[1], 1.35)):
    M = S._root_matrix(held, t)
    c = T.cyl(S._fxname("Luchtstoot"), (0, 0, 0), 0.05, 1.0, air, r2=0.7, seg=16, ol=0)
    c.rotation_euler = M.to_euler()
    p0 = M @ V(0, 0, 0.8)
    back = (M.to_3x3() @ V(0, 0, -1)).normalized()
    key(c, t - 1 / FPS, loc=p0, scale=0.001)
    key(c, t + 0.15, loc=p0 + back * 0.8, scale=(1.0, 1.0, 1.6))
    key(c, t + 0.5, loc=p0 + back * 2.5, scale=0.001)

# ---------------------------------------------------------------- camera
HP = lambda t: S._root_matrix(held, t).translation
S.cam(0.0, ((LAUNCH.x + 6, LAUNCH.y - 8, 2.2), (LAUNCH.x, LAUNCH.y, 1.3), 30), ((LAUNCH.x + 5, LAUNCH.y - 7, 2.0), (LAUNCH.x, LAUNCH.y, 1.3), 32))
S.cam(CLAP - 0.4, S.shot(held, CLAP, "med", az=10, lens=30), S.shot(held, CLAP + 0.8, "med", az=10, lens=32),
      shake=lambda t: max(0.0, 1.6 - (t - CLAP) * 2.0) if t > CLAP else 0.0)
S.cam(l2[0] - 0.1, S.shot(held, l2[0] + 0.6, "mcu", az=15, lens=34), S.shot(held, l2[1], "mcu", az=12, lens=38))
S.cam(D30 - 0.1, ((LAUNCH.x - 12, LAUNCH.y - 18, 3.5), (LAUNCH.x, LAUNCH.y + 10, 1.5), 26), ((LAUNCH.x - 11, LAUNCH.y - 16, 3.0), (LAUNCH.x, LAUNCH.y + 10, 1.5), 28))
S.cam(RAISE - 0.3, ((LAUNCH.x + 1.6, LAUNCH.y - 3.0, 0.5), (LAUNCH.x, LAUNCH.y, 1.6), 24), ((LAUNCH.x + 1.4, LAUNCH.y - 2.8, 0.45), (LAUNCH.x, LAUNCH.y, 1.6), 24),
      shake=lambda t: max(0.0, 2.0 - (t - PUSH) * 1.5) if t > PUSH else 0.0)
S.cam(PUSH + 1.2, ((LAUNCH.x + 14, LAUNCH.y - 14, 7), (LAUNCH.x, LAUNCH.y, 1.0), 26), ((LAUNCH.x + 13, LAUNCH.y - 13, 6.5), (LAUNCH.x, LAUNCH.y, 1.4), 26))
S.cam(THICK - 0.2, None, fn=lambda t: (HP(t) + V(1.8, 3.0, 1.35), HP(t) + V(0, 0, 1.15), 30))      # van voren: zijn gezicht als de lucht dik wordt
S.cam(SWIM - 0.3, None, fn=lambda t: (HP(t) + V(5.0, -4.0, -1.0), HP(t) + V(0, 1.0, 0.5), 28))
S.cam(l6[0] + 2.0, None, fn=lambda t: (HP(t) + V(-3.5, -6.0, -6.0), HP(t) + V(0, 2.0, 0.0), 26))
S.cam(l7[0] - 0.2, None, fn=lambda t: (HP(t) + V(4.0, 4.5, 0.6), HP(t) + V(0, 0.8, 0.2), 30))
S.cam(FLYING - 0.3, None, fn=lambda t: (HP(t) + V(10, -14, 5), HP(t) + V(-4, 30, 0), 24))
S.cam(l8[0] + 1.4, None, fn=lambda t: (HP(t) + V(1.6, 2.7, 1.35), HP(t) + V(0, 0, 1.3), 32))
S.cam(FAR - 0.2, None, fn=lambda t: (HP(t) + V(1.0, -2.6, 1.8), CITY, 30))
S.cam(SMALL - 0.2, None, fn=lambda t: (HP(t) + V(1.0, -2.6, 1.8) + V(0, -(t - SMALL) * 0.9, (t - SMALL) * 0.4), CITY, 30 + (t - SMALL) * 3))

S.finish(length=END)
