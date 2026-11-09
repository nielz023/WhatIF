# Cartoon-gevecht: de pestkop haalt uit, Bram duikt weg, geeft een duw, de pestkop valt op zijn billen,
# Bram juicht... en helpt hem daarna overeind.
#   blender -b --disable-autoexec <glans_hoofdpersonage_volledig.blend> -P vecht_bram.py -- <stills|anim> <uitvoermap>
import bpy, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene_lib as L
from scene_lib import R, key, rot_keys, curve, smoothstep

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "stills"
OUT = argv[1] if len(argv) > 1 else os.path.join(HERE, "render_vecht")
random.seed(3)

scene, buiten = L.setup({"hoofdpersonage", "pestkop"})
bram = L.rig_bram()
pest = L.rig_named("pestkop")
L.build_outdoor(buiten)
cam, aim = L.camera(buiten, lens=40, fstop=4.0, focus_parent=None)
cam.data.dof.focus_distance = 5.0

END = 184
B, P = bram, pest
BN, PN = 1, -1            # arm aan de camerakant: Bram +x, pestkop -x


def guard(rig, f, near):
    for s in (-1, 1):
        rot_keys(rig.sh[s], [(f, (-30, -s * 12, 0))])
        rot_keys(rig.el[s], [(f, (-115, 0, 0))])


def neutral_legs(rig, f):
    for s in (-1, 1):
        rot_keys(rig.hip[s], [(f, (0, 0, 0))])


# ---------------------------------------------------------------- posities
key(B.char, "rotation_euler", 1, (0, 0, R(-90)))
key(P.char, "rotation_euler", 1, (0, 0, R(90)))
for f, x in ((1, 0.6), (60, 0.6), (64, 0.48), (66, 0.42), (132, 0.42), (150, -0.2), (END, -0.2)):
    key(B.char, "location", f, Vector((x, 0, 0)))
for f, x in ((1, -0.45), (38, -0.45), (43, -0.27), (50, -0.2), (58, -0.3), (66, -0.3), (72, -0.95),
             (80, -1.45), (END, -1.45)):
    key(P.char, "location", f, Vector((x, 0, 0)))

# ---------------------------------------------------------------- 1-30: tegenover elkaar, vuisten omhoog
for rig in (B, P):
    guard(rig, 1, None)
    guard(rig, 30, None)
    neutral_legs(rig, 1)
    L.brow_keys(rig, 1, -0.004, 14)
    L.brow_keys(rig, 30, -0.005, 16)
L.mouth_keys(B, 1, Boos=1.0, Lach=0.0, E=0.0, X=0.0, Schreeuw=0.0)
L.mouth_keys(B, 30, Boos=1.0, Lach=0.0, E=0.0)

# heen-en-weer veren (per frame), daarna overschreven door de actie
for f in range(1, 31):
    key(B.mover, "location", f, Vector((0, 0, -0.012 * (0.5 - 0.5 * math.cos(2 * math.pi * f / 12)))))
    key(P.mover, "location", f, Vector((0, 0, -0.012 * (0.5 - 0.5 * math.cos(2 * math.pi * (f + 6) / 12)))))

# ---------------------------------------------------------------- 30-58: pestkop slaat, Bram duikt weg
rot_keys(P.sh[PN], [(38, (35, 6, 0)), (43, (-92, 0, 0)), (50, (-70, 0, 0)), (58, (-30, 12, 0)), (66, (-30, 12, 0))])
rot_keys(P.el[PN], [(38, (-95, 0, 0)), (43, (-4, 0, 0)), (50, (-20, 0, 0)), (58, (-115, 0, 0)), (66, (-115, 0, 0))])
rot_keys(P.sh[-PN], [(43, (-30, -12, 0)), (48, (-10, -60, 0)), (54, (-20, -30, 0)), (58, (-30, -12, 0)),
                     (66, (-30, -12, 0))])
rot_keys(P.root, [(1, (0, 0, 0)), (30, (0, 0, 0)), (38, (-6, 0, 0)), (43, (14, 0, 0)), (50, (24, 0, 0)),
                  (58, (2, 0, 0)), (66, (2, 0, 0))])
rot_keys(P.hip[PN], [(43, (0, 0, 0)), (47, (-26, 0, 0)), (52, (0, 0, 0))])
key(P.mover, "location", 31, Vector((0, 0, 0)))
key(P.mover, "location", 66, Vector((0, 0, 0)))
L.brow_keys(P, 50, 0.004, 4)
L.brow_keys(P, 58, -0.006, 18)

rot_keys(B.root, [(1, (0, 0, 0)), (34, (0, 0, 0)), (40, (-30, 0, 0)), (46, (-28, 0, 0)), (53, (0, 0, 0))])
key(B.mover, "location", 31, Vector((0, 0, 0)))
key(B.mover, "location", 40, Vector((0, 0, -0.05)))
key(B.mover, "location", 53, Vector((0, 0, 0)))
rot_keys(B.head, [(1, (0, 0, 0)), (34, (0, 0, 0)), (40, (-10, 0, 0)), (50, (-4, 0, 0)), (56, (0, 0, 0))])
for s in (-1, 1):
    rot_keys(B.sh[s], [(36, (-30, -s * 12, 0)), (41, (-15, -s * 30, 0)), (52, (-30, -s * 12, 0))])
L.brow_keys(B, 36, 0.016, -12)
L.mouth_keys(B, 36, Boos=0.0, E=1.0, Lach=0.0)
L.brow_keys(B, 50, 0.0, 10)
L.mouth_keys(B, 50, Boos=0.0, E=0.0, Lach=0.7)

# ---------------------------------------------------------------- 56-80: Bram duwt, pestkop vliegt achteruit
for s in (-1, 1):
    rot_keys(B.sh[s], [(56, (-30, -s * 12, 0)), (61, (28, -s * 8, 0)), (65, (-90, -s * 4, 0)),
                       (70, (-80, -s * 4, 0)), (78, (-20, -s * 8, 0))])
    rot_keys(B.el[s], [(56, (-115, 0, 0)), (61, (-90, 0, 0)), (65, (-8, 0, 0)), (70, (-12, 0, 0)),
                       (78, (-60, 0, 0))])
rot_keys(B.root, [(56, (0, 0, 0)), (61, (-7, 0, 0)), (65, (16, 0, 0)), (68, (19, 0, 0)), (76, (3, 0, 0))])
rot_keys(B.hip[BN], [(59, (0, 0, 0)), (63, (-24, 0, 0)), (68, (0, 0, 0))])
L.mouth_keys(B, 58, Lach=0.0, Boos=0.4, Schreeuw=0.0)
L.mouth_keys(B, 64, Boos=0.0, Schreeuw=1.0)
L.mouth_keys(B, 72, Schreeuw=0.0, E=0.0)
L.brow_keys(B, 60, -0.006, 18)

# pestkop vliegt: boog, kantelt achterover, landt zittend
for f, z in ((66, 0.0), (72, 0.22), (77, 0.0), (80, -0.62), (83, -0.6), (END, -0.6)):
    key(P.mover, "location", f, Vector((0, 0, z)))
rot_keys(P.mover, [(66, (0, 0, 0)), (71, (-28, 0, 0)), (77, (-18, 0, 0)), (80, (0, 0, 0)), (END, (0, 0, 0))])
for s in (-1, 1):
    rot_keys(P.hip[s], [(66, (0, 0, 0)), (72, (-55, 0, 0)), (79, (-88, 0, 0)), (END, (-86, 0, 0))])
    rot_keys(P.sh[s], [(66, (-30, -s * 12, 0)), (70, (-60, -s * 70, 0)), (76, (-20, -s * 40, 0)),
                       (80, (38, -s * 10, 0)), (150, (38, -s * 10, 0))])
    rot_keys(P.el[s], [(66, (-115, 0, 0)), (70, (-20, 0, 0)), (80, (-8, 0, 0)), (150, (-8, 0, 0))])
rot_keys(P.root, [(66, (2, 0, 0)), (70, (-20, 0, 0)), (80, (-14, 0, 0)), (END, (-12, 0, 0))])
for f, sxy, sz in ((66, 1, 1), (68, 0.9, 1.12), (79, 1, 1), (80, 1.14, 0.84), (84, 0.97, 1.04), (88, 1, 1)):
    key(P.root, "scale", f, Vector((sxy, sxy, sz)))
L.brow_keys(P, 68, 0.016, -16)
L.brow_keys(P, 90, 0.008, -10)

# duizelig: hoofd wiebelt na de landing
for f in range(84, END + 1):
    t = f - 84
    decay = math.exp(-t / 45)
    look_up = smoothstep(150, 160, f)
    key(P.head, "rotation_euler", f, (R(-14 * look_up), R(10 * decay * math.sin(2 * math.pi * t / 16)),
                                      R(9 * decay * math.cos(2 * math.pi * t / 16))))
key(P.head, "rotation_euler", 83, (0, 0, 0))
L.blink_bake(P, [20, 150, 170], END, base=[(1, 1.0), (66, 1.0), (70, 1.3), (82, 1.2), (88, 0.55),
                                           (140, 0.6), (154, 1.0), (END, 1.0)])

# ---------------------------------------------------------------- 74-130: Bram verbaasd, dan juichen
rot_keys(B.head, [(74, (0, 0, 0)), (82, (16, 0, 0)), (96, (14, 0, 0)), (102, (-4, 0, 0)), (110, (-10, 0, 0)),
                  (128, (-6, 0, 0))])
for s in (-1, 1):
    rot_keys(B.sh[s], [(82, (-28, -s * 6, 0)), (96, (-26, -s * 8, 0)), (102, (0, -s * 30, 0)),
                       (110, (0, -s * 128, 0)), (114, (0, -s * 112, 0)), (128, (0, -s * 118, 0)),
                       (134, (0, -s * 4, 0))])
    rot_keys(B.el[s], [(82, (-100, 0, 0)), (96, (-104, 0, 0)), (102, (-30, 0, 0)), (110, (0, -s * 22, 0)),
                       (128, (0, -s * 18, 0)), (134, (-12, 0, 0))])
L.brow_keys(B, 80, 0.018, -10)
L.mouth_keys(B, 80, E=0.9, Lach=0.0, Boos=0.0)
L.brow_keys(B, 98, 0.018, -8)
L.mouth_keys(B, 98, E=0.0, Lach=1.0, X=0.7)
for f, z in ((96, 0.0), (104, -0.045), (110, 0.18), (116, 0.0), (120, 0.0)):
    key(B.mover, "location", f, Vector((0, 0, z)))
for f, sxy, sz in ((96, 1, 1), (104, 1.04, 0.95), (108, 0.97, 1.05), (116, 1.07, 0.92), (121, 1, 1)):
    key(B.root, "scale", f, Vector((sxy, sxy, sz)))

# ---------------------------------------------------------------- 132-184: Bram loopt naar hem toe en helpt hem
for i, (fa, s) in enumerate(((132, BN), (138, -BN), (144, BN))):
    rot_keys(B.hip[s], [(fa, (0, 0, 0)), (fa + 3, (-22, 0, 0)), (fa + 6, (0, 0, 0))])
    rot_keys(B.hip[-s], [(fa, (0, 0, 0)), (fa + 3, (10, 0, 0)), (fa + 6, (0, 0, 0))])
    key(B.mover, "location", fa, Vector((0, 0, 0)))
    key(B.mover, "location", fa + 3, Vector((0, 0, 0.02)))
    key(B.mover, "location", fa + 6, Vector((0, 0, 0)))
rot_keys(B.sh[BN], [(150, (-6, -4, 0)), (158, (-58, -6, 0)), (END, (-56, -6, 0))])
rot_keys(B.el[BN], [(150, (-14, 0, 0)), (158, (-14, 0, 0)), (END, (-12, 0, 0))])
rot_keys(B.root, [(150, (3, 0, 0)), (158, (14, 0, 0)), (END, (13, 0, 0))])
rot_keys(B.head, [(150, (-2, 0, 0)), (158, (14, 0, 0)), (END, (12, 0, 0))])
L.brow_keys(B, 150, 0.006, -6)
L.mouth_keys(B, 150, Lach=0.85, X=0.0)
L.mouth_keys(B, END, Lach=0.85, X=0.0)
L.brow_keys(B, END, 0.006, -6)
L.blink_bake(B, [24, 88, 148], END, base=[(1, 1.0), (36, 1.0), (40, 1.2), (52, 1.0), (78, 1.0), (84, 1.18),
                                          (98, 0.85), (128, 0.85), (140, 1.0), (END, 1.0)])

# pestkop pakt de hand
rot_keys(P.sh[-PN], [(150, (38, 10, 0)), (164, (-70, 4, 0)), (END, (-68, 4, 0))])
rot_keys(P.el[-PN], [(150, (-8, 0, 0)), (164, (-18, 0, 0)), (END, (-16, 0, 0))])
L.brow_keys(P, 154, 0.006, -4)
L.brow_keys(P, END, 0.006, -4)

# ---------------------------------------------------------------- camera (met schok bij de klappen)
for f in range(1, END + 1):
    cx = curve([(1, 0.1), (64, 0.05), (82, -0.45), (130, -0.4), (160, -0.6), (END, -0.65)], f)
    cy = curve([(1, -5.2), (60, -4.9), (90, -5.4), (END, -4.8)], f)
    ax = curve([(1, 0.05), (64, 0.05), (82, -0.5), (130, -0.45), (160, -0.75), (END, -0.8)], f)
    az = curve([(1, 1.0), (64, 1.0), (84, 0.8), (130, 0.85), (END, 0.8)], f)
    shake = 0.0
    for hit, strength in ((66, 0.04), (80, 0.06)):
        if hit <= f < hit + 9:
            shake = strength * (1 - (f - hit) / 9)
    key(cam, "location", f, Vector((cx + random.uniform(-shake, shake), cy, 1.05 + random.uniform(-shake, shake))))
    key(aim, "location", f, Vector((ax, 0, az)))
cam.data.dof.focus_distance = 5.0

L.render_settings(samples=28)
L.run(MODE, OUT, os.path.join(HERE, "bram_vecht.blend"), (20, 42, 66, 76, 112, 175), END)
