"""D13j · Straat beneden, 2200 (script scène 13j).
13j  WIDE 3 s: een krater in de stoep. Mensen van 2200 kijken op van hun hologramtelefoons.
     Hij staat op, kraakt zijn nek, en loopt gewoon weg tussen de mensen.
     VO: "You'll still feel everything. But nobody can keep you."

    python3 anim/v4/scenes/d13j_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d13j", "toekomst", "straat2200", exposure=0.15)
sh = S.cuts([4.4])
END = sh[-1][1]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

SW = 0.15                                                  # stoep
KR = V(10.5, 4.0, 0.13)                                    # krater


def face(p, q):
    """rotatie (graden) waarmee iemand op p naar q kijkt (facing = (sin r, -cos r))."""
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


# ---------------------------------------------------------------- stof dat nog neerdaalt
for t in (0.0, 0.25):
    S.puff(KR + V(0.6, 0.6, 0.1), t, n=5, r=(0.25, 0.55), grow=1.6, dur=1.4, color=(0.78, 0.78, 0.80), rise=1.2, spread=1.6)

# ---------------------------------------------------------------- hij: zit geknield in de krater, staat op, kraakt zijn nek, loopt weg
CAMP = V(8.4, -1.9, 1.45)
held = S.actor("hoofdpersonage_2200", KR, face(KR, CAMP))
DOWN = arms(arm("L", (0.30, 0.45, -0.85), (0.15, 0.55, -0.82)), arm("R", (0.30, 0.45, -0.85), (0.15, 0.55, -0.82)))
S.beat(held, 0.0, "staan", arms=DOWN, crouch=(0.38, 34), face="inspanning", face_amt=0.7, body={"head": (-25, 0, 0)})
S.beat(held, 0.7, "staan", arms=DOWN, crouch=(0.36, 30), face="inspanning", face_amt=0.7, body={"head": (-20, 0, 0)})
S.beat(held, 1.45, "staan", crouch=(0.0, 0), face="neutraal", face_amt=0.5, at=CAMP + V(0, 0, -0.2))
S.beat(held, 1.85, "staan", face="inspanning", face_amt=0.5, body={"head": (0, 0, 22)})          # nek kraken: links
S.beat(held, 2.15, "staan", face="inspanning", face_amt=0.5, body={"head": (0, 0, -22)})         # en rechts
S.beat(held, 2.45, "staan", face="zelfverzekerd", face_amt=0.6, body={"head": (0, 0, 0)})
S.eyes_closed(held, 1.8, 2.3)
PATH = [KR, V(10.4, 6.6, SW), V(10.7, 10.6, SW)]
S.walk(held, 2.65, END + 0.6, PATH, stride=0.42)
S.hold(held, END)

# ---------------------------------------------------------------- mensen van 2200 met hologramtelefoons
PHONE = arms(arm("R", (0.22, 0.30, -0.92), (0.05, 0.92, 0.38)))
mensen = []
for k, (name, p) in enumerate([("mens_2200_a", (13.3, 2.0)), ("mens_2200_b", (12.8, 7.9)), ("toekomst_a", (8.6, 8.9)),
                               ("toekomstvrouw", (14.6, 5.1)), ("toekomst_b", (13.9, -0.4))]):
    P_ = V(p[0], p[1], SW)
    r0 = face(P_, KR) + (25 if k % 2 else -25)                       # eerst half weggedraaid, naar hun telefoon
    ch = S.actor(name, P_, r0)
    mensen.append(ch)
    tel = T.box(f"Holotelefoon_{k}", (0, 0, 0), (0.07, 0.01, 0.12),
                ND.pbr(f"holo_tel_{k}", (0.36, 0.92, 1.0), emit=(0.36, 0.92, 1.0), strength=6.0), bevel=0, ol=0)
    grab(S, tel, ch, 0.0, "hand.R", loc=(0, 0.08, 0.03), rot=(0, 0, 0))
    S.beat(ch, 0.0, "staan", arms=PHONE, face="neutraal", face_amt=0.4, body={"head": (-28, 0, 0)})
    tl = 0.35 + 0.12 * k                                                # kijken op, één voor één
    S.beat(ch, tl, "staan", arms=PHONE, face="verbaasd", face_amt=0.9, at=KR + V(0, 0, 0.6))
    S.place(ch, tl, P_, r0)
    S.place(ch, tl + 0.3, P_, face(P_, KR))
    S.beat(ch, 1.6, "staan", arms=PHONE, face="geschrokken", face_amt=0.8, at=S.head(held, 1.6))
    S.beat(ch, 3.4, "staan", arms=PHONE, face="verbaasd", face_amt=0.8, at=S.head(held, 3.4))
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, (CAMP, KR + V(0.2, 1.2, 0.7), 28), (CAMP + V(0.25, 0.6, 0.0), KR + V(0.1, 3.4, 0.9), 28))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2200, t0=0.0, tick=False)
S.say("D13-07", at=0.35)
S.sfx("sfx_grond_kruimelt", 0.0, 0.25)
S.sfx("sfx_knokkels", 1.85, 0.35)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.08)
S.ambience("sfx_hologram", 0.0, END, vol=0.04)
S.music("m_spanning_puls", 0.0, END, vol=0.12, fade_in=0.0, fade_out=1.2)
S.finish(length=END, tail=0.0)
