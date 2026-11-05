"""N21b · Middernacht, precies 10 jaar later (script scène 21b-21k). Stadsplein, nacht, alle schermen rood.
(21a = exact hetzelfde shot als 5c: in de montage hergebruiken we de render van n05c.)
21b  CLOSE: de jongen (volwassen) schrikt op aan de tafel, zijn telefoon licht rood op (zelfde schrik als 5a).
21c  WIDE trage push: het hele plein staat stil en kijkt naar het scherm (ademhaling, één keer knipperen).
21d  DETAIL push-in: TEST COMPLETE. verschijnt letter voor letter, een tik per letter.
21e  CLOSE: de jongen leest, zijn lippen bewegen mee.
21f  DETAIL: RESULT: HUMANS CREATE NEW RULES WITHIN 9 DAYS.
21g  CLOSE: de wetenschapper naast hem fluistert: "Test? Whose test?" (N21-01)
21h  DETAIL push-in: PHASE 2 BEGINS AT SUNRISE. Het alarm stopt in één klap, 2 s stilte.
21i  WIDE trage pull-back: het plein rood verlicht, aan de horizon de eerste blauwe streep van de ochtend. VO N21-02.
21j  CLOSE: de jongen kijkt naar de horizon.
21k  CLOSE push-in: VO N21-03.

    blender -b -P anim/v3/scenes/n21b_middernacht.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n21b", "stadsplein", "middernacht", exposure=0.1, night=True)
sh = S.cuts([2.5, 4.0, 4.0, 3.0, 4.0, 3.0, 4.0, 5.0, 4.0, 4.0])
END = sh[-1][1]
t_c, t_d, t_e, t_f, t_g, t_h, t_i, t_j, t_k = [s[0] for s in sh[1:]]
rnd = random.Random(21)
bpy.context.view_layer.update()

for o in list(bpy.data.objects):
    if o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA":
        o.hide_render = o.hide_viewport = True

TC = V(0.0, 4.0, 0)
SCR = V(0.0, 22.8, 14.1)                # midden van het grote scherm op de raadszaal


def chair(k):
    a = k / 7 * math.tau + 0.2
    return V(math.cos(a) * 2.15, 4 + math.sin(a) * 2.15, 0)


def seat(name, k, **kw):
    p = chair(k)
    d = TC - p
    ch = S.actor(name, p, math.degrees(math.atan2(d.x, -d.y)), **kw)
    spec, z = sit(ch, seat_top=0.46)
    ch.rig.location.z = z
    ch.rig.keyframe_insert("location", frame=1)
    ch.spec = spec
    return ch


# ---------------------------------------------------------------- het scherm: tekst letter voor letter / regel voor regel
for key in ("test", "result", "phase"):
    for scr in ("Scherm_1", "Scherm_2", "Scherm_3"):
        g = S.obj(f"{scr}_tekst_{key}")
        for o in [g] + list(g.children):
            o.hide_render = o.hide_viewport = True
root = S.obj("Scherm_1")
TXT_COL = (1.0, 0.95, 0.9)


def typed(text, z, size, t0, rate, tick=True):
    """Tekst die letter voor letter verschijnt (prefix-objecten, links uitgelijnd op de plek van de hele regel)."""
    full = ST3.label("Scherm_typ_meet", text, (0, -0.09, z), size, TXT_COL, glow=9.0)
    full.parent = root
    bpy.context.view_layer.update()
    x0 = min((full.matrix_world @ V(c)).x for c in full.bound_box)
    bpy.data.objects.remove(full)
    objs = []
    for k in range(1, len(text) + 1):
        if text[k - 1] == " ":
            continue
        o = ST3.label(f"Scherm_typ_{text[:3]}_{k}", text[:k], (x0, -0.09, z), size, TXT_COL, glow=9.0, align="LEFT")
        o.parent = root
        objs.append((o, t0 + (k - 1) * rate))
        if tick:
            S.sfx("sfx_letter_tik", t0 + (k - 1) * rate, 0.25)
    for i, (o, ta) in enumerate(objs):
        visible(o, 0.0, False)
        visible(o, ta, True)
        if i + 1 < len(objs):
            visible(o, objs[i + 1][1], False)
    return objs[-1][1]


def lines(texts, zs, size, t0, gap, until=None):
    for i, (tx, z) in enumerate(zip(texts, zs)):
        o = ST3.label(f"Scherm_regel_{tx[:6]}_{i}", tx, (0, -0.09, z), size, TXT_COL, glow=9.0)
        o.parent = root
        visible(o, 0.0, False)
        visible(o, t0 + i * gap, True)
        if until is not None:
            visible(o, until, False)
        S.sfx("sfx_letter_tik", t0 + i * gap, 0.3)


T_TEST = t_d + 0.6
done = typed("TEST COMPLETE.", 13.65, 0.95, T_TEST, 0.15)
# na TEST COMPLETE blijft de tekst staan tot de RESULT-regels komen
lines(["RESULT:", "HUMANS CREATE NEW RULES", "WITHIN 9 DAYS."], [15.0, 14.0, 13.0], 0.7, t_f + 0.3, 0.9, until=t_h)
lines(["PHASE 2 BEGINS", "AT SUNRISE."], [14.5, 13.2], 0.95, t_h + 0.4, 1.0)
# de TEST-regel verdwijnt als RESULT komt, PHASE verdringt RESULT
for o in [o for o in bpy.data.objects if o.name.startswith("Scherm_typ_")]:
    visible(o, t_f + 0.3, False)

# ---------------------------------------------------------------- de stadsraad aan tafel
held = seat("hoofdpersonage_volwassen", 0)
pest = seat("pestkop_volwassen", 6)
wet = seat("wetenschapper", 1)
male_scientist(S, wet)
oma = seat("oma", 3)
buur = seat("buurman", 4)
ag = seat("agent", 5, drop=("agent_badge",))
HH = S.headpos(held, 0.0)

# telefoon in zijn hand, licht rood op
phone = T.box("Telefoon_volwassen", (0, 0, 0), (0.08, 0.012, 0.15), S.mat("telefoon_zwart", (0.05, 0.05, 0.06)), bevel=0.01, ol=0.002)
scr = T.box("Telefoon_volwassen_scherm", (0, -0.007, 0.005), (0.07, 0.002, 0.13), S.mat("telefoon_rood", (1.0, 0.05, 0.03), 6.0), bevel=0, ol=0)
scr.parent = phone
grab(S, phone, held, 0.0, "hand.R", loc=(0.0, 0.0, -0.05), rot=(80, 0, 0))
PH = HH + V(-0.3, 0.12, -0.58)      # op borsthoogte: hoger zitten de armen in zijn grote hoofd
S.reach(held, 0.0, "R", PH)
# 21b: de schrik (krimpt even, dan omhoog), telefoon glijdt maar hij vangt hem
S.beat(held, 0.0, face="neutraal", face_amt=0.5, at=PH, body={"spine": (10, 0, 0)}, **held.spec)
S.beat(held, 0.35, face="geschrokken", face_amt=0.6, at=PH, body={"spine": (12, 0, 0), "head": (4, 0, 0)}, **held.spec)
S.beat(held, 0.6, face="geschrokken", face_amt=1.0, at=PH, body={"spine": (-8, 0, 0), "head": (-6, 0, 0)}, **held.spec)
S.reach(held, 0.6, "R", PH + V(0.0, 0.0, 0.12))
S.reach(held, 0.8, "R", PH + V(0.02, -0.04, 0.05))
S.reach(held, 0.95, "R", PH + V(0.0, 0.0, 0.1))
S.reach(held, 0.6, "L", inf=0.0)
S.reach(held, 0.75, "L", PH + V(0.06, -0.08, 0.0))
S.reach(held, 1.0, "L", PH + V(0.06, -0.07, 0.1))
S.reach(held, 0.0, "L", inf=0.0)
S.beat(held, 1.4, face="bang", face_amt=0.7, at=PH + V(0, 0, 0.1), body={"spine": (-4, 0, 0)}, **held.spec)
S.reach(held, t_c - 0.3, "R", PH + V(0.0, 0.0, 0.1))
S.reach(held, t_c - 0.3, "L", PH + V(0.06, -0.07, 0.1))
S.reach(held, t_c + 0.4, "R", PH + V(0.0, 0.0, 0.06))
S.reach(held, t_c + 0.2, "L", PH + V(0.06, -0.07, 0.08))
S.reach(held, t_c + 0.4, "L", inf=0.0)
# 21c-21e: hij kijkt naar het scherm en leest, lippen bewegen mee
S.beat(held, t_c - 0.2, face="bang", face_amt=0.6, at=SCR, body={"spine": (-6, 0, 0)}, **held.spec)
S.beat(held, t_e, face="verbaasd", face_amt=0.6, at=SCR, body={"spine": (-6, 0, 0)}, **held.spec)
for k, t in enumerate(frange(t_e + 0.3, t_e + 2.5, 0.13)):
    A.key_prop(held.rig, "mond_open", 0.12 if k % 2 else 0.02, F(t))
A.key_prop(held.rig, "mond_open", 0.0, F(t_e + 2.6))
A.blink_at(held, F(t_e + 2.7))
S.beat(held, t_g + 0.6, face="bang", face_amt=0.7, at=S.headpos(wet, t_g), **held.spec)
S.beat(held, t_h, face="geschrokken", face_amt=0.7, at=SCR, **held.spec)

# 21i-21k: hij staat op en kijkt naar de horizon (zuid, -y)
H_UP = chair(0) + V(0.5, -0.9, 0)
S.teleport(held, t_i, H_UP, 0)
held.rig.location = tuple(H_UP)
held.rig.keyframe_insert("location", frame=F(t_i))
S.beat(held, t_i, "staan", face="bang", face_amt=0.5, at=V(0, -260, 18))
S.reach(held, t_i - 0.05, "R", PH + V(0.0, 0.0, 0.06))      # telefoon vast tot de snede, niet 10 s langzaam laten zakken
S.reach(held, t_i, "R", inf=0.0)
S.beat(held, t_j, "staan", face="twijfel", face_amt=0.6, at=V(0, -260, 18))
A.blink_at(held, F(t_j + 2.2))
S.beat(held, t_k, "staan", face="vastberaden", face_amt=0.6, at=V(0, -260, 18))
S.hold(held, END)
visible(phone, 0.0, True)
visible(scr, 0.0, True)

# de rest van de raad: bevroren, kijkt naar het scherm, ademt
for i, ch in enumerate((pest, wet, oma, buur, ag)):
    S.beat(ch, 0.0, face="neutraal", face_amt=0.5, at=TC + V(0, 0, 0.8), **ch.spec)
    S.beat(ch, 0.4 + 0.1 * i, face="geschrokken", face_amt=0.8, at=SCR, **ch.spec)
    for j, t in enumerate(frange(1.2 + 0.2 * i, END, 1.6)):
        S.beat(ch, t, face="bang", face_amt=0.6, at=SCR, body={"spine": (-3 if j % 2 else -6, 0, 0)}, **ch.spec)
    A.blink_at(ch, F(t_c + 1.0 + 0.4 * i))
S.beat(wet, t_g, face="bang", face_amt=0.8, at=HH, **wet.spec)
S.say("N21-01", who=wet, at=t_g + 0.4)
S.beat(wet, t_g + 2.5, face="bang", face_amt=0.7, at=SCR, **wet.spec)

# het plein: mensen staan stil en kijken omhoog
CROWD = [("papa_grijs", (-4.0, 0.0)), ("mama_grijs", (-3.2, -0.6)), ("broertje_tiener", (-5.2, -1.2)), ("figurant_a", (4.5, -1.0)),
         ("figurant_b", (5.6, 0.4)), ("figurant_c", (-6.5, 2.0)), ("figurant_d", (3.6, -2.6)), ("figurant_e", (6.8, -2.2)),
         ("figurant_f", (-2.0, -3.0)), ("kind_a", (-6.0, -3.4)), ("kind_b", (2.2, -1.8)), ("volgeling_a", (7.2, 1.6))]
for i, (n, (x, y)) in enumerate(CROWD):
    p = V(x, y, 0)
    d = SCR - p
    ch = S.actor(n, p, math.degrees(math.atan2(d.x, -d.y)))
    for j, t in enumerate(frange(0.0, END, 1.5 + 0.1 * (i % 4))):
        S.beat(ch, t, "staan", face="bang" if j else "geschrokken", face_amt=0.6, at=SCR, body={"spine": (-2 if j % 2 else -5, 0, 0)})
    A.blink_at(ch, F(t_c + 0.5 + 0.25 * i))
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 21b CLOSE de jongen schrikt op
S.cam(0.0, (HH + V(-1.55, -0.55, -0.5), HH + V(0, 0, -0.2), 32), handheld=0.4)
# 21c WIDE trage push: het bevroren plein
S.cam(t_c, ((6.0, -22.0, 4.0), (0.0, 10.0, 7.0), 24), ((4.6, -17.0, 3.6), (0.0, 10.0, 7.0), 24))
# 21d DETAIL het scherm, TEST COMPLETE.
S.cam(t_d, ((0.0, 10.0, 11.5), SCR, 35), ((0.0, 12.5, 12.2), SCR, 37))
# 21e CLOSE hij leest
dS = SCR - HH
dS.z = 0
dS.normalize()
S.cam(t_e, (HH + dS * 1.25 + V(0, 0, -0.1), HH + V(0, 0, -0.25), 32), (HH + dS * 1.1 + V(0, 0, -0.1), HH + V(0, 0, -0.25), 34))
# 21f DETAIL RESULT
S.cam(t_f, ((0.0, 12.5, 12.2), SCR, 37), ((0.0, 13.5, 12.6), SCR, 38))
# 21g CLOSE de wetenschapper
HW = S.headpos(wet, t_g)
dW = (TC - HW).normalized()
dW.z = 0
dW.normalize()
S.cam(t_g, (HW + dW * 1.4 + V(0, 0, -0.02), HW + V(0, 0, -0.02), 32), (HW + dW * 1.3 + V(0, 0, -0.02), HW + V(0, 0, -0.02), 33))
# 21h DETAIL push-in PHASE 2
S.cam(t_h, ((0.0, 10.0, 11.5), SCR, 35), ((0.0, 14.5, 12.8), SCR, 40))
# 21i WIDE trage pull-back naar het zuiden: het rode plein, de blauwe streep aan de horizon
S.cam(t_i, ((0.0, 12.0, 5.0), (0.0, -60.0, 3.0), 24), ((0.0, 19.0, 8.0), (0.0, -60.0, 3.0), 24))
# 21j CLOSE de jongen kijkt naar de horizon (van voren)
HU_ = S.headpos(held, t_j)
S.cam(t_j, (HU_ + V(0.25, -1.3, -0.02), HU_ + V(0, 0, -0.04), 32), (HU_ + V(0.22, -1.2, -0.02), HU_ + V(0, 0, -0.04), 34))
# 21k CLOSE trage push-in
S.cam(t_k, (HU_ + V(-0.3, -1.4, 0.0), HU_ + V(0, 0, -0.02), 36), (HU_ + V(-0.25, -1.2, 0.0), HU_ + V(0, 0, -0.02), 40))

# ---------------------------------------------------------------- geluid en stem (geen HUD)
T_STOP = t_h + 1.6
S.sfx("sfx_glitch", 0.0, 0.3)
S.sfx("sfx_alarm_nucleair", 0.0, 0.9, keys=[(0.0, 0.9), (1.5, 0.3), (T_STOP - 0.05, 0.3), (T_STOP, 0.0)], loop_to=T_STOP)
S.sfx("sfx_hartslag", t_d, 0.2, loop_to=t_h)
S.ambience("sfx_stad_nacht_wind", T_STOP + 2.0, END, vol=0.05)
S.music("m_nacht_angst", T_STOP + 2.0, END, vol=0.16, fade_in=1.0, fade_out=0.6)
S.say("N21-02", at=t_i + 2.6)
S.say("N21-03", at=t_k + 0.5)
S.finish(length=END, tail=0.0)
