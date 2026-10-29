"""F08a · Dag 2 → dag 3 · keuken. AWAKE 20:40, zijn ogen branden; hij doet ze even dicht. Zwart. Ogen open:
08:44, DAY 3 · 100x. Hij springt op naar mama: één snelle stap is sneller dan het geluid. BOEM. Alle glazen en
ramen knallen naar buiten, de duizend kraanvogels vliegen op en blijven in de lucht hangen. Zijn schoenen roken,
zijn ouders houden hun handen voor hun oren. Hij gaat weg, heel langzaam.

    blender -b -P anim/v2/scenes/f08a_knal.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f08a", "keuken", "knal")
rnd = random.Random(8)

TX, TY, TZ = 0.2, -0.6, 0.76
YB = 4.2 / 2 - 0.31
SEAT = S.obj("Stoel_2").location.copy()          # (0.58, -1.22): hij zit met zijn gezicht naar de tafel (+y)
STEP_TO = V(1.35, -0.35, 0)                      # waar de set ruimte heeft gelaten tussen de kraanvogels
MOM_AT = V(1.05, 0.85, 0)
DAD_AT = V(-1.15, 0.55, 0)
DOOR = V(-2.25, 0.95, 0)

# ---------------------------------------------------------------- figuren
ROBE = (0.86, 0.62, 0.76)
held = S.actor("hoofdpersonage", SEAT, 180)
SIT_H, zh = sit(held)
S.place(held, 0, SEAT + V(0, 0, zh), 180)
mama = S.actor("mama", MOM_AT, heading(MOM_AT, SEAT), outfit=dict(shirt=ROBE, broek=ROBE))
papa = S.actor("papa", DAD_AT, heading(DAD_AT, SEAT))

# ---------------------------------------------------------------- tijdlijn
l1 = S.say("F08-01", gap=0.6)
CLOSE = l1[1] - 0.9                              # 'just for a second'
BLACK0, BLACK1 = CLOSE + 0.5, CLOSE + 2.1        # zwart en stil
OPEN = BLACK1 + 0.1
l2 = S.say("F08-02", at=OPEN + 0.5)
UP = l2[0] + 0.5                                 # 'No.' hij springt op
BOOM = l2[1] - 0.3                               # 'and you run to your mom' -> de eerste stap
l3 = S.say("F08-03", at=BOOM + 2.4)
l4 = S.say("F08-04", gap=0.5)
LEAVE = l4[1] - 1.6
END = l4[1] + 1.5

S.hud2(2, "10x", clock=clock(8 * 3600 + 26 * 60 + 10, 0.1, dec=1, day="TUE"), t0=0.3, t1=BLACK0,
       awake=awake(20 + 40 / 60, rate=1 / 3600, t0=0.0, secs=True), awake_t0=0.5)
S.hud2(3, "100x", clock=clock(8 * 3600 + 44 * 60 + 2, 0.01, dec=2, day="TUE", t0=OPEN), t0=OPEN,
       awake=awake(20 + 41 / 60, rate=1 / 3600, t0=OPEN, secs=True), awake_t0=OPEN + 0.1)
S.card("", BLACK0, BLACK1, dim=1.0, fin=6, fout=1)
S.music("drone", 0.0, BLACK0, vol=0.16, fade_in=1.5, fade_out=0.6)
S.music("pizz_spanning", OPEN + 0.2, BOOM, vol=0.14, fade_in=0.4, fade_out=0.05)
S.sfx("sfx_sonic_boom", BOOM, 0.55)
S.sfx("sfx_glas_klink", BOOM + 0.6, 0.2)
S.music("strijk_noot", BOOM + 1.2, END + 1, vol=0.13, fade_in=2.0, fade_out=1.5)
S.ambience("sfx_binnen_sfeer", 0.0, BLACK0, vol=0.05)
S.gauge2("STEP: 15 km/h × 100", l3[0] + 1.4, l3[1], color=GOLD, row=0)
S.gauge2("= 1,500 km/h", l3[0] + 4.2, l3[1], color=GOLD, row=1)
S.gauge2("SOUND: 1,235 km/h", l3[0] + 5.4, l3[1], color=(1.0, 0.45, 0.35, 1), row=2)

WAVE = 3.43                                      # m/s: de geluidsgolf in zijn tijd (343 m/s gedeeld door honderd)
ORIGIN = STEP_TO + V(-0.2, -0.2, 0.3)


def arrive(p):
    """Wanneer de schokgolf punt p bereikt."""
    return BOOM + (Vector(p) - ORIGIN).length / WAVE


# ---------------------------------------------------------------- vóór de knal: heel raam, glazen, kraanvogels op tafel
pane = T.box("Keukenraam_glas_heel", (-0.2, 2.08, 1.55), (1.38, 0.01, 0.98), T.glass("raamglas", (0.8, 0.9, 1.0), alpha=0.25), bevel=0, ol=0)
show(pane, 0.0, arrive(pane.location))
glasses = [T.cyl(f"Drinkglas_{k}", (-1.48 + 0.12 * k, YB - 0.12, 0.9), 0.035, 0.12, T.glass("drinkglas", (0.8, 0.9, 1.0), alpha=0.5),
                 seg=14, ol=0.002) for k in range(4)]
for g in glasses:
    show(g, 0.0, arrive(g.location))
for o in bpy.data.objects:
    if o.name.startswith("Glasscherven"):
        t0 = arrive(V(-0.2, 2.1, 1.55) if "raam" in o.name else V(-1.3, YB, 1.0))
        show(o, t0)
        key(o, t0, loc=(0, -0.12, -0.02) if "raam" in o.name else (0, 0, -0.06))
        key(o, END + 1, loc=(0, 0.03, 0) if "raam" in o.name else (0, 0, 0.02))      # ze drijven heel langzaam verder
        for fc in A._fcurves(o):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"

# de duizend kraanvogels: liggen eerst op tafel, op het aanrecht en de vloer; de golf blaast ze omhoog
cranes = sorted([o for o in bpy.data.objects if o.name.startswith("Kraanvogel_zwevend")], key=lambda o: o.name)
BODY = []                                        # niet door de figuren heen laten hangen


def body_pts(at, h=1.0):
    return [(at + V(0, 0, 1.5 * h), 0.42), (at + V(0, 0, 0.95 * h), 0.36), (at + V(0, 0, 0.5 * h), 0.3)]


BODY += body_pts(MOM_AT) + body_pts(DAD_AT, 1.05) + body_pts(STEP_TO) + body_pts(STEP_TO + V(-0.45, 0.05, 0))
BODY += [(V(-0.2, 2.0, 1.9), 0.55), (V(2.2, -1.2, 1.6), 0.6), (V(0.9, -2.0, 1.2), 0.7)]   # vlak voor de lenzen
for k, o in enumerate(cranes):
    air = o.location.copy()
    if any((air - c).length < r for c, r in BODY):
        o.hide_render = True
        continue
    u = k / len(cranes)
    if u < 0.65:                                 # tafel
        rest = V(TX + rnd.uniform(-0.68, 0.68), TY + rnd.uniform(-0.4, 0.4), TZ + rnd.uniform(0.0, 0.3) * rnd.random())
    elif u < 0.8:                                # aanrecht
        rest = V(rnd.uniform(-1.5, -0.3), YB - 0.05 + rnd.uniform(-0.2, 0.2), 0.92 + rnd.uniform(0, 0.1))
    else:                                        # vloer
        rest = V(TX - 0.2 + rnd.uniform(-1.3, 1.3), TY - 0.1 + rnd.uniform(-0.95, 0.95), 0.0)
    rot_air = o.rotation_euler.copy()
    t0 = arrive(rest)
    key(o, 0.0, loc=rest, rot=(0, 0, math.degrees(rot_air.z)))
    key(o, t0, loc=rest, rot=(0, 0, math.degrees(rot_air.z)))
    key(o, t0 + rnd.uniform(0.35, 0.6), loc=air - (air - rest) * 0.04,
        rot=tuple(math.degrees(a) for a in rot_air))
    key(o, END + 1, loc=air, rot=tuple(math.degrees(a) for a in rot_air))         # en dan hangen ze (bijna) stil

# de schokgolf: een vage bol die met de geluidssnelheid (in zijn tijd) door de keuken trekt
wm = bpy.data.materials.new("schokgolf")
wm.use_nodes = True
b = wm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.95, 0.97, 1.0, 1)
b.inputs["Alpha"].default_value = 0.07
wm.surface_render_method = "BLENDED"
wm.diffuse_color = (0.95, 0.97, 1.0, 0.07)
shock = T.sphere("Schokgolf", ORIGIN, 1.0, wm, seg=32, ol=0)
show(shock, BOOM, BOOM + 1.3)
key(shock, BOOM, scale=(0.05, 0.05, 0.05))
key(shock, BOOM + 1.3, scale=(WAVE * 1.3,) * 3)
for fc in A._fcurves(shock):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

# rook van zijn schoenen
sm = bpy.data.materials.new("schoenrook")
sm.use_nodes = True
b = sm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.7, 0.7, 0.72, 1)
b.inputs["Alpha"].default_value = 0.35
sm.surface_render_method = "BLENDED"
sm.diffuse_color = (0.7, 0.7, 0.72, 0.35)

# ---------------------------------------------------------------- hij
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.5, at=V(TX, TY, TZ + 0.55))
S.beat(held, l1[0] + 1.2, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=V(TX, TY, TZ + 0.5))
S.beat(held, CLOSE, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.6, at=V(TX, TY, TZ + 0.45), body={"head": (6, 0, 0)})
S.eyes_closed(held, CLOSE, OPEN)
S.beat(held, OPEN, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=1.0, at=V(TX, TY + 0.4, TZ + 0.5))
S.beat(held, UP - 0.2, **SIT_H, pose="ontspannen", face="bang", face_amt=1.0, at=S.head(mama, UP))
S.teleport(held, UP, SEAT + V(0.15, 0.25, 0), heading(SEAT, MOM_AT))
S.beat(held, UP, "staan", face="bang", face_amt=1.0, at=S.head(mama, UP))
S.beat(held, BOOM - 0.4, "staan", face="vastberaden", face_amt=0.9, at=S.head(mama, BOOM))
S.walk(held, BOOM - 0.25, BOOM + 0.15, [SEAT + V(0.15, 0.25, 0), STEP_TO], stride=0.9, end_rot=heading(STEP_TO, MOM_AT))
S.beat(held, BOOM + 0.5, "staan", face="geschrokken", face_amt=1.0, at=S.head(mama, BOOM), arms=arms(HAND_OUT_L, HAND_OUT_R))
S.beat(held, l3[0] + 1.0, "staan", face="geschrokken", face_amt=0.8, look=(0.3, 0.3))
S.beat(held, l3[1] - 2.0, "staan", face="verdrietig", face_amt=0.7, at=S.head(mama, l3[1]))
S.beat(held, l4[0] + 0.3, "staan", face="verdrietig", face_amt=0.8, at=STEP_TO + V(0.1, -0.2, 0.0), body={"head": (6, 0, 0)})
S.beat(held, l4[0] + 3.0, "staan", face="verdrietig", face_amt=1.0, at=S.head(mama, l4[0] + 3.0))
S.walk(held, LEAVE, END, [STEP_TO, STEP_TO + V(-0.9, 0.1, 0)], stride=0.18, end_rot=heading(STEP_TO, DOOR))   # heel, heel voorzichtig
S.hold(held, END)
# rookwolkjes bij zijn schoenen (vanaf de knal)
for k in range(int((END - BOOM) / 0.2) + 1):
    side = 1 if k % 2 else -1
    t0 = BOOM + 0.3 + k * 0.2
    if t0 > END:
        break
    base = S.root_pos(held, t0) if hasattr(S, "root_pos") else S._root_matrix(held, t0).translation
    p0 = Vector(base) + V(0.07 * side + rnd.uniform(-0.03, 0.03), rnd.uniform(-0.05, 0.08), 0.05)
    puff = T.sphere(f"Schoenrook_{k}", (0, 0, 0), 0.045, sm, seg=10, ol=0)
    show(puff, t0, t0 + 3.0)
    key(puff, t0, loc=p0, scale=(0.6, 0.6, 0.6))
    key(puff, t0 + 3.0, loc=p0 + V(rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06), 0.4), scale=(2.2, 2.2, 2.2))

# ---------------------------------------------------------------- mama en papa (honderd keer te langzaam na de knal)
EARS = arms(arm("L", (0.85, 0.15, 0.4), (-0.35, 0.1, 0.93)), arm("R", (0.85, 0.15, 0.4), (-0.35, 0.1, 0.93)))
for ch, face in ((mama, "nerveus"), (papa, "twijfel")):
    S.beat(ch, 0.0, "staan", face=face, face_amt=0.5, at=S.head(held, 0.0))
    S.beat(ch, BOOM, "staan", face=face, face_amt=0.5, at=S.head(held, BOOM))
    S.beat(ch, l4[0] - 0.5, "staan", face="geschrokken", face_amt=0.9, at=S.head(held, l4[0]), arms=EARS)
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
HH = S.headpos(held, CLOSE)
S.cam(0.0, ((1.35, 0.5, 1.3), (SEAT.x - 0.05, SEAT.y + 0.1, 1.0), 28), ((1.3, 0.42, 1.28), (SEAT.x - 0.05, SEAT.y + 0.1, 1.0), 30))
S.cam(l1[0] + 2.8, (HH + V(-0.3, 1.0, -0.12), HH + V(0, 0, -0.02), 30), (HH + V(-0.27, 0.9, -0.12), HH + V(0, 0, -0.02), 33), dof=1.2)
S.cam(UP - 0.1, ((2.1, -0.4, 1.4), (SEAT.x + 0.2, SEAT.y + 0.6, 1.1), 26), ((2.1, -0.3, 1.4), (SEAT.x + 0.4, SEAT.y + 0.8, 1.1), 28))
S.cam(BOOM + 0.05, ((0.9, -2.0, 1.2), (-0.4, 1.6, 1.55), 22), ((0.85, -1.85, 1.22), (-0.4, 1.6, 1.55), 24))
S.cam(l3[0] + 3.0, ((-0.2, 2.0, 1.9), (0.3, -0.6, 1.0), 22), ((-0.25, 1.9, 1.85), (0.3, -0.6, 1.0), 24))
FEET = STEP_TO + V(0, 0, 0.12)
S.cam(l4[0] - 0.1, (FEET + V(0.55, -0.6, 0.15), FEET + V(0, 0, 0.12), 34), (FEET + V(0.5, -0.55, 0.15), FEET + V(0, 0, 0.12), 38), dof=0.9)
S.cam(l4[0] + 2.4, S.shot(mama, l4[0] + 3, "mcu", az=-25, lens=34), S.shot(mama, l4[0] + 5, "mcu", az=-22, lens=38))
S.cam(LEAVE - 0.3, ((2.2, -1.2, 1.6), (-1.6, 0.9, 1.0), 24), ((2.15, -1.15, 1.6), (-1.6, 0.9, 1.0), 25))
S.wall(0.0, BOOM)

S.finish(length=END)
