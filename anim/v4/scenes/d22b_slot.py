"""D22b · Slot: naar het lichtpuntje (script scène 22b-22d). Het donker, geen HUD.
22b  CLOSE 4 s: hij zweeft naar het warme lichtpuntje toe, het horloge open voor zich uit, de wijzers gloeien.
     VO: "And who... or what... do you think is out there? Tell me in the comments."
22c  WIDE trage pull-back 5 s: het lichtpuntje en zijn kleine gloed, steeds kleiner in het zwart.
     VO: "And hit subscribe. You've got time."  SFX: tik... tik.
22c2 DETAIL 3 s: het horloge in zijn hand, de klep open; de gravure licht nog één keer op.  SFX: tik.
22d  ZWART 2 s: Driftmark-logo (in de montage). Geen verwijzing naar een volgende video.

    python3 anim/v4/scenes/d22b_slot.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d22b", "ruimte_nd", "donker", exposure=0.1)
sh = S.cuts([5.6, 5.0, 3.2, 2.0])
END = sh[-1][1]
t_c, t_c2, t_d = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker", "Zakhorloge", "Horloge_gloed")
S.no_hud.append((0.0, END))

for o in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    e = 3.5 if o.name == "Blauwe_rand" else 0.0
    for t, v in ((0.0, e), (t_d, e), (t_d + 0.01, 0.0)):
        o.data.energy = v
        o.data.keyframe_insert("energy", frame=F(t))
wd = bpy.context.scene.world
for n in ([n for n in wd.node_tree.nodes if n.type == "BACKGROUND"] if wd and wd.node_tree else []):
    n.inputs["Strength"].default_value = 0.0
    n.inputs["Strength"].keyframe_insert("default_value", frame=F(0.0))

# het lichtpuntje (al dichterbij dan in 21), links voor hem
LP = V(110.0, 28.0, 14.0)
lp = bpy.data.objects.get("Lichtpuntje")
if lp:
    key(lp, 0.0, loc=tuple(LP), scale=(4, 4, 4))
emission_key("Lichtpuntje_gloed", 0.0, 6.0)
emission_key("Lichtpuntje_gloed", t_d, 0.0)

DL = LP.normalized()
ROT = math.degrees(math.atan2(DL.x, -DL.y))              # gezicht naar het lichtpuntje
HIP0 = V(0.0, 0.0, 0.0)
held = S.actor("hoofdpersonage_rafels", HIP0, ROT)
FW = V(math.sin(math.radians(ROT)), -math.cos(math.radians(ROT)), 0)
SD = V(FW.y, -FW.x, 0)
S.beat(held, 0.0, "staan", face="blij", face_amt=0.5, at=LP)
S.beat(held, t_c2, "staan", face="blij", face_amt=0.4, look=(0.0, -0.8), body={"head": (16, 0, 0)})
S.hold(held, END)
# hij drijft langzaam naar het licht
S.place(held, 0.0, HIP0, ROT)
S.place(held, t_c2, HIP0 + DL * 1.6, ROT)
S.place(held, END, HIP0 + DL * 1.9, ROT)

hw = S.watch(held, 0.0, side="R", name="Opa_horloge", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3,
             lume=3.0, gravure_gloed=0.0)
gl = T.point_light("Opa_horloge_gloed", (0, 0, 0), color=(0.75, 1.0, 0.6), energy=0.35, radius=0.02, shadow=False)
gl.parent = hw
gl.location = (0, 0, 0.04)
S.watch_hands("Opa_horloge", 0.0, t_d, every=1.0, start=(10, 10, 40))

# 22b: horloge open voor zich uit, naar het licht
SH = S.bone_world(held, "upper_arm.R", 0.5, tail=False)
OUT = SH + (LP - SH).normalized() * 0.40 + V(0, 0, -0.05)
S.reach(held, 0.0, "R", OUT)
S.reach(held, t_c2 - 0.3, "R", OUT + DL * 1.6)
# 22c2: horloge terug voor de borst, gravure licht op
def LOOKH(ch, f):
    A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
S.reach(held, t_c2, "R", None, 0.0)
S.beat(held, t_c2, "staan", arms=LOOKH, face="blij", face_amt=0.4, look=(0.0, -0.8), body={"head": (16, 0, 0)})
for t, v in ((0.0, 0.0), (t_c2 + 0.6, 0.0), (t_c2 + 1.3, 3.0), (t_c2 + 2.6, 3.0), (t_d, 0.0)):
    emission_key("Opa_horloge_gravure", t, v, interp="LINEAR")
emission_key("Opa_horloge_lume", t_d, 0.0)
for t, e in ((0.0, 0.35), (t_d - 0.04, 0.35), (t_d, 0.0)):
    gl.data.energy = e
    gl.data.keyframe_insert("energy", frame=F(t))

HD = S.headpos(held, 1.0)
HDc = S.headpos(held, t_c2 + 0.8)
WC = S.bone_world(held, "hand.R", t_c2 + 1.0)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (HD + FW * 1.25 - SD * 0.35 + V(0, 0, -0.1), HD + V(0, 0, -0.15), 38),
      (HD + DL * 0.9 + FW * 1.1 - SD * 0.3 + V(0, 0, -0.1), HD + DL * 0.9 + V(0, 0, -0.15), 38))
CB = HD - DL * 3.0 + SD * 1.2 + V(0, 0, 0.8)
S.cam(t_c, (CB, HD + DL * 1.2, 30), (CB - DL * 9.0 + V(0, 0, 2.5), HD + DL * 4.0, 30))
S.cam(t_c2, (WC + FW * 0.6 + SD * 0.2 + V(0, 0, 0.12), WC, 48), (WC + FW * 0.53 + SD * 0.18 + V(0, 0, 0.1), WC, 48))
S.cam(t_d, (V(0, -400, 0), V(0, -800, 0), 30))      # zwart: camera weg van alles

# ---------------------------------------------------------------- stem en geluid
S.say("D22-02", at=0.3)
S.say("D22-03", at=t_c + 0.6)
for t in (t_c + 3.2, t_c + 4.2, t_c2 + 1.3):
    S.tick(t, 0.3)
S.far_tick(t_c + 3.7, 0.12)
S.music("m_hoop", 0.0, t_d + 1.6, vol=0.10, fade_in=1.0, fade_out=1.5)
S.finish(length=END, tail=0.0)
