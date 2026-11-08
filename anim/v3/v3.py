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
    def actor(self, name, loc=(0, 0, 0), rot=0.0, energy=1.0, rim=None, frozen=False, cane=False, **kw):
        if name == "opa" and not cane:                   # stok alleen als hij staat/loopt (cane=True), anders door tafels
            kw["drop"] = tuple(kw.get("drop") or ()) + ("wandelstok",)
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

    def _build_cams(self):
        if os.environ.get("WHATIF_LIGHT", "1") != "0":
            # filmische scherptediepte: (half)close-ups (lens >= 30) krijgen f/2.8-4 met focus op het richtpunt
            for c in self.cams:
                if c["dof"] is None and not c["fn"]:
                    lenses = [c["a"][2]] + ([c["b"][2]] if c["b"] else [])
                    if all(isinstance(x, (int, float)) for x in lenses) and min(lenses) >= 30:
                        c["dof"] = 2.8 if min(lenses) >= 40 else 4.0
        super()._build_cams()

    def post_cams(self):
        if os.environ.get("WHATIF_LIGHT", "1") != "0":
            self._cine_light()
        super().post_cams()
        if os.environ.get("WHATIF_LIGHT", "1") != "0":
            self._cine_post()
        if os.environ.get("WHATIF_LIGHTDUMP"):          # bv. "0.3,1.0": welke lampen staan dicht bij welk hoofd
            for tt in (float(x) for x in os.environ["WHATIF_LIGHTDUMP"].split(",")):
                self.sc.frame_set(F(tt))
                for ch in self.cast[:3]:
                    hp = self.headpos(ch, tt)
                    rows = []
                    for o in bpy.data.objects:
                        if o.type == "LIGHT" and not o.hide_render and o.data.type != "SUN":
                            d = (o.matrix_world.translation - hp).length
                            if o.data.energy > 0 and d < 6:
                                rows.append((round(o.data.energy / max(0.05, d * d), 1), o.name, round(d, 2), round(o.data.energy, 1)))
                    rows.sort(reverse=True)
                    print("LAMPEN", tt, ch.name, ch.rig.users_collection[0].name, rows[:3])
        sc = self.sc
        sc.view_settings.exposure = self.exposure + (0.15 if _v2.ENGINE == "EEVEE" else 0.0)
        try:                                   # grote sets: anders 'Shadow buffer full' en ontbrekende schaduwen
            sc.eevee.shadow_pool_size = "1024"
        except Exception:
            pass
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
                    # hand haalt zijn doel niet (arm te kort): figuur/doel dichterbij zetten
                    ik = pb.get(f"hand_ik.{side}")
                    fa = pb.get(f"forearm.{side}")
                    if ik is not None and fa is not None and "Hand_IK" in fa.constraints \
                            and fa.constraints["Hand_IK"].influence > 0.5:
                        if ((M @ fa.tail) - (M @ ik.head)).length > 0.12:
                            warn("ARM_REIKT_NIET", t, f"{ch.name} {side}")
                    # hele arm (boven- en onderarm, 5 punten per bot) mag niet in de hoofdbol zitten
                    hit = False
                    for ab in (f"upper_arm.{side}", f"forearm.{side}"):
                        if ab not in pb or hit:
                            continue
                        a0, a1 = M @ pb[ab].head, M @ pb[ab].tail
                        for k in range(1, 6):
                            q = a0.lerp(a1, k / 5)
                            if (q - hcen).length < hr * 0.85:
                                warn("ARM_DOOR_HOOFD", t, f"{ch.name} {side}")
                                hit = True
                                break
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
        # 5-10: lessen video 3 (fouten die niels pas in de eindversie zag), zie qc_v3lessen()
        if os.environ.get("WHATIF_QC_SNEL") != "1":
            self.qc_v3lessen(warn, shots, people)
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
# Kwaliteitscheck: lessen uit video 3 (2026-11-08). Fouten die stills niet vangen omdat ze in de BEWEGING zitten.
NL_WOORDEN = {"opa", "oma", "oom", "tante", "broer", "broertje", "zus", "zusje", "niet", "geen", "regel", "regels",
              "dag", "dagen", "nieuws", "uitgang", "ingang", "kassa", "gesloten", "politie", "winkel", "supermarkt",
              "aanbieding", "korting", "welkom", "bedankt", "alstublieft", "straat", "huis", "het", "een", "van",
              "voor", "met", "wel", "altijd", "nooit", "lief", "luister", "eten", "schoon", "verboden", "pas", "op",
              "ja", "nee", "jij", "jou", "mij", "wij", "ons", "zijn", "haar", "hij", "zij", "school", "les", "uur"}
NL_OOK_ENGELS = {"school", "op", "pas", "zij"}       # komen ook in Engelse woorden/afkortingen voor: alleen samen tellen
FX_PREFIX = ("Brokstuk", "Stof", "Scherf", "Flits", "Ring", "Vonk", "Druppel", "Regen", "Rook", "Confetti", "Snelheid",
             "Wolk", "Vogel", "Kraai", "Blad", "Sneeuw", "Ster", "Vuur", "Vlam", "Gloed", "Lichtpunt", "Deeltje")
VOERTUIG_PREFIX = ("Auto_", "Bus", "Vrachtwagen", "Vuilniswagen", "Trein", "Tram", "Boot", "Vliegtuig", "Helikopter")


def _tekst_rect(d, t):
    """Benaderde schermrechthoek (x0, y0, x1, y1 in 0..1, y omhoog) van een 2D-overlay uit self.texts."""
    body = d["body"](t) if callable(d["body"]) else str(d["body"])
    w = max(1, len(body)) * d["size"] * 0.58 / 1920.0
    h = d["size"] * 1.0 / 1080.0
    x, y = d["loc"]
    ax, ay = d.get("anchor", ("LEFT", "TOP"))
    x0 = x if ax == "LEFT" else (x - w if ax == "RIGHT" else x - w / 2)
    y1 = y if ay == "TOP" else (y + h if ay == "BOTTOM" else y + h / 2)
    return (x0, y1 - h, x0 + w, y1), body


def _overlap(a, b, pad=0.006):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def qc_v3lessen(self, warn, shots, people):
    """Extra checks na video 3:
    5. SCHOK / BOTSING / DOOR_ELKAAR: de bewegingsprobe draait nu altijd mee (niet alleen met WHATIF_PROBE).
    6. CAMERA_DOOR_OBJECT: de camera mag tussen twee frames nergens doorheen gaan (grijze flits door een paal, 2:51).
    7. PROP_ZONDER_PERSOON: een bewegend voorwerp (kar, product, fiets, voertuig) in beeld zonder iemand erbij.
    8. TEKST_ONDER_HUD / HUD_BOTSING: 3D-tekst (logo, bord) of twee overlays op dezelfde plek (NEWS 24 over de klok).
    9. NEDERLANDS_IN_BEELD: Nederlandse woorden in beeldtekst (OPA/OMA op het koelkastbriefje).
    10. LICHT_IN_HOOFD: een lamp (rand-/keylicht) vlak bij of in een hoofd (witte flits bij fietsshots)."""
    import re
    from bpy_extras.object_utils import world_to_camera_view
    sc = self.sc
    if not hasattr(self, "probe_rows"):
        self.probe_rows = []
    # 5. beweging
    self._probe()
    self._probe_people()
    for kind, t, msg in self.probe_rows:
        warn(kind, t, msg)

    def cam_at(t):
        for t0, t1, cam in shots:
            if t0 <= t < t1:
                return cam
        return None

    skip_lens = ("Irradiance", "Randlicht", "Keylicht", "Vullicht", "Volume", "Mist", "Lucht", "Sky")
    # 6. camera door een object: straal van de vorige naar de huidige camerapositie, elk frame binnen een shot
    for t0, t1, cam in shots:
        prev = None
        for f in range(F(t0), F(t1)):
            sc.frame_set(f)
            p = cam.matrix_world.translation.copy()
            if prev is not None:
                d = p - prev
                if d.length > 1e-4:
                    dg = bpy.context.evaluated_depsgraph_get()
                    hit, loc, nrm, _i, ob, _m = sc.ray_cast(dg, prev, d.normalized(), distance=d.length + 0.15)
                    if hit and ob is not None and not ob.name.startswith(skip_lens) and not ob.hide_render:
                        warn("CAMERA_DOOR_OBJECT", (f - 1) / FPS, f"{cam.name} gaat door {ob.name}")
            prev = p
    # 7. bewegende voorwerpen zonder persoon (alleen wat in beeld is)
    rigs = set()
    for ch in people:
        rigs.add(ch.rig)
        rigs.update(ch.rig.children_recursive)
    movers = []
    for o in bpy.data.objects:
        if o in rigs or o.type not in ("MESH", "EMPTY", "FONT", "CURVE") or o.name.startswith(FX_PREFIX):
            continue
        if o.parent is not None and (o.parent in rigs or o.parent.type == "ARMATURE"):
            continue
        anim = o.animation_data is not None and o.animation_data.action is not None
        if not anim or any(c.type == "CHILD_OF" for c in o.constraints):
            continue                                   # vastgemaakt aan een hand (grab) = er is een persoon
        if o.parent is not None and o.parent.animation_data and o.parent.animation_data.action:
            continue                                   # de ouder wordt al bekeken
        movers.append(o)
    step = 2
    for o in movers:
        veh = o.name.startswith(VOERTUIG_PREFIX)
        reach = 3.5 if veh else 1.1
        prev, last_warn = None, -9.0
        for f in range(1, F(self.length) + 1, step):
            sc.frame_set(f)
            t = (f - 1) / FPS
            p = o.matrix_world.translation.copy()
            if prev is None or o.hide_render or min(o.matrix_world.to_scale()) < 0.01:
                prev = p
                continue
            v = (p - prev).length * FPS / step
            prev = p
            if v < 0.25 or t - last_warn < 1.0:
                continue
            cam = cam_at(t)
            if cam is None:
                continue
            q = world_to_camera_view(sc, cam, p)
            if not (q.z > 0 and -0.05 <= q.x <= 1.05 and -0.05 <= q.y <= 1.05):
                continue
            near = False
            for ch in people:
                if ch.body is not None and (ch.body.hide_render or min(ch.body.matrix_world.to_scale()) < 0.01):
                    continue
                M = ch.rig.matrix_world
                for bn in ("hand.L", "hand.R", "hips"):
                    pb = ch.rig.pose.bones.get(bn)
                    if pb and ((M @ pb.tail) - p).length < reach * max(ch.rig.scale.z, 0.5):
                        near = True
                        break
                if near:
                    break
            if not near:
                warn("PROP_ZONDER_PERSOON", t, f"{o.name} beweegt ({v:.1f} m/s) zonder iemand die hem duwt/draagt/bestuurt")
                last_warn = t
    # 8. tekst: 3D-tekst onder een overlay en overlays die elkaar raken
    fonts = [o for o in bpy.data.objects if o.type == "FONT"]
    texts = [d for d in self.texts if d["t1"] is None or d["t1"] > d["t0"]]
    for i, d in enumerate(texts):
        t1 = d["t1"] if d["t1"] is not None else self.length
        for t0s, t1s, cam in shots:
            a, b = max(d["t0"], t0s), min(t1, t1s)
            if b - a < 0.1:
                continue
            tm = (a + b) / 2
            r, body = _tekst_rect(d, tm)
            sc.frame_set(F(tm))
            for o in fonts:
                if o.hide_render or min(o.matrix_world.to_scale()) < 0.01:
                    continue
                pts = [world_to_camera_view(sc, cam, o.matrix_world @ Vector(c)) for c in o.bound_box]
                if any(q.z <= 0 for q in pts):
                    continue
                orc = (min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts))
                if orc[2] < 0 or orc[0] > 1 or orc[3] < 0 or orc[1] > 1 or (orc[2] - orc[0]) < 0.02:
                    continue
                th = orc[3] - orc[1]
                cov = 0.0
                if _overlap(r, orc, pad=0.0):
                    ix = min(r[2], orc[2]) - max(r[0], orc[0])
                    iy = min(r[3], orc[3]) - max(r[1], orc[1])
                    cov = max(0.0, ix) * max(0.0, iy) / max(1e-6, (orc[2] - orc[0]) * th)
                if os.environ.get("WHATIF_QC_DEBUG"):
                    print("TEKSTDBG", o.name, round(th, 3), round(cov, 2), body[:12])
                if th >= 0.02 and cov > 0:             # leesbare 3D-tekst (>= 2% beeldhoogte) die de overlay raakt
                    warn("TEKST_ONDER_HUD", tm, f"{cam.name}: '{o.data.body[:20]}' ({o.name}) onder overlay '{re.sub(r'[0-9:]+', '#', body)[:24]}'")
        for e in texts[i + 1:]:
            e1 = e["t1"] if e["t1"] is not None else self.length
            a, b = max(d["t0"], e["t0"]), min(t1, e1)
            if b - a < 0.05 or tuple(d["loc"]) == tuple(e["loc"]):
                continue                               # zelfde plek = HUD_OVERLAP (hierboven)
            tm = (a + b) / 2
            r1, b1 = _tekst_rect(d, tm)
            r2, b2 = _tekst_rect(e, tm)
            if _overlap(r1, r2, pad=0.0):
                warn("HUD_BOTSING", tm, f"'{b1[:20]}' raakt '{b2[:20]}'")
    # 9. Nederlands in beeld (scripts en beeldtekst zijn Engels)
    bodies = [(o.name, o.data.body) for o in fonts if not o.hide_render]
    bodies += [("overlay", d["body"]) for d in self.texts if isinstance(d["body"], str)]
    bodies += [("kaart", c["body"] or "") for c in self.cards] + [("kaart", c.get("sub") or "") for c in self.cards]
    for nm, body in bodies:
        words = {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]+", body or "")}
        nl = words & NL_WOORDEN
        if nl - NL_OOK_ENGELS or len(nl) >= 2:
            warn("NEDERLANDS_IN_BEELD", 0.0, f"{nm}: '{body[:40]}' ({', '.join(sorted(nl))})")
    # 10. lamp in/vlak bij een hoofd
    lamps = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type != "SUN"]
    for f in range(1, F(self.length) + 1, 3):
        sc.frame_set(f)
        t = (f - 1) / FPS
        for ch in people:
            if ch.body is not None and (ch.body.hide_render or min(ch.body.matrix_world.to_scale()) < 0.01):
                continue
            pb = ch.rig.pose.bones.get("head")
            if pb is None:
                continue
            hr = ch.J["head_r"].z * ch.rig.scale.z
            hc = ch.rig.matrix_world @ pb.head + Vector((0, 0, hr * 0.9))
            for o in lamps:
                if o.hide_render or o.data.energy <= 0:
                    continue
                if (o.matrix_world.translation - hc).length < hr * 1.4:
                    warn("LICHT_IN_HOOFD", t, f"{o.name} bij het hoofd van {ch.name}")


Scene3.qc_v3lessen = qc_v3lessen


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


def ride_path(S, ch, crank, t0, t1, pts, cadence=1.6, lean=18, stand=False, sway=0.0, plant=None, crouch_fn=None, ease=0.0,
              accel=None, decel=False):
    """Fietsen langs punten: wortel beweegt mee (zonder loopcyclus), trappers draaien, lichte stuurzwaai."""
    pts = [Vector(p) for p in pts]
    prev = getattr(ch, "_ride_prev", None)
    joined = bool(prev and abs(prev[0] - t0) <= 1.5 / FPS)
    acc = (0.9 if joined and prev[3] else 0.0) if accel is None else accel     # na stilstaan (voet aan de grond) rustig optrekken
    segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(segs) or 1e-6
    frames = list(range(F(t0), F(t1) + 1))
    locs, rots = [], []
    for f in frames:
        t = (f - 1) / FPS
        u = max(0.0, min(1.0, (t - t0) / max(1e-3, t1 - t0)))
        if acc > 0:                                      # optrekken vanuit stilstand: snelheid loopt lineair op
            T = max(1e-3, t1 - t0)
            tt = min(T, t - t0)
            u = (tt * tt / (2 * acc) if tt < acc else tt - acc / 2) / (T - acc / 2)
        elif decel:                                      # remmen tot stilstand: snelheid loopt lineair af naar 0
            u = 1 - (1 - u) ** 2
        elif ease > 0:                                     # zacht wegrijden/afremmen
            u = (1 - ease) * u + ease * (u * u * (3 - 2 * u))
        d = total * u
        for i, L in enumerate(segs):
            if d <= L or i == len(segs) - 1:
                w = min(1.0, d / L) if L > 0 else 1.0
                p = pts[i].lerp(pts[i + 1], w)
                dv = pts[i + 1] - pts[i]
                break
            d -= L
        locs.append(tuple(p))
        rots.append([math.radians(sway * math.sin(t * cadence * 2 * math.pi)), 0.0, math.atan2(dv.x, -dv.y)])
    # stuurrichting zonder sprongen: hoek doorlopend maken en over ~0,4 s uitsmeren (geen ruk in bochten)
    for i in range(1, len(rots)):
        while rots[i][2] - rots[i - 1][2] > math.pi:
            rots[i][2] -= 2 * math.pi
        while rots[i][2] - rots[i - 1][2] < -math.pi:
            rots[i][2] += 2 * math.pi
    yaw = [r[2] for r in rots]
    W = 6
    for i in range(len(rots)):
        lo, hi = max(0, i - W), min(len(rots), i + W + 1)
        rots[i][2] = sum(yaw[lo:hi]) / (hi - lo)
    y_prev = getattr(ch, "_ride_yaw", None)
    if joined and y_prev is not None and rots:      # sluit aan op de stuurhoek van het vorige stuk, verschil wegwerken in ~0,6 s
        d0 = y_prev - rots[0][2]
        d0 = (d0 + math.pi) % (2 * math.pi) - math.pi
        for i, r in enumerate(rots):
            u = min(1.0, i / (0.6 * FPS))
            r[2] += d0 * (1 - u * u * (3 - 2 * u))
    ch._ride_yaw = rots[-1][2] if rots else None
    # bochten afronden: knik in de lijn gaf een ruk in snelheid (zelfde venster als de stuurhoek, begin/eind vast)
    raw = [Vector(p) for p in locs]
    n = len(raw)
    for i in range(n):
        k = min(W, i, n - 1 - i)
        locs[i] = tuple(sum(raw[i - k:i + k + 1], Vector()) / (2 * k + 1))
    bake(ch.rig, "location", frames, locs, interp="BEZIER")
    bake(ch.rig, "rotation_euler", frames, [tuple(r) for r in rots], interp="BEZIER")
    ride(S, ch, crank, t0, t1, cadence=cadence, lean=lean, stand=stand, plant=plant, crouch_fn=crouch_fn)
    ch.last = None


# ---------------------------------------------------------------- filmische belichting (niels 2026-11-05)
def _subjects(S, t0, t1, cam, maxd=7.0):
    """Figuren die in dit shot het onderwerp zijn: dichtbij de camera en dicht bij het midden van het beeld."""
    out = []
    tm = 0.5 * (t0 + t1)
    loc, tgt, lens = S._cam_eval(cam, tm, t1)
    loc, tgt = Vector(loc), Vector(tgt)
    fwd = (tgt - loc).normalized()
    half = math.atan(18.0 / max(8.0, lens))              # halve beeldhoek (horizontaal, 36 mm sensor)
    for ch in S.cast:
        try:
            h = S.headpos(ch, tm)
        except Exception:
            continue
        v = h - loc
        d = v.length
        if d < 0.3 or d > maxd * max(1.0, lens / 35.0):
            continue
        ang = fwd.angle(v.normalized(), math.pi)
        if ang > half * 1.1:
            continue
        out.append((ang / half + d / (maxd * 2), ch, h, loc))
    out.sort(key=lambda x: x[0])
    return out[:2]


def S_head(S, ch, t):
    try:
        return S.headpos(ch, t)
    except Exception:
        return S.bone_world(ch, "head", t)


def _cine_light(self):
    """Per shot een zacht key-licht van de camerakant op de onderwerpen (light linking: alleen op het figuur),
    plus oranje/blauwe randlichten (zoals bij het hoofdpersonage) voor iedereen die ergens onderwerp is."""
    night = getattr(self, "night", False)
    keys = {}
    order = []
    moving_keys = {}
    for t0, t1, camobj in getattr(self, "shots_plan", []) or []:
        pass
    cams = sorted(self.cams, key=lambda c: c["t0"])
    for k, c in enumerate(cams):
        t0 = c["t0"]
        t1 = cams[k + 1]["t0"] if k + 1 < len(cams) else self.length
        if t1 - t0 < 0.05:
            continue
        for rank, (_, ch, h, cl) in enumerate(_subjects(self, t0, t1, c)):
            if ch not in keys:
                ld = bpy.data.lights.new(f"Key_{ch.name}", "AREA")
                ld.shape, ld.size = "DISK", 1.2
                ld.color = (0.75, 0.82, 1.0) if night else (1.0, 0.88, 0.74)
                ld.energy = 0.0
                lo = bpy.data.objects.new(ld.name, ld)
                lo.visible_camera = False
                lo.light_linking.receiver_collection = ch.rig.users_collection[0]
                bpy.context.scene.collection.objects.link(lo)
                ld.keyframe_insert("energy", frame=1)
                keys[ch] = lo
                order.append(ch)
            lo = keys[ch]
            d = cl - h
            d.z = 0
            if d.length < 1e-3:
                d = Vector((0, -1, 0))
            d.normalize()
            side = Vector((-d.y, d.x, 0))
            sc_ = ch.rig.scale.z
            dist = 1.7 * sc_
            off = (d * math.cos(0.6) + side * math.sin(0.6)) * dist + Vector((0, 0, 0.75 * sc_))
            e = (15.0 if rank == 0 else 9.0) * sc_ * sc_ * (1.0 if night else 0.6)
            fa, fb = F(t0), max(F(t0), F(t1) - 1)
            # het licht reist mee met het hoofd (een fietser/renner reed anders dóór het stilstaande licht: witte flits)
            moving = (S_head(self, ch, t0) - S_head(self, ch, (t1 - 1.0 / FPS))).length > 0.3
            frames = sorted(set(list(range(fa, fb + 1, 3)) + [fb])) if moving else [fa, fb]
            lo.data.energy = e
            lo.data.keyframe_insert("energy", frame=fa)
            for f in frames:
                hh = S_head(self, ch, (f - 1) / FPS) if moving else h
                lo.location = hh + off
                lo.rotation_euler = (hh - lo.location).to_track_quat("-Z", "Y").to_euler()
                lo.keyframe_insert("location", frame=f)
                lo.keyframe_insert("rotation_euler", frame=f)
            lo.data.energy = 0.0
            lo.data.keyframe_insert("energy", frame=F(t1))
            moving_keys.setdefault(lo, set()).update(frames if moving else [])
            if os.environ.get("WHATIF_LIGHTDBG"):
                print("KEYLICHT", ch.name, round(t0, 2), round(t1, 2), "bewegend" if moving else "stil", round(e, 1),
                      "afstand bij start", round((S_head(self, ch, t0) - (h + off)).length, 2))
    for lo in keys.values():
        mk = moving_keys.get(lo, set())
        for owner in (lo, lo.data):
            for fc in A._fcurves(owner):
                for kp in fc.keyframe_points:
                    # binnen een bewegend shot: positie lineair tussen de sleutels; bij een cut/energie: hard
                    lin = owner is lo and int(round(kp.co.x)) in mk and fc.data_path in ("location", "rotation_euler")
                    kp.interpolation = "LINEAR" if lin else "CONSTANT"
    # randlichten ook voor de belangrijkste bijfiguren (max 4 extra)
    for ch in order[:6]:
        if ch not in self.heroes and len(self.heroes) < 5:
            self.heroes.append(ch)


def _cine_post(self):
    """Compositor: zachte bloom op lampen/schermen en een lichte vignet (filmlook). Alleen EEVEE/Cycles."""
    if _v2.ENGINE == "WORKBENCH":
        return
    sc = self.sc
    # randlicht duidelijker (oranje/blauw rand moet zichtbaar blijven naast het key-licht en daglicht)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name.startswith("Randlicht_"):
            o.data.energy *= 1.8 if self.night else 2.6
    try:
        ng = bpy.data.node_groups.new("Filmlook", "CompositorNodeTree")
        sc.compositing_node_group = ng
        N, L = ng.nodes, ng.links
        rl = N.new("CompositorNodeRLayers")
        out = N.new("NodeGroupOutput")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        gl = N.new("CompositorNodeGlare")
        for k, v in (("Type", "Bloom"), ("Quality", "High")):
            try:
                gl.inputs[k].default_value = v
            except Exception:
                try:
                    setattr(gl, k.lower() if k == "Quality" else "glare_type", v.upper())
                except Exception:
                    pass
        for name, v in (("Threshold", 1.0), ("Strength", 0.35), ("Size", 0.6)):
            if name in gl.inputs:
                gl.inputs[name].default_value = v
        L.new(rl.outputs["Image"], gl.inputs["Image"])
        em = N.new("CompositorNodeEllipseMask")
        for name, v in (("Size", (0.95, 0.85)),):
            if name in em.inputs:
                em.inputs[name].default_value = v
        try:
            em.width, em.height = 0.95, 0.85
        except Exception:
            pass
        bl = N.new("CompositorNodeBlur")
        try:
            bl.size_x = bl.size_y = 400
        except Exception:
            if "Size" in bl.inputs:
                bl.inputs["Size"].default_value = (400, 400)
        L.new(em.outputs[0], bl.inputs[0])
        mr = N.new("ShaderNodeMapRange")
        L.new(bl.outputs[0], mr.inputs[0])
        mr.inputs[1].default_value, mr.inputs[2].default_value = 0.0, 1.0
        mr.inputs[3].default_value, mr.inputs[4].default_value = 0.62, 1.0
        mx = N.new("ShaderNodeMix")
        mx.data_type, mx.blend_type = "RGBA", "MULTIPLY"
        mx.inputs[0].default_value = 1.0
        ins = {i.identifier: i for i in mx.inputs}
        outs = {o.identifier: o for o in mx.outputs}
        L.new(gl.outputs["Image"], ins["A_Color"])
        L.new(mr.outputs[0], ins["B_Color"])
        mx_out = outs["Result_Color"]
        L.new(mx_out, out.inputs[0])
        sc.render.use_compositing = True
    except Exception as ex:                              # nooit een render laten vallen op de filmlook
        print("FILMLOOK overgeslagen:", ex)


Scene3._cine_light = _cine_light
Scene3._cine_post = _cine_post


# ---------------------------------------------------------------- dieren (hondje, hondje_oud, zebra)
class Animal:
    pass


def animal(S, name, loc=(0, 0, 0), rot=0.0, scale=1.0):
    """Laad een dier uit assets/dieren (kijkt bij rot 0 naar -y, net als de figuren)."""
    before = set(bpy.data.objects)
    acts_before = set(bpy.data.actions)
    fps = S.sc.render.fps / S.sc.render.fps_base
    bpy.ops.import_scene.gltf(filepath=os.path.join(R.ASSETS, "dieren", name + ".glb"))
    new = [o for o in bpy.data.objects if o not in before]
    for o in [o for o in new if o.name.startswith("Icosphere")]:
        new.remove(o)
        bpy.data.objects.remove(o, do_unlink=True)
    an = Animal()
    an.name = name
    an.rig = [o for o in new if o.type == "ARMATURE"][0]
    an.rig.name = f"DIER_{name}_{len([o for o in bpy.data.objects if o.name.startswith('DIER_')])}"
    an.rig.animation_data_create()
    an.rig.animation_data.action = None
    an.acts = {a.name.split(".")[0]: a for a in bpy.data.actions if a not in acts_before}
    an.fps = fps
    an.rig.scale = (scale, scale, scale)
    an.rig.location = tuple(loc)
    an.rig.rotation_euler = (0, 0, math.radians(rot))
    an.rig.keyframe_insert("location", frame=1)
    an.rig.keyframe_insert("rotation_euler", frame=1)
    for o in new:
        if o.type == "MESH":
            o.visible_shadow = True
    _zebra_stripes(new)
    return an


_STRIPES = {"zebra_streep_lijf": ("Y", 6.5, 2.2), "zebra_streep_nek": ("Z", 9.0, 1.5), "zebra_streep_poot": ("Z", 14.0, 0.8)}


def _zebra_stripes(objs):
    """De zebrastrepen zijn procedureel en gaan verloren in de glb: hier opnieuw opbouwen (objectcoordinaten,
    dus ze plakken op de delen die aan de botten hangen)."""
    done = set()
    for o in objs:
        if o.type != "MESH":
            continue
        for m in o.data.materials:
            if not m or m in done:
                continue
            key = next((k for k in _STRIPES if m.name.startswith(k)), None)
            if key is None:
                continue
            done.add(m)
            axis, scale, distort = _STRIPES[key]
            m.use_nodes = True
            nt = m.node_tree
            b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if b is None:
                continue
            tc = nt.nodes.new("ShaderNodeTexCoord")
            w = nt.nodes.new("ShaderNodeTexWave")
            w.wave_type, w.bands_direction, w.wave_profile = "BANDS", axis, "SIN"
            w.inputs["Scale"].default_value = scale
            w.inputs["Distortion"].default_value = distort
            w.inputs["Detail"].default_value = 1.5
            w.inputs["Detail Scale"].default_value = 0.6
            nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = 0.46
            ramp.color_ramp.elements[0].color = (0.88, 0.85, 0.80, 1)
            ramp.color_ramp.elements[1].position = 0.54
            ramp.color_ramp.elements[1].color = (0.008, 0.007, 0.009, 1)
            nt.links.new(w.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])


def animal_act(an, t0, t1, action, speed=1.0):
    """Speel een (lus)actie van t0 tot t1 (NLA, herhaald)."""
    act = an.acts.get(action) or bpy.data.actions[action]
    a0, a1 = act.frame_range
    L = max(1e-3, a1 - a0)
    sc = FPS / an.fps / speed
    tr = an.rig.animation_data.nla_tracks.new()
    st = tr.strips.new(action, F(t0), act)
    st.scale = sc
    st.repeat = max(0.05, (F(t1) - F(t0)) / (L * sc))
    st.extrapolation = "NOTHING"
    st.blend_in = st.blend_out = 0
    return st


def animal_path(an, t0, t1, pts, action=None, speed=1.0, ease=0.0):
    """Beweeg een dier langs punten (z = vloer) met de neus in looprichting; optioneel met een lusactie."""
    pts = [Vector(p) for p in pts]
    segs = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(segs) or 1e-6

    def at(d):
        for i, L in enumerate(segs):
            if d <= L or i == len(segs) - 1:
                w = min(1.0, d / L) if L > 0 else 1.0
                return pts[i].lerp(pts[i + 1], w), pts[i + 1] - pts[i]
        return pts[-1], pts[-1] - pts[-2]
    rprev = an.rig.rotation_euler.z
    f0, f1 = F(t0), F(t1)
    for f in range(f0, f1 + 1, 2) if f1 > f0 else [f0]:
        u = (f - f0) / max(1, f1 - f0)
        if ease:
            u = u * u * (3 - 2 * u) * ease + u * (1 - ease)
        p, d = at(u * total)
        r = math.atan2(d.x, -d.y) if d.length > 1e-6 else rprev
        while r - rprev > math.pi:
            r -= 2 * math.pi
        while r - rprev < -math.pi:
            r += 2 * math.pi
        rprev = r
        an.rig.location = p
        an.rig.rotation_euler = (0, 0, r)
        an.rig.keyframe_insert("location", frame=f)
        an.rig.keyframe_insert("rotation_euler", frame=f)
    if action:
        animal_act(an, t0, t1, action, speed)


def animal_place(an, t, loc, rot):
    an.rig.location = tuple(loc)
    an.rig.rotation_euler = (0, 0, math.radians(rot))
    an.rig.keyframe_insert("location", frame=F(t))
    an.rig.keyframe_insert("rotation_euler", frame=F(t))


def leash(S, ch, an, t0, t1, side="R", step=0.125, color=(0.75, 0.12, 0.1)):
    """Hondenlijn van de hand van ch naar de halsband van het dier (dun stokje dat per frame meegaat)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.008, depth=1.0)
    o = bpy.context.active_object
    o.name = f"Lijn_{an.rig.name}"
    o.data.materials.append(S.mat("hondenlijn", color))
    o.rotation_mode = "QUATERNION"
    ring = [ob for ob in bpy.data.objects if ob.parent == an.rig and "lijnring" in ob.name]
    t = t0
    while t <= t1 + 1e-6:
        a = S.bone_world(ch, f"hand.{side}", t, tail=False)
        S.sc.frame_set(F(t))
        b = ring[0].matrix_world.translation.copy() if ring else an.rig.matrix_world @ Vector((0, -0.2, 0.3))
        d = b - a
        o.location = (a + b) / 2
        o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
        o.scale = (1, 1, max(0.01, d.length * 0.97))
        for p in ("location", "rotation_quaternion", "scale"):
            o.keyframe_insert(p, frame=F(t))
        t += step
    return o


# ---------------------------------------------------------------- bestek (echte lepel/vork/mes, geen staafjes)
def cutlery(S, kind, name, scale=1.6):
    """Bestek op maat van de grote handen. Oorsprong = waar de hand het vastpakt; het werkende eind wijst naar +z.
    kind: lepel, vork, mes, opscheplepel."""
    met = P.m("metaal")
    s = scale
    parts = [T.box(name + "_steel", (0, 0, 0.02 * s), (0.014 * s, 0.006 * s, 0.11 * s), met, base=False, bevel=0.003, ol=0)]
    if kind in ("lepel", "opscheplepel"):
        k = 1.6 if kind == "opscheplepel" else 1.0
        parts.append(T.sphere(name + "_kom", (0, -0.006 * s, 0.1 * s * k), 0.024 * s * k, met, scale=(0.8, 0.35, 1.25), seg=16, ol=0))
    elif kind == "vork":
        parts.append(T.box(name + "_hals", (0, 0, 0.085 * s), (0.026 * s, 0.005 * s, 0.018 * s), met, base=False, bevel=0.002, ol=0))
        for i in (-1, 0, 1):
            parts.append(T.box(f"{name}_tand{i}", (i * 0.009 * s, 0, 0.11 * s), (0.004 * s, 0.004 * s, 0.035 * s), met, base=False,
                               bevel=0.001, ol=0))
    elif kind == "mes":
        parts.append(T.box(name + "_lemmet", (0.004 * s, 0, 0.115 * s), (0.02 * s, 0.003 * s, 0.085 * s), met, base=False, bevel=0.002,
                           ol=0))
    o = T.merge(name, parts, ol=0)
    return o


def male_scientist(S, ch):
    """De wetenschapper is in video 3 een MAN (niels 2026-11-04): knot met band, wimpers, blosjes en klembord uit het
    samengevoegde lichaam halen, volle wenkbrauwen en een korte baard met snor aan het hoofdbot. Direct na S.actor."""
    import bmesh
    bpy.context.view_layer.update()
    body = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent == ch.rig and o.name.endswith("_lichaam")), None)
    if body is None:
        print("LET OP: geen lichaam voor", ch.name)
        return
    mats = [m.name if m else "" for m in body.data.materials]
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.faces.ensure_lookup_table()

    def comps(pred):
        todo = {f for f in bm.faces if pred(mats[f.material_index])}
        out = []
        while todo:
            f0 = todo.pop()
            grp, stack = [f0], [f0]
            while stack:
                f = stack.pop()
                for e in f.edges:
                    for g in e.link_faces:
                        if g in todo:
                            todo.remove(g)
                            grp.append(g)
                            stack.append(g)
            vs = {v for f in grp for v in f.verts}
            lo = V([min(v.co[i] for v in vs) for i in range(3)])
            hi = V([max(v.co[i] for v in vs) for i in range(3)])
            out.append((grp, lo, hi))
        return out

    kill = set()
    hair = comps(lambda n: "_haar_" in n)
    if len(hair) > 1:
        hair.sort(key=lambda c: (c[2] - c[1]).length)
        for grp, lo, hi in hair[:-1]:                     # alles behalve de haarkap = de knot
            kill.update(grp)
    for grp, lo, hi in comps(lambda n: "2D6CDF" in n):    # haarband (pasje en pen zitten lager, op de jas)
        if lo.z > 1.3:
            kill.update(grp)
    for grp, lo, hi in comps(lambda n: "1B1214" in n):    # wimpers: de kleinste zwarte vlakjes bij de ogen
        if max(hi - lo) < 0.03:
            kill.update(grp)
    for grp, lo, hi in comps(lambda n: "E09C7D" in n or "A0703D" in n or "C0C0C0" in n or "_FFFFFF_" in n):
        kill.update(grp)                                    # blosjes en klembord
    bmesh.ops.delete(bm, geom=list(kill), context="FACES")
    # hoofd (grootste huidkleurige bol) voor de baard
    skin = comps(lambda n: "huid_DDB08A" in n)
    head = max(skin, key=lambda c: (c[2] - c[1]).length) if skin else None
    bm.to_mesh(body.data)
    bm.free()
    if head is None:
        return
    Mw = body.matrix_world
    lo, hi = Mw @ head[1], Mw @ head[2]
    c = (lo + hi) / 2
    r = (hi.z - lo.z) / 2
    M = ch.rig.matrix_world.to_3x3()
    fwd, up = (M @ V(0, -1, 0)).normalized(), V(0, 0, 1)
    side = fwd.cross(up).normalized()
    hairm = S.mat("baard_wetenschapper", (0.13, 0.10, 0.08))
    yaw = math.degrees(math.atan2(fwd.x, -fwd.y))
    parts = [T.sphere(ch.name + "_baard", tuple(c + fwd * (r * 0.5) - up * (r * 0.74)), r * 0.58, hairm,
                      scale=(1.0, 0.7, 0.55), rot=(0, 0, yaw), seg=20, ol=0.004),
             T.sphere(ch.name + "_snor_L", tuple(c + fwd * (r * 0.93) - up * (r * 0.3) + side * (r * 0.14)), r * 0.16, hairm,
                      scale=(1.5, 0.6, 0.55), rot=(0, 0, yaw - 12), seg=12, ol=0.003),
             T.sphere(ch.name + "_snor_R", tuple(c + fwd * (r * 0.93) - up * (r * 0.3) - side * (r * 0.14)), r * 0.16, hairm,
                      scale=(1.5, 0.6, 0.55), rot=(0, 0, yaw + 12), seg=12, ol=0.003)]
    bpy.context.view_layer.update()
    for o in parts:
        mw = o.matrix_world.copy()
        o.parent = ch.rig
        o.parent_type = "BONE"
        o.parent_bone = "head"
        bpy.context.view_layer.update()
        o.matrix_world = mw
    print("MAN: knot/wimpers/blos/klembord weg:", len(kill), "vlakken; baard op", tuple(round(x, 2) for x in c), "r", round(r, 3))
    return parts


def no_phone(ch, screen="6FB7FF", case="1A1A1A"):
    """Haal de telefoon uit de hand van een figuur (samengevoegd lichaam): het blauwe scherm en de zwarte behuizing
    die het scherm raakt. Nodig als hij iets anders vasthoudt (een stuur)."""
    import bmesh
    body = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent == ch.rig and o.name.endswith("_lichaam")), None)
    if body is None:
        return
    mats = [m.name if m else "" for m in body.data.materials]
    bm = bmesh.new()
    bm.from_mesh(body.data)

    def comps(key):
        todo = {f for f in bm.faces if key in mats[f.material_index]}
        out = []
        while todo:
            f0 = todo.pop()
            grp, stack = [f0], [f0]
            while stack:
                for e in stack.pop().edges:
                    for g in e.link_faces:
                        if g in todo:
                            todo.remove(g)
                            grp.append(g)
                            stack.append(g)
            vs = {v for f in grp for v in f.verts}
            out.append((grp, V([min(v.co[i] for v in vs) for i in range(3)]), V([max(v.co[i] for v in vs) for i in range(3)])))
        return out

    kill = set()
    scr = comps(screen)
    for grp, lo, hi in scr:
        kill.update(grp)
        for g2, l2, h2 in comps(case):
            if all(l2[i] <= hi[i] + 0.02 and h2[i] >= lo[i] - 0.02 for i in range(3)) and max(h2 - l2) < 0.25:
                kill.update(g2)
    bmesh.ops.delete(bm, geom=list(kill), context="FACES")
    bm.to_mesh(body.data)
    bm.free()
    print("TELEFOON WEG", ch.name, len(kill), "vlakken")


def night_sky(stars=1.0, milky=1.0, band=(0.95, 0.3, 0.12), width=0.3):
    """Sterren en een Melkweg in de wereld (op de lucht die de camera ziet). band = normaal van het Melkwegvlak."""
    w = bpy.context.scene.world
    N, L = w.node_tree.nodes, w.node_tree.links
    bg = next(n for n in N if n.type == "BACKGROUND" and n.inputs["Color"].is_linked)
    sky = bg.inputs["Color"].links[0].from_socket
    tc = next(n for n in N if n.type == "TEX_COORD")
    nrm = N.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    L.new(tc.outputs["Generated"], nrm.inputs[0])

    def stars_layer(scale, size, gain):
        vor = N.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = scale
        L.new(nrm.outputs["Vector"], vor.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = size
        mr.inputs["From Max"].default_value = 0.0
        mr.inputs["To Max"].default_value = gain
        L.new(vor.outputs["Distance"], mr.inputs["Value"])
        return mr.outputs["Result"]

    s1 = stars_layer(260.0, 0.05, 6.0 * stars)
    s2 = stars_layer(700.0, 0.06, 2.5 * stars)
    dot = N.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    bn = V(band).normalized()
    dot.inputs[1].default_value = tuple(bn)
    L.new(nrm.outputs["Vector"], dot.inputs[0])
    ab = N.new("ShaderNodeMath")
    ab.operation = "ABSOLUTE"
    L.new(dot.outputs["Value"], ab.inputs[0])
    bandm = N.new("ShaderNodeMapRange")
    bandm.inputs["From Min"].default_value = width
    bandm.inputs["From Max"].default_value = 0.0
    bandm.interpolation_type = "SMOOTHSTEP"
    L.new(ab.outputs["Value"], bandm.inputs["Value"])
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.5
    noise.inputs["Detail"].default_value = 12.0
    L.new(nrm.outputs["Vector"], noise.inputs["Vector"])
    nmr = N.new("ShaderNodeMapRange")
    nmr.inputs["From Min"].default_value = 0.3
    nmr.inputs["From Max"].default_value = 0.8
    L.new(noise.outputs["Fac"], nmr.inputs["Value"])
    glow = N.new("ShaderNodeMath")
    glow.operation = "MULTIPLY"
    L.new(bandm.outputs["Result"], glow.inputs[0])
    L.new(nmr.outputs["Result"], glow.inputs[1])
    g2 = N.new("ShaderNodeMath")
    g2.operation = "MULTIPLY"
    g2.inputs[1].default_value = 0.35 * milky
    L.new(glow.outputs[0], g2.inputs[0])
    dense = N.new("ShaderNodeMath")
    dense.operation = "MULTIPLY"
    L.new(s2, dense.inputs[0])
    L.new(bandm.outputs["Result"], dense.inputs[1])
    tot = N.new("ShaderNodeMath")
    tot.operation = "ADD"
    L.new(s1, tot.inputs[0])
    L.new(dense.outputs[0], tot.inputs[1])
    # alleen boven de horizon
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(nrm.outputs["Vector"], sep.inputs[0])
    hz = N.new("ShaderNodeMapRange")
    hz.inputs["From Min"].default_value = 0.02
    hz.inputs["From Max"].default_value = 0.2
    L.new(sep.outputs["Z"], hz.inputs["Value"])
    star_col = N.new("ShaderNodeCombineColor")
    for i in range(3):
        mm = N.new("ShaderNodeMath")
        mm.operation = "MULTIPLY_ADD"
        L.new(tot.outputs[0], mm.inputs[0])
        mm.inputs[1].default_value = (1.0, 1.0, 1.0)[i]
        L.new(g2.outputs[0], mm.inputs[2])
        m2 = N.new("ShaderNodeMath")
        m2.operation = "MULTIPLY"
        L.new(mm.outputs[0], m2.inputs[0])
        L.new(hz.outputs["Result"], m2.inputs[1])
        m3 = N.new("ShaderNodeMath")
        m3.operation = "MULTIPLY"
        m3.inputs[1].default_value = (0.85, 0.9, 1.05)[i]
        L.new(m2.outputs[0], m3.inputs[0])
        L.new(m3.outputs[0], star_col.inputs[i])
    add = N.new("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    add.inputs["Factor"].default_value = 1.0
    L.new(sky, add.inputs["A"])
    L.new(star_col.outputs[0], add.inputs["B"])
    L.new(add.outputs["Result"], bg.inputs["Color"])
