"""S01 · Cold open (0:00-0:55): de remmen van THE TITAN falen en jij staat op de baan.

Bouwt de pretpark-set (sets/build_pretpark.py), laadt het hoofdpersonage, de beste
vriend en 24 passagiers, animeert de trein, het acteren en twaalf camerashots, en
slaat alles op als out/s01/s01_cold_open.blend.

Gebruik (Blender 5.2):
    blender -b -P anim/scenes/s01_cold_open.py -- [--render] [--pct 100] [--samples 16]
    blender -b -P anim/scenes/s01_cold_open.py -- --stills 3,12.5,30   (losse testbeelden)

Met --render komen de beelden in out/s01/frames/. Daarna maakt anim/edit/montage.py
er een MP4 met stem, geluid, muziek en HUD van.

Tijden staan overal in seconden (24 fps); F(t) zet ze om naar frames.
"""
import argparse
import math
import os
import random
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sets"))
sys.path.insert(0, os.path.join(REPO, "anim", "lib"))
import bpy  # noqa: E402
from mathutils import Vector, Matrix, Quaternion, noise  # noqa: E402
from lib import toon as T  # noqa: E402
import rig as R  # noqa: E402
import acting as A  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--render", action="store_true", help="alle frames renderen")
ap.add_argument("--pct", type=int, default=100, help="resolutie in procent van 1920x1080")
ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--out", default=os.path.join(REPO, "out", "s01"))
ap.add_argument("--stills", default=None, help="komma-lijst van tijden in seconden voor testbeelden")
args = ap.parse_args(argv)

FPS = 24
END_T = 51.6          # smash cut naar zwart; daarna alleen montage ("16 DAYS EARLIER")


def F(t):
    return int(round(t * FPS)) + 1


def smooth(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, w):
    return a + (b - a) * w


def vlerp(a, b, w):
    return Vector(a).lerp(Vector(b), w)


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
            return ys[-1] + m[-1] * (x - xs[-1])
        i = max(j for j in range(n - 1) if xs[j] <= x)
        t = (x - xs[i]) / h[i]
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
                + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f


# ---------------------------------------------------------------------------
# Set bouwen (zonsondergang) en opruimen
# ---------------------------------------------------------------------------
os.environ["SET_RENDER"] = "0"
os.environ["SET_SAMPLES"] = str(args.samples)
_argv = sys.argv
sys.argv = [_argv[0], "--", "zonsondergang", os.path.join(args.out, "set")]
SET = runpy.run_path(os.path.join(REPO, "sets", "build_pretpark.py"))
sys.argv = _argv

sc = bpy.context.scene
sc.name = "S01_cold_open"
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, F(END_T)
old = bpy.data.collections.get("Hoofdpersonage (schaal)")
if old:
    for o in list(old.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(old)
for o in [o for o in sc.objects if o.type == "CAMERA"]:
    bpy.data.objects.remove(o, do_unlink=True)

path, N, HERO_I, GAUGE = SET["path"], SET["N"], SET["HERO_I"], SET["GAUGE"]
cars = SET["cars"]
STEP = 0.75                      # baanpunten liggen 0,75 m uit elkaar
HP = path[HERO_I].copy()         # midden van de baan waar hij staat
GROUND = HP.z - 0.05             # bovenkant dwarsliggers
RAIL_TOP = HP.z + 0.075


def P(s):
    i = math.floor(s)
    return path[i % N].lerp(path[(i + 1) % N], s - i)


def frame_at(s):
    t = (P(s + 1) - P(s - 1)).normalized()
    side = t.cross(Vector((0, 0, 1))).normalized()
    return t, side, side.cross(t).normalized()


def H(x, y, z):
    """Punt rond de held: x = naar de trein toe (+x wereld), y = zijn linkerkant, z boven de dwarsliggers."""
    return Vector((HP.x + x, HP.y + y, GROUND + z))


# ---------------------------------------------------------------------------
# Tijd: slow motion. r(t) = hoe snel de wereld loopt; tau(t) = verstreken 'echte' tijd.
# ---------------------------------------------------------------------------
def rate(t):
    return 1.0 - 0.9 * smooth(8.6, 10.8, t) + 0.9 * smooth(50.7, 51.3, t)


TAU = [0.0]
for f in range(1, F(END_T) + 30):
    TAU.append(TAU[-1] + rate((f - 1) / FPS) / FPS)


def tau(t):
    return TAU[max(0, min(len(TAU) - 1, int(t * FPS)))]


# Afstand van de neus van de trein tot de held (m). De simulatie (24,2-37,6) is een
# 'wat als': daar rijdt de trein door en neemt hem mee.
D_REAL1 = pchip([(0, 66), (2.0, 63.2), (4.2, 58), (7.6, 40), (8.6, 22), (11.4, 18), (24.2, 12)])
D_SIM = pchip([(24.2, 12), (30.0, 0.0), (34.9, -6.5), (37.6, -13)])
D_REAL2 = pchip([(37.6, 11.5), (48.8, 9.0), (50.6, 7.6), (51.1, 5.2), (51.65, 0.4)])
SIM = (24.2, 37.6)


def D(t):
    if t < SIM[0]:
        return D_REAL1(t)
    if t < SIM[1]:
        return D_SIM(t)
    return D_REAL2(t)


NOSE = 1.3      # van het midden van wagen 1 tot het puntje van de neus


def car_s(t, k):
    return HERO_I - (D(t) + NOSE) / STEP - k * 3


def car_matrix(s):
    t, side, up = frame_at(s)
    M = Matrix((t, -side, up)).transposed().to_4x4()
    M.translation = P(s) + up * 0.25
    return M


# ---------------------------------------------------------------------------
# Keyframes in bulk (per frame), veel sneller dan keyframe_insert in een lus
# ---------------------------------------------------------------------------
def bake(owner, prop, frames, rows, interp="LINEAR"):
    n = len(rows[0])
    for i in range(n):
        owner.keyframe_insert(prop, index=i if n > 1 else -1, frame=frames[0])
    target = owner.id_data
    full = owner.path_from_id(prop) if owner != target else prop
    fcs = {fc.array_index: fc for fc in A._fcurves(target) if fc.data_path == full}
    for i in range(n):
        fc = fcs[i]
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(frames))
        co = []
        for f, r in zip(frames, rows):
            co += [f, r[i]]
        fc.keyframe_points.foreach_set("co", co)
        for kp in fc.keyframe_points:
            kp.interpolation = interp
        fc.update()


def bake_matrices(obj, frames, mats):
    obj.rotation_mode = "QUATERNION"
    locs, quats = [], []
    prev = None
    for M in mats:
        loc, q, _ = M.decompose()
        if prev is not None and prev.dot(q) < 0:
            q.negate()
        prev = q
        locs.append(tuple(loc))
        quats.append(tuple(q))
    bake(obj, "location", frames, locs)
    bake(obj, "rotation_quaternion", frames, quats)


ALL_FRAMES = list(range(1, F(END_T) + 2))

# ---------------------------------------------------------------------------
# Trein
# ---------------------------------------------------------------------------
for k, c in enumerate(cars):
    c.scale = (1, 1, 1)      # de set zette de wagens met een gespiegelde matrix neer (schaal -1)
    bake_matrices(c, ALL_FRAMES, [car_matrix(car_s((f - 1) / FPS, k)) for f in ALL_FRAMES])


def nose_pos(t):
    s = car_s(t, 0)
    tt, _, up = frame_at(s)
    return P(s) + tt * NOSE + up * 0.55


# ---------------------------------------------------------------------------
# Passagiers: 8 ontwerpen (castfiguren met andere kleren). Wagen 1 en 2 zijn echte,
# geanimeerde figuren; wagen 3 t/m 6 krijgen vastgezette kopieën (twee houdingen).
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

riders = []
for d in RIDERS:
    ch = R.load(d["cast"], label=d["label"], outfit=d.get("outfit"), drop=d["drop"])
    ch.style = d["style"]
    ch.kid = ch.J["pelvis"].z < 0.45
    riders.append(ch)


def sit(ch, f):
    """Zitten in de wagen: heupen omlaag, voeten naar voren."""
    depth = 0.03 if ch.kid else max(0.0, ch.J["pelvis"].z - 0.36)
    A.crouch(ch, f, depth, 0.0)
    for s in "LR":
        A.foot(ch, f, s, (0.0, 0.0 if ch.kid else 0.26, 0.0))


def arms_mix(ch, f, pa, pb_, wl, wr):
    """Armen ergens tussen houding pa en pb_ (0..1 per kant), voor zwaaien en flapperen."""
    for side, w in (("L", wl), ("R", wr)):
        a = A.POSES[pa].get(side, A.POSES[pa]["L"])
        b = A.POSES[pb_].get(side, A.POSES[pb_]["L"])
        a = A.POSES["staan"]["L"] if a == A.REST else a
        b = A.POSES["staan"]["L"] if b == A.REST else b
        up = tuple(lerp(x, y, w) for x, y in zip(a[0], b[0]))
        fo = tuple(lerp(x, y, w) for x, y in zip(a[1], b[1]))
        A.aim_arm(ch, f, side, up, fo)


# Vastgezette kopieën voor wagen 3-6
for ch in riders:
    sit(ch, 1)
    A.pose(ch, 1, "armen_omhoog", extra={"spine": (-8, 0, 0), "head": (-10, 0, 0)})
    A.expr(ch, 1, "schreeuw")
    A.key_prop(ch.rig, "mond_open", 0.9, 1)
    sit(ch, 2)
    A.pose(ch, 2, "zitten_beugel", extra={"spine": (-4, 0, 0), "head": (6, 0, 0)})
    A.expr(ch, 2, "bang", ogen_knijp=0.5)
    A.key_prop(ch.rig, "mond_open", 0.6, 2)
static_meshes = []
for f in (1, 2):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    for ch in riders[1:]:
        me = bpy.data.meshes.new_from_object(ch.body.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        me.name = f"{ch.name}_vast_{f}"
        static_meshes.append((me, ch.rig.matrix_world.inverted() @ ch.body.matrix_world, ch.kid))
coll_static = T.collection("Passagiers (vast)")
seat_n = 0
for k in range(2, 6):
    for (x, y) in SEATS:
        me, rel, kid = static_meshes[(seat_n * 5) % len(static_meshes)]
        o = bpy.data.objects.new(f"Passagier_{k + 1}_{seat_n % 4 + 1}", me)
        coll_static.objects.link(o)
        o.parent = cars[k]
        o.matrix_parent_inverse = Matrix.Identity(4)
        base = Matrix.Translation((x, y, 0.30 if kid else 0.12)) @ Matrix.Rotation(math.radians(90), 4, "Z")
        o.matrix_basis = base @ rel
        seat_n += 1

# de laatste ontwerp-figuur was alleen voor de kopieën
last = riders.pop()
last_coll = last.rig.users_collection[0]
for o in list(last_coll.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(last_coll)
for ch in riders:
    ch.rig.animation_data_clear()
    for pb in ch.rig.pose.bones:
        pb.location, pb.rotation_quaternion = (0, 0, 0), (1, 0, 0, 0)
        pb.rotation_euler, pb.scale = (0, 0, 0), (1, 1, 1)
    for p in R.FACE_PROPS:
        ch.rig[p] = 0.0

# zusje voorin rechts, de rest verdeeld over wagen 1 en 2
for n, ch in enumerate(riders):
    k, (x, y) = n // 4, SEATS[n % 4]
    ch.rig.parent = cars[k]
    ch.rig.matrix_parent_inverse = Matrix.Identity(4)
    ch.rig.location = (x, y, 0.30 if ch.kid else 0.12)
    ch.rig.rotation_euler = (0, 0, math.radians(90))


def rider_anim(ch, n):
    rnd = random.Random(n * 17 + 3)
    ph = rnd.uniform(0, 6.28)
    # voor het remmen: opgewonden op de top
    f0 = 1
    sit(ch, f0)
    A.pose(ch, f0, "zitten_beugel" if ch.style != "durf" else "juichen", amount=1.0 if ch.style != "durf" else 0.55)
    A.expr(ch, f0, "lach" if ch.style != "zusje" else "blij", look=(0.0, -0.3))
    A.key_prop(ch.rig, "mond_open", 0.3, f0)
    A.blinks(ch, 1, F(4.0), seed=n)
    # de knal (2,0 s)
    for f, e, mo in ((F(2.0), "blij", 0.3), (F(2.15), "geschrokken", 0.6), (F(2.9), "bang", 0.35)):
        A.expr(ch, f, e, look=(0.0, -0.2) if e != "geschrokken" else (rnd.uniform(-0.5, 0.5), 0.1))
        A.key_prop(ch.rig, "mond_open", mo, f)
    A.pose(ch, F(2.0), "zitten_beugel", amount=1.0)
    A.pose(ch, F(2.2), "zitten_beugel", extra={"head": (-12, rnd.uniform(-20, 20), 0), "spine": (-6, 0, 0)})
    A.pose(ch, F(3.0), "zitten_beugel", extra={"head": (8, 0, 0), "spine": (4, 0, 0)})
    sit(ch, F(3.0))
    # de afdaling en daarna: gillen (in slow motion vanaf 8,6 s)
    f = F(4.0)
    A.expr(ch, f, "schreeuw" if ch.style != "zusje" else "bang", ogen_knijp=0.6 if ch.style == "zusje" else 0.0)
    while f <= F(END_T) + 1:
        t = (f - 1) / FPS
        u = tau(t)
        g = smooth(4.2, 5.0, t) * (1 - smooth(8.4, 9.0, t))    # g-kracht in de afdaling
        hx = -10 * g + 6 * noise.noise(Vector((u * 2.0, n, 0.5)))
        hy = 14 * noise.noise(Vector((u * 1.5, n, 1.5)))
        body = {"spine": (-10 * g, 0, 0), "head": (hx, hy, 4 * noise.noise(Vector((u, n, 2.5))))}
        if ch.style == "durf":
            A.pose(ch, f, "armen_omhoog", extra=body, arms=False)
            wl = 0.5 + 0.5 * math.sin(u * 7.0 + ph)
            wr = 0.5 + 0.5 * math.sin(u * 7.0 + ph + 1.9)
            arms_mix(ch, f, "armen_omhoog", "juichen", wl, wr)
        elif ch.style == "bang":
            A.pose(ch, f, "zitten_beugel", extra=body, arms=False)
            w = 0.5 + 0.5 * math.sin(u * 5.0 + ph)
            arms_mix(ch, f, "zitten_beugel", "handen_hoofd", w * 0.6, w * 0.6)
        else:
            A.pose(ch, f, "zitten_beugel", extra=body)
        A.key_prop(ch.rig, "mond_open", 0.75 + 0.25 * noise.noise(Vector((u * 6.0, n, 3.0))), f)
        f += 3


for n, ch in enumerate(riders):
    rider_anim(ch, n)

# ---------------------------------------------------------------------------
# Het hoofdpersonage
# ---------------------------------------------------------------------------
hero = R.load("hoofdpersonage", loc=(HP.x, HP.y, GROUND), rot_z=90)


def before(t):
    """Het frame vlak voor een cut (om de oude stand vast te houden)."""
    return (F(t) - 2) / FPS


REACH = 0.55    # zijn handen raken de neus als die nog 0,55 m van hem af is


def hero_root(t):
    """Plaats en kanteling van de held. In de simulatie duwt de trein hem achteruit."""
    if not (SIM[0] <= t < SIM[1]):
        return Vector((HP.x, HP.y, GROUND)), 0.0
    s = HERO_I + max(0.0, REACH - D_SIM(t)) / STEP
    p = P(s)
    lift = smooth(34.9, 35.5, t)
    loc = Vector((p.x, p.y, GROUND + lift * 0.55))
    return loc, 35 * lift     # tegen de neus geplakt en meegesleurd


root_rows, rot_rows = [], []
for f in ALL_FRAMES:
    loc, tilt = hero_root((f - 1) / FPS)
    root_rows.append(tuple(loc))
    rot_rows.append((math.radians(tilt), 0.0, math.radians(90)))
bake(hero.rig, "location", ALL_FRAMES, root_rows)
bake(hero.rig, "rotation_euler", ALL_FRAMES, rot_rows)

RAIL_R = H(0.30, -GAUGE, 0.13)      # pols op de rechterrail (zijn rechterkant = -y)
RAIL_L = H(0.30, GAUGE, 0.13)


def hero_beat(t, pose="staan", amount=1.0, crouch=(0.0, 0.0), feet=((0, 0, 0), (0, 0, 0)), face="neutraal",
              face_amt=1.0, look=None, mouth=0.0, body=None, hands=0.0, sink=0.0, arms=None, **face_extra):
    """Eén moment in het acteren van de held: alles wordt gekeyd, zodat sprongen bij cuts kloppen."""
    f = F(t)
    A.pose(hero, f, pose, amount=amount, extra=body)
    if arms:
        arms(f)
    A.crouch(hero, f, *crouch)
    A.foot(hero, f, "L", feet[0])
    A.foot(hero, f, "R", feet[1])
    A.expr(hero, f, face, amount=face_amt, look=look, **face_extra)
    A.key_prop(hero.rig, "mond_open", mouth, f)
    A.hand_ik(hero, f, "L", hands, RAIL_L - Vector((0, 0, sink)), rot=(0, 0, 0))
    A.hand_ik(hero, f, "R", hands, RAIL_R - Vector((0, 0, sink)), rot=(0, 0, 0))


def kraak(f):
    A.aim_arm(hero, f, "L", (0.30, 0.55, -0.70), (-0.80, 0.55, 0.20))
    A.aim_arm(hero, f, "R", (0.30, 0.55, -0.70), (-0.80, 0.55, 0.20))


GRAB = dict(pose="schrap", crouch=(0.30, 15.0), feet=((0.22, 0.0, 0), (-0.22, 0.0, 0)),
            body={"spine": (10, 0, 0), "chest": (8, 0, 0), "head": (-28, 0, 0)}, hands=1.0)
TURN_R = {"head": (0, -40, 0), "neck": (0, -12, 0)}

# 0-11,4: staat al op de baan (alleen klein in het totaalshot)
hero_beat(0.0, "vuisten", face="nerveus", look=(0, 0.3))
# S5 onthulling: zenuwachtig, slikt, wordt vastberaden
hero_beat(11.4, "vuisten", face="nerveus", look=(0.0, 0.35), body={"head": (-8, 0, 0)})
hero_beat(12.5, "vuisten", face="nerveus", face_amt=1.2, look=(0.1, 0.4), body={"head": (-10, 3, 0)})
hero_beat(13.1, "vuisten", face="nerveus", look=(0.0, 0.1), body={"head": (6, 0, 0), "neck": (4, 0, 0)}, mouth=0.05)
hero_beat(13.6, "vuisten", face="vastberaden", face_amt=0.6, look=(0, 0.3), body={"head": (-6, 0, 0)})
hero_beat(14.4, "vuisten", crouch=(0.06, 4.0), face="vastberaden", look=(0, 0.35), body={"head": (-9, 0, 0)})
# S6: hoort zijn vriend en kijkt om
hero_beat(15.6, "vuisten", crouch=(0.06, 4.0), face="vastberaden", look=(0, 0.35))
hero_beat(16.2, "vuisten", crouch=(0.04, 2.0), face="verbaasd", face_amt=0.4, look=(-0.6, 0), body=TURN_R)
hero_beat(17.6, "vuisten", crouch=(0.04, 2.0), face="zelfverzekerd", face_amt=0.5, look=(-0.6, 0), body=TURN_R)
# S7: knokkels kraken, grijns naar de camera, schouders op bij "Easy"
hero_beat(18.4, "vuisten", face="zelfverzekerd", face_amt=0.6, look=(-0.3, 0.1), body={"head": (0, -18, 0)})
hero_beat(19.0, "kraken", arms=kraak, face="zelfverzekerd", look=(-0.2, -0.3), body={"head": (10, -10, 0)})
hero_beat(19.35, "kraken", arms=kraak, face="grijns", look=(-0.2, -0.3), body={"head": (12, -10, -4), "chest": (3, 0, 0)})
hero_beat(19.9, "vuisten", face="zelfverzekerd", look=(-0.4, 0.0), body={"head": (0, -24, 0)})
hero_beat(20.7, "schouders_op", face="twijfel", face_amt=0.6, look=(-0.5, 0.1), body={"head": (-4, -28, 8)})
hero_beat(21.3, "vuisten", face="zelfverzekerd", look=(-0.5, 0.0), body={"head": (0, -30, 0)})
hero_beat(22.6, "vuisten", face="grijns", look=(-0.6, 0.0), body={"head": (-3, -34, 5)})
hero_beat(23.6, "vuisten", face="vastberaden", look=(0, 0.3), body={"head": (-6, 0, 0)})
hero_beat(before(24.2), "vuisten", face="vastberaden", look=(0, 0.3), body={"head": (-6, 0, 0)})
# S8 SIMULATIE: zetten, duwen, wegglijden, meegenomen worden
hero_beat(24.2, "vuisten", face="vastberaden", look=(0, 0.2))
hero_beat(25.4, "schrap", crouch=(0.12, 8.0), feet=((0.04, 0.22, 0), (-0.04, -0.28, 0)), face="vastberaden", look=(0, 0.3))
hero_beat(27.4, "duwen", crouch=(0.14, 12.0), feet=((0.04, 0.22, 0), (-0.04, -0.30, 0)), face="vastberaden", look=(0, 0.3))
hero_beat(29.9, "duwen", crouch=(0.15, 14.0), feet=((0.04, 0.22, 0), (-0.04, -0.30, 0)), face="inspanning", face_amt=0.6, look=(0, 0.2))
hero_beat(30.3, "duwen", crouch=(0.20, 20.0), feet=((0.04, 0.20, 0), (-0.04, -0.34, 0)), face="inspanning", mouth=0.2, body={"spine": (18, 0, 0), "head": (-14, 0, 0)})
hero_beat(32.6, "duwen", crouch=(0.22, 22.0), feet=((0.04, 0.18, 0), (-0.04, -0.36, 0)), face="inspanning", mouth=0.3, body={"spine": (20, 0, 0), "head": (-16, 0, 0)})
hero_beat(33.6, "duwen", crouch=(0.18, 14.0), feet=((0.04, 0.18, 0), (-0.04, -0.36, 0)), face="geschrokken", face_amt=0.7, mouth=0.3, look=(0, 0.2))
hero_beat(34.9, "schrik", crouch=(0.10, 0.0), feet=((0.04, 0.10, 0.1), (-0.04, -0.10, 0.0)), face="geschrokken", mouth=0.6)
hero_beat(35.5, "armen_omhoog", feet=((0.06, 0.25, 0.25), (-0.06, 0.15, 0.10)), face="schreeuw", mouth=1.0)
hero_beat(36.3, "handen_hoofd", feet=((0.06, 0.30, 0.15), (-0.06, 0.05, 0.25)), face="schreeuw", mouth=0.9)
hero_beat(37.0, "armen_omhoog", feet=((0.06, 0.20, 0.25), (-0.06, 0.25, 0.10)), face="schreeuw", mouth=1.0)
hero_beat(before(37.6), "handen_hoofd", feet=((0.06, 0.30, 0.15), (-0.06, 0.05, 0.25)), face="schreeuw", mouth=0.9)
# S9: terug in het echt. Grijpt de rails
hero_beat(37.6, "vuisten", face="vastberaden", look=(0, 0.3))
hero_beat(38.6, "vuisten", crouch=(0.04, 4.0), face="vastberaden", look=(0, -0.6), body={"head": (16, 0, 0)})
hero_beat(39.3, "schrap", crouch=(0.22, 18.0), feet=((0.14, 0.03, 0), (-0.14, 0.03, 0)), face="vastberaden", look=(0, -0.5),
          body={"spine": (10, 0, 0), "head": (6, 0, 0)}, hands=0.0)
hero_beat(40.0, **{**GRAB, "hands": 0.7}, face="vastberaden", look=(0, 0.4))
hero_beat(40.4, **GRAB, face="inspanning", face_amt=0.7, look=(0, 0.4))
hero_beat(41.0, **GRAB, face="inspanning", face_amt=0.8, look=(0, 0.4), sink=0.0)
hero_beat(41.9, **GRAB, face="inspanning", look=(0, 0.45), sink=0.07, mouth=0.1)
hero_beat(43.2, **GRAB, face="inspanning", look=(0, 0.45), sink=0.07, mouth=0.1)
# S10: "And then you hear it" - pupillen klein, kijkt omlaag naar de bouten
SCARED = dict(pupil_klein=1.0, ogen_wijd=1.0, mond_verdrietig=0.6, mond_lach=0.0)
hero_beat(43.9, **GRAB, face="bang", face_amt=0.8, look=(0.35, -0.65), sink=0.07, mouth=0.15, **SCARED)
hero_beat(45.4, **GRAB, face="bang", face_amt=0.9, look=(0.45, -0.7), sink=0.07, mouth=0.2, **SCARED)
hero_beat(48.6, **GRAB, face="bang", look=(0.0, 0.3), sink=0.07, mouth=0.2, **SCARED)
hero_beat(50.6, **GRAB, face="inspanning", look=(0.0, 0.4), sink=0.07, mouth=0.25)
hero_beat(END_T + 0.1, **GRAB, face="schreeuw", face_amt=0.8, look=(0.0, 0.4), sink=0.07, mouth=0.8)
A.blinks(hero, 1, F(END_T), seed=5, every=(60, 120))
for t in (12.75, 16.25, 38.7, 44.0):
    A.blink_at(hero, F(t))
A.alive(hero, 1, F(END_T), energy=1.2, seed=7)

# ---------------------------------------------------------------------------
# De beste vriend, op het pad: filmt met zijn telefoon (rechts) en schreeuwt
# ---------------------------------------------------------------------------
FRIEND_POS = Vector((25.0, -23.4, 0.02))
to_hero = (Vector((HP.x, HP.y, 0)) - Vector((FRIEND_POS.x, FRIEND_POS.y, 0))).normalized()
friend_rot = math.degrees(math.atan2(to_hero.x, -to_hero.y))
friend = R.load("beste_vriend", loc=tuple(FRIEND_POS), rot_z=friend_rot)


def wave(w):
    return lambda f: A.aim_arm(friend, f, "L", *[tuple(lerp(a, b, w) for a, b in zip(u, v))
                                                     for u, v in zip(A.POSES["zwaaien_a"]["L"][:2], A.POSES["zwaaien_b"]["L"][:2])])


def friend_beat(t, face, amt=1.0, arms=None, body=None, crouch=(0.0, 0.0), look=None):
    f = F(t)
    A.pose(friend, f, "filmen_R", extra=body)
    if arms:
        arms(f)
    A.crouch(friend, f, *crouch)
    A.expr(friend, f, face, amount=amt, look=look)


friend_beat(0.0, "bang", look=(0, 0.3))
friend_beat(15.3, "bang", look=(0, 0.3), body={"head": (-6, 0, 0)})
friend_beat(15.55, "schreeuw", arms=wave(0.0), crouch=(0.05, 8), body={"chest": (6, 0, 0), "head": (-8, 0, 0)}, look=(0, 0.3))
for k, t in enumerate([15.85, 16.15, 16.45, 16.75, 17.05, 17.35, 17.65]):
    friend_beat(t, "schreeuw", arms=wave(1.0 if k % 2 == 0 else 0.0), crouch=(0.05, 8),
                body={"chest": (6, 0, 4 if k % 2 else -4), "head": (-8, 0, 0)}, look=(0, 0.3))
friend_beat(18.2, "bang", amt=0.8, arms=wave(0.5), body={"head": (-4, 0, 0)}, look=(0, 0.3))
friend_beat(21.0, "bang", look=(0, 0.3))
A.lipsync(friend, os.path.join(R.ASSETS, "audio", "S01", "S01-04_Vriend.mp3"), F(15.6), base_open=0.15, gain=1.2)
A.key_prop(friend.rig, "mond_open", 0.15, F(15.0))
A.blinks(friend, 1, F(END_T), seed=11)
A.alive(friend, 1, F(END_T), energy=1.5, seed=13)

# ---------------------------------------------------------------------------
# Bouten die eruit schieten (S11), vonken en de labels van de simulatie
# ---------------------------------------------------------------------------
BOLT_MAT = T.toon("bout_los", (0.78, 0.78, 0.74))
T.use_collection(T.collection("Effecten"))
bolts = []
BOLT_T = [45.92, 46.95, 47.86]
for k, i in enumerate((HERO_I - 3, HERO_I - 5, HERO_I - 7)):
    t_, s_, u_ = frame_at(i)
    q = path[i] - s_ * GAUGE * 1.05 - u_ * 0.12
    b = T.cyl(f"Bout_los_{k + 1}", (0, 0, 0), 0.05, 0.12, BOLT_MAT, seg=6, ol=0.006)
    T.cyl(f"Bout_kop_{k + 1}", (0, 0, 0.12), 0.07, 0.04, BOLT_MAT, seg=6, ol=0.006).parent = b
    b.location = q
    b.keyframe_insert("location", frame=1)
    b.keyframe_insert("rotation_euler", frame=1)
    tp = BOLT_T[k]
    rnd = random.Random(k)
    b.keyframe_insert("location", frame=F(tp))
    b.keyframe_insert("rotation_euler", frame=F(tp))
    for j in range(1, 30):
        tt = j / FPS * 0.5
        b.location = q + Vector((rnd.uniform(-0.6, 0.6) * tt, -0.4 * tt, 3.2 * tt - 4.9 * tt * tt))
        b.rotation_euler = (9 * tt * (k + 1), 13 * tt, 4 * tt)
        b.keyframe_insert("location", frame=F(tp) + j)
        b.keyframe_insert("rotation_euler", frame=F(tp) + j)
    bolts.append((b, q))


def flash(name, loc, t, size=0.25):
    o = T.sphere(name, tuple(loc), 1.0, T.glow("flits_wit", (1.0, 0.85, 0.55), 4), seg=12, ol=0)
    for tt, s in ((t - 1 / FPS, 0.001), (t, size), (t + 3 / FPS, size * 0.4), (t + 6 / FPS, 0.001)):
        o.scale = (s, s, s)
        o.keyframe_insert("scale", frame=F(tt))
    return o


for k, (b, q) in enumerate(bolts):
    flash(f"Flits_bout_{k + 1}", q + Vector((0, 0, 0.1)), BOLT_T[k], 0.07)
flash("Flits_remmen", car_matrix(car_s(2.0, 2)).translation, 2.0, 0.3)


def sparks(name, parent_loc_fn, t0, t1, count=250, speed=3.0, frames_keyed=None):
    """Vonkenregen: een particle-systeem dat kleine gloeiende streepjes uitstoot."""
    spark = bpy.data.objects.get("Vonk")
    if spark is None:
        spark = T.sphere("Vonk", (0, 0, -60), 1.0, T.glow("vonk", (1.0, 0.62, 0.18), 18), scale=(0.012, 0.012, 0.07), seg=6, ol=0)
    em = T.box(name, (0, 0, 0), (0.4, 0.4, 0.05), None, bevel=0, ol=0)
    em.show_instancer_for_render = False
    em.show_instancer_for_viewport = False
    for f in frames_keyed or [F(t0) - 2, F(t1) + 2]:
        em.location = parent_loc_fn((f - 1) / FPS)
        em.keyframe_insert("location", frame=f)
    ps = em.modifiers.new("Vonken", "PARTICLE_SYSTEM").particle_system
    st = ps.settings
    st.count = count
    st.frame_start, st.frame_end = F(t0), F(t1)
    st.lifetime = 10
    st.lifetime_random = 0.5
    st.emit_from = "FACE"
    st.normal_factor = speed
    st.factor_random = speed * 0.8
    st.render_type = "OBJECT"
    st.instance_object = spark
    st.particle_size = 1.0
    st.size_random = 0.5
    st.use_rotations = True
    st.rotation_mode = "VEL"
    st.physics_type = "NEWTON"
    ps.point_cache.frame_start = F(t0) - 2
    ps.point_cache.frame_end = F(t1) + 14
    return em


sparks("Vonken_remmen", lambda t: car_matrix(car_s(t, 2)).translation + Vector((0, 0, -0.1)), 2.0, 2.9, count=400, speed=4.0,
       frames_keyed=list(range(F(1.9), F(3.5))))
sparks("Vonken_schoenen", lambda t: hero_root(t)[0] + Vector((0.1, 0, 0.03)), 30.2, 34.8, count=500, speed=2.0,
       frames_keyed=list(range(F(30.0), F(35.0), 2)))
sparks("Vonken_handen_R", lambda t: RAIL_R + Vector((0.05, 0, -0.1)), 41.0, 41.6, count=80, speed=1.5)
sparks("Vonken_handen_L", lambda t: RAIL_L + Vector((0.05, 0, -0.1)), 41.0, 41.6, count=80, speed=1.5)

# simulatielabels (alleen tussen 24,2 en 37,6 te zien; de montage kleurt dat stuk blauw)
HOLO = T.glow("holo_cyaan", (0.25, 0.95, 1.0), 6)


def label(name, body, size, loc_fn, t_show):
    o = T.text(name, body, (0, 0, 0), size, HOLO, extrude=0.0)
    frames = list(range(F(SIM[0]) - 1, F(SIM[1]) + 1))
    bake(o, "location", frames, [tuple(loc_fn((f - 1) / FPS)) for f in frames])
    for f, h in ((1, True), (F(t_show), False), (F(SIM[1]), True)):
        o.hide_render = h
        o.hide_viewport = h
        o.keyframe_insert("hide_render", frame=f)
        o.keyframe_insert("hide_viewport", frame=f)
        for fc in A._fcurves(o):
            if fc.data_path.startswith("hide"):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"
    return o


label("Label_75kg", "75 KG", 0.4, lambda t: hero_root(t)[0] + Vector((0, 0, 1.9)), 26.1)
label("Label_6000kg", "6,000 KG", 0.55, lambda t: nose_pos(t) + Vector((-2.4, 0, 1.25)), 28.8)

# ---------------------------------------------------------------------------
# Camera's: één camera per shot, gewisseld met markers in de tijdlijn
# ---------------------------------------------------------------------------
T.use_collection(T.collection("Camera's"))
SHOTS = []


def shot(name, t0, t1, fn, dof=None, shake=None):
    """fn(t) -> (positie, doel, lens). shake(t) -> sterkte in graden."""
    cd = bpy.data.cameras.new(name)
    cd.clip_start, cd.clip_end = 0.03, 3000
    cd.sensor_width = 36
    cam = bpy.data.objects.new(name, cd)
    T._link(cam)
    frames = list(range(F(t0) - 1, F(t1) + 2))
    mats, lens_rows, focus_rows = [], [], []
    seed = len(SHOTS) * 3.3
    for f in frames:
        t = (f - 1) / FPS
        loc, tgt, lens = fn(t)
        q = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y")
        if shake:
            amp = math.radians(shake(t))
            e = (noise.noise(Vector((t * 9, seed, 0))) * amp, noise.noise(Vector((t * 9, seed, 5))) * amp,
                 noise.noise(Vector((t * 9, seed, 9))) * amp * 0.5)
            q = q @ Quaternion((1, 0, 0), e[0]) @ Quaternion((0, 1, 0), e[1]) @ Quaternion((0, 0, 1), e[2])
        M = q.to_matrix().to_4x4()
        M.translation = Vector(loc)
        mats.append(M)
        lens_rows.append((lens,))
        focus_rows.append(((Vector(tgt) - Vector(loc)).length,))
    bake_matrices(cam, frames, mats)
    bake(cd, "lens", frames, lens_rows)
    if dof:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = dof
        bake(cd.dof, "focus_distance", frames, focus_rows)
    m = sc.timeline_markers.new(name, frame=F(t0))
    m.camera = cam
    SHOTS.append((t0, t1, cam))
    return cam


def car_frame(t, k):
    s = car_s(t, k)
    tt, side, up = frame_at(s)
    return P(s) + up * 0.25, tt, side, up


def decay(t0, peak, length):
    return lambda t: peak * max(0.0, 1 - (t - t0) / length) if t >= t0 else 0.0


# S1 totaal: zonsondergang, de trein kruipt over de top
shot("S01_totaal", 0.0, 1.8, lambda t: (vlerp((47, -64, 9.5), (49, -60, 10.0), t / 1.8),
                                        vlerp((80, -12, 22), nose_pos(t), 0.55), 30))
# S2 remmen: dichtbij de wielen van wagen 3, knal en vonken op 2,0
shot("S02_remmen", 1.8, 4.2, lambda t: (lambda c: (c[0] - c[2] * 3.0 - c[3] * 0.05 - c[1] * 1.2,
                                                    c[0] - c[3] * 0.2 + c[1] * 0.3, 32))(car_frame(t, 2)),
     shake=lambda t: decay(2.0, 2.5, 1.4)(t) + 0.3)
# S3a over de hoofden, de afdaling in
shot("S03a_afdaling", 4.2, 5.95, lambda t: (lambda c, c1: (c[0] + c[3] * 2.5 - c[1] * 1.4,
                                                           c1[0] + c1[1] * 10 - c1[3] * 3.0, 24))(car_frame(t, 2), car_frame(t, 0)),
     shake=lambda t: 0.9)
# S3b aan boord, terugkijkend naar de gillende passagiers (24 mensen)
shot("S03b_aan_boord", 5.95, 7.6, lambda t: (lambda c: (c[0] + c[1] * 2.3 + c[3] * 1.25,
                                                        c[0] - c[1] * 1.2 + c[3] * 0.8, 21))(car_frame(t, 0)),
     shake=lambda t: 1.1)
# S4 vanaf de grond: de trein raast voorbij en vertraagt tot slow motion
S4_CAM = Vector((40.5, -19.5, 3.4))
shot("S04_zijkant", 7.6, 11.4, lambda t: (S4_CAM + Vector((0.0, 0.0, 0.15 * smooth(8.6, 11.4, t))),
                                          vlerp(nose_pos(t) - Vector((0, 0, 0.6)), (HP.x + 6, HP.y, HP.z + 2.5), smooth(9.4, 11.4, t) * 0.5),
                                          lerp(24, 30, smooth(9, 11.4, t))),
     shake=lambda t: 0.8 * (1 - smooth(8.6, 9.6, t)))


def arc(t):
    w = smooth(11.6, 15.0, t)
    ang = math.radians(lerp(196, 318, w))
    r = lerp(3.1, 2.3, w)
    loc = H(r * math.cos(ang), r * math.sin(ang), lerp(0.35, 1.05, w))
    tgt = H(0, 0, lerp(1.05, 1.42, w))
    return loc, tgt, lerp(24, 34, w)


# S5 "...is you": laag achter hem met de trein op de achtergrond, draait naar zijn gezicht
shot("S05_held", 11.4, 15.3, arc)
# S6 de vriend met zijn telefoon
perp = Vector((-to_hero.y, to_hero.x, 0))
shot("S06_vriend", 15.3, 18.4, lambda t: (FRIEND_POS + to_hero * lerp(2.9, 2.4, (t - 15.3) / 3.1) + perp * 0.8 + Vector((0, 0, 1.3)),
                                          FRIEND_POS + Vector((0, 0, 1.38)) + perp * 0.1, 40))
# S7 medium shot: knokkels, grijns naar de camera
shot("S07_grijns", 18.4, 24.2, lambda t: (vlerp(H(2.05, -2.35, 1.30), H(1.75, -2.0, 1.28), smooth(18.4, 24.2, t)),
                                          H(0, 0, 1.30), 38))


# S8 simulatie: zijaanzicht, de camera volgt het midden van de actie
def sim_cam(t):
    dd = D_SIM(t)
    mid = (dd * 0.5 + 0.6) if dd > 0 else dd + 0.6
    x = H(mid, 0, 0).x
    dist = max(5.5, min(10.0, 4.5 + dd * 0.55))
    return Vector((x - 0.3, HP.y - dist, GROUND + 1.6)), Vector((x, HP.y, GROUND + 1.25)), 28


shot("S08_simulatie", 24.2, 37.6, sim_cam)
# S9a de rails grijpen (zijkant, trein op de achtergrond)
shot("S09a_grijpen", 37.6, 40.8, lambda t: (vlerp(H(1.0, -4.0, 1.25), H(0.9, -3.4, 1.05), smooth(37.6, 40.8, t)),
                                            H(0.6, 0, 0.78), 30))
# S9b close-up van zijn rechterhand die in het staal zakt
shot("S09b_hand", 40.8, 43.2, lambda t: (RAIL_R + Vector((0.62, -0.50, 0.14)) + Vector((-0.08, 0.06, 0)) * smooth(40.8, 43.2, t),
                                         RAIL_R + Vector((0.02, 0, -0.12)), 45),
     dof=2.8, shake=lambda t: decay(41.0, 1.2, 0.6)(t) + decay(42.9, 0.8, 0.5)(t))
# S10 gezicht (positie wordt na het poseren gemeten)
sc.frame_set(F(44.0))
head_w = hero.rig.matrix_world @ hero.rig.pose.bones["head"].head
face_c = head_w + Vector((0.10, 0, 0.22))
shot("S10_gezicht", 43.2, 45.6, lambda t: (face_c + Vector((lerp(1.05, 0.85, smooth(43.2, 45.6, t)), -0.32, -0.02)),
                                          face_c, 50), dof=2.8)
# S11 de bouten: laag langs de rail, held op de achtergrond
b2 = bolts[1][1]
shot("S11_bouten", 45.6, 48.8, lambda t: (b2 + Vector((2.0, -0.55, 0.22)) + Vector((-0.25, 0.05, 0)) * smooth(45.6, 48.8, t),
                                          b2 + Vector((-0.4, 0.15, 0.05)), 32),
     dof=4.0, shake=lambda t: sum(decay(tp, 0.9, 0.35)(t) for tp in BOLT_T))
# S12 achter hem: de trein komt recht op de camera af
shot("S12_trein", 48.8, END_T, lambda t: (vlerp(H(-2.6, -0.60, 1.45), H(-2.2, -0.55, 1.35), smooth(48.8, END_T, t)),
                                          H(6.0, 0.35, 1.25), 30),
     shake=lambda t: 0.25 + 1.6 * smooth(50.6, END_T, t))
sc.camera = SHOTS[0][2]

# ---------------------------------------------------------------------------
# Opslaan en renderen
# ---------------------------------------------------------------------------
sc.render.resolution_percentage = args.pct
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(args.out, "frames", "")
sc.frame_set(1)
os.makedirs(args.out, exist_ok=True)
blend = os.path.join(args.out, "s01_cold_open.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
print("OPGESLAGEN", blend)

if args.stills:
    for t in [float(x) for x in args.stills.split(",")]:
        f = F(t)
        sc.frame_set(f)
        for t0, t1, cam in SHOTS:
            if t0 <= t < t1:
                sc.camera = cam
        sc.render.filepath = os.path.join(args.out, "stills", f"t{t:05.1f}_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    sc.render.filepath = os.path.join(args.out, "frames", "")
if args.render:
    bpy.ops.render.render(animation=True)
    print("KLAAR: frames in", os.path.join(args.out, "frames"))
