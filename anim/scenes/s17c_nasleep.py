"""S17c · Dag 16 · na de klap: dit stuk is echt (de bolder), 'That's my little sister', 24 mensen lopen
weg van de achtbaan. Maar het filmpje dat viraal gaat: jij in het puin, en mensen die van je wegrennen.

    blender -b -P anim/scenes/s17c_nasleep.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401
from titan import Track, riders, cam_hide, build_coil, build_rope, rope_hands, coil_points, X_PUSH, RIDERS  # noqa: E402

S = Scene("s17c", "pretpark", "zonsondergang")
TR = Track(S)
HP, G, HI = TR.HP, TR.GROUND, TR.HERO_I
X_AFTER = HP.x - X_PUSH
D_STOP = -1.73

# ---------------------------------------------------------------- de stand na de klap
TR.bake_train(lambda t: D_STOP, 1.0)
piece = TR.rail_gap(HI + 5, HI + 16)
piece.hide_render = True
piece.hide_viewport = True
build_coil(TR)
build_rope(TR, "Rail_touw", X_AFTER)
rs = riders(S, TR.cars, calm=True)
zus = rs[0]

# ---------------------------------------------------------------- tijdlijn
S.hud(16, "65,536x STRONGER", t0=0.0, tick=False)
S.music("piano_zacht", 0.0, 60, vol=0.2, fade_in=1.2, fade_out=1.0)
PIANO = S.sounds[-1]
S.ambience("sfx_pretpark_sfeer", 0.0, 60, vol=0.06)
l9 = S.say("S17-09", gap=0.5)
SAILORS = l9[0] + 1.33
BOLLARD = l9[0] + 5.32                          # 'It's called a bollard.'
FRICTION = l9[0] + 6.63
COASTER = l9[0] + 11.42                         # 'You just did it with a roller coaster.'
S.real(l9[0] + 0.1, FRICTION + 3.4)
S.text("BOLLARD", BOLLARD, FRICTION - 0.1, loc=(0.5, 0.16), size=96, color=WHITE, anchor=("CENTER", "BOTTOM"))
S.text("2 WRAPS  →  FRICTION DOES THE WORK", FRICTION + 0.3, COASTER - 0.2, loc=(0.5, 0.12), size=52, color=CYAN,
       anchor=("CENTER", "BOTTOM"))
SISTER = l9[1] + 0.4
S.t = SISTER + 1.6
RUN_IN = SISTER + 0.9
l10 = S.say("S17-10", gap=0.0)
PIANO["loop_to"] = SISTER
S.music("strijkers_emo", SISTER - 0.2, 60, vol=0.24, fade_in=1.0, fade_out=1.5)
EMO = S.sounds[-1]
l11 = S.say("S17-11", gap=0.6)
WALK = l11[0] - 0.3
VIRAL0 = l11[0] + 3.84                          # 'But that's not the video that goes viral.'
l12 = S.say("S17-12", gap=0.5)
WRECK = l12[0] - 0.1
RUN = l12[0] + 7.4                              # 'And people running away from you.'
S.wait(1.6)
END = S.t
EMO["loop_to"] = RUN - 0.2
S.music("drone", RUN - 0.6, END + 0.3, vol=0.26, fade_in=0.6, fade_out=0.6)
S.text("● REC", WRECK, END, loc=(0.965, 0.94), size=52, color=RED, anchor=("RIGHT", "TOP"))
S.gauge("▶ 48,000,000 VIEWS", l12[0] + 2.6, END, color=WHITE)

# ---------------------------------------------------------------- de kade: zo stoppen matrozen een schip
DK = V(0.0, -230.0, 0.0)
water = S.mat("water", (0.10, 0.32, 0.55))
T.plane("Kade_water", tuple(DK + V(0, -16, 0.05)), (160, 30), water)
T.box("Kade", tuple(DK + V(0, 2, 0)), (70, 8, 1.2), S.mat("kade_beton", (0.62, 0.60, 0.57)), bevel=0.05, ol=0.03)
T.box("Kade_rand", tuple(DK + V(0, -1.9, 1.2)), (70, 0.3, 0.15), S.mat("kade_geel", (0.95, 0.75, 0.1)), bevel=0.02)
T.box("Schip_romp_rood", tuple(DK + V(0, -8.5, -1.5)), (44, 9.4, 3.2), S.mat("romp_rood", (0.65, 0.1, 0.08)), bevel=0.3, ol=0.04)
T.box("Schip_romp", tuple(DK + V(0, -8.5, 1.7)), (44, 9.4, 3.4), S.mat("romp_blauw", (0.08, 0.16, 0.35)), bevel=0.3, ol=0.04)
T.box("Schip_dek", tuple(DK + V(-10, -8.5, 5.1)), (12, 7.6, 5.0), S.mat("dek_wit", (0.93, 0.93, 0.9)), bevel=0.15, ol=0.03)
T.cyl("Schip_schoorsteen", tuple(DK + V(-12, -8.5, 10.1)), 1.1, 3.4, S.mat("schoorsteen", (0.9, 0.5, 0.1)), seg=20)
for k in range(5):
    T.box(f"Schip_raam_{k}", tuple(DK + V(-14 + k * 2.0, -4.68, 7.6)), (1.2, 0.05, 0.8), S.mat("raam_geel", (1.0, 0.85, 0.5), 2.0), bevel=0, ol=0)
BOL = DK + V(2.0, 1.0, 1.2)
dark = S.mat("bolder", (0.12, 0.12, 0.14))
T.cyl("Bolder", tuple(BOL), 0.28, 0.7, dark, seg=20)
T.cyl("Bolder_kop", tuple(BOL + V(0, 0, 0.7)), 0.38, 0.14, dark, seg=20)
rope_m = S.mat("touw", (0.85, 0.75, 0.55))
CLEAT = DK + V(5.0, -3.9, 5.15)
wraps = [BOL + V(0.33 * math.cos(-math.pi / 2 - 2 * 2 * math.pi * k / 40), 0.33 * math.sin(-math.pi / 2 - 2 * 2 * math.pi * k / 40),
                 0.55 - 0.3 * k / 40) for k in range(41)]
sailor = S.extra(1, DK + V(3.4, 2.6, 1.2), heading(DK + V(3.4, 2.6, 0), BOL), energy=0.8)
SAIL_H = DK + V(3.05, 2.05, 2.05)
T.tube("Touw_schip", [tuple(p) for p in [CLEAT, CLEAT.lerp(wraps[0], 0.5) + V(0, 0, -0.6), wraps[0]] + wraps + [SAIL_H]], 0.05, rope_m)
for side in "LR":
    S.reach(sailor, 0.0, side, SAIL_H + V(0.06 if side == "L" else -0.06, 0, 0), inf=1.0)
S.beat(sailor, 0.0, "schrap", crouch=(0.12, 10.0), feet=((0.12, 0.2, 0), (-0.12, -0.3, 0)), face="vastberaden", face_amt=0.7,
       at=BOL + V(0, 0, 0.6))
S.hold(sailor, END)

# ---------------------------------------------------------------- de held: in het stof, de rail nog in zijn handen
held = S.actor("hoofdpersonage", V(X_AFTER, HP.y, G), 90)
rh, lh = rope_hands(TR, X_AFTER)
for side, p in (("R", rh), ("L", lh)):
    S.reach(held, 0.0, side, p, inf=1.0)
    S.reach(held, RUN - 0.6, side, p, inf=1.0)
    S.reach(held, RUN + 0.2, side, p + V(-0.1, 0, -0.12), inf=0.6)
LEAN = dict(pose="schrap", crouch=(0.24, 16.0), feet=((0.16, 0.1, 0), (-0.16, -0.5, 0)))
S.beat(held, 0.0, **LEAN, body={"spine": (14, 0, 0), "head": (-6, 0, 0)}, face="verdrietig", face_amt=0.5, look=(0, 0.1))
S.beat(held, WRECK, **LEAN, body={"spine": (8, 0, 0), "head": (6, 0, 0)}, face="verdrietig", face_amt=0.6, look=(0, -0.4),
       ogen_knijp=0.3)
S.beat(held, l12[0] + 3.0, pose="staan", crouch=(0.08, 4.0), feet=((0.14, 0.1, 0), (-0.14, -0.3, 0)), body={"head": (4, -20, 0)},
       face="neutraal", face_amt=0.6, look=(-0.5, -0.3))
S.beat(held, RUN, pose="staan", crouch=(0.06, 2.0), feet=((0.14, 0.1, 0), (-0.14, -0.3, 0)), body={"head": (6, -45, 0), "neck": (0, -10, 0)},
       face="verdrietig", face_amt=0.9, look=(-0.7, -0.3), mond_verdrietig=0.8)
S.hold(held, END)
for k, t in enumerate(frange(0.0, END, 2.6)):               # laag, dun stof rond zijn voeten (niet voor zijn gezicht)
    S.puff(V(X_AFTER + 0.5, HP.y + (0.5 if k % 2 else -0.5), G + 0.08), t, n=4, r=(0.06, 0.13), grow=1.6, dur=2.4,
           color=(0.72, 0.69, 0.64), rise=0.35, spread=0.9)

# de passagiers in de trein (vóór ze uitstappen): stil, geschrokken
for n, ch in enumerate(rs):
    A.pose(ch, 1, "zitten_beugel", extra={"spine": (-4, 0, 0), "head": (-6, 0, 0)})
    A.expr(ch, 1, "bang" if n else "verdrietig", ogen_knijp=0.3)
    A.key_prop(ch.rig, "mond_open", 0.15, 1)
    A.blinks(ch, 1, F(WALK), seed=n)
A.pose(zus, F(SISTER), "zitten_beugel", extra={"head": (4, 0, 0)})
A.expr(zus, F(SISTER), "verdrietig", amount=1.0, ogen_knijp=0.4)
A.key_prop(zus.rig, "mond_open", 0.35, F(SISTER))
A.pose(zus, F(l10[0] + 0.6), "zitten_beugel", extra={"head": (-10, -35, 0)})
A.expr(zus, F(l10[0] + 0.6), "verdrietig", amount=0.8, look=(-0.6, -0.5))
for ch in rs:
    visible(ch.rig, 0.0, True)
    visible(ch.rig, WALK, False)
for o in [o for o in bpy.data.objects if o.name.startswith("Passagier_")]:
    visible(o, 0.0, True)
    visible(o, WALK, False)

# ---------------------------------------------------------------- de pestkop rent naar voren
SEAT_W = TR.car_matrix(TR.car_s(D_STOP, 0)) @ V(0.6, 0.38, 0.3)
BULLY_STOP = V(SEAT_W.x + 0.2, HP.y - 2.0, 0)
pest = S.actor("pestkop", V(BULLY_STOP.x - 6.0, BULLY_STOP.y - 7.5, 0), 0, energy=1.3)
S.walk(pest, RUN_IN - 1.6, l10[0] + 0.3, [V(BULLY_STOP.x - 6.0, BULLY_STOP.y - 7.5, 0), BULLY_STOP], stride=0.85, arms=1.0,
       end_rot=heading(BULLY_STOP, SEAT_W))
S.beat(pest, l10[0] + 0.35, "staan", crouch=(0.08, 14), face="bang", face_amt=1.0, at=SEAT_W + V(0, 0, 0.8), mouth=0.3,
       body={"chest": (10, 0, 0)}, arms=HAND_OUT_R)
S.beat(pest, l10[0] + 1.6, "staan", crouch=(0.05, 8), face="verdrietig", face_amt=1.0, at=SEAT_W + V(0, 0, 0.8),
       arms=arms(HAND_OUT_R, HAND_OUT_L), mond_verdrietig=1.0)
S.hold(pest, l11[1])

# ---------------------------------------------------------------- 24 mensen lopen weg (en later: rennen weg)
walkers = []
starts = [(0.0, 0.0), (0.9, 0.5), (-0.8, 0.6), (1.6, -0.3), (0.4, 1.4), (-1.4, 1.5), (2.2, 1.0), (-0.3, 2.3), (1.3, 2.4)]
for n, d in enumerate(RIDERS[1:8]):
    walkers.append(S.actor(d["cast"], (0, 0, 0), 0, energy=1.2, label=d["label"] + "_lopen", outfit=d.get("outfit"), drop=d["drop"]))
zus_g = S.actor("zusje_pestkop", (0, 0, 0), 0, energy=1.3, label="zusje_lopen")
W0 = V(BULLY_STOP.x - 0.5, BULLY_STOP.y - 0.6, 0)
DIR = V(-0.45, -0.89, 0)
SIDE = V(0.89, -0.45, 0)
group = walkers + [zus_g]
for n, ch in enumerate(group):
    dx, dy = starts[n]
    p0 = W0 + SIDE * dx - DIR * dy
    p1 = p0 + DIR * 6.5
    p2 = p1 + DIR * 10.0 + SIDE * (dx * 0.6)
    S.place(ch, 0.0, p0, heading(p0, p1))
    S.teleport(ch, WALK - 0.05, p0, heading(p0, p1))
    visible(ch.rig, 0.0, False)                         # tot dan zitten ze nog in de trein
    visible(ch.rig, WALK, True)
    S.walk(ch, WALK, RUN - 0.1, [p0, p1], stride=0.4 if ch is not zus_g else 0.3, arms=0.3)
    S.walk(ch, RUN, END, [p1, p2], stride=0.95 if ch is not zus_g else 0.6, arms=1.2)
    S.beat(ch, WALK, "staan", face="verdrietig" if n % 2 else "bang", face_amt=0.7, look=(0, -0.3), feet="keep", face_only=True)
    S.beat(ch, RUN - 0.3, "staan", face="bang", face_amt=1.0, at=S.head(held, RUN), face_only=True)
    S.beat(ch, RUN + 0.6, "staan", face="schreeuw" if n % 3 == 0 else "bang", face_amt=1.0, look=(0.5, 0.2), face_only=True)
# de pestkop pakt zijn zusje en loopt mee
S.walk(pest, WALK, RUN - 0.1, [BULLY_STOP, BULLY_STOP + DIR * 6.0], stride=0.5, arms=0.3)
S.walk(pest, RUN, END, [BULLY_STOP + DIR * 6.0, BULLY_STOP + DIR * 15.0], stride=1.0, arms=1.2)
S.beat(pest, RUN + 0.3, "staan", face="bang", face_amt=1.0, at=S.head(held, RUN), face_only=True)

# de vriend filmt
FRIEND_AT = V(X_AFTER - 4.5, HP.y - 9.0, 0)
vriend = S.actor("beste_vriend", FRIEND_AT, heading(FRIEND_AT, V(X_AFTER, HP.y, 0)), energy=1.2)
S.beat(vriend, 0.0, "filmen_R", face="verbaasd", face_amt=0.7, at=V(X_AFTER, HP.y, G + 1.3))
S.beat(vriend, VIRAL0 - 0.6, "filmen_R", face="nerveus", face_amt=0.8, at=V(X_AFTER, HP.y, G + 1.3))
S.hold(vriend, END)
PHONE = FRIEND_AT + V(0, 0, 1.45) + (V(X_AFTER, HP.y, 0) - FRIEND_AT).normalized() * 0.35

# ---------------------------------------------------------------- camera
coil_c = coil_points(TR)[30]
S.cam(0.0, ((X_AFTER - 3.0, HP.y - 8.5, G + 0.4), (X_AFTER + 1.0, HP.y, G + 0.4), 30), ((X_AFTER - 2.6, HP.y - 7.8, G + 0.3), (X_AFTER + 1.0, HP.y, G + 0.4), 32))
S.cam(SAILORS - 0.1, (DK + V(-16, 12, 7.0), DK + V(1, -3, 2.4), 28), (DK + V(-14, 11, 6.2), DK + V(1.5, -2, 2.0), 30))
S.cam(BOLLARD - 0.1, (BOL + V(-1.7, 2.3, 1.15), BOL + V(0.5, 0.4, 0.5), 32), (BOL + V(-1.45, 2.0, 1.05), BOL + V(0.5, 0.4, 0.5), 34))
S.cam(FRICTION - 0.1, ((HP.x + 1.5, HP.y - 2.4, 1.45), (HP.x, HP.y - 0.2, 1.5), 34), ((HP.x + 1.3, HP.y - 2.1, 1.5), (HP.x, HP.y - 0.2, 1.5), 36))
S.cam(COASTER - 0.1, ((X_AFTER - 7.0, HP.y - 9.5, 5.4), (X_AFTER + 2.5, HP.y, 3.3), 28), ((X_AFTER - 6.4, HP.y - 8.8, 5.2), (X_AFTER + 2.5, HP.y, 3.3), 30))
ZH = S.headpos(zus, SISTER + 0.5)
S.cam(SISTER, (ZH + V(-1.2, -0.55, 0.05), ZH + V(0, 0, -0.05), 40), (ZH + V(-1.0, -0.45, 0.05), ZH + V(0, 0, -0.05), 44))
S.cam(RUN_IN - 0.2, ((BULLY_STOP.x + 3.0, BULLY_STOP.y - 3.5, 1.0), (BULLY_STOP.x - 0.5, BULLY_STOP.y, 2.2), 26),
      ((BULLY_STOP.x + 2.8, BULLY_STOP.y - 3.2, 1.0), (BULLY_STOP.x - 0.5, BULLY_STOP.y + 0.5, 2.4), 28))
BH = S.head(pest, l10[0] + 0.5)
S.cam(l10[0] + 0.6, (BH + V(0.8, 1.7, 0.45), BH + V(0, 0, -0.2), 30), (BH + V(0.7, 1.55, 0.42), BH + V(0, 0, -0.2), 33))
S.cam(WALK, ((W0.x - 7.5, W0.y - 11.0, 1.5), (W0.x, W0.y, 2.4), 30), ((W0.x - 7.0, W0.y - 10.2, 1.5), (W0.x, W0.y, 2.4), 32))
S.cam(VIRAL0 - 0.2, S.shot(vriend, VIRAL0, "mcu", az=35, lens=32), S.shot(vriend, VIRAL0 + 1.8, "mcu", az=30, lens=36))
S.cam(WRECK, (PHONE, V(X_AFTER + 0.3, HP.y, G + 0.9), 55), (PHONE + V(0.15, 0.2, 0), V(X_AFTER + 0.3, HP.y, G + 1.0), 75), handheld=1.2)
S.cam(RUN - 0.2, ((W0.x - 11.0, W0.y - 19.0, 1.4), (W0.x - 2.0, W0.y - 4.0, 1.9), 26), ((W0.x - 10.5, W0.y - 18.5, 1.4), (W0.x - 2.0, W0.y - 4.0, 2.1), 28),
      handheld=0.8)

S.finish(length=END)
