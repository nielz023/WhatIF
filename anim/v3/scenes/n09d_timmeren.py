"""N09d · Dag 3: papa timmert een plank voor het raam (script scène 9d), voorkant van het huis, grijze ochtend.
Hamer in de rechterhand: anticipatie (hamer naar achter), slag, hamer stuitert terug. Plank tegen het kozijn.
VO: "Families start to hide what they have."

    blender -b -P anim/v3/scenes/n09d_timmeren.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n09d", "straat", "grijs", exposure=0.0)
sh = S.cuts([3.6])
END = sh[-1][1]

for o in list(bpy.data.objects):
    if o.name.startswith(("Vuilniswagen", "Kraai", "Plastic_zak", "Raamtekst", "Koplamp")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- planken voor het voorraam (x = 1.2, gevel y = 12.93)
WX, WY = 1.2, 12.86
PL = S.mat("plank_steigerhout", (0.62, 0.48, 0.32))
NAIL = S.mat("spijker", (0.55, 0.55, 0.58))
for k, (z, rx) in enumerate(((1.15, 4), (1.5, -3))):
    T.box(f"Raamplank_{k}", (WX, WY, z), (2.2, 0.035, 0.18), PL, rot=(0, rx, 0), base=False, bevel=0.005, ol=0.004)
    for sx in (-0.95, 0.95):
        T.cyl(f"Raamplank_spijker_{k}_{sx}", (WX + sx, WY - 0.02, z), 0.008, 0.01, NAIL, rot=(90, 0, 0), seg=8, ol=0)
ZP = 1.84
T.box("Raamplank_nieuw", (WX, WY, ZP), (2.2, 0.035, 0.18), PL, rot=(0, -2, 0), base=False, bevel=0.005, ol=0.004)
NX = WX + 0.95                                              # de spijker rechts, waar hij op slaat
spijker = T.cyl("Spijker_nieuw", (NX, WY - 0.06, ZP), 0.006, 0.07, NAIL, rot=(90, 0, 0), seg=8, ol=0)

# ---------------------------------------------------------------- hamer (steel langs lokaal z, kop bovenaan)
hm = [T.cyl("Hamer_steel", (0, 0, -0.06), 0.014, 0.3, S.mat("hamer_steel", (0.55, 0.36, 0.2)), seg=10, ol=0),
      T.box("Hamer_kop", (0, 0, 0.24), (0.13, 0.035, 0.035), S.mat("hamer_kop", (0.25, 0.26, 0.28)), base=False, bevel=0.006, ol=0)]
hamer = T.merge("Hamer", hm, ol=0.003)

# ---------------------------------------------------------------- papa
# hij staat op een krat dicht bij de gevel: met zijn korte armen haalt hij de bovenste plank anders niet
KZ = 0.25
T.box("Krat", (WX + 0.45, WY - 0.44, 0.12), (0.5, 0.36, KZ), S.mat("krat_rood", (0.62, 0.12, 0.1)), bevel=0.01, ol=0.004)
papa = S.actor("papa", (WX + 0.45, WY - 0.44, 0.12 + KZ), 180)
S.beat(papa, 0.0, "staan", face="vastberaden", face_amt=0.7, at=V(NX, WY, ZP))
# linkerhand houdt de plank tegen het kozijn
S.reach(papa, 0.0, "L", V(WX + 0.1, WY - 0.06, ZP - 0.07))
S.reach(papa, END, "L", V(WX + 0.1, WY - 0.06, ZP - 0.07))
HIT = V(NX - 0.05, WY - 0.3, ZP - 0.08)                     # pols bij de slag (hamerkop op de spijker)
UPP = V(NX - 0.03, WY - 0.57, ZP + 0.02)                    # pols bij de anticipatie (naast het hoofd, naar achter)
S.reach(papa, 0.0, "R", HIT + V(0, -0.1, 0.05))
HITS = (0.75, 1.45, 2.15, 2.85)
for k, th in enumerate(HITS):
    S.reach(papa, th - 0.32, "R", UPP)
    S.reach(papa, th, "R", HIT)
    S.reach(papa, th + 0.12, "R", HIT + V(0, -0.08, 0.14))          # stuitert terug
    S.sfx("sfx_hamer_spijker", th, 0.3)
    spijker.location.y = WY - 0.06 + 0.012 * k
    spijker.keyframe_insert("location", frame=F(th) - 1)
    spijker.location.y = WY - 0.06 + 0.012 * (k + 1)
    spijker.keyframe_insert("location", frame=F(th))
    S.beat(papa, th, "staan", face="inspanning", face_amt=0.7, at=V(NX, WY, ZP), body={"spine": (4, 0, 0)})
    S.beat(papa, th + 0.3, "staan", face="vastberaden", face_amt=0.6, at=V(NX, WY, ZP), body={"spine": (0, 0, 0)})
S.reach(papa, END, "R", UPP + V(0, 0.1, -0.2))
S.hold(papa, END)

# de hamer volgt de rechterhand; de kop wijst bij de anticipatie omhoog/naar achter en bij de slag naar de spijker
DIRS = [(0.0, V(0, 1, 0.4))]
for th in HITS:
    DIRS += [(th - 0.32, V(0, -0.35, 1)), (th, V(0, 1, -0.1)), (th + 0.12, V(0, 0.6, 0.6))]
DIRS.append((END, V(0, 0.3, 1)))


def head_dir(t):
    for (ta, da), (tb, db) in zip(DIRS, DIRS[1:]):
        if ta <= t <= tb:
            return da.normalized().lerp(db.normalized(), (t - ta) / max(1e-4, tb - ta)).normalized()
    return DIRS[-1][1].normalized()


hamer.rotation_mode = "QUATERNION"
for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    hp = (S.bone_world(papa, "hand.R", t, tail=False) + S.bone_world(papa, "hand.R", t)) / 2
    d = head_dir(t)
    hamer.location = hp + d * 0.04
    hamer.rotation_quaternion = d.to_track_quat("Z", "X")
    hamer.keyframe_insert("location", frame=f)
    hamer.keyframe_insert("rotation_quaternion", frame=f)

# ---------------------------------------------------------------- camera: handheld medium, schuin van opzij
S.cam(0.0, ((WX + 2.9, WY - 1.25, 1.95), (WX + 0.35, WY - 0.45, 1.8), 30), ((WX + 2.7, WY - 1.15, 1.95), (WX + 0.35, WY - 0.45, 1.8), 32), handheld=0.35)

S.counter("DAY 3", 0, t0=0.0)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.03)
S.say("N09-03", at=0.6)
S.finish(length=END, tail=0.0)
