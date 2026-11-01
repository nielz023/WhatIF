"""F02 · Titel en spelregels · dag 1 · 1x · slaapkamer, maandagochtend.
Wekker 07:00, drie keer snooze (07:09, 07:18, 07:27). Mama roept van beneden. 'What if...',
titelkaart, de regels, 'Remember this Monday.'

    blender -b -P anim/v2/scenes/f02_titel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f02", "slaapkamer", "ochtend")

# ---------------------------------------------------------------- set
wekker = S.obj("Wekker")
digits = {}
for txt in ("07:00", "07:09", "07:18", "07:27"):
    o = T.text("Wekker_" + txt, txt, (0, -0.0445, 0.034), 0.034, T.glow("wekker_cijfers", (1.0, 0.25, 0.15), 6), extrude=0.001)
    o.parent = wekker
    digits[txt] = o
from lib import huis as HU  # noqa: E402
HU.waterglas("Glas_water", (-0.92, 1.47, 0.55), vol=0.8)
CLOCK_P = wekker.matrix_world.translation + V(0, -0.03, 0.06)
BED_EDGE = V(-0.93, 0.55, 0)
SIT = dict(pose="ontspannen", crouch=(0.13, -4.0), feet=((0.02, 0.30, 0.17), (-0.02, 0.30, 0.17)))
LIE_AT = V(-1.38, 0.1, 0.4)                    # voeten richting voeteneinde, hoofd (+y) op het kussen
DOOR = V(1.5, -1.6, 0)
# hij ligt onder het dekbed: een bol dekbed over zijn lijf tot hij overeind schiet
COVER = T.box("Dekbed_over_hem", (-1.47, 0.36, 0.44), (1.12, 1.6, 0.47), S.obj("Dekbed_blauw").active_material, bevel=0.14, ol=0)
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = True

held = S.actor("hoofdpersonage", LIE_AT, 180)


def lie(t, on=True):
    """Liggen op zijn rug (hoofd naar het hoofdeinde) of weer rechtop."""
    rig = held.rig
    if on:
        rig.location, rig.rotation_euler = LIE_AT, (math.radians(-75), 0, 0)      # iets rechtop: het grote hoofd in het kussen
    else:
        rig.location, rig.rotation_euler = BED_EDGE, (0, 0, math.radians(90))
    for p in ("location", "rotation_euler"):
        rig.keyframe_insert(p, frame=F(t))
    LIE_KEYS.append(F(t))


LIE_KEYS = []


def lie_const():
    """Na alle andere keys: harde overgang liggen -> zitten (geen glijden door de lucht)."""
    for fc in A._fcurves(held.rig):
        if fc.data_path in ("location", "rotation_euler"):
            for kp in fc.keyframe_points:
                if any(abs(kp.co.x - f) < 0.5 for f in LIE_KEYS) or kp.co.x < LIE_KEYS[-1]:
                    kp.interpolation = "CONSTANT"


# ---------------------------------------------------------------- tijdlijn
SNOOZE = [0.0, 2.35, 4.6, 6.6]                 # 07:00, 07:09, 07:18, 07:27 verschijnen


def clk(t):
    k = sum(1 for s in SNOOZE[1:] if t >= s)
    if k < 3:
        return f"MON 07:{(0, 9, 18)[k]:02d}"
    m = 27 + int((t - SNOOZE[3]) / 60)
    return f"MON 07:{m:02d}"


S.hud2(1, "1x", clock=clk, t0=0.3)
l1 = S.say("F02-01", gap=0.55)
l2 = S.say("F02-02", gap=0.35, at=max(S.t + 0.35, SNOOZE[3] + 1.0))
l3 = S.say("F02-03", gap=0.6)
S.wait(0.3)
CARD = S.t + 0.1
S.sfx("sfx_whoosh_titel", CARD - 0.25, 0.8)
S.sfx("sfx_titel", CARD, 0.5)
S.card("WHAT IF YOU GOT\n10x FASTER\nEVERY DAY?", CARD, CARD + 3.0, size=120)
l4 = S.say("F02-04", gap=0.6, at=CARD + 3.2)
l5 = S.say("F02-05", gap=0.45)
END = l5[1] + 0.9

for k, s in enumerate(SNOOZE[:3]):
    S.sfx("sfx_wekker", s + 0.05, 0.45, cut=(0, 1.1))
    show(digits[("07:00", "07:09", "07:18")[k]], s, SNOOZE[k + 1])
    S.sfx("sfx_hout_klop", s + 1.15, 0.35)
show(digits["07:27"], SNOOZE[3])
S.music("ochtend", 0.0, CARD, vol=0.22, fade_in=0.6, fade_out=0.3)
S.music("strijkers_warm", CARD + 1.0, END, vol=0.24, fade_in=1.2)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.06)

# ---------------------------------------------------------------- hij: snooze, snooze, snooze
lie(0.0, True)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.3)
for k, s in enumerate(SNOOZE[:3]):             # linkerhand slaat op de wekker
    S.reach(held, s + 0.45, "L", None, 0.0)
    S.reach(held, s + 0.85, "L", CLOCK_P + V(-0.05, 0.02, 0.12))
    S.reach(held, s + 1.1, "L", CLOCK_P + V(0, 0, 0.02))
    S.reach(held, s + 1.6, "L", CLOCK_P + V(-0.12, 0, 0.15))
    S.reach(held, s + 2.0, "L", None, 0.0)
# mama roept: hij schiet overeind op de bedrand
WAKE = l2[0] + 0.15
show(COVER, 0.0, WAKE)
S.eyes_closed(held, 0.0, WAKE - 0.05)
lie(WAKE, False)
S.beat(held, WAKE, **SIT, face="geschrokken", look=(0.4, 0.2), body={"head": (-6, 30, 0)})
S.beat(held, l2[1] + 0.3, **SIT, face="nerveus", face_amt=0.8, look=(0.3, 0.1), body={"head": (-4, 25, 0)})
# 'what if...' hij kijkt naar zijn handen, dan naar ons
HANDS = BED_EDGE + V(0.42, 0, 0.55)
S.beat(held, l3[0] + 0.3, **{**SIT, "pose": "staan"}, face="twijfel", face_amt=0.6, at=HANDS, arms=LOOK_HANDS)
S.beat(held, l3[0] + 3.2, **{**SIT, "pose": "staan"}, face="verbaasd", face_amt=0.7, at=HANDS, arms=LOOK_HANDS)
S.beat(held, l3[1] - 1.6, **{**SIT, "pose": "vuisten"}, face="verbaasd", face_amt=0.9, look=(0, 0.1), body={"head": (-4, -8, 0)})
# na de titel: opstaan, naar de deur
STAND = V(-0.4, 0.3, 0)
S.hold(held, CARD + 0.3)
S.beat(held, CARD + 1.0, "staan", crouch=(0.2, 20), feet=((0.02, 0.18, 0), (-0.02, 0.18, 0)), face="neutraal")
S.place(held, CARD + 0.3, BED_EDGE, 90)
S.place(held, CARD + 1.6, BED_EDGE + V(0.35, 0, 0), 90)
S.beat(held, CARD + 1.8, "staan", face="neutraal", face_amt=0.4)
S.walk(held, CARD + 2.0, CARD + 3.6, [BED_EDGE + V(0.35, 0, 0), STAND], end_rot=heading(STAND, (0.6, -3.0, 0)))
# 'your legs, your hands, your brain, your heart'
S.beat(held, l4[0] + 4.6, "staan", face="twijfel", face_amt=0.5, at=STAND + V(0, 0, 0.35), body={"head": (20, 0, 0)})
S.beat(held, l4[0] + 5.8, "staan", face="verbaasd", face_amt=0.5, at=STAND + V(0.3, -0.4, 0.65), arms=LOOK_HANDS)
S.beat(held, l4[0] + 7.6, "staan", face="neutraal", look=(0, 0.1), body={"head": (-4, 0, 0)}, arms=HOLD_FRONT_R)
S.beat(held, l4[1] - 0.2, "handen_zij", face="blij", face_amt=0.5, look=(0, 0))
# 'remember this Monday': hij pakt zijn tas niet eens, rent naar de deur
S.beat(held, l5[0] + 1.6, "staan", face="neutraal", look=(0.3, 0))
S.walk(held, l5[0] + 2.6, l5[0] + 4.6, [STAND, V(0.8, -0.9, 0), DOOR], arms=0.9, stride=0.6)
S.hold(held, END)

# ---------------------------------------------------------------- camera
# 1-3: de wekker, telkens een andere tijd, een hand die erop slaat
# (camera aan de kamerkant: zijn hand komt van links uit het dekbed)
S.cam(0.0, (CLOCK_P + V(0.62, -0.62, 0.3), CLOCK_P + V(-0.18, 0, 0.02), 32), (CLOCK_P + V(0.56, -0.56, 0.28), CLOCK_P + V(-0.18, 0, 0.02), 35), dof=1.4)
S.cam(SNOOZE[1], (CLOCK_P + V(0.75, -0.9, 0.35), CLOCK_P + V(-0.35, 0, -0.05), 32), dof=1.6)
S.cam(SNOOZE[2], (CLOCK_P + V(0.3, -0.62, 0.42), CLOCK_P + V(-0.15, 0, 0.0), 36), dof=1.4)
# 4: breed: hij in bed, de kamer
S.cam(SNOOZE[3], ((0.9, -2.6, 1.6), (-1.3, 0.9, 0.7), 24), ((0.8, -2.35, 1.55), (-1.3, 0.9, 0.7), 26))
# 5: mama roept: hij zit rechtop
S.cam(WAKE - 0.05, S.shot(held, WAKE + 0.5, "mcu", az=-30, lens=32, h=0.1))
# 6: 'so what if...' langzaam naar hem toe
S.cam(l3[0] + 2.4, S.shot(held, l3[0] + 3, "med", az=-25, lens=30), S.shot(held, l3[1], "mcu", az=-15, lens=36))
# 7: na de titel: opstaan en de kamer in
S.cam(CARD, ((1.0, -2.9, 1.5), (-0.5, 0.4, 0.85), 22), ((0.9, -2.7, 1.5), (-0.4, 0.3, 0.85), 23))
S.cam(l4[0] + 4.2, S.shot(held, l4[0] + 5, "med", az=-20, lens=32), S.shot(held, l4[0] + 8, "mcu", az=-15, lens=36))
S.cam(l4[0] + 8.2, S.shot(held, l4[1], "full", az=-35, lens=28))
# 8: 'remember this Monday' - de wekker op 07:27 op de voorgrond, hij gaat
S.cam(l5[0] - 0.1, (CLOCK_P + V(0.35, -0.9, 0.25), V(0.2, -0.4, 0.9), 26), (CLOCK_P + V(0.3, -1.0, 0.3), V(0.6, -0.9, 0.95), 26))

lie_const()
S.finish(length=END)
