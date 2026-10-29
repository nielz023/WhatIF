"""Gedeelde set voor F11 en F12: de verjaardagskeuken na de knal, met de deur naar de gang open.

    from feest import party_set
    O = party_set(S)          # O["cake"], O["flames"], O["glow"], O["plates"], O["lighter"], O["gift"], O["wb5"], O["wb6"]
"""
import math

from v2 import *  # noqa: F401,F403

TX, TY, TZ = 0.2, -0.6, 0.76
DOORWAY = V(-2.46, 0.95, 0)


def party_set(S, ring=False):
    """Raamglas weg (dag 3 gesneuveld), geen ballonnen/slingers, deur naar de gang open met een stukje gang erachter.
    ring=False: de kring kraanvogels om de taart (en de laatste kraanvogel) zijn er nog niet."""
    hide = ("Keukenraam_glas", "Ballonnen", "Slinger") + (() if ring else ("Kraanvogel_tafelrand", "Kraanvogel_de_laatste"))
    for o in bpy.data.objects:
        if o.name.startswith(hide):
            o.hide_render = True
            o.hide_viewport = True
    cake = S.obj("Verjaardagstaart")
    flames = sorted([o for o in bpy.data.objects if o.name.startswith("Verjaardagstaart_vlam_")], key=lambda o: o.name)
    glow = S.obj("Verjaardagstaart_kaarslicht")
    plates = S.obj("Bordjes")
    lighter = S.obj("Aansteker")
    gift = S.obj("Cadeau_opa_oma")
    S.obj("Glas_water").location = (TX + 0.62, TY - 0.32, TZ)
    S.obj("Knijpfles").location = (TX - 0.1, TY - 0.32, TZ)
    wb_lines = {k: [o for o in bpy.data.objects if o.name.startswith(f"Whiteboard_achter_regel{k}")] for k in (5, 6)}

    # deuropening naar de gang (de deur staat open; opa en oma staan erin)
    S.obj("Keukendeur").hide_render = True
    S.obj("Keukendeur").hide_viewport = True
    for nm in ("Keuken_muur_left", "Keuken_plint_left"):
        w = S.obj(nm)
        cut = T.box(nm + "_deurgat", (DOORWAY.x, DOORWAY.y, -0.05), (0.5, 0.9, 2.1), P.m("wit"), bevel=0, ol=0)
        cut.hide_render = True
        cut.display_type = "WIRE"
        m = w.modifiers.new("deurgat", "BOOLEAN")
        m.object = cut
        m.operation = "DIFFERENCE"
        m.solver = "EXACT"
        m.use_hole_tolerant = True
    frame = S.mat("kozijn_wit", (0.95, 0.95, 0.93))
    for nm, loc, size in (("l", (-2.39, 0.47, 0), (0.06, 0.08, 2.05)), ("r", (-2.39, 1.43, 0), (0.06, 0.08, 2.05)),
                          ("b", (-2.39, 0.95, 2.03), (0.06, 1.04, 0.08))):
        T.box("Deurkozijn_" + nm, loc, size, frame, bevel=0.005, ol=0)
    blad = T.box("Keukendeur_open", (0, 0.45, 0), (0.05, 0.9, 2.03), S.mat("deur_keuken", (0.85, 0.85, 0.82)), bevel=0.01, ol=0)
    blad.location = (-2.5, 0.5, 0)
    blad.rotation_euler.z = math.radians(-100)       # open, de gang in
    gang_wall = S.mat("gang_behang", (0.93, 0.86, 0.72))
    T.box("Gang_vloer", (-3.6, 0.95, -0.02), (2.3, 1.6, 0.02), S.mat("gang_vloer", (0.55, 0.38, 0.24)), bevel=0, ol=0)
    T.box("Gang_loper", (-3.6, 0.95, 0.0), (2.0, 0.7, 0.012), S.mat("gang_loper", (0.62, 0.16, 0.16)), bevel=0.004, ol=0)
    T.box("Gang_plafond", (-3.6, 0.95, 2.6), (2.3, 1.6, 0.05), S.mat("gang_plafond", (0.97, 0.97, 0.95)), bevel=0, ol=0)
    for nm, loc, size in (("zuid", (-3.6, 0.13, 0), (2.3, 0.1, 2.6)), ("noord", (-3.6, 1.77, 0), (2.3, 0.1, 2.6)),
                          ("eind", (-4.75, 0.95, 0), (0.1, 1.6, 2.6))):
        T.box("Gang_muur_" + nm, loc, size, gang_wall, bevel=0, ol=0)
    T.box("Gang_lijst", (-3.6, 1.71, 1.5), (0.4, 0.02, 0.3), S.mat("lijst_goud", (0.85, 0.72, 0.4)), bevel=0.005, ol=0)
    ld = bpy.data.lights.new("Gang_lamp", "POINT")
    ld.energy = 60
    ld.color = (1.0, 0.86, 0.66)
    lo = bpy.data.objects.new("Gang_lamp", ld)
    lo.location = (-3.4, 0.95, 2.4)
    T._link(lo)
    return dict(cake=cake, flames=flames, glow=glow, plates=plates, lighter=lighter, gift=gift, wb5=wb_lines[5], wb6=wb_lines[6])
