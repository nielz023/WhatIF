"""Raamwerk voor de scènes S02-S28: set, figuren, stemmen, acteren, camera's, effecten en montage.

Elke scène (of elk deel van een scène met een andere set) is een kort script:

    from scene import *
    S = Scene("s02", "slaapkamer", "ochtend")
    held = S.actor("hoofdpersonage", (0.35, -0.55, 0), -15)
    t0, t1 = S.say("S02-01")                 # verteller, achter elkaar op de tijdlijn
    S.beat(held, t0, "staan", face="verbaasd")
    S.cam(0.0, ((1, -3, 1.5), (0, 0, 1.2), 30))
    S.finish()

Tijden staan in seconden (24 fps). S.finish() bewaart out/<code>/<code>.blend, schrijft
out/<code>/montage.json (stem, muziek, geluid, HUD) en rendert met --render of --stills.
anim/edit/montage.py maakt daar een MP4 van.
"""
import argparse
import glob
import json
import math
import os
import random
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "sets"))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
from mathutils import Vector, Matrix, Quaternion, Euler, noise  # noqa: E402
from lib import toon as T  # noqa: E402
from lib import props as P  # noqa: E402
from lib import interior as I  # noqa: E402
from lib import street as ST  # noqa: E402
import rig as R  # noqa: E402
import acting as A  # noqa: E402

FPS = 24
# Uitvoer-fps. Alles wordt in 24-fps-frames geanimeerd; bij WHATIF_FPS=60 rekt Blender de tijd op
# (frame_map 24 -> 60) en tussenframes worden uit de curves geïnterpoleerd. 60-fps-beeld n toont t = (n - 2.5) / 60.
OUT_FPS = int(os.environ.get("WHATIF_FPS", FPS))
AUDIO = os.path.join(R.ASSETS, "audio")
GOLD = (1.0, 0.82, 0.18, 1)
WHITE = (1, 1, 1, 1)
RED = (1.0, 0.25, 0.2, 1)
CYAN = (0.35, 0.95, 1.0, 1)


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


def frange(a, b, step):
    """Tijden van a tot (niet t/m) b met stap step."""
    out = []
    t = a
    while t < b - 1e-6:
        out.append(t)
        t += step
    return out


def V(*a):
    return Vector(a[0] if len(a) == 1 else a)


def audio_len(path):
    import aud
    s = aud.Sound(path)
    try:
        return s.length / s.specs[0]
    except Exception:
        import numpy as np
        return len(np.asarray(s.data())) / s.specs[0]


def voice_file(line_id):
    hits = sorted(glob.glob(os.path.join(AUDIO, line_id[:3], line_id + "_*.mp3")))
    hits = [h for h in hits if not h.endswith("_traag.mp3")] or hits   # vertraagde versie alleen expliciet
    if not hits:
        raise SystemExit("Geen stem voor " + line_id)
    return hits[0]


def heading(frm, to):
    """rot_z (graden) zodat een figuur op `frm` naar `to` kijkt (figuren kijken naar -y bij 0)."""
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    return math.degrees(math.atan2(dx, -dy))


def fmt(n):
    return f"{n:,}"


# ---------------------------------------------------------------------------
# Keyframes in bulk
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
        keep = [(kp.co.x, kp.co.y) for kp in fc.keyframe_points if kp.co.x < frames[0] - 0.5 or kp.co.x > frames[-1] + 0.5]
        fc.keyframe_points.clear()
        pts = sorted(keep + [(f, r[i]) for f, r in zip(frames, rows)])
        fc.keyframe_points.add(len(pts))
        co = []
        for f, v in pts:
            co += [f, v]
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


def constant(obj, path_prefix="hide"):
    for fc in A._fcurves(obj):
        if fc.data_path.startswith(path_prefix):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def key(obj, t, loc=None, rot=None, scale=None, interp=None):
    """Keyframe een object op tijd t (rot in graden)."""
    f = F(t)
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=f)
    if rot is not None:
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = Euler([math.radians(a) for a in rot])
        obj.keyframe_insert("rotation_euler", frame=f)
    if scale is not None:
        obj.scale = (scale,) * 3 if isinstance(scale, (int, float)) else scale
        obj.keyframe_insert("scale", frame=f)
    if interp:
        for fc in A._fcurves(obj):
            for kp in fc.keyframe_points:
                if abs(kp.co.x - f) < 0.5:
                    kp.interpolation = interp


def visible(obj, t, on):
    """Zet een object (en zijn kinderen) zichtbaar/onzichtbaar vanaf tijd t."""
    for o in [obj] + list(obj.children_recursive):
        o.hide_render = not on
        o.hide_viewport = not on
        o.keyframe_insert("hide_render", frame=F(t))
        o.keyframe_insert("hide_viewport", frame=F(t))
        constant(o)


def show(obj, t0, t1=None):
    visible(obj, 0, False)
    visible(obj, t0, True)
    if t1 is not None:
        visible(obj, t1, False)


# Figuranten: castfiguren met andere kleren (zelfde ontwerpen als in de cold open)
EXTRAS = [
    dict(label="figurant_a", cast="gymleraar", drop=("fluitje", "koord", "rits"),
         outfit=dict(shirt=(0.85, 0.20, 0.15), broek=(0.15, 0.15, 0.20), haar=(0.10, 0.07, 0.05))),
    dict(label="figurant_b", cast="nieuwslezeres", drop=("microfoon", "oorbel"),
         outfit=dict(shirt=(0.98, 0.75, 0.10), broek=(0.20, 0.30, 0.60), haar=(0.55, 0.30, 0.12))),
    dict(label="figurant_c", cast="wetenschapper", drop=("klembord", "pen", "pasje", "bril", "labjas_zakje"),
         outfit=dict(shirt=(0.30, 0.70, 0.35), broek=(0.25, 0.22, 0.20), haar=(0.60, 0.45, 0.20))),
    dict(label="figurant_d", cast="mama", drop=("oorbel",),
         outfit=dict(shirt=(0.85, 0.35, 0.65), broek=(0.15, 0.15, 0.18), haar=(0.08, 0.06, 0.05))),
    dict(label="figurant_e", cast="papa", drop=(),
         outfit=dict(shirt=(0.95, 0.50, 0.10), broek=(0.30, 0.25, 0.20))),
    dict(label="figurant_f", cast="gymleraar", drop=("fluitje", "koord", "rits"),
         outfit=dict(shirt=(0.10, 0.60, 0.60), broek=(0.20, 0.20, 0.25), haar=(0.70, 0.50, 0.25))),
    dict(label="figurant_g", cast="nieuwslezeres", drop=("microfoon", "oorbel"),
         outfit=dict(shirt=(0.55, 0.30, 0.75), broek=(0.30, 0.30, 0.35), haar=(0.15, 0.10, 0.07))),
    dict(label="figurant_h", cast="wetenschapper", drop=("klembord", "pen", "pasje", "bril", "labjas_zakje"),
         outfit=dict(shirt=(0.20, 0.50, 0.95), broek=(0.90, 0.85, 0.75), haar=(0.08, 0.06, 0.05))),
]


# ---------------------------------------------------------------------------
# De scène
# ---------------------------------------------------------------------------
class Scene:
    def __init__(self, code, set_name=None, variant=None, samples=16):
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
        ap = argparse.ArgumentParser()
        ap.add_argument("--render", action="store_true")
        ap.add_argument("--pct", type=int, default=100)
        ap.add_argument("--samples", type=int, default=samples)
        ap.add_argument("--out", default=None)
        ap.add_argument("--stills", default=None, help="tijden (komma's) of 'auto' (midden van elk shot)")
        ap.add_argument("--nosave", action="store_true")
        self.args = ap.parse_args(argv)
        self.code = code
        self.out = os.path.abspath(self.args.out or os.path.join(REPO, "out", code))
        self.t = 0.0
        self.voice, self.sounds, self.texts, self.cards = [], [], [], []
        self.cast, self.cams = [], []
        self.length = None
        self.fx_n = 0
        self.mats = {}
        self.SET = {}
        if set_name:
            self.build_set(set_name, variant)
        sc = bpy.context.scene
        sc.name = code
        sc.render.fps = FPS
        self.sc = sc
        T.use_collection(T.collection("Animatie " + code))

    # -- set ---------------------------------------------------------------
    def build_set(self, set_name, variant):
        os.environ["SET_RENDER"] = "0"
        os.environ["SET_SAMPLES"] = str(self.args.samples)
        _argv = sys.argv
        sys.argv = [_argv[0], "--", variant or "", os.path.join(self.out, "set")]
        self.SET = runpy.run_path(os.path.join(REPO, "sets", f"build_{set_name}.py"))
        sys.argv = _argv
        sc = bpy.context.scene
        for cname in [c.name for c in bpy.data.collections if c.name.startswith("Hoofdpersonage (")]:
            c = bpy.data.collections[cname]
            for o in list(c.all_objects):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(c)
        for o in [o for o in sc.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o, do_unlink=True)
        for o in [o for o in bpy.data.objects if o.name == "Hoofdpersonage" and not o.users_collection]:
            bpy.data.objects.remove(o)

    def obj(self, name):
        """Object uit de set (exacte naam of het eerste dat ermee begint)."""
        o = bpy.data.objects.get(name)
        if o is None:
            for ob in bpy.data.objects:
                if ob.name.startswith(name):
                    return ob
        return o

    def mat(self, name, color, glow=0.0):
        k = (name, tuple(color), glow)
        if k not in self.mats:
            nm = name if not any(kk[0] == name for kk in self.mats) else f"{name}_{len(self.mats)}"
            self.mats[k] = T.glow(nm, color, glow) if glow else T.toon(nm, color)
        return self.mats[k]

    def wall(self, t0, t1, side="front"):
        """Laat een verborgen muur (meestal de voorkant) zien van t0 tot t1, voor tegenshots."""
        for o in bpy.data.objects:
            if o.name.endswith("_muur_" + side):
                o.visible_camera = False
                o.keyframe_insert("visible_camera", frame=1)
                o.visible_camera = True
                o.keyframe_insert("visible_camera", frame=F(t0))
                o.visible_camera = False
                o.keyframe_insert("visible_camera", frame=F(t1))
                for fc in A._fcurves(o):
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"

    # -- figuren -------------------------------------------------------------
    def actor(self, name, loc=(0, 0, 0), rot=0.0, energy=1.0, **kw):
        ch = R.load(name, loc=tuple(loc), rot_z=rot, **kw)
        ch.energy = energy
        ch.last = None
        self.cast.append(ch)
        A.place(ch, 1, tuple(loc), rot)
        return ch

    def extra(self, k, loc=(0, 0, 0), rot=0.0, energy=1.0):
        """Figurant k (castfiguur met andere kleren), voor klasgenoten, publiek, voorbijgangers."""
        d = EXTRAS[k % len(EXTRAS)]
        return self.actor(d["cast"], loc, rot, energy, label=f"{d['label']}_{len(self.cast)}", outfit=d.get("outfit"), drop=d["drop"])

    def head(self, ch, t=None, up=0.0):
        """Wereldpositie van het midden van het hoofd (rustpose; snel)."""
        if t is not None:
            M = self._root_matrix(ch, t)
        else:
            M = ch.rig.matrix_basis
        return M @ (ch.J["head_c"] + Vector((0, 0, up)))

    def _root_matrix(self, ch, t):
        f = F(t)
        loc = [ch.rig.location[i] for i in range(3)]
        rot = [ch.rig.rotation_euler[i] for i in range(3)]
        for fc in A._fcurves(ch.rig):
            if fc.data_path == "location":
                loc[fc.array_index] = fc.evaluate(f)
            elif fc.data_path == "rotation_euler":
                rot[fc.array_index] = fc.evaluate(f)
        M = Euler(rot).to_matrix().to_4x4()
        M.translation = Vector(loc)
        return M @ Matrix.Diagonal(ch.rig.scale.to_4d())

    def bone_world(self, ch, bone, t, tail=True):
        """Echte wereldpositie van een bot op tijd t (evalueert de pose)."""
        self.sc.frame_set(F(t))
        pb = ch.rig.pose.bones[bone]
        return ch.rig.matrix_world @ (pb.tail if tail else pb.head)

    def look_dir(self, ch, t, target):
        """Hoofd/nek-rotatie (graden) zodat ch naar een wereldpunt kijkt."""
        M = self._root_matrix(ch, t)
        p = M.inverted() @ Vector(target) - ch.J["head_c"]
        yaw = math.degrees(math.atan2(p.x, -p.y))
        pitch = math.degrees(math.atan2(-p.z, math.hypot(p.x, p.y)))
        yaw = max(-80, min(80, yaw))
        pitch = max(-35, min(40, pitch))
        return yaw, pitch

    def beat(self, ch, t, pose="staan", amount=1.0, face=None, face_amt=1.0, look=None, at=None, body=None,
             crouch=(0.0, 0.0), feet=None, arms=None, mouth=None, hold=None, face_only=False, **face_extra):
        """Eén moment in het acteren: houding, gezicht, kijkrichting. Alles gekeyd op t (en t+hold)."""
        spec = dict(pose=pose, amount=amount, face=face, face_amt=face_amt, look=look, at=at, body=body,
                    crouch=crouch, feet=feet, arms=arms, mouth=mouth, face_only=face_only, extra=face_extra)
        self._beat(ch, t, spec)
        if hold:
            self._beat(ch, t + hold, spec)
        ch.last = spec

    def hold(self, ch, t):
        """Herhaal de laatste beat op t (houding vasthouden tot daar)."""
        if ch.last:
            self._beat(ch, t, ch.last)

    def _beat(self, ch, t, s):
        f = F(t)
        body = dict(s["body"] or {})
        look = s["look"]
        if s["at"] is not None:
            yaw, pitch = self.look_dir(ch, t, s["at"])
            nk = body.get("neck", (0, 0, 0))
            hd = body.get("head", (0, 0, 0))
            body["neck"] = (nk[0] + pitch * 0.35, nk[1] + yaw * 0.4, nk[2])
            body["head"] = (hd[0] + pitch * 0.55, hd[1] + yaw * 0.5, hd[2])
            if look is None:
                look = (max(-1, min(1, yaw * 0.1 / 8)), max(-1, min(1, -pitch / 40)))
        if not s["face_only"]:
            A.pose(ch, f, s["pose"], amount=s["amount"], extra=body)
            if s["arms"]:
                s["arms"](ch, f)
            if s["feet"] != "keep":                      # "keep": tijdens walk() de benen niet aanraken
                A.crouch(ch, f, *s["crouch"])
                fl, fr = s["feet"] or ((0, 0, 0), (0, 0, 0))
                A.foot(ch, f, "L", fl)
                A.foot(ch, f, "R", fr)
        if s["face"]:
            A.expr(ch, f, s["face"], amount=s["face_amt"], look=look, **s["extra"])
        elif look:
            A.look(ch, f, *look)
        if s["mouth"] is not None:
            A.key_prop(ch.rig, "mond_open", s["mouth"], f)

    def face(self, ch, t, name, amt=1.0, look=None, **extra):
        A.expr(ch, F(t), name, amount=amt, look=look, **extra)

    def _rot_now(self, ch, t):
        for fc in A._fcurves(ch.rig):
            if fc.data_path == "rotation_euler" and fc.array_index == 2:
                return fc.evaluate(F(t))
        return ch.rig.rotation_euler.z

    def _near(self, ch, t, rot_deg):
        """Hoek (graden) die het dichtst bij de huidige draaiing ligt (geen rondtollen)."""
        cur = self._rot_now(ch, t)
        r = math.radians(rot_deg)
        while r - cur > math.pi:
            r -= 2 * math.pi
        while r - cur < -math.pi:
            r += 2 * math.pi
        return math.degrees(r)

    def place(self, ch, t, loc=None, rot=None):
        if rot is not None:
            rot = self._near(ch, t, rot)
        A.place(ch, F(t), tuple(loc) if loc is not None else None, rot)

    def reach(self, ch, t, side, target=None, inf=1.0, rot=None):
        """Hand-IK: pols naar een wereldpunt op tijd t (inf=0: IK uit). Houdt rekening met waar het figuur dan staat."""
        M = self._root_matrix(ch, t)
        loc, rq, sc = M.decompose()
        ch.rig.location = loc
        ch.rig.rotation_euler = rq.to_euler()
        A.hand_ik(ch, F(t), side, inf, Vector(target) if target is not None else None, rot)

    def teleport(self, ch, t, loc, rot=None):
        """Harde verplaatsing op een snede: houdt de oude stand vast tot vlak voor t."""
        M = self._root_matrix(ch, t - 1.0 / FPS)
        A.place(ch, F(t) - 1, tuple(M.translation), math.degrees(self._rot_now(ch, t - 1.0 / FPS)))
        A.place(ch, F(t), tuple(loc), rot if rot is not None else math.degrees(self._rot_now(ch, t - 1.0 / FPS)))

    def turn(self, ch, t0, t1, rot, loc=None):
        """Ter plekke omdraaien (met twee stapjes) van t0 tot t1."""
        M = self._root_matrix(ch, t0)
        here = M.translation.copy()
        self.place(ch, t0, here, math.degrees(self._rot_now(ch, t0)))
        self.place(ch, t1, loc if loc is not None else here, rot)
        for k, side in enumerate(("L", "R")):
            tm = t0 + (t1 - t0) * (0.3 + 0.4 * k)
            A.foot(ch, F(tm - 0.08), side, (0, 0, 0))
            A.foot(ch, F(tm), side, (0, 0.02, 0.06))
            A.foot(ch, F(tm + 0.1), side, (0, 0, 0))

    def walk(self, ch, t0, t1, pts, stride=0.55, turn=True, arms=0.6, end_rot=None):
        """Lopen langs punten (wereld, z = vloer) van t0 tot t1, met voetstappen zonder glijden."""
        pts = [Vector(p) for p in pts]
        segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
        total = sum(segs) or 1e-6
        dur = t1 - t0
        speed = total / dur
        period = 2 * stride / max(speed, 1e-3)     # twee stappen per cyclus

        def at_dist(d):
            for i, L in enumerate(segs):
                if d <= L or i == len(segs) - 1:
                    w = min(1.0, d / L) if L > 0 else 1.0
                    return pts[i].lerp(pts[i + 1], w), (pts[i + 1] - pts[i])
                d -= L
            return pts[-1], pts[-1] - pts[-2]

        frames = list(range(F(t0), F(t1) + 1))
        locs, rots = [], []
        # houd de stand van vóór het lopen vast tot t0
        M0 = self._root_matrix(ch, t0)
        rot_prev = r0 = self._rot_now(ch, t0)
        A.place(ch, F(t0) - 1, tuple(M0.translation), math.degrees(rot_prev))
        for f in frames:
            t = (f - 1) / FPS
            # rustig op gang komen en afremmen
            u = (t - t0) / dur
            ease = smooth(0, 1, u) * 0.5 + u * 0.5
            p, d = at_dist(total * ease)
            locs.append(tuple(p))
            r = math.atan2(d.x, -d.y) if turn else r0
            while r - rot_prev > math.pi:
                r -= 2 * math.pi
            while r - rot_prev < -math.pi:
                r += 2 * math.pi
            rot_prev = r
            w = smooth(t0 - 0.05, t0 + 0.4, t)          # eerst de bocht in, niet in één frame
            rots.append((0.0, 0.0, r0 + (r - r0) * w))
        bake(ch.rig, "location", frames, locs, interp="BEZIER")
        bake(ch.rig, "rotation_euler", frames, rots, interp="BEZIER")
        for f in frames[::2] + [frames[-1]]:
            t = (f - 1) / FPS
            u = (t - t0) / dur
            env = smooth(0, 0.12, u) * (1 - smooth(0.88, 1.0, u))
            ph = ((t - t0) / period) % 1.0
            for side, off in (("L", 0.0), ("R", 0.5)):
                q = (ph + off) % 1.0
                if q < 0.5:                              # standbeen: voet glijdt mee terug
                    y = stride * (0.5 - 2 * q) * 0.5
                    z = 0.0
                else:                                    # zwaaibeen
                    w = (q - 0.5) * 2
                    y = stride * (-0.5 + w) * 0.5
                    z = math.sin(w * math.pi) * 0.09
                A.foot(ch, f, side, (0, y * env, z * env), (-20 * math.sin(q * 2 * math.pi) * env, 0, 0))
            sw = math.sin(ph * 2 * math.pi) * (arms or 0.0) * env
            if arms is not None:                         # arms=None: armen vrij voor beat(..., feet="keep")
                A.aim_arm(ch, f, "L", (0.18, 0.30 * sw, -0.95), (0.08, 0.15 + 0.35 * max(0, sw), -0.9))
                A.aim_arm(ch, f, "R", (0.18, -0.30 * sw, -0.95), (0.08, 0.15 + 0.35 * max(0, -sw), -0.9))
            bob = abs(math.cos(ph * 2 * math.pi)) * 0.025 * env
            A.crouch(ch, f, 0.02 + bob, 3 * env)
            ch.pb["spine"].rotation_euler = Euler((math.radians(3 * env), math.radians(4 * sw), 0))
            ch.pb["spine"].keyframe_insert("rotation_euler", frame=f)
        if end_rot is not None:
            r = math.radians(end_rot)
            while r - rot_prev > math.pi:
                r -= 2 * math.pi
            while r - rot_prev < -math.pi:
                r += 2 * math.pi
            ch.rig.rotation_euler = (0, 0, r)
            ch.rig.keyframe_insert("rotation_euler", frame=F(t1) + 6)
        ch.last = None

    # -- tijdlijn en geluid --------------------------------------------------
    def say(self, line_id, who=None, gap=0.3, at=None, gain=1.1):
        """Plaats een stemregel. who = sprekend personage (lipsync); None = verteller."""
        path = voice_file(line_id)
        dur = audio_len(path)
        t0 = at if at is not None else self.t + gap
        self.voice.append((os.path.relpath(path, AUDIO), t0))
        t1 = t0 + dur
        self.t = max(self.t, t1)
        if who is not None:
            A.lipsync(who, path, F(t0), gain=gain)
        return t0, t1

    def wait(self, s):
        self.t += s
        return self.t

    def sfx(self, name, t, vol=1.0, cut=None, keys=None, loop_to=None, duck=False):
        self.sounds.append(dict(file=name if "/" in name else "sfx/" + name, t=t, vol=vol, cut=cut, keys=keys,
                                loop_to=loop_to, duck=duck))

    def music(self, name, t0, t1, vol=0.35, fade_in=0.8, fade_out=1.2, duck=True, start=0.0):
        """Muziek (loopt door tot t1, met in- en uitfaden en ducking onder de stem)."""
        self.sounds.append(dict(file="muziek/" + name, t=t0, vol=vol, cut=(start, None), keys=None,
                                loop_to=t1, duck=duck, fade_in=fade_in, fade_out=fade_out))

    def ambience(self, name, t0, t1, vol=0.25):
        self.sounds.append(dict(file="sfx/" + name, t=t0, vol=vol, cut=None, keys=None, loop_to=t1, duck=True,
                                fade_in=0.5, fade_out=0.8))

    def text(self, body, t0, t1, loc=(0.035, 0.94), size=92, color=WHITE, anchor=("LEFT", "TOP"), pop=True):
        self.texts.append(dict(body=body, t0=t0, t1=t1, loc=loc, size=size, color=color, anchor=anchor, pop=pop))

    def hud(self, day, power, t0=0.3, t1=None, color=GOLD, tick=True):
        """De vaste teller linksboven: DAY N en de kracht."""
        self.texts.append(dict(body=f"DAY {day}", t0=t0, t1=t1, loc=(0.035, 0.94), size=92, color=WHITE,
                               anchor=("LEFT", "TOP"), pop=True, hud=True))
        if power:
            self.texts.append(dict(body=power, t0=t0 + 0.12, t1=t1, loc=(0.035, 0.845), size=52, color=color,
                                   anchor=("LEFT", "TOP"), pop=True, hud=True))
        if tick:
            self.sfx("sfx_hud_tik", t0, 0.6)

    def gauge(self, body, t0, t1, color=GOLD, size=64):
        """Extra teller onder de HUD (EGGS BROKEN, km/h, kg...)."""
        self.texts.append(dict(body=body, t0=t0, t1=t1, loc=(0.035, 0.76), size=size, color=color,
                               anchor=("LEFT", "TOP"), pop=True))

    def real(self, t0, t1):
        """'THIS PART IS REAL' rechtsonder, zolang de uitleg loopt."""
        self.texts.append(dict(body="THIS PART IS REAL", t0=t0, t1=t1, loc=(0.965, 0.07), size=44, color=CYAN,
                               anchor=("RIGHT", "BOTTOM"), pop=True))

    def card(self, body, t0, t1, size=110, dim=0.65, color=WHITE, sub=None, bg=None, fin=5, fout=5):
        """Titelkaart midden in beeld, met verdonkerde achtergrond. bg = kleur van het vlak (wit voor een flits),
        fin/fout = in- en uitfaden in frames. Lege body: alleen het vlak."""
        self.cards.append(dict(body=body, t0=t0, t1=t1, size=size, dim=dim, color=color, sub=sub, bg=bg, fin=fin, fout=fout))

    # -- camera's --------------------------------------------------------------
    def cam(self, t0, a, b=None, fn=None, dof=None, shake=None, ease=True, name=None, handheld=0.25):
        """Shot vanaf t0 tot het volgende shot. a/b = (positie, doel, lens), b = eindstand (camerabeweging).
        Positie/doel mogen ook functies van t zijn. handheld = lichte cameraruis in graden."""
        self.cams.append(dict(t0=t0, a=a, b=b, fn=fn, dof=dof, shake=shake, ease=ease,
                              name=name or f"{self.code.upper()}_shot_{len(self.cams) + 1:02d}", hh=handheld))

    SIZES = dict(ecu=0.34, cu=0.66, mcu=0.98, med=1.4, full=2.4, wide=4.2, xwide=8.0)

    def frame_of(self, ch, t=0.0):
        """(positie, voorwaarts, links) van een figuur op tijd t."""
        M = self._root_matrix(ch, t)
        R3 = M.to_3x3().normalized()
        return M.translation.copy(), R3 @ Vector((0, -1, 0)), R3 @ Vector((1, 0, 0))

    def headpos(self, ch, t):
        """Echte wereldpositie van het midden van het hoofd op tijd t (met houding)."""
        hb = self.bone_world(ch, "head", t, tail=False)
        return hb + Vector((0, 0, (ch.J["head_c"].z - ch.J["neck_top"].z) * ch.rig.scale.z))

    def shot(self, ch, t=0.0, size="med", az=25.0, lens=35, h=0.0, lr=0.0, up=0.0, dist=None):
        """Kader een figuur: size = ecu/cu/mcu/med/full/wide/xwide of framehoogte in meters,
        az = graden vanaf zijn neus (+ = naar zijn linkerkant), h = camera hoger/lager dan het doel,
        lr = doel opzij (m, + = zijn links; zet hem dan rechts in beeld), up = doel omhoog."""
        pos, fwd, left = self.frame_of(ch, t)
        sc = ch.rig.scale.z
        fh = self.SIZES[size] if isinstance(size, str) else size
        # echte hoofdpositie (zitten, bukken, voorover leunen)
        hc = self.headpos(ch, t)
        top = hc.z + ch.J["head_r"].z * sc
        if size == "ecu":
            tz = hc.z + 0.03
        else:
            tz = top - fh * 0.5 + fh * 0.07
        base = Vector((hc.x, hc.y, pos.z)) if fh < 1.5 else pos
        tgt = Vector((base.x, base.y, max(tz, pos.z + fh * 0.42) + up)) + left * lr
        d = dist or fh * lens / 20.25
        a = math.radians(az)
        cam = tgt + (fwd * math.cos(a) + left * math.sin(a)) * d + Vector((0, 0, h))
        return (tuple(cam), tuple(tgt), lens)

    def ots(self, a, b, t=0.0, lens=35, side=1, back=0.75, out=0.32, rise=0.12, tgt_up=0.0):
        """Over-de-schouder: achter figuur a, kijkend naar het gezicht van b. side=1: over zijn rechterschouder."""
        ha = self.head(a, t)
        hb = self.head(b, t) + Vector((0, 0, tgt_up))
        d = hb - ha
        d.z = 0
        d.normalize()
        right = d.cross(Vector((0, 0, 1)))
        cam = ha - d * back + right * out * side + Vector((0, 0, rise))
        return (tuple(cam), tuple(hb), lens)

    def _cam_eval(self, c, t, t1):
        if c["fn"]:
            return c["fn"](t)
        w = smooth(c["t0"], t1, t) if c["ease"] else max(0.0, min(1.0, (t - c["t0"]) / max(1e-3, t1 - c["t0"])))

        def ev(x):
            return Vector(x(t)) if callable(x) else Vector(x)
        a = c["a"]
        b = c["b"] or a
        loc = ev(a[0]).lerp(ev(b[0]), w)
        tgt = ev(a[1]).lerp(ev(b[1]), w)
        return loc, tgt, lerp(a[2], b[2], w)

    def _build_cams(self):
        T.use_collection(T.collection("Camera's " + self.code))
        cams = sorted(self.cams, key=lambda c: c["t0"])
        self.shots = []
        for k, c in enumerate(cams):
            t0 = c["t0"]
            t1 = cams[k + 1]["t0"] if k + 1 < len(cams) else self.length
            cd = bpy.data.cameras.new(c["name"])
            cd.clip_start, cd.clip_end = c.get("clip") or getattr(self, "clip", (0.02, 6000))
            cd.sensor_width = 36
            cam = bpy.data.objects.new(c["name"], cd)
            T._link(cam)
            frames = list(range(max(1, F(t0) - 1), F(t1) + 2))
            mats, lens_rows, focus_rows = [], [], []
            seed = k * 3.3 + 1.7
            for f in frames:
                t = (f - 1) / FPS
                loc, tgt, lens = self._cam_eval(c, max(t0, min(t1, t)), t1)
                q = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y")
                amp = math.radians((c["shake"](t) if c["shake"] else 0.0) + c["hh"])
                fr = 9 if c["shake"] else 0.6
                e = (noise.noise(Vector((t * fr, seed, 0))) * amp, noise.noise(Vector((t * fr, seed, 5))) * amp,
                     noise.noise(Vector((t * fr, seed, 9))) * amp * 0.5)
                q = q @ Quaternion((1, 0, 0), e[0]) @ Quaternion((0, 1, 0), e[1]) @ Quaternion((0, 0, 1), e[2])
                M = q.to_matrix().to_4x4()
                M.translation = Vector(loc)
                mats.append(M)
                lens_rows.append((lens,))
                focus_rows.append(((Vector(tgt) - Vector(loc)).length,))
            bake_matrices(cam, frames, mats)
            bake(cd, "lens", frames, lens_rows)
            if c["dof"]:
                cd.dof.use_dof = True
                cd.dof.aperture_fstop = c["dof"]
                bake(cd.dof, "focus_distance", frames, focus_rows)
            m = self.sc.timeline_markers.new(c["name"], frame=F(t0))
            m.camera = cam
            self.shots.append((t0, t1, cam))
        self.sc.camera = self.shots[0][2]

    # -- effecten --------------------------------------------------------------
    def _fxname(self, base):
        self.fx_n += 1
        return f"{base}_{self.fx_n:02d}"

    def flash(self, loc, t, size=0.3, color=(1.0, 0.9, 0.6), strength=6):
        o = T.sphere(self._fxname("Flits"), tuple(loc), 1.0, self.mat("flits", color, strength), seg=16, ol=0)
        for tt, s in ((t - 1 / FPS, 0.001), (t, size), (t + 3 / FPS, size * 0.5), (t + 7 / FPS, 0.001)):
            key(o, tt, scale=s)
        return o

    def ring(self, loc, t, r0=0.3, r1=6.0, dur=0.6, color=(1, 1, 1), strength=2.5, thick=0.06, rot=(0, 0, 0)):
        """Uitdijende schokgolf-ring."""
        o = T.torus(self._fxname("Schokgolf"), tuple(loc), 1.0, thick, self.mat("schokgolf", color, strength),
                    rot=rot, seg=64, seg2=8, ol=0)
        key(o, t - 1 / FPS, scale=0.001)
        key(o, t, scale=r0)
        key(o, t + dur * 0.85, scale=r1 * 0.95)
        key(o, t + dur, scale=0.001)
        return o

    def debris(self, origin, t, n=20, size=(0.03, 0.08), color=(0.6, 0.6, 0.6), speed=(2.0, 5.0), up=0.6,
               direction=None, spread=1.0, life=1.4, floor=None, shape="box", mat=None, spin=12, name="Brokstuk"):
        """Rondvliegende stukjes (ballistisch, zonder simulatie). direction = hoofdrichting."""
        rnd = random.Random(self.fx_n * 7 + n)
        m = mat or self.mat("brok", color)
        floor = (origin[2] - 0.02) if floor is None else floor
        dirv = Vector(direction).normalized() if direction else None
        objs = []
        frames = list(range(F(t) - 1, F(t + life) + 1))
        for i in range(n):
            s = rnd.uniform(*size)
            nm = self._fxname(name)
            if shape == "box":
                o = T.box(nm, (0, 0, 0), (s, s * rnd.uniform(0.5, 1.4), s * rnd.uniform(0.4, 1.0)), m, base=False, bevel=0, ol=0.004)
            else:
                o = T.sphere(nm, (0, 0, 0), s, m, seg=8, ol=0.004)
            v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 1)) * up)).normalized()
            if dirv is not None:
                v = (dirv + v * spread).normalized()
            v *= rnd.uniform(*speed)
            w = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * spin
            p0 = Vector(origin) + Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)))
            locs, rots, scs = [], [], []
            landed = None
            for f in frames:
                tt = max(0.0, (f - 1) / FPS - t)
                p = p0 + v * tt + Vector((0, 0, -4.9 * tt * tt))
                if p.z < floor + s * 0.5:
                    if landed is None:
                        landed = (p.copy(), tt)
                    p = Vector((landed[0].x, landed[0].y, floor + s * 0.5))
                    r = w * landed[1]
                else:
                    r = w * tt
                locs.append(tuple(p))
                rots.append(tuple(r))
                scs.append((0.001,) * 3 if (f - 1) / FPS < t else (1.0,) * 3)
            o.rotation_mode = "XYZ"
            bake(o, "location", frames, locs)
            bake(o, "rotation_euler", frames, rots)
            bake(o, "scale", frames, scs, interp="CONSTANT")
            objs.append(o)
        return objs

    def puff(self, loc, t, n=8, r=(0.2, 0.5), grow=2.5, dur=1.2, color=(0.85, 0.82, 0.75), rise=0.5, spread=0.6):
        """Stofwolk: bollen die opzwellen en weer krimpen."""
        rnd = random.Random(self.fx_n + 31)
        m = self.mat("stof", color)
        objs = []
        for i in range(n):
            rr = rnd.uniform(*r)
            o = T.sphere(self._fxname("Stof"), (0, 0, 0), 1.0, m, seg=12, ol=0.0)
            off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 0.5))) * spread
            d0 = t + rnd.uniform(0, 0.12)
            key(o, d0 - 1 / FPS, loc=Vector(loc) + off * 0.3, scale=0.001)
            key(o, d0 + dur * 0.35, loc=Vector(loc) + off + Vector((0, 0, rise * 0.5)), scale=rr * grow * 0.8)
            key(o, d0 + dur, loc=Vector(loc) + off * 1.3 + Vector((0, 0, rise)), scale=0.001)
            objs.append(o)
        return objs

    def shatter(self, center, size, t, n=40, normal=(0, -1, 0), speed=(1.5, 4.0), floor=0.0):
        """Glas dat springt: lichtblauwe scherven vanaf een vlak."""
        rnd = random.Random(self.fx_n + 77)
        glas = self.mat("glasscherf", (0.75, 0.9, 1.0), 1.2)
        nrm = Vector(normal).normalized()
        side = nrm.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = Vector((1, 0, 0))
        side.normalize()
        objs = []
        for i in range(n):
            p = Vector(center) + side * rnd.uniform(-size[0] / 2, size[0] / 2) + Vector((0, 0, rnd.uniform(-size[1] / 2, size[1] / 2)))
            objs += self.debris(p, t + rnd.uniform(0, 0.05), n=1, size=(0.03, 0.09), mat=glas, speed=speed,
                                direction=nrm, spread=0.6, up=0.3, floor=floor, life=1.6, name="Scherf")
        return objs

    # -- afronden ----------------------------------------------------------------
    def pre_finish(self):
        """Haak voor subklassen: vlak voor het bouwen van de camera's."""

    def post_cams(self):
        """Haak voor subklassen: na het bouwen van de camera's (self.shots bestaat dan)."""

    def finish(self, length=None, tail=0.8, picture_end=None, title=None):
        self.length = length or (self.t + tail)
        sc = self.sc
        sc.frame_start, sc.frame_end = 1, F(self.length)
        self.pre_finish()
        for i, ch in enumerate(self.cast):
            A.blinks(ch, 1, F(self.length), seed=i * 3 + 1)
            A.alive(ch, 1, F(self.length), energy=getattr(ch, "energy", 1.0), seed=i * 5 + 2)
        self._build_cams()
        self.post_cams()
        spec = dict(code=self.code, length=self.length, picture_end=picture_end or self.length,
                    voice=self.voice, sounds=self.sounds, texts=self.texts, cards=self.cards, title=title, fps=OUT_FPS)
        os.makedirs(self.out, exist_ok=True)
        with open(os.path.join(self.out, "montage.json"), "w") as fh:
            json.dump(spec, fh, indent=1)
        sc.render.resolution_percentage = self.args.pct
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(self.out, "frames", "")
        if hasattr(sc, "eevee"):
            try:
                sc.eevee.taa_render_samples = self.args.samples
            except Exception:
                pass
        sc.frame_set(1)
        if OUT_FPS != FPS:
            sc.render.fps = OUT_FPS
            sc.render.frame_map_old, sc.render.frame_map_new = FPS, OUT_FPS
            sc.frame_start = 3
            sc.frame_end = int(math.ceil(self.length * OUT_FPS + 2.5))
            # (cameramarkers blijven in 24-fps-frames: Blender vergelijkt ze met de opgerekte tijd)
            sc.frame_set(3)
        if not self.args.nosave:
            blend = os.path.join(self.out, self.code + ".blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
            print("OPGESLAGEN", blend, "lengte", round(self.length, 2), "s")
        if self.args.stills:
            if self.args.stills == "auto":
                times = [round((a + b) / 2, 2) for a, b, _ in self.shots]
            else:
                times = [float(x) for x in self.args.stills.split(",")]
            for t in times:
                f = F(t) if OUT_FPS == FPS else int(round(t * OUT_FPS + 2.5))
                sc.frame_set(f)
                for t0, t1, cam in self.shots:
                    if t0 <= t < t1:
                        sc.camera = cam
                print("STILL", t, "frame", f, "camera", sc.camera.name)
                sc.render.filepath = os.path.join(self.out, "stills", f"{self.code}_t{t:05.1f}.png")
                bpy.ops.render.render(write_still=True)
            sc.render.filepath = os.path.join(self.out, "frames", "")
        if self.args.render:
            bpy.ops.render.render(animation=True)
            print("KLAAR: frames in", os.path.join(self.out, "frames"))


# ---------------------------------------------------------------------------
# Kleine rekwisieten (toon-stijl)
# ---------------------------------------------------------------------------
def prop_mug(S, name="Mok", loc=(0, 0, 0), handle=True, cracked=False, scale=1.0):
    """De mok 'WORLD'S OKAYEST MOM' (wit met rode tekst). Oorsprong = onderkant midden."""
    white = S.mat("mok_wit", (0.95, 0.94, 0.9))
    red = S.mat("mok_rood", (0.85, 0.15, 0.15))
    body = T.cyl(name, (0, 0, 0), 0.042, 0.095, white, seg=24, ol=0.004)
    inner = T.cyl(name + "_thee", (0, 0, 0.07), 0.037, 0.005, S.mat("thee", (0.55, 0.3, 0.12)), seg=20, ol=0)
    inner.parent = body
    txt = T.text(name + "_tekst", "WORLD'S\nOKAYEST\nMOM", (0, -0.0425, 0.03), 0.014, red, rot=(90, 0, 0), extrude=0.0)
    txt.parent = body
    if handle:
        h = T.torus(name + "_oor", (0.048, 0, 0.048), 0.022, 0.006, white, rot=(90, 0, 0), seg=20, seg2=8, ol=0.003)
        h.parent = body
    if cracked:
        crack = T.tube(name + "_barst", [(-0.02, -0.0428, 0.085), (-0.005, -0.0428, 0.06), (-0.012, -0.0428, 0.045),
                                         (0.004, -0.0428, 0.03), (-0.002, -0.0428, 0.008)], 0.0012,
                       S.mat("barst", (0.15, 0.12, 0.1)))
        crack.parent = body
    body.location = loc
    body.scale = (scale,) * 3
    return body


def prop_phone(S, name="Telefoon", loc=(0, 0, 0), screen=(0.35, 0.65, 1.0)):
    o = T.box(name, (0, 0, 0), (0.07, 0.008, 0.145), S.mat("telefoon", (0.1, 0.1, 0.12)), base=False, bevel=0.006, ol=0.003)
    s = T.box(name + "_scherm", (0, -0.0045, 0), (0.062, 0.001, 0.132), S.mat("scherm_" + name, screen, 2.0), base=False, bevel=0, ol=0)
    s.parent = o
    o.location = loc
    return o


def attach(obj, ch, bone="hand.R", loc=(0, 0, 0), rot=(0, 0, 0)):
    """Hang een object aan een bot (volgt de hand). loc/rot relatief aan het botuiteinde."""
    obj.parent = ch.rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = loc
    obj.rotation_euler = Euler([math.radians(a) for a in rot])


def grab(S, obj, ch, t, bone="hand.R", loc=(0, 0, 0), rot=(0, 0, 0), release=None, mode="full", target=None, offset=None):
    """Object ligt los tot t, zit daarna in de hand (tot release). mode="loc": alleen de positie volgen
    (het object blijft rechtop). target = bestaand leeg object om te volgen; offset = wereldverschuiving."""
    if target is None:
        emp = bpy.data.objects.new(S._fxname("Greep"), None)
        T._link(emp)
        attach(emp, ch, bone, loc, rot)
    else:
        emp = target
    if offset is not None:
        e2 = bpy.data.objects.new(S._fxname("Greep_ofs"), None)
        T._link(e2)
        cl = e2.constraints.new("COPY_LOCATION")
        cl.target = emp
        cl.use_offset = True
        e2.location = Vector(offset)
        emp = e2
    c = obj.constraints.new("COPY_TRANSFORMS" if mode == "full" else "COPY_LOCATION")
    c.target = emp
    c.influence = 0.0
    c.keyframe_insert("influence", frame=F(t) - 1)
    c.influence = 1.0
    c.keyframe_insert("influence", frame=F(t))
    if release is not None:
        c.keyframe_insert("influence", frame=F(release) - 1)
        c.influence = 0.0
        c.keyframe_insert("influence", frame=F(release))
    for fc in A._fcurves(obj):
        if "influence" in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    return emp


# Veelgebruikte armhoudingen (lichaamsrichtingen: x = zijn linkerkant, y = voor, z = op)
def arm(side, upper, fore, hand=None):
    return lambda ch, f: A.aim_arm(ch, f, side, upper, fore, hand)


def arms(*fns):
    def go(ch, f):
        for fn in fns:
            fn(ch, f)
    return go


HAND_OUT_R = arm("R", (0.15, 0.85, -0.45), (0.0, 1.0, 0.05))            # hand vooruit (aanpakken)
HAND_OUT_L = arm("L", (0.15, 0.85, -0.45), (0.0, 1.0, 0.05))
LOOK_HANDS = arms(arm("L", (0.25, 0.55, -0.75), (-0.25, 0.75, 0.55)), arm("R", (0.25, 0.55, -0.75), (-0.25, 0.75, 0.55)))
HOLD_FRONT_R = arm("R", (0.12, 0.45, -0.85), (-0.15, 0.9, 0.35))        # iets voor de borst vasthouden
HOLD_FRONT_L = arm("L", (0.12, 0.45, -0.85), (-0.15, 0.9, 0.35))
WAVE_SMALL_R = arm("R", (0.35, 0.25, -0.85), (0.25, 0.2, 0.95))         # het rare kleine zwaaitje
WAVE_SMALL_R2 = arm("R", (0.35, 0.25, -0.85), (0.55, 0.2, 0.8))
PHONE_EAR_R = arm("R", (0.30, 0.15, -0.90), (-0.55, 0.15, 0.82))
CLAP_A = arms(arm("L", (0.2, 0.9, -0.3), (-0.4, 0.9, 0.1)), arm("R", (0.2, 0.9, -0.3), (-0.4, 0.9, 0.1)))
CLAP_B = arms(arm("L", (0.3, 0.8, -0.3), (0.3, 0.9, 0.1)), arm("R", (0.3, 0.8, -0.3), (0.3, 0.9, 0.1)))


# ---------------------------------------------------------------------------
# Zitten, scharnieren en nog wat rekwisieten
# ---------------------------------------------------------------------------
def sit(ch, seat_top=0.49, lean=-4.0, spread=0.07):
    """Zithouding voor beat(): geeft (spec, root_z). Zet de wortel van het figuur boven het midden van de
    zitting op hoogte root_z (> 0 voor kinderen, hun voeten bungelen dan)."""
    P_ = ch.J["pelvis"].z
    ank = ch.J["ankle.L"].z
    L = P_ - ank
    want = seat_top + 0.07
    if P_ - 0.03 > want:
        root_z, drop = 0.0, P_ - want
        vert = P_ - drop - ank
        fwd = math.sqrt(max(0.0, (0.97 * L) ** 2 - vert ** 2))
        feet = ((spread * 0.3, fwd, 0.0), (-spread * 0.3, fwd, 0.0))
    else:
        drop = 0.03
        root_z = want - (P_ - drop)
        feet = ((spread * 0.3, 0.16, 0.06), (-spread * 0.3, 0.12, 0.03))
    return dict(crouch=(drop, lean), feet=feet), root_z


def hinge(obj, pivot, children=()):
    """Maak een scharnier (lege ouder op pivot) voor deuren/deksels. Draai daarna de teruggegeven ouder."""
    e = bpy.data.objects.new(obj.name + "_scharnier", None)
    T._link(e)
    e.location = Vector(pivot)
    inv = Matrix.Translation(Vector(pivot)).inverted()
    for o in (obj,) + tuple(children):
        o.parent = e
        o.matrix_parent_inverse = inv
    return e


def prop_tablet(S, name="Tablet", loc=(0, 0, 0), screen=(0.85, 0.9, 1.0)):
    o = T.box(name, (0, 0, 0), (0.24, 0.012, 0.17), S.mat("tablet", (0.12, 0.12, 0.14)), base=False, bevel=0.008, ol=0.003)
    s = T.box(name + "_scherm", (0, -0.0065, 0), (0.22, 0.001, 0.15), S.mat("scherm_" + name, screen, 1.5), base=False, bevel=0, ol=0)
    s.parent = o
    for k in range(4):
        r = T.box(f"{name}_regel{k}", (-0.02, -0.0075, 0.05 - k * 0.03), (0.16 - (k % 2) * 0.05, 0.001, 0.012),
                  S.mat("tablet_tekst", (0.3, 0.32, 0.4)), base=False, bevel=0, ol=0)
        r.parent = o
    o.location = loc
    return o


def prop_jar(S, name="Augurkenpot", loc=(0, 0, 0)):
    """Augurkenpot met deksel. Geeft (pot, deksel_met_rand) terug; de rand is het bovenste stuk glas."""
    glas = T.glass("pot_glas", (0.75, 0.9, 0.75), alpha=0.45)
    jar = T.cyl(name, (0, 0, 0), 0.055, 0.13, glas, seg=24, ol=0.003)
    pick = S.mat("augurk", (0.35, 0.55, 0.15))
    for k in range(5):
        a = k * 1.256
        o = T.cyl(f"{name}_augurk{k}", (0.025 * math.cos(a), 0.025 * math.sin(a), 0.01), 0.014, 0.11, pick, seg=8, ol=0)
        o.parent = jar
    T.cyl(name + "_pekel", (0, 0, 0.005), 0.052, 0.11, T.glass("pekel", (0.85, 0.9, 0.5), alpha=0.35), seg=24, ol=0).parent = jar
    top = T.cyl(name + "_deksel", (0, 0, 0), 0.058, 0.022, S.mat("deksel", (0.85, 0.2, 0.15)), seg=24, ol=0.003)
    rim = T.cyl(name + "_rand", (0, 0, -0.025), 0.055, 0.025, glas, seg=24, ol=0.003)
    rim.parent = top
    lab = T.cyl(name + "_etiket", (0, 0, 0.03), 0.0565, 0.05, S.mat("etiket", (0.98, 0.9, 0.55)), seg=24, ol=0, cap=False)
    lab.parent = jar
    jar.location = Vector(loc)
    top.location = Vector(loc) + Vector((0, 0, 0.155))
    return jar, top


def prop_egg(S, name="Ei", loc=(0, 0, 0)):
    return T.sphere(name, tuple(loc), 0.024, S.mat("ei", (0.98, 0.93, 0.85)), scale=(1, 1, 1.3), seg=14, ol=0.002)


def prop_bike(S, ch, name="Fiets", color=(0.85, 0.15, 0.15)):
    """Fiets op maat van de figuren, vast aan de wortel van ch (rijdt mee). Geeft (fiets, crank) terug.
    Lokaal: figuur kijkt naar -y; trapas op (0, 0, 0.25), wielen r 0.27."""
    fr = S.mat("fietsframe_" + name, color)
    blk = P.m("zwart")
    met = P.m("metaal")
    parts = []
    for k, y in enumerate((-0.45, 0.40)):
        parts.append(T.torus(f"{name}_band{k}", (0, y, 0.27), 0.25, 0.025, blk, rot=(0, 90, 0), seg=32, seg2=8, ol=0))
        parts.append(T.torus(f"{name}_velg{k}", (0, y, 0.27), 0.22, 0.008, met, rot=(0, 90, 0), seg=32, seg2=6, ol=0))
        parts.append(T.cyl(f"{name}_naaf{k}", (-0.04, y, 0.27), 0.025, 0.08, met, rot=(0, 90, 0), seg=10, ol=0))
    pts = [((0, 0.40, 0.27), (0, 0.0, 0.25)), ((0, 0.0, 0.25), (0, 0.10, 0.60)), ((0, 0.10, 0.60), (0, 0.40, 0.27)),
           ((0, 0.10, 0.56), (0, -0.33, 0.66)), ((0, 0.0, 0.25), (0, -0.33, 0.62)), ((0, -0.33, 0.62), (0, -0.45, 0.27)),
           ((0, -0.33, 0.62), (0, -0.36, 0.80))]
    for k, (a, b) in enumerate(pts):
        parts.append(T.to_mesh(T.tube(f"{name}_buis{k}", [a, b], 0.018, fr)))
    parts.append(T.to_mesh(T.tube(f"{name}_stuur", [(-0.22, -0.30, 0.82), (-0.1, -0.36, 0.80), (0.1, -0.36, 0.80), (0.22, -0.30, 0.82)], 0.014, met)))
    for x in (-0.22, 0.22):
        parts.append(T.cyl(f"{name}_handvat{x}", (x - 0.04, -0.30, 0.82), 0.02, 0.08, blk, rot=(0, 90, 0), seg=8, ol=0))
    parts.append(T.box(f"{name}_zadel", (0, 0.12, 0.60), (0.1, 0.22, 0.05), blk, bevel=0.02, ol=0))
    parts.append(T.box(f"{name}_spatbord", (0, 0.40, 0.53), (0.08, 0.3, 0.02), fr, bevel=0.01, ol=0))
    bike = T.merge(name, parts, ol=0.006)
    crank = T.merge(name + "_crank", [T.box(f"{name}_crankarm", (0, 0, -0.13), (0.03, 0.03, 0.26), met, base=False, bevel=0.005, ol=0),
                                      T.box(f"{name}_pedaal1", (0.07, 0, -0.13), (0.09, 0.05, 0.02), blk, base=False, bevel=0, ol=0),
                                      T.box(f"{name}_pedaal2", (-0.07, 0, 0.13), (0.09, 0.05, 0.02), blk, base=False, bevel=0, ol=0),
                                      T.cyl(f"{name}_tandwiel", (0.04, 0, 0), 0.08, 0.01, met, rot=(0, 90, 0), seg=20, ol=0)], ol=0.004)
    for o in (bike, crank):
        o.parent = ch.rig
        o.matrix_parent_inverse = Matrix.Identity(4)
    bike.location = (0, 0, 0)
    crank.location = (0, 0, 0.25)
    return bike, crank


def ride(S, ch, crank, t0, t1, cadence=2.2, lean=24, phase=0.0):
    """Fietsen: zit op het zadel, handen aan het stuur, voeten op de trappers die rondgaan."""
    for f in range(F(t0), F(t1) + 1, 2):
        t = (f - 1) / FPS
        ph = phase + (t - t0) * cadence * 2 * math.pi
        A.crouch(ch, f, 0.07, lean)
        for side, off in (("R", 0.0), ("L", math.pi)):
            a = ph + off
            A.foot(ch, f, side, (0, 0.13 * math.cos(a), 0.15 + 0.13 * math.sin(a)), (-15 * math.sin(a), 0, 0))
        crank.rotation_euler = (ph, 0, 0)
        crank.keyframe_insert("rotation_euler", frame=f)
    M = S._root_matrix(ch, t0)
    for side, x in (("L", 0.2), ("R", -0.2)):
        for t in (t0, t1):
            M = S._root_matrix(ch, t)
            S.reach(ch, t, side, M @ Vector((x, -0.30, 0.83)))
    for fc in A._fcurves(crank):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def prop_bus(S, name="Bus", color=(0.95, 0.85, 0.15)):
    """Stadsbus (11 m), rijdt langs +x. Oorsprong onder het midden."""
    body = S.mat("bus_" + name, color)
    glas = S.mat("busruit", (0.15, 0.22, 0.3))
    p = [T.box(name + "_romp", (0, 0, 0.35), (11.0, 2.5, 2.7), body, bevel=0.15, ol=0),
         T.box(name + "_ramen", (0, 0, 1.45), (10.4, 2.54, 1.0), glas, bevel=0.05, ol=0),
         T.box(name + "_voorruit", (5.47, 0, 1.0), (0.1, 2.3, 1.7), glas, bevel=0.04, ol=0),
         T.box(name + "_streep", (0, 0, 0.95), (11.02, 2.52, 0.12), S.mat("busstreep", (0.15, 0.35, 0.8)), bevel=0, ol=0),
         T.box(name + "_bord", (5.52, 0, 2.65), (0.04, 1.6, 0.3), S.mat("busbord", (1.0, 0.65, 0.15), 2.0), bevel=0, ol=0)]
    for i, (x, y) in enumerate([(3.6, 1.15), (-3.4, 1.15), (3.6, -1.15), (-3.4, -1.15)]):
        p.append(T.cyl(f"{name}_wiel{i}", (x, y - 0.12 * (1 if y > 0 else -1), 0.5), 0.5, 0.3, P.m("zwart"), rot=(90, 0, 0), seg=18, ol=0))
    for y in (0.85, -0.85):
        p.append(T.sphere(f"{name}_lamp{y}", (5.5, y, 0.6), 0.14, T.toon("koplamp", (1, 0.97, 0.85)), scale=(0.4, 1, 0.7), seg=10, ol=0))
    return T.merge(name, p, ol=0.02)
