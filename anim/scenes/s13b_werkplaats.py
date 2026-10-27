"""S13b · Dag 12 · werkplaats van de beste vriend: het vest van 200 kilo. 'We're calling it the Anchor.'

    blender -b -P anim/scenes/s13b_werkplaats.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s13b", "kleine_interieurs", "werkplaats")

HERO_AT = V(0.0, 0.6, 0)
FR_AT = V(-1.15, 0.95, 0)
BENCH = V(0.3, 2.6, 0)
TIE_AT = V(0.72, 0.62, 0)                       # naast hem, vastsnoeren
held = S.actor("hoofdpersonage", HERO_AT, 0)
vriend = S.actor("beste_vriend", FR_AT, 40)

# ---------------------------------------------------------------- het vest (vast aan de borst; bot-assen: y = op, z = voor)
steel = S.mat("vest_staal", (0.62, 0.65, 0.70))
chain_m = S.mat("vest_ketting", (0.28, 0.28, 0.32))
tie_m = S.mat("vest_tiewrap", (0.08, 0.08, 0.09))
vest = {"plates": [], "chains": [], "ties": []}
for nm, z in (("voor", 0.17), ("achter", -0.17)):
    o = T.box(f"Vest_plaat_{nm}", (0, 0, 0), (0.46, 0.42, 0.035), steel, base=False, bevel=0.01, ol=0.004)
    attach(o, held, "chest", (0, -0.27, z))
    vest["plates"].append(o)
for k, (a, b) in enumerate((((-0.24, -0.02), (0.24, -0.46)), ((0.24, -0.02), (-0.24, -0.46)))):
    pts = [(lerp(a[0], b[0], u), lerp(a[1], b[1], u), 0.2 + 0.02 * math.sin(u * math.pi)) for u in (0, 0.25, 0.5, 0.75, 1)]
    o = T.tube(f"Vest_ketting_{k}", pts, 0.016, chain_m)
    attach(o, held, "chest", (0, 0, 0))
    vest["chains"].append(o)
    for i in range(7):
        u = (i + 0.5) / 7
        ln = T.torus(f"Vest_schakel_{k}_{i}", (0, 0, 0), 0.03, 0.007, chain_m, seg=10, seg2=4, ol=0.002)
        attach(ln, held, "chest", (lerp(a[0], b[0], u), lerp(a[1], b[1], u), 0.215), (0, 90 if i % 2 else 0, 0))
        vest["chains"].append(ln)
rnd = random.Random(13)
for k in range(14):
    side = 1 if k % 2 else -1
    o = T.box(f"Vest_tiewrap_{k}", (0, 0, 0), (0.012, 0.09, 0.006), tie_m, base=False, bevel=0, ol=0.002)
    attach(o, held, "chest", (side * rnd.uniform(0.18, 0.25), rnd.uniform(-0.45, -0.1), 0.19 if k < 9 else -0.19), (0, 0, rnd.uniform(-30, 30)))
    vest["ties"].append(o)
# de plaat die de vriend straks vasthoudt
plate_hand = T.box("Staalplaat_hand", (0, 0, 0), (0.46, 0.035, 0.42), steel, base=False, bevel=0.01, ol=0.004)
attach(plate_hand, vriend, "hand.R", (0.0, 0.08, 0.1), (0, 0, 0))

# ---------------------------------------------------------------- tijdlijn
S.hud(12, "4,096x STRONGER", t0=0.0, tick=False)
S.music("werkplaats", 0.0, 60, vol=0.26, fade_in=0.4, fade_out=0.2)
SHOP = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.06)
l4 = S.say("S13-04", who=vriend, gap=0.5, gain=1.2)
l5 = S.say("S13-05", gap=0.4)
VEST = l5[0] + 1.5
P_PLATES, P_CHAINS, P_TIES, KILOS = l5[0] + 1.6, l5[0] + 2.5, l5[0] + 3.4, l5[0] + 4.7
S.sfx("sfx_bouten", l5[0] + 0.2, 0.5)
S.sfx("sfx_staal", P_PLATES, 0.35)
S.sfx("sfx_knokkels", P_TIES, 0.3)
l6 = S.say("S13-06", gap=0.5)
PAUSE = l6[0] + 8.0
SILLY = l6[0] + 11.4                            # 'You look ridiculous.'
WORKS = l6[0] + 12.9                            # 'It works.'
l7 = S.say("S13-07", who=vriend, gap=0.7, gain=1.2)
ANCHOR = l7[0] + 1.2                            # '...the Anchor.'
SHOP["loop_to"] = ANCHOR - 0.05
S.music("orkest_held", ANCHOR - 0.1, l7[1] + 1.0, vol=0.3, fade_in=0.05, fade_out=0.6)
l8 = S.say("S13-08", gap=0.6)
S.wait(1.0)
END = S.t
S.music("werkplaats", l8[0] - 0.2, END + 0.2, vol=0.22, fade_in=0.5, fade_out=0.6, start=30.0)

S.gauge("VEST: 200 kg", KILOS, l6[0] + 0.5)
S.real(l6[0] + 0.05, PAUSE + 0.2)
S.text("MORE MASS = MORE GRIP", l6[0] + 1.5, PAUSE + 0.2, loc=(0.965, 0.22), size=48, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("+ MORE MASS TO PUSH WITH", l6[0] + 3.3, PAUSE + 0.2, loc=(0.965, 0.14), size=48, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.card("THE ANCHOR", ANCHOR, l7[1] + 0.6, size=130, dim=0.3, color=GOLD)

# ---------------------------------------------------------------- vest verschijnt stuk voor stuk
for o in vest["plates"]:
    show(o, P_PLATES)
for o in vest["chains"]:
    show(o, P_CHAINS)
for o in vest["ties"]:
    show(o, P_TIES)
show(plate_hand, 0.0, P_PLATES)

# ---------------------------------------------------------------- vriend
S.beat(vriend, 0.0, "staan", face="zelfverzekerd", face_amt=0.7, at=S.head(held, 0), arms=HOLD_FRONT_R)
S.beat(vriend, l4[0] + 0.1, "wijzen", amount=0.8, face="zelfverzekerd", face_amt=0.9, at=S.head(held, 0))
S.beat(vriend, l4[0] + 1.3, "staan", face="grijns", face_amt=0.9, at=S.head(held, 0), arms=HOLD_FRONT_R, wenkbrauw_op=0.7)
S.hold(vriend, l5[0] - 0.15)
# aan de werkbank
S.teleport(vriend, l5[0] - 0.1, BENCH, 180)
S.beat(vriend, l5[0] - 0.1, "staan", face="vastberaden", face_amt=0.8, at=BENCH + V(0, -0.45, 0.95), crouch=(0.04, 18), arms=CLAP_A)
S.beat(vriend, l5[0] + 0.5, "staan", face="inspanning", face_amt=0.6, at=BENCH + V(0.2, -0.45, 0.95), crouch=(0.04, 18), arms=CLAP_B)
S.beat(vriend, l5[0] + 1.0, "staan", face="vastberaden", face_amt=0.8, at=BENCH + V(-0.2, -0.45, 0.95), crouch=(0.04, 18), arms=CLAP_A)
S.hold(vriend, VEST - 0.05)
# naast hem, tie-wraps aantrekken
S.teleport(vriend, VEST, TIE_AT, heading(TIE_AT, HERO_AT))
S.beat(vriend, VEST, "staan", face="inspanning", face_amt=0.7, at=S.head(held, VEST) + V(0, 0, -0.4), crouch=(0.05, 14))
for k in range(4):
    t = VEST + 0.2 + k * 0.7
    S.reach(vriend, t, "R", S.head(held, t) + V(0.3, -0.12, -0.5 - 0.06 * k))
    S.reach(vriend, t + 0.35, "R", S.head(held, t) + V(0.42, -0.1, -0.52 - 0.06 * k))
S.reach(vriend, l6[0] + 0.2, "R", None, 0.0)
S.walk(vriend, l6[0] + 0.3, l6[0] + 1.6, [TIE_AT, V(-0.4, 1.4, 0), FR_AT], end_rot=40)
S.beat(vriend, l6[0] + 1.8, "armen_over", face="zelfverzekerd", face_amt=0.9, at=S.head(held, l6[0]))
S.beat(vriend, PAUSE, "handen_zij", face="zelfverzekerd", face_amt=1.0, at=S.head(held, PAUSE), body={"chest": (-6, 0, 0)})
S.beat(vriend, WORKS + 0.6, "juichen", amount=0.6, face="lach", face_amt=1.0, at=S.head(held, WORKS))
S.beat(vriend, l7[0] + 0.1, "staan", face="zelfverzekerd", face_amt=1.0, look=(0, 0), arms=HOLD_FRONT_R)
S.beat(vriend, ANCHOR, "armen_omhoog", face="lach", face_amt=1.0, look=(0, 0.3))
S.beat(vriend, l8[0] + 0.3, "handen_zij", face="grijns", face_amt=0.9, at=S.head(held, l8[0]))
S.hold(vriend, END)

# ---------------------------------------------------------------- hij
S.beat(held, 0.0, "staan", face="twijfel", face_amt=0.5, at=S.head(vriend, 0))
S.beat(held, l4[0] + 0.8, "staan", face="twijfel", face_amt=0.8, at=S.head(vriend, l4[0]), wenkbrauw_op=0.6)
S.beat(held, VEST, "staan", face="nerveus", face_amt=0.6, look=(0.3, -0.5), arms=arms(arm("L", (0.6, 0.0, -0.8), (0.7, 0.1, -0.7)), arm("R", (0.6, 0.0, -0.8), (0.7, 0.1, -0.7))))
S.beat(held, KILOS, "staan", face="inspanning", face_amt=0.3, look=(0, -0.6), crouch=(0.05, 4),
       arms=arms(arm("L", (0.6, 0.0, -0.8), (0.7, 0.1, -0.7)), arm("R", (0.6, 0.0, -0.8), (0.7, 0.1, -0.7))))
S.beat(held, l6[0] + 1.0, "staan", face="neutraal", face_amt=0.5, look=(0, 0), crouch=(0.03, 2))
S.beat(held, PAUSE, "staan", face="neutraal", face_amt=0.8, look=(0, 0), crouch=(0.03, 2))
S.beat(held, SILLY - 0.1, "staan", face="verdrietig", face_amt=0.6, look=(0, -0.4), body={"head": (8, 0, 0)}, crouch=(0.03, 2))
S.hold(held, WORKS - 0.1)
WALK_TO = HERO_AT + V(0.6, -1.0, 0)
S.walk(held, WORKS, WORKS + 1.6, [HERO_AT, WALK_TO], stride=0.45, end_rot=0)
S.beat(held, WORKS + 0.1, "staan", face="verbaasd", face_amt=0.6, look=(0, -0.3))
S.beat(held, WORKS + 1.7, "vuisten", amount=0.6, face="blij", face_amt=0.8, look=(0, 0))
S.beat(held, l7[0] + 0.2, "staan", face="blij", face_amt=0.5, at=S.head(vriend, l7[0]))
S.beat(held, ANCHOR + 0.3, "staan", face="twijfel", face_amt=0.9, at=S.head(vriend, ANCHOR))
S.beat(held, l8[0] + 0.1, "armen_over", face="boos", face_amt=0.5, at=S.head(vriend, l8[0]))
S.beat(held, l8[1], "armen_over", face="grijns", face_amt=0.6, look=(0.3, 0.1), body={"head": (0, 0, -8)})
S.hold(held, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.8, -4.4, 1.6), (-0.4, 1.2, 1.0), 22), ((1.5, -3.9, 1.55), (-0.4, 1.2, 1.0), 24))
S.cam(l4[0] - 0.1, S.shot(vriend, l4[0], "mcu", az=-20, lens=30), S.shot(vriend, l4[1], "mcu", az=-15, lens=34))
S.cam(l5[0] - 0.1, ((2.3, 2.0, 1.45), (0.25, 2.65, 0.95), 28), ((2.2, 2.1, 1.4), (0.25, 2.65, 0.95), 32))
S.cam(VEST, ((0.15, -1.7, 1.2), (0.15, 0.6, 0.85), 30), ((0.15, -1.45, 1.15), (0.15, 0.6, 0.85), 34))
S.cam(l6[0] - 0.1, S.shot(held, l6[0], "med", az=20, lens=30, lr=0.35), S.shot(held, PAUSE, "med", az=15, lens=32, lr=0.35))
S.cam(PAUSE, ((0.0, -3.4, 1.3), (-0.45, 0.8, 0.85), 26))
S.cam(SILLY - 0.15, S.shot(held, SILLY, "cu", az=-10, lens=34), S.shot(held, WORKS, "cu", az=-8, lens=38))
S.cam(WORKS - 0.1, ((0.9, -2.6, 1.1), (0.3, -0.2, 0.75), 28), ((0.9, -2.6, 1.1), (0.5, -0.4, 0.75), 30))
S.cam(l7[0] - 0.1, S.shot(vriend, l7[0], "mcu", az=-25, lens=30), S.shot(vriend, l7[1], "med", az=-20, lens=28))
S.cam(l8[0] - 0.1, S.shot(held, l8[0], "mcu", az=10, lens=32), S.shot(held, END, "cu", az=8, lens=38))

S.finish(length=END)
