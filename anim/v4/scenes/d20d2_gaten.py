"""D20d2 · De zwarte gaten verdampen (script scène 20d2).
20d2 WIDE trage drift 5 s: in het zwart alleen zwarte gaten als dunne gloeiende ringen; één voor één verdampen ze
     in een zwakke flits.  VO: "Then, very slowly, even the black holes evaporate."

    python3 anim/v4/scenes/d20d2_gaten.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d20d2", "ruimte_nd", "zwarte_gaten", exposure=0.1)
sh = S.cuts([5.0])
END = sh[-1][1]
S.cine_light = False                              # geen key-/randlicht: alleen het licht uit de scène zelf
S.hide("Personage_marker", "Character_marker")

# een voor een verdampen: ring flitst kort op en dooft, het gat krimpt weg
gaten = sorted([o for o in bpy.data.objects if o.name.startswith("Zwart_gat_") and o.parent is None and o.type == "EMPTY"],
               key=lambda o: o.location.x)
T0 = [1.0, 1.9, 2.6, 3.2, 3.7]
for k, g in enumerate(gaten):
    t = T0[k % len(T0)]
    m = g.name + "_ring"
    emission_key(m, 0.0, 10.0, interp="LINEAR")
    emission_key(m, t - 0.1, 10.0, interp="LINEAR")
    emission_key(m, t + 0.08, 28.0, interp="LINEAR")
    emission_key(m, t + 0.45, 0.0, interp="LINEAR")
    s = tuple(g.scale)
    key(g, 0.0, scale=s)
    key(g, t, scale=s)
    key(g, t + 0.45, scale=tuple(x * 0.02 for x in s))
    show(g, 0.0, t + 0.5)
    S.sfx("sfx_glitch", t + 0.05, 0.05)

# hij zweeft als klein silhouet op de voorgrond, met zijn rug naar ons
held = S.actor("hoofdpersonage_rafels", (0.9, -3.2, 0.0), 180, rim=False)
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.4, at=V(0, 300, 10))
S.hold(held, END)

S.cam(0.0, (V(0, -6.0, 1.5), V(0, 300, 10), 24), (V(0.15, -5.6, 1.5), V(0, 300, 12), 24))

S.year([(0.0, "googol")], t0=0.0, tick=False)
S.say("D20-05", at=0.3)
S.music("cello", 0.0, END, vol=0.10, fade_in=0.3, fade_out=0.8)
S.ticks(0.5, END, every=1.0, vol=0.12)
S.finish(length=END, tail=0.0)
