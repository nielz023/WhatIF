"""N04b · De laatste seconden voor middernacht (script scène 4e-4g).
De jongen ligt in bed met zijn telefoon (blauw maanlicht, schermlicht op zijn gezicht), gaapt en rekt zich uit.
Detail: de wekker op het nachtkastje springt van 23:59:57 naar 58, 59. Close: ogen vallen bijna dicht, en de
aftelklok verdwijnt met een harde cut.

    blender -b -P anim/v3/scenes/n04b_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n04b", "slaapkamer", "nr_nacht", exposure=0.3, night=True)
sh = S.cuts([3.5, 3.0, 1.5])
END = sh[-1][1]
t_f, t_g = sh[1][0], sh[2][0]

# ---------------------------------------------------------------- de jongen half liggend tegen zijn kussen
BX, BY = -1.38, 0.86
# zoals n05a: hij LIGT onder het dekbed (benen en buik eronder), alleen armen en hoofd erboven; licht rechtop tegen het kussen
LIE_AT = V(-1.38, 0.1, 0.4)
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = o.hide_viewport = True
duv = S.obj("Dekbed_blauw")
DUV_TOP = 0.80
held = S.actor("hoofdpersonage_pyjama", LIE_AT, 0)
spec, rz = sit(held, seat_top=0.52, lean=4)
LEG = held.J["pelvis"].z - held.J["ankle.L"].z
FZ = 0.6 - rz
spec["feet"] = ((0.06, 0.8 * LEG, FZ), (-0.06, 0.8 * LEG, FZ))
P_ = held.J["pelvis"].z
HIP = LIE_AT + V(0, P_ * math.sin(math.radians(75)), P_ * math.cos(math.radians(75)))
SIT_AT = V(LIE_AT.x, HIP.y - 0.05, rz)
YB = HIP.y - 0.12
T.box("Dekbed_benen", (-1.47, (YB - 0.62) / 2, 0.44), (1.12, YB + 0.62, DUV_TOP - 0.44), duv.active_material, bevel=0.12, ol=0)
# dekbed tot over zijn borst (onder de oksels), de armen met de telefoon erboven
T.box("Dekbed_borst", (-1.47, YB + 0.22, 0.44), (1.12, 0.44, 0.40), duv.active_material, bevel=0.14, ol=0)
HIPZ = rz + held.J["pelvis"].z - spec["crouch"][0]
PIV = V(LIE_AT.x, HIP.y, HIPZ)
piv = bpy.data.objects.new("N04b_heup_draaipunt", None)
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
held.rig.location = V(0, 0.0, -P_)                    # liggend: heup = draaipunt, benen gestrekt naar het voeteneinde
held.rig.rotation_euler = (0, 0, 0)
held.rig.keyframe_insert("location", frame=F(0.0))
held.rig.keyframe_insert("rotation_euler", frame=F(0.0))
TILT = -74.0                                          # half liggend tegen het kussen (hoofd naar het hoofdeinde, +y)
for t in (0.0, END):
    piv.rotation_euler = (math.radians(TILT), 0, 0)
    piv.keyframe_insert("rotation_euler", frame=F(t))
held.last = None

# telefoon in zijn handen boven zijn gezicht, met schermlicht op zijn gezicht
phone = prop_phone(S, "Telefoon_bed", screen=(0.5, 0.75, 1.0))
grab(S, phone, held, 0.0, "hand.R", loc=(0, 0.07, 0.02), rot=(90, 0, 180), release=t_f - 0.05)
HOLD = arms(arm("R", (0.25, 0.55, -0.6), (-0.35, 0.85, 0.35)), arm("L", (0.25, 0.55, -0.6), (-0.4, 0.85, 0.3)))
S.beat(held, 0.0, "staan", arms=HOLD, face="neutraal", face_amt=0.6, look=(0.0, -0.4))
glow = T.point_light("Schermlicht", (BX, 0.75, 1.15), color=(0.55, 0.75, 1.0), energy=25, radius=0.1, shadow=False)
# duim scrolt
for k, t in enumerate(frange(0.2, 1.6, 0.3)):
    A.bone_rot(held, F(t), "hand.R", (8 if k % 2 else -6, 0, 0))
# gaapt en rekt zich uit
S.beat(held, 1.7, "staan", arms=HOLD, face="verbaasd", face_amt=0.9, look=(0.0, 0.3))
A.key_prop(held.rig, "mond_open", 0.0, F(1.6))
A.key_prop(held.rig, "mond_open", 0.9, F(2.0))
A.key_prop(held.rig, "mond_open", 0.9, F(2.5))
A.key_prop(held.rig, "mond_open", 0.0, F(2.9))
S.beat(held, 2.1, "armen_omhoog", amount=0.6, face="verbaasd", face_amt=0.8, look=(0.0, 0.5))
S.beat(held, 2.9, "staan", arms=HOLD, face="neutraal", face_amt=0.6, look=(0.0, -0.4))
A.blink_at(held, F(2.95), closed=6)
# 4g: half in slaap, ogen vallen bijna dicht
S.beat(held, t_g, "staan", arms=arms(arm("R", (0.2, 0.3, -0.93), (0.0, 0.9, -0.3)), arm("L", (0.2, 0.3, -0.93), (0.0, 0.9, -0.3))),
       face="neutraal", face_amt=0.4, look=(0.0, -0.2))
A.blink_at(held, F(t_g + 0.5), closed=9)                # ogen vallen bijna dicht (zware, trage knipper)
S.hold(held, END)

# de telefoon ligt in 4f naast de wekker (de set-telefoon), in 4e niet
for nm in ("Telefoon", "Telefoon_scherm"):
    o = S.obj(nm)
    if o and o.name in (nm,):
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=1)
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=F(t_f))
light_key(glow, 0.0, 25)
light_key(glow, t_f, 0)

# ---------------------------------------------------------------- 4f: de wekker 23:59:57 -> 58 -> 59
secs = {s: S.obj(f"Wekker_sec_{s}") for s in ("57", "58", "59", "00")}
for k, s in enumerate(("57", "58", "59")):
    o = secs[s]
    if o is None:
        continue
    t_on = t_f + k * 1.0
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=1)
    o.hide_render = False
    o.keyframe_insert("hide_render", frame=F(t_on))
    if k < 2:
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=F(t_on + 1.0))
    o.hide_viewport = False

# ---------------------------------------------------------------- camera's
CLOCK = S.obj("Wekker").matrix_world.translation.copy()
HH = S.headpos(held, 1.0)
# 4e WIDE trage push naar het bed
S.cam(0.0, ((0.75, -1.5, 1.55), HH + V(0.1, -0.3, -0.25), 24), ((0.35, -0.9, 1.45), HH + V(0.05, -0.2, -0.2), 26))
# 4f DETAIL wekker (statisch, lichte drift)
S.cam(t_f, (CLOCK + V(0.12, -0.42, 0.05), CLOCK + V(0, 0, 0.01), 55), (CLOCK + V(0.11, -0.4, 0.05), CLOCK + V(0, 0, 0.01), 57))
# 4g CLOSE op zijn gezicht
HG = S.headpos(held, t_g + 0.5)
S.cam(t_g, (HG + V(0.25, -0.75, 0.8), HG + V(0, 0, -0.02), 34), (HG + V(0.23, -0.68, 0.74), HG + V(0, 0, -0.02), 36))

# ---------------------------------------------------------------- HUD en geluid
S.countdown(0, 0.3, t_g + 0.95, jumps=[(0.0, 10), (t_f, 3), (t_g, 1)])
S.ambience("sfx_krekels_nacht", 0.0, t_f, vol=0.12)
S.sfx("sfx_klok_tik", 0.0, 0.12, loop_to=t_f)
for k in range(3):
    S.sfx("sfx_klok_tik", t_f + k * 1.0, 0.5, cut=(0.0, 0.5))
S.sfx("sfx_klok_tik", t_g, 0.55, cut=(0.0, 0.5))
S.finish(length=END, tail=0.0)
