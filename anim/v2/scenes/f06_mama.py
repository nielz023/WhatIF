"""F06 · Dag 2 · 10x · keuken, 07:30. Mama komt de taart bakken en vindt hem tussen duizend kraanvogels.
Ze laat een ei vallen; hij loopt om de tafel en vangt het. 'Mom, it's me' klinkt als een vogeltje. Het whiteboard:
MOM. IT'S ME. I'M FAST. I'M OK. Zij schrijft trillend terug: Are you hurt? Papa komt binnen, belt een natuurkundige
en begint aan een mop over een slak.

    blender -b -P anim/v2/scenes/f06_mama.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f06", "keuken", "kraanvogels")

TX, TY, TZ = 0.2, -0.6, 0.76
FX = 4.8 / 2 - 0.42
WB_Y = 4.2 / 2 - 0.73 - 0.008
WB = V(FX + 0.06, WB_Y - 0.03, 0.82)             # midden van het bord (de kant naar de kamer)
MOM_COUNTER = V(0.95, 1.12, 0)                   # bij de bakspullen
TABLE = V(TX, TY, 0)
HERO0 = V(-0.25, -1.35, 0)                       # aan de voorkant van de tafel, tussen de kraanvogels
BOARD_HERO = V(1.62, 0.86, 0)                    # links voor het bord
BOARD_MOM = V(1.5, 0.94, 0)
BACK_HERO = V(0.95, 0.1, 0)                     # hij doet een stap terug als zij komt schrijven
DAD_AT = V(-1.45, 0.55, 0)

# ---------------------------------------------------------------- whiteboard: begint met de voorkant, hij draait hem om
wb = S.obj("Whiteboard")
lines = {k: [o for o in bpy.data.objects if o.name.startswith(f"Whiteboard_achter_regel{k}")] for k in (1, 2, 3, 4)}

# ---------------------------------------------------------------- figuren
ROBE = (0.86, 0.62, 0.76)                        # mama in haar badjas
mama = S.actor("mama", MOM_COUNTER, 180, outfit=dict(shirt=ROBE, broek=ROBE))
held = S.actor("hoofdpersonage", HERO0, heading(HERO0, MOM_COUNTER))
papa = S.actor("papa", DAD_AT + V(-0.35, 0, 0), 90)   # verschijnt pas als hij binnenkomt
egg = prop_egg(S, "Ei_mama", (0, 0, 0))

# ---------------------------------------------------------------- tijdlijn
BLACK = 1.0                                      # patroononderbreking: een seconde zwart en stilte
S.card("", 0.0, BLACK, dim=1.0, fin=1, fout=4)
S.hud2(2, "10x", clock=clock(7 * 3600 + 29 * 60 + 59.6, 0.1, dec=1, day="TUE", t0=0.0), t0=BLACK)
l1 = S.say("F06-01", at=BLACK + 0.5)
l2 = S.say("F06-02", gap=0.4)
DROP = l2[0] + 0.3
CATCH = DROP + 3.6
l3 = S.say("F06-03", gap=0.5)
CHIRP = l3[0] + 1.3
l4 = S.say("F06-04", gap=0.4)
l5 = S.say("F06-05", gap=0.5)
FLIP = l5[0] + 0.3
WRITE = [l5[0] + 1.3, l5[0] + 2.3, l5[0] + 3.2]  # zijn regels: voor haar verschijnen ze gewoon
M0 = l5[0] + 6.4                                 # mama schrijft terug, letter voor letter
l6 = S.say("F06-06", gap=0.5)
M1 = l6[0] + 3.6                                 # 'Are you hurt?' staat er
l7 = S.say_slow("F06-07", "Papa", who=papa, gap=0.5, sub="DAD", subtitle="Okay. Okay. Why did the snail...", gain=1.0)
l8 = S.say("F06-08", gap=0.2)
END = l8[1] + 1.2
S.music("piano_warm", BLACK + 0.2, l4[1], vol=0.16, fade_in=1.0, fade_out=1.0, start=30.0)
S.music("strijkers_emo", l5[0] - 0.5, l6[1] + 1.5, vol=0.18, fade_in=1.5, fade_out=1.5)
S.music("strijkers_warm", l7[0] - 0.4, END + 1, vol=0.15, fade_in=1.5, fade_out=1.0)
S.ambience("sfx_binnen_sfeer", BLACK, END, vol=0.06)
S.sfx("sfx_tjilp", CHIRP, 0.45)
S.sfx("sfx_tjilp", CHIRP + 0.75, 0.4)
S.sfx("sfx_stift", WRITE[0] - 0.1, 0.3, cut=(0, 1.2))
S.sfx("sfx_stift", M0, 0.2, cut=(0, 4.0))
S.gauge2("JOKE: 10 MIN", l8[0] + 5.0, END, color=GOLD)

# ---------------------------------------------------------------- whiteboard
key(wb, 0.0, rot=(0, 0, 0))
key(wb, FLIP, rot=(0, 0, 0))
key(wb, FLIP + 0.6, rot=(0, 0, 180))
for k, t in zip((1, 2, 3), WRITE):
    for o in lines[k]:
        show(o, t)
# 'Are you hurt?': een witte strook voor de tekst die van links naar rechts wegschuift (zij schrijft)
bpy.context.view_layer.update()
key(wb, 0.0, rot=(0, 0, 0))
pts = []
for o in lines[4]:
    for c in o.bound_box:
        pts.append(o.matrix_world @ Vector(c))
wb.rotation_euler.z = math.radians(180)
bpy.context.view_layer.update()
pts = []
for o in lines[4]:
    for c in o.bound_box:
        pts.append(o.matrix_world @ Vector(c))
x0, x1 = min(p.x for p in pts) - 0.01, max(p.x for p in pts) + 0.01
z0, z1 = min(p.z for p in pts) - 0.01, max(p.z for p in pts) + 0.01
yf = min(p.y for p in pts) - 0.0015
me = bpy.data.meshes.new("Whiteboard_dekstrook")
me.from_pydata([(-(x1 - x0), 0, 0), (0, 0, 0), (0, 0, z1 - z0), (-(x1 - x0), 0, z1 - z0)], [], [(0, 1, 2, 3)])
cover = bpy.data.objects.new("Whiteboard_dekstrook", me)
T._link(cover)
cover.data.materials.append(S.mat("whiteboard_wit2", (0.97, 0.97, 0.98)))
cover.location = (x1, yf, z0)
key(cover, 0.0, scale=(1, 1, 1))
key(cover, M0, scale=(1, 1, 1))
for k in range(1, 13):                           # schokkerig: per letter een stapje, met trillende pauzes
    u = k / 12
    key(cover, M0 + (M1 - M0) * u, scale=(max(0.0001, 1 - u), 1, 1))
for fc in A._fcurves(cover):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
wb.rotation_euler.z = 0.0
show(cover, 0.0, M1 + 0.1)

# ---------------------------------------------------------------- mama: (tien keer te langzaam) ei in de hand, draait zich om, ziet hem
FACE_T = heading(MOM_COUNTER, TABLE)
TURN0, TURN1 = l1[0] + 2.4, DROP - 0.5
S.beat(mama, 0.0, "staan", face="neutraal", face_amt=0.4, at=MOM_COUNTER + V(-0.2, 0.6, 0.9))
grab(S, egg, mama, 0.0, "hand.L", mode="loc", offset=(0, 0, -0.03), release=DROP)
S.reach(mama, 0.0, "L", MOM_COUNTER + V(-0.18, 0.3, 1.04))
S.reach(mama, 0.0, "R", None, 0.0)
S.reach(mama, TURN0, "L", MOM_COUNTER + V(-0.18, 0.3, 1.04))
S.beat(mama, TURN0 - 0.6, "staan", face="neutraal", face_amt=0.5, at=S.head(held, TURN0))
S.turn(mama, TURN0, TURN1, FACE_T)
fwd = (TABLE - MOM_COUNTER).normalized()
left = V(-fwd.y, fwd.x, 0)                       # haar linkerkant
S.reach(mama, TURN1, "L", MOM_COUNTER + fwd * 0.3 + left * 0.18 + V(0, 0, 1.04))
S.beat(mama, l1[1] - 0.6, "staan", face="verbaasd", face_amt=0.8, at=S.head(held, l1[1]))
S.beat(mama, DROP - 0.2, "staan", face="geschrokken", face_amt=0.9, at=S.head(held, DROP))
EG0 = S.bone_world(mama, "hand.L", DROP, tail=True) + V(0, 0, -0.03)
FALL_T = CATCH - DROP
for k in range(9):                               # het ei valt in slow motion (g gedeeld door honderd)
    t = k * FALL_T / 8
    key(egg, DROP + t, loc=EG0 + fwd * (0.06 * t / FALL_T) + V(0, 0, -0.049 * t * t))
EGG_CATCH = EG0 + fwd * 0.06 + V(0, 0, -0.049 * FALL_T * FALL_T)
S.reach(mama, DROP + 0.9, "L", None, 0.0)
S.beat(mama, CATCH, "staan", face="bang", face_amt=0.5, at=S.head(held, CATCH))
S.beat(mama, l4[0] + 1.0, "staan", face="bang", face_amt=0.9, at=S.head(held, l4[0] + 1.0), crouch=(0.02, -6))
S.reach(mama, l4[0] + 1.0, "L", MOM_COUNTER + fwd * 0.12 + left * 0.15 + V(0, 0, 1.15))   # hand naar haar borst
S.beat(mama, l4[1], "staan", face="bang", face_amt=0.6, at=S.head(held, l4[1]), crouch=(0.01, -3))
S.reach(mama, l4[1], "L", None, 0.0)
S.beat(mama, WRITE[0], "staan", face="verbaasd", face_amt=0.9, at=WB)
# naar het bord en terugschrijven (langzaam, haar hand trilt)
S.walk(mama, WRITE[-1] + 0.5, M0 - 0.3, [MOM_COUNTER, BOARD_MOM], end_rot=heading(BOARD_MOM, WB), stride=0.3)
S.reach(mama, M0 - 0.6, "R", None, 0.0)
for k in range(int((M1 - M0) / 0.12)):           # haar hand trilt
    t = M0 + k * 0.12
    u = min(1.0, (t - M0) / (M1 - M0))
    j = 0.006 * (1 if k % 2 else -1)
    S.reach(mama, t, "R", V(x0 + 0.04 + (x1 - x0) * u, yf - 0.03, (z0 + z1) / 2 + j))
S.reach(mama, M1 + 0.3, "R", None, 0.0)
STRIP = V((x0 + x1) / 2, yf, (z0 + z1) / 2)
S.beat(mama, M0, "staan", face="verdrietig", face_amt=0.5, at=STRIP)
S.beat(mama, M1 + 0.2, "staan", face="verdrietig", face_amt=0.8, at=S.head(held, M1))
S.turn(mama, l7[0] + 1.0, l7[0] + 3.0, heading(BOARD_MOM, DAD_AT))
S.beat(mama, l7[0] + 1.0, "staan", face="nerveus", face_amt=0.6, at=S.head(papa, l7[0] + 1.0))
S.hold(mama, END)

# ---------------------------------------------------------------- hij: om de tafel, het ei vangen (linkerhand)
CATCH_AT = V(EGG_CATCH.x + 0.3, EGG_CATCH.y - 0.14, 0)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.6, at=S.head(mama, 0.0))
S.beat(held, l1[1] - 0.8, "staan", face="geschrokken", face_amt=0.7, at=S.head(mama, l1[1]))
S.walk(held, DROP + 0.3, CATCH - 0.35, [HERO0, V(1.3, -1.4, 0), V(1.85, -0.4, 0), CATCH_AT],
       stride=0.55, end_rot=heading(CATCH_AT, EGG_CATCH) - 30)   # het ei links voor hem, gezicht naar mama
S.beat(held, CATCH - 0.45, "staan", face="vastberaden", face_amt=0.8, at=EGG_CATCH, crouch=(0.3, 30))
S.reach(held, CATCH - 0.9, "L", None, 0.0)
S.reach(held, CATCH - 0.3, "L", EGG_CATCH + V(0.0, 0.0, 0.07))
grab(S, egg, held, CATCH, "hand.L", mode="loc", offset=(0, 0, 0.03))
S.beat(held, CATCH + 0.7, "staan", face="blij", face_amt=0.5, at=S.head(mama, CATCH))
S.reach(held, CATCH + 0.7, "L", CATCH_AT + V(-0.28, -0.12, 0.85))
S.beat(held, CHIRP - 0.2, "staan", face="blij", face_amt=0.7, at=S.head(mama, CHIRP))
for k in range(6):                               # 'Mom, it's me': snel gepraat
    A.key_prop(held.rig, "mond_open", 0.5 if k % 2 == 0 else 0.1, F(CHIRP + k * 0.12))
S.beat(held, l4[0] + 0.6, "staan", face="verdrietig", face_amt=0.8, at=S.head(mama, l4[0] + 0.6))
S.reach(held, l4[0] + 0.6, "L", CATCH_AT + V(-0.2, -0.12, 0.72))
S.beat(held, l4[1] - 1.5, "staan", face="verdrietig", face_amt=1.0, at=S.head(mama, l4[1]), body={"head": (-8, 0, 0)})
# naar het bord: omdraaien, schrijven
S.walk(held, l5[0] - 0.7, FLIP - 0.1, [CATCH_AT, BOARD_HERO], end_rot=heading(BOARD_HERO, WB), stride=0.4)
S.beat(held, FLIP - 0.2, "staan", face="vastberaden", face_amt=0.7, at=WB)
S.reach(held, FLIP - 0.6, "R", None, 0.0)
S.reach(held, FLIP - 0.1, "R", WB + V(0.2, -0.04, 0.05))
S.reach(held, FLIP + 0.5, "R", WB + V(-0.2, -0.04, 0.05))
for k, t in enumerate(WRITE):
    zr = (0.38, 0.24, 0.10)[k] * 0.58 - 0.015
    for j in range(5):                           # de stift beweegt over de regel
        S.reach(held, t - 0.75 + 0.18 * j, "R", WB + V(-0.13 + 0.065 * j, -0.05, zr + 0.01 * (j % 2)))
S.reach(held, WRITE[-1] + 0.4, "R", None, 0.0)
S.beat(held, WRITE[-1] + 0.1, "staan", face="nerveus", face_amt=0.7, at=S.head(mama, WRITE[-1]))
S.walk(held, WRITE[-1] + 0.4, WRITE[-1] + 1.5, [BOARD_HERO, BACK_HERO], end_rot=heading(BACK_HERO, WB), stride=0.4)
S.beat(held, M0, "staan", face="nerveus", face_amt=0.7, at=STRIP)
S.beat(held, M1, "staan", face="verdrietig", face_amt=0.9, at=STRIP)
S.beat(held, l6[1] - 1.6, "staan", face="blij", face_amt=0.5, at=S.head(mama, l6[1]))
S.turn(held, l7[0] + 0.4, l7[0] + 1.0, heading(BACK_HERO, DAD_AT))
S.beat(held, l7[0] + 0.6, "staan", face="verbaasd", face_amt=0.6, at=S.head(papa, l7[0] + 0.6))
S.beat(held, l8[0] + 5.5, "staan", face="twijfel", face_amt=0.8, at=S.head(papa, l8[0] + 5.5))
S.beat(held, END - 1.2, "staan", face="twijfel", face_amt=1.0, at=S.head(papa, END), body={"head": (0, 0, -8)})
S.hold(held, END)

# ---------------------------------------------------------------- papa: komt binnen (tien keer te langzaam), belt, de mop
PAPA_IN = l7[0] - 1.6
S.beat(papa, 0.0, "staan", face="neutraal")
for c in papa.rig.children_recursive:
    if c.type == "MESH":
        show(c, PAPA_IN)
S.walk(papa, PAPA_IN, l7[0] + 1.2, [DAD_AT + V(-0.35, 0, 0), DAD_AT], stride=0.25, end_rot=heading(DAD_AT, BACK_HERO))
S.beat(papa, PAPA_IN, "staan", face="geschrokken", face_amt=0.7, at=S.head(held, l7[0]))
S.beat(papa, l7[0] + 1.5, "staan", face="nerveus", face_amt=0.6, at=S.head(held, l7[0]), arms=arms(HAND_OUT_L, HAND_OUT_R))
phone = prop_phone(S, "Telefoon_papa", (0, 0, 0))
grab(S, phone, papa, l8[0] + 0.5, "hand.R", loc=(0.0, 0.07, 0.02), rot=(90, 0, 180), release=l8[0] + 4.4)
show(phone, l8[0] + 0.5, l8[0] + 4.4)
S.beat(papa, l8[0] + 0.8, "staan", face="nerveus", face_amt=0.6, look=(0.2, 0.1), arms=PHONE_EAR_R)
S.beat(papa, l8[0] + 4.4, "staan", face="grijns", face_amt=0.7, at=S.head(held, l8[0] + 4.6))
t = l8[0] + 5.0
while t < END:                                    # de mop: zijn mond gaat heel langzaam open en dicht
    A.key_prop(papa.rig, "mond_open", 0.5, F(t))
    A.key_prop(papa.rig, "mond_open", 0.15, F(t + 1.1))
    t += 2.2
S.hold(papa, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-1.9, -1.9, 1.7), (0.9, 0.6, 1.0), 22), ((-1.8, -1.8, 1.65), (0.9, 0.7, 1.05), 24))
HM = S.headpos(mama, l1[1])
S.cam(l1[0] + 3.0, ((0.45, 0.1, 1.45), HM + V(0, 0, -0.1), 28), ((0.5, 0.18, 1.45), HM + V(0, 0, -0.1), 30), dof=1.4)
S.cam(DROP - 0.2, ((-0.2, -0.2, 1.15), (1.1, 0.8, 0.95), 26), ((-0.1, -0.12, 1.05), (1.15, 0.75, 0.75), 28))
MID = (S.headpos(mama, CATCH + 1.0) + S.headpos(held, CATCH + 1.0)) / 2
S.cam(CATCH + 0.5, ((0.0, 0.45, 1.45), MID + V(0, 0, -0.2), 24), ((0.06, 0.45, 1.45), MID + V(0, 0, -0.15), 26))
S.cam(l4[0] - 0.1, S.shot(mama, l4[0] + 1, "cu", az=-35, lens=42, h=0.05), S.shot(mama, l4[0] + 4, "cu", az=-32, lens=48, h=0.05), dof=1.5)
HC2 = S.headpos(held, l4[0] + 5)
S.cam(l4[0] + 4.2, (HC2 + V(-1.03, 0.37, -0.05), HC2, 32), (HC2 + V(-0.95, 0.34, -0.05), HC2, 35), dof=1.5)
S.cam(l5[0] - 0.3, ((2.05, -0.6, 1.15), WB + V(-0.12, -0.25, 0.12), 32), ((2.05, -0.5, 1.12), WB + V(-0.12, -0.25, 0.12), 34))
S.cam(WRITE[0] - 0.4, ((2.15, 0.9, 1.55), WB + V(-0.04, 0, 0.1), 38), ((2.15, 0.93, 1.53), WB + V(-0.04, 0, 0.1), 41), dof=1.0)
S.cam(WRITE[-1] + 0.5, ((2.3, -0.65, 1.5), (1.3, 0.8, 1.0), 26), ((2.28, -0.55, 1.48), (1.3, 0.8, 1.0), 28))
S.cam(M0 - 0.2, ((2.08, -0.1, 0.95), STRIP + V(-0.06, 0, 0.12), 46), ((2.08, -0.02, 0.93), STRIP + V(-0.05, 0, 0.1), 50), dof=1.4)
HH = S.headpos(held, M0 + 4)
S.cam(M0 + 3.6, (HH + V(0.95, 0.5, -0.35), HH + V(0, 0, -0.1), 34), (HH + V(0.88, 0.46, -0.33), HH + V(0, 0, -0.1), 38), dof=1.4)
S.cam(l6[0] + 1.2, ((1.98, 0.2, 1.1), STRIP + V(0.0, 0, 0.06), 36), ((1.98, 0.28, 1.08), STRIP + V(0.0, 0, 0.06), 40), dof=1.1)
S.cam(M1 + 0.4, S.ots(held, mama, M1 + 1.2, lens=36, side=1, back=1.5, out=0.85, rise=0.12))
S.cam(PAPA_IN, ((0.6, -1.95, 1.6), (-0.4, 0.6, 1.05), 22), ((0.55, -1.9, 1.58), (-0.6, 0.6, 1.05), 24))
S.cam(l8[0] + 4.2, S.shot(papa, l8[0] + 5, "mcu", az=-25, lens=36), S.shot(papa, END, "mcu", az=-20, lens=40))
S.cam(l8[1] - 2.2, S.shot(held, END, "mcu", az=-25, lens=36))

S.finish(length=END)
