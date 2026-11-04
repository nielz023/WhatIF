"""Raamwerk voor video 3 "What IF There Were NO RULES?" (bovenop anim/v2/v2.py en anim/lib/scene.py).

Nieuw t.o.v. video 2 (lessen uit de analyse van video 2, zie project memory lessen-video2):
- cast_v3 (glans 2) en dieren; elk hoofdpersonage-variant krijgt randlicht;
- HUD rechtsboven "DAY 3  ·  RULES: 0" (wit met donkere rand, nooit rood), aftelklok midden boven;
- knippen met een vaste shotlijst: S.cuts([3, 2.5, ...]) -> [(t0, t1), ...];
- belichting 0 tot +0,3 (geen -0,2 meer), echt wit in beeld; nachtscènes met blauw vullicht;
- AUTOMATISCHE KWALITEITSCHECK vóór elke render (S.qc in finish): shots > 6 s, hoofden uit beeld of ogen op de
  onderrand, camera in een object of muur, achterhoofd vlak voor de lens, hoofden door elkaar, handen door het
  eigen hoofd, voeten onder de vloer, HUD-overlap, rode HUD, gaten zonder camera. Schrijft out/<code>/qc.txt.
  Met WHATIF_QC_STRICT=1 stopt --render bij een fout.

    from v3 import *
    S = Scene3("n01", "stad", "nacht")
    held = S.actor("hoofdpersonage_pyjama", (0, -4, 0), 0)
    sh = S.cuts([3.0, 2.5, 1.5])
    ...
    S.finish(length=sh[-1][1])
"""
import math
import os
import sys

os.environ.setdefault("WHATIF_CAST", "cast_v3")
os.environ.setdefault("WHATIF_FPS", "30")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "v2"))
from v2 import *  # noqa: E402,F401,F403
import v2 as _v2  # noqa: E402

HUD_Y = (1.0, 0.86, 0.25, 1)          # geel voor een veranderend getal (leesbaar met donkere rand)
DOT = "  ·  "


def rules_fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


class Scene3(_v2.Scene2):
    def __init__(self, code, set_name=None, variant=None, samples=None, exposure=0.15, night=False):
        super().__init__(code, set_name, variant, samples=samples)
        self.exposure = exposure
        self.night = night
        self.allow_long = set()          # shotnummers die bewust > 6 s mogen (bijna nooit)
        self.no_hud = []                 # (t0, t1) waar geen HUD mag staan (flashback, kaart, twist)
        self.qc_skip = set()             # namen van figuren die niet in beeld hoeven (silhouetten e.d.)

    # -- figuren ---------------------------------------------------------------
    def actor(self, name, loc=(0, 0, 0), rot=0.0, energy=1.0, rim=None, frozen=False, **kw):
        if rim is None:
            rim = name.startswith("hoofdpersonage")
        ch = super().actor(name, loc, rot, energy, rim=rim, frozen=frozen, **kw)
        return ch

    # -- montage-ritme -----------------------------------------------------------
    def turn(self, ch, t0, t1, rot, loc=None, via=None):
        """Omdraaien zonder verrassingen: draait de korte kant op (of via=+1/-1 een vaste kant) en splitst
        grote draaien in stukken < 120 graden, anders kiest _near soms de verkeerde kant (rug naar camera)."""
        cur = math.degrees(self._rot_now(ch, t0))
        d = (rot - cur + 180.0) % 360.0 - 180.0
        if via is not None and d * via < 0:
            d += 360.0 * via
        n = max(1, int(abs(d) // 120) + 1) if abs(d) > 120 else 1
        for k in range(n):
            a, b = t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n
            _v2.Scene2.turn(self, ch, a, b, cur + d * (k + 1) / n, loc if k == n - 1 else None)

    def cuts(self, durs, t0=0.0):
        """Shotlijst: [3.0, 2.5, ...] -> [(t0, t1), ...] aaneengesloten vanaf t0."""
        out, t = [], t0
        for d in durs:
            out.append((t, t + d))
            t += d
        self._cutlist = getattr(self, "_cutlist", []) + out
        return out

    def whiteflash(self, t, frames=2):
        """Witte flits-frame tussen twee shots (flash-forwards)."""
        self.card("", t - frames / 48, t + frames / 48, dim=1.0, bg=(1, 1, 1), fin=0, fout=1)
        self.sfx("sfx_whoosh", t - 0.15, 0.5)

    def black(self, t0, t1, body="", size=110):
        """Zwart beeld (tijdsprongkaart, harde cut naar zwart). Geen HUD in dit stuk."""
        self.card(body, t0, t1, size=size, dim=1.0, bg=(0, 0, 0), fin=0, fout=0)
        self.no_hud.append((t0, t1))

    # -- HUD ---------------------------------------------------------------------
    def counter(self, label, rules, t0=0.3, t1=None, tick=True, big=False):
        """'DAY 3  ·  RULES: 0' rechtsboven. rules = getal, tekst of lijst [(t, waarde), ...]
        (bij elke verandering verschijnt het getal opnieuw met een pop en een tik).
        big=True: eerst 1,5 s groot in het midden (tijdsprong), daarna rechtsboven."""
        t1 = t1 if t1 is not None else 10 ** 6
        seq = rules if isinstance(rules, list) else [(t0, rules)]
        if big:
            v = seq[0][1]
            self.texts.append(dict(body=f"{label}{DOT}RULES: {rules_fmt(v)}", t0=t0, t1=t0 + 1.5, loc=(0.5, 0.55),
                                   size=120, color=HUD_W, anchor=("CENTER", "CENTER"), pop=True, hud=True))
            self.sfx("sfx_hud_tik", t0, 0.7)
            t0 = t0 + 1.5
            seq = [(max(t, t0), v) for t, v in seq]
        for i, (ta, v) in enumerate(seq):
            tb = seq[i + 1][0] if i + 1 < len(seq) else t1
            self.texts.append(dict(body=f"{label}{DOT}RULES: {rules_fmt(v)}", t0=ta, t1=tb, loc=(0.965, 0.94), size=72,
                                   color=HUD_W if i == 0 else HUD_Y, anchor=("RIGHT", "TOP"), pop=(i == 0 or True), hud=True))
            if tick and (i > 0 or not big):
                self.sfx("sfx_hud_tik", ta, 0.6)
        self._hud_t1 = t1

    def rolling(self, label, start, end, t0, dur, t1=None):
        """Getal dat snel omhoog rolt (jaar 10: 6,300 -> 48,000+) en stopt met een pop."""
        steps = 18
        seq = []
        for k in range(steps):
            w = (k / (steps - 1)) ** 0.6
            seq.append((t0 + dur * k / (steps - 1), int(start + (end - start) * w)))
        seq[-1] = (t0 + dur, f"{end:,}+")
        for i, (ta, v) in enumerate(seq):
            tb = seq[i + 1][0] if i + 1 < len(seq) else (t1 if t1 is not None else 10 ** 6)
            self.texts.append(dict(body=f"{label}{DOT}RULES: {rules_fmt(v)}", t0=ta, t1=tb, loc=(0.965, 0.94), size=72,
                                   color=HUD_Y if i == len(seq) - 1 else HUD_W, anchor=("RIGHT", "TOP"),
                                   pop=(i == 0 or i == len(seq) - 1), hud=True))
        self.sfx("sfx_hud_tik", t0 + dur, 0.8)

    def countdown(self, start_sec, t0, t1, rate=1.0, jumps=None):
        """'MIDNIGHT IN 11:42:10' midden boven. jumps = [(t, seconden_tot_middernacht), ...] springt per shot."""
        def fmt(s):
            s = max(0, int(s))
            return f"MIDNIGHT IN {s // 3600}:{(s // 60) % 60:02d}:{s % 60:02d}"
        pts = sorted(jumps or [(t0, start_sec)])

        def f(t):
            base_t, base_s = pts[0]
            for pt, ps in pts:
                if pt <= t:
                    base_t, base_s = pt, ps
            return fmt(base_s - (t - base_t) * rate)
        cur, ts = f(t0), t0
        t = t0
        step = 1 / 30
        first = True
        while t < t1:
            t = min(t1, t + step)
            v = f(t) if t < t1 else None
            if v != cur:
                self.texts.append(dict(body=cur, t0=ts, t1=t, loc=(0.5, 0.95), size=58, color=HUD_W,
                                       anchor=("CENTER", "TOP"), pop=first, hud=True))
                first, cur, ts = False, v, t

    def real(self, t0, t1):
        """'THIS PART IS REAL' rechtsonder (wit/cyaan met donkere rand)."""
        self.texts.append(dict(body="THIS PART IS REAL", t0=t0, t1=t1, loc=(0.965, 0.07), size=46, color=CYAN,
                               anchor=("RIGHT", "BOTTOM"), pop=True))

    def screen_text(self, body, t0, t1, size=86, y=0.5, color=(1.0, 0.22, 0.18, 1)):
        """Tekst op een scherm in de wereld als grafische laag (DETAIL-shots van de telefoon/tv). Rood mag hier: decor."""
        self.texts.append(dict(body=body, t0=t0, t1=t1, loc=(0.5, y), size=size, color=color,
                               anchor=("CENTER", "CENTER"), pop=False))

    # -- camera-hulpjes --------------------------------------------------------------
    def follow(self, ch, offset, look_up=0.0, lens=35, lag=0.0, look_offset=(0, 0, 0)):
        """Camera die een figuur volgt (wereld-offset t.o.v. zijn wortel), voor tracking-shots."""
        def fn(t):
            M = self._root_matrix(ch, max(0.0, t - lag))
            p = M.translation
            loc = p + Vector(offset)
            tgt = p + Vector((0, 0, 1.2 * ch.rig.scale.z + look_up)) + Vector(look_offset)
            return loc, tgt, lens
        return fn

    def shake(self, amp=1.2):
        return lambda t: amp

    # -- afronden ------------------------------------------------------------------
    def pre_finish(self):
        super().pre_finish()
        # HUD weg bij kaarten/zwart/flashbacks
        for d in self.texts:
            if not d.get("hud"):
                continue
            for a, b in self.no_hud:
                if d["t0"] < b and d["t1"] > a:
                    if d["t0"] >= a and d["t1"] <= b:
                        d["t1"] = d["t0"]
                    elif d["t0"] < a:
                        d["t1"] = a
                    else:
                        d["t0"] = b

    def post_cams(self):
        super().post_cams()
        sc = self.sc
        sc.view_settings.exposure = self.exposure + (0.15 if _v2.ENGINE == "EEVEE" else 0.0)
        if os.environ.get("WHATIF_NOQC") != "1":
            self.qc()

    # -- automatische kwaliteitscheck -------------------------------------------------
    def qc(self):
        from bpy_extras.object_utils import world_to_camera_view
        sc = self.sc
        dg = bpy.context.evaluated_depsgraph_get()
        issues = []

        def warn(kind, t, msg):
            issues.append((kind, round(t, 2), msg))

        people = getattr(self, "all_cast", None) or self.cast
        # 1. shotlengte en gaten
        shots = sorted(self.shots, key=lambda s: s[0])
        if shots and shots[0][0] > 0.01:
            warn("GAT", 0.0, "eerste shot begint pas op %.2f s" % shots[0][0])
        for k, (t0, t1, cam) in enumerate(shots):
            if t1 - t0 > 6.05 and k not in self.allow_long:
                hidden = any(c["t0"] <= t0 and c["t1"] >= t1 for c in self.cards if c.get("dim", 0) >= 1.0)
                if not hidden:
                    warn("SHOT>6s", t0, "%s duurt %.1f s" % (cam.name, t1 - t0))
        # 2. per shot een paar momenten: hoofden, camera in object, achterhoofd voor de lens
        for t0, t1, cam in shots:
            dur = t1 - t0
            if dur < 0.05:
                continue
            if any(c["t0"] <= t0 + 0.05 and c["t1"] >= t1 - 0.05 for c in self.cards if c.get("dim", 0) >= 1.0):
                continue          # shot helemaal achter een zwarte/witte kaart
            for w in (0.15, 0.5, 0.85):
                t = t0 + dur * w
                sc.frame_set(F(t))
                sc.camera = cam
                dg = bpy.context.evaluated_depsgraph_get()
                cp = cam.matrix_world.translation.copy()
                # camera in een object: straal naar 6 kanten, raakt binnenkant (normaal wijst weg) binnen 2 m
                inside = 0
                for d in (Vector((1, 0, 0)), Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, -1, 0)), Vector((0, 0, 1)), Vector((0, 0, -1))):
                    hit, loc, nrm, _i, ob, _m = sc.ray_cast(dg, cp, d, distance=2.0)
                    if hit and nrm.dot(d) > 0.2 and not (ob and ob.name.startswith(("Irradiance", "Randlicht"))):
                        inside += 1
                if inside >= 3:
                    warn("CAMERA_IN_OBJECT", t, cam.name)
                fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
                hit, loc, nrm, _i, ob, _m = sc.ray_cast(dg, cp, fwd, distance=0.25)
                if hit:
                    warn("OBJECT_VOOR_LENS", t, "%s raakt %s op %.2f m" % (cam.name, ob.name if ob else "?", (loc - cp).length))
                for ch in people:
                    if ch.name in self.qc_skip:
                        continue
                    kids = [o for o in ch.rig.children_recursive if o.type == "MESH"]
                    if not kids or all(o.hide_render for o in kids):
                        continue
                    hc = self.headpos(ch, t)
                    r = ch.J["head_r"].z * ch.rig.scale.z
                    v = world_to_camera_view(sc, cam, hc)
                    if v.z <= 0:
                        continue
                    top = world_to_camera_view(sc, cam, hc + Vector((0, 0, r)))
                    eye = world_to_camera_view(sc, cam, hc + Vector((0, 0, r * 0.1)))
                    size = abs(top.y - v.y)                      # straal van het hoofd in beeldhoogtes
                    if not (-size <= v.x <= 1 + size and -size <= v.y <= 1 + size):
                        continue
                    if size < 0.03:
                        continue                                 # klein figuurtje in de verte
                    pb = ch.rig.pose.bones["head"]
                    R3 = ch.rig.matrix_world.to_3x3() @ (pb.matrix.to_3x3() @ pb.bone.matrix_local.to_3x3().inverted())
                    fwd = (R3 @ Vector((0, -1, 0))).normalized()
                    tocam = (cp - hc).normalized()
                    facing = fwd.dot(tocam)
                    nm = f"{cam.name}: {ch.name}"
                    if size > 0.55:
                        warn("HOOFD_TE_GROOT", t, f"{nm} vult het beeld (straal {size:.2f})")
                    if facing < -0.35 and size > 0.12:
                        warn("ACHTERHOOFD", t, f"{nm} staat met zijn rug/achterhoofd naar de camera")
                    if 0 <= v.x <= 1 and top.y > 1.0 and v.y < 1.0:
                        warn("HOOFD_AFGESNEDEN", t, f"{nm}: kruin boven de beeldrand")
                    if 0 <= v.x <= 1 and eye.y < 0.15 and size > 0.06:
                        warn("OGEN_ONDERRAND", t, f"{nm}: ogen op {eye.y * 100:.0f}% hoogte")
                    if (0 <= v.x <= 1) and (v.x < 0.03 or v.x > 0.97) and size > 0.12:
                        warn("HOOFD_RAND", t, f"{nm}: hoofd half uit beeld opzij")
        # 3. clipping-heuristiek: hoofden door elkaar, hand door eigen hoofd, voeten onder de vloer
        step = max(1, int(FPS / 4))
        for f in range(1, F(self.length), step):
            sc.frame_set(f)
            t = (f - 1) / FPS
            heads = []
            for ch in people:
                kids = [o for o in ch.rig.children_recursive if o.type == "MESH"]
                if not kids or all(o.hide_render for o in kids):
                    continue
                pb = ch.rig.pose.bones
                M = ch.rig.matrix_world
                hb = M @ pb["head"].head
                hr = ch.J["head_r"].z * ch.rig.scale.z
                hcen = hb + Vector((0, 0, hr * 0.9))
                heads.append((ch, hcen, hr))
                for side in ("L", "R"):
                    bn = f"hand.{side}" if f"hand.{side}" in pb else None
                    if bn:
                        hp = M @ pb[bn].tail
                        if (hp - hcen).length < hr * 0.6:
                            warn("HAND_DOOR_HOOFD", t, ch.name)
            for i in range(len(heads)):
                for j in range(i + 1, len(heads)):
                    a, b = heads[i], heads[j]
                    if (a[1] - b[1]).length < (a[2] + b[2]) * 0.75:
                        warn("HOOFDEN_DOOR_ELKAAR", t, f"{a[0].name} / {b[0].name}")
        # 4. HUD: overlap en kleur
        hud = [d for d in self.texts if d.get("hud") and d["t1"] > d["t0"]]
        for i in range(len(hud)):
            a = hud[i]
            if tuple(a["color"][:3]) == tuple(RED[:3]):
                warn("HUD_ROOD", a["t0"], a["body"])
            for j in range(i + 1, len(hud)):
                b = hud[j]
                if tuple(a["loc"]) == tuple(b["loc"]) and a["t0"] < b["t1"] - 1e-3 and b["t0"] < a["t1"] - 1e-3:
                    warn("HUD_OVERLAP", max(a["t0"], b["t0"]), f"'{a['body']}' en '{b['body']}'")
        # samenvatten (zelfde soort + shot niet 20 keer herhalen)
        seen, rows = set(), []
        for kind, t, msg in issues:
            k = (kind, msg.split(" op ")[0])
            if k in seen:
                continue
            seen.add(k)
            rows.append(f"{kind:20s} t={t:6.2f}  {msg}")
        os.makedirs(self.out, exist_ok=True)
        with open(os.path.join(self.out, "qc.txt"), "w") as fh:
            fh.write("\n".join(rows) + ("\n" if rows else "OK\n"))
        print("QC %s: %d meldingen" % (self.code, len(rows)))
        for r in rows:
            print("  QC", r)
        self.qc_rows = rows
        if rows and self.args.render and os.environ.get("WHATIF_QC_STRICT") == "1":
            raise SystemExit("QC-fouten, render afgebroken (zie qc.txt)")
        sc.frame_set(1)


# ---------------------------------------------------------------------------
# Kleine hulpjes voor de sets van video 3
# ---------------------------------------------------------------------------
def emission_key(mat_name, t, strength, interp="CONSTANT"):
    """Emission Strength van een (set-)materiaal op tijd t (verkeerslichten, ramen per blok, schermen)."""
    m = bpy.data.materials.get(mat_name)
    if m is None or not m.node_tree:
        print("LET OP: materiaal ontbreekt", mat_name)
        return
    for n in m.node_tree.nodes:
        sock = None
        if n.type == "EMISSION":
            sock = n.inputs["Strength"]
        elif n.type == "BSDF_PRINCIPLED" and "Emission Strength" in n.inputs:
            sock = n.inputs["Emission Strength"]
        if sock is not None:
            sock.default_value = strength
            sock.keyframe_insert("default_value", frame=F(t))
    if m.node_tree.animation_data and m.node_tree.animation_data.action:
        for fc in A._fcurves(m.node_tree):
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def light_key(obj, t, energy, interp="CONSTANT"):
    obj.data.energy = energy
    obj.data.keyframe_insert("energy", frame=F(t))
    for fc in A._fcurves(obj.data):
        for kp in fc.keyframe_points:
            kp.interpolation = interp


def swap(obj_off, obj_on, t):
    """Op tijd t: obj_off weg, obj_on zichtbaar (met kinderen). Vóór t andersom."""
    visible(obj_on, 0, False)
    visible(obj_on, t, True)
    visible(obj_off, 0, True)
    visible(obj_off, t, False)


def hide_all(prefix):
    for o in bpy.data.objects:
        if o.name.startswith(prefix):
            o.hide_render = True
            o.hide_viewport = True


def bike(S, ch, color=(0.15, 0.35, 0.75), name=None, lamp=False, jerrycan=False):
    """Fiets aan de wortel van ch (prop_bike), met eventueel een brandende lamp en een jerrycan aan het stuur."""
    name = name or f"Fiets_{ch.name}"
    b, crank = prop_bike(S, ch, name=name, color=color)
    extra = []
    if jerrycan:
        jc = T.box(name + "_jerrycan", (0.0, -0.52, 0.55), (0.16, 0.10, 0.22), S.mat("jerrycan", (0.15, 0.45, 0.9)),
                   bevel=0.02, ol=0.004)
        extra.append(jc)
    if lamp:
        lp = T.cyl(name + "_lamp", (0, -0.40, 0.78), 0.035, 0.05, S.mat("fietslamp", (1.0, 0.95, 0.8), 6.0),
                   rot=(90, 0, 0), seg=12, ol=0)
        extra.append(lp)
        lt = bpy.data.lights.new(name + "_lichtbundel", "SPOT")
        lt.energy, lt.spot_size, lt.color = 120, math.radians(45), (1.0, 0.93, 0.8)
        lo = bpy.data.objects.new(lt.name, lt)
        bpy.context.scene.collection.objects.link(lo)
        lo.location = (0, -0.45, 0.78)
        lo.rotation_euler = (math.radians(-75), 0, 0)
        extra.append(lo)
    for o in extra:
        o.parent = ch.rig
        o.matrix_parent_inverse = Matrix.Identity(4)
    return b, crank


def ride_path(S, ch, crank, t0, t1, pts, cadence=1.6, lean=18, stand=False, sway=0.0):
    """Fietsen langs punten: wortel beweegt mee (zonder loopcyclus), trappers draaien, lichte stuurzwaai."""
    pts = [Vector(p) for p in pts]
    segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(segs) or 1e-6
    frames = list(range(F(t0), F(t1) + 1))
    locs, rots = [], []
    for f in frames:
        t = (f - 1) / FPS
        u = (t - t0) / max(1e-3, t1 - t0)
        d = total * u
        for i, L in enumerate(segs):
            if d <= L or i == len(segs) - 1:
                w = min(1.0, d / L) if L > 0 else 1.0
                p = pts[i].lerp(pts[i + 1], w)
                dv = pts[i + 1] - pts[i]
                break
            d -= L
        locs.append(tuple(p))
        r = math.atan2(dv.x, -dv.y)
        rots.append((math.radians(sway * math.sin(t * cadence * 2 * math.pi)), 0.0, r))
    bake(ch.rig, "location", frames, locs, interp="BEZIER")
    bake(ch.rig, "rotation_euler", frames, rots, interp="BEZIER")
    ride(S, ch, crank, t0, t1, cadence=cadence, lean=lean)
    if stand:
        for f in range(F(t0), F(t1) + 1, 2):
            A.crouch(ch, f, -0.12, lean + 10)
    ch.last = None
