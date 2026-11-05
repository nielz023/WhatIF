"""N06a · Het raam (script scène 6a-6b).
6a OTS: de jongen kijkt door zijn raam naar het kruispunt in de verte, waar de verkeerslichten oranje knipperen.
   Hij legt een hand plat op het glas, zijn adem condenseert op het raam.
6b CLOSE: zijn gezicht in het oranje knipperlicht. VO: "And tonight, eight billion people stopped believing."

    blender -b -P anim/v3/scenes/n06a_raam.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n06a", "slaapkamer", "nr_nacht", exposure=0.3, night=True)
sh = S.cuts([4.0, 4.0])
END = sh[-1][1]
t_b = sh[1][0]
ORANJE = (1.0, 0.55, 0.08)
BLINK = 0.5                      # knippert 1x per seconde (0,5 s aan, 0,5 s uit)

# wekker staat nu op 00:0x, de telefoon ligt niet meer naast de wekker (hij heeft hem in zijn hand)
for s_, vis in (("57", False), ("58", False), ("59", False), ("00", True)):
    o = S.obj(f"Wekker_sec_{s_}")
    if o:
        o.hide_render = o.hide_viewport = not vis
tijd = S.obj("Wekker_tijd")
if tijd:
    tijd.data.body = "00:04"
for nm in ("Telefoon", "Telefoon_scherm"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- buiten: de straat naar het kruispunt in de verte
for o in list(bpy.data.objects):
    if o.name.startswith(("Buurhuis", "Boom_tuin2")):
        o.hide_render = o.hide_viewport = True
T.use_collection(T.collection("N06a_buiten"))
Z = -3.0
asfalt = S.mat("asfalt_nacht", (0.10, 0.10, 0.12))
stoep = S.mat("stoep_nacht", (0.30, 0.30, 0.32))
T.box("Weg_lang", (1.0, 40.0, Z + 0.01), (6.0, 64.0, 0.02), asfalt, bevel=0, ol=0)
T.box("Weg_dwars", (1.0, 46.0, Z + 0.015), (70.0, 6.0, 0.02), asfalt, bevel=0, ol=0)
for x in (-2.6, 4.6):
    T.box(f"Stoep_{x}", (x, 40.0, Z), (1.6, 64.0, 0.12), stoep, bevel=0, ol=0)
rnd = random.Random(11)
gevels = [(0.32, 0.20, 0.17), (0.28, 0.24, 0.22), (0.35, 0.27, 0.20), (0.25, 0.22, 0.26)]
for side in (-1, 1):
    for k, y in enumerate(range(12, 70, 7)):
        if 40 <= y <= 52:
            continue
        x = 1.0 + side * 9.5
        h = rnd.uniform(5.5, 7.5)
        T.box(f"Huis_ver_{side}_{k}", (x, y, Z), (6.0, 6.4, h), S.mat(f"gevel_ver_{k % 4}", gevels[k % 4]), bevel=0.05, ol=0.02)
        for j in range(2):
            lit = rnd.random()
            col, st = ((1.0, 0.75, 0.4), 1.6) if lit < 0.45 else ((1.0, 0.1, 0.06), 2.2) if lit < 0.6 else ((0.05, 0.06, 0.1), 0.3)
            T.box(f"Huis_ver_raam_{side}_{k}_{j}", (x - side * 3.02, y - 1.5 + 3.0 * j, Z + 3.4), (0.04, 1.1, 1.0),
                  S.mat(f"raam_ver_{side}_{k}_{j}", col, st), bevel=0, ol=0)
# lantaarns langs de weg
for k, y in enumerate((14, 26, 38)):
    for x in (-2.2, 4.2):
        T.cyl(f"Lantaarn_{k}_{x}", (x, y, Z), 0.06, 4.2, P.m("zwart"), seg=8, ol=0.006)
        T.sphere(f"Lantaarn_lamp_{k}_{x}", (x, y, Z + 4.25), 0.16, S.mat("lantaarn_lamp", (1.0, 0.82, 0.55), 4.0), seg=12, ol=0)
    T.point_light(f"Lantaarnlicht_{k}", (1.0, y, Z + 3.8), color=(1.0, 0.75, 0.45), energy=500, radius=0.3, shadow=False)
# het kruispunt: verkeerslichten die oranje knipperen
lampen = []
for k, (x, y) in enumerate(((-2.3, 42.6), (4.3, 42.6), (-2.3, 49.4), (4.3, 49.4))):
    T.cyl(f"Verkeerslicht_paal_{k}", (x, y, Z), 0.07, 3.0, P.m("zwart"), seg=8, ol=0.006)
    T.box(f"Verkeerslicht_kast_{k}", (x, y - 0.12, Z + 2.5), (0.32, 0.22, 0.9), P.m("zwart"), bevel=0.03, ol=0.006)
    lampen.append(T.sphere(f"Verkeerslicht_oranje_{k}", (x, y - 0.24, Z + 2.95), 0.11, S.mat("oranje_knipper", ORANJE, 8.0), seg=12, ol=0))
gloed = T.point_light("Kruispunt_oranje", (1.0, 46.0, Z + 3.0), color=ORANJE, energy=2500, radius=1.0, shadow=False)
t = 0.0
on = True
while t <= END + 0.01:
    emission_key("oranje_knipper", t, 8.0 if on else 0.2)
    light_key(gloed, t, 2500 if on else 0)
    t += BLINK
    on = not on

# gordijnen verder open, zodat ze niet tussen hem en het glas hangen
for nm, dx in (("Raam_gordijn_l", -0.42), ("Raam_gordijn_r", 0.3)):
    o = S.obj(nm)
    if o:
        o.location.x += dx
# ---------------------------------------------------------------- de jongen bij het raam
HX, HY = 0.62, 1.42
held = S.actor("hoofdpersonage_pyjama", (HX, HY, 0), 172)
phone = prop_phone(S, "Telefoon_raam", screen=(1.0, 0.08, 0.05))
grab(S, phone, held, 0.0, "hand.L", loc=(0, 0.07, 0.02), rot=(90, 0, 180))
LOW = arms(arm("L", (0.25, 0.2, -0.95), (0.05, 0.6, -0.8)))
S.beat(held, 0.0, "staan", arms=LOW, face="nerveus", face_amt=0.5, look=(0.0, 0.0), feet="keep")
GLASS = V(HX + 0.3, 1.93, 1.2)
S.reach(held, 0.0, "R", inf=0.0)
S.reach(held, 1.15, "R", S.bone_world(held, "hand.R", 1.15, tail=False), inf=0.0)   # IK-doel start bij de hangende hand
S.reach(held, 1.5, "R", GLASS + V(0, -0.04, 0))
S.reach(held, 1.7, "R", GLASS)
S.reach(held, END, "R", GLASS)
S.beat(held, 1.6, "staan", arms=LOW, face="nerveus", face_amt=0.6, look=(0.0, -0.1), feet="keep", body={"spine": (4, 0, 0)})
S.beat(held, 2.8, "staan", arms=LOW, face="verdrietig", face_amt=0.4, look=(0.1, -0.1), feet="keep", body={"spine": (5, 0, 0)})
S.beat(held, t_b + 0.6, "staan", arms=LOW, face="verdrietig", face_amt=0.5, look=(0.0, -0.15), feet="keep", body={"spine": (5, 0, 0)})
S.beat(held, t_b + 2.6, "staan", arms=LOW, face="vastberaden", face_amt=0.3, look=(0.0, -0.1), feet="keep", body={"spine": (5, 0, 0)})
A.blink_at(held, F(t_b + 1.7), closed=5)
S.hold(held, END)
# oranje knipperlicht op zijn gezicht
gl = T.point_light("Gezicht_oranje", (HX + 0.1, 1.85, 1.5), color=ORANJE, energy=0, radius=0.3, shadow=False)
t, on = 0.0, True
while t <= END + 0.01:
    light_key(gl, t, 35 if on else 4)
    t += BLINK
    on = not on

# ---------------------------------------------------------------- camera's
HH = S.headpos(held, 2.0)
# adem condenseert op het glas (vlekje dat groeit en weer vervaagt, twee keer)
mist = T.sphere("Condens", (HH.x, 1.925, HH.z - 0.13), 0.12, S.mat("condens", (0.85, 0.9, 0.95), 0.25), scale=(1.0, 0.05, 0.75), seg=16, ol=0)
for t, sc in ((0.0, 0.01), (1.9, 0.01), (2.2, 1.0), (3.2, 0.5), (3.6, 0.2), (4.6, 1.0), (5.6, 0.5), (6.2, 0.15), (6.6, 1.0), (END, 0.6)):
    mist.scale = (sc, sc * 0.05, sc * 0.75)
    mist.keyframe_insert("scale", frame=F(t))
# 6a OTS: achter hem, zijn schouder aan de rand van het beeld, push-in naar het raam
S.cam(0.0, ((1.65, -1.05, 1.8), (1.12, 1.96, 1.42), 28), ((1.55, -0.75, 1.76), (1.12, 1.96, 1.42), 30))
# 6b CLOSE: naast het raam, driekwart op zijn gezicht
H2 = S.headpos(held, t_b + 1.5)
S.cam(t_b, (H2 + V(-0.05, 1.75, 0.0), H2 + V(0.02, 0, 0.0), 34), (H2 + V(-0.05, 1.62, 0.0), H2 + V(0.02, 0, 0.0), 36))

# ---------------------------------------------------------------- geluid
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.12)
S.sfx("sfx_alarm_nucleair", 0.0, 0.06, loop_to=END)
S.say("N06-01", at=t_b + 0.2)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
