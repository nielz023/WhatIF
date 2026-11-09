# Losse render van de mok "WORLD'S OKAYEST MOM" uit video 1 (toon-look), helemaal in beeld.
# Gebruik: SET_LOOK=toon SET_SAMPLES=64 python3 render_mok_okayest.py <0|1 gebarsten> <uit.png>
# Verwacht sets/lib/toon.py naast dit script (map sets/).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sets"))
import bpy
from lib import toon as T
cracked = sys.argv[-2] == "1"
out = sys.argv[-1]
T.new_scene("mok", T.MOODS["binnen"], samples=int(os.environ.get("SET_SAMPLES", 32)))
mats = {}
def M(n, c):
    if n not in mats: mats[n] = T.toon(n, c)
    return mats[n]
# aanrecht en muur (kleuren zoals in de keuken van video 1)
T.box("aanrecht", (0, 0.2, -0.04), (1.6, 1.2, 0.04), M("aanrecht", (0.62, 0.66, 0.78)), bevel=0.0, ol=0)
T.box("muur", (0, 0.55, -0.04), (3, 0.02, 1.5), M("muur", (0.78, 0.74, 0.76)), bevel=0.0, ol=0)
white = M("mok_wit", (0.95, 0.94, 0.9)); red = M("mok_rood", (0.85, 0.15, 0.15))
body = T.cyl("Mok", (0, 0, 0), 0.042, 0.095, white, seg=48, ol=0.0025)
inner = T.cyl("Mok_thee", (0, 0, 0.07), 0.037, 0.005, M("thee", (0.55, 0.3, 0.12)), seg=40, ol=0)
txt = T.text("Mok_tekst", "WORLD'S\nOKAYEST\nMOM", (0, -0.0425, 0.03), 0.014, red, rot=(90, 0, 0), extrude=0.0)
h = T.torus("Mok_oor", (0.048, 0, 0.048), 0.022, 0.006, white, rot=(90, 0, 0), seg=32, seg2=12, ol=0.0025)
if cracked:
    T.tube("Mok_barst", [(-0.02, -0.0428, 0.085), (-0.005, -0.0428, 0.06), (-0.012, -0.0428, 0.045),
                          (0.004, -0.0428, 0.03), (-0.002, -0.0428, 0.008)], 0.0012, M("barst", (0.15, 0.12, 0.1)))
ink = M("lijn", (0.025, 0.018, 0.035))
T.torus("Mok_rand_onder", (0, 0, 0.0015), 0.0425, 0.0016, ink, seg=64, seg2=8, ol=0)
T.torus("Mok_rand_boven", (0, 0, 0.095), 0.0425, 0.0014, ink, seg=64, seg2=8, ol=0)
cam = T.camera("Cam", (0.03, -0.50, 0.21), (0.012, 0, 0.046), lens=60)
cam.data.dof.use_dof = False
bpy.context.scene.camera = cam
sc = bpy.context.scene
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
