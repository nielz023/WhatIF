"""N22c · Slotbeeld: zonsopgang boven het plein (script scène 22c-22d).
22c  WIDE trage pull-back: de zon komt op boven het plein, alle rode schermen gaan tegelijk uit. Stilte. Dan licht nog één
     telefoon op, in de hand van de jongen. Hij kijkt ernaar, zijn duim beweegt er langzaam naartoe. VO N22-03.
22d  Zwart, 2 s: harde cut naar zwart voordat we het scherm zien. Driftmark-logo (in de montage). Geen verwijzing naar een
     volgende video.

    blender -b -P anim/v3/scenes/n22c_zonsopgang.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n22c", "stadsplein", "middernacht", exposure=0.2, night=True)
sh = S.cuts([3.3, 2.7, 2.0])
END = sh[-1][1]
t_c2, t_d = sh[1][0], sh[2][0]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True
for key in ("test", "result", "phase"):
    for scr in ("Scherm_1", "Scherm_2", "Scherm_3"):
        g = S.obj(f"{scr}_tekst_{key}")
        for o in [g] + list(g.children):
            o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de schermen gaan tegelijk uit
T_OFF = 1.3
for i in (1, 2, 3):
    emission_key(f"Scherm_{i}_licht", 0.0, 2.6)
    emission_key(f"Scherm_{i}_licht", T_OFF, 0.0)
    lt = S.obj(f"Scherm_{i}_rood_schijnsel")
    if lt is not None:
        light_key(lt, 0.0, lt.data.energy)
        light_key(lt, T_OFF, 0.0)

# ---------------------------------------------------------------- de zon komt op (zuid, achter de horizonstreep)
SUN = T.sphere("Zon_opkomst", (0, -240, 2), 9.0, S.mat("zon_oranje", (1.0, 0.62, 0.25), 12.0), seg=24, ol=0)
for t, z in ((0.0, -4.0), (END, 9.0)):
    SUN.location.z = z
    SUN.keyframe_insert("location", index=2, frame=F(t))
sl = bpy.data.lights.new("Zonlicht_opkomst", "SUN")
sl.color = (1.0, 0.72, 0.45)
so = bpy.data.objects.new(sl.name, sl)
S.sc.collection.objects.link(so)
so.rotation_euler = (math.radians(82), 0, 0)               # laag uit het zuiden
light_key(so, 0.0, 0.0, interp="LINEAR")
light_key(so, END, 3.2, interp="LINEAR")
# dageraad: een warme gloed laag aan de zuidelijke horizon, achter de zon (wordt sterker terwijl de zon opkomt)
GLOW = T.box("Dageraad_gloed", (0, -236, -6), (520, 0.5, 46), S.mat("dageraad_gloed", (1.0, 0.45, 0.16), 0.0), bevel=0, ol=0)
GLOW.visible_shadow = False
emission_key("dageraad_gloed", 0.0, 0.4, interp="LINEAR")
emission_key("dageraad_gloed", 6.0, 3.0, interp="LINEAR")
GLOW2 = T.box("Dageraad_gloed_hoog", (0, -238, 40), (520, 0.5, 70), S.mat("dageraad_gloed_hoog", (0.95, 0.55, 0.45), 0.0), bevel=0, ol=0)
GLOW2.visible_shadow = False
emission_key("dageraad_gloed_hoog", 0.0, 0.1, interp="LINEAR")
emission_key("dageraad_gloed_hoog", 6.0, 0.9, interp="LINEAR")

# ---------------------------------------------------------------- de jongen met zijn telefoon
TC = V(0.0, 4.0, 0)
H = V(math.cos(0.2) * 2.15 + 0.5, 4 + math.sin(0.2) * 2.15 - 0.9, 0)
held = S.actor("hoofdpersonage_volwassen", H, 0)            # kijkt naar het zuiden, de zon in
phone = T.box("Telefoon_slot", (0, 0, 0), (0.08, 0.012, 0.15), S.mat("telefoon_zwart", (0.05, 0.05, 0.06)), bevel=0.01, ol=0.002)
scr = T.box("Telefoon_slot_scherm", (0, -0.007, 0.005), (0.07, 0.002, 0.13), S.mat("telefoon_slot_licht", (0.9, 0.95, 1.0), 0.0), bevel=0, ol=0)
scr.parent = phone
grab(S, phone, held, 0.0, "hand.R", loc=(0.0, 0.0, -0.05), rot=(80, 0, 0))
T_PH = 3.3
emission_key("telefoon_slot_licht", 0.0, 0.0)
emission_key("telefoon_slot_licht", T_PH, 6.0)
HH = S.headpos(held, 0.0)
LOW = H + V(-0.28, -0.05, 0.75)
UP_ = HH + V(-0.12, -0.32, -0.35)
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(0, -240, 4))
S.reach(held, 0.0, "R", LOW)
S.reach(held, T_PH + 0.2, "R", LOW)
S.reach(held, T_PH + 1.0, "R", UP_)
S.reach(held, END, "R", UP_)
S.beat(held, 1.6, "staan", face="blij", face_amt=0.3, at=V(0, -240, 4))
S.beat(held, T_PH + 0.2, "staan", face="verbaasd", face_amt=0.5, at=LOW)
S.beat(held, T_PH + 1.0, "staan", face="nerveus", face_amt=0.4, at=UP_)
# de duim (linkerhand) beweegt langzaam naar het scherm
S.reach(held, 0.0, "L", inf=0.0)
S.reach(held, T_PH + 1.6, "L", inf=0.0)                     # korte overgang: anders hangt de arm halverwege
S.reach(held, T_PH + 1.9, "L", UP_ + V(0.1, -0.06, 0.02))
S.reach(held, t_d, "L", UP_ + V(0.05, -0.05, 0.03))
S.hold(held, END)

# ---------------------------------------------------------------- camera: trage pull-back, dan zwart
# 22c1 schuin achter hem, de opkomende zon in: hij als silhouet tegen de dageraad, de schermen gaan uit
S.cam(0.0, (H + V(1.25, 1.9, 1.55), H + V(-0.35, -4.0, 1.25), 30), (H + V(1.9, 3.3, 2.0), H + V(-0.35, -5.0, 1.15), 29))
# 22c2 van voren, warm zonlicht op zijn gezicht: de telefoon licht op, zijn duim beweegt ernaartoe; trage pull-back
S.cam(t_c2, ((2.4, -0.6, 1.75), HH + V(0, 0, -0.25), 32), ((3.2, -2.6, 2.1), HH + V(0, 0, -0.2), 30))
S.black(t_d, END, "")

# ---------------------------------------------------------------- geluid, stem
S.ambience("sfx_dageraad_straat", T_OFF + 0.3, t_d, vol=0.06)
S.sfx("sfx_stroom_thunk", T_OFF, 0.3)
S.sfx("sfx_meldingen", T_PH, 0.12)
S.music("piano_zacht", T_PH - 0.5, t_d, vol=0.14, fade_in=1.0, fade_out=0.05)
S.say("N22-03", at=2.2)
S.finish(length=END, tail=0.0)
