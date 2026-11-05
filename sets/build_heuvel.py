"""Set (video 4, Never Die): DE HEUVEL met bank, eik en uitzicht op de stad. Vaste plek voor elke tijdsprong.

Het vaste camerastandpunt heet in elke variant CAM_HEUVEL (zelfde plek, zelfde lens), zodat een harde cut
tussen de jaren precies op elkaar valt. De bank staat op de oorsprong en kijkt naar +Y (de stad).

Varianten:
    2032     scène 8:  zomer, zonsondergang, houten bank, gewone stad
    2051     scène 9:  herfst, twee nieuwe glazen torens, opengeklapt horloge op de bank + bloemen (9d)
    2086     scène 11: winter, kale eik, sneeuw op de bank, twee bosjes bloemen in de sneeuw, vliegende lichtjes
    2110     scène 12: lente, eik weer in blad, nieuwe stenen bank, nog meer torens
    3026     scène 14: ruïnes: stad overwoekerd, eik is een reus, alleen de stenen voet van de bank staat nog
    ijs      scène 15: een witte vlakte; alleen de top van de bankvoet en een paar torenspitsen steken uit het ijs
    1mln     scène 16: woeste groene vlakte, vreemde grazers, drie kolonieschepen stijgen op; schip met loopplank
    dood     scène 0, 2, 19: dode aarde: zwartgebakken, gloeiende scheuren, enorme rode zon, as, vuurmuur
    super    scène 17, 17b: supercontinent: rode rotsen, droog gebergte, de laatste zonsverduistering (Zon + Maan)
    zout     scène 18: droge zeebodem: witte zoutvlakte, wrak van een toekomstschip, scheve vuurtoren, laatste plas

Gebruik:
    python3 sets/build_heuvel.py <variant> [uitvoermap]
Snel testen: SET_PCT=40 SET_SAMPLES=12 SET_MAXCAMS=1
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import stad as S  # noqa: E402
from lib import nooitdood as ND  # noqa: E402
from lib import street as ST  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
VAR = args[0] if args else "2032"
OUT = args[1] if len(args) > 1 else f"/mnt/project-files/videos/nooit-dood/sets/01_heuvel_{VAR}"
rnd = random.Random(26)

# ---------------------------------------------------------------------------
# Licht per variant
# ---------------------------------------------------------------------------
M = T.MOODS
mood = {
    "2032": dict(M["zonsondergang"], sun_rot=(78, 0, 152), sun_disc=dict(color=(1.0, 0.78, 0.42), size=6.0, dir=(152, 5))),
    "2051": dict(M["dag"], sun_color=(1.0, 0.80, 0.55), sun_strength=0.95, sun_rot=(62, 0, 140),
                 sky_horizon=(0.95, 0.80, 0.62), sky_top=(0.30, 0.45, 0.80), fog_color=(0.95, 0.82, 0.66), bloom=0.4),
    "2086": dict(M["bewolkt"], sky_top=(0.45, 0.52, 0.62), sky_horizon=(0.78, 0.82, 0.88), sun_color=(0.85, 0.9, 1.0),
                 sun_strength=0.55, ambient=(0.45, 0.50, 0.58), fog_color=(0.80, 0.84, 0.90), fog_start=20.0,
                 fog_end=320.0, bloom=0.5),
    "2110": dict(M["ochtend"], sun_rot=(58, 0, 125), sky_top=(0.30, 0.55, 1.0), bloom=0.3),
    "3026": dict(M["dag"], sun_rot=(50, 0, 130), sun_color=(1.0, 0.94, 0.80), fog_color=(0.75, 0.85, 0.80),
                 fog_start=40.0, bloom=0.3),
    "ijs": dict(M["bewolkt"], sky_top=(0.55, 0.65, 0.82), sky_horizon=(0.86, 0.92, 1.0), ground_glow=(0.8, 0.88, 1.0),
                sun_color=(0.80, 0.88, 1.0), sun_strength=0.6, sun_rot=(65, 0, 160), ambient=(0.55, 0.62, 0.75),
                fog_color=(0.85, 0.90, 0.98), fog_start=10.0, fog_end=220.0, fog_max=0.8, bloom=0.5, exposure=-0.35),
    "1mln": dict(M["zonsondergang"], sky_top=(0.25, 0.32, 0.62), sky_horizon=(1.0, 0.70, 0.40), sun_color=(1.0, 0.80, 0.50),
                 sun_strength=1.1, sun_rot=(72, 0, 150), sun_disc=dict(color=(1.0, 0.85, 0.5), size=5.0, dir=(150, 12)),
                 bloom=0.6),
    "dood": dict(sky_top=(0.20, 0.02, 0.01), sky_horizon=(1.0, 0.25, 0.04), ground_glow=(0.6, 0.12, 0.03),
                 sun_color=(1.0, 0.30, 0.08), sun_strength=2.2, sun_rot=(70, 0, 180), ambient=(0.35, 0.08, 0.04),
                 shadow_tint=(0.4, 0.1, 0.1), lit_tint=(1.0, 0.5, 0.3), fog_color=(0.9, 0.25, 0.08), fog_start=20.0,
                 fog_end=500.0, fog_max=0.6, sun_disc=None, bloom=1.2, exposure=-0.4),
    # tijdens de verduistering (17b): schemer, lage zon, donkere hemel (sun_strength keyframen 1.2 -> 0.25 als de maan schuift)
    "super": dict(M["dag"], sky_top=(0.05, 0.06, 0.13), sky_horizon=(0.62, 0.36, 0.24), sun_color=(1.0, 0.70, 0.50),
                  sun_strength=0.3, ambient=(0.10, 0.08, 0.10), exposure=0.1, sun_rot=(55, 0, 180), fog_color=(0.92, 0.72, 0.55), fog_start=60.0, bloom=0.5),
    "zout": dict(M["dag"], sky_top=(0.52, 0.62, 0.78), sky_horizon=(0.98, 0.96, 0.92), ground_glow=(1.0, 1.0, 0.98),
                 sun_color=(1.0, 0.98, 0.94), sun_strength=1.5, sun_rot=(62, 0, 175),
                 sun_disc=dict(color=(1.0, 1.0, 0.96), size=12.0, dir=(175, 30)), ambient=(0.6, 0.6, 0.62),
                 fog_color=(0.95, 0.94, 0.92), fog_start=30.0, fog_end=500.0, bloom=0.9, exposure=-0.45),
}[VAR]
T.new_scene("Heuvel_" + VAR, mood, samples=32)

HILL = VAR not in ("super", "zout", "ijs")


def hz(x, y):
    """Hoogte van de heuvel: vlak plateau rond de bank, steile helling naar de stad (+Y)."""
    if not HILL:
        return 0.0
    front = 44.0 * (lambda t: t * t * (3 - 2 * t))(max(0.0, min(1.0, (y - 6.0) / 90.0)))
    back = 3.0 * (lambda t: t * t * (3 - 2 * t))(max(0.0, min(1.0, (-y - 7.0) / 34.0)))
    side = 5.0 * (lambda t: t * t * (3 - 2 * t))(max(0.0, min(1.0, (abs(x) - 11.0) / 45.0))) * (0.4 + 0.6 * max(0, min(1, (y + 10) / 40)))
    flat = math.exp(-((x * x + y * y) / 30.0))
    n = (0.35 * math.sin(x * 0.17 + 1.3) * math.cos(y * 0.13) + 0.18 * math.sin(x * 0.41 + y * 0.29)) * (1 - flat)
    return -(front + back + side) + n


def terrain(name, mat, x0=-140, x1=140, y0=-60, y1=200, step=1.25):
    bm = bmesh.new()
    nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
    vs = [[bm.verts.new((x0 + i * step, y0 + j * step, hz(x0 + i * step, y0 + j * step))) for i in range(nx + 1)]
          for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = T._obj(name, me, mat, (0, 0, 0), None, 0, smooth=True)
    return o


def crack_ground(name, base, crack_col, crack_strength, scale=1.6, dark=None):
    """Grond met een Voronoi-scheurpatroon: zwartgebakken met gloeiende scheuren, of zout met donkere naden."""
    mt = bpy.data.materials.new(name)
    mt.use_nodes = True
    N, L = mt.node_tree.nodes, mt.node_tree.links
    b = N.get("Principled BSDF")
    b.inputs["Roughness"].default_value = 0.85
    tc = N.new("ShaderNodeTexCoord")
    vo = N.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = scale
    L.new(tc.outputs["Object"], vo.inputs["Vector"])
    vo2 = N.new("ShaderNodeTexVoronoi")
    vo2.feature = "DISTANCE_TO_EDGE"
    vo2.inputs["Scale"].default_value = scale * 4.3
    L.new(tc.outputs["Object"], vo2.inputs["Vector"])
    mn = N.new("ShaderNodeMath")
    mn.operation = "MINIMUM"
    m1 = N.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    m1.inputs[1].default_value = 3.0      # grote cellen: dunnere naden (anders brede wazige banen)
    L.new(vo.outputs["Distance"], m1.inputs[0])
    L.new(m1.outputs[0], mn.inputs[0])
    m2 = N.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    m2.inputs[1].default_value = 1.6
    L.new(vo2.outputs["Distance"], m2.inputs[0])
    L.new(m2.outputs[0], mn.inputs[1])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.035
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    L.new(mn.outputs[0], mr.inputs["Value"])
    nz = N.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*base, 1)
    mix.inputs["B"].default_value = (*(dark or [c * 0.7 for c in base]), 1)
    L.new(nz.outputs["Fac"], mix.inputs["Factor"])
    if crack_strength > 0:
        L.new(mix.outputs["Result"], b.inputs["Base Color"])
        b.inputs["Emission Color"].default_value = (*crack_col, 1)
        L.new(mr.outputs["Result"], b.inputs["Emission Strength"])
        em = N.new("ShaderNodeMath")
        em.operation = "MULTIPLY"
        em.inputs[1].default_value = crack_strength
        L.new(mr.outputs["Result"], em.inputs[0])
        L.new(em.outputs[0], b.inputs["Emission Strength"])
    else:
        m3 = N.new("ShaderNodeMix")
        m3.data_type = "RGBA"
        m3.inputs["B"].default_value = (*crack_col, 1)
        L.new(mr.outputs["Result"], m3.inputs["Factor"])
        L.new(mix.outputs["Result"], m3.inputs["A"])
        L.new(m3.outputs["Result"], b.inputs["Base Color"])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.02
    # alleen de fijne scheuren in de bump; de grote cellen gaven brede, wazige "schaduwnetten"
    mr2 = N.new("ShaderNodeMapRange")
    mr2.inputs["From Min"].default_value = 0.0
    mr2.inputs["From Max"].default_value = 0.035
    mr2.inputs["To Min"].default_value = 1.0
    mr2.inputs["To Max"].default_value = 0.0
    L.new(m2.outputs[0], mr2.inputs["Value"])
    L.new(mr2.outputs["Result"], bump.inputs["Height"])
    L.new(bump.outputs["Normal"], b.inputs["Normal"])
    mt["glans"] = True
    return mt


def city(era, ruin=False):
    """De stad in het dal (zelfde stad als video 3), per tijdperk iets anders."""
    T.use_collection(T.collection("Stad " + era))
    cols = [(0.66, 0.58, 0.52), (0.52, 0.55, 0.62), (0.72, 0.62, 0.50), (0.45, 0.48, 0.52), (0.80, 0.75, 0.68)]
    if ruin:
        cols = [(0.42, 0.45, 0.36), (0.38, 0.42, 0.40), (0.46, 0.44, 0.36)]
    lit = {"2032": 0.35, "2051": 0.15, "2086": 0.45, "2110": 0.1}.get(era, 0.0)
    r = random.Random(77)
    zc = -44.0
    blds = []
    for row in range(4):
        for i in range(20):
            x = -270 + i * 28 + r.uniform(-4, 4) + row * 7
            y = 300 + row * 34 + r.uniform(-4, 4)
            if abs(x) < 8 and row == 0:
                continue
            b = S.building(f"Flat_{row}_{i}", (x, y, zc), w=r.uniform(10, 14), d=11, floors=r.randint(4 + row, 8 + 2 * row),
                           color=r.choice(cols), lit=lit, seed=row * 40 + i, block="ABCD"[row])
            blds.append(b)
            if ruin:
                b.rotation_euler.x = math.radians(r.uniform(-3, 3))
                b.rotation_euler.y = math.radians(r.uniform(-4, 4))
    if era in ("2051", "2086", "2110"):
        towers = [(-40, 360, 120), (30, 380, 150)]
        if era in ("2086", "2110"):
            towers += [(-110, 400, 105), (95, 395, 135)]
        if era == "2110":
            towers += [(5, 440, 190), (-170, 430, 95), (160, 430, 125)]
        for k, (x, y, h) in enumerate(towers):
            ND.glazen_toren(f"Glazen_toren_{k}", (x, y, zc), w=r.uniform(12, 16), h=h, seed=k, round_=(k % 2 == 1),
                            lit=0.5 if era == "2086" else 0.25, col=[(0.35, 0.55, 0.70), (0.45, 0.62, 0.72)][k % 2])
    if era == "2086":
        ND.vliegende_lichtjes("Vliegende_lichtjes", (0, 380, zc), spread=(420, 160, 40), n=80, z0=55)
    if ruin:
        # natuur neemt het over: bomen uit de daken, klimop langs de gevels, bomen in de straten
        km = T.toon("blad_klimop_gevel", (0.14, 0.36, 0.12))
        kl = []
        for b in blds:
            bx, by, _ = b.location
            hgt = max(c.z for c in [b.matrix_world @ Vector(cc) for ch in b.children if ch.type == "MESH" for cc in ch.bound_box])
            for k in range(3):
                kl.append(T.box(f"{b.name}_klimop{k}", (bx + r.uniform(-5, 5), by - 0.3, zc), (r.uniform(2, 4), 0.5,
                                (hgt - zc) * r.uniform(0.4, 0.95)), km, bevel=0.1, ol=0))
            if r.random() < 0.7:
                P.tree(f"{b.name}_dakboom", (bx + r.uniform(-3, 3), by + 5, hgt), h=r.uniform(4, 7), r=r.uniform(2, 3.2),
                       seed=r.randint(0, 99))
        T.merge("Klimop_gevels", kl, ol=0)
        for k in range(40):
            P.tree(f"Straatboom_{k}", (r.uniform(-200, 200), r.uniform(280, 420), zc), h=r.uniform(9, 15),
                   r=r.uniform(3.5, 5.5), seed=k)
    T.plane("Dal_grond", (0, 600, zc - 0.05), (3000, 1400), T.toon("gras_dal" if era not in ("dood",) else "grond_dal",
                                                                     (0.24, 0.42, 0.16) if era != "ijs" else (0.9, 0.95, 1.0)))
    T.use_collection(None)


def grass_tufts(name, n, area, col, z_of=hz, seed=3):
    r = random.Random(seed)
    gm = T.toon(f"gras_pluk_{'%.2f%.2f%.2f' % col}", col)
    ps = []
    for k in range(n):
        x, y = r.uniform(area[0], area[1]), r.uniform(area[2], area[3])
        if abs(x) < 1.4 and abs(y) < 0.8:
            continue
        z = z_of(x, y)
        for j in range(5):
            ps.append(T.cyl(f"{name}_{k}_{j}", (x + r.uniform(-0.07, 0.07), y + r.uniform(-0.07, 0.07), z), 0.012,
                            r.uniform(0.07, 0.16), gm, r2=0.001, seg=4, ol=0,
                            rot=(r.uniform(-25, 25), r.uniform(-25, 25), 0)))
    return T.merge(name, ps, ol=0)


def flowers(name, n, area, cols, seed=5):
    r = random.Random(seed)
    ps = []
    for k in range(n):
        x, y = r.uniform(area[0], area[1]), r.uniform(area[2], area[3])
        if abs(x) < 1.4 and abs(y) < 0.8:
            continue
        c = r.choice(cols)
        ps.append(T.sphere(f"{name}_{k}", (x, y, hz(x, y) + 0.12), 0.045, T.toon(f"bloem_wild_{'%.2f%.2f%.2f' % c}", c),
                           scale=(1, 1, 0.5), seg=8, ol=0))
    return T.merge(name, ps, ol=0)


def leaves_ground(name, n, area, cols, seed=6):
    r = random.Random(seed)
    ps = []
    for k in range(n):
        x, y = r.uniform(area[0], area[1]), r.uniform(area[2], area[3])
        c = r.choice(cols)
        ps.append(T.box(f"{name}_{k}", (x, y, hz(x, y) + 0.01), (0.09, 0.06, 0.004),
                        T.toon(f"blad_gevallen_{'%.2f%.2f%.2f' % c}", c), rot=(r.uniform(-20, 20), r.uniform(-20, 20),
                                                                               r.uniform(0, 360)), bevel=0, ol=0))
    return T.merge(name, ps, ol=0)


# ---------------------------------------------------------------------------
# Ondergrond
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Heuvel"))
EIK = (-5.6, 3.4, 0)
if VAR in ("2032", "2051", "2110", "3026", "1mln"):
    gcol = {"2032": (0.30, 0.50, 0.18), "2051": (0.48, 0.50, 0.20), "2110": (0.34, 0.60, 0.20), "3026": (0.20, 0.44, 0.14),
            "1mln": (0.16, 0.48, 0.14)}[VAR]
    terrain("Heuvel_grond", T.toon("gras_heuvel_" + VAR, gcol))
    grass_tufts("Graspollen", 2200 if VAR in ("3026", "1mln") else 1400, (-16, 16, -14, 12),
                tuple(c * 0.85 for c in gcol))
elif VAR == "2086":
    terrain("Heuvel_grond", T.toon("sneeuw_heuvel", (0.88, 0.92, 0.98)))
elif VAR == "dood":
    terrain("Heuvel_grond", crack_ground("grond_verbrand", (0.035, 0.028, 0.026), (1.0, 0.32, 0.05), 3.0, scale=0.9,
                                         dark=(0.015, 0.012, 0.012)))
elif VAR == "ijs":
    T.plane("Ijsvlakte", (0, 400, 0.12), (3000, 3000), crack_ground("sneeuw_ijs_vlakte", (0.86, 0.92, 1.0), (0.62, 0.74, 0.9),
                                                                    0.0, scale=0.05))
elif VAR == "super":
    rots = crack_ground("zand_rots_rood", (0.55, 0.22, 0.10), (0.30, 0.10, 0.05), 0.0, scale=0.25, dark=(0.42, 0.16, 0.08))
    T.plane("Rode_vlakte", (0, 400, 0), (3000, 3000), rots)
elif VAR == "zout":
    T.plane("Zoutvlakte", (0, 400, 0), (3000, 3000), crack_ground("zout_vlakte", (0.95, 0.94, 0.90), (0.62, 0.58, 0.52), 0.0,
                                                                  scale=0.45, dark=(0.88, 0.86, 0.80)))

# ---------------------------------------------------------------------------
# Eik en bank (of wat ervan over is)
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Eik en bank"))
if VAR == "2032":
    ND.eik("Eik", EIK, "zomer")
    ND.heuvelbank("Bank", (0, 0, 0), rot_z=180)
elif VAR == "2051":
    ND.eik("Eik", EIK, "herfst")
    ND.heuvelbank("Bank", (0, 0, 0), rot_z=180)
    leaves_ground("Gevallen_bladeren", 500, (-10, 4, -6, 8), [(0.80, 0.34, 0.06), (0.92, 0.58, 0.10), (0.62, 0.22, 0.06)])
    ND.zakhorloge("Zakhorloge", (0.25, 0.05, 0.47), rot=(0, 0, 200), open_=0.55)
    ND.bloemen("Bloemen_opa", (1.25, -0.25, 0.0), rot_z=-30, kleur=(0.95, 0.95, 0.92), seed=1)
elif VAR == "2086":
    ND.eik("Eik", EIK, "winter", sneeuw=True)
    ND.heuvelbank("Bank", (0, 0, 0), rot_z=180, sneeuw=True)
    ND.bloemen("Bloemen_mama", (-1.05, -0.35, 0.0), rot_z=-10, kleur=(0.95, 0.40, 0.55), seed=2)
    ND.bloemen("Bloemen_papa", (-1.35, -0.1, 0.0), rot_z=20, kleur=(0.95, 0.85, 0.30), seed=3)
    sn = [T.sphere(f"Sneeuwhoop_{k}", (rnd.uniform(-12, 12), rnd.uniform(-8, 10), 0), rnd.uniform(0.3, 0.9),
                   T.toon("sneeuw_hoop", (0.9, 0.94, 1.0)), scale=(1.6, 1.2, 0.35), seg=12, ol=0) for k in range(30)]
    for s in sn:
        s.location.z = hz(s.location.x, s.location.y)
    T.merge("Sneeuwhopen", sn, ol=0)
    ND.snoepzak("Snoepzak", (-0.55, 0.05, 0.47), rot_z=10)
elif VAR == "2110":
    ND.eik("Eik", EIK, "lente")
    ND.stenen_bank("Stenen_bank", (0, 0, 0), rot_z=180)
    flowers("Wilde_bloemen", 300, (-14, 14, -10, 10), [(0.95, 0.85, 0.2), (0.95, 0.95, 0.95), (0.85, 0.4, 0.9)])
elif VAR == "3026":
    ND.eik("Eik", EIK, "groen", schaal=1.9, klimop=True)
    ND.stenen_bank("Bankvoet", (0, 0, 0), rot_z=180, alleen_voet=True, mos=1.0)
    for k in range(25):
        ST.bird(f"Vogel_{k}", (rnd.uniform(-60, 60), rnd.uniform(40, 200), rnd.uniform(10, 40)), rot_z=rnd.uniform(0, 360),
                    span=0.8, wings_up=rnd.uniform(-20, 40))
elif VAR == "ijs":
    ND.stenen_bank("Bankvoet", (0, 0, -0.2), rot_z=180, alleen_voet=True)
    for k, (x, y, h) in enumerate([(-40, 220, 9), (35, 300, 14), (120, 420, 6), (-160, 520, 11), (8, 180, 4)]):
        T.cyl(f"Torenspits_{k}", (x, y, 0), 2.0 + h * 0.15, h, T.toon("glas_toren_ijs", (0.35, 0.5, 0.62)), r2=0.3, seg=12, ol=0)
        T.cyl(f"Torenspits_{k}_naald", (x, y, h), 0.2, h * 0.5, T.toon("staal_spits", (0.8, 0.82, 0.85)), r2=0.03, seg=8, ol=0)
    # sneeuwstorm: strepen in de lucht rond de camera
    ps = []
    sm = T.toon("sneeuw_vlok", (0.95, 0.97, 1.0))
    for k in range(1800):
        x, y, z = rnd.uniform(-25, 25), rnd.uniform(-20, 40), rnd.uniform(0.1, 9)
        ps.append(T.box(f"Vlok_{k}", (x, y, z), (0.012, 0.18, 0.012), sm, rot=(10, 0, 60), bevel=0, ol=0))
    T.merge("Sneeuwstorm", ps, ol=0)
    for k in range(40):
        s = T.sphere(f"Sneeuwduin_{k}", (rnd.uniform(-60, 60), rnd.uniform(-20, 150), 0.1), rnd.uniform(1.5, 5),
                     T.toon("sneeuw_duin", (0.88, 0.93, 1.0)), scale=(3, 1.2, 0.18), rot=(0, 0, 60), seg=14, ol=0)
elif VAR == "1mln":
    ND.stenen_bank("Bankvoet", (0, 0, 0), rot_z=180, alleen_voet=True, mos=1.5)
    flowers("Wilde_bloemen", 400, (-16, 16, -10, 12), [(0.95, 0.55, 0.15), (0.75, 0.30, 0.85), (0.95, 0.95, 0.85)])
    for k in range(14):
        x, y = rnd.uniform(-60, 60), rnd.uniform(40, 140)
        ND.grazer(f"Grazer_{k}", (x, y, hz(x, y)), rot_z=rnd.uniform(0, 360), schaal=rnd.uniform(0.9, 1.3), seed=k,
                  col=[(0.36, 0.30, 0.24), (0.45, 0.38, 0.30), (0.28, 0.26, 0.22)][k % 3])
    for k in range(18):
        x, y = rnd.uniform(-120, 120), rnd.uniform(30, 190)
        P.tree(f"Wildboom_{k}", (x, y, hz(x, y)), h=rnd.uniform(7, 12), r=rnd.uniform(3, 4.5), seed=k)
    for k, (x, y, z, h) in enumerate([(-260, 1300, 160, 420), (180, 1500, 320, 480), (420, 1200, 90, 380)]):
        ND.ruimteschip(f"Kolonieschip_{k}", (x, y, z), hoogte=h)
    ND.ruimteschip("Schip_loopplank", (40, 150, -42), hoogte=150, vlam=False, rot_z=-20, scherm=("GOODBYE, EARTH", "00:00:00"))
    ND.loopplank("Loopplank", (32.5, 130, -40.5), rot_z=-20, lengte=10)
elif VAR == "dood":
    ND.eik("Eik_verkoold", EIK, "verkoold", schaal=0.9)
    ND.stenen_bank("Bankvoet", (0, 0, 0), rot_z=180, alleen_voet=True, verkoold=True)
    # de rode reus: een enorme gloeiende bol achter de horizon + corona
    zon = T.sphere("Rode_zon", (0, 2600, 260), 950, ND.pbr("Rode_zon_gloed", (1.0, 0.25, 0.05), emit=(1.0, 0.28, 0.05),
                                                          strength=8.0), seg=64, ol=0)
    zon.visible_shadow = False
    T.sphere("Rode_zon_corona", (0, 2650, 260), 1080, ND.pbr("Rode_zon_corona", (1.0, 0.35, 0.08), emit=(1.0, 0.4, 0.1),
                                                              strength=1.2, alpha=0.25), seg=48, ol=0).visible_shadow = False
    # vuurmuur aan de horizon (0c, 19d): keyframe location.y van ~700 naar 0
    vm = T.cyl("Vuurmuur", (0, 0, -30), 700, 120, ND.pbr("Vuurmuur_gloed", (1.0, 0.3, 0.06), emit=(1.0, 0.28, 0.05), strength=3.0,
                                                          alpha=0.85), seg=96, ol=0, cap=False)
    vm.location = (0, 0, -30)
    vm.visible_shadow = False
    vm.scale = (1, 1, 1)
    vm["uitleg"] = "keyframe scale x/y van 1.0 naar ~0.01 = de vuurmuur komt op hem af"
    # as die opwaait
    ps = []
    am = T.toon("as_grijs", (0.10, 0.09, 0.09))
    gm = ND.pbr("as_gloeiend", (1.0, 0.4, 0.1), emit=(1.0, 0.45, 0.12), strength=6.0)
    for k in range(900):
        x, y, z = rnd.uniform(-20, 20), rnd.uniform(-15, 35), rnd.uniform(0.2, 12)
        ps.append(T.box(f"As_{k}", (x, y, z), (0.03, 0.03, 0.008), gm if k % 7 == 0 else am,
                        rot=(rnd.uniform(0, 90), rnd.uniform(0, 90), rnd.uniform(0, 90)), bevel=0, ol=0))
    T.merge("As", ps, ol=0)
    # gestolde ruïnes in het dal
    for k in range(20):
        x, y = rnd.uniform(-200, 200), rnd.uniform(280, 420)
        T.box(f"Ruine_{k}", (x, y, -44), (rnd.uniform(6, 14), rnd.uniform(6, 12), rnd.uniform(4, 30)),
              T.toon("beton_verkoold", (0.05, 0.04, 0.04)), rot=(rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(0, 90)),
              bevel=0.3, ol=0)
elif VAR == "super":
    # rode rotsen, tafelbergen en een bergkam
    rk = []
    rm = T.toon("steen_rots_rood", (0.50, 0.20, 0.09))
    rm2 = T.toon("steen_rots_oker", (0.66, 0.34, 0.14))
    tex = bpy.data.textures.new("rots_ruis", "CLOUDS")
    tex.noise_scale = 1.2
    for k in range(70):
        x, y = rnd.uniform(-60, 60), rnd.uniform(-20, 140)
        if abs(x) < 3 and -3 < y < 3:
            continue
        s = rnd.uniform(0.4, 3.0) * (1 + max(0, y) / 80)
        o = T.sphere(f"Rots_{k}", (x, y, -s * 0.2), s, rm if k % 3 else rm2, scale=(1.3, 1.0, 0.7), seg=14, ol=0,
                     rot=(0, 0, rnd.uniform(0, 360)))
        d = o.modifiers.new("ruis", "DISPLACE")
        d.texture = tex
        d.strength = s * 0.35
        rk.append(o)
    T.merge("Rotsen", rk, ol=0)
    for k in range(9):
        x = -500 + k * 125 + rnd.uniform(-30, 30)
        T.cyl(f"Tafelberg_{k}", (x, 700 + rnd.uniform(-100, 200), 0), rnd.uniform(40, 90), rnd.uniform(40, 110),
              rm2 if k % 2 else rm, r2=rnd.uniform(30, 70), seg=10, ol=0)
    for k in range(14):
        x = -900 + k * 140
        T.cyl(f"Gebergte_{k}", (x, 1500, 0), rnd.uniform(150, 260), rnd.uniform(160, 340),
              T.toon("steen_gebergte_paars", (0.42, 0.24, 0.26)), r2=4, seg=7, ol=0)
    T.cyl("Bergkam", (14, 30, -4), 22, 12, rm, r2=3, seg=9, ol=0, rot=(0, 0, 20))
    # de laatste zonsverduistering: Maan iets kleiner dan de Zon, zodat er een ring overblijft (17b-b)
    zd = Vector((0, math.cos(math.radians(32)), math.sin(math.radians(32))))
    zon = T.sphere("Zon_17b", tuple(zd * 2600), 44, ND.pbr("Zon_17b_gloed", (1.0, 0.95, 0.85), emit=(1.0, 0.92, 0.75),
                                                           strength=60.0), seg=48, ol=0)
    zon.visible_shadow = False
    maan = T.sphere("Maan", tuple(zd * 1800), 29.4, T.toon("maan_donker", (0.02, 0.02, 0.025)), seg=48, ol=0)
    T.sphere("Zon_17b_corona", tuple(zd * 2610), 75, ND.pbr("Zon_17b_corona", (1.0, 0.85, 0.65), emit=(1.0, 0.82, 0.6),
                                                            strength=3.0, alpha=0.18), seg=48, ol=0).visible_shadow = False
    maan["uitleg"] = "location keyframen langs de zon; op zd*1800 (huidige plek) blijft precies een ring over"
elif VAR == "zout":
    # wrak van een toekomstschip, half in het zout
    wm = T.toon("metaal_wrak_roest", (0.42, 0.20, 0.10))
    wm2 = T.toon("metaal_wrak_wit", (0.70, 0.68, 0.64))
    w = [T.sphere("Wrak_romp", (0, 0, 0), 1.0, wm2, scale=(70, 14, 12), seg=40, ol=0)]
    for k in range(14):
        w.append(T.torus(f"Wrak_rib{k}", (-55 + k * 8, 0, 0), 13.5, 0.7, wm, rot=(0, 90, 0), seg=40, seg2=8, ol=0))
    wr = T.merge("Wrak_toekomstschip", w, ol=0)
    wr.location = (34, 120, -5)
    wr.rotation_euler = (math.radians(12), math.radians(-8), math.radians(25))
    # scheve vuurtoren
    vt = [T.cyl("Vuurtoren_schacht", (0, 0, 0), 3.0, 30, T.toon("steen_vuurtoren_wit", (0.85, 0.84, 0.80)), r2=2.2, seg=24, ol=0)]
    for k in range(3):
        vt.append(T.cyl(f"Vuurtoren_band{k}", (0, 0, 5 + k * 9), 2.95 - k * 0.25, 4, T.toon("verf_vuurtoren_rood_roest",
                                                                                         (0.55, 0.12, 0.06)), seg=24, ol=0))
    vt += [T.cyl("Vuurtoren_kap", (0, 0, 30), 2.6, 4, T.glass("glas_vuurtoren", (0.5, 0.6, 0.6), 0.5), seg=16, ol=0),
           T.cyl("Vuurtoren_dak", (0, 0, 34), 3.0, 2.5, wm, r2=0.3, seg=16, ol=0)]
    vto = T.merge("Vuurtoren", vt, ol=0)
    vto.location = (-38, 70, -8)
    vto.rotation_euler = (math.radians(-6), math.radians(14), 0)
    # de laatste plassen (18c) met damp
    for k, (x, y, r_) in enumerate([(2.5, 3.0, 0.9), (-6, 12, 1.6), (9, 20, 2.2)]):
        T.cyl(f"Plas_{k}", (x, y, -0.015), r_, 0.02, ND.pbr("water_plas", (0.45, 0.6, 0.62), rough=0.05), seg=32, ol=0)
        damp = [T.sphere(f"Damp_{k}_{j}", (x + rnd.uniform(-0.4, 0.4), y + rnd.uniform(-0.4, 0.4), 0.3 + j * 0.45),
                         r_ * (0.25 + j * 0.1), ND.pbr("damp", (1, 1, 1), rough=1.0, alpha=0.05), scale=(1, 1, 1.8), seg=12, ol=0)
                for j in range(5)]
        T.merge(f"Damp_{k}", damp, ol=0)
    for k in range(30):
        T.sphere(f"Zoutkorst_{k}", (rnd.uniform(-60, 60), rnd.uniform(-10, 160), 0), rnd.uniform(0.3, 1.5),
                 T.toon("zout_korst", (0.97, 0.96, 0.93)), scale=(2.5, 1.5, 0.15), seg=10, ol=0)

if VAR in ("2032", "2051", "2086", "2110"):
    city(VAR)
elif VAR == "3026":
    city("3026", ruin=True)
elif VAR in ("1mln", "dood"):
    T.plane("Dal_grond", (0, 600, -44.05), (3000, 1400), T.toon("gras_dal_wild" if VAR == "1mln" else "grond_dal_verbrand",
                                                                  (0.18, 0.44, 0.14) if VAR == "1mln" else (0.03, 0.025, 0.02)))

# ---------------------------------------------------------------------------
# Hoofdpersonage (schaal) en camera's
# ---------------------------------------------------------------------------
T.use_collection(None)
if VAR in ("dood",):
    T.character((0.0, -1.2, 0.0), rot_z=0)
elif VAR in ("super", "zout", "ijs"):
    T.character((0.6, -1.0, 0.12 if VAR == "ijs" else 0.0), rot_z=10)
else:
    T.character((1.3, -0.7, hz(1.3, -0.7)), rot_z=20)

cams = [T.camera("CAM_HEUVEL", (-3.6, -9.5, 2.3), (0.8, 8.0, -0.6), lens=22)]
if VAR in ("2032", "2051", "2086", "2110", "3026"):
    cams.append(T.camera("CAM_BANK_VOOR", (2.4, 4.6, 1.15), (-0.2, 0.0, 0.8), lens=30))
    cams.append(T.camera("CAM_STAD", (0.6, -1.6, 1.25), (4, 300, -30), lens=35))
if VAR == "2051":
    cams.append(T.camera("CAM_HORLOGE_BANK", (0.55, 0.45, 0.68), (0.25, 0.05, 0.47), lens=50))
if VAR == "2086":
    cams.append(T.camera("CAM_BLOEMEN_SNEEUW", (-0.6, -2.4, 0.55), (-1.2, -0.2, 0.1), lens=40))
if VAR == "3026":
    cams.append(T.camera("CAM_RUINES", (-2, -4, 3.5), (0, 300, -28), lens=28))
if VAR == "ijs":
    cams.append(T.camera("CAM_VLAKTE_DRONE", (-30, -60, 40), (10, 120, 0), lens=24))
    cams.append(T.camera("CAM_STORM", (3.5, -4.5, 1.3), (0.6, -1.0, 1.0), lens=35))
if VAR == "1mln":
    cams.append(T.camera("CAM_SCHEPEN_LAAG", (-1.5, -3.5, 0.6), (0, 200, 60), lens=24))
    cams.append(T.camera("CAM_LOOPPLANK", (12, 86, -40.3), (38, 140, -22), lens=28))
if VAR == "dood":
    cams += [T.camera("CAM_0a_CLOSE_ZON", (0.35, -3.1, 1.32), (0.0, -1.2, 1.5), lens=40),
             T.camera("CAM_0c_LAAG_WIJD", (0.8, -6.5, 0.35), (0, 20, 5), lens=20)]
if VAR == "super":
    cams += [T.camera("CAM_17b_ECLIPS_LAAG", (1.5, -4.0, 0.4), (0, 2600 * 0.85, 2600 * 0.53), lens=24),
            T.camera("CAM_17b_RING", (1.8, -2.6, 0.9), (0, 2600 * 0.848, 2600 * 0.53), lens=200)]
if VAR == "zout":
    cams.append(T.camera("CAM_WRAK", (-6, -10, 2.4), (30, 110, 4), lens=24))
    cams.append(T.camera("CAM_PLAS", (3.6, 1.3, 0.6), (2.5, 3.0, 0.0), lens=35))
blend, renders = T.finish(OUT, "heuvel_" + VAR, cams)
print("KLAAR", blend, renders)
