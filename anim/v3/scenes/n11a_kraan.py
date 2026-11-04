"""N11a · Dag 5: geen water (script scène 11a-11b), keuken met planken voor het raam, ochtend.
11a DETAIL: de kraan sputtert, spuugt twee druppels en stopt.
    VO: "This part is real. Most tap water is pumped by electric pumps. No power... no water."
11b MEDIUM: mama draait de kraan helemaal open en weer dicht, twee keer, tikt met haar knokkel op de kraan, zucht.

    blender -b -P anim/v3/scenes/n11a_kraan.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n11a", "keuken", "nr_kaarsen", exposure=0.5)
sh = S.cuts([3.2, 3.8])
END = sh[-1][1]
t_b = sh[1][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Kaars_tafel", "Lucifers", "Kaarsvlam", "Kaars_licht")):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# ---------------------------------------------------------------- kraan: hendel bovenop, druppels uit de tuit
TIP = V(-0.2, 1.845, 1.172)                                  # onderkant van de tuit
SINK_Z = 0.927                                               # bodem van de spoelbak (op de donkere binnenbak)
T.box("Spoelbak_rand", (-0.2, 1.75, 0.921), (0.56, 0.4, 0.004), S.mat("spoelbak_rand", (0.8, 0.82, 0.86)), base=False, bevel=0.01, ol=0)
T.box("Spoelbak_binnen", (-0.2, 1.75, 0.923), (0.48, 0.32, 0.004), S.mat("spoelbak_binnen", (0.32, 0.35, 0.4)), base=False, bevel=0.02, ol=0)
T.cyl("Spoelbak_putje", (-0.2, 1.75, 0.9255), 0.02, 0.002, S.mat("putje", (0.15, 0.15, 0.17)), seg=16, ol=0)
STEEL = S.mat("kraan_staal", (0.78, 0.80, 0.84))
piv = bpy.data.objects.new("Kraan_hendel_as", None)
bpy.context.scene.collection.objects.link(piv)
piv.location = (-0.2, 2.01, 1.225)
lever = T.box("Kraan_hendel", (0.045, 0, 0.012), (0.09, 0.016, 0.012), STEEL, base=False, bevel=0.004, ol=0.002)
knob = T.sphere("Kraan_hendel_knop", (0.09, 0, 0.012), 0.012, STEEL, seg=10, ol=0)
cap = T.cyl("Kraan_hendel_voet", (0, 0, 0.004), 0.022, 0.016, STEEL, seg=16, ol=0.002)
for o in (lever, knob, cap):
    o.parent = piv
piv.rotation_mode = "XYZ"
# open = hendel 70 graden naar de muur toe gedraaid (draaipunt boven de kraan)
LEV = [(0.0, 0), (0.15, 0), (0.45, 70), (t_b - 0.01, 70),       # 11a: staat al open, sputtert
       (t_b + 0.15, 0), (t_b + 0.55, 0), (t_b + 0.8, 70), (t_b + 1.15, 70), (t_b + 1.4, 0),   # dicht, nog eens open... niets
       (t_b + 1.6, 0), (t_b + 1.85, 70), (t_b + 2.1, 70), (t_b + 2.3, 0)]
for t, a in LEV:
    piv.rotation_euler = (0, 0, math.radians(a))
    piv.keyframe_insert("rotation_euler", index=2, frame=F(t))


def lever_tip(t):
    S.sc.frame_set(F(t))
    return piv.matrix_world @ V(0.09, 0, 0.012)


WATER = S.mat("waterdruppel", (0.62, 0.82, 0.98), 0.6)
SPLASH = S.mat("waterspat", (0.75, 0.88, 1.0), 0.4)


def drop(name, t_form, t_fall, r=0.011, stay=False):
    """Druppel groeit aan de tuit, rekt uit, valt (versnelt) en spat in de spoelbak."""
    d = T.sphere(name, tuple(TIP), r, WATER, seg=14, ol=0)
    visible(d, 0.0, False)
    visible(d, t_form, True)
    for t, s, sz in ((t_form, 0.25, 1.0), (t_fall - 0.25, 0.85, 1.15), (t_fall, 1.0, 1.4)):
        d.location = TIP - V(0, 0, r * s * sz)
        d.scale = (s, s, s * sz)
        d.keyframe_insert("location", frame=F(t))
        d.keyframe_insert("scale", frame=F(t))
    if stay:
        return d
    z0 = TIP.z - r * 1.4
    f0, t_hit = F(t_fall), t_fall + math.sqrt(2 * (z0 - SINK_Z) / 9.8)
    for f in range(f0 + 1, F(t_hit) + 1):
        dt = (f - f0) / FPS
        d.location = (TIP.x, TIP.y, max(SINK_Z, z0 - 0.5 * 9.8 * dt * dt))
        d.scale = (0.9, 0.9, 1.6)
        d.keyframe_insert("location", frame=f)
        d.keyframe_insert("scale", frame=f)
    visible(d, t_hit + 1 / FPS, False)
    # spatje: platte ring en twee mini-druppeltjes die opspringen
    ring = T.sphere(name + "_spat", (TIP.x, TIP.y, SINK_Z + 0.002), 0.012, SPLASH, scale=(1, 1, 0.12), seg=14, ol=0)
    visible(ring, 0.0, False)
    visible(ring, t_hit, True)
    visible(ring, t_hit + 0.3, False)
    for t, s in ((t_hit, 0.4), (t_hit + 0.28, 2.6)):
        ring.scale = (s, s, 0.12)
        ring.keyframe_insert("scale", frame=F(t))
    for k, dx in enumerate((-1, 1)):
        m = T.sphere(f"{name}_spatje_{k}", (TIP.x, TIP.y, SINK_Z), 0.004, WATER, seg=8, ol=0)
        visible(m, 0.0, False)
        visible(m, t_hit, True)
        visible(m, t_hit + 0.22, False)
        for t, off in ((t_hit, V(0, 0, 0.002)), (t_hit + 0.1, V(0.012 * dx, -0.006, 0.03)), (t_hit + 0.22, V(0.025 * dx, -0.012, 0.004))):
            m.location = V(TIP.x, TIP.y, SINK_Z) + off
            m.keyframe_insert("location", frame=F(t))
    return d


# sputter: lucht en een paar spetters schieten eruit
for k in range(5):
    sp = T.sphere(f"Sputter_{k}", tuple(TIP), 0.0045, WATER, seg=8, ol=0)
    visible(sp, 0.0, False)
    visible(sp, 0.42 + k * 0.03, True)
    visible(sp, 0.72 + k * 0.03, False)
    dirv = V(0.05 * math.sin(k * 2.1), -0.04 - 0.02 * (k % 2), -0.25)
    for t, u in ((0.42 + k * 0.03, 0.0), (0.72 + k * 0.03, 1.0)):
        sp.location = TIP + dirv * u
        sp.keyframe_insert("location", frame=F(t))
drop("Druppel_1", 0.95, 1.55)
drop("Druppel_2", 1.85, 2.5, r=0.009)
drop("Druppel_3", 2.75, END + 1, r=0.007, stay=True)        # blijft hangen, valt niet meer

# ---------------------------------------------------------------- mama aan het aanrecht
M_AT = V(-0.12, 1.12, 0)
mama = S.actor("mama", M_AT, 180)
for o in [mama.rig] + list(mama.rig.children_recursive):      # 11a is een detail van de kraan: mama pas in 11b in beeld
    visible(o, 0.0, False)
    visible(o, t_b, True)
LOOK = TIP + V(0, 0.1, 0.22)                                # naar de kraan, niet steil omlaag
S.beat(mama, 0.0, "staan", face="twijfel", face_amt=0.6, at=LOOK, body={"spine": (5, 0, 0)})
S.reach(mama, 0.0, "L", inf=0.0)
S.reach(mama, END, "L", inf=0.0)
for t, a in LEV:
    S.reach(mama, t, "R", lever_tip(t) + V(0.0, -0.03, 0.03))
# knokkel: tikt twee keer op de tuit, dan valt de hand en zucht ze
TAP = V(-0.2, 1.93, 1.24)
for t, dz in ((t_b + 2.45, 0.08), (t_b + 2.6, 0.0), (t_b + 2.72, 0.07), (t_b + 2.84, 0.0)):
    S.reach(mama, t, "R", TAP + V(0.0, -0.04, dz))
S.reach(mama, t_b + 3.1, "R", inf=0.0)
S.reach(mama, END, "R", inf=0.0)
S.beat(mama, t_b + 0.6, "staan", face="nerveus", face_amt=0.6, at=LOOK, body={"spine": (5, 0, 0)})
S.beat(mama, t_b + 1.5, "staan", face="verbaasd", face_amt=0.5, at=LOOK, body={"spine": (5, 0, 0)})
S.beat(mama, t_b + 2.4, "staan", face="boos", face_amt=0.4, at=LOOK, body={"spine": (9, 0, 0)})
S.beat(mama, t_b + 3.0, "staan", face="twijfel", face_amt=0.8, at=LOOK + V(0.1, 0, -0.08), body={"spine": (4, 0, 0), "chest": (6, 0, 0)})
S.beat(mama, END, "staan", face="twijfel", face_amt=0.9, at=LOOK + V(0.3, -0.2, -0.1), body={"spine": (3, 0, 0), "chest": (9, 0, 0)})
A.blink_at(mama, F(t_b + 3.15), closed=5)
S.hold(mama, END)

# ---------------------------------------------------------------- camera's
# 11a DETAIL de tuit en de spoelbak, net boven het aanrecht
S.cam(0.0, ((0.15, 1.3, 1.25), (-0.2, 1.86, 1.06), 35), ((0.12, 1.34, 1.23), (-0.2, 1.86, 1.06), 39))
# 11b MEDIUM vanaf het aanrecht rechts, langs de muur: mama 3/4 van voren aan de kraan
S.wall(t_b, END + 1, "front")                              # tegenshot naar -y: voormuur dicht
S.cam(t_b, ((0.42, 2.0, 1.4), (-0.15, 1.25, 1.32), 18), ((0.4, 1.98, 1.39), (-0.15, 1.25, 1.32), 19))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 5", 0, t0=0.0)
S.sfx("sfx_kraan_sputter", 0.3, 0.35)
S.sfx("sfx_kraan_sputter", t_b + 0.75, 0.12)
S.sfx("sfx_knokkels", t_b + 2.55, 0.35)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.03)
S.say("N11-01", at=0.3)
S.finish(length=END, tail=0.0)
