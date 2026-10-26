"""S27d · Dag 40 · in de ruimte. De radio kraakt: zijn beste vriend heeft zich in de controlekamer gepraat, het hele
gezin is er. Mama heeft het oor van de mok bewaard. Het broertje heeft het nooit verteld. De zon komt op. In zijn zak:
de mok. Actie is reactie: één worp en hij gaat naar huis. Hard gooien is een meteoor, zacht gooien is misschien
thuiskomen. Maar morgen is hij weer twee keer sterker. 'So... do you throw it?' Zwart. DAY 41.

    blender -b -P anim/scenes/s27d_mok.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401
from ruimte import suit_actor, follow_lights  # noqa: E402

S = Scene("s27d", "ruimte", "ruimte")
S.clip = (0.05, 30000)

o = S.obj("Mok_gelijmd")
if o:
    for c in [o] + list(o.children_recursive):
        c.hide_render = True
TOP = V(0.0, 0.0, 400.0)
SUN = V(0.876, 0.0, -0.46).normalized() * 9000
held = suit_actor(S, TOP, 200, energy=0.8)
follow_lights(S, held)

# ---------------------------------------------------------------- de controlekamer (ver weg in dezelfde scène)
MC = V(0.0, 0.0, -6000.0)
room = I.room("Controlekamer", 10.0, 8.0, 3.5, wall_color=(0.20, 0.23, 0.30), floor_color=(0.16, 0.17, 0.20), skirting=False)
for ob in room.values():
    ob.location = ob.location + MC
scherm_m = S.mat("groot_scherm", (0.05, 0.14, 0.32), 1.6)
T.box("Groot_scherm", tuple(MC + V(0, 3.92, 1.0)), (6.4, 0.06, 2.3), scherm_m, bevel=0.02, ol=0.01)
wit = S.mat("scherm_tekst", (1, 1, 1), 2.5)
T.text("Scherm_titel", "MISSION CONTROL  ·  LIVE", tuple(MC + V(0, 3.86, 3.0)), 0.22, wit, rot=(90, 0, 0), extrude=0.0)
T.text("Scherm_hoogte", "ALTITUDE 100 KM", tuple(MC + V(-1.6, 3.86, 1.5)), 0.3, S.mat("scherm_cyaan", (0.35, 0.95, 1.0), 2.5),
       rot=(90, 0, 0), extrude=0.0)
T.cyl("Scherm_aarde", tuple(MC + V(1.6, 3.86, 1.2)), 0.75, 0.02, S.mat("scherm_aarde", (0.15, 0.45, 0.95), 2.0), seg=40, ol=0).rotation_euler = (math.radians(90), 0, 0)
T.sphere("Scherm_stip", tuple(MC + V(1.6, 3.84, 2.12)), 0.06, S.mat("scherm_stip", (1.0, 0.85, 0.2), 6.0), seg=12, ol=0)
mon = S.mat("monitor_gloed", (0.25, 0.75, 0.9), 1.8)
for k, (x, y) in enumerate([(0.0, 1.25), (-2.6, 1.25), (2.6, 1.25), (-1.3, -2.3), (1.3, -2.3), (-3.6, -2.3), (3.6, -2.3)]):
    I.table(f"Console_{k}", tuple(MC + V(x, y, 0)), size=(2.0, 0.8, 0.75), color=(0.30, 0.32, 0.36))
    for dx in (-0.62, 0.62):
        T.box(f"Monitor_{k}_{dx}", tuple(MC + V(x + dx, y + 0.18, 0.75)), (0.5, 0.04, 0.34), mon, bevel=0.01, ol=0.006)
I.chair("Bureaustoel_vriend", tuple(MC + V(0.0, 0.55, 0)), rot=0, color=(0.15, 0.15, 0.18), office=True)
for k, (x, y, e) in enumerate([(-3.0, 0.3, 900), (3.0, 0.3, 900), (0.0, -1.0, 700), (0.0, 2.6, 900), (-3.5, -3.0, 500), (3.5, -3.0, 500)]):
    T.point_light(f"Controlekamer_licht_{k}", tuple(MC + V(x, y, 3.1)), color=(0.95, 0.95, 1.0), energy=e, radius=0.4)

vriend = S.actor("beste_vriend", MC + V(0.0, 0.55, 0), 180, energy=0.9)
SIT_V, zv = sit(vriend, seat_top=0.5, lean=6)
S.place(vriend, 0.0, MC + V(0.0, 0.55, zv), 180)
for sx in (-1, 1):
    cup = T.sphere(f"Koptelefoon_{sx}", (0, 0, 0), 0.09, S.mat("koptelefoon", (0.12, 0.12, 0.14)), scale=(0.45, 1.0, 1.0), seg=16, ol=0.004)
    attach(cup, vriend, "head", (sx * vriend.J["head_r"].x * 1.0, -(vriend.J["head_top"].z - vriend.J["head_c"].z), 0))
mic = T.cyl("Microfoon_arm", (0, 0, 0), 0.012, 0.28, S.mat("koptelefoon", (0.12, 0.12, 0.14)), seg=8, ol=0.003)
attach(mic, vriend, "head", (vriend.J["head_r"].x * 0.95, -(vriend.J["head_top"].z - vriend.J["head_c"].z) * 1.55, 0.05), (70, 0, 0))
FAM = dict(mama=V(-0.75, -0.35, 0), papa=V(0.85, -0.45, 0), opa=V(-1.6, -0.85, 0), oma=V(1.65, -0.85, 0), broertje=V(-1.05, 0.45, 0))
fam = {n: S.actor(n, MC + p, 180 + (8 if p.x < 0 else -8), energy=0.8) for n, p in FAM.items()}
mama, bro = fam["mama"], fam["broertje"]
oor = T.torus("Mok_oor_los", (0, 0, 0), 0.028, 0.008, S.mat("mok_wit", (0.95, 0.94, 0.9)), rot=(90, 0, 0), seg=20, seg2=8, ol=0.003)
oor.scale = (1.6, 1.6, 1.6)
attach(oor, mama, "hand.R", (0, 0.06, 0.03), (0, 0, 0))
for k, x in enumerate((-1.3, 1.3)):
    ex = S.actor("wetenschapper", MC + V(x, -1.75, 0), 180, energy=0.5, label=f"controle_{k}",
                 outfit=dict(shirt=(0.30, 0.40, 0.55), broek=(0.2, 0.2, 0.25), haar=((0.15, 0.1, 0.07), (0.6, 0.45, 0.3))[k]), drop=("bril",))
    sp, zz = sit(ex, seat_top=0.5, lean=8)
    I.chair(f"Bureaustoel_{k}", tuple(MC + V(x, -1.75, 0)), rot=0, color=(0.15, 0.15, 0.18), office=True)
    S.place(ex, 0.0, MC + V(x, -1.75, zz), 180)
    S.beat(ex, 0.0, **sp, face="neutraal", face_amt=0.5, look=(0, -0.1), arms=LOOK_HANDS)

# de mok in zijn zak (verschijnt in zijn hand)
mug = prop_mug(S, "Mok_ruimte", TOP, handle=False, cracked=True)

# ---------------------------------------------------------------- tijdlijn
S.hud(40, "1,099,511,627,776x STRONGER", t0=0.3, tick=False)
S.sfx("sfx_ademhaling_helm", 0.0, vol=0.2, loop_to=0)
BREATHE = S.sounds[-1]
S.music("drone", 0.0, 0, vol=0.1, fade_in=1.5, fade_out=1.5)
DRONE = S.sounds[-1]
l14 = S.say("S27-14", who=None, gap=1.4, gain=1.0)
S.sfx("sfx_radio_ruis", l14[0] - 0.45, vol=0.3, cut=(0.0, 0.6))
l15 = S.say("S27-15", gap=0.5)
l16 = S.say("S27-16", who=vriend, gap=0.5, gain=1.0)
MOM_SAYS = l16[0] + 2.34
HANDLE = l16[0] + 5.54                         # 'she says she kept the handle.'
l17 = S.say("S27-17", gap=0.6)
l18 = S.say("S27-18", who=bro, gap=0.5, gain=1.0)
l19 = S.say("S27-19", gap=1.4)
l20 = S.say("S27-20", gap=0.6)
POCKET = l20[0] + 0.2
THE_MUG = l20[0] + 2.2                         # 'The mug.'
l21 = S.say("S27-21", gap=0.6)
CAN = l21[0] + 2.87                            # 'You CAN go home.'
l22 = S.say("S27-22", gap=0.9)
EQUAL = l22[0] + 5.1                           # 'Every action has an equal and opposite reaction.'
ONE = l22[0] + 8.59                            # 'One throw of that mug...'
l23 = S.say("S27-23", gap=0.7)
HIT = l23[0] + 3.2                             # 'You'll hit.'
METEOR = l23[0] + 4.55
l24 = S.say("S27-24", gap=0.6)
EGGS = l24[0] + 1.55                           # 'the way you learned with the eggs'
FLOAT = l24[0] + 5.88                          # 'and maybe, just maybe, you float home.'
l25 = S.say("S27-25", gap=0.8)
TOMORROW = l25[0] + 3.68
AFTER = l25[0] + 6.26
l26 = S.say("S27-26", gap=1.2)
BLACK = l26[1] + 1.0
END = BLACK + 4.2
BREATHE["loop_to"] = BLACK
DRONE["loop_to"] = l15[0] + 1.0
# zachte strijkers voor het oor en de zon, en dan stilte onder de vraag (alleen het tikken van de HUD)
S.music("strijkers_emo", l16[0] + 1.0, 0, vol=0.18, fade_in=2.5, fade_out=1.5)
EMO = S.sounds[-1]
EMO["loop_to"] = l19[0] + 0.5
S.music("strijkers_warm", l19[0] - 0.4, 0, vol=0.2, fade_in=1.5, fade_out=2.0)
WARM = S.sounds[-1]
WARM["loop_to"] = l22[0] + 0.5
S.music("subbas", l22[0] + 0.2, 0, vol=0.16, fade_in=2.0, fade_out=0.25)
SUB = S.sounds[-1]
SUB["loop_to"] = l26[0] - 0.3
for t in frange(l26[0] - 0.2, BLACK + 0.2, 1.0):
    S.sfx("sfx_hud_tik", t, 0.35)

S.real(l22[0] + 0.1, ONE + 2.6)
S.text("ACTION  =  REACTION", EQUAL - 0.2, l22[1] + 0.3, loc=(0.5, 0.16), size=80, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("MUG GOES UP  →  YOU GO DOWN", ONE, l22[1] + 0.3, loc=(0.5, 0.08), size=52, color=CYAN, anchor=("CENTER", "BOTTOM"))
S.text("THROW HARD  =  METEOR", l23[0] + 0.2, l23[1] + 0.5, loc=(0.5, 0.12), size=64, color=RED, anchor=("CENTER", "BOTTOM"))
S.card("", HIT - 0.05, HIT + 0.5, bg=(0.6, 0.05, 0.02), dim=0.25, fin=2, fout=8)
S.text("THROW GENTLY  =  FLOAT HOME?", l24[0] + 0.3, l24[1] + 0.5, loc=(0.5, 0.12), size=64, color=CYAN, anchor=("CENTER", "BOTTOM"))
S.text("LIKE THE EGGS", EGGS, FLOAT - 0.2, loc=(0.965, 0.22), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("TOMORROW: x2", TOMORROW, l25[1] + 0.6, loc=(0.035, 0.76), size=60, color=WHITE)
S.text("THE DAY AFTER: x4", AFTER, l25[1] + 0.6, loc=(0.035, 0.69), size=60, color=WHITE)
S.card("", BLACK, END + 0.5, bg=(0.0, 0.0, 0.0), dim=1.0, fin=1, fout=1)
S.hud(41, "2,199,023,255,552x STRONGER", t0=BLACK + 1.4)
S.texts[0]["t1"] = BLACK                       # DAY 40 verdwijnt in het zwart
S.texts[1]["t1"] = BLACK

# ---------------------------------------------------------------- hij, zwevend
for k, t in enumerate(frange(0.0, END + 0.1, 2.0)):
    key(held.rig, t, loc=TOP + V(0.015 * t, 0.0, 0.006 * t), rot=(10 + t * 0.25, t * 0.12, 200 + t * 0.4))
TREAD_A = arms(arm("L", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)), arm("R", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)))
POCKET_R = arm("R", (-0.25, 0.05, -0.97), (-0.1, 0.2, -0.97))
CRADLE = arms(arm("L", (0.15, 0.55, -0.8), (-0.4, 0.85, 0.2)), HOLD_FRONT_R)
LIFT = arms(arm("L", (0.6, 0.3, -0.7), (0.7, 0.4, -0.3)), arm("R", (0.1, 0.6, -0.6), (-0.1, 0.9, 0.25)))
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.7, arms=TREAD_A, look=(0, -0.5), body={"head": (16, 0, 0)}, mond_verdrietig=0.6)
S.beat(held, l14[0] + 0.3, "staan", face="verbaasd", face_amt=0.7, arms=TREAD_A, look=(0, 0.1), body={"head": (0, 0, 0)})
S.beat(held, l14[1] + 0.3, "staan", face="blij", face_amt=0.4, arms=TREAD_A, look=(0, 0.0), mond_verdrietig=0.5)
S.beat(held, l17[0] + 0.2, "staan", face="verdrietig", face_amt=0.8, arms=TREAD_A, look=(0, -0.2), mond_verdrietig=0.8, ogen_knijp=0.3)
S.beat(held, l18[0] + 0.6, "staan", face="lach", face_amt=0.4, arms=TREAD_A, look=(0, -0.1), mond_verdrietig=0.6, ogen_knijp=0.5)
S.beat(held, l19[0] + 0.4, "staan", face="verbaasd", face_amt=0.4, arms=TREAD_A, at=SUN, mond_verdrietig=0.3)
S.beat(held, POCKET, "staan", face="neutraal", face_amt=0.5, arms=POCKET_R, look=(-0.2, -0.6), body={"head": (14, 0, 0)})
S.beat(held, THE_MUG - 0.3, "staan", face="verbaasd", face_amt=0.6, arms=CRADLE, look=(0, -0.7), body={"head": (18, 0, 0)})
S.beat(held, l21[0] + 0.4, "staan", face="twijfel", face_amt=0.5, arms=CRADLE, look=(0, -0.6), body={"head": (16, 0, 0)})
S.beat(held, CAN - 0.1, "staan", face="verbaasd", face_amt=0.9, arms=CRADLE, look=(0, 0.1), body={"head": (0, 0, 0)})
S.beat(held, CAN + 0.6, "staan", face="blij", face_amt=0.8, arms=CRADLE, look=(0, 0.0), mond_verdrietig=0.2)
S.beat(held, ONE, "staan", face="vastberaden", face_amt=0.5, arms=LIFT, look=(0.3, 0.3), body={"head": (-10, 15, 0)})
S.beat(held, l23[0] + 0.3, "staan", face="nerveus", face_amt=0.8, arms=CRADLE, look=(0, -0.6), body={"head": (14, 0, 0)})
S.beat(held, HIT, "staan", face="bang", face_amt=0.8, arms=CRADLE, look=(0, -0.8), body={"head": (20, 0, 0)})
S.beat(held, l24[0] + 0.4, "staan", face="neutraal", face_amt=0.5, arms=CRADLE, look=(0, -0.7), body={"head": (18, 0, 0)})
S.beat(held, FLOAT, "staan", face="blij", face_amt=0.4, arms=CRADLE, look=(0, -0.2), body={"head": (6, 0, 0)}, mond_verdrietig=0.4)
S.beat(held, l25[0] + 0.3, "staan", face="twijfel", face_amt=0.6, arms=CRADLE, look=(0, -0.7), body={"head": (16, 0, 0)})
S.beat(held, AFTER, "staan", face="bang", face_amt=0.6, arms=CRADLE, look=(0, -0.8), body={"head": (20, 0, 0)}, mond_verdrietig=0.5)
S.beat(held, l26[0], "staan", face="verdrietig", face_amt=0.7, arms=CRADLE, look=(0, -0.8), body={"head": (20, 0, 0)}, mond_verdrietig=0.6)
S.hold(held, END)
visible(mug, 0.0, False)
visible(mug, POCKET + 0.7, True)
emp = grab(S, mug, held, 0.0, "hand.R", (0.0, 0.07, 0.06), (90, 0, 0))
key(emp, l26[0] - 0.4, rot=(90, 0, 0))
key(emp, BLACK, rot=(90, 0, 70))               # hij draait de mok langzaam in zijn hand

# ---------------------------------------------------------------- de controlekamer acteert
HEADS = S.head(vriend, 0.0) + V(0, 3.0, 0.4)   # ze kijken naar het grote scherm
S.beat(vriend, 0.0, **SIT_V, face="nerveus", face_amt=0.6, at=HEADS, arms=LOOK_HANDS)
S.beat(vriend, l14[0] - 0.2, **SIT_V, face="verdrietig", face_amt=0.4, at=HEADS, arms=arm("R", (-0.2, 0.3, 0.2), (0.6, 0.2, 0.75)))
S.beat(vriend, l16[0] - 0.1, **SIT_V, face="blij", face_amt=0.4, at=HEADS, arms=arm("R", (-0.2, 0.3, 0.2), (0.6, 0.2, 0.75)))
S.beat(vriend, MOM_SAYS - 0.3, **SIT_V, face="neutraal", face_amt=0.6, at=S.head(mama, 0.0), arms=LOOK_HANDS)
S.beat(vriend, HANDLE, **SIT_V, face="blij", face_amt=0.5, at=HEADS, arms=LOOK_HANDS, mond_verdrietig=0.4)
S.hold(vriend, END)
for name, ch in fam.items():
    S.beat(ch, 0.0, "staan", face="nerveus" if name != "broertje" else "verdrietig", face_amt=0.5, at=HEADS + V(0, 0, 0.3), feet="keep")
S.beat(mama, MOM_SAYS, "staan", face="verdrietig", face_amt=0.6, at=HEADS + V(0, 0, 0.3), arms=HOLD_FRONT_R, feet="keep")
S.beat(mama, HANDLE - 0.2, "staan", face="blij", face_amt=0.4, at=HEADS + V(0, 0, 0.3), arms=arm("R", (0.1, 0.7, -0.2), (0.0, 0.6, 0.8)),
       mond_verdrietig=0.7, ogen_knijp=0.4, feet="keep")
S.hold(mama, l17[1])
S.beat(mama, l17[1] + 0.4, "staan", face="verdrietig", face_amt=0.6, at=HEADS + V(0, 0, 0.3), arms=HOLD_FRONT_R, feet="keep")
BRO_MIC = MC + V(-0.42, 0.42, 0)
S.walk(bro, l17[1] - 0.6, l18[0] - 0.1, [MC + FAM["broertje"], BRO_MIC], stride=0.25, arms=0.2, end_rot=150)
S.beat(bro, l18[0] - 0.1, "staan", crouch=(0.05, 18), face="verdrietig", face_amt=0.5, at=S.head(vriend, 0.0), arms=HAND_OUT_L)
S.beat(bro, l18[1] + 0.3, "staan", face="blij", face_amt=0.5, at=HEADS + V(0, 0, 0.3), mond_verdrietig=0.5)
for ch in fam.values():
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
HPOS = lambda t: S._root_matrix(held, t).translation
MCC = lambda x, y, z: MC + V(x, y, z)
S.cam(0.0, ((-5.0, -14.0, 403.0), (0.0, 0.0, 400.6), 40), ((-4.7, -13.0, 402.8), (0.0, 0.0, 400.6), 40))
S.cam(l14[0] - 0.2, S.shot(held, l14[0] + 0.5, "mcu", az=10, lens=34), S.shot(held, l14[1], "mcu", az=8, lens=37))
S.cam(l15[0] + 1.0, (MCC(2.4, 3.3, 1.9), MCC(-0.4, -0.2, 1.1), 22), (MCC(2.1, 3.3, 1.85), MCC(-0.4, -0.2, 1.1), 24))
S.cam(l16[0] - 0.1, S.shot(vriend, l16[0] + 0.5, "mcu", az=12, lens=32), S.shot(vriend, MOM_SAYS, "mcu", az=10, lens=35))
S.cam(MOM_SAYS - 0.1, S.shot(mama, MOM_SAYS + 0.5, "med", az=-10, lens=32), S.shot(mama, HANDLE, "med", az=-8, lens=34))
MH = S.bone_world(mama, "hand.R", HANDLE + 0.4)
S.cam(HANDLE + 0.1, (MH + V(0.15, 0.75, 0.12), MH + V(0, 0, 0.05), 45), (MH + V(0.13, 0.68, 0.11), MH + V(0, 0, 0.05), 48))
S.cam(l17[0] + 1.3, S.shot(held, l17[0] + 1.6, "mcu", az=-12, lens=34), S.shot(held, l17[1], "mcu", az=-10, lens=37))
S.cam(l18[0] - 0.2, S.shot(bro, l18[0] + 0.3, "med", az=-20, lens=30), S.shot(bro, l18[1], "med", az=-18, lens=32))
S.cam(l19[0] - 0.2, (V(3.0, -4.0, 399.5), V(2000, 300, -900), 28), (V(3.2, -4.2, 399.4), V(2000, 300, -880), 30))
S.cam(POCKET - 0.1, S.shot(held, POCKET + 0.4, "med", az=20, lens=30), S.shot(held, POCKET + 1.4, "med", az=18, lens=32))
H1 = S.bone_world(held, "hand.R", THE_MUG + 0.3)
S.cam(THE_MUG - 0.1, (H1 + V(0.25, -0.45, 0.2), H1 + V(0, 0, 0.03), 40), (H1 + V(0.22, -0.4, 0.18), H1 + V(0, 0, 0.03), 42))
S.cam(l21[0] + 0.6, S.shot(held, l21[0] + 1.0, "mcu", az=15, lens=34), S.shot(held, CAN + 0.6, "mcu", az=12, lens=37))
S.cam(l22[0] - 0.1, (V(-2.5, -7.5, 401.8), V(1.0, 25.0, 385.0), 24), (V(-2.2, -7.0, 401.6), V(1.0, 25.0, 385.0), 26))
S.cam(ONE - 0.1, S.shot(held, ONE + 0.5, "full", az=-25, lens=30), S.shot(held, l22[1], "full", az=-22, lens=32))
S.cam(l23[0] - 0.1, (V(0.0, -3.0, 410.0), V(0.0, 40.0, 0.0), 30), (V(0.0, -3.0, 412.0), V(0.0, 40.0, 0.0), 30))
H2 = S.bone_world(held, "hand.R", l24[0] + 1.0)
S.cam(l24[0] + 0.2, (H2 + V(-0.35, -0.55, 0.25), H2 + V(0, 0, 0.1), 34), (H2 + V(-0.32, -0.5, 0.23), H2 + V(0, 0, 0.1), 36))
S.cam(FLOAT - 0.2, S.shot(held, FLOAT + 0.3, "mcu", az=20, lens=34), S.shot(held, l24[1], "mcu", az=18, lens=37))
S.cam(l25[0] - 0.1, (V(-7.0, -12.0, 404.0), V(0.0, 0.0, 400.6), 32), (V(-7.5, -13.5, 404.3), V(0.0, 0.0, 400.6), 32))
S.cam(TOMORROW - 0.1, S.shot(held, TOMORROW + 0.4, "mcu", az=-15, lens=34), S.shot(held, l25[1], "mcu", az=-12, lens=38))
H3 = S.bone_world(held, "hand.R", l26[0])
S.cam(l26[0] - 0.25, (H3 + V(0.12, -0.32, 0.1), H3 + V(0, 0, 0.04), 50), (H3 + V(0.1, -0.27, 0.085), H3 + V(0, 0, 0.04), 50))

S.finish(length=END)
