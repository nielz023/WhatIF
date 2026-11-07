"""D22a · Flashback: opa's doosje (script scène 22a). Keuken 2026, geen HUD.
22a  DETAIL trage push-in 4 s: de verjaardagstafel; opa klikt het doosje open, het horloge glanst.
     VO: "So... would you take it? Living forever, if this is how it ends?"

    python3 anim/v4/scenes/d22a_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d22a", "keuken", "nd_verjaardag", exposure=0.2)
sh = S.cuts([4.6])
END = sh[-1][1]
S.no_hud.append((0.0, END + 2.0))

TX, TY, TZ = 0.2, -0.6, 0.76
BY = TY + 0.62
HERO_AT, OPA_AT = V(TX, BY, 0), V(TX + 0.72, BY, 0)
achter = sorted([o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")
                 and o.location.y > TY], key=lambda o: o.location.x)
for o in [o for o in bpy.data.objects if o.name.startswith("Stoel") and not o.name.startswith("Stoel_kop")]:
    if o.location.y < TY - 0.3:
        o.hide_render = o.hide_viewport = True
for o, x in zip(achter, (TX - 0.72, HERO_AT.x, OPA_AT.x)):
    o.location.x = x
taart = S.obj("Verjaardagstaart")
taart.location = (HERO_AT.x, TY + 0.0, TZ)
for o in bpy.data.objects:
    if o.name.startswith("Verjaardagstaart_vlam") or o.name.startswith("Verjaardagstaart_kaarslicht"):
        o.hide_render = o.hide_viewport = True                 # kaarsjes zijn al uitgeblazen
    if o.name.startswith("Taartbordje_") and abs(o.location.x - TX) < 0.05:
        o.hide_render = o.hide_viewport = True
bpy.context.view_layer.update()

held = S.actor("hoofdpersonage_kind", HERO_AT, 0)
opa = S.actor("opa", OPA_AT, 0, drop=("wandelstok",))
SEAT = {}
for ch, at in ((held, HERO_AT), (opa, OPA_AT)):
    spec, z = sit(ch)
    SEAT[ch] = spec
    S.place(ch, 0, at + V(0, 0, z), 0)
H_HEAD = S.head(held)

BOX = V(HERO_AT.x + 0.22, TY + 0.36, TZ)
doos = ND.horlogedoosje("Horlogedoosje", tuple(BOX), rot_z=180)
dek = S.obj("Horlogedoosje_deksel")
in_doos = ND.zakhorloge("Zakhorloge_doos", (0, 0, 0), open_=0.95, ketting=False)
in_doos.parent = doos
in_doos.location = (0.004, -0.01, 0.034)
in_doos.rotation_euler = (0, 0, math.radians(180))
T_OPEN = 1.6
for t, v in ((0.0, 0.0), (T_OPEN, 0.0), (T_OPEN + 0.35, 1.0)):
    dek.rotation_euler.x = -math.radians(105) * v
    dek.keyframe_insert("rotation_euler", index=0, frame=F(t))

# opa klikt het doosje open
S.beat(opa, 0.0, **SEAT[opa], face="blij", face_amt=0.8, at=BOX)
S.reach(opa, 0.0, "R", None, 0.0)
S.reach(opa, 0.8, "R", BOX + V(0.06, -0.03, 0.09))
S.reach(opa, T_OPEN + 0.3, "R", BOX + V(0.04, -0.06, 0.13))
S.reach(opa, T_OPEN + 1.2, "R", None, 0.0)
S.beat(opa, T_OPEN + 1.0, **SEAT[opa], face="blij", face_amt=1.0, at=H_HEAD)
S.beat(held, 0.0, **SEAT[held], face="verbaasd", face_amt=0.6, at=BOX)
S.beat(held, T_OPEN + 0.4, **SEAT[held], face="verbaasd", face_amt=1.0, at=BOX, ogen_wijd=0.5)
for ch in (held, opa):
    S.hold(ch, END + 2.0)

S.cam(0.0, (BOX + V(0.38, -0.5, 0.3), BOX + V(0, 0, 0.04), 45), (BOX + V(0.32, -0.42, 0.26), BOX + V(0, 0, 0.04), 45))

S.say("D22-01", at=0.3)
S.sfx("sfx_doosje_klik", T_OPEN + 0.3, 0.3)
S.music("m_vredig_klok", 0.0, END, vol=0.08, fade_in=0.6, fade_out=1.0)
S.finish(length=END, tail=0.0)
