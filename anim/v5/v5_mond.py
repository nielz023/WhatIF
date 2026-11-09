"""Praatmond (12 vormen, tanden, tong) voor benoemde personages, naar het voorbeeld van scene_lib._bram_face.
Gebruik na rig = L.rig_named(cname):  v5_mond.face_named(rig, cname)
Daarna werken L.lipsync(rig, ...), L.emotion(...) en mouth_keys gewoon, net als bij Bram."""
import math
import bpy
from mathutils import Vector
import scene_lib as L

O = bpy.data.objects


def _bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def face_named(rig, cname):
    coll = bpy.data.collections[cname]
    head = O[f"{cname}_hoofd"]
    mn, mx = _bbox([head])
    hc = (mn + mx) / 2
    hr = max(mx.x - mn.x, mx.z - mn.z) / 2
    old = [o for o in coll.objects if o.name.startswith((f"{cname}_mond", f"{cname}_tong"))]
    if old:
        omn, omx = _bbox(old)
        mz = (omn.z + omx.z) / 2
        mx_ = (omn.x + omx.x) / 2
    else:
        mz, mx_ = hc.z - 0.29 * hr, hc.x
    k = hr / 0.3
    saved = (L.HC, L.HR, L.MZ, L._surf)

    def surf(u, v, off):
        z = mz + v
        dz = z - hc.z
        y = hc.y - math.sqrt(max((hr + off) ** 2 - u * u - dz * dz, 1e-6))
        return Vector((u + mx_, y, z))

    L.HC, L.HR, L.MZ, L._surf = hc, hr, mz, surf
    try:
        vis = {n: {a: (b * k if a in ("w", "uh", "lh", "corner", "teeth") else b) for a, b in p.items()}
               for n, p in L.VIS.items()}
        NC, NR = L.NC, L.NR

        def grid(base, cols, rows, mat):
            fs = []
            for i in range(cols):
                for j in range(rows):
                    a = base + i * (rows + 1) + j
                    b = base + (i + 1) * (rows + 1) + j
                    fs.append(((a, b, b + 1, a + 1), mat))
            return fs

        n_int = (NC + 1) * (NR + 1)
        n_band = (NC + 1) * 2
        faces = grid(0, NC, NR, 0) + grid(n_int, NC, 1, 1) + grid(n_int + n_band, NC, 1, 2)
        me = bpy.data.meshes.new(f"{cname}_Mond")
        me.from_pydata([tuple(v) for v in L._gen(vis["A"])], [], [f for f, _ in faces])
        for poly, (_, m) in zip(me.polygons, faces):
            poly.material_index = m
            poly.use_smooth = True
        mouth = bpy.data.objects.new(f"{cname}_Mond", me)
        coll.objects.link(mouth)
        inner = old[0].data.materials[0] if old and old[0].data.materials else L.material(f"{cname}_mondbinnen", (70, 25, 30), rough=0.5)
        tong = next((o for o in old if "tong" in o.name and o.data.materials), None)
        me.materials.append(inner)
        me.materials.append(L.material(f"{cname}_Tanden", (250, 250, 246), rough=0.25, coat=0.5))
        me.materials.append(tong.data.materials[0] if tong else L.material(f"{cname}_Tong", (215, 95, 100), rough=0.45))
        mouth.shape_key_add(name="Basis", from_mix=False)
        rig.mouth_shapes = {}
        for name, p in vis.items():
            if name == "A":
                continue
            sk = mouth.shape_key_add(name=name, from_mix=False)
            for i, v in enumerate(L._gen(p)):
                sk.data[i].co = v
            sk.slider_min, sk.slider_max = 0.0, 1.2
            sk.value = 0.0
            rig.mouth_shapes[name] = sk
        L.reparent(mouth, rig.nod)
        for o in old:
            o.hide_render = True
            o.hide_viewport = True
    finally:
        L.HC, L.HR, L.MZ, L._surf = saved
    return mouth
