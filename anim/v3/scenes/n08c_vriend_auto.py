"""N08c · Dag 2: de beste vriend rijdt auto (script scène 8c-8d), straat, zonnig.
8c WIDE: een cabrio komt zigzaggend de straat in; achter het stuur de vriend, nauwelijks boven het dashboard,
   handen te hoog op tien voor twee, hoofd ver naar voren. Remt schokkerig.
8d MEDIUM push-in: de vriend roept "No license needed anymore! Get in!". De jongen doet een stap naar voren,
   aarzelt, kijkt naar zijn huis en doet een stap terug.

    blender -b -P anim/v3/scenes/n08c_vriend_auto.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n08c", "straat", "zonnig", exposure=0.0)
sh = S.cuts([3.0, 1.9, 2.6])
END = sh[-1][1]
t_d, t_d2 = sh[1][0], sh[2][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Boodschappentas", "Appels")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de auto: zigzag de straat in, schokkerig remmen
car = ST3.car2("Auto_vriend", (-34.0, 0.5, 0.0), rot=0, color=(0.95, 0.75, 0.12), open_cab=True)
PTS = [V(-34, 0.5, 0), V(-28, 1.7, 0), V(-22, -0.4, 0), V(-16, 1.6, 0), V(-10.5, -0.2, 0), V(-6, 1.5, 0), V(-3.4, 2.7, 0), V(-1.6, 3.0, 0)]
T_STOP = 2.75


def along(u):
    """Punt en richting op de polyline (u = 0..1, gelijk verdeeld naar afstand)."""
    segs = [(PTS[i], PTS[i + 1]) for i in range(len(PTS) - 1)]
    lens = [(b - a).length for a, b in segs]
    d = u * sum(lens)
    for (a, b), L in zip(segs, lens):
        if d <= L or (a, b) == segs[-1]:
            w = min(1.0, d / L)
            return a.lerp(b, w), (b - a).normalized()
        d -= L


prev_yaw = None
N = 34
for k in range(N + 1):
    t = T_STOP * k / N
    s = k / N
    u = 1 - (1 - s) ** 1.6                                   # remt af naar het einde
    p, d = along(u)
    yaw = math.atan2(d.y, d.x)
    if k == N:
        yaw = 0.0
    car.location = p
    car.rotation_euler = (0, 0, yaw)
    car.keyframe_insert("location", frame=F(t))
    car.keyframe_insert("rotation_euler", frame=F(t))
# schokkerig remmen: twee korte duiken naar voren (pitch) en een klein schokje terug
for t, pitch in ((T_STOP - 0.9, 0.0), (T_STOP - 0.75, 3.5), (T_STOP - 0.6, 0.0), (T_STOP, 0.0), (T_STOP + 0.12, 4.5), (T_STOP + 0.3, -1.5),
                 (T_STOP + 0.45, 0.0), (END, 0.0)):
    car.rotation_euler = (0, math.radians(pitch), 0.0 if t >= T_STOP else car.rotation_euler.z)
    car.keyframe_insert("rotation_euler", index=1, frame=F(t))

# ---------------------------------------------------------------- de vriend achter het stuur (hangt aan de auto)
vr = S.actor("beste_vriend", (-34.0, 0.9, 0.0), 90)
spec, rz = sit(vr, seat_top=0.80, lean=-14)
vr.rig.parent = car
ad = vr.rig.animation_data
if ad and ad.action:
    for fc in list(A._fcurves(vr.rig)):
        if fc.data_path in ("location", "rotation_euler"):
            try:
                ad.action.fcurves.remove(fc)
            except Exception:
                fc.keyframe_points.clear()
vr.rig.location = (-0.35, 0.4, rz)
vr.rig.rotation_euler = (0, 0, math.radians(90))               # lokaal: kijkt naar +x van de auto
vr.rig.keyframe_insert("location", frame=F(0.0))
vr.rig.keyframe_insert("rotation_euler", frame=F(0.0))
vr.last = None
WHEEL = arms(arm("R", (0.25, 0.75, 0.45), (0.15, 0.75, 0.45)), arm("L", (0.25, 0.75, 0.45), (0.15, 0.75, 0.45)))
WAVE = arms(arm("R", (0.25, 0.75, 0.45), (0.15, 0.75, 0.45)), arm("L", (0.55, 0.3, 0.5), (0.2, 0.2, 0.95)))
S.beat(vr, 0.0, "staan", arms=WHEEL, face="grijns", face_amt=0.9, look=(0.0, 0.2), body={"spine": (14, 0, 0), "neck": (12, 0, 0)}, **spec)
for k, t in enumerate(frange(0.35, T_STOP, 0.45)):              # stuurt wild mee met de zigzag
    S.beat(vr, t, "staan", arms=WHEEL, face="grijns", face_amt=0.9, look=(0.0, 0.2),
           body={"spine": (14, 0, 9 if k % 2 else -9), "neck": (12, 0, 0)}, **spec)
S.beat(vr, T_STOP + 0.15, "staan", arms=WHEEL, face="geschrokken", face_amt=0.7, look=(0.0, 0.0), body={"spine": (20, 0, 0)}, **spec)
# 8d: draait zich naar de jongen (links, +y) en roept, linkerarm zwaait
S.beat(vr, t_d + 0.1, "staan", arms=WAVE, face="blij", face_amt=1.0, look=(0.6, 0.2), body={"spine": (0, 22, 0), "head": (-6, 35, 0)}, **spec)
S.beat(vr, END, "staan", arms=WAVE, face="grijns", face_amt=1.0, look=(0.6, 0.2), body={"spine": (0, 22, 0), "head": (-6, 35, 0)}, **spec)
S.hold(vr, END)

# ---------------------------------------------------------------- de jongen op de stoep voor zijn huis
held = S.actor("hoofdpersonage_kind", (-0.9, 7.3, 0.12), -15)
S.beat(held, 0.0, "staan", face="verbaasd", face_amt=0.7, at=V(-12.0, 1.5, 1.0))
S.beat(held, 1.6, "staan", face="verbaasd", face_amt=0.9, at=V(-4.0, 2.5, 1.0))
S.beat(held, t_d + 0.2, "staan", face="blij", face_amt=0.6, at=V(-1.95, 3.6, 1.3))
S.walk(held, t_d2 + 0.1, t_d2 + 0.6, [V(-0.9, 7.3, 0.12), V(-0.95, 6.75, 0.12)], stride=0.45)
S.beat(held, t_d2 + 0.7, "staan", face="twijfel", face_amt=0.9, at=V(-1.95, 3.6, 1.3))
S.beat(held, t_d2 + 1.0, "staan", face="twijfel", face_amt=1.0, at=V(3.5, 9.8, 2.0))       # kijkt over zijn linkerschouder naar zijn huis
S.beat(held, t_d2 + 1.5, "staan", face="nerveus", face_amt=0.9, at=V(-1.95, 3.6, 1.3))
S.walk(held, t_d2 + 1.6, t_d2 + 2.2, [V(-0.95, 6.75, 0.12), V(-0.9, 7.3, 0.12)], stride=0.45, turn=False)
S.beat(held, t_d2 + 2.25, "staan", face="nerveus", face_amt=0.9, at=V(-1.95, 3.6, 1.3))
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 8c WIDE: vanaf de stoep oostwaarts de straat in, de auto zwalkt op ons af
S.cam(0.0, ((6.5, 5.1, 1.3), (-18.0, 1.5, 1.0), 26), ((6.2, 5.0, 1.25), (-6.0, 2.2, 1.0), 26), handheld=0.3)
# 8d-1 MEDIUM push-in op de vriend, vanaf de stoepkant (zo zien we zijn gezicht als hij naar de jongen roept)
HV = V(-1.95, 3.6, 1.35)
S.cam(t_d, (HV + V(2.6, 2.6, 0.0), HV, 32), (HV + V(2.1, 2.2, 0.0), HV, 34))
# 8d-2 MEDIUM op de jongen vanaf de auto: stap naar voren, twijfel, blik op zijn huis, stap terug
HB = S.headpos(held, t_d2 + 0.8)
S.cam(t_d2, (HB + V(2.6, -1.0, -0.1), HB + V(0, 0, -0.2), 32), (HB + V(2.3, -0.85, -0.1), HB + V(0, 0, -0.2), 34))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 2", 0, t0=0.0)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.1)
S.sfx("sfx_auto_optrekken", 0.0, 0.35)
S.sfx("sfx_remmen", T_STOP - 0.8, 0.35)
S.sfx("sfx_auto_toeter", T_STOP + 0.2, 0.3)
S.say("N08-03", who=vr, at=t_d + 0.25)
S.finish(length=END, tail=0.0)
