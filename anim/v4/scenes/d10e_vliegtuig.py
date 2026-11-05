"""D10e · De sprong uit het vliegtuig (script scène 10e-10f).
10e WIDE 3 s: hij staat in de open deur van een testvliegtuig, helm met camera op, zonder parachute. Een wetenschapper
    kijkt op de schermen.  VO: "Scientists actually measured this."
10f MEDIUM 4 s, trage roll: hij valt door de wolken, armen gespreid, wangen klapperend.
    VO: "A falling human reaches about two hundred kilometers an hour."

    python3 anim/v4/scenes/d10e_vliegtuig.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d10e", "kleine_nd", "vliegtuig", exposure=0.15)
sh = S.cuts([3.0, 4.0])
END = sh[-1][1]
t_f = sh[1][0]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True


def helmet(ch, name):
    hm = S.mat("helm_wit", (0.92, 0.92, 0.94), 0.3)
    h = T.sphere(name, (0, 0, 0), 0.33, hm, scale=(1.0, 1.0, 0.82), seg=20, ol=0)
    cam = T.box(name + "_camera", (0, 0.0, 0.3), (0.07, 0.10, 0.06), S.mat("helmcamera", (0.1, 0.1, 0.11)), bevel=0.01, ol=0)
    lens = T.cyl(name + "_lens", (0, -0.055, 0.3), 0.022, 0.02, S.mat("lens_blauw", (0.2, 0.4, 0.8), 0.2), rot=(90, 0, 0), seg=12, ol=0)
    cam.parent = h
    lens.parent = h
    grab(S, h, ch, 0.0, "head", loc=(0, 0.05, 0.02), rot=(0, 0, 0))
    return h


# ---------------------------------------------------------------- 10e: in de open deur
held = S.actor("hoofdpersonage_kind", (0.75, 1.5, 0.05), 90)
helmet(held, "Helm")
S.beat(held, 0.0, "staan", face="zelfverzekerd", face_amt=0.7, at=V(6.0, 1.5, -2.0),
       arms=arms(arm("L", (0.40, 0.05, -0.92), (0.25, 0.30, -0.92)), arm("R", (0.40, 0.05, -0.92), (0.25, 0.30, -0.92))))
S.beat(held, 1.6, "staan", face="grijns", face_amt=0.8, at=V(-0.6, -1.5, 1.4), body={"head": (0, -30, 0)})   # kijkt achterom
S.beat(held, 2.4, "staan", face="zelfverzekerd", face_amt=0.9, at=V(6.0, 1.5, -3.0), crouch=(0.06, 10))
S.hold(held, t_f)
show(held.rig, 0.0, t_f)
wet = S.actor("wetenschapper", (-0.55, 0.6, 0.05), -100, drop=("klembord",))
S.beat(wet, 0.0, "staan", face="nerveus", face_amt=0.7, at=V(-0.95, -1.0, 1.0))
S.beat(wet, 1.4, "staan", face="nerveus", face_amt=0.9, at=S.head(held))
S.beat(wet, 2.4, "staan", face="geschrokken", face_amt=0.7, at=V(-0.95, -0.6, 1.1))
S.hold(wet, t_f)

# ---------------------------------------------------------------- 10f: vrije val door de wolken (bij x 300, y 0)
FALL0 = V(300.0, 0.0, -470.0)
FALL1 = V(300.0, 0.0, -690.0)                          # ~55 m/s: 200 km/u
vh = S.actor("hoofdpersonage_kind", FALL0, 0, label="hoofdpersonage_val")
show(vh.rig, t_f)
helmet(vh, "Helm_val")
vb = Body(S, vh, FALL0, 0)
S.qc_skip.add(vh.name)
for k, t in enumerate(frange(t_f, END + 0.01, 0.5)):
    u = (t - t_f) / (END - t_f)
    vb.key(t, FALL0.lerp(FALL1, u), tilt=-90, roll=-25 + 50 * u, interp="LINEAR")
SPREAD_A = arms(arm("L", (0.95, 0.15, 0.25), (0.90, 0.30, 0.30)), arm("R", (0.95, 0.15, 0.25), (0.90, 0.30, 0.30)))
SPREAD_B = arms(arm("L", (0.95, 0.10, 0.30), (0.88, 0.25, 0.40)), arm("R", (0.95, 0.10, 0.30), (0.88, 0.25, 0.40)))
for k, t in enumerate(frange(t_f, END, 0.12)):
    S.beat(vh, t, "staan", arms=SPREAD_A if k % 2 else SPREAD_B, face="schreeuw" if (k // 3) % 2 else "lach",
           face_amt=1.0, body={"head": (-35, 0, 0)}, mouth=0.6 + 0.3 * (k % 2), feet=((0.18, -0.15, 0.12), (-0.18, -0.15, 0.12)))
S.hold(vh, END)

# wolkflarden langs de val (schieten voorbij de camera)
import random as _r
_rnd = _r.Random(10)
wm = S.mat("wolk_wit_val", (0.97, 0.97, 0.98))
fl = [T.sphere(f"Wolkflard_{k}", (300 + _rnd.choice((-1, 1)) * _rnd.uniform(3, 9), _rnd.uniform(-6, 8), -500 - k * 22),
               _rnd.uniform(2.5, 6.0), wm, scale=(1.8, 1.4, 0.7), seg=12, ol=0) for k in range(9)]
T.merge("Wolkflarden", fl, ol=0)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-0.2, -1.4, 1.6), V(0.9, 1.6, 0.9), 22), (V(-0.15, -1.2, 1.58), V(0.9, 1.6, 0.9), 22))
S.cam(t_f, None, fn=lambda t: (vb.at(t) + V(0.9, -1.9, -1.3), vb.at(t) + V(0, 0, -0.1), 30), handheld=0.2)

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2066, t0=0.0, tick=False)
S.say("D10-06", at=0.25)
S.say("D10-07", at=t_f + 0.1)
S.ambience("sfx_wind_hoog", 0.0, t_f, vol=0.18)
S.sfx("sfx_vrije_val", t_f, 0.3, loop_to=END)
S.music("drums_build", 0.0, END, vol=0.15, fade_in=0.2, fade_out=0.3)
S.finish(length=END, tail=0.0)
