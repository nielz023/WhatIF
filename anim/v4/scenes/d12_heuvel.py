"""D12 · De laatste die je kent, 2110 (script scène 12a-12f). Heuvel, lente, nieuwe stenen bank.
12a  WIDE CAM_HEUVEL 5 s: een heel oude man in een rolstoel wordt de heuvel op geduwd door een verpleger: de pestkop, 98.
     VO: "In 2110, one more visitor makes it up the hill. The last one."
12b  MEDIUM 4,6 s: PESTKOP: "I pushed you off that ramp."  JONGEN: "Like a hundred times."
12c  CLOSE pestkop 3,6 s: "I'm sorry, kid. For all of it." Zijn hand trilt als hij die uitsteekt; de jongen pakt hem vast.
12d  CLOSE 4,3 s: VO "Here's the hard part. The oldest person who ever lived..."
12d2 DETAIL 3 s: oude zwart-witfoto van een heel oude vrouw, eronder 122 YEARS.  VO "...made it to one hundred and twenty-two."
12d3 DETAIL 4 s: de pestkop drukt zijn oude politiepenning in zijn hand.  PESTKOP: "Somebody's gotta watch your back."
12e  WIDE CAM_HEUVEL 4 s: dezelfde bank, een week later. Hij zit alleen.  VO: "Everyone who ever knew you as a kid... is gone."
12f  CLOSE trage push-in 3,2 s: hij kijkt naar de stad. Tik.  VO: "And you're still fourteen."  Whoosh.

    python3 anim/v4/scenes/d12_heuvel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d12", "heuvel", "2110", exposure=0.15)
sh = S.cuts([5.0, 4.6, 3.6, 4.3, 3.0, 4.0, 4.0, 3.2])
END = sh[-1][1]
t_b, t_c, t_d, t_d2, t_d3, t_e, t_f = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

SEAT = 0.46
H_AT = V(0.22, -0.02, 0.0)
held = S.actor("hoofdpersonage_kind", H_AT, 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, H_AT + V(0, 0, hz_), 180)
HH = S.head(held)
CITY = V(0.0, 60.0, 5.0)
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST_R = arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST = arms(REST_L, REST_R)

# ---------------------------------------------------------------- de rolstoel komt de heuvel op
C0, C1 = V(4.2, -7.5, 0.0), V(1.32, -0.30, 0.0)
D = (C1 - C0).normalized()
R_PATH = math.degrees(math.atan2(D.x, -D.y))
R_END = -150.0
T_ARR = 4.4
stoel = ND.rolstoel("Rolstoel", tuple(C0), rot_z=R_PATH)
for t, p, r in ((0.0, C0, R_PATH), (T_ARR - 0.4, C1 - D * 0.15, R_PATH), (T_ARR, C1, R_END), (END, C1, R_END)):
    key(stoel, t, loc=tuple(p), rot=(0, 0, r))
pk = S.actor("pestkop_oud", C0, R_PATH)
ps, pz = sit(pk, seat_top=0.47)
for t, p, r in ((0.0, C0, R_PATH), (T_ARR - 0.4, C1 - D * 0.15, R_PATH), (T_ARR, C1, R_END)):
    S.place(pk, t, p + V(0, 0, pz), r)
verp = S.actor("verpleger", C0 - D * 1.05, R_PATH)
S.walk(verp, 0.0, T_ARR - 0.4, [C0 - D * 1.05, C1 - D * 1.2], stride=0.5)
S.beat(verp, T_ARR, "staan", face="blij", face_amt=0.5, at=HH)
S.hold(verp, t_e)
for o in [stoel] + list(stoel.children_recursive):
    show(o, 0.0, t_e)
show(pk.rig, 0.0, t_e)
show(verp.rig, 0.0, t_e)
PH_ = S.head(pk, T_ARR + 0.2)

S.beat(pk, 0.0, **ps, arms=arms(arm("L", (0.30, 0.55, -0.78), (0.10, 0.95, 0.10)), arm("R", (0.30, 0.55, -0.78), (0.10, 0.95, 0.10))),
       face="neutraal", face_amt=0.5, at=HH)
S.beat(held, 0.0, **hs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(held, 2.6, **hs, arms=REST, face="verbaasd", face_amt=0.6, at=S.head(pk, 2.6))
S.beat(held, T_ARR, **hs, arms=REST, face="neutraal", face_amt=0.6, at=PH_)

# ---------------------------------------------------------------- 12b-12c
PK_REST = arms(arm("L", (0.30, 0.55, -0.78), (0.10, 0.95, 0.10)), arm("R", (0.30, 0.55, -0.78), (0.10, 0.95, 0.10)))
S.beat(pk, t_b, **ps, arms=PK_REST, face="grijns", face_amt=0.5, at=HH)                 # "I pushed you off that ramp."
S.beat(held, t_b + 2.2, **hs, arms=REST, face="grijns", face_amt=0.6, at=PH_)           # "Like a hundred times."
S.beat(pk, t_b + 2.8, **ps, arms=PK_REST, face="lach", face_amt=0.6, at=HH, body={"head": (6, 0, 4)})
S.beat(pk, t_c, **ps, arms=PK_REST, face="verdrietig", face_amt=0.6, at=HH)
MEET = (HH + PH_) * 0.5 + V(0, 0.15, -0.75)
S.reach(pk, t_c + 0.3, "R", None, 0.0)
for k, t in enumerate(frange(t_c + 0.9, t_c + 2.4, 0.08)):                                # trillende hand
    S.reach(pk, t, "R", MEET + V(0.12, 0.0, 0.012 if k % 2 else -0.012))
S.reach(held, t_c + 1.8, "R", None, 0.0)
S.reach(held, t_c + 2.4, "R", MEET + V(-0.06, 0.0, 0.0))
S.reach(pk, t_c + 2.4, "R", MEET + V(0.06, 0.0, 0.0))
S.reach(pk, t_d2, "R", MEET + V(0.06, 0.0, 0.0))
S.reach(held, t_d2, "R", MEET + V(-0.06, 0.0, 0.0))
S.beat(held, t_c, **hs, arms=REST, face="verbaasd", face_amt=0.6, at=PH_)
S.beat(held, t_d, **hs, arms=REST, face="verdrietig", face_amt=0.4, at=PH_)
S.beat(pk, t_d, **ps, arms=PK_REST, face="blij", face_amt=0.4, at=HH)

# ---------------------------------------------------------------- 12d3: de penning in zijn hand
PALM = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.10, 0.90, 0.30), None, (0, 160, 0))
S.reach(held, t_d3 - 0.05, "R", None, 0.0)
S.reach(pk, t_d3 - 0.05, "R", None, 0.0)
S.beat(held, t_d3, **hs, arms=arms(REST_L, PALM), face="verbaasd", face_amt=0.5, look=(0.3, -0.8), body={"head": (16, 20, 0)})
pen = ND.politiepenning("Politiepenning", (0, 0, 0), rot=(0, 0, 0), kras=True)
pen.scale = (1.4,) * 3
grab(S, pen, held, t_d3, "hand.R", loc=(0, 0.06, 0.02), rot=(0, 0, 0))
for o in [pen] + list(pen.children_recursive):
    show(o, t_d3, t_e)
HAND = S.bone_world(held, "hand.R", t_d3 + 0.5)
S.reach(pk, t_d3 + 0.3, "R", HAND + V(0.10, 0.05, 0.12))
S.reach(pk, t_d3 + 1.0, "R", HAND + V(0.04, 0.03, 0.07))                                  # drukt hem in zijn hand
S.reach(pk, t_d3 + 2.6, "R", HAND + V(0.04, 0.03, 0.07))
S.reach(pk, t_d3 + 3.4, "R", None, 0.0)
S.beat(pk, t_d3, **ps, arms=PK_REST, face="blij", face_amt=0.5, at=HAND)
S.beat(pk, t_d3 + 1.5, **ps, arms=PK_REST, face="grijns", face_amt=0.5, at=HH)
S.hold(pk, t_e)

# ---------------------------------------------------------------- 12d2: de oudste mens ooit (foto op een eigen podium)
ST = V(520.0, 0.0, 0.0)
T.box("Foto122_achter", tuple(ST + V(0, 1.0, 0)), (4.0, 0.1, 3.4), S.mat("foto_grijs_achter", (0.55, 0.53, 0.50)), bevel=0, ol=0)
T.plane("Foto122_vloer", tuple(ST + V(0, 0, 0)), (6, 6), S.mat("foto_grijs_vloer", (0.45, 0.44, 0.42)))
oud = S.actor("oma", ST + V(0, 0.3, 0), 0, label="oudste_vrouw")
os_, oz = sit(oud, seat_top=0.45)
T.box("Foto122_stoel", tuple(ST + V(0, 0.32, 0)), (0.5, 0.5, 0.45), S.mat("foto_grijs_stoel", (0.35, 0.34, 0.33)), bevel=0.02, ol=0)
S.place(oud, 0, ST + V(0, 0.3, oz), 0)
S.beat(oud, 0.0, **os_, face="blij", face_amt=0.4, at=ST + V(0, -4, 1.0), arms=PK_REST)
S.hold(oud, END)
S.qc_skip.add(oud.name)
rand = S.mat("fotorand_oud", (0.92, 0.88, 0.78))
CAMP = ST + V(0, -2.6, 1.0)
for nm, (x, z, w, h) in (("o", (0, -0.37, 0.80, 0.08)), ("b", (0, 0.37, 0.80, 0.08)), ("l", (-0.45, 0, 0.1, 0.82)), ("r", (0.45, 0, 0.1, 0.82))):
    T.box(f"Foto122_rand_{nm}", tuple(CAMP + V(x, 1.15, z - h / 2)), (w, 0.01, h), rand, bevel=0, ol=0)
S.text("122 YEARS", t_d2 + 0.4, t_d3, loc=(0.5, 0.16), size=150, color=(1.0, 1.0, 1.0), anchor=("CENTER", "CENTER"))
S.no_hud.append((t_d2, t_d3))

# ---------------------------------------------------------------- 12e-12f: alleen
S.beat(held, t_e, **hs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(held, t_f, **hs, arms=REST, face="verdrietig", face_amt=0.35, at=CITY)
S.hold(held, END)
A.blink_at(held, F(t_f + 1.0))

# ---------------------------------------------------------------- camera's
CAMH = (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22)
S.cam(0.0, CAMH)
MID = (HH + PH_) * 0.5
S.cam(t_b, (MID + V(-0.3, 2.6, -0.55), MID + V(0, 0, -0.3), 30), (MID + V(-0.28, 2.45, -0.55), MID + V(0, 0, -0.3), 30))
S.cam(t_c, (HH + V(-0.75, 0.55, 0.12), PH_ + V(0, 0, -0.3), 35), (HH + V(-0.7, 0.52, 0.1), PH_ + V(0, 0, -0.3), 35))
S.cam(t_d, (HH + V(0.45, 1.3, -0.3), HH + V(0, 0, -0.12), 35), (HH + V(0.42, 1.2, -0.3), HH + V(0, 0, -0.12), 35))
S.cam(t_d2, (CAMP, ST + V(0, 0.3, 1.0), 35), (CAMP + V(0, 0.12, 0), ST + V(0, 0.3, 1.0), 35))
S.cam(t_d3, (HAND + V(-0.25, 0.55, 0.42), HAND, 40), (HAND + V(-0.22, 0.5, 0.38), HAND, 40))
S.cam(t_e, CAMH)
S.cam(t_f, (HH + V(0.5, 1.6, -0.25), HH + V(0, 0, -0.1), 32), (HH + V(0.4, 1.25, -0.22), HH + V(0, 0, -0.1), 32))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2110, t0=0.0, big=True)
S.jump(0.0)
S.say("D12-01", at=0.2)
S.say("D12-02", who=pk, at=t_b + 0.15)
S.say("D12-03", who=held, at=t_b + 2.4)
S.say("D12-04", who=pk, at=t_c + 0.4)
S.say("D12-05", at=t_d + 0.15)
S.say("D12-06", at=t_d2 + 0.2)
S.say("D12-07", who=pk, at=t_d3 + 1.4)
S.say("D12-08", at=t_e + 0.25)
S.say("D12-09", at=t_f + 0.3)
S.tick(t_f + 2.4, 0.5)
S.sfx("sfx_whoosh", END - 0.35, 0.45)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.08)
S.music("m_vredig_klok", 0.0, END, vol=0.15, fade_in=0.5, fade_out=0.3)
S.finish(length=END, tail=0.0)
