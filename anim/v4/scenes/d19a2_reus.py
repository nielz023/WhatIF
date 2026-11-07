"""D19a2 · De rode reus van hoog (script scène 19a2).
19a2 WIDE trage crane 4 s: de rode zon over de horizon, de aarde als een klein zwart bolletje ervoor.
     VO: "And it might swallow the Earth whole."

    python3 anim/v4/scenes/d19a2_reus.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d19a2", "ruimte_nd", "rode_reus", exposure=0.1)
sh = S.cuts([3.4])
END = sh[-1][1]
S.hide("Personage_marker", "Character_marker")
aarde = bpy.data.objects.get("Aarde_silhouet")
if aarde:                                                   # de aarde schuift langzaam naar de rand van de zon
    key(aarde, 0.0, loc=(-6.0, 260.0, 4.0))
    key(aarde, END, loc=(-4.0, 262.0, 2.5))
S.cam(0.0, (V(-12.0, -320.0, 60.0), V(0, 1000, 0), 24), (V(-12.0, -300.0, 30.0), V(0, 1000, 0), 24))
S.year(5000000000, t0=0.0, tick=False)
S.say("D19-02", at=0.2)
S.ambience("sfx_zon_gebrul", 0.0, END, vol=0.12)
S.music("subbas", 0.0, END, vol=0.14, fade_in=0.0, fade_out=0.0)
S.finish(length=END, tail=0.0)
