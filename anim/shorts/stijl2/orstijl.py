"""Originele shorts OR1-OR7 in de NIEUWE animatiestijl (zonnige speelgoed/Pixar-look, animator/scenes/scene_lib.py).

Wat gelijk blijft aan de eerste versie: stem (v2.5-clips), ondertitels, titels, tellers, geluid en eindkaart. Die staan
vast in anim/shorts/stijl2/tekst/orN.json (de montage.json van de eerste versie) en worden ongewijzigd naar
out/orN/montage.json gekopieerd. Alleen het beeld is nieuw: Bram uit het cast-bestand, Cycles + AgX Punchy, bloom, DOF.

Eén script per short, één scène (locaties ver uit elkaar), 30 fps (beeld n = tijd (n-1)/30), 1080x1920.

    blender -b --disable-autoexec <glans_hoofdpersonage_volledig.blend> -P anim/shorts/stijl2/or1_spiegel.py -- [--render]
    python3 anim/shorts/stijl2/or1_spiegel.py -- --stills auto --pct 25          (container: opent het cast-bestand zelf)
    blender -b -P anim/edit/montage.py -- or1
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAST_PATHS = [os.environ.get("WHATIF_CAST", ""),
              os.path.join(REPO, "cast", "glans", "glans_hoofdpersonage_volledig.blend"),
              "/mnt/project-files/cast/glans/glans_hoofdpersonage_volledig.blend"]
if "hoofdpersonage" not in bpy.data.collections:          # python3 + bpy-module: cast-bestand zelf openen
    bpy.ops.wm.open_mainfile(filepath=next(p for p in CAST_PATHS if p and os.path.exists(p)))
sys.path.insert(0, os.path.join(REPO, "animator", "scenes"))
import scene_lib as L  # noqa: E402  (pas NA het openen importeren: scene_lib bewaart bpy.data.objects)
from scene_lib import R, curve, key, material, prim, smoothstep, srgb  # noqa: E402,F401

FPS = 30
W, H = 1080, 1920
AUDIO = os.path.join(REPO, "assets", "audio")


def FR(t):
    """Beeldnummer (1 = t 0) bij 30 fps."""
    return int(round(t * FPS)) + 1


def TT(f):
    return (f - 1) / FPS


def V(*a):
    return Vector(a[0] if len(a) == 1 else a)


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    o = dict(render=False, stills=None, pct=None, samples=None, frames=None)
    i = 0
    while i < len(a):
        k = a[i]
        if k == "--render":
            o["render"] = True
        elif k in ("--stills", "--pct", "--samples", "--frames") and i + 1 < len(a):
            o[k[2:]] = a[i + 1]
            i += 1
        i += 1
    return o


def audio_len(path):
    import aud
    s = aud.Sound(path)
    try:
        return s.length / s.specs[0]
    except Exception:
        import numpy as np
        return len(np.asarray(s.data())) / s.specs[0]


# ------------------------------------------------------------------------------------------- emoties (uitgebreid)
#            wenkbrauw dz, kanteling, Lach, Boos, Schreeuw, E (o-mond), ooggrootte
EMO = {
    "neutraal": (0.000, 0, 0.35, 0.0, 0.0, 0.0, 1.00),
    "blij": (0.010, -4, 0.95, 0.0, 0.0, 0.0, 0.88),
    "heel_blij": (0.020, -6, 1.00, 0.0, 0.0, 0.0, 0.82),
    "grijns": (0.006, 8, 1.00, 0.0, 0.0, 0.0, 0.85),
    "trots": (0.006, 4, 0.80, 0.0, 0.0, 0.0, 0.90),
    "verbaasd": (0.022, -10, 0.00, 0.0, 0.0, 0.55, 1.15),
    "nieuwsgierig": (0.012, -6, 0.20, 0.0, 0.0, 0.0, 1.05),
    "bezorgd": (0.010, -15, 0.00, 0.3, 0.0, 0.0, 1.00),
    "nerveus": (0.014, -14, 0.10, 0.25, 0.0, 0.15, 1.08),
    "bang": (0.024, -18, 0.00, 0.45, 0.0, 0.25, 1.22),
    "geschrokken": (0.028, -14, 0.00, 0.2, 0.0, 0.85, 1.28),
    "boos": (-0.005, 16, 0.00, 1.0, 0.0, 0.0, 1.00),
    "leeg": (0.000, 0, 0.00, 0.0, 0.0, 0.0, 1.00),
}

# ------------------------------------------------------------------------------------------- armhoudingen
# per kant s (+1 = rechts in rustpose / +x): (schouder xyz, elleboog xyz) in graden; Y en Z worden met -s vermenigvuldigd
ARMS = {
    "rust": ((2, 4, 0), (-10, 0, 0)),
    "los": ((-6, 10, 0), (-22, 0, 0)),
    "omhoog": ((0, 108, 0), (0, 18, 0)),
    "juichen": ((-10, 128, 0), (0, 12, 0)),
    "hoofd": ((-10, 140, 0), (0, 125, 0)),          # handen tegen de wangen (schrik)
    "gezicht": ((-80, 18, 20), (-70, 0, 0)),         # handen voor je gezicht, je kijkt ernaar
    "handen_voor": ((-58, 14, 8), (-62, 0, 0)),
    "tasten": ((-78, 18, -6), (-14, 0, 0)),
    "duwen": ((-84, 8, 0), (-8, 0, 0)),
    "schrik": ((-28, 46, 0), (-70, 0, 0)),
    "afweer": ((-55, 30, 18), (-100, 0, 0)),
    "zweven": ((-8, 70, 0), (-14, 0, 0)),
    "telefoon": ((-40, 8, 20), (-80, 0, 0)),
    "lippen": ((-72, 4, 30), (-92, 0, 0)),           # één arm: vinger naar de lippen
    "radio": ((-52, 10, 18), (-48, 0, 0)),
    "typen": ((-46, 12, 16), (-58, 0, 0)),
    "zij": ((0, 35, 0), (-40, -60, 0)),
}


class Rig2:
    pass


class Kort:
    """Eén originele short in de nieuwe stijl."""

    def __init__(self, code, cast=("hoofdpersonage",)):
        self.code = code
        self.a = args()
        self.scene, self.buiten = L.setup(set(cast))
        self.scene.render.fps = FPS
        self.spec = json.load(open(os.path.join(HERE, "tekst", code + ".json")))
        self.spec["fps"] = FPS
        self.total = self.spec["length"]
        self.END = int(round(self.total * FPS))
        self.L = {}
        for rel, t0 in self.spec["voice"]:
            n = int(os.path.basename(rel).split("-")[1].split("_")[0])
            self.L[n] = (t0, t0 + audio_len(os.path.join(AUDIO, rel)))
        wp = os.path.join(REPO, "videos", "originele-shorts", "woorden", code.upper() + "_regels.json")
        self.words = json.load(open(wp)) if os.path.exists(wp) else {}
        self.rigs = []
        self.shots = []
        self.bram = self.add_rig(L.rig_bram())
        cam, aim = L.camera(self.buiten, lens=40, fstop=2.8)
        self.cam, self.aim = cam, aim
        cam.data.sensor_fit = "VERTICAL"
        cam.data.sensor_height = 24.0
        self.cam.data.clip_start, self.cam.data.clip_end = 0.05, 3000
        self.out = os.path.join(REPO, "out", code)
        self.extra_bake = []
        self.world_fn = None

    # -- tijd --------------------------------------------------------------------------------------------
    def W(self, n, i):
        """Begintijd van woord i in stemregel n."""
        return self.L[n][0] + self.words[f"{self.code.upper()}-{n:02d}"][i]["s"]

    def r(self, n):
        return self.L[n][0]

    def e(self, n):
        return self.L[n][1]

    # -- personages ----------------------------------------------------------------------------------------
    def add_rig(self, rig):
        rig.eye_track = [(1, 1.0)]
        rig.blink_at = []
        rig.breath = True
        rig.char.rotation_mode = "XYZ"
        self.rigs.append(rig)
        return rig

    def extra(self, cname):
        return self.add_rig(L.rig_named(cname))

    def clone(self, rig, suffix):
        """Volledige kopie van een personage (met eigen rig-empties en mond), bv. spiegelbeeld of schaduw."""
        objs = [rig.char] + list(rig.char.children_recursive)
        coll = bpy.data.collections.new(rig.name + "_" + suffix)
        self.scene.collection.children.link(coll)
        m = {}
        for o in objs:
            c = o.copy()
            if o.data is not None:
                c.data = o.data.copy()
            c.animation_data_clear()
            c.name = o.name + "_" + suffix
            coll.objects.link(c)
            m[o] = c
        for o, c in m.items():
            if o.parent in m:
                c.parent = m[o.parent]
                c.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        n = Rig2()
        n.name = rig.name + "_" + suffix
        for attr in ("char", "mover", "root", "head", "nod"):
            setattr(n, attr, m[getattr(rig, attr)])
        for attr in ("sh", "el", "hip", "eyes", "brows"):
            setattr(n, attr, {s: m[o] for s, o in getattr(rig, attr).items()})
        n.brow_base = {s: v.copy() for s, v in rig.brow_base.items()}
        n.leg_len = rig.leg_len
        n.mouth_shapes = None
        if getattr(rig, "mouth_shapes", None):
            mouth = next(o for o in objs if o.name == "Bram_Mond")
            kb = m[mouth].data.shape_keys.key_blocks
            n.mouth_shapes = {k: kb[k] for k in rig.mouth_shapes}
        n.objs = list(m.values())
        n.coll = coll
        return self.add_rig(n)

    def place(self, rig, t, pos, yaw=0.0):
        f = FR(t)
        key(rig.char, "location", f, V(pos))
        key(rig.char, "rotation_euler", f, (0, 0, R(yaw)))

    def teleport(self, rig, t, pos, yaw=0.0):
        """Harde sprong (bij een knip): vorige stand tot t, nieuwe vanaf t."""
        f = FR(t)
        bpy.context.scene.frame_set(f - 1)
        loc, rot = rig.char.location.copy(), rig.char.rotation_euler.copy()
        key(rig.char, "location", f - 1, loc)
        key(rig.char, "rotation_euler", f - 1, rot)
        key(rig.char, "location", f, V(pos))
        key(rig.char, "rotation_euler", f, (0, 0, R(yaw)))
        for fc in _fcurves(rig.char):
            for kp in fc.keyframe_points:
                if abs(kp.co[0] - (f - 1)) < 0.01:
                    kp.interpolation = "CONSTANT"

    def face(self, rig, t, name, amt=1.0, eyes=None, mouth=None):
        """Gezicht op tijd t: emotie (zie EMO), amt mengt met neutraal. mouth = dict met extra mondvormen."""
        f = FR(t)
        dz, tilt, lach, boos, schr, ee, eye = EMO[name]
        n0 = EMO["leeg"]
        mix = lambda a, b: b + (a - b) * amt
        L.brow_keys(rig, f, mix(dz, n0[0]), mix(tilt, n0[1]))
        if rig.mouth_shapes:
            w = dict(Lach=mix(lach, 0.0), Boos=mix(boos, 0.0), Schreeuw=mix(schr, 0.0), E=mix(ee, 0.0), X=0.0)
            if mouth:
                w.update(mouth)
            L.mouth_keys(rig, f, **{k: v for k, v in w.items() if k in rig.mouth_shapes})
        rig.eye_track.append((f, eyes if eyes is not None else mix(eye, 1.0)))

    def blink(self, rig, *times):
        rig.blink_at += [FR(t) for t in times]

    def arms(self, rig, t, left="rust", right=None, l_add=None, r_add=None):
        """Armen op tijd t. left = arm aan de -x-kant (s=-1), right = +x (s=+1). Naam uit ARMS of (sh, el)-tuple."""
        right = left if right is None else right
        f = FR(t)
        for s, p, add in ((-1, left, l_add), (1, right, r_add)):
            sh, el = ARMS[p] if isinstance(p, str) else p
            if add:
                sh = tuple(a + b for a, b in zip(sh, add[0]))
                el = tuple(a + b for a, b in zip(el, add[1]))
            key(rig.sh[s], "rotation_euler", f, (R(sh[0]), R(-s * sh[1]), R(-s * sh[2])))
            key(rig.el[s], "rotation_euler", f, (R(el[0]), R(-s * el[1]), R(-s * el[2])))

    def body(self, rig, t, lean=0.0, side=0.0, dz=0.0, squash=1.0, twist=0.0):
        f = FR(t)
        key(rig.root, "rotation_euler", f, (R(lean), R(side), R(twist)))
        key(rig.mover, "location", f, Vector((0, 0, dz)))
        sxy = 1 + (1 - squash) * 0.8
        key(rig.root, "scale", f, Vector((sxy, sxy, squash)))

    def head(self, rig, t, up=0.0, tilt=0.0, turn=0.0):
        L.head_keys(rig, FR(t), up, tilt, turn)

    def legs(self, rig, t, l=0.0, r=None, spread=0.0):
        """Benen: + = naar voren (zitten = 85)."""
        r = l if r is None else r
        f = FR(t)
        for s, a in ((-1, l), (1, r)):
            key(rig.hip[s], "rotation_euler", f, (R(-a), R(-s * spread), 0))

    def beat(self, rig, t, arms="rust", face=None, amt=1.0, body=None, head=None, legs=0.0, r_arm=None, mouth=None):
        """Alles in één keer: armen, gezicht, romp, hoofd (en benen) op tijd t."""
        self.arms(rig, t, arms, r_arm)
        if face:
            self.face(rig, t, face, amt, mouth=mouth)
        self.body(rig, t, **(body or {}))
        self.head(rig, t, **(head or {}))
        if legs is not None:
            self.legs(rig, t, *legs) if isinstance(legs, tuple) else self.legs(rig, t, legs)

    def walk(self, rig, t0, t1, pts, back=False, theta=22.0, arms_amt=1.0, face_dir=None, ease=0.35):
        """Loopcyclus uit loop_bram.py langs een polylijn, per beeld gebakken (benen, armen, romp, positie, richting).
        back=True: achteruit lopen (kijkt de andere kant op). face_dir: vaste kijkrichting (yaw) i.p.v. de looprichting."""
        pts = [V(p) for p in pts]
        seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
        tot = sum(seg) or 1e-6
        LEG = rig.leg_len
        stride = 2 * LEG * math.sin(R(theta))
        f0, f1 = FR(t0), FR(t1)
        n = max(1, f1 - f0)
        rest = {s: rig.hip[s].location.copy() for s in (-1, 1)}

        def at(d):
            d = max(0.0, min(tot, d))
            for i, sl in enumerate(seg):
                if d <= sl or i == len(seg) - 1:
                    u = d / sl if sl else 0
                    return pts[i].lerp(pts[i + 1], u), (pts[i + 1] - pts[i])
                d -= sl
            return pts[-1], pts[-1] - pts[-2]

        # afstand als functie van tijd: rustig op gang, rustig uitlopen
        e = min(ease, 0.45)
        prof = lambda u: (u * u / (2 * e * (1 - e)) if u < e else
                          (e / (2 * (1 - e)) + (u - e) / (1 - e) if u < 1 - e else
                           1 - (1 - u) ** 2 / (2 * e * (1 - e))))
        last_yaw = None
        for k in range(n + 1):
            f = f0 + k
            u = k / n
            d = tot * prof(u)
            p, dirv = at(d)
            if face_dir is not None:
                yaw = face_dir
            else:
                yaw = math.degrees(math.atan2(dirv.x, -dirv.y)) + (180 if back else 0)
                if last_yaw is not None:
                    while yaw - last_yaw > 180:
                        yaw -= 360
                    while yaw - last_yaw < -180:
                        yaw += 360
            last_yaw = yaw
            amp = smoothstep(0, 0.12, u) * (1 - smoothstep(0.88, 1.0, u))
            ph = d / (2 * stride) if not back else -d / (2 * stride)
            ang, lift = {}, {}
            for s, off in ((-1, 0.0), (1, 0.5)):
                q = (ph + off) % 1.0
                if q < 0.5:
                    g, li = theta * (1 - 4 * q), 0.0
                else:
                    sw = (q - 0.5) / 0.5
                    g, li = -theta + 2 * theta * smoothstep(0, 1, sw), math.sin(math.pi * sw)
                ang[s], lift[s] = g * amp, li * amp
            stance = ang[-1] if lift[-1] == 0 else ang[1]
            key(rig.char, "location", f, p)
            key(rig.char, "rotation_euler", f, (0, 0, R(yaw)))
            key(rig.mover, "location", f, Vector((0, 0, -LEG * (1 - math.cos(R(stance))))))
            for s in (-1, 1):
                key(rig.hip[s], "rotation_euler", f, (R(-ang[s]), 0, 0))
                key(rig.hip[s], "location", f, rest[s] + Vector((0, 0, 0.05 * lift[s])))
                sx = 1.1 * ang[s] * arms_amt
                el = -18 - 14 * max(0.0, -ang[s] / theta) * amp * arms_amt
                key(rig.sh[s], "rotation_euler", f, (R(sx), R(-s * 3), 0))
                key(rig.el[s], "rotation_euler", f, (R(el), 0, 0))
            cyc = 2 * math.pi * ph
            key(rig.root, "rotation_euler", f, (R(4 * amp), 0, R(4 * amp * math.sin(cyc))))
            key(rig.root, "scale", f, Vector((1, 1, 1)))
        return f1

    # -- camera -----------------------------------------------------------------------------------------
    def shot(self, t0, a, b=None, focus="bram", fstop=2.8, shake=0.0):
        """Shot vanaf t0 tot het volgende. a/b = (camera, kijkpunt, lens) begin/eind. focus: rig, punt of 'aim'."""
        self.shots.append(dict(t0=t0, a=a, b=b or a, focus=self.bram if focus == "bram" else focus, fstop=fstop,
                               shake=shake))

    def _bake_cams(self):
        if os.environ.get("WHATIF_TESTCAM"):          # test: één vaste camera "x,y,z,tx,ty,tz,lens"
            v = [float(x) for x in os.environ["WHATIF_TESTCAM"].split(",")]
            self.shots = [dict(t0=0.0, a=(v[0:3], v[3:6], v[6]), b=(v[0:3], v[3:6], v[6]), focus="aim", fstop=8, shake=0)]
        sh = sorted(self.shots, key=lambda s: s["t0"])
        sc = bpy.context.scene
        cam, aim, cd = self.cam, self.aim, self.cam.data
        cd.dof.focus_object = None
        rnd = random.Random(5)
        noise = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(self.END // 6 + 3)]
        for f in range(1, self.END + 1):
            t = TT(f)
            i = max([k for k, s in enumerate(sh) if s["t0"] <= t + 1e-6] or [0])
            s = sh[i]
            ta = s["t0"]
            tb = sh[i + 1]["t0"] if i + 1 < len(sh) else self.total
            u = smoothstep(0, 1, (t - ta) / max(tb - ta, 1e-6))
            (c0, a0, l0), (c1, a1, l1) = s["a"], s["b"]
            c = V(c0).lerp(V(c1), u)
            ap = V(a0).lerp(V(a1), u)
            if s["shake"]:
                k = f / 6
                j = int(k)
                fr = k - j
                nx = noise[j][0] * (1 - fr) + noise[j + 1][0] * fr
                ny = noise[j][1] * (1 - fr) + noise[j + 1][1] * fr
                ap = ap + Vector((nx, 0, ny)) * s["shake"] * (ap - c).length * 0.01
            key(cam, "location", f, c)
            key(aim, "location", f, ap)
            cd.lens = l0 + (l1 - l0) * u
            cd.keyframe_insert("lens", frame=f)
            foc = s["focus"]
            if foc == "aim" or foc is None:
                fp = ap
            elif isinstance(foc, (tuple, list, Vector)):
                fp = V(foc)
            else:
                sc.frame_set(f)
                fp = foc.nod.matrix_world @ Vector((0, -0.25, 0.27))
            cd.dof.focus_distance = max(0.1, (fp - c).length)
            cd.dof.keyframe_insert("focus_distance", frame=f)
            cd.dof.aperture_fstop = s["fstop"]
            cd.dof.keyframe_insert("aperture_fstop", frame=f)
        for idb in (cam, aim, cd):
            for fc in _fcurves(idb):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"

    # -- afronden ---------------------------------------------------------------------------------------
    def _bake_faces(self):
        for i, rig in enumerate(self.rigs):
            rnd = random.Random(11 + i)
            auto, f = [], 18 + rnd.randint(0, 30)
            while f < self.END - 6:
                auto.append(f)
                f += rnd.randint(58, 105)
            frames = sorted(set(rig.blink_at + [a for a in auto if all(abs(a - b) > 20 for b in rig.blink_at)]))
            base = sorted(rig.eye_track)
            L.blink_bake(rig, frames, self.END, base=base)
            if rig.breath:
                for f in range(1, self.END + 1, 4):
                    key(rig.mover, "scale", f, Vector((1, 1, 1 + 0.006 * math.sin(2 * math.pi * TT(f) / 2.3 + i))))

    def done(self):
        sc = bpy.context.scene
        self._bake_faces()
        for fn in self.extra_bake:
            fn()
        self._bake_cams()
        if self.world_fn:
            self.world_fn()                 # wereld (blaadjes) altijd als laatste bouwen
        L.render_settings(samples=int(self.a["samples"] or 28))
        r = sc.render
        r.resolution_x, r.resolution_y = W, H
        r.fps = FPS
        sc.frame_start, sc.frame_end = 1, self.END
        os.makedirs(self.out, exist_ok=True)
        with open(os.path.join(self.out, "montage.json"), "w") as fh:
            json.dump(self.spec, fh, indent=1)
        r.image_settings.file_format = "PNG"
        r.image_settings.color_mode = "RGB"
        if self.a["stills"]:
            r.resolution_percentage = int(self.a["pct"] or 25)
            sc.cycles.samples = int(self.a["samples"] or 12)
            if self.a["stills"] == "auto":
                times = []
                sh = sorted(self.shots, key=lambda s: s["t0"])
                for k, s in enumerate(sh):
                    tb = sh[k + 1]["t0"] if k + 1 < len(sh) else self.total
                    times += [round(s["t0"] + 0.15, 2), round(tb - 0.15, 2)]
            else:
                times = [float(x) for x in self.a["stills"].split(",")]
            os.makedirs(os.path.join(self.out, "stills2"), exist_ok=True)
            for t in times:
                sc.frame_set(FR(t))
                r.filepath = os.path.join(self.out, "stills2", f"{self.code}_t{t:05.2f}.png")
                bpy.ops.render.render(write_still=True)
            print("STILLS KLAAR", len(times))
        if self.a["render"]:
            r.resolution_percentage = int(self.a["pct"] or 100)
            if self.a["frames"]:
                a_, b_ = self.a["frames"].split("-")
                sc.frame_start, sc.frame_end = int(a_), int(b_)
            fdir = os.path.join(self.out, "frames")
            os.makedirs(fdir, exist_ok=True)
            # al gerenderde beelden overslaan (hervatten na een onderbreking)
            r.use_overwrite = False
            r.use_placeholder = True
            r.filepath = os.path.join(fdir, "")
            bpy.ops.render.render(animation=True)
            print("KLAAR", self.code, sc.frame_start, "-", sc.frame_end)


def _fcurves(idb):
    ad = getattr(idb, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    out = []
    try:
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
    except Exception:
        pass
    return out


# =========================================================================================== speelgoedwereld
_LEAF = {}


def mat(name, rgb, rough=0.45, coat=0.25, sss=0.0, sheen=0.0, emit=0.0):
    m = bpy.data.materials.get(name)
    if m and m.get("orstijl"):
        return m
    m = material(name, rgb, rough=rough, sss=sss, sheen=sheen, coat=coat, emit=emit)
    m["orstijl"] = 1
    return m


def glow(name, rgb, strength=6.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = srgb(*rgb)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m


def bevel(o, w=0.02, seg=3):
    b = o.modifiers.new("Bevel", "BEVEL")
    b.width, b.segments = w, seg
    b.limit_method = "ANGLE"
    return o


def box(name, loc, size, m, bev=0.02, rot=(0, 0, 0)):
    """Doos met afmetingen size (volle maat), rond afgewerkt."""
    o = prim("cube", name, loc, tuple(s / 2 for s in size), m)
    o.rotation_euler = tuple(R(a) for a in rot)
    if bev:
        bevel(o, min(bev, min(size) * 0.45))
    return o


def ball(name, loc, r, m, scale=(1, 1, 1)):
    return prim("sphere", name, loc, tuple(r * s for s in scale), m)


def cyl(name, loc, r, h, m, rot=(0, 0, 0), bev=0.0, r2=None):
    """Cilinder met de onderkant op loc (as langs z vóór rotatie)."""
    if r2 is None:
        o = prim("cyl", name, (0, 0, 0), (r, r, h / 2), m)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r, radius2=r2, depth=h)
        o = bpy.context.active_object
        o.name = name
        L.smooth(o)
        o.data.materials.append(m)
    o.data.transform(Matrix.Translation((0, 0, h / 2)))
    o.location = loc
    o.rotation_euler = tuple(R(a) for a in rot)
    if bev:
        bevel(o, bev)
    return o


def text3d(name, body, loc, size, m, rot=(90, 0, 0), extrude=0.01, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = tuple(R(a) for a in rot)
    cu.materials.append(m)
    return o


def visible(o, t, on):
    """Zichtbaarheid sleutelen (render + camera)."""
    f = FR(t)
    o.hide_render = not on
    o.keyframe_insert("hide_render", frame=f)
    o.hide_viewport = not on
    o.keyframe_insert("hide_viewport", frame=f)


def show(o, t0, t1=None):
    visible(o, 0, False)
    visible(o, t0, True)
    if t1 is not None:
        visible(o, t1, False)


def leaf_group():
    """Geometry-nodes 'blaadjes' (zelfde als build_outdoor)."""
    if "ng" in _LEAF:
        return _LEAF["ng"]
    holder = bpy.data.collections.get("buiten")
    leaf_me = bpy.data.meshes.new("Blad")
    lv = [(0.13 * math.cos(2 * math.pi * k / 16), 0.09 * math.sin(2 * math.pi * k / 16),
           0.012 * math.cos(2 * math.pi * k / 16) ** 2) for k in range(16)]
    leaf_me.from_pydata([(0, 0, -0.012)] + lv, [], [(0, 1 + k, 1 + (k + 1) % 16) for k in range(16)])
    leaf = bpy.data.objects.new("Blad_bron", leaf_me)
    holder.objects.link(leaf)
    leaf.hide_render = leaf.hide_viewport = True
    lm = bpy.data.materials.new("Blad")
    ln = lm.node_tree
    lb = ln.nodes.get("Principled BSDF")
    oi = ln.nodes.new("ShaderNodeObjectInfo")
    ramp = ln.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(95, 170, 45)
    ramp.color_ramp.elements[1].color = srgb(175, 225, 80)
    ln.links.new(oi.outputs["Random"], ramp.inputs["Fac"])
    ln.links.new(ramp.outputs["Color"], lb.inputs["Base Color"])
    L.set_in(lb, "Roughness", 0.45)
    L.set_in(lb, "Subsurface Weight", 0.15)
    L.set_in(lb, "Sheen Weight", 0.3)
    leaf_me.materials.append(lm)
    ng = bpy.data.node_groups.new("Bladeren", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, li = ng.nodes, ng.links
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    dist = n.new("GeometryNodeDistributePointsOnFaces")
    dist.inputs["Density"].default_value = 75.0
    info = n.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = leaf
    inst = n.new("GeometryNodeInstanceOnPoints")
    rnd = n.new("FunctionNodeRandomValue")
    rnd.data_type = "FLOAT"
    L.sock(rnd.inputs, "Min").default_value = 0.75
    L.sock(rnd.inputs, "Max").default_value = 1.3
    join = n.new("GeometryNodeJoinGeometry")
    li.new(gi.outputs[0], dist.inputs["Mesh"])
    li.new(dist.outputs["Points"], inst.inputs["Points"])
    li.new(info.outputs["Geometry"], inst.inputs["Instance"])
    rv = n.new("FunctionNodeRandomValue")
    rv.data_type = "FLOAT_VECTOR"
    L.sock(rv.inputs, "Min").default_value = (-0.6, -0.6, -3.14)
    L.sock(rv.inputs, "Max").default_value = (0.6, 0.6, 3.14)
    e2r = n.new("FunctionNodeEulerToRotation")
    rr = n.new("FunctionNodeRotateRotation")
    rr.rotation_space = "LOCAL"
    li.new(L.sock(rv.outputs), e2r.inputs[0])
    li.new(dist.outputs["Rotation"], rr.inputs[0])
    li.new(e2r.outputs[0], rr.inputs[1])
    li.new(rr.outputs[0], inst.inputs["Rotation"])
    li.new(L.sock(rnd.outputs), inst.inputs["Scale"])
    li.new(gi.outputs[0], join.inputs[0])
    li.new(inst.outputs["Instances"], join.inputs[0])
    li.new(join.outputs[0], go.inputs[0])
    _LEAF["ng"] = ng
    return ng


def tree(name, x, y, z0=0.0, r=1.6, h=None, leaves=True):
    """Bolle speelgoedboom: stam + kruin (met blaadjes). Geeft (stam, kruin)."""
    bark = mat("Schors", (110, 74, 46), rough=0.8, coat=0)
    inner = mat("Bladbinnen", (52, 105, 30), rough=0.8, coat=0)
    h = h if h is not None else r * 1.3
    st = cyl(name + "_stam", (x, y, z0), 0.1 * r, h + r * 0.3, bark)
    cr = ball(name + "_kruin", (x, y, z0 + h + r * 0.75), r, inner, (1, 1, 0.95))
    if leaves:
        cr.modifiers.new("Bladeren", "NODES").node_group = leaf_group()
    return st, cr


def sky(kind="dag", strength=None):
    """Wereld: blauwe lucht met zonnegloed (dag), oranje-paars (avond) of donkerblauw met sterrengloed (nacht)."""
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Lucht_" + kind)
    scene.world = world
    wn, wl = world.node_tree.nodes, world.node_tree.links
    bg = wn.get("Background")
    tcw = wn.new("ShaderNodeTexCoord")
    sep = wn.new("ShaderNodeSeparateXYZ")
    wl.new(tcw.outputs["Generated"], sep.inputs[0])
    mr = wn.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.4
    wl.new(sep.outputs["Z"], mr.inputs["Value"])
    skyr = wn.new("ShaderNodeValToRGB")
    cols = {"dag": ((125, 180, 240), (38, 100, 205), (255, 236, 190), 0.85),
            "avond": ((255, 160, 110), (70, 60, 140), (255, 190, 120), 0.7),
            "nacht": ((28, 40, 80), (6, 10, 30), (90, 110, 170), 0.55),
            "binnen": ((150, 190, 235), (70, 120, 200), (255, 240, 210), 0.6)}[kind]
    skyr.color_ramp.elements[0].color = srgb(*cols[0])
    skyr.color_ramp.elements[1].color = srgb(*cols[1])
    wl.new(mr.outputs["Result"], skyr.inputs["Fac"])
    dot = wn.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = Vector((-0.42, 0.78, 0.46)).normalized()
    wl.new(tcw.outputs["Generated"], dot.inputs[0])
    gm = wn.new("ShaderNodeMapRange")
    gm.inputs["From Min"].default_value = 0.78
    gm.inputs["From Max"].default_value = 1.0
    wl.new(dot.outputs["Value"], gm.inputs["Value"])
    pw = wn.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 3.0
    wl.new(gm.outputs["Result"], pw.inputs[0])
    mix = wn.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "ADD"
    mix.inputs["B"].default_value = srgb(*cols[2])
    wl.new(pw.outputs[0], mix.inputs["Factor"])
    wl.new(skyr.outputs["Color"], mix.inputs["A"])
    wl.new(mix.outputs["Result"], bg.inputs["Color"])
    L.set_in(bg, "Strength", strength if strength is not None else cols[3])
    return world, bg


def sun(energy=4.5, color=(1.0, 0.88, 0.72), d=(-0.6, -0.35, 0.72), angle=3.0, name="Zon"):
    sd = bpy.data.lights.new(name, "SUN")
    sd.energy, sd.color, sd.angle = energy, color, R(angle)
    so = bpy.data.objects.new(name, sd)
    bpy.data.collections["buiten"].objects.link(so)
    so.rotation_mode = "QUATERNION"
    so.rotation_quaternion = Vector(d).normalized().to_track_quat("Z", "Y")
    return so


def area(name, loc, target, size, energy, rgb=(1, 1, 1), camera=False):
    ld = bpy.data.lights.new(name, "AREA")
    ld.size, ld.energy, ld.color = size, energy, rgb
    o = bpy.data.objects.new(name, ld)
    bpy.data.collections["buiten"].objects.link(o)
    o.location = loc
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
    if not camera:
        o.visible_camera = False
        o.visible_glossy = False
    return o


def point(name, loc, energy, rgb=(1, 1, 1), r=0.1):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = energy, rgb, r
    o = bpy.data.objects.new(name, ld)
    bpy.data.collections["buiten"].objects.link(o)
    o.location = loc
    return o


def three_point(prefix, c, yaw=0.0, scale=1.0, warm=1.0):
    """Vul-, koel- en randlicht zoals build_outdoor, om punt c en gedraaid met yaw (graden)."""
    c = V(c)
    rot = Matrix.Rotation(R(yaw), 3, "Z")
    out = []
    for nm, off, tgt, size, en, rgb in (("Vullicht", (3.2, -5.0, 2.2), (0, 0, 1.1), 4.0, 260, (1.0, 0.93, 0.85)),
                                         ("Koel_vul", (-3.5, -3.5, 1.2), (0, 0, 1.0), 3.0, 120, (0.75, 0.85, 1.0)),
                                         ("Randlicht", (1.5, 2.5, 2.4), (0, 0, 1.3), 1.5, 250, (1.0, 0.85, 0.65))):
        rgb = tuple(min(1.0, x * (warm if i == 0 else 1)) for i, x in enumerate(rgb))
        out.append(area(f"{prefix}_{nm}", c + rot @ (V(off) * scale), c + rot @ V(tgt), size * scale, en * scale * scale, rgb))
    return out


def key_energy(light, pts):
    for t, e in pts:
        light.data.energy = e
        light.data.keyframe_insert("energy", frame=FR(t))


def ground(name, loc, size, m):
    o = prim("plane", name, loc, (size[0] / 2, size[1] / 2, 1), m)
    return o


# ------------------------------------------------------------------------------------------- huizen, auto's, kamers
def house(name, x, y, w=5.0, d=5.0, h=6.0, wall=(235, 200, 160), roof=(200, 80, 60), yaw=0.0, windows=True,
          lit=None, door=True, flat=False):
    """Speelgoedhuis: blok met dak, ramen en deur. Voorkant = -y (voor yaw 0). Geeft (objecten, ramen)."""
    wm = mat(f"Muur_{wall}", wall, rough=0.6, coat=0.1)
    rm = mat(f"Dak_{roof}", roof, rough=0.5, coat=0.2)
    glass_m = lit or mat("Raam", (150, 200, 235), rough=0.08, coat=0.6)
    frame_m = mat("Kozijn", (250, 248, 240), rough=0.4)
    objs, wins = [], []
    body = box(name, (0, 0, h / 2), (w, d, h), wm, bev=0.06)
    objs.append(body)
    if flat:
        objs.append(box(name + "_dakrand", (0, 0, h + 0.15), (w + 0.2, d + 0.2, 0.3), rm, bev=0.05))
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, radius2=0, depth=1)
        r_ = bpy.context.active_object
        r_.name = name + "_dak"
        r_.data.transform(Matrix.Rotation(R(45), 4, "Z"))
        r_.data.transform(Matrix.Diagonal(((w + 0.5) / 1.414, (d + 0.5) / 1.414, h * 0.45, 1)))
        r_.location = (0, 0, h + h * 0.225)
        r_.data.materials.append(rm)
        bevel(r_, 0.05)
        objs.append(r_)
    if windows:
        nx = max(1, int(w / 1.7))
        nz = max(1, int((h - 0.6) / 2.2))
        for i in range(nx):
            for j in range(nz):
                wx = -w / 2 + (i + 0.5) * w / nx
                wz = 1.5 + j * 2.2
                if door and j == 0 and i == nx // 2:
                    continue
                fr = box(f"{name}_kozijn_{i}_{j}", (wx, -d / 2 - 0.02, wz), (0.95, 0.08, 1.15), frame_m, bev=0.02)
                gl = box(f"{name}_raam_{i}_{j}", (wx, -d / 2 - 0.06, wz), (0.78, 0.04, 0.98), glass_m, bev=0.0)
                objs += [fr, gl]
                wins.append(gl)
    if door:
        dx = -w / 2 + (max(1, int(w / 1.7)) // 2 + 0.5) * w / max(1, int(w / 1.7))
        objs.append(box(name + "_deur", (dx, -d / 2 - 0.03, 1.0), (0.95, 0.1, 2.0), mat("Deur", (120, 70, 45)), bev=0.03))
    root = bpy.data.objects.new(name + "_huis", None)
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        o.parent = root
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, R(yaw))
    return root, wins


def car(name, x, y, yaw=0.0, color=(220, 60, 50), z=0.0):
    """Bolle speelgoedauto (lengte ~4 m langs lokale x). Geeft de root-empty."""
    body_m = mat(f"Lak_{color}", color, rough=0.25, coat=0.8)
    glass_m = mat("Autoruit", (60, 80, 100), rough=0.05, coat=0.8)
    tyre = mat("Band", (35, 35, 38), rough=0.7, coat=0)
    hub = mat("Velg", (230, 230, 235), rough=0.3, coat=0.4)
    lamp = mat("Koplamp", (255, 245, 200), rough=0.2, emit=1.5)
    objs = [box(name + "_onder", (0, 0, 0.62), (3.9, 1.8, 0.75), body_m, bev=0.3),
            box(name + "_kap", (-0.2, 0, 1.25), (2.2, 1.6, 0.75), body_m, bev=0.3),
            box(name + "_ruit_v", (0.92, 0, 1.25), (0.05, 1.42, 0.55), glass_m, bev=0.02, rot=(0, -25, 0)),
            box(name + "_ruit_a", (-1.32, 0, 1.25), (0.05, 1.42, 0.5), glass_m, bev=0.02, rot=(0, 25, 0)),
            box(name + "_ruit_l", (-0.2, 0.81, 1.27), (1.8, 0.03, 0.5), glass_m, bev=0.02),
            box(name + "_ruit_r", (-0.2, -0.81, 1.27), (1.8, 0.03, 0.5), glass_m, bev=0.02)]
    for sx in (1, -1):
        objs.append(ball(f"{name}_lamp_{sx}", (1.93, sx * 0.6, 0.72), 0.14, lamp, (0.4, 1, 1)))
    for wx in (1.25, -1.25):
        for wy in (0.88, -0.88):
            objs.append(cyl(f"{name}_wiel_{wx}_{wy}", (wx, wy - 0.15 * (1 if wy > 0 else -1), 0.38), 0.38, 0.3, tyre,
                            rot=(90 if wy > 0 else -90, 0, 0)))
            objs[-1].location = (wx, wy + (-0.15 if wy > 0 else 0.15), 0.38)
            objs.append(cyl(f"{name}_velg_{wx}_{wy}", (wx, wy + (0.16 if wy > 0 else -0.16), 0.38), 0.2, 0.02, hub,
                            rot=(-90 if wy > 0 else 90, 0, 0)))
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        o.parent = root
    root.location = (x, y, z)
    root.rotation_euler = (0, 0, R(yaw))
    return root


def room(name, c, w, d, h, wall=(240, 225, 200), floor=(200, 150, 100), open_side="-y", ceiling=True,
         window=None, wall_m=None, floor_m=None):
    """Kamer met 3 (of 4) muren rond c (vloer op c.z). open_side: welke muur weg blijft (voor de camera).
    window = (muur, x-of-y midden, z midden, breedte, hoogte): raam met lucht erachter."""
    c = V(c)
    wm = wall_m or mat(f"Wand_{wall}", wall, rough=0.7, coat=0.05)
    fm = floor_m or mat(f"Vloer_{floor}", floor, rough=0.5, coat=0.3)
    objs = [box(name + "_vloer", c + V(0, 0, -0.05), (w + 0.4, d + 0.4, 0.1), fm, bev=0.01)]
    if ceiling:
        objs.append(box(name + "_plafond", c + V(0, 0, h + 0.05), (w + 0.4, d + 0.4, 0.1), wm, bev=0.0))
    t = 0.15
    walls = {"-y": (V(0, -d / 2 - t / 2, h / 2), (w + 2 * t, t, h)),
             "+y": (V(0, d / 2 + t / 2, h / 2), (w + 2 * t, t, h)),
             "-x": (V(-w / 2 - t / 2, 0, h / 2), (t, d, h)),
             "+x": (V(w / 2 + t / 2, 0, h / 2), (t, d, h))}
    for side, (p, s) in walls.items():
        if side == open_side:
            continue
        if window and window[0] == side:
            _, mid, zm, ww, wh = window
            horiz = side in ("-y", "+y")
            length = s[0] if horiz else s[1]
            a0, a1 = -length / 2, length / 2
            w0, w1 = mid - ww / 2, mid + ww / 2
            for k, (q0, q1) in enumerate(((a0, w0), (w1, a1))):
                lc = (q0 + q1) / 2
                ln_ = q1 - q0
                off = V(lc, 0, 0) if horiz else V(0, lc, 0)
                sz = (ln_, t, h) if horiz else (t, ln_, h)
                objs.append(box(f"{name}_muur{side}_{k}", c + p + off, sz, wm, bev=0.0))
            for k, (z0, z1) in enumerate(((0, zm - wh / 2), (zm + wh / 2, h))):
                off = (V(mid, 0, 0) if horiz else V(0, mid, 0)) + V(0, 0, (z0 + z1) / 2 - h / 2)
                sz = (ww, t, z1 - z0) if horiz else (t, ww, z1 - z0)
                objs.append(box(f"{name}_muur{side}_z{k}", c + p + off, sz, wm, bev=0.0))
            frm = mat("Kozijn", (250, 248, 240), rough=0.4)
            off = (V(mid, 0, 0) if horiz else V(0, mid, 0)) + V(0, 0, zm - h / 2)
            for k, dd in enumerate((-1, 1)):
                o2 = (V(0, 0, dd * wh / 2) if True else V())
                sz = (ww + 0.1, t + 0.06, 0.08) if horiz else (t + 0.06, ww + 0.1, 0.08)
                objs.append(box(f"{name}_kozijn{side}_{k}", c + p + off + o2, sz, frm, bev=0.01))
        else:
            objs.append(box(f"{name}_muur{side}", c + p, s, wm, bev=0.0))
    return objs


def material_swap(objs, fn):
    """Vervang per object elk materiaal door fn(oud) (cache per oud materiaal)."""
    cache = {}
    for o in objs:
        if o.type not in ("MESH", "CURVE", "FONT") or not o.data or not hasattr(o.data, "materials"):
            continue
        for i, m in enumerate(o.data.materials):
            if m is None:
                continue
            if m.name not in cache:
                cache[m.name] = fn(m)
            o.data.materials[i] = cache[m.name]
    return cache


def fade_material(m, tag, target="glass"):
    """Kopie van m met een Mix Shader naar glas/transparant; geeft (nieuw materiaal, mengwaarde-socket)."""
    n = m.copy()
    n.name = m.name + "_" + tag
    nt = n.node_tree
    out = next(x for x in nt.nodes if x.type == "OUTPUT_MATERIAL" and x.is_active_output) if any(
        x.type == "OUTPUT_MATERIAL" and x.is_active_output for x in nt.nodes) else next(
        x for x in nt.nodes if x.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket if out.inputs["Surface"].links else None
    mix = nt.nodes.new("ShaderNodeMixShader")
    if target == "glass":
        g = nt.nodes.new("ShaderNodeBsdfGlass")
        g.inputs["Color"].default_value = (0.92, 0.97, 1.0, 1)
        g.inputs["Roughness"].default_value = 0.02
        g.inputs["IOR"].default_value = 1.33
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx2 = nt.nodes.new("ShaderNodeMixShader")
        mx2.inputs[0].default_value = 0.55
        nt.links.new(g.outputs[0], mx2.inputs[1])
        nt.links.new(tr.outputs[0], mx2.inputs[2])
        dst = mx2.outputs[0]
    else:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        dst = tr.outputs[0]
    if src:
        nt.links.new(src, mix.inputs[1])
    nt.links.new(dst, mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    mix.inputs[0].default_value = 0.0
    return n, mix.inputs[0]


def key_value(sock, pts):
    for t, v in pts:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=FR(t))


def face_in_mirror(objs, tag="spiegel"):
    """De gezichtsdelen in het cast-bestand (ogen, wenkbrauwen, mond) zijn alleen voor camerastralen zichtbaar
    (Light Path 'Is Camera Ray'). Voor een spiegelbeeld: ook voor glossy-stralen zichtbaar maken (kopie van het materiaal)."""
    def fix(m):
        nt = m.node_tree
        lp = next((n for n in nt.nodes if n.type == "LIGHT_PATH"), None) if nt else None
        if not lp or not lp.outputs["Is Camera Ray"].links:
            return m
        n = m.copy()
        n.name = m.name + "_" + tag
        nt = n.node_tree
        lp = next(x for x in nt.nodes if x.type == "LIGHT_PATH")
        mx = nt.nodes.new("ShaderNodeMath")
        mx.operation = "MAXIMUM"
        nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
        nt.links.new(lp.outputs["Is Glossy Ray"], mx.inputs[1])
        for li in list(lp.outputs["Is Camera Ray"].links):
            if li.to_node != mx:
                to = li.to_socket
                nt.links.remove(li)
                nt.links.new(mx.outputs[0], to)
        return n
    material_swap(objs, fix)


def tile_mat(name, c1, c2, mortar=(245, 248, 245), axis="y", scale=6.0, mortar_size=0.015, rough=0.25, coat=0.5,
             row=0.5, width=1.0):
    """Tegels (Brick-textuur) op een vlak met normaal langs axis ('x', 'y' of 'z')."""
    m = material(name, c1, rough=rough, coat=coat)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tc.outputs["Object"], sp.inputs[0])
    a, b_ = {"x": ("Y", "Z"), "y": ("X", "Z"), "z": ("X", "Y")}[axis]
    nt.links.new(sp.outputs[a], cb.inputs["X"])
    nt.links.new(sp.outputs[b_], cb.inputs["Y"])
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = srgb(*c1)
    br.inputs["Color2"].default_value = srgb(*c2)
    br.inputs["Mortar"].default_value = srgb(*mortar)
    br.inputs["Scale"].default_value = scale
    br.inputs["Mortar Size"].default_value = mortar_size
    br.inputs["Brick Width"].default_value = width
    br.inputs["Row Height"].default_value = row
    br.offset = 0.0
    nt.links.new(cb.outputs[0], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


# ------------------------------------------------------------------------------------------- speelgoedstad
PASTEL = [(250, 205, 150), (170, 210, 235), (245, 170, 160), (200, 225, 160), (250, 230, 170), (215, 190, 235),
          (240, 240, 230), (180, 220, 210)]
ROOFS = [(200, 80, 60), (90, 110, 160), (150, 90, 60), (210, 120, 70), (110, 140, 110)]


def town(cx=0.0, cy=0.0, half=56.0, cross=True, trees=True, lamps=True, blocks=None, lit_kind="warm", seed=1,
         skip=None, house_x=11.5, lights_on=False):
    """Speelgoedstadje: weg langs y (x = cx), optioneel kruising langs x op y = cy, stoepen, huizen, bomen,
    lantaarns, zebrapaden en verkeerslichten. blocks(x, y) -> bloknaam bepaalt welk raam-materiaal een huis krijgt
    (voor 'de stroom valt uit'). Geeft dict met o.a. 'win_mats' {blok: materiaal}, 'lamps' [(paal, lamp, licht, blok)]."""
    rnd = random.Random(seed)
    c = V(cx, cy, 0)
    asphalt = mat("Asfalt", (70, 72, 78), rough=0.85, coat=0)
    walk_m = mat("Stoep", (205, 205, 210), rough=0.7, coat=0)
    curb_m = mat("Stoeprand", (235, 235, 238), rough=0.6, coat=0)
    white = mat("Wegverf", (250, 250, 250), rough=0.5, coat=0)
    grass = mat("Gras", (96, 170, 70), rough=0.8, coat=0, sheen=0.5)
    ground(f"Grond_{seed}", c + V(0, 0, -0.03), (2 * half + 80, 2 * half + 80), grass)
    out = dict(win_mats={}, lamps=[], houses=[], lights=[])
    RW, SW = 3.5, 3.0                  # halve wegbreedte, stoepbreedte

    def road(name, a, b_, along):
        L_ = (V(b_) - V(a)).length
        mid = (V(a) + V(b_)) / 2
        size = (2 * RW, L_, 0.04) if along == "y" else (L_, 2 * RW, 0.04)
        box(name, mid + V(0, 0, -0.02), size, asphalt, bev=0)
        for s in (-1, 1):
            off = V(s * (RW + SW / 2), 0, 0) if along == "y" else V(0, s * (RW + SW / 2), 0)
            sz = (SW, L_, 0.15) if along == "y" else (L_, SW, 0.15)
            box(f"{name}_stoep{s}", mid + off + V(0, 0, 0.075), sz, walk_m, bev=0.02)
            off2 = V(s * (RW + 0.1), 0, 0) if along == "y" else V(0, s * (RW + 0.1), 0)
            sz2 = (0.2, L_, 0.17) if along == "y" else (L_, 0.2, 0.17)
            box(f"{name}_rand{s}", mid + off2 + V(0, 0, 0.085), sz2, curb_m, bev=0.03)
        n = int(L_ / 4)
        for k in range(n):
            u = (k + 0.5) / n
            p = V(a).lerp(V(b_), u)
            if cross and ((along == "y" and abs(p.y - cy) < RW + SW + 2) or (along == "x" and abs(p.x - cx) < RW + SW + 2)):
                continue
            box(f"{name}_streep{k}", p + V(0, 0, 0.002), (0.15, 1.8, 0.01) if along == "y" else (1.8, 0.15, 0.01), white, bev=0)

    if cross:
        road("Weg_y_zuid", c + V(0, -half, 0), c + V(0, -(RW + SW), 0), "y")
        road("Weg_y_noord", c + V(0, RW + SW, 0), c + V(0, half, 0), "y")
        road("Weg_x_west", c + V(-half, 0, 0), c + V(-(RW + SW), 0, 0), "x")
        road("Weg_x_oost", c + V(RW + SW, 0, 0), c + V(half, 0, 0), "x")
        box("Kruispunt", c + V(0, 0, -0.02), (2 * (RW + SW), 2 * (RW + SW), 0.04), asphalt, bev=0)
        # zebrapaden aan vier kanten
        for side, (ax, off) in enumerate((("y", -1), ("y", 1), ("x", -1), ("x", 1))):
            for k in range(7):
                q = -RW + 0.5 + k * 1.0
                if ax == "y":
                    p = c + V(q, off * (RW + SW / 2 + 0.3), 0.003)
                    sz = (0.55, 2.6, 0.01)
                else:
                    p = c + V(off * (RW + SW / 2 + 0.3), q, 0.003)
                    sz = (2.6, 0.55, 0.01)
                box(f"Zebra_{side}_{k}", p, sz, white, bev=0)
        # stoephoeken
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(f"Stoephoek_{sx}_{sy}", c + V(sx * (RW + SW / 2), sy * (RW + SW / 2), 0.075), (SW, SW, 0.15), walk_m, bev=0.02)
    else:
        road("Weg_y", c + V(0, -half, 0), c + V(0, half, 0), "y")

    # huizen
    spots = []
    for s in (-1, 1):
        y = -half + 4
        while y < half - 4:
            if not (cross and abs(y - cy) < RW + SW + 5):
                spots.append((c.x + s * house_x, c.y + y, -90 * s))
            y += rnd.uniform(7.5, 9.0)
        if cross:
            x = -half + 4
            while x < half - 4:
                if abs(x) > RW + SW + 5 + 4:
                    spots.append((c.x + x, c.y + s * house_x, 0 if s > 0 else 180))
                x += rnd.uniform(7.5, 9.0)
    for i, (x, y, yaw) in enumerate(spots):
        if skip and skip(x, y):
            continue
        blk = blocks(x, y) if blocks else "A"
        if blk not in out["win_mats"]:
            if lit_kind:
                m_ = bpy.data.materials.new(f"Ramen_{blk}")
                b_ = m_.node_tree.nodes["Principled BSDF"]
                b_.inputs["Base Color"].default_value = srgb(150, 200, 235)
                b_.inputs["Roughness"].default_value = 0.08
                L.set_in(b_, "Coat Weight", 0.6)
                b_.inputs["Emission Color"].default_value = srgb(255, 205, 130)
                b_.inputs["Emission Strength"].default_value = 3.0 if lights_on else 0.0
            else:
                m_ = None
            out["win_mats"][blk] = m_
        w = rnd.uniform(5.5, 7.0)
        h = rnd.choice((4.5, 5.5, 6.5, 8.5))
        root, wins = house(f"Huis_{seed}_{i}", x, y, w, rnd.uniform(5.5, 7.0), h, wall=rnd.choice(PASTEL),
                           roof=rnd.choice(ROOFS), yaw=yaw, lit=out["win_mats"][blk], flat=h > 7)
        out["houses"].append((root, blk))
    # bomen en lantaarns langs de stoep
    pole_m = mat("Paal", (60, 70, 80), rough=0.4, coat=0.3)
    for s in (-1, 1):
        for k, y in enumerate(range(int(-half + 8), int(half - 6), 16)):
            if cross and abs(y) < RW + SW + 6:
                continue
            p = c + V(s * (RW + SW - 0.6), y, 0.15)
            if trees:
                tree(f"Boom_{seed}_{s}_{k}", p.x, p.y + 4, 0.15, r=1.4, h=1.9)
            if lamps:
                blk = blocks(p.x, p.y) if blocks else "A"
                post = cyl(f"Lantaarnpaal_{seed}_{s}_{k}", p, 0.07, 4.2, pole_m)
                arm = cyl(f"Lantaarnarm_{seed}_{s}_{k}", p + V(0, 0, 4.1), 0.05, 0.9, pole_m, rot=(0, -90 * s, 0))
                lm = bpy.data.materials.get(f"Lamp_{blk}") or glow(f"Lamp_{blk}", (255, 220, 160), 6.0 if lights_on else 0.2)
                bulb = ball(f"Lantaarnlamp_{seed}_{s}_{k}", p + V(-s * 0.85, 0, 4.05), 0.2, lm, (1.3, 1.3, 0.6))
                li = point(f"Lantaarnlicht_{seed}_{s}_{k}", p + V(-s * 0.85, 0, 3.8), 300 if lights_on else 0, (1.0, 0.8, 0.55), 0.2)
                out["lamps"].append((post, bulb, li, blk))
    # verkeerslichten op de hoeken
    if cross:
        out["tl"] = []
        for k, (sx, sy, yaw) in enumerate(((1, -1, 0), (-1, 1, 180), (1, 1, 90), (-1, -1, -90))):
            p = c + V(sx * (RW + 0.6), sy * (RW + 0.6), 0.15)
            cyl(f"Verkeerslichtpaal_{k}", p, 0.07, 3.0, pole_m)
            kast = box(f"Verkeerslicht_{k}", p + V(0, 0, 3.25), (0.4, 0.35, 1.0), mat("Kast_zwart", (30, 32, 36)), bev=0.06)
            kast.rotation_euler = (0, 0, R(yaw))
            lamps_ = []
            for j, col in enumerate(((255, 60, 50), (255, 190, 40), (70, 230, 90))):
                gm = glow(f"VL_{k}_{j}", col, 0.3)
                bl = ball(f"VL_lamp_{k}_{j}", (0, -0.19, 0.3 - j * 0.3), 0.11, gm, (1, 0.5, 1))
                bl.parent = kast
                lamps_.append(gm)
            out["tl"].append(lamps_)
    return out


def tl_state(town_, t, state):
    """Verkeerslichten op tijd t: 'rood', 'oranje', 'groen' (alle vier gelijk)."""
    j = {"rood": 0, "oranje": 1, "groen": 2}[state]
    for lamps_ in town_.get("tl", []):
        for i, gm in enumerate(lamps_):
            s = gm.node_tree.nodes["Emission"].inputs["Strength"]
            s.default_value = 8.0 if i == j else 0.3
            s.keyframe_insert("default_value", frame=FR(t))
            for fc in _fcurves(gm.node_tree):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def puff(name, pos, t, dur=1.2, r=0.25, rise=0.5, color=(235, 235, 240), grow=2.2, drift=(0, 0, 0)):
    """Speelgoedwolkje: bolletje dat opkomt, groeit en wegtrekt (krimpt weg)."""
    m = bpy.data.materials.get(f"Wolk_{color}") or mat(f"Wolk_{color}", color, rough=0.9, coat=0, sheen=0.4)
    o = ball(name, pos, 1.0, m)
    o.scale = (0.001, 0.001, 0.001)
    f0, f1 = FR(t), FR(t + dur)
    key(o, "scale", max(1, f0 - 1), Vector((0.001,) * 3))
    key(o, "location", f0, V(pos))
    key(o, "scale", f0, Vector((r * 0.4,) * 3))
    key(o, "scale", int(f0 + (f1 - f0) * 0.4), Vector((r * grow * 0.8,) * 3))
    key(o, "location", f1, V(pos) + V(0, 0, rise) + V(drift))
    key(o, "scale", f1, Vector((0.001,) * 3))
    return o


SKY = {"dag": ((125, 180, 240), (38, 100, 205), (255, 236, 190), 0.85),
       "avond": ((255, 160, 110), (70, 60, 140), (255, 190, 120), 0.7),
       "nacht": ((28, 40, 80), (6, 10, 30), (90, 110, 170), 0.55),
       "binnen": ((150, 190, 235), (70, 120, 200), (255, 240, 210), 0.6)}


def _sky_color(wn, wl, kind, tcw):
    cols = SKY[kind]
    sep = wn.new("ShaderNodeSeparateXYZ")
    wl.new(tcw.outputs["Generated"], sep.inputs[0])
    mr = wn.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.4
    wl.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = wn.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(*cols[0])
    ramp.color_ramp.elements[1].color = srgb(*cols[1])
    wl.new(mr.outputs["Result"], ramp.inputs["Fac"])
    dot = wn.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = Vector((-0.42, 0.78, 0.46)).normalized()
    wl.new(tcw.outputs["Generated"], dot.inputs[0])
    gm = wn.new("ShaderNodeMapRange")
    gm.inputs["From Min"].default_value = 0.78
    gm.inputs["From Max"].default_value = 1.0
    wl.new(dot.outputs["Value"], gm.inputs["Value"])
    pw = wn.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 3.0
    wl.new(gm.outputs["Result"], pw.inputs[0])
    mix = wn.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "ADD"
    mix.inputs["B"].default_value = srgb(*cols[2])
    wl.new(pw.outputs[0], mix.inputs["Factor"])
    wl.new(ramp.outputs["Color"], mix.inputs["A"])
    return mix.outputs["Result"]


def sky_blend(kinds=("dag", "avond")):
    """Lucht die tussen twee soorten overvloeit. Geeft (mengfactor-socket, sterkte-socket)."""
    world = bpy.data.worlds.new("Lucht_" + "_".join(kinds))
    bpy.context.scene.world = world
    wn, wl = world.node_tree.nodes, world.node_tree.links
    bg = wn.get("Background")
    tcw = wn.new("ShaderNodeTexCoord")
    c1 = _sky_color(wn, wl, kinds[0], tcw)
    c2 = _sky_color(wn, wl, kinds[1], tcw)
    mx = wn.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    wl.new(c1, mx.inputs["A"])
    wl.new(c2, mx.inputs["B"])
    wl.new(mx.outputs["Result"], bg.inputs["Color"])
    mx.inputs["Factor"].default_value = 0.0
    bg.inputs["Strength"].default_value = SKY[kinds[0]][3]
    return mx.inputs["Factor"], bg.inputs["Strength"]


def frange(a, b_, s):
    out, t = [], a
    while t <= b_ + 1e-6:
        out.append(t)
        t += s
    return out


fcurves = _fcurves


def rig_objs(rig):
    """De bewegende empties van een personage (zonder gezicht)."""
    out = [rig.char, rig.mover, rig.root, rig.head, rig.nod]
    for d in (rig.sh, rig.el, rig.hip):
        out += list(d.values())
    return out


def copy_anim(objs, src_a, src_b, dst_a, dst_b):
    """Speel de animatie van objs uit [src_a, src_b] opnieuw af in [dst_a, dst_b] (src_a > src_b = achteruit,
    terugspoelen). Bakt elk beeld (30 fps)."""
    jobs = []
    for o in objs:
        for fc in fcurves(o):
            if fc.data_path.startswith('["') or fc.data_path.startswith("hide"):
                continue
            vals = []
            for f in range(FR(dst_a), FR(dst_b) + 1):
                u = (TT(f) - dst_a) / max(dst_b - dst_a, 1e-6)
                ts = src_a + (src_b - src_a) * min(1.0, max(0.0, u))
                vals.append((f, fc.evaluate(ts * FPS + 1)))
            jobs.append((fc, vals))
    for fc, vals in jobs:
        for f, v in vals:
            fc.keyframe_points.insert(f, v, options={"FAST"})
        fc.update()


def attach(obj, parent, local_loc, local_rot=(0, 0, 0)):
    """Hang obj aan een rig-empty (bv. hand = elleboog-empty) met een vaste lokale positie."""
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = local_loc
    obj.rotation_euler = tuple(R(a) for a in local_rot)
    return obj


def hand_offset(rig, s):
    """Lokale positie van de hand t.o.v. de elleboog-empty (rustpose)."""
    return Vector((0.02 * s, -0.05, -0.19))
