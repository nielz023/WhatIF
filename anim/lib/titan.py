"""Gedeelde stukken voor de Titan-scènes (S17): de baan, de trein, de passagiers, het gat in de rail,
de rail als touw om de pilaar. Zelfde baan en trein als de cold open (anim/scenes/s01_cold_open.py)."""
import math
import random

from scene import *  # noqa: F401,F403

STEP = 0.75                      # baanpunten liggen 0,75 m uit elkaar
NOSE = 1.3                       # van het midden van wagen 1 tot het puntje van de neus


def pchip(keys):
    """Monotone kubische interpolatie door (t, waarde)-sleutels: geen doorschieten."""
    xs = [k[0] for k in keys]
    ys = [k[1] for k in keys]
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0] + m[0] * (x - xs[0])
        if x >= xs[-1]:
            return ys[-1]
        i = max(j for j in range(n - 1) if xs[j] <= x)
        t = (x - xs[i]) / h[i]
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
                + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f


def catmull_pts(pts, n=8):
    """Gladde lijn door punten (open Catmull-Rom), n tussenpunten per stuk."""
    P_ = [Vector(p) for p in pts]
    P_ = [P_[0] * 2 - P_[1]] + P_ + [P_[-1] * 2 - P_[-2]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P_[-2])
    return out


class Track:
    def __init__(self, S):
        self.S = S
        self.path, self.N, self.HERO_I, self.GAUGE = S.SET["path"], S.SET["N"], S.SET["HERO_I"], S.SET["GAUGE"]
        self.cars = S.SET["cars"]
        for c in self.cars:
            c.scale = (1, 1, 1)
        self.HP = self.path[self.HERO_I].copy()
        self.GROUND = self.HP.z - 0.05           # bovenkant dwarsliggers
        self.red = S.obj("Titan_rail_links").active_material

    def P(self, s):
        i = math.floor(s)
        return self.path[i % self.N].lerp(self.path[(i + 1) % self.N], s - i)

    def frame_at(self, s):
        t = (self.P(s + 1) - self.P(s - 1)).normalized()
        side = t.cross(Vector((0, 0, 1))).normalized()
        return t, side, side.cross(t).normalized()

    def ground(self, s):
        return self.P(s).z - 0.05

    def car_s(self, D, k):
        """D = afstand van de neus tot het punt van de held (m, langs de baan)."""
        return self.HERO_I - (D + NOSE) / STEP - k * 3

    def car_matrix(self, s):
        t, side, up = self.frame_at(s)
        M = Matrix((t, -side, up)).transposed().to_4x4()
        M.translation = self.P(s) + up * 0.25
        return M

    def nose(self, D):
        s = self.car_s(D, 0)
        tt, _, up = self.frame_at(s)
        return self.P(s) + tt * NOSE + up * 0.55

    def bake_train(self, D, t1):
        frames = list(range(1, F(t1) + 2))
        for k, c in enumerate(self.cars):
            bake_matrices(c, frames, [self.car_matrix(self.car_s(D((f - 1) / FPS), k)) for f in frames])

    def rail_pt(self, i, side=-1):
        t, s, u = self.frame_at(i)
        return self.path[i % self.N] + s * self.GAUGE * side

    def rail_gap(self, a, b):
        """Vervang de rechterrail door een rail met een gat van punt a t/m b; geeft het losse stuk terug
        (oorsprong op punt b, zodat het als een scharnier omhoog kan draaien)."""
        old = self.S.obj("Titan_rail_rechts")
        old.hide_render = True
        old.hide_viewport = True
        rest = [tuple(self.rail_pt(i)) for i in range(b + 1, a + self.N)]
        o = T.to_mesh(T.tube("Titan_rail_rechts_rest", rest, 0.075, self.red))
        T.outline(o, 0.03)
        pivot = self.rail_pt(b)
        piece = T.to_mesh(T.tube("Titan_rail_stuk", [tuple(self.rail_pt(i) - pivot) for i in range(a, b + 1)], 0.075, self.red))
        T.outline(piece, 0.03)
        piece.location = pivot
        return piece


# ---------------------------------------------------------------------------
# Passagiers (zoals in de cold open): 8 echte figuren in wagen 1-2, vaste kopieën in wagen 3-6
# ---------------------------------------------------------------------------
RIDERS = [
    dict(label="zusje", cast="zusje_pestkop", drop=("suikerspin",), style="zusje"),
    dict(label="rijder_1", cast="gymleraar", drop=("fluitje", "koord", "rits"), style="durf",
         outfit=dict(shirt=(0.85, 0.20, 0.15), broek=(0.15, 0.15, 0.20), haar=(0.10, 0.07, 0.05))),
    dict(label="rijder_2", cast="nieuwslezeres", drop=("microfoon", "oorbel"), style="bang",
         outfit=dict(shirt=(0.98, 0.75, 0.10), broek=(0.20, 0.30, 0.60), haar=(0.55, 0.30, 0.12))),
    dict(label="rijder_3", cast="wetenschapper", drop=("klembord", "pen", "pasje", "bril", "labjas_zakje"), style="durf",
         outfit=dict(shirt=(0.30, 0.70, 0.35), broek=(0.25, 0.22, 0.20), haar=(0.60, 0.45, 0.20))),
    dict(label="rijder_4", cast="broertje", drop=("streep", "sproet"), style="durf",
         outfit=dict(shirt=(0.20, 0.50, 0.95), broek=(0.90, 0.85, 0.75), haar=(0.15, 0.10, 0.07))),
    dict(label="rijder_5", cast="mama", drop=("oorbel",), style="bang",
         outfit=dict(shirt=(0.85, 0.35, 0.65), broek=(0.15, 0.15, 0.18), haar=(0.08, 0.06, 0.05))),
    dict(label="rijder_6", cast="papa", drop=(), style="durf",
         outfit=dict(shirt=(0.95, 0.50, 0.10), broek=(0.30, 0.25, 0.20))),
    dict(label="rijder_7", cast="oma", drop=("bril", "tas"), style="bang",
         outfit=dict(shirt=(0.55, 0.30, 0.75), broek=(0.30, 0.30, 0.35))),
    dict(label="rijder_8", cast="gymleraar", drop=("fluitje", "koord", "rits"), style="durf",
         outfit=dict(shirt=(0.10, 0.60, 0.60), broek=(0.20, 0.20, 0.25), haar=(0.70, 0.50, 0.25))),
]
SEATS = [(0.60, 0.38), (0.60, -0.38), (-0.30, 0.38), (-0.30, -0.38)]   # (x, y) in de wagen


def seat(ch, f):
    """Zitten in de wagen: heupen omlaag, voeten naar voren."""
    depth = 0.03 if ch.kid else max(0.0, ch.J["pelvis"].z - 0.36)
    A.crouch(ch, f, depth, 0.0)
    for s in "LR":
        A.foot(ch, f, s, (0.0, 0.0 if ch.kid else 0.26, 0.0))


def _arms_mix(ch, f, pa, pb_, wl, wr):
    for side, w in (("L", wl), ("R", wr)):
        a = A.POSES[pa].get(side, A.POSES[pa]["L"])
        b = A.POSES[pb_].get(side, A.POSES[pb_]["L"])
        a = A.POSES["staan"]["L"] if a == A.REST else a
        b = A.POSES["staan"]["L"] if b == A.REST else b
        A.aim_arm(ch, f, side, tuple(lerp(x, y, w) for x, y in zip(a[0], b[0])), tuple(lerp(x, y, w) for x, y in zip(a[1], b[1])))


def riders(S, cars, static_cars=(2, 3, 4, 5), copies=True, calm=False):
    """Laad de passagiers. Geeft de 8 echte figuren terug (riders[0] = het zusje, voorin rechts)."""
    rs = []
    for d in RIDERS:
        ch = R.load(d["cast"], label=d["label"], outfit=d.get("outfit"), drop=d["drop"])
        ch.style = d["style"]
        ch.kid = ch.J["pelvis"].z < 0.45
        ch.energy = 1.2
        ch.last = None
        rs.append(ch)
    if copies:
        for ch in rs:
            seat(ch, 1)
            if calm:                             # na de stop: geschrokken, stil
                A.pose(ch, 1, "zitten_beugel", extra={"spine": (6, 0, 0), "head": (14, 12, 0)})
                A.expr(ch, 1, "verdrietig", ogen_knijp=0.3)
                A.key_prop(ch.rig, "mond_open", 0.1, 1)
            else:
                A.pose(ch, 1, "armen_omhoog", extra={"spine": (-8, 0, 0), "head": (-10, 0, 0)})
                A.expr(ch, 1, "schreeuw")
                A.key_prop(ch.rig, "mond_open", 0.9, 1)
            seat(ch, 2)
            A.pose(ch, 2, "zitten_beugel", extra={"spine": (-4, 0, 0), "head": (6, 0, 0)})
            A.expr(ch, 2, "bang", ogen_knijp=0.5)
            A.key_prop(ch.rig, "mond_open", 0.6, 2)
        meshes = []
        for f in (1, 2):
            S.sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            for ch in rs[1:]:
                me = bpy.data.meshes.new_from_object(ch.body.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
                me.name = f"{ch.name}_vast_{f}"
                meshes.append((me, ch.rig.matrix_world.inverted() @ ch.body.matrix_world, ch.kid))
        coll = T.collection("Passagiers (vast)")
        n = 0
        for k in static_cars:
            for (x, y) in SEATS:
                me, rel, kid = meshes[(n * 5) % len(meshes)]
                o = bpy.data.objects.new(f"Passagier_{k + 1}_{n % 4 + 1}", me)
                coll.objects.link(o)
                o.parent = cars[k]
                o.matrix_parent_inverse = Matrix.Identity(4)
                o.matrix_basis = Matrix.Translation((x, y, 0.30 if kid else 0.12)) @ Matrix.Rotation(math.radians(90), 4, "Z") @ rel
                n += 1
    last = rs.pop()
    lc = last.rig.users_collection[0]
    for o in list(lc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(lc)
    for ch in rs:
        ch.rig.animation_data_clear()
        for pb in ch.rig.pose.bones:
            pb.location, pb.rotation_quaternion = (0, 0, 0), (1, 0, 0, 0)
            pb.rotation_euler, pb.scale = (0, 0, 0), (1, 1, 1)
        for p in R.FACE_PROPS:
            ch.rig[p] = 0.0
    for n, ch in enumerate(rs):
        k, (x, y) = n // 4, SEATS[n % 4]
        ch.rig.parent = cars[k]
        ch.rig.matrix_parent_inverse = Matrix.Identity(4)
        ch.rig.location = (x, y, 0.30 if ch.kid else 0.12)
        ch.rig.rotation_euler = (0, 0, math.radians(90))
    return rs


def scream(rs, t0, t1, t_bang=None, rate=None):
    """Passagiers: blij vóór de knal, daarna gillen (armen omhoog of de beugel vastklemmen)."""
    rate = rate or (lambda t: 1.0)
    for n, ch in enumerate(rs):
        rnd = random.Random(n * 17 + 3)
        ph = rnd.uniform(0, 6.28)
        f0 = F(t0)
        seat(ch, f0)
        A.pose(ch, f0, "zitten_beugel" if ch.style != "durf" else "juichen", amount=1.0 if ch.style != "durf" else 0.55)
        A.expr(ch, f0, "lach" if ch.style != "zusje" else "blij", look=(0.0, -0.3))
        A.key_prop(ch.rig, "mond_open", 0.3, f0)
        A.blinks(ch, f0, F(t1), seed=n)
        start = t0
        if t_bang is not None:
            for t, e, mo in ((t_bang, "blij", 0.3), (t_bang + 0.15, "geschrokken", 0.6), (t_bang + 0.9, "bang", 0.35)):
                A.expr(ch, F(t), e, look=(0.0, -0.2) if e != "geschrokken" else (rnd.uniform(-0.5, 0.5), 0.1))
                A.key_prop(ch.rig, "mond_open", mo, F(t))
            A.pose(ch, F(t_bang), "zitten_beugel")
            A.pose(ch, F(t_bang + 0.2), "zitten_beugel", extra={"head": (-12, rnd.uniform(-20, 20), 0), "spine": (-6, 0, 0)})
            seat(ch, F(t_bang + 1.0))
            start = t_bang + 1.2
        A.expr(ch, F(start), "schreeuw" if ch.style != "zusje" else "bang", ogen_knijp=0.6 if ch.style == "zusje" else 0.0)
        f = F(start)
        u = 0.0
        while f <= F(t1):
            t = (f - 1) / FPS
            u += 3 * rate(t) / FPS
            body = {"spine": (0, 0, 0), "head": (6 * noise.noise(Vector((u * 2.0, n, 0.5))), 14 * noise.noise(Vector((u * 1.5, n, 1.5))),
                                               4 * noise.noise(Vector((u, n, 2.5))))}
            if ch.style == "durf":
                A.pose(ch, f, "armen_omhoog", extra=body, arms=False)
                _arms_mix(ch, f, "armen_omhoog", "juichen", 0.5 + 0.5 * math.sin(u * 7.0 + ph), 0.5 + 0.5 * math.sin(u * 7.0 + ph + 1.9))
            elif ch.style == "bang":
                A.pose(ch, f, "zitten_beugel", extra=body, arms=False)
                w = 0.5 + 0.5 * math.sin(u * 5.0 + ph)
                _arms_mix(ch, f, "zitten_beugel", "handen_hoofd", w * 0.6, w * 0.6)
            else:
                A.pose(ch, f, "zitten_beugel", extra=body)
            A.key_prop(ch.rig, "mond_open", 0.75 + 0.25 * noise.noise(Vector((u * 6.0, n, 3.0))), f)
            f += 3


def cam_hide(obj, t0, t1):
    """Object onzichtbaar voor de camera van t0 tot t1 (bijvoorbeeld de grond in een doorsnede)."""
    for f, v in ((1, True), (F(t0), False), (F(t1), True)):
        obj.visible_camera = v
        obj.keyframe_insert("visible_camera", frame=f)
    for fc in A._fcurves(obj):
        if fc.data_path == "visible_camera":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


# ---------------------------------------------------------------------------
# De rail als touw: twee slagen om de pilaar onder zijn plek, het eind in zijn handen
# ---------------------------------------------------------------------------
COIL_TOP, COIL_BOT = 1.75, 1.25
X_PUSH = 1.73 + 0.35             # hoe ver de neus hem achteruit duwt (eindstand: neus op HP.x - 1.73)


def coil_points(TR):
    pil = TR.HP
    r = 0.38 + pil.z * 0.008 + 0.08
    pts = []
    for k in range(65):
        a = -math.pi / 2 - 2 * 2 * math.pi * k / 64
        pts.append(Vector((pil.x + r * math.cos(a), pil.y + r * math.sin(a), lerp(COIL_TOP, COIL_BOT, k / 64))))
    tail = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.35 + Vector((0, 0, -0.05))
    return pts + [tail]


def build_coil(TR, name="Rail_om_pilaar"):
    return T.tube(name, [tuple(p) for p in coil_points(TR)], 0.075, TR.red)


def rope_hands(TR, x):
    """(rechterhand, linkerhand) op het touw als hij op x staat (gezicht naar +x)."""
    HP, G = TR.HP, TR.GROUND
    return Vector((x + 0.40, HP.y - 0.14, G + 0.62)), Vector((x + 0.34, HP.y + 0.02, G + 0.70))


def build_rope(TR, name, x, hands=None):
    HP, G = TR.HP, TR.GROUND
    rh, lh = hands or rope_hands(TR, x)
    entry = coil_points(TR)[0]
    pts = [lh + Vector((-0.14, 0.08, 0.06)), lh, rh, Vector((rh.x + 0.35, HP.y - 0.85, G + 0.3)),
           Vector((min(rh.x + 1.2, HP.x - 0.05), HP.y - 0.93, G - 0.25)), Vector((HP.x, HP.y - 0.93, G - 0.85)), entry]
    return T.tube(name, [tuple(p) for p in catmull_pts(pts, 6)], 0.075, TR.red)
