"""N15f · Dag 14: de pestkop op zijn troon (script scène 15f-15g). Atrium van het winkelcentrum.
15f MEDIUM: de pestkop op een troon van winkelkarren met een kroon van karton. Leunt achterover, wijst naar een
    volgeling die meteen gaat rennen. PESTKOP: "Rule twelve! No running in my mall!" De volgeling stopt midden in
    een pas en gaat stijf wandelen.
15g CLOSE: de pestkop grijnst onder zijn kroon. VO: "He now had the strictest rules in the whole city."

    blender -b -P anim/v3/scenes/n15f_troon.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n15f", "koninkrijk", "troon", exposure=0.1)
sh = S.cuts([4.4, 3.6])
END = sh[-1][1]
t_g = sh[1][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de pestkop op de troon (kijkt naar -y)
TR = V(0.0, 6.55, 0)
SEAT_TOP = 1.68
pest = S.actor("pestkop", TR, 0)
spec, z = sit(pest, seat_top=SEAT_TOP, lean=-16)
S.place(pest, 0.0, TR + V(0, 0.05, z), 0)
S.beat(pest, 0.0, **spec, face="zelfverzekerd", face_amt=0.8, look=(0.0, -0.1))
# kroon op zijn hoofd (per frame gebakken op de kruin)
kroon = S.obj("Kroon_karton")
kroon.rotation_mode = "XYZ"

# volgelingen: twee aan de kant, één loopt (rent) door het atrium
v_a = S.actor("volgeling_a", V(-4.6, 3.4, 0), 90)                  # kijkt naar +x
v_b = S.actor("volgeling_b", V(-2.9, 5.1, 0), 160)
v_c = S.actor("volgeling_c", V(2.8, 4.7, 0), -150)
for ch in (v_b, v_c):
    S.beat(ch, 0.0, "staan", face="neutraal", face_amt=0.5, at=S.headpos(pest, 0.0))
S.beat(v_a, 0.0, "staan", face="blij", face_amt=0.5, look=(0.0, 0.0))
T_RUN0, T_STOP = 0.4, 1.75
R0, R1 = V(-4.6, 3.4, 0), V(-0.9, 3.4, 0)
S.run(v_a, T_RUN0, T_STOP, [R0, R1], stride=1.0)
# hij stopt midden in een pas en gaat stijf wandelen
S.beat(v_a, T_STOP + 0.05, "staan", face="geschrokken", face_amt=0.9, at=S.headpos(pest, 0.0), feet="keep")
R2 = V(1.9, 3.4, 0)
S.walk(v_a, T_STOP + 0.6, END, [R1, R2], stride=0.22, arms=0.0)
S.beat(v_a, T_STOP + 0.7, "staan", face="nerveus", face_amt=0.8, at=S.headpos(pest, 0.0), feet="keep", body={"spine": (-4, 0, 0)})

# de pestkop wijst naar hem en schreeuwt
S.beat(pest, T_RUN0 + 0.5, **spec, face="boos", face_amt=0.7, at=S.headpos(v_a, T_RUN0 + 0.8))
S.reach(pest, 0.0, "R", inf=0.0)
S.reach(pest, T_RUN0 + 0.6, "R", inf=0.0)
for t in (T_RUN0 + 0.9, T_RUN0 + 1.4, T_STOP + 0.4):
    hp = S.headpos(v_a, t)
    sp = S.bone_world(pest, "upper_arm.R", t, tail=False)
    S.reach(pest, t, "R", sp + (hp - sp).normalized() * 0.55)
S.reach(pest, T_STOP + 1.0, "R", inf=0.0)
S.say("N15-04", who=pest, at=T_RUN0 + 0.7)
S.beat(pest, T_STOP + 1.1, **spec, face="zelfverzekerd", face_amt=0.9, look=(0.1, -0.1))
S.beat(pest, t_g, **spec, face="grijns", face_amt=1.0, look=(0.0, -0.15))
for ch in (pest, v_b, v_c):
    S.hold(ch, END)

for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    hd = S.bone_world(pest, "head", t, tail=True)
    hb = S.bone_world(pest, "head", t, tail=False)
    up = (hd - hb).normalized()
    kroon.location = hd + up * 0.04 - V(0, 0, 0.06)
    e = up.to_track_quat("Z", "Y").to_euler()
    kroon.rotation_euler = e
    kroon.keyframe_insert("location", frame=f)
    kroon.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- camera's
PH = S.headpos(pest, 1.0)
S.cam(0.0, ((0.9, -0.6, 1.7), (-0.4, 5.0, 1.5), 24), ((0.85, -0.2, 1.7), (-0.4, 5.2, 1.5), 25))
PG = S.headpos(pest, t_g + 1.0)
S.cam(t_g, (PG + V(0.25, -1.45, -0.25), PG + V(0, 0, -0.05), 32), (PG + V(0.22, -1.32, -0.22), PG + V(0, 0, -0.05), 34))

S.counter("DAY 14", 6, t0=0.0)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.05)
S.music("m_spanning_puls", 0.0, END, vol=0.15, fade_in=0.2, fade_out=0.3)
S.say("N15-05", at=t_g + 0.25)
S.finish(length=END, tail=0.0)
