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
            A.blinks(ch, F(self.t0), F(self.t1), seed=i * 3 + 1)
            A.alive(ch, F(self.t0), F(self.t1), energy=getattr(ch, "energy", 1.0), seed=i * 5 + 2)
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
