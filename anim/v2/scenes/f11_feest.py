"""F11 · Dag 5 → dag 7 · de keuken wordt een feest. Elke dag probeert hij wakker te blijven (19, 23, 25 uur).
Tussen de sneden schuift zijn familie een paar centimeter: papa zet de taart neer, mama steekt de negen kaarsjes
aan en schrijft WE'LL WAIT FOR YOU op het whiteboard. Dag 7 · 1.000.000x: een traan op mama's wang, opa en oma
in de deuropening met een cadeau, zijn beste vriend midden in een sprint bij het tuinhek.

    blender -b -P anim/v2/scenes/f11_feest.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403
from lib import huis as HU  # noqa: E402
from feest import party_set  # noqa: E402

S = Scene2("f11", "keuken", "verjaardag")
rnd = random.Random(11)

TX, TY, TZ = 0.2, -0.6, 0.76
SEAT = S.obj("Stoel_2").location.copy()          # (0.58, -1.22): hij, gezicht naar de tafel (+y)
BRO_SEAT = S.obj("Stoel_4").location.copy()      # (0.58, 0.02): het broertje, tegenover hem
CAKE = V(0.5, -0.6, TZ)                          # de taart komt naar hem toe
WB = V(2.04, 1.362, 0.78)                        # whiteboard op de koelkast
DOORWAY = V(-2.46, 0.95, 0)
GATE = V(-0.2, 8.4, 0)                           # net binnen het tuinhek
ROBE = (0.86, 0.62, 0.76)

# ---------------------------------------------------------------- set (gedeeld met F12)
O = party_set(S)
cake, flames, glow, plates, lighter, gift = O["cake"], O["flames"], O["glow"], O["plates"], O["lighter"], O["gift"]
wb_lines = {5: O["wb5"], 6: O["wb6"]}

# ---------------------------------------------------------------- tijdlijn
l1 = S.say("F11-01", gap=0.6)
d1 = l1[1] - l1[0]
ST = [l1[0] - 0.4, l1[0] + 0.17 * d1, l1[0] + 0.30 * d1, l1[0] + 0.47 * d1, l1[0] + 0.58 * d1, l1[0] + 0.72 * d1]
CLOSE5, CLOSE6 = ST[3] - 0.75, ST[5] - 0.6       # zijn ogen vallen dicht, zwart
# (dag, snelheid, wakker om, uren wakker) per toestand
DAYS = [(5, 10_000, 8 * 3600 + 59 * 60 + 50.0, 3), (5, 10_000, 8 * 3600 + 59 * 60 + 50.0, 11), (5, 10_000, 8 * 3600 + 59 * 60 + 50.0, 19),
        (6, 100_000, 8 * 3600 + 59 * 60 + 59.0, 8), (6, 100_000, 8 * 3600 + 59 * 60 + 59.0, 23), (7, 1_000_000, 8 * 3600 + 59 * 60 + 59.9, 25)]
l2 = S.say("F11-02", at=l1[1] + 0.8)
d2 = l2[1] - l2[0]
WIDE2 = l2[0] + 0.66 * d2                        # 'But he wasn't doing it in a world where nothing moves.'
l3 = S.say("F11-03", gap=0.9)
l4 = S.say("F11-04", gap=0.5)
l5 = S.say("F11-05", gap=0.8)
d5 = l5[1] - l5[0]
TEAR = l5[0] + 0.52 * d5                         # 'There's a tear on your mom's cheek.'
l6 = S.say("F11-06", gap=0.7)
l7 = S.say("F11-07", gap=0.8)
l8 = S.say("F11-08", gap=0.6)
END = l8[1] + 1.6


def state(t):
    k = 0
    for i, ts in enumerate(ST):
        if t >= ts:
            k = i
    return k


def his_h(t):
    k = state(t)
    return DAYS[k][3] + max(0.0, t - ST[k]) / 3600


def real_clock(t):
    day, spd, wake, _ = DAYS[state(t)]
    return wake + his_h(t) * 3600 / spd


S.hud2(5, "10,000x", clock=lambda t: hms(real_clock(t), 3, "TUE"), t0=0.3, t1=ST[3],
       awake=lambda t: awake(his_h(t), rate=0)(t), awake_t0=0.5)
S.hud2(6, "100,000x", clock=lambda t: hms(real_clock(t), 3, "TUE"), t0=ST[3], t1=ST[5],
       awake=lambda t: awake(his_h(t), rate=0)(t), awake_t0=ST[3] + 0.1, tick=True)
S.hud2(7, "1,000,000x", clock=lambda t: hms(real_clock(t), 4, "TUE"), t0=ST[5],
       awake=lambda t: awake(his_h(t), rate=0)(t), awake_t0=ST[5] + 0.1, tick=True)
S.gauge2("RECORD: 11 DAYS AWAKE", l2[0] + 0.4, WIDE2, color=GOLD, row=0)
S.real(l2[0] + 0.3, WIDE2 - 0.2)
S.gauge2("1 SECOND = 12 DAYS", l5[0] + 1.6, TEAR - 0.2, color=GOLD, row=0)
S.card("", CLOSE5 + 0.3, ST[3], dim=1.0, fin=6, fout=4)
S.card("", CLOSE6 + 0.3, ST[5], dim=1.0, fin=6, fout=4)
S.music("strijkers_warm", 0.0, l7[0] - 0.2, vol=0.14, fade_in=1.5, fade_out=1.5)
S.music("piano_zacht", l7[0] + 0.5, END, vol=0.1, fade_in=2.0, fade_out=1.5)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.04)
S.sfx("sfx_klok_motief", 0.4, 0.14)
S.sfx("sfx_klok_motief", l3[0] - 0.4, 0.12)

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", SEAT, 180)
SIT_H, zh = sit(held)
bro = S.actor("broertje_dino", V(1.6, -0.2, 0), heading(V(1.6, -0.2, 0), BRO_SEAT))
SIT_B, zb = sit(bro)
mama = S.actor("mama", V(1.25, -0.35, 0), heading(V(1.25, -0.35, 0), CAKE), outfit=dict(shirt=ROBE, broek=ROBE))
papa = S.actor("papa", V(-0.75, 1.15, 0), heading(V(-0.75, 1.15, 0), CAKE))
opa = S.actor("opa", V(-2.1, 1.22, 0), heading(V(-2.1, 1.22, 0), CAKE))
oma = S.actor("oma", V(-2.48, 0.78, 0), heading(V(-2.48, 0.78, 0), CAKE))
friend = S.actor("beste_vriend", GATE, 0)
for ch in (held, bro, mama, papa, opa, oma, friend):
    S.reach(ch, 0.0, "L", None, 0.0)
    S.reach(ch, 0.0, "R", None, 0.0)
for ch in (opa, oma, friend):                    # komen pas op dag 6 in beeld
    for o in ch.rig.children_recursive:
        show(o, ST[3])


def at_cut(ch, k, loc, rot, **beat):
    """Bevroren figuur: nieuwe stand op snede k (houdt de vorige vast tot vlak ervoor)."""
    t = ST[k] if k > 0 else 0.0
    if k > 0:
        S.teleport(ch, t, loc, rot)
        if ch.last:
            S._beat(ch, t - 1.0 / FPS, ch.last)
    else:
        S.place(ch, 0.0, loc, rot)
    S.beat(ch, t, **beat)


def obj_cut(o, k, loc, rot=None):
    t = ST[k] if k > 0 else 0.0
    if k > 0:
        key(o, t - 1.0 / FPS, loc=tuple(o.location), rot=tuple(math.degrees(a) for a in o.rotation_euler), interp="CONSTANT")
    key(o, t, loc=loc, rot=rot if rot is not None else tuple(math.degrees(a) for a in o.rotation_euler), interp="CONSTANT")


def hands_to(ch, k, l=None, r=None):
    t = ST[k] if k > 0 else 0.0
    for side, p in (("L", l), ("R", r)):
        if k > 0:
            S.reach(ch, t - 1.0 / FPS, side, *(ch._hand.get(side, (None, 0.0))))
        S.reach(ch, t, side, p, 1.0 if p is not None else 0.0)
        ch._hand = getattr(ch, "_hand", {})
        ch._hand[side] = (p, 1.0 if p is not None else 0.0)


for ch in (held, bro, mama, papa, opa, oma, friend):
    ch._hand = {}

# papa met de taart -> taart op tafel -> bordjes, lachend om zijn eigen grap
P0, P1, P2 = V(-0.75, 1.15, 0), V(-0.35, 0.25, 0), V(-0.42, -0.62, 0)
CAKE0 = P0 + V(0.25, -0.38, 0.9)
CAKE1 = P1 + V(0.35, -0.3, 0.9)
obj_cut(cake, 0, CAKE0)
at_cut(papa, 0, P0, heading(P0, CAKE), pose="staan", face="blij", face_amt=0.7, at=CAKE0 + V(0, 0, 0.1))
hands_to(papa, 0, CAKE0 + V(-0.12, 0.08, 0.04), CAKE0 + V(0.12, -0.08, 0.04))
obj_cut(cake, 1, CAKE1)
at_cut(papa, 1, P1, heading(P1, CAKE), pose="staan", face="blij", face_amt=0.8, at=CAKE1 + V(0, 0, 0.1), feet=((0, 0.12, 0.05), (0, -0.1, 0.0)))
hands_to(papa, 1, CAKE1 + V(-0.13, 0.06, 0.04), CAKE1 + V(0.13, -0.08, 0.04))
obj_cut(cake, 2, CAKE)
PL = P2 + V(0.32, 0.0, 0.95)
at_cut(papa, 2, P2, 90, pose="staan", face="blij", face_amt=0.8, at=CAKE + V(0, 0, 0.25))
hands_to(papa, 2, PL + V(0, 0.12, -0.02), PL + V(0, -0.12, -0.02))
obj_cut(plates, 2, PL + V(0, 0, -0.05))
at_cut(papa, 3, P2 + V(0.02, 0, 0), 92, pose="staan", face="lach", face_amt=0.7, at=S.head(held, 0) + V(0, 0, 0.2), mouth=0.4)
hands_to(papa, 3, PL + V(0.02, 0.12, -0.02), PL + V(0.02, -0.12, -0.02))
obj_cut(plates, 3, PL + V(0.02, 0, -0.05))
at_cut(papa, 5, P2 + V(0.03, 0, 0), 93, pose="staan", face="lach", face_amt=1.0, at=S.head(held, 0) + V(0, 0, 0.2), mouth=0.6,
       body={"spine": (-6, 0, 0), "head": (-10, 0, 4)})
hands_to(papa, 5, PL + V(0.03, 0.12, -0.02), PL + V(0.03, -0.12, -0.02))
obj_cut(plates, 5, PL + V(0.03, 0, -0.05))

# mama met de aansteker -> kaarsjes aan -> whiteboard (stift), daarna kijkt ze naar hem, met een traan
M0, M1 = V(1.25, -0.35, 0), V(1.0, -0.42, 0)
MB = V(1.62, 0.92, 0)                            # bij het whiteboard
MF = V(1.35, 0.72, 0)                            # dag 7: ze heeft zich naar hem omgedraaid
marker = T.cyl("Stift_mama", (0, 0, 0), 0.012, 0.13, S.mat("stift_rood", (0.85, 0.12, 0.1)), rot=(90, 0, 0), seg=10, ol=0)
obj_cut(lighter, 0, M0 + V(-0.32, -0.12, 0.92), (0, 0, 200))
at_cut(mama, 0, M0, heading(M0, CAKE0), pose="staan", face="blij", face_amt=0.5, at=CAKE0 + V(0, 0, 0.2))
hands_to(mama, 0, None, M0 + V(-0.32, -0.12, 0.92) + V(0.06, 0, 0))
obj_cut(lighter, 1, M0 + V(-0.32, -0.1, 0.94), (0, 0, 200))
at_cut(mama, 1, M0 + V(-0.03, 0, 0), heading(M0, CAKE1), pose="staan", face="blij", face_amt=0.6, at=CAKE1 + V(0, 0, 0.2))
hands_to(mama, 1, None, M0 + V(-0.32, -0.1, 0.94) + V(0.06, 0, 0))
CANDLE = CAKE + V(0.08, 0.0, 0.33)
obj_cut(lighter, 2, CANDLE + V(0.2, 0.0, 0.01), (0, 0, 180))
at_cut(mama, 2, M1, heading(M1, CAKE), pose="staan", face="blij", face_amt=0.4, at=CANDLE, body={"spine": (12, 0, 0)})
hands_to(mama, 2, None, CANDLE + V(0.3, 0.0, 0.0))
WRITE = WB + V(-0.08, -0.06, -0.12)
obj_cut(lighter, 3, CAKE + V(0.32, 0.22, 0.02), (0, 0, 150))
at_cut(mama, 3, MB, heading(MB, WB), pose="staan", face="nerveus", face_amt=0.5, at=WB + V(0, 0, -0.1))
hands_to(mama, 3, None, WRITE + V(-0.04, -0.04, 0))
at_cut(mama, 4, MB + V(-0.04, -0.03, 0), heading(MB, WB) + 25, pose="staan", face="verdrietig", face_amt=0.5, at=WB + V(0, 0, -0.1))
hands_to(mama, 4, None, WRITE + V(0.06, -0.08, -0.15))
at_cut(mama, 5, MF, heading(MF, SEAT), pose="staan", face="verdrietig", face_amt=0.9, at=S.head(held, 0) + V(0, 0, 0.1))
hands_to(mama, 5, MF + V(-0.12, -0.18, 1.18), MF + V(-0.08, -0.32, 1.05))
grab(S, marker, mama, ST[3], "hand.R", mode="loc", offset=(0, 0.02, 0))
show(marker, ST[3])
grab(S, lighter, mama, 0.0, "hand.R", mode="loc", offset=(0.0, 0.0, -0.02), release=ST[3])
for o in wb_lines[5]:
    show(o, ST[3])
for o in wb_lines[6]:
    show(o, ST[4])
# kaarsjes: dag 5 (19 uur) de eerste vier, dag 6 allemaal
for i, f in enumerate(flames):
    show(f, ST[2] if i < 4 else ST[3])
show(glow, ST[2])

# het broertje komt binnen, gaat zitten, leunt naar de kaarsjes (wangen vol lucht: dat is voor straks)
B0, B1 = V(1.6, -0.2, 0), V(1.15, 0.35, 0)
at_cut(bro, 0, B0, heading(B0, BRO_SEAT), pose="staan", face="blij", face_amt=0.8, at=CAKE0 + V(0, 0, 0.2),
       feet=((0, 0.14, 0.06), (0, -0.1, 0.0)))
at_cut(bro, 1, B1, heading(B1, BRO_SEAT), pose="staan", face="blij", face_amt=0.9, at=CAKE1 + V(0, 0, 0.1),
       feet=((0, -0.1, 0.0), (0, 0.14, 0.06)))
at_cut(bro, 2, BRO_SEAT + V(0, 0, zb), 0, **SIT_B, pose="ontspannen", face="blij", face_amt=1.0, at=CAKE + V(0, 0, 0.3))
at_cut(bro, 3, BRO_SEAT + V(0, -0.03, zb), 0, **SIT_B, pose="ontspannen", face="blij", face_amt=1.0, at=CAKE + V(0, 0, 0.3),
       body={"spine": (10, 0, 0)})
at_cut(bro, 5, BRO_SEAT + V(0, -0.06, zb), 0, **SIT_B, pose="ontspannen", face="blij", face_amt=0.8, at=CAKE + V(0, 0, 0.3),
       body={"spine": (16, 0, 0), "head": (6, 0, 0)}, mouth=0.0, mond_O=0.35)
hands_to(bro, 5, CAKE + V(-0.3, 0.3, 0.02), CAKE + V(0.0, 0.32, 0.02))

# opa en oma in de deuropening (oma met het cadeau); opa midden in het visverhaal
at_cut(oma, 3, V(-2.4, 0.78, 0), heading(V(-2.4, 0.78, 0), CAKE), pose="staan", face="blij", face_amt=0.7, at=S.head(held, 0))
OG = V(-2.4, 0.78, 0) + V(0.28, -0.08, 0.85)
hands_to(oma, 3, OG + V(-0.04, 0.17, 0.05), OG + V(0.04, -0.17, 0.05))
obj_cut(gift, 0, gift.location.copy())
obj_cut(gift, 3, OG + V(0, 0, -0.04), (0, 0, heading(V(-2.4, 0.78, 0), CAKE)))
at_cut(oma, 5, V(-2.36, 0.77, 0), heading(V(-2.4, 0.78, 0), CAKE), pose="staan", face="blij", face_amt=0.8, at=S.head(held, 0))
hands_to(oma, 5, OG + V(0.0, 0.17, 0.05), OG + V(0.08, -0.17, 0.05))
obj_cut(gift, 5, OG + V(0.04, -0.01, -0.04))
TALK = arms(arm("R", (0.35, 0.55, -0.55), (0.1, 0.75, 0.65)))   # vertelhand omhoog
at_cut(opa, 3, V(-2.05, 1.22, 0), heading(V(-2.05, 1.22, 0), CAKE), pose="staan", face="lach", face_amt=0.6,
       at=S.head(held, 0) + V(0, 0, 0.3), mouth=0.6, arms=TALK)
at_cut(opa, 5, V(-2.0, 1.2, 0), heading(V(-2.05, 1.22, 0), CAKE) - 4, pose="staan", face="lach", face_amt=0.8,
       at=S.head(held, 0) + V(0, 0, 0.3), mouth=0.7, arms=TALK)

# de beste vriend: midden in een sprint, één voet in de lucht, telefoon in zijn hand
at_cut(friend, 3, GATE + V(0, 0.15, 0), 0, pose="rennen", face="inspanning", face_amt=0.7, look=(0, 0))
run_pose(S, friend, ST[3], front="L", look=(0, 0))
at_cut(friend, 5, GATE, 0, pose="rennen", face="inspanning", face_amt=0.8, look=(0, 0))
run_pose(S, friend, ST[5], front="L", look=(0, 0))
phone = T.box("Telefoon_vriend", (0, 0, 0), (0.035, 0.008, 0.07), S.mat("telefoon_zwart", (0.08, 0.08, 0.1)), bevel=0.004, ol=0)
grab(S, phone, friend, 0.0, "hand.R", loc=(0.0, 0.07, 0.02), rot=(90, 0, 180))

# ---------------------------------------------------------------- hij: wakker blijven
for ch in (opa, oma, friend, bro, papa, mama):
    S.hold(ch, END)
run_pose(S, friend, END, front="L", look=(0, 0))
S.beat(held, 0.0, **SIT_H, pose="ontspannen", face="vastberaden", face_amt=0.5, at=CAKE0 + V(0, 0, 0.3))
S.teleport(held, ST[1], SEAT + V(0.75, -0.25, 0), heading(SEAT + V(0.75, -0.25, 0), V(2.1, -0.25, 0)))
S.beat(held, ST[1], "handen_hoofd", face="inspanning", face_amt=0.8, at=CAKE1 + V(0, 0, 0.3))
S.beat(held, ST[1] + 0.8, "armen_omhoog", amount=0.8, face="inspanning", face_amt=1.0, look=(0, 0.2))
S.teleport(held, ST[2], SEAT + V(0, 0, zh), 180)
S.beat(held, ST[2], **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=CAKE + V(0, 0, 0.3))
S.beat(held, CLOSE5, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.3, look=(0, -0.3), body={"head": (14, 0, 0)})
S.eyes_closed(held, CLOSE5, ST[3] + 0.1)
S.teleport(held, ST[3], V(1.0, -0.05, 0), heading(V(1.0, -0.05, 0), WB))
S.beat(held, ST[3], "staan", face="verdrietig", face_amt=0.5, at=WB + V(0, 0, -0.1))
S.teleport(held, ST[4], SEAT + V(0, 0, zh), 180)
S.beat(held, ST[4], **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=CAKE + V(0, 0, 0.3))
S.beat(held, CLOSE6, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.3, look=(0, -0.3), body={"head": (16, 0, 0)})
S.eyes_closed(held, CLOSE6, ST[5] + 0.1)
S.beat(held, ST[5] + 0.2, **SIT_H, pose="ontspannen", face="geschrokken", face_amt=0.6, at=CAKE + V(0, 0, 0.3))
S.beat(held, l1[1] - 1.6, **SIT_H, pose="ontspannen", face="blij", face_amt=0.3, at=CANDLE)       # 'smell the cake'
S.beat(held, l1[1] + 0.3, **SIT_H, pose="ontspannen", face="neutraal", face_amt=0.4, at=CANDLE)
# Randy Gardner: hij staat op en loopt rond, het enige dat beweegt
W0 = SEAT + V(0.45, -0.1, 0)
S.teleport(held, l2[0] - 0.2, W0, heading(W0, V(1.6, -0.4, 0)))
S.beat(held, l2[0] - 0.2, "staan", face="inspanning", face_amt=0.6, look=(0, 0))
S.walk(held, l2[0] + 0.2, WIDE2 + 2.5, [W0, V(1.55, -1.25, 0), V(1.75, -0.3, 0), V(1.1, 0.25, 0)], stride=0.55,
       end_rot=heading(V(1.1, 0.25, 0), BRO_SEAT))
S.beat(held, l2[0] + 2.0, "handen_hoofd", face="inspanning", face_amt=0.7, look=(0, 0))
S.beat(held, l2[0] + 4.0, "staan", face="verdrietig", face_amt=0.5, at=S.head(mama, ST[5]))
S.beat(held, WIDE2 + 2.6, "staan", face="verdrietig", face_amt=0.6, at=S.head(bro, ST[5]))
# 'they bring the candles to you': weer op zijn stoel, de taart voor zijn neus
S.teleport(held, l3[0] - 0.4, SEAT + V(0, 0, zh), 180)
S.beat(held, l3[0] - 0.4, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.4, at=CANDLE)
S.beat(held, l3[1] - 1.0, **SIT_H, pose="ontspannen", face="blij", face_amt=0.4, at=S.head(bro, ST[5]))
S.beat(held, l4[1], **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=WB)
S.beat(held, l5[0] + 1.0, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.7, at=S.head(mama, ST[5]))
S.beat(held, l6[0] + 0.5, **SIT_H, pose="ontspannen", face="blij", face_amt=0.4, at=S.head(opa, ST[5]))
# naar het raam: zijn vriend bij het hek
WIN_AT = V(-0.55, 1.62, 0)
S.teleport(held, l7[0] - 0.3, WIN_AT, 180)
S.beat(held, l7[0] - 0.3, "staan", face="verdrietig", face_amt=0.6, at=S.head(friend, ST[5]))
S.reach(held, l7[0] - 0.3, "L", V(-0.3, 1.95, 0.98))      # hand op de vensterbank
S.beat(held, l8[0] + 1.6, "staan", face="verdrietig", face_amt=1.0, at=S.head(friend, ST[5]))
S.hold(held, END)

# de traan: een druppel op mama's wang (ze staat stil, hij dus ook)
bpy.context.scene.frame_set(F(ST[5] + 0.5))
dg = bpy.context.evaluated_depsgraph_get()
MH = S.headpos(mama, ST[5] + 0.5)
pos, fwd, left = S.frame_of(mama, ST[5] + 0.5)
o0 = MH + fwd * 1.0 + left * 0.11 + V(0, 0, -0.06)
hit, loc, nrm, _, ob, _ = bpy.context.scene.ray_cast(dg, o0, -fwd)
tear_at = loc + nrm * 0.006 if hit else MH + fwd * 0.3 + left * 0.11 + V(0, 0, -0.06)
tear = T.sphere("Traan_mama", tear_at, 0.011, HU.water("traan"), scale=(1, 1, 1.5), seg=12, ol=0)
show(tear, ST[5])

# ---------------------------------------------------------------- camera
S.wall(0.0, END + 1)
WIDE = ((2.2, -1.95, 1.75), (0.1, 0.0, 0.9), 22)
S.cam(0.0, WIDE, ((2.15, -1.9, 1.72), (0.1, 0.0, 0.9), 23))
HS = S.bone_world(held, "head", ST[1] + 0.3, tail=False) + V(0, 0, 0.2)
S.cam(ST[1], ((2.15, -0.3, 1.45), HS, 30), ((2.15, -0.35, 1.45), HS, 32))
S.cam(ST[2], ((2.0, -1.95, 2.15), (0.6, -0.6, 0.9), 26), ((1.95, -1.9, 2.12), (0.6, -0.6, 0.9), 27))
S.cam(ST[3], ((2.3, -0.75, 1.75), (1.6, 1.0, 1.15), 22), ((2.3, -0.7, 1.75), (1.6, 1.0, 1.15), 23))
S.cam(ST[4], ((-2.2, -1.95, 2.4), (0.4, -0.1, 0.8), 21), ((-2.15, -1.9, 2.38), (0.4, -0.1, 0.8), 22))
HD7 = S.bone_world(held, "head", ST[5] + 0.5, tail=False) + V(0, 0, 0.18)
S.cam(ST[5], ((0.9, -0.28, 1.42), HD7, 20), ((0.88, -0.32, 1.4), HD7, 23), dof=1.0)
S.cam(l1[1] - 1.8, (CAKE + V(0.45, 0.02, 0.3), CANDLE + V(-0.08, 0, -0.04), 40), (CAKE + V(0.4, 0.02, 0.29), CANDLE + V(-0.08, 0, -0.04), 44), dof=0.4)
# Randy Gardner
S.cam(l2[0] - 0.2, ((2.25, -1.95, 1.5), (1.2, -0.6, 1.1), 26), ((2.25, -1.9, 1.5), (1.5, 0.0, 1.1), 26))
S.cam(WIDE2, ((-2.2, -1.95, 2.45), (0.5, 0.0, 0.8), 20), ((-2.15, -1.9, 2.4), (0.6, 0.1, 0.8), 21))
# de taart voor hem
HD3 = S.bone_world(held, "head", l3[0] + 1.0, tail=False) + V(0, 0, 0.18)
S.cam(l3[0] - 0.4, ((1.35, 0.3, 1.4), HD3 + V(0, 0, -0.15), 30), ((1.25, 0.12, 1.32), HD3 + V(0, 0, -0.15), 34), dof=1.2)
# whiteboard
S.cam(l4[0] - 0.3, ((1.72, 0.32, 0.98), WB + V(-0.04, 0, -0.12), 40), ((1.74, 0.38, 0.97), WB + V(-0.04, 0, -0.12), 44), dof=0.8)
# mama, de traan
MH5 = S.headpos(mama, l5[0] + 1.0)
S.cam(l5[0] - 0.4, ((2.2, -0.95, 1.75), MH5 + V(0, 0, -0.15), 30), ((2.15, -0.85, 1.75), MH5 + V(0, 0, -0.1), 34))
S.cam(TEAR - 0.3, (MH5 + fwd * 1.15 + left * 0.2 + V(0, 0, -0.02), MH5 + left * 0.06 + V(0, 0, -0.03), 40),
      (MH5 + fwd * 1.0 + left * 0.18 + V(0, 0, -0.02), MH5 + left * 0.06 + V(0, 0, -0.03), 44), dof=0.8)
# opa en oma
S.cam(l6[0] - 0.3, ((-0.7, -0.3, 1.45), (-2.25, 1.0, 1.15), 30), ((-0.8, -0.2, 1.45), (-2.25, 1.0, 1.15), 34))
OH = S.headpos(opa, ST[5] + 0.5)
S.cam(l6[0] + 0.48 * (l6[1] - l6[0]), ((-0.85, 0.3, 1.5), OH + V(0, 0, -0.1), 26), ((-0.9, 0.33, 1.5), OH + V(0, 0, -0.1), 29), dof=1.2)
# de vriend bij het hek
S.cam(l7[0] - 0.3, ((0.35, 0.6, 1.75), (-0.2, 8.4, 0.9), 30), ((0.3, 0.9, 1.72), (-0.2, 8.4, 0.9), 36))
FH = S.headpos(friend, ST[5] + 0.5)
S.cam(l7[0] + 0.45 * (l7[1] - l7[0]), ((1.6, 6.1, 0.9), FH + V(0, 0, -0.5), 24), ((1.55, 6.2, 0.9), FH + V(0, 0, -0.5), 26))
# hij bij het raam
HW = S.bone_world(held, "head", l8[0] + 0.5, tail=False) + V(0, 0, 0.2)
S.cam(l8[0] - 0.3, ((-0.5, 3.1, 1.55), HW, 34), ((-0.52, 2.9, 1.52), HW, 38), dof=1.2)

S.finish(length=END)
