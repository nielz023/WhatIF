"""N15h · Dag 14: de jongen kijkt van een afstand naar het winkelcentrum (script scène 15h).
15h-1 CLOSE: de jongen kijkt. VO: "This part is real: scientists think humans work best in groups of about a hundred and
      fifty people. That's about... one street."
15h-2 WIDE van achter hem: klein figuurtje op het lege parkeerterrein, het koninkrijk in de verte.
15h-3 WIDE trage crane omhoog boven hem, de lucht wordt donker. VO: "But one thing was still missing. Light."

    blender -b -P anim/v3/scenes/n15h_afstand.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n15h", "koninkrijk", "ingang", exposure=-0.15)
sh = S.cuts([4.4, 4.6, 3.8])
END = sh[-1][1]
t_2, t_3 = sh[1][0], sh[2][0]

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

H = V(2.0, -32.0, 0)
held = S.actor("hoofdpersonage_kind", H, 180)                     # kijkt naar +y, naar het winkelcentrum
MALL = V(-1.0, 0.0, 3.0)
S.beat(held, 0.0, "staan", face="twijfel", face_amt=0.5, at=MALL)
S.beat(held, 2.2, "staan", face="vastberaden", face_amt=0.4, at=MALL + V(2, 0, 0))
A.blink_at(held, F(1.6))
S.beat(held, t_2 + 1.5, "staan", face="vastberaden", face_amt=0.5, at=MALL)
S.hold(held, END)

HH = S.headpos(held, 1.0)
S.cam(0.0, (HH + V(-0.35, 1.3, -0.05), HH + V(0, 0, -0.06), 32), (HH + V(-0.32, 1.18, -0.05), HH + V(0, 0, -0.06), 34))
S.cam(t_2, ((H.x + 0.8, H.y - 4.2, 1.2), MALL + V(0, 0, 0.5), 30), ((H.x + 0.7, H.y - 3.8, 1.2), MALL + V(0, 0, 0.5), 31))
S.cam(t_3, ((H.x + 0.6, H.y - 3.0, 1.6), MALL + V(0, 0, 2.0), 26), ((H.x + 0.4, H.y - 5.0, 7.5), MALL + V(0, 0, 4.0), 26))

S.counter("DAY 14", 6, t0=0.0)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.05)
S.music("m_nacht_angst", 0.0, END, vol=0.14, fade_in=0.4, fade_out=0.6)
S.say("N15-06", at=0.3)
S.say("N15-07", at=t_3 + 0.3)
S.finish(length=END, tail=0.0)
