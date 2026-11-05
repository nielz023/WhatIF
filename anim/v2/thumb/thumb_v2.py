"""Thumbnail video 2 "What IF You Got 10x FASTER Every Day?".

Zelfde moment als het eerste beeld van de video (cold open, dag 4, 1.000x): het broertje in zijn
dinopyjama bevroren midden op straat, de vuilniswagen met koplampen aan op drie meter, de kraai
en de plastic zak hangen stil. Voor de thumbnail stormt hij erop af in super speed, met een
gloeiend snelheidsspoor achter zich en rokende schoenen.

Drie camera's = drie varianten (A breed laag, B dichtbij zijn gezicht, C broertje + wagen).
Tekst en HUD komen erbij in thumb_tekst.py (PIL).

    WHATIF_ENGINE=CYCLES blender -b -P anim/v2/thumb/thumb_v2.py -- --stills 0.5,1.5,2.5 --samples 96 \
        --out out/thumb_v2 --nosave
"""
import os
import sys

os.environ.setdefault("WHATIF_ENGINE", "CYCLES")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

EXPO = float(os.environ.get("THUMB_EXPO", "0.25"))   # lessen video 2: beeld niet dof, belichting 0..+0,3


class Thumb(Scene2):
    def post_cams(self):
        super().post_cams()
        sc = self.sc
        sc.view_settings.exposure = EXPO
        sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
        sc.render.film_transparent = False
        if sc.render.engine == "CYCLES":
            sc.cycles.use_adaptive_sampling = True
            sc.cycles.adaptive_threshold = 0.02


S = Thumb("thumb_v2", "straat", "grijs")

# ---------------------------------------------------------------- set (zoals f01)
BRO_AT = V(-1.4, 1.2, 0)
TRUCK_X = -8.75                                  # neus op ~3 m van het broertje
truck = S.obj("Vuilniswagen")
truck.location = (TRUCK_X, 1.5, 0)
S.obj("Auto_geparkeerd_2").location.x = -21.0
for o in bpy.data.objects:
    if o.name.startswith("Raamtekst"):
        o.hide_render = True
S.obj("Kraai").hide_render = True
crow = G.crow("kraai", (-3.0, 1.6, 2.9), rot_z=-80, wing=40)
bag = S.obj("Plastic_zak")
bag.location = (-2.6, 0.2, 1.45)

# koplampen extra op het gezicht van het broertje ("headlights on his cheek")
for y, nm in ((0.75, "L"), (2.25, "R")):
    ld = bpy.data.lights.new(f"Thumb_koplamp_{nm}", "SPOT")
    ld.energy, ld.color, ld.spot_size, ld.spot_blend = 900, (1.0, 0.93, 0.78), math.radians(38), 0.6
    ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(ld.name, ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.location = (TRUCK_X + 4.35, y, 0.85)
    lo.rotation_euler = (BRO_AT + V(0, 0, 0.9) - lo.location).to_track_quat("-Z", "Y").to_euler()
    lo.visible_camera = False

# ---------------------------------------------------------------- figuren
bro = S.actor("broertje_dino", BRO_AT, 0, frozen=True)
run_pose(S, bro, 0.0, front="R", amount=0.85, lift=0.14, reach=0.12, back=0.16, face="blij", look=(0.15, 0.1))
A.key_prop(bro.rig, "mond_open", 0.35, F(0.0))
S.hold(bro, 3.0)

HERO_AT = V(0.9, 1.05, 0)                        # stormt van rechts op hem af (naar -x)
held = S.actor("hoofdpersonage", HERO_AT, heading(HERO_AT, BRO_AT))
run_pose(S, held, 0.0, front="L", amount=1.0, lift=0.28, reach=0.3, back=0.34, face="vastberaden",
         look=(0.0, 0.05), pose="sprint")
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
S.hold(held, 3.0)

# snelheidsspoor: gloeiende kopieën achter hem (+x) en rokende schoenen
G.ghosts(held, F(0.0), [V(0.32 * k, 0.0, 0.0) for k in range(1, 6)],
         alphas=[0.55, 0.40, 0.28, 0.18, 0.10], tint="#9CCBFF")
G.smoke(held, "foot.L", t0=F(0.0) - 30, t1=F(0.0) + 10, n=7, rise=0.35, size=0.07, seed=3)
G.smoke(held, "foot.R", t0=F(0.0) - 30, t1=F(0.0) + 10, n=7, rise=0.35, size=0.07, seed=7)

# ---------------------------------------------------------------- camera's (één per variant)
HB = S.head(bro, 0)
HH = S.headpos(held, 0)
# A: breed en laag vanaf de stoep: wagen links, broertje midden, hij rechts met spoor
S.cam(0.0, ((-0.2, -4.6, 0.55), (-1.6, 1.4, 1.15), 22), dof=None, handheld=0)
# B: dichtbij zijn gezicht, broertje en koplampen achter hem
S.cam(1.0, (HH + V(-1.25, -1.15, -0.25), HH + V(-0.15, 0.05, -0.1), 30), dof=None, handheld=0)
# C: laag vóór het broertje: zijn gezicht in het koplamplicht, de wagen erachter, hij komt van rechts
S.cam(2.0, ((0.9, -2.6, 0.45), (-2.2, 1.6, 1.2), 24), dof=None, handheld=0)

S.finish(length=3.0, picture_end=3.0)
