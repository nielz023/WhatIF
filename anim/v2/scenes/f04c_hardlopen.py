"""F04c · Dag 2 · 10x · straat bij dageraad. Een rondje joggen: 248 km/u. Hij haalt de bestelbus in (de chauffeur
doet heel langzaam zijn mond open) en dan de bus. Voor het eerst in zijn leven wint hij.

    blender -b -P anim/v2/scenes/f04c_hardlopen.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f04c", "straat", "dageraad")

VAN_V = 1.4                                      # m/s in zijn tijd (50 km/u gedeeld door tien)
BUS_V = 1.2
van = S.obj("Bestelbus")
bus = S.obj("Stadsbus")
VAN0 = Vector(van.location)
BUS0 = Vector(bus.location)
LANE = 5.25                                      # fietspad
SIDE = 7.0                                       # stoep

for nm in ("Auto_geparkeerd_3", "Auto_geparkeerd_4"):   # stonden in het shot voor de bestelbus en in de busbaan
    S.obj(nm).hide_render = True
    for c in S.obj(nm).children_recursive:
        c.hide_render = True

# de cabine van de bestelbus openmaken (boolean) en er doorzichtige ruiten in zetten, zodat de chauffeur te zien is
glas = bpy.data.materials.new("bestelbus_ruit_glas")
glas.use_nodes = True
b = glas.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.75, 0.85, 0.95, 1)
b.inputs["Roughness"].default_value = 0.05
b.inputs["Alpha"].default_value = 0.22
glas.surface_render_method = "BLENDED"
glas.diffuse_color = (0.6, 0.75, 0.9, 0.2)
cut = T.box("Bestelbus_cabine_uitsparing", (1.55, 0, 1.0), (1.3, 2.3, 1.2), glas, bevel=0, ol=0)
cut.parent = van
cut.hide_render = True
cut.display_type = "WIRE"
mod = van.modifiers.new("cabine", "BOOLEAN")
mod.object = cut
mod.operation = "DIFFERENCE"
mod.solver = "EXACT"
mod.use_self = True
mod.use_hole_tolerant = True
for nm, loc, size in (("voor", (2.18, 0, 1.0), (0.03, 1.95, 1.2)), ("links", (1.55, 0.99, 1.0), (1.3, 0.03, 1.2)),
                      ("rechts", (1.55, -0.99, 1.0), (1.3, 0.03, 1.2))):
    g = T.box("Bestelbus_ruit_" + nm, loc, size, glas, bevel=0, ol=0)
    g.parent = van
T.box("Bestelbus_stoel", (1.25, 0.45, 0.35), (0.5, 0.5, 0.55), S.mat("busstoel", (0.15, 0.15, 0.18)), bevel=0.04, ol=0).parent = van
T.box("Bestelbus_stuur_as", (1.75, 0.45, 1.05), (0.04, 0.04, 0.3), P.m("zwart"), rot=(0, -40, 0), bevel=0, ol=0).parent = van
T.torus("Bestelbus_stuur", (1.68, 0.45, 1.2), 0.17, 0.02, P.m("zwart"), rot=(0, 55, 0), seg=24, seg2=6, ol=0).parent = van

# ---------------------------------------------------------------- tijdlijn
S.hud2(2, "10x", clock=clock(6 * 3600 + 52 * 60 + 5, 0.1, dec=1, day="TUE"), t0=0.4)
S.ambience("sfx_dageraad_straat", 0.0, 40, vol=0.14)
l1 = S.say("F04-06", gap=0.5)
FAST = l1[0] + 2.8                               # 'two hundred and fifty kilometers an hour'
l2 = S.say("F04-07", gap=0.35)
PASSV = l2[0] + 0.9                              # langs de bestelbus
l3 = S.say("F04-08", gap=0.35)
PASSB = l3[0] + 0.7
WIN = l3[1] - 1.6
END = l3[1] + 1.2
S.music("ochtend", 0.0, END + 1, vol=0.2, fade_in=0.4, fade_out=1.0, start=20.0)
S.sfx("sfx_whoosh", FAST - 0.1, 0.3)
S.sfx("sfx_whoosh", PASSV - 0.15, 0.35)
S.sfx("sfx_brass_hit", PASSV + 0.05, 0.3)
S.sfx("sfx_whoosh", PASSB - 0.1, 0.3)


def speed(t):
    if t < l1[0] + 0.8:
        v = 12
    else:
        v = 12 + (248 - 12) * smooth(l1[0] + 0.8, FAST + 1.2, t)
    return f"{int(round(v)):,} km/h"


S.gauge2(speed, l1[0] + 0.6, END, color=GOLD)

# ---------------------------------------------------------------- de bestelbus en de bus kruipen naar +x
for t in (0.0, END + 1):
    key(van, t, loc=VAN0 + V(VAN_V * t, 0, 0))
    key(bus, t, loc=BUS0 + V(BUS_V * t, 0, 0))
for o in (van, bus):
    for fc in A._fcurves(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def van_x(t):
    return VAN0.x + VAN_V * t


def bus_x(t):
    return BUS0.x + BUS_V * t


# de chauffeur, als kind van de bestelbus (lokale coördinaten: +x = rijrichting)
drv = S.actor("bezorger", (0, 0, 0), 90)
drv.rig.parent = van
drv.rig.matrix_parent_inverse.identity()
SIT_D, zd = sit(drv, seat_top=0.9)
DRV_LOC = V(1.25, 0.45, zd)
S.place(drv, 0, DRV_LOC, 90)
S.beat(drv, 0.0, **SIT_D, pose="staan", face="neutraal", face_amt=0.5, look=(0, 0), arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2))))
S.beat(drv, PASSV + 0.4, **SIT_D, pose="staan", face="verbaasd", face_amt=0.4, look=(0.5, 0.1), body={"head": (0, 20, 0)},
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2))))
S.beat(drv, l2[1] + 0.5, **SIT_D, pose="staan", face="geschrokken", face_amt=1.0, look=(0.7, 0.1), body={"head": (-4, 40, 0)},
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.9, 0.2))))
S.hold(drv, END)
A.key_prop(drv.rig, "mond_open", 0.0, F(PASSV + 0.4))
A.key_prop(drv.rig, "mond_open", 0.9, F(l2[1] + 0.6))         # heel langzaam open

# ---------------------------------------------------------------- hij
held = S.actor("hoofdpersonage", V(-1.4, 8.0, 0.12), 0)
# 1. de voortuin uit, rustig joggen over de stoep
S.beat(held, 0.0, "staan", face="blij", face_amt=0.5, look=(0.4, 0))
S.run(held, 0.2, FAST, [V(-1.4, 8.0, 0.12), V(-0.6, SIDE, 0.12), V(10.0, SIDE, 0.12)], stride=0.85, lift=0.14, lean=8, ease_in=0.2, ease_out=0.0)
# 2. 248 km/u (in zijn tijd): over het fietspad, de huizen vegen voorbij
RUN2 = (V(-75.0, LANE, 0.01), V(-14.0, LANE, 0.01))
S.teleport(held, FAST, RUN2[0], 90)
S.run(held, FAST, PASSV - 0.9, list(RUN2), stride=2.2, lift=0.3, lean=22, ease_in=0.0, ease_out=0.0, arms=1.3)
# 3. langs de bestelbus
P3 = (V(van_x(PASSV) - 18, LANE, 0.01), V(van_x(PASSV) + 30, LANE, 0.01))
S.teleport(held, PASSV - 0.9, P3[0], 90)
S.run(held, PASSV - 0.9, l2[1], list(P3), stride=2.2, lift=0.3, lean=22, ease_in=0.0, ease_out=0.0, arms=1.3)
# 4. langs de bus, omkijken, zwaaien, en dan: gewonnen
P4a = V(bus_x(PASSB) - 16, LANE, 0.01)
P4b = V(bus_x(PASSB) + 14, LANE, 0.01)
S.teleport(held, l2[1], P4a, 90)
S.run(held, l2[1], PASSB + 0.9, [P4a, P4b], stride=2.2, lift=0.3, lean=22, ease_in=0.0, ease_out=0.35, arms=1.3, end_rot=-70)
WAVE_AT = PASSB + 1.0
S.beat(held, WAVE_AT, "staan", face="lach", face_amt=0.9, at=Vector((bus_x(WAVE_AT) + 6, BUS0.y, 2.0)), arms=WAVE_SMALL_R)
S.beat(held, WAVE_AT + 0.35, "staan", face="lach", face_amt=0.9, at=Vector((bus_x(WAVE_AT) + 6, BUS0.y, 2.0)), arms=WAVE_SMALL_R2)
S.beat(held, WAVE_AT + 0.7, "staan", face="lach", face_amt=0.9, at=Vector((bus_x(WAVE_AT) + 6, BUS0.y, 2.0)), arms=WAVE_SMALL_R)
S.beat(held, WIN, "juichen", face="lach", face_amt=1.0, look=(0, 0.3))
S.hold(held, END)

# ---------------------------------------------------------------- camera
# 1. hij komt de tuin uit, op ons af
S.cam(0.0, ((9.0, 3.6, 1.2), (0.0, 7.4, 1.0), 30), ((8.6, 3.7, 1.2), (3.0, 7.2, 1.0), 32))


def follow(t0, t1, side_y, height, lead, lens):
    """Camera rijdt naast hem mee (over het fietspad uitgerekt)."""
    def fn(t):
        p = S._root_matrix(held, t).translation
        return ((p.x + lead, side_y, height), (p.x, LANE, 0.95), lens)
    return fn


# 2. meerijdend, lage zijkant: de geparkeerde auto's en bomen flitsen voorbij
S.cam(FAST, None, fn=follow(FAST, PASSV - 0.9, 2.3, 0.95, 1.2, 30))
# 3a. laag voor de bestelbus: hij schiet op het fietspad voorbij, de bus staat bijna stil
VF = Vector((van_x(PASSV) + 9.0, 2.6, 0.7))
S.cam(PASSV - 0.9, (VF, Vector((van_x(PASSV) - 6.0, 3.6, 1.2)), 26), (VF, Vector((van_x(PASSV) - 2.0, 3.8, 1.25)), 27))
# 3b. de chauffeur achter de voorruit: zijn mond gaat heel langzaam open


def drv_cam(t):
    x = van_x(t)
    return ((x + 2.6, VAN0.y + 2.5, 1.75), (x + 1.25, VAN0.y + 0.45, 1.65), 34)


S.cam(PASSV + 1.0, None, fn=drv_cam)
# 4. de bus: hij komt erlangs, draait zich om, zwaait, juicht
S.cam(l2[1], ((bus_x(PASSB) + 26.0, 3.0, 1.3), (bus_x(PASSB) + 6.0, 3.8, 1.4), 40),
      ((bus_x(PASSB) + 25.0, 3.1, 1.3), (bus_x(PASSB) + 9.0, 3.8, 1.4), 44))
S.cam(WAVE_AT + 0.2, S.shot(held, WAVE_AT + 0.4, "med", az=-40, lens=30), S.shot(held, END, "mcu", az=-30, lens=36))

S.finish(length=END)
