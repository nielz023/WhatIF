"""N09f · Dag 3: de pestkop neemt het park in (script scène 9f-9g).
9f WIDE push-in: de pestkop en zijn volgelingen slepen dranghekken om het park. Twee jongens trekken één hek,
   schuifelend achteruit, voeten schrap. De pestkop wijst en commandeert: "This park? It's ours now."
9g CLOSE: de jongen en de beste vriend op hun fietsen aan de andere kant van het hek.
   VRIEND: "He can't just... take a park."  JONGEN: "Who's going to stop him?"

    blender -b -P anim/v3/scenes/n09f_park_hekken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n09f", "park", "dag3", exposure=0.0)
sh = S.cuts([4.4, 2.9, 2.5])
END = sh[-1][1]
t_g, t_g2 = sh[1][0], sh[2][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Fiets_held", "Fiets_vriend")):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# ---------------------------------------------------------------- twee jongens slepen hek 9 op zijn plek (naar -y)
hek = S.obj("Dranghek_9")
X9, Y_END, Y_START = hek.location.x, hek.location.y, hek.location.y + 4.3
T0, T1 = 0.2, 3.9
for t, y in ((0.0, Y_START), (T0, Y_START), (T1, Y_END), (END, Y_END)):
    hek.location.y = y
    hek.keyframe_insert("location", frame=F(t))
GAP = 0.55
pullers = []
for k, (nm, dx) in enumerate((("volgeling_a", -0.55), ("volgeling_b", 0.55))):
    p0 = V(X9 + dx, Y_START - GAP, 0)
    p1 = V(X9 + dx, Y_END - GAP, 0)
    e = S.actor(nm, p0, 180, label=f"sleper_{k}")         # kijkt naar het hek (+y), loopt achteruit
    S.walk(e, T0, T1, [p0, p1], stride=0.32, turn=False)
    S.beat(e, T0, "staan", face="inspanning", face_amt=0.8, at=V(X9, Y_START, 0.9), body={"spine": (-10, 0, 0)}, feet="keep")
    S.beat(e, T1, "staan", face="inspanning", face_amt=0.6, at=V(X9, Y_END, 0.9), body={"spine": (-8, 0, 0)}, feet="keep")
    S.beat(e, T1 + 0.5, "staan", face="grijns", face_amt=0.6, at=V(1.0, -14.6, 1.5), feet="keep")
    for side, sx in (("L", -0.18), ("R", 0.18)):
        # personage kijkt naar +y: zijn linkerhand zit aan +x
        hx = X9 + dx - sx
        for j in range(7):
            u = j / 6
            t = T0 + (T1 - T0) * u
            y = Y_START + (Y_END - Y_START) * u
            S.reach(e, t, side, V(hx, y - 0.03, 1.08))
        S.reach(e, T1 + 0.3, side, inf=0.0)
        S.reach(e, 0.0, side, V(hx, Y_START - 0.03, 1.08))
    S.hold(e, END)
    pullers.append(e)

# twee andere volgelingen zetten verderop een hek recht (achtergrond)
hek2 = S.obj("Dranghek_12")
for t, rz in ((0.0, 35), (1.0, 35), (2.6, 0), (END, 0)):
    hek2.rotation_euler.z = math.radians(rz)
    hek2.keyframe_insert("rotation_euler", frame=F(t))
for k, (nm, p) in enumerate((("kind_a", V(10.9, -13.0, 0)), ("volgeling_c", V(13.1, -14.1, 0)))):
    e = S.actor(nm, p, 180 if k == 0 else 0, label=f"helper_{k}")
    S.beat(e, 0.0, "duwen", amount=0.7, face="inspanning", face_amt=0.7, at=hek2.location + V(0, 0, 0.8))
    S.beat(e, 2.6, "staan", face="neutraal", face_amt=0.5, at=hek2.location + V(0, 0, 0.8))
    S.hold(e, END)

# ---------------------------------------------------------------- de pestkop: wijst, commandeert, draait naar de fietsers
P_AT = V(2.1, -11.3, 0)
bully = S.actor("pestkop", P_AT, 110)
S.beat(bully, 0.0, "armen_over", amount=1.0, face="grijns", face_amt=0.7, at=V(X9, -11.0, 0.8))
S.beat(bully, 0.9, "wijzen", amount=1.0, face="boos", face_amt=0.6, at=V(X9, -11.5, 0.8))
S.beat(bully, 1.9, "wijzen", amount=1.0, face="boos", face_amt=0.8, at=V(X9, -12.8, 0.8))
S.turn(bully, 2.0, 2.4, 172)
S.beat(bully, 2.4, "handen_zij", amount=1.0, face="grijns", face_amt=1.0, at=V(0.5, -6.5, 1.5))
S.beat(bully, 3.6, "armen_over", amount=1.0, face="grijns", face_amt=0.9, at=V(0.5, -6.5, 1.5))
S.beat(bully, END, "armen_over", amount=1.0, face="grijns", face_amt=0.8, at=V(2.6, -17.0, 1.3))
S.hold(bully, END)

# ---------------------------------------------------------------- 9g: de jongen en de vriend op de fiets, buiten het hek
held = S.actor("hoofdpersonage_kind", (-1.6, -17.3, 0), 180)
vr = S.actor("beste_vriend", (0.2, -17.5, 0), 180)
_, crank_h = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen")
_, crank_v = bike(S, vr, color=(0.85, 0.12, 0.12), name="Fiets_vriend")
# staan stil op hun fiets op het fietspad, voorwiel naar het hek (+y)
ride_path(S, held, crank_h, 0.0, END, [V(-1.6, -17.3, 0), V(-1.6, -17.25, 0)], cadence=0.05, lean=3)
ride_path(S, vr, crank_v, 0.0, END, [V(0.2, -17.5, 0), V(0.2, -17.45, 0)], cadence=0.05, lean=3)
for ch in (held, vr):
    visible(ch.body, 0.0, True)
S.face(vr, t_g, "verbaasd", 0.9, look=(-0.2, 0.3))
S.face(vr, t_g + 1.2, "boos", 0.6, look=(-0.3, 0.3))
S.face(held, t_g, "twijfel", 0.6, look=(0.3, 0.2))
S.face(held, t_g2, "nerveus", 0.8, look=(0.0, 0.2))
S.face(held, t_g2 + 1.2, "twijfel", 0.9, look=(-0.2, 0.0))
A.bone_rot(vr, F(t_g), "head", (0, 0, 0))
A.bone_rot(vr, F(t_g + 0.4), "head", (-6, -22, 0))                   # kijkt opzij naar de jongen
A.bone_rot(vr, F(END), "head", (-6, -22, 0))
A.bone_rot(held, F(t_g2), "head", (-8, 0, 0))
A.bone_rot(held, F(t_g2 + 0.5), "head", (-4, 20, 0))                  # kijkt naar zijn vriend
A.bone_rot(held, F(END), "head", (-6, 18, 0))

# ---------------------------------------------------------------- camera's
# 9f WIDE: vanuit het park, de slepers en de pestkop kijken naar ons, de fietsers achter het hek, push-in
S.cam(0.0, ((0.6, -5.2, 1.55), (2.0, -14.0, 1.0), 26), ((0.9, -6.3, 1.5), (2.2, -14.0, 1.0), 28), handheld=0.15)
# 9g-1 CLOSE de vriend, vanaf de parkkant
HV = S.headpos(vr, t_g + 1.0)
S.cam(t_g, (HV + V(0.6, 2.3, -0.05), HV + V(0, 0, -0.08), 40), (HV + V(0.5, 2.0, -0.05), HV + V(0, 0, -0.08), 42), handheld=0.15)
# 9g-2 CLOSE de jongen, vanaf de andere kant
HH = S.headpos(held, t_g2 + 0.8)
S.cam(t_g2, (HH + V(-0.6, 2.3, -0.05), HH + V(0, 0, -0.08), 40), (HH + V(-0.5, 2.0, -0.05), HH + V(0, 0, -0.08), 42), handheld=0.15)

# ---------------------------------------------------------------- HUD, geluid en stemmen
S.counter("DAY 3", 0, t0=0.0)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.05)
S.sfx("sfx_dranghek", T0, 0.35)
S.sfx("sfx_dranghek", 2.4, 0.25)
S.sfx("sfx_dranghek", T1 - 0.1, 0.4)
S.say("N09-04", who=bully, at=1.6)
S.say("N09-05", who=vr, at=t_g + 0.2)
S.say("N09-06", who=held, at=t_g2 + 0.3)
S.finish(length=END, tail=0.0)
