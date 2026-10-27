"""S03a · Dag 1 · badkamer: de tandpasta belandt op de spiegel.

    blender -b -P anim/scenes/s03a_badkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s03a", "badkamer", "binnen")

SX, D = -0.55, 2.5
SPOT = V(SX + 0.02, 0.48, 0)                 # voor de wastafel, kijkt naar de spiegel (+y)
MIRROR_Y = D / 2 - 0.06
SPLAT = V(SX - 0.04, MIRROR_Y, 1.42)

held = S.actor("hoofdpersonage", SPOT, 180)

# tandpasta dichter bij de rand van het blad, tandenborstel al in zijn rechterhand
tube = S.obj("Tandpasta")
tube.location = (SX - 0.22, D / 2 - 0.42, 0.885)
tube.rotation_euler = (0, 0, math.radians(80))
brush = S.obj("Tandenborstel_1")
for o in bpy.data.objects:
    if o.name.startswith("Plafondlamp"):
        o.hide_render = True

# ---------------------------------------------------------------- tijdlijn
S.hud(1, "2x STRONGER", t0=0.15, tick=False)
S.music("speels", 0.0, 9.0, vol=0.30, fade_in=0.2, start=21.0)
S.ambience("sfx_binnen_sfeer", 0.0, 9.0, vol=0.04)
l1 = S.say("S03-01", gap=0.5)
SQ = l1[0] + 2.75                             # het knijpen
S.sfx("sfx_tandpasta", SQ + 0.12 - 0.7, 0.9)        # de klets zit op 0,7 s
S.wait(1.6)

# ---------------------------------------------------------------- acteren
HANDS = SPOT + V(0, 0.36, 1.02)
S.beat(held, 0.0, "ontspannen", face="neutraal", face_amt=0.6, look=(0, -0.2), body={"head": (8, 0, 0)})
grab(S, brush, held, 0.0, "hand.R", (0, 0.02, 0.0), (90, 0, 0))
# pakt de tube
S.beat(held, l1[0] + 0.3, "staan", face="neutraal", at=tube.location, crouch=(0.03, 12))
S.reach(held, l1[0] + 0.2, "L", None, 0.0)
S.reach(held, l1[0] + 0.8, "L", tube.location + V(0, 0, 0.05), 1.0)
grab(S, tube, held, l1[0] + 0.85, "hand.L", (0, 0.03, 0), (0, 0, 90))
# beide handen voor de borst, tube en borstel tegen elkaar
S.reach(held, l1[0] + 1.5, "L", HANDS + V(-0.08, 0, 0), 1.0)
S.reach(held, l1[0] + 0.8, "R", None, 0.0)
S.reach(held, l1[0] + 1.5, "R", HANDS + V(0.10, 0, -0.02), 1.0)
S.beat(held, l1[0] + 1.5, "staan", face="blij", face_amt=0.3, at=HANDS, crouch=(0.02, 6))
S.hold(held, SQ - 0.15)
S.reach(held, SQ - 0.15, "L", HANDS + V(-0.08, 0, 0), 1.0)
S.reach(held, SQ - 0.15, "R", HANDS + V(0.10, 0, -0.02), 1.0)
# knijpen: de hele tube spuit leeg
S.reach(held, SQ + 0.05, "L", HANDS + V(-0.06, 0.03, 0.01), 1.0)
S.beat(held, SQ + 0.05, "schrik", amount=0.3, face="geschrokken", crouch=(0.0, -6), body={"head": (-8, 0, 0)})
S.reach(held, SQ + 0.6, "L", HANDS + V(-0.1, -0.05, 0.03), 1.0)
S.reach(held, SQ + 0.6, "R", HANDS + V(0.12, -0.05, 0.02), 1.0)
S.beat(held, SQ + 0.9, "staan", face="verbaasd", face_amt=0.8, at=SPLAT, crouch=(0.0, -4))
# kijkt van de spiegel naar de lege tube, dan naar ons
S.beat(held, SQ + 1.8, "staan", face="twijfel", face_amt=0.7, at=HANDS + V(-0.08, 0, 0))
S.reach(held, SQ + 1.8, "L", HANDS + V(-0.06, -0.08, 0.1), 1.0)
S.beat(held, l1[1] + 0.4, "staan", face="nerveus", face_amt=0.8, look=(0.6, 0.1), body={"head": (0, -28, 0), "neck": (0, -12, 0)})
S.hold(held, l1[1] + 1.6)

# de tube wordt plat
key(tube, SQ - 0.1, scale=(1, 1, 1))
key(tube, SQ + 0.08, scale=(1.05, 1, 0.25))

# de straal tandpasta: wit-blauwe druppels van de tube naar de spiegel
paste = S.mat("tandpasta_wit", (0.97, 0.97, 1.0))
blue = S.mat("tandpasta_blauw", (0.25, 0.5, 0.95))
NOZ = HANDS + V(-0.03, 0.08, 0.02)
for k in range(14):
    o = T.sphere(f"Pasta_{k}", (0, 0, 0), 0.018 + 0.006 * (k % 3), blue if k % 4 == 1 else paste, scale=(1, 1.8, 1), seg=10, ol=0.002)
    t0 = SQ + k * 0.012
    t1 = t0 + 0.12
    tgt = SPLAT + V(((k * 37) % 9 - 4) * 0.025, -0.02, ((k * 53) % 7 - 3) * 0.03)
    key(o, t0 - 1 / FPS, loc=NOZ, scale=0.001)
    key(o, t0, loc=NOZ, scale=1.0)
    key(o, t1, loc=tgt, scale=(1.4, 0.2, 1.4))
    key(o, t1 + 0.8, loc=tgt + V(0, 0, -0.06), scale=(1.2, 0.2, 1.8))
# de klodder op de spiegel, met druipers
blob = T.sphere("Pasta_klodder", tuple(SPLAT), 0.11, paste, scale=(1.3, 0.12, 1.0), seg=20, ol=0.004)
key(blob, SQ + 0.08, scale=0.001)
key(blob, SQ + 0.18, scale=(1.3, 0.12, 1.0))
stripe = T.sphere("Pasta_streep", tuple(SPLAT + V(0.03, -0.012, 0.01)), 0.06, blue, scale=(1.6, 0.1, 0.35), rot=(0, 20, 0), seg=14, ol=0.002)
key(stripe, SQ + 0.08, scale=0.001)
key(stripe, SQ + 0.2, scale=(1.6, 0.1, 0.35))
for k, (dx, ln) in enumerate(((-0.08, 0.16), (0.02, 0.24), (0.09, 0.12))):
    d = T.sphere(f"Pasta_druiper{k}", tuple(SPLAT + V(dx, -0.008, -0.06)), 0.018, paste, scale=(1, 0.5, 1), seg=8, ol=0.002)
    key(d, SQ + 0.3, loc=SPLAT + V(dx, -0.008, -0.06), scale=0.001)
    key(d, SQ + 0.5, loc=SPLAT + V(dx, -0.008, -0.07), scale=(1, 0.5, 1))
    key(d, l1[1] + 1.5, loc=SPLAT + V(dx, -0.008, -0.06 - ln), scale=(1, 0.5, 1 + ln * 6))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.3, -2.6, 1.65), (SX, 0.7, 1.15), 24), ((0.25, -2.2, 1.6), (SX, 0.7, 1.2), 26))
S.cam(l1[0] + 1.2, ((0.12, 0.78, 1.0), HANDS + V(-0.02, 0.02, 0.0), 30), ((0.06, 0.8, 0.98), HANDS + V(-0.02, 0.02, 0.0), 34), dof=3.5)
S.cam(SQ + 0.02, ((0.18, 0.25, 1.68), SPLAT + V(0.05, 0, -0.08), 28),
      ((0.15, 0.3, 1.66), SPLAT + V(0.05, 0, -0.08), 30), shake=lambda t: max(0.0, 1.2 - (t - SQ) * 3))
S.cam(SQ + 1.6, S.shot(held, SQ + 1.6, "cu", az=-14, lens=18, dist=0.66, h=0.0),
      S.shot(held, SQ + 3.0, "cu", az=-20, lens=19, dist=0.64, h=0.0))

S.finish(tail=0.4)
