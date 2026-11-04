"""Overzicht van een set: camera's, markers en objecten met positie (voor het schrijven van scènescripts).

    python3 anim/v3/setinfo.py <set> <variant>      -> out/setinfo/<set>_<variant>.txt
"""
import os, re, sys, runpy
import bpy
from mathutils import Vector
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
set_name, variant = sys.argv[-2], sys.argv[-1]
os.environ["SET_RENDER"] = "0"
os.environ["SET_SAMPLES"] = "4"
out = os.path.join(REPO, "out", "setinfo")
os.makedirs(out, exist_ok=True)
sys.argv = [sys.argv[0], "--", variant, os.path.join(out, "tmp")]
runpy.run_path(os.path.join(REPO, "sets", f"build_{set_name}.py"))
bpy.context.view_layer.update()
L = []
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.type == "CAMERA":
        fw = o.matrix_world.to_3x3() @ Vector((0, 0, -1))
        L.append(f"CAM  {o.name:30s} loc {tuple(round(x, 2) for x in o.matrix_world.translation)} dir {tuple(round(x, 2) for x in fw)} lens {o.data.lens:.0f}")
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.type == "EMPTY" or o.name.startswith("MARK"):
        L.append(f"MARK {o.name:30s} {tuple(round(x, 2) for x in o.matrix_world.translation)}")
seen = {}
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.type in ("CAMERA",) or o.parent is not None:
        continue
    base = re.sub(r"(\.\d+|_\d+)$", "", o.name)
    seen.setdefault(base, []).append(o)
for base, obs in seen.items():
    o = obs[0]
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box] if o.type == "MESH" else [o.matrix_world.translation]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    L.append(f"{o.type[:4]} {base:34s} x{len(obs):<3d} at {tuple(round(x, 1) for x in o.matrix_world.translation)} bb {tuple(round(x, 1) for x in mn)}..{tuple(round(x, 1) for x in mx)}")
mats = sorted(m.name for m in bpy.data.materials)
L.append("MATS " + ", ".join(mats))
p = os.path.join(out, f"{set_name}_{variant}.txt")
open(p, "w").write("\n".join(L) + "\n")
print("SETINFO", p, len(L))
