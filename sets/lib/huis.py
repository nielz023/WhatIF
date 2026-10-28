"""Props voor video 2 ("What IF You Got 10x FASTER Every Day?"): whiteboard op de
koelkast, verjaardagstaart met 9 kaarsjes, papieren kraanvogels, hogesnelheidscamera,
laptop, knijpfles, kapotte sneakers, bakspullen, cadeau, hangende regendruppels en
glasscherven in de lucht. Zelfde conventies als props.py: nulpunt op de grond (of het
tafelblad) in het midden, echte maten in meters."""
import math
import os
import random

import bpy
import bmesh
from mathutils import Vector, Euler

from . import toon as T
from . import props as P

FONT_MARKER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts",
                           "PermanentMarker-Regular.ttf")
MARKER = dict(blauw=(0.05, 0.18, 0.75), rood=(0.85, 0.06, 0.05), zwart=(0.03, 0.03, 0.04),
              groen=(0.05, 0.50, 0.15))
PAPIER = [(0.95, 0.20, 0.25), (0.98, 0.55, 0.10), (0.98, 0.85, 0.15), (0.25, 0.70, 0.30),
          (0.15, 0.55, 0.95), (0.55, 0.30, 0.85), (0.98, 0.50, 0.70), (0.97, 0.96, 0.92)]


def _set_rough(mat, rough):
    """Glans-look: papier en stof minder glimmend dan vinyl."""
    if T.GLANS:
        for n in mat.node_tree.nodes:
            if n.type == "GROUP" and "Ruwheid" in n.inputs:
                n.inputs["Ruwheid"].default_value = rough
    return mat


def paper(name, color):
    return _set_rough(T.toon(name, color), 0.75)


def water(name="water"):
    """Echt glas/water (Principled met transmissie) voor druppels, glazen en de fles."""
    key = "water_" + name
    if key in T._mats:
        return T._mats[key]
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    b = mt.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.85, 0.93, 1.0, 1)
    b.inputs["Roughness"].default_value = 0.03
    b.inputs["IOR"].default_value = 1.33
    b.inputs["Transmission Weight"].default_value = 1.0
    mt.diffuse_color = (0.7, 0.85, 1.0, 0.3)
    if not T.GLANS:
        return T.glass(name, (0.7, 0.85, 1.0), alpha=0.35)
    T._mats[key] = mt
    return mt


def font_marker():
    f = bpy.data.fonts.get("PermanentMarker-Regular")
    if f is None and os.path.exists(FONT_MARKER):
        f = bpy.data.fonts.load(FONT_MARKER)
    return f


def marker_text(name, body, loc, size, color="blauw", rot=(90, 0, 0), align="CENTER", parent=None):
    """Handgeschreven stifttekst (Permanent Marker). Plat, zodat hij op een bord of raam ligt."""
    o = T.text(name, body, loc, size, T.toon("stift_" + color, MARKER[color]), rot=rot, extrude=0.0004, align=align)
    f = font_marker()
    if f:
        o.data.font = f
    if parent:
        o.parent = parent
    return o


def arrow(name, loc, length, size, color="blauw", rot=(90, 0, 0), parent=None):
    """Getekende pijl naar rechts (het lettertype heeft geen pijlteken)."""
    t, h = size * 0.12, size * 0.35
    v = [(0, -t, 0), (length - h, -t, 0), (length - h, -h, 0), (length, 0, 0), (length - h, h, 0), (length - h, t, 0), (0, t, 0)]
    o = T.mesh_from(name, [(x, y, 0) for x, y, _ in v], [tuple(range(7))], T.toon("stift_" + color, MARKER[color]))
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    if parent:
        o.parent = parent
    return o


# ---------------------------------------------------------------------------
# Whiteboard op de koelkast
# ---------------------------------------------------------------------------
def whiteboard(name, loc, rot_z=0.0, w=0.44, h=0.58):
    """Magnetisch whiteboard. Nulpunt = midden van de achterkant (tegen de koelkastdeur),
    voorkant kijkt naar -y. Geeft (ouder, voorkant_z_midden) terug; tekst komt erop via
    whiteboard_tekst(). Draai de ouder 180 graden om de achterkant te laten zien."""
    d = 0.014
    parts = [T.box(name + "_bord", (0, 0, 0), (w, d, h), T.toon("whiteboard_wit", (0.97, 0.97, 0.98)), bevel=0.004, base=False, ol=0),
             T.box(name + "_lijst_o", (0, 0, -h / 2), (w + 0.02, d + 0.006, 0.018), T.toon("whiteboard_lijst", (0.15, 0.45, 0.85)), bevel=0.006, base=False, ol=0),
             T.box(name + "_lijst_b", (0, 0, h / 2), (w + 0.02, d + 0.006, 0.018), T.toon("whiteboard_lijst", (0.15, 0.45, 0.85)), bevel=0.006, base=False, ol=0),
             T.box(name + "_lijst_l", (-w / 2, 0, 0), (0.018, d + 0.006, h + 0.02), T.toon("whiteboard_lijst", (0.15, 0.45, 0.85)), bevel=0.006, base=False, ol=0),
             T.box(name + "_lijst_r", (w / 2, 0, 0), (0.018, d + 0.006, h + 0.02), T.toon("whiteboard_lijst", (0.15, 0.45, 0.85)), bevel=0.006, base=False, ol=0),
             T.box(name + "_bakje", (0, -0.02, -h / 2 - 0.012), (w * 0.7, 0.035, 0.012), T.toon("whiteboard_lijst", (0.15, 0.45, 0.85)), bevel=0.003, base=False, ol=0)]
    board = T.merge(name + "_bord", parts, ol=0.004)
    pen = [T.cyl(name + "_stift_body", (0, 0, 0), 0.008, 0.11, P.m("wit"), rot=(0, 90, 0), seg=10, ol=0),
           T.cyl(name + "_stift_dop", (0.11, 0, 0), 0.0085, 0.035, T.toon("stift_blauw", MARKER["blauw"]), rot=(0, 90, 0), seg=10, ol=0)]
    pen_o = T.merge(name + "_stift", pen, ol=0.002)
    pen_o.location = (-0.07, -0.028, -h / 2 - 0.002)
    root = T.group(name, [board, pen_o], loc=loc, rot=(0, 0, rot_z))
    root["w"], root["h"], root["d"] = w, h, d
    return root


def whiteboard_tekst(root, regels, kant="voor"):
    """Schrijf regels op het whiteboard. regels = [(tekst, grootte, kleur, z_rel), ...]
    z_rel tussen -0.5 (onder) en 0.5 (boven). Tekst '->' wordt een getekende pijl.
    kant='achter' schrijft op de achterkant (zichtbaar als het bord 180 graden gedraaid is).
    Elke regel is een apart object, zodat hij in de animatie letter voor letter kan verschijnen."""
    w, h, d = root["w"], root["h"], root["d"]
    y = -d / 2 - 0.0006 if kant == "voor" else d / 2 + 0.0006
    rot = (90, 0, 0) if kant == "voor" else (90, 0, 180)
    out = []
    sgn = 1 if kant == "voor" else -1
    for k, (body, size, color, zr) in enumerate(regels):
        z = zr * h - size * 0.35
        nm = f"{root.name}_{kant}_regel{k + 1}"
        stukken = [p.strip() for p in body.split("->")]
        objs = []
        for i, part in enumerate(stukken):
            if i:
                objs.append(("pijl", None, size * (0.9 if size > 0.08 else 1.3)))
            if part:
                t = marker_text(nm + "abc"[i], part, (0, y, z), size, color, rot=rot, align="LEFT", parent=root)
                bpy.context.view_layer.update()
                objs.append(("tekst", t, t.dimensions.x))
        gap = size * 0.25
        tot = sum(wd for _, _, wd in objs) + gap * (len(objs) - 1)
        x = -tot / 2
        for kind, t, wd in objs:
            if kind == "pijl":
                out.append(arrow(nm + "_pijl", (sgn * x, y, z + size * 0.35), wd, size, color, rot=(90, 0, 0 if kant == "voor" else 180), parent=root))
            else:
                t.location.x = sgn * x
                out.append(t)
            x += wd + gap
    return out


# ---------------------------------------------------------------------------
# Verjaardagstaart met kaarsjes
# ---------------------------------------------------------------------------
def taart(name, loc, kaarsjes=9, aan=True, seed=9):
    """Ronde taart (2 lagen) op een taartplateau, met kaarsjes. loc = tafelblad.
    Vlammen zijn aparte objecten (naam ..._vlam_N) met een eigen klein lampje."""
    rnd = random.Random(seed)
    cake = T.toon("taart_biscuit", (0.98, 0.86, 0.62))
    icing = T.toon("taart_glazuur", (0.98, 0.62, 0.78))
    cream = T.toon("taart_slagroom", (0.99, 0.97, 0.94))
    parts = [T.cyl(name + "_plateau_voet", (0, 0, 0), 0.05, 0.07, P.m("wit"), r2=0.035, seg=24, ol=0),
             T.cyl(name + "_plateau", (0, 0, 0.07), 0.2, 0.012, P.m("wit"), seg=40, ol=0),
             T.cyl(name + "_laag1", (0, 0, 0.082), 0.16, 0.08, icing, seg=40, bevel=0.01, ol=0),
             T.cyl(name + "_laag2", (0, 0, 0.162), 0.115, 0.07, icing, seg=40, bevel=0.01, ol=0)]
    # druppels glazuur langs de rand en toefjes slagroom
    for r, z, n in ((0.16, 0.162, 22), (0.115, 0.232, 16)):
        for k in range(n):
            a = 2 * math.pi * k / n
            parts.append(T.sphere(f"{name}_druppel{z}_{k}", (r * math.cos(a), r * math.sin(a), z - rnd.uniform(0.012, 0.03)),
                                  0.012, icing, scale=(0.8, 0.8, rnd.uniform(1.5, 2.6)), seg=8, ol=0))
        for k in range(n // 2):
            a = 2 * math.pi * (k + 0.5) / (n // 2)
            parts.append(T.sphere(f"{name}_toef{z}_{k}", ((r - 0.02) * math.cos(a), (r - 0.02) * math.sin(a), z + 0.008),
                                  0.014, cream, scale=(1, 1, 0.8), seg=10, ol=0))
    o = T.merge(name, parts, ol=0.004)
    # hagelslag
    spr = [(math.cos(a) * r, math.sin(a) * r, 0.236) for a, r in
           ((rnd.uniform(0, 6.283), 0.1 * math.sqrt(rnd.random())) for _ in range(120))]
    cols = [(0.95, 0.2, 0.2), (0.2, 0.6, 0.95), (0.98, 0.85, 0.1), (0.3, 0.8, 0.3)]
    for c in range(4):
        hs = P.points_mesh(f"{name}_hagelslag{c}", spr[c::4], 0.0035, T.toon(f"hagelslag{c}", cols[c]), seg=6)
        hs.parent = o
    # kaarsjes in een kring, gestreept
    flames = []
    for k in range(kaarsjes):
        a = 2 * math.pi * k / kaarsjes + 0.3
        x, y = 0.075 * math.cos(a), 0.075 * math.sin(a)
        c = T.cyl(f"{name}_kaars{k + 1}", (x, y, 0.232), 0.0055, 0.075, T.toon(f"kaars{k % 4}", cols[k % 4]), seg=10, ol=0)
        c.parent = o
        T.cyl(f"{name}_lont{k + 1}", (x, y, 0.307), 0.0012, 0.008, P.m("zwart"), seg=5, ol=0).parent = o
        if aan:
            f = T.sphere(f"{name}_vlam_{k + 1}", (x, y, 0.326), 0.0075, T.glow("kaarsvlam", (1.0, 0.62, 0.22), 25),
                         scale=(1, 1, 2.2), seg=10, ol=0)
            f.parent = o
            flames.append(f)
    if aan:
        T.point_light(f"{name}_kaarslicht", (0, 0, 0.36), color=(1.0, 0.6, 0.28), energy=14, radius=0.08).parent = o
    o.location = loc
    return o, flames


def taart_9(name, loc):
    """Cijfer 9 als taarttopper."""
    t = T.text(name, "9", (0, 0, 0), 0.07, T.toon("topper_goud", (0.95, 0.72, 0.2)), extrude=0.006)
    t.location = loc
    return t


# ---------------------------------------------------------------------------
# Papieren kraanvogels
# ---------------------------------------------------------------------------
def _crane_mesh(name, s=1.0, droevig=False):
    """Origami-kraanvogel van ~18 cm spanwijdte (s=1 is 14 cm; standaard 1.3, iets groter dan echt zodat hij leesbaar is naast de chibi-figuren), kijkt naar +x. droevig=True: het
    mislukte eerste exemplaar van het broertje ('een zielige duif')."""
    v = [(0.042, 0, 0.004), (-0.042, 0, 0.004), (0, 0, -0.026), (0, 0.012, 0.012), (0, -0.012, 0.012),
         # vleugels: brede driehoeken op de rug, punt iets naar achter en omhoog
         (0.032, 0.006, 0.011), (-0.032, 0.006, 0.011), (-0.012, 0.088, 0.03),
         (0.032, -0.006, 0.011), (-0.032, -0.006, 0.011), (-0.012, -0.088, 0.03),
         # nek met geknikt kopje
         (0.02, 0.009, -0.018), (0.02, -0.009, -0.018), (0.044, 0, 0.012), (0.078, 0, 0.062), (0.071, 0, 0.058), (0.094, 0, 0.049),
         # staart
         (-0.02, 0.009, -0.018), (-0.02, -0.009, -0.018), (-0.044, 0, 0.012), (-0.084, 0, 0.066)]
    f = [(2, 0, 3), (2, 3, 1), (2, 1, 4), (2, 4, 0),
         (5, 6, 7), (8, 10, 9),
         (11, 13, 14), (12, 14, 13), (11, 14, 12), (15, 14, 16),
         (17, 20, 19), (18, 19, 20), (17, 18, 20)]
    if droevig:
        rnd = random.Random(4)
        v = [(x * 1.1 + rnd.uniform(-0.006, 0.006), y * (0.6 if abs(y) > 0.03 else 1) + rnd.uniform(-0.005, 0.005),
              z * (0.35 if z > 0.02 else 1) + rnd.uniform(-0.006, 0.006)) for x, y, z in v]
    v = [(x * s, y * s, z * s + 0.022 * s) for x, y, z in v]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.validate()
    return me


_crane_meshes = {}


def kraanvogel(name, loc, color_idx=0, rot=(0, 0, 0), s=1.3, droevig=False):
    """Eén kraanvogel. Kraanvogels met dezelfde kleur delen één mesh (licht voor 1.000 stuks)."""
    key = (color_idx, s, droevig)
    me = _crane_meshes.get(key)
    if me is None or me.name not in bpy.data.meshes:
        me = _crane_mesh(f"kraanvogel_mesh_{color_idx}{'_droevig' if droevig else ''}", s, droevig)
        me.materials.append(paper(f"origamipapier{color_idx}", PAPIER[color_idx % len(PAPIER)]))
        _crane_meshes[key] = me
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    T._link(o)
    return o


def kraanvogels_hoop(prefix, center, size, n, height=0.25, seed=1, z0=0.0):
    """Hoop kraanvogels (heuvel) op een tafel of aanrecht. size = (breedte x, diepte y)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        u, w = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        x, y = center[0] + u * size[0] / 2, center[1] + w * size[1] / 2
        # hoger in het midden, met wat ruis
        hz = height * max(0.0, 1 - (u * u + w * w) * 0.75) * rnd.uniform(0.5, 1.0)
        out.append(kraanvogel(f"{prefix}_{k + 1:04d}", (x, y, z0 + hz), rnd.randrange(8),
                              rot=(rnd.uniform(-25, 25), rnd.uniform(-25, 25), rnd.uniform(0, 360))))
    return out


def kraanvogels_lucht(prefix, bounds, n, seed=2, avoid=None):
    """Kraanvogels die stilhangen in de lucht (na de knal). bounds = ((x0,x1),(y0,y1),(z0,z1))."""
    rnd = random.Random(seed)
    out = []
    k = 0
    while len(out) < n and k < n * 4:
        k += 1
        p = Vector([rnd.uniform(*b) for b in bounds])
        if avoid and any((p - Vector(c)).length < r for c, r in avoid):
            continue
        out.append(kraanvogel(f"{prefix}_{len(out) + 1:04d}", p, rnd.randrange(8),
                              rot=(rnd.uniform(-180, 180), rnd.uniform(-180, 180), rnd.uniform(0, 360))))
    return out


def papierstapels(name, loc, n=6, seed=3):
    """Stapeltjes gekleurd origamipapier (15 x 15 cm). loc = tafelblad."""
    rnd = random.Random(seed)
    objs = []
    for k in range(n):
        x, y = (k % 3) * 0.17 - 0.17, (k // 3) * 0.17 - 0.08
        hgt = rnd.uniform(0.01, 0.04)
        b = T.box(f"{name}_{k}", (x, y, 0), (0.15, 0.15, hgt), paper(f"origamipapier{k % 8}", PAPIER[k % 8]),
                  rot=(0, 0, rnd.uniform(-12, 12)), bevel=0.001, ol=0)
        objs.append(b)
    return T.group(name, objs, loc=loc)


# ---------------------------------------------------------------------------
# Apparatuur van de natuurkundige
# ---------------------------------------------------------------------------
def hogesnelheidscamera(name, loc, rot_z=0.0, hoogte=1.35):
    """Hogesnelheidscamera ('filmt kogels') op een statief. Lens kijkt naar +x."""
    dk = T.toon("camera_body", (0.10, 0.11, 0.13))
    parts = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        parts.append(T.to_mesh(T.tube(f"{name}_poot{k}", [(0, 0, hoogte - 0.12), (0.42 * math.cos(a), 0.42 * math.sin(a), 0.0)], 0.013, P.m("zwart"))))
        parts.append(T.sphere(f"{name}_voet{k}", (0.42 * math.cos(a), 0.42 * math.sin(a), 0.01), 0.018, T.toon("rubber", (0.2, 0.2, 0.22)), seg=8, ol=0))
    parts += [T.cyl(name + "_zuil", (0, 0, hoogte - 0.4), 0.02, 0.32, P.m("metaal"), seg=12, ol=0),
              T.cyl(name + "_kop", (0, 0, hoogte - 0.1), 0.045, 0.06, P.m("zwart"), seg=16, ol=0),
              T.box(name + "_body", (0, 0, hoogte - 0.04), (0.2, 0.13, 0.14), dk, bevel=0.012, ol=0),
              T.box(name + "_handgreep", (-0.02, 0, hoogte + 0.1), (0.12, 0.03, 0.03), P.m("zwart"), bevel=0.01, ol=0),
              T.cyl(name + "_lens", (0.1, 0, hoogte + 0.03), 0.045, 0.14, P.m("zwart"), rot=(0, 90, 0), seg=24, ol=0),
              T.cyl(name + "_lensring", (0.2, 0, hoogte + 0.03), 0.048, 0.012, T.toon("lensring_rood", (0.85, 0.08, 0.06)), rot=(0, 90, 0), seg=24, ol=0),
              T.cyl(name + "_lensglas", (0.24, 0, hoogte + 0.03), 0.036, 0.004, T.toon("lensglas", (0.05, 0.10, 0.25)), rot=(0, 90, 0), seg=24, ol=0),
              T.box(name + "_schermpje", (-0.101, 0, hoogte + 0.0), (0.004, 0.09, 0.06), T.glow("camerascherm", (0.4, 0.75, 1.0), 2), bevel=0, base=False, ol=0)]
    o = T.merge(name, parts, ol=0.006)
    led = T.sphere(name + "_opname_led", (0.05, -0.066, hoogte + 0.08), 0.006, T.glow("led_rood", (1.0, 0.05, 0.03), 12), seg=8, ol=0)
    led.parent = o
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def laptop(name, loc, rot_z=0.0, scherm=(0.45, 0.70, 1.0)):
    """Open laptop met een oplichtend scherm (afspelen in slow motion). loc = tafelblad."""
    body = T.toon("laptop_grijs", (0.55, 0.57, 0.62))
    lap = [T.box(name + "_onder", (0, 0, 0), (0.34, 0.24, 0.016), body, bevel=0.005, ol=0),
           T.box(name + "_toetsen", (0, -0.01, 0.016), (0.29, 0.12, 0.002), P.m("zwart"), bevel=0, ol=0),
           T.box(name + "_klep", (0, 0.12, 0.0), (0.34, 0.012, 0.23), body, rot=(-15, 0, 0), bevel=0.005, ol=0)]
    o = T.merge(name, lap, ol=0.004)
    scr = T.box(name + "_beeld", (0, 0.112, 0.012), (0.31, 0.003, 0.2), T.glow("laptop_beeld_v2", scherm, 4.0), rot=(-15, 0, 0), bevel=0, ol=0)
    scr.parent = o
    # tijdlijn van de video-speler onderin het beeld
    bar = T.box(name + "_tijdlijn", (0, 0.108, 0.03), (0.27, 0.002, 0.006), T.glow("laptop_tijdlijn", (1.0, 0.35, 0.2), 2.5), rot=(-15, 0, 0), bevel=0, ol=0)
    bar.parent = o
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def schoudertas(name, loc, rot_z=0.0, color=(0.45, 0.30, 0.18)):
    m = T.toon("tas_leer", color)
    p = [T.box(name + "_vak", (0, 0, 0), (0.38, 0.12, 0.28), m, bevel=0.03, ol=0),
         T.box(name + "_klep", (0, -0.062, 0.1), (0.38, 0.01, 0.18), T.toon("tas_klep", tuple(c * 0.8 for c in color)), bevel=0.01, ol=0),
         T.box(name + "_gesp", (0, -0.07, 0.11), (0.05, 0.006, 0.03), P.m("metaal"), bevel=0.003, ol=0)]
    p.append(T.to_mesh(T.tube(name + "_band", [(-0.19, 0, 0.26), (-0.12, 0, 0.55), (0.12, 0, 0.55), (0.19, 0, 0.26)], 0.012, T.toon("tas_band", (0.15, 0.12, 0.10)))))
    o = T.merge(name, p, ol=0.004)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


# ---------------------------------------------------------------------------
# Kleine props
# ---------------------------------------------------------------------------
def knijpfles(name, loc, color=(0.15, 0.55, 0.95)):
    """Sportbidon met knijpdop. loc = tafelblad."""
    p = [T.cyl(name + "_fles", (0, 0, 0), 0.036, 0.19, T.toon("bidon", color), seg=24, bevel=0.006, ol=0),
         T.cyl(name + "_ring", (0, 0, 0.09), 0.037, 0.03, T.toon("bidon_grip", (0.95, 0.95, 0.97)), seg=24, ol=0),
         T.cyl(name + "_dop", (0, 0, 0.19), 0.03, 0.025, P.m("wit"), seg=20, ol=0),
         T.cyl(name + "_tuit", (0, 0, 0.215), 0.012, 0.03, P.m("wit"), r2=0.007, seg=12, ol=0)]
    o = T.merge(name, p, ol=0.003)
    o.location = loc
    return o


def waterglas(name, loc, vol=0.7, rot=(0, 0, 0)):
    """Drinkglas met water. Het water is een apart object (..._water) voor de animatie."""
    g = T.cyl(name, (0, 0, 0), 0.034, 0.11, water("glas"), seg=24, r2=0.04, ol=0, cap=True)
    w = T.cyl(name + "_water", (0, 0, 0.004), 0.031, 0.105 * vol, water("water"), seg=24, r2=0.031 + 0.006 * vol, ol=0)
    w.parent = g
    g.location = loc
    g.rotation_euler = Euler([math.radians(a) for a in rot])
    return g


def kapotte_sneaker(name, loc, rot=0, color=(0.85, 0.12, 0.12)):
    """Sneaker na een sprint op 250 km/u: losse zool, zwart geschroeide neus, gat in de hiel."""
    burnt = T.toon("geschroeid", (0.06, 0.05, 0.05))
    s = [T.box(name + "_zool", (0.02, 0, 0), (0.25, 0.11, 0.03), P.m("wit"), bevel=0.012, ol=0),
         T.box(name + "_zool_los", (0.16, 0, 0.0), (0.1, 0.105, 0.012), burnt, rot=(0, 14, 0), bevel=0.004, ol=0),
         T.box(name + "_body", (-0.03, 0, 0.03), (0.22, 0.1, 0.07), T.toon("sneaker_rood", color), bevel=0.03, ol=0),
         T.box(name + "_hiel", (-0.1, 0, 0.03), (0.08, 0.1, 0.11), T.toon("sneaker_rood", color), bevel=0.03, ol=0),
         T.box(name + "_neus", (0.1, 0, 0.03), (0.08, 0.1, 0.04), burnt, bevel=0.02, ol=0),
         T.sphere(name + "_gat", (-0.14, 0.0, 0.08), 0.025, burnt, scale=(0.4, 1, 1), seg=10, ol=0),
         T.box(name + "_veter", (0.0, 0, 0.1), (0.08, 0.06, 0.008), P.m("wit"), bevel=0.003, ol=0)]
    o = T.merge(name, s, ol=0.004)
    o.location = loc
    o.rotation_euler.z = math.radians(rot)
    return o


def aansteker(name, loc, rot=(0, 0, 0)):
    """Lange keukenaansteker (mama steekt de kaarsjes aan)."""
    p = [T.box(name + "_greep", (0, 0, 0), (0.12, 0.025, 0.035), T.toon("aansteker", (0.95, 0.35, 0.1)), bevel=0.01, ol=0),
         T.cyl(name + "_buis", (0.06, 0, 0.02), 0.005, 0.15, P.m("metaal"), rot=(0, 90, 0), seg=8, ol=0),
         T.box(name + "_trekker", (0.0, 0, -0.012), (0.03, 0.015, 0.02), P.m("zwart"), bevel=0.004, ol=0)]
    o = T.merge(name, p, ol=0.003)
    o.location = loc
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    return o


def cadeau(name, loc, size=(0.32, 0.24, 0.2), color=(0.15, 0.45, 0.95), lint=(0.98, 0.85, 0.15), rot_z=0):
    """Ingepakt cadeau met lint en strik (van opa en oma)."""
    sx, sy, sz = size
    L = T.toon("lint_" + str(lint), lint)
    p = [T.box(name + "_doos", (0, 0, 0), size, T.toon("cadeaupapier_" + str(color), color), bevel=0.01, ol=0),
         T.box(name + "_lint1", (0, 0, -0.001), (0.03, sy + 0.004, sz + 0.004), L, bevel=0, ol=0),
         T.box(name + "_lint2", (0, 0, -0.001), (sx + 0.004, 0.03, sz + 0.004), L, bevel=0, ol=0),
         T.torus(name + "_strik1", (-0.03, 0, sz + 0.02), 0.03, 0.009, L, rot=(90, 0, 25), seg=16, seg2=6, ol=0),
         T.torus(name + "_strik2", (0.03, 0, sz + 0.02), 0.03, 0.009, L, rot=(90, 0, -25), seg=16, seg2=6, ol=0)]
    o = T.merge(name, p, ol=0.004)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def bordenstapel(name, loc, n=6):
    p = [T.cyl(f"{name}_{k}", (0, 0, k * 0.012), 0.13, 0.011, P.m("wit"), r2=0.12, seg=32, ol=0) for k in range(n)]
    o = T.merge(name, p, ol=0.003)
    o.location = loc
    return o


def bakspullen(name, loc, seed=5):
    """Wat mama klaarzet om de taart te bakken: twee bakvormen, mengkom met garde,
    zak bloem, doos eieren. loc = midden op het aanrecht."""
    rnd = random.Random(seed)
    objs = []
    for k in range(2):
        objs.append(T.cyl(f"{name}_bakvorm{k}", (-0.45 + k * 0.05, -0.05 + k * 0.03, k * 0.05), 0.12, 0.05, P.m("metaal"), seg=32, cap=True, ol=0))
    bowl = [T.cyl(f"{name}_kom", (0, 0, 0), 0.07, 0.11, T.toon("mengkom", (0.95, 0.95, 0.97)), r2=0.14, seg=32, ol=0),
            T.cyl(f"{name}_beslag", (0, 0, 0.085), 0.125, 0.012, T.toon("beslag", (0.98, 0.88, 0.62)), seg=32, ol=0),
            T.cyl(f"{name}_garde", (0.05, 0, 0.1), 0.008, 0.25, P.m("metaal"), rot=(0, 30, 0), seg=8, ol=0)]
    objs.append(T.merge(f"{name}_mengkom", bowl, ol=0.003))
    flour = [T.box(f"{name}_bloem_zak", (0, 0, 0), (0.14, 0.09, 0.22), paper("bloemzak", (0.95, 0.93, 0.86)), bevel=0.02, ol=0),
             T.box(f"{name}_bloem_band", (0, -0.0455, 0.07), (0.12, 0.002, 0.07), T.toon("bloem_label", (0.15, 0.45, 0.85)), bevel=0, ol=0)]
    fo = T.merge(f"{name}_bloem", flour, ol=0.003)
    fo.location = (0.28, 0.08, 0)
    objs.append(fo)
    eggs = [T.box(f"{name}_eierdoos", (0, 0, 0), (0.2, 0.1, 0.04), paper("eierdoos", (0.72, 0.66, 0.55)), bevel=0.01, ol=0)]
    for k in range(6):
        eggs.append(T.sphere(f"{name}_ei{k}", (-0.065 + (k % 3) * 0.065, -0.025 + (k // 3) * 0.05, 0.05), 0.022, T.toon("ei", (0.92, 0.78, 0.6)), scale=(1, 1, 1.3), seg=12, ol=0))
    eo = T.merge(f"{name}_eieren", eggs, ol=0.003)
    eo.location = (0.5, -0.02, 0)
    eo.rotation_euler.z = math.radians(rnd.uniform(-10, 10))
    objs.append(eo)
    return T.group(name, objs, loc=loc)


# ---------------------------------------------------------------------------
# Regen die stilhangt en glas dat wegvliegt
# ---------------------------------------------------------------------------
def regendruppels(name, bounds, n, seed=7, r=0.006, rek=2.2, dicht_bij=None):
    """Regendruppels die stil in de lucht hangen, als één mesh. bounds = ((x0,x1),(y0,y1),(z0,z1)).
    dicht_bij = (punt, straal, extra): nog 'extra' druppels rond een punt (bv. de camera of zijn hand)."""
    rnd = random.Random(seed)
    pts = [tuple(rnd.uniform(*b) for b in bounds) for _ in range(n)]
    if dicht_bij:
        c, rad, extra = dicht_bij
        for _ in range(extra):
            v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized() * rad * rnd.random() ** 0.5
            pts.append(tuple(Vector(c) + v))
    # één druppel als sjabloon, daarna snel kopiëren (bmesh-ops per druppel worden traag bij duizenden)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0)
    tv = [Vector((v.co.x, v.co.y, v.co.z * rek + (0.6 if v.co.z < 0 else 0))) for v in bm.verts]
    tf = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    verts, faces = [], []
    for p in pts:
        s = r * rnd.uniform(0.7, 1.3)
        o = len(verts)
        pv = Vector(p)
        verts.extend(tuple(pv + c * s) for c in tv)
        faces.extend([i + o for i in f] for f in tf)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for f in me.polygons:
        f.use_smooth = True
    me.materials.append(water("regendruppel"))
    o = bpy.data.objects.new(name, me)
    T._link(o)
    return o


def glasscherven_lucht(name, center, n, spread=(1.5, 0.6, 1.0), richting=(0, -1, 0), seed=8, size=0.04):
    """Glasscherven die naar buiten wegvliegen en stilhangen (de knal op dag 3)."""
    rnd = random.Random(seed)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    d = Vector(richting).normalized()
    for _ in range(n):
        t = rnd.random()
        p = Vector(center) + d * t * 2.5 + Vector((rnd.gauss(0, spread[0] * (0.4 + t)), rnd.gauss(0, spread[1] * (0.4 + t)),
                                                   rnd.gauss(0, spread[2] * (0.4 + t))))
        s = size * rnd.uniform(0.4, 1.4)
        vs = [bm.verts.new(p + Vector((rnd.uniform(-s, s), rnd.uniform(-s, s) * 0.2, rnd.uniform(-s, s)))) for _ in range(3)]
        bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(water("glasscherf"))
    o = bpy.data.objects.new(name, me)
    o.rotation_euler = (0, 0, 0)
    T._link(o)
    return o


def vlaggenlijn(name, a, b, sag=0.25, n=14, colors=None):
    """Slinger met driehoekige vlaggetjes tussen twee punten."""
    colors = colors or PAPIER[:7]
    pts = P.catenary(Vector(a), Vector(b), sag, n * 2)
    objs = [T.to_mesh(T.tube(name + "_touw", [tuple(p) for p in pts], 0.004, P.m("wit")))]
    for k in range(n):
        p0, p1 = pts[2 * k], pts[min(2 * k + 2, len(pts) - 1)]
        mid = (p0 + p1) / 2
        v = [tuple(p0), tuple(p1), tuple(mid + Vector((0, 0, -0.16)))]
        objs.append(T.mesh_from(f"{name}_vlag{k}", v, [(0, 1, 2)], paper(f"vlag{k % len(colors)}", colors[k % len(colors)])))
    return T.merge(name, objs, ol=0.003)
