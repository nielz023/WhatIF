"""Raamwerk voor video 2 "What IF You Got 10x FASTER Every Day?" (bovenop anim/lib/scene.py).

Verschillen met video 1:
- glans-look: figuren via glans.character(), randlichten (oranje/blauw) per shot op het hoofdpersonage;
- 60 fps (WHATIF_FPS=60, standaard aan): animatie in 24-fps-tijd, Blender rekt op bij het renderen;
- render-engine via WHATIF_ENGINE (EEVEE standaard, CYCLES kan ook), afgesteld op de glans-look;
- HUD rechtsboven: DAY · SPEED, de echte klok (die tikt) en vanaf de twist AWAKE;
- ondertitels voor vertraagde stemmen (say_slow) en tellers onder de HUD (gauge2).

    from v2 import *
    S = Scene2("f01", "straat", "grijs")
    held = S.actor("hoofdpersonage", (0, 0, 0), 0)
    S.hud2(4, "1,000x", clock=clock(8 * 3600 + 58 * 60 + 40, 1 / 1000, dec=2))
    ...
    S.finish()
"""
import math
import os
import sys

os.environ.setdefault("SET_LOOK", "glans")
os.environ.setdefault("WHATIF_FPS", "60")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from scene import *  # noqa: E402,F401,F403
import scene as _scene  # noqa: E402
import glans as G  # noqa: E402

ENGINE = os.environ.get("WHATIF_ENGINE", "EEVEE")
HUD_W = (1, 1, 1, 1)
HUD_CLOCK = (0.80, 0.90, 1.0, 1)
HUD_AWAKE = (1.0, 0.55, 0.25, 1)
SUB = (1.0, 0.95, 0.75, 1)
DAYS = ["MON", "TUE"]


def hms(sec, dec=0, day="TUE"):
    """Kloktekst: 'TUE 08:58:40' of met decimalen 'TUE 08:59:59.99990'."""
    if dec:
        sec = math.floor(sec * 10 ** dec + 1e-6) / 10 ** dec
    h = int(sec // 3600)
    m = int(sec // 60) % 60
    s = sec - h * 3600 - m * 60
    if dec:
        ss = f"{s:0{3 + dec}.{dec}f}"
    else:
        ss = f"{int(s):02d}"
    return f"{day} {h:02d}:{m:02d}" + ("" if dec < 0 else f":{ss}")


def clock(start, rate=1.0, dec=0, day="TUE", t0=0.0, hhmm=False):
    """Klokfunctie voor de HUD: echte tijd = start + (t - t0) * rate (rate = 1/snelheid)."""
    def f(t):
        sec = start + max(0.0, t - t0) * rate
        if hhmm:
            return f"{day} {int(sec // 3600):02d}:{int(sec // 60) % 60:02d}"
        return hms(sec, dec, day)
    return f


def awake(start_h, rate=1.0, t0=0.0, secs=False):
    """AWAKE-teller (zijn eigen uren): start in uren, loopt met rate uur per seconde beeld."""
    def f(t):
        x = start_h + max(0.0, t - t0) * rate
        h = int(x)
        m = int((x - h) * 60 + 1e-6)
        if secs:
            s = int(((x - h) * 60 - m) * 60 + 1e-6)
            return f"AWAKE {h:02d}:{m:02d}:{s:02d}"
        return f"AWAKE {h:02d}:{m:02d}"
    return f


# extra houdingen voor deze video (zelfde als cast/cast_10x_poses.py)
A.POSES.update({
    "rennen": dict(L=((0.12, 0.65, -0.55), (0.05, 0.75, 0.62), None),
                   R=((0.12, -0.55, -0.75), (0.08, 0.15, -0.95), None),
                   body={"spine": (12, 0, 0), "chest": (6, 0, 0), "head": (-14, 0, 0)}),
    "sprint": dict(L=((0.15, -0.6, -0.7), (0.1, 0.2, -0.95), None),
                   R=((0.12, 0.7, -0.45), (0.05, 0.6, 0.78), None),
                   body={"spine": (18, 0, 0), "chest": (8, 0, 0), "head": (-18, 0, 0)}),
    "schrijven": dict(L=((0.22, 0.85, -0.35), (0.0, 0.95, 0.2), None), R=A.REST, body={"head": (-6, 0, 0)}),
    "stuur": dict(L=((0.25, 0.8, -0.45), (-0.05, 0.98, 0.15), None), body={"spine": (4, 0, 0)}),
    "cadeau": dict(L=((0.2, 0.6, -0.75), (-0.4, 0.9, 0.12), None), body={"head": (-4, 0, 0)}),
    "lachen_hol": dict(L=((0.35, 0.25, -0.85), (-0.7, 0.6, 0.1), None),
                       body={"spine": (-6, 0, 0), "chest": (-8, 0, 0), "head": (-16, 0, 6)}),
})


def run_feet(front="L", lift=0.22, reach=0.2, back=0.26):
    """Voeten voor beat(feet=...): voorste voet vooruit en omhoog, achterste hoog achter."""
    f = ((0, reach, lift), (0, -back, lift * 1.15))
    return f if front == "L" else (f[1], f[0])


def run_pose(S, ch, t, front="L", amount=1.0, lift=0.22, reach=0.2, back=0.26, face="inspanning", look=None, pose="rennen"):
    """Bevroren midden in een sprint (cast_10x_poses.run_legs)."""
    S.beat(ch, t, pose, amount=amount, face=face, look=look, crouch=(-0.02, 0))
    rear = "R" if front == "L" else "L"
    A.foot(ch, F(t), front, loc=(0, reach, lift), rot=(-25, 0, 0))
    A.foot(ch, F(t), rear, loc=(0, -back, lift * 1.15), rot=(70, 0, 0))


class Scene2(Scene):
    def __init__(self, code, set_name=None, variant=None, samples=None):
        super().__init__(code, set_name, variant, samples=samples or (64 if ENGINE == "EEVEE" else 48))
        # het set-script zette randlichten op zijn eigen (inmiddels verwijderde) hoofdpersonage
        for o in [o for o in bpy.data.objects if o.name.startswith("Randlicht_")]:
            bpy.data.objects.remove(o)
        self.sc.render.use_compositing = False
        self.heroes = []
        self.room = ROOMS.get(set_name)

    # -- figuren -------------------------------------------------------------
    def actor(self, name, loc=(0, 0, 0), rot=0.0, energy=1.0, rim=None, frozen=False, **kw):
        """frozen=True: iemand in de (voor hem) stilstaande wereld: niet knipperen, niet ademen."""
        ch = super().actor(name, loc, rot, energy, **kw)
        ch.frozen = frozen
        G.character(ch)
        if rim if rim is not None else name == "hoofdpersonage":
            self.heroes.append(ch)
        return ch

    def run(self, ch, t0, t1, pts, stride=1.1, lift=0.2, lean=14, ease_in=0.15, ease_out=0.15, arms=1.0, end_rot=None):
        """Rennen langs punten: zoals walk(), maar met (bijna) constante snelheid, hoge knieën,
        voorover leunen en pompende armen. ease_in/out = deel van de tijd om op gang te komen/af te remmen."""
        pts = [Vector(p) for p in pts]
        segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
        total = sum(segs) or 1e-6
        dur = t1 - t0
        speed = total / dur
        period = 2 * stride / max(speed, 1e-3)

        def at_dist(d):
            for i, L in enumerate(segs):
                if d <= L or i == len(segs) - 1:
                    w = min(1.0, d / L) if L > 0 else 1.0
                    return pts[i].lerp(pts[i + 1], w), (pts[i + 1] - pts[i])
                d -= L
            return pts[-1], pts[-1] - pts[-2]

        # afstand als functie van u: lineair, met zachte aanloop/uitloop
        def dist(u):
            a, b = max(ease_in, 1e-3), max(ease_out, 1e-3)
            vmax = 1.0 / (1 - a / 2 - b / 2)
            if u < a:
                return vmax * u * u / (2 * a)
            if u > 1 - b:
                return 1 - vmax * (1 - u) ** 2 / (2 * b)
            return vmax * (a / 2 + (u - a))

        frames = list(range(F(t0), F(t1) + 1))
        locs, rots = [], []
        M0 = self._root_matrix(ch, t0)
        rot_prev = r0 = self._rot_now(ch, t0)
        A.place(ch, F(t0) - 1, tuple(M0.translation), math.degrees(rot_prev))
        for f in frames:
            t = (f - 1) / FPS
            u = min(1.0, max(0.0, (t - t0) / dur))
            p, d = at_dist(total * dist(u))
            locs.append(tuple(p))
            r = math.atan2(d.x, -d.y)
            while r - rot_prev > math.pi:
                r -= 2 * math.pi
            while r - rot_prev < -math.pi:
                r += 2 * math.pi
            rot_prev = r
            w = smooth(t0 - 0.05, t0 + 0.25, t)
            rots.append((0.0, 0.0, r0 + (r - r0) * w))
        bake(ch.rig, "location", frames, locs, interp="BEZIER")
        bake(ch.rig, "rotation_euler", frames, rots, interp="BEZIER")
        for f in frames:
            t = (f - 1) / FPS
            u = (t - t0) / dur
            env = smooth(0, 0.08, u) * (1 - smooth(0.92, 1.0, u))
            ph = ((t - t0) / period) % 1.0
            for side, off in (("L", 0.0), ("R", 0.5)):
                q = (ph + off) % 1.0
                if q < 0.4:                              # standbeen
                    y = stride * (0.5 - q / 0.4) * 0.5
                    z = 0.0
                else:                                    # zwaaibeen: knie hoog
                    w = (q - 0.4) / 0.6
                    y = stride * (-0.5 + w) * 0.5
                    z = math.sin(w * math.pi) * lift
                A.foot(ch, f, side, (0, y * env, z * env), (-35 * math.sin(q * 2 * math.pi) * env, 0, 0))
            sw = math.sin(ph * 2 * math.pi) * arms * env
            A.aim_arm(ch, f, "L", (0.15, 0.55 * sw, -0.8), (0.05, 0.75 + 0.2 * sw, 0.45))
            A.aim_arm(ch, f, "R", (0.15, -0.55 * sw, -0.8), (0.05, 0.75 - 0.2 * sw, 0.45))
            bob = abs(math.cos(ph * 2 * math.pi)) * 0.05 * env
            A.crouch(ch, f, 0.04 + bob, lean * env)
            ch.pb["spine"].rotation_euler = Euler((math.radians(lean * 0.4 * env), math.radians(6 * sw), 0))
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

    # -- HUD -------------------------------------------------------------------
    def _ticking(self, fn, t0, t1, loc, size, color, step=1 / 24):
        """Tekst die verandert (klok): één strook per nieuwe waarde, alleen de eerste springt in beeld.
        Wordt pas in finish() uitgerekend, als de lengte bekend is."""
        self._ticks = getattr(self, "_ticks", []) + [(fn, t0, t1, loc, size, color, step)]

    def _ticking_now(self, fn, t0, t1, loc, size, color, step):
        t1 = min(t1 if t1 is not None else self.length, self.length)
        if not callable(fn):
            self.texts.append(dict(body=fn, t0=t0, t1=t1, loc=loc, size=size, color=color,
                                   anchor=("RIGHT", "TOP"), pop=True, hud=True))
            return
        cur, ts, first = fn(t0), t0, True
        t = t0
        while t < t1:
            t = min(t1, t + step)
            v = fn(t) if t < t1 else None
            if v != cur:
                self.texts.append(dict(body=cur, t0=ts, t1=t, loc=loc, size=size, color=color,
                                       anchor=("RIGHT", "TOP"), pop=first, hud=True))
                first, cur, ts = False, v, t

    def hud2(self, day, speed, clock=None, t0=0.3, t1=None, awake=None, awake_t0=None, tick=True, step=None):
        """HUD rechtsboven: 'DAY 4 · 1,000x', daaronder de echte klok en eventueel AWAKE.
        clock/awake = tekst of functie van t (zie clock() en awake())."""
        t1 = t1 if t1 is not None else 10 ** 6
        self.texts.append(dict(body=f"DAY {day}  ·  {speed}", t0=t0, t1=t1, loc=(0.965, 0.94), size=78,
                               color=HUD_W, anchor=("RIGHT", "TOP"), pop=True, hud=True))
        self._hud_t1 = t1
        if clock is not None:
            self._ticking(clock, t0 + 0.1, t1, (0.965, 0.855), 54, HUD_CLOCK, step or 1 / 24)
        if awake is not None:
            self._ticking(awake, awake_t0 if awake_t0 is not None else t0 + 0.2, t1, (0.965, 0.785), 50,
                          HUD_AWAKE, step or 1 / 24)
        if tick:
            self.sfx("sfx_hud_tik", t0, 0.6)

    def gauge2(self, body, t0, t1, color=GOLD, size=56, row=0, step=1 / 24):
        """Extra teller onder de HUD (CRANES, km/h, MOVED); body mag een functie van t zijn."""
        self._ticking(body, t0, t1, (0.965, 0.715 - row * 0.07), size, color, step)

    def sub(self, who, body, t0, t1):
        """Ondertitel onderaan voor een vertraagde stem."""
        self.texts.append(dict(body=f'{who}: "{body}"', t0=t0, t1=t1, loc=(0.5, 0.075), size=58, color=SUB,
                               anchor=("CENTER", "BOTTOM"), pop=True))

    def say_slow(self, line_id, speaker, who=None, gap=0.3, at=None, sub=None, subtitle=None, gain=1.1):
        """Vertraagde, verlaagde stem (zoals hij de wereld hoort) met ondertitel."""
        path = os.path.join(AUDIO, line_id[:3], f"{line_id}_{speaker}_traag.mp3")
        dur = audio_len(path)
        t0 = at if at is not None else self.t + gap
        self.voice.append((os.path.relpath(path, AUDIO), t0))
        t1 = t0 + dur
        self.t = max(self.t, t1)
        if who is not None:
            A.lipsync(who, path, F(t0), gain=gain)
        if subtitle:
            self.sub(sub or speaker.upper(), subtitle, t0, t1 + 0.4)
        return t0, t1

    # -- afronden ----------------------------------------------------------------
    def eyes_closed(self, ch, t0, t1):
        """Ogen dicht (slapen) van t0 tot t1; gaat boven het automatische knipperen."""
        self._closed = getattr(self, "_closed", []) + [(ch, t0, t1)]

    def _apply_closed(self):
        for ch, t0, t1 in getattr(self, "_closed", []):
            for fc in A._fcurves(ch.rig):
                if fc.data_path == '["knipper"]':
                    for kp in [kp for kp in fc.keyframe_points if F(t0) - 1 <= kp.co.x <= F(t1) + 1][::-1]:
                        fc.keyframe_points.remove(kp)
            for f, v in ((F(t0) - 1, 0.0), (F(t0), 1.0), (F(t1), 1.0), (F(t1) + 2, 0.0)):
                A.key_prop(ch.rig, "knipper", v, max(1, f))

    def pre_finish(self):
        for tk in getattr(self, "_ticks", []):
            self._ticking_now(*tk)
        for d in self.texts:
            if d["t1"] is None or d["t1"] > self.length:
                d["t1"] = self.length
        self.cast = [ch for ch in self.cast if not getattr(ch, "frozen", False)]

    def post_cams(self):
        self._apply_closed()
        self._rim()
        self._engine()

    def _rim(self):
        """Oranje en blauw randlicht schuin achter elk hoofdpersonage, per shot opnieuw geplaatst
        vanuit de camera van dat shot (light linking: alleen op de figuur)."""
        for ch in self.heroes:
            coll = ch.rig.users_collection[0]
            for tag, s_, col, e in (("oranje", -1, (1.0, 0.33, 0.045), 700), ("blauw", 1, (0.047, 0.24, 1.0), 800)):
                ld = bpy.data.lights.new(f"Randlicht_{tag}_{ch.name}", "AREA")
                ld.shape, ld.size, ld.energy, ld.color = "DISK", 0.6, e, col
                lo = bpy.data.objects.new(ld.name, ld)
                lo.visible_camera = False
                lo.light_linking.receiver_collection = coll
                bpy.context.scene.collection.objects.link(lo)
                for t0, t1, cam in self.shots:
                    p = self.headpos(ch, t0) + Vector((0, 0, -0.15))
                    cm = self._cam_eval([c for c in self.cams if c["name"] == cam.name][0], t0, t1)[0]
                    d = Vector(cm) - p
                    d.z = 0
                    if d.length < 1e-3:
                        d = Vector((0, -1, 0))
                    d.normalize()
                    side = Vector((-d.y, d.x, 0))
                    sc = ch.rig.scale.z
                    lo.location = p - d * 1.6 * sc + side * s_ * 1.4 * sc + Vector((0, 0, 0.6 * sc))
                    lo.rotation_euler = (p - lo.location).to_track_quat("-Z", "Y").to_euler()
                    for path in ("location", "rotation_euler"):
                        lo.keyframe_insert(path, frame=F(t0))
                for fc in A._fcurves(lo):
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"

    def _engine(self):
        sc = self.sc
        for o in bpy.data.objects:
            if o.type == "LIGHT":
                o.visible_camera = False
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
        if ENGINE == "WORKBENCH":              # snelle layout-stills in de container
            sc.render.engine = "BLENDER_WORKBENCH"
            sh = sc.display.shading
            sh.light, sh.color_type = "STUDIO", "MATERIAL"
            sh.show_shadows, sh.show_cavity = True, True
            sc.view_settings.view_transform = "Standard"
            sc.view_settings.look = "None"
            for o in bpy.data.objects:          # workbench kent visible_camera niet (verborgen voormuur)
                if not o.visible_camera and not (o.animation_data and o.animation_data.action):
                    o.hide_render = True
            return
        if ENGINE == "CYCLES":
            sc.render.engine = "CYCLES"
            sc.cycles.device = "GPU" if os.environ.get("SET_GPU") == "1" else "CPU"
            sc.cycles.samples = self.args.samples
            sc.cycles.use_denoising = True
            return
        eevee_glans(sc, self.args.samples, self.room, bake=self.args.render or os.environ.get("WHATIF_BAKE") == "1")
        sc.view_settings.exposure += 0.15     # EEVEE is iets minder warm dan Cycles
        sc.render.use_motion_blur = False      # 60 fps; bewegingsonscherpte kost in EEVEE een veelvoud aan rendertijd


# EEVEE afgesteld op de glans-look (rendertest op niels' pc, keuken dag 1, 1080p: ~1,2 s per beeld).
# Het korrelige zat in de schaduwen: schaduw-jitter haalt dat weg; een irradiance volume net binnen de
# muren geeft de warme kaatsing van Cycles. Het bakken kost ~10 s per scène en gebeurt vlak voor het renderen.
def eevee_glans(sc, samples=32, room=None, bake=True):
    e = sc.eevee
    sc.render.engine = "BLENDER_EEVEE"
    e.taa_render_samples = samples
    e.use_shadows = True
    e.shadow_ray_count = 3
    e.shadow_step_count = 6
    e.shadow_resolution_scale = 1.0
    e.use_raytracing = True
    e.ray_tracing_method = "SCREEN"
    rt = e.ray_tracing_options
    rt.resolution_scale = "2"
    rt.use_denoise = rt.denoise_spatial = rt.denoise_temporal = rt.denoise_bilateral = True
    rt.screen_trace_quality = 0.5
    rt.trace_max_roughness = 0.5
    e.use_fast_gi = True
    e.fast_gi_method = "GLOBAL_ILLUMINATION"
    e.fast_gi_distance = 0.0
    e.fast_gi_resolution = "2"
    e.fast_gi_ray_count = 2
    e.fast_gi_step_count = 8
    e.fast_gi_quality = 0.25
    e.gi_diffuse_bounces = 3
    e.indirect_light_intensity = 1.4
    for ob in sc.objects:
        if ob.type == "LIGHT":
            ob.data.use_shadow = True
            ob.data.use_shadow_jitter = True
            ob.data.shadow_jitter_overblur = 10.0
    if room:
        center, half = room
        pd = bpy.data.lightprobes.new("Irradiance", "VOLUME")
        pv = bpy.data.objects.new("Irradiance_volume", pd)
        sc.collection.objects.link(pv)
        pv.location, pv.scale = center, half
        pd.resolution_x, pd.resolution_y, pd.resolution_z = 24, 21, 13
        pd.bake_samples = 1024
        if bake:
            for o in bpy.context.view_layer.objects:
                o.select_set(False)
            bpy.context.view_layer.objects.active = pv
            pv.select_set(True)
            bpy.ops.object.lightprobe_cache_bake(subset="ALL")


# binnen-sets: irradiance volume net binnen de muren (midden, halve maten)
ROOMS = {
    "keuken": ((0, 0, 1.3), (2.3, 2.0, 1.2)),
    "slaapkamer": ((0, 0, 1.3), (2.0, 1.8, 1.2)),
    "gymzaal": ((0, 0, 3.8), (13.8, 8.3, 3.7)),
}
