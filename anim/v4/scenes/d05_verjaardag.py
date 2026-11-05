"""D05 · Opa's horloge (script scène 5a-5g). Keuken, 14e verjaardag, 's middags.
5a  WIDE 3,5 s: het hele gezin aan tafel, hij blaast de 14 kaarsjes uit, iedereen klapt.
5a1 MEDIUM 3,4 s: hij grijnst, het gezin klapt.  VO (over 5a en 5a1): "That afternoon, the whole family squeezes ..."
5a2 CLOSE 4,2 s: oma knijpt in zijn wang.  OMA: "Fourteen already. You'll be grown before we know it."
5b  MEDIUM 3 s: opa schuift een doosje over tafel.  OPA: "This was my father's."
5c  DETAIL 3 s: hij klikt het doosje open: een gouden zakhorloge, de gravure in de klep.
5d  CLOSE 3,8 s: opa glimlacht.  OPA: "Time is the one thing nobody gets more of."
5e  DETAIL 2,5 s: zijn hand met het horloge; de schaafwond op zijn knokkels trekt weg.
5f  CLOSE 4 s, push-in: hij kijkt van het horloge naar opa, glimlach verdwijnt; kijkt naar mama, oma, broertje. VO: "Nobody."
5g  CLOSE 5,3 s: VO "Except you. And at fourteen... you haven't figured out what that means yet."  SFX: tik.

    python3 anim/v4/scenes/d05_verjaardag.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d05", "keuken", "nd_verjaardag", exposure=0.2)
sh = S.cuts([3.5, 3.4, 4.2, 3.0, 3.0, 3.8, 2.5, 4.0, 5.3])
END = sh[-1][1]
t_a1, t_a2, t_b, t_c, t_d, t_e, t_f, t_g = (s[0] for s in sh[1:])

TX, TY, TZ = 0.2, -0.6, 0.76
BY = TY + 0.62
OMA_AT, HERO_AT, OPA_AT = V(TX - 0.72, BY, 0), V(TX, BY, 0), V(TX + 0.72, BY, 0)
BRO_AT = V(TX - 0.72, TY - 0.62, 0)             # voor aan tafel, met zijn rug half naar de camera
MAMA_AT, PAPA_AT = V(TX - 1.72, TY, 0), V(TX + 1.48, TY, 0)
# stoelen: voorste rij weg behalve die van het broertje, achterste rij onder de drie figuren, kopse stoelen naar de tafel
for o in [o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")]:
    if o.location.y < TY - 0.3 and abs(o.location.x - BRO_AT.x) > 0.2:
        o.hide_render = o.hide_viewport = True
achter = sorted([o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")
                 and o.location.y > TY], key=lambda o: o.location.x)
for o, x in zip(achter, (OMA_AT.x, HERO_AT.x, OPA_AT.x)):
    o.location.x = x
for o in [o for o in bpy.data.objects if o.name.startswith("Stoel_kop")]:
    if o.location.x > TX:
        o.location.x += PAPA_AT.x - (TX + 1.72)
# taart en cadeau op hun plek (taart voor hem)
taart = S.obj("Verjaardagstaart")
taart.location = (HERO_AT.x, TY + 0.0, TZ)
cad = S.obj("Cadeau_ouders")
if cad:
    cad.location = (TX + 0.95, TY - 0.15, TZ)
for o in bpy.data.objects:
    if o.name.startswith("Taartbordje_") and abs(o.location.x - TX) < 0.05:
        o.hide_render = o.hide_viewport = True
bpy.context.view_layer.update()

# ---------------------------------------------------------------- het gezin
bro = S.actor("broertje", BRO_AT, 180)
oma = S.actor("oma", OMA_AT, 0)
held = S.actor("hoofdpersonage_kind", HERO_AT, 0)
opa = S.actor("opa", OPA_AT, 0, drop=("wandelstok",))
mama = S.actor("mama", MAMA_AT, 90)
papa = S.actor("papa", PAPA_AT, -90)
SEAT = {}
for ch, at, r in ((bro, BRO_AT, 180), (oma, OMA_AT, 0), (held, HERO_AT, 0), (opa, OPA_AT, 0), (mama, MAMA_AT, 90), (papa, PAPA_AT, -90)):
    spec, z = sit(ch)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0, z), r)


def seat(ch, lean=None):
    d = dict(SEAT[ch])
    if lean is not None:
        d["crouch"] = (d["crouch"][0], lean)
    return d


H_HEAD = S.head(held)
CAKE_TOP = V(HERO_AT.x, TY + 0.0, TZ + 0.33)
FAM = (bro, oma, opa, mama, papa)

# 5a: hij buigt naar de taart en blaast; de vlammetjes gaan uit; iedereen klapt
S.beat(held, 0.0, **seat(held), face="grijns", face_amt=0.8, at=CAKE_TOP)
S.beat(held, 0.7, **seat(held, 18), face="verbaasd", face_amt=0.7, at=CAKE_TOP, mond_O=1.0)
S.beat(held, 1.5, **seat(held, 20), face="verbaasd", face_amt=0.7, at=CAKE_TOP, mond_O=1.0)
S.beat(held, 1.9, **seat(held), face="lach", face_amt=1.0, at=S.head(mama))
T_OUT = 1.25
flames = [o for o in bpy.data.objects if o.name.startswith("Verjaardagstaart_vlam") or o.name.startswith("Verjaardagstaart_kaarslicht")]
for o in flames:
    show(o, 0.0, T_OUT + 0.04 * (hash(o.name) % 5))
for ch in FAM:
    S.beat(ch, 0.0, **SEAT[ch], face="blij", face_amt=0.7, at=H_HEAD)
for k, t in enumerate(frange(1.6, t_a2 - 0.2, 0.22)):
    for j, ch in enumerate(FAM):
        if ch is opa and t > t_a2 - 1.0:
            continue
        S.beat(ch, t + 0.03 * j, **SEAT[ch], arms=CLAP_A if (k + j) % 2 else CLAP_B, face="lach", face_amt=0.9, at=H_HEAD)
for ch in FAM:
    S.beat(ch, t_a2, **SEAT[ch], face="blij", face_amt=0.8, at=H_HEAD)
S.beat(held, t_a1 + 0.6, **seat(held), face="grijns", face_amt=1.0, at=S.head(papa))
S.beat(held, t_a1 + 2.2, **seat(held), face="lach", face_amt=0.9, at=S.head(bro))

# 5a2: oma knijpt in zijn wang (haar linkerhand, ~0,3 m voor zijn hoofdcentrum, aan haar kant)
CHEEK = H_HEAD + V(-0.26, -0.14, -0.08)
S.beat(oma, t_a2, **SEAT[oma], face="lach", face_amt=0.9, at=H_HEAD)
S.reach(oma, t_a2 - 0.1, "L", None, 0.0)
S.reach(oma, t_a2 + 0.5, "L", CHEEK)
S.reach(oma, t_a2 + 1.0, "L", CHEEK + V(0.01, 0.0, 0.01))
S.reach(oma, t_a2 + 1.3, "L", CHEEK + V(0.0, 0.0, -0.01))
S.reach(oma, t_a2 + 1.9, "L", None, 0.0)
S.beat(oma, t_a2 + 2.0, **SEAT[oma], face="blij", face_amt=1.0, at=H_HEAD + V(0, 0, -0.5))   # bekijkt hem van top tot teen
S.beat(oma, t_a2 + 3.0, **SEAT[oma], face="lach", face_amt=0.8, at=H_HEAD)
S.beat(held, t_a2 + 0.3, **seat(held), face="twijfel", face_amt=0.6, at=S.head(oma), body={"head": (0, 0, -8)})
S.beat(held, t_a2 + 1.4, **seat(held), face="grijns", face_amt=0.7, at=S.head(oma), body={"head": (0, 0, -6)})
S.beat(held, t_a2 + 3.0, **seat(held), face="blij", face_amt=0.7, at=S.head(oma))

# 5b: opa schuift een doosje over tafel
BOX0, BOX1 = V(OPA_AT.x - 0.2, TY + 0.40, TZ), V(HERO_AT.x + 0.22, TY + 0.36, TZ)
doos = ND.horlogedoosje("Horlogedoosje", tuple(BOX0), rot_z=180)
dek = S.obj("Horlogedoosje_deksel")
for t, p in ((0.0, BOX0), (t_b + 0.4, BOX0), (t_b + 1.6, BOX1)):
    key(doos, t, loc=tuple(p))
S.beat(opa, t_b - 0.3, **seat(opa, 10), face="blij", face_amt=0.7, at=BOX0)
S.reach(opa, t_b - 0.3, "R", None, 0.0)
S.reach(opa, t_b + 0.3, "R", BOX0 + V(0.03, -0.02, 0.09))
S.reach(opa, t_b + 1.6, "R", BOX1 + V(0.06, -0.03, 0.09))
S.reach(opa, t_b + 2.1, "R", None, 0.0)
S.beat(opa, t_b + 1.0, **seat(opa, 14), face="blij", face_amt=0.8, at=H_HEAD)
S.beat(opa, t_b + 2.2, **SEAT[opa], face="blij", face_amt=0.8, at=H_HEAD)
S.beat(held, t_b, **seat(held), face="verbaasd", face_amt=0.6, at=BOX0)
S.beat(held, t_b + 1.4, **seat(held, 10), face="verbaasd", face_amt=0.7, at=BOX1)

# 5c: hij klikt het doosje open; het horloge ligt erin met de klep open (gravure)
in_doos = ND.zakhorloge("Zakhorloge_doos", (0, 0, 0), open_=0.95, ketting=False)
in_doos.parent = doos
in_doos.location = (0.004, -0.01, 0.034)
in_doos.rotation_euler = (0, 0, math.radians(180))
T_OPEN = t_c + 0.9
for t, v in ((0.0, 0.0), (T_OPEN, 0.0), (T_OPEN + 0.35, 1.0)):
    dek.rotation_euler.x = -math.radians(105) * v
    dek.keyframe_insert("rotation_euler", index=0, frame=F(t))
S.reach(held, t_c, "R", BOX1 + V(0.04, -0.07, 0.06))
S.reach(held, T_OPEN + 0.3, "R", BOX1 + V(0.04, -0.08, 0.10))
S.reach(held, t_c + 2.4, "R", None, 0.0)
S.beat(held, t_c, **seat(held, 14), face="verbaasd", face_amt=0.7, at=BOX1)
S.beat(held, T_OPEN + 0.4, **seat(held, 14), face="verbaasd", face_amt=1.0, at=BOX1, ogen_wijd=0.5)

# 5d: opa glimlacht
S.beat(opa, t_d, **SEAT[opa], face="blij", face_amt=0.9, at=H_HEAD)
S.beat(opa, t_d + 2.0, **SEAT[opa], face="blij", face_amt=1.0, at=H_HEAD + V(0, 0, -0.05), body={"head": (6, 0, 4)})
A.blink_at(opa, F(t_d + 1.4))
S.beat(held, t_d, **seat(held), face="blij", face_amt=0.6, at=S.head(opa))

# 5e: het horloge in zijn hand (palm omhoog, voor zijn borst); schaafwond trekt weg
def LOOKH(ch, f):                                    # hand voor de borst, palm omhoog (onderarm gedraaid)
    A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
hand_w = S.watch(held, t_e - 0.1, side="R", name="Zakhorloge", open_=0.95, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3)
show(hand_w, t_e - 0.1)
show(in_doos, 0.0, t_e - 0.1)
for o in in_doos.children_recursive:
    show(o, 0.0, t_e - 0.1)
for o in hand_w.children_recursive:
    show(o, t_e - 0.1)
S.beat(held, t_e - 0.1, **seat(held, 8), arms=LOOKH, face="blij", face_amt=0.5, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.watch_hands("Zakhorloge", t_e, END, every=1.0)
plek = T.sphere("Schaafwond", (0, 0, 0), 0.02, S.mat("schaafwond", (0.85, 0.25, 0.25)), scale=(1.6, 1.0, 0.35), seg=12, ol=0)
plek.parent = held.rig
plek.parent_type = "BONE"
plek.parent_bone = "hand.R"
plek.matrix_parent_inverse = Matrix.Identity(4)
plek.location = (0.0, -0.01, -0.03)
for t, s in ((0.0, 1.0), (t_e + 0.5, 1.0), (t_e + 2.0, 0.001)):
    key(plek, t, scale=s)

def glance(ch):
    """Kijkpunt richting ch, maar half naar de camera (hoofd draait ~30 graden, gezicht blijft zichtbaar)."""
    d = S.head(ch) - H_HEAD
    d.z = 0
    return H_HEAD + d.normalized() * 0.6 + V(0, -1.0, -0.1)


# 5f: hij kijkt van het horloge naar opa, de glimlach verdwijnt; mama, oma, broertje
S.beat(held, t_f, **seat(held, 8), arms=LOOKH, face="blij", face_amt=0.5, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.beat(held, t_f + 0.7, **seat(held), arms=LOOKH, face="blij", face_amt=0.3, at=glance(opa))
S.beat(held, t_f + 1.6, **seat(held), arms=LOOKH, face="neutraal", face_amt=0.6, at=glance(opa))
S.beat(held, t_f + 2.3, **seat(held), arms=LOOKH, face="nerveus", face_amt=0.4, at=glance(mama))
S.beat(held, t_f + 3.0, **seat(held), arms=LOOKH, face="nerveus", face_amt=0.5, at=glance(oma))
S.beat(held, t_f + 3.6, **seat(held), arms=LOOKH, face="verdrietig", face_amt=0.3, at=glance(bro))
A.blink_at(held, F(t_f + 1.9))
for ch in (oma, mama, papa, bro):
    S.beat(ch, t_f, **SEAT[ch], face="blij", face_amt=0.7, at=H_HEAD)
S.beat(bro, t_f + 1.0, **SEAT[bro], face="lach", face_amt=0.8, at=S.head(mama))
# 5g: hij kijkt weer naar het horloge
S.beat(held, t_g + 0.2, **seat(held, 6), arms=LOOKH, face="verdrietig", face_amt=0.25, look=(0.0, -0.7), body={"head": (16, 0, 0)})
S.beat(held, t_g + 3.0, **seat(held, 6), arms=LOOKH, face="twijfel", face_amt=0.4, look=(0.0, -0.7), body={"head": (17, 0, 3)})
A.blink_at(held, F(t_g + 2.2))
for ch in (held, bro, oma, opa, mama, papa):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(TX + 1.5, TY - 2.6, 1.75), V(TX - 0.1, BY - 0.2, 0.95), 24), (V(TX + 1.3, TY - 2.25, 1.68), V(TX - 0.05, BY - 0.2, 0.98), 24))
S.cam(t_a1, (V(TX + 0.15, TY - 1.45, 1.35), V(TX, BY, 1.05), 30), (V(TX + 0.12, TY - 1.3, 1.33), V(TX, BY, 1.08), 30))
S.cam(t_a2, (V(TX - 0.40, TY - 0.95, 1.3), V(TX - 0.36, BY, 1.12), 32), (V(TX - 0.38, TY - 0.85, 1.3), V(TX - 0.36, BY, 1.12), 32))
S.cam(t_b, (V(TX + 0.75, TY - 0.95, 1.55), V(OPA_AT.x - 0.25, BY - 0.25, 0.98), 30),
      (V(TX + 0.65, TY - 0.90, 1.50), V(HERO_AT.x + 0.25, BY - 0.25, 0.95), 30))
S.cam(t_c, (BOX1 + V(0.10, -0.30, 0.38), BOX1 + V(0, 0, 0.03), 45), (BOX1 + V(0.07, -0.20, 0.27), BOX1 + V(0, 0, 0.035), 45))
S.cam(t_d, S.shot(opa, t_d + 1.0, size="cu", az=-30, lens=40), S.shot(opa, t_d + 1.0, size=0.62, az=-28, lens=40))
S.cam(t_e, None, fn=lambda t: (S.bone_world(held, "hand.R", t_e + 0.5) + V(-0.15, -0.30, 0.40),
                               S.bone_world(held, "hand.R", t_e + 0.5) + V(0, 0, 0.03), 50))
S.cam(t_f, S.shot(held, t_f + 1.0, size="cu", az=0, lens=40), S.shot(held, t_f + 3.0, size=0.55, az=0, lens=40))
S.cam(t_g, S.shot(held, t_g + 1.0, size="mcu", az=28, lens=35), S.shot(held, t_g + 4.0, size=0.85, az=24, lens=35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.0, tick=False)
S.say("D05-01", at=0.2)
S.sfx("sfx_applaus_gezin", 1.5, 0.3)
S.say("D05-02", who=oma, at=t_a2 + 0.25)
S.say("D05-03", who=opa, at=t_b + 0.5)
S.sfx("sfx_doosje_klik", T_OPEN, 0.45)
S.say("D05-04", who=opa, at=t_d + 0.2)
S.tick(t_e + 0.6, 0.25)
S.tick(t_e + 1.6, 0.25)
S.say("D05-05", at=t_f + 1.5)
S.say("D05-06", at=t_g + 0.15)
S.tick(END - 0.2, 0.55)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.08)
S.music("piano_warm", 0.0, END, vol=0.16, fade_in=0.5, fade_out=0.6)
S.finish(length=END, tail=0.0)
