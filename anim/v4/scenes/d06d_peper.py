"""D06d · De heetste peper (script scène 6d). Supermarkt, dag.
6d MEDIUM 3,9 s: hij eet de heetste peper van de winkel (rood bakje met doodshoofd). Hij wordt paars, tranen,
   rook uit zijn oren (cartoon).  VO: "You can't die. But you can definitely suffer."

    python3 anim/v4/scenes/d06d_peper.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d06d", "supermarkt", "nr_normaal", exposure=0.15)
sh = S.cuts([3.9])
END = sh[-1][1]

AT = V(-2.25, -3.0, 0.0)
held = S.actor("hoofdpersonage_kind", AT, 0)
HC = S.head(held)
FRONT = HC + V(0, -1.5, -0.1)

# bakje in zijn linkerhand, peper in zijn rechterhand
bak = ND.peperbakje("Peperbakje", (0, 0, 0))
grab(S, bak, held, 0.0, "hand.L", loc=(0, 0.07, 0.03), rot=(90, 0, 0))
peper = T.sphere("Peper_heet", (0, 0, 0), 0.02, S.mat("peper_rood", (0.85, 0.05, 0.03)), scale=(0.7, 0.7, 2.2), seg=12, ol=0)
steel = T.cyl("Peper_steel", (0, 0, 0.042), 0.004, 0.015, S.mat("peper_steel", (0.2, 0.55, 0.15)), seg=6, ol=0)
steel.parent = peper
grab(S, peper, held, 0.0, "hand.R", loc=(0, 0.06, 0.02), rot=(0, 0, 0))
show(peper, 0.0, 1.15)
show(steel, 0.0, 1.15)

HOLD_L = arm("L", (0.30, 0.45, -0.84), (0.05, 0.95, 0.30))
UP_R = arm("R", (0.30, 0.55, -0.78), (-0.35, 0.70, 0.62))          # peper voor zijn mond (~0,35 m voor het hoofd)
LOW_R = arm("R", (0.30, 0.40, -0.87), (0.05, 0.90, 0.40))
S.beat(held, 0.0, "staan", arms=arms(HOLD_L, LOW_R), face="zelfverzekerd", face_amt=1.0, at=FRONT)
S.beat(held, 0.45, "staan", arms=arms(HOLD_L, UP_R), face="grijns", face_amt=1.0, at=FRONT, body={"head": (4, 0, 0)})
S.beat(held, 0.9, "staan", arms=arms(HOLD_L, UP_R), face="inspanning", face_amt=0.3, at=FRONT, mouth=0.5)
S.beat(held, 1.2, "staan", arms=arms(HOLD_L, LOW_R), face="zelfverzekerd", face_amt=0.7, at=FRONT)
# het slaat toe: ogen wijd, paars, tranen, rook uit zijn oren, handen wapperen voor zijn mond
FAN_A = arms(HOLD_L, arm("R", (0.35, 0.55, -0.76), (-0.20, 0.75, 0.63)))
FAN_B = arms(HOLD_L, arm("R", (0.45, 0.50, -0.74), (0.20, 0.80, 0.56)))
S.beat(held, 1.55, "staan", arms=arms(HOLD_L, LOW_R), face="geschrokken", face_amt=1.0, at=FRONT, crouch=(0.03, -4))
for k, t in enumerate(frange(1.85, END, 0.14)):
    S.beat(held, t, "staan", arms=FAN_A if k % 2 else FAN_B, face="schreeuw", face_amt=1.0, at=FRONT,
           crouch=(0.05 + 0.02 * (k % 2), 6), body={"head": (-4, 0, 6 if k % 2 else -6)})
MOUTH = HC + V(0.04, -0.36, -0.20)
S.reach(held, 0.3, "R", None, 0.0)
S.reach(held, 0.7, "R", MOUTH + V(0.02, -0.02, 0.0))
S.reach(held, 1.0, "R", MOUTH)
S.reach(held, 1.3, "R", None, 0.0)
S.reach(held, 1.8, "R", None, 0.0)
for k, t in enumerate(frange(2.0, END, 0.14)):
    S.reach(held, t, "R", MOUTH + V(0.10 if k % 2 else -0.04, -0.06, -0.04))
S.hold(held, END)
skin_tint(held, [(0.0, 0.0), (1.5, 0.0), (2.0, 0.85)])
# tranen: druppels uit beide ogen
tm = S.mat("traan", (0.55, 0.8, 1.0), 0.6)
for side in (-1, 1):
    for j in range(4):
        d = T.sphere(f"Traan_{side}_{j}", (0, 0, 0), 0.018, tm, scale=(0.8, 0.8, 1.2), seg=10, ol=0)
        t0 = 1.9 + j * 0.45 + (0.12 if side > 0 else 0)
        p0 = HC + V(side * 0.13, -0.27, 0.0)
        key(d, 0.0, loc=tuple(p0), scale=0.001)
        key(d, t0, loc=tuple(p0), scale=0.001)
        key(d, t0 + 0.05, loc=tuple(p0), scale=1.0)
        key(d, t0 + 0.55, loc=tuple(p0 + V(side * 0.10, -0.08, -0.45)), scale=0.8)
        key(d, t0 + 0.6, loc=tuple(p0 + V(side * 0.10, -0.08, -0.48)), scale=0.001)
# rook uit zijn oren (cartoonpufjes)
for t in (2.0, 2.45, 2.9, 3.35):
    for side in (-1, 1):
        S.puff(HC + V(side * 0.36, 0.02, 0.0), t, n=4, r=(0.04, 0.08), grow=1.6, dur=0.7, color=(0.92, 0.92, 0.95),
               rise=0.35, spread=0.15)

S.cam(0.0, (V(-2.05, -5.0, 1.45), HC + V(0, 0, -0.12), 28), (V(-2.10, -4.7, 1.45), HC + V(0, 0, -0.06), 28))

S.year(2026, t0=0.0, tick=False)
S.say("D06-04", at=0.2)
S.sfx("sfx_rook_sis", 2.0, 0.3)
S.ambience("sfx_supermarkt_sfeer", 0.0, END, vol=0.08)
S.music("funky", 0.0, END, vol=0.17, fade_in=0.1, fade_out=0.2)
S.finish(length=END, tail=0.0)
