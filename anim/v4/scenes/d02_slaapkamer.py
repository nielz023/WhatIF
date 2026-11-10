"""D02 · Dinsdag, zijn 14e verjaardag (script scène 2d, 2e, 3a, 3b). Slaapkamer, ochtend.
2d  CLOSE 3,4 s: hij ligt in bed, ogen open, de wekker gaat; de teller verschijnt (YEAR 2026 · AGE 14).
    VO: "It starts on a Tuesday. Your fourteenth birthday."
2e  WIDE 3,3 s: hij springt uit bed, loopt langs het bed en stoot zijn teen tegen de hoekpost.  "Ow, ow, OW!"
2e2 MEDIUM 2,9 s: hij hinkt op één been, handen bij zijn knie.  VO: "Rule one. You can still get hurt."
3a  DETAIL 2,6 s: zijn teen, de rode plek trekt in een seconde weg.  VO: "Rule two. You always heal. Every single time."
3b  CLOSE 3,4 s: hij staart naar zijn voet, fronst, wiebelt met zijn tenen.  JONGEN: "...huh."

    python3 anim/v4/scenes/d02_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d02", "slaapkamer", "ochtend", exposure=0.25)
sh = S.cuts([3.4, 3.3, 3.35, 2.6, 3.6])   # 2e2 langer: D02-04 liep over D03-01 heen
END = sh[-1][1]
t_e, t_e2, t_3a, t_3b = sh[1][0], sh[2][0], sh[3][0], sh[4][0]

# wekker: 07:00
tijd = S.obj("Wekker_tijd")
if tijd and getattr(tijd.data, "body", None) is not None:
    tijd.data.body = "07:00"

# ---------------------------------------------------------------- 2d: hij ligt in bed (zelfde opbouw als video 3 n05a)
LIE_AT = V(-1.45, 0.1, 0.4)
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = o.hide_viewport = True
duv = S.obj("Dekbed_blauw") or S.obj("Dekbed")
DUV_TOP = 0.80
lig = S.actor("hoofdpersonage_kind", LIE_AT, 0)
spec, rz = sit(lig, seat_top=0.52, lean=4)
LEG = lig.J["pelvis"].z - lig.J["ankle.L"].z
FZ = 0.49 - rz
spec["feet"] = ((0.06, 0.8 * LEG, FZ), (-0.06, 0.8 * LEG, FZ))
P_ = lig.J["pelvis"].z
HIP = LIE_AT + V(0, P_ * math.sin(math.radians(75)), P_ * math.cos(math.radians(75)))
SIT_AT = V(LIE_AT.x, HIP.y - 0.05, rz)
YB = HIP.y - 0.12
dmat = duv.active_material if duv else S.mat("dekbed_blauw", (0.25, 0.45, 0.85))
deken = [T.box("Dekbed_benen", (LIE_AT.x - 0.09, (YB - 0.62) / 2, 0.44), (1.0, YB + 0.62, DUV_TOP - 0.44), dmat, bevel=0.12, ol=0),
         T.box("Dekbed_borst", (LIE_AT.x - 0.09, (YB + 1.32) / 2, 0.44), (1.0, 1.32 - YB, 0.44), dmat, bevel=0.14, ol=0)]
HIPZ = rz + lig.J["pelvis"].z - spec["crouch"][0]
PIV = V(LIE_AT.x, HIP.y, HIPZ)
piv = bpy.data.objects.new("D02_heup_draaipunt", None)
T._link(piv)
piv.location = PIV
lig.rig.parent = piv
ad = lig.rig.animation_data
if ad and ad.action:
    for fc in list(A._fcurves(lig.rig)):
        if fc.data_path in ("location", "rotation_euler"):
            try:
                ad.action.fcurves.remove(fc)
            except Exception:
                fc.keyframe_points.clear()
lig.rig.location = SIT_AT - PIV
lig.rig.rotation_euler = (0, 0, 0)
lig.rig.keyframe_insert("location", frame=F(0.0))
lig.rig.keyframe_insert("rotation_euler", frame=F(0.0))
piv.rotation_euler = (math.radians(-80), 0, 0)
lig.last = None
a = math.radians(80)
drop = spec["crouch"][0]
legs = []
for (sx, fwd0, fz0) in spec["feet"]:
    rest = lig.J["ankle.L"].z - (P_ - drop)
    v0y, v0z = -fwd0, fz0 + rest
    y = v0y * math.cos(a) - v0z * math.sin(a)
    z = v0y * math.sin(a) + v0z * math.cos(a)
    legs.append((sx, -y, z - rest))
LIE = dict(crouch=spec["crouch"], feet=tuple(legs))
T_RING = 0.45
S.beat(lig, 0.0, "staan", face="neutraal", face_amt=0.3, look=(0.0, 0.1), body={"head": (-4, 10, 0)}, **LIE)
S.beat(lig, T_RING + 0.15, "staan", face="verbaasd", face_amt=0.4, look=(0.6, 0.3), body={"head": (-6, 22, 0)}, **LIE)
S.beat(lig, 1.7, "staan", face="blij", face_amt=0.6, look=(0.0, 0.2), body={"head": (-4, 8, 0)}, **LIE)
S.beat(lig, 2.6, "staan", face="grijns", face_amt=0.9, look=(0.0, 0.0), body={"head": (-2, 4, 0)}, **LIE)
S.hold(lig, t_e)
A.blink_at(lig, F(1.25))
for o in [lig.rig] + deken:
    show(o, 0.0, t_e)
S.qc_skip.add(lig.name)       # ligt half onder het dekbed: QC-hoofdregels gelden niet voor de liggende kopie

# ---------------------------------------------------------------- 2e: uit bed, teen tegen de hoekpost, hinken
held = S.actor("hoofdpersonage_kind", (-0.70, 0.95, 0.0), 0)
show(held.rig, t_e)
CORNER = V(-1.0, -0.19, 0.0)                         # hoekpost van het voeteneinde
S.teleport(held, t_e, (-0.70, 0.95, 0.0), 0)
# landt uit een sprong (gebogen knieën), kijkt opgewekt de kamer in
S.beat(held, t_e, "armen_omhoog", amount=0.5, face="lach", face_amt=0.8, crouch=(0.16, 8))
S.beat(held, t_e + 0.35, "juichen", amount=0.6, face="lach", face_amt=0.9, crouch=(0.04, 2))
# loopt langs het bed naar het voeteneinde (richting -y) ... linkervoet blijft achter de hoekpost haken
T_STUB = t_e + 1.55
S.walk(held, t_e + 0.45, T_STUB, [(-0.70, 0.95, 0), (-0.80, 0.30, 0), (-0.86, -0.02, 0)], stride=0.42, arms=0.8)
S.beat(held, t_e + 1.0, "staan", face="blij", face_amt=0.8, feet="keep", at=V(0.6, -2.0, 1.0))
S.beat(held, T_STUB - 0.05, "staan", face="blij", face_amt=0.7, feet=((0, 0.10, 0.0), (0, -0.08, 0.04)), at=V(0.6, -2.0, 1.0))
# BAM: schrik, ogen dicht geknepen, linkerknie omhoog
KNEE = arms(arm("L", (0.25, 0.55, -0.80), (-0.15, 0.85, -0.50)), arm("R", (0.25, 0.55, -0.80), (0.20, 0.85, -0.50)))
S.beat(held, T_STUB + 0.06, "schrik", face="inspanning", face_amt=1.0, crouch=(0.06, 10),
       feet=((0, 0.10, 0.10), (0, 0.0, 0.0)))
S.beat(held, T_STUB + 0.30, "staan", arms=KNEE, face="schreeuw", face_amt=1.0, crouch=(0.08, 22),
       feet=((0, 0.16, 0.30), (0, 0.0, 0.0)))
# hinken op het rechterbeen: kleine sprongetjes, rondje om de as
HOP0 = V(-0.86, -0.02, 0.0)
hop_t = [t for t in frange(T_STUB + 0.35, END + 0.01, 0.32) if t < t_3b - 0.05]
for k, t in enumerate(hop_t):
    p = HOP0 + V(0.10 * math.sin(k * 0.9), -0.08 * k, 0.0)
    up = (k % 2 == 0)
    rot = 15 * math.sin(k * 0.8)
    if t < t_3a or t > t_3b:
        S.place(held, t, p + V(0, 0, 0.07 if up else 0.0), rot)
    else:
        S.place(held, t, HOP0 + V(0, -0.45, 0), 0)
    S.beat(held, t, "staan", arms=KNEE, face="schreeuw" if t < t_e2 + 0.8 else "inspanning",
           face_amt=1.0 if t < t_e2 + 0.8 else 0.7, crouch=(0.10 if up else 0.16, 20),
           feet=((0, 0.16, 0.30 + (0.03 if up else 0.0)), (0, 0.0, 0.0)))
# 3b: staat weer op twee voeten en staart naar zijn tenen (geen hinken meer)
S.place(held, t_3b - 0.02, HOP0 + V(0, -0.45, 0), 0)
S.beat(held, t_3b, "staan", face="twijfel", face_amt=0.6, at=HOP0 + V(-0.1, -0.75, 0.0), body={"spine": (14, 0, 0)},
       arms=arms(arm("L", (0.30, 0.20, -0.93), (0.15, 0.30, -0.94)), arm("R", (0.30, 0.20, -0.93), (0.15, 0.30, -0.94))),
       feet=((0, 0.08, 0.0), (0, -0.04, 0.0)))
for k, t in enumerate(frange(t_3b + 0.4, END - 0.3, 0.35)):           # wiebelt met zijn tenen
    A.bone_rot(held, F(t), "toe.L" if "toe.L" in held.pb else "foot.L", (12 if k % 2 else -6, 0, 0))
S.beat(held, t_3b + 1.8, "staan", face="verbaasd", face_amt=0.6, at=HOP0 + V(-0.1, -0.75, 0.0), body={"spine": (14, 0, 6)},
       arms=arms(arm("L", (0.30, 0.20, -0.93), (0.15, 0.30, -0.94)), arm("R", (0.30, 0.20, -0.93), (0.15, 0.30, -0.94))),
       feet=((0, 0.08, 0.0), (0, -0.04, 0.0)))
A.blink_at(held, F(t_3b + 1.2))
S.hold(held, END)

# ---------------------------------------------------------------- 3a: de rode plek op zijn teen trekt weg
foot_o = None
plek = T.sphere("Blauwe_plek", (0, 0, 0), 0.028, S.mat("blauwe_plek", (0.55, 0.12, 0.35), 0.0), scale=(1.0, 1.0, 0.45), seg=16, ol=0)
plek.parent = held.rig
plek.parent_type = "BONE"
plek.parent_bone = "toe.L" if "toe.L" in held.pb else "foot.L"
plek.matrix_parent_inverse = Matrix.Identity(4)
plek.location = (0.0, 0.03, 0.035)
for t, s in ((0.0, 0.001), (T_STUB, 0.001), (T_STUB + 0.05, 1.0), (t_3a + 0.7, 1.0), (t_3a + 1.6, 0.001)):
    key(plek, t, scale=s)

# ---------------------------------------------------------------- camera's
HL = S.headpos(lig, 1.0)
# 2d CLOSE: van boven-opzij op zijn gezicht in het kussen, trage push-in
S.cam(0.0, (HL + V(0.85, -0.55, 0.55), HL + V(0, 0, -0.03), 30), (HL + V(0.72, -0.46, 0.47), HL + V(0, 0, -0.03), 32))
# 2e WIDE vanuit de deurhoek: hij springt eruit en loopt naar het voeteneinde
S.cam(t_e, (V(1.55, -1.55, 1.35), V(-0.95, 0.35, 0.75), 22), (V(1.45, -1.62, 1.3), V(-0.95, 0.10, 0.70), 22))
# 2e2 MEDIUM: hinken, iets lager
HM = S.headpos(held, t_e2 + 1.2)
S.cam(t_e2, (HM + V(1.05, -1.75, -0.35), HM + V(0, 0, -0.35), 28), (HM + V(0.95, -1.6, -0.35), HM + V(0, 0, -0.35), 29),
      handheld=0.6)
# 3a DETAIL: zijn opgetrokken voet (hij staat nog op één been), trage drift
S.sc.frame_set(F(t_3a + 1.0))
FT = held.rig.matrix_world @ held.pb["foot.L"].tail
S.cam(t_3a, (FT + V(0.80, -1.00, 0.50), FT + V(0, 0, 0.10), 42), (FT + V(0.74, -0.93, 0.46), FT + V(0, 0, 0.10), 45))   # hoger en verder: zijn been komt anders voor de lens
# 3b CLOSE: zijn gezicht, hij kijkt omlaag (camera laag)
HB = S.headpos(held, t_3b + 1.5)
S.cam(t_3b, (HB + V(0.25, -1.12, -0.62), HB + V(0, 0, -0.12), 26), (HB + V(0.22, -1.06, -0.60), HB + V(0, 0, -0.12), 27))   # verder weg: hij buigt naar voren

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2026, t0=0.6)
S.sfx("sfx_wekker", T_RING, 0.45, cut=(0.0, 2.6))
S.say("D02-02", at=0.15)
S.sfx("sfx_teen_stoot", T_STUB, 0.6)
S.say("D02-03", who=held, at=T_STUB + 0.12)
S.say("D02-04", at=t_e2 + 0.55)
S.say("D03-01", at=t_3a + 0.1)
S.say("D03-02", who=held, at=t_3b + 2.2)
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.08)
S.music("speels", t_e + 1.6, END, vol=0.22, fade_in=1.0)
S.finish(length=END, tail=0.0)
