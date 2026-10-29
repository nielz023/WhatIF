"""F10b · Dag 4 → dag 5 · de gang en de keuken. Hij loopt met piepkleine, voorzichtige stapjes door de gang
(voor hen een millimeter per seconde: Snail). Dag 5 · 10.000x · 08:59:50: hij kiepert een glas water om en het
water blijft erin. Hij grijpt gewoon naar de knijpfles en zijn mouw begint te roken.

    blender -b -P anim/v2/scenes/f10b_gang_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402

S = Scene2("f10b", "keuken", "verjaardag")
rnd = random.Random(10)

TX, TY, TZ = 0.2, -0.6, 0.76
SEAT = S.obj("Stoel_2").location.copy()          # (0.58, -1.22): hij zit met zijn gezicht naar de tafel (+y)
MOM_AT = V(1.05, 0.85, 0)
GLASS = V(TX + 0.55, TY - 0.2, TZ)
BOTTLE = V(TX + 0.05, TY - 0.32, TZ)             # de knijpfles staat vandaag op tafel, links van hem

# ---------------------------------------------------------------- dag 5, 08:59:50: het feest moet nog beginnen
PARTY = ("Verjaardagstaart", "Kaars", "Vlammetje", "Kaarslicht", "Bordjes", "Aansteker", "Cadeau_opa_oma", "Slinger",
         "Ballonnen", "Whiteboard_achter_regel5", "Whiteboard_achter_regel6", "Kraanvogel_tafelrand", "Kraanvogel_de_laatste")
for o in bpy.data.objects:
    if o.name.startswith(PARTY):
        o.hide_render = True
        o.hide_viewport = True
glass = S.obj("Glas_water")
bottle = S.obj("Knijpfles")
bottle.location = BOTTLE

# ---------------------------------------------------------------- de gang (los gebouwd, ver van de keuken)
HX = -20.0                                       # gang langs y, voordeur op y -3, keukendeur op y +3
GW, GL, GH = 1.5, 6.0, 2.6
wall = S.mat("gang_behang", (0.93, 0.86, 0.72))
wood = S.mat("gang_plint", (0.95, 0.94, 0.9))
T.box("Gang_vloer", (HX, 0, -0.02), (GW + 0.4, GL + 0.4, 0.02), S.mat("gang_vloer", (0.55, 0.38, 0.24)), bevel=0, ol=0)
T.box("Gang_loper", (HX, 0.0, 0.0), (0.8, 4.6, 0.012), S.mat("gang_loper", (0.62, 0.16, 0.16)), bevel=0.004, ol=0)
T.box("Gang_plafond", (HX, 0, GH), (GW + 0.4, GL + 0.4, 0.05), S.mat("gang_plafond", (0.97, 0.97, 0.95)), bevel=0, ol=0)
for s in (-1, 1):
    T.box(f"Gang_muur_{s}", (HX + s * (GW / 2 + 0.05), 0, 0), (0.1, GL, GH), wall, bevel=0, ol=0)
    T.box(f"Gang_plint_{s}", (HX + s * (GW / 2 - 0.01), 0, 0), (0.02, GL, 0.1), wood, bevel=0.003, ol=0)
T.box("Gang_muur_voor", (HX, -GL / 2 - 0.05, 0), (GW + 0.2, 0.1, GH), wall, bevel=0, ol=0)
T.box("Gang_voordeur", (HX, -GL / 2 + 0.01, 0), (0.95, 0.04, 2.15), S.mat("voordeur_rood", (0.85, 0.20, 0.15)), bevel=0.01, ol=0)
T.sphere("Gang_voordeur_klink", (HX + 0.35, -GL / 2 + 0.05, 1.05), 0.035, S.mat("messing", (0.85, 0.68, 0.25)), seg=10, ol=0)
T.box("Gang_deurmat", (HX, -GL / 2 + 0.45, 0.0), (0.8, 0.5, 0.015), S.mat("deurmat", (0.45, 0.33, 0.2)), bevel=0.004, ol=0)
# keukenkant: een deuropening met warm licht erachter
for s in (-1, 1):
    T.box(f"Gang_muur_achter_{s}", (HX + s * 0.62, GL / 2 + 0.05, 0), (0.42, 0.1, GH), wall, bevel=0, ol=0)
T.box("Gang_muur_achter_boven", (HX, GL / 2 + 0.05, 2.1), (0.85, 0.1, 0.5), wall, bevel=0, ol=0)
T.box("Gang_keukengloed", (HX, GL / 2 + 0.6, 0), (1.2, 0.05, 2.4), S.mat("keuken_gloed", (1.0, 0.85, 0.6), glow=1.2), bevel=0, ol=0)
# kapstok met jassen, schoenenrek met zijn kapotte sneakers van dag 2
T.box("Gang_kapstok", (HX - GW / 2 + 0.03, -1.2, 1.65), (0.04, 1.1, 0.08), wood, bevel=0.01, ol=0)
for k, (c, dy) in enumerate((((0.2, 0.35, 0.65), -1.55), ((0.85, 0.55, 0.15), -1.15), ((0.3, 0.55, 0.3), -0.8))):
    T.box(f"Gang_jas_{k}", (HX - GW / 2 + 0.13, dy, 0.85), (0.2, 0.36, 0.8), S.mat(f"jas_{k}", c), bevel=0.08, ol=0)
T.box("Gang_schoenenrek", (HX + GW / 2 - 0.17, -1.6, 0.0), (0.3, 0.8, 0.32), wood, bevel=0.01, ol=0)
for k, dy in enumerate((-1.75, -1.48)):
    sn = HU.kapotte_sneaker(f"Gang_sneaker_{k}", (HX + GW / 2 - 0.17, -1.6 + dy + 1.6 + (k - 0.5) * 0.12, 0.33), rot=90)
# fotolijstjes
for k, (dy, z, c) in enumerate(((0.4, 1.55, (0.4, 0.6, 0.85)), (0.95, 1.7, (0.9, 0.6, 0.4)), (1.5, 1.5, (0.5, 0.8, 0.5)))):
    T.box(f"Gang_lijst_{k}", (HX + GW / 2 - 0.01, dy, z), (0.02, 0.36, 0.28), S.mat("lijst_goud", (0.85, 0.72, 0.4)), bevel=0.005, ol=0)
    T.box(f"Gang_foto_{k}", (HX + GW / 2 - 0.025, dy, z + 0.03), (0.01, 0.3, 0.22), S.mat(f"foto_{k}", c), bevel=0, ol=0)
# een slak op de loper (zelfde tempo als hij, voor hen)
slak = [T.sphere("Slak_huis", (0, 0, 0.055), 0.05, S.mat("slakkenhuis", (0.62, 0.42, 0.22)), scale=(1.0, 0.75, 1.0), seg=16, ol=0),
        T.torus("Slak_spiraal", (0, -0.038, 0.055), 0.028, 0.008, S.mat("slakkenhuis_d", (0.42, 0.26, 0.12)), rot=(90, 0, 0), seg=20, seg2=6, ol=0),
        T.box("Slak_lijf", (0.02, 0, 0.0), (0.16, 0.045, 0.03), S.mat("slak_lijf", (0.72, 0.66, 0.5)), bevel=0.014, ol=0),
        T.cyl("Slak_spriet_l", (0.085, 0.012, 0.02), 0.004, 0.05, S.mat("slak_lijf", (0.72, 0.66, 0.5)), rot=(0, 25, 0), seg=6, ol=0),
        T.cyl("Slak_spriet_r", (0.085, -0.012, 0.02), 0.004, 0.05, S.mat("slak_lijf", (0.72, 0.66, 0.5)), rot=(0, 25, 0), seg=6, ol=0)]
snail = T.merge("Slak", slak, ol=0)
snail.location = (HX + 0.32, 0.1, 0.012)
snail.rotation_euler.z = math.radians(90)          # kruipt ook richting de keuken
for nm, loc, e in (("Gang_lamp_1", (HX, -1.2, 2.45), 70), ("Gang_lamp_2", (HX, 1.4, 2.45), 70), ("Gang_keukenlicht", (HX, GL / 2 + 0.4, 1.6), 60)):
    ld = bpy.data.lights.new(nm, "POINT")
    ld.energy = e
    ld.color = (1.0, 0.86, 0.66)
    ld.shadow_soft_size = 0.3
    lo = bpy.data.objects.new(nm, ld)
    lo.location = loc
    T._link(lo)

# ---------------------------------------------------------------- tijdlijn
G0 = V(HX + 0.05, -2.2, 0.0)
G1 = V(HX + 0.0, 1.9, 0.0)
l1 = S.say("F10-04", gap=0.8)
SNAIL = l1[0] + 0.52 * (l1[1] - l1[0])          # 'Snail.'
GANG_END = l1[1] + 0.9
BLACK0, BLACK1 = GANG_END, GANG_END + 1.4         # hij valt in slaap; zwart
DAY5 = BLACK1
l2 = S.say("F10-05", at=DAY5 + 0.9)
d2 = l2[1] - l2[0]
TIP0 = l2[0] + 0.30 * d2                         # 'Water won't pour anymore.'
TIP1 = TIP0 + 0.9
l3 = S.say("F10-06", gap=0.6)
d3 = l3[1] - l3[0]
GRAB = l3[0] + 0.6                               # hij beweegt zijn arm gewoon
SMOKE = GRAB + 0.35
METEOR = l3[0] + 0.30 * d3                       # 'meteors burn'
BACK = l3[0] + 0.62 * d3
END = l3[1] + 1.8

START4 = 8 * 3600 + 59 * 60 + 13.0               # na de raamscène
S.hud2(4, "1,000x", clock=clock(START4, 1 / 1000, dec=2, day="TUE"), t0=0.3, t1=BLACK0,
       awake=awake(8 + 50 / 60, rate=1 / 3600, t0=0.0), awake_t0=0.5)
S.hud2(5, "10,000x", clock=clock(8 * 3600 + 59 * 60 + 50.0, 1 / 10000, dec=3, day="TUE", t0=DAY5), t0=DAY5 + 0.2,
       awake=awake(0.0, rate=1 / 3600, t0=DAY5, secs=True), awake_t0=DAY5 + 0.4)
S.gauge2("YOUR SPEED (FOR THEM): 1 mm/s", l1[0] + 0.3, SNAIL - 0.2, color=GOLD, row=0)
S.real(METEOR - 0.2, BACK + 1.5)
S.card("", BLACK0 - 0.4, BLACK1, dim=1.0, fin=20, fout=8)
S.music("piano_zacht", 0.0, BLACK0, vol=0.15, fade_in=1.0, fade_out=1.0)
S.music("drone", SMOKE - 0.4, END, vol=0.18, fade_in=0.8, fade_out=1.5)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.05)
S.sfx("sfx_hud_tik", DAY5 + 0.2, 0.5)
S.sfx("sfx_klok_motief", DAY5 + 0.3, 0.16)
S.sfx("sfx_rook_sis", SMOKE, 0.22, cut=(0, 3.0))

# ---------------------------------------------------------------- hij in de gang
held = S.actor("hoofdpersonage", G0, 180)
SIT_H, zh = sit(held)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
CAREFUL = arms(arm("L", (0.45, 0.25, -0.85), (0.3, 0.6, -0.4)), arm("R", (0.45, 0.25, -0.85), (0.3, 0.6, -0.4)))
S.beat(held, 0.0, "staan", face="inspanning", face_amt=0.5, look=(0, -0.15), arms=CAREFUL)
S.walk(held, 0.3, GANG_END, [G0, G1], stride=0.14, arms=0.1)
S.beat(held, SNAIL - 0.3, "staan", face="verdrietig", face_amt=0.5, at=snail.location + V(0, 0, 0.05), arms=CAREFUL)
S.beat(held, SNAIL + 1.3, "staan", face="inspanning", face_amt=0.4, look=(0, -0.1), arms=CAREFUL)
S.hold(held, GANG_END)

# dag 5: aan tafel, hoofd op zijn armen; hij komt overeind
S.teleport(held, BLACK1 - 0.3, SEAT + V(0, 0, zh), 180)
ARMS_TABLE = arms(arm("L", (0.2, 0.85, -0.2), (-0.6, 0.6, 0.0)), arm("R", (0.2, 0.85, -0.2), (-0.6, 0.6, 0.0)))
S.beat(held, BLACK1 - 0.3, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.3, look=(0, -0.3),
       body={"spine": (14, 0, 0), "head": (20, 0, 0)}, arms=ARMS_TABLE)
S.eyes_closed(held, BLACK1 - 0.3, DAY5 + 0.5)
S.beat(held, DAY5 + 0.9, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=0.6, at=GLASS + V(0, 0, 0.25))
S.beat(held, TIP0 - 0.5, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=GLASS + V(0, 0, 0.1))
# het glas: rechterhand pakt het en kiepert het boven de tafel om. Het water blijft gewoon in het glas.
TIP_AT = GLASS + V(-0.12, -0.05, 0.34)
S.reach(held, TIP0 - 0.6, "R", None, 0.0)
S.reach(held, TIP0 - 0.15, "R", GLASS + V(0.05, -0.04, 0.07))
S.reach(held, TIP0 + 0.25, "R", TIP_AT + V(0.04, 0.0, 0.0))
S.reach(held, TIP1, "R", TIP_AT)
S.reach(held, l2[1] + 0.3, "R", TIP_AT + V(0.0, 0.0, 0.01))
S.beat(held, TIP1, **SIT_H, pose="ontspannen", face="verbaasd", face_amt=0.9, at=TIP_AT + V(0, 0, 0.05))
# glas weer neerzetten
S.reach(held, l3[0] - 0.1, "R", GLASS + V(0.05, -0.04, 0.07))


def tilt(t):
    """Hoek van het glas (graden om y): rechtop, omgekiept, weer rechtop."""
    for (ta, va), (tb, vb) in zip(GT, GT[1:]):
        if t <= tb:
            u = 0 if tb == ta else (t - ta) / (tb - ta)
            u = u * u * (3 - 2 * u)
            return va + (vb - va) * u
    return GT[-1][1]


GT = [(0.0, 0.0), (TIP0 + 0.1, 0.0), (TIP1, -150.0), (l3[0] - 0.4, -150.0), (l3[0] - 0.1, 0.0), (99.0, 0.0)]


def hand_c(t):
    return S.bone_world(held, "hand.R", t, tail=False).lerp(S.bone_world(held, "hand.R", t, tail=True), 0.45)


GRIP = GLASS + V(0, 0, 0.055) - hand_c(TIP0)   # het glas zit vast in zijn hand vanaf TIP0
key(glass, 0.0, loc=GLASS, rot=(0, 0, 0))
key(glass, TIP0, loc=GLASS, rot=(0, 0, 0))
t = TIP0 + 1 / 12
while t < l3[0] - 0.1:
    a = math.radians(tilt(t))
    key(glass, t, loc=hand_c(t) + GRIP - V(0.055 * math.sin(a), 0, 0.055 * math.cos(a)), rot=(0, tilt(t), 0))
    t += 1 / 12
key(glass, l3[0] - 0.1, loc=GLASS, rot=(0, 0, 0))
S.reach(held, l3[0] + 0.2, "R", None, 0.0)
# de knijpfles: zijn linkerarm gaat gewoon, en zijn mouw begint te roken
S.reach(held, GRAB - 0.3, "L", None, 0.0)
S.reach(held, GRAB, "L", BOTTLE + V(0.06, -0.06, 0.12))
S.beat(held, GRAB - 0.2, **SIT_H, pose="ontspannen", face="vastberaden", face_amt=0.5, at=BOTTLE + V(0, 0, 0.1))
S.beat(held, SMOKE + 0.3, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=1.0, at=BOTTLE + V(0.05, -0.2, 0.3))
S.reach(held, BACK - 0.6, "L", BOTTLE + V(0.06, -0.06, 0.12))
S.reach(held, BACK, "L", None, 0.0)                     # hij trekt zijn arm (heel langzaam) terug
S.beat(held, BACK, **SIT_H, pose="ontspannen", face="bang", face_amt=0.8, look=(0.35, -0.3),
       arms=arms(arm("L", (0.15, 0.6, -0.75), (-0.5, 0.75, 0.3))))
S.beat(held, END - 1.0, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.8, look=(0.35, -0.3),
       arms=arms(arm("L", (0.15, 0.6, -0.75), (-0.5, 0.75, 0.3))))
S.hold(held, END)

# rook van zijn mouw (alfa-wolkjes, zoals de schoenrook op dag 3)
sm = bpy.data.materials.new("mouwrook")
sm.use_nodes = True
b = sm.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.72, 0.72, 0.74, 1)
b.inputs["Alpha"].default_value = 0.32
sm.surface_render_method = "BLENDED"
sm.diffuse_color = (0.72, 0.72, 0.74, 0.32)
for k in range(int((BACK + 0.6 - SMOKE) / 0.12)):
    t0 = SMOKE + k * 0.12
    life = 2.4
    w = S.bone_world(held, "forearm.L", t0, tail=False).lerp(S.bone_world(held, "forearm.L", t0, tail=True), rnd.uniform(0.4, 1.0))
    p0 = w + V(rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), 0.04)
    puff = T.sphere(f"Mouwrook_{k}", (0, 0, 0), 0.035, sm, seg=10, ol=0)
    show(puff, t0, min(END + 0.1, t0 + life))
    key(puff, t0, loc=p0, scale=(0.5, 0.5, 0.5))
    key(puff, t0 + life, loc=p0 + V(rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), 0.45), scale=(2.4, 2.4, 2.4))
# gloed op zijn mouw (de lucht wordt heet)
gl = T.sphere("Mouwgloed", (0, 0, 0), 0.05, S.mat("mouwgloed", (1.0, 0.45, 0.15), glow=4.0), scale=(1.6, 0.8, 0.8), seg=12, ol=0)
grab(S, gl, held, 0.0, "forearm.L", loc=(0, 0.12, 0))
show(gl, SMOKE, BACK + 0.4)

# ---------------------------------------------------------------- mama, bevroren aan het aanrecht
ROBE = (0.86, 0.62, 0.76)
mama = S.actor("mama", MOM_AT, heading(MOM_AT, SEAT), outfit=dict(shirt=ROBE, broek=ROBE))
S.beat(mama, 0.0, "staan", face="nerveus", face_amt=0.5, at=SEAT + V(0, 0, 1.0))
S.hold(mama, END)
show_list = [o for o in mama.rig.children_recursive]
for o in show_list:
    show(o, DAY5 - 0.5)

# ---------------------------------------------------------------- camera
# gang
S.cam(0.0, ((HX + 0.3, 2.6, 1.3), (HX, -1.6, 0.9), 30), ((HX + 0.3, 2.5, 1.3), (HX, -1.2, 0.9), 32))
S.cam(l1[0] + 2.0, ((HX - 0.55, -0.5, 0.25), (HX + 0.05, -1.15, 0.15), 30), ((HX - 0.55, -0.35, 0.25), (HX + 0.05, -0.95, 0.15), 30))
S.cam(SNAIL - 0.4, ((HX + 0.65, 0.35, 0.18), (HX + 0.3, 0.05, 0.06), 40), ((HX + 0.64, 0.38, 0.18), (HX + 0.3, 0.06, 0.06), 42), dof=0.4)
S.cam(SNAIL + 1.2, ((HX - 0.6, 2.7, 2.2), (HX, -0.3, 0.7), 26), ((HX - 0.55, 2.7, 2.2), (HX, 0.1, 0.7), 27))
# keuken, dag 5
S.wall(DAY5 - 0.3, END + 1)
S.cam(DAY5 - 0.1, ((2.25, -1.05, 1.7), (0.5, -0.1, 0.9), 24), ((2.2, -1.0, 1.68), (0.5, -0.1, 0.9), 25))
HD = S.bone_world(held, "head", DAY5 + 1.2, tail=False) + V(0, 0, 0.2)
S.cam(DAY5 + 1.5, ((SEAT.x + 1.4, SEAT.y + 1.2, 1.5), HD + V(-0.1, 0, -0.05), 32), ((SEAT.x + 1.35, SEAT.y + 1.1, 1.45), HD + V(-0.1, 0, -0.05), 34))
S.cam(TIP0 - 0.3, (TIP_AT + V(0.08, 0.75, 0.0), TIP_AT + V(0.0, 0, -0.1), 40),
      (TIP_AT + V(0.06, 0.62, 0.0), TIP_AT + V(0.0, 0, -0.08), 46), dof=0.6)
S.cam(GRAB - 0.5, ((BOTTLE.x - 0.9, BOTTLE.y + 0.5, 1.35), BOTTLE + V(0.25, -0.35, 0.2), 30),
      ((BOTTLE.x - 0.85, BOTTLE.y + 0.45, 1.3), BOTTLE + V(0.25, -0.35, 0.2), 32))
FA = S.bone_world(held, "forearm.L", SMOKE + 0.8, tail=False).lerp(S.bone_world(held, "forearm.L", SMOKE + 0.8), 0.6)
S.cam(SMOKE + 0.6, (FA + V(-0.55, -0.3, 0.4), FA + V(0.05, 0.05, 0.12), 36), (FA + V(-0.5, -0.28, 0.38), FA + V(0.05, 0.05, 0.14), 40), dof=0.7)
HB = S.bone_world(held, "head", BACK + 0.6, tail=False) + V(0, 0, 0.2)
S.cam(BACK - 0.1, ((SEAT.x - 0.25, SEAT.y + 1.25, 1.3), HB, 34), ((SEAT.x - 0.22, SEAT.y + 1.15, 1.3), HB, 36), dof=1.0)

S.finish(length=END)
