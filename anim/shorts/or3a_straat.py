"""OR3a · What if you could rewind time ten seconds? · stad (middag), zebrapad, één deel.

1  hook: een auto raast door rood op je af... en spoelt terug (alles achteruit, << REWIND).
2  REWIND 1: je laat je telefoon vallen. Terugspoelen: hij vliegt terug in je hand. Hij valt weer: gevangen.
3  REWIND 2: je stapt het zebrapad op, de auto rijdt door rood. Terugspoelen. Je stapt terug; de auto raast voorbij.
4  Je tikt op je horloge... en dezelfde tien seconden beginnen opnieuw (de telefoon valt weer). LOOP.
5-6 "And again." Steeds weer hetzelfde stukje, jij steeds banger.

    python3 anim/shorts/or3a_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or3", "a", "stad", "middag", lines=(1, 2, 3, 4, 5, 6))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR3-{n:02d}"][i]["s"]
S.clip = (0.05, 3000)
CYAN = (0.35, 0.9, 1.0, 1)

CURB = V(-6.7, -8.0, 0.15)            # stoeprand bij het zebrapad over de y-weg (rijbaan x -6..6)
held = S.actor("hoofdpersonage", CURB, 90)          # kijkt naar +x, de weg over
HEAD = S.head(held, 0.0)

# -- telefoon: één in je hand (aan het bot), één los (vallen) -----------------------------------------
ph_m = S.mat("telefoon_zwart", (0.05, 0.05, 0.06))
scr_m = S.mat("telefoon_scherm_or3", (0.5, 0.75, 1.0), 2.0)


def phone(name):
    o = T.box(name, (0, 0, 0), (0.075, 0.15, 0.012), ph_m, base=False, bevel=0.004, ol=0.002)
    s_ = T.box(name + "_scherm", (0, 0, 0.0065), (0.066, 0.14, 0.001), scr_m, base=False, bevel=0, ol=0)
    s_.parent = o
    return o


HOLD = CURB + V(0.3, -0.04, 0.72)
S.reach(held, 0.0, "R", HOLD)
ph_hand = phone("Telefoon_hand")
ph_hand.location = HOLD + V(0.03, 0.0, 0.02)
ph_hand.rotation_euler = (math.radians(-55), 0, math.radians(90))
attach_keep(ph_hand, held, "hand.R", 0.0)
ph_free = phone("Telefoon_los")
FLOOR = V(HOLD.x + 0.1, HOLD.y + 0.05, 0.157)

# -- de auto die door rood rijdt (zuidwaarts op de linkerbaan, x = -3) ---------------------------------
car = S.obj("Auto_rijdt")
CX = -3.0
CAR_ROT = (0, 0, -90)                 # car2 kijkt naar +x; -90 = naar -y


def car_at(t, y):
    key(car, t, loc=(CX, y, 0), rot=CAR_ROT)


# ===================================================================== regel 3 (eerst: de hook kopieert dit)
r3 = L[3][0]
STEP = V(-4.4, -8.0, 0.0)
t_hit = W(3, 6) - 0.08                 # vlak voor "Rewind": de auto staat bijna tegen je aan
S.place(held, r3, CURB, 90)
S.reach(held, r3, "R", None, 0.0)
S.beat(held, r3, "staan", face="neutraal", look=(0, 0.1))
S.walk(held, r3 + 0.25, W(3, 5) + 0.15, [CURB, V(-5.6, -8.0, 0.0), STEP], stride=0.42, arms=0.45)
S.beat(held, W(3, 5), "staan", face="neutraal", look=(0.6, 0.1), body={"head": (0, 0, 30)}, feet="keep")
S.beat(held, t_hit - 0.25, "schrik", face="geschrokken", face_amt=1.0, look=(0.8, 0.0), body={"head": (0, 0, 55), "neck": (0, 0, 15)})
S.beat(held, t_hit, "schrik", face="geschrokken", face_amt=1.0, look=(0.8, 0.0), body={"head": (0, 0, 60), "neck": (0, 0, 15)})
car_at(r3, 60.0)
car_at(r3 + 0.6, 45.0)
car_at(t_hit, -8.0 + 2.6)              # de neus 0,5 m voor je
# terugspoelen (achteruit) naar het begin van de regel
RW1, RW2 = W(3, 6), W(3, 7) - 0.15
copy_anim([held.rig, car], t_hit, r3 + 0.3, RW1, RW2)
# "You step back": je deinst achteruit, de auto raast voor je langs
S.place(held, RW2 + 0.02, CURB, 90)
S.beat(held, RW2 + 0.02, "staan", face="nerveus", face_amt=0.6, look=(0.6, 0.0), body={"head": (0, 0, 40)})
S.walk(held, W(3, 8) - 0.1, W(3, 9) + 0.35, [CURB, CURB + V(-0.6, 0, 0)], stride=0.3, turn=False, arms=0.3)
S.beat(held, W(3, 9) + 0.3, "schrik", amount=0.6, face="geschrokken", face_amt=0.8, look=(0.4, 0.0), body={"head": (0, 0, 20)}, feet="keep")
S.beat(held, W(3, 10) + 0.2, "staan", face="blij", face_amt=0.8, look=(0, 0.1), body={"spine": (-4, 0, 0)})
S.beat(held, L[3][1], "ontspannen", face="blij", face_amt=0.9, look=(0, 0.1))
car_at(RW2 + 0.01, 45.0)
car_at(W(3, 9) - 0.4, 16.0)
car_at(W(3, 9) + 0.25, -8.0)
car_at(W(3, 9) + 1.0, -40.0)
car_at(W(3, 9) + 1.05, -300.0)
S.sfx("sfx_remmen", t_hit - 0.6, 0.0) if False else None
S.sfx("sfx_auto_toeter", t_hit - 0.55, 0.35)
S.sfx("sfx_glitch", RW1 - 0.03, 0.35)
S.sfx("sfx_whoosh", W(3, 9) - 0.1, 0.45)
S.sfx("sfx_auto_optrekken", W(3, 9) - 0.5, 0.25)

# ===================================================================== regel 1: de hook
# het einde van regel 3 vooruit (de auto op je af), dan terugspoelen
H_HIT = 1.05
copy_anim([held.rig, car], r3 + 0.3, t_hit, 0.0, H_HIT)
copy_anim([held.rig, car], t_hit, r3 + 0.3, H_HIT + 0.08, L[1][1])
S.face(held, 0.0, "nerveus", 0.6, look=(0.8, 0.0))
S.face(held, H_HIT - 0.3, "geschrokken", 1.0, look=(0.8, 0.0))
S.face(held, L[1][1], "geschrokken", 0.7, look=(0.8, 0.0))
S.sfx("sfx_auto_toeter", 0.1, 0.35)
S.sfx("sfx_glitch", H_HIT, 0.35)
S.text("<< REWIND", H_HIT + 0.02, L[1][1], loc=(0.5, 0.62), size=110, color=CYAN, anchor=("CENTER", "CENTER"), pop=False)
S.texts[-1]["box"] = True

# ===================================================================== regel 2: de telefoon
r2 = L[2][0]
S.place(held, r2, CURB, 90)
S.beat(held, r2, "staan", face="neutraal", look=(0.1, -0.5), body={"head": (14, 0, 0)})
S.reach(held, r2, "R", HOLD)
car_at(r2, -300.0)
drop, land = W(2, 1) + 0.05, W(2, 1) + 0.5
show(ph_hand, 0.0, drop)
visible(ph_hand, r3, False)
key(ph_free, drop - 0.01, loc=tuple(HOLD + V(0.03, 0, 0.02)), rot=(-55, 0, 90))
key(ph_free, land, loc=tuple(FLOOR), rot=(-180, 0, 140))
key(ph_free, land + 0.15, loc=tuple(FLOOR + V(0.05, 0.02, 0)), rot=(-180, 0, 150))
S.beat(held, drop + 0.15, "staan", face="geschrokken", face_amt=1.0, look=(0.1, -0.8), body={"head": (22, 0, 0)})
S.reach(held, drop + 0.2, "R", HOLD + V(0.04, 0, -0.12))
S.sfx("sfx_val_klap", land, 0.3)
S.sfx("sfx_glas_klink", land + 0.02, 0.25)
# terugspoelen: de telefoon vliegt terug in je hand
RA, RB = W(2, 4) - 0.05, W(2, 4) + 0.55
copy_anim([ph_free], land, drop - 0.01, RA, RB)
copy_anim([held.rig], drop + 0.25, r2 + 0.1, RA, RB)
S.sfx("sfx_glitch", RA - 0.03, 0.35)
S.text("<< REWIND", RA, RB + 0.1, loc=(0.5, 0.62), size=110, color=CYAN, anchor=("CENTER", "CENTER"), pop=False)
S.texts[-1]["box"] = True
# en weer valt hij... je vangt hem
d2b = W(2, 5) - 0.45
CATCH = HOLD + V(0.06, -0.02, -0.32)
S.beat(held, RB + 0.02, "staan", face="vastberaden", face_amt=0.7, look=(0.1, -0.6), body={"head": (16, 0, 0)})
S.reach(held, RB + 0.02, "R", HOLD)
key(ph_free, RB + 0.01, loc=tuple(HOLD + V(0.03, 0, 0.02)), rot=(-55, 0, 90))
key(ph_free, d2b - 0.01, loc=tuple(HOLD + V(0.03, 0, 0.02)), rot=(-55, 0, 90))
key(ph_free, d2b + 0.22, loc=tuple(CATCH + V(0.03, 0, 0.02)), rot=(-75, 0, 110))
S.reach(held, d2b + 0.02, "R", HOLD)
S.reach(held, d2b + 0.22, "R", CATCH)
S.beat(held, d2b + 0.3, "staan", face="lach", face_amt=0.9, look=(0.1, -0.6), body={"head": (16, 0, 0)})
S.reach(held, W(2, 6) + 0.4, "R", HOLD)
S.beat(held, L[2][1], "staan", face="blij", face_amt=0.9, look=(0.2, 0.2))
visible(ph_free, 0.0, False)
visible(ph_free, drop, True)
visible(ph_free, RB, False)
visible(ph_free, RB + 0.01, False)
visible(ph_free, d2b, True)
visible(ph_free, d2b + 0.23, False)
visible(ph_hand, RB, True)
visible(ph_hand, d2b, False)
visible(ph_hand, d2b + 0.23, True)

# ===================================================================== regel 4: het horloge, de lus
r4 = L[4][0]
WATCH_BONE = "hand.L"
watch = T.box("Horloge", tuple(CURB + V(0.0, 0.0, 0.0)), (0.06, 0.05, 0.02), S.mat("horloge", (0.1, 0.1, 0.12)), base=False, bevel=0.005, ol=0.002)
wglow = T.box("Horloge_gloed", (0, 0, 0.011), (0.045, 0.035, 0.002), S.mat("horloge_gloed", (0.35, 0.9, 1.0), 5.0), base=False, bevel=0, ol=0)
wglow.parent = watch
S.place(held, r4, CURB, 90)
S.reach(held, r4, "R", None, 0.0)
WR = CURB + V(0.3, 0.12, 0.85)
S.reach(held, r4, "L", None, 0.0)
S.reach(held, r4 + 0.3, "L", WR)
S.reach(held, r4 + 0.3, "R", WR + V(0.06, -0.14, 0.04))
S.beat(held, r4, "staan", face="neutraal", look=(0.2, -0.5), body={"head": (16, 0, 0)})
S.reach(held, W(4, 4) - 0.1, "R", WR + V(0.06, -0.14, 0.04))
S.reach(held, W(4, 4) + 0.05, "R", WR + V(0.0, -0.06, 0.03))
S.reach(held, W(4, 5) + 0.2, "R", WR + V(0.06, -0.16, 0.0))
S.beat(held, W(4, 5) + 0.2, "staan", face="verbaasd", face_amt=0.7, look=(0.2, -0.5), body={"head": (16, 0, 0)})
watch.location = WR + V(0.0, 0.0, 0.03)
attach_keep(watch, held, WATCH_BONE, r4 + 0.3)
show(watch, r4)
key(wglow, 0.0, scale=(1, 1, 1))
S.sfx("sfx_hud_tik", W(4, 4) + 0.05, 0.5)
S.sfx("sfx_tijd_stop", W(4, 5), 0.35)
# "the same ten seconds start again": precies de telefoon-scène, opnieuw
LOOP1 = W(4, 6) - 0.05
LOOP_SRC = (r2, RB + 0.3)


def loop(a, b, scared):
    """Speel het begin van regel 2 opnieuw af in [a, b] en zet de telefoons zoals daar."""
    dur = min(b - a, LOOP_SRC[1] - LOOP_SRC[0])
    src_b = LOOP_SRC[0] + dur
    S.reach(held, a - 0.02, "L", None, 0.0)
    copy_anim([held.rig, ph_free], LOOP_SRC[0], src_b, a, a + dur)
    off = a - LOOP_SRC[0]
    visible(ph_hand, a, True)
    visible(ph_hand, drop + off, False)
    visible(ph_free, a, False)
    visible(ph_free, drop + off, True)
    visible(ph_free, min(RB + off, b), False)
    if RB + off < b:
        visible(ph_hand, RB + off, True)
    S.face(held, a, "nerveus" if scared < 1 else "bang", 0.6 + 0.4 * min(1, scared), look=(0.1, -0.6))
    S.face(held, drop + off + 0.15, "geschrokken" if scared < 1 else "bang", 1.0, look=(0.1, -0.8))
    S.sfx("sfx_glitch", a - 0.04, 0.3 + 0.1 * scared)
    if land + off < b:
        S.sfx("sfx_val_klap", land + off, 0.3)


visible(watch, LOOP1, True)
loop(LOOP1, L[5][0] - 0.02, 0.0)
loop(L[5][0] - 0.02, L[6][0] - 0.02, 1.0)
loop(L[6][0] - 0.02, END, 2.0)
S.face(held, L[6][1] - 0.2, "bang", 1.0, look=(0.0, 0.2))
S.face(held, END, "bang", 1.0, look=(0.0, 0.2))

# -- tellers, geluid ---------------------------------------------------------------------------------
S.counter("REWIND 1", r2, L[2][1])
S.counter("REWIND 2", r3, L[3][1])
S.counter("REWIND 3", r4, LOOP1)
S.counter("LOOP", LOOP1, L[5][0] - 0.02, color=RED)
S.counter("LOOP 2", L[5][0], L[6][0] - 0.02, color=RED)
S.counter("LOOP 3", L[6][0], END, color=RED)
S.ambience("sfx_stad_dag", 0.0, END, vol=0.08)
S.music_all("m_spanning_puls", vol=0.22)
S.sfx("sfx_klok_tik", L[5][0], 0.25, cut=END)

# -- camera's ----------------------------------------------------------------------------------------
LOWROAD = ((-5.0, -12.2, 0.55), (-3.4, 2.0, 1.4), 22)
S.cam(0.0, LOWROAD, ((-5.1, -12.0, 0.55), (-3.5, 2.0, 1.4), 24))
PH_CAM = ((CURB.x + 1.2, CURB.y - 0.9, 1.0), tuple(HOLD + V(0, 0, 0.12)), 32)
S.cam(r2, PH_CAM, ((CURB.x + 1.15, CURB.y - 0.85, 0.98), tuple(HOLD + V(0, 0, 0.2)), 28))
S.cam(r3, LOWROAD, ((-5.1, -12.0, 0.6), (-3.5, 2.0, 1.4), 24))
S.cam(RW2, ((-9.2, -12.5, 1.1), (-4.4, -6.8, 0.9), 24), ((-9.0, -12.2, 1.1), (-4.6, -7.0, 0.9), 26))
S.cam(r4, ((CURB.x + 0.9, CURB.y - 0.55, 1.15), tuple(WR * 0.5 + HEAD * 0.5), 24),
      ((CURB.x + 0.8, CURB.y - 0.5, 1.12), tuple(WR * 0.5 + HEAD * 0.5), 28))
S.cam(LOOP1, PH_CAM, ((CURB.x + 1.15, CURB.y - 0.85, 0.98), tuple(HOLD + V(0, 0, 0.2)), 28))
S.cam(L[5][0] - 0.02, ((CURB.x + 1.1, CURB.y - 0.8, 1.05), tuple(HOLD + V(0, 0, 0.25)), 30),
      ((CURB.x + 1.0, CURB.y - 0.7, 1.05), tuple(HOLD + V(0, 0, 0.28)), 33))
S.cam(L[6][0] - 0.02, ((CURB.x + 0.95, CURB.y - 0.6, 1.25), tuple(HEAD + V(0, 0, -0.08)), 30),
      ((CURB.x + 0.85, CURB.y - 0.5, 1.25), tuple(HEAD + V(0, 0, -0.08)), 38))
S.done()
