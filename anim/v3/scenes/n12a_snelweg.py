"""N12a · Dag 6: de tocht door de stad (script scène 12a-12c), de lege snelweg vol verlaten auto's.
12a WIDE track naast de fietsen: ze slalommen tussen de auto's met open deuren door, de vriend staand op de pedalen.
12b WIDE: het open dierentuinhek, half uit zijn scharnieren, CITY ZOO. De fietsen flitsen voor het beeld langs.
    VO: "Without zookeepers, somebody simply... opened the gates."
12c MEDIUM: een zebra draaft tussen de auto's door vlak voor de fietsen, schrikt en maakt een zijsprong.
    De jongens remmen hard, de vriend zet zijn voet aan de grond, de jongen klapt bijna op zijn stuur.
    BESTE VRIEND: "Was that... a zebra?"

    blender -b -P anim/v3/scenes/n12a_snelweg.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n12a", "snelweg", "snelweg", exposure=0.1)
sh = S.cuts([3.5, 3.4, 4.6])
END = sh[-1][1]
t_b, t_c = sh[1][0], sh[2][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- obstakels op de noordelijke rijbaan (auto's met open deuren, koffers)
bpy.context.view_layer.update()
OBST = []
for o in bpy.data.objects:
    if (o.name.startswith("Auto_") and o.parent is None) or o.name.startswith("Koffer_"):
        pts = []
        for c in [o] + list(o.children_recursive):
            if c.type == "MESH":
                pts += [c.matrix_world @ V(cc) for cc in c.bound_box]
        if pts:
            OBST.append((min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts),
                         max(p.z for p in pts)))


def clear(x, y):
    """Afstand van (x, y) tot het dichtstbijzijnde obstakel (rechthoek)."""
    d = 99.0
    for x0, y0, x1, y1, _ in OBST:
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        d = min(d, math.hypot(dx, dy))
    return d


def plan(xa, xb, ya, yb, step=1.0, need=1.15):
    """Kortste slalom van (xa, ya) naar (xb, yb) over de rijbaan (y 3..12) die overal 'need' m van de auto's blijft."""
    YS = [3.0 + 0.2 * k for k in range(47)]
    XS = [xa + step * i for i in range(int((xb - xa) / step) + 1)]
    INF = 1e9
    cost = {y: (abs(y - ya) * 50 if clear(xa, y) >= need else INF) for y in YS}
    back = []
    for x in XS[1:]:
        nc, bk = {}, {}
        for y in YS:
            c_here = clear(x, y)
            if c_here < need:
                nc[y], bk[y] = INF, None
                continue
            best, arg = INF, None
            for yp in YS:
                if abs(y - yp) > 0.85 * step or cost[yp] >= INF:
                    continue
                c = cost[yp] + (y - yp) ** 2 * 6 + 0.6 / c_here
                if c < best:
                    best, arg = c, yp
            nc[y], bk[y] = best, arg
        back.append(bk)
        cost = nc
    y = min(YS, key=lambda yy: cost[yy] + abs(yy - yb) * 3)
    if cost[y] >= INF:
        raise RuntimeError("geen vrije slalom gevonden")
    path = [y]
    for bk in reversed(back):
        y = bk[y]
        path.append(y)
    path.reverse()
    return [V(x, yy, 0) for x, yy in zip(XS, path)]


def smooth(pts, n=2):
    for _ in range(n):
        pts = [pts[0]] + [(pts[i - 1] + pts[i] * 2 + pts[i + 1]) / 4 for i in range(1, len(pts) - 1)] + [pts[-1]]
    return pts


# de zebra steekt over waar een vrije strook dwars over de rijbaan ligt (ergens tussen x 52 en 75)
X_Z = None
for xi in range(52, 76):
    if all(clear(xi, 3.0 + 0.25 * k) >= 1.0 for k in range(37)):
        X_Z = float(xi)
        break
if X_Z is None:
    X_Z = max(range(52, 76), key=lambda xi: min(clear(xi, 3.0 + 0.25 * k) for k in range(37)))
    X_Z = float(X_Z)
print("ZEBRA OVERSTEEK OP x =", X_Z)

V_RIDE = 6.4
T_BRAKE = t_c + 0.9                                       # hier knijpt hij in de remmen
X_BRAKE = X_Z - 4.2
route = smooth(plan(X_BRAKE - V_RIDE * T_BRAKE * 0.93, X_BRAKE, 7.5, 7.5))
L = sum((route[i + 1] - route[i]).length for i in range(len(route) - 1))
print("ROUTE", round(route[0].x, 1), "->", round(route[-1].x, 1), "lengte", round(L, 1), "snelheid", round(L / T_BRAKE, 2))
STOP_H = route[-1] + V(1.7, 0.0, 0)
LAST = route[-1]

# ---------------------------------------------------------------- de jongen en de vriend op hun fietsen
held = S.actor("hoofdpersonage_kind", tuple(route[0]), 90)
_, crank_h = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen", jerrycan=False)
vr = S.actor("beste_vriend", tuple(route[0] + V(-2.5, 0, 0)), 90)
_, crank_v = bike(S, vr, color=(0.85, 0.12, 0.10), name="Fiets_vriend")

# de jongen: slalom, dan hard remmen (twee korte stukjes met afnemende snelheid) en stilstaan
ride_path(S, held, crank_h, 0.0, T_BRAKE, route, cadence=1.9, lean=18, sway=3)
ride_path(S, held, crank_h, T_BRAKE, T_BRAKE + 0.35, [LAST, LAST + V(1.3, 0, 0)], cadence=0.4, lean=34)
ride_path(S, held, crank_h, T_BRAKE + 0.35, T_BRAKE + 0.6, [LAST + V(1.3, 0, 0), STOP_H], cadence=0.05, lean=40)
ride_path(S, held, crank_h, T_BRAKE + 0.6, END, [STOP_H, STOP_H + V(0.01, 0, 0)], cadence=0.02, lean=6)
# bijna over zijn stuur: zwaar voorover, dan terug
for t, dz, ln in ((T_BRAKE + 0.3, -0.05, 55), (T_BRAKE + 0.55, -0.06, 62), (T_BRAKE + 0.9, 0.0, 20), (T_BRAKE + 1.3, 0.04, 6)):
    A.crouch(held, F(t), dz, ln)
for f in range(F(T_BRAKE + 0.7), F(END), 2):
    A.foot(held, f, "R", (-0.3, 0.05, -0.02))

# de vriend: zelfde spoor, een halve seconde erachter, staand op de pedalen; remt naast hem met zijn voet aan de grond
DELAY = 0.45
vroute = [p + V(0, 0, 0) for p in route]
T_BRAKE_V = T_BRAKE + DELAY
ride_path(S, vr, crank_v, 0.0, DELAY, [route[0] + V(-2.9, 0, 0), route[0]], cadence=2.2, lean=22, stand=True, sway=6)
ride_path(S, vr, crank_v, DELAY, T_BRAKE_V, vroute, cadence=2.2, lean=22, stand=True, sway=6)
STOP_V = STOP_H + V(-0.9, -1.3 if clear(STOP_H.x - 0.9, STOP_H.y - 1.3) > 0.8 else 1.3, 0)
ride_path(S, vr, crank_v, T_BRAKE_V, T_BRAKE_V + 0.5, [LAST, STOP_V], cadence=0.3, lean=30)
ride_path(S, vr, crank_v, T_BRAKE_V + 0.5, END, [STOP_V, STOP_V + V(0.01, 0, 0)], cadence=0.02, lean=5)
for f in range(F(T_BRAKE_V + 0.35), F(END), 2):
    A.foot(vr, f, "L", (0.32, 0.05, -0.02))
S.face(held, 0.0, "vastberaden", 0.7, look=(0.0, 0.1))
S.face(held, t_b + 1.0, "verbaasd", 0.5, look=(0.6, 0.2))           # kijkt naar het open hek
S.face(held, t_c + 0.5, "geschrokken", 1.0, look=(0.0, 0.0))
S.face(held, t_c + 1.8, "verbaasd", 0.8, look=(0.4, 0.0))
S.face(vr, 0.0, "grijns", 0.6, look=(0.0, 0.1))
S.face(vr, t_c + 0.6, "geschrokken", 1.0, look=(0.0, 0.0))
S.face(vr, t_c + 1.9, "verbaasd", 0.9, look=(0.5, 0.0))
A.blink_at(vr, F(t_c + 1.7))
S.say("N12-02", who=vr, at=t_c + 2.0)

# ---------------------------------------------------------------- de zebra
zb = animal(S, "zebra", (X_Z, 13.0, 0), 0, scale=1.35)
T_Z0 = t_c + 0.1
T_SHY = t_c + 1.05
ZMID = V(X_Z, STOP_H.y + 1.6, 0)
animal_path(zb, 0.0, T_Z0, [V(X_Z + 0.5, 12.6, 0), V(X_Z, 12.5, 0)], action=None)
animal_path(zb, T_Z0, T_SHY, [V(X_Z, 12.5, 0), ZMID], action="zebra_draf", speed=1.2)
animal_act(zb, T_SHY, T_SHY + 0.75, "zebra_schrik")
# zijsprong: weg van de fietsen (+x) en verder over de rijbaan
animal_path(zb, T_SHY + 0.25, T_SHY + 0.75, [ZMID, ZMID + V(0.6, -1.5, 0)])
animal_path(zb, T_SHY + 0.75, END, [ZMID + V(0.6, -1.5, 0), V(X_Z + 0.4, 2.8, 0), V(X_Z - 2.0, 2.6, 0)], action="zebra_draf", speed=1.3)
print("ZEBRA", ZMID, "STOP", STOP_H, STOP_V)

# ---------------------------------------------------------------- camera's
# 12a WIDE track naast de fietsen, boven de auto's uit, iets voor ze
S.cam(0.0, None, fn=S.follow(held, (-4.0, -5.0, 3.0), lens=24, look_offset=(9.0, 3.5, -2.2)), shake=S.shake(0.2))
# 12b WIDE: vanaf de middenberm het open zoohek; de fietsen flitsen erdoor
S.cam(t_b, ((35.5, 5.5, 1.9), (40.5, 24.0, 2.4), 28), ((35.9, 6.2, 1.9), (40.5, 24.0, 2.4), 30))


def cam_ok(p):
    return clear(p.x, p.y) > 0.6 or p.z > 2.2


# 12c MEDIUM: laag, voor de fietsen, de zebra steekt tussen camera en fietsen over
C3 = V(X_Z + 9.0, STOP_H.y + 0.3, 1.3)
for dy in (0.0, -1.0, 1.0, -2.0, 2.0, 3.0):
    if cam_ok(C3 + V(0, dy, 0)):
        C3 = C3 + V(0, dy, 0)
        break
S.cam(t_c, (C3, STOP_H + V(0.4, -0.3, 1.0), 26), (C3 + V(-0.8, 0.05, 0), STOP_H + V(0.4, -0.3, 1.0), 29), handheld=0.3)

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 6", 0, t0=0.0)
S.music("m_reis", 0.0, END, vol=0.22, fade_in=0.3, fade_out=0.3)
S.sfx("sfx_fiets_snel", 0.0, 0.2, loop_to=T_BRAKE)
S.sfx("sfx_wind_hoog", 0.0, 0.05, loop_to=END)
S.sfx("sfx_fiets_remmen", T_BRAKE - 0.05, 0.4)
S.sfx("sfx_zebra_hoeven", T_Z0, 0.3)
S.say("N12-01", at=t_b + 0.1)
S.finish(length=END, tail=0.0)
