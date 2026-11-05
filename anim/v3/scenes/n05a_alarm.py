"""N05a · Middernacht: het alarm (script scène 5a-5b).
Hij slaapt. De telefoon naast hem op het dekbed schiet aan: rood scherm, nucleair alarm. Hij schrikt wakker,
gaat rechtop zitten in bed, pakt de telefoon en kijkt erop (feedback niels: eerst slapen, dan rechtop, telefoon goed in de hand).
Detail: THIS IS NOT A TEST. AS OF 00:00, ALL LAWS AND RULES ARE CANCELLED. THERE ARE NO MORE RULES.

    blender -b -P anim/v3/scenes/n05a_alarm.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n05a", "slaapkamer", "nr_nacht", exposure=0.3, night=True)
sh = S.cuts([2.6, 1.9, 3.0])
t_a2 = sh[1][0]
END = sh[-1][1]
t_b = sh[2][0]
RED = (1.0, 0.08, 0.05)

# wekker op 00:00
for s_, vis in (("57", False), ("58", False), ("59", False), ("00", True)):
    o = S.obj(f"Wekker_sec_{s_}")
    if o:
        o.hide_render = o.hide_viewport = not vis
tijd = S.obj("Wekker_tijd")
if tijd:
    tijd.data.body = "00:00"
for nm in ("Telefoon", "Telefoon_scherm"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de jongen: slaapt, schrikt wakker, gaat rechtop zitten
T_PING = 0.55                                     # telefoon schiet aan
T_WAKE = 0.8                                      # ogen open
T_UP0, T_UP1 = 0.95, 1.5                          # rechtop gaan zitten
T_GRAB = 1.85                                     # pakt de telefoon
T_LOOK = 2.35                                     # telefoon voor zijn gezicht
LIE_AT = V(-1.38, 0.1, 0.4)                       # zoals in video 2: voeten naar het voeteneinde, hoofd in het kussen
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = o.hide_viewport = True
duv = S.obj("Dekbed_blauw")
DUV_TOP = 0.80

held = S.actor("hoofdpersonage_pyjama", LIE_AT, 0)
spec, rz = sit(held, seat_top=0.52, lean=4)
LEG = held.J["pelvis"].z - held.J["ankle.L"].z
FZ = 0.49 - rz                                     # hielen op de matras, benen gestrekt onder het dekbed
spec["feet"] = ((0.06, 0.8 * LEG, FZ), (-0.06, 0.8 * LEG, FZ))
P_ = held.J["pelvis"].z
HIP = LIE_AT + V(0, P_ * math.sin(math.radians(75)), P_ * math.cos(math.radians(75)))
SIT_AT = V(LIE_AT.x, HIP.y - 0.05, rz)
# dekbed: over zijn benen (vast) en over zijn borst; dat deel valt als hij rechtop gaat zitten op zijn schoot
YB = HIP.y - 0.12
T.box("Dekbed_benen", (-1.47, (YB - 0.62) / 2, 0.44), (1.12, YB + 0.62, DUV_TOP - 0.44), duv.active_material, bevel=0.12, ol=0)
borst = T.box("Dekbed_borst", (-1.47, (YB + 1.32) / 2, 0.44), (1.12, 1.32 - YB, 0.44), duv.active_material, bevel=0.14, ol=0)
B0 = borst.location.copy()
for t, sy, sz, y in ((0.0, 1.0, 1.0, B0.y), (T_UP0, 1.0, 1.0, B0.y), (T_UP0 + 0.35, 0.18, 0.75, YB + 0.02), (END, 0.18, 0.75, YB + 0.02)):
    borst.scale = (1.0, sy, sz)
    borst.location = (B0.x, y, B0.z)
    borst.keyframe_insert("scale", frame=F(t))
    borst.keyframe_insert("location", frame=F(t))
# draaipunt in zijn heup: liggen = hele figuur 80 graden achterover om de heup, zitten = rechtop met benen vooruit
HIPZ = rz + held.J["pelvis"].z - spec["crouch"][0]
PIV = V(LIE_AT.x, HIP.y, HIPZ)
piv = bpy.data.objects.new("N05a_heup_draaipunt", None)
T._link(piv)
piv.location = PIV
held.rig.parent = piv
ad = held.rig.animation_data
if ad and ad.action:
    for fc in list(A._fcurves(held.rig)):
        if fc.data_path in ("location", "rotation_euler"):
            try:
                ad.action.fcurves.remove(fc)
            except Exception:
                fc.keyframe_points.clear()
held.rig.location = SIT_AT - PIV
held.rig.rotation_euler = (0, 0, 0)
held.rig.keyframe_insert("location", frame=F(0.0))
held.rig.keyframe_insert("rotation_euler", frame=F(0.0))
for t, tilt in ((0.0, -80), (T_UP0, -80), (T_UP0 + 0.3, -30), (T_UP1, 0), (END, 0)):
    piv.rotation_euler = (math.radians(tilt), 0, 0)
    piv.keyframe_insert("rotation_euler", frame=F(t))
held.last = None


# benen blijven plat op de matras (onder het dekbed) terwijl het lijf om de heup omhoog kantelt:
# voor kanteling a (graden achterover) wijzen de benen in rig-ruimte (0, -cos a, -sin a)
def legs(a_deg):
    a = math.radians(a_deg)
    drop = spec["crouch"][0]
    out = []
    for (sx, fwd0, fz0) in spec["feet"]:
        rest = held.J["ankle.L"].z - (P_ - drop)          # rust-enkel t.o.v. de (gezakte) heup
        v0y, v0z = -fwd0, fz0 + rest                      # zittend: enkel t.o.v. heup (wereld = rig bij 0 graden)
        y = v0y * math.cos(a) - v0z * math.sin(a)
        z = v0y * math.sin(a) + v0z * math.cos(a)
        out.append((sx, -y, z - rest))
    return tuple(out)


TILTS = ((0.0, 80), (T_UP0, 80), (T_UP0 + 0.3, 30), (T_UP1, 0), (END, 0))


def tilt_at(t):
    for (a, ta), (b, tb) in zip(TILTS, TILTS[1:]):
        if a <= t <= b:
            w = (t - a) / max(1e-3, b - a)
            w = w * w * (3 - 2 * w)
            return ta + (tb - ta) * w
    return 0.0


LIE = dict(crouch=spec["crouch"], feet=legs(80))
# slapen: armen langs het lijf, ogen dicht, rustige adem
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.2, look=(0.0, 0.0), body={"head": (-4, 10, 0)}, **LIE)
S.eyes_closed(held, 0.0, T_WAKE)
for k, t in enumerate(frange(0.0, T_PING, 0.5)):
    A.bone_rot(held, F(t), "chest", (3 if k % 2 else -2, 0, 0))
S.beat(held, T_PING + 0.05, "staan", face="neutraal", face_amt=0.3, look=(0.0, 0.0), body={"head": (-4, 10, 0)}, **LIE)
S.beat(held, T_WAKE + 0.05, "staan", face="geschrokken", face_amt=0.8, look=(0.5, -0.2), body={"head": (-8, 22, 0)}, **LIE)
# rechtop: zithouding (benen onder het dekbed), kijkt naar de telefoon naast zich
S.beat(held, T_UP1, "staan", face="geschrokken", face_amt=1.0, look=(0.6, -0.6), body={"head": (-18, 25, 0)}, **spec)

# tijdens het overeind komen: benen per beeld plat houden (overschrijft de tussenwaarden van de beats)
# de voet zelf draait mee terug (anders staan de tenen liggend rechtop en prikken ze door het dekbed)
FSGN = float(os.environ.get("N05A_FSGN", "-1"))
for f in range(1, F(T_UP1) + 1):
    a = tilt_at((f - 1) / FPS)
    fl, fr = legs(a)
    A.crouch(held, f, *spec["crouch"])
    A.foot(held, f, "L", fl, (FSGN * a, 0, 0))
    A.foot(held, f, "R", fr, (FSGN * a, 0, 0))
# de telefoon ligt naast zijn linkerhand op het dekbed (set-telefoon op het nachtkastje weg)
for nm in ("Telefoon", "Telefoon_scherm", "Telefoon_gloed"):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = o.hide_viewport = True
PH = V(-1.0, SIT_AT.y - 0.12, DUV_TOP + 0.006)
phone = prop_phone(S, "Telefoon_alarm", loc=PH, screen=RED)
phone.rotation_euler = (math.radians(-90), 0, math.radians(8))
scr_mat = S.obj("Telefoon_alarm_scherm").active_material
emission_key(scr_mat.name, 0.0, 0.0)
emission_key(scr_mat.name, T_PING, 0.0)
emission_key(scr_mat.name, T_PING + 0.04, 2.5)
# trilt op het dekbed tot hij hem pakt
for k, t in enumerate(frange(T_PING, T_GRAB, 0.06)):
    phone.location = PH + V(0.006 * (1 if k % 2 else -1), 0.004 * (1 if k % 3 else -1), 0)
    phone.keyframe_insert("location", frame=F(t))
phone.location = PH
phone.keyframe_insert("location", frame=F(0.0))
# pakken: linkerhand naar de telefoon, dan met twee handen voor zijn borst, scherm naar zijn gezicht
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, T_UP1, "L", None, 0.0)
S.sc.frame_set(F(T_GRAB))                       # rig hangt aan het kantelpunt: reach() rekent via matrix_world van dit beeld
S.reach(held, T_GRAB, "L", PH + V(0.0, 0.0, 0.05))
S.reach(held, T_GRAB + 0.2, "L", None, 0.0)
grab(S, phone, held, T_GRAB, "hand.L", loc=(0, 0.06, 0.0), mode="loc", offset=(-0.03, -0.05, 0.06))
LOOKP = arms(arm("L", (0.2, 0.5, -0.8), (-0.62, 0.6, 0.5)), arm("R", (0.2, 0.5, -0.8), (-0.62, 0.6, 0.5)))
S.beat(held, T_LOOK, "staan", arms=LOOKP, face="geschrokken", face_amt=1.0, look=(0.0, -0.7), body={"head": (16, 0, 0)}, **spec)
S.beat(held, END, "staan", arms=LOOKP, face="geschrokken", face_amt=0.9, look=(0.0, -0.7), body={"head": (18, 0, 0)}, **spec)
A.blink_at(held, F(T_LOOK + 0.6))
S.hold(held, END)
# telefoon draait mee: plat op het dekbed -> rechtop met het scherm naar hem toe (hij kijkt naar -y)
for t, rx, rzz in ((0.0, -90, 8), (T_GRAB, -90, 8), (T_LOOK, -30, 180), (END, -30, 180)):
    phone.rotation_euler = (math.radians(rx), 0, math.radians(rzz))
    phone.keyframe_insert("rotation_euler", frame=F(t))
# rood schermlicht: eerst van onderen op het plafond/zijn wang, dan op zijn gezicht
glow = T.point_light("Schermlicht_rood", tuple(PH + V(0, 0, 0.25)), color=RED, energy=0, radius=0.1, shadow=False)
light_key(glow, 0.0, 0)
light_key(glow, T_PING, 0)
light_key(glow, T_PING + 0.04, 45)
light_key(glow, END, 60)
glow.location = PH + V(0, 0, 0.25)
glow.keyframe_insert("location", frame=F(T_GRAB))
moon = T.point_light("N05a_vul", (0.0, -1.0, 2.0), color=(0.4, 0.5, 1.0), energy=60, radius=0.5, shadow=False)

# ---------------------------------------------------------------- 5b: het telefoonscherm, leesbaar (grote telefoon bij de lens)
P0 = V(30.0, 0.0, 1.0)
big = T.box("Scherm_close", P0, (0.62, 0.04, 1.25), S.mat("telefoon", (0.08, 0.08, 0.1)), base=False, bevel=0.06, ol=0.004)
scr = T.box("Scherm_close_rood", P0 + V(0, -0.022, 0), (0.56, 0.005, 1.15), S.mat("alarmrood", (0.85, 0.05, 0.03), 2.5), base=False, bevel=0,
            ol=0)
LINES = [("EMERGENCY ALERT", 0.42, 0.055), ("THIS IS NOT A TEST.", 0.24, 0.046), ("AS OF 00:00,", 0.12, 0.046),
         ("ALL LAWS AND RULES", 0.02, 0.046), ("ARE CANCELLED.", -0.08, 0.046), ("THERE ARE", -0.24, 0.06), ("NO MORE RULES.", -0.33, 0.06)]
for k, (txt, z, sz) in enumerate(LINES):
    ST3.label(f"Scherm_regel_{k}", txt, P0 + V(0, -0.027, z), sz, col=(1, 1, 1), rot=(90, 0, 0), glow=2.0)
T.box("Scherm_achtergrond", P0 + V(0, 1.2, -1.5), (6.0, 0.1, 5.0), S.mat("donker_dekbed", (0.03, 0.05, 0.14)), bevel=0, ol=0)
T.point_light("Scherm_licht", tuple(P0 + V(0.0, -1.2, 0.3)), color=(1.0, 0.4, 0.35), energy=60, radius=0.4, shadow=False)

# ---------------------------------------------------------------- camera's
HL = S.headpos(held, 0.2)
HS = S.headpos(held, T_LOOK + 0.3)
GL_AT = HS + V(0.0, -0.45, -0.25)
glow.location = GL_AT
glow.keyframe_insert("location", frame=F(T_LOOK))
# 5a MEDIUM: hij slaapt, telefoon schiet aan, hij schiet overeind (camera schudt mee met het alarm)
S.cam(0.0, ((-0.5, -1.05, 1.6), (HL + HS) / 2 + V(0, 0, 0.0), 24), ((-0.52, -1.0, 1.6), (HL + HS) / 2 + V(0, 0, 0.02), 24.5),
      shake=S.shake(0.5), ease=False)
# 5a2 CLOSE: rood licht op zijn gezicht, hij kijkt naar het scherm
S.cam(t_a2, (HS + V(0.5, -1.5, -0.25), HS + V(0, 0, -0.15), 32), (HS + V(0.45, -1.38, -0.25), HS + V(0, 0, -0.14), 33), handheld=0.3)
# 5b DETAIL push-in op het scherm
S.cam(t_b, (P0 + V(0.05, -2.3, 0.05), P0 + V(0, 0, 0.0), 40), (P0 + V(0.03, -1.95, 0.03), P0 + V(0, 0, 0.02), 40), handheld=0.2)

# ---------------------------------------------------------------- geluid: hard op de cut, na 1,5 s 10 dB omlaag
S.sfx("sfx_alarm_nucleair", T_PING, 1.0, keys=[(T_PING, 1.0), (T_PING + 1.5, 1.0), (T_PING + 1.9, 0.32)], loop_to=END)
S.sfx("sfx_alarm_piep", T_PING, 0.8)
S.sfx("sfx_dreun", T_PING, 0.6)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
