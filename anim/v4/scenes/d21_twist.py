"""D21 · De twist: er tikt iets terug (script scène 21a-21j). Geen HUD, geen muziek: alleen de tik.
21a  DETAIL push-in 4 s: zijn handen in het donker, hij windt het horloge op; de lichtgevende wijzers gloeien op.
21b  CLOSE 3 s: zijn gezicht, onderaf verlicht; het horloge bij zijn oor. Tik.
21c  CLOSE 3 s: hij houdt het horloge stil, duim op de wijzer. Stilte.
21d  CLOSE push-in 3 s: ver weg, links: tik. Zijn ogen schieten open.
21e  DETAIL 2,5 s: de secondewijzer staat stil. Het was niet zijn horloge.
21f  CLOSE: nog een tik, iets dichterbij.  VO (gewone stem, niet fluisteren): "There's no air out here. Sound can't travel through empty space."
21g  CLOSE: VO "So you shouldn't be able to hear that." Hij draait langzaam zijn hoofd naar links.
21h  WIDE 4 s: heel ver weg één warm lichtpuntje dat op de tik aan en uit gaat.  VO: "But you do."
21i  CLOSE push-in 4 s: hij houdt opa's horloge omhoog naar het lichtje en laat de wijzer los. Tik. Ver weg: tik, tik.
21i2 WIDE push-in 4 s: het lichtpuntje komt dichterbij.  VO: "Something else made it to the end of everything."
21j  CLOSE: langzaam een glimlach.  VO: "After a googol years... you are not alone."

    python3 anim/v4/scenes/d21_twist.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d21", "ruimte_nd", "donker", exposure=0.1)
sh = S.cuts([4.0, 3.0, 3.0, 3.0, 2.5, 4.9, 2.9, 4.0, 4.0, 4.0, 5.5])   # 21j langer: D21-05 met gewone stem (4,5 s)
END = sh[-1][1]
t_b, t_c, t_d, t_e, t_f, t_g, t_h, t_i, t_i2, t_j = (s[0] for s in sh[1:])
S.cine_light = False                              # geen key-/randlicht: alleen het licht uit de scène zelf
S.hide("Personage_marker", "Character_marker", "Zakhorloge", "Horloge_gloed")
S.no_hud.append((0.0, END))

# ---------------------------------------------------------------- donker: alleen de blauwe rand, het horloge en het lichtpuntje
for o in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    e = 25.0 if o.name == "Blauwe_rand" else 0.0
    o.data.energy = e
    o.data.keyframe_insert("energy", frame=F(0.0))
wd = bpy.context.scene.world
for n in ([n for n in wd.node_tree.nodes if n.type == "BACKGROUND"] if wd and wd.node_tree else []):
    n.inputs["Strength"].default_value = 0.0
    n.inputs["Strength"].keyframe_insert("default_value", frame=F(0.0))

# het lichtpuntje: links van hem, heel ver weg
LP = V(160.0, -210.0, 30.0)                         # links voor hem (hij kijkt naar -Y; links = +X)
lp = bpy.data.objects.get("Lichtpuntje")
if lp:
    key(lp, 0.0, loc=tuple(LP), scale=(10, 10, 10))
    key(lp, t_i2, loc=tuple(LP), scale=(10, 10, 10))
BASE, FLASH = 30.0, 220.0
emission_key("Lichtpuntje_gloed", 0.0, 0.0)
emission_key("Lichtpuntje_gloed", t_g, BASE)


def far(t, vol=0.14, pan=-0.75):
    """Tik van ver weg + het lichtpuntje gloeit kort op."""
    S.far_tick(t, vol, pan)
    emission_key("Lichtpuntje_gloed", t, FLASH)
    emission_key("Lichtpuntje_gloed", t + 0.25, BASE)


# ---------------------------------------------------------------- hij, zwevend, horloge voor zijn borst
held = S.actor("hoofdpersonage_rafels", (0.0, 0.0, 0.0), 0, rim=False)
dim_flat(held, [(0.0, 0.12)])
FW, SD = V(0, -1, 0), V(-1, 0, 0)                       # gezicht naar -Y; rechts = -X, links = +X


def LOOKH(ch, f):                                        # hand voor de borst, palm omhoog
    A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))


S.beat(held, 0.0, "staan", arms=LOOKH, face="verdrietig", face_amt=0.4, look=(0.0, -0.8), body={"head": (16, 0, 0)})
hw = S.watch(held, 0.0, side="R", name="Opa_horloge", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3,
             lume=0.0, gravure_gloed=0.0)
gl = T.point_light("Opa_horloge_gloed", (0, 0, 0), color=(0.75, 1.0, 0.6), energy=0.0, radius=0.02, shadow=False)
gl.parent = hw
gl.location = (0, 0, 0.04)
for t, v, e in ((0.0, 0.4, 0.1), (0.6, 0.4, 0.1), (2.8, 8.0, 2.5)):
    emission_key("Opa_horloge_lume", t, v, interp="LINEAR")
    gl.data.energy = e
    gl.data.keyframe_insert("energy", frame=F(t))
S.beat(held, 2.4, "staan", arms=LOOKH, face="verdrietig", face_amt=0.4, look=(0.0, -0.8), body={"head": (16, 0, 0)})


def wpos(t):
    bpy.context.scene.frame_set(F(t))
    bpy.context.view_layer.update()
    return hw.matrix_world.translation.copy()


WP = wpos(1.0)
# 21a: linkerhand windt het kroontje op (klein heen-en-weer)
CROWN = WP + V(0.04, -0.05, 0.03)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.6, "L", CROWN)
for k, t in enumerate(frange(0.9, t_b - 0.4, 0.3)):
    S.reach(held, t, "L", CROWN + V(0.0, 0.0, 0.012 if k % 2 else -0.004))
S.reach(held, t_b - 0.1, "L", None, 0.0)
S.sfx("sfx_horloge_opwinden", 0.5, 0.35, loop_to=t_b - 0.4)
S.watch_hands("Opa_horloge", 0.5, t_c + 0.4, every=1.0, start=(10, 10, 32))
n_sec = int((t_c + 0.4 - 0.5) // 1.0) + 1

# 21b: horloge bij zijn oor
S.beat(held, t_b, "staan", face="neutraal", face_amt=0.4, look=(-0.4, -0.1), body={"head": (0, 0, -8)})
HD = S.headpos(held, t_b + 0.6)
EAR = HD + SD * 0.36 + V(0, 0, -0.04)
S.reach(held, t_b - 0.4, "R", None, 0.0)
S.reach(held, t_b, "R", EAR)
S.reach(held, t_c - 0.1, "R", EAR)
S.tick(t_b + 0.8, 0.4)
S.tick(t_b + 1.8, 0.4)
S.eyes_closed(held, t_b + 0.6, t_d + 0.7)

# 21c: horloge terug voor de borst, duim op de wijzer: stilstand en stilte
S.reach(held, t_c + 0.4, "R", None, 0.0)
S.beat(held, t_c + 0.4, "staan", arms=LOOKH, face="verdrietig", face_amt=0.3, look=(0.0, -0.8), body={"head": (16, 0, 0)})
THUMB = WP + V(0.05, -0.04, 0.035)
S.reach(held, t_c + 0.3, "L", THUMB)
S.reach(held, END, "L", THUMB)

# 21d: ver weg, links: tik. Ogen open, adem in
far(t_d + 0.5, 0.11)
S.beat(held, t_d + 0.75, "staan", arms=LOOKH, face="bang", face_amt=0.5, look=(0.0, -0.6), body={"head": (12, 0, 0)}, mouth=0.0)
S.beat(held, t_e, "staan", arms=LOOKH, face="bang", face_amt=0.55, look=(0.3, -0.7), body={"head": (16, 0, 0)})

# 21f-21g: nog een tik, iets dichterbij; hij draait zijn hoofd naar links, naar het geluid
far(t_f + 0.4, 0.15)
S.beat(held, t_f, "staan", arms=LOOKH, face="bang", face_amt=0.5, look=(0.4, -0.2))
S.beat(held, t_g + 0.3, "staan", arms=LOOKH, face="bang", face_amt=0.4, at=LP)
far(t_g + 1.2, 0.16)
S.beat(held, t_h, "staan", arms=LOOKH, face="verbaasd", face_amt=0.5, at=LP)

# 21h: tik, tik op de maat
for t in frange(t_h + 0.5, t_i - 0.2, 1.0):
    far(t, 0.16)

# 21i: horloge omhoog naar het lichtje; hij laat de wijzer los: tik. Antwoord: tik, tik.
S.reach(held, t_i + 0.2, "L", None, 0.0)
SH = S.bone_world(held, "upper_arm.R", t_i + 0.5, tail=False) if "upper_arm.R" in held.rig.pose.bones else HD + V(-0.25, 0, -0.45)
RAISE = SH + (LP - SH).normalized() * 0.42 + V(0, 0, 0.05)
S.reach(held, t_i, "R", None, 0.0)
S.reach(held, t_i + 1.0, "R", RAISE)
S.reach(held, END, "R", RAISE)
S.watch_hands("Opa_horloge", t_i + 1.6, END, every=1.0, start=(10, 10, 32 + n_sec))
S.tick(t_i + 1.6, 0.4)
far(t_i + 2.4, 0.17)
far(t_i + 3.0, 0.17)

# 21i2: het lichtpuntje komt dichterbij
NEAR = HD + (LP - HD) * 0.45
if lp:
    key(lp, END, loc=tuple(NEAR), scale=(10, 10, 10))
for k, t in enumerate(frange(t_i2 + 0.5, END - 0.3, 1.0)):
    far(t, min(0.26, 0.18 + 0.02 * k), -0.6)

# 21j: langzaam een glimlach
S.beat(held, t_j, "staan", face="verbaasd", face_amt=0.3, at=LP)
S.beat(held, t_j + 1.6, "staan", face="blij", face_amt=0.3, at=LP)
S.beat(held, t_j + 3.4, "staan", face="blij", face_amt=0.7, at=LP)
S.hold(held, END)
HJ = S.headpos(held, t_j + 1.0)
DL = (LP - HD).normalized()

# ---------------------------------------------------------------- camera's
WA = wpos(1.5)
S.cam(0.0, (WA + V(0.25, -0.9, 0.12), WA + V(0.05, 0, 0), 35), (WA + V(0.21, -0.76, 0.1), WA + V(0.05, 0, 0), 35))
S.cam(t_b, (HD + V(0.3, -1.25, -0.12), HD + V(-0.05, 0, -0.05), 40), (HD + V(0.27, -1.15, -0.12), HD + V(-0.05, 0, -0.05), 40))
S.cam(t_c, (HD + V(0.15, -1.3, -0.15), HD + V(0, 0, -0.12), 38))
S.cam(t_d, (HD + V(0.12, -1.25, -0.1), HD + V(0, 0, -0.05), 40), (HD + V(0.1, -1.05, -0.08), HD + V(0, 0, -0.05), 40))
WE = wpos(t_e + 1.0)
S.cam(t_e, (WE + V(0.2, -0.75, 0.18), WE, 40))
S.cam(t_f, (HD + V(0.2, -1.2, -0.1), HD + V(0, 0, -0.05), 40), (HD + V(0.18, -1.1, -0.1), HD + V(0, 0, -0.05), 40))
S.cam(t_g, (HD + V(0.55, -1.15, -0.05), HD + V(0.05, 0, -0.05), 38))
CW = HD + V(-0.75, 1.3, 0.35)                      # schuin achter hem: zijn silhouet, het lichtpuntje ver weg
S.cam(t_h, (CW, LP, 30))
S.cam(t_i, (HD + V(0.95, -1.15, -0.05), (HD + RAISE) * 0.5, 34), (HD + V(0.85, -1.0, -0.05), (HD + RAISE) * 0.5, 34))
CW2 = HD - DL * 5.0 + V(0, -1.6, 0.9)
S.cam(t_i2, (CW2, LP, 28), (CW2 + DL * 1.5, LP, 28))
S.cam(t_j, (HJ + V(1.15, -0.75, -0.08), HJ + V(0, 0, -0.08), 38), (HJ + V(1.02, -0.67, -0.08), HJ + V(0, 0, -0.08), 38))

# ---------------------------------------------------------------- stem (geen muziek)
S.say("D21-01", at=t_f + 0.3)
S.say("D21-02", at=t_g + 0.25)
S.say("D21-03", at=t_h + 1.7)
S.say("D21-04", at=t_i2 + 0.6)
S.say("D21-05", at=t_j + 0.35)
S.finish(length=END, tail=0.0)
