"""N03g · Detailmontage van regels die je niet meer ziet (script scène 3g, 4 x 1,5 s).
Rij bij de kassa met PLEASE QUEUE HERE, een rinkelende schoolbel, een bord SILENCE PLEASE, een hondje naast NO DOGS.
VO: "This part is real: you follow hundreds of rules every single day. You just stopped noticing them."

    blender -b -P anim/v3/scenes/n03g_details.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n03g", "supermarkt", "nr_normaal", exposure=0.2)
sh = S.cuts([1.6, 1.5, 1.5, 1.7])
END = sh[-1][1]

# ---------------------------------------------------------------- 1: de rij bij de kassa
queue = []
for k, y in enumerate((-7.6, -6.7, -5.8, -4.9, -4.0)):
    e = S.actor(["figurant_b", "figurant_d", "figurant_a", "figurant_e", "figurant_c"][k], (-10.55 + 0.08 * (k % 2), y, 0), 0)
    queue.append(e)
    for j, t in enumerate(frange(0.0, END, 0.6 + 0.08 * k)):
        S.beat(e, t, "staan" if j % 2 else "handen_zij", amount=0.6, face="neutraal" if j % 2 else "twijfel", face_amt=0.5,
               at=V(-10.0, -12.0, 1.4) if (j + k) % 3 else V(-8.0, -6.0, 1.2), body={"spine": (0, 0, 3 if (j + k) % 2 else -3)})
    S.hold(e, END)
# schuifelt een stapje op (de rij beweegt)
S.walk(queue[0], 0.3, 1.2, [V(-10.55, -7.6, 0), V(-10.55, -8.2, 0)], stride=0.3)
S.obj("Bord_PLEASE_QUEUE_HERE").rotation_euler.z = 0          # tekst naar de camera, de rij erachter
S.cam(sh[0][0], ((-13.9, -11.3, 1.55), (-10.6, -7.2, 1.3), 34), ((-13.7, -11.0, 1.53), (-10.6, -7.2, 1.3), 37), dof=4.2)

# ---------------------------------------------------------------- 2: de schoolbel (aan de achterwand)
BELL = V(6.0, 17.85, 3.0)
T.use_collection(T.collection("N03g_props"))
plaat = T.box("Schoolbel_plaat", BELL + V(0, 0.04, 0), (0.42, 0.04, 0.42), S.mat("bel_hout", (0.55, 0.36, 0.2)), bevel=0.01, ol=0.004)
kap = T.sphere("Schoolbel_kap", BELL + V(0, -0.12, 0), 0.17, S.mat("bel_rood", (0.85, 0.08, 0.06)), scale=(1, 0.55, 1), seg=24, ol=0.004)
hamer = T.sphere("Schoolbel_hamer", BELL + V(0.17, -0.18, -0.12), 0.035, P.m("metaal"), seg=12, ol=0)
for f in range(F(sh[1][0]), F(sh[1][1]) + 1):
    hamer.location = BELL + V(0.17 + (0.025 if f % 2 else -0.01), -0.18, -0.12)
    hamer.keyframe_insert("location", frame=f)
    kap.rotation_euler = (0, math.radians(1.5 if f % 2 else -1.5), 0)
    kap.keyframe_insert("rotation_euler", frame=f)
S.cam(sh[1][0], (BELL + V(-0.9, -1.9, -0.45), BELL + V(0.0, -0.1, -0.05), 45), (BELL + V(-0.8, -1.7, -0.4), BELL + V(0.0, -0.1, -0.05), 48),
      handheld=0.3, dof=1.2)

# ---------------------------------------------------------------- 3: SILENCE PLEASE (bibliotheekbord met boeken eronder)
SIL = V(-14.92, 6.0, 2.2)
ST3.wall_sign("Bord_SILENCE_PLEASE", ["SILENCE", "PLEASE"], SIL, rot_z=90, w=1.1, h=0.55, bg=(0.12, 0.2, 0.42),
              fg=(0.97, 0.95, 0.85))
rnd = __import__("random").Random(7)
for k in range(14):
    col = [(0.7, 0.15, 0.12), (0.15, 0.35, 0.6), (0.2, 0.5, 0.25), (0.85, 0.7, 0.2), (0.4, 0.25, 0.5)][k % 5]
    hgt = rnd.uniform(0.24, 0.32)
    T.box(f"Boek_{k}", (-14.75, 5.35 + k * 0.095, 1.80 + hgt / 2), (0.22, 0.08, hgt), S.mat(f"boek_{k % 5}", col), bevel=0.006, ol=0.003)
T.box("Boekenplank", (-14.75, 6.0, 1.815), (0.3, 1.5, 0.04), S.mat("plank_hout", (0.6, 0.42, 0.26)), bevel=0.005, ol=0.003)
S.cam(sh[2][0], (SIL + V(2.3, -0.7, 0.1), SIL + V(0, 0, 0.1), 35), (SIL + V(2.0, -0.55, 0.1), SIL + V(0, 0, 0.1), 38), dof=2.1)

# ---------------------------------------------------------------- 4: NO DOGS op de parkeerplaats, het hondje zit ernaast
ND = V(-17.0, -26.0, 0)
ST3.sign("Bord_NO_DOGS_parkeer", ["NO DOGS"], ND, rot_z=0, w=0.7, h=0.32, bg=(0.95, 0.95, 0.95), fg=(0.85, 0.1, 0.1), post_h=1.1)
hond = animal(S, "hondje", ND + V(0.45, -0.25, 0), 20)
animal_act(hond, sh[3][0], END, "hond_kwispel")
hk = hond.rig.pose.bones.get("kop")
if hk:
    hk.rotation_mode = "XYZ"
    for t, a in ((sh[3][0], 0), (sh[3][0] + 0.5, 0), (sh[3][0] + 0.8, 20), (END, 22)):
        hk.rotation_euler = (math.radians(-10), math.radians(a), 0)
        hk.keyframe_insert("rotation_euler", frame=F(t))
S.cam(sh[3][0], (ND + V(1.1, -2.9, 0.62), ND + V(0.25, 0, 0.62), 36), (ND + V(1.0, -2.6, 0.6), ND + V(0.25, 0, 0.64), 39), dof=2.8)

# ---------------------------------------------------------------- HUD, geluid en stem
S.countdown(0, 0.3, END, jumps=[(0.0, 6 * 3600 + 12 * 60 + 5), (sh[1][0], 5 * 3600 + 41 * 60 + 30),
                                (sh[2][0], 5 * 3600 + 2 * 60 + 47), (sh[3][0], 4 * 3600 + 31 * 60 + 10)])
S.ambience("sfx_supermarkt_sfeer", 0.0, sh[1][0], vol=0.18)
S.sfx("sfx_kassa_piep", 0.4, 0.25)
S.sfx("sfx_schoolbel", sh[1][0], 0.35, cut=(0.0, 1.6))
S.sfx("sfx_klok_tik", sh[2][0], 0.18, loop_to=sh[3][0])
S.ambience("sfx_park_ochtend", sh[3][0], END, vol=0.15)
S.sfx("sfx_hond_blaf", sh[3][0] + 0.9, 0.2)
S.say("N03-05", at=0.1)
S.finish(length=END, tail=0.0)
