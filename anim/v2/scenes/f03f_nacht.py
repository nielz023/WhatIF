"""F03f · Dag 1 · 1x · slaapkamer, 's nachts. Hij doet het lampje uit, de HUD flikkert en dooft.
'At eleven, you fall asleep. For the last time as a normal kid.'

    blender -b -P anim/v2/scenes/f03f_nacht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f03f", "slaapkamer", "nacht")

LIE_AT = V(-1.38, 0.1, 0.4)                      # zoals in F02: voeten naar het voeteneinde, hoofd in het kussen
LAMP = S.obj("Leeslamp")
LAMP_P = LAMP.matrix_world.translation + V(0, 0, 0.3)
for nm in ("Telefoon_scherm", "Telefoon_gloed"):
    S.obj(nm).hide_render = True
for o in bpy.data.objects:
    if o.name.startswith("Dekbed_bobbel"):
        o.hide_render = True
T.box("Dekbed_over_hem", (-1.47, 0.36, 0.44), (1.12, 1.6, 0.47), S.obj("Dekbed_blauw").active_material, bevel=0.14, ol=0)

held = S.actor("hoofdpersonage", LIE_AT, 0)
held.rig.location, held.rig.rotation_euler = LIE_AT, (math.radians(-75), 0, 0)
for p in ("location", "rotation_euler"):
    held.rig.keyframe_insert(p, frame=F(0))

# het leeslampje: warm licht tot de klik
lamp_l = T.point_light("Leeslamp_licht", LAMP_P + V(0, 0, -0.08), color=(1.0, 0.72, 0.42), energy=45, radius=0.08)
glow = T.sphere("Leeslamp_peer", LAMP_P + V(0, 0, -0.1), 0.035, T.glow("leeslamp_peer", (1.0, 0.8, 0.5), 8), seg=10, ol=0)

# ---------------------------------------------------------------- tijdlijn
CLICK = 1.3
l1 = S.say("F03-15", gap=CLICK + 0.7)
END = l1[1] + 1.6
FLICK = l1[1] - 1.9                              # 'for the last time as a normal kid': de HUD hapert
OUT = l1[1] + 0.2
S.sfx("sfx_lichtknop", CLICK, 0.5)
S.music("strijkers_warm", 0.0, END, vol=0.16, fade_in=1.0, fade_out=1.5, start=12.0)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.05)
S.sfx("sfx_hud_tik", FLICK, 0.35)
S.sfx("sfx_hud_tik", FLICK + 0.55, 0.25)
S.card("", OUT + 0.6, END + 0.5, dim=1.0, fin=round(0.8 * 24), fout=1)

lamp_l.data.energy = 45
lamp_l.data.keyframe_insert("energy", frame=F(CLICK))
lamp_l.data.energy = 0
lamp_l.data.keyframe_insert("energy", frame=F(CLICK) + 1)
for fc in A._fcurves(lamp_l.data):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
show(glow, 0.0, CLICK + 1 / 24)

# HUD: 22:59:5x tikt naar 23:00, dan flikkert hij en gaat uit (eigen tekstregels, geen pop-in)
segs = [(0.3, FLICK), (FLICK + 0.08, FLICK + 0.2), (FLICK + 0.32, FLICK + 0.36), (FLICK + 0.5, FLICK + 1.1), (FLICK + 1.2, FLICK + 1.25),
        (FLICK + 1.4, OUT)]
clk = clock(22 * 3600 + 59 * 60 + 48, 1.0, day="MON", t0=0.0)
for k, (a, b) in enumerate(segs):
    S.texts.append(dict(body="DAY 1  ·  1x", t0=a, t1=b, loc=(0.965, 0.94), size=78, color=HUD_W, anchor=("RIGHT", "TOP"),
                        pop=(k == 0), hud=True))
    S._ticking(clk, a + (0.1 if k == 0 else 0.0), b, (0.965, 0.855), 54, HUD_CLOCK, 1 / 24)
S.sfx("sfx_hud_tik", 0.3, 0.5)

# ---------------------------------------------------------------- hij: lampje uit, ogen dicht
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=LAMP_P)
S.reach(held, 0.4, "L", None, 0.0)
S.reach(held, 0.9, "L", LAMP_P + V(-0.06, -0.05, -0.12))
S.reach(held, CLICK + 0.05, "L", LAMP_P + V(-0.04, -0.04, -0.14))
S.reach(held, CLICK + 0.7, "L", None, 0.0)
S.beat(held, CLICK + 0.6, "staan", face="neutraal", face_amt=0.3, look=(0, 0.3), body={"head": (-6, 0, 0)})
S.beat(held, l1[0] + 1.0, "staan", face="blij", face_amt=0.25, look=(0, 0.3), body={"head": (-4, 8, 0)})
S.eyes_closed(held, l1[0] + 2.2, END + 1)
S.hold(held, END)

# ---------------------------------------------------------------- camera
HH = LIE_AT + V(0, 1.42, 0.38)                   # zijn hoofd in het kussen
S.cam(0.0, ((0.2, -0.6, 1.45), (-1.05, 1.15, 0.7), 28), ((0.1, -0.45, 1.4), (-1.05, 1.15, 0.7), 30))
S.cam(l1[0] + 0.8, (HH + V(0.45, -0.75, 0.85), HH + V(0, -0.05, 0.05), 38), (HH + V(0.38, -0.62, 0.72), HH + V(0, -0.05, 0.05), 42), dof=1.4)   # gezicht kijkt omhoog

S.finish(length=END)
