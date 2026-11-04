"""N09a · Dag 3: niemand gaat meer werken (script scène 9a). Lege bushalte, grijze ochtend.
Het display springt van "LINE 4 · 2 MIN" naar "LINE 4 · ---". Vuilniszakken stapelen zich op naast het bushokje.
VO: "Why would you go to work, if nobody pays you, and nobody can fire you?"

    blender -b -P anim/v3/scenes/n09a_bushalte.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n09a", "straat", "grijs", exposure=0.0)
sh = S.cuts([5.2])
END = sh[-1][1]
rnd = random.Random(9)

# video 2-dingen uit de grijze variant weg
for o in list(bpy.data.objects):
    if o.name.startswith(("Vuilniswagen", "Kraai", "Plastic_zak", "Raamtekst", "Koplamp")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- het display onder het dak van het bushokje
DSP = V(23.3, 6.86, 2.22)
T.box("Busdisplay_kast", tuple(DSP + V(0, 0, -0.14)), (1.5, 0.08, 0.36), S.mat("display_zwart", (0.03, 0.03, 0.04)), bevel=0.01, ol=0.004)
for x in (-0.6, 0.6):
    T.box(f"Busdisplay_ophanging_{x}", tuple(DSP + V(x, 0, 0.12)), (0.03, 0.03, 0.18), S.mat("metaal_donker", (0.2, 0.2, 0.22)), bevel=0, ol=0)
AMBER = (1.0, 0.55, 0.08)
T_SW = 1.1
old = ST3.label("Busdisplay_2min", "LINE 4 · 2 MIN", DSP + V(0, -0.045, -0.06), 0.15, col=AMBER, glow=4.0)
new = ST3.label("Busdisplay_streep", "LINE 4 · ---", DSP + V(0, -0.045, -0.06), 0.15, col=AMBER, glow=4.0)
for o, keys in ((old, ((0.0, True), (T_SW, False))), (new, ((0.0, False), (T_SW, True)))):
    for t, vis in keys:
        o.hide_render = not vis
        o.hide_viewport = not vis
        o.keyframe_insert("hide_render", frame=F(t))
        o.keyframe_insert("hide_viewport", frame=F(t))
# het "---" knippert twee keer na de sprong
for t, vis in ((T_SW + 0.25, False), (T_SW + 0.4, True), (T_SW + 0.65, False), (T_SW + 0.8, True)):
    new.hide_render = not vis
    new.keyframe_insert("hide_render", frame=F(t))
for o in (old, new):
    for fc in A._fcurves(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"

# ---------------------------------------------------------------- vuilniszakken naast het bushokje (op de stoep, niet erdoorheen)
BAG = [S.mat("vuilniszak_zwart", (0.05, 0.06, 0.07)), S.mat("vuilniszak_groen", (0.10, 0.22, 0.12))]
for k in range(9):
    row = 0 if k < 6 else 1
    i = k if row == 0 else k - 6
    x = 26.35 + (i % 3) * 0.55 + rnd.uniform(-0.06, 0.06) + 0.25 * row
    y = 7.55 + (i // 3) * 0.55 + rnd.uniform(-0.05, 0.05)
    r = 0.3 + rnd.uniform(-0.03, 0.04)
    z = 0.12 + r * 0.8 + row * 0.42
    b = T.sphere(f"Vuilniszak_{k}", (x, y, z), r, BAG[k % 3 == 2], scale=(1.0, 0.92, 0.8), seg=14, ol=0.008)
    b.rotation_euler = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 3))
    T.cyl(f"Vuilniszak_knoop_{k}", (x, y, z + r * 0.8), 0.05, 0.12, BAG[k % 3 == 2], seg=8, ol=0.004)

# ---------------------------------------------------------------- camera: statisch met trage drift
S.cam(0.0, ((20.6, 3.9, 1.45), (24.6, 7.4, 1.75), 24), ((20.9, 4.2, 1.45), (24.7, 7.4, 1.8), 25), handheld=0.08)

S.counter("DAY 3", 0, t0=0.0)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.03)
S.sfx("sfx_stad_nacht_wind", 0.0, 0.06, loop_to=END)
S.say("N09-01", at=0.3)
S.finish(length=END, tail=0.0)
