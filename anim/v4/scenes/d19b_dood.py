"""D19b · De rode reus, het einde van de aarde (script scène 19b-19f).
19b  CLOSE push-in 3 s: zijn gezicht, rood verlicht (zelfde beeld als de cold open).  VO: "This is where you started this video."
19c  DETAIL 2 s: het horloge in zijn hand; het glas barst door de hitte, de wijzers tikken door.
19d  LOW WIDE 3 s: de vuurmuur komt over de horizon op hem af.
19e  CLOSE 3 s · GROOT MOMENT: hij doet zijn ogen dicht en houdt het horloge tegen zijn borst. Alleen het gebrul.
19f  WIT 1 s: witte flits, de teller glitcht en is weg.

    python3 anim/v4/scenes/d19b_dood.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d19b", "heuvel", "dood", exposure=0.1)
sh = S.cuts([3.0, 2.2, 3.2, 3.2, 1.0])
END = sh[-1][1]
t_c, t_d, t_e, t_f = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker")

SUN = V(0.0, 2600.0, 260.0)
HP = V(0.0, -1.2, 0.0)
held = S.actor("hoofdpersonage_rafels", HP, 180)
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.5, at=SUN)
S.beat(held, t_c, "staan", arms=arms(REST_L, LOOKH), face="neutraal", face_amt=0.4, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.beat(held, t_d, "staan", arms=arms(REST_L, LOOKH), face="bang", face_amt=0.6, at=SUN + V(0, -1800, -250))
S.beat(held, t_d + 1.6, "staan", arms=arms(REST_L, LOOKH), face="bang", face_amt=0.8, at=SUN + V(0, -2200, -250))
CHEST = S.headpos(held, t_e) + V(0, 0.18, -0.62)
S.beat(held, t_e, "staan", face="verdrietig", face_amt=0.3, at=SUN, body={"head": (6, 0, 0)})
S.reach(held, t_e - 0.3, "R", None, 0.0)
S.reach(held, t_e - 0.3, "L", None, 0.0)
S.reach(held, t_e + 0.1, "R", CHEST + V(-0.05, 0, 0))
S.reach(held, t_e + 0.1, "L", CHEST + V(0.08, 0, 0.02))
S.reach(held, END, "R", CHEST + V(-0.05, 0, 0))
S.reach(held, END, "L", CHEST + V(0.08, 0, 0.02))
S.eyes_closed(held, t_e + 0.5, END)
S.hold(held, END)
hw = S.watch(held, t_c - 0.1, side="R", name="Zakhorloge_dood", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3,
             barst=True, oud=True)
for o in [hw] + list(hw.children_recursive):
    show(o, t_c - 0.1)
barst = [o for o in bpy.data.objects if o.name.startswith("Zakhorloge_dood") and "barst" in o.name]
for o in barst:
    show(o, t_c + 1.0)
S.watch_hands("Zakhorloge_dood", t_c, END, every=1.0)
WH = S.bone_world(held, "hand.R", t_c + 0.8)
HD = S.headpos(held, 0.5)

# de vuurmuur komt op hem af (19d) en raakt hem (19f)
vm = bpy.data.objects.get("Vuurmuur")
if vm:
    key(vm, 0.0, scale=(1, 1, 1))
    key(vm, t_d, scale=(1, 1, 1))
    key(vm, t_f, scale=(0.05, 0.05, 1))
# 19f: witte flits (een wit vlak vlak voor de camera)
CAMF = HD + V(0.0, 1.6, 0.0)
wit = T.box("Witte_flits", tuple(CAMF + V(0, -0.3, 0)), (3.0, 0.01, 2.0), ND.pbr("witte_flits", (1, 1, 1), emit=(1, 1, 1), strength=40.0),
            bevel=0, ol=0, base=False)
show(wit, t_f)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (HD + V(0.25, 1.6, -0.05), HD + V(0, 0, -0.05), 40), (HD + V(0.18, 1.2, -0.05), HD + V(0, 0, -0.05), 40))
S.cam(t_c, (WH + V(0.1, 0.32, 0.45), WH, 45), (WH + V(0.09, 0.29, 0.41), WH, 45))
S.cam(t_d, (V(0.8, -6.5, 0.35), V(0, 20, 5), 20), (V(0.8, -6.3, 0.36), V(0, 20, 5), 20), handheld=0.2)
S.cam(t_e, (HD + V(0.3, 1.7, -0.15), HD + V(0, 0, -0.28), 32), (HD + V(0.26, 1.55, -0.15), HD + V(0, 0, -0.28), 32), handheld=0.08)
S.cam(t_f, (CAMF, HD, 35))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(5000000000, t0=0.0, t1=t_f + 0.25, tick=False)
S.say("D19-03", at=0.3)
S.sfx("sfx_glas_klink", t_c + 1.0, 0.2)
S.tick(t_c + 0.3, 0.35)
S.tick(t_c + 1.3, 0.35)
S.sfx("sfx_glitch", t_f, 0.3)
S.ambience("sfx_zon_gebrul", 0.0, END, vol=0.16)
S.sfx("sfx_vuur", t_d, 0.2, loop_to=t_f)
S.music("subbas", 0.0, t_d, vol=0.12, fade_in=0.0, fade_out=0.6)
S.finish(length=END, tail=0.0)
