"""N11c · Dag 5: opa's pillen zijn op (script scène 11c-11d), opa's kamer (slaapkamer-set, grijs ochtendlicht).
11c MEDIUM handheld: opa zit op de rand van zijn bed, bleek. Hij opent het pillendoosje uit scène 3: alle vakjes leeg.
    Handen trillen licht, duim klikt vakje na vakje open.
11d CLOSE: de jongen in de deuropening ziet het lege doosje. OPA (zacht): "I'll be fine. A few days."
    Kaak spant aan, hij knikt, maar draait zich meteen om.

    blender -b -P anim/v3/scenes/n11c_pillendoosje.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402
from lib import huis as HU  # noqa: E402

S = Scene3("n11c", "slaapkamer", "ochtend", exposure=-0.15)
sh = S.cuts([3.6, 3.8])
END = sh[-1][1]
t_d = sh[1][0]
rnd = random.Random(11)

# ---------------------------------------------------------------- van de kamer van de jongen opa's kamer maken
for o in list(bpy.data.objects):
    if o.name.startswith(("Ruimteposter", "Poster_", "Laptop", "Schoolboek", "Pennenbak", "Hoodie", "Globe", "Plankboeken",
                          "Sneaker", "Telefoon", "Wekker")):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True
lt = S.obj("Ochtendlicht_raam")
if lt:
    lt.data.color, lt.data.energy = (0.82, 0.86, 0.95), 32          # grijze ochtend, geen stroom
# opa's spullen: een leeg glas op het nachtkastje, een ingelijste strandfoto aan de muur (zijn wandelstok zit aan zijn figuur)
HU.waterglas("Glas_leeg", (-0.6, 1.5, 0.55), vol=0.0)
T.box("Foto_lijst", (-2.09, 0.85, 1.55), (0.02, 0.5, 0.38), S.mat("lijst_hout", (0.35, 0.22, 0.12)), base=False, bevel=0.01, ol=0.004)
T.box("Foto_beeld", (-2.075, 0.85, 1.55), (0.006, 0.42, 0.3), S.mat("foto_strand", (0.55, 0.72, 0.85)), base=False, bevel=0, ol=0)
T.box("Foto_zand", (-2.072, 0.85, 1.45), (0.004, 0.42, 0.1), S.mat("foto_zand", (0.92, 0.82, 0.55)), base=False, bevel=0, ol=0)

# ---------------------------------------------------------------- opa op de rand van het bed
O_AT = V(-1.06, 0.38, 0)
opa = S.actor("opa", O_AT, 90)
spec, rz = sit(opa, seat_top=0.6, lean=-8)
opa.rig.location.z = rz
opa.rig.keyframe_insert("location", frame=F(0.0))

# pillendoosje (zelfde als scène 3, vergroot voor de stripfiguurhanden), leeg, ligt op zijn schoot
SC = 2.4
BOX = V(-0.7, 0.38, 0.74)
box = ST3.pillendoosje("Pillendoosje_opa", tuple(BOX), rot_z=-90, empty=True)
box.scale = (SC, SC, SC)
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def lid_pos(i):
    """Wereldpositie van het dekseltje van dag i (lokale x langs de dagen, gedraaid -90: MON aan +y)."""
    x = -0.081 + i * 0.027
    return BOX + V(0.0, -x * SC, 0.026 * SC)


T_OPEN = [0.55 + i * 0.36 for i in range(7)]
for i, d in enumerate(DAYS):
    hng = S.obj(f"Pillendoosje_opa_deksel_{d}")
    for t, a in ((0.0, 0), (T_OPEN[i] - 0.06, 0), (T_OPEN[i] + 0.04, -80), (T_OPEN[i] + 0.12, -118), (T_OPEN[i] + 0.2, -108)):
        hng.rotation_euler.x = math.radians(a)
        hng.keyframe_insert("rotation_euler", index=0, frame=F(t))

S.beat(opa, 0.0, "staan", face="nerveus", face_amt=0.5, at=BOX, body={"head": (14, 0, 0), "spine": (6, 0, 0)}, **spec)
S.beat(opa, 2.2, "staan", face="twijfel", face_amt=0.6, at=BOX, body={"head": (16, 0, 0), "spine": (7, 0, 0)}, **spec)
S.beat(opa, 3.2, "staan", face="bang", face_amt=0.4, at=BOX + V(0.2, 0, 0.1), body={"head": (12, 0, 0), "spine": (5, 0, 0)}, **spec)
# rechterhand houdt het SUN-einde vast (trillend), linkerhand klikt de dekseltjes open van MON naar SUN
HOLD_R = BOX + V(-0.02, -0.25, 0.03)
for t in frange(0.0, END + 0.01, 0.12):
    S.reach(opa, t, "R", HOLD_R + V(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)) * 0.005)
S.reach(opa, 0.0, "L", BOX + V(-0.04, 0.26, 0.04))
for i, t in enumerate(T_OPEN):
    p = lid_pos(i) + V(-0.06, 0.0, 0.0)
    S.reach(opa, t - 0.2, "L", p + V(-0.02, 0.0, 0.05))
    S.reach(opa, t - 0.04, "L", p + V(0.0, 0.0, 0.012))
    S.reach(opa, t + 0.08, "L", p + V(0.02, 0.0, 0.04) + V(0, 0, rnd.uniform(0, 0.006)))
S.reach(opa, T_OPEN[-1] + 0.5, "L", BOX + V(-0.04, 0.2, 0.05))
S.reach(opa, END, "L", BOX + V(-0.04, 0.2, 0.05))
A.blink_at(opa, F(2.9), closed=4)
# 11d: opa praat zacht (buiten beeld, de close-up is op de jongen)
S.beat(opa, t_d + 0.2, "staan", face="blij", face_amt=0.25, at=V(1.8, -1.1, 1.3), body={"head": (4, 0, 0)}, **spec)
S.hold(opa, END)

# ---------------------------------------------------------------- de jongen in de deuropening (bij de deur, rechterwand)
H_AT = V(1.72, -1.05, 0)
held = S.actor("hoofdpersonage_kind", H_AT, -90)                       # kijkt naar -x, de kamer in
S.beat(held, 0.0, "staan", face="geschrokken", face_amt=0.4, at=BOX)
S.beat(held, t_d + 0.3, "staan", face="geschrokken", face_amt=0.55, at=BOX, body={"head": (6, 0, 0)})
S.beat(held, t_d + 1.4, "staan", face="vastberaden", face_amt=0.5, at=BOX + V(0, 0, 0.3), body={"head": (0, 0, 0)})
# kaak spant aan, knik
S.beat(held, t_d + 2.25, "staan", face="vastberaden", face_amt=0.9, at=BOX + V(0, 0, 0.5), body={"head": (-4, 0, 0)})
S.beat(held, t_d + 2.45, "staan", face="vastberaden", face_amt=0.9, at=BOX + V(0, 0, 0.5), body={"head": (14, 0, 0)})
S.beat(held, t_d + 2.65, "staan", face="vastberaden", face_amt=0.9, at=BOX + V(0, 0, 0.5), body={"head": (0, 0, 0)})
S.turn(held, t_d + 2.85, END, 90)                                    # draait zich meteen om, naar de deur
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 11c MEDIUM handheld: van schuin voor opa, het bed en de foto erachter
S.cam(0.0, ((0.7, -0.6, 1.0), (-0.9, 0.42, 1.12), 24), ((0.58, -0.52, 0.98), (-0.9, 0.42, 1.1), 26), handheld=0.35)
# 11d CLOSE de jongen bij de deur
HH = S.headpos(held, t_d + 1.0)
S.cam(t_d, (HH + V(-1.35, -0.4, -0.05), HH + V(0, 0, -0.12), 30), (HH + V(-1.22, -0.36, -0.05), HH + V(0, 0, -0.12), 32), handheld=0.15)

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 5", 0, t0=0.0)
for t in T_OPEN:
    S.sfx("sfx_pillendoosje", t - 0.05, 0.22)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.03)
S.say("N11-02", who=opa, at=t_d + 0.2)
S.finish(length=END, tail=0.0)
