"""N20a · Jaar 10: de stadsraad op het plein, avond (script scène 20a-20f).
20a  WIDE trage crane: tijdsprongkaart 10 YEARS LATER. Het plein vol borden met regels, de ronde tafel van de stadsraad,
     lampjes aan. De teller rolt naar 48,000+.
20b  MEDIUM push-in: de jongen, nu volwassen, aan de tafel tussen de wetenschapper en de oud-pestkop. Hij tikt met zijn pen
     op het papier, kijkt op en glimlacht naar de oud-pestkop.
20c  CLOSE: de jongen. VO N20-01.
20d  WIDE: het broertje (tiener) met het oude hondje over het plein, papa en mama zwaaien vanaf een bankje. VO N20-02.
20e  CLOSE: de jongen kijkt naar het grote bord; insert: 1. NOBODY GOES HUNGRY (oma's handschrift). VO N20-03.
20f  DETAIL: de klok aan de raadszaal, 23:59:58... 59. Alles valt weg tot het tikken.

    blender -b -P anim/v3/scenes/n20a_raad.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n20a", "stadsplein", "jaar10", exposure=0.15)
CARD = 1.3
sh = S.cuts([CARD, 4.0, 3.5, 3.6, 4.0, 2.2, 2.4, 3.0])
END = sh[-1][1]
t_a, t_b, t_c, t_d, t_e, t_e2, t_f = [s[0] for s in sh[1:]]
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

TC = V(0.0, 4.0, 0)                      # midden van de raadstafel
BOARD1 = V(-2.4, 11.95, 4.9)             # regel 1 bovenaan het grote bord


def chair(k, r=2.15):
    a = k / 7 * math.tau + 0.2
    return V(math.cos(a) * r, 4 + math.sin(a) * r, 0)


def seat(name, k, r=2.15, **kw):
    p = chair(k, r)
    d = TC - p
    ch = S.actor(name, p, math.degrees(math.atan2(d.x, -d.y)), **kw)
    spec, z = sit(ch, seat_top=0.46)
    ch.rig.location.z = z
    ch.rig.keyframe_insert("location", frame=1)
    ch.spec = spec
    return ch


# ---------------------------------------------------------------- de stadsraad
# de jongen schuift aan tot tegen de tafel (korte armen): stoel, papier en pen mee naar binnen
held = seat("hoofdpersonage_volwassen", 0, r=1.95)
for _n, _dr in (("Raadsstoel_0", -0.2), ("Papier_0", 0.18), ("Pen_jongen", 0.18)):
    _o = S.obj(_n)
    if _o is not None:
        _o.location += V(math.cos(0.2), math.sin(0.2), 0) * _dr
pest = seat("pestkop_volwassen", 6)
wet = seat("wetenschapper", 2)
male_scientist(S, wet)
oma = seat("oma", 3)
buur = seat("buurman", 4)
ag = seat("agent", 5, drop=("agent_badge",))
HH = S.headpos(held, 0.0)
for i, ch in enumerate((pest, wet, oma, buur, ag)):
    for j, t in enumerate(frange(0.0, END, 1.5 + 0.2 * i)):
        tgt = S.headpos(held, 0.0) if (i + j) % 2 else TC + V(0, 0, 0.8)
        S.beat(ch, t, face="blij" if j % 2 else "neutraal", face_amt=0.5, at=tgt, **ch.spec)
    S.hold(ch, END)

# de jongen tikt met zijn pen op het papier, kijkt op en glimlacht naar de oud-pestkop
pen = S.obj("Pen_jongen")
PAPER = V(math.cos(0.2) * 1.43, 4 + math.sin(0.2) * 1.43, 0.81)
grab(S, pen, held, 0.0, "hand.R", loc=(0.0, 0.0, -0.04), rot=(90, 0, 0))
S.beat(held, 0.0, face="neutraal", face_amt=0.5, at=PAPER, body={"spine": (16, 0, 0)}, **held.spec)
for k, t in enumerate(frange(0.0, t_b + 1.4, 0.32)):
    S.reach(held, t, "R", PAPER + V(0.05, 0.12, 0.1 if k % 2 else 0.03))
# hij kijkt naar -x: zijn rechterhand is de +y-kant; na het tikken rusten beide handen vlak bij de tafelrand
S.reach(held, t_b + 1.7, "R", PAPER + V(0.15, 0.14, 0.08))
S.reach(held, END, "R", PAPER + V(0.15, 0.14, 0.08))
S.reach(held, 0.0, "L", PAPER + V(0.18, -0.22, 0.03))
S.reach(held, END, "L", PAPER + V(0.18, -0.22, 0.03))
S.beat(held, t_b + 1.6, face="neutraal", face_amt=0.4, at=S.headpos(pest, t_b), **held.spec)
S.beat(held, t_b + 2.2, face="blij", face_amt=0.7, at=S.headpos(pest, t_b), **held.spec)
S.beat(pest, t_b + 2.4, face="blij", face_amt=0.7, at=HH, **pest.spec)
S.beat(held, t_c + 0.3, face="zelfverzekerd", face_amt=0.4, look=(0.0, 0.0), **held.spec)
A.blink_at(held, F(t_c + 1.6))
# 20e: hij kijkt naar het grote bord
S.beat(held, t_e - 0.1, face="neutraal", face_amt=0.4, at=BOARD1, **held.spec)
S.beat(held, t_e + 1.0, face="blij", face_amt=0.5, at=BOARD1, **held.spec)
S.hold(held, END)
S.hold(pest, END)

# ---------------------------------------------------------------- 20d: het broertje met het oude hondje, papa en mama op het bankje
bro = S.actor("broertje_tiener", V(6.0, -1.4, 0), -90)
B0, B1 = V(6.0, -1.4, 0), V(1.6, -1.2, 0)
S.walk(bro, t_d - 0.6, END, [B0, B1 + (B1 - B0) * 0.4], stride=0.5)
S.beat(bro, t_d, "staan", face="blij", face_amt=0.6, at=V(11.5, 6.0, 1.0), feet="keep")
hond = animal(S, "hondje", V(5.2, -1.8, 0), -90)
animal_path(hond, t_d - 0.6, END, [V(5.2, -1.8, 0), V(0.2, -1.6, 0)], action="hond_loop", speed=0.7)
leash(S, bro, hond, 0.0, END)
BANK = V(11.5, 6.0, 0)
for n, dy, side in (("papa_grijs", -0.42, "R"), ("mama_grijs", 0.42, "L")):
    ch = S.actor(n, BANK + V(0.05, dy, 0), -90)
    spec, z = sit(ch, seat_top=0.45)
    ch.rig.location.z = z
    ch.rig.keyframe_insert("location", frame=1)
    S.beat(ch, 0.0, face="blij", face_amt=0.6, at=S.headpos(bro, t_d + 1.5), **spec)
    for k, t in enumerate(frange(t_d + 0.3, t_e, 0.3)):
        S.beat(ch, t, pose="zwaaien_a" if k % 2 else "zwaaien_b", face="lach", face_amt=0.8, at=S.headpos(bro, t), **spec)
    S.hold(ch, END)
S.beat(bro, t_d + 1.2, "zwaaien_a", amount=0.6, face="lach", face_amt=0.7, at=BANK + V(0, 0, 1.0), feet="keep")
S.beat(bro, t_d + 2.6, "staan", face="blij", face_amt=0.6, at=BANK + V(0, 0, 1.0), feet="keep")
S.hold(bro, END)

# ---------------------------------------------------------------- 20f: de klok, 23:59:58 ... 59
sec = S.obj("Raadsklok_seconde")
sec.rotation_mode = "XYZ"
for t, s in ((0.0, 58), (t_f + 1.3, 58), (t_f + 1.36, 59.15), (t_f + 1.42, 59)):
    sec.rotation_euler.y = math.radians(s * 6)
    sec.keyframe_insert("rotation_euler", index=1, frame=F(t))

# ---------------------------------------------------------------- camera's
S.black(0.0, CARD, "10 YEARS LATER")
S.cam(0.0, ((8.0, -24.0, 9.0), (0.0, 5.0, 1.2), 24))
# 20a WIDE trage crane omlaag over het plein
S.cam(t_a, ((8.0, -24.0, 9.0), (0.0, 5.0, 1.2), 24), ((6.0, -13.0, 3.4), (0.0, 5.0, 1.4), 24))
# 20b MEDIUM push-in: over de tafel naar de jongen
S.cam(t_b, ((-0.9, 3.9, 1.35), HH + V(0, 0, -0.15), 28), ((-0.4, 3.95, 1.3), HH + V(0, 0, -0.12), 30))
# 20c CLOSE de jongen
HC = S.headpos(held, t_c + 1.5)
S.cam(t_c, ((0.85, HC.y - 0.2, HC.z + 0.06), HC + V(0, 0, 0.03), 30), ((0.95, HC.y - 0.18, HC.z + 0.06), HC + V(0, 0, 0.03), 31))
# 20d WIDE: het broertje met de hond, papa en mama op het bankje
S.cam(t_d, ((16.0, -4.0, 2.2), (8.3, 2.4, 0.9), 20), ((15.6, -3.8, 2.2), (8.0, 2.4, 0.9), 20))
# 20e CLOSE: de jongen kijkt naar het bord; insert regel 1
dB = (BOARD1 - HH)
dB.z = 0
dB.normalize()
S.cam(t_e, (HH + dB * 1.3 + V(0, 0, 0.05), HH + V(0, 0, -0.03), 32), (HH + dB * 1.15 + V(0, 0, 0.05), HH + V(0, 0, -0.03), 34))
S.cam(t_e2, ((0.5, 8.5, 3.2), BOARD1 + V(0.9, 0, -0.1), 40), ((0.2, 9.0, 3.5), BOARD1 + V(0.9, 0, -0.1), 46))
# 20f DETAIL de klok
S.cam(t_f, ((0.0, 15.0, 9.6), (0.0, 22.85, 10.0), 45), ((0.0, 16.0, 9.75), (0.0, 22.85, 10.0), 52))

# ---------------------------------------------------------------- HUD, geluid, stem
S.rolling("YEAR 10", 6300, 48000, t_a + 0.4, 2.4, t1=t_f)
S.ambience("sfx_krekels_nacht", t_a, t_f, vol=0.05)
S.ambience("sfx_menigte_mompel", t_a, t_e2, vol=0.04)
S.music("strijkers_emo", t_a, t_f - 0.2, vol=0.18, fade_in=0.6, fade_out=0.8)
S.sfx("sfx_klok_tik", t_f + 0.3, 0.5)
S.sfx("sfx_klok_tik", t_f + 1.3, 0.5)
S.say("N20-01", at=t_c + 0.0)
S.say("N20-02", at=t_d + 1.4)
S.say("N20-03", at=t_e2 + 0.3)
S.finish(length=END, tail=0.0)
