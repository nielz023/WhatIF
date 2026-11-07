"""D20a · Het einde van alles: de sterren gaan uit (script scène 20a-20d).
20a  WIDE heel trage drift 4 s: sterrenhemel, sterrenstelsels.  VO: "Here's the strangest part."
20a2 WIDE drift 4,5 s: de stelsels drijven uit elkaar tot de lucht bijna leeg is.
     VO: "First, the galaxies drift so far apart you can't see them anymore."
20b  WIDE 5 s: de sterren gaan één voor één uit, steeds sneller.  VO: "In about a hundred trillion years, the last stars in the universe burn out."
20c  CLOSE 4 s: zijn gezicht, verlicht door één laatste rood sterretje; hij steekt zijn hand ernaar uit.  VO: "Then the last one."
20d  CLOSE 2 s: het sterretje gaat uit. Zwart. Teller springt naar YEAR 10^100.

    python3 anim/v4/scenes/d20a_sterren.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d20a", "ruimte_nd", "sterren", exposure=0.1)
sh = S.cuts([3.0, 4.9, 5.1, 4.0, 2.2])
END = sh[-1][1]
t_a2, t_b, t_c, t_d = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker")

# stelsels drijven weg en krimpen
for o in [o for o in bpy.data.objects if o.name.startswith("Stelsel_") and o.parent is None]:
    p = o.location.copy()
    key(o, 0.0, loc=tuple(p), scale=tuple(o.scale))
    key(o, t_a2, loc=tuple(p), scale=tuple(o.scale))
    key(o, t_b, loc=tuple(p * 1.25), scale=tuple(o.scale * 0.02))
    show(o, 0.0, t_b)
# sterren uit, steeds sneller
mat = bpy.data.materials.get("Sterrenveld_mat")
node = None
if mat and mat.node_tree:
    node = next((n for n in mat.node_tree.nodes if n.label == "Sterren uit" or n.name == "Sterren uit"), None)
if node:
    sock = node.outputs[0]
    for t, v in ((0.0, 0.0), (t_b + 0.3, 0.0), (t_b + 2.5, 0.25), (t_b + 4.0, 0.7), (t_c, 1.0)):
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=F(t))
# het laatste rode sterretje gaat uit (20d)
ST = V(0.6, -14.0, 3.2)
emission_key("Laatste_ster_gloed", 0.0, 60.0)
emission_key("Laatste_ster_gloed", t_d + 0.6, 60.0)
emission_key("Laatste_ster_gloed", t_d + 0.9, 0.0)
lamp = bpy.data.objects.get("Laatste_ster_licht")
if lamp:
    for t, e in ((0.0, 900.0), (t_d + 0.6, 900.0), (t_d + 0.9, 0.0)):
        lamp.data.energy = e
        lamp.data.keyframe_insert("energy", frame=F(t))

# ---------------------------------------------------------------- hij, zwevend
held = S.actor("hoofdpersonage_rafels", (0.0, 0.0, 0.0), 0)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, at=V(-2, -20, 9))
S.beat(held, t_b, "staan", face="verdrietig", face_amt=0.4, at=V(2, -20, 12))
S.beat(held, t_c, "staan", face="verdrietig", face_amt=0.5, at=ST)
HD = S.headpos(held, t_c + 0.5)
SH = S.bone_world(held, "upper_arm.R", t_c + 0.5, tail=False) if "upper_arm.R" in held.rig.pose.bones else HD + V(-0.25, 0, -0.45)
REACH = SH + (ST - SH).normalized() * 0.42
S.reach(held, t_c + 1.0, "R", None, 0.0)
S.reach(held, t_c + 2.4, "R", REACH)
S.reach(held, END, "R", REACH)
S.beat(held, t_d + 0.9, "staan", face="bang", face_amt=0.5, at=ST)
S.hold(held, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(1.0, 1.9, 1.9), V(-2, -20, 12), 20), (V(0.95, 1.8, 1.9), V(-2.2, -20, 12.3), 20))
S.cam(t_a2, (V(1.0, 1.9, 1.9), V(-2, -20, 12), 20), (V(1.2, 2.5, 2.2), V(-2, -20, 12), 18))
S.cam(t_b, (V(-3.0, 4.0, 2.0), V(1.0, -20, 6), 22), (V(-2.8, 3.6, 1.9), V(1.0, -20, 6), 22))
S.cam(t_c, (V(0.1, -2.3, 1.5), HD, 45), (V(0.1, -2.0, 1.5), HD, 45))
S.cam(t_d, (V(0.1, -2.0, 1.5), HD, 45))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year([(0.0, "100T"), (t_d + 1.0, "googol")], t0=0.0, big=True)
S.jump(0.0)
S.say("D20-01", at=0.3)
S.say("D20-02", at=t_a2 + 0.2)
S.say("D20-03", at=t_b + 0.2)
S.say("D20-04", at=t_c + 0.6)
S.music("cello", 0.0, END, vol=0.12, fade_in=1.0, fade_out=0.8)
S.ticks(0.5, END, every=1.0, vol=0.15)
S.finish(length=END, tail=0.0)
