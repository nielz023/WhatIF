"""Setcheck: zoekt GATEN in een set vanuit elke camera (lessen video 1-4: ontbrekende muren, camera die
door een muur kijkt, de lucht door een gat in het plafond, een eindeloze grond zonder achtergrond).

Per camera schiet hij een raster van stralen (standaard 64x36) door het beeld:
    binnen (interieur): elke straal die NIETS raakt is een gat -> SET_GAT
    buiten: een straal die niets raakt en (bijna) horizontaal of naar beneden gaat is een gat
            (onder de horizon hoort altijd grond, gebouw of boom); omhoog = lucht = goed
    elke straal die een object van ACHTEREN raakt (normaal wijst van de camera af) -> ACHTERKANT
            (kijkt door een muur heen of in een object)
    camera binnen een gesloten object -> CAMERA_IN_OBJECT (via toon.check_cameras)
Objecten die voor de camera onzichtbaar zijn (visible_camera False) tellen niet mee.

Uitvoer: setcheck.txt in de setmap, één regel per melding plus een samenvatting. Een set is
pas klaar als er geen enkele melding is.

Gebruik (aan het eind van een builder, vóór T.finish):
    from lib import setcheck
    setcheck.check(cams, out_dir, binnen=True)
"""
import math
import os

import bpy
from mathutils import Vector


def _rays(cam, nx, ny):
    sc = bpy.context.scene
    fr = cam.data.view_frame(scene=sc)  # 4 hoeken in camera-ruimte
    mw = cam.matrix_world
    o = mw.translation
    tr, br, bl, tl = [mw @ v for v in fr]
    for j in range(ny):
        v = (j + 0.5) / ny
        for i in range(nx):
            u = (i + 0.5) / nx
            top = tl.lerp(tr, u)
            bot = bl.lerp(br, u)
            p = top.lerp(bot, v)
            yield i, j, o, (p - o).normalized()


def _zichtbaar_maken():
    """Tijdelijk de voor de camera verborgen objecten uit de ray-cast halen."""
    weg = []
    for ob in bpy.data.objects:
        if ob.type in {"MESH", "CURVE", "FONT"} and not ob.hide_get() and (not ob.visible_camera or ob.hide_render):
            ob.hide_set(True)
            weg.append(ob)
    return weg


def _camera_in(sc, dg, cam):
    """Camera zit ín een object als (bijna) elke kant op een ACHTERKANT van hetzelfde object geraakt wordt.
    (Echte test met stralen, geen bounding box: bomen, regen of een ring om het meer geven geen vals alarm.)"""
    o = cam.matrix_world.translation
    tel = {}
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        d = Vector(d)
        hit, loc, nrm, _i, ob, _m = sc.ray_cast(dg, o, d, distance=200.0)
        if hit and ob is not None and nrm.dot(d) > 0:
            tel[ob.name] = tel.get(ob.name, 0) + 1
    for n, k in tel.items():
        if k >= 5:
            return n
    return None


def check(cameras, out_dir, binnen=False, nx=64, ny=36, horizon=-0.002, max_afstand=5000.0, naam="setcheck.txt"):
    sc = bpy.context.scene
    weg = _zichtbaar_maken()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    regels, totaal = [], 0
    for cam in cameras:
        gaten, achter = [], []
        for i, j, o, d in _rays(cam, nx, ny):
            hit, loc, nrm, _idx, ob, _m = sc.ray_cast(dg, o, d, distance=max_afstand)
            if not hit:
                # buiten: alleen een gat als de straal binnen ~1,4 km de grond had moeten raken (verder = horizon in de mist)
                if binnen or d.z < min(horizon, -max(o.z, 0.5) / 1400.0):
                    gaten.append((i, j))
                continue
            if nrm.dot(d) > 0.2 and (loc - o).length < 50:
                achter.append((i, j, ob.name if ob else "?"))
        for (i, j) in gaten[:6]:
            regels.append(f"SET_GAT  {cam.name}  pixel ~({i / nx:.2f}, {j / ny:.2f})  niets geraakt")
        if len(gaten) > 6:
            regels.append(f"SET_GAT  {cam.name}  ... en nog {len(gaten) - 6} stralen")
        namen = {}
        for (i, j, n) in achter:
            namen.setdefault(n, []).append((i, j))
        for n, lst in namen.items():
            if len(lst) >= 3:  # 1-2 stralen = rand van een dun object, geen echte fout
                i, j = lst[0]
                regels.append(f"ACHTERKANT  {cam.name}  {n}  {len(lst)} stralen, bv. ({i / nx:.2f}, {j / ny:.2f})")
        totaal += len(gaten) + sum(len(v) for v in namen.values() if len(v) >= 3)
    for cam in cameras:
        ob = _camera_in(sc, dg, cam)
        if ob:
            regels.append(f"CAMERA_IN_OBJECT  {cam.name}  {ob}")
            totaal += 1
    for ob in weg:
        ob.hide_set(False)
    os.makedirs(out_dir, exist_ok=True)
    kop = f"setcheck {'binnen' if binnen else 'buiten'}  camera's: {len(cameras)}  stralen per camera: {nx * ny}\n"
    kop += "SCHOON\n" if not regels else f"{len(regels)} meldingen\n"
    with open(os.path.join(out_dir, naam), "w") as f:
        f.write(kop + "\n".join(regels) + ("\n" if regels else ""))
    print(kop + "\n".join(regels))
    return regels
