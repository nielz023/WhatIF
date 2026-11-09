# Gedeelde bouwstenen voor alle scènes:
#   - personages zichtbaar maken en "riggen" met draaipunten (heup, benen, armen, hoofd, ogen, wenkbrauwen)
#   - Bram krijgt een mond met vormen (praten, lachen, boos)
#   - zonnige buitenwereld (stenen richel, bomen met blaadjes, blauwe lucht, zon) + render-instellingen
import bpy, math, os
from mathutils import Vector, Quaternion, Matrix

R = math.radians
O = bpy.data.objects


# ---------------------------------------------------------------- algemene helpers
def srgb(r, g, b):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(r), c(g), c(b), 1.0)


def set_in(node, name, value):
    if node is not None and name in node.inputs:
        node.inputs[name].default_value = value


def material(name, rgb, rough=0.5, sss=0.0, sheen=0.0, coat=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes.get("Principled BSDF")
    set_in(b, "Base Color", srgb(*rgb))
    set_in(b, "Roughness", rough)
    if sss:
        set_in(b, "Subsurface Weight", sss)
    if sheen:
        set_in(b, "Sheen Weight", sheen)
    if coat:
        set_in(b, "Coat Weight", coat)
        set_in(b, "Coat Roughness", 0.2)
    if emit:
        set_in(b, "Emission Color", srgb(*rgb))
        set_in(b, "Emission Strength", emit)
    return m


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def prim(kind, name, loc, scale=(1, 1, 1), mat=None):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=2)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=2)
    elif kind == "plane":
        bpy.ops.mesh.primitive_plane_add(size=2)
    o = bpy.context.active_object
    o.name = name
    o.data.transform(Matrix.Diagonal((*scale, 1.0)))
    o.location = loc
    if kind in ("sphere", "cyl"):
        smooth(o)
    if mat:
        o.data.materials.append(mat)
    return o


def empty(name, loc, coll):
    e = bpy.data.objects.new(name, None)
    coll.objects.link(e)
    e.location = loc
    e.empty_display_size = 0.05
    return e


def reparent(child, par):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = par
    child.parent_type = "OBJECT"
    child.matrix_parent_inverse = par.matrix_world.inverted()
    child.matrix_basis = mw


def key(obj, path, frame, value):
    setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)


def rot_keys(obj, keys):
    for f, (x, y, z) in keys:
        key(obj, "rotation_euler", f, (R(x), R(y), R(z)))


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def curve(points, f):
    """Vloeiende waarde tussen (frame, waarde)-punten."""
    if f <= points[0][0]:
        return points[0][1]
    for (f0, v0), (f1, v1) in zip(points, points[1:]):
        if f0 <= f <= f1:
            return v0 + (v1 - v0) * smoothstep(f0, f1, f)
    return points[-1][1]


def bbox(objs):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


# ---------------------------------------------------------------- scène opzetten
def setup(show):
    scene = bpy.context.scene
    vl = bpy.context.view_layer
    for lc in vl.layer_collection.children:
        if lc.name == "cast":
            lc.exclude = False
            for c in lc.children:
                c.exclude = c.name not in show
        elif lc.name in ("studio", "glans_tmp"):
            lc.exclude = True
    buiten = bpy.data.collections.new("buiten")
    scene.collection.children.link(buiten)
    vl.active_layer_collection = vl.layer_collection.children["buiten"]
    return scene, buiten


class Rig:
    """Draaipunten van één personage. Kanten: -1 = links in rustpose (−x), +1 = rechts (+x)."""
    pass


def _rig_common(rig, coll, char, torso_parts, head_parts, legs, arms_up, arms_low, eyes, brows,
                hip_z, neck, shoulders, elbows, hips):
    rig.char = char
    char.rotation_mode = "XYZ"      # sommige personages komen uit glTF met quaternion-rotatie
    rig.mover = empty(f"{char.name}_Beweging", (0, 0, 0), coll)
    reparent(rig.mover, char)
    rig.root = empty(f"{char.name}_Heup", (0, 0, hip_z), coll)
    reparent(rig.root, rig.mover)
    rig.head = empty(f"{char.name}_Nek", neck, coll)
    reparent(rig.head, rig.root)
    rig.nod = empty(f"{char.name}_Knik", neck, coll)
    reparent(rig.nod, rig.head)
    for o in torso_parts:
        reparent(o, rig.root)
    for o in head_parts:
        reparent(o, rig.nod)
    rig.sh, rig.el, rig.hip, rig.eyes, rig.brows = {}, {}, {}, {}, {}
    for s in (-1, 1):
        rig.hip[s] = empty(f"{char.name}_HeupGewricht_{s}", hips[s], coll)
        reparent(rig.hip[s], rig.mover)
        for o in legs[s]:
            reparent(o, rig.hip[s])
        rig.sh[s] = empty(f"{char.name}_Schouder_{s}", shoulders[s], coll)
        reparent(rig.sh[s], rig.root)
        rig.el[s] = empty(f"{char.name}_Elleboog_{s}", elbows[s], coll)
        reparent(rig.el[s], rig.sh[s])
        for o in arms_up[s]:
            reparent(o, rig.sh[s])
        for o in arms_low[s]:
            reparent(o, rig.el[s])
        if eyes.get(s):
            mn, mx = bbox(eyes[s])
            rig.eyes[s] = empty(f"{char.name}_Oog_{s}", (mn + mx) / 2, coll)
            reparent(rig.eyes[s], rig.nod)
            for o in eyes[s]:
                reparent(o, rig.eyes[s])
        if brows.get(s):
            mn, mx = bbox(brows[s])
            rig.brows[s] = empty(f"{char.name}_Wenkbrauw_{s}", (mn + mx) / 2, coll)
            reparent(rig.brows[s], rig.nod)
            for o in brows[s]:
                reparent(o, rig.brows[s])
    rig.brow_base = {s: b.location.copy() for s, b in rig.brows.items()}
    rig.leg_len = hips[1][2] - 0.02
    return rig


def rig_bram():
    coll = bpy.data.collections["hoofdpersonage"]
    P = lambda i: O[f"Bram_part_{i}"]
    rig = Rig()
    rig.name = "Bram"
    legs = {-1: [P(0), P(1)], 1: [P(2), P(3)]}
    _rig_common(
        rig, coll, O["hoofdpersonage"],
        torso_parts=[P(i) for i in (4, 5, 6, 7, 8, 9, 10, 11, 12, 27)],
        head_parts=[P(i) for i in range(28, 55) if i not in range(33, 53)],
        legs=legs,
        arms_up={-1: [P(13)], 1: [P(20)]},
        arms_low={-1: [P(14), P(15), P(16), O["Node_20"]], 1: [P(21), P(22), P(23), O["Node_28"]]},
        eyes={-1: [P(i) for i in range(33, 40)], 1: [P(i) for i in range(40, 47)]},
        brows={-1: [P(i) for i in (47, 48, 49)], 1: [P(i) for i in (50, 51, 52)]},
        hip_z=0.64, neck=(0, 0, 1.2),
        shoulders={-1: (-0.15, -0.01, 1.11), 1: (0.15, -0.01, 1.11)},
        elbows={-1: (-0.24, -0.02, 0.86), 1: (0.24, -0.02, 0.86)},
        hips={-1: (-0.087, 0, 0.72), 1: (0.087, 0, 0.72)},
    )
    _bram_face(rig, coll)
    _toy_materials()
    return rig


def rig_named(cname):
    """Personages met namen als 'pestkop_bovenarm_R', 'pestkop_hoofd', ..."""
    coll = bpy.data.collections[cname]
    char = O[cname]
    rig = Rig()
    rig.name = cname
    for o in list(coll.objects):
        if o is not char and o.parent is None:
            reparent(o, char)
    meshes = [o for o in coll.objects if o.type == "MESH"]

    def side_of(o):
        mn, mx = bbox([o])
        return -1 if (mn.x + mx.x) / 2 < 0 else 1

    def has(o, *tokens):
        n = o.name[len(cname) + 1:]
        return any(n.startswith(t) for t in tokens)

    legs = {-1: [], 1: []}
    up = {-1: [], 1: []}
    low = {-1: [], 1: []}
    eyes = {-1: [], 1: []}
    brows = {-1: [], 1: []}
    head, torso = [], []
    for o in meshes:
        if has(o, "been_", "schoen_"):
            legs[side_of(o)].append(o)
        elif has(o, "bovenarm_", "mouwzoom_"):
            up[side_of(o)].append(o)
        elif has(o, "onderarm_", "elleboog_", "manchet_", "hand_", "duim_", "vingers_", "telefoon"):
            low[side_of(o)].append(o)
        elif has(o, "oog_"):
            eyes[side_of(o)].append(o)
        elif has(o, "wenkbrauw_"):
            brows[side_of(o)].append(o)
        elif has(o, "hoofd", "oor_", "mond", "tong", "haar", "krul", "pet", "bril", "neus", "baard", "snor"):
            head.append(o)
        else:
            torso.append(o)
    hips, shoulders, elbows = {}, {}, {}
    for s in (-1, 1):
        lmn, lmx = bbox([o for o in legs[s] if "been_" in o.name] or legs[s])
        hips[s] = ((lmn.x + lmx.x) / 2, (lmn.y + lmx.y) / 2, lmx.z - 0.06)
        amn, amx = bbox([o for o in up[s] if "bovenarm_" in o.name] or up[s])
        inner = amx.x if s < 0 else amn.x
        shoulders[s] = (inner + s * 0.04, (amn.y + amx.y) / 2, amx.z - 0.04)
        emn, emx = bbox([o for o in low[s] if "elleboog_" in o.name] or low[s])
        elbows[s] = tuple((emn + emx) / 2)
    hmn, hmx = bbox([o for o in head if o.name.endswith("hoofd")] or head)
    neck = (0, 0, hmn.z + 0.02)
    _rig_common(rig, coll, char, torso, head, legs, up, low, eyes, brows,
                hip_z=hips[1][2] - 0.08, neck=neck, shoulders=shoulders, elbows=elbows, hips=hips)
    rig.mouth_shapes = None
    return rig


# ---------------------------------------------------------------- Bram: mond met vormen + blosjes
HC, HR, MZ = Vector((0, 0, 1.47)), 0.3, 1.383
NC, NR = 28, 5
VIS = {
    "A": dict(w=0.044, uh=0.0015, lh=0.0005, corner=0.006, teeth=0.0, tongue=0.0),
    "X": dict(w=0.050, uh=0.005, lh=0.030, corner=0.008, teeth=0.006, tongue=0.45),
    "B": dict(w=0.048, uh=0.004, lh=0.013, corner=0.006, teeth=0.007, tongue=0.0),
    "C": dict(w=0.047, uh=0.007, lh=0.030, corner=0.005, teeth=0.007, tongue=0.35),
    "D": dict(w=0.049, uh=0.010, lh=0.048, corner=0.004, teeth=0.008, tongue=0.45),
    "E": dict(w=0.034, uh=0.011, lh=0.030, corner=0.000, teeth=0.005, tongue=0.30),
    "F": dict(w=0.021, uh=0.008, lh=0.014, corner=-0.001, teeth=0.0, tongue=0.0),
    "G": dict(w=0.044, uh=0.003, lh=0.007, corner=0.004, teeth=0.009, tongue=0.0),
    "H": dict(w=0.047, uh=0.007, lh=0.030, corner=0.005, teeth=0.006, tongue=0.85),
    "Lach": dict(w=0.057, uh=0.0015, lh=0.002, corner=0.015, teeth=0.0, tongue=0.0),
    "Boos": dict(w=0.040, uh=-0.004, lh=-0.006, corner=-0.012, teeth=0.0, tongue=0.0),
    "Schreeuw": dict(w=0.046, uh=0.016, lh=0.05, corner=-0.004, teeth=0.008, tongue=0.4),
}


def _surf(u, v, off):
    z = MZ + v
    dz = z - HC.z
    y = -math.sqrt(max((HR + off) ** 2 - u * u - dz * dz, 1e-6))
    return Vector((u, y, z))


def _curves(p, t):
    up = p["corner"] * t * t + p["uh"] * (1 - t * t)
    lo = p["corner"] * t * t - p["lh"] * max(0.0, 1 - t * t) ** 0.85
    if lo > up:
        lo = up
    return up, lo


def _gen(p):
    vs = []
    w = p["w"]
    for i in range(NC + 1):
        t = -1 + 2 * i / NC
        up, lo = _curves(p, t)
        for j in range(NR + 1):
            vs.append(_surf(t * w, lo + (up - lo) * j / NR, 0.0015))
    for i in range(NC + 1):
        t = -0.78 + 1.56 * i / NC
        up, lo = _curves(p, t)
        top = up - 0.0006
        bot = min(top, max(top - p["teeth"], lo + 0.0006))
        for j in range(2):
            vs.append(_surf(t * w, bot + (top - bot) * j, 0.0028))
    up0, lo0 = _curves(p, 0)
    for i in range(NC + 1):
        t = -0.62 + 1.24 * i / NC
        up, lo = _curves(p, t)
        bot = lo + 0.0008
        top = bot + p["tongue"] * (up0 - lo0) * 0.55 * math.sqrt(max(0.0, 1 - (t / 0.62) ** 2))
        top = max(bot, min(top, up - 0.0012))
        for j in range(2):
            vs.append(_surf(t * w, bot + (top - bot) * j, 0.0022))
    return vs


def _bram_face(rig, coll):
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
    me = bpy.data.meshes.new("Bram_Mond")
    me.from_pydata([tuple(v) for v in _gen(VIS["A"])], [], [f for f, _ in faces])
    for poly, (_, m) in zip(me.polygons, faces):
        poly.material_index = m
        poly.use_smooth = True
    mouth = bpy.data.objects.new("Bram_Mond", me)
    coll.objects.link(mouth)
    me.materials.append(O["Bram_part_53"].data.materials[0])
    me.materials.append(material("Bram_Tanden", (250, 250, 246), rough=0.25, coat=0.5))
    me.materials.append(O["Bram_part_54"].data.materials[0])
    mouth.shape_key_add(name="Basis", from_mix=False)
    rig.mouth_shapes = {}
    for name, p in VIS.items():
        if name == "A":
            continue
        sk = mouth.shape_key_add(name=name, from_mix=False)
        for i, v in enumerate(_gen(p)):
            sk.data[i].co = v
        sk.slider_min, sk.slider_max = 0.0, 1.2
        sk.value = 0.0          # Blender 5 zet nieuwe vormen standaard op 1.0
        rig.mouth_shapes[name] = sk
    # mond meeroteren met de rest van het hoofd (Bram staat nog in rustpose op de oorsprong)
    reparent(mouth, rig.nod)
    for i in (53, 54):
        O[f"Bram_part_{i}"].hide_render = True
        O[f"Bram_part_{i}"].hide_viewport = True

    blush = bpy.data.materials.new("Bram_Blos")
    nt = blush.node_tree
    bs = nt.nodes.get("Principled BSDF")
    set_in(bs, "Base Color", srgb(240, 130, 125))
    set_in(bs, "Roughness", 0.6)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 0.032, 1 / 0.032, 1 / 0.022)
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.55
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nt.links.new(gr.outputs["Fac"], mul.inputs[0])
    nt.links.new(mul.outputs[0], bs.inputs["Alpha"])
    for s in (-1, 1):
        cx, cz = s * 0.165, 1.425
        centre = _surf(cx, cz - MZ, 0.0012)
        vs, fs = [], []
        ring, segs = 6, 32
        for a in range(ring + 1):
            for b in range(segs):
                ang = 2 * math.pi * b / segs
                rr = a / ring
                vs.append(_surf(cx + 0.032 * rr * math.cos(ang), cz - MZ + 0.022 * rr * math.sin(ang), 0.0012) - centre)
        for a in range(ring):
            for b in range(segs):
                i0 = a * segs + b
                i1 = a * segs + (b + 1) % segs
                fs.append((i0, i1, i1 + segs, i0 + segs))
        bm = bpy.data.meshes.new("Blos")
        bm.from_pydata([tuple(v) for v in vs], [], fs)
        bo = bpy.data.objects.new("Bram_Blos", bm)
        coll.objects.link(bo)
        bo.location = centre
        bm.materials.append(blush)
        smooth(bo)
        reparent(bo, rig.nod)


def _toy_materials():
    for mname, kw in (("Material_5", dict(sss=0.18, coat=0.3)), ("Material_2", dict(sheen=0.45)),
                      ("Material_0", dict(sheen=0.3)), ("Material_1", dict(coat=0.4)),
                      ("Material_4", dict(coat=0.3))):
        m = bpy.data.materials.get(mname)
        if m and m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if "sss" in kw:
                set_in(b, "Subsurface Weight", kw["sss"])
            if "coat" in kw:
                set_in(b, "Coat Weight", kw["coat"])
                set_in(b, "Coat Roughness", 0.25)
            if "sheen" in kw:
                set_in(b, "Sheen Weight", kw["sheen"])


def mouth_keys(rig, frame, **weights):
    """Zet mondvormen op een frame, bv. mouth_keys(bram, 10, Lach=1, Boos=0)."""
    if not rig.mouth_shapes:
        return
    for n, sk in rig.mouth_shapes.items():
        if n in weights:
            sk.value = weights[n]
            sk.keyframe_insert("value", frame=frame)


def blink_bake(rig, frames, end, base=None):
    """Knipperen (en optioneel ooggrootte-curve) per frame bakken."""
    for f in range(1, end + 1):
        b = 1.0
        for bf in frames:
            d = abs(f - bf)
            if d < 3:
                b = min(b, (0.05, 0.4, 0.85)[int(d)])
        v = (curve(base, f) if base else 1.0) * b
        for ep in rig.eyes.values():
            key(ep, "scale", f, Vector((1, 1, v)))


def brow_keys(rig, frame, dz=0.0, tilt=0.0):
    """tilt > 0 = boos (binnenkant omlaag), tilt < 0 = bezorgd/verbaasd (binnenkant omhoog)."""
    for s, b in rig.brows.items():
        key(b, "location", frame, rig.brow_base[s] + Vector((0, 0, dz)))
        key(b, "rotation_euler", frame, (0, R(-s * tilt), 0))


# ---------------------------------------------------------------- audio, lipsync, knikjes
def add_sound(wav, lead, channel=1):
    """Stem als geluidsspoor in de Video Sequencer (handig om in Blender mee te kijken)."""
    scene = bpy.context.scene
    try:
        se = scene.sequence_editor_create()
        strips = se.strips if hasattr(se, "strips") else se.sequences
        strips.new_sound(os.path.basename(wav), wav, channel, int(lead) + 1)
    except Exception as e:
        print("geluidsspoor niet toegevoegd:", e)


def audio_peaks(wav, lead, fps=24, thresh=0.45, min_gap=7):
    """Klemtonen (frames) + duur (sec) uit een mono 16-bit WAV."""
    import wave, struct
    with wave.open(wav, "rb") as wf:
        sr, nch, nfr = wf.getframerate(), wf.getnchannels(), wf.getnframes()
        raw = wf.readframes(nfr)
    samples = struct.unpack("<%dh" % (len(raw) // 2), raw)[::nch]
    dur = len(samples) / sr
    hop = sr // fps
    env = []
    for k in range(int(dur * fps) + 1):
        seg = samples[k * hop:(k + 1) * hop]
        env.append(math.sqrt(sum(x * x for x in seg) / max(1, len(seg))) if seg else 0.0)
    mx = max(env) or 1.0
    env = [e / mx for e in env]
    sm = [sum(env[max(0, k - 1):k + 2]) / len(env[max(0, k - 1):k + 2]) for k in range(len(env))]
    peaks, last = [], -99
    for k in range(1, len(sm) - 1):
        if sm[k] > thresh and sm[k] >= sm[k - 1] and sm[k] >= sm[k + 1] and k - last >= min_gap:
            peaks.append(lead + k + 1)
            last = k
    return peaks, dur


def lipsync(rig, cues_path, lead, fps=24, strength=0.92, end=None):
    """Rhubarb-JSON -> mondvorm-keys. Geeft zinnen terug als [(start_frame, eind_frame), ...]
    (een stilte 'X' van >= 0,3 s scheidt twee zinnen)."""
    import json
    cues = json.load(open(cues_path, encoding="utf-8"))["mouthCues"]
    F = lambda sec: lead + sec * fps + 1
    names = [n for n in "XBCDEFGH" if n in rig.mouth_shapes]
    keys = [(max(1, F(cues[0]["start"]) - 2), "A")]
    for c in cues:
        f0, f1 = F(c["start"]), F(c["end"])
        fa, fb = f0 + 0.75, f1 - 0.75
        for fr in ([fa, fb] if fb > fa + 0.5 else [(f0 + f1) / 2]):
            keys.append((fr, c["value"]))
    if end:
        keys.append((end, "A"))
    for fr, v in keys:
        for n in names:
            sk = rig.mouth_shapes[n]
            sk.value = strength if n == v else 0.0
            sk.keyframe_insert("value", frame=fr)
    phrases, cur = [], None
    for c in cues:
        if c["value"] == "X" and c["end"] - c["start"] >= 0.3:
            if cur:
                phrases.append((F(cur[0]), F(c["start"])))
                cur = None
        else:
            cur = (cur[0] if cur else c["start"], c["end"])
    if cur:
        phrases.append((F(cur[0]), F(cur[1])))
    return phrases


def nods(rig, peak_frames, deg=3.5):
    """Kleine hoofdknik op elke klemtoon (eigen kanaal: rig.nod)."""
    key(rig.nod, "rotation_euler", 1, (0, 0, 0))
    for f in peak_frames:
        key(rig.nod, "rotation_euler", f - 2, (0, 0, 0))
        key(rig.nod, "rotation_euler", f + 1, (R(deg), 0, 0))
        key(rig.nod, "rotation_euler", f + 5, (0, 0, 0))


# ---------------------------------------------------------------- emoties en gebaren
EMOTIES = {
    #             wenkbrauw hoogte, kanteling, Lach, Boos, ooggrootte
    "neutraal":     (0.000, 0, 0.35, 0.0, 1.00),
    "blij":         (0.010, -4, 0.95, 0.0, 0.85),
    "heel_blij":    (0.020, -6, 1.00, 0.0, 0.80),
    "boos":         (-0.005, 16, 0.00, 1.0, 1.00),
    "verbaasd":     (0.020, -10, 0.00, 0.0, 1.15),
    "bezorgd":      (0.010, -15, 0.00, 0.3, 1.00),
    "nieuwsgierig": (0.012, -6, 0.20, 0.0, 1.05),
    "trots":        (0.006, 4, 0.80, 0.0, 0.90),
}


def emotion(rig, frame, name, eye_track=None):
    """Zet een gezichtsuitdrukking op een frame. eye_track = lijst waar de ooggrootte in komt
    (geef die later door aan blink_bake(..., base=eye_track))."""
    dz, tilt, lach, boos, eye = EMOTIES[name]
    brow_keys(rig, frame, dz, tilt)
    if rig.mouth_shapes:
        mouth_keys(rig, frame, Lach=lach, Boos=boos)
    if eye_track is not None:
        eye_track.append((frame, eye))


def _arm(rig, s, f, sh, el):
    key(rig.sh[s], "rotation_euler", f, tuple(R(v) for v in sh))
    key(rig.el[s], "rotation_euler", f, tuple(R(v) for v in el))


def rest(rig, f, sides=(-1, 1)):
    for s in sides:
        _arm(rig, s, f, (0, 0, 0), (0, 0, 0))


def gesture(rig, name, f0, s=1, length=24):
    """Gebaar dat op frame f0 begint, voor arm s (+1 = rechts in rustpose, -1 = links).
    Geeft het eindframe terug. Arm gaat NIET vanzelf terug: roep daarna rest() of een nieuw gebaar aan."""
    f = f0
    if name == "zwaai":
        _arm(rig, s, f + 6, (-10, -s * 100, 0), (0, -s * 38, 0))
        _arm(rig, s, f + 10, (-8, -s * 86, 0), (0, -s * 24, 0))
        t, up = f + 14, True
        while t < f0 + length:
            _arm(rig, s, t, (-8, -s * 90, 0), (0, -s * (50 if up else 24), 0))
            t += 6
            up = not up
        return t
    if name == "hand_op_borst":
        _arm(rig, s, f + 8, (-18, -s * 10, -s * 28), (-95, 0, 0))
        _arm(rig, s, f + length, (-16, -s * 8, -s * 30), (-92, 0, 0))
    elif name == "uitleggen":
        _arm(rig, s, f + 7, (-8, -s * 14, 0), (-75, 0, 0))
        t, k = f + 13, 0
        while t < f0 + length:
            _arm(rig, s, t, (-6 - 2 * (k % 2), -s * (18 if k % 2 else 14), 0), (-64 - 14 * (k % 2), 0, 0))
            t += 7
            k += 1
    elif name == "armen_omhoog":
        _arm(rig, s, f + 6, (0, -s * 25, 0), (0, -s * 12, 0))
        _arm(rig, s, f + 11, (0, -s * 112, 0), (0, -s * 24, 0))
        _arm(rig, s, f + 15, (0, -s * 98, 0), (0, -s * 12, 0))
        _arm(rig, s, f + length, (0, -s * 104, 0), (0, -s * 18, 0))
    elif name == "wijzen":
        _arm(rig, s, f + 6, (-84, -s * 8, 0), (-6, 0, 0))
        _arm(rig, s, f + length, (-80, -s * 10, 0), (-8, 0, 0))
    elif name == "vuisten":
        _arm(rig, s, f + 6, (-30, -s * 12, 0), (-115, 0, 0))
        _arm(rig, s, f + length, (-30, -s * 12, 0), (-115, 0, 0))
    elif name == "handen_in_zij":
        _arm(rig, s, f + 8, (0, -s * 35, 0), (-40, s * 60, 0))
        _arm(rig, s, f + length, (0, -s * 35, 0), (-40, s * 60, 0))
    else:
        raise ValueError(f"onbekend gebaar: {name}")
    return f0 + length


def body_keys(rig, f, lean=0.0, side=0.0, dz=0.0, squash=1.0):
    """Romp: lean>0 = voorover, side = opzij kantelen, dz = op/neer, squash<1 = indrukken."""
    key(rig.root, "rotation_euler", f, (R(lean), R(side), 0))
    key(rig.mover, "location", f, Vector((0, 0, dz)))
    sxy = 1 + (1 - squash) * 0.8
    key(rig.root, "scale", f, Vector((sxy, sxy, squash)))


def head_keys(rig, f, up=0.0, tilt=0.0, turn=0.0):
    """Hoofd: up>0 = omhoog kijken, tilt = scheef, turn = links/rechts draaien."""
    key(rig.head, "rotation_euler", f, (R(-up), R(tilt), R(turn)))


# ---------------------------------------------------------------- zonnige buitenwereld
def sock(socks, name=None, idx=0):
    live = [s for s in socks if s.enabled and (name is None or s.name == name)]
    if not live:
        live = [s for s in socks if name is None or s.name == name]
    return live[idx]


def build_outdoor(buiten):
    scene = bpy.context.scene
    stone = material("Steen", (170, 170, 176), rough=0.65)
    sn = stone.node_tree
    noise = sn.nodes.new("ShaderNodeTexNoise")
    set_in(noise, "Scale", 40.0)
    bump = sn.nodes.new("ShaderNodeBump")
    set_in(bump, "Strength", 0.06)
    sn.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    sn.links.new(bump.outputs["Normal"], sn.nodes["Principled BSDF"].inputs["Normal"])
    ledge = prim("cube", "Richel", (3.4, 1.5, -0.8), (5.6, 2.5, 0.8), stone)
    bv = ledge.modifiers.new("Bevel", "BEVEL")
    bv.width, bv.segments = 0.03, 3

    grass = material("Gras", (96, 170, 70), rough=0.8, sheen=0.5)
    prim("plane", "Grasveld", (0, 20, -1.6), (80, 60, 1), grass)
    for i, (x, y, r, h) in enumerate(((-14, 40, 14, 3.5), (6, 55, 20, 5), (28, 45, 16, 4), (-35, 60, 22, 6))):
        prim("sphere", f"Heuvel{i}", (x, y, -1.6), (r, r * 0.6, h), grass)

    leaf_me = bpy.data.meshes.new("Blad")
    lv = [(0.13 * math.cos(2 * math.pi * k / 16), 0.09 * math.sin(2 * math.pi * k / 16),
           0.012 * math.cos(2 * math.pi * k / 16) ** 2) for k in range(16)]
    leaf_me.from_pydata([(0, 0, -0.012)] + lv, [], [(0, 1 + k, 1 + (k + 1) % 16) for k in range(16)])
    leaf = bpy.data.objects.new("Blad_bron", leaf_me)
    buiten.objects.link(leaf)
    leaf.hide_render = leaf.hide_viewport = True
    leaf_mat = bpy.data.materials.new("Blad")
    ln = leaf_mat.node_tree
    lb = ln.nodes.get("Principled BSDF")
    oi = ln.nodes.new("ShaderNodeObjectInfo")
    ramp = ln.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(95, 170, 45)
    ramp.color_ramp.elements[1].color = srgb(175, 225, 80)
    ln.links.new(oi.outputs["Random"], ramp.inputs["Fac"])
    ln.links.new(ramp.outputs["Color"], lb.inputs["Base Color"])
    set_in(lb, "Roughness", 0.45)
    set_in(lb, "Subsurface Weight", 0.15)
    set_in(lb, "Sheen Weight", 0.3)
    leaf_me.materials.append(leaf_mat)

    ng = bpy.data.node_groups.new("Bladeren", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, l = ng.nodes, ng.links
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    dist = n.new("GeometryNodeDistributePointsOnFaces")
    dist.inputs["Density"].default_value = 75.0
    info = n.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = leaf
    inst = n.new("GeometryNodeInstanceOnPoints")
    rnd = n.new("FunctionNodeRandomValue")
    rnd.data_type = "FLOAT"
    sock(rnd.inputs, "Min").default_value = 0.75
    sock(rnd.inputs, "Max").default_value = 1.3
    join = n.new("GeometryNodeJoinGeometry")
    l.new(gi.outputs[0], dist.inputs["Mesh"])
    l.new(dist.outputs["Points"], inst.inputs["Points"])
    l.new(info.outputs["Geometry"], inst.inputs["Instance"])
    rv = n.new("FunctionNodeRandomValue")
    rv.data_type = "FLOAT_VECTOR"
    sock(rv.inputs, "Min").default_value = (-0.6, -0.6, -3.14)
    sock(rv.inputs, "Max").default_value = (0.6, 0.6, 3.14)
    e2r = n.new("FunctionNodeEulerToRotation")
    rr = n.new("FunctionNodeRotateRotation")
    rr.rotation_space = "LOCAL"
    l.new(sock(rv.outputs), e2r.inputs[0])
    l.new(dist.outputs["Rotation"], rr.inputs[0])
    l.new(e2r.outputs[0], rr.inputs[1])
    l.new(rr.outputs[0], inst.inputs["Rotation"])
    l.new(sock(rnd.outputs), inst.inputs["Scale"])
    l.new(gi.outputs[0], join.inputs[0])
    l.new(inst.outputs["Instances"], join.inputs[0])
    l.new(join.outputs[0], go.inputs[0])

    inner = material("Bladbinnen", (52, 105, 30), rough=0.8)
    bark = material("Schors", (110, 74, 46), rough=0.8)
    for i, (x, y, cz, r) in enumerate(((-3.6, 3.6, 0.35, 1.9), (-1.2, 9.5, 1.1, 2.3), (-8.5, 11.0, 0.9, 2.2),
                                       (11.0, 12.0, 1.0, 2.4))):
        prim("cyl", f"Stam{i}", (x, y, (cz - 1.6) / 2 - 0.8), (0.16 * r / 1.7, 0.16 * r / 1.7, (cz + 1.6) / 2), bark)
        c = prim("sphere", f"Kruin{i}", (x, y, cz), (r, r, r * 0.95), inner)
        c.modifiers.new("Bladeren", "NODES").node_group = ng

    glow_dir = Vector((-0.42, 0.78, 0.46)).normalized()
    sun_dir = Vector((-0.6, -0.35, 0.72)).normalized()
    world = bpy.data.worlds.new("Lucht")
    scene.world = world
    wn, wl = world.node_tree.nodes, world.node_tree.links
    bg = wn.get("Background")
    tcw = wn.new("ShaderNodeTexCoord")
    sep = wn.new("ShaderNodeSeparateXYZ")
    wl.new(tcw.outputs["Generated"], sep.inputs[0])
    mr = wn.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.4
    wl.new(sep.outputs["Z"], mr.inputs["Value"])
    sky = wn.new("ShaderNodeValToRGB")
    sky.color_ramp.elements[0].color = srgb(125, 180, 240)
    sky.color_ramp.elements[1].color = srgb(38, 100, 205)
    wl.new(mr.outputs["Result"], sky.inputs["Fac"])
    dot = wn.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = glow_dir
    wl.new(tcw.outputs["Generated"], dot.inputs[0])
    glow = wn.new("ShaderNodeMapRange")
    glow.inputs["From Min"].default_value = 0.78
    glow.inputs["From Max"].default_value = 1.0
    wl.new(dot.outputs["Value"], glow.inputs["Value"])
    pw = wn.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 3.0
    wl.new(glow.outputs["Result"], pw.inputs[0])
    mix = wn.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "ADD"
    mix.inputs["B"].default_value = srgb(255, 236, 190)
    wl.new(pw.outputs[0], mix.inputs["Factor"])
    wl.new(sky.outputs["Color"], mix.inputs["A"])
    wl.new(mix.outputs["Result"], bg.inputs["Color"])
    set_in(bg, "Strength", 0.85)

    sun_d = bpy.data.lights.new("Zon", "SUN")
    sun_d.energy, sun_d.color, sun_d.angle = 4.5, (1.0, 0.88, 0.72), R(3)
    sun = bpy.data.objects.new("Zon", sun_d)
    buiten.objects.link(sun)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat("Z", "Y")

    def area(name, loc, target, size, energy, rgb):
        ld = bpy.data.lights.new(name, "AREA")
        ld.size, ld.energy, ld.color = size, energy, rgb
        o = bpy.data.objects.new(name, ld)
        buiten.objects.link(o)
        o.location = loc
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
        try:
            o.visible_camera = False
        except Exception:
            pass

    area("Vullicht", (3.2, -5.0, 2.2), (0, 0, 1.1), 4.0, 260, (1.0, 0.93, 0.85))
    area("Koel_vul", (-3.5, -3.5, 1.2), (0, 0, 1.0), 3.0, 120, (0.75, 0.85, 1.0))
    area("Randlicht", (1.5, 2.5, 2.4), (0, 0, 1.3), 1.5, 250, (1.0, 0.85, 0.65))


def camera(buiten, lens=50, fstop=2.8, focus_parent=None, focus_loc=(0, -0.3, 1.45)):
    scene = bpy.context.scene
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    buiten.objects.link(cam)
    scene.camera = cam
    aim = empty("CameraDoel", (0, 0, 1.0), buiten)
    trk = cam.constraints.new("TRACK_TO")
    trk.target, trk.track_axis, trk.up_axis = aim, "TRACK_NEGATIVE_Z", "UP_Y"
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    if focus_parent is not None:
        focus = empty("Scherpstelpunt", focus_loc, buiten)
        reparent(focus, focus_parent)
        cd.dof.focus_object = focus
    return cam, aim


def render_settings(samples=32):
    scene = bpy.context.scene
    r = scene.render
    r.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "OPTIX"
        scene.cycles.device = "GPU"
    except Exception as e:
        print("GPU setup failed:", e)
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5
    r.use_persistent_data = True
    r.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    try:
        cg = bpy.data.node_groups.new("Gloed", "CompositorNodeTree")
        cg.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = cg.nodes.new("CompositorNodeRLayers")
        gl = cg.nodes.new("CompositorNodeGlare")
        go = cg.nodes.new("NodeGroupOutput")
        for nm, val in (("Type", "Bloom"), ("Quality", "High"), ("Threshold", 0.9), ("Strength", 0.35),
                        ("Size", 0.6)):
            if nm in gl.inputs:
                try:
                    gl.inputs[nm].default_value = val
                except Exception:
                    pass
        cg.links.new(rl.outputs["Image"], gl.inputs["Image"])
        cg.links.new(gl.outputs["Image"], go.inputs[0])
        scene.compositing_node_group = cg
    except Exception as e:
        print("bloom overgeslagen:", e)
    r.image_settings.file_format = "PNG"
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100


def run(mode, out, blend_path, still_frames, end):
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.frame_start, scene.frame_end = 1, end
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)
    r = scene.render
    if mode == "stills":
        r.resolution_percentage = 50
        scene.cycles.samples = 16
        for f in still_frames:
            scene.frame_set(f)
            r.filepath = os.path.join(out, f"still_{f:03d}.png")
            bpy.ops.render.render(write_still=True)
    else:
        r.filepath = os.path.join(out, "f_")
        bpy.ops.render.render(animation=True)
    print("KLAAR")
