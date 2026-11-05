"""N19a · Jaar 5: de herbouwde stad (script scène 19a-19c).
19a  WIDE drone: tijdsprongkaart 5 YEARS LATER. De stad is herbouwd maar anders: zonnepanelen op elk dak, groene daken,
     fietsen overal. VO N19-01.
19b  MEDIUM: een bord BIKES ONLY midden op de weg. Fietsers rijden erlangs, een auto komt aan, stopt en keert om.
19c  MEDIUM: een bord NO MUSIC AFTER 10 PM. Een man op de stoep zet zijn radio zachter. VO N19-02.

    blender -b -P anim/v3/scenes/n19a_stad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n19a", "stad", "middag", exposure=0.25)
CARD = 1.3
sh = S.cuts([CARD, 4.2, 3.4, 3.6])
END = sh[-1][1]
t_a, t_b, t_c = [s[0] for s in sh[1:]]
rnd = random.Random(19)
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True
# minder auto's: de geparkeerde auto's zijn weg, er staan fietsen
for o in list(bpy.data.objects):
    if o.name.startswith("Auto_geparkeerd"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- daken: zonnepanelen en groene daken
PANEL = S.mat("zonnecel_dak", (0.08, 0.12, 0.3))
FRAME = S.mat("paneel_frame", (0.8, 0.82, 0.85))
GREEN = S.mat("groen_dak", (0.32, 0.62, 0.28))
for g in [o for o in bpy.data.objects if o.name.startswith("Gebouw_") and o.type == "EMPTY"]:
    meshes = [c for c in g.children_recursive if c.type == "MESH"]
    if not meshes:
        continue
    pts = [c.matrix_world @ V(b) for c in meshes for b in c.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    top = max(p.z for p in pts)
    w, d = x1 - x0, y1 - y0
    if w < 3 or d < 3:
        continue
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if rnd.random() < 0.4:
        T.box(g.name + "_groendak", (cx, cy, top), (w * 0.86, d * 0.86, 0.12), GREEN, bevel=0.05, ol=0)
        for k in range(5):
            T.sphere(f"{g.name}_struik{k}", (cx + rnd.uniform(-w, w) * 0.35, cy + rnd.uniform(-d, d) * 0.35, top + 0.3), 0.45,
                     S.mat("boomblad_dak", (0.22, 0.5, 0.2)), scale=(1, 1, 0.7), seg=10, ol=0)
    else:
        nx, ny = max(1, int(w * 0.8 / 2.2)), max(1, int(d * 0.8 / 1.4))
        for i in range(nx):
            for j in range(ny):
                px = x0 + w * 0.1 + (i + 0.5) * (w * 0.8 / nx)
                py = y0 + d * 0.1 + (j + 0.5) * (d * 0.8 / ny)
                T.box(f"{g.name}_pv_{i}_{j}", (px, py, top + 0.3), (1.9, 1.1, 0.05), PANEL, rot=(25, 0, 0), bevel=0.01, ol=0.004)

# ---------------------------------------------------------------- fietsers overal
RIDERS = [("figurant_a", [V(-2.2, -40, 0), V(-2.2, 40, 0)], 0.0, END, (0.85, 0.15, 0.12)),
          ("figurant_e", [V(2.4, 40, 0), V(2.4, -40, 0)], 0.0, END, (0.15, 0.45, 0.85)),
          ("figurant_f", [V(-40, -2.4, 0), V(40, -2.4, 0)], 0.0, END, (0.95, 0.75, 0.15)),
          ("kind_a", [V(40, 2.2, 0), V(-40, 2.2, 0)], 0.0, END, (0.3, 0.7, 0.35))]
for k, (n, pts, t0, t1, col) in enumerate(RIDERS):
    d = pts[1] - pts[0]
    ch = S.actor(n, pts[0], math.degrees(math.atan2(d.x, -d.y)), label=f"fietser_{k}")
    _, crank = bike(S, ch, color=col, name=f"Fiets_stad_{k}")
    a = pts[0] + d * (0.25 + 0.1 * k)
    ride_path(S, ch, crank, t0, t1, [a, a + d.normalized() * 5.2 * (t1 - t0)], cadence=1.3, lean=10)
    S.face(ch, 0.0, "blij", 0.6)
# 19b: twee fietsers rijden langs het bord BIKES ONLY
B_SIGN = V(0.0, 18.0, 0)
for k, (n, x, col) in enumerate((("figurant_b", -1.3, (0.2, 0.6, 0.6)), ("kind_b", 1.2, (0.9, 0.4, 0.6)))):
    ch = S.actor(n, V(x, 8.0, 0), 180, label=f"fietser_b{k}")
    _, crank = bike(S, ch, color=col, name=f"Fiets_bord_{k}")
    ride_path(S, ch, crank, t_b - 0.6 + 0.5 * k, t_c + 0.2, [V(x, 6.0 - 2 * k, 0), V(x, 24.0, 0)], cadence=1.3, lean=8)
    S.face(ch, t_b, "lach", 0.6)

# ---------------------------------------------------------------- 19b: het bord en de auto die omkeert
sign_b = ST3.sign("Bord_BIKES_ONLY_wijk", ["BIKES ONLY"], tuple(B_SIGN), rot_z=-26, w=1.4, h=0.5, bg=(0.15, 0.45, 0.25),
                  fg=(1, 1, 1), post_h=1.3, marker=True)
car = S.obj("Auto_rijdt")
car.rotation_mode = "XYZ"
R = 2.6
C = V(0.0, 14.2, 0)
T_STOP0, T_STOP1 = t_b + 1.1, t_b + 1.5
T_TURN1 = t_c + 0.3
for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    if t < T_STOP0:
        u = (t - (t_b - 1.2)) / (T_STOP0 - (t_b - 1.2))
        u = max(0.0, min(1.0, u))
        u = 1 - (1 - u) ** 2
        loc, head = V(R, 3.0, 0).lerp(V(R, 14.2, 0), u), V(0, 1, 0)
    elif t < T_STOP1:
        loc, head = V(R, 14.2, 0), V(0, 1, 0)
    else:
        u = min(1.0, (t - T_STOP1) / (T_TURN1 - T_STOP1))
        u = u * u * (3 - 2 * u)
        a = math.pi * u
        loc = C + V(R * math.cos(a), R * math.sin(a) * 0.9, 0)
        head = V(-math.sin(a), math.cos(a), 0)
        if u >= 1.0:
            extra = (t - T_TURN1) * 4.0
            loc = C + V(-R, -extra, 0)
            head = V(0, -1, 0)
    car.location = loc
    car.rotation_euler = (0, 0, math.atan2(head.y, head.x) - math.pi)
    car.keyframe_insert("location", frame=f)
    car.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- 19c: NO MUSIC AFTER 10 PM, de radio gaat zachter
M_SIGN = V(-8.3, -15.0, 0.2)
ST3.sign("Bord_NO_MUSIC", ["NO MUSIC", "AFTER 10 PM"], tuple(M_SIGN), rot_z=28, w=1.1, h=0.6, bg=(0.95, 0.92, 0.8),
         fg=(0.12, 0.25, 0.65), post_h=1.2, marker=False)
STOEP = V(-9.0, -17.2, 0.2)
T.box("Krat_radio", tuple(STOEP + V(0.45, 0.0, 0)), (0.4, 0.35, 0.36), S.mat("plastic_krat_blauw", (0.15, 0.35, 0.75)), bevel=0.03, ol=0.004)
RB = STOEP + V(0.45, 0.0, 0.36)
radio = T.box("Radio_boombox", tuple(RB), (0.44, 0.16, 0.24), S.mat("radio_zilver", (0.72, 0.74, 0.78)), bevel=0.03, ol=0.004)
for sx in (-1, 1):
    T.cyl(f"Radio_speaker{sx}", (sx * 0.13, -0.085, 0.12), 0.075, 0.02, S.mat("radio_zwart", (0.06, 0.06, 0.07)), rot=(90, 0, 0), seg=16, ol=0.002).parent = radio
knob = T.cyl("Radio_knop", (0, -0.09, 0.19), 0.025, 0.03, S.mat("radio_rood", (0.85, 0.15, 0.1)), rot=(90, 0, 0), seg=12, ol=0.002)
knob.parent = radio
T.to_mesh(T.tube("Radio_hengsel", [(-0.15, 0, 0.24), (-0.12, 0, 0.32), (0.12, 0, 0.32), (0.15, 0, 0.24)], 0.012, S.mat("radio_zwart", (0.06, 0.06, 0.07)))).parent = radio
knob.rotation_mode = "XYZ"
T_KNOB0, T_KNOB1 = t_c + 1.2, t_c + 2.0
for t, a in ((0.0, 0), (T_KNOB0, 0), (T_KNOB1, -110)):
    knob.rotation_euler.y = math.radians(a)
    knob.keyframe_insert("rotation_euler", index=1, frame=F(t))
man = S.actor("buurman", RB + V(0.1, 0.58, -0.36), -10)
S.beat(man, t_c, "staan", face="blij", face_amt=0.6, at=RB + V(0, 0, 0.1), body={"spine": (8, 0, 0)})
S.beat(man, t_c + 0.6, "staan", face="twijfel", face_amt=0.6, at=M_SIGN + V(0, 0, 1.5))
S.beat(man, T_KNOB0 - 0.2, "staan", face="neutraal", face_amt=0.5, at=RB, body={"spine": (14, 0, 0)}, crouch=(0.06, 8))
S.reach(man, t_c, "R", inf=0.0)
S.reach(man, T_KNOB0 - 0.3, "R", RB + V(0.0, -0.05, 0.3))
S.reach(man, T_KNOB1, "R", RB + V(0.0, -0.05, 0.3))
S.reach(man, T_KNOB1 + 0.4, "R", inf=0.0)
S.beat(man, T_KNOB1 + 0.3, "staan", face="blij", face_amt=0.5, at=M_SIGN + V(0, 0, 1.5))
S.hold(man, END)
S.reach(man, 0.0, "R", inf=0.0)

# ---------------------------------------------------------------- camera's
S.black(0.0, CARD, "5 YEARS LATER")
S.cam(0.0, ((2.0, -66.0, 58.0), (0.0, 6.0, 0.0), 24))
# 19a WIDE drone: over de daken met zonnepanelen naar het kruispunt
S.cam(t_a, ((2.0, -66.0, 58.0), (0.0, 6.0, 0.0), 24), ((1.0, -46.0, 40.0), (0.0, 8.0, 0.0), 24))
# 19b MEDIUM: het bord BIKES ONLY, de auto keert
S.cam(t_b, ((-4.6, 8.4, 1.5), (0.8, 16.5, 1.1), 28), ((-4.4, 8.8, 1.5), (0.8, 16.5, 1.1), 29))
# 19c MEDIUM: de man met de radio en het bord
S.cam(t_c, ((-6.2, -19.4, 1.45), (-8.5, -16.2, 1.0), 28), ((-6.4, -19.1, 1.42), (-8.5, -16.2, 1.0), 30))

# ---------------------------------------------------------------- HUD, geluid, stem
S.counter("YEAR 5", 6300, t0=t_a)
S.sfx("sfx_whoosh", 0.0, 0.3)
S.ambience("sfx_stad_dag", t_a, END, vol=0.14)
S.sfx("sfx_fiets_bus", t_a + 0.5, 0.12)
S.sfx("sfx_remmen", T_STOP0 - 0.3, 0.15)
S.sfx("sfx_radio_ruis", t_c, 0.25, keys=[(t_c, 0.25), (T_KNOB0, 0.25), (T_KNOB1, 0.03)])
S.music("strijkers_warm", t_a, END, vol=0.16, fade_in=0.5, fade_out=0.5)
S.say("N19-01", at=t_a + 0.4)
S.say("N19-02", at=t_b + 1.6)
S.finish(length=END, tail=0.0)
