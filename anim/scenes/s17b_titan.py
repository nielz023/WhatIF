"""S17b · Dag 16 · de Titan, zonsondergang: de remmen falen (de cold open nog eens, sneller), de bouten
springen eruit, hij scheurt een stuk rail los, slaat het als een touw om de pilaar onder hem, en houdt vast.
De trein raakt hem met negentig. Witte flits. Stilte. Hij stopt, één meter voor het einde van de baan.

    blender -b -P anim/scenes/s17b_titan.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401
from titan import Track, pchip, riders, scream, cam_hide, coil_points, build_coil, rope_hands, build_rope  # noqa: E402

S = Scene("s17b", "pretpark", "zonsondergang")
TR = Track(S)
HP, G = TR.HP, TR.GROUND
HI = TR.HERO_I
S0X = HP.x - 0.6                                # waar hij staat als hij vasthoudt (net achter de pilaar)
A_GAP, B_GAP = HI + 5, HI + 16                  # het stuk rail dat hij losscheurt (achter hem)
PIL = Vector((HP.x, HP.y, 0))                   # de pilaar recht onder hem
PIL_R = 0.38 + HP.z * 0.008

# ---------------------------------------------------------------- tijdlijn
S.hud(16, "65,536x STRONGER", t0=0.3, tick=False)
S.sounds.append(dict(file="sfx/muziek_spanning", t=0.0, vol=0.3, cut=(0.0, None), keys=None, loop_to=60, duck=True,
                     fade_in=0.2, fade_out=0.05))
TENSION = S.sounds[-1]
S.ambience("sfx_pretpark_sfeer", 0.0, 60, vol=0.1)
AMB = S.sounds[-1]
l2 = S.say("S17-02", gap=0.3)
BANG = l2[0] + 2.45                             # 'fail'
S.sfx("sfx_remmen", BANG - 0.05, 0.55)
l3 = S.say("S17-03", gap=0.4)
KMH = l3[0] + 1.3                               # 'Ninety kilometers an hour.'
GRAB = l3[0] + 3.25                             # 'You grab the rails.'
BOLTS = l3[0] + 5.1                             # 'And the bolts start to go.'
PINGS = [BOLTS + 0.15, BOLTS + 0.75, BOLTS + 1.35]
S.sfx("sfx_trein_raast", l3[0] - 0.2, 0.45)
S.sfx("sfx_slowmo", GRAB - 0.35, 0.5)
S.sfx("sfx_metaal_buigt", GRAB + 0.05, 0.4)
S.sfx("sfx_bouten", BOLTS + 0.1, 0.55)
l4 = S.say("S17-04", gap=0.3)
NOTHING = l4[0] + 2.0                           # 'It's not heavy enough either.'
l5 = S.say("S17-05", gap=0.3)
PILLARS = l5[0] + 0.9
SUNK = l5[0] + 3.3                              # 'Each one sunk ten meters into the ground.'
l6 = S.say("S17-06", gap=0.3)
TEAR = l6[0]
WRAP = l6[0] + 2.0                              # 'wrap it around the nearest pillar'
HOLD = l6[0] + 4.0                              # 'and you hold on.'
S.sfx("sfx_rail_scheuren", TEAR + 0.2, 0.6)
S.sfx("sfx_staal", WRAP + 0.1, 0.4)
l7 = S.say("S17-07", gap=0.3)
IMPACT = l7[1] + 0.05
TENSION["loop_to"] = IMPACT
AMB["loop_to"] = IMPACT
S.sfx("sfx_inslag", IMPACT - 0.02, 0.8)
S.card(" ", IMPACT, IMPACT + 2.5, dim=1.0, bg=(1.0, 1.0, 1.0), fin=1, fout=34)
l8 = S.say("S17-08", at=IMPACT + 1.6)
ONE_M = l8[0] + 1.56                            # 'One meter from the end of the track.'
S.music("strijk_noot", l8[0] + 0.4, 60, vol=0.2, fade_in=1.5, fade_out=0.8)
STR = S.sounds[-1]
S.wait(1.3)
END = S.t
STR["loop_to"] = END
S.gauge("SPEED: 90 KM/H  ·  6 TONS", KMH, GRAB - 0.3, color=(1.0, 0.45, 0.2, 1))
S.text("↓ 10 M", SUNK + 0.3, l5[1] + 0.2, loc=(0.965, 0.30), size=64, color=CYAN, anchor=("RIGHT", "BOTTOM"))
S.text("SUNK INTO THE GROUND", SUNK + 0.5, l5[1] + 0.2, loc=(0.965, 0.22), size=44, color=CYAN, anchor=("RIGHT", "BOTTOM"))
S.gauge("1 METER LEFT", ONE_M + 0.2, END, color=GOLD)

# ---------------------------------------------------------------- de trein: D = afstand van de neus tot zijn plek
SLOW0, SLOW1 = GRAB - 0.4, l7[0]
D = pchip([(0.0, 66.0), (BANG, 63.6), (l3[0], 59.0), (l3[0] + 1.2, 48.0), (GRAB - 0.6, 34.0), (GRAB + 0.6, 31.0),
           (l4[0], 29.0), (l5[0], 25.5), (l6[0], 22.5), (l7[0], 18.5), (l7[0] + 1.0, 14.0), (IMPACT, S0X + 0.35 - HP.x),
           (IMPACT + 0.15, -1.1), (IMPACT + 0.5, -1.62), (IMPACT + 1.2, -1.73)])
TR.bake_train(D, END)
nose_x = lambda t: HP.x + D(t)
rate = lambda t: 1.0 - 0.85 * smooth(SLOW0, SLOW0 + 0.6, t) + 0.85 * smooth(SLOW1, SLOW1 + 0.4, t)

rs = riders(S, TR.cars)
scream(rs, 0.0, IMPACT, t_bang=BANG, rate=rate)
for n, ch in enumerate(rs):                     # na de klap: naar voren geslingerd, dan stil
    A.pose(ch, F(IMPACT + 0.1), "zitten_beugel", extra={"spine": (25, 0, 0), "head": (20, 0, 0)})
    A.expr(ch, F(IMPACT + 0.1), "geschrokken")
    A.pose(ch, F(IMPACT + 0.8), "zitten_beugel", extra={"spine": (-6, 0, 0), "head": (-4, 0, 0)})
    A.expr(ch, F(IMPACT + 0.8), "bang", ogen_knijp=0.4)
    A.key_prop(ch.rig, "mond_open", 0.2, F(IMPACT + 0.8))

# vonken bij de remmen
brake = TR.car_matrix(TR.car_s(D(BANG), 2)).translation
S.flash(brake, BANG, size=0.5, color=(1.0, 0.8, 0.4), strength=8)
S.debris(brake + V(0, 0, -0.2), BANG, n=30, size=(0.015, 0.035), mat=S.mat("vonk", (1.0, 0.65, 0.2), 14), speed=(3, 7), up=1.0, life=1.0,
         floor=brake.z - 30, name="Vonk")

# ---------------------------------------------------------------- het gat in de rail, het losse stuk, de bouten
piece = TR.rail_gap(A_GAP, B_GAP)
pivot = piece.location.copy()
L_PIECE = (TR.rail_pt(A_GAP) - pivot).length


def lift(t):
    """Hoek (graden) van het losse stuk tijdens het scheuren."""
    return 13.0 * smooth(TEAR + 0.3, TEAR + 1.4, t) + 1.5 * math.sin(t * 40) * smooth(TEAR + 0.3, TEAR + 0.6, t) * (1 - smooth(TEAR + 1.2, TEAR + 1.4, t))


tfr = list(range(F(TEAR) - 1, F(WRAP) + 1))
bake(piece, "rotation_euler", tfr, [(0.0, -math.radians(lift((f - 1) / FPS)), 0.0) for f in tfr])
bake(piece, "location", tfr, [tuple(pivot + V(0, 0, 0.5 * smooth(TEAR + 1.45, TEAR + 1.7, (f - 1) / FPS))) for f in tfr])
visible(piece, WRAP, False)
for k in range(5):                              # bouten die het stuk loslaten
    i = A_GAP + 1 + k * 2
    S.debris(TR.rail_pt(i) + V(0, 0, -0.08), TEAR + 0.35 + k * 0.18, n=2, size=(0.04, 0.06), mat=S.mat("bout", (0.78, 0.78, 0.74)),
             speed=(2.5, 4.5), up=1.6, life=1.2, floor=G - 0.05, name="Bout_los")
S.debris(pivot + V(0, 0, 0.05), TEAR + 1.45, n=18, size=(0.015, 0.03), mat=S.mat("vonk", (1.0, 0.65, 0.2), 14), speed=(2, 5), up=1.5,
         life=0.8, floor=G - 3, name="Vonk")

RAIL_R = V(HP.x + 0.30, HP.y - TR.GAUGE, G + 0.13)
RAIL_L = V(HP.x + 0.30, HP.y + TR.GAUGE, G + 0.13)
bolt_at = [TR.rail_pt(HI - 3 - 2 * k) + V(0, 0, -0.12) for k in range(3)]
for k, (tp, q) in enumerate(zip(PINGS, bolt_at)):
    S.flash(q + V(0, 0, 0.1), tp, size=0.08)
    S.debris(q, tp, n=1, size=(0.05, 0.06), mat=S.mat("bout", (0.78, 0.78, 0.74)), speed=(1.0, 1.4), up=2.5, life=2.5,
             floor=G - 3, name="Bout_ping")
    S.sfx("sfx_hud_tik", tp, 0.25)

# ---------------------------------------------------------------- de rail als touw om de pilaar
coil_pts = coil_points(TR)
coil = build_coil(TR)
coil.data.bevel_factor_mapping_end = "SPLINE"
coil.data.bevel_factor_end = 0.0
coil.data.keyframe_insert("bevel_factor_end", frame=F(WRAP + 0.15))
coil.data.bevel_factor_end = 1.0
coil.data.keyframe_insert("bevel_factor_end", frame=F(WRAP + 1.5))
show(coil, WRAP)
ENTRY = coil_pts[0]
hands = lambda x: rope_hands(TR, x)


def rope(name, x, t0, t1):
    o = build_rope(TR, name, x)
    show(o, t0, t1)
    return o


X_AFTER = D(END) + HP.x - 0.35              # = HP.x - X_PUSH (titan.py)
rope("Rail_touw_voor", S0X, HOLD, IMPACT)
rope("Rail_touw_na", X_AFTER, IMPACT, None)
for t, p in ((WRAP + 0.2, ENTRY), (WRAP + 0.8, coil_pts[32]), (WRAP + 1.3, coil_pts[60])):
    S.puff(p, t, n=4, r=(0.08, 0.16), grow=2.0, dur=0.9, color=(0.75, 0.73, 0.70), rise=0.3, spread=0.3)
    S.debris(p, t, n=8, size=(0.02, 0.05), color=(0.7, 0.7, 0.68), speed=(1, 3), up=0.8, life=1.0, floor=0.0, name="Betonsplinter")

# de 'einde van de baan'-maat (1 meter)
mk = S.mat("maat_cyaan", (0.35, 0.95, 1.0), 5)
END_X = TR.rail_pt(A_GAP - 1).x
NOSE_STOP = HP.x + D(END)
for nm, x in (("Maat_a", NOSE_STOP), ("Maat_b", END_X)):
    o = T.cyl(nm, (x, HP.y - 1.05, G - 0.05), 0.02, 0.5, mk, seg=8, ol=0)
    show(o, ONE_M + 0.1)
o = T.tube("Maat_lijn", [(NOSE_STOP, HP.y - 1.05, G + 0.2), (END_X, HP.y - 1.05, G + 0.2)], 0.015, mk)
show(o, ONE_M + 0.1)
o = T.text("Maat_tekst", "1 M", ((NOSE_STOP + END_X) / 2, HP.y - 1.08, G + 0.32), 0.22, mk, extrude=0.0)
show(o, ONE_M + 0.1)

# ---------------------------------------------------------------- doorsnede: de pilaar gaat 10 m de grond in
CUT0, CUT1 = SUNK - 0.1, l6[0]
soil = T.box("Doorsnede_aarde", (PIL.x, PIL.y + 14, -25), (36, 28, 24.8), S.mat("aarde", (0.42, 0.27, 0.16)), bevel=0, ol=0.02)
grass = T.box("Doorsnede_gras", (PIL.x, PIL.y + 14, -0.2), (36, 28, 0.2), S.mat("gras_rand", (0.24, 0.50, 0.18)), bevel=0, ol=0.02)
deep = T.cyl("Pilaar_ondergronds", (PIL.x, PIL.y, -10.0), PIL_R, 10.0, S.obj("Titan_pilaren_beton").active_material, seg=24, ol=0.02)
for k in range(11):
    T.box(f"Maat_streep_{k}", (PIL.x + 0.75, PIL.y - 0.4, -k - 0.02), (0.3 if k % 5 else 0.6, 0.04, 0.04), mk, bevel=0, ol=0)
tick = T.tube("Maat_diepte", [(PIL.x + 0.75, PIL.y - 0.4, 0.0), (PIL.x + 0.75, PIL.y - 0.4, -10.0)], 0.03, mk)
lbl = T.text("Maat_10m", "10 M", (PIL.x + 1.9, PIL.y - 0.45, -5.4), 0.9, mk, extrude=0.0)
for o in (soil, grass, deep, tick, lbl) + tuple(bpy.data.objects[f"Maat_streep_{k}"] for k in range(11)):
    show(o, CUT0, CUT1)
for nm in ("Gras", "Hoofdpad", "Plein_botsauto"):
    if S.obj(nm):
        cam_hide(S.obj(nm), CUT0, CUT1)

# ---------------------------------------------------------------- de held
held = S.actor("hoofdpersonage", V(HP.x, HP.y, G), 90)
GRAB_SPEC = dict(pose="schrap", crouch=(0.30, 15.0), feet=((0.22, 0.0, 0), (-0.22, 0.0, 0)),
                 body={"spine": (10, 0, 0), "chest": (8, 0, 0), "head": (-28, 0, 0)})
S.beat(held, 0.0, "vuisten", face="nerveus", face_amt=0.8, look=(0, 0.3))
S.beat(held, l3[0] + 0.5, "vuisten", face="vastberaden", face_amt=0.8, look=(0, 0.3), body={"head": (-6, 0, 0)})
S.beat(held, GRAB - 0.5, "schrap", crouch=(0.18, 12.0), feet=((0.14, 0.03, 0), (-0.14, 0.03, 0)), face="vastberaden", look=(0, -0.5),
       body={"spine": (8, 0, 0), "head": (6, 0, 0)})
for side, tgt in (("L", RAIL_L), ("R", RAIL_R)):
    S.reach(held, GRAB - 0.5, side, tgt, inf=0.0)
    S.reach(held, GRAB - 0.1, side, tgt, inf=1.0)
S.beat(held, GRAB - 0.1, **GRAB_SPEC, face="inspanning", face_amt=0.7, look=(0, 0.4))
S.beat(held, BOLTS - 0.3, **GRAB_SPEC, face="inspanning", face_amt=0.9, look=(0, 0.45))
SCARED = dict(pupil_klein=1.0, ogen_wijd=1.0, mond_verdrietig=0.6, mond_lach=0.0)
S.beat(held, BOLTS + 0.2, **GRAB_SPEC, face="bang", face_amt=0.9, look=(0.35, -0.65), **SCARED)
S.beat(held, l4[0] + 1.2, **GRAB_SPEC, face="bang", face_amt=1.0, look=(0.45, -0.7), **SCARED)
for side, tgt in (("L", RAIL_L), ("R", RAIL_R)):
    S.reach(held, NOTHING - 0.1, side, tgt, inf=1.0)
    S.reach(held, NOTHING + 0.3, side, tgt, inf=0.0)
S.beat(held, NOTHING + 0.3, "vuisten", face="nerveus", face_amt=1.0, look=(-0.7, 0.1), body={"head": (0, 55, 0), "neck": (0, 15, 0)})
S.beat(held, NOTHING + 1.2, "vuisten", face="nerveus", face_amt=1.0, look=(0.7, 0.1), body={"head": (0, -55, 0), "neck": (0, -15, 0)})
S.beat(held, l5[0] + 0.1, "vuisten", face="verbaasd", face_amt=0.8, look=(0, -0.8), body={"head": (28, 0, 0), "neck": (8, 0, 0)})
S.beat(held, PILLARS + 0.4, "vuisten", face="vastberaden", face_amt=0.9, look=(0, -0.7), body={"head": (24, 0, 0)})
S.hold(held, TEAR - 0.05)

# scheuren: achter hem, gezicht naar -x, het eind van het stuk omhoog trekken
TEAR_AT = V(TR.rail_pt(A_GAP).x + 0.48, HP.y - 0.36, G)
S.teleport(held, TEAR, TEAR_AT, -90)


def piece_end(t, back=0.0):
    a = math.radians(lift(t))
    r = L_PIECE - back
    return pivot + V(r * math.cos(a), 0, r * math.sin(a) + 0.5 * smooth(TEAR + 1.45, TEAR + 1.7, t))


S.beat(held, TEAR, "schrap", crouch=(0.32, 24.0), feet=((0.2, 0.1, 0), (-0.2, -0.15, 0)), face="inspanning", face_amt=0.8, look=(0, -0.4),
       body={"spine": (12, 0, 0), "head": (-10, 0, 0)})
S.beat(held, TEAR + 0.9, "schrap", crouch=(0.18, 6.0), feet=((0.2, 0.1, 0), (-0.2, -0.15, 0)), face="inspanning", face_amt=1.0,
       mouth=0.5, look=(0, 0.1), body={"spine": (-6, 0, 0), "head": (-6, 0, 0)})
S.beat(held, TEAR + 1.5, "schrap", crouch=(0.06, -6.0), feet=((0.2, 0.1, 0), (-0.2, -0.15, 0)), face="schreeuw", face_amt=0.9,
       mouth=0.8, look=(0, 0.5), body={"spine": (-12, 0, 0), "head": (-18, 0, 0)})
for side in "LR":
    S.reach(held, TEAR - 0.05, side, None, inf=0.0)
for t in (TEAR, TEAR + 0.45, TEAR + 0.9, TEAR + 1.25, TEAR + 1.5, WRAP - 0.05):
    S.reach(held, t, "L", piece_end(t, 0.05), inf=1.0)
    S.reach(held, t, "R", piece_end(t, 0.3), inf=1.0)

# vasthouden: terug op de baan, schrap, het touw in beide handen
S.teleport(held, HOLD, V(S0X, HP.y, G), 90)
BRACE = dict(pose="schrap", crouch=(0.22, 10.0), feet=((0.16, 0.25, 0), (-0.16, -0.35, 0)), body={"spine": (8, 0, 0), "head": (-14, 0, 0)})
rh0, lh0 = hands(S0X)
rh1, lh1 = hands(X_AFTER)
for t, (rh, lh) in ((HOLD, (rh0, lh0)), (IMPACT, (rh0, lh0)), (IMPACT + 0.5, (rh1, lh1)), (END, (rh1, lh1))):
    S.reach(held, t, "R", rh, inf=1.0)
    S.reach(held, t, "L", lh, inf=1.0)
S.beat(held, HOLD, **BRACE, face="vastberaden", face_amt=1.0, look=(0, 0.3))
S.beat(held, l7[0] + 0.2, **BRACE, face="schreeuw", face_amt=0.8, mouth=0.7, look=(0, 0.35))
S.beat(held, IMPACT - 0.05, **BRACE, face="inspanning", face_amt=1.0, mouth=0.5, look=(0, 0.3), ogen_knijp=0.8)
S.beat(held, IMPACT + 0.3, pose="schrap", crouch=(0.25, -4.0), feet=((0.16, 0.1, 0), (-0.16, -0.5, 0)),
       body={"spine": (-2, 0, 0), "chest": (0, 0, 0), "head": (-12, 0, 0)}, face="inspanning", face_amt=1.0, mouth=0.4, ogen_knijp=1.0)
S.hold(held, l8[0] + 0.2)
S.beat(held, l8[0] + 1.0, pose="schrap", crouch=(0.22, -3.0), feet=((0.16, 0.1, 0), (-0.16, -0.5, 0)),
       body={"spine": (-2, 0, 0), "chest": (0, 0, 0), "head": (-6, 0, 0)}, face="verbaasd", face_amt=0.6, look=(0, 0.2), mouth=0.2)
S.beat(held, ONE_M + 0.5, pose="schrap", crouch=(0.2, -2.0), feet=((0.16, 0.1, 0), (-0.16, -0.5, 0)),
       body={"spine": (-1, 0, 0), "chest": (0, 0, 0), "head": (-2, 0, 0)}, face="verdrietig", face_amt=0.5, look=(0, 0.1), mouth=0.15)
S.hold(held, END)
# meegeduwd door de trein na de klap
ifr = list(range(F(IMPACT) - 1, F(END) + 1))
bake(held.rig, "location", ifr, [(min(S0X, nose_x((f - 1) / FPS) - 0.35), HP.y, G) for f in ifr])
S.puff(V(S0X, HP.y, G + 0.1), IMPACT + 0.05, n=10, r=(0.2, 0.45), grow=2.5, dur=1.8, color=(0.8, 0.78, 0.74), rise=0.8, spread=1.0)
S.debris(V(S0X - 0.2, HP.y, G + 0.05), IMPACT + 0.05, n=40, size=(0.015, 0.03), mat=S.mat("vonk", (1.0, 0.65, 0.2), 14), speed=(2, 6),
         up=1.2, direction=(-1, 0, 0.3), spread=0.8, life=0.9, floor=G - 3, name="Vonk")

# ---------------------------------------------------------------- camera
car0 = lambda t: (lambda s: (TR.P(s) + TR.frame_at(s)[2] * 0.25, *TR.frame_at(s)))(TR.car_s(D(t), 0))
H = lambda x, y, z: V(HP.x + x, HP.y + y, G + z)
S.cam(0.0, None, fn=lambda t: (vlerp((47, -64, 9.5), (49, -60, 10.0), t / 3.0), vlerp((80, -12, 22), TR.nose(D(t)), 0.55), 30),
      shake=lambda t: max(0.0, 2.2 - 1.6 * abs(t - BANG)) if t > BANG - 0.1 else 0.0)
S.cam(l3[0] - 0.1, None, fn=lambda t: (lambda c: (c[0] + c[1] * 2.3 + c[3] * 1.25, c[0] - c[1] * 1.2 + c[3] * 0.8, 21))(car0(t)),
      shake=lambda t: 1.1)
S.cam(KMH - 0.1, None, fn=lambda t: (V(40.5, -19.5, 3.4), TR.nose(D(t)) - V(0, 0, 0.6), 24), shake=lambda t: 0.6)
S.cam(GRAB - 0.25, (H(2.7, -1.7, 1.05), H(0.0, 0, 0.72), 30), (H(2.5, -1.55, 1.0), H(0.0, 0, 0.72), 31),
      shake=lambda t: max(0.0, 1.2 - (t - GRAB) * 2.0) if t > GRAB else 0.0)
b2 = bolt_at[1]
S.cam(BOLTS - 0.2, (b2 + V(2.0, -0.55, 0.22), b2 + V(-0.4, 0.15, 0.05), 32), (b2 + V(1.75, -0.5, 0.22), b2 + V(-0.4, 0.15, 0.05), 32),
      dof=4.0, shake=lambda t: sum(max(0.0, 0.9 - (t - tp) * 2.5) for tp in PINGS if t > tp))
S.cam(l4[0] - 0.1, (H(1.0, -3.4, 1.05), H(0.5, 0, 0.75), 30), (H(0.9, -3.0, 0.95), H(0.5, 0, 0.75), 32), shake=lambda t: 0.5)
S.cam(NOTHING, (H(-2.7, 2.3, 2.0), H(2.4, -0.3, 0.8), 26), (H(-2.45, 2.1, 1.95), H(2.4, -0.3, 0.8), 27))
S.cam(l5[0] - 0.1, (H(3.2, -4.4, -2.3), H(0, 0, -0.6), 24), (H(2.5, -3.5, -2.2), H(0, 0, -0.4), 24))
S.cam(CUT0, ((PIL.x + 4.5, PIL.y - 19.0, -1.0), (PIL.x, PIL.y, -3.6), 22), ((PIL.x + 4.0, PIL.y - 17.5, -1.3), (PIL.x, PIL.y, -3.8), 22))
S.cam(TEAR - 0.05, ((TEAR_AT.x + 2.0, HP.y - 3.4, G + 1.1), (TEAR_AT.x - 0.6, HP.y - 0.4, G + 0.9), 28),
      ((TEAR_AT.x + 1.8, HP.y - 3.1, G + 1.2), (TEAR_AT.x - 0.8, HP.y - 0.4, G + 1.3), 28),
      shake=lambda t: max(0.0, 1.4 - abs(t - TEAR - 1.45) * 3.0))
S.cam(WRAP, ((PIL.x + 1.5, PIL.y - 2.4, 1.45), (PIL.x, PIL.y - 0.2, 1.5), 34), ((PIL.x + 1.3, PIL.y - 2.1, 1.5), (PIL.x, PIL.y - 0.2, 1.5), 36))
S.cam(HOLD, ((S0X - 2.6, HP.y - 1.9, G + 1.2), (S0X + 3.0, HP.y, G + 1.0), 28), ((S0X - 2.4, HP.y - 1.7, G + 1.15), (S0X + 3.0, HP.y, G + 1.0), 30))
S.cam(l7[0], None, fn=lambda t: (vlerp(H(-3.4, -0.75, 1.35), H(-3.0, -0.7, 1.3), smooth(l7[0], IMPACT, t)), H(6.0, 0.3, 1.2), 30),
      shake=lambda t: 0.3 + 1.8 * smooth(l7[0] + 0.8, IMPACT, t))
S.cam(IMPACT, ((X_AFTER - 2.4, HP.y - 5.2, G + 0.9), (X_AFTER - 0.1, HP.y, G + 0.8), 28),
      ((X_AFTER - 2.2, HP.y - 4.6, G + 0.85), (X_AFTER - 0.2, HP.y, G + 0.75), 30))

S.finish(length=END)
