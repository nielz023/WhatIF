"""N22a · Eindvraag: de keuken van het oude huis (script scène 22a).
22a  DETAIL trage push-in: op de koelkast hangt nog altijd het vergeelde vel HOUSE RULES uit scène 4. Onderaan heeft iemand
     een nieuwe regel bijgeschreven: 5. ALWAYS LISTEN TO OMA. VO N22-01.
(22b = de jongen als kind bij zijn raam uit scène 6: in de montage hergebruiken we 6b, met VO N22-02.)

    blender -b -P anim/v3/scenes/n22a_huisregels.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n22a", "keuken", "nr_oud", exposure=0.1)
sh = S.cuts([4.4])
END = sh[-1][1]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

HR = S.obj("HOUSE_RULES").matrix_world.translation.copy()
# trage push-in van het hele vel naar de onderste (nieuwe) regel
S.cam(0.0, ((1.63, 0.5, 1.15), HR + V(0.0, 0.0, 0.0), 38), ((1.76, 0.95, 1.02), HR + V(0.0, 0.0, -0.14), 48), handheld=0.05)

S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.08)
S.sfx("sfx_koelkast", 0.0, 0.08)
S.music("piano_zacht", 0.0, END, vol=0.16, fade_in=0.8, fade_out=0.3)
S.say("N22-01", at=0.4)
S.finish(length=END, tail=0.0)
