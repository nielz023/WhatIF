"""S05 · Dag 3 · gymzaal: 200 optrekken, de stang buigt, armpje drukken met de pestkop.

    blender -b -P anim/scenes/s05_gymzaal.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s05", "gymzaal", "binnen")

# ---------------------------------------------------------------- set: losse optrekstang en een breekbare klaptafel
for o in bpy.data.objects:
    if o.name.startswith(("Optrekstang", "Klaptafel")):
        o.hide_render = True
BX, BY0, BY1, BZ = -9.0, 2.9, 4.3, 2.45
BYM = (BY0 + BY1) / 2
metal = P.m("metaal")
for y in (BY0, BY1):
    T.cyl(f"Rekpaal_{y}", (BX, y, 0), 0.04, BZ + 0.1, S.mat("rekpaal", (0.2, 0.35, 0.75)), seg=12, ol=0.008)
    T.box(f"Rekvoet_{y}", (BX, y, 0), (0.9, 0.12, 0.05), S.mat("rekpaal", (0.2, 0.35, 0.75)), bevel=0.01, ol=0.006)
halves = []
for k, (y0, y1) in enumerate(((BY0, BYM), (BYM, BY1))):
    h = T.cyl(f"Stang_helft{k}", (BX, y0 if k == 0 else BYM, BZ), 0.025, BYM - BY0, metal, rot=(-90, 0, 0), seg=10, ol=0.006)
    halves.append(hinge(h, (BX, y0 if k == 0 else y1, BZ)))


def bar_sag(deg, t):
    key(halves[0], t, rot=(-deg, 0, 0))
    key(halves[1], t, rot=(deg, 0, 0))


TBX, TBY, TBZ = 2.0, -1.0, 0.74
wood = S.mat("klaptafel", (0.92, 0.92, 0.9))
tab = []
for k, s in enumerate((-1, 1)):
    top = T.box(f"Klaptafel_helft{k}", (TBX, TBY + s * 0.175, TBZ - 0.04), (1.2, 0.35, 0.04), wood, bevel=0.01, ol=0.008)
    legs = [T.cyl(f"Klaptafel_poot{k}{j}", (TBX + x, TBY + s * 0.3, 0), 0.018, TBZ - 0.04, metal, seg=8, ol=0.004) for j, x in enumerate((-0.52, 0.52))]
    tab.append(hinge(top, (TBX, TBY, TBZ - 0.04), legs))

# ---------------------------------------------------------------- figuren
HANG = V(BX, BYM, 0)
held = S.actor("hoofdpersonage", HANG, 90, energy=0.6)
leraar = S.actor("gymleraar", (-7.4, 2.3, 0), heading((-7.4, 2.3), HANG))
vriend = S.actor("beste_vriend", (-7.2, 4.9, 0), heading((-7.2, 4.9), HANG))
pest = S.actor("pestkop", (-5.6, 6.4, 0), heading((-5.6, 6.4), HANG), energy=0.7)
phone = prop_phone(S, "Telefoon_vriend")
attach(phone, vriend, "hand.L", (0, 0.02, 0.03), (90, 0, 180))
CLASS_AT = [(-7.0, 3.6), (-6.6, 2.9), (-6.9, 5.6), (-6.2, 4.3), (-7.8, 1.6), (-6.0, 3.4)]
klas = []
for k, (x, y) in enumerate(CLASS_AT):
    ch = S.extra(k, (x, y, 0), heading((x, y), HANG) + (k % 3 - 1) * 8, energy=0.8)
    klas.append(ch)

# ---------------------------------------------------------------- tijdlijn
S.hud(3, "8x STRONGER", t0=0.35)
S.sfx("sfx_fluitje", 0.15, 0.7)
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.10)
l1 = S.say("S05-01", gap=0.9)
S.music("funky", 0.2, 0, vol=0.32)                           # einde hieronder gezet
l2 = S.say("S05-02", gap=0.4)
STOP = l2[0] + 4.9                                             # 'At two hundred'
BEND = l2[0] + 7.6                                             # 'Because the bar is bending'
S.sfx("sfx_metaal_buigt", BEND - 0.6, 0.7)
l3 = S.say("S05-03", gap=0.5, who=vriend, gain=1.2)
l4 = S.say("S05-04", gap=0.6)
S.music("pizz_spanning", l4[0] - 0.3, 0, vol=0.26, fade_in=0.4)
TABLE = l4[1] + 0.4                                            # snede naar de klaptafel
l5 = S.say("S05-05", at=TABLE + 0.7, who=pest, gain=1.2)
l6 = S.say("S05-06", gap=0.6)
l7 = S.say("S05-07", gap=0.5)
S.music("episch_slowmo", l7[0] - 0.4, l7[1] + 0.3, vol=0.34, fade_in=0.3, fade_out=0.3)
S.sfx("sfx_slowmo", l7[0] - 0.5, 0.5)
S.real(l7[0], l7[1])
SNAP = l7[1] + 0.35
S.sfx("sfx_tafel_breekt", SNAP - 0.05, 1.0)
l8 = S.say("S05-08", at=SNAP + 2.3, who=pest, gain=1.3)
S.wait(1.6)
END = S.t
# pizz_spanning stond open: sluit af bij de slow motion
for snd in S.sounds:
    if snd.get("file") == "muziek/pizz_spanning":
        snd["loop_to"] = l7[0]
    if snd.get("file") == "muziek/funky":
        snd["loop_to"] = l4[0]

# optrekteller
S.gauge("PULL-UPS: 1", l2[0] + 0.6, l2[0] + 1.4, color=WHITE)
for k, n in enumerate((2, 3, 9, 27, 58, 96, 131, 167, 188, 200)):
    t0 = l2[0] + 1.4 + k * 0.33
    S.gauge(f"PULL-UPS: {n}", t0, t0 + 0.33 if n != 200 else BEND + 1.5, color=GOLD if n == 200 else WHITE)
S.text("GRIP", l7[0] + 1.0, l7[1], loc=(0.965, 0.42), size=40, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("AVERAGE GUY: 45 KG", l7[0] + 1.6, l7[1], loc=(0.965, 0.35), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("YOU: 360 KG", l7[0] + 4.3, l7[1], loc=(0.965, 0.27), size=60, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("WORLD RECORD: ~150 KG", l7[0] + 7.4, l7[1], loc=(0.965, 0.20), size=44, color=CYAN, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- de optrekstang
REP0 = l2[0] + 0.5
bar_sag(0, 0.0)
bar_sag(0, BEND - 0.7)
bar_sag(9, BEND + 0.6)
bar_sag(11, BEND + 1.2)
sag_z = lambda t: 0.0 if t < BEND - 0.7 else (BYM - BY0) * math.sin(math.radians(min(11, max(0, (t - BEND + 0.7) / 1.3 * 9))))
LOW = BZ - 1.60                                               # wortel bij gestrekte armen
reps = [REP0 + 0.95 * k for k in range(3)]                     # rustig
t = reps[-1] + 0.95
period = 0.5
while t < STOP:                                                # steeds sneller
    reps.append(t)
    t += period
    period = max(0.11, period * 0.82)
S.place(held, 0.0, (BX, BYM, LOW), 90)
for k, r in enumerate(reps):
    dur = (reps[k + 1] - r) if k + 1 < len(reps) else 0.8
    S.place(held, r, (BX, BYM, LOW), None)
    S.place(held, r + dur * 0.45, (BX, BYM, LOW + 0.34), None)
S.place(held, STOP, (BX, BYM, LOW + 0.34), None)                # blijft boven hangen
for t in (BEND - 0.7, BEND + 0.6, BEND + 1.2, TABLE - 0.05):
    S.place(held, t, (BX, BYM, LOW + 0.34 - sag_z(t)), None)
for t in [0.0] + [r for r in reps] + [STOP, BEND - 0.7, BEND + 0.6, BEND + 1.2, TABLE - 0.05]:
    for side, dy in (("L", 0.19), ("R", -0.19)):
        S.reach(held, t, side, (BX + 0.03, BYM + dy * 0.9, BZ - sag_z(t) - 0.01), 1.0)
S.beat(held, 0.0, "armen_omhoog", face="zelfverzekerd", face_amt=0.5, feet=((0, -0.12, 0.1), (0, -0.1, 0.12)))
S.beat(held, reps[3], "armen_omhoog", face="blij", face_amt=0.6, feet=((0, -0.12, 0.1), (0, -0.1, 0.12)))
S.beat(held, STOP + 0.2, "armen_omhoog", face="verbaasd", face_amt=0.5, at=S.head(leraar), feet=((0, -0.12, 0.1), (0, -0.1, 0.12)))
S.beat(held, BEND, "armen_omhoog", face="geschrokken", face_amt=0.7, look=(0, 0.9), body={"head": (-30, 0, 0)}, feet=((0, -0.12, 0.1), (0, -0.1, 0.12)))
S.beat(held, l3[0] + 0.3, "armen_omhoog", face="nerveus", face_amt=0.7, at=S.head(vriend), feet=((0, -0.12, 0.1), (0, -0.1, 0.12)))
S.hold(held, TABLE - 0.05)

# de leraar: fluit, kijkt, steekt zijn hand op
S.beat(leraar, 0.0, "staan", face="vastberaden", face_amt=0.5, at=S.head(held, 0))
S.beat(leraar, reps[4], "armen_over", face="neutraal", at=S.head(held, reps[4]))
S.beat(leraar, STOP - 0.6, "armen_over", face="verbaasd", face_amt=0.7, at=S.head(held, STOP))
S.beat(leraar, STOP, "wijzen", face="nerveus", at=S.head(held, STOP), body={"chest": (-4, 0, 0)})
S.beat(leraar, BEND + 0.2, "handen_hoofd", face="geschrokken", at=(BX, BYM, BZ))
S.hold(leraar, TABLE - 0.05)
# de klas staart; de vriend filmt (te laat)
for k, ch in enumerate(klas):
    S.beat(ch, 0.0, "ontspannen", face="neutraal", face_amt=0.5, at=S.head(held, 0) + V(0, 0, -0.3))
    S.beat(ch, reps[5] + k * 0.1, "staan", face="verbaasd", face_amt=0.7, at=S.head(held, reps[5]))
    S.beat(ch, STOP + 0.3 + k * 0.08, "schrik" if k % 2 else "handen_hoofd", amount=0.6, face="geschrokken", face_amt=0.8, at=S.head(held, STOP))
    S.beat(ch, l3[0] + 0.2 * k, "staan", face="verbaasd", face_amt=0.9, at=S.head(held, STOP) + V(0, 0, 0.3))
    S.hold(ch, TABLE - 0.05)
S.beat(vriend, 0.0, "ontspannen", face="blij", face_amt=0.5, at=S.head(held, 0))
S.beat(vriend, reps[5], "juichen", face="lach", at=S.head(held, reps[5]))
S.beat(vriend, STOP, "handen_hoofd", face="verbaasd", at=S.head(held, STOP))
S.beat(vriend, l3[0] - 0.2, "filmen", face="lach", face_amt=0.9, at=S.head(held, l3[0]), body={"head": (-6, 0, 0)})
S.beat(vriend, l3[0] + 1.2, "filmen", face="schreeuw", face_amt=0.6, at=S.head(held, l3[0]))
S.beat(vriend, l3[1] - 0.2, "filmen", face="lach", face_amt=0.7, at=S.head(held, l3[0]))
S.hold(vriend, TABLE - 0.05)
show(phone, l3[0] - 0.3)
# de pestkop: armen over elkaar, komt naar voren
S.beat(pest, 0.0, "armen_over", face="boos", face_amt=0.4, at=S.head(held, 0))
S.beat(pest, BEND, "armen_over", face="twijfel", face_amt=0.7, at=S.head(held, BEND))
S.walk(pest, l4[0] + 0.6, l4[0] + 3.0, [V(-5.6, 6.4, 0), V(-6.4, 5.4, 0), V(-7.4, 4.3, 0)], end_rot=heading((-7.4, 4.3), HANG))
S.beat(pest, l4[0] + 3.4, "armen_over", face="zelfverzekerd", face_amt=0.9, at=S.head(held, l4[0]))
S.hold(pest, TABLE - 0.05)

# ---------------------------------------------------------------- de klaptafel
HERO_T = V(TBX, TBY - 0.47, 0)
PEST_T = V(TBX, TBY + 0.47, 0)
SIT_H, zh = sit(held)
SIT_P, zp = sit(pest)
S.teleport(held, TABLE, HERO_T + V(0, 0, zh), 180)
S.teleport(pest, TABLE, PEST_T + V(0.0, 0.35, 0), 0)
S.place(pest, l5[0] + 1.0, PEST_T + V(0.0, 0.35, 0), 0)
S.place(pest, l5[1] + 0.2, PEST_T + V(0, 0, zp), 0)
CROWD = [(3.2, -1.9), (3.4, -1.1), (3.25, -0.3), (2.9, 0.35), (3.0, -2.6), (3.7, -0.7)]
for k, ch in enumerate(klas):
    x, y = CROWD[k]
    S.teleport(ch, TABLE, (x, y, 0), heading((x, y), (TBX, TBY)))
S.teleport(leraar, TABLE, (3.0, 0.9, 0), heading((3.0, 0.9), (TBX, TBY)))
S.teleport(vriend, TABLE, (1.0, -2.25, 0), heading((1.0, -2.25), (TBX, TBY)))
G_UP = V(TBX, TBY, TBZ + 0.22)                                  # handen in elkaar, rechtop
G_DOWN = V(TBX - 0.32, TBY + 0.02, TBZ + 0.04)                  # pestkop verliest (naar zijn rechterkant, -x)
S.reach(held, TABLE, "L", None, 0.0)
S.reach(held, TABLE, "R", None, 0.0)
S.beat(held, TABLE, **SIT_H, pose="ontspannen", face="neutraal", at=S.head(pest, l5[0]))
S.beat(held, l5[0] + 1.2, **SIT_H, pose="ontspannen", face="twijfel", face_amt=0.6, at=S.head(pest, l5[0] + 1))
# de pestkop slaat met zijn hand op tafel en gaat zitten
S.beat(pest, TABLE, "armen_over", face="boos", at=S.head(held, TABLE))
S.beat(pest, l5[0] + 0.4, "wijzen", face="boos", face_amt=1.0, at=S.head(held, TABLE), body={"spine": (14, 0, 0), "head": (-12, 0, 0)})
S.sfx("sfx_dreun", l5[0] + 0.45, 0.35)
S.beat(pest, l5[1] - 0.5, "armen_over", face="zelfverzekerd", at=S.head(held, TABLE))
S.beat(pest, l5[1] + 0.25, **SIT_P, pose="staan", face="vastberaden", at=S.head(held, TABLE))
GRIP = l5[1] + 1.0
for ch, side in ((held, "R"), (pest, "R")):
    S.reach(ch, GRIP - 0.6, side, None, 0.0)
    S.reach(ch, GRIP, side, G_UP)
S.reach(pest, GRIP, "L", (TBX + 0.35, TBY + 0.2, TBZ + 0.02))
S.reach(held, GRIP, "L", (TBX - 0.3, TBY - 0.25, TBZ + 0.02))
S.beat(held, GRIP, **{**SIT_H, "crouch": (SIT_H["crouch"][0], 4)}, pose="staan", face="zelfverzekerd", face_amt=0.5, at=S.head(pest, GRIP))
S.beat(pest, GRIP, **{**SIT_P, "crouch": (SIT_P["crouch"][0], 5)}, pose="staan", face="vastberaden", face_amt=1.0, at=S.head(held, GRIP))
# 'you go easy': hij kijkt verveeld rond; de pestkop perst alles eruit
S.beat(held, l6[0] + 1.0, **{**SIT_H, "crouch": (SIT_H["crouch"][0], 4)}, pose="staan", face="blij", face_amt=0.4, look=(0.6, 0.3), body={"head": (-4, 25, 0)})
S.beat(held, l6[1], **{**SIT_H, "crouch": (SIT_H["crouch"][0], 4)}, pose="staan", face="zelfverzekerd", face_amt=0.6, at=S.head(pest, GRIP))
S.beat(pest, l6[0] + 0.6, **{**SIT_P, "crouch": (SIT_P["crouch"][0], 6)}, pose="staan", face="inspanning", face_amt=1.0, at=S.head(held, GRIP))
for k in range(8):                                               # trillen van inspanning
    tt = l6[0] + 1.0 + k * 0.4
    S.reach(pest, tt, "R", G_UP + V(0.012 * (-1) ** k, 0.0, 0.006 * (k % 2)))
    S.reach(held, tt, "R", G_UP + V(0.012 * (-1) ** k, 0.0, 0.006 * (k % 2)))
S.beat(pest, l6[1], **{**SIT_P, "crouch": (SIT_P["crouch"][0], 7)}, pose="staan", face="inspanning", face_amt=1.0, at=G_UP, body={"head": (0, 0, 10)})
# slow motion: de arm van de pestkop gaat langzaam om (tijdens regel 7)
DOWN0, DOWN1 = l7[0] + 1.0, l7[1] - 0.2
for k in range(9):
    w = k / 8
    tt = lerp(DOWN0, DOWN1, w)
    g = G_UP.lerp(G_DOWN, smooth(0, 1, w))
    S.reach(held, tt, "R", g)
    S.reach(pest, tt, "R", g)
S.beat(pest, DOWN0 + 2.0, **{**SIT_P, "crouch": (SIT_P["crouch"][0], 8)}, pose="staan", face="schreeuw", face_amt=1.0, at=S.head(held, GRIP), body={"head": (0, 0, 16), "chest": (0, -10, 0)})
S.beat(pest, DOWN1 - 0.4, **{**SIT_P, "crouch": (SIT_P["crouch"][0], 10)}, pose="staan", face="bang", face_amt=1.0, at=S.head(held, GRIP), body={"head": (10, 0, 20), "chest": (0, -16, 0)})
S.beat(held, DOWN0 + 2.5, **{**SIT_H, "crouch": (SIT_H["crouch"][0], 4)}, pose="staan", face="nerveus", face_amt=0.4, at=S.head(pest, GRIP))
S.beat(held, DOWN1, **{**SIT_H, "crouch": (SIT_H["crouch"][0], 4)}, pose="staan", face="geschrokken", face_amt=0.6, at=S.head(pest, GRIP))
# de knak: tafel in tweeën, pestkop op de grond
for k, s in enumerate((-1, 1)):
    key(tab[k], SNAP - 0.02, rot=(0, 0, 0))
    key(tab[k], SNAP + 0.18, loc=(TBX, TBY, TBZ - 0.04), rot=(s * -38, 0, 0))
    key(tab[k], SNAP + 0.42, loc=(TBX, TBY, 0.02), rot=(s * -72, 0, 0))
    key(tab[k], SNAP - 0.02, loc=(TBX, TBY, TBZ - 0.04))
S.debris(V(TBX, TBY, TBZ), SNAP, n=10, size=(0.02, 0.05), color=(0.85, 0.85, 0.8), speed=(1.0, 2.6), up=0.9, floor=0.0, life=1.5, name="Splinter")
S.puff(V(TBX, TBY, 0.1), SNAP + 0.4, n=6, r=(0.15, 0.3), color=(0.9, 0.85, 0.75), rise=0.3)
S.reach(pest, SNAP, "R", None, 0.0)
S.reach(pest, SNAP, "L", None, 0.0)
S.reach(held, SNAP + 0.1, "R", G_DOWN + V(0, -0.05, 0.1), 1.0)
S.reach(held, SNAP + 0.4, "R", None, 0.0)
S.reach(held, SNAP, "L", None, 0.0)
S.place(pest, SNAP + 0.05, PEST_T + V(0, 0, zp), 0)
S.place(pest, SNAP + 0.45, PEST_T + V(-0.1, 0.3, -0.52), 0)
S.beat(pest, SNAP + 0.45, "schrik", face="geschrokken", crouch=(0.0, -18), feet=((0.08, 0.5, 0.42), (-0.08, 0.45, 0.44)))
S.beat(pest, l8[0] - 0.2, "ontspannen", face="verdrietig", face_amt=0.9, at=S.head(held, SNAP), crouch=(0.0, -10), feet=((0.08, 0.5, 0.42), (-0.08, 0.45, 0.44)))
S.hold(pest, END)
S.beat(held, SNAP + 0.5, **SIT_H, pose="schouders_op", face="nerveus", face_amt=0.8, at=S.head(pest, SNAP + 0.5))
S.beat(held, l8[1], **SIT_H, pose="ontspannen", face="blij", face_amt=0.5, at=S.head(pest, SNAP + 0.5))
S.hold(held, END)
for k, ch in enumerate(klas + [leraar, vriend]):
    S.beat(ch, TABLE + 0.1, "armen_over" if k % 3 == 0 else "ontspannen", face="neutraal", face_amt=0.6, at=G_UP + V(0, 0, 0.3))
    S.beat(ch, GRIP + 0.5 + k * 0.1, "ontspannen" if k % 2 else "vuisten", face="twijfel" if k % 2 else "blij", face_amt=0.6, at=G_UP + V(0, 0, 0.2))
    S.beat(ch, SNAP + 0.1 + k * 0.05, "schrik", face="geschrokken", at=V(TBX, TBY, 0.3))
    S.beat(ch, SNAP + 1.2 + k * 0.1, "juichen" if k % 2 else "handen_hoofd", face="lach" if k % 2 else "verbaasd", at=V(TBX, TBY, 0.3))
    S.hold(ch, END)
S.beat(vriend, GRIP + 0.4, "filmen", face="blij", at=G_UP)
S.beat(vriend, SNAP + 0.2, "filmen", face="geschrokken", at=V(TBX, TBY, 0.3))
S.beat(vriend, SNAP + 1.4, "filmen", face="lach", at=V(TBX, TBY, 0.3))
S.hold(vriend, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-1.5, -4.5, 3.2), (-8.5, 3.5, 1.6), 24), ((-2.5, -3.6, 3.0), (-8.5, 3.6, 1.7), 26))
S.cam(l2[0] + 0.3, ((-5.6, 1.3, 2.1), (BX, BYM, 1.9), 26), ((-5.9, 1.6, 2.1), (BX, BYM, 2.0), 28))
S.cam(reps[4], ((-7.2, 3.0, 1.3), (BX, BYM, 2.1), 22), shake=lambda t: 0.6)
S.cam(STOP - 0.3, S.shot(leraar, STOP, "mcu", az=-15, lens=32))
S.cam(BEND - 0.9, ((BX + 1.5, BYM - 0.6, 1.75), (BX, BYM, BZ - 0.2), 26), ((BX + 1.35, BYM - 0.5, 1.8), (BX, BYM, BZ - 0.25), 28))
S.cam(l3[0] - 0.2, S.shot(vriend, l3[0], "mcu", az=10, lens=30), S.shot(vriend, l3[1], "cu", az=8, lens=34))
S.cam(l4[0] - 0.1, ((-2.8, 3.6, 1.5), (-6.5, 4.8, 1.4), 30))
S.cam(l4[0] + 2.0, S.shot(pest, l4[0] + 3.5, "mcu", az=10, lens=26, h=-0.2), S.shot(pest, l4[1], "cu", az=8, lens=28, h=-0.15))
S.cam(TABLE, ((0.0, -1.0, 1.25), (TBX + 0.5, TBY, 1.0), 26), ((0.2, -1.0, 1.25), (TBX + 0.5, TBY, 1.0), 28))
S.cam(l5[0] + 1.3, S.shot(pest, l5[0] + 1.3, "mcu", az=-65, lens=30))
S.cam(GRIP - 0.2, ((TBX - 1.4, TBY, 1.05), G_UP, 30), ((TBX - 1.2, TBY - 0.05, 1.05), G_UP, 32))
HP = S.headpos(pest, l6[0] + 2)
HH = S.headpos(held, l6[0] + 3)
S.cam(l6[0] + 1.6, ((TBX - 1.5, TBY + 0.15, 1.3), HP + V(0, 0, -0.1), 36))
S.cam(l6[0] + 3.0, ((TBX - 1.5, TBY - 0.15, 1.3), HH + V(0, 0, -0.1), 36))
S.cam(l7[0] - 0.3, ((TBX - 0.75, TBY - 0.1, 0.95), G_UP + V(0, 0, -0.05), 34), ((TBX - 0.7, TBY + 0.05, 0.9), G_DOWN + V(0, 0, 0.05), 36))
HP2 = S.headpos(pest, l7[0] + 5.5)
S.cam(l7[0] + 3.6, ((TBX - 1.5, TBY + 0.2, 1.25), HP2 + V(0, 0, -0.1), 38), ((TBX - 1.3, TBY + 0.25, 1.22), HP2 + V(0, 0, -0.08), 44))
S.cam(l7[0] + 6.8, ((TBX - 1.6, TBY - 0.4, 1.0), (TBX - 0.1, TBY, 0.85), 26))
S.cam(SNAP + 0.9, ((TBX - 2.4, TBY - 1.3, 1.5), (TBX, TBY, 0.6), 24), ((TBX - 2.2, TBY - 1.2, 1.45), (TBX, TBY, 0.6), 26))
S.cam(l8[0] - 0.3, S.shot(pest, l8[0], "mcu", az=-25, lens=30, h=0.4), S.shot(pest, l8[1], "mcu", az=-22, lens=33, h=0.4))

S.finish(length=END)
