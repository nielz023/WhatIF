"""Raamwerk voor de 7 originele shorts (OR1-OR7, staand 1080x1920, ~20 s, 30 fps).

Bouwt op anim/shorts/short.py (delen per set op één gedeelde tijdlijn). Verschillen:
- stem: één ElevenLabs-take (v2.5) per short, per zin geknipt op woordtijden (videos/originele-shorts/knip.py);
  de pauzes zitten al in de clips, dus bijna geen extra GAPS;
- ondertiteling op de echte woordtijden (videos/originele-shorts/woorden/ORn_regels.json), ook de laatste zin;
- eindkaart SUBSCRIBE na de cliffhanger (geen "full version": deze shorts staan op zichzelf);
- uitvoer in 30 fps (WHATIF_FPS, standaard 30), zoals de lange video's;
- titel en teller met een donkere balk erachter (leesbaar op lichte hoofden).

    python3 anim/shorts/or1a_badkamer.py -- [--render] [--stills auto|t1,t2] [--pct 25]
    blender -b -P anim/edit/montage.py -- or1
"""
import json
import math
import os
import re

import short as _sh
from short import *  # noqa: F401,F403

OR_TITLES = {
    "or1": ("WHAT IF YOUR REFLECTION", "STOPPED COPYING YOU?"),
    "or2": ("WHAT IF EVERYONE", "DISAPPEARED EXCEPT YOU?"),
    "or3": ("WHAT IF YOU COULD", "REWIND 10 SECONDS?"),
    "or4": ("WHAT IF GRAVITY TURNED", "OFF FOR 1 SECOND?"),
    "or5": ("WHAT IF YOU", "TURNED INVISIBLE?"),
    "or6": ("WHAT IF YOU NEVER", "NEEDED SLEEP AGAIN?"),
    "or7": ("WHAT IF THE MOON CAME", "2x CLOSER?"),
}
_sh.TITLES.update(OR_TITLES)
for _c in OR_TITLES:
    _sh.GAPS[_c] = {n: 0.03 for n in range(1, 12)}
_sh.GAPS["or1"].update({1: 0.15})
_sh.GAPS["or2"].update({4: 0.3, 6: 0.45})
_sh.GAPS["or3"].update({4: 0.2, 5: 0.25, 6: 0.25})
_sh.TAIL = 1.5                      # na de cliffhanger: eindkaart

OUT_FPS_OR = int(os.environ.get("WHATIF_FPS", "30"))
OFF = OUT_FPS_OR / 24.0             # beeld n toont t = (n - OFF) / OUT_FPS
WORDS = os.path.join(REPO, "videos", "originele-shorts", "woorden")


def NF(t):
    """Uitvoerbeeld (30 fps) voor tijd t."""
    return int(math.ceil(t * OUT_FPS_OR + OFF - 1e-6))


class ORShort(Short):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        p = os.path.join(WORDS, self.code.upper() + "_regels.json")
        self.words = json.load(open(p)) if os.path.exists(p) else {}

    def counter(self, body, t0, t1=None, color=YELLOW, size=150, sub=None, tick=True):
        super().counter(body, t0, t1, color, size, sub, tick)
        self.texts[-1 if not sub else -2]["box"] = True
        if sub:
            self.texts[-1]["box"] = True

    def _captions(self):
        """Woordgroepjes (max ~16 tekens) precies op de woordtijden uit de transcriptie."""
        for n in self.mylines:
            lid = f"{self.code.upper()}-{n:02d}"
            ws = self.words.get(lid)
            t0, t1 = self.L[n]
            if not ws:
                continue
            groups, cur = [], []
            for w in ws:
                txt = w["w"]
                if cur and (len(" ".join(x["w"] for x in cur)) + 1 + len(txt) > 16 or cur[-1]["w"][-1] in ".?!,"):
                    groups.append(cur)
                    cur = []
                cur.append(w)
            if cur:
                groups.append(cur)
            for i, g in enumerate(groups):
                a = t0 + g[0]["s"] - 0.04
                b = t0 + (groups[i + 1][0]["s"] - 0.04 if i + 1 < len(groups) else g[-1]["e"] + 0.25)
                b = min(b, t1 + 0.3)
                self.texts.append(dict(body=" ".join(x["w"] for x in g).upper(), t0=a, t1=b, loc=(0.5, 0.30), size=125,
                                       color=WHITE, anchor=("CENTER", "CENTER"), pop=False, box=True))

    def done(self):
        code, last = self.code, max(self.L)
        if 1 in self.mylines:
            ti = OR_TITLES[code]
            for k, (body, y, col) in enumerate(((ti[0], 0.925, WHITE), (ti[1], 0.885, YELLOW))):
                self.texts.append(dict(body=body, t0=0.0, t1=self.total, loc=(0.5, y), size=84, color=col,
                                       anchor=("CENTER", "CENTER"), pop=False, box=True))
        if last in self.mylines:
            c0 = self.L[last][1] + 0.35
            self.card("SUBSCRIBE", c0, self.total, size=170, dim=0.55, color=YELLOW, sub="FOR MORE WHAT IFS", fin=5, fout=1)
            self.cards[-1]["sub_scale"] = 0.5
            self.sfx("sfx_whoosh_titel", c0 - 0.15, 0.4)
        self._captions()
        self._finish_part()

    def _finish_part(self):
        sc = self.sc
        self.length = self.t1
        for i, ch in enumerate(self.cast):
            end = F(getattr(ch, "frozen", None) or self.t1)
            if end > F(self.t0) + 2:
                A.blinks(ch, F(self.t0), end, seed=i * 3 + 1)
                A.alive(ch, F(self.t0), end, energy=getattr(ch, "energy", 1.0), seed=i * 5 + 2)
        if self.cams:
            first = min(self.cams, key=lambda c: c["t0"])
            first["t0"] = min(first["t0"], self.t0)
        self._build_cams()
        os.makedirs(self.out, exist_ok=True)
        part = dict(part=self.part, t0=self.t0, t1=self.t1, voice=self.voice, sounds=self.sounds, texts=self.texts,
                    cards=self.cards)
        with open(os.path.join(self.out, f"deel_{self.part}.json"), "w") as fh:
            json.dump(part, fh, indent=1)
        merge_or(self.out, self.total, self.code)
        sc.render.resolution_percentage = self.args.pct
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(self.out, "frames", "")
        # 24-fps-animatie, opgerekt naar 30 fps; beeldnummers lopen door over alle delen
        sc.render.fps = OUT_FPS_OR
        sc.render.frame_map_old, sc.render.frame_map_new = 24, OUT_FPS_OR
        sc.frame_start, sc.frame_end = NF(self.t0), NF(self.t1) - 1
        sc.frame_set(sc.frame_start)
        if os.environ.get("WHATIF_ENGINE") == "WORKBENCH":   # snelle layout-stills in de container
            sc.render.engine = "BLENDER_WORKBENCH"
            sh = sc.display.shading
            sh.light, sh.color_type = "STUDIO", "MATERIAL"
            sh.show_shadows = True
            sc.view_settings.view_transform = "Standard"
            sc.view_settings.look = "None"
        if not self.args.nosave:
            blend = os.path.join(self.out, f"{self.code}{self.part}.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
            print("OPGESLAGEN", blend, f"{self.t0:.2f}-{self.t1:.2f} s van {self.total:.2f} s")
        if self.args.stills:
            if self.args.stills == "auto":
                times = []
                for a, b, _ in self.shots:
                    a, b = max(a, self.t0), min(b, self.t1)
                    if b > a:
                        times += [round(a + 0.1, 2), round((a + b) / 2, 2), round(b - 0.1, 2)]
            else:
                times = [float(x) for x in self.args.stills.split(",")]
            for t in times:
                sc.frame_set(NF(t))
                for a, b, cam in self.shots:
                    if a <= t < b:
                        sc.camera = cam
                sc.render.filepath = os.path.join(self.out, "stills", f"{self.code}{self.part}_t{t:05.2f}.png")
                bpy.ops.render.render(write_still=True)
            sc.render.filepath = os.path.join(self.out, "frames", "")
        if self.args.render:
            bpy.ops.render.render(animation=True)
            print("KLAAR: frames", sc.frame_start, "-", sc.frame_end, "in", os.path.join(self.out, "frames"))


def merge_or(out, total, code):
    _sh.merge(out, total, code)
    p = os.path.join(out, "montage.json")
    spec = json.load(open(p))
    spec["fps"] = OUT_FPS_OR
    json.dump(spec, open(p, "w"), indent=1)


def copy_anim(objs, src_a, src_b, dst_a, dst_b, skip_face=True):
    """Speel de animatie van objs uit [src_a, src_b] opnieuw af in [dst_a, dst_b] (src_a > src_b = achteruit,
    terugspoelen). Bakt elk beeld; gezichts-eigenschappen (["..."]) blijven vrij voor eigen beats."""
    bake_ = []
    for o in objs:
        for fc in A._fcurves(o):
            if skip_face and fc.data_path.startswith('["'):
                continue
            vals = []
            for f in range(F(dst_a), F(dst_b) + 1):
                u = ((f - 1) / FPS - dst_a) / max(dst_b - dst_a, 1e-6)
                ts = src_a + (src_b - src_a) * min(1.0, max(0.0, u))
                vals.append((f, fc.evaluate(ts * FPS + 1)))
            bake_.append((fc, vals))
    for fc, vals in bake_:
        for f, v in vals:
            fc.keyframe_points.insert(f, v, options={"FAST"})
        fc.update()
