"""S20a · Dag 19 · de schoolgang: 'You go back to school one last time. Not for class. To say goodbye.'
Iedereen bij de kluisjes stopt met praten en kijkt; hij loopt tot de deur van het lokaal.

    blender -b -P anim/scenes/s20a_gang.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s20a", "school", "gang")

START = V(0.25, 6.6, 0)
DOOR_AT = V(-1.35, 0.72, 0)                    # voor de lokaaldeur (linkermuur), kijkt naar -x
HANDLE = V(-1.9, 1.05, 1.0)
held = S.actor("hoofdpersonage", START, 0)

# leerlingen bij de kluisjes: (plek, kant van hun kluisje, wanneer ze hem zien)
KIDS = [((1.2, 5.3), 1, 0.7), ((-1.2, 4.4), -1, 1.0), ((1.15, 3.1), 1, 1.5), ((-1.15, -1.3), -1, 2.2),
        ((1.1, -0.2), 1, 2.0), ((0.95, -4.2), 1, 2.8), ((-1.0, -3.4), -1, 2.6)]
kids = []
for k, ((x, y), side, _) in enumerate(KIDS):
    kids.append(S.extra(k, (x, y, 0), 90 if side > 0 else -90, energy=0.8))

# ---------------------------------------------------------------- tijdlijn
S.hud(19, "524,288x STRONGER", t0=0.4)
S.ambience("sfx_binnen_sfeer", 0.0, 30, vol=0.07)
S.ambience("sfx_klas_geroezemoes", 0.0, 1.9, vol=0.05)      # het geroezemoes valt stil als ze hem zien
S.music("piano_hol", 0.3, 30, vol=0.22, fade_in=1.0, fade_out=1.0)
l1 = S.say("S20-01", gap=0.8)
BACK = l1[0] + 1.5                             # 'You go back to school one last time.'
NOT_CLASS = l1[0] + 4.02
GOODBYE = l1[0] + 5.24
S.wait(1.2)
END = S.t

# ---------------------------------------------------------------- hij: rustig, beetje omlaag kijkend, tot de deur
S.beat(held, 0.0, "ontspannen", face="verdrietig", face_amt=0.4, look=(0, -0.2), body={"head": (6, 0, 0)})
ARRIVE = GOODBYE - 0.5
S.walk(held, 0.3, ARRIVE, [START, V(0.15, 3.4, 0), V(-0.55, 1.6, 0), DOOR_AT], stride=0.5, arms=0.3, end_rot=-90)
S.beat(held, 1.6, "ontspannen", face="verdrietig", face_amt=0.5, look=(-0.6, 0), face_only=True)
S.beat(held, 2.6, "ontspannen", face="nerveus", face_amt=0.5, look=(0.6, -0.1), face_only=True)
S.beat(held, NOT_CLASS - 0.3, "ontspannen", face="verdrietig", face_amt=0.5, look=(0, -0.4), face_only=True)
S.beat(held, ARRIVE + 0.1, "staan", face="verdrietig", face_amt=0.6, at=HANDLE + V(0, -0.2, 0.55))
S.reach(held, GOODBYE, "R", None, inf=0.0)
S.reach(held, GOODBYE + 0.5, "R", HANDLE, inf=1.0)
S.beat(held, GOODBYE + 0.6, "staan", face="verdrietig", face_amt=0.7, at=HANDLE + V(0, -0.3, 0.6), body={"head": (8, 0, 0)})
S.beat(held, END - 0.4, "staan", face="verdrietig", face_amt=0.8, look=(0, -0.3), body={"head": (14, 0, 0)}, mond_verdrietig=0.4)
S.hold(held, END)

# ---------------------------------------------------------------- de leerlingen: praten, zien hem, deinzen terug
TALK = ["lach", "blij", "grijns", "lach", "blij", "grijns", "blij"]
SEEN = ["bang", "nerveus", "geschrokken", "nerveus", "bang", "nerveus", "bang"]
for k, (ch, ((x, y), side, tn)) in enumerate(zip(kids, KIDS)):
    here = V(x, y, 0)
    S.place(ch, 0.0, here, 90 if side > 0 else -90)
    S.beat(ch, 0.0, "ontspannen", face=TALK[k], face_amt=0.6, look=(0.3 * side, 0))
    S.beat(ch, tn - 0.5, "ontspannen", face=TALK[k], face_amt=0.4, look=(-0.4 * side, 0), body={"head": (0, -side * 25, 0)})
    # omdraaien naar de gang, met de rug tegen de kluisjes
    back = here + V(side * 0.18, 0, 0)
    S.turn(ch, tn, tn + 0.6, heading(back, S.head(held, tn + 0.6)), loc=back)
    S.beat(ch, tn + 0.15, "schrik", amount=0.35, face=SEEN[k], face_amt=0.9, at=S.head(held, tn + 0.15))
    for t in frange(tn + 0.8, END, 0.9):
        pose = "armen_over" if k % 3 == 0 else ("handen_zij" if k % 3 == 1 else "staan")
        S.beat(ch, t, pose, amount=0.8, face=SEEN[k], face_amt=0.8, at=S.head(held, t), crouch=(0.03, -4))
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
# 1 · laag en breed door de gang: hij komt op ons af, de gang valt stil
S.cam(0.0, ((0.55, -6.6, 0.9), (0.0, 6.0, 1.35), 30), ((0.5, -5.9, 0.95), (0.0, 6.0, 1.35), 32))
# 2 · rijdend voor hem uit
def track(dy, dz, dx=0.18):
    return lambda t: tuple(S.head(held, min(t, ARRIVE - 1.0)) + V(dx, dy, dz))
S.cam(BACK, (track(-2.5, -0.05, 0.25), track(0.0, -0.22, 0.0), 32))
# 3 · een van de leerlingen, ingedrukt tegen zijn kluisje
kc = kids[4]
KH = S.head(kc, NOT_CLASS)
S.cam(NOT_CLASS - 0.15, (V(-0.35, KH.y - 1.5, KH.z + 0.05), KH + V(0, 0, -0.15), 36), (V(-0.25, KH.y - 1.3, KH.z + 0.05), KH + V(0, 0, -0.12), 40))
# 4 · bij de deur, in profiel, langzaam dichterbij
S.cam(GOODBYE - 0.1, ((-1.2, -1.3, 1.45), (-1.55, 0.85, 1.3), 30), ((-1.25, -1.0, 1.45), (-1.55, 0.85, 1.32), 33))

S.finish(length=END)
