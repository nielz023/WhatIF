"""N05a · Middernacht: het alarm (script scène 5a-5b).
De telefoon in zijn hand schiet aan: rood scherm, nucleair alarm. Hij schrikt rechtop en vangt de telefoon.
Detail: THIS IS NOT A TEST. AS OF 00:00, ALL LAWS AND RULES ARE CANCELLED. THERE ARE NO MORE RULES.

    blender -b -P anim/v3/scenes/n05a_alarm.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n05a", "slaapkamer", "nr_nacht", exposure=0.3, night=True)
sh = S.cuts([2.2, 3.0])
END = sh[-1][1]
t_b = sh[1][0]
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

# ---------------------------------------------------------------- de jongen: half in slaap, dan rechtop
BX = -1.52
held = S.actor("hoofdpersonage_pyjama", (BX, 0.32, 0.5), 0)
for t, tilt, y in ((0.0, -70, 0.32), (0.35, -74, 0.32), (0.55, -22, 0.62), (0.75, -16, 0.64), (0.95, -20, 0.63), (END, -20, 0.63)):
    held.rig.rotation_euler = (math.radians(tilt), 0, 0)
    held.rig.keyframe_insert("rotation_euler", frame=F(t))
    held.rig.location = (BX, y, 0.5)
    held.rig.keyframe_insert("location", frame=F(t))
held.last = None
phone = prop_phone(S, "Telefoon_alarm", screen=RED)
grab(S, phone, held, 0.0, "hand.R", loc=(0, 0.07, 0.02), rot=(90, 0, 180))
HOLD = arms(arm("R", (0.25, 0.55, -0.6), (-0.35, 0.85, 0.35)), arm("L", (0.25, 0.55, -0.6), (-0.4, 0.85, 0.3)))
S.beat(held, 0.0, "staan", arms=HOLD, face="neutraal", face_amt=0.4, look=(0.0, -0.3), feet="keep")
A.blink_at(held, F(0.05), closed=6)
# schok: lijf krimpt (anticipatie), dan omhoog; de telefoon glipt en hij vangt hem
S.beat(held, 0.3, "staan", arms=HOLD, face="geschrokken", face_amt=0.6, look=(0.0, -0.3), feet="keep", crouch=(0.04, 10))
S.beat(held, 0.6, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, look=(0.0, -0.5), feet="keep")
S.beat(held, 0.95, "staan", arms=arms(arm("R", (0.3, 0.75, -0.3), (-0.2, 0.9, 0.3)), arm("L", (0.3, 0.75, -0.3), (-0.3, 0.9, 0.25))),
       face="geschrokken", face_amt=1.0, look=(0.0, -0.5), feet="keep")
S.beat(held, 1.25, "staan", arms=HOLD, face="geschrokken", face_amt=0.85, look=(0.0, -0.4), feet="keep")
S.hold(held, END)
# rood schermlicht op zijn gezicht
glow = T.point_light("Schermlicht_rood", (BX, 1.0, 1.3), color=RED, energy=0, radius=0.1, shadow=False)
light_key(glow, 0.0, 0)
light_key(glow, 0.12, 60)
light_key(glow, END, 60)
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
HH = S.headpos(held, 1.2)
H0 = S.headpos(held, 0.0)
# 5a CLOSE statisch, schok (camera schudt mee met het alarm)
S.cam(0.0, (HH + V(0.4, -1.7, 0.25), H0 + V(0, 0, 0.15), 28), (HH + V(0.4, -1.7, 0.25), HH + V(0, 0, -0.05), 28), shake=S.shake(0.6),
      ease=False)
# 5b DETAIL push-in op het scherm
S.cam(t_b, (P0 + V(0.05, -2.3, 0.05), P0 + V(0, 0, 0.0), 40), (P0 + V(0.03, -1.95, 0.03), P0 + V(0, 0, 0.02), 40), handheld=0.2)

# ---------------------------------------------------------------- geluid: hard op de cut, na 1,5 s 10 dB omlaag
S.sfx("sfx_alarm_nucleair", 0.1, 1.0, keys=[(0.1, 1.0), (1.6, 1.0), (2.0, 0.32)], loop_to=END)
S.sfx("sfx_alarm_piep", 0.1, 0.8)
S.sfx("sfx_dreun", 0.1, 0.6)
S.no_hud.append((0.0, END))
S.finish(length=END, tail=0.0)
