"""Props en hulpfuncties voor video 5, "What If You Could See How Many Days Everyone Has Left?".

Het belangrijkste element is het GETAL boven ieders hoofd (zie script, "De getallen"):
    getal(...)        3D-tekst (blijft een tekstobject, dus het getal kan wisselen), wit/amber/rood,
                      met een donkere rand (tweede tekst erachter met offset), Track To naar de camera.
    zet_getal(o, v)   zet een nieuw getal + juiste kleur (op het huidige frame).
    rol_getal(...)    keyframet een gokkast-rol van oud naar nieuw getal (0,8 s, ease-out), via een
                      frame-handler die de tekst per frame uit de property "dagen_anim" zet.
    bak_volger(...)   bakt een gesmoothde volger boven een hoofdbot (kritisch gedempt), zodat het
                      getal nooit schokt of trilt (regel G.7). Zie ook GETAL_SCHOKT in de qc.
    puls(...)         trage puls (1 per seconde, 1,0 -> 1,06 -> 1,0) voor getallen onder de 10.

Daarnaast de props uit bijlage C van het script: goudviskom, pannenkoekenpan, koffiebeker, kinderwagen,
blikkenstapel, vishengel + schepnet + klapkrukje, brandalarmknop, tekening, leunstoel + deken,
envelop + brief, paraplu, grafsteen, scooter. Elk prop staat op z=0 (op de grond/tafel) en bewegende
delen zijn LOSSE objecten met een duidelijke naam (deksel, glaasje, pannenkoek, blik_N, lijn, dobber).
"""
import math
import os
import random

import bpy
from mathutils import Vector

from . import toon as T
from . import stad as S
from . import nooitdood as ND
from . import huis as H

WIT = (1.0, 1.0, 1.0)
AMBER = (1.0, 0.62, 0.12)
ROOD = (1.0, 0.10, 0.06)
RAND = (0.03, 0.03, 0.05)
GETAL_HOOGTE = 0.14      # hoogte van de cijfers (m)
GETAL_BOVEN_KRUIN = 0.22  # afstand kruin -> onderkant getal (m)


def _p(name, col, rough=0.45, metal=0.0, coat=0.2, alpha=1.0):
    return ND.pbr(name, col, rough=rough, metal=metal, coat=coat, alpha=alpha)


def _root(name, loc, rot_z=0.0):
    r = bpy.data.objects.new(name, None)
    r.empty_display_size = 0.2
    bpy.context.collection.objects.link(r)
    r.location = loc
    r.rotation_euler.z = math.radians(rot_z)
    return r


def _kids(root, objs):
    for o in objs:
        if o is not None and o.parent is None:
            o.parent = root
    return root


# ---------------------------------------------------------------------------
# HET GETAL
# ---------------------------------------------------------------------------
def kleur_voor(v):
    return WIT if v >= 100 else AMBER if v >= 10 else ROOD


def tekst_voor(v):
    return f"{int(v):,}"


def _getal_mat(name, col):
    mt = bpy.data.materials.get(name)
    if mt:
        return mt
    mt = ND.pbr(name, col, rough=0.3, emit=col, strength=2.0)
    return mt


def getal(name, waarde, loc=(0, 0, 0), camera=None, parent=None):
    """Getal-object (FONT) met donkere rand erachter. 'loc' = plek van de ONDERKANT van het getal
    (dus kruin + 0,22 m). Het tekstobject zelf heet <name>, de rand <name>_rand (kind)."""
    font = S._bold()
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = tekst_voor(waarde)
    cu.size = GETAL_HOOGTE / 0.72          # Inter: cijferhoogte ~0,72 em
    cu.extrude = 0.004
    cu.align_x, cu.align_y = "CENTER", "BOTTOM"
    if font:
        cu.font = font
    for c in (WIT, AMBER, ROOD):
        cu.materials.append(_getal_mat("getal_%s" % {WIT: "wit", AMBER: "amber", ROOD: "rood"}[c], c))
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (math.radians(90), 0, 0)
    # rand: dezelfde tekst, iets dikker (offset) en 6 mm erachter
    cr = cu.copy()
    cr.name = name + "_rand"
    cr.materials.clear()
    cr.materials.append(ND.pbr("getal_rand", RAND, rough=0.6))
    cr.offset = 0.006
    cr.extrude = 0.002
    r = bpy.data.objects.new(name + "_rand", cr)
    bpy.context.collection.objects.link(r)
    r.parent = o
    r.location = (0, 0, -0.008)
    # de rand volgt de tekst via een driver op de body kan niet; zet_getal() past beide aan
    o["dagen"] = int(waarde)
    o["dagen_anim"] = float(waarde)
    o["getal"] = True
    o.visible_shadow = False
    r.visible_shadow = False
    if parent is not None:
        o.parent = parent
    if camera is not None:
        richt_op(o, camera)
    zet_getal(o, waarde)
    return o


def richt_op(o, camera):
    """Track To naar de camera (altijd leesbaar, nooit gespiegeld)."""
    for c in list(o.constraints):
        if c.type == "TRACK_TO":
            o.constraints.remove(c)
    c = o.constraints.new("TRACK_TO")
    c.target = camera
    c.track_axis = "TRACK_Z"
    c.up_axis = "UP_Y"
    return c


def zet_getal(o, v):
    """Nieuw getal + kleur (wit >= 100, amber 10-99, rood 0-9) voor tekst én rand."""
    v = int(round(v))
    idx = 0 if v >= 100 else 1 if v >= 10 else 2
    body = tekst_voor(v)
    o.data.body = body
    for i in range(len(body)):
        o.data.body_format[i].material_index = idx
    for ch in o.children:
        if ch.type == "FONT" and ch.name.endswith("_rand"):
            ch.data.body = body
    o["dagen"] = v


def rol_getal(o, van, naar, frame, duur=24):
    """Gokkast-rol van 'van' naar 'naar' in 'duur' frames (30 fps -> 0,8 s), ease-out.
    Werkt via de property dagen_anim + de frame-handler (registreer_handler)."""
    o["dagen_anim"] = float(van)
    o.keyframe_insert('["dagen_anim"]', frame=frame)
    o["dagen_anim"] = float(naar)
    o.keyframe_insert('["dagen_anim"]', frame=frame + duur)
    fc = o.animation_data.action.fcurves.find('["dagen_anim"]') if hasattr(o.animation_data.action, "fcurves") else None
    if fc:
        for kp in fc.keyframe_points:
            kp.interpolation = "EXPO"
            kp.easing = "EASE_OUT"
    registreer_handler()


def _handler(scene, *_):
    for o in scene.objects:
        if o.type == "FONT" and o.get("getal") and "dagen_anim" in o:
            v = int(round(o["dagen_anim"]))
            if v != o.get("dagen"):
                zet_getal(o, v)


def registreer_handler():
    hs = bpy.app.handlers.frame_change_pre
    if not any(getattr(h, "__name__", "") == "_handler" for h in hs):
        hs.append(_handler)


def puls(o, f0, f1, fps=30):
    """1 Hz puls: schaal 1,0 -> 1,06 -> 1,0 (alleen voor rode getallen)."""
    f = f0
    while f <= f1:
        for df, s in ((0, 1.0), (fps // 2, 1.06)):
            o.scale = (s, s, s)
            o.keyframe_insert("scale", frame=f + df)
        f += fps
    o.scale = (1, 1, 1)
    o.keyframe_insert("scale", frame=f)


def bak_volger(o, rig, bone="head", f0=1, f1=250, kruin=0.12, stijfheid=0.35):
    """Bakt de positie van het getal boven een hoofdbot met een kritisch gedempte volger.
    kruin = afstand van de bot-kop tot de kruin. stijfheid 0,35 = hooguit ~2 frames naijlen bij
    een snelle hoofdbeweging, nooit trillen. Haalt eerst de verticale ruis (ademen, stappen) eruit
    met een moving average over 5 frames, dan de volger."""
    sc = bpy.context.scene
    pb = rig.pose.bones.get(bone)
    if pb is None:
        raise ValueError(f"bot {bone} niet gevonden in {rig.name}")
    raw = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        m = rig.matrix_world @ pb.matrix
        raw.append(Vector(m.translation) + Vector((0, 0, kruin + GETAL_BOVEN_KRUIN)))
    # 1) verticale ruis eruit (stappen/ademen mag het getal niet laten dansen)
    z = [p.z for p in raw]
    zs = [sum(z[max(0, i - 2):i + 3]) / len(z[max(0, i - 2):i + 3]) for i in range(len(z))]
    # 2) kritisch gedempte volger (positie + snelheid)
    pos, vel = raw[0].copy(), Vector((0, 0, 0))
    k = stijfheid
    o.parent = None
    for i, f in enumerate(range(f0, f1 + 1)):
        tgt = Vector((raw[i].x, raw[i].y, zs[i]))
        acc = (tgt - pos) * (k * k) - vel * (2 * k)
        vel += acc
        pos += vel
        o.location = pos
        o.keyframe_insert("location", frame=f)
    return o


# ---------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------
def goudviskom(name="Goudviskom", loc=(0, 0, 0), getal_=None):
    """Bolle kom (glas met breking), water, grind, plantje en een goudvis (los object 'Goudvis')."""
    root = _root(name, loc)
    glas = H.water(name + "_glas") if False else T.glass("glas_kom", (0.85, 0.93, 1.0), 0.25)
    w = H.water("water_kom")
    kom = T.sphere(name + "_glas", (0, 0, 0.13), 0.14, glas, scale=(1, 1, 0.92), seg=40, ol=0)
    water = T.sphere(name + "_water", (0, 0, 0.12), 0.132, w, scale=(1, 1, 0.78), seg=40, ol=0)
    grind = T.cyl(name + "_grind", (0, 0, 0.02), 0.085, 0.025, _p("grind_kom", (0.85, 0.75, 0.55), rough=0.8), seg=24, ol=0)
    plant = [T.tube(f"{name}_plant{k}", [(0.04 * math.cos(k * 2), 0.04 * math.sin(k * 2), 0.04),
                                          (0.05 * math.cos(k * 2), 0.05 * math.sin(k * 2), 0.12),
                                          (0.03 * math.cos(k * 2 + 0.5), 0.03 * math.sin(k * 2 + 0.5), 0.17)], 0.006,
                     _p("blad_waterplant", (0.15, 0.55, 0.25), rough=0.5)) for k in range(4)]
    plant = [T.to_mesh(p) for p in plant]
    vis = T.sphere("Goudvis", (0.02, 0.0, 0.13), 0.028, _p("goudvis_oranje", (1.0, 0.45, 0.08), coat=0.6), scale=(1.6, 0.7, 1.0), seg=16, ol=0)
    staart = T.mesh_from("Goudvis_staart", [(-0.04, 0, 0), (-0.075, 0, 0.022), (-0.075, 0, -0.022)], [(0, 1, 2)],
                         _p("goudvis_oranje", (1.0, 0.45, 0.08)))
    staart.location = (0.02, 0, 0.13)
    staart.parent = vis
    staart.location = (0, 0, 0)
    oog = T.sphere("Goudvis_oog", (0.058, -0.017, 0.137), 0.005, _p("oog_zwart", (0.02, 0.02, 0.02)), seg=8, ol=0)
    oog.parent = vis
    oog.matrix_parent_inverse = vis.matrix_world.inverted()
    _kids(root, [kom, water, grind, vis] + plant)
    return root


def pannenkoekenpan(name="Pan", loc=(0, 0, 0), rot_z=0.0):
    """Pan met steel, losse pannenkoek ('<name>_pannenkoek', kan flippen) en spatel ('Spatel')."""
    root = _root(name, loc, rot_z)
    zwart = _p("pan_zwart", (0.06, 0.06, 0.07), rough=0.35, metal=0.6)
    p = [T.cyl(name + "_bodem", (0, 0, 0), 0.13, 0.012, zwart, seg=40, ol=0),
         T.cyl(name + "_rand", (0, 0, 0.0), 0.14, 0.035, zwart, r2=0.15, seg=40, ol=0, cap=False),
         T.cyl(name + "_steel", (0.24, 0, 0.025), 0.013, 0.2, _p("steel_bakeliet", (0.12, 0.08, 0.06)), rot=(0, 85, 0), seg=12, ol=0)]
    pan = T.merge(name + "_pan", p, ol=0)
    koek = T.cyl(name + "_pannenkoek", (0, 0, 0.014), 0.115, 0.008, _p("pannenkoek", (0.93, 0.70, 0.35), rough=0.7), seg=32, bevel=0.003, ol=0)
    spatel = T.merge("Spatel", [T.box("Spatel_blad", (0.0, 0, 0), (0.09, 0.08, 0.004), _p("spatel_rvs", (0.8, 0.8, 0.82), metal=1, rough=0.3), bevel=0.003, ol=0),
                                T.cyl("Spatel_steel", (0.15, 0, 0.0), 0.008, 0.22, _p("steel_bakeliet", (0.12, 0.08, 0.06)), rot=(0, 90, 0), seg=10, ol=0)], ol=0)
    spatel.location = (0.05, 0.25, 0.0)
    _kids(root, [pan, koek, spatel])
    return root


def pannenkoekstapel(name="Stapel_pannenkoeken", loc=(0, 0, 0), n=8):
    mt = _p("pannenkoek", (0.93, 0.70, 0.35), rough=0.7)
    bord = T.cyl(name + "_bord", (0, 0, 0), 0.14, 0.015, _p("bord_wit", (0.96, 0.96, 0.94), coat=0.5), r2=0.11, seg=40, ol=0)
    ks = [T.cyl(f"{name}_{k}", (random.Random(k).uniform(-0.006, 0.006), random.Random(k + 9).uniform(-0.006, 0.006), 0.016 + k * 0.009),
                0.105, 0.008, mt, seg=28, bevel=0.003, ol=0) for k in range(n)]
    o = T.merge(name, [bord] + ks, ol=0)
    o.location = loc
    return o


def sapkan(name="Sapkan", loc=(0, 0, 0)):
    gl = T.glass("glas_kan", (0.9, 0.95, 1.0), 0.3)
    p = [T.cyl(name + "_glas", (0, 0, 0), 0.055, 0.22, gl, seg=28, ol=0),
         T.cyl(name + "_sap", (0, 0, 0.005), 0.05, 0.15, _p("sinaasappelsap", (1.0, 0.55, 0.05), rough=0.2), seg=28, ol=0),
         T.to_mesh(T.tube(name + "_oor", [(0.05, 0, 0.18), (0.1, 0, 0.16), (0.1, 0, 0.06), (0.05, 0, 0.04)], 0.008, gl))]
    o = T.merge(name, p, ol=0)
    o.location = loc
    return o


def krant(name="Krant", loc=(0, 0, 0), rot_z=0.0, gevouwen=True):
    pap = _p("krantpapier", (0.90, 0.88, 0.82), rough=0.9, coat=0)
    w, d = (0.30, 0.22) if gevouwen else (0.58, 0.40)
    p = [T.box(name + "_blad", (0, 0, 0), (w, d, 0.01), pap, bevel=0.002, ol=0)]
    for k in range(6):
        p.append(T.box(f"{name}_kolom{k}", (-w / 2 + 0.03 + k * (w - 0.06) / 6 + 0.02, -0.02, 0.0101), ((w - 0.08) / 6 - 0.01, d - 0.08, 0.0005),
                       _p("krantinkt", (0.45, 0.45, 0.45), rough=0.9, coat=0), bevel=0, ol=0))
    o = T.merge(name, p, ol=0)
    S.label(name + "_kop", "THE DAILY", (0, d / 2 - 0.035, 0.0106), 0.028, (0.1, 0.1, 0.1), rot=(0, 0, 0)).parent = o
    o.location = loc
    o.rotation_euler.z = math.radians(rot_z)
    return o


def koffiebeker(name="Koffiebeker", loc=(0, 0, 0), plas=False):
    """Kartonnen beker, deksel als los object ('<name>_deksel') zodat hij eraf kan springen.
    plas=True: plas koffie op de grond (los object '<name>_plas', schaal 0 -> 1 animeren)."""
    root = _root(name, loc)
    beker = T.cyl(name + "_beker", (0, 0, 0), 0.036, 0.13, _p("karton_beker", (0.92, 0.90, 0.86), rough=0.8, coat=0), r2=0.045, seg=28, ol=0)
    hoes = T.cyl(name + "_hoes", (0, 0, 0.04), 0.0405, 0.05, _p("karton_hoes", (0.55, 0.38, 0.22), rough=0.9, coat=0), r2=0.0425, seg=28, ol=0)
    deksel = T.cyl(name + "_deksel", (0, 0, 0.13), 0.047, 0.014, _p("plastic_deksel", (0.06, 0.06, 0.07), rough=0.4), r2=0.042, seg=28, bevel=0.003, ol=0)
    objs = [beker, hoes, deksel]
    if plas:
        pl = T.cyl(name + "_plas", (0.18, 0, 0.002), 0.22, 0.002, _p("koffie_plas", (0.18, 0.09, 0.04), rough=0.05, coat=0.8), seg=32, ol=0)
        pl.scale = (1.3, 0.8, 1)
        objs.append(pl)
    return _kids(root, objs)


def kinderwagen(name="Kinderwagen", loc=(0, 0, 0), rot_z=0.0, kleur=(0.18, 0.30, 0.55)):
    """Kinderwagen (kijkt naar +x), wielen als losse objecten (<name>_wiel_N, voor draaien),
    plek voor de baby: empty '<name>_baby_plek'."""
    root = _root(name, loc, rot_z)
    stof = _p("stof_kinderwagen_%.2f" % kleur[0], kleur, rough=0.8, coat=0)
    frame = _p("kinderwagen_frame", (0.15, 0.15, 0.17), rough=0.3, metal=0.7)
    bak = T.box(name + "_bak", (0.0, 0, 0.45), (0.78, 0.42, 0.3), stof, bevel=0.1, ol=0)
    kap = T.sphere(name + "_kap", (-0.22, 0, 0.75), 0.25, stof, scale=(1.0, 0.85, 0.75), seg=24, ol=0)
    kap_cut = T.box(name + "_kap_snijder", (0.1, 0, 0.75), (0.5, 0.6, 0.6), stof, bevel=0, ol=0)
    mod = kap.modifiers.new("snij", "BOOLEAN")
    mod.object = kap_cut
    mod.operation = "DIFFERENCE"
    bpy.context.view_layer.objects.active = kap
    T._apply_mods(kap)
    bpy.data.objects.remove(kap_cut)
    p = [T.to_mesh(T.tube(name + "_duwstang", [(-0.3, 0, 0.5), (-0.55, 0, 0.95), (-0.6, 0, 1.05)], 0.014, frame))]
    for s in (-1, 1):
        p.append(T.to_mesh(T.tube(f"{name}_poot_v{s}", [(0.2, s * 0.2, 0.45), (0.28, s * 0.24, 0.15)], 0.012, frame)))
        p.append(T.to_mesh(T.tube(f"{name}_poot_a{s}", [(-0.25, s * 0.2, 0.45), (-0.3, s * 0.24, 0.15)], 0.012, frame)))
    p.append(T.cyl(name + "_handvat", (-0.6, 0, 1.05), 0.022, 0.5, _p("schuim_zwart", (0.05, 0.05, 0.05), rough=0.9), rot=(90, 0, 0), seg=12, ol=0))
    p[-1].location.y = 0.25
    wielen = []
    for k, (x, y) in enumerate(((0.28, 0.24), (0.28, -0.24), (-0.3, 0.24), (-0.3, -0.24))):
        w = T.cyl(f"{name}_wiel_{k}", (x, y - 0.02 * math.copysign(1, y), 0.15), 0.15, 0.04, _p("rubber_wiel", (0.05, 0.05, 0.05), rough=0.8), rot=(90, 0, 0), seg=28, ol=0)
        wielen.append(w)
    baby = bpy.data.objects.new(name + "_baby_plek", None)
    bpy.context.collection.objects.link(baby)
    baby.location = (0.05, 0, 0.62)
    _kids(root, [bak, kap, T.merge(name + "_frame", p, ol=0), baby] + wielen)
    return root


def blikkenstapel(name="Blikken", loc=(0, 0, 0), rijen=7, rot_z=0.0, seed=3):
    """Piramide van blikken, ELK BLIK LOS (<name>_blik_<rij>_<n>) voor rigid body. Rij 0 = onderaan."""
    root = _root(name, loc, rot_z)
    rnd = random.Random(seed)
    cols = [(0.85, 0.12, 0.10), (0.95, 0.75, 0.15), (0.15, 0.45, 0.85), (0.20, 0.60, 0.30)]
    objs = []
    r, h = 0.042, 0.12
    for rij in range(rijen):
        n = rijen - rij
        for i in range(n):
            x = (i - (n - 1) / 2) * (2 * r + 0.004)
            c = cols[(rij + i) % len(cols)]
            b = T.cyl(f"{name}_blik_{rij}_{i}", (x, 0, rij * (h + 0.001)), r, h, _p("blik_rvs", (0.75, 0.75, 0.78), metal=1, rough=0.3), seg=20, ol=0)
            et = T.cyl(f"{name}_etiket_{rij}_{i}", (x, 0, rij * (h + 0.001) + 0.015), r + 0.001, h - 0.03,
                       _p("etiket_%d" % cols.index(c), c, rough=0.5), seg=20, ol=0, cap=False)
            b = T.merge(f"{name}_blik_{rij}_{i}", [b, et], ol=0)
            b.rotation_euler.z = rnd.uniform(0, 6.28)
            objs.append(b)
    return _kids(root, objs)


def vishengel(name="Vishengel", grip=(0, 0, 0), tip=(2.2, 0, 1.6), dobber=(4.5, 0, 0.0)):
    """Hengel van grip naar tip (positie in wereld), molen bij de grip, lijn als bezier-curve (los object
    '<name>_lijn', 2 punten + doorhang; punten mag de animatie verplaatsen) en een dobber ('<name>_dobber')."""
    g, t, d = Vector(grip), Vector(tip), Vector(dobber)
    hout = _p("hengel_carbon", (0.12, 0.14, 0.16), rough=0.3, metal=0.3, coat=0.6)
    stok = T.cyl(name + "_stok", (0, 0, 0), 0.012, (t - g).length, hout, r2=0.003, seg=12, ol=0)
    stok.location = g
    stok.rotation_euler = (t - g).to_track_quat("Z", "Y").to_euler()
    kurk = T.cyl(name + "_kurk", (0, 0, 0), 0.017, 0.3, _p("kurk", (0.70, 0.52, 0.32), rough=0.9), seg=12, ol=0)
    kurk.location = g
    kurk.rotation_euler = stok.rotation_euler
    dirv = (t - g).normalized()
    molen = T.cyl(name + "_molen", (0, 0, 0), 0.035, 0.04, _p("molen_metaal", (0.6, 0.6, 0.62), metal=1, rough=0.3), seg=20, ol=0)
    molen.location = g + dirv * 0.35 - Vector((0, 0, 0.05))
    molen.rotation_euler = (math.radians(90), 0, math.atan2(dirv.y, dirv.x))
    # lijn
    cu = bpy.data.curves.new(name + "_lijn", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.0012
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    mid = (t + d) / 2
    for bp, co, hl, hr in ((sp.bezier_points[0], t, t, t + (mid - t) * 0.6 - Vector((0, 0, 0.3))),
                           (sp.bezier_points[1], d, d + (mid - d) * 0.6 - Vector((0, 0, 0.3)), d)):
        bp.co = co
        bp.handle_left, bp.handle_right = hl, hr
    cu.materials.append(_p("vislijn", (0.9, 0.9, 0.92), rough=0.3))
    lijn = bpy.data.objects.new(name + "_lijn", cu)
    bpy.context.collection.objects.link(lijn)
    rood = _p("dobber_rood", (0.95, 0.12, 0.08), coat=0.6)
    db = T.merge(name + "_dobber", [T.sphere(name + "_dobber_r", (0, 0, 0.0), 0.03, rood, seg=16, ol=0),
                                    T.sphere(name + "_dobber_w", (0, 0, 0.022), 0.024, _p("dobber_wit", (0.97, 0.97, 0.95)), seg=16, ol=0),
                                    T.cyl(name + "_dobber_pin", (0, 0, 0.04), 0.004, 0.06, rood, seg=8, ol=0)], ol=0)
    db.location = d
    root = _root(name, (0, 0, 0))
    _kids(root, [stok, kurk, molen, lijn, db])
    return root


def schepnet(name="Schepnet", loc=(0, 0, 0), rot_z=0.0):
    root = _root(name, loc, rot_z)
    steel = T.cyl(name + "_steel", (0, 0, 0), 0.012, 1.4, _p("hout_steel", (0.55, 0.38, 0.2), rough=0.6), rot=(0, 80, 0), seg=10, ol=0)
    ring = T.torus(name + "_ring", (1.52, 0, 0.27), 0.2, 0.008, _p("metaal_ring", (0.5, 0.5, 0.52), metal=1), rot=(0, 10, 0), seg=32, seg2=8, ol=0)
    net = T.sphere(name + "_net", (1.52, 0, 0.2), 0.19, _p("net_groen", (0.15, 0.35, 0.2), rough=0.9, alpha=0.6), scale=(1, 1, 0.8), seg=16, ol=0)
    return _kids(root, [steel, ring, net])


def klapkrukje(name="Klapkrukje", loc=(0, 0, 0), rot_z=0.0):
    root = _root(name, loc, rot_z)
    m = _p("krukje_frame", (0.2, 0.22, 0.2), metal=0.7, rough=0.4)
    p = []
    for s in (-1, 1):
        p.append(T.to_mesh(T.tube(f"{name}_poot{s}a", [(-0.18, s * 0.15, 0), (0.18, s * 0.15, 0.42)], 0.01, m)))
        p.append(T.to_mesh(T.tube(f"{name}_poot{s}b", [(0.18, s * 0.15, 0), (-0.18, s * 0.15, 0.42)], 0.01, m)))
    p.append(T.box(name + "_zitting", (0, 0, 0.42), (0.38, 0.32, 0.02), _p("stof_krukje", (0.20, 0.35, 0.22), rough=0.9), bevel=0.01, ol=0))
    o = T.merge(name, p, ol=0)
    o.parent = root
    return root


def brandalarm(name="Brandalarm", loc=(0, 0, 0), rot_z=0.0):
    """Rode brandmelder aan de muur (kijkt naar -y). Glaasje = los object '<name>_glaasje' (breekt),
    knop = '<name>_knop' (gaat in)."""
    root = _root(name, loc, rot_z)
    rood = _p("brandalarm_rood", (0.85, 0.06, 0.05), coat=0.5)
    kast = T.box(name + "_kast", (0, -0.03, 0), (0.13, 0.06, 0.13), rood, bevel=0.012, ol=0)
    wit = T.box(name + "_vlak", (0, -0.061, 0.025), (0.09, 0.002, 0.08), _p("brandalarm_wit", (0.95, 0.95, 0.93)), bevel=0, ol=0)
    knop = T.cyl(name + "_knop", (0, -0.062, 0.065), 0.016, 0.01, _p("knop_zwart", (0.05, 0.05, 0.05)), rot=(90, 0, 0), seg=16, ol=0)
    glaasje = T.box(name + "_glaasje", (0, -0.071, 0.025), (0.088, 0.003, 0.078), T.glass("glas_alarm", (0.9, 0.95, 1.0), 0.3), bevel=0, ol=0)
    tekst = S.label(name + "_tekst", "FIRE", (0, -0.062, 0.105), 0.016, (1, 1, 1), rot=(90, 0, 0))
    tekst2 = S.label(name + "_tekst2", "PUSH HERE", (0, -0.062, 0.03), 0.009, (0.1, 0.1, 0.1), rot=(90, 0, 0))
    return _kids(root, [kast, wit, knop, glaasje, tekst, tekst2])


def tekening(name="Tekening", loc=(0, 0, 0), rot=(0, 0, 0)):
    """A4 van het broertje: het gezin als poppetjes + 'GET BETTER' in stift, papier licht gebogen."""
    pap = _p("tekenpapier", (0.97, 0.96, 0.92), rough=0.9, coat=0)
    me_o = T.plane(name, (0, 0, 0), (0.297, 0.21), pap)
    me_o.modifiers.new("sub", "SUBSURF").levels = 3
    bend = me_o.modifiers.new("buig", "SIMPLE_DEFORM")
    bend.deform_method = "BEND"
    bend.angle = math.radians(18)
    bend.deform_axis = "Y"
    kleuren = [(0.85, 0.15, 0.15), (0.15, 0.4, 0.9), (0.2, 0.7, 0.3), (0.95, 0.6, 0.1), (0.6, 0.2, 0.7), (0.3, 0.3, 0.3), (0.95, 0.4, 0.6)]
    p = []
    for k, c in enumerate(kleuren):
        x = -0.11 + k * 0.036
        hgt = 0.06 if k < 5 else 0.04
        m = _p(f"stift_{k}", c, rough=0.8, coat=0)
        p.append(T.torus(f"{name}_hoofd{k}", (x, 0.0 + hgt / 2 + 0.012, 0.001), 0.009, 0.0016, m, seg=16, seg2=4, ol=0))
        p.append(T.to_mesh(T.tube(f"{name}_lijf{k}", [(x, hgt / 2, 0.001), (x, -0.02, 0.001)], 0.0016, m)))
        p.append(T.to_mesh(T.tube(f"{name}_benen{k}", [(x - 0.008, -0.045, 0.001), (x, -0.02, 0.001), (x + 0.008, -0.045, 0.001)], 0.0016, m)))
        p.append(T.to_mesh(T.tube(f"{name}_armen{k}", [(x - 0.012, 0.0, 0.001), (x + 0.012, 0.0, 0.001)], 0.0016, m)))
    zon = T.torus(name + "_zon", (0.11, 0.075, 0.001), 0.014, 0.002, _p("stift_geel", (1.0, 0.85, 0.1), rough=0.8, coat=0), seg=16, seg2=4, ol=0)
    t = H.marker_text(name + "_tekst", "GET BETTER!!", (0, 0.06, 0.001), 0.022, color="rood", rot=(0, 0, 0))
    o = T.merge(name + "_strepen", p + [zon], ol=0)
    o.parent = me_o
    t.parent = me_o
    me_o.location = loc
    me_o.rotation_euler = [math.radians(a) for a in rot]
    return me_o


def leunstoel(name="Leunstoel", loc=(0, 0, 0), rot_z=0.0, deken=False, kleur=(0.45, 0.20, 0.14)):
    """Oorfauteuil van opa (kijkt naar -y). deken=True: opgevouwen deken op de zitting (scène 16/19)."""
    root = _root(name, loc, rot_z)
    stof = _p("stof_leunstoel", kleur, rough=0.85, coat=0)
    hout = _p("hout_poot_donker", (0.25, 0.14, 0.08), rough=0.5)
    p = [T.box(name + "_zitting", (0, -0.05, 0.25), (0.72, 0.62, 0.2), stof, bevel=0.06, ol=0),
         T.box(name + "_kussen", (0, -0.08, 0.45), (0.56, 0.55, 0.1), stof, bevel=0.05, ol=0),
         T.box(name + "_rug", (0, 0.28, 0.25), (0.76, 0.18, 0.88), stof, bevel=0.07, ol=0),
         T.sphere(name + "_rug_top", (0, 0.28, 1.06), 0.38, stof, scale=(1.0, 0.24, 0.85), seg=28, ol=0)]
    for s in (-1, 1):
        p.append(T.box(f"{name}_leuning{s}", (s * 0.34, -0.05, 0.25), (0.13, 0.62, 0.4), stof, bevel=0.05, ol=0))
        for y in (-0.3, 0.3):
            p.append(T.cyl(f"{name}_poot{s}{y}", (s * 0.3, y, 0), 0.025, 0.25, hout, r2=0.018, seg=10, ol=0))
    o = T.merge(name + "_stoel", p, ol=0)
    objs = [o]
    if deken:
        d = T.box(name + "_deken", (0.0, -0.1, 0.5), (0.42, 0.34, 0.06), T.pattern("stof_deken_ruit", (0.55, 0.12, 0.1), (0.85, 0.75, 0.55),
                                                                                  size=(0.06, 0.06), kind="schaak"), bevel=0.025, ol=0)
        objs.append(d)
    return _kids(root, objs)


BRIEF = [
    "Kid,",
    "",
    "If you're reading this, you can see them too.",
    "I saw them since I was fourteen.",
    "The first one I saved was your grandma. 1966.",
    "Forty-three people after her. I counted.",
    "",
    "Every one cost me something. It was worth it.",
    "Every single time.",
    "",
    "But listen. You don't owe the world all of it.",
    "Choose. And choose with your eyes open.",
    "",
    "I'm proud of you. I always was.",
    "",
    "Grandpa",
]


def envelop_brief(name="Brief", loc=(0, 0, 0), rot_z=0.0, open_=True, regels=None):
    """Envelop + brief in handschrift (Permanent Marker, Engels). Elke regel een eigen tekstobject
    '<name>_regel_NN' zodat de animatie ze één voor één kan laten verschijnen (17c-17h)."""
    root = _root(name, loc, rot_z)
    pap = _p("briefpapier", (0.96, 0.94, 0.86), rough=0.9, coat=0)
    env = _p("envelop", (0.92, 0.88, 0.78), rough=0.9, coat=0)
    e = T.box(name + "_envelop", (-0.17, 0.02, 0), (0.22, 0.11, 0.004), env, rot=(0, 0, 8), bevel=0.001, ol=0)
    S.label(name + "_envelop_tekst", "For the kid", (-0.17, 0.02, 0.0045), 0.016, (0.1, 0.12, 0.3), rot=(0, 0, 8), bold=False).parent = e
    flap = T.mesh_from(name + "_klep", [(-0.11, 0.055, 0), (0.11, 0.055, 0), (0, 0.11 if open_ else -0.0, 0)], [(0, 1, 2)], env)
    flap.location = (-0.17, 0.02, 0.0042)
    flap.rotation_euler.z = math.radians(8)
    blad = T.box(name + "_blad", (0.08, 0, 0), (0.21, 0.297, 0.0015), pap, bevel=0.0005, ol=0)
    objs = [e, flap, blad]
    f = H.font_marker()
    inkt = _p("inkt_blauw", (0.08, 0.12, 0.38), rough=0.6, coat=0)
    for i, regel in enumerate(regels or BRIEF):
        if not regel:
            continue
        cu = bpy.data.curves.new(f"{name}_regel_{i:02d}", "FONT")
        cu.body = regel
        cu.size = 0.0105
        cu.align_x = "LEFT"
        if f:
            cu.font = f
        cu.materials.append(inkt)
        o = bpy.data.objects.new(f"{name}_regel_{i:02d}", cu)
        bpy.context.collection.objects.link(o)
        o.location = (0.08 - 0.09, 0.125 - i * 0.0165, 0.0019)
        o.rotation_euler.z = math.radians(random.Random(i).uniform(-0.6, 0.6))
        objs.append(o)
    return _kids(root, objs)


def paraplu(name="Paraplu", loc=(0, 0, 0), kleur=(0.05, 0.05, 0.07), open_=True, tilt=8):
    """Open paraplu, 'loc' = handvat. Kap is 8-hoekig met baleinen."""
    root = _root(name, loc)
    stof = _p("paraplu_%.2f" % kleur[0], kleur, rough=0.5, coat=0.4)
    steel = T.cyl(name + "_steel", (0, 0, 0), 0.008, 0.85, _p("paraplu_steel", (0.6, 0.6, 0.62), metal=1, rough=0.3), seg=10, ol=0)
    haak = T.to_mesh(T.tube(name + "_haak", [(0, 0, 0.0), (0, 0, -0.08), (0.04, 0, -0.12), (0.07, 0, -0.08)], 0.011,
                            _p("hout_handvat", (0.3, 0.17, 0.08), rough=0.5)))
    r, hgt = (0.55, 0.22) if open_ else (0.06, 0.6)
    vs = [(0, 0, 0.85)]
    for k in range(8):
        a = k / 8 * 2 * math.pi
        vs.append((r * math.cos(a), r * math.sin(a), 0.85 - hgt))
    fs = [(0, 1 + k, 1 + (k + 1) % 8) for k in range(8)]
    kap = T.mesh_from(name + "_kap", vs, fs, stof)
    kap.modifiers.new("dik", "SOLIDIFY").thickness = 0.004
    root.rotation_euler.x = math.radians(tilt)
    return _kids(root, [steel, haak, kap])


def grafsteen(name="Grafsteen", loc=(0, 0, 0), rot_z=0.0, naam=None, nieuw=False):
    """Grafsteen (kijkt naar -y). naam=None: geen naam leesbaar in beeld (scriptregel)."""
    root = _root(name, loc, rot_z)
    steen = _p("steen_graf_%s" % ("nieuw" if nieuw else "oud"), (0.45, 0.46, 0.48) if nieuw else (0.55, 0.55, 0.52), rough=0.6 if nieuw else 0.9)
    p = [T.box(name + "_steen", (0, 0, 0.12), (0.6, 0.12, 0.75), steen, bevel=0.03, ol=0),
         T.sphere(name + "_top", (0, 0, 0.87), 0.3, steen, scale=(1.0, 0.2, 1.0), seg=24, ol=0),
         T.box(name + "_voet", (0, 0, 0), (0.75, 0.3, 0.12), steen, bevel=0.02, ol=0)]
    o = T.merge(name + "_steen", p, ol=0)
    objs = [o]
    if naam:
        objs.append(S.label(name + "_naam", naam, (0, -0.062, 0.6), 0.06, (0.85, 0.8, 0.6), rot=(90, 0, 0)))
    return _kids(root, objs)


def scooter(name="Scooter", loc=(0, 0, 0), rot_z=0.0, kleur=(0.95, 0.35, 0.10), licht=True):
    """Scooter (kijkt naar +x). Plek voor de bestuurder: empty '<name>_bestuurder' (zitting) met de
    handen op '<name>_handvat_L/_R'. NOOIT zonder bestuurder laten rijden (regel G.12)."""
    root = _root(name, loc, rot_z)
    lak = _p("scooterlak_%.2f" % kleur[0], kleur, rough=0.25, coat=0.9)
    zwart = _p("scooter_zwart", (0.06, 0.06, 0.07), rough=0.5)
    p = [T.box(name + "_romp", (-0.3, 0, 0.3), (0.75, 0.36, 0.4), lak, bevel=0.15, ol=0),
         T.box(name + "_vloer", (0.15, 0, 0.22), (0.45, 0.32, 0.08), zwart, bevel=0.02, ol=0),
         T.box(name + "_front", (0.5, 0, 0.25), (0.14, 0.4, 0.75), lak, rot=(0, -15, 0), bevel=0.06, ol=0),
         T.box(name + "_zitting", (-0.28, 0, 0.72), (0.6, 0.3, 0.1), zwart, bevel=0.05, ol=0),
         T.cyl(name + "_stuurstang", (0.58, 0, 0.6), 0.025, 0.5, zwart, rot=(0, -15, 0), seg=10, ol=0),
         T.cyl(name + "_stuur", (0.66, 0, 1.08), 0.016, 0.62, zwart, rot=(90, 0, 0), seg=10, ol=0),
         T.box(name + "_kap_stuur", (0.66, 0, 1.03), (0.16, 0.3, 0.12), lak, bevel=0.05, ol=0)]
    p[-2].location.y = 0.31
    wielen = [T.cyl(f"{name}_wiel_{k}", (x, 0.05, 0.2), 0.2, 0.1, _p("rubber_wiel", (0.05, 0.05, 0.05), rough=0.8), rot=(90, 0, 0), seg=28, ol=0)
              for k, x in enumerate((0.62, -0.55))]
    lamp = T.cyl(name + "_koplamp", (0.6, 0, 0.92), 0.06, 0.04, ND.pbr("scooter_koplamp", (1, 0.97, 0.85), emit=(1, 0.95, 0.8), strength=8 if licht else 0),
                 rot=(0, 75, 0), seg=16, ol=0)
    o = T.merge(name + "_body", p, ol=0)
    objs = [o, lamp] + wielen
    for nm, xyz in (("_bestuurder", (-0.32, 0, 0.77)), ("_handvat_L", (0.66, 0.3, 1.08)), ("_handvat_R", (0.66, -0.3, 1.08))):
        e = bpy.data.objects.new(name + nm, None)
        e.empty_display_size = 0.08
        bpy.context.collection.objects.link(e)
        e.location = xyz
        objs.append(e)
    return _kids(root, objs)


def plek(name, loc, rot_z=0.0, size=0.25):
    """Empty als markering voor een personage of camera (de animatie zet de figuur hierop)."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "SINGLE_ARROW"
    e.empty_display_size = size
    bpy.context.collection.objects.link(e)
    e.location = loc
    e.rotation_euler.z = math.radians(rot_z)
    e["plek"] = True
    return e
