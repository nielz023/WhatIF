"""
Testclip van 5 seconden in de glans-look: het hoofdpersonage springt van blijdschap,
zijn beste vriend zwaait. Gebruikt cast_video1.blend en cast/render_glans.py.

    python anim_test/glans_test.py --out pad/uitvoer [--frames 1,60] [--samples 24] [--pct 100]
Zonder --frames rendert hij alle 120 beelden en maakt er glans_test.mp4 van.
"""
import bpy
import math
import os
import sys
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import render_glans as RG  # noqa: E402

FPS = 24
END = 5 * FPS


def arg(name, default):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def group(root, names):
    """Bovenste objecten (direct onder root) van een lichaamsdeel."""
    tops = set()
    for ob in root.children_recursive:
        if ob.name.rsplit("_", 1)[-1] in names or any(ob.name.endswith(n) for n in names):
            top = ob
            while top.parent is not None and top.parent != root:
                top = top.parent
            tops.add(top)
    return list(tops)


def pivot(root, name, objs, loc):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    root.users_collection[0].objects.link(e)
    e.parent = root
    e.matrix_world = Matrix.Translation(loc) @ root.matrix_world.to_3x3().to_4x4()
    bpy.context.view_layer.update()
    for ob in objs:
        mw = ob.matrix_world.copy()
        ob.parent = e
        ob.matrix_world = mw
    return e


def top_of(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    zmax = max(p.z for p in pts)
    top = [p for p in pts if p.z > zmax - 0.05]
    return sum(top, Vector()) / len(top)


def key(ob, path, frame, value, idx=None):
    if idx is None:
        setattr(ob, path, value)
        ob.keyframe_insert(path, frame=frame)
    else:
        getattr(ob, path)[idx] = value
        ob.keyframe_insert(path, index=idx, frame=frame)


def ease_all():
    for ob in bpy.data.objects:
        ad = ob.animation_data
        if ad and ad.action:
            for fc in getattr(ad.action, "fcurves", []):
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.easing = "AUTO"


def rig_figure(root, prefix_hero):
    """Draaipunten voor beide armen en het hoofd."""
    if prefix_hero:
        arm = {-1: [f"part_{i}" for i in (13, 14, 15, 16)] + ["Node_20"],
               +1: [f"part_{i}" for i in (20, 21, 22, 23)] + ["Node_28"]}
        head = [f"part_{i}" for i in range(28, 55)]
    else:
        lab = ("bovenarm", "onderarm", "elleboog", "manchet", "hand", "duim", "vingers", "mouwzoom")
        arm = {-1: [f"{l}_R" for l in lab] + ["telefoon", "telefoon_scherm"],
               +1: [f"{l}_L" for l in lab]}
        head = ["hoofd", "oor_R", "oor_L", "oor_R_binnen", "oor_L_binnen", "mond", "tong", "haar"] + \
               [n for n in ("oog", "wenkbrauw", "krul", "wimper", "sproet", "blos")]
    piv = {}
    for side, names in arm.items():
        objs = [o for o in root.children_recursive if any(o.name.endswith(n) for n in names)]
        objs = [o for o in objs if o.parent == root or o.parent.name.endswith(("Node_20", "Node_28"))]
        tops = []
        for o in objs:
            t = o
            while t.parent is not None and t.parent != root:
                t = t.parent
            if t not in tops:
                tops.append(t)
        p = top_of([o for o in tops if o.type == "MESH"])
        piv[side] = pivot(root, f"{root.name}_schouder_{side}", tops, p - Vector((0, 0, 0.04)))
    hobjs = []
    for o in root.children:
        n = o.name
        if any(("_" + h) in n for h in head) and o.type == "MESH" and "schouder" not in n:
            hobjs.append(o)
    hz = min((o.matrix_world @ Vector(c)).z for o in hobjs if o.name.endswith(("hoofd", "part_28"))
             for c in o.bound_box)
    piv[0] = pivot(root, f"{root.name}_nek", hobjs, Vector((0, 0, hz + 0.02)))
    return piv


def main():
    out = arg("--out", "/tmp/glans_test")
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=arg("--blend", "/mnt/project-files/cast/cast_video1.blend"))
    sc = bpy.context.scene
    studio = RG.setup_look(int(arg("--samples", "24")), int(arg("--pct", "100")))
    sc.render.use_persistent_data = True
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, END
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720

    vl = bpy.context.view_layer
    keep = ("hoofdpersonage", "beste_vriend")
    for lc in vl.layer_collection.children["cast"].children:
        lc.exclude = lc.name not in keep
    figs = bpy.data.collections.new("figuren")
    bpy.data.collections["cast"].children.link  # noqa
    for ob in studio.objects:
        if ob.type == "LIGHT" and ob.name != "kruin":
            ob.light_linking.receiver_collection = bpy.data.collections["cast"]

    hero = bpy.data.objects["hoofdpersonage"]
    friend = bpy.data.objects["beste_vriend"]
    hero.location = (-0.45, 0, 0)
    friend.location = (0.5, 0.15, 0)
    friend.rotation_euler = (0, 0, math.radians(18))
    bpy.context.view_layer.update()
    hp = rig_figure(hero, True)
    fp = rig_figure(friend, False)

    # --- hoofdpersonage: inzakken, springen met beide armen omhoog, landen -----
    f = lambda s: 1 + round(s * FPS)  # noqa: E731
    for t, z, sz in ((0, 0, 1), (0.9, 0, 1), (1.15, 0, 0.9), (1.35, 0.05, 1.06), (1.7, 0.55, 1.0),
                     (2.0, 0.05, 1.04), (2.1, 0, 0.88), (2.35, 0, 1.0), (5, 0, 1)):
        key(hero, "location", f(t), z, 2)
        key(hero, "scale", f(t), sz, 2)
        key(hero, "scale", f(t), 1 + (1 - sz) * 0.5, 0)
        key(hero, "scale", f(t), 1 + (1 - sz) * 0.5, 1)
    for side in (-1, +1):
        p = hp[side]
        for t, a in ((0, 0), (1.0, 0), (1.15, -10), (1.55, 165), (1.95, 160), (2.4, 20), (2.7, 0), (5, 0)):
            key(p, "rotation_euler", f(t), math.radians(a) * (1 if side < 0 else -1), 1)
    for t, a, b in ((0, 0, 0), (1.1, -8, 0), (1.7, 10, 0), (2.3, -6, 0), (2.8, 0, 6), (3.6, 0, -4),
                    (4.4, 3, 4), (5, 0, 0)):
        key(hp[0], "rotation_euler", f(t), math.radians(a), 0)
        key(hp[0], "rotation_euler", f(t), math.radians(b), 1)

    # --- beste vriend: lacht, kijkt naar hem en zwaait naar de camera -----------
    p = fp[+1]
    seq = [(0, 0), (2.3, 0), (2.7, -140)]
    t = 2.7
    for k in range(5):
        t += 0.22
        seq.append((t, -120 if k % 2 == 0 else -145))
    seq += [(t + 0.4, -140), (t + 0.8, 0), (5, 0)]
    for tt, a in seq:
        key(p, "rotation_euler", f(tt), math.radians(a), 1)
    for tt, a, b in ((0, 0, 0), (1.2, 0, -8), (2.2, 6, -10), (2.8, 0, 8), (4.0, 0, 10), (5, 0, 0)):
        key(fp[0], "rotation_euler", f(tt), math.radians(a), 0)
        key(fp[0], "rotation_euler", f(tt), math.radians(b), 1)
    for tt, z in ((0, 0), (2.5, 0), (2.7, 0.03), (2.9, 0), (3.1, 0.03), (3.3, 0), (5, 0)):
        key(friend, "location", f(tt), z, 2)

    # --- camera: langzame duw naar binnen met een klein boogje -----------------
    cam = sc.camera
    cam.data.lens = 38
    for tt, x, y, z in ((0, 0.9, -5.2, 1.45), (5, 0.25, -4.1, 1.3)):
        cam.location = (x, y, z)
        cam.rotation_euler = (Vector((0.0, 0, 1.12)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f(tt))
        cam.keyframe_insert("rotation_euler", frame=f(tt))
    ease_all()

    frames = arg("--frames", "")
    sc.render.image_settings.file_format = "PNG"
    if frames:
        for fr in [int(x) for x in frames.split(",")]:
            sc.frame_set(fr)
            sc.render.filepath = os.path.join(out, f"test_{fr:03d}.png")
            bpy.ops.render.render(write_still=True)
        return
    sc.render.filepath = os.path.join(out, "frames", "f_")
    bpy.ops.render.render(animation=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "glans_test.blend"))


if __name__ == "__main__":
    main()
