"""S03b · Dag 1 · keuken: de koelkastdeur, de mok van mama, 'I saw that', de gelijmde mok.

    blender -b -P anim/scenes/s03b_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s03b", "keuken", "ochtend")

W, D = 4.8, 4.2
FX, FRONT = W / 2 - 0.42, D / 2 - 0.73          # koelkast: midden x, voorkant y
TX, TY, TZ = 0.2, -0.6, 0.76
TOP = 0.9                                       # werkblad
MUG_AT = V(1.02, 1.6, TOP)
AT_FRIDGE = V(1.82, 0.88, 0)
AT_MUGS = V(0.98, 1.2, 0)

# ---------------------------------------------------------------- set aanpassen
for n in ("Mok_WORLDS_OKAYEST_MOM", "Mok_tekst1", "Mok_tekst2", "Krant"):
    S.obj(n).hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Krant_kolom"):
        o.hide_render = True
S.obj("Ontbijt_bord").location = (TX - 0.38, TY + 0.22, TZ)

# koelkastdeur (los, aan een scharnier), met de magneten en de tekening erop
door = T.box("Koelkastdeur", (FX, FRONT - 0.03, 0.03), (0.74, 0.035, 1.84), S.mat("koelkastdeur", (0.95, 0.95, 0.96)), bevel=0.03, ol=0.008)
grips = [T.box(f"Koelkastdeur_greep{k}", (FX - 0.3, FRONT - 0.07, z), (0.03, 0.03, 0.32), P.m("metaal"), bevel=0.01, ol=0.003)
         for k, z in enumerate((1.2, 0.68))]
kids = list(grips)
for o in bpy.data.objects:
    if o.name.startswith("Magneet_") or o.name == "Kindertekening":
        o.location.y -= 0.05
        kids.append(o)
hinge_e = hinge(door, (FX + 0.37, FRONT - 0.03, 0), kids)
# binnenkant: licht, planken en wat spullen
glow = S.mat("koelkast_licht", (0.85, 0.95, 1.0), 1.4)
T.box("Koelkast_binnen", (FX, FRONT + 0.002, 0.08), (0.66, 0.004, 1.74), glow, base=True, bevel=0, ol=0)
for z in (0.55, 0.95, 1.35):
    T.box(f"Koelkast_plank{z}", (FX, FRONT - 0.01, z), (0.64, 0.02, 0.015), S.mat("plank_glas", (0.7, 0.85, 0.95)), bevel=0, ol=0.002)
for k, (x, z, w, h, c) in enumerate(((-0.18, 0.565, 0.08, 0.22, (0.95, 0.95, 0.98)), (0.0, 0.565, 0.1, 0.12, (0.95, 0.8, 0.2)),
                                      (0.18, 0.565, 0.07, 0.25, (0.3, 0.7, 0.3)), (-0.1, 0.965, 0.16, 0.08, (0.9, 0.3, 0.25)),
                                      (0.15, 0.965, 0.09, 0.18, (0.95, 0.6, 0.2)), (0.0, 1.365, 0.2, 0.1, (0.6, 0.4, 0.9)))):
    T.box(f"Koelkast_ding{k}", (FX + x, FRONT - 0.04, z), (w, 0.06, h), S.mat(f"koelkastding{k}", c), bevel=0.01, ol=0.003)

# de mok (los oor, zodat het oor in zijn hand blijft)
mug = prop_mug(S, "Mok_mama", MUG_AT, handle=False)
handle = T.torus("Mok_mama_oor", (0, 0, 0), 0.022, 0.006, S.mat("mok_wit", (0.95, 0.94, 0.9)), rot=(90, 0, 0), seg=20, seg2=8, ol=0.003)
MUG_ROT = -40.0                                 # tekst schuin naar de camera, oor naar zijn rechterhand
_c, _s = math.cos(math.radians(MUG_ROT)), math.sin(math.radians(MUG_ROT))
OOR = V(0.048 * _c, 0.048 * _s, 0.048)
mug.rotation_euler.z = math.radians(MUG_ROT)
HANDLE_AT = MUG_AT + OOR
handle.location = HANDLE_AT
handle.rotation_euler.z = math.radians(MUG_ROT)
glued = prop_mug(S, "Mok_gelijmd", MUG_AT, handle=True, cracked=True)
glued.rotation_euler.z = math.radians(MUG_ROT + 15)
show(glued, 999)
glue = T.merge("Lijmtube", [T.box("lijm_tube", (0, 0, 0), (0.11, 0.03, 0.02), S.mat("lijm", (0.95, 0.85, 0.2)), bevel=0.008, ol=0),
                            T.cyl("lijm_dop", (0.065, 0, 0.01), 0.008, 0.025, S.mat("lijmdop", (0.9, 0.2, 0.2)), rot=(0, 90, 0), seg=8, ol=0)], ol=0.003)
glue.location = MUG_AT + V(-0.16, -0.05, 0.0)
glue.rotation_euler.z = math.radians(-25)
show(glue, 999)

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", AT_FRIDGE, 180)
papa = S.actor("papa", (TX - 0.38, TY + 0.6, 0), 0, energy=0.6)
SIT_P, zp = sit(papa)
S.place(papa, 0, (TX - 0.38, TY + 0.6, zp), 0)
broer = S.actor("broertje", (TX + 0.38, TY - 0.57, 0), 180, energy=1.2)
SIT_B, zb = sit(broer)
S.place(broer, 0, (TX + 0.38, TY - 0.57, zb), 180)
tablet = prop_tablet(S, "Tablet_papa", (TX - 0.38, TY + 0.2, 0.95))
tablet.rotation_euler = (math.radians(-28), 0, math.radians(180))
spoon = T.merge("Lepel_broertje", [T.cyl("lepel_steel", (0, 0, 0), 0.005, 0.12, P.m("metaal"), seg=6, ol=0),
                                   T.sphere("lepel_kop", (0, 0, 0.13), 0.016, P.m("metaal"), scale=(1, 0.4, 1.3), seg=8, ol=0)], ol=0.002)
attach(spoon, broer, "hand.R", (0, 0.0, 0.0), (90, 0, 0))
BOWL = V(TX + 0.38, TY - 0.25, TZ + 0.07)

# ---------------------------------------------------------------- tijdlijn
S.hud(1, "2x STRONGER", t0=0.15, tick=False)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.05)
l2 = S.say("S03-02", gap=0.4)
SLAM = l2[0] + 2.2
S.sfx("sfx_koelkast", SLAM - 0.02, 0.9)
l3 = S.say("S03-03", gap=1.0)
PICK = l3[0] + 7.1                              # 'by the handle'
CRACK = l3[1] + 0.6
S.sfx("sfx_mok_breekt", CRACK - 0.2, 1.0)        # krak op 0,2 s, de vloer op 1,55 s
HIT = CRACK + 1.35
S.music("speels", 0.0, CRACK, vol=0.30, fade_in=0.3, fade_out=0.05, start=27.0)
l4 = S.say("S03-04", at=HIT + 0.55)
l5 = S.say("S03-05", gap=0.25, who=held, gain=1.3)
l6 = S.say("S03-06", gap=0.7, who=broer, gain=1.4)
S.music("pizz_spanning", l6[0] - 0.4, l6[0] + 9.5, vol=0.22, fade_in=0.6, fade_out=1.0)
l7 = S.say("S03-07", gap=0.5)
GLUE = l7[1] + 0.6
l8 = S.say("S03-08", at=GLUE + 0.4)
KEEP = l8[1] - 1.7                              # 'Keep an eye on this mug'
S.music("mok_thema", KEEP - 0.5, KEEP + 8.0, vol=0.45, fade_in=0.05, fade_out=1.5, duck=False)
S.wait(2.6)
END = S.t + 0.2

# ---------------------------------------------------------------- koelkast
HANDLE_F = V(FX - 0.3, FRONT - 0.09, 1.1)
S.beat(held, 0.0, "ontspannen", face="neutraal", face_amt=0.5, look=(0, 0.1))
S.beat(held, l2[0] + 0.9, "staan", face="blij", face_amt=0.3, at=HANDLE_F, crouch=(0.02, 4))
S.reach(held, l2[0] + 0.9, "L", None, 0.0)
S.reach(held, l2[0] + 1.6, "L", HANDLE_F, 1.0)
S.reach(held, SLAM - 0.3, "L", HANDLE_F, 1.0)
key(hinge_e, SLAM - 0.3, rot=(0, 0, 0))
key(hinge_e, SLAM - 0.24, rot=(0, 0, 8))
key(hinge_e, SLAM, rot=(0, 0, 91), interp="LINEAR")
key(hinge_e, SLAM + 0.12, rot=(0, 0, 76))
key(hinge_e, SLAM + 0.3, rot=(0, 0, 88))
key(hinge_e, SLAM + 0.5, rot=(0, 0, 84))
S.reach(held, SLAM - 0.15, "L", None, 0.0)
S.beat(held, SLAM + 0.05, "schrik", face="geschrokken", crouch=(0.02, -8), look=(0.5, 0.1), body={"head": (-6, -25, 0)})
S.beat(held, SLAM + 0.9, "schrik", amount=0.6, face="verbaasd", face_amt=0.8, at=V(W / 2, 1.0, 1.2))
S.beat(held, SLAM + 1.9, "staan", face="nerveus", face_amt=0.7, at=V(FX, FRONT, 1.0))
# magneten vallen van de deur, stof van de muur
S.debris(V(W / 2 - 0.08, 1.0, 1.3), SLAM, n=7, size=(0.025, 0.04), color=(0.9, 0.2, 0.2), speed=(0.6, 1.6), up=0.4,
         direction=(-1, -0.4, 0.2), floor=0.0, shape="sphere", life=1.8, name="Magneet_los")
S.puff(V(W / 2 - 0.05, 1.0, 1.25), SLAM, n=6, r=(0.08, 0.16), grow=2.0, dur=1.4, color=(0.95, 0.9, 0.75), rise=0.2, spread=0.35)

# ---------------------------------------------------------------- de mok
S.walk(held, l3[0] + 0.3, l3[0] + 2.3, [AT_FRIDGE, AT_FRIDGE + V(-0.3, 0.05, 0), AT_MUGS], end_rot=180)
S.beat(held, l3[0] + 2.8, "ontspannen", face="blij", face_amt=0.4, at=MUG_AT + V(0, 0, 0.05))
S.beat(held, PICK - 0.9, "staan", face="neutraal", at=HANDLE_AT, crouch=(0.02, 14))
S.reach(held, PICK - 0.9, "R", None, 0.0)
S.reach(held, PICK - 0.1, "R", HANDLE_AT + V(0.02, 0, 0), 1.0)
LIFT = HANDLE_AT + V(0.0, -0.16, 0.08)
S.reach(held, PICK + 0.2, "R", HANDLE_AT + V(0.02, 0, 0.01), 1.0)
S.reach(held, CRACK - 0.4, "R", LIFT, 1.0)
S.reach(held, CRACK, "R", LIFT + V(0, -0.02, 0.01), 1.0)
S.beat(held, CRACK - 0.4, "staan", face="blij", face_amt=0.5, at=LIFT + V(-0.05, 0, -0.05), crouch=(0.0, 4))
S.hold(held, CRACK)
# het oor volgt de hand; de mok volgt het oor tot de krak
key(mug, 0.0, loc=MUG_AT, rot=(0, 0, MUG_ROT))
key(mug, CRACK, loc=MUG_AT, rot=(0, 0, MUG_ROT))
emp = grab(S, handle, held, PICK, "hand.R", (0, -0.045, 0), mode="loc")
grab(S, mug, held, PICK, mode="loc", target=emp, offset=-OOR, release=CRACK + 0.03)
# de val (vanaf de hand op het moment van de krak)
hand_at = S.bone_world(held, "hand.R", CRACK) + V(0, 0, 0) - OOR
key(mug, CRACK + 0.03, loc=hand_at, rot=(0, 0, MUG_ROT))
fall = HIT - CRACK
key(mug, CRACK + 0.03 + fall * 0.5, loc=hand_at + V(-0.02, -0.04, -(hand_at.z) * 0.3), rot=(0, 10, MUG_ROT))
key(mug, HIT, loc=(hand_at.x - 0.04, hand_at.y - 0.08, 0.0), rot=(0, 25, MUG_ROT + 10))
for fc in A._fcurves(mug):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
show(mug, 0, HIT + 1 / FPS)
FLOOR_HIT = V(hand_at.x - 0.04, hand_at.y - 0.08, 0.0)

S.debris(FLOOR_HIT + V(0, 0, 0.04), HIT, n=12, size=(0.03, 0.065), color=(0.95, 0.94, 0.9), speed=(0.5, 1.6), up=0.5,
         floor=0.0, life=1.2, name="Mokscherf")
# reactie: verstijft, kijkt naar het oor in zijn hand, dan naar de deur (mama), draait om
S.beat(held, CRACK + 0.15, "staan", face="geschrokken", face_amt=0.7, at=LIFT, crouch=(0.0, 0))
S.reach(held, CRACK + 0.3, "R", LIFT + V(0, 0.0, 0.03), 1.0)
S.beat(held, HIT + 0.1, "schrik", amount=0.4, face="bang", at=FLOOR_HIT, crouch=(0.02, 10))
S.reach(held, HIT + 0.4, "R", LIFT + V(0.05, 0.05, 0.0), 1.0)
TURN = HIT + 0.45
S.reach(held, TURN, "R", None, 0.0)
S.turn(held, TURN, TURN + 0.45, 0, AT_MUGS + V(0, -0.08, 0))
S.beat(held, TURN + 0.45, "schrik", amount=0.4, face="bang", at=FLOOR_HIT)
S.beat(held, l4[0] + 0.3, "schrik", amount=0.3, face="bang", look=(0.7, 0.1), body={"head": (0, -30, 0), "neck": (0, -15, 0)})
# 'Nothing!': handen (en het oor) achter de rug
BEHIND = arms(arm("R", (0.2, -0.45, -0.85), (-0.5, -0.5, -0.3)), arm("L", (0.2, -0.45, -0.85), (-0.5, -0.5, -0.3)))
S.beat(held, l5[0], "staan", face="lach", face_amt=0.7, arms=BEHIND, look=(-0.4, 0.1), body={"head": (0, 18, 0)})
S.beat(held, l5[1] + 0.3, "staan", face="nerveus", face_amt=0.9, arms=BEHIND, look=(0.0, 0.0))
S.beat(held, l6[0] + 0.3, "staan", face="nerveus", face_amt=0.9, arms=BEHIND, at=S.head(broer, 0))
S.beat(held, l7[0] + 3.5, "staan", face="nerveus", face_amt=1.0, arms=BEHIND, at=S.head(broer, 0), body={"neck": (6, 0, 0)})
S.hold(held, GLUE - 0.1)

# ---------------------------------------------------------------- papa en broertje
S.beat(papa, 0.0, **SIT_P, pose="staan", face="neutraal", face_amt=0.5, at=tablet.location + V(0, 0, -0.02))
for side, dx in (("L", 0.11), ("R", -0.11)):
    S.reach(papa, 0.0, side, tablet.location + V(dx, 0.03, -0.05), 1.0)
for k, t in enumerate((4.0, 9.0, 14.0)):
    S.beat(papa, t, **SIT_P, pose="staan", face="blij" if k == 1 else "twijfel", face_amt=0.35,
           at=tablet.location + V(0.04 * (k - 1), 0, -0.02))
S.beat(papa, SLAM + 0.15, **SIT_P, pose="staan", face="verbaasd", face_amt=0.5, at=V(FX, FRONT, 1.2))
S.beat(papa, SLAM + 1.6, **SIT_P, pose="staan", face="twijfel", face_amt=0.4, at=tablet.location)
# bij de krak kijkt papa niet eens op: hij scrolt door
S.beat(papa, HIT + 0.2, **SIT_P, pose="staan", face="blij", face_amt=0.4, at=tablet.location + V(0.03, 0, -0.03))
S.hold(papa, END)

# broertje eet cornflakes (lepel naar de kom en naar zijn mond), tot de krak
S.beat(broer, 0.0, **SIT_B, pose="staan", face="blij", face_amt=0.4, at=BOWL)
S.reach(broer, 0.0, "R", BOWL + V(0.03, 0.0, 0.03), 1.0)
mouth = lambda: S.head(broer, 0) + V(-0.06, 0.18, -0.16)
t = 0.6
while t < HIT - 1.4:
    S.reach(broer, t, "R", BOWL + V(0.03, 0.0, 0.02), 1.0)
    S.reach(broer, t + 0.5, "R", BOWL + V(0.03, 0.0, 0.05), 1.0)
    S.reach(broer, t + 0.95, "R", mouth(), 1.0)
    A.key_prop(broer.rig, "mond_open", 0.0, F(t + 0.75))
    A.key_prop(broer.rig, "mond_open", 0.6, F(t + 0.92))
    A.key_prop(broer.rig, "mond_open", 0.0, F(t + 1.1))
    A.key_prop(broer.rig, "mond_open", 0.25, F(t + 1.3))
    A.key_prop(broer.rig, "mond_open", 0.0, F(t + 1.5))
    t += 2.2
S.beat(broer, SLAM + 0.1, **SIT_B, pose="staan", face="verbaasd", at=V(FX, FRONT, 1.2))
S.beat(broer, SLAM + 1.4, **SIT_B, pose="staan", face="lach", face_amt=0.6, at=V(FX, FRONT, 1.2))
S.beat(broer, l3[0] + 1.0, **SIT_B, pose="staan", face="blij", face_amt=0.4, at=BOWL)
# de krak: lepel blijft halverwege hangen, hij kijkt op
S.reach(broer, HIT - 0.2, "R", mouth() + V(0, 0.02, -0.08), 1.0)
S.reach(broer, l7[1], "R", mouth() + V(0, 0.02, -0.08), 1.0)
S.beat(broer, HIT + 0.05, **SIT_B, pose="staan", face="verbaasd", face_amt=0.9, at=S.head(held, HIT))
S.beat(broer, l6[0] - 0.3, **SIT_B, pose="staan", face="twijfel", face_amt=0.9, at=S.head(held, l6[0]), body={"head": (6, 0, -8)})
S.beat(broer, l7[0] + 1.5, **SIT_B, pose="staan", face="zelfverzekerd", face_amt=0.6, at=S.head(held, l6[0]), body={"head": (8, 0, -10)})
S.beat(broer, l7[1] - 1.0, **SIT_B, pose="staan", face="grijns", face_amt=1.0, at=S.head(held, l6[0]), body={"head": (10, 0, -12)})
S.hold(broer, END)

# ---------------------------------------------------------------- gelijmd
show(handle, 0, GLUE)
for o in [o for o in bpy.data.objects if o.name.startswith("Mokscherf")]:
    show(o, 0, GLUE)
show(glued, GLUE)
show(glue, GLUE)
S.place(held, GLUE, AT_MUGS + V(0.42, 0.02, 0), 200)
S.beat(held, GLUE, "staan", face="vastberaden", face_amt=0.5, at=MUG_AT, crouch=(0.03, 16))
S.beat(held, KEEP - 0.5, "staan", face="nerveus", face_amt=0.5, at=MUG_AT, crouch=(0.03, 14))
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.55, 0.2, 1.55), (FX - 0.1, FRONT - 0.2, 1.05), 22), ((0.65, 0.3, 1.5), (FX - 0.1, FRONT - 0.2, 1.05), 24))
S.cam(SLAM - 0.08, ((1.0, 0.1, 1.35), (W / 2 - 0.2, 1.0, 1.15), 22), shake=lambda t: max(0.0, 2.0 - (t - SLAM) * 4))
S.cam(l3[0] + 0.2, ((-1.9, -3.7, 2.1), (0.4, 0.4, 0.95), 22), ((-1.6, -3.3, 2.0), (0.4, 0.5, 0.95), 24))
S.cam(l3[0] + 3.0, (MUG_AT + V(-0.42, -0.2, 0.08), MUG_AT + V(0, 0, 0.05), 40), (MUG_AT + V(-0.36, -0.18, 0.07), MUG_AT + V(0, 0, 0.05), 44), dof=2.0)
S.cam(CRACK - 0.25, (LIFT + V(-0.36, 0.14, 0.02), LIFT + V(0.0, 0, -0.03), 38), dof=2.4)
S.cam(CRACK + 1.0, ((1.48, 1.42, 0.3), FLOOR_HIT + V(0, 0, 0.05), 26), shake=lambda t: max(0.0, 1.5 - (t - HIT) * 3) if t > HIT else 0.0)
S.cam(TURN + 0.5, S.shot(held, l4[0] + 0.5, "cu", az=25, lens=32), S.shot(held, l4[1], "cu", az=22, lens=36))
S.cam(l5[0] - 0.05, S.shot(held, l5[0] + 0.5, "mcu", az=10, lens=30, h=0.05))
S.cam(l6[0] - 0.25, S.shot(broer, l6[0], "cu", az=-8, lens=38, h=0.02), S.shot(broer, l6[1] + 0.5, "cu", az=-4, lens=44, h=0.02))
S.cam(l7[0] + 0.2, S.ots(broer, held, l7[0] + 0.3, lens=28, side=-1, back=0.6, out=0.48, rise=0.05),
      S.ots(broer, held, l7[0] + 3.0, lens=30, side=-1, back=0.55, out=0.46, rise=0.05))
S.cam(l7[0] + 3.4, S.shot(broer, l7[1], "cu", az=-12, lens=42, h=0.02), S.shot(broer, l7[1], "ecu", az=-8, lens=46, h=0.02))
S.cam(GLUE, (MUG_AT + V(-0.2, -0.45, 0.12), MUG_AT + V(0, 0, 0.05), 40), (MUG_AT + V(-0.08, -0.3, 0.07), MUG_AT + V(0, 0, 0.045), 52), dof=1.8)

S.finish(length=END + 0.2)
