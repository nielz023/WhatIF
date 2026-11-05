"""D09d · De heuvel, 2051 (script scène 9d-9f). Heuvel, herfst.
9d  WIDE CAM_HEUVEL 2,2 s + DETAIL 1,8 s: op de bank alleen het zakhorloge, opengeklapt; ernaast een bosje bloemen.
    Opa is er niet meer (geen sterfscène). Geen VO: wind en de tik.
9e  CLOSE 3,6 s: hij komt aanlopen in zwart, gaat zitten, pakt het horloge.  VO: "Opa was right. Nobody gets more time."
9f  CLOSE 2,6 s: VO "Nobody... except you."  Hij klikt de klep dicht. Tik.

    python3 anim/v4/scenes/d09d_heuvel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d09d", "heuvel", "2051", exposure=0.15)
sh = S.cuts([2.2, 1.8, 3.6, 2.6])
END = sh[-1][1]
t_d1, t_e, t_f = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

# het horloge van de set (op de bank) verdwijnt als hij het pakt
WATCH_AT = V(0.25, 0.05, 0.47)
T_GRAB = t_e + 2.55
setw = bpy.data.objects["Zakhorloge"]
for o in [setw] + list(setw.children_recursive):
    show(o, 0.0, T_GRAB)
S.watch_hands("Zakhorloge", 0.0, T_GRAB, every=1.0)

# ---------------------------------------------------------------- hij: komt aanlopen in zwart, gaat zitten
SEAT_AT = V(-0.32, -0.02, 0.0)
held = S.actor("hoofdpersonage_pak", (-1.6, 0.75, 0), 120)
show(held.rig, t_e)
hs, hz_ = sit(held, seat_top=0.45)
S.walk(held, t_e, t_e + 1.15, [(-1.6, 0.75, 0), (-0.75, 0.55, 0), SEAT_AT + V(0, 0.32, 0)], stride=0.42, end_rot=180)
S.beat(held, t_e, "staan", face="verdrietig", face_amt=0.6, look=(0.0, -0.4))
S.beat(held, t_e + 1.15, "staan", face="verdrietig", face_amt=0.6, at=WATCH_AT + V(0, 0, 0.1))
S.place(held, t_e + 1.2, SEAT_AT + V(0, 0.32, 0), 180)
S.place(held, t_e + 1.65, SEAT_AT + V(0, 0, hz_), 180)
S.beat(held, t_e + 1.65, **hs, face="verdrietig", face_amt=0.6, at=WATCH_AT + V(0, 0, 0.1))
S.reach(held, t_e + 1.9, "R", None, 0.0)
S.reach(held, t_e + 2.35, "R", WATCH_AT + V(0.0, 0.0, 0.05))
S.reach(held, T_GRAB, "R", WATCH_AT + V(0.0, 0.0, 0.06))
S.reach(held, T_GRAB + 0.45, "R", None, 0.0)
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
S.beat(held, T_GRAB + 0.45, **hs, arms=arms(REST_L, LOOKH), face="verdrietig", face_amt=0.6, look=(0.0, -0.8),
       body={"head": (18, 0, 0)})
S.beat(held, t_f + 0.8, **hs, arms=arms(REST_L, LOOKH), face="verdrietig", face_amt=0.4, look=(0.0, -0.8),
       body={"head": (18, 0, 0)})
S.beat(held, t_f + 1.5, **hs, arms=arms(REST_L, LOOKH), face="neutraal", face_amt=0.5, at=V(0, 60, 6))   # kijkt op, naar de stad
S.hold(held, END)
A.blink_at(held, F(t_f + 0.4))
hw = S.watch(held, T_GRAB, side="R", name="Zakhorloge_hand", open_=0.55, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3)
for o in [hw] + list(hw.children_recursive):
    show(o, T_GRAB)
S.watch_open("Zakhorloge_hand", t_f + 1.25, t_f + 1.4, a=0.55, b=0.0)
S.watch_hands("Zakhorloge_hand", T_GRAB, END, every=1.0, start=(10, 10, 32 + int(T_GRAB)))

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22))                                   # CAM_HEUVEL, statisch
S.cam(t_d1, (V(0.55, 0.45, 0.68), V(0.25, 0.05, 0.47), 50), (V(0.52, 0.42, 0.66), V(0.25, 0.05, 0.47), 50))   # CAM_HORLOGE_BANK
S.cam(t_e, (V(-1.1, 2.6, 1.2), V(-0.3, 0.1, 0.95), 28), (V(-1.05, 2.45, 1.19), V(-0.3, 0.1, 0.95), 28))
HH = S.head(held, t_f + 0.5)
S.cam(t_f, (HH + V(0.45, 1.45, -0.3), HH + V(0.08, 0.0, -0.42), 32), (HH + V(0.42, 1.35, -0.3), HH + V(0.08, 0.0, -0.42), 32))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2051, t0=0.0, tick=False)
S.ticks(0.3, t_e, every=1.0, vol=0.3)
S.say("D09-05", at=t_e + 0.25)
S.say("D09-06", at=t_f + 0.05)
S.tick(t_f + 1.4, 0.55)
S.ambience("sfx_wind_heuvel", 0.0, END, vol=0.14)
S.music("piano_zacht", t_e - 0.2, END, vol=0.15, fade_in=0.8, fade_out=0.4)
S.finish(length=END, tail=0.0)
