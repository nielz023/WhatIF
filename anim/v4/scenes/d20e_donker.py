"""D20e · Eén googol jaar: het totale zwart (script scène 20e-20g).
20e  ZWART 4 s: totaal zwart, alleen de tik, heel zacht.  VO: "One googol years. A one... with a hundred zeros."
20f  ZWART met een zweem randlicht 4 s: zijn silhouet net zichtbaar door een heel zwakke blauwe rand.
     VO: "No stars. No planets. No light. No one."
20g  ZWART 3 s: VO "Just you. Forever."  Daarna 2 s volledige stilte; de teller verdwijnt.

    python3 anim/v4/scenes/d20e_donker.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d20e", "ruimte_nd", "donker", exposure=0.1)
sh = S.cuts([5.2, 4.9, 4.5])
END = sh[-1][1]
t_f, t_g = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker", "Zakhorloge", "Horloge_gloed", "Lichtpuntje")

# alles uit, behalve de blauwe rand in 20f
for o in [o for o in bpy.data.objects if o.type == "LIGHT"]:
    e = o.data.energy
    ks = ((0.0, 0.0), (t_f, 0.0), (t_f + 0.8, e), (t_g - 0.3, e), (t_g, 0.0)) if o.name == "Blauwe_rand" else ((0.0, 0.0),)
    for t, v in ks:
        o.data.energy = v
        o.data.keyframe_insert("energy", frame=F(t))
wd = bpy.context.scene.world
for n in ([n for n in wd.node_tree.nodes if n.type == "BACKGROUND"] if wd and wd.node_tree else []):
    n.inputs["Strength"].default_value = 0.0
    n.inputs["Strength"].keyframe_insert("default_value", frame=F(0.0))

held = S.actor("hoofdpersonage_rafels", (0.0, 0.0, 0.0), 0)
S.qc_skip.add(held.name)                         # bewust (bijna) onzichtbaar
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.4, look=(0.0, -0.3))
S.beat(held, t_f + 1.0, "staan", face="verdrietig", face_amt=0.6, look=(0.2, -0.4), body={"head": (8, 0, -4)})
A.blink_at(held, F(t_f + 2.6))
S.hold(held, END)
HD = S.headpos(held, t_f + 1.0)

S.cam(0.0, (V(0.3, -3.2, 1.3), HD + V(0, 0, -0.35), 30))
S.cam(t_f, (HD + V(0.9, -2.1, 0.0), HD + V(0, 0, -0.3), 32), (HD + V(0.8, -1.85, 0.0), HD + V(0, 0, -0.3), 32))
S.cam(t_g, (V(0.3, -3.2, 1.3), HD + V(0, 0, -0.35), 30))

S.year([(0.0, "googol")], t0=0.0, t1=t_g + 2.6, tick=False)
S.say("D20-06", at=0.35)
S.say("D20-07", at=t_f + 0.3)
S.say("D20-08", at=t_g + 0.3)
S.ticks(0.6, t_g, every=1.0, vol=0.08)          # heel zacht; daarna 2 s volledige stilte
S.music("cello", 0.0, t_g, vol=0.06, fade_in=0.5, fade_out=1.2)
S.finish(length=END, tail=0.0)
