"""N07a · Dag 1: niemand gelooft het (script scène 7a-7c), kruispunt, grijze ochtend.
7a WIDE: auto's en voetgangers wachten keurig voor rood. VO: "The next morning, almost everybody still waits at the red light."
7b MEDIUM push-in: een man in een rode auto trommelt op zijn stuur, bijt op zijn lip, kijkt links, rechts, in zijn spiegel... gas.
7c WIDE: de rode auto rijdt door rood. Een seconde stilte. Dan een tweede auto, en een derde. VO: "Almost."

    blender -b -P anim/v3/scenes/n07a_rood_licht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n07a", "stad", "ochtend", exposure=0.25)
sh = S.cuts([3.4, 3.2, 4.0])
END = sh[-1][1]
t_b, t_c = sh[1][0], sh[2][0]

# ---------------------------------------------------------------- de rode auto en zijn bestuurder
CAR = S.obj("Auto_wacht_0")
C0 = CAR.location.copy()                        # (3.0, -18.6, 0), kijkt naar +y
DRV_OFF = V(-0.4, 0.0, 0.0)                     # bestuurder links (wereld -x)
drv = S.actor("figurant_b", C0 + DRV_OFF, 180)
spec, rz = sit(drv, seat_top=0.80, lean=-6)
WHEEL = C0 + V(-0.4, 0.45, 1.0)


def car_path(obj, t0, dist, dur, t_end, extra=None):
    """Optrekken vanuit stilstand: afstand ~ t^2 tot halverwege, daarna constante snelheid; elke 0,1 s gekeyd."""
    p0 = obj.location.copy()
    keys = [(0.0, 0.0), (t0, 0.0)]
    acc = 2 * dist / (dur * dur) * 0.5
    t = t0
    while t < t_end:
        t = min(t_end, t + 0.1)
        u = t - t0
        d = acc * u * u if u < dur else acc * dur * dur + 2 * acc * dur * (u - dur)
        keys.append((t, d))
    for t, d in keys:
        obj.location = p0 + V(0, d, 0)
        obj.keyframe_insert("location", frame=F(t))
        if extra is not None:
            extra.location = p0 + DRV_OFF + V(0, d, rz)
            extra.keyframe_insert("location", frame=F(t))
    for o in (obj, extra):
        if o is not None:
            for fc in A._fcurves(o):
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"


T_GAS = t_b + 2.9
car_path(CAR, T_GAS, 14.0, 1.6, END, extra=drv.rig)
car_path(S.obj("Auto_wacht_1"), t_c + 1.9, 12.0, 1.5, END)
car_path(S.obj("Auto_wacht_2"), t_c + 2.7, 10.0, 1.4, END)

HANDS = arms(arm("R", (0.25, 0.55, -0.75), (-0.25, 0.9, 0.3)), arm("L", (0.25, 0.55, -0.75), (-0.25, 0.9, 0.3)))
S.reach(drv, 0.0, "R", WHEEL + V(0.15, 0.0, 0.05))
S.reach(drv, 0.0, "L", WHEEL + V(-0.15, 0.0, 0.05))
S.beat(drv, 0.0, "staan", arms=HANDS, face="nerveus", face_amt=0.5, look=(0.0, 0.0), **spec)
S.beat(drv, t_b + 0.2, "staan", arms=HANDS, face="nerveus", face_amt=0.7, look=(-0.8, 0.0), mond_verdrietig=0.6, **spec)
S.beat(drv, t_b + 0.8, "staan", arms=HANDS, face="nerveus", face_amt=0.7, look=(0.8, 0.0), mond_verdrietig=0.6,
       body={"head": (0, 0, -18)}, **spec)
S.beat(drv, t_b + 1.4, "staan", arms=HANDS, face="twijfel", face_amt=0.8, look=(0.2, 0.6), body={"head": (-6, 0, 10)}, **spec)
S.beat(drv, t_b + 2.1, "staan", arms=HANDS, face="vastberaden", face_amt=0.6, look=(0.0, 0.0), **spec)
S.beat(drv, T_GAS + 0.1, "staan", arms=HANDS, face="grijns", face_amt=0.7, look=(0.0, 0.0), body={"spine": (-6, 0, 0)}, **spec)
S.hold(drv, END)
# vingers trommelen op het stuur
for k, t in enumerate(frange(0.1, T_GAS, 0.13)):
    A.bone_rot(drv, F(t), "hand.R", (14 if k % 2 else -4, 0, 0))
    A.bone_rot(drv, F(t + 0.06), "hand.L", (12 if k % 2 else -3, 0, 0))

# ---------------------------------------------------------------- voetgangers wachten voor rood
peds = []
for k, (nm, x, y, r) in enumerate((("figurant_a", -7.6, -7.4, -90), ("figurant_e", -8.3, -7.9, -80), ("figurant_d", 7.5, -7.6, 90),
                                   ("figurant_f", 8.2, -7.2, 100), ("figurant_c", -7.4, 7.6, -100))):
    e = S.actor(nm, (x, y, 0.2), r)
    for j, t in enumerate(frange(0.0, END, 0.9 + 0.1 * k)):
        S.beat(e, t, "staan" if j % 2 else "handen_zij", amount=0.5, face="neutraal", face_amt=0.4,
               look=((-0.3 if (j + k) % 2 else 0.3), 0.1), feet="keep")
    S.hold(e, END)
    peds.append(e)
# in 7c kijken ze de rode auto na
for e in peds:
    S.beat(e, t_c + 0.9, "staan", face="verbaasd", face_amt=0.8, at=V(3.0, 2.0, 1.2), feet="keep")
    S.hold(e, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, ((9.6, -4.2, 2.5), (2.0, -21.0, 1.0), 24), ((9.3, -4.6, 2.45), (2.0, -21.0, 1.0), 24))
HD = C0 + DRV_OFF + V(0, 0, 1.3)
S.cam(t_b, (HD + V(-1.6, 3.0, 0.2), HD + V(0, 0, 0.05), 32), (HD + V(-1.15, 2.25, 0.15), HD + V(0, 0, 0.05), 35))
S.cam(t_c, ((-7.5, -9.5, 5.3), (3.0, -2.0, 0.6), 22), ((-7.3, -9.2, 5.25), (3.0, -1.0, 0.6), 22))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 1", 0)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.14, )
S.sfx("sfx_klok_tik", t_b, 0.2, loop_to=T_GAS)
S.sfx("sfx_auto_optrekken", T_GAS - 0.1, 0.6)
S.sfx("sfx_auto_optrekken", t_c + 1.8, 0.4)
S.sfx("sfx_auto_optrekken", t_c + 2.6, 0.35)
S.say("N07-01", at=0.2)
S.say("N07-02", at=t_c + 1.2)
S.finish(length=END, tail=0.0)
