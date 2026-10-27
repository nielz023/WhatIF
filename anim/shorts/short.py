"""Raamwerk voor de teaser-shorts (staand 1080x1920, 30-45 s).

Bouwt voort op anim/lib/scene.py (zelfde sets, figuren, acteren, camera's en montage). Extra's voor shorts:

- beeld staand (9:16); S.shot kadert op de staande beeldhoogte;
- één short kan uit meerdere delen (sets) bestaan. Alle delen delen één tijdlijn: de stemregels liggen vast
  (TIMING hieronder), elk deel rendert alleen zijn eigen stuk, met de frame-nummers van de hele short, in
  dezelfde map out/<code>/frames. Zo plakt de montage alles vanzelf aan elkaar en loopt de muziek door;
- titel bovenin, grote teller (DAY 2, HOUR 3 ...), ondertiteling in woordgroepjes, eindkaart LIKE & SUBSCRIBE.

Een deel:

    S = Short("sh1", "a", "keuken", "ochtend", lines=(1, 2))
    l1, l2 = S.L[1], S.L[2]               # (start, eind) van stemregel 1 en 2 op de tijdlijn van de short
    ...
    S.done()

Renderen:  blender -b -P anim/shorts/sh1a_keuken.py -- [--render] [--stills auto] [--pct 25]
Montage (na alle delen): blender -b -P anim/edit/montage.py -- sh1
"""
import glob as _glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from scene import *  # noqa: E402,F401,F403

W, H = 1080, 1920
YELLOW = (1.0, 0.86, 0.15, 1)

TITLES = {
    "sh1": ("WHAT IF YOU GOT", "10x FASTER EVERY DAY?"),
    "sh2": ("WHAT IF TIME STOPPED", "AND ONLY YOU COULD MOVE?"),
    "sh3": ("WHAT IF YOU COULD SEE", "1 YEAR INTO THE FUTURE?"),
    "sh4": ("WHAT IF YOU TURNED INTO", "WHATEVER YOU TOUCHED?"),
    "sh5": ("WHAT IF YOU SHRANK", "10x EVERY HOUR?"),
    "sh7": ("WHAT IF EVERY TELEPORT", "MADE A COPY OF YOU?"),
    "sh8": ("WHAT IF YOU WERE", "1,000,000x HEAVIER?"),
}
# stilte vóór een stemregel (s); standaard 0.12. Langere pauzes alleen waar het beeld tijd nodig heeft.
GAPS = {
    "sh1": {1: 0.25, 4: 0.3, 7: 0.3, 8: 0.35},
    "sh2": {1: 0.3, 2: 0.5, 4: 0.5, 7: 0.4, 8: 0.6},
    "sh3": {1: 0.3, 5: 0.4, 6: 0.6, 8: 0.6},
    "sh4": {1: 0.3, 3: 0.3, 4: 0.3, 6: 0.3, 7: 0.25, 8: 1.2},
    "sh5": {1: 0.3, 4: 0.2, 6: 0.3, 7: 0.2, 8: 0.9},
    "sh7": {1: 0.3, 3: 0.3, 5: 0.4, 6: 0.3, 7: 0.9},
    "sh8": {1: 0.3, 3: 0.3, 6: 0.3, 8: 0.9},
}
TAIL = 0.6        # na de laatste regel


def timeline(code):
    """{regel: (start, eind)} voor de hele short, uit de stembestanden en GAPS."""
    files = sorted(_glob.glob(os.path.join(AUDIO, code.upper(), f"{code.upper()}-*_Verteller.mp3")))
    t, out = 0.0, {}
    for p in files:
        n = int(re.findall(r"-(\d+)_", os.path.basename(p))[0])
        t += GAPS.get(code, {}).get(n, 0.12)
        d = audio_len(p)
        out[n] = (t, t + d)
        t += d
    return out


class Short(Scene):
    def __init__(self, code, part, set_name=None, variant=None, lines=(), t0=None, t1=None, samples=16):
        super().__init__(code, set_name, variant, samples=samples)
        self.part = part
        sc = self.sc
        sc.render.resolution_x, sc.render.resolution_y = W, H
        self.L = timeline(code)
        last = max(self.L)
        self.total = self.L[last][1] + TAIL
        self.mylines = list(lines)
        for n in self.mylines:
            a, b = self.L[n]
            self.voice.append((os.path.relpath(voice_file(f"{code.upper()}-{n:02d}"), AUDIO), a))
        # stuk van de tijdlijn dat dit deel rendert
        self.t0 = t0 if t0 is not None else (0.0 if 1 in self.mylines else self.L[min(self.mylines)][0] - 0.1)
        self.t1 = t1 if t1 is not None else (self.total if last in self.mylines else self.L[max(self.mylines) + 1][0] - 0.1)
        self.t = self.t0
        p = os.path.join(AUDIO, code.upper(), "zinnen.txt")
        self.script = [l_.strip() for l_ in open(p, encoding="utf-8") if l_.strip()] if os.path.exists(p) else []

    # -- staand kader: de beeldhoogte is de 36 mm-kant van de sensor -------------------
    def shot(self, ch, t=0.0, size="med", az=25.0, lens=35, h=0.0, lr=0.0, up=0.0, dist=None):
        # staand beeld is smal: neem 1,6x zoveel hoogte, anders vult het chibi-hoofd de hele breedte
        fh = (self.SIZES[size] if isinstance(size, str) else size) * 1.6
        return super().shot(ch, t, fh, az, lens, h, lr, up, dist=dist or fh * lens / 36.0)

    def lip(self, ch, n, gain=1.1):
        """Lipsync van ch op stemregel n (als het personage zelf spreekt)."""
        A.lipsync(ch, voice_file(f"{self.code.upper()}-{n:02d}"), F(self.L[n][0]), gain=gain)

    # -- tekst ------------------------------------------------------------------------
    def _captions(self):
        """Woordgroepjes van max ~16 tekens, de tijd verdeeld naar het aantal tekens."""
        last = max(self.L)
        for n in self.mylines:
            if n == last or n - 1 >= len(self.script):
                continue                      # de oproep staat al op de eindkaart
            t0, t1 = self.L[n]
            words = re.sub(r"\s+", " ", self.script[n - 1].replace("...", "... ")).split(" ")
            chunks, cur = [], ""
            for w_ in words:
                if not w_:
                    continue
                if cur and (len(cur) + 1 + len(w_) > 16 or cur[-1] in ".?!:"):
                    chunks.append(cur)
                    cur = w_
                else:
                    cur = (cur + " " + w_).strip()
            if cur:
                chunks.append(cur)
            tot = sum(len(c) + 3 for c in chunks)
            a, b = t0 + 0.05, t1 - 0.12
            tt = a
            for c in chunks:
                d = (b - a) * (len(c) + 3) / tot
                self.texts.append(dict(body=c.upper(), t0=tt, t1=tt + d, loc=(0.5, 0.30), size=120, color=WHITE,
                                       anchor=("CENTER", "CENTER"), pop=False))
                tt += d

    def counter(self, body, t0, t1=None, color=YELLOW, size=150, sub=None, tick=True):
        """Grote teller onder de titel (DAY 2 / HOUR 3 / 10,000x). t1=None: tot het eind van dit deel."""
        t1 = self.t1 if t1 is None else t1
        self.texts.append(dict(body=body, t0=t0, t1=t1, loc=(0.5, 0.79), size=size, color=color,
                               anchor=("CENTER", "CENTER"), pop=True))
        if sub:
            self.texts.append(dict(body=sub, t0=t0 + 0.1, t1=t1, loc=(0.5, 0.735), size=66, color=WHITE,
                                   anchor=("CENTER", "CENTER"), pop=True))
        if tick:
            self.sfx("sfx_hud_tik", t0, 0.5)

    def real(self, t0, t1):
        self.texts.append(dict(body="THIS PART IS REAL", t0=t0, t1=t1, loc=(0.5, 0.68), size=62, color=CYAN,
                               anchor=("CENTER", "CENTER"), pop=True))

    def music_all(self, name, vol=0.3, start=0.0, fade_in=0.6):
        """Muziek voor de hele short (zet dit in deel a)."""
        self.music(name, 0.0, self.total, vol=vol, fade_in=fade_in, fade_out=0.8, start=start)

    # -- afronden -------------------------------------------------------------------
    def done(self):
        code, last = self.code, max(self.L)
        if 1 in self.mylines:
            # titel bovenin de hele short; eindkaart over de oproep
            ti = TITLES.get(code, ("WHAT IF", ""))
            self.texts.append(dict(body=ti[0], t0=0.0, t1=self.total, loc=(0.5, 0.925), size=86, color=WHITE,
                                   anchor=("CENTER", "CENTER"), pop=False))
            self.texts.append(dict(body=ti[1], t0=0.0, t1=self.total, loc=(0.5, 0.885), size=86, color=YELLOW,
                                   anchor=("CENTER", "CENTER"), pop=False))
        if last in self.mylines:
            c0 = self.L[last][0]
            self.card("LIKE & SUBSCRIBE", c0 + 0.1, self.total, size=150, dim=0.62, color=YELLOW,
                      sub="FOR THE FULL VERSION", fin=6, fout=1)
            self.sfx("sfx_whoosh_titel", c0 - 0.1, 0.45)
        self._captions()
        self._finish_part()

    def _finish_part(self):
        sc = self.sc
        self.length = self.t1
        sc.frame_start, sc.frame_end = F(self.t0), F(self.t1) - 1
        for i, ch in enumerate(self.cast):
            end = F(getattr(ch, "frozen", None) or self.t1)     # bevroren figuren: geen knipperen of ademen meer
            if end > F(self.t0) + 2:
                A.blinks(ch, F(self.t0), end, seed=i * 3 + 1)
                A.alive(ch, F(self.t0), end, energy=getattr(ch, "energy", 1.0), seed=i * 5 + 2)
        # camera's: het eerste shot begint op t0
        if self.cams:
            first = min(self.cams, key=lambda c: c["t0"])
            first["t0"] = min(first["t0"], self.t0)
        self._build_cams()
        os.makedirs(self.out, exist_ok=True)
        part = dict(part=self.part, t0=self.t0, t1=self.t1, voice=self.voice, sounds=self.sounds, texts=self.texts,
                    cards=self.cards)
        with open(os.path.join(self.out, f"deel_{self.part}.json"), "w") as fh:
            json.dump(part, fh, indent=1)
        merge(self.out, self.total, self.code)
        sc.render.resolution_percentage = self.args.pct
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(self.out, "frames", "")
        try:
            sc.eevee.taa_render_samples = self.args.samples
        except Exception:
            pass
        sc.frame_set(F(self.t0))
        if not self.args.nosave:
            blend = os.path.join(self.out, f"{self.code}{self.part}.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
            print("OPGESLAGEN", blend, f"{self.t0:.2f}-{self.t1:.2f} s van {self.total:.2f} s")
        if self.args.stills:
            if self.args.stills == "auto":
                times = [round((a + b) / 2, 2) for a, b, _ in self.shots]
            else:
                times = [float(x) for x in self.args.stills.split(",")]
            for t in times:
                sc.frame_set(F(t))
                for a, b, cam in self.shots:
                    if a <= t < b:
                        sc.camera = cam
                sc.render.filepath = os.path.join(self.out, "stills", f"{self.code}{self.part}_t{t:05.1f}.png")
                bpy.ops.render.render(write_still=True)
            sc.render.filepath = os.path.join(self.out, "frames", "")
        if self.args.render:
            bpy.ops.render.render(animation=True)
            print("KLAAR: frames", sc.frame_start, "-", sc.frame_end, "in", os.path.join(self.out, "frames"))


def merge(out, total, code):
    """Voegt de deel_*.json samen tot montage.json voor anim/edit/montage.py."""
    spec = dict(code=code, length=total, picture_end=total, voice=[], sounds=[], texts=[], cards=[], title=None)
    for p in sorted(_glob.glob(os.path.join(out, "deel_*.json"))):
        d = json.load(open(p))
        for k in ("voice", "sounds", "texts", "cards"):
            spec[k] += d[k]
    with open(os.path.join(out, "montage.json"), "w") as fh:
        json.dump(spec, fh, indent=1)


# ---------------------------------------------------------------------------
# Kleine hulpjes voor de shorts
# ---------------------------------------------------------------------------
def materials_of(ch):
    return [o for o in bpy.data.objects if o.type == "MESH" and o.parent == ch.rig]


def body_copy(S, ch, mat, name):
    """Een tweede lichaam op hetzelfde skelet, helemaal in één materiaal (hout, staal, glas ...).
    Met show() wissel je tussen het gewone lichaam en de kopieën."""
    src = [o for o in ch.rig.children if o.type == "MESH"]
    out = []
    for o in src:
        c = o.copy()
        c.data = o.data.copy()
        c.name = f"{o.name}_{name}"
        for coll in o.users_collection:
            coll.objects.link(c)
        for i in range(len(c.material_slots)):
            c.material_slots[i].link = "OBJECT"
            c.material_slots[i].material = mat
        out.append(c)
    return out


def show_objs(objs, t0, t1=None):
    for o in objs:
        show(o, t0, t1)


# -- materiaal dat zich over het lichaam verspreidt (SH4) ------------------------------------
def spread_shader(kind):
    """Schaduw-netwerk voor een materiaal dat over het lichaam kruipt: 'hout', 'staal' of 'glas'.
    Geeft een functie die (nodes, links) krijgt en een shader-socket teruggeeft."""
    def build(N, L):
        g = N.new("ShaderNodeGroup")
        g.node_tree = bpy.data.node_groups["ToonLicht"]
        if kind == "hout":
            tc = N.new("ShaderNodeTexCoord")
            wv = N.new("ShaderNodeTexWave")
            wv.inputs["Scale"].default_value = 7.0
            wv.inputs["Distortion"].default_value = 4.0
            wv.inputs["Detail"].default_value = 1.0
            L.new(tc.outputs["Object"], wv.inputs["Vector"])
            rp = N.new("ShaderNodeValToRGB")
            rp.color_ramp.elements[0].color = (0.42, 0.22, 0.09, 1)
            rp.color_ramp.elements[1].color = (0.66, 0.40, 0.18, 1)
            L.new(wv.outputs["Fac"], rp.inputs[0])
            L.new(rp.outputs[0], g.inputs["Kleur"])
            return g.outputs[0]
        if kind == "staal":
            g.inputs["Kleur"].default_value = (0.58, 0.62, 0.68, 1)
            gl = N.new("ShaderNodeBsdfGlossy")
            gl.inputs["Roughness"].default_value = 0.25
            gl.inputs["Color"].default_value = (0.8, 0.85, 0.9, 1)
            mx = N.new("ShaderNodeMixShader")
            mx.inputs[0].default_value = 0.3
            L.new(g.outputs[0], mx.inputs[1])
            L.new(gl.outputs[0], mx.inputs[2])
            return mx.outputs[0]
        # glas: licht blauw, half doorzichtig, met een glimrand
        g.inputs["Kleur"].default_value = (0.72, 0.9, 1.0, 1)
        tr = N.new("ShaderNodeBsdfTransparent")
        lw = N.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.35
        mp = N.new("ShaderNodeMapRange")
        mp.inputs["To Min"].default_value = 0.35
        mp.inputs["To Max"].default_value = 0.9
        L.new(lw.outputs["Facing"], mp.inputs[0])
        mx = N.new("ShaderNodeMixShader")
        L.new(mp.outputs[0], mx.inputs[0])
        L.new(tr.outputs[0], mx.inputs[1])
        L.new(g.outputs[0], mx.inputs[2])
        return mx.outputs[0]
    return build


def material_spread(ch, stages, skip=("_vlak", "Contour")):
    """stages = [(kind, empty), ...]. Per stadium kruipt het materiaal vanaf het lege object over het lichaam:
    alles binnen een bol met straal = schaal van het lege object. Later stadium wint. Ogen/mond blijven gewoon."""
    done = set()
    for o in ch.rig.children_recursive:
        if o.type != "MESH":
            continue
        for slot in o.material_slots:
            mt = slot.material
            if mt is None or mt.name in done or any(s in mt.name for s in skip) or not mt.use_nodes:
                continue
            done.add(mt.name)
            N, L = mt.node_tree.nodes, mt.node_tree.links
            out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
            if not out.inputs["Surface"].links:
                continue
            cur = out.inputs["Surface"].links[0].from_socket
            for kind, emp in stages:
                tc = N.new("ShaderNodeTexCoord")
                tc.object = emp
                ln = N.new("ShaderNodeVectorMath")
                ln.operation = "LENGTH"
                L.new(tc.outputs["Object"], ln.inputs[0])
                nz = N.new("ShaderNodeTexNoise")
                nz.inputs["Scale"].default_value = 9.0
                ad = N.new("ShaderNodeMath")
                ad.operation = "MULTIPLY_ADD"
                tg = N.new("ShaderNodeTexCoord")
                L.new(tg.outputs["Object"], nz.inputs["Vector"])
                L.new(nz.outputs["Fac"], ad.inputs[0])
                ad.inputs[1].default_value = 0.35
                L.new(ln.outputs["Value"], ad.inputs[2])
                lt = N.new("ShaderNodeMath")
                lt.operation = "LESS_THAN"
                L.new(ad.outputs[0], lt.inputs[0])
                lt.inputs[1].default_value = 1.15
                mx = N.new("ShaderNodeMixShader")
                L.new(lt.outputs[0], mx.inputs[0])
                L.new(cur, mx.inputs[1])
                L.new(spread_shader(kind)(N, L), mx.inputs[2])
                cur = mx.outputs[0]
            L.new(cur, out.inputs["Surface"])


def spreader(S, ch, name, t0, t1, r1=2.5, bone="hand.R"):
    """Leeg object op de hand; groeit van niets (t0) tot straal r1 (t1). Daarna blijft het groot."""
    emp = bpy.data.objects.new(name, None)
    T._link(emp)
    attach(emp, ch, bone)
    key(emp, 0, scale=0.001)
    key(emp, t0, scale=0.001)
    key(emp, t1, scale=r1)
    return emp


def rock(name, loc, r, mat, seed=0, squash=0.75, ol=0.01, sub=2):
    """Onregelmatige steen/korrel (ijsbol met verschoven punten)."""
    import bmesh
    rnd = random.Random(seed)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    sx, sy = rnd.uniform(0.8, 1.25), rnd.uniform(0.8, 1.25)
    for v in bm.verts:
        n = noise.noise(v.co * (2.2 / r) + Vector((seed * 3.1, seed, 0)))
        v.co = v.co * (1 + 0.28 * n)
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * squash))
    bm.to_mesh(me)
    bm.free()
    o = T._obj(name, me, mat, tuple(loc), (0, 0, rnd.uniform(0, 360)), ol * r)
    return o


def parent_keep(objs, parent):
    """Hang objecten aan een leeg object zonder dat ze verspringen."""
    bpy.context.view_layer.update()
    for o in objs:
        o.parent = parent
        o.matrix_parent_inverse = parent.matrix_world.inverted()


def face_points(S, ch, t, fwd, region, step=0.022, depth=1.5):
    """Punten op het gezicht (wereld) via stralen naar het hoofd, op tijd t. fwd = kijkrichting van het figuur.
    region(u, v) -> True houdt een punt (u = links/rechts, v = op/neer t.o.v. het hoofdmidden, in meters)."""
    sc = S.sc
    sc.frame_set(F(t))
    dg = bpy.context.evaluated_depsgraph_get()
    hc = S.headpos(ch, t)
    fwd = Vector(fwd).normalized()
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    out = []
    n = int(0.4 / step)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * step, j * step
            if not region(u, v):
                continue
            o = hc + side * u + Vector((0, 0, v)) + fwd * depth
            hit, loc, nor, idx, ob, M = sc.ray_cast(dg, o, -fwd)
            if hit and ob and ob.parent == ch.rig:
                out.append(loc + nor * 0.004)
    return out


def attach_keep(obj, ch, bone, t):
    """Hang obj aan een bot zonder dat het verspringt (zoals het nu op tijd t in de wereld staat)."""
    S_frame = bpy.context.scene
    S_frame.frame_set(F(t))
    pb = ch.rig.pose.bones[bone]
    Mb = ch.rig.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
    W_ = obj.matrix_world.copy()
    obj.parent = ch.rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_parent_inverse = Mb.inverted()
    obj.matrix_basis = W_


def eye_glow(ch, keys, color=(0.85, 0.95, 1.0), strength=8.0, slots=range(8, 22)):
    """Ogen gloeien wit op (SH3). keys = [(t, 0..1), ...]. De oogmaterialen zijn Material_8 ... Material_21."""
    for o in ch.rig.children_recursive:
        if o.type != "MESH":
            continue
        for slot in o.material_slots:
            mt = slot.material
            if mt is None or not mt.use_nodes:
                continue
            m = re.search(r"Material_(\d+)\.", mt.name)
            if not m or int(m.group(1)) not in slots or "gloei" in mt.get("fx", ""):
                continue
            mt["fx"] = "gloei"
            N, L = mt.node_tree.nodes, mt.node_tree.links
            out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
            if not out.inputs["Surface"].links:
                continue
            cur = out.inputs["Surface"].links[0].from_socket
            em = N.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*color, 1)
            em.inputs["Strength"].default_value = strength
            mx = N.new("ShaderNodeMixShader")
            L.new(cur, mx.inputs[1])
            L.new(em.outputs[0], mx.inputs[2])
            L.new(mx.outputs[0], out.inputs["Surface"])
            for t, v in keys:
                mx.inputs[0].default_value = v
                mx.inputs[0].keyframe_insert("default_value", frame=F(t))


def tele_fx(S, pos, t, sound=True, vol=0.4):
    """Teleport-effect op pos (voeten): blauwe vonkjes, ring en een lichtflits."""
    pos = Vector(pos)
    S.puff(pos + Vector((0, 0, 0.8)), t, n=8, r=(0.12, 0.3), grow=1.8, dur=0.5, color=(0.55, 0.8, 1.0), rise=0.4, spread=0.4)
    S.debris(pos + Vector((0, 0, 0.9)), t, n=16, size=(0.02, 0.04), color=(0.7, 0.9, 1.0), speed=(1.0, 2.5), up=0.6,
             floor=pos.z, life=0.8, name="Vonk")
    lamp = T.point_light(S._fxname("Teleportlicht"), tuple(pos + Vector((0, 0, 1.0))), color=(0.6, 0.85, 1.0), energy=0,
                         radius=0.2)
    for tt, e in ((t - 0.05, 0), (t, 300), (t + 0.35, 0)):
        lamp.data.energy = e
        lamp.data.keyframe_insert("energy", frame=F(tt))
    if sound:
        S.sfx("sfx_teleport", t - 0.05, vol)
