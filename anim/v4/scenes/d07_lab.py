"""D07 · Het lab (script scène 7a-7i). Lab van de wetenschapper, koel blauw licht.
7a  WIDE 4,8 s, trage pan: hij ligt in een scanner, mama met haar armen om zichzelf, de wetenschapper typt.
    VO: "A week later, Mom drives you to the lab. She hasn't slept since the fall."
7b  DETAIL 2,5 s: het scherm CELL AGE: 0 DAYS, knipperend.
7c  MEDIUM 3,5 s: de wetenschapper zet de glazen bak met het kwalletje naast hem.  "Meet the only other one like you."
7d  DETAIL 3,4 + 3,4 s: het kwalletje krimpt en wordt weer jong, in een lus.  VO: "Here's the crazy part. ..."
7d2 CLOSE 5,6 s: hij drukt zijn neus tegen het glas.  VO: "It's the closest thing to immortal ... Until you."
7e  CLOSE 3 s: de wetenschapper, bril in zijn hand.  "You'll outlive everyone you know."
7f  CLOSE 2,5 s: mama pakt zijn hand; hij kijkt naar haar hand, dan naar haar gezicht.
7g  DETAIL 3,6 s: het nieuws op tv: THE BOY WHO CAN'T DIE.  NIEUWSLEZERES: "...and doctors say he hasn't aged a single day."
7h  CLOSE 5,4 s: hij haalt het horloge uit zijn zak. Tik.  VO: "The whole world wants to know how long you'll live. ..."
7i  CLOSE 2 s: VO "How long will they?"

    python3 anim/v4/scenes/d07_lab.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene4("d07", "lab", None, exposure=0.1)
sh = S.cuts([4.8, 2.5, 3.5, 3.4, 3.4, 5.6, 3.0, 2.5, 3.6, 5.4, 2.0])
END = sh[-1][1]
t_b, t_c, t_d, t_d1, t_d2, t_e, t_f, t_g, t_h, t_i = (s[0] for s in sh[1:])
S.hide("Hydraulische_pers", "Pers_label", "Veiligheidslijn")
for o in bpy.data.objects:
    if o.name.startswith(("Personage_marker", "Character_marker")):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de scanner (op de plek van de pers)
WIT = S.mat("scanner_wit", (0.94, 0.95, 0.97))
BLAUW = S.mat("scanner_blauw", (0.25, 0.6, 1.0), 2.0)
T.box("Scanner_bed_voet", (0, 3.0, 0), (0.6, 1.6, 0.62), S.mat("scanner_grijs", (0.6, 0.63, 0.68)), bevel=0.05, ol=0.004)
T.box("Scanner_bed", (0, 3.4, 0.62), (0.75, 3.0, 0.16), WIT, bevel=0.05, ol=0.004)
T.torus("Scanner_ring", (0, 4.45, 1.12), 0.78, 0.30, WIT, rot=(90, 0, 0), seg=48, seg2=16, ol=0.004)
T.torus("Scanner_ring_licht", (0, 4.12, 1.12), 0.62, 0.025, BLAUW, rot=(90, 0, 0), seg=48, seg2=8, ol=0)
T.box("Scanner_sokkel", (0, 4.45, 0), (1.9, 0.62, 0.40), WIT, bevel=0.05, ol=0.004)
BED_Z = 0.78
# kar voor de kwallenbak
T.box("Kar_kwal", (1.1, 3.0, 0), (0.45, 0.4, 1.12), S.mat("kar_metaal", (0.7, 0.73, 0.78)), bevel=0.02, ol=0.004)
bak = ND.kwallenbak("Kwallenbak", (1.1, 3.0, 1.12), rot_z=90)
kwal = S.obj("Kwallenbak_kwal")
show(bak, t_c - 0.1)
for o in bak.children_recursive:
    show(o, t_c - 0.1)
# het kwalletje krimpt en wordt weer jong (lus) en drijft op en neer
K0 = V(kwal.location)
for k, t in enumerate(frange(t_c, END, 1.6)):
    key(kwal, t, loc=tuple(K0 + V(0, 0, 0.012 * (k % 2))), scale=1.0)
    key(kwal, t + 0.8, loc=tuple(K0 + V(0, 0, 0.012 * ((k + 1) % 2))), scale=0.45 if k % 2 == 0 else 1.0)

# ---------------------------------------------------------------- het scherm: CELL AGE: 0 DAYS
MON = S.obj("Monitor_1")
MP = V(MON.location) + V(0, -0.06, 0.08)
lbl = ST3.label("Scherm_cell_age", "CELL AGE: 0 DAYS", MP, 0.11, col=(0.4, 0.95, 1.0), rot=(90, 0, 0), glow=4.0)
for k, t in enumerate(frange(t_b, t_c, 0.45)):
    lbl.hide_render = k % 2 == 1
    lbl.keyframe_insert("hide_render", frame=F(t))

# ---------------------------------------------------------------- 7a: hij ligt in de scanner
lig = S.actor("hoofdpersonage_kind", (0, 3.35, BED_Z), 0)
lb = Body(S, lig, (0, 3.35, BED_Z + 0.14), 0)
lb.key(0.0, (0, 3.35, BED_Z + 0.14), tilt=78)
S.beat(lig, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0, 0.6), body={"head": (16, 0, 0)},
       arms=arms(arm("L", (0.30, 0.05, -0.95), (0.25, 0.20, -0.95)), arm("R", (0.30, 0.05, -0.95), (0.25, 0.20, -0.95))),
       **lb.legs(78, spread=0.25))
A.blink_at(lig, F(2.2))
S.hold(lig, t_c)
show(lig.rig, 0.0, t_c)
S.qc_skip.add(lig.name)

mama = S.actor("mama", (-0.95, 3.0, 0), 90)
S.beat(mama, 0.0, "armen_over", face="nerveus", face_amt=0.8, at=V(0, 4.0, 1.1))
S.beat(mama, 2.4, "armen_over", face="verdrietig", face_amt=0.5, at=V(0, 3.9, 1.05), crouch=(0.02, 4))
wet = S.actor("wetenschapper", (4.3, 6.75, 0), 180, drop=("klembord",))
TYPE_A = arms(arm("L", (0.20, 0.70, -0.68), (0.0, 0.92, -0.38)), arm("R", (0.20, 0.70, -0.68), (0.05, 0.90, -0.42)))
TYPE_B = arms(arm("L", (0.20, 0.70, -0.68), (0.05, 0.90, -0.42)), arm("R", (0.20, 0.70, -0.68), (0.0, 0.92, -0.38)))
for k, t in enumerate(frange(0.0, t_c - 0.3, 0.2)):
    S.beat(wet, t, "staan", arms=TYPE_A if k % 2 else TYPE_B, face="neutraal", face_amt=0.6, look=(0, -0.3), crouch=(0.03, 10))

# ---------------------------------------------------------------- vanaf 7c: hij zit op de rand van het bed
SIT = V(0.42, 3.0, 0.0)
zit = S.actor("hoofdpersonage_kind", SIT, 90)
spec, rz = sit(zit, seat_top=BED_Z)
S.place(zit, 0, SIT + V(0, 0, rz), 90)
show(zit.rig, t_c)
GLASS = V(0.98, 3.0, 1.28)
HANDS_BED = arms(arm("L", (0.35, -0.10, -0.93), (0.20, 0.10, -0.97)), arm("R", (0.35, -0.10, -0.93), (0.20, 0.10, -0.97)))


def zs(lean=None):
    d = dict(spec)
    if lean is not None:
        d["crouch"] = (d["crouch"][0], lean)
    return d


S.beat(zit, t_c, **zs(), arms=HANDS_BED, face="twijfel", face_amt=0.5, at=GLASS + V(0.4, 0.3, 0.6))
S.beat(zit, t_c + 1.2, **zs(), arms=HANDS_BED, face="verbaasd", face_amt=0.6, at=GLASS)
EYE_GL = V(1.6, 3.0, 1.6)                              # recht vooruit door de bak: gezicht naar de camera
S.beat(zit, t_d2, **zs(8), arms=HANDS_BED, face="verbaasd", face_amt=0.8, at=EYE_GL)
S.beat(zit, t_d2 + 1.5, **zs(10), arms=HANDS_BED, face="blij", face_amt=0.7, at=EYE_GL)   # neus tegen het glas
S.beat(zit, t_d2 + 4.5, **zs(10), arms=HANDS_BED, face="blij", face_amt=0.5, at=EYE_GL)
S.beat(zit, t_e, **zs(), arms=HANDS_BED, face="neutraal", face_amt=0.6, at=V(1.25, 3.35, 1.6))
S.beat(zit, t_f, **zs(), arms=HANDS_BED, face="nerveus", face_amt=0.4, look=(0.0, -0.8), body={"head": (18, 30, 0)})   # haar hand
S.beat(zit, t_f + 1.3, **zs(), arms=HANDS_BED, face="verdrietig", face_amt=0.4, at=V(0.75, 2.2, 1.55))                 # haar gezicht
# 7h: hij haalt het horloge uit zijn zak (rechterhand), kijkt ernaar
POCKET = arm("R", (0.30, 0.05, -0.95), (0.35, 0.40, -0.85))
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
S.beat(zit, t_h, **zs(), arms=arms(arm("L", (0.35, -0.10, -0.93), (0.20, 0.10, -0.97)), POCKET),
       face="neutraal", face_amt=0.5, look=(0.0, -0.8), body={"head": (16, 0, 0)})
S.beat(zit, t_h + 1.0, **zs(6), arms=arms(arm("L", (0.35, -0.10, -0.93), (0.20, 0.10, -0.97)), LOOKH), face="neutraal",
       face_amt=0.5, look=(0.0, -0.8), body={"head": (20, 0, 0)})
S.beat(zit, t_i, **zs(6), arms=arms(arm("L", (0.35, -0.10, -0.93), (0.20, 0.10, -0.97)), LOOKH), face="verdrietig",
       face_amt=0.4, look=(0.0, -0.8), body={"head": (20, 0, 0)})
A.blink_at(zit, F(t_h + 3.0))
S.hold(zit, END)
hw = S.watch(zit, t_h + 0.55, side="R", name="Zakhorloge", open_=0.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3)
show(hw, t_h + 0.55)
for o in hw.children_recursive:
    show(o, t_h + 0.55)
S.watch_open("Zakhorloge", t_h + 1.6, t_h + 1.9)
S.watch_hands("Zakhorloge", t_h, END, every=1.0)

# mama en de wetenschapper bij hem (vanaf 7c)
S.place(mama, t_c - 0.05, (0.3, 2.3, 0), 170)
S.beat(mama, t_c, "armen_over", face="nerveus", face_amt=0.6, at=S.head(zit))
S.beat(mama, t_e, "armen_over", face="verdrietig", face_amt=0.6, at=V(1.25, 3.35, 1.7))
HAND_Z = SIT + V(0.12, -0.22, BED_Z + 0.05)            # zijn rechterhand op het bed
S.beat(mama, t_f, "staan", face="verdrietig", face_amt=0.7, at=S.head(zit))
S.reach(mama, t_f, "L", None, 0.0)
S.reach(mama, t_f + 0.6, "L", HAND_Z + V(0.0, -0.02, 0.06))
S.reach(mama, END, "L", HAND_Z + V(0.0, -0.02, 0.06))
S.hold(mama, END)
S.place(wet, t_c - 0.05, (1.45, 3.5, 0), -64)
S.beat(wet, t_c, "staan", face="neutraal", face_amt=0.6, at=S.head(zit))
S.reach(wet, t_c - 0.45, "R", None, 0.0)
S.reach(wet, t_c - 0.05, "R", V(1.28, 3.18, 1.42))
S.reach(wet, t_c + 1.2, "R", V(1.27, 3.17, 1.40))
S.reach(wet, t_c + 1.8, "R", None, 0.0)
S.beat(wet, t_c + 1.0, "staan", face="blij", face_amt=0.5, at=S.head(zit))
S.hold(wet, t_e)
show(wet.rig, 0.0, t_e)
# 7e: zelfde wetenschapper zonder bril, de bril in zijn hand
wet2 = S.actor("wetenschapper", (1.45, 3.5, 0), -64, drop=("klembord", "bril"), label="wetenschapper_zonder_bril")
show(wet2.rig, t_e, t_g)
gm = S.mat("bril_montuur", (0.15, 0.12, 0.1))
bril = [T.torus("Bril_glas_L", (0.035, 0, 0), 0.028, 0.004, gm, rot=(90, 0, 0), seg=20, seg2=6, ol=0),
        T.torus("Bril_glas_R", (-0.035, 0, 0), 0.028, 0.004, gm, rot=(90, 0, 0), seg=20, seg2=6, ol=0),
        T.box("Bril_brug", (0, 0, 0.005), (0.016, 0.004, 0.004), gm, base=False, bevel=0, ol=0)]
br = T.merge("Bril_hand", bril, ol=0)
grab(S, br, wet2, 0.0, "hand.R", loc=(0, 0.06, 0.0), rot=(0, 0, 90))
show(br, t_e, t_g)
LOW_GL = arm("R", (0.30, 0.45, -0.84), (0.0, 0.95, 0.30))
S.beat(wet2, t_e, "staan", arms=LOW_GL, face="verdrietig", face_amt=0.5, at=S.head(zit))
S.beat(wet2, t_e + 1.5, "staan", arms=LOW_GL, face="verdrietig", face_amt=0.7, at=S.head(zit) + V(0, 0, -0.05), body={"head": (6, 0, 4)})
A.blink_at(wet2, F(t_e + 0.9))
S.hold(wet2, END)

# ---------------------------------------------------------------- 7g: het nieuws (een studio ver buiten het lab, beeld vult het scherm)
ST = V(80.0, 0.0, 0.0)
T.box("Studio_achterwand", ST + V(0, 3.0, 0), (9.0, 0.2, 5.0), S.mat("studio_blauw", (0.12, 0.25, 0.65), 1.2), bevel=0, ol=0)
T.box("Studio_vloer", ST + V(0, 0, -0.02), (12.0, 12.0, 0.02), S.mat("studio_vloer", (0.1, 0.1, 0.14)), bevel=0, ol=0)
T.box("Studio_desk", ST + V(0, 0.15, 0), (2.2, 0.8, 0.95), S.mat("studio_desk", (0.85, 0.86, 0.9)), bevel=0.04, ol=0.004)
ST3.label("Studio_logo", "NEWS 24", ST + V(-1.15, 2.88, 2.05), 0.3, col=(1, 1, 1), rot=(90, 0, 0), glow=2.0)
key_l = bpy.data.lights.new("Studio_key", "AREA")
key_l.energy, key_l.size = 600, 2.0
ko = bpy.data.objects.new("Studio_key", key_l)
bpy.context.scene.collection.objects.link(ko)
ko.location = ST + V(1.2, -3.0, 2.8)
ko.rotation_euler = (math.radians(60), 0, math.radians(20))
nl = S.actor("nieuwslezeres", ST + V(0, 0.75, 0), 0)
DESK = arms(arm("L", (0.25, 0.6, -0.75), (-0.2, 0.95, 0.15)), arm("R", (0.25, 0.6, -0.75), (-0.2, 0.95, 0.15)))
S.beat(nl, 0.0, "staan", arms=DESK, face="zelfverzekerd", face_amt=0.6, look=(0, 0))
S.beat(nl, t_g + 1.8, "staan", arms=DESK, face="verbaasd", face_amt=0.4, look=(0, 0), body={"head": (0, 0, 5)})
S.hold(nl, END)
# onderbalk: THE BOY WHO CAN'T DIE (en een klein fotootje van hem)
CAMP = ST + V(0.0, -2.2, 1.3)                    # band staat 1 m voor de camera
band = T.box("Nieuws_band", CAMP + V(0, 1.0, -0.20), (1.25, 0.004, 0.12), S.mat("tv_band", (0.85, 0.08, 0.06), 2.5), base=False, bevel=0, ol=0)
ST3.label("Nieuws_band_tekst", "THE BOY WHO CAN'T DIE", CAMP + V(0.06, 0.995, -0.225), 0.055, col=(1, 1, 1), rot=(90, 0, 0), glow=3.0)
T.box("Nieuws_live", CAMP + V(-0.45, 0.995, -0.20), (0.14, 0.004, 0.08), S.mat("live_wit", (1, 1, 1), 2.5), base=False, bevel=0, ol=0)
ST3.label("Nieuws_live_tekst", "LIVE", CAMP + V(-0.45, 0.99, -0.215), 0.04, col=(0.85, 0.08, 0.06), rot=(90, 0, 0), glow=3.0)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(3.6, -1.4, 2.4), V(0.0, 3.8, 1.1), 26), (V(1.8, -2.5, 2.3), V(-0.6, 4.2, 1.1), 26))
S.cam(t_b, (MP + V(0.25, -1.5, 0.05), MP, 35), (MP + V(0.18, -1.0, 0.03), MP, 35), handheld=0.1)
S.cam(t_c, (V(2.4, 1.8, 1.9), V(0.6, 3.05, 1.35), 28), (V(2.3, 1.9, 1.88), V(0.6, 3.05, 1.35), 28))
KP = V(1.1, 3.0, 1.27)
S.cam(t_d, (KP + V(0.0, -0.55, 0.04), KP, 40), (KP + V(0.0, -0.45, 0.03), KP, 40), handheld=0.1)
S.cam(t_d1, (KP + V(-0.08, -0.42, 0.0), KP + V(0, 0, 0.01), 60), (KP + V(-0.06, -0.37, 0.0), KP + V(0, 0, 0.01), 60), handheld=0.1)
S.cam(t_d2, (V(1.85, 3.04, 1.52), V(0.5, 3.0, 1.52), 35), (V(1.75, 3.03, 1.52), V(0.5, 3.0, 1.52), 35))   # door de bak heen
S.cam(t_e, S.shot(wet2, t_e + 1.0, size="mcu", az=-25, lens=35), S.shot(wet2, t_e + 1.0, size=0.85, az=-22, lens=35))
S.cam(t_f, (V(1.6, 2.0, 1.45), V(0.4, 2.65, 1.25), 28), (V(1.55, 2.05, 1.44), V(0.4, 2.65, 1.25), 28))
S.cam(t_g, (CAMP, ST + V(0, 0.6, 1.3), 35))
S.cam(t_h, (V(1.75, 2.0, 1.4), V(0.5, 3.0, 1.3), 30), (V(1.6, 2.1, 1.38), V(0.5, 3.0, 1.3), 30))
S.cam(t_i, (V(1.45, 2.3, 1.12), V(0.55, 2.95, 1.32), 40), (V(1.38, 2.35, 1.14), V(0.55, 2.95, 1.33), 40))   # laag: gezicht en horloge

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D07-01", at=0.2)
S.sfx("sfx_lab_zoem", 0.0, 0.12, loop_to=t_c)
S.sfx("sfx_alarm_piep", t_b + 0.1, 0.12)
S.say("D07-02", who=wet, at=t_c + 0.6)
S.say("D07-03", at=t_d + 0.1)
S.say("D07-04", at=t_d2 + 0.1)
S.say("D07-05", who=wet2, at=t_e + 0.25)
S.say("D07-06", who=nl, at=t_g + 0.1)
S.say("D07-07", at=t_h + 0.15)
S.tick(t_h + 1.9, 0.4)
S.ticks(t_h + 2.9, END - 0.3, every=1.0, vol=0.22)
S.say("D07-08", at=t_i + 0.2)
S.tick(END - 0.15, 0.5)
S.ambience("sfx_lab_zoem", 0.0, END, vol=0.05)
S.music("cello", 0.0, END, vol=0.15, fade_in=0.8, fade_out=0.4)
S.finish(length=END, tail=0.0)
