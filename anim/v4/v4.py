"""Raamwerk voor video 4 "What IF You Could Never Die?" (bovenop anim/v3/v3.py).

Nieuw t.o.v. video 3:
- cast_v4 (WHATIF_CAST): hoofdpersonage per tijdperk (hoofdpersonage_kind, _pak, _2200, _ijs, _zwerver, _rafels),
  leeftijdsvarianten (mama_oud, broertje_oud, pestkop_oud ...);
- HUD rechtsboven "YEAR 2026  ·  AGE 14": YEAR springt met een pop en een horlogetik, AGE blijft altijd 14;
  S.years([(t, 3030), (t2, 3045)]) laat de teller ratelen; S.year_rattle() rolt snel door (tijdsprong);
- opa's zakhorloge als prop in de hand: S.watch(ch, ...) met klep, wijzers die tikken, lume en gravure;
- tik van het horloge: S.tick(t) (droog, dichtbij), boven alles hoorbaar maar zacht;
- stemmen staan in assets/audio/Dnn (regels in videos/never-die/regels.tsv).

    from v4 import *
    S = Scene4("d05", "keuken", "verjaardag")
    held = S.actor("hoofdpersonage_kind", (0, 0, 0), 0)
    S.year(2026, t0=0.0)
    ...
    S.finish(length=END, tail=0.0)
"""
import math
import os
import sys

os.environ.setdefault("WHATIF_CAST", "cast_v4,cast_v3")   # figuranten uit video 3 als achtergrond
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "v3"))
from v3 import *  # noqa: E402,F401,F403
import v3 as _v3  # noqa: E402
from lib import nooitdood as ND  # noqa: E402

SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def year_fmt(y):
    """2026 -> '2026', 1000000 -> '1,000,000', 'googol' -> '10¹⁰⁰', '100T' -> '100 TRILLION'."""
    if isinstance(y, str):
        if y == "googol":
            return "10" + "100".translate(SUP)
        if y.endswith("T"):
            return y[:-1] + " TRILLION"
        return y
    if y < 10000:
        return str(y)
    return f"{y:,}"


class Scene4(_v3.Scene3):
    def __init__(self, code, set_name=None, variant=None, samples=None, exposure=0.15, night=False):
        super().__init__(code, set_name, variant, samples=samples, exposure=exposure, night=night)

    # -- HUD -------------------------------------------------------------------------
    def year(self, seq, t0=0.3, t1=None, tick=True, big=False):
        """'YEAR 2026  ·  AGE 14' rechtsboven. seq = jaartal of [(t, jaar), ...]. Elke sprong: pop + horlogetik.
        big=True: eerst 1,3 s groot in het midden (tijdsprong), daarna rechtsboven."""
        t1 = t1 if t1 is not None else 10 ** 6
        seq = seq if isinstance(seq, list) else [(t0, seq)]
        if big:
            v = seq[0][1]
            self.texts.append(dict(body=f"YEAR {year_fmt(v)}{DOT}AGE 14", t0=seq[0][0], t1=seq[0][0] + 1.3,
                                   loc=(0.5, 0.55), size=118, color=HUD_W, anchor=("CENTER", "CENTER"), pop=True, hud=True))
            if tick:
                self.tick(seq[0][0], 0.55)
            b = seq[0][0] + 1.3
            seq = [(max(t, b), v) for t, v in seq]
        for i, (ta, v) in enumerate(seq):
            tb = seq[i + 1][0] if i + 1 < len(seq) else t1
            if tb - ta < 1e-3:
                continue
            self.texts.append(dict(body=f"YEAR {year_fmt(v)}{DOT}AGE 14", t0=ta, t1=tb, loc=(0.965, 0.94), size=72,
                                   color=HUD_W if i == 0 else HUD_Y, anchor=("RIGHT", "TOP"), pop=True, hud=True))
            if tick and (i > 0 or not big):
                self.sfx("sfx_hud_tik", ta, 0.5)
        self._hud_t1 = t1

    def year_rattle(self, y0, y1, t0, dur, t1=None, steps=16):
        """Teller ratelt van y0 naar y1 (alleen gehele jaren) en stopt met een pop."""
        seq = []
        for k in range(steps):
            w = (k / (steps - 1)) ** 0.7
            seq.append((t0 + dur * k / (steps - 1), int(round(y0 + (y1 - y0) * w))))
        seq[-1] = (t0 + dur, y1)
        for i, (ta, v) in enumerate(seq):
            tb = seq[i + 1][0] if i + 1 < len(seq) else (t1 if t1 is not None else 10 ** 6)
            self.texts.append(dict(body=f"YEAR {year_fmt(v)}{DOT}AGE 14", t0=ta, t1=tb, loc=(0.965, 0.94), size=72,
                                   color=HUD_Y if i == len(seq) - 1 else HUD_W, anchor=("RIGHT", "TOP"),
                                   pop=(i == 0 or i == len(seq) - 1), hud=True))
        self.sfx("sfx_letter_tik", t0, 0.25, loop_to=t0 + dur)
        self.tick(t0 + dur, 0.6)

    # -- geluid ------------------------------------------------------------------------
    def tick(self, t, vol=0.45):
        """Eén droge tik van opa's horloge (dichtbij)."""
        self.sfx("sfx_horloge_tik", t, vol, cut=(0.0, 0.45))

    def ticks(self, t0, t1, every=1.0, vol=0.3):
        t = t0
        while t < t1 - 0.05:
            self.tick(t, vol)
            t += every

    def jump(self, t, vol=0.5):
        """Tijdsprong: whoosh + tik (harde cut naar de heuvel)."""
        self.sfx("sfx_whoosh", t - 0.25, vol * 0.8)
        self.tick(t, vol)

    # -- opa's zakhorloge in de hand --------------------------------------------------------
    def watch(self, ch=None, t=0.0, side="R", name="Zakhorloge", open_=0.0, loc=(0, 0.075, 0.0), rot=(0, 0, 0), release=None,
              world=None, scale=1.0, tijd=(10, 10, 32), **kw):
        """Opa's zakhorloge. Met ch: in de hand (gegrepen op t, wijzerplaat naar boven als de hand plat ligt).
        Zonder ch: los neergezet op `world` (positie) met `rot` in graden. Geeft het root-object terug.
        Het horloge is maar 5 cm: zet scale=1.6 als het in een wijd shot zichtbaar moet zijn (chibi-handen)."""
        root = ND.zakhorloge(name, (0, 0, 0), rot=(0, 0, 0), open_=open_, tijd=tijd, **kw)
        root.scale = (scale,) * 3
        if ch is not None:
            grab(self, root, ch, t, f"hand.{side}", loc=loc, rot=rot, release=release)
        else:
            root.location = Vector(world or (0, 0, 0))
            root.rotation_euler = tuple(math.radians(a) for a in rot)
        return root

    def watch_open(self, name, t0, t1, a=0.0, b=1.0):
        """Klep open (b=1) of dicht (b=0) tussen t0 en t1."""
        klep = bpy.data.objects.get(name + "_klep")
        if klep is None:
            return
        for t, v in ((t0, a), (t1, b)):
            klep.rotation_euler.y = -2.8 * v
            klep.keyframe_insert("rotation_euler", index=1, frame=F(t))

    def watch_hands(self, name, t0, t1, every=1.0, start=(10, 10, 32), stop=None):
        """Secondewijzer tikt (CONSTANT) van t0 tot t1; stop = tijd waarna hij stilstaat."""
        sec = bpy.data.objects.get(name + "_wijzer_sec")
        if sec is None:
            return
        s0 = start[2]
        t = t0
        k = 0
        while t <= t1 + 1e-3:
            if stop is not None and t > stop:
                break
            sec.rotation_euler.z = -math.radians(6 * (s0 + k))
            sec.keyframe_insert("rotation_euler", index=2, frame=F(t))
            t += every
            k += 1
        for fc in A._fcurves(sec):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

    def glow_key(self, mat_name, t, strength, interp="LINEAR"):
        emission_key(mat_name, t, strength, interp=interp)

    # -- algemeen ------------------------------------------------------------------------
    def hide(self, *prefixes):
        for o in bpy.data.objects:
            if o.name.startswith(prefixes):
                o.hide_render = o.hide_viewport = True


def vis(obj, t0, t1=None):
    """Zichtbaar van t0 tot t1 (met kinderen)."""
    show(obj, t0, t1)


class Body:
    """Hele figuur kantelen om de heup: vallen, op de grond liggen, rechtop gaan zitten.
    Het rig hangt onder een leeg object op de heup; beweeg dat met key(). Gebruik daarna geen
    place/teleport/walk/at= meer voor dit figuur (die rekenen zonder ouder).
    tilt = graden achterover (0 = rechtop, ~78 = plat op de rug met het grote hoofd op de grond)."""

    def __init__(self, S, ch, hip, rot=0.0):
        self.S, self.ch, self.rot = S, ch, rot
        self.P = ch.J["pelvis"].z
        self.L = self.P - ch.J["ankle.L"].z
        piv = bpy.data.objects.new(S._fxname("Heup_draaipunt"), None)
        T._link(piv)
        piv.location = Vector(hip)
        piv.rotation_euler = (0, 0, math.radians(rot))
        ad = ch.rig.animation_data
        if ad and ad.action:
            for fc in list(A._fcurves(ch.rig)):
                if fc.data_path in ("location", "rotation_euler"):
                    try:
                        ad.action.fcurves.remove(fc)
                    except Exception:
                        fc.keyframe_points.clear()
        ch.rig.parent = piv
        ch.rig.matrix_parent_inverse = Matrix.Identity(4)
        ch.rig.location = (0, 0, -self.P)
        ch.rig.rotation_euler = (0, 0, 0)
        ch.rig.keyframe_insert("location", frame=1)
        ch.rig.keyframe_insert("rotation_euler", frame=1)
        ch.last = None
        self.piv = piv

    def key(self, t, hip, tilt=0.0, roll=0.0, yaw=None, interp=None):
        p = self.piv
        p.location = Vector(hip)
        p.rotation_euler = (math.radians(-tilt), math.radians(roll), math.radians(self.rot if yaw is None else yaw))
        p.keyframe_insert("location", frame=F(t))
        p.keyframe_insert("rotation_euler", frame=F(t))
        if interp:
            for fc in A._fcurves(p):
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - F(t)) < 0.5:
                        kp.interpolation = interp

    def legs(self, tilt, spread=0.10, bend=0.97, lift=0.0):
        """Benen plat vooruit over de grond bij kanteling tilt (zittend 0, liggend ~78). Voor beat(**...)."""
        a = math.radians(tilt + lift)
        fwd = bend * self.L * math.cos(a)
        up = self.L - bend * self.L * math.sin(a)
        return dict(crouch=(0.0, 0.0), feet=((spread * 0.3, fwd, up), (-spread * 0.3, fwd * 0.97, up)))

    def hip_world(self, t):
        return self.S.bone_world(self.ch, "hips", t, tail=False)

    def at(self, t):
        """Wereldpositie van de heup volgens de keys van het draaipunt (voor camera's die meelopen)."""
        loc = list(self.piv.location)
        for fc in A._fcurves(self.piv):
            if fc.data_path == "location":
                loc[fc.array_index] = fc.evaluate(F(t))
        return Vector(loc)


def skin_tint(ch, keys, color=(0.42, 0.10, 0.62)):
    """Huid kleurt (bv. paars van de peper): keys = [(t, 0..1), ...]. Werkt op de huid-materialen van ch."""
    mats = {sl.material for o in ch.rig.children for sl in o.material_slots if sl.material and "huid" in sl.material.name}
    for m in mats:
        nt = m.node_tree
        bs = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]
        if not bs:
            continue
        inp = bs[0].inputs["Base Color"]
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MIX"
        if inp.links:
            nt.links.new(inp.links[0].from_socket, mix.inputs[6])
        else:
            mix.inputs[6].default_value = inp.default_value
        mix.inputs[7].default_value = tuple(color) + (1.0,)
        nt.links.new(mix.outputs[2], inp)
        for t, v in keys:
            mix.inputs[0].default_value = v
            mix.inputs[0].keyframe_insert("default_value", frame=F(t))
