"""N08e · Dag 2: pretpark zonder personeel (script scène 8e-8f).
8e WIDE: tieners lopen over de rails van de achtbaan de optakeling op, voorovergebogen; één glijdt even uit
   en vangt zich. Geen val.
8f CLOSE: de jongen kijkt vanuit de cabrio van zijn vriend omhoog naar de achtbaan: "Okay. This is not fun anymore."

    blender -b -P anim/v3/scenes/n08e_achtbaan.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n08e", "pretpark", "dag", exposure=0.0)
sh = S.cuts([3.2, 3.8])
END = sh[-1][1]
t_f = sh[1][0]

# ---------------------------------------------------------------- de middellijn van de baan (optakeling, y = -12)
pad = S.obj("Titan_pad (voor animatie)")
MW = pad.matrix_world
TRACK = [MW @ V(p.co[:3]) for p in pad.data.splines[0].points]
LIFT = sorted([p for p in TRACK if -50.0 < p.x < -33.0 and p.y < -8.0 and p.z < 16.0], key=lambda p: -p.x)


def on_track(x):
    """Punt op de middellijn bij x (lineair tussen de gesampelde punten)."""
    for a, b in zip(LIFT, LIFT[1:]):
        if b.x <= x <= a.x:
            w = (a.x - x) / (a.x - b.x)
            return a.lerp(b, w)
    return LIFT[-1] if x < LIFT[-1].x else LIFT[0]


# ---------------------------------------------------------------- tieners klimmen over de rails omhoog
TEENS = [("volgeling_a", -37.5, 0.0), ("volgeling_b", -39.2, 0.15), ("kind_a", -41.0, 0.3)]
SLIP = 2                                                   # de bovenste glijdt even uit
teens = []
for k, (nm, x0, dt) in enumerate(TEENS):
    p0 = on_track(x0) + V(0, 0, 0.05)
    p1 = on_track(x0 - 3.2) + V(0, 0, 0.05)
    e = S.actor(nm, p0, 90 + 180, label=f"tiener_{k}")    # kijkt naar -x (de heuvel op)
    mid = [on_track(x0 - 3.2 * u) + V(0, 0, 0.05) for u in (0.0, 0.33, 0.66, 1.0)]
    S.run(e, 0.0, t_f, mid, stride=0.55, lift=0.25, lean=34, arms=0.4, ease_in=0.0, ease_out=0.0)
    S.beat(e, 0.1 + dt, "staan", face="inspanning", face_amt=0.8, look=(0.0, 0.4), feet="keep")
    if k == SLIP:
        # glijdt weg (lijf zakt, armen schieten uit), vangt zich en kijkt naar beneden
        S.beat(e, 1.5, "schrik", amount=0.9, face="geschrokken", face_amt=1.0, look=(0.0, -0.6), feet="keep")
        S.beat(e, 1.9, "staan", arms=arms(arm("L", (0.6, 0.6, -0.4), (0.3, 0.9, -0.3)), arm("R", (0.6, 0.6, -0.4), (0.3, 0.9, -0.3))),
               face="geschrokken", face_amt=0.9, look=(0.0, -0.7), feet="keep")
        S.beat(e, 2.5, "staan", face="nerveus", face_amt=0.8, look=(0.0, 0.3), feet="keep")
    S.hold(e, END)
    teens.append(e)

# ---------------------------------------------------------------- 8f: de cabrio van de vriend aan de rand van het park
CAR_AT, CAR_ROT = V(-27.0, -31.0, 0.0), 120.0
car = ST3.car2("Auto_vriend", tuple(CAR_AT), rot=CAR_ROT, color=(0.95, 0.75, 0.12), open_cab=True)


def seat(ch, car_obj, local, seat_top=0.80, lean=-6):
    """Zet een figuur vast op een autostoel (lokaal in de auto, kijkt naar +x van de auto)."""
    spec, rz = sit(ch, seat_top=seat_top, lean=lean)
    ch.rig.parent = car_obj
    ad = ch.rig.animation_data
    if ad and ad.action:
        for fc in list(A._fcurves(ch.rig)):
            if fc.data_path in ("location", "rotation_euler"):
                try:
                    ad.action.fcurves.remove(fc)
                except Exception:
                    fc.keyframe_points.clear()
    ch.rig.location = (local[0], local[1], rz)
    ch.rig.rotation_euler = (0, 0, math.radians(90))
    ch.rig.keyframe_insert("location", frame=F(0.0))
    ch.rig.keyframe_insert("rotation_euler", frame=F(0.0))
    ch.last = None
    return spec


vr = S.actor("beste_vriend", CAR_AT, 0)
spv = seat(vr, car, (-0.35, 0.4))
held = S.actor("hoofdpersonage_kind", CAR_AT, 0)
sph = seat(held, car, (-0.35, -0.42))
for ch, sp in ((vr, spv), (held, sph)):
    visible(ch.body, 0.0, False)
    visible(ch.body, t_f - 0.05, True)
LIFT_TOP = on_track(-46.0) + V(0, 0, 1.0)
S.beat(vr, t_f, "staan", face="blij", face_amt=0.8, at=LIFT_TOP, **spv)
S.beat(vr, END, "staan", face="grijns", face_amt=0.7, at=LIFT_TOP, **spv)
S.hold(vr, END)
S.beat(held, t_f, "staan", face="nerveus", face_amt=0.6, at=LIFT_TOP, **sph)
S.beat(held, t_f + 1.0, "staan", face="twijfel", face_amt=1.0, at=LIFT_TOP + V(0, 0, 2.0), **sph)
S.beat(held, t_f + 2.6, "staan", face="nerveus", face_amt=1.0, at=LIFT_TOP, body={"head": (-4, 0, 0)}, **sph)
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 8e WIDE laag op de grond, omhoog naar de optakeling, langzame tilt mee omhoog
S.cam(0.0, ((-35.5, -19.5, 1.3), on_track(-39.0) + V(0, 0, 0.4), 26), ((-35.8, -19.2, 1.3), on_track(-41.0) + V(0, 0, 0.9), 27),
      handheld=0.2)
# 8f CLOSE: de jongen in de auto, schuin van voren, de achtbaan boven hem in de achtergrond
HH = S.headpos(held, t_f + 1.5)
fwd = V(math.cos(math.radians(CAR_ROT)), math.sin(math.radians(CAR_ROT)), 0)
side = V(-fwd.y, fwd.x, 0)
S.cam(t_f, (HH + fwd * 1.9 - side * 1.3 + V(0, 0, -0.4), HH + V(0, 0, 0.12), 36),
      (HH + fwd * 1.7 - side * 1.15 + V(0, 0, -0.4), HH + V(0, 0, 0.12), 38), handheld=0.2)

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 2", 0, t0=0.0)
S.ambience("sfx_pretpark_sfeer", 0.0, END, vol=0.04)
S.sfx("sfx_metaal_stap", 0.3, 0.3)
S.sfx("sfx_metaal_stap", 1.5, 0.45)
S.sfx("sfx_wind_hoog", 0.0, 0.12, loop_to=END)
S.say("N08-04", who=held, at=t_f + 0.3)
S.finish(length=END, tail=0.0)
