"""N04a · Het zondagsdiner (script scène 4a-4d).
Het hele gezin aan tafel, HOUSE RULES op de koelkast. Papa schept aardappels op, opa snijdt vlees, het broertje zit
onder tafel op zijn telefoon. Papa: "Phones away. House rule." Op tv de nieuwslezeres over een storing in de
alarmsystemen; opa stopt met kauwen. De zin wordt afgekapt door een storing.

    blender -b -P anim/v3/scenes/n04a_diner.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n04a", "keuken", "nr_diner", exposure=0.2)
# 4a 4.0 · 4b 3.0 · 4c tv 0.9 · 4c studio 3.0 · 4d 3.3
sh = S.cuts([4.0, 3.0, 0.9, 3.0, 3.55])
END = sh[-1][1]
t_b, t_tv, t_st, t_d = sh[1][0], sh[2][0], sh[3][0], sh[4][0]

TX, TY, TZ = 0.2, -0.6, 0.80
OPA_AT, OMA_AT, HERO_AT = V(TX - 0.8, TY + 0.62, 0), V(TX - 0.25, TY + 0.62, 0), V(TX + 0.3, TY + 0.62, 0)
MAMA_AT, PAPA_AT = V(TX - 1.72, TY, 0), V(TX + 1.48, TY, 0)     # papa dicht aan de kop: korte armen moeten bord en schaal halen
BRO_AT = V(TX + 0.85, TY + 0.62, 0)                # achter de tafel, naast papa
# stoelen vooraan weg (open voor de camera), behalve die van het broertje; kopse stoelen naar de tafel
for k, o in enumerate(sorted([o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")],
                             key=lambda o: o.name)):
    if o.location.y < TY - 0.3:
        o.hide_render = o.hide_viewport = True
achter = sorted([o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")
                 and o.location.y > TY], key=lambda o: o.location.x)
for o, x in zip(achter, (OPA_AT.x, OMA_AT.x, HERO_AT.x)):
    o.location.x = x
for o in [o for o in bpy.data.objects if o.name.startswith("Stoel_kop")]:
    o.rotation_euler.z = math.radians(90 if o.location.x < TX else -90)
    if o.location.x > TX:
        o.location.x += PAPA_AT.x - (TX + 1.72)          # papa's stoel schuift mee naar de tafel
stoel_b = T.box("Stoel_broertje", BRO_AT + V(0, 0.08, 0.0), (0.42, 0.42, 0.46), S.mat("stoel_hout", (0.55, 0.38, 0.22)), bevel=0.02,
                ol=0.004)
bpy.context.view_layer.update()

# ---------------------------------------------------------------- het gezin
opa = S.actor("opa", OPA_AT, 0, drop=("wandelstok",))       # stok niet door de tafel
oma = S.actor("oma", OMA_AT, 0)
held = S.actor("hoofdpersonage_kind", HERO_AT, 0)
mama = S.actor("mama", MAMA_AT, 90)
papa = S.actor("papa", PAPA_AT, -90)
bro = S.actor("broertje", BRO_AT, 0)
SEAT = {}
for ch, at, r in ((opa, OPA_AT, 0), (oma, OMA_AT, 0), (held, HERO_AT, 0), (mama, MAMA_AT, 90), (papa, PAPA_AT, -90),
                  (bro, BRO_AT, 0)):
    spec, z = sit(ch)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0, z), r)
PLATE = {opa: V(OPA_AT.x, TY + 0.25, TZ), oma: V(OMA_AT.x, TY + 0.25, TZ), held: V(HERO_AT.x, TY + 0.25, TZ),
         mama: V(TX - 0.9, TY, TZ), papa: V(TX + 0.9, TY, TZ)}          # = Bord_kop_1/2 van de set (tafel TL 2.2)

# schaal aardappels naast papa
SX, SY = TX + 0.98, TY + 0.29                       # schaal op tafel, rechts naast papa's bord (aan de kant van zijn schephand)
schaal = T.cyl("Schaal_aardappels", (SX, SY, TZ), 0.15, 0.08, S.mat("schaal_wit", (0.95, 0.94, 0.9)), seg=24, ol=0.003)
rnd = __import__("random").Random(3)
for k in range(9):
    T.sphere(f"Aardappel_{k}", (SX + rnd.uniform(-0.08, 0.08), SY + rnd.uniform(-0.08, 0.08), TZ + 0.1),
             0.035, S.mat("aardappel", (0.93, 0.78, 0.4)), scale=(1.2, 1, 0.9), seg=12, ol=0)
pile = T.sphere("Aardappel_op_bord", PLATE[papa] + V(0, 0, 0.04), 0.035, S.mat("aardappel", (0.93, 0.78, 0.4)), scale=(1.3, 1, 0.8),
                seg=12, ol=0)
pile.hide_render = True
pile.keyframe_insert("hide_render", frame=1)
pile.hide_render = False
pile.keyframe_insert("hide_render", frame=F(2.6))

# ---------------------------------------------------------------- 4a: papa schept op (lepel goed vast, bolle kant naar beneden)
lepel = cutlery(S, "opscheplepel", "Opscheplepel_papa")
grab(S, lepel, papa, 0.0, "hand.R", loc=(0, 0.06, 0.0), rot=(-70, 0, 0), release=None)   # losgelaten bij 4b (zie lepel_rest)
S.beat(papa, 0.0, **SEAT[papa], face="blij", face_amt=0.6, at=schaal.location + V(0, 0, 0.1))
# pols een lepellengte vóór schaal/bord (de lepel steekt voorbij de hand)
S.reach(papa, 0.3, "R", schaal.location + V(0.15, -0.05, 0.28))
S.reach(papa, 0.9, "R", schaal.location + V(0.12, 0.0, 0.16))
S.reach(papa, 1.4, "R", schaal.location + V(0.14, 0.0, 0.3))
S.reach(papa, 2.2, "R", PLATE[papa] + V(0.12, 0.0, 0.24))
S.reach(papa, 2.6, "R", PLATE[papa] + V(0.12, 0.02, 0.16))
S.reach(papa, 3.1, "R", PLATE[papa] + V(0.2, -0.06, 0.2))
S.beat(papa, 2.2, **SEAT[papa], face="blij", face_amt=0.6, at=PLATE[papa])

# opa snijdt vlees: vork links, mes rechts, ellebogen laag
vork = cutlery(S, "vork", "Vork_opa")
mes = cutlery(S, "mes", "Mes_opa")
grab(S, vork, opa, 0.0, "hand.L", loc=(0, 0.05, 0.0), rot=(-80, 0, 0))
grab(S, mes, opa, 0.0, "hand.R", loc=(0, 0.05, 0.0), rot=(-80, 0, 0))
vlees = T.box("Vlees_opa", PLATE[opa] + V(0, 0, 0.02), (0.1, 0.07, 0.025), S.mat("vlees", (0.55, 0.28, 0.16)), bevel=0.01, ol=0.002)
S.beat(opa, 0.0, **SEAT[opa], face="neutraal", face_amt=0.5, at=PLATE[opa], body={"head": (14, 0, 0)})
S.reach(opa, 0.0, "L", PLATE[opa] + V(0.06, -0.12, 0.17))
for k, t in enumerate(frange(0.0, t_tv, 0.3)):
    S.reach(opa, t, "R", PLATE[opa] + V(-0.05 + (0.05 if k % 2 else 0.0), -0.16 + (0.04 if k % 2 else 0.0), 0.15))
S.reach(opa, t_tv, "L", PLATE[opa] + V(0.06, -0.12, 0.17))
# oma, de jongen en mama eten en kijken rond
for ch in (oma, held, mama):
    S.beat(ch, 0.0, **SEAT[ch], face="blij", face_amt=0.5, at=PLATE[ch], body={"head": (12, 0, 0)})
S.beat(oma, 1.4, **SEAT[oma], face="lach", face_amt=0.6, at=S.head(opa))
S.beat(held, 1.0, **SEAT[held], face="grijns", face_amt=0.6, at=S.head(bro))
S.beat(mama, 1.6, **SEAT[mama], face="blij", face_amt=0.6, at=S.head(papa))

# broertje: telefoon onder de tafel, duim tikt (linkerhand: papa zit aan zijn linkerkant)
phone = prop_phone(S, "Telefoon_broertje")
g1 = grab(S, phone, bro, 0.0, "hand.L", loc=(0, 0.06, 0.0), rot=(0, 0, 0), release=t_b + 1.95)
UNDER = arms(arm("R", (0.12, 0.25, -0.96), (-0.15, 0.95, -0.2)), arm("L", (0.12, 0.25, -0.96), (-0.3, 0.9, -0.2)))   # in zijn schoot, onder de tafelrand
S.beat(bro, 0.0, **SEAT[bro], arms=UNDER, face="grijns", face_amt=0.5, look=(0.0, -0.7), body={"head": (24, 0, 0)})
for k, t in enumerate(frange(0.2, t_b + 0.6, 0.35)):
    A.bone_rot(bro, F(t), "thumb.01.L" if "thumb.01.L" in bro.pb else "hand.L", (8 if k % 2 else -8, 0, 0))

# ---------------------------------------------------------------- 4b: papa steekt zijn hand uit, palm omhoog
BRO_KIJK = S.head(bro) + V(-0.15, -0.35, 0)           # papa kijkt naar het broertje, iets naar de camera gedraaid
S.beat(papa, t_b, **SEAT[papa], face="zelfverzekerd", face_amt=0.6, at=BRO_KIJK)
lepel_rest = V(TX + 0.98, TY + 0.0, TZ + 0.01)
# hij legt de lepel op tafel vóór hij zijn hand uitsteekt (niet mee onder de tafel)
S.reach(papa, t_b - 0.45, "R", lepel_rest + V(0.06, -0.04, 0.07))
for c in lepel.constraints:
    if c.type == "COPY_TRANSFORMS":
        c.keyframe_insert("influence", frame=F(t_b - 0.3) - 1)
        c.influence = 0.0
        c.keyframe_insert("influence", frame=F(t_b - 0.3))
lepel.location = lepel_rest
lepel.rotation_euler = (0.0, 0.0, math.radians(90))
lepel.scale = (1, 1, 1)
# overgavepunt tussen papa en het broertje in (beiden korte armen): papa steekt zijn rechterhand uit
HAND_P = V(TX + 1.18, TY + 0.47, 0.92)                # net naast de schaal, boven de tafelkop
S.beat(papa, t_b + 0.2, **SEAT[papa], face="zelfverzekerd", face_amt=0.7, at=BRO_KIJK, body={"spine": (6, 0, 0)})
S.reach(papa, t_b + 0.45, "R", HAND_P + V(0.04, -0.04, -0.03))
S.reach(papa, t_b + 2.3, "R", HAND_P + V(0.05, -0.05, -0.02))
S.reach(papa, t_b + 2.7, "R", inf=0.0)
pl = S.say("N04-01", who=papa, at=t_b + 0.25)
# broertje rolt met zijn ogen (kijkt omhoog, zucht) en legt de telefoon in papa's hand
S.beat(bro, t_b + 0.3, **SEAT[bro], arms=UNDER, face="twijfel", face_amt=0.8, look=(0.0, 0.8), body={"head": (-6, 0, 0)})
S.beat(bro, t_b + 1.2, **SEAT[bro], face="boos", face_amt=0.5, at=S.head(papa))
S.reach(bro, 0.0, "L", inf=0.0)
S.reach(bro, t_b + 0.9, "L", inf=0.0)
S.reach(bro, t_b + 1.2, "L", HAND_P + V(-0.04, 0.05, 0.08))
S.reach(bro, t_b + 1.85, "L", HAND_P + V(-0.03, 0.03, 0.04))
S.reach(bro, t_b + 2.3, "L", inf=0.0)
grab(S, phone, papa, t_b + 1.95, "hand.R", loc=(0, 0.06, 0.02), rot=(90, 0, 0))
S.beat(bro, t_b + 2.4, **SEAT[bro], arms=arms(arm("L", (0.2, 0.4, -0.88), (0.0, 0.7, 0.7))), face="twijfel", face_amt=0.6,
           at=PLATE[held] + V(0.6, -0.4, 0))
S.beat(papa, t_b + 2.3, **SEAT[papa], face="blij", face_amt=0.6, at=BRO_KIJK,
       arms=arm("L", (0.2, 0.55, -0.75), (0.0, 0.9, 0.3)))
S.beat(held, t_b + 0.4, **SEAT[held], face="lach", face_amt=0.7, at=S.head(bro))

# ---------------------------------------------------------------- tv tegen de linkermuur
TV = V(-2.36, -1.7, 1.3)
tvkast = T.box("Tvkast", V(-2.2, -1.7, 0), (0.4, 1.2, 0.75), S.mat("kast_donker", (0.18, 0.15, 0.13)), bevel=0.02, ol=0.004)
tv = T.box("Tv", TV, (0.06, 1.05, 0.62), S.mat("tv_zwart", (0.05, 0.05, 0.06)), base=False, bevel=0.01, ol=0.004)
scr = T.box("Tv_scherm", TV + V(0.035, 0, 0), (0.005, 0.97, 0.55), S.mat("tv_beeld", (0.25, 0.45, 0.95), 2.2), base=False, bevel=0, ol=0)
txt = ST3.label("Tv_tekst", "BREAKING NEWS", TV + V(0.04, 0, -0.17), 0.075, col=(1, 1, 1), rot=(90, 0, 90), glow=3.0)
band = T.box("Tv_band", TV + V(0.038, 0, -0.17), (0.003, 0.97, 0.11), S.mat("tv_band", (0.85, 0.08, 0.06), 2.5), base=False, bevel=0,
             ol=0)

# 4c: iedereen draait zich naar de tv
for ch in (opa, oma, held, mama):
    S.beat(ch, t_tv - 0.3, **SEAT[ch], face="neutraal", face_amt=0.5, at=TV)
S.beat(papa, t_tv - 0.1, **SEAT[papa], face="twijfel", face_amt=0.5, at=TV)
S.beat(bro, t_tv - 0.1, **SEAT[bro], face="neutraal", face_amt=0.5, at=TV)

# ---------------------------------------------------------------- de nieuwsstudio (ver buiten het huis)
ST = V(60.0, 0.0, 0.0)
T.box("Studio_achterwand", ST + V(0, 3.0, 0), (9.0, 0.2, 5.0), S.mat("studio_blauw", (0.12, 0.25, 0.65), 1.2), bevel=0, ol=0)
T.box("Studio_vloer", ST + V(0, 0, -0.02), (12.0, 12.0, 0.02), S.mat("studio_vloer", (0.1, 0.1, 0.14)), bevel=0, ol=0)
T.box("Studio_desk", ST + V(0, 0.15, 0), (2.2, 0.8, 0.95), S.mat("studio_desk", (0.85, 0.86, 0.9)), bevel=0.04, ol=0.004)
T.box("Studio_desk_streep", ST + V(0, -0.26, 0.55), (2.22, 0.02, 0.12), S.mat("tv_band", (0.85, 0.08, 0.06), 2.5), bevel=0, ol=0)
ST3.label("Studio_logo", "NEWS 24", ST + V(-1.55, 2.88, 1.72), 0.3, col=(1, 1, 1), rot=(90, 0, 0), glow=2.0)
ST3.label("Studio_band_tekst", "ALERT SYSTEM FAULT  ·  WORLDWIDE", ST + V(0, -0.28, 0.52), 0.075, col=(1, 1, 1), rot=(90, 0, 0), glow=2.0)
key = bpy.data.lights.new("Studio_key", "AREA")
key.energy, key.size = 600, 2.0
ko = bpy.data.objects.new("Studio_key", key)
bpy.context.scene.collection.objects.link(ko)
ko.location = ST + V(1.2, -3.0, 2.8)
ko.rotation_euler = (math.radians(60), 0, math.radians(20))
nl = S.actor("nieuwslezeres", ST + V(0, 0.75, 0), 0)
pap = T.box("Nieuws_papieren", (0, 0, 0), (0.24, 0.01, 0.32), S.mat("papier", (0.96, 0.96, 0.94)), bevel=0.002, ol=0.002)
grab(S, pap, nl, 0.0, "hand.R", loc=(0, 0.08, 0.02), rot=(90, 0, 0))
DESK = arms(arm("L", (0.25, 0.6, -0.75), (-0.2, 0.95, 0.15)), arm("R", (0.25, 0.6, -0.75), (-0.2, 0.95, 0.15)))
S.beat(nl, 0.0, "staan", arms=DESK, face="zelfverzekerd", face_amt=0.6, look=(0, 0))
nline = S.say("N04-02", who=nl, at=t_tv + 0.2)
# papieren rechtzetten (tik op de desk), korte blik opzij naar iemand buiten beeld
S.beat(nl, t_st + 0.4, "staan", arms=DESK, face="zelfverzekerd", face_amt=0.6, look=(0, 0), crouch=(0.02, 4))
S.beat(nl, t_st + 0.6, "staan", arms=DESK, face="zelfverzekerd", face_amt=0.6, look=(0, 0))
S.beat(nl, t_st + 1.7, "staan", arms=DESK, face="nerveus", face_amt=0.6, look=(0.8, 0.0), body={"head": (0, 25, 0)})
S.beat(nl, t_st + 2.3, "staan", arms=DESK, face="zelfverzekerd", face_amt=0.5, look=(0, 0))
S.hold(nl, END)

# ---------------------------------------------------------------- 4d: opa stopt met kauwen, vork halverwege boven zijn bord
S.beat(opa, t_d, **SEAT[opa], face="neutraal", face_amt=0.5, at=TV)
for k, t in enumerate(frange(t_d, t_d + 1.3, 0.25)):
    A.key_prop(opa.rig, "mond_open", 0.25 if k % 2 else 0.0, F(t))
A.key_prop(opa.rig, "mond_open", 0.0, F(t_d + 1.45))
S.reach(opa, t_d, "L", PLATE[opa] + V(0.2, -0.08, 0.3))
S.reach(opa, t_d + 0.6, "L", PLATE[opa] + V(0.22, -0.1, 0.24))
S.reach(opa, END, "L", PLATE[opa] + V(0.22, -0.1, 0.24))
S.beat(opa, t_d + 1.5, **SEAT[opa], face="twijfel", face_amt=0.9, at=TV)
A.blink_at(opa, F(t_d + 0.8))
for ch in (oma, held, mama, papa, bro, opa):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 4a WIDE trage dolly langs de tafel (HOUSE RULES op de koelkast rechts in beeld)
S.cam(0.0, ((-0.9, -3.4, 2.15), (0.1, -0.3, 0.9), 24), ((-0.15, -3.45, 2.12), (0.3, -0.3, 0.9), 23))
# 4b MEDIUM: papa en het broertje
S.cam(t_b, ((1.0, -2.9, 1.5), (1.45, -0.2, 1.05), 30), ((1.05, -2.6, 1.47), (1.45, -0.2, 1.05), 33))
# 4c OTS vanaf de tafelrand (geen hoofd in beeld), push-in naar de tv
S.cam(t_tv, ((0.7, -1.2, 1.2), TV, 48), ((0.2, -1.35, 1.22), TV, 54))
# 4c de nieuwslezeres op tv (beeld vult het scherm)
S.cam(t_st, (ST + V(0.0, -2.2, 1.3), ST + V(0, 0.6, 1.15), 35), (ST + V(0.0, -2.0, 1.3), ST + V(0, 0.6, 1.15), 37))
# 4d CLOSE op opa
HO = S.headpos(opa, t_d + 1.0)
S.cam(t_d, (HO + V(-0.12, -1.6, 0.0), HO + V(0.12, 0, -0.05), 36), (HO + V(-0.1, -1.45, 0.0), HO + V(0.12, 0, -0.05), 38))

# ---------------------------------------------------------------- HUD en geluid
S.countdown(0, 0.3, END, jumps=[(0.0, 3 * 3600 + 21 * 60 + 5), (t_b, 3 * 3600 + 20 * 60 + 40), (t_tv, 3 * 3600 + 20 * 60 + 30)])
S.ambience("sfx_diner_sfeer", 0.0, t_st, vol=0.18)
S.sfx("sfx_klok_tik", 0.0, 0.1, loop_to=END)
S.sfx("sfx_glas_klink", 1.2, 0.18)
S.sfx("sfx_ruis_tv", t_tv, 0.12, cut=(0.0, 0.9))
S.sfx("sfx_glitch", nline[1] - 0.05, 0.6)
S.finish(length=END, tail=0.0)
