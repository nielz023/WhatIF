"""F03a · Dag 1 · 1x · keuken, ontbijt. Het whiteboard: TUESDAY 9:00 -> CANDLES!!
Broertje: 'Don't be late for my candles.' Papa: 'You know why you're always late?...'

    blender -b -P anim/v2/scenes/f03a_ontbijt.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f03a", "keuken", "dag1")

TX, TY, TZ = 0.2, -0.6, 0.76
FX = 4.8 / 2 - 0.42
WB = V(FX + 0.06, 4.2 / 2 - 0.73 - 0.008, 0.78)          # midden van het whiteboard op de koelkast
DAD_AT = V(TX - 0.38, TY + 0.62, 0)
BRO_AT = V(TX + 0.38, TY + 0.62, 0)
MOM_AT = V(-0.95, 1.2, 0)
HERO_AT = V(1.25, -1.05, 0)

# ---------------------------------------------------------------- set
for o in bpy.data.objects:
    if o.name.startswith("Krant"):
        o.hide_render = True                    # papa leest op zijn tablet
bowl = S.obj("Ontbijt_broertje")
bowl.location = (TX + 0.36, TY + 0.27, TZ)
S.obj("Ontbijt_bord").location = (TX - 0.38, TY + 0.26, TZ)
S.obj("Koffiemok").location = (TX - 0.16, TY + 0.3, TZ)
# niets tussen de camera en de gezichten: doos naast het broertje, fruit naar de hoek, melk weg
for nm, d in (("Cornflakes", V(0.4, 0.35, 0)), ("Fruit", V(-0.65, -0.25, 0)), ("Melkpak", None)):
    for o in bpy.data.objects:
        if o.name.startswith(nm) and o.parent is None:
            if d is None:
                o.hide_render = True
            else:
                o.location += d
lunch = []
for k, (x, c) in enumerate(((-1.15, (0.95, 0.35, 0.15)), (-0.75, (0.25, 0.55, 0.95)), (-0.35, (0.35, 0.8, 0.35)))):
    lunch.append(T.box(f"Broodtrommel_{k + 1}", (x, 1.5, 0.9), (0.2, 0.14, 0.07), S.mat(f"broodtrommel{k}", c), bevel=0.015, ol=0))
T.box("Boterham_stapel", (-0.55, 1.62, 0.9), (0.11, 0.11, 0.05), S.mat("brood", (0.92, 0.75, 0.45)), bevel=0.01, ol=0)

# ---------------------------------------------------------------- figuren
papa = S.actor("papa", DAD_AT, 0)
bro = S.actor("broertje", BRO_AT, -8)
mama = S.actor("mama", MOM_AT, 180, energy=0.8)
held = S.actor("hoofdpersonage", HERO_AT, heading(HERO_AT, BRO_AT))
SIT_D, zd = sit(papa)
SIT_B, zb = sit(bro)
S.place(papa, 0, DAD_AT + V(0, 0, zd), 0)
S.place(bro, 0, BRO_AT + V(0, 0, zb), -8)
tablet = prop_tablet(S, "Tablet_papa", (0, 0, 0))
spoon = T.cyl("Lepel_broertje", (0, 0, 0), 0.006, 0.15, P.m("metaal"), seg=6, ol=0)

# ---------------------------------------------------------------- tijdlijn
S.hud2(1, "1x", clock=clock(7 * 3600 + 34 * 60, 1.0, hhmm=True, day="MON"), t0=0.3)
l1 = S.say("F03-01", gap=0.4)
l2 = S.say("F03-02", gap=0.4)
l3 = S.say("F03-03", gap=0.35, who=bro, gain=1.2)
l4 = S.say("F03-04", gap=0.3)
l5 = S.say("F03-05", gap=0.35, who=papa, gain=1.2)
l6 = S.say("F03-06", gap=0.25)
END = l6[1] + 0.6
S.music("piano_warm", 0.0, END + 2, vol=0.2, fade_in=0.6, fade_out=0.8)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.10)
WBT = l1[0] + 2.4                               # whiteboard in beeld
S.sfx("sfx_klok_motief", WBT + 0.1, 0.28, cut=(0, 5.0))

# ---------------------------------------------------------------- papa: tablet, dan zijn grap
S.beat(papa, 0.0, **SIT_D, pose="staan", face="neutraal", look=(0, -0.6), body={"head": (18, 0, 0)}, arms=HOLD_FRONT_L)
grab(S, tablet, papa, 0.0, "hand.L", loc=(0.0, 0.06, 0.04), rot=(-70, 0, 0))
S.beat(papa, l2[0] + 2.0, **SIT_D, pose="staan", face="blij", face_amt=0.3, look=(0.1, -0.6), body={"head": (16, 0, 0)}, arms=HOLD_FRONT_L)
S.beat(papa, l5[0] - 0.4, **SIT_D, pose="staan", face="zelfverzekerd", face_amt=0.7, at=S.head(held), arms=HOLD_FRONT_L)
S.beat(papa, l5[0] + 1.9, **SIT_D, pose="staan", face="grijns", at=S.head(held), arms=HOLD_FRONT_L, body={"head": (0, 0, 6)})
S.beat(papa, l5[1] + 0.2, **SIT_D, pose="staan", face="lach", face_amt=0.8, at=S.head(held), arms=HOLD_FRONT_L, body={"chest": (-6, 0, 0)})
S.hold(papa, END)

# ---------------------------------------------------------------- broertje: luid cornflakes eten
BOWL = Vector(bowl.location) + V(0, 0, 0.08)
S.beat(bro, 0.0, **SIT_B, pose="staan", face="blij", at=BOWL)
grab(S, spoon, bro, 0.0, "hand.R", loc=(0, 0.05, 0.0), rot=(90, 0, 0))
t = 0.3
while t < l3[0] - 0.6:                          # lepel naar de kom, naar de mond
    S.reach(bro, t, "R", BOWL + V(-0.02, -0.02, 0.02))
    S.reach(bro, t + 0.45, "R", S.head(bro) + V(0.05, -0.28, -0.12))
    A.key_prop(bro.rig, "mond_open", 0.0, F(t + 0.3))
    A.key_prop(bro.rig, "mond_open", 0.5, F(t + 0.5))
    A.key_prop(bro.rig, "mond_open", 0.1, F(t + 0.7))
    t += 1.1
S.reach(bro, l3[0] - 0.4, "R", BOWL + V(-0.03, -0.03, 0.05))
S.beat(bro, l3[0] - 0.3, **SIT_B, pose="staan", face="vastberaden", face_amt=0.6, at=S.head(held), body={"head": (-6, 0, 0)})
S.beat(bro, l3[0] + 0.6, **SIT_B, pose="wijzen", amount=0.6, face="vastberaden", face_amt=0.8, at=S.head(held))
S.beat(bro, l4[0] + 0.6, **SIT_B, pose="staan", face="blij", at=S.head(held))
S.beat(bro, l5[0] + 0.5, **SIT_B, pose="staan", face="twijfel", face_amt=0.6, at=S.head(papa))
S.beat(bro, l6[0] + 0.3, **SIT_B, pose="staan", face="blij", face_amt=0.5, at=BOWL)
S.hold(bro, END)

# ---------------------------------------------------------------- mama: broodtrommels inpakken
S.beat(mama, 0.0, "staan", face="neutraal", look=(0, -0.5), body={"head": (16, 0, 0)})
for k, t in enumerate((0.4, 2.0, 3.6, 5.2, 6.8, 8.4, 10.0, 11.6)):
    b = lunch[k % 3].location
    S.reach(mama, t, "L" if k % 2 else "R", Vector(b) + V(0.05 * (1 if k % 2 else -1), -0.05, 0.12))
S.beat(mama, l3[0] + 0.2, "staan", face="blij", face_amt=0.7, at=S.head(bro), body={"head": (0, -30, 0)})
S.beat(mama, l4[1], "staan", face="neutraal", look=(0, -0.5), body={"head": (16, 0, 0)})
S.beat(mama, l5[1] + 0.1, "staan", face="twijfel", face_amt=0.6, at=S.head(papa), body={"head": (0, -25, 0)})
S.hold(mama, END)

# ---------------------------------------------------------------- hij
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=WB + V(0, 0, 0.1))
S.beat(held, l2[0] + 0.5, "staan", face="blij", face_amt=0.4, at=S.head(bro))
S.beat(held, l3[1] - 0.1, "staan", face="blij", face_amt=0.7, at=S.head(bro), body={"head": (10, 0, 0)})    # knikt
S.beat(held, l4[0] + 0.4, "staan", face="blij", face_amt=0.7, at=S.head(bro), body={"head": (-4, 0, 0)})
S.beat(held, l5[0] + 0.3, "staan", face="neutraal", at=S.head(papa))
S.beat(held, l6[0] + 0.2, "armen_over", face="twijfel", face_amt=0.9, at=S.head(papa))
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.6, -4.0, 1.75), (-0.2, 0.4, 1.0), 22), ((1.4, -3.7, 1.7), (-0.2, 0.4, 1.0), 23))
S.cam(WBT, (WB + V(-0.3, -1.05, 0.12), WB, 40), (WB + V(-0.22, -0.78, 0.08), WB, 44), dof=2.0)
S.cam(l2[0] + 0.6, S.shot(bro, l2[0] + 1, "mcu", az=-15, lens=36, h=0.1), S.shot(bro, l2[0] + 4, "mcu", az=-10, lens=40, h=0.1))
S.cam(l2[0] + 4.4, S.shot(mama, l2[0] + 5, "med", az=150, lens=32, h=0.15))
S.cam(l3[0] - 0.2, S.shot(bro, l3[0], "cu", az=20, lens=42, h=0.05))
S.cam(l4[0] - 0.1, S.shot(held, l4[0], "mcu", az=-15, lens=36), S.shot(held, l4[1], "cu", az=-10, lens=42))
S.cam(l5[0] - 0.2, S.shot(papa, l5[0], "mcu", az=12, lens=36, h=0.05), S.shot(papa, l5[1], "cu", az=10, lens=42, h=0.05))
S.cam(l6[0] - 0.05, S.shot(held, l6[0] + 0.5, "mcu", az=-25, lens=38))
S.wall(l4[0] - 0.1, l5[0] - 0.2)                 # tegenshots op hem: de voormuur achter hem
S.wall(l6[0] - 0.05, l6[1] - 0.6)
S.cam(l6[1] - 0.6, ((1.5, -3.9, 1.7), (-0.2, 0.3, 1.0), 23))

S.finish(length=END)
