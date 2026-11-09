"""
Glans-look, volledige figuur (top tot teen) van één castlid, staand formaat.
Gebruik:
    blender -b -P cast/render_glans_volledig.py -- --fig hoofdpersonage --out pad/map
Opties: --blend pad  --samples 160  --pct 100  --no-render (alleen .blend opslaan)
Schrijft glans_<fig>_volledig.png en glans_<fig>_volledig.blend (scène klaar om te renderen).
"""
import os
import sys
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_glans as rg  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    o = {"--blend": "/mnt/project-files/cast/cast_video1.blend", "--fig": "hoofdpersonage",
         "--out": "/mnt/project-files/cast/glans", "--samples": "160", "--pct": "100"}
    flags = set()
    i = 0
    while i < len(argv):
        if argv[i] in o:
            o[argv[i]] = argv[i + 1]
            i += 2
        else:
            flags.add(argv[i])
            i += 1
    os.makedirs(o["--out"], exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=o["--blend"])
    sc = bpy.context.scene
    studio = rg.setup_look(int(o["--samples"]), int(o["--pct"]))
    cam = sc.camera
    for lc in bpy.context.view_layer.layer_collection.children["cast"].children:
        lc.exclude = True
    tmp = bpy.data.collections.new("glans_tmp")
    sc.collection.children.link(tmp)
    c = bpy.data.collections[o["--fig"]]
    rg.instance(c, (0, 0, 0), 0.0, tmp)

    pts = [o2.matrix_world @ Vector(b) for o2 in c.objects if o2.type == "MESH" for b in o2.bound_box]
    zmin = min(p.z for p in pts)
    zmax = max(p.z for p in pts)
    H = zmax - zmin
    zc = zmin + H * 0.5
    print("figuurhoogte", H, zmin, zmax)

    # licht iets breder en lager zodat benen en schoenen ook licht krijgen
    for ob in studio.objects:
        if ob.type == "LIGHT":
            ob.data.size *= 1.6
            ob.data.energy *= 1.3
    rg.area(studio, "vullicht_laag", 160, 2.5, (0.8, -3.6, 0.4), (0, 0, 0.5), "#FFE6CC")
    for ob in studio.objects:
        if ob.type == "LIGHT" and ob.name != "kruin":
            ob.light_linking.receiver_collection = tmp

    # staand kader, hele figuur met wat ruimte, licht van opzij zoals de close-up
    lens = 50
    dist = 0.67 * H / (18 / lens)
    rg.aim(cam, (dist * 0.25, -dist, zc - 0.02), (0, 0, zc - 0.07), lens=lens)
    cam.data.sensor_fit = "AUTO"
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 2400
    base = os.path.join(o["--out"], f"glans_{o['--fig']}_volledig")
    bpy.ops.wm.save_as_mainfile(filepath=base + ".blend", compress=True)
    if "--no-render" not in flags:
        rg.render(base + ".png", 1600, 2400)


if __name__ == "__main__":
    main()
