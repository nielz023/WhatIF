"""Stad, straat en terugkerende props voor video 3 "What IF There Were NO RULES?".

Alles in de glans-look (via toon.py). Waar de animatie iets moet kunnen aan- of uitzetten,
staat dat in een eigen object of materiaal met een duidelijke naam:

- verkeerslicht: materialen "<naam>_rood/_oranje/_groen" (Emission Strength keyframen; 0 = uit)
- reclameborden: kinderen "<naam>_reclame" en "<naam>_alarm" (zichtbaarheid wisselen)
- gebouwen: ramen per gebouw in "<naam>_ramen_licht" (materiaal "ramen_<blok>", sterkte keyframen)
- lantaarns: materiaal "lantaarn_<blok>" + puntlampen in collectie "Lantaarnlicht_<blok>"
- slagboom: kind "<naam>_arm" draait om zijn scharnier (rotation_euler.y)
- pillendoosje: dekseltjes "<naam>_deksel_MON".."SUN" (rotation_euler.x openen)
- fietslamp: materiaal "<naam>_lamp" + spotlicht "<naam>_lichtbundel"
"""
import math
import random

import bpy
import bmesh
from mathutils import Vector, Euler

from . import toon as T
from . import props as P
from . import huis as HU

FONT_BOLD = None


def _m(name, col):
    return T.toon(name, col)


def _glowmat(name, col, strength):
    """Eigen (niet gedeeld) lichtgevend materiaal, zodat de sterkte per stuk te animeren is."""
    mt = bpy.data.materials.get(name)
    if mt:
        return mt
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N = mt.node_tree.nodes
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*col, 1)
    em.inputs["Strength"].default_value = strength
    mt.node_tree.links.new(em.outputs[0], out.inputs["Surface"])
    mt.diffuse_color = (*col, 1)
    return mt


def _empty(name, loc=(0, 0, 0), rot=None, size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = size
    e.location = loc
    if rot is not None:
        e.rotation_euler = Euler([math.radians(a) for a in rot])
    T._link(e)
    return e


def _parent(objs, par):
    for o in objs:
        if o is not None and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = par
            o.matrix_parent_inverse = par.matrix_world.inverted()
            o.matrix_world = mw


def _place(o, loc, rot_z=0.0):
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def _bold():
    global FONT_BOLD
    if FONT_BOLD is None:
        import os
        fp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "InterDisplay-Bold.otf")
        FONT_BOLD = bpy.data.fonts.load(fp, check_existing=True) if os.path.exists(fp) else False
    return FONT_BOLD or None


def label(name, text, loc, size, col=(1, 1, 1), rot=(90, 0, 0), glow=0.0, extrude=0.004, align="CENTER", bold=True):
    """Tekst in de vette bordletter (Inter Display Bold, wordt in de .blend ingepakt)."""
    mat = _glowmat(f"tekst_{name}", col, glow) if glow else _m("tekst_" + "%.2f%.2f%.2f" % col, col)
    o = T.text(name, text, loc, size, mat, rot=rot, extrude=extrude, align=align)
    f = _bold() if bold else None
    if f:
        o.data.font = f
    return o


# ---------------------------------------------------------------------------
# Borden met tekst
# ---------------------------------------------------------------------------
def sign(name, lines, loc, rot_z=0.0, w=0.9, h=0.5, bg=(0.10, 0.45, 0.22), fg=(0.97, 0.97, 0.95),
         post_h=0.9, post=True, size=None, knocked=False, marker=False, border=True):
    """Bord op een paaltje (KEEP OFF THE GRASS, NO DOGS ...). Nulpunt = voet van de paal.
    knocked=True: het bord ligt plat in het gras (scène 8g)."""
    root = _empty(name, size=0.2)
    parts = []
    if post:
        parts.append(T.box(name + "_paal", (0, 0.03, 0), (0.06, 0.06, post_h + h * 0.5), _m("bordpaal_hout", (0.45, 0.30, 0.18)), bevel=0.01, ol=0))
    zc = post_h + h / 2 if post else h / 2
    parts.append(T.box(name + "_plaat", (0, 0, zc - h / 2), (w, 0.03, h), _m(f"bordplaat_{name}", bg), bevel=0.012, ol=0))
    if border:
        parts.append(T.box(name + "_rand", (0, 0.004, zc - h / 2 - 0.012), (w + 0.04, 0.026, h + 0.024), _m("bordrand_wit", fg), bevel=0.012, ol=0))
    s = size or min(h / (len(lines) + 0.6) * 0.62, w / max(len(l) for l in lines) * 1.45)
    n = len(lines)
    for i, ln in enumerate(lines):
        z = zc + (n / 2 - i - 1) * s * 1.35 + s * 0.12
        if marker:
            t = HU.marker_text(f"{name}_tekst{i + 1}", ln, (0, -0.017, z), s, "wit")
        else:
            t = label(f"{name}_tekst{i + 1}", ln, (0, -0.017, z), s, fg)
        parts.append(t)
    for p in parts:
        p.parent = root
    root.location = loc
    if knocked:
        root.rotation_euler = (math.radians(-88), 0, math.radians(rot_z))  # voorkant omhoog
        root.location.z += 0.03
    else:
        root.rotation_euler.z = math.radians(rot_z)
    return root


def wall_sign(name, lines, loc, rot_z=0.0, w=1.2, h=0.5, bg=(0.95, 0.95, 0.93), fg=(0.1, 0.1, 0.12)):
    return sign(name, lines, loc, rot_z, w, h, bg, fg, post=False, border=False)


# ---------------------------------------------------------------------------
# Verkeer
# ---------------------------------------------------------------------------
LIGHT_STATES = {"rood": (1, 0, 0), "oranje": (0, 1, 0), "groen": (0, 0, 1), "alles": (1, 1, 1), "knipper": (0, 1, 0), "uit": (0, 0, 0)}


def traffic_light(name, loc, rot_z=0.0, state="rood", arm=4.5, h=5.2):
    """Verkeerslicht met een arm over de weg (kijkt naar -y). De drie lampen hebben eigen
    materialen <naam>_rood/_oranje/_groen: Emission Strength 0 = uit, ~8 = aan."""
    root = _empty(name)
    pole = _m("verkeerspaal", (0.20, 0.21, 0.23))
    parts = [T.cyl(name + "_paal", (0, 0, 0), 0.09, h, pole, seg=14, ol=0),
             T.cyl(name + "_voet", (0, 0, 0), 0.18, 0.25, pole, r2=0.12, seg=14, ol=0),
             T.cyl(name + "_arm", (0, 0, h - 0.2), 0.065, arm, pole, rot=(0, 90, 0), seg=12, ol=0)]
    on = LIGHT_STATES[state]
    for kx, x in enumerate((arm * 0.55, arm - 0.25)):
        hz = h - 0.25
        parts.append(T.box(f"{name}_kast{kx}", (x, 0, hz - 1.05), (0.42, 0.34, 1.15), _m("verkeerslicht_kast", (0.10, 0.10, 0.11)), bevel=0.05, ol=0))
        parts.append(T.box(f"{name}_achterplaat{kx}", (x, 0.04, hz - 1.15), (0.62, 0.04, 1.35), _m("verkeerslicht_plaat", (0.08, 0.08, 0.09)), bevel=0.02, ol=0))
        for i, (col_n, col) in enumerate((("rood", (1.0, 0.05, 0.02)), ("oranje", (1.0, 0.45, 0.02)), ("groen", (0.05, 1.0, 0.35)))):
            mat = _glowmat(f"{name}_{col_n}", col, 9.0 if on[i] else 0.0)
            zz = hz - 0.27 - i * 0.36
            parts.append(T.cyl(f"{name}_lamp_{col_n}{kx}", (x, -0.17, zz), 0.13, 0.03, mat, rot=(90, 0, 0), seg=20, ol=0))
            parts.append(T.cyl(f"{name}_kapje_{col_n}{kx}", (x, -0.2, zz + 0.06), 0.15, 0.16, _m("verkeerslicht_kast", (0.10, 0.10, 0.11)), rot=(90, 0, 0), seg=16, ol=0, cap=False))
    for p in parts:
        p.parent = root
    _place(root, loc, rot_z)
    # licht van de brandende lampen op straat
    if any(on):
        col = (1.0, 0.1, 0.03) if on[0] and not on[1] else (1.0, 0.5, 0.05) if on[1] and not on[2] else (0.1, 1.0, 0.4)
        lt = T.point_light(name + "_schijnsel", (0, 0, 0), color=col, energy=350, radius=0.3, shadow=False)
        lt.parent = root
        lt.location = (arm * 0.8, -0.6, h - 0.9)
    return root


def ped_light(name, loc, rot_z=0.0, state="rood"):
    """Voetgangerslicht: rood of groen poppetje (materialen <naam>_rood/_groen)."""
    root = _empty(name)
    pole = _m("verkeerspaal", (0.20, 0.21, 0.23))
    parts = [T.cyl(name + "_paal", (0, 0, 0), 0.06, 2.6, pole, seg=12, ol=0),
             T.box(name + "_kast", (0, -0.05, 2.0), (0.32, 0.22, 0.75), _m("verkeerslicht_kast", (0.10, 0.10, 0.11)), bevel=0.03, ol=0),
             T.box(name + "_drukknop", (0, -0.08, 1.05), (0.14, 0.12, 0.22), _m("drukknop_geel", (0.95, 0.78, 0.1)), bevel=0.02, ol=0)]
    for i, (cn, col) in enumerate((("rood", (1.0, 0.05, 0.03)), ("groen", (0.1, 1.0, 0.4)))):
        on = (state == "rood") == (i == 0)
        mat = _glowmat(f"{name}_{cn}", col, 6.0 if on else 0.0)
        z = 2.48 - i * 0.34
        parts.append(T.box(f"{name}_vak_{cn}", (0, -0.165, z - 0.14), (0.24, 0.02, 0.28), _m("verkeerslicht_plaat", (0.05, 0.05, 0.05)), bevel=0, ol=0))
        # poppetje: hoofd + lijf + benen
        parts.append(T.sphere(f"{name}_pop_hoofd_{cn}", (0, -0.178, z + 0.07), 0.025, mat, seg=10, ol=0))
        parts.append(T.box(f"{name}_pop_lijf_{cn}", (0, -0.178, z - 0.06), (0.05, 0.01, 0.1), mat, bevel=0, ol=0))
        for s in (-1, 1):
            parts.append(T.box(f"{name}_pop_been_{cn}{s}", (s * (0.02 if i == 0 else 0.035), -0.178, z - 0.13), (0.018, 0.01, 0.075), mat,
                               rot=(0, s * (0 if i == 0 else 20), 0), bevel=0, ol=0))
    for p in parts:
        p.parent = root
    return _place(root, loc, rot_z)


def crosswalk(name, center, width, length, rot_z=0.0, stripe=0.5):
    """Zebrapad: witte strepen dwars op de rijrichting."""
    parts = []
    n = int(width / (stripe * 2))
    for i in range(n):
        x = -width / 2 + stripe / 2 + i * stripe * 2
        parts.append(T.plane(f"{name}_{i}", (x, 0, 0.006), (stripe, length), _m("wegverf_wit", (0.92, 0.92, 0.9))))
    o = T.merge(name, parts, ol=0)
    return _place(o, center, rot_z)


# ---------------------------------------------------------------------------
# Auto (glans 2: velgen, grille, spiegels, deuren die open kunnen)
# ---------------------------------------------------------------------------
def car2(name, loc, rot=0.0, color=(0.1, 0.35, 0.8), kind="hatch", doors_open=(), lights=False, phone=False, open_cab=False):
    """Auto van 4,2 m, kijkt naar +x. doors_open: ("L", "R") voor open voordeuren (scène 12a).
    open_cab=True: holle cabine (dak, stijlen, doorzichtige ruiten) zodat je de bestuurder ziet zitten.
    Deuren zijn eigen objecten (<naam>_deur_L/_R) met hun scharnier aan de voorkant."""
    root = _empty(name, size=0.5)
    body = _m(f"autolak_{'%.2f%.2f%.2f' % color}", color)
    glass = _m("autoruit", (0.10, 0.15, 0.22))
    rub = _m("autorubber", (0.06, 0.06, 0.07))
    chrome = _m("chroom_auto", (0.8, 0.82, 0.85))
    L, W = 4.15, 1.78
    cab_x, cab_l = (-0.25, 2.3) if kind == "hatch" else (-0.05, 2.0) if kind == "sedan" else (-0.15, 2.6)
    cab_h = 0.62 if kind != "suv" else 0.72
    base_h = 0.62 if kind != "suv" else 0.78
    p = [T.box(name + "_onder", (0, 0, 0.3), (L, W, base_h), body, bevel=0.16, ol=0),
         T.box(name + "_bumper_v", (L / 2 - 0.05, 0, 0.26), (0.18, W - 0.05, 0.22), rub, bevel=0.06, ol=0),
         T.box(name + "_bumper_a", (-L / 2 + 0.05, 0, 0.26), (0.18, W - 0.05, 0.22), rub, bevel=0.06, ol=0),
         T.box(name + "_grille", (L / 2 + 0.01, 0, 0.5), (0.04, 0.8, 0.16), rub, bevel=0.02, ol=0),
         T.box(name + "_kenteken_v", (L / 2 + 0.05, 0, 0.3), (0.02, 0.5, 0.11), _m("kenteken_geel", (0.95, 0.8, 0.1)), bevel=0, ol=0),
         T.box(name + "_kenteken_a", (-L / 2 - 0.05, 0, 0.32), (0.02, 0.5, 0.11), _m("kenteken_geel", (0.95, 0.8, 0.1)), bevel=0, ol=0)]
    z0, z1 = 0.3 + base_h - 0.04, 0.3 + base_h - 0.04 + cab_h
    if open_cab:
        # cabrio: geen dak, alleen een voorruit met stijlen (zo zie je de bestuurder helemaal)
        gl = T.glass("autoruit_open", (0.70, 0.82, 0.92), 0.18)
        x1, w2 = cab_x + cab_l / 2, (W - 0.16) / 2
        for yy in (w2 - 0.04, -w2 + 0.04):
            p.append(T.box(f"{name}_stijl{yy:.2f}", (x1 - 0.1, yy, z0), (0.06, 0.06, 0.42), body, rot=(0, -25, 0), bevel=0.02, ol=0))
        p += [T.box(name + "_ruit_voor", (x1 - 0.1, 0, z0 + 0.02), (0.02, W - 0.3, 0.36), gl, rot=(0, -25, 0), bevel=0, ol=0),
              T.box(name + "_ruitlijst", (x1 - 0.02, 0, z0 + 0.4), (0.06, W - 0.2, 0.05), body, rot=(0, -25, 0), bevel=0.02, ol=0)]
    else:
        p += [T.box(name + "_cabine", (cab_x, 0, z0), (cab_l, W - 0.16, cab_h), body, bevel=0.14, ol=0),
              T.box(name + "_ruiten", (cab_x, 0, 0.3 + base_h + 0.02), (cab_l + 0.03, W - 0.13, cab_h - 0.14), glass, bevel=0.08, ol=0)]
    headl = _glowmat(f"{name}_koplampen", (1.0, 0.95, 0.85), 6.0 if lights else 0.0)
    for y in (0.6, -0.6):
        p.append(T.sphere(f"{name}_koplamp{y}", (L / 2 - 0.02, y, 0.62), 0.13, headl, scale=(0.35, 1.0, 0.55), seg=12, ol=0))
        p.append(T.box(f"{name}_achterlicht{y}", (-L / 2 - 0.01, y * 1.05, 0.66), (0.04, 0.3, 0.12),
                       _m("achterlicht_rood", (0.8, 0.05, 0.04)), bevel=0.02, ol=0))
        # spiegels
        p.append(T.box(f"{name}_spiegel{y}", (cab_x + cab_l / 2 - 0.15, y * 1.62, 0.3 + base_h + 0.05), (0.16, 0.14, 0.12), body, bevel=0.04, ol=0))
    for i, (x, y) in enumerate([(1.3, 1), (-1.3, 1), (1.3, -1), (-1.3, -1)]):
        yy = y * (W / 2 - 0.08)
        p.append(T.cyl(f"{name}_band{i}", (x, yy - y * 0.12, 0.35), 0.35, 0.24, rub, rot=(90, 0, 0), seg=24, ol=0, bevel=0.03))
        p.append(T.cyl(f"{name}_velg{i}", (x, yy + y * 0.125, 0.35), 0.22, 0.02, chrome, rot=(90, 0, 0), seg=20, ol=0))
        p.append(T.cyl(f"{name}_naaf{i}", (x, yy + y * 0.14, 0.35), 0.06, 0.02, rub, rot=(90, 0, 0), seg=12, ol=0))
        # wielkast
        p.append(T.cyl(f"{name}_wielkast{i}", (x, yy - y * 0.15, 0.36), 0.42, 0.3, rub, rot=(90, 0, 0), seg=24, ol=0, cap=False))
    # stoelen binnen (door de ruit en bij open deuren zichtbaar)
    for y in (0.4, -0.4):
        p.append(T.box(f"{name}_stoel{y}", (cab_x + 0.25, y, 0.62), (0.5, 0.48, 0.18), _m("autostoel", (0.16, 0.16, 0.18)), bevel=0.05, ol=0))
        p.append(T.box(f"{name}_leuning{y}", (cab_x - 0.05, y, 0.75), (0.12, 0.46, 0.6), _m("autostoel", (0.16, 0.16, 0.18)), rot=(0, -12, 0), bevel=0.05, ol=0))
    p.append(T.box(name + "_dashboard", (cab_x + cab_l / 2 - 0.2, 0, 0.82), (0.35, W - 0.3, 0.22), rub, bevel=0.05, ol=0))
    p.append(T.torus(name + "_stuur", (cab_x + cab_l / 2 - 0.45, 0.4, 1.0), 0.17, 0.022, rub, rot=(0, 65, 0), seg=24, seg2=8, ol=0))
    o = T.merge(name + "_carrosserie", p, ol=0)
    o.parent = root
    # deuren (zijpanelen die open kunnen)
    for side, y in (("L", 1), ("R", -1)):
        hinge_x = cab_x + cab_l / 2 - 0.1
        d = _empty(f"{name}_deur_{side}", (hinge_x, y * (W / 2 + 0.01), 0.3), size=0.15)
        d.parent = root
        dp = [T.box(f"{name}_deurpaneel_{side}", (-0.55, 0, 0.05), (1.1, 0.04, base_h - 0.1), body, bevel=0.03, ol=0),
              T.box(f"{name}_deurruit_{side}", (-0.55, 0, base_h - 0.04), (1.0, 0.03, cab_h - 0.16), glass, bevel=0.02, ol=0) if not open_cab else
              T.box(f"{name}_deurrand_{side}", (-0.55, 0, base_h - 0.06), (1.1, 0.05, 0.05), body, bevel=0.02, ol=0),
              T.box(f"{name}_deurgreep_{side}", (-0.85, y * 0.03, base_h - 0.2), (0.16, 0.03, 0.04), chrome, bevel=0.01, ol=0)]
        dm = T.merge(f"{name}_deurblad_{side}", dp, ol=0)
        dm.parent = d
        if side in doors_open:
            d.rotation_euler.z = math.radians(-60 * y)
    if phone:
        # telefoon op het dashboard die rood oplicht (scène 1d)
        ph = T.box(name + "_telefoon", (cab_x + cab_l / 2 - 0.25, 0.2, 0.95), (0.08, 0.16, 0.01), _glowmat(f"{name}_telefoonscherm", (1.0, 0.05, 0.03), 8.0), rot=(0, -20, 0), bevel=0, ol=0)
        ph.parent = root
    _place(root, loc, rot)
    return root


# ---------------------------------------------------------------------------
# Gebouwen
# ---------------------------------------------------------------------------
def building(name, loc, w=12.0, d=10.0, floors=5, color=(0.72, 0.60, 0.50), lit=0.0, seed=0, rot_z=0.0,
             shop=None, shop_color=(0.15, 0.35, 0.7), block="A", glass_col=(0.40, 0.55, 0.70), roof=True):
    """Stadsflat met raampjes; de gevel kijkt naar -y. Ramen die branden zitten in één object
    "<naam>_ramen_licht" met materiaal "ramen_<blok>" (sterkte keyframen = blok gaat uit)."""
    rnd = random.Random(seed)
    root = _empty(name, size=1.0)
    fh = 3.1
    h = floors * fh + 1.0
    wall = _m(f"gevel_{'%.2f%.2f%.2f' % color}", color)
    trim = _m("gevel_lijst", (0.88, 0.86, 0.82))
    p = [T.box(name + "_romp", (0, d / 2, 0), (w, d, h), wall, bevel=0.04, ol=0)]
    if roof:
        p.append(T.box(name + "_daklijst", (0, d / 2, h), (w + 0.3, d + 0.3, 0.35), trim, bevel=0.03, ol=0))
        if rnd.random() < 0.6:
            p.append(T.box(name + "_dakopbouw", (rnd.uniform(-w / 4, w / 4), d * 0.6, h + 0.35), (2.2, 2.2, 1.6), trim, bevel=0.03, ol=0))
    lit_wins, dark_wins = [], []
    cols = max(2, int(w / 2.2))
    start_floor = 1 if shop else 0
    for f in range(start_floor, floors):
        z = 1.0 + f * fh + 0.6
        p.append(T.box(f"{name}_verdieping{f}", (0, -0.05, z - 0.7), (w + 0.04, 0.12, 0.14), trim, bevel=0.01, ol=0))
        for c in range(cols):
            x = -w / 2 + (c + 0.5) * w / cols
            p.append(T.box(f"{name}_kozijn{f}_{c}", (x, -0.03, z - 0.06), (1.3, 0.08, 1.62), trim, bevel=0.01, ol=0))
            (lit_wins if rnd.random() < lit else dark_wins).append((x, z))
    gl = _m(f"flatraam_{'%.2f%.2f%.2f' % glass_col}", glass_col)
    for k, lst in (("licht", lit_wins), ("donker", dark_wins)):
        if not lst:
            continue
        mat = _glowmat(f"ramen_{block}", (1.0, 0.78, 0.45), 2.2) if k == "licht" else gl
        ws = [T.box(f"{name}_raam_{k}{i}", (x, -0.075, z), (1.1, 0.02, 1.4), mat, bevel=0, ol=0) for i, (x, z) in enumerate(lst)]
        o = T.merge(f"{name}_ramen_{k}", ws, ol=0)
        o.parent = root
    if shop:
        p.append(T.box(name + "_pui", (0, -0.06, 0), (w - 0.3, 0.1, 3.0), _m("pui_glas", (0.20, 0.28, 0.36)), bevel=0.02, ol=0))
        p.append(T.box(name + "_luifel", (0, -0.6, 3.0), (w - 0.2, 1.2, 0.12), _m(f"luifel_{'%.2f%.2f%.2f' % shop_color}", shop_color), bevel=0.03, ol=0))
        p.append(T.box(name + "_winkelbord", (0, -0.14, 3.15), (min(w - 1, 8), 0.12, 0.7), _m(f"luifel_{'%.2f%.2f%.2f' % shop_color}", shop_color), bevel=0.03, ol=0))
        t = label(name + "_winkelnaam", shop, (0, -0.215, 3.28), 0.42, (1, 1, 1), extrude=0.02)
        t.parent = root
        p.append(T.box(name + "_deur", (w / 2 - 1.5, -0.12, 0), (1.4, 0.05, 2.5), _m("winkeldeur", (0.12, 0.14, 0.16)), bevel=0.01, ol=0))
    o = T.merge(name + "_gebouw", p, ol=0)
    o.parent = root
    _place(root, loc, rot_z)
    root["blok"] = block
    return root


def billboard(name, loc, rot_z=0.0, w=6.0, h=3.2, z=6.0, ad=("SUMMER SALE", "-50%"), ad_col=(0.98, 0.75, 0.15),
              alarm=("THERE ARE", "NO MORE RULES"), mode="reclame", wall=False):
    """Groot scherm (reclamebord). Kinderen <naam>_reclame en <naam>_alarm: wissel de
    zichtbaarheid om het bord naar rood te laten 'omklappen' (scène 1a)."""
    root = _empty(name, size=1.0)
    fr = _m("billboard_frame", (0.14, 0.15, 0.17))
    parts = [T.box(name + "_frame", (0, 0.08, z - 0.15), (w + 0.3, 0.25, h + 0.3), fr, bevel=0.04, ol=0)]
    if not wall:
        parts.append(T.cyl(name + "_paal", (0, 0.2, 0), 0.22, z, fr, seg=16, ol=0))
    for p in parts:
        p.parent = root
    for kind, lines, bg, fg, st in (("reclame", ad, ad_col, (0.08, 0.08, 0.1), 2.2), ("alarm", alarm, (0.85, 0.02, 0.02), (1.0, 0.95, 0.9), 2.6)):
        g = _empty(f"{name}_{kind}", (0, 0, 0), size=0.3)
        g.parent = root
        scr = T.box(f"{name}_{kind}_scherm", (0, -0.06, z), (w, 0.04, h), _glowmat(f"{name}_{kind}_licht", bg, st), bevel=0, ol=0)
        scr.parent = g
        n = len(lines)
        s = min(h / (n + 1) * 0.8, w / max(len(l) for l in lines) * 1.35)
        for i, ln in enumerate(lines):
            tz = z + h - (i + 1) * h / (n + 1) - s * 0.35
            t = label(f"{name}_{kind}_tekst{i + 1}", ln, (0, -0.09, tz), s, fg, glow=9.0 if kind == "alarm" else 0.0, extrude=0.005)
            t.parent = g
        vis = kind == mode
        for o in [g] + list(g.children):
            o.hide_render = not vis
            o.hide_viewport = not vis
    _place(root, loc, rot_z)
    if mode == "alarm":
        lt = T.area_light(name + "_rood_schijnsel", (0, 0, 0), (0, -1, 0), size=(w, h), color=(1.0, 0.05, 0.03), energy=2500)
        lt.parent = root
        lt.location = (0, -0.6, z)
        lt.rotation_euler = (math.radians(90), 0, 0)
    return root


def street_lamp(name, loc, rot_z=0.0, on=True, block="A", h=6.0, energy=450):
    """Moderne straatlantaarn met arm. Kap-materiaal "lantaarn_<blok>"; het licht hangt in
    collectie "Lantaarnlicht_<blok>", zodat een heel blok tegelijk uit kan (dag 4)."""
    root = _empty(name)
    pole = _m("lantaarnpaal", (0.22, 0.24, 0.26))
    p = [T.cyl(name + "_paal", (0, 0, 0), 0.08, h, pole, r2=0.06, seg=12, ol=0),
         T.cyl(name + "_voet", (0, 0, 0), 0.16, 0.6, pole, r2=0.1, seg=12, ol=0),
         T.to_mesh(T.tube(name + "_arm", [(0, 0, h - 0.1), (0, -0.6, h + 0.25), (0, -1.4, h + 0.25)], 0.045, pole)),
         T.box(name + "_kap", (0, -1.5, h + 0.08), (0.35, 0.7, 0.16), pole, bevel=0.05, ol=0)]
    o = T.merge(name + "_mast", p, ol=0)
    o.parent = root
    mat = _glowmat(f"lantaarn_{block}", (1.0, 0.78, 0.48), 12.0 if on else 0.0)
    bulb = T.box(name + "_lamp", (0, -1.5, h + 0.04), (0.28, 0.56, 0.04), mat, bevel=0.01, ol=0)
    bulb.parent = root
    _place(root, loc, rot_z)
    if on:
        cname = f"Lantaarnlicht_{block}"
        c = bpy.data.collections.get(cname)
        if c is None:
            c = bpy.data.collections.new(cname)
            bpy.context.scene.collection.children.link(c)
        ld = bpy.data.lights.new(name + "_licht", "SPOT")
        ld.energy = energy
        ld.color = (1.0, 0.75, 0.45)
        ld.spot_size = math.radians(110)
        ld.spot_blend = 0.6
        ld.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(name + "_licht", ld)
        c.objects.link(lo)
        lo.parent = root
        lo.location = (0, -1.5, h - 0.05)
        lo.rotation_euler = (0, 0, 0)
    return root


def skyline(name, center, rows=4, per_row=10, seed=3, lit=0.55, spacing=14.0, depth_step=16.0):
    """Achtergrondstad: rijen flats, elke rij een eigen 'blok' (A, B, C ...) voor de
    stroomuitval van dag 4 (blok voor blok op zwart). Rij 0 is het dichtst bij."""
    rnd = random.Random(seed)
    cols = [(0.62, 0.58, 0.55), (0.52, 0.55, 0.62), (0.70, 0.62, 0.50), (0.45, 0.48, 0.52), (0.78, 0.74, 0.68)]
    out = []
    for r in range(rows):
        blk = "ABCDEFGH"[r]
        for i in range(per_row):
            x = center[0] + (i - per_row / 2) * spacing + rnd.uniform(-2, 2)
            y = center[1] + r * depth_step + rnd.uniform(-2, 2)
            out.append(building(f"{name}_{blk}{i}", (x, y, 0), w=rnd.uniform(9, 13), d=10, floors=rnd.randint(4 + r, 9 + 2 * r),
                                color=rnd.choice(cols), lit=lit, seed=seed * 100 + r * 20 + i, block=blk, roof=True))
    return out


# ---------------------------------------------------------------------------
# Fiets (glans 2): spaken, trappers, lamp, sticker, jerrycan aan het stuur
# ---------------------------------------------------------------------------
def fiets2(name, loc, rot=0.0, color=(0.85, 0.12, 0.10), lamp_on=False, sticker=False, jerrycan=False, basket=False):
    """Fiets van 1,75 m die naar +x kijkt. Wielen zijn eigen objecten (<naam>_wiel_v/_a,
    rotation_euler.y draaien), het stuur ook (<naam>_stuurdeel, draait om z)."""
    root = _empty(name)
    fm = _m(f"fietsframe_{'%.2f%.2f%.2f' % color}", color)
    blk = _m("fiets_zwart", (0.05, 0.05, 0.06))
    chrome = _m("chroom_fiets", (0.82, 0.84, 0.86))
    R = 0.34
    for wn, x in (("v", 0.55), ("a", -0.55)):
        w = _empty(f"{name}_wiel_{wn}", (x, 0, R), size=0.2)
        w.parent = root
        parts = [T.torus(f"{name}_band_{wn}", (0, 0, 0), R - 0.02, 0.028, blk, rot=(90, 0, 0), seg=40, seg2=8, ol=0),
                 T.torus(f"{name}_velg_{wn}", (0, 0, 0), R - 0.055, 0.012, chrome, rot=(90, 0, 0), seg=40, seg2=6, ol=0),
                 T.cyl(f"{name}_naaf_{wn}", (0, -0.05, 0), 0.03, 0.1, chrome, rot=(-90, 0, 0), seg=10, ol=0)]
        for k in range(16):
            a = 2 * math.pi * k / 16
            parts.append(T.to_mesh(T.tube(f"{name}_spaak_{wn}{k}", [(0, 0, 0), ((R - 0.06) * math.cos(a), 0, (R - 0.06) * math.sin(a))], 0.0025, chrome)))
        m = T.merge(f"{name}_wielset_{wn}", parts, ol=0)
        m.parent = w
    fr = []
    for a, b in [((-0.55, 0, R), (-0.08, 0, 0.36)), ((-0.08, 0, 0.36), (0.46, 0, 0.82)), ((-0.16, 0, 0.82), (0.46, 0, 0.82)),
                 ((-0.08, 0, 0.36), (-0.18, 0, 0.88)), ((-0.55, 0, R), (-0.16, 0, 0.82))]:
        fr.append(T.to_mesh(T.tube(f"{name}_buis", [a, b], 0.02, fm)))
    for s in (-1, 1):
        fr.append(T.to_mesh(T.tube(f"{name}_vork{s}", [(0.46, s * 0.04, 0.84), (0.55, s * 0.05, R)], 0.013, fm)))
    fr.append(T.box(name + "_zadel", (-0.21, 0, 0.9), (0.26, 0.13, 0.06), blk, bevel=0.025, ol=0))
    fr.append(T.cyl(name + "_zadelpen", (-0.19, 0, 0.84), 0.012, 0.08, chrome, seg=8, ol=0))
    # trappers en ketting
    fr.append(T.cyl(name + "_tandwiel", (-0.08, 0.05, 0.36), 0.09, 0.01, chrome, rot=(90, 0, 0), seg=20, ol=0))
    for s, a in ((1, 0.0), (-1, math.pi)):
        px, pz = -0.08 + 0.16 * math.cos(a + 0.6), 0.36 + 0.16 * math.sin(a + 0.6)
        fr.append(T.to_mesh(T.tube(f"{name}_crank{s}", [(-0.08, s * 0.07, 0.36), (px, s * 0.07, pz)], 0.012, chrome)))
        fr.append(T.box(f"{name}_trapper{s}", (px, s * 0.11, pz - 0.015), (0.09, 0.08, 0.03), blk, bevel=0.01, ol=0))
    fr.append(T.to_mesh(T.tube(name + "_ketting", [(-0.08, 0.06, 0.45), (-0.55, 0.06, R + 0.04), (-0.55, 0.06, R - 0.04), (-0.08, 0.06, 0.27)], 0.006, blk)))
    # spatborden
    for wn, x in (("v", 0.55), ("a", -0.55)):
        pts = [(x + (R + 0.04) * math.cos(t), 0, R + (R + 0.04) * math.sin(t)) for t in [math.radians(a) for a in range(20, 161, 20)]]
        fr.append(T.to_mesh(T.tube(f"{name}_spatbord_{wn}", pts, 0.03, fm)))
    if sticker:
        fr.append(T.box(name + "_sticker", (0.15, 0.022, 0.62), (0.12, 0.004, 0.06), _m("sticker_geel", (0.98, 0.82, 0.1)), rot=(0, -40, 0), bevel=0, ol=0))
        fr.append(T.sphere(name + "_sticker_ster", (0.15, 0.026, 0.62), 0.022, _m("sticker_blauw", (0.1, 0.35, 0.9)), scale=(1, 0.15, 1), seg=8, ol=0))
    frame = T.merge(name + "_frame", fr, ol=0)
    frame.parent = root
    st = _empty(name + "_stuurdeel", (0.46, 0, 0.84), size=0.15)
    st.parent = root
    sp = [T.to_mesh(T.tube(name + "_stuur", [(-0.06, 0.28, 0.2), (0.0, 0.0, 0.16), (-0.06, -0.28, 0.2)], 0.014, blk)),
          T.cyl(name + "_stuurpen", (0, 0, 0), 0.016, 0.17, chrome, seg=8, ol=0)]
    for s in (-1, 1):
        sp.append(T.cyl(f"{name}_handvat{s}", (-0.06, s * 0.27, 0.2), 0.02, 0.1, blk, rot=(90, 0, 0), seg=10, ol=0))
    lampmat = _glowmat(f"{name}_lamp", (1.0, 0.96, 0.85), 15.0 if lamp_on else 0.0)
    sp.append(T.cyl(name + "_lamphuis", (0.06, 0, 0.0), 0.04, 0.08, blk, rot=(0, 90, 0), seg=14, ol=0))
    sp.append(T.cyl(name + "_lampglas", (0.14, 0, 0.0), 0.034, 0.005, lampmat, rot=(0, 90, 0), seg=14, ol=0))
    if basket:
        sp.append(T.box(name + "_mandje", (0.2, 0, 0.0), (0.3, 0.36, 0.22), _m("mandje_riet", (0.75, 0.55, 0.3)), bevel=0.03, ol=0))
    stm = T.merge(name + "_stuurset", sp, ol=0)
    stm.parent = st
    if jerrycan:
        jc = jerrycan_(name + "_jerrycan", (0.0, 0.22, -0.12), 0.0, scale=0.55)
        jc.parent = st
    _place(root, loc, rot)
    if lamp_on:
        ld = bpy.data.lights.new(name + "_lichtbundel", "SPOT")
        ld.energy = 120
        ld.spot_size = math.radians(40)
        ld.spot_blend = 0.5
        ld.color = (1.0, 0.95, 0.85)
        lo = bpy.data.objects.new(name + "_lichtbundel", ld)
        T._link(lo)
        lo.parent = st
        lo.location = (0.16, 0, 0.0)
        lo.rotation_euler = (0, math.radians(-100), 0)
    return root


def jerrycan_(name, loc, rot_z=0.0, color=(0.15, 0.45, 0.9), scale=1.0):
    """Jerrycan (water, blauw) van 45 cm hoog; nulpunt = handvat (om aan een stuur te hangen)."""
    s = scale
    c = _m(f"jerrycan_{'%.2f%.2f%.2f' % color}", color)
    p = [T.box(name + "_romp", (0, 0, -0.45 * s), (0.17 * s, 0.32 * s, 0.4 * s), c, bevel=0.03 * s, ol=0),
         T.box(name + "_handvat", (0, 0, -0.06 * s), (0.05 * s, 0.2 * s, 0.05 * s), c, bevel=0.015 * s, ol=0),
         T.box(name + "_steun", (0, 0, -0.08 * s), (0.04 * s, 0.04 * s, 0.05 * s), c, bevel=0.01 * s, ol=0),
         T.cyl(name + "_dop", (0, 0.12 * s, -0.06 * s), 0.035 * s, 0.05 * s, _m("jerrycan_dop", (0.95, 0.95, 0.95)), seg=12, ol=0)]
    o = T.merge(name, p, ol=0)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def zaklamp(name, loc, rot=(0, 0, 0), on=True):
    """Zaklamp van de agent (22 cm), schijnt naar +x. Licht: <naam>_bundel."""
    root = _empty(name, size=0.1)
    p = [T.cyl(name + "_greep", (0, 0, 0), 0.022, 0.16, _m("zaklamp_zwart", (0.06, 0.06, 0.07)), rot=(0, 90, 0), seg=14, ol=0),
         T.cyl(name + "_kop", (0.16, 0, 0), 0.032, 0.06, _m("zaklamp_zwart", (0.06, 0.06, 0.07)), r2=0.038, rot=(0, 90, 0), seg=16, ol=0),
         T.cyl(name + "_glas", (0.221, 0, 0), 0.034, 0.003, _glowmat(name + "_licht", (1, 0.97, 0.9), 20 if on else 0), rot=(0, 90, 0), seg=16, ol=0),
         T.box(name + "_knop", (0.07, 0, 0.022), (0.03, 0.015, 0.008), _m("zaklamp_knop", (0.85, 0.1, 0.1)), bevel=0.003, ol=0)]
    m = T.merge(name + "_lamp", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    if on:
        ld = bpy.data.lights.new(name + "_bundel", "SPOT")
        ld.energy = 80
        ld.spot_size = math.radians(28)
        ld.spot_blend = 0.4
        lo = bpy.data.objects.new(name + "_bundel", ld)
        T._link(lo)
        lo.parent = root
        lo.location = (0.23, 0, 0)
        lo.rotation_euler = (0, math.radians(-90), 0)
    return root


# ---------------------------------------------------------------------------
# Terugkerende props (bijlage C van het script)
# ---------------------------------------------------------------------------
DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def pillendoosje(name, loc, rot_z=0.0, open_=(), empty=False):
    """Opa's pillendoosje (19 cm) met zeven vakjes en dekseltjes MON..SUN.
    open_=("SAT",) zet dat dekseltje open; empty=True = geen pillen (scène 11c)."""
    root = _empty(name, size=0.05)
    body = _m("pillendoos_doorzichtig", (0.55, 0.75, 0.95))
    lid_cols = [(0.95, 0.3, 0.3), (0.98, 0.6, 0.15), (0.98, 0.85, 0.2), (0.35, 0.8, 0.35), (0.25, 0.6, 0.95), (0.55, 0.4, 0.9), (0.95, 0.45, 0.75)]
    T.box(name + "_bak", (0, 0, 0), (0.19, 0.035, 0.022), _m("pillendoos_wit", (0.95, 0.95, 0.95)), bevel=0.004, ol=0).parent = root
    rnd = random.Random(4)
    for i, d in enumerate(DAYS):
        x = -0.081 + i * 0.027
        if not empty and d not in ("THU", "FRI") or (not empty and d == "SAT"):
            for k in range(2):
                pl = T.sphere(f"{name}_pil_{d}{k}", (x + (k - 0.5) * 0.008, rnd.uniform(-0.006, 0.006), 0.016), 0.0045,
                              _m("pil_" + ("wit" if k else "geel"), (0.96, 0.96, 0.94) if k else (0.98, 0.85, 0.3)), scale=(1.6, 1, 1), seg=10, ol=0)
                pl.parent = root
        hinge = _empty(f"{name}_deksel_{d}", (x, 0.0175, 0.023), size=0.01)
        hinge.parent = root
        lid = T.box(f"{name}_dekselblad_{d}", (0, -0.0175, 0), (0.025, 0.035, 0.004), _m(f"pildeksel_{i}", lid_cols[i]), bevel=0.001, ol=0)
        lid.parent = hinge
        t = label(f"{name}_dag_{d}", d, (0, -0.0175, 0.0021), 0.0065, (1, 1, 1), rot=(0, 0, 0), extrude=0.0003)
        t.parent = hinge
        if d in open_:
            hinge.rotation_euler.x = math.radians(-110)
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def house_rules(name, loc, rot=(90, 0, 0), extra=None, yellowed=False):
    """Vel HOUSE RULES in kinderhandschrift met vier regels (plus extra regel 5, scène 22)."""
    root = _empty(name, size=0.05)
    paper = HU.paper(name + "_papier", (0.93, 0.86, 0.62) if yellowed else (0.98, 0.98, 0.95))
    sheet = T.box(name + "_vel", (0, 0, -0.15), (0.21, 0.002, 0.297), paper, bevel=0, ol=0)
    sheet.parent = root
    mag = T.cyl(name + "_magneet", (0, -0.004, 0.13), 0.012, 0.008, _m("magneet_rood", (0.9, 0.15, 0.12)), rot=(90, 0, 0), seg=12, ol=0)
    mag.parent = root
    lines = [("HOUSE RULES", 0.024, "rood"), ("1. NO PHONES AT DINNER", 0.0125, "blauw"), ("2. WAIT FOR GREEN", 0.0125, "blauw"),
             ("3. BED AT 9", 0.0125, "blauw"), ("4. BE NICE TO OPA", 0.0125, "blauw")]
    if extra:
        lines.append((extra, 0.0125, "zwart"))
    for i, (tx, s, col) in enumerate(lines):
        t = HU.marker_text(f"{name}_regel{i}", tx, (0 if i == 0 else -0.09, -0.0015, 0.1 - i * 0.038 - (0.01 if i else 0)), s, col,
                           align="CENTER" if i == 0 else "LEFT")
        t.parent = root
    root.location = loc
    root.rotation_euler = Euler([math.radians(a) for a in rot])
    return root


def kroon(name, loc, rot_z=0.0):
    """Kartonnen kroon van de pestkop (doorsnede 34 cm, past op de chibi-kop)."""
    mat = _m("karton_kroon", (0.80, 0.62, 0.36))
    goud = _m("goudverf", (0.95, 0.75, 0.2))
    n = 7
    verts, faces = [], []
    R, h0, h1 = 0.17, 0.07, 0.13
    seg = n * 2
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        top = h1 if i % 2 == 0 else h0
        verts += [(R * math.cos(a), R * math.sin(a), 0), (R * math.cos(a), R * math.sin(a), top)]
    for i in range(seg):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    o = T.mesh_from(name + "_band", verts, faces, mat)
    sol = o.modifiers.new("dik", "SOLIDIFY")
    sol.thickness = 0.004
    parts = [o]
    for i in range(0, seg, 2):
        a = 2 * math.pi * i / seg
        parts.append(T.sphere(f"{name}_juweel{i}", (R * 1.01 * math.cos(a), R * 1.01 * math.sin(a), 0.045), 0.012,
                              _m("kroon_juweel_" + str(i % 3), [(0.9, 0.1, 0.1), (0.1, 0.4, 0.95), (0.1, 0.75, 0.3)][i % 3]), seg=10, ol=0))
    parts.append(HU.marker_text(name + "_tekst", "BOSS", (0, -R - 0.006, 0.035), 0.03, "zwart"))
    texts = [p for p in parts if p.type != "MESH"]
    k = T.merge(name, [p for p in parts if p.type == "MESH"], ol=0)
    for p in texts:
        p.parent = k
    k.location = loc
    k.rotation_euler.z = math.radians(rot_z)
    return k


def batterijen(name, loc, n=6, seed=2):
    rnd = random.Random(seed)
    parts = []
    for i in range(n):
        x = (i % 3) * 0.022
        y = (i // 3) * 0.06
        parts.append(T.cyl(f"{name}_{i}", (x, y, 0.007), 0.007, 0.05, _m("batterij_" + ("goud" if i % 2 else "zwart"), (0.85, 0.65, 0.15) if i % 2 else (0.08, 0.08, 0.09)),
                           rot=(90, 0, rnd.uniform(-8, 8)), seg=12, ol=0))
        parts.append(T.cyl(f"{name}_{i}_pool", (x, y - 0.025, 0.007), 0.003, 0.004, _m("chroom_batterij", (0.85, 0.85, 0.88)), rot=(90, 0, 0), seg=8, ol=0))
    o = T.merge(name, parts, ol=0)
    o.location = loc
    return o


def stripboeken(name, loc, n=6, seed=5, rot_z=0.0):
    rnd = random.Random(seed)
    cols = [(0.9, 0.2, 0.15), (0.15, 0.45, 0.95), (0.98, 0.8, 0.15), (0.2, 0.7, 0.3), (0.7, 0.3, 0.8)]
    parts = []
    z = 0
    for i in range(n):
        parts.append(T.box(f"{name}_{i}", (rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), z), (0.17, 0.26, 0.006),
                           _m(f"strip_{i % 5}", cols[i % 5]), rot=(0, 0, rnd.uniform(-8, 8)), bevel=0.001, ol=0))
        parts.append(T.box(f"{name}_{i}_titel", (0, -0.08, z + 0.006), (0.12, 0.06, 0.001), _m("strip_titel", (0.98, 0.98, 0.95)), bevel=0, ol=0))
        z += 0.0065
    o = T.merge(name, parts, ol=0)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def medicijndoos(name, loc, rot_z=0.0):
    p = [T.box(name + "_doos", (0, 0, 0), (0.11, 0.05, 0.07), _m("medicijn_wit", (0.97, 0.97, 0.97)), bevel=0.004, ol=0),
         T.box(name + "_band", (0, -0.0255, 0.025), (0.11, 0.002, 0.022), _m("medicijn_groen", (0.15, 0.65, 0.45)), bevel=0, ol=0),
         T.box(name + "_kruis_h", (-0.035, -0.027, 0.045), (0.018, 0.002, 0.006), _m("medicijn_groen", (0.15, 0.65, 0.45)), bevel=0, ol=0),
         T.box(name + "_kruis_v", (-0.035, -0.027, 0.039), (0.006, 0.002, 0.018), _m("medicijn_groen", (0.15, 0.65, 0.45)), bevel=0, ol=0)]
    o = T.merge(name, p, ol=0)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def kaars(name, loc, h=0.16, lit=True, r=0.025, energy=25):
    """Kaars met vlammetje en warm puntlicht (<naam>_licht; energy keyframen = flakkeren)."""
    root = _empty(name, size=0.05)
    p = [T.cyl(name + "_was", (0, 0, 0), r, h, _m("kaarsvet", (0.96, 0.93, 0.85)), seg=16, ol=0),
         T.cyl(name + "_pit", (0, 0, h), 0.002, 0.012, _m("kaarspit", (0.1, 0.08, 0.06)), seg=6, ol=0),
         T.cyl(name + "_schotel", (0, 0, 0), r * 2.4, 0.012, _m("kandelaar_messing", (0.8, 0.62, 0.25)), seg=20, ol=0)]
    m = T.merge(name + "_kaars", p, ol=0)
    m.parent = root
    if lit:
        fl = T.sphere(name + "_vlam", (0, 0, h + 0.024), 0.009, _glowmat(name + "_vlamgloed", (1.0, 0.62, 0.2), 25), scale=(1, 1, 2.2), seg=10, ol=0)
        fl.parent = root
        lt = T.point_light(name + "_licht", (0, 0, h + 0.05), color=(1.0, 0.58, 0.25), energy=energy, radius=0.02)
        lt.parent = root
    root.location = loc
    return root


def vuurkorf(name, loc, lit=True, energy=900):
    """Vuurkorf op pootjes met vlammen en gloed (scène 14 en 17)."""
    root = _empty(name, size=0.3)
    iron = _m("staal_vuurkorf", (0.12, 0.11, 0.10))
    p = []
    for k in range(14):
        a = 2 * math.pi * k / 14
        p.append(T.to_mesh(T.tube(f"{name}_spijl{k}", [(0.32 * math.cos(a), 0.32 * math.sin(a), 0.45), (0.42 * math.cos(a), 0.42 * math.sin(a), 0.95)], 0.012, iron)))
    p.append(T.torus(name + "_ring_o", (0, 0, 0.45), 0.32, 0.015, iron, seg=24, seg2=6, ol=0))
    p.append(T.torus(name + "_ring_b", (0, 0, 0.95), 0.42, 0.015, iron, seg=24, seg2=6, ol=0))
    p.append(T.cyl(name + "_bodem", (0, 0, 0.43), 0.32, 0.03, iron, seg=20, ol=0))
    for k in range(3):
        a = 2 * math.pi * k / 3
        p.append(T.to_mesh(T.tube(f"{name}_poot{k}", [(0.3 * math.cos(a), 0.3 * math.sin(a), 0.45), (0.45 * math.cos(a), 0.45 * math.sin(a), 0.0)], 0.02, iron)))
    rnd = random.Random(7)
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        p.append(T.cyl(f"{name}_hout{k}", (0.15 * math.cos(a), 0.15 * math.sin(a), 0.5), 0.04, 0.45, _m("haardhout", (0.38, 0.24, 0.12)),
                       rot=(rnd.uniform(-60, 60), rnd.uniform(-60, 60), 0), seg=8, ol=0))
    m = T.merge(name + "_korf", p, ol=0)
    m.parent = root
    if lit:
        fire = _glowmat(name + "_vuur", (1.0, 0.45, 0.08), 14)
        for k in range(7):
            a = rnd.uniform(0, 6.28)
            f = T.sphere(f"{name}_vlam{k}", (0.12 * math.cos(a), 0.12 * math.sin(a), 0.85 + rnd.uniform(0, 0.15)), rnd.uniform(0.07, 0.11),
                         fire, scale=(1, 1, 2.6), seg=10, ol=0)
            f.parent = root
        lt = T.point_light(name + "_gloed", (0, 0, 1.2), color=(1.0, 0.5, 0.18), energy=energy, radius=0.3)
        lt.parent = root
    root.location = loc
    return root


def kampvuur(name, loc, lit=True):
    root = _empty(name, size=0.3)
    rnd = random.Random(3)
    p = []
    for k in range(9):
        a = 2 * math.pi * k / 9
        p.append(T.sphere(f"{name}_steen{k}", (0.45 * math.cos(a), 0.45 * math.sin(a), 0.06), 0.11, _m("steen_kampvuur", (0.5, 0.5, 0.5)),
                          scale=(1.2, 1, 0.7), seg=10, ol=0))
    for k in range(6):
        a = 2 * math.pi * k / 6
        p.append(T.cyl(f"{name}_blok{k}", (0.12 * math.cos(a), 0.12 * math.sin(a), 0.02), 0.04, 0.5, _m("haardhout", (0.38, 0.24, 0.12)),
                       rot=(math.degrees(math.sin(a)) * 0.9 - 0, 0, math.degrees(a)), seg=8, ol=0))
    m = T.merge(name + "_hout", p, ol=0)
    m.parent = root
    if lit:
        fire = _glowmat(name + "_vuur", (1.0, 0.45, 0.08), 14)
        for k in range(6):
            a = rnd.uniform(0, 6.28)
            T.sphere(f"{name}_vlam{k}", (0.08 * math.cos(a), 0.08 * math.sin(a), 0.2 + rnd.uniform(0, 0.12)), rnd.uniform(0.08, 0.13),
                     fire, scale=(1, 1, 2.4), seg=10, ol=0).parent = root
        T.point_light(name + "_gloed", (0, 0, 0.5), color=(1.0, 0.5, 0.18), energy=700, radius=0.3).parent = root
    root.location = loc
    return root


def zonnepaneel(name, loc, rot_z=0.0, w=1.0, d=1.6, tilt=25, legs=True):
    root = _empty(name, size=0.3)
    frame = _m("aluminium_paneel", (0.75, 0.77, 0.8))
    cell = _m("zonnecel", (0.05, 0.10, 0.25))
    g = _empty(name + "_plaat", (0, 0, 0.5 if legs else 0.0), (tilt, 0, 0), size=0.1)
    g.parent = root
    p = [T.box(name + "_frame", (0, 0, -0.02), (w, d, 0.04), frame, bevel=0.005, ol=0)]
    for i in range(4):
        for j in range(6):
            p.append(T.box(f"{name}_cel{i}{j}", (-w / 2 + (i + 0.5) * w / 4, -d / 2 + (j + 0.5) * d / 6, 0.0), (w / 4 - 0.02, d / 6 - 0.02, 0.008), cell, bevel=0, ol=0))
    m = T.merge(name + "_paneel", p, ol=0)
    m.parent = g
    if legs:
        for x in (-w / 2 + 0.05, w / 2 - 0.05):
            T.box(f"{name}_poot_v{x}", (x, -d * 0.4, 0), (0.04, 0.04, 0.3), frame, bevel=0, ol=0).parent = root
            T.box(f"{name}_poot_a{x}", (x, d * 0.4, 0), (0.04, 0.04, 0.95), frame, bevel=0, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def winkelkar(name, loc, rot=0.0, tipped=False):
    """Winkelwagen met draadmand (glans 2)."""
    root = _empty(name, size=0.3)
    M = _m("chroom_kar", (0.78, 0.8, 0.82))
    red = _m("kar_rood", (0.88, 0.12, 0.12))
    p = []
    # mand: draadraster
    x0, x1, y0, y1, z0, z1 = -0.28, 0.28, -0.45, 0.45, 0.45, 0.95
    for k in range(7):
        y = y0 + (y1 - y0) * k / 6
        p.append(T.to_mesh(T.tube(f"{name}_d1{k}", [(x0, y, z0), (x0, y, z1)], 0.005, M)))
        p.append(T.to_mesh(T.tube(f"{name}_d2{k}", [(x1, y, z0), (x1, y, z1)], 0.005, M)))
        p.append(T.to_mesh(T.tube(f"{name}_d3{k}", [(x0, y, z0), (x1, y, z0)], 0.005, M)))
    for k in range(5):
        z = z0 + (z1 - z0) * k / 4
        p.append(T.to_mesh(T.tube(f"{name}_r{k}", [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), (x0, y0, z)], 0.006, M)))
        x = x0 + (x1 - x0) * k / 4
        p.append(T.to_mesh(T.tube(f"{name}_v{k}", [(x, y0, z0), (x, y0, z1)], 0.005, M)))
        p.append(T.to_mesh(T.tube(f"{name}_w{k}", [(x, y1, z0), (x, y1, z1)], 0.005, M)))
    p.append(T.to_mesh(T.tube(name + "_onderstel", [(-0.22, -0.4, 0.12), (0.22, -0.4, 0.12), (0.22, 0.42, 0.12), (-0.22, 0.42, 0.12), (-0.22, -0.4, 0.12)], 0.015, M)))
    for x in (-0.24, 0.24):
        p.append(T.to_mesh(T.tube(f"{name}_stijl{x}", [(x, 0.42, 0.12), (x, 0.45, 0.5), (x, 0.55, 1.05)], 0.015, M)))
    p.append(T.cyl(name + "_handvat", (-0.28, 0.56, 1.05), 0.022, 0.56, red, rot=(0, 90, 0), seg=12, ol=0))
    for x in (-0.22, 0.22):
        for y in (-0.38, 0.38):
            p.append(T.cyl(f"{name}_wiel{x}{y}", (x - 0.02, y, 0.06), 0.06, 0.04, _m("kar_wiel", (0.1, 0.1, 0.12)), rot=(0, 90, 0), seg=12, ol=0))
    m = T.merge(name + "_kar", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler = (0, math.radians(85) if tipped else 0, math.radians(rot))
    if tipped:
        root.location.z += 0.3
    return root


def dranghek(name, loc, rot_z=0.0, l=2.4):
    root = _empty(name, size=0.3)
    M = _m("staal_dranghek", (0.72, 0.74, 0.76))
    p = [T.to_mesh(T.tube(name + "_kader", [(-l / 2, 0, 0.2), (-l / 2, 0, 1.1), (l / 2, 0, 1.1), (l / 2, 0, 0.2), (-l / 2, 0, 0.2)], 0.022, M))]
    for k in range(1, 16):
        x = -l / 2 + l * k / 16
        p.append(T.to_mesh(T.tube(f"{name}_spijl{k}", [(x, 0, 0.2), (x, 0, 1.1)], 0.009, M)))
    for x in (-l / 2 + 0.1, l / 2 - 0.1):
        p.append(T.to_mesh(T.tube(f"{name}_voet{x}", [(x, -0.3, 0.0), (x, 0, 0.22), (x, 0.3, 0.0)], 0.018, M)))
    m = T.merge(name + "_hek", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def slagboom(name, loc, rot_z=0.0, open_=False, snow=False):
    """Slagboom van de straat (scène 15, 17): een winkelkar als tegenwicht, planken als arm
    en een verkeersbord. De arm (<naam>_arm) draait om zijn scharnier (rotation_euler.y)."""
    root = _empty(name, size=0.4)
    wood = _m("plank_steigerhout", (0.62, 0.48, 0.30))
    p = [T.box(name + "_paal", (0, 0, 0), (0.14, 0.14, 1.2), wood, bevel=0.01, ol=0),
         T.box(name + "_paal_voet", (0, 0, 0), (0.6, 0.6, 0.1), _m("betonblok", (0.6, 0.6, 0.58)), bevel=0.02, ol=0),
         T.box(name + "_steunpaal", (5.0, 0, 0), (0.12, 0.12, 0.95), wood, bevel=0.01, ol=0),
         T.box(name + "_steun_klos", (5.0, 0, 0.92), (0.28, 0.16, 0.06), wood, bevel=0.01, ol=0)]
    m = T.merge(name + "_staanders", p, ol=0)
    m.parent = root
    kar = winkelkar(name + "_tegenwicht", (-0.75, 0, 0), rot=90)
    kar.parent = root
    arm = _empty(name + "_arm", (0, 0, 1.08), size=0.2)
    arm.parent = root
    ap = [T.box(name + "_plank1", (2.6, 0, 0), (5.4, 0.04, 0.16), wood, bevel=0.01, ol=0),
          T.box(name + "_plank2", (2.4, 0.045, 0.02), (4.6, 0.04, 0.14), wood, rot=(0, 1.2, 0), bevel=0.01, ol=0)]
    for k in range(6):
        ap.append(T.box(f"{name}_streep{k}", (0.6 + k * 0.85, -0.022, 0.0), (0.4, 0.004, 0.16), _m("verf_rood", (0.88, 0.12, 0.1)), bevel=0, ol=0))
    am = T.merge(name + "_planken", ap, ol=0)
    am.parent = arm
    # touw naar de kar (tegenwicht)
    T.to_mesh(T.tube(name + "_touw", [(-0.2, 0, 0.05), (-0.55, 0, -0.1)], 0.01, _m("touw", (0.75, 0.65, 0.45)))).parent = arm
    bord = sign(name + "_stopbord", ["STOP"], (0.4, -0.15, 0), 0.0, w=0.6, h=0.6, bg=(0.85, 0.08, 0.08), fg=(1, 1, 1), post_h=1.3)
    bord.parent = root
    if open_:
        arm.rotation_euler.y = math.radians(-75)
    if snow:
        sn = _m("sneeuw", (0.95, 0.97, 1.0))
        T.box(name + "_sneeuwrug", (2.6, 0, 0.08), (5.3, 0.06, 0.05), sn, bevel=0.02, ol=0).parent = arm
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def regelbord(name, loc, rot_z=0.0, w=4.0, h=2.6, rules=None, title="OUR RULES", stand=True, color="zwart", size=0.11):
    """Groot houten bord vol handgeschreven regels. Elke regel is een eigen object
    (<naam>_regel_N), zodat er in de animatie één bij kan komen."""
    root = _empty(name, size=0.5)
    wood = _m("regelbord_hout", (0.74, 0.56, 0.34))
    dark = _m("regelbord_paal", (0.42, 0.28, 0.16))
    p = []
    zb = 0.6 if stand else 0.0
    for k in range(int(h / 0.25)):
        p.append(T.box(f"{name}_plank{k}", (0, 0, zb + k * 0.25), (w, 0.05, 0.24), wood, bevel=0.01, ol=0))
    if stand:
        for x in (-w / 2 + 0.15, w / 2 - 0.15):
            p.append(T.box(f"{name}_poot{x}", (x, 0.06, 0), (0.16, 0.12, zb + h + 0.25), dark, bevel=0.01, ol=0))
    p.append(T.box(name + "_kap", (0, -0.05, zb + h), (w + 0.3, 0.3, 0.1), dark, bevel=0.02, ol=0))
    m = T.merge(name + "_bord", p, ol=0)
    m.parent = root
    t = HU.marker_text(name + "_titel", title, (0, -0.03, zb + h - 0.32), size * 1.9, "rood")
    t.parent = root
    rules = rules or []
    cols = 2 if len(rules) > 14 else 1
    per = math.ceil(len(rules) / cols) if rules else 1
    for i, r in enumerate(rules):
        c, rr = divmod(i, per)
        x = -w / 2 + 0.2 + c * (w / cols)
        z = zb + h - 0.55 - rr * size * 1.45
        if z < zb + 0.1:
            break
        t = HU.marker_text(f"{name}_regel_{i + 1}", r, (x, -0.03, z), size, color, align="LEFT")
        t.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def ladder(name, loc, rot_z=0.0, h=3.0, lean=12):
    root = _empty(name, size=0.2)
    al = _m("aluminium_ladder", (0.78, 0.8, 0.82))
    p = [T.box(name + "_boom_l", (-0.22, 0, 0), (0.05, 0.06, h), al, bevel=0.005, ol=0),
         T.box(name + "_boom_r", (0.22, 0, 0), (0.05, 0.06, h), al, bevel=0.005, ol=0)]
    for k in range(int(h / 0.28)):
        p.append(T.cyl(f"{name}_sport{k}", (-0.22, 0, 0.25 + k * 0.28), 0.018, 0.44, al, rot=(0, 90, 0), seg=8, ol=0))
    m = T.merge(name + "_ladder", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler = (math.radians(-lean), 0, math.radians(rot_z))
    return root


def klimrek(name, loc, rot_z=0.0):
    """Klimrek (koepel van buizen) in vrolijke kleuren, 2,2 m hoog."""
    root = _empty(name, size=0.5)
    cols = [_m("speeltoestel_rood", (0.9, 0.18, 0.12)), _m("speeltoestel_geel", (0.98, 0.78, 0.12)), _m("speeltoestel_blauw", (0.12, 0.42, 0.92))]
    p = []
    R = 1.8
    nlon = 10
    for i in range(nlon):
        a = 2 * math.pi * i / nlon
        pts = [(R * math.cos(t) * math.cos(a), R * math.cos(t) * math.sin(a), R * 1.2 * math.sin(t)) for t in [k * math.pi / 2 / 8 for k in range(9)]]
        p.append(T.to_mesh(T.tube(f"{name}_boog{i}", pts, 0.035, cols[i % 3])))
    for j, t in enumerate([math.pi / 2 * k / 5 for k in range(1, 5)]):
        r = R * math.cos(t)
        z = R * 1.2 * math.sin(t)
        pts = [(r * math.cos(b), r * math.sin(b), z) for b in [2 * math.pi * k / 40 for k in range(41)]]
        p.append(T.to_mesh(T.tube(f"{name}_ring{j}", pts, 0.03, cols[(j + 1) % 3])))
    m = T.merge(name + "_buizen", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def ijskraam(name, loc, rot_z=0.0):
    """Ijskraam met luifel, toonbank en ijsjes (scène 7k). Kijkt naar -y."""
    root = _empty(name, size=0.5)
    p = [T.box(name + "_kast", (0, 0, 0), (2.4, 1.2, 1.05), _m("ijskraam_wit", (0.96, 0.96, 0.95)), bevel=0.04, ol=0),
         T.box(name + "_toonbank", (0, -0.1, 1.05), (2.5, 1.35, 0.06), _m("ijskraam_roze", (0.98, 0.55, 0.7)), bevel=0.02, ol=0),
         T.box(name + "_vitrine", (0, 0, 1.11), (2.2, 0.9, 0.3), T.glass("ijsvitrine", (0.8, 0.92, 1.0), alpha=0.25), bevel=0.02, ol=0)]
    for x in (-1.15, 1.15):
        p.append(T.cyl(f"{name}_paal{x}", (x, 0.5, 1.1), 0.04, 1.3, _m("ijskraam_roze", (0.98, 0.55, 0.7)), seg=10, ol=0))
    m = T.merge(name + "_kraam", p, ol=0)
    m.parent = root
    P.striped_awning(name + "_luifel", (0, 0.1, 2.4), 2.8, 1.6, colors=("roze", "wit")).parent = root
    flav = [(0.98, 0.9, 0.75), (0.45, 0.25, 0.12), (0.98, 0.6, 0.7), (0.6, 0.85, 0.5), (0.98, 0.85, 0.3)]
    for i, c in enumerate(flav):
        T.sphere(f"{name}_bak{i}", (-0.85 + i * 0.42, 0.05, 1.15), 0.12, _m(f"ijs_{i}", c), scale=(1.3, 1.0, 0.55), seg=14, ol=0).parent = root
    # één ijsje op de toonbank (pakt de pestkop)
    ijs = _empty(name + "_ijsje", (0.6, -0.55, 1.08), size=0.05)
    ijs.parent = root
    T.cyl(name + "_hoorntje", (0, 0, 0), 0.008, 0.13, _m("hoorntje", (0.85, 0.62, 0.32)), r2=0.035, seg=12, ol=0).parent = ijs
    T.sphere(name + "_bol", (0, 0, 0.15), 0.038, _m("ijs_2", flav[2]), seg=14, ol=0).parent = ijs
    sign(name + "_bord", ["ICE CREAM"], (0, -0.62, 2.0), 0, w=1.6, h=0.35, bg=(0.98, 0.55, 0.7), fg=(1, 1, 1), post=False).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def moestuinbak(name, loc, size=(2.4, 1.2), crop="sla", seed=1, rot_z=0.0):
    rnd = random.Random(seed)
    root = _empty(name, size=0.3)
    w, d = size
    wood = _m("plank_moestuin", (0.55, 0.38, 0.22))
    p = [T.box(name + "_rand_v", (0, -d / 2, 0), (w, 0.05, 0.3), wood, bevel=0.01, ol=0),
         T.box(name + "_rand_a", (0, d / 2, 0), (w, 0.05, 0.3), wood, bevel=0.01, ol=0),
         T.box(name + "_rand_l", (-w / 2, 0, 0), (0.05, d, 0.3), wood, bevel=0.01, ol=0),
         T.box(name + "_rand_r", (w / 2, 0, 0), (0.05, d, 0.3), wood, bevel=0.01, ol=0),
         T.box(name + "_aarde", (0, 0, 0), (w - 0.05, d - 0.05, 0.27), _m("aarde_moestuin", (0.28, 0.18, 0.10)), bevel=0.02, ol=0)]
    m = T.merge(name + "_bak", p, ol=0)
    m.parent = root
    plants = []
    for i in range(int(w / 0.3)):
        for j in range(int(d / 0.35)):
            x = -w / 2 + 0.2 + i * 0.3
            y = -d / 2 + 0.22 + j * 0.35
            if crop == "tomaat":
                plants.append(T.cyl(f"{name}_stok{i}{j}", (x, y, 0.27), 0.008, 0.8, _m("bamboe", (0.8, 0.72, 0.45)), seg=6, ol=0))
                plants.append(T.sphere(f"{name}_blad{i}{j}", (x, y, 0.65), 0.14, _m("blad_tomaat", (0.2, 0.55, 0.18)), scale=(1, 1, 1.6), seg=10, ol=0))
                for k in range(3):
                    plants.append(T.sphere(f"{name}_tomaat{i}{j}{k}", (x + rnd.uniform(-0.1, 0.1), y - 0.1, 0.45 + k * 0.15), 0.035, _m("tomaat", (0.9, 0.15, 0.08)), seg=10, ol=0))
            else:
                plants.append(T.sphere(f"{name}_krop{i}{j}", (x, y, 0.32), rnd.uniform(0.09, 0.12), _m("blad_sla", (0.45, 0.78, 0.25)), scale=(1, 1, 0.7), seg=12, ol=0))
    pm = T.merge(name + "_planten", plants, ol=0)
    pm.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def strandwachtstoel(name, loc, rot_z=0.0):
    root = _empty(name, size=0.5)
    wood = _m("hout_strandwacht", (0.95, 0.95, 0.92))
    red = _m("strandwacht_rood", (0.88, 0.12, 0.1))
    p = []
    for x in (-0.5, 0.5):
        for y in (-0.5, 0.5):
            p.append(T.to_mesh(T.tube(f"{name}_poot{x}{y}", [(x * 1.4, y * 1.4, 0), (x, y, 2.0)], 0.05, wood)))
    for k in range(4):
        p.append(T.box(f"{name}_trede{k}", (0, -0.55 - (3 - k) * 0.1, 0.4 + k * 0.45), (0.9, 0.2, 0.05), wood, bevel=0.01, ol=0))
    p.append(T.box(name + "_zit", (0, 0, 2.0), (1.1, 1.1, 0.08), wood, bevel=0.02, ol=0))
    p.append(T.box(name + "_rug", (0, 0.5, 2.0), (1.1, 0.08, 0.8), red, bevel=0.02, ol=0))
    p.append(T.box(name + "_armleuning_l", (-0.55, 0.05, 2.35), (0.06, 1.0, 0.06), wood, bevel=0.01, ol=0))
    p.append(T.box(name + "_armleuning_r", (0.55, 0.05, 2.35), (0.06, 1.0, 0.06), wood, bevel=0.01, ol=0))
    m = T.merge(name + "_stoel", p, ol=0)
    m.parent = root
    pw = P.striped_awning(name + "_parasol", (0, 0.1, 3.3), 1.4, 1.4, colors=("rood", "wit"))
    pw.parent = root
    T.cyl(name + "_parasolstok", (0, 0.45, 2.0), 0.025, 1.3, wood, seg=8, ol=0).parent = root
    label(name + "_tekst", "LIFEGUARD", (0, 0.45, 2.45), 0.14, (1, 1, 1), rot=(90, 0, 0), extrude=0.003).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def strandstoel(name, loc, rot_z=0.0, color=(0.15, 0.5, 0.9)):
    root = _empty(name, size=0.3)
    wood = _m("hout_strandstoel", (0.85, 0.7, 0.45))
    cloth = _m(f"stof_strandstoel_{'%.2f%.2f%.2f' % color}", color)
    p = []
    for x in (-0.3, 0.3):
        p.append(T.to_mesh(T.tube(f"{name}_achter{x}", [(x, 0.45, 0), (x, -0.2, 0.9)], 0.02, wood)))
        p.append(T.to_mesh(T.tube(f"{name}_voor{x}", [(x, -0.35, 0), (x, 0.25, 0.42)], 0.02, wood)))
        p.append(T.to_mesh(T.tube(f"{name}_arm{x}", [(x, -0.3, 0.42), (x, 0.2, 0.42)], 0.018, wood)))
    p.append(T.box(name + "_doek_zit", (0, 0.02, 0.28), (0.58, 0.5, 0.02), cloth, rot=(-15, 0, 0), bevel=0.005, ol=0))
    p.append(T.box(name + "_doek_rug", (0, -0.03, 0.45), (0.58, 0.02, 0.5), cloth, rot=(-40, 0, 0), bevel=0.005, ol=0))
    m = T.merge(name + "_stoel", p, ol=0)
    m.parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def handdoek(name, loc, rot_z=0.0, color=(0.95, 0.4, 0.2), stripes=(1.0, 1.0, 1.0)):
    p = [T.box(name + "_doek", (0, 0, 0), (0.9, 1.8, 0.012), _m(f"stof_handdoek_{'%.2f%.2f%.2f' % color}", color), bevel=0.004, ol=0)]
    for k in range(3):
        p.append(T.box(f"{name}_streep{k}", (0, -0.6 + k * 0.6, 0.012), (0.9, 0.12, 0.002), _m("stof_handdoek_streep", stripes), bevel=0, ol=0))
    o = T.merge(name, p, ol=0)
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def parasol(name, loc, colors=("blauw", "wit"), tilt=8):
    root = _empty(name, size=0.3)
    T.cyl(name + "_stok", (0, 0, 0), 0.025, 2.2, _m("parasolstok", (0.92, 0.92, 0.9)), seg=8, ol=0).parent = root
    cols = [P.m(c) for c in colors]
    n = 12
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        tri = T.mesh_from(f"{name}_baan{i}", [(0, 0, 2.3), (1.2 * math.cos(a0), 1.2 * math.sin(a0), 1.95), (1.2 * math.cos(a1), 1.2 * math.sin(a1), 1.95)],
                          [(0, 1, 2)], cols[i % 2])
        tri.parent = root
    root.location = loc
    root.rotation_euler.x = math.radians(tilt)
    return root


def vlag(name, loc, color=(0.88, 0.12, 0.1), h=2.6):
    root = _empty(name, size=0.2)
    T.cyl(name + "_stok", (0, 0, 0), 0.02, h, _m("vlaggenstok", (0.9, 0.9, 0.9)), seg=8, ol=0).parent = root
    verts, faces = [], []
    for i in range(9):
        x = i * 0.08
        z_off = 0.04 * math.sin(i * 0.9)
        verts += [(x, z_off * 0.5, h - 0.5), (x, z_off, h - 0.05)]
    for i in range(8):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    T.mesh_from(name + "_doek", verts, faces, _m(f"vlagdoek_{'%.2f%.2f%.2f' % color}", color)).parent = root
    root.location = loc
    return root


def tankstation_bord(name, loc, rot_z=0.0, price="1.89"):
    """Prijsbord met losse cijfers (<naam>_prijs_oud/_nieuw), scène 8b: 1.89 -> 18.90."""
    root = _empty(name, size=0.4)
    p = [T.box(name + "_paal", (0, 0.05, 0), (0.2, 0.2, 3.2), _m("tank_paal", (0.15, 0.16, 0.18)), bevel=0.02, ol=0),
         T.box(name + "_kast", (0, 0, 3.2), (1.6, 0.25, 1.6), _m("tank_rood", (0.88, 0.12, 0.1)), bevel=0.04, ol=0),
         T.box(name + "_prijsveld", (0, -0.13, 3.3), (1.3, 0.02, 0.55), _m("prijsveld_zwart", (0.05, 0.05, 0.06)), bevel=0.01, ol=0)]
    m = T.merge(name + "_bord", p, ol=0)
    m.parent = root
    label(name + "_kop", "FUEL", (0, -0.13, 4.15), 0.28, (1, 1, 1), extrude=0.01).parent = root
    for kind, txt in (("oud", "1.89"), ("nieuw", "18.90")):
        t = label(f"{name}_prijs_{kind}", txt, (0, -0.15, 3.38), 0.36, (1.0, 0.8, 0.15), glow=5.0, extrude=0.005)
        t.parent = root
        vis = (kind == "oud") == (price == "1.89")
        t.hide_render = not vis
        t.hide_viewport = not vis
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def muurklok(name, loc, rot_z=0.0, hh=11, mm=59, r=0.4):
    """Klok aan de raadszaal (scène 20f): wijzers <naam>_uur/_minuut/_seconde draaien om y."""
    root = _empty(name, size=0.2)
    p = [T.cyl(name + "_rand", (0, 0, 0), r, 0.08, _m("klok_zwart", (0.08, 0.08, 0.09)), rot=(90, 0, 0), seg=40, ol=0),
         T.cyl(name + "_wijzerplaat", (0, -0.081, 0), r * 0.9, 0.005, _m("klok_wit", (0.97, 0.96, 0.92)), rot=(90, 0, 0), seg=40, ol=0)]
    for k in range(12):
        a = 2 * math.pi * k / 12
        p.append(T.box(f"{name}_streep{k}", (r * 0.78 * math.sin(a), -0.087, r * 0.78 * math.cos(a) - 0.03), (0.02, 0.004, 0.06), _m("klok_zwart", (0.08, 0.08, 0.09)),
                       rot=(0, math.degrees(a), 0), bevel=0, ol=0))
    m = T.merge(name + "_klok", p, ol=0)
    m.parent = root
    for nm, L, wd, ang in (("uur", 0.5, 0.03, (hh % 12 + mm / 60) * 30), ("minuut", 0.75, 0.02, mm * 6), ("seconde", 0.8, 0.008, 58 * 6)):
        e = _empty(f"{name}_{nm}", (0, -0.095, 0), size=0.05)
        e.parent = root
        T.box(f"{name}_{nm}_wijzer", (0, 0, 0), (wd, 0.006, r * L), _m("klok_wijzer_" + ("rood" if nm == "seconde" else "zwart"), (0.85, 0.1, 0.1) if nm == "seconde" else (0.08, 0.08, 0.09)),
              bevel=0, ol=0).parent = e
        e.rotation_euler.y = math.radians(ang)
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def troon(name, loc, rot_z=0.0):
    """Troon van de pestkop: drie winkelkarren met een kussen en een gordijn als mantel."""
    root = _empty(name, size=0.5)
    winkelkar(name + "_kar_zit", (0, 0, 0), rot=0).parent = root
    winkelkar(name + "_kar_l", (-0.75, 0.15, 0), rot=12).parent = root
    winkelkar(name + "_kar_r", (0.75, 0.15, 0), rot=-12).parent = root
    T.box(name + "_kussen", (0, 0, 0.95), (0.65, 0.95, 0.18), _m("stof_kussen_rood", (0.75, 0.08, 0.12)), bevel=0.06, ol=0).parent = root
    T.box(name + "_rugkussen", (0, 0.5, 1.0), (0.7, 0.18, 0.9), _m("stof_kussen_rood", (0.75, 0.08, 0.12)), bevel=0.06, ol=0).parent = root
    T.box(name + "_podium", (0, 0, -0.25), (2.6, 1.8, 0.25), _m("podium_pallet", (0.62, 0.48, 0.3)), bevel=0.02, ol=0).parent = root
    root.location = (loc[0], loc[1], loc[2] + 0.25)
    root.rotation_euler.z = math.radians(rot_z)
    return root


def apotheekkruis(name, loc, rot_z=0.0, on=False):
    root = _empty(name, size=0.2)
    mat = _glowmat(name + "_licht", (0.1, 0.9, 0.35), 5 if on else 0.0) if on else _m("apotheek_groen", (0.1, 0.65, 0.3))
    T.box(name + "_h", (0, 0, -0.15), (0.9, 0.12, 0.3), mat, bevel=0.02, ol=0).parent = root
    T.box(name + "_v", (0, 0, -0.45), (0.3, 0.12, 0.9), mat, bevel=0.02, ol=0).parent = root
    T.box(name + "_arm", (0, 0.4, -0.05), (0.06, 0.7, 0.06), _m("staal_arm", (0.3, 0.3, 0.32)), bevel=0, ol=0).parent = root
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def zoo_gate(name, loc, rot_z=0.0, open_deg=70):
    """Hek van de dierentuin met bord CITY ZOO; één vleugel hangt half uit zijn scharnier."""
    root = _empty(name, size=0.5)
    stone = _m("steen_zoo", (0.65, 0.6, 0.52))
    iron = _m("staal_hek_groen", (0.12, 0.25, 0.16))
    p = [T.box(name + "_pilaar_l", (-3.2, 0, 0), (0.8, 0.8, 4.0), stone, bevel=0.04, ol=0),
         T.box(name + "_pilaar_r", (3.2, 0, 0), (0.8, 0.8, 4.0), stone, bevel=0.04, ol=0),
         T.box(name + "_boog", (0, 0, 4.0), (7.2, 0.6, 0.9), stone, bevel=0.04, ol=0)]
    m = T.merge(name + "_poort", p, ol=0)
    m.parent = root
    label(name + "_naam", "CITY ZOO", (0, -0.31, 4.15), 0.55, (0.95, 0.85, 0.35), extrude=0.03).parent = root
    for side, x, ang in (("l", -2.8, open_deg), ("r", 2.8, -15)):
        hinge = _empty(f"{name}_vleugel_{side}", (x, 0, 0.05), size=0.2)
        hinge.parent = root
        bars = []
        sgn = 1 if side == "l" else -1
        for k in range(10):
            xx = sgn * (0.1 + k * 0.27)
            bars.append(T.to_mesh(T.tube(f"{name}_spijl_{side}{k}", [(xx, 0, 0.1), (xx, 0, 2.9)], 0.025, iron)))
            bars.append(T.sphere(f"{name}_punt_{side}{k}", (xx, 0, 2.95), 0.05, iron, scale=(1, 1, 1.8), seg=8, ol=0))
        bars.append(T.to_mesh(T.tube(f"{name}_ligger_{side}", [(sgn * 0.05, 0, 0.4), (sgn * 2.7, 0, 0.4)], 0.03, iron)))
        bars.append(T.to_mesh(T.tube(f"{name}_ligger2_{side}", [(sgn * 0.05, 0, 2.4), (sgn * 2.7, 0, 2.4)], 0.03, iron)))
        bm = T.merge(f"{name}_hekwerk_{side}", bars, ol=0)
        bm.parent = hinge
        hinge.rotation_euler.z = math.radians(ang)
        if side == "l":
            hinge.rotation_euler.y = math.radians(6)   # half uit zijn scharnier
    root.location = loc
    root.rotation_euler.z = math.radians(rot_z)
    return root


def mark(name, loc, rot_z=0.0):
    """Markering (leeg object) voor de animatie: waar iemand staat of loopt."""
    e = _empty(name, loc, (0, 0, rot_z), size=0.4)
    e.empty_display_type = "SINGLE_ARROW"
    return e
