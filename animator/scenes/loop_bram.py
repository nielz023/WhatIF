# Bram loopt over de richel, stopt, draait naar de camera en zwaait.
#   blender -b --disable-autoexec <glans_hoofdpersonage_volledig.blend> -P loop_bram.py -- <stills|anim> <uitvoermap>
import bpy, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene_lib as L
from scene_lib import R, key, curve, smoothstep

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "stills"
OUT = argv[1] if len(argv) > 1 else os.path.join(HERE, "render_loop")

scene, buiten = L.setup({"hoofdpersonage"})
bram = L.rig_bram()
L.build_outdoor(buiten)
cam, aim = L.camera(buiten, lens=45, fstop=2.8, focus_parent=bram.nod, focus_loc=(0, -0.3, 1.45))

END = 160
F0 = 8            # eerste stap
T = 20            # frames per looppas-cyclus (2 stappen)
TH = 22.0         # beenzwaai in graden
LEG = bram.leg_len
STOP = 112        # vanaf hier uitlopen


def amp(f):
    return smoothstep(F0, F0 + 10, f) * (1 - smoothstep(STOP - 6, STOP + 6, f))


def leg_angle(ph):
    """+ = been voor. Standfase lineair (voet blijft staan), zwaaifase vloeiend."""
    ph %= 1.0
    if ph < 0.5:
        return TH * (1 - 4 * ph), 0.0
    s = (ph - 0.5) / 0.5
    return -TH + 2 * TH * smoothstep(0, 1, s), math.sin(math.pi * s)


hip_rest = {s: bram.hip[s].location.copy() for s in (-1, 1)}
x = -1.7
xs = {}
for f in range(1, END + 1):
    a = amp(f)
    stride = 2 * LEG * math.sin(R(TH * a))
    x += stride / (T / 2)
    xs[f] = x

for f in range(1, END + 1):
    a = amp(f)
    ph = max(0.0, (f - F0) / T)
    ang, lift = {}, {}
    for s, off in ((-1, 0.0), (1, 0.5)):
        g, li = leg_angle(ph + off)
        ang[s], lift[s] = g * a, li * a
    stance = ang[-1] if lift[-1] == 0 else ang[1]

    # draaien naar de camera + twee stapjes na het stoppen
    yaw = curve([(1, 90), (122, 90), (138, 6), (END, 4)], f)
    turn_lift = {-1: 0.04 * math.sin(math.pi * smoothstep(122, 130, f)) if 122 <= f <= 130 else 0.0,
                 1: 0.04 * math.sin(math.pi * smoothstep(128, 136, f)) if 128 <= f <= 136 else 0.0}

    key(bram.char, "location", f, Vector((xs[f], 0, 0)))
    key(bram.char, "rotation_euler", f, (0, 0, R(yaw)))
    settle = -0.015 * math.sin(math.pi * smoothstep(STOP + 2, STOP + 12, f)) if STOP + 2 <= f <= STOP + 12 else 0.0
    key(bram.mover, "location", f, Vector((0, 0, -LEG * (1 - math.cos(R(stance))) + settle)))
    for s in (-1, 1):
        key(bram.hip[s], "rotation_euler", f, (R(-ang[s]), 0, 0))
        key(bram.hip[s], "location", f, hip_rest[s] + Vector((0, 0, 0.05 * lift[s] + turn_lift[s])))
        # armen zwaaien tegengesteld aan de benen
        sx = 1.1 * ang[s]
        el = -18 - 14 * max(0.0, -ang[s] / TH) * a
        wave = s == 1 and f >= 138
        if wave:
            sy = curve([(138, 0), (146, -118), (150, -104), (154, -110), (END, -108)], f)
            ey = curve([(138, 0), (146, -36), (149, -20), (152, -52), (155, -22), (158, -50), (END, -40)], f)
            key(bram.sh[s], "rotation_euler", f, (R(sx * (1 - smoothstep(138, 144, f))), R(sy), 0))
            key(bram.el[s], "rotation_euler", f, (R(el * (1 - smoothstep(138, 144, f))), R(ey), 0))
        else:
            key(bram.sh[s], "rotation_euler", f, (R(sx), R(-s * 3), 0))
            key(bram.el[s], "rotation_euler", f, (R(el), 0, 0))

    cyc = 2 * math.pi * ph
    key(bram.root, "rotation_euler", f, (R(4 * a), 0, R(4 * a * math.sin(cyc))))
    key(bram.root, "location", f, Vector((0, 0, 0.64 + 0.008 * a * abs(math.sin(cyc)))))
    head_z = curve([(1, -16), (122, -16), (138, 0), (END, 0)], f)
    head_x = curve([(1, 0), (138, 0), (146, -6), (END, -4)], f)
    key(bram.head, "rotation_euler", f, (R(head_x), R(curve([(1, 0), (140, 0), (148, 6), (END, 5)], f)), R(head_z)))
    key(bram.nod, "rotation_euler", f, (R(-2.0 * a * math.sin(2 * cyc)), 0, 0))

    # camera volgt Bram
    k = smoothstep(108, END, f)
    key(cam, "location", f, Vector((xs[f] + 1.5 - 0.6 * k, -5.6 + 1.2 * k, 0.95)))
    key(aim, "location", f, Vector((xs[f] + 0.15, 0, 1.0 + 0.1 * k)))

L.mouth_keys(bram, 1, Lach=0.75, X=0.0)
L.mouth_keys(bram, 136, Lach=0.8, X=0.0)
L.mouth_keys(bram, 144, Lach=1.0, X=0.7)
L.mouth_keys(bram, END, Lach=1.0, X=0.6)
L.brow_keys(bram, 1, 0.0, 0)
L.brow_keys(bram, 136, 0.0, 0)
L.brow_keys(bram, 145, 0.018, -6)
L.brow_keys(bram, END, 0.016, -5)
L.blink_bake(bram, [40, 98, 152], END, base=[(1, 1.0), (138, 1.0), (146, 0.85), (END, 0.85)])

L.render_settings(samples=28)
L.run(MODE, OUT, os.path.join(HERE, "bram_loopt.blend"), (20, 60, 118, 150), END)
