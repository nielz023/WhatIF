"""D08e · De groepsfoto en terug op de heuvel (script scène 8e-8f).
8e DETAIL 4,4 s, trage push-in: groepsfoto eindexamen. De klas met diploma's, iedereen volwassen; hij staat ervoor als
   een broertje dat per ongeluk mee op de foto staat.  VO: "On every photo, you look more and more like somebody's
   little brother."  (De foto staat ver buiten de heuvel, met een eigen achterwand en flitslicht.)
8f CLOSE 3 s, de heuvel 2032: hij lacht erom. Nog wel.  SFX: tik, whoosh.

    python3 anim/v4/scenes/d08e_foto.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403
from lib import stad as SD  # noqa: E402

S = Scene4("d08e", "heuvel", "2032", exposure=0.15)
sh = S.cuts([4.4, 3.0])
END = sh[-1][1]
t_f = sh[1][0]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- 8e: de fotostudio buiten de heuvel
PH = V(0.0, -420.0, 0.0)
T.plane("Foto_vloer", tuple(PH + V(0, 1.0, 0.0)), (14, 10), S.mat("foto_vloer", (0.55, 0.55, 0.52)))
T.box("Foto_muur", tuple(PH + V(0, 2.2, 0)), (12.0, 0.3, 6.0), S.mat("foto_baksteen", (0.62, 0.32, 0.22)), bevel=0, ol=0)
T.box("Foto_banier", tuple(PH + V(0, 2.03, 2.55)), (4.4, 0.04, 0.75), S.mat("foto_banier", (0.10, 0.18, 0.45)), bevel=0, ol=0)
SD.label("Foto_banier_tekst", "CLASS OF 2032", tuple(PH + V(0, 2.0, 2.66)), 0.42, (1.0, 0.85, 0.3), glow=1.5, extrude=0.01)
T.point_light("Foto_flits", tuple(PH + V(0.0, -3.5, 3.0)), color=(1.0, 0.97, 0.92), energy=1400, radius=1.5)

dm = S.mat("diploma_papier", (0.96, 0.94, 0.86))
lint = S.mat("diploma_lint", (0.8, 0.08, 0.08))
klas = [("figurant_a", (-1.25, 1.0)), ("figurant_b", (-0.42, 1.1)), ("beste_vriend_20", (0.42, 1.05)),
        ("figurant_c", (1.25, 1.0)), ("figurant_d", (-0.85, 0.3)), ("figurant_e", (0.0, 0.38)), ("figurant_f", (0.85, 0.3))]
GRIN = ["lach", "blij", "grijns", "lach", "blij", "lach", "grijns"]
for i, (name, (x, y)) in enumerate(klas):
    ch = S.actor(name, PH + V(x, y, 0), 0)
    ch.rig.scale = (1.18,) * 3                       # volwassenen: duidelijk groter dan hij
    hold_up = i % 3 == 0
    a = arm("R", (0.35, 0.45, -0.82), (-0.05, 0.55, 0.83)) if hold_up else arm("R", (0.30, 0.40, -0.87), (0.05, 0.90, 0.40))
    S.beat(ch, 0.0, "staan", arms=arms(a), face=GRIN[i], face_amt=0.9, at=PH + V(0, -5.0, 1.5))
    S.hold(ch, t_f)
    d = T.cyl(f"Diploma_{i}", (0, 0, 0), 0.025, 0.24, dm, rot=(0, 90, 0), seg=12, ol=0)
    rb = T.cyl(f"Diploma_{i}_lint", (0, 0, 0), 0.028, 0.03, lint, rot=(0, 90, 0), seg=12, ol=0)
    rb.parent = d
    grab(S, d, ch, 0.0, "hand.R", loc=(0, 0.07, 0.0), rot=(0, 0, 90))
    show(d, 0.0, t_f)
    show(rb, 0.0, t_f)
    show(ch.rig, 0.0, t_f)
    S.qc_skip.add(ch.name)

fh = S.actor("hoofdpersonage_kind", PH + V(0.1, -0.45, 0), 0, label="hoofdpersonage_foto")
S.beat(fh, 0.0, "staan", arms=arms(arm("L", (0.30, 0.20, -0.93), (0.25, 0.30, -0.92)), arm("R", (0.30, 0.20, -0.93), (0.25, 0.30, -0.92))),
       face="grijns", face_amt=0.6, at=PH + V(0, -5.0, 1.0), body={"head": (0, 0, 5)})
S.hold(fh, t_f)
show(fh.rig, 0.0, t_f)
CAMF = PH + V(0.0, -5.6, 1.45)

# ---------------------------------------------------------------- 8f: terug op de heuvel, hij lacht erom
SEAT = 0.45
HERO_AT = V(-0.42, -0.02, 0.0)
VR_AT = V(0.48, -0.04, 0.0)
held = S.actor("hoofdpersonage_kind", HERO_AT, 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, HERO_AT + V(0, 0, hz_), 180)
vr = S.actor("beste_vriend_20", VR_AT, 180)
vs, vz = sit(vr, seat_top=SEAT)
S.place(vr, 0, VR_AT + V(0, 0, vz), 180)
show(held.rig, t_f)
show(vr.rig, t_f)
HH = S.head(held)
VH = S.head(vr)
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST_R = arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
S.beat(vr, t_f, **vs, arms=arms(REST_L, REST_R), face="lach", face_amt=0.9, at=HH)
S.hold(vr, END)
S.beat(held, t_f, **hs, arms=arms(REST_L, REST_R), face="grijns", face_amt=0.6, at=VH)
S.beat(held, t_f + 0.6, **hs, arms=arms(REST_L, REST_R), face="lach", face_amt=1.0, at=HH + V(0.5, 2.0, 0.2),
       body={"head": (-8, 0, -4), "spine": (-4, 0, 0)})
S.beat(held, t_f + 1.1, **hs, arms=arms(REST_L, REST_R), face="lach", face_amt=0.9, at=HH + V(0.4, 2.0, -0.1), body={"head": (4, 0, 3)})
S.beat(held, t_f + 1.6, **hs, arms=arms(REST_L, REST_R), face="lach", face_amt=1.0, at=HH + V(0.5, 2.0, 0.1), body={"head": (-6, 0, -3)})
S.beat(held, t_f + 2.3, **hs, arms=arms(REST_L, REST_R), face="blij", face_amt=0.6, at=V(0.0, 60.0, 4.0))   # kijkt naar de stad
S.hold(held, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (CAMF + V(0, 0, -0.2), PH + V(0, 0.4, 1.35), 35), (CAMF + V(0, 0.6, -0.22), PH + V(0, 0.4, 1.33), 35))   # trage push-in
S.cam(t_f, (HH + V(-0.75, 1.6, -0.3), HH + V(0.2, 0, -0.15), 35), (HH + V(-0.7, 1.5, -0.29), HH + V(0.2, 0, -0.15), 35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2032, t0=0.0, tick=False)
S.sfx("sfx_zaklamp_klik", 0.1, 0.35)                     # sluiter
S.say("D08-08", at=0.3)
S.tick(t_f + 2.3, 0.4)
S.sfx("sfx_whoosh", END - 0.35, 0.4)
S.ambience("sfx_wind_heuvel", t_f, END, vol=0.1)
S.music("piano_warm", 0.0, END, vol=0.16, fade_in=0.3, fade_out=0.4)
S.finish(length=END, tail=0.0)
