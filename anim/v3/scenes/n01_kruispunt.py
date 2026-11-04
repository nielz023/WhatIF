"""N01 · Cold open: de lege kruising om middernacht (script scène 1, 0:09-0:24).
De jongen sprint in pyjamabroek en hoodie over het lege kruispunt, achter hem klappen drie reclameborden om
naar rood: THERE ARE NO MORE RULES. Nucleair alarm. Hij remt af, kijkt omhoog en dan recht in de lens.

    blender -b -P anim/v3/scenes/n01_kruispunt.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n01", "stad", "nacht", exposure=0.3, night=True)

# shots: 1a 3.0 · 1b 2.5 · 1c 1.5 · 1e 3.5 · 1f 4.0 · 1g 3.0
sh = S.cuts([3.0, 2.5, 1.5, 3.5, 4.0, 3.0])
END = sh[-1][1]

# ---------------------------------------------------------------- set: borden eerst reclame, dan alarm
FLIP = {"Billboard_1": 0.55, "Billboard_2": 1.35, "Billboard_groot": 2.1}
for o in [o for o in bpy.data.objects if o.name.startswith("Billboard_") and o.name.count("_") == 1]:
    nm = o.name
    rec, alm = S.obj(nm + "_reclame"), S.obj(nm + "_alarm")
    lt = S.obj(nm + "_rood_schijnsel")
    t = FLIP.get(nm, -1.0)
    if rec is None or alm is None:
        continue
    if t > 0:
        swap(rec, alm, t)
        if lt:
            light_key(lt, 0, 0.0)
            light_key(lt, t, 3200.0)
            light_key(lt, t + 0.12, 2500.0)
        S.sfx("sfx_dreun", t, 0.55)
# verlaten auto's: tweede auto met knipperende alarmlichten mag blijven; de verlaten auto midden op de weg weg
for nm in ("Auto_verlaten",):
    for o in [o for o in bpy.data.objects if o.name.startswith(nm) and not o.name.startswith("Auto_verlaten2")]:
        o.hide_render = True
        o.hide_viewport = True

# verkeerslichten: alles tegelijk aan, vanaf 1c knippert alleen oranje
VKL = ["VKL_zuid", "VKL_noord", "VKL_oost", "VKL_west"]
for v in VKL:
    for col in ("rood", "oranje", "groen"):
        emission_key(f"{v}_{col}", 0.0, 9.0)
c0 = sh[2][0] + 0.5
for v in VKL:
    emission_key(f"{v}_rood", c0, 0.0)
    emission_key(f"{v}_groen", c0, 0.0)
    k = 0
    t = c0
    while t < END:
        emission_key(f"{v}_oranje", t, 9.0 if k % 2 == 0 else 0.4)
        t += 0.5
        k += 1

# mist en blauw maanlicht staan in de set; extra laag vullicht zodat het nooit bijna zwart is
T.point_light("N01_vul_laag", (0, -14, 6), color=(0.35, 0.45, 1.0), energy=2500, radius=4, shadow=False)

# ---------------------------------------------------------------- de jongen
bpy.context.view_layer.update()
held = S.actor("hoofdpersonage_pyjama", (0.3, 3.0, 0), 0)
S.beat(held, 0.0, "sprint", face="geschrokken", face_amt=0.7)
# 1a + 1b: volle sprint naar de camera (zuid, -y)
S.run(held, 0.0, sh[1][1] + 0.3, [V(0.3, 3.0, 0), V(0.1, -8.5, 0), V(0.0, -17.0, 0)], stride=1.1, lift=0.24, lean=16,
      ease_in=0.0, ease_out=0.0)
# bij het tweede bord kijkt hij over zijn schouder zonder af te remmen
S.face(held, 1.2, "geschrokken", 0.9, look=(0.8, 0.3))
S.face(held, 1.9, "geschrokken", 0.8, look=(0.0, 0.0))
A.bone_rot(held, F(1.0), "head", (0, 0, 0))
A.bone_rot(held, F(1.3), "head", (-8, 40, 0))
A.bone_rot(held, F(1.85), "head", (-6, 0, 0))
# 1b: hijgt met open mond, knippert hard als een bord opflitst
S.face(held, sh[1][0], "geschrokken", 1.0, look=(0.0, 0.1))
A.key_prop(held.rig, "mond_open", 0.6, F(sh[1][0]))
A.blink_at(held, F(sh[1][0] + 1.3), closed=4)
for tt in (sh[1][0] - 0.1, sh[1][1]):
    A.bone_rot(held, F(tt), "head", (-16, 0, 0))
# 1e: komt midden op het kruispunt aanrennen, remt af met twee korte stappen, draait om en kijkt omhoog
t_e = sh[3][0]
STOP = V(0.0, -1.6, 0)
S.teleport(held, t_e, V(0.0, 1.6, 0), 0)
S.walk(held, t_e, t_e + 0.75, [V(0.0, 1.6, 0), STOP], stride=0.55, arms=0.5)
S.beat(held, t_e, "rennen", amount=0.5, face="geschrokken", face_amt=0.8, crouch=(0.05, 8), feet="keep")
S.beat(held, t_e + 0.8, "staan", face="nerveus", face_amt=0.9, crouch=(0.06, -6),
       arms=arms(arm("L", (0.45, 0.15, -0.8), (0.75, 0.1, -0.55)), arm("R", (0.45, 0.15, -0.8), (0.75, 0.1, -0.55))))
S.beat(held, t_e + 1.1, "staan", face="nerveus", face_amt=0.9)
# via de camerakant (-x) draaien, niet met zijn rug ernaartoe
S.turn(held, t_e + 1.1, t_e + 2.1, -179, via=-1)
S.beat(held, t_e + 2.2, "staan", face="verbaasd", face_amt=0.8, at=V(0, 81.6, 30))
S.beat(held, sh[4][1], "staan", face="nerveus", face_amt=1.0, at=V(0, 81.6, 34))
# ademt hijgend (borst op en neer)
for k in range(int((END - t_e) / 0.45)):
    t = t_e + k * 0.45
    A.bone_rot(held, F(t), "chest", (-4 if k % 2 else 3, 0, 0))
# 1g: kijkt recht in de lens, slikt, kaak spant aan
t_g = sh[5][0]
S.beat(held, t_g, "staan", face="nerveus", face_amt=0.8, look=(0.0, 0.0))
A.key_prop(held.rig, "mond_open", 0.15, F(t_g + 0.6))
A.key_prop(held.rig, "mond_open", 0.0, F(t_g + 1.0))
S.beat(held, t_g + 1.4, "staan", face="vastberaden", face_amt=0.8, look=(0.0, 0.0))
A.blink_at(held, F(t_g + 2.0))
S.hold(held, END)

# ---------------------------------------------------------------- camera's
# 1a WIDE push-in: hij sprint recht op de camera af, de borden klappen achter hem om
S.cam(sh[0][0], ((0.0, -13.5, 1.0), (0.0, 6.0, 4.5), 17), ((0.0, -12.6, 1.0), (0.0, 4.0, 3.6), 18), handheld=0.4)
# 1b CLOSE handheld: meebewegend voor zijn gezicht uit
S.cam(sh[1][0], None, fn=S.follow(held, (0.35, -2.1, 1.3), look_up=0.25, lens=35), shake=S.shake(0.5))
# 1c DETAIL verkeerslicht (alles tegelijk aan, daarna alleen oranje)
LAMP = S.obj("VKL_noord_lamp_oranje1").matrix_world.translation.copy()
S.cam(sh[2][0], (LAMP + V(-0.6, -2.6, -0.9), LAMP, 45), (LAMP + V(-0.5, -2.3, -0.8), LAMP, 48), handheld=0.15)
# 1e MEDIUM: camera draait mee om hem heen terwijl hij afremt en zich omdraait
H0 = STOP + V(0, 0, 1.5)
S.cam(t_e, ((-3.6, -3.4, 1.05), H0 + V(0, 0.4, 0), 30), ((-3.1, -1.2, 0.85), H0 + V(0, 0, 0.15), 34))
# 1f LOW WIDE trage pull-back: klein in het midden, achter hem de rode schermen (borden 3 en 4)
S.cam(sh[4][0], ((0.5, 4.5, 0.3), (0.0, -8.0, 6.5), 16), ((0.8, 8.0, 0.25), (0.0, -8.0, 7.5), 14), handheld=0.15)
# 1g CLOSE: recht in de lens
HH = S.headpos(held, t_g + 1.0)
S.cam(t_g, (HH + V(0.25, 1.7, -0.05), HH + V(0, 0, 0.0), 45), (HH + V(0.22, 1.5, -0.05), HH, 48))

# rood flakkeren op zijn gezicht in 1g
fl = T.point_light("N01_rood_flakker", tuple(HH + V(0.8, -1.2, 1.0)), color=(1.0, 0.08, 0.05), energy=0, radius=0.5, shadow=False)
for k in range(int(3.0 / 0.1)):
    light_key(fl, t_g + k * 0.1, 0 if k == 0 else (60 if k % 3 else 20), interp="LINEAR")

# ---------------------------------------------------------------- geluid en tekst
S.sfx("sfx_alarm_nucleair", 0.0, 1.0, keys=[(0.0, 1.0), (2.0, 0.35)], loop_to=t_g + 1.8)
S.sfx("sfx_alarm_piep", t_g + 1.85, 0.6)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.18)
S.music("drone", 0.0, END, vol=0.22, fade_in=0.3, fade_out=0.2)
S.sfx("sfx_hartslag", sh[3][0], 0.45, cut=(0.0, 6.0))
S.say("N01-01", at=0.05)
S.say("N01-02", at=sh[2][0] + 0.05)
S.say("N01-03", at=sh[3][0] + 0.6)
S.say("N01-04", at=sh[4][0] + 0.7)
S.say("N01-05", at=t_g + 0.5)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
