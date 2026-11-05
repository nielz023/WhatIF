"""D08a · De heuvel, 2032 (script scène 8a-8b). Heuvel, zomer, zonsondergang.
8a WIDE CAM_HEUVEL 3,3 s: tijdsprong naar YEAR 2032. Op de bank hij (14) en de beste vriend (20, sikje), die
   autosleutels om zijn vinger draait.  VO: "Six years later, your best friend is twenty."
8b MEDIUM 4,5 s: VRIEND: "Want a ride? Oh wait. You're fourteen. Forever."  Hij grijnst en stoot hem met zijn elleboog.

    python3 anim/v4/scenes/d08a_heuvel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d08a", "heuvel", "2032", exposure=0.15)
sh = S.cuts([3.3, 4.5])
END = sh[-1][1]
t_b = sh[1][0]
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

SEAT = 0.45
HERO_AT = V(-0.42, -0.02, 0.0)
VR_AT = V(0.48, -0.04, 0.0)
held = S.actor("hoofdpersonage_kind", HERO_AT, 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, HERO_AT + V(0, 0, hz_), 180)
vr = S.actor("beste_vriend_20", VR_AT, 180)
vs, vz = sit(vr, seat_top=SEAT)
S.place(vr, 0, VR_AT + V(0, 0, vz), 180)
CITY = V(0.0, 60.0, 4.0)
HH = S.head(held)
VH = S.head(vr)

# ---------------------------------------------------------------- autosleutels: ring draait om zijn wijsvinger
km = S.mat("sleutel_metaal", (0.78, 0.78, 0.80), 0.2)
spin = bpy.data.objects.new("Sleutels_hand", None)          # volgt de hand (grijp-constraint)
T._link(spin)
grab(S, spin, vr, 0.0, "hand.R", loc=(0, 0.075, 0.0), rot=(0, 0, 0))
sk = bpy.data.objects.new("Sleutels", None)                 # kind-empty: hierin zit de draai
T._link(sk)
sk.parent = spin
sk.scale = (1.8, 1.8, 1.8)                                  # chibi-handen: anders onzichtbaar
for o in (T.torus("Sleutels_ring", (0, 0, -0.03), 0.022, 0.003, km, rot=(0, 90, 0), seg=20, seg2=6, ol=0),
          T.box("Sleutel_1", (0, 0.0, -0.075), (0.012, 0.004, 0.05), km, bevel=0.002, ol=0),
          T.box("Sleutel_hanger", (0, 0.012, -0.07), (0.022, 0.008, 0.03), S.mat("sleutel_hanger", (0.1, 0.1, 0.12)),
                bevel=0.004, ol=0)):
    o.parent = sk
T_STOP = t_b + 2.3                                           # hij stopt met draaien bij "You're fourteen"
for t, turns in ((0.0, 0.0), (T_STOP, T_STOP * 2.2), (END, T_STOP * 2.2)):
    sk.rotation_euler.x = math.radians(360 * turns)
    sk.keyframe_insert("rotation_euler", index=0, frame=F(t))
for fc in A._fcurves(sk):
    for p in fc.keyframe_points:
        p.interpolation = "LINEAR"

# ---------------------------------------------------------------- acting
SPIN_R = arm("R", (0.40, 0.45, -0.80), (0.15, 0.55, 0.82))         # onderarm omhoog, sleutels aan de vinger
REST_R = arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
NUDGE_L = arm("L", (0.92, 0.0, -0.40), (0.55, 0.30, -0.78))          # elleboog opzij, naar hem toe
S.beat(vr, 0.0, **vs, arms=arms(REST_L, SPIN_R), face="zelfverzekerd", face_amt=0.8, at=CITY)
S.beat(vr, 1.6, **vs, arms=arms(REST_L, SPIN_R), face="zelfverzekerd", face_amt=0.9, at=HH + V(0.2, 0.6, 0.1))
S.beat(vr, t_b + 0.2, **vs, arms=arms(REST_L, SPIN_R), face="grijns", face_amt=0.9, at=HH)
S.beat(vr, t_b + 1.4, **vs, arms=arms(REST_L, SPIN_R), face="verbaasd", face_amt=0.6, at=HH, body={"head": (0, 0, 8)})   # "oh wait"
S.beat(vr, t_b + 2.4, **vs, arms=arms(REST_L, REST_R), face="grijns", face_amt=1.0, at=HH)
S.beat(vr, t_b + 3.1, **dict(vs, crouch=(vs["crouch"][0], 6)), arms=arms(NUDGE_L, REST_R), face="lach", face_amt=1.0, at=HH,
       body={"spine": (0, 0, 10)})
S.beat(vr, t_b + 3.6, **vs, arms=arms(REST_L, REST_R), face="lach", face_amt=0.9, at=HH)
S.hold(vr, END)
A.blink_at(vr, F(0.9))

S.beat(held, 0.0, **hs, arms=arms(REST_L, REST_R), face="neutraal", face_amt=0.5, at=CITY)
S.beat(held, 1.8, **hs, arms=arms(REST_L, REST_R), face="twijfel", face_amt=0.4, at=VH + V(0, 0.5, -0.3))   # kijkt naar de sleutels
S.beat(held, t_b + 0.3, **hs, arms=arms(REST_L, REST_R), face="neutraal", face_amt=0.5, at=VH)
S.beat(held, t_b + 2.5, **hs, arms=arms(REST_L, REST_R), face="twijfel", face_amt=0.7, at=VH, body={"head": (0, 0, -6)})
S.beat(held, t_b + 3.2, **hs, arms=arms(REST_L, REST_R), face="grijns", face_amt=0.6, at=VH, body={"spine": (0, 0, -9), "head": (0, 0, -8)})
S.beat(held, t_b + 3.8, **hs, arms=arms(REST_L, REST_R), face="lach", face_amt=0.7, at=VH)
S.hold(held, END)
A.blink_at(held, F(t_b + 1.0))

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22), (V(-3.45, -9.2, 2.28), V(0.8, 8.0, -0.6), 22))   # CAM_HEUVEL
MID = (HH + VH) * 0.5
S.cam(t_b, (V(0.25, 2.7, 1.05), MID + V(0, 0, -0.25), 32), (V(0.22, 2.5, 1.04), MID + V(0, 0, -0.25), 32))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2032, t0=0.0, big=True)
S.jump(0.0)
S.say("D08-01", at=0.35)
S.say("D08-02", who=vr, at=t_b + 0.15)
S.ambience("sfx_wind_heuvel", 0.0, END, vol=0.1)
S.music("piano_warm", 0.0, END, vol=0.17, fade_in=0.4, fade_out=0.3)
S.finish(length=END, tail=0.0)
