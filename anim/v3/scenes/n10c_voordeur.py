"""N10c · Dag 4: de voordeur (script scène 10c3-10c5). Straat zonder stroom, blauw maanlicht. Ook bron voor teaser 0d.
10c3 MEDIUM statisch met trage push: zijn fiets ligt op de stoep, hij rent naar de voordeur en rukt twee keer aan de klink.
     Op slot. Achter hem stapt een lange schaduw uit het donker, een hand komt op zijn schouder. Hij bevriest.
10c4 MEDIUM statisch: hij draait zich met een ruk om, rug tegen de deur, handen half omhoog. Het is de agent;
     hij knipt zijn zaklamp aan en richt hem naar de grond. AGENT: "Easy. It's me. Get inside, kid. Nobody should be out here tonight."
10c5 CLOSE: de deur gaat open, papa trekt hem aan zijn onderarm naar binnen, de deur valt dicht. De agent loopt weg in het donker.

    blender -b -P anim/v3/scenes/n10c_voordeur.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n10c", "straat", "nr_stroomuit", exposure=0.2, night=True)
sh = S.cuts([2.6, 5.6, 2.6])
END = sh[-1][1]
t_4, t_5 = sh[1][0], sh[2][0]

for o in list(bpy.data.objects):
    if o.name.startswith("Zaklamp_agent"):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# ---------------------------------------------------------------- de voordeur als los blad (scharnier links), met donkere gang erachter
DX0, DX1, DY, DZ0, DZ1 = -1.88, -0.92, 12.9, 0.3, 2.45
T.box("Deuropening_donker", ((DX0 + DX1) / 2, DY + 0.012, DZ0), (DX1 - DX0, 0.005, DZ1 - DZ0), S.mat("gang_donker", (0.02, 0.025, 0.04)),
      bevel=0, ol=0)
hinge = bpy.data.objects.new("Voordeur_scharnier", None)
T._link(hinge)
hinge.location = (DX0, DY - 0.03, DZ0)
blad = T.box("Voordeur_blad", ((DX1 - DX0) / 2, 0, 0), (DX1 - DX0 - 0.01, 0.05, DZ1 - DZ0 - 0.01), S.mat("voordeur_rood", (0.55, 0.12, 0.10)),
             bevel=0.01, ol=0.004)
klink = T.box("Voordeur_klink", ((DX1 - DX0) - 0.12, -0.05, 1.0), (0.12, 0.04, 0.025), S.mat("messing", (0.85, 0.65, 0.25)), bevel=0.005, ol=0)
blad.parent = hinge
klink.parent = hinge
T_OPEN, T_SHUT = t_5 + 0.15, t_5 + 1.35
for t, a in ((0.0, 0), (T_OPEN, 0), (T_OPEN + 0.35, -95), (T_SHUT - 0.2, -95), (T_SHUT, 0), (END, 0)):
    hinge.rotation_euler = (0, 0, math.radians(a))
    hinge.keyframe_insert("rotation_euler", frame=F(t))
# rammelen aan de klink: de klink zakt twee keer
KL = V(DX1 - 0.12, DY - 0.08, DZ0 + 1.0)
for t, rx in ((0.0, 0), (1.15, 0), (1.25, -25), (1.4, 0), (1.55, -25), (1.7, 0)):
    klink.rotation_euler = (0, math.radians(rx), 0)
    klink.keyframe_insert("rotation_euler", frame=F(t))

# ---------------------------------------------------------------- de jongen: rent naar de deur, rukt aan de klink
DOORSTEP = V(-1.32, 12.42, 0.3)
held = S.actor("hoofdpersonage_kind", (0.0, 7.7, 0.12), 150)
S.run(held, 0.0, 1.0, [V(0.0, 7.7, 0.12), V(-1.25, 9.2, 0.02), V(-1.3, 11.7, 0.02), DOORSTEP], stride=0.6, lift=0.22, lean=16,
      ease_in=0.0, ease_out=0.3)
S.beat(held, 0.05, "staan", face="bang", face_amt=1.0, feet="keep")
S.reach(held, 0.0, "R", inf=0.0)
for t, dz in ((1.1, 0.0), (1.25, -0.06), (1.42, 0.0), (1.57, -0.06), (1.75, 0.0)):
    S.reach(held, t, "R", KL + V(0.0, -0.04, dz - 0.02))
S.beat(held, 1.25, "staan", face="bang", face_amt=1.0, body={"spine": (-6, 0, 0)}, feet="keep")
S.beat(held, 1.57, "staan", face="bang", face_amt=1.0, body={"spine": (-6, 0, 0)}, feet="keep")
# de hand op zijn schouder: hij bevriest, schouders schieten omhoog
T_HAND = 2.0
S.beat(held, T_HAND + 0.05, "schouders_op", amount=1.0, face="geschrokken", face_amt=1.0, feet="keep")
S.reach(held, T_HAND, "R", KL + V(0, -0.05, -0.03))
S.reach(held, T_HAND + 0.15, "R", inf=0.0)
# 10c4: draait met een ruk om, rug tegen de deur, handen half omhoog, laat ze zakken als hij de agent herkent
S.turn(held, t_4 + 0.05, t_4 + 0.3, 20)
S.beat(held, t_4 + 0.3, "schrik", amount=0.8, face="bang", face_amt=1.0, at=V(-2.0, 11.5, 1.7), body={"spine": (-5, 0, 0)}, feet="keep")
S.beat(held, t_4 + 1.6, "staan", face="geschrokken", face_amt=0.7, at=V(-2.0, 11.5, 1.7), feet="keep")
S.beat(held, t_4 + 2.2, "staan", face="nerveus", face_amt=0.6, at=V(-2.0, 11.5, 1.7), body={"chest": (-4, 0, 0)}, feet="keep")
S.beat(held, t_4 + 4.6, "staan", face="twijfel", face_amt=0.6, at=V(-2.0, 11.5, 1.6), feet="keep")
# 10c5: papa trekt hem aan zijn onderarm naar binnen
IN0 = V(-0.95, 12.4, 0.3)
S.teleport(held, t_5, IN0, 20)
S.walk(held, t_5 + 0.55, t_5 + 1.0, [IN0, V(-1.25, 12.8, 0.3)], stride=0.4, turn=False)
visible(held.body, 0.0, True)
visible(held.body, t_5 + 1.05, False)
S.hold(held, END)

# ---------------------------------------------------------------- de agent stapt uit het donker
agent = S.actor("agent", (-5.2, 10.3, 0.02), 110)
AG_END = V(-1.78, 12.0, 0.05)                              # vlak achter de jongen: zijn arm rekt niet
S.walk(agent, 0.55, 1.95, [V(-5.2, 10.3, 0.02), V(-3.3, 10.9, 0.02), AG_END], stride=0.62)
S.beat(agent, 1.95, "staan", face="neutraal", face_amt=0.5, at=S.head(held, 2.0), feet="keep")
S.reach(agent, 0.0, "L", inf=0.0)
S.reach(agent, 1.75, "L", inf=0.0)
SH = DOORSTEP + V(-0.2, 0.0, 1.05)                          # linkerschouder van de jongen (staat met zijn rug naar ons)
S.reach(agent, T_HAND, "L", SH)
S.reach(agent, t_4 + 0.2, "L", SH + V(-0.15, -0.1, 0.0))
S.reach(agent, t_4 + 0.45, "L", inf=0.0)
S.beat(agent, t_4 + 0.5, "staan", face="neutraal", face_amt=0.6, at=S.head(held, t_4 + 0.5), feet="keep")
S.beat(agent, t_4 + 1.5, "staan", face="blij", face_amt=0.25, at=S.head(held, t_4 + 1.5), feet="keep")
S.beat(agent, t_5, "staan", face="neutraal", face_amt=0.5, at=V(-1.4, 12.6, 1.3), feet="keep")
S.walk(agent, t_5 + 1.0, END, [AG_END, V(-2.5, 10.3, 0.02), V(-1.6, 8.6, 0.02)], stride=0.6)
S.hold(agent, END)
# zaklamp in zijn rechterhand, knipt aan en schijnt naar de grond
zl = [T.cyl("Zaklamp_romp", (0, 0, -0.1), 0.022, 0.2, S.mat("zaklamp_zwart", (0.08, 0.08, 0.09)), seg=12, ol=0),
      T.cyl("Zaklamp_kop", (0, 0, 0.1), 0.034, 0.05, S.mat("zaklamp_zwart", (0.08, 0.08, 0.09)), seg=12, ol=0)]
zaklamp = T.merge("Zaklamp", zl, ol=0.003)
glas = T.cyl("Zaklamp_glas", (0, 0, 0.15), 0.03, 0.004, S.mat("zaklamp_glas", (1.0, 0.95, 0.8), 0.01), seg=12, ol=0)
glas.parent = zaklamp
spot = bpy.data.lights.new("Zaklamp_bundel", "SPOT")
spot.energy, spot.spot_size, spot.spot_blend, spot.color = 0.0, math.radians(32), 0.4, (1.0, 0.93, 0.8)
so = bpy.data.objects.new("Zaklamp_bundel", spot)
bpy.context.scene.collection.objects.link(so)
so.parent = zaklamp
so.location = (0, 0, 0.16)
so.rotation_euler = (math.radians(180), 0, 0)               # spot schijnt langs lokaal -z: draai zodat hij langs +z (de kop) schijnt
T_CLICK = t_4 + 1.1
for t, e in ((0.0, 0.0), (T_CLICK, 0.0), (T_CLICK + 0.04, 900.0), (END, 900.0)):
    spot.energy = e
    spot.keyframe_insert("energy", frame=F(t))
emission_key("zaklamp_glas", 0.0, 0.0)
emission_key("zaklamp_glas", T_CLICK + 0.04, 8.0)
# de lamp volgt zijn rechterhand en wijst schuin naar de grond voor de jongen
zaklamp.rotation_mode = "QUATERNION"
for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    hp = (S.bone_world(agent, "hand.R", t, tail=False) + S.bone_world(agent, "hand.R", t)) / 2
    tgt = V(-1.5, 12.0, 0.0) if t < t_5 + 1.0 else hp + V(0.3, -1.5, -1.2)
    d = (tgt - hp).normalized()
    zaklamp.location = hp
    zaklamp.rotation_quaternion = d.to_track_quat("Z", "Y")
    zaklamp.keyframe_insert("location", frame=f)
    zaklamp.keyframe_insert("rotation_quaternion", frame=f)
S.reach(agent, 0.0, "R", inf=0.0)

# ---------------------------------------------------------------- papa in de deuropening
papa = S.actor("papa", (-1.45, 12.75, 0.3), 10)
visible(papa.body, 0.0, False)
visible(papa.body, T_OPEN + 0.1, True)
visible(papa.body, T_SHUT - 0.15, False)
S.beat(papa, T_OPEN, "staan", face="bang", face_amt=0.6, at=S.head(held, t_5 + 0.3))
S.reach(papa, 0.0, "L", inf=0.0)
S.reach(papa, T_OPEN + 0.2, "L", inf=0.0)
# rechterbovenarm van de jongen (staat met zijn gezicht naar ons), met papa's linkerhand: die is dichterbij
FA = (S.bone_world(held, "upper_arm.R", t_5 + 0.3, tail=False) + S.bone_world(held, "upper_arm.R", t_5 + 0.3)) / 2
S.reach(papa, T_OPEN + 0.35, "L", FA)
S.reach(papa, t_5 + 1.0, "L", V(-1.3, 12.85, 1.1))
S.walk(papa, t_5 + 0.5, t_5 + 1.0, [V(-1.45, 12.75, 0.3), V(-1.6, 13.15, 0.3)], stride=0.35, turn=False)   # stapt achteruit naar binnen
S.hold(papa, END)

# ---------------------------------------------------------------- camera's
# 10c3 MEDIUM vanaf de stoep: hij rent naar de deur, de agent komt van links uit het donker
S.cam(0.0, ((0.4, 7.2, 1.55), (-1.5, 12.0, 1.25), 28), ((0.25, 7.6, 1.55), (-1.5, 12.0, 1.25), 30))
# 10c4 MEDIUM statisch: zijn gezicht tegen de deur, de agent in profiel links
S.cam(t_4, ((-0.55, 9.9, 1.45), (-1.7, 12.1, 1.3), 30), ((-0.6, 10.05, 1.45), (-1.7, 12.1, 1.3), 31))
# 10c5 CLOSE: de deuropening
S.cam(t_5, ((0.35, 10.1, 1.45), (-1.3, 12.6, 1.3), 30), ((0.25, 10.3, 1.45), (-1.3, 12.6, 1.3), 31), handheld=0.25)

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 4", 0, t0=0.0)
S.sfx("sfx_tuinhek_rammel", 1.2, 0.35)
S.sfx("sfx_tuinhek_rammel", 1.55, 0.35)
S.sfx("sfx_stad_nacht_wind", 0.0, 0.05, loop_to=END)
S.sfx("sfx_zaklamp_klik", T_CLICK, 0.4)
S.say("N10-02", who=agent, at=t_4 + 0.45)
S.finish(length=END, tail=0.0)
