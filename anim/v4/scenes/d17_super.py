"""D17 · Het supercontinent, 250 miljoen jaar (script scène 17b-17d). Rode rotsvlakte, gebergte in de verte.
17b  WIDE track 3 s: hij loopt over een droge vlakte tussen rode rotsen.  VO: "You walk from what used to be Europe..."
17c  WIDE 3 s: hij komt over een bergkam; aan de andere kant dezelfde vlakte.  VO: "...to what used to be America."
17d  CLOSE 3 s: JONGEN (schor): "Took me six hundred years."  Hij gaat zitten en schudt zand uit zijn schoen.

    python3 anim/v4/scenes/d17_super.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d17", "heuvel", "super", exposure=0.15)
sh = S.cuts([3.4, 3.0, 3.6])
END = sh[-1][1]
t_c, t_d = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker")
S.hide("Zon_17b", "Maan")                                  # de verduistering is pas scène 17b


def ground(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = bpy.context.scene.ray_cast(dg, Vector((x, y, 300.0)), Vector((0, 0, -1)))
    return loc.z if hit else 0.0


# ---------------------------------------------------------------- 17b: lopen tussen de rotsen
P0, P1 = V(-6.0, -2.0, 0.0), V(2.0, 4.0, 0.0)
P0.z, P1.z = ground(P0.x, P0.y), ground(P1.x, P1.y)
loop = S.actor("hoofdpersonage_zwerver", P0, 127, label="hoofdpersonage_loop")
show(loop.rig, 0.0, t_c)
S.walk(loop, 0.0, t_c, [P0, P1], stride=0.4)
for t in (0.0, 1.6):
    S.beat(loop, t, "staan", face="vastberaden", face_amt=0.5, body={"spine": (6, 0, 0)}, look=(0.0, -0.2))

# ---------------------------------------------------------------- 17c: boven op de bergkam (Bergkam: top op z 8 bij (14, 30))
KAM = V(14.0, 30.0, 8.0)
KAM.z = ground(KAM.x, KAM.y)
kam = S.actor("hoofdpersonage_zwerver", KAM + V(-1.6, -1.6, 0), 135, label="hoofdpersonage_kam")
show(kam.rig, t_c, t_d)
S.walk(kam, t_c, t_c + 2.2, [KAM + V(-1.6, -1.6, 0), KAM + V(0.3, 0.3, 0)], stride=0.36)
S.beat(kam, t_c, "staan", face="vastberaden", face_amt=0.5, body={"spine": (8, 0, 0)})
S.beat(kam, t_c + 2.3, "handen_zij", face="twijfel", face_amt=0.6, at=KAM + V(60, 60, -10))
S.hold(kam, t_d)

# ---------------------------------------------------------------- 17d: zitten op een rots, zand uit de schoen
ROTS = V(3.0, 6.0, 0.0)
ROTS.z = ground(ROTS.x, ROTS.y)
T.sphere("Zitrots", tuple(ROTS + V(0, 0, 0.12)), 0.45, S.mat("zitrots_rood", (0.50, 0.20, 0.09)), scale=(1.2, 1.0, 0.75), seg=16, ol=0)
SEAT = ROTS.z + 0.12 + 0.45 * 0.75
held = S.actor("hoofdpersonage_zwerver", ROTS, 200)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, V(ROTS.x, ROTS.y, hz_), 200)
show(held.rig, t_d)
REST = arms(arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)), arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)))
S.beat(held, t_d, **hs, arms=REST, face="neutraal", face_amt=0.5, body={"spine": (4, 0, 0)}, look=(0.0, -0.3))
FOOT = S.bone_world(held, "foot.R", t_d + 0.1) if "foot.R" in held.rig.pose.bones else V(ROTS.x, ROTS.y, ROTS.z + 0.1)
S.beat(held, t_d + 1.4, **hs, arms=REST, face="twijfel", face_amt=0.5, body={"spine": (22, 0, 0), "head": (14, 0, 0)}, mouth=0.3)
S.reach(held, t_d + 1.5, "R", FOOT + V(0, 0, 0.12))
for k, t in enumerate(frange(t_d + 1.8, t_d + 3.0, 0.15)):
    S.reach(held, t, "R", FOOT + V(0.03 if k % 2 else -0.03, 0, 0.14))
S.hold(held, END)
for t in (t_d + 2.0, t_d + 2.4, t_d + 2.8):
    S.puff(FOOT + V(0, 0, 0.05), t, n=3, r=(0.02, 0.05), grow=1.6, dur=0.7, color=(0.72, 0.42, 0.22), rise=-0.1, spread=0.1)
HD = S.headpos(held, t_d + 0.5)

# ---------------------------------------------------------------- camera's
S.cam(0.0, None, fn=lambda t: (S._root_matrix(loop, t).translation + V(1.8, -6.0, 1.6), S._root_matrix(loop, t).translation + V(0, 0, 1.0), 26))
S.cam(t_c, (KAM + V(-4.5, -4.5, 1.4), KAM + V(20, 20, -1.0), 22), (KAM + V(-4.2, -4.2, 1.5), KAM + V(20, 20, -1.0), 22))
FW = V(math.sin(math.radians(200)), -math.cos(math.radians(200)), 0)
S.cam(t_d, (HD + FW * 1.9 + V(0.45, 0, -0.25), HD + V(0, 0, -0.4), 30), (HD + FW * 1.75 + V(0.42, 0, -0.25), HD + V(0, 0, -0.4), 30))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(250000000, t0=0.0, tick=False)
S.say("D17-03", at=0.3)
S.say("D17-04", at=t_c + 0.2)
S.say("D17-05", who=held, at=t_d + 0.2)
S.ambience("sfx_wind_hoog", 0.0, END, vol=0.08)
S.music("m_spanning_puls", 0.0, END, vol=0.12, fade_in=0.0, fade_out=0.6)
S.finish(length=END, tail=0.0)
