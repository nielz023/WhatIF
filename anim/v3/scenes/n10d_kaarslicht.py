"""N10d · Dag 4: de nacht zonder stroom (script scène 10d-10k), keuken met planken voor het raam, maanlicht.
10d MEDIUM push: het gezin in het donker aan tafel, de telefoons gaan één voor één aan, gezichten van onder verlicht.
10e DETAIL: de telefoon van de jongen: 3% · NO SERVICE.
10f MEDIUM: mama strijkt een lucifer af (anticipatie, korte haal), beschermt de vlam en steekt de kaars aan.
10g CLOSE trage push: kaarslicht op het gezicht van de jongen, een autoalarm in de verte, zijn ogen schieten naar het raam.
10h CLOSE: het broertje kruipt tegen opa aan. BROERTJE: "Opa? Who's out there?"  OPA: "Just people. Scared people."
10i WIDE door het geplankte raam: buiten in het blauwe maanlicht lopen schaduwen voorbij. Voetstappen, een tuinhek, honden.
10j CLOSE: papa staat bij de deur, hand op de klink, oor tegen de deur, houdt zijn adem in, ademt uit als de stappen weggaan.
10k WIDE: de kaars flakkert bijna uit. VO: "That night, nobody in the whole city slept." / "And the next morning... the water stopped."

    blender -b -P anim/v3/scenes/n10d_kaarslicht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402
from mathutils import Matrix  # noqa: E402

S = Scene3("n10d", "keuken", "nr_kaarsen", exposure=0.0, night=True)
sh = S.cuts([3.6, 2.4, 3.6, 3.8, 5.8, 4.0, 3.6, 6.6])
END = sh[-1][1]
t_e, t_f, t_g, t_h, t_i, t_j, t_k = [s[0] for s in sh[1:]]
rnd = random.Random(10)

# ---------------------------------------------------------------- kaarsen: eerst uit, mama steekt die aan haar kant aan
CANDLE = S.obj("Kaars_tafel_2")
CANDLE.location.y = -0.8                                  # iets naar mama toe geschoven: haar korte armen halen hem zo
for k in range(3):
    fl, lt = S.obj(f"Kaars_tafel_{k}_vlam"), S.obj(f"Kaars_tafel_{k}_licht")
    if k != 2:
        fl.hide_render = fl.hide_viewport = True
        lt.data.energy = 0.0
T_LIT = t_f + 2.2
fl1, lt1 = S.obj("Kaars_tafel_2_vlam"), S.obj("Kaars_tafel_2_licht")
visible(fl1, 0.0, False)
visible(fl1, T_LIT, True)
light_key(lt1, 0.0, 0.0)
# flakkeren; in 10k bijna uit
fl1.scale = (1, 1, 1)
fl1.keyframe_insert("scale", frame=F(T_LIT))
t = T_LIT
while t < END:
    dip = t > t_k + 2.4
    e = rnd.uniform(14, 22) * (0.25 if dip and rnd.random() < 0.5 else 1.0)
    light_key(lt1, t, e, interp="LINEAR")
    s = e / 18
    fl1.scale = (1, 1, max(0.25, s))
    fl1.keyframe_insert("scale", frame=F(t))
    t += rnd.uniform(0.08, 0.2)
light_key(lt1, T_LIT - 1 / 24, 0.0)

# ---------------------------------------------------------------- het gezin aan tafel
OPA_CHAIR = S.obj("Stoel_1").copy()
OPA_CHAIR.data = S.obj("Stoel_1").data
bpy.context.scene.collection.objects.link(OPA_CHAIR)
OPA_CHAIR.name = "Stoel_opa"
bpy.context.view_layer.update()
c1 = S.obj("Stoel_1")
OPA_CHAIR.matrix_world = Matrix.Translation(V(-1.0, -0.6, 0) - V(c1.matrix_world.translation.x, c1.matrix_world.translation.y, 0)) @ c1.matrix_world
OPA_CHAIR.rotation_euler.z += math.radians(-90)

SEATS = {"hoofdpersonage_kind": (V(-0.18, -1.3, 0), 180), "mama": (V(0.58, -1.3, 0), 180), "papa": (V(0.58, 0.12, 0), 0),
         "broertje": (V(-0.18, 0.12, 0), 0), "opa": (V(-1.08, -0.6, 0), 90)}
fam = {}
for nm, (p, rot) in SEATS.items():
    ch = S.actor(nm, p, rot)
    spec, rz = sit(ch, seat_top=0.47, lean=-4)
    ch.rig.location.z = rz
    ch.rig.keyframe_insert("location", frame=F(0.0))
    fam[nm] = (ch, spec, p, rot)
held, sp_h = fam["hoofdpersonage_kind"][0], fam["hoofdpersonage_kind"][1]
mama, sp_m = fam["mama"][0], fam["mama"][1]
papa, sp_p = fam["papa"][0], fam["papa"][1]
bro, sp_b = fam["broertje"][0], fam["broertje"][1]
opa, sp_o = fam["opa"][0], fam["opa"][1]

# telefoons plat op tafel voor iedereen behalve opa; het scherm gaat aan en verlicht het gezicht van onder
PH = {}
T_ON = {"papa": 0.6, "mama": 1.2, "broertje": 1.7, "hoofdpersonage_kind": 2.3}
for nm, t_on in T_ON.items():
    ch, sp, p, rot = fam[nm]
    fwd = V(math.sin(math.radians(rot)), -math.cos(math.radians(rot)), 0)
    loc = V(p.x, p.y, 0.765) + fwd * 0.42
    ph = prop_phone(S, f"Telefoon_{nm}", tuple(loc), screen=(0.55, 0.75, 1.0))
    ph.rotation_euler = (math.radians(-90), 0, math.radians(rot + 180))
    scr = S.obj(f"Telefoon_{nm}_scherm")
    visible(scr, 0.0, False)
    visible(scr, t_on, True)
    pl = T.point_light(f"Telefoonlicht_{nm}", tuple(loc + V(0, 0, 0.12)), color=(0.6, 0.75, 1.0), energy=0, radius=0.05, shadow=False)
    light_key(pl, 0.0, 0.0)
    light_key(pl, t_on, 6.0)
    light_key(pl, T_LIT + 0.6, 6.0)
    light_key(pl, T_LIT + 1.4, 0.0, interp="LINEAR")         # de telefoons gaan weer uit (batterij sparen)
    visible(scr, T_LIT + 1.4, False)
    PH[nm] = loc
for nm, (ch, sp, p, rot) in fam.items():
    S.beat(ch, 0.0, "staan", face="nerveus", face_amt=0.5, at=PH.get(nm, V(0, -0.6, 0.8)) + V(0, 0, 0.02), **sp)
    if nm in T_ON:
        S.beat(ch, T_ON[nm], "staan", face="nerveus", face_amt=0.7, at=PH[nm], body={"head": (8, 0, 0)}, **sp)

# 10e: het scherm van de jongen
ph_h = S.obj("Telefoon_hoofdpersonage_kind")
for k, (txt, z, sz) in enumerate((("3%", 0.035, 0.022), ("NO SERVICE", -0.005, 0.011))):
    lab = ST3.label(f"Scherm_held_{k}", txt, (0, -0.0055, z), sz, col=(1.0, 0.25, 0.2) if k == 0 else (0.15, 0.18, 0.25), rot=(90, 0, 0), glow=2.0 if k == 0 else 0.0)
    lab.parent = ph_h
    visible(lab, 0.0, False)
    visible(lab, T_ON["hoofdpersonage_kind"], True)
    visible(lab, T_LIT + 1.4, False)

# 10f: mama strijkt een lucifer af en steekt de kaars aan
luc = T.box("Lucifer", (0, 0, 0), (0.004, 0.004, 0.05), S.mat("lucifer_hout", (0.85, 0.7, 0.45)), base=False, bevel=0, ol=0)
kop = T.sphere("Lucifer_vlam", (0, 0, 0.032), 0.009, S.mat("vlam_lucifer", (1.0, 0.65, 0.2), 8.0), scale=(1, 1, 1.8), seg=10, ol=0)
kop.parent = luc
visible(luc, 0.0, False)
visible(luc, t_f + 0.2, True)
visible(kop, 0.0, False)
visible(kop, t_f + 0.95, True)
visible(luc, T_LIT + 0.5, False)
llt = T.point_light("Lucifer_licht", (0, 0, 0.04), color=(1.0, 0.6, 0.2), energy=0, radius=0.02, shadow=False)
llt.parent = luc
light_key(llt, 0.0, 0.0)
light_key(llt, t_f + 0.95, 10.0)
light_key(llt, T_LIT + 0.5, 0.0)
grab(S, luc, mama, 0.0, "hand.R", loc=(0, 0.05, 0.0), rot=(90, 0, 0))
bpy.context.view_layer.update()
CPOS = CANDLE.matrix_world.translation + V(0, 0, 0.32)
S.reach(mama, 0.0, "R", inf=0.0)
S.reach(mama, t_f + 0.05, "R", inf=0.0)
S.reach(mama, t_f + 0.3, "R", V(0.55, -1.0, 0.85))                       # doosje, anticipatie (dicht bij haar: korte armen)
S.reach(mama, t_f + 0.75, "R", V(0.55, -1.0, 0.85))
S.reach(mama, t_f + 0.95, "R", V(0.47, -0.95, 0.90))                     # korte haal
S.reach(mama, t_f + 1.6, "R", CPOS + V(0.05, -0.12, 0.0))
S.reach(mama, T_LIT, "R", CPOS + V(0.02, -0.06, -0.01))
S.reach(mama, T_LIT + 0.6, "R", V(0.5, -1.0, 0.82))
S.reach(mama, T_LIT + 0.9, "R", inf=0.0)
S.reach(mama, 0.0, "L", inf=0.0)
S.reach(mama, t_f + 1.2, "L", inf=0.0)
S.reach(mama, t_f + 1.6, "L", CPOS + V(-0.06, -0.1, 0.02))               # hand beschermt de vlam
S.reach(mama, T_LIT + 0.5, "L", CPOS + V(-0.06, -0.1, 0.02))
S.reach(mama, T_LIT + 0.9, "L", inf=0.0)
S.beat(mama, t_f + 0.3, "staan", face="vastberaden", face_amt=0.6, at=V(0.4, -0.9, 0.8), **sp_m)
S.beat(mama, t_f + 1.5, "staan", face="vastberaden", face_amt=0.6, at=CPOS, body={"spine": (10, 0, 0)}, **sp_m)
S.beat(mama, T_LIT + 0.7, "staan", face="nerveus", face_amt=0.4, at=CPOS, **sp_m)
for nm in ("papa", "broertje", "hoofdpersonage_kind", "opa"):
    ch, sp = fam[nm][0], fam[nm][1]
    S.beat(ch, T_LIT + 0.2, "staan", face="nerveus", face_amt=0.5, at=CPOS, **sp)

# 10g: de jongen, ogen schieten naar het raam (autoalarm in de verte)
WIN = V(-0.2, 2.1, 1.5)
S.beat(held, t_g + 1.4, "staan", face="nerveus", face_amt=0.7, at=CPOS, **sp_h)
S.beat(held, t_g + 1.7, "staan", face="geschrokken", face_amt=0.6, at=WIN, look=(0.0, 0.2), **sp_h)
S.beat(held, t_g + 3.4, "staan", face="nerveus", face_amt=0.8, at=WIN, **sp_h)

# 10h: het broertje kruipt tegen opa aan
BRO_H = V(-0.92, -0.12, 0)
S.teleport(bro, t_h, BRO_H, 120)
bro.rig.location = (BRO_H.x, BRO_H.y, 0.0)
bro.rig.keyframe_insert("location", frame=F(t_h))
S.beat(bro, t_h, "staan", face="bang", face_amt=0.7, at=S.head(opa, t_h), body={"spine": (6, 0, -8)}, feet="keep")
S.beat(bro, t_h + 0.4, "armen_over", amount=0.6, face="bang", face_amt=0.8, at=S.head(opa, t_h), body={"spine": (8, 0, -12), "head": (0, 0, -10)}, feet="keep")
S.beat(bro, t_h + 2.6, "armen_over", amount=0.6, face="nerveus", face_amt=0.7, at=S.head(opa, t_h), body={"spine": (8, 0, -12), "head": (0, 0, -14)}, feet="keep")
S.beat(opa, t_h, "staan", face="neutraal", face_amt=0.5, at=CPOS, **sp_o)
S.beat(opa, t_h + 2.4, "staan", face="neutraal", face_amt=0.6, at=S.head(bro, t_h + 2.4), **sp_o)
S.reach(opa, 0.0, "L", inf=0.0)
S.reach(opa, t_h + 2.5, "L", inf=0.0)
S.reach(opa, t_h + 3.2, "L", BRO_H + V(0.05, 0.15, 0.95))                 # arm om het broertje
S.reach(opa, END, "L", BRO_H + V(0.05, 0.15, 0.95))

# 10i: kieren tussen de planken voor het raam (planken iets smaller), schaduwen lopen door de tuin
for k in range(4):
    pl = S.obj(f"Raamplank_{k}")
    pl.scale.z *= 0.72
# schaduwen buiten achter de schutting (y = 9), alleen hoofden en schouders erboven
shadows = []
for k, (nm, x0, x1, t0, t1) in enumerate((("figurant_a", -6.0, 5.0, t_i - 0.2, t_i + 3.8), ("figurant_d", -7.5, 3.0, t_i + 0.6, t_i + 4.2))):
    e = S.actor(nm, (x0, 7.4 + 0.6 * k, 0), 90, label=f"schaduw_{k}")
    S.walk(e, t0, t1, [V(x0, 7.4 + 0.6 * k, 0), V(x1, 7.4 + 0.6 * k, 0)], stride=0.6)
    visible(e.body, 0.0, False)
    visible(e.body, t_i - 0.25, True)
    visible(e.body, t_j, False)
    S.hold(e, END)
    S.qc_skip.add(nm)
    shadows.append(e)

# 10j: papa bij de keukendeur, hand op de klink, oor tegen de deur
P_DOOR = V(-1.97, 1.22, 0)                                # kijkt naar -y, de deur (x=-2.4) aan zijn rechterkant
S.teleport(papa, t_j, P_DOOR, 0)
papa.rig.location = (P_DOOR.x, P_DOOR.y, 0.0)
papa.rig.keyframe_insert("location", frame=F(t_j))
S.beat(papa, t_j, "staan", face="nerveus", face_amt=0.7, at=V(-2.2, -1.0, 1.5), body={"spine": (0, 0, 4)}, feet="keep")
S.reach(papa, 0.0, "R", inf=0.0)
S.reach(papa, t_j - 0.05, "R", inf=0.0)
S.reach(papa, t_j, "R", V(-2.33, 1.3, 1.02))
S.reach(papa, END, "R", V(-2.33, 1.3, 1.02))
S.beat(papa, t_j + 1.0, "staan", face="bang", face_amt=0.6, at=V(-2.25, -1.0, 1.45), body={"spine": (0, 0, 4), "chest": (-3, 0, 0)}, feet="keep")
S.beat(papa, t_j + 2.6, "staan", face="nerveus", face_amt=0.5, at=V(-2.1, -1.0, 1.4), body={"chest": (3, 0, 0)}, feet="keep")
for ch in (held, mama, opa, bro):
    S.hold(ch, END)
S.hold(papa, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, ((2.25, -0.55, 2.0), (-0.6, -0.6, 0.85), 22), ((2.15, -0.58, 1.95), (-0.6, -0.6, 0.85), 24))
PHH = PH["hoofdpersonage_kind"]
S.cam(t_e, (PHH + V(0.0, -0.07, 0.22), PHH + V(0, 0.01, 0), 34), (PHH + V(0.0, -0.06, 0.19), PHH + V(0, 0.01, 0), 36))
S.cam(t_f, ((1.85, -0.2, 1.35), (0.45, -0.9, 1.0), 32), ((1.78, -0.25, 1.33), (0.45, -0.9, 1.0), 34))
HH = S.headpos(held, t_g + 1.0)
S.wall(t_g, t_h, "front")                                  # tegenshot naar -y: voormuur dicht
S.cam(t_g, (HH + V(0.35, 1.05, 0.05), HH + V(0, 0, -0.08), 26), (HH + V(0.3, 0.95, 0.05), HH + V(0, 0, -0.08), 28))
HO = S.headpos(opa, t_h + 1.5)
S.cam(t_h, (HO + V(1.45, 0.3, 0.05), HO + V(0.1, 0.2, -0.15), 32), (HO + V(1.35, 0.28, 0.05), HO + V(0.1, 0.2, -0.15), 34))
S.cam(t_i, ((-0.2, 1.72, 1.335), (-0.2, 9.0, 1.5), 28), ((-0.2, 1.78, 1.335), (-0.2, 9.0, 1.5), 30))
HP = S.headpos(papa, t_j + 1.0)
S.cam(t_j, (HP + V(0.4, -1.3, -0.05), HP + V(-0.12, 0.0, -0.04), 28), (HP + V(0.36, -1.18, -0.05), HP + V(-0.12, 0.0, -0.04), 30))
S.cam(t_k, ((2.25, -0.75, 2.15), (-0.5, -0.55, 0.8), 20), ((2.2, -0.72, 2.1), (-0.5, -0.55, 0.8), 21))
S.allow_long.add(8)

# ---------------------------------------------------------------- HUD, geluid en stemmen
S.counter("DAY 4", 0, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.03)
S.sfx("sfx_lucifer", t_f + 0.9, 0.5)
S.sfx("sfx_autoalarm", t_g + 1.2, 0.05, loop_to=t_h)
S.sfx("sfx_voetstappen_buiten", t_i - 0.2, 0.35)
S.sfx("sfx_tuinhek_rammel", t_i + 2.2, 0.3)
S.sfx("sfx_honden_blaffen", t_i + 2.8, 0.15)
S.sfx("sfx_voetstappen_buiten", t_j + 0.2, 0.25)
S.say("N10-03", who=bro, at=t_h + 0.3)
S.say("N10-04", who=opa, at=t_h + 2.6)
S.say("N10-05", at=t_k + 0.3)
S.say("N10-06", at=t_k + 3.7)
S.finish(length=END, tail=0.0)
