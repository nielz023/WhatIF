"""N11e · Dag 5: op weg naar de apotheek (script scène 11e-11f), straat voor het huis, grijze ochtend, planken voor de ramen.
11e-1 MEDIUM push-in: de jongen komt het tuinpad af en gooit zijn rugzak over één schouder.
11e-2 MEDIUM: de beste vriend wacht op zijn rode fiets, één voet aan de grond, wiebelt ongeduldig.
      BESTE VRIEND: "The pharmacy is all the way downtown. You know that, right?"
11e-3 CLOSE: de jongen op zijn fiets. JONGEN: "Then we'd better go." Hij zet af.
11f-1 WIDE track achter de twee fietsen de lege straat uit.
11f-2 WIDE drone pull-back: twee stipjes in een lege stad.
      VO: "It's twelve kilometers to the nearest pharmacy. Twelve kilometers... through a city with no rules."

    blender -b -P anim/v3/scenes/n11e_vertrek.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n11e", "straat", "grijs", exposure=0.0)
sh = S.cuts([3.0, 2.6, 2.6, 3.0, 3.9])
END = sh[-1][1]
t_2, t_3, t_f1, t_f2 = [s[0] for s in sh[1:]]

for o in list(bpy.data.objects):
    if o.name.startswith(("Fiets_held", "Vuilniswagen", "Kraai", "Plastic_zak", "Raamtekst", "Koplamp")):
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# ---------------------------------------------------------------- planken voor de ramen (zoals papa ze op dag 3 timmerde)
PL = S.mat("plank_steigerhout", (0.62, 0.48, 0.32))
for x in (0, -12, 18, -30, 30):
    for k, (z, rx) in enumerate(((1.15, 4), (1.5, -3), (1.84, -2))):
        T.box(f"Raamplank_{x}_{k}", (x + 1.2, 12.86, z), (2.2, 0.035, 0.18), PL, rot=(0, rx + (x % 7) * 0.5, 0), base=False,
              bevel=0.005, ol=0.004)

# ---------------------------------------------------------------- de rugzak (per frame gebakken: eerst in de hand, dan op de rug)
BAG = S.mat("rugzak_groen", (0.20, 0.42, 0.30))
bag = T.box("Rugzak", (0, 0, 0), (0.30, 0.16, 0.38), BAG, base=False, bevel=0.05, ol=0.006)
T.box("Rugzak_vak", (0, -0.09, -0.07), (0.22, 0.04, 0.16), S.mat("rugzak_vak", (0.16, 0.34, 0.24)), base=False, bevel=0.02, ol=0.004).parent = bag
T.box("Rugzak_riem", (0.0, 0.0, 0.2), (0.12, 0.03, 0.06), S.mat("rugzak_riem", (0.1, 0.1, 0.1)), base=False, bevel=0.01, ol=0).parent = bag
bag.rotation_mode = "XYZ"

# ---------------------------------------------------------------- de jongen: tuinpad af met de rugzak
held = S.actor("hoofdpersonage_kind", (-1.4, 12.0, 0), 0)
T_SLING = 1.45
S.walk(held, 0.2, t_2 + 2.4, [V(-1.4, 12.0, 0), V(-1.4, 8.6, 0), V(-1.4, 8.2, 0.12)], stride=0.42)
S.beat(held, 0.0, "staan", face="vastberaden", face_amt=0.6, look=(0.0, 0.2))
S.reach(held, 0.0, "R", inf=0.0)
S.reach(held, T_SLING - 0.35, "R", inf=0.0)
BACK = V(0.06, 0.2, 0.86)            # lokaal t.o.v. de wortel: achter hem (+y), iets naar rechts (-x is rechts), op rughoogte
for f in range(F(0.0), F(t_3)):
    t = (f - 1) / FPS
    M = S._root_matrix(held, t)
    yaw = M.to_euler().z
    if t < T_SLING:
        loc = S.bone_world(held, "hand.R", t) + V(0, 0, -0.2)
        rot = (0.0, 0.0, yaw)
    elif t < T_SLING + 0.3:
        u = (t - T_SLING) / 0.3
        a = S.bone_world(held, "hand.R", t) + V(0, 0, -0.2)
        b = M @ BACK
        loc = a.lerp(b, u * u * (3 - 2 * u)) + V(0, 0, 0.35 * math.sin(math.pi * u))
        rot = (math.radians(-40 * math.sin(math.pi * u)), 0.0, yaw)
    else:
        sw = math.sin((t - T_SLING - 0.3) * 9.0) * math.exp(-(t - T_SLING - 0.3) * 3.0)     # riem loopt na
        loc = M @ (BACK + V(0, 0.02 * sw, 0))
        rot = (math.radians(6 + 10 * sw), 0.0, yaw)
    bag.location, bag.rotation_euler = loc, rot
    bag.keyframe_insert("location", frame=f)
    bag.keyframe_insert("rotation_euler", frame=f)
# de zwaai: rechterhand omhoog langs de schouder
for t, off in ((T_SLING, V(-0.32, 0.0, 1.2)), (T_SLING + 0.25, V(-0.28, 0.12, 1.32)), (T_SLING + 0.5, V(-0.24, -0.02, 1.15))):
    S.reach(held, t, "R", S._root_matrix(held, t) @ off)
S.reach(held, T_SLING + 0.75, "R", inf=0.0)
for sd in ("L", "R"):                                         # IK blijft uit tot hij op de fiets zit (geen trage overgang naar het stuur)
    S.reach(held, t_3 - 1.0 / FPS, sd, inf=0.0)
S.face(held, t_2, "vastberaden", 0.7, look=(0.3, 0.1))

# ---------------------------------------------------------------- zijn fiets staat geparkeerd op de stoep (tot de cut naar 11e-3)
park = ST3.fiets2("Fiets_jongen_geparkeerd", (1.2, 8.15, 0.12), rot=180, color=(0.15, 0.35, 0.75), jerrycan=False)
visible(park, 0.0, True)
visible(park, t_3, False)

# ---------------------------------------------------------------- de beste vriend op zijn rode fiets op het fietspad
vr = S.actor("beste_vriend", (-0.6, 5.2, 0), 90)
_, crank_v = bike(S, vr, color=(0.85, 0.12, 0.10), name="Fiets_vriend")
T_GO_V = t_3 + 2.1
ride_path(S, vr, crank_v, 0.0, T_GO_V, [V(-0.6, 5.2, 0), V(-0.58, 5.2, 0)], cadence=0.02, lean=4)
ride_path(S, vr, crank_v, T_GO_V, END, [V(-0.58, 5.2, 0), V(3.5, 3.3, 0), V(47.0, 3.3, 0)], cadence=1.6, lean=14, sway=2)
# ongeduldig wiebelen, linkervoet aan de grond
frames = list(range(F(0.0), F(T_GO_V)))
bake(vr.rig, "rotation_euler", frames, [(math.radians(4.0 * math.sin(2 * math.pi * 1.4 * (f - 1) / FPS)), 0.0, math.radians(90))
                                         for f in frames], interp="BEZIER")
for f in range(F(0.0), F(T_GO_V) - 2, 2):
    A.foot(vr, f, "L", (0.3, 0.05, -0.02))
S.face(vr, 0.0, "grijns", 0.4, look=(-0.6, 0.2))                    # (op de fiets: alleen gezicht en ogen, geen beat)
S.face(vr, t_2, "twijfel", 0.7, look=(-0.5, 0.15))
S.face(vr, t_2 + 1.4, "grijns", 0.5, look=(-0.4, 0.1))
S.face(vr, t_3, "grijns", 0.6, look=(-0.6, 0.0))
S.say("N11-03", who=vr, at=0.6)

# ---------------------------------------------------------------- 11e-3: hij zit op zijn fiets (eigen fiets aan zijn wortel)
hb, crank_h = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen")
visible(hb, 0.0, False)
visible(hb, t_3, True)
T_GO_H = t_3 + 2.2
ride_path(S, held, crank_h, t_3, T_GO_H, [V(-2.8, 5.2, 0), V(-2.78, 5.2, 0)], cadence=0.02, lean=4)
ride_path(S, held, crank_h, T_GO_H, END, [V(-2.78, 5.2, 0), V(2.0, 2.2, 0), V(45.0, 2.2, 0)], cadence=1.8, lean=16, sway=2)
S.face(held, t_3, "vastberaden", 0.8, look=(0.3, 0.0))
S.face(held, t_3 + 1.2, "vastberaden", 0.9, look=(0.0, 0.1))
S.say("N11-04", who=held, at=t_3 + 0.25)
for f in range(F(t_3), F(T_GO_H) - 2, 2):
    A.foot(held, f, "R", (-0.3, 0.05, -0.02))

# ---------------------------------------------------------------- camera's
# 11e-1 MEDIUM push-in vanaf de stoep: het tuinpad, de jongen komt eraan
S.cam(0.0, ((-2.45, 6.35, 1.5), (-1.3, 10.8, 1.0), 30), ((-2.3, 6.9, 1.45), (-1.3, 10.6, 1.0), 33))
# 11e-2 MEDIUM de vriend van schuin voor, de heg en het huis erachter
S.cam(t_2, ((1.5, 3.2, 1.2), (-0.8, 5.7, 1.0), 32), ((1.35, 3.35, 1.2), (-0.8, 5.7, 1.0), 34), handheld=0.2)
# 11e-3 CLOSE de jongen op zijn fiets
HH = S.headpos(held, t_3 + 1.0)
S.cam(t_3, (HH + V(1.2, 0.75, 0.0), HH + V(0, 0, -0.14), 32), (HH + V(1.1, 0.68, 0.0), HH + V(0, 0, -0.14), 34))
# 11f-1 WIDE track achter de fietsen aan
S.cam(t_f1, None, fn=S.follow(held, (-5.5, 1.6, 1.9), lens=26, look_offset=(9.0, 0.6, -0.4)), shake=S.shake(0.2))
# 11f-2 WIDE drone pull-back: de lege straat, twee kleine fietsers
S.cam(t_f2, ((16.0, -5.0, 13.0), (26.0, 3.0, 0.5), 26), ((2.0, -24.0, 30.0), (38.0, 4.0, 0.0), 26))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 5", 0, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.04)
S.sfx("sfx_fiets_snel", T_GO_H, 0.18)
S.say("N11-05", at=t_f1 + 0.25)
S.finish(length=END, tail=0.0)
