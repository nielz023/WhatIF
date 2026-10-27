"""SH1b · What if you got 10x faster every day? · straat: dag 2 de geluidsbarrière (alle ramen eruit),
dag 3 slaat de lucht hem in zijn gezicht en vliegt zijn hoodie in brand. Dag 4 komt eraan.

    blender -b -P anim/shorts/sh1b_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh1", "b", "straat", "zonnig", lines=(3, 4, 5, 6, 7, 8))
l3, l4, l5, l6, l7, l8 = (S.L[n] for n in (3, 4, 5, 6, 7, 8))
S.clip = (0.05, 2000)

Z0 = 0.12                                       # stoep
START = V(0.6, 7.3, Z0)                        # voor zijn huis
for n in ("Auto_geparkeerd_2", "Auto_geparkeerd_3"):
    o = S.obj(n)
    if o:
        o.hide_render = True

held = S.actor("hoofdpersonage", START, 90)     # kijkt naar +x, de straat af

# ---------------------------------------------------------------- tijden
GO = l3[0] + 2.6                                # weg: een oranje streep over de stoep
BOOM = l4[0] + 0.15                             # 'That bang?'
RUN0 = l5[0] - 0.15                             # dag 3, in slow motion
SMOKE = l6[0]
FIRE = l6[0] + 1.25                             # 'Your hoodie... is on fire'
END = S.t1

# ---------------------------------------------------------------- muziek en geluid
S.ambience("sfx_straat_sfeer", S.t0, BOOM, vol=0.14)
S.sfx("sfx_whoosh", GO - 0.05, 0.8)
S.sfx("sfx_donderslag", BOOM - 0.02, 1.0)
S.sfx("sfx_nies_boem", BOOM + 0.05, 0.8)
for k in range(5):
    S.sfx("sfx_glasdeur", BOOM + 0.2 + k * 0.22, 0.55)
S.sfx("sfx_autoalarm", BOOM + 1.2, 0.35, loop_to=RUN0 - 0.2)
S.sfx("sfx_slowmo", RUN0 - 0.1, 0.6)
S.ambience("sfx_wind_hoog", RUN0, END, vol=0.22)
S.sfx("sfx_hartslag", RUN0 + 0.5, 0.45, loop_to=END)
S.sfx("sfx_vuur", FIRE - 0.1, 0.9)
S.sfx("sfx_vuur", FIRE + 1.9, 0.7)
S.sfx("sfx_riser", l7[0] - 0.5, 0.6)
S.sfx("sfx_cliffhanger", l7[1] - 4.6, 0.8)
S.counter("DAY 2", l3[0] + 0.1, l5[0] - 0.05, sub="100x FASTER")
S.gauge_y = 0.69
S.texts.append(dict(body="1,500 km/h", t0=l3[0] + 2.0, t1=l4[0] + 1.5, loc=(0.5, 0.68), size=96, color=WHITE,
                    anchor=("CENTER", "CENTER"), pop=True))
S.real(l4[0] + 1.6, l4[1])
S.counter("DAY 3", l5[0] + 0.05, l7[0] - 0.05, sub="1,000x FASTER")
S.counter("DAY 4", l7[0] + 0.9, None, color=RED, sub="10,000x FASTER")

# ---------------------------------------------------------------- dag 2: klaar, en weg
S.beat(held, S.t0, "staan", face="grijns", face_amt=0.8, look=(0.4, 0))
S.beat(held, l3[0] + 1.2, "schrap", face="vastberaden", face_amt=1.0, look=(0, 0.2), crouch=(0.22, 24),
       body={"chest": (14, 0, 0), "head": (-12, 0, 0)})
S.hold(held, GO - 0.05)
visible(held.rig, 0, True)
visible(held.rig, GO, False)
visible(held.rig, RUN0 - 0.05, True)             # terug voor de slow motion
# de oranje streep: 0,2 s van het huis tot ver de straat in
streak = T.cyl("Snelheidsstreep", (0, 0, 0), 0.22, 6.0, S.mat("streep", (1.0, 0.55, 0.15), glow=3.0), rot=(0, 90, 0), seg=16, ol=0)
key(streak, GO - 1 / FPS, loc=(START.x, START.y, 0.8), scale=(1, 1, 0.01))
key(streak, GO, loc=(START.x + 2, START.y, 0.8), scale=(1, 1, 1))
key(streak, GO + 0.2, loc=(START.x + 70, START.y, 0.8), scale=(1, 1, 1))
show(streak, GO - 1 / FPS, GO + 0.22)
for k in range(6):
    S.debris(START + V(1.0 + k * 3.0, 0, 0.1), GO + k * 0.03, n=8, size=(0.04, 0.09), color=(0.45, 0.6, 0.2),
             speed=(2.0, 4.5), up=1.2, floor=Z0, life=3.0, name="Blad")
    S.puff(START + V(1.0 + k * 3.0, 0, 0.2), GO + k * 0.03, n=4, r=(0.2, 0.4), grow=2.0, dur=1.2, rise=0.4)

# ---------------------------------------------------------------- de knal: kegel, schokgolf, ramen eruit
BX = START.x + 18
S.ring(V(BX, START.y, 1.0), BOOM, r0=0.5, r1=30.0, dur=0.7, rot=(0, 90, 0), thick=0.12)
cone = T.cyl("Dampkegel", (0, 0, 0), 1.6, 3.0, S.mat("dampkegel", (0.95, 0.97, 1.0), glow=1.2), r2=0.05, rot=(0, -90, 0), seg=32, ol=0)
key(cone, BOOM - 1 / FPS, loc=(BX, START.y, 1.0), scale=0.001)
key(cone, BOOM, loc=(BX, START.y, 1.0), scale=1.0)
key(cone, BOOM + 0.25, loc=(BX + 6, START.y, 1.0), scale=1.4)
key(cone, BOOM + 0.4, loc=(BX + 8, START.y, 1.0), scale=0.001)
broken = S.mat("raam_kapot", (0.08, 0.09, 0.12))
WINS = [(-1.4, 3.6, 1.5, 1.3), (1.4, 3.6, 1.5, 1.3), (1.2, 1.0, 2.2, 1.5)]
for hx in range(-6, 31, 6):
    for side, fy, s in (("n", 13.0, -1), ("z", -10.5, 1)):
        for k, (wx, wz, ww, wh) in enumerate(WINS):
            x = hx + (wx if s == -1 else -wx)
            y = fy + s * 0.095
            dt = max(0.0, (x - START.x) / 120.0) + (0.12 if s == 1 else 0.0)
            hole = T.box(f"Raamgat_{side}{hx}_{k}", (x, y, wz + 0.08), (ww * 0.98, 0.02, wh * 0.98), broken, bevel=0, ol=0)
            show(hole, BOOM + dt)
            if abs(hx) <= 18:
                S.shatter(V(x, y, wz + 0.08 + wh / 2), (ww, wh), BOOM + dt, n=10, normal=(0, s, 0), speed=(2.0, 5.0), floor=0.0)

# ---------------------------------------------------------------- dag 3: slow motion over de rijbaan
RY = 0.5
RX0 = -25.0
RUN_V = 5.5                                     # in slow motion: gewone sprint
RUN_D = RUN_V * (END - RUN0)


def rx(t):
    """Zelfde versnelling als S.walk, zodat camera, lijnen en rook hem precies volgen."""
    u = min(1.0, max(0.0, (t - RUN0) / (END - RUN0)))
    return RX0 + RUN_D * (smooth(0, 1, u) * 0.5 + u * 0.5)


S.teleport(held, RUN0 - 0.05, V(RX0, RY, 0), 90)
S.walk(held, RUN0, END, [V(RX0, RY, 0), V(rx(END), RY, 0)], stride=0.95, arms=1.0)
S.beat(held, RUN0, "staan", face="vastberaden", face_amt=1.0, look=(0, 0), feet="keep", arms=None,
       body={"chest": (16, 0, 0), "head": (-14, 0, 0)})
S.beat(held, l5[0] + 3.2, "staan", face="inspanning", face_amt=1.0, look=(0, 0), mouth=0.15, feet="keep", arms=None,
       body={"chest": (20, 0, 0), "head": (-16, 0, 0)})
S.beat(held, SMOKE + 0.2, "staan", face="nerveus", face_amt=1.0, look=(0, -0.8), mouth=0.1, feet="keep", arms=None,
       body={"chest": (22, 0, 0), "head": (10, 0, 0)})
S.beat(held, FIRE + 0.1, "staan", face="bang", face_amt=1.0, look=(0.3, -0.5), mouth=0.45, feet="keep", arms=None,
       body={"chest": (18, 0, 0), "head": (6, 0, 14)})
S.beat(held, l7[0] + 0.5, "staan", face="geschrokken", face_amt=1.0, look=(0, 0.2), mouth=0.85, feet="keep", arms=None,
       body={"chest": (12, 0, 0), "head": (-10, 0, 0)})
S.hold(held, END)

# snelheidslijnen: de lucht raast langs hem, na de rook worden ze oranje (heet)
pfr = list(range(F(RUN0), F(END) + 1))
rnd = random.Random(5)
lw = S.mat("windlijn", (0.95, 0.97, 1.0), glow=1.6)
lh = S.mat("windlijn_heet", (1.0, 0.5, 0.12), glow=2.4)
for k in range(16):
    dy, z, ph, ln = rnd.uniform(-0.7, 0.7), rnd.uniform(0.25, 1.7), rnd.uniform(0, 3), rnd.uniform(0.5, 1.1)
    if abs(dy) < 0.3:
        dy = 0.3 if dy >= 0 else -0.3
    for mat, a0, a1 in ((lw, RUN0, SMOKE + 0.6), (lh, SMOKE + 0.6, END)):
        o = T.cyl(f"Windlijn_{k}_{mat.name}", (0, 0, 0), 0.008, ln, mat, rot=(0, 90, 0), seg=6, ol=0)
        o.visible_shadow = False
        bake(o, "location", pfr, [(rx((f - 1) / FPS) + 1.6 - (((f - 1) / FPS) * 9 + ph) % 3.4, RY + dy, z) for f in pfr])
        show(o, a0, a1)

# rook uit zijn schoenen, dan vlammen op zijn hoodie
for k, t in enumerate(frange(SMOKE, END, 0.18)):
    S.puff(V(rx(t) - 0.15, RY + (0.12 if k % 2 else -0.12), 0.1), t, n=2, r=(0.08, 0.16), grow=2.5, dur=0.9,
           color=(0.55, 0.55, 0.55), rise=0.5, spread=0.2)
fl_mats = [S.mat("vlam_geel", (1.0, 0.85, 0.2), glow=2.6), S.mat("vlam_oranje", (1.0, 0.45, 0.05), glow=2.2)]
rnd = random.Random(8)
for k in range(12):
    fl = T.cyl(f"Vlam_{k}", (0, 0, 0), 0.07 + rnd.uniform(0, 0.04), 0.3 + rnd.uniform(0, 0.2), fl_mats[k % 2], r2=0.004,
               seg=10, ol=0)
    bone = ("chest", "spine", "upper_arm.L", "upper_arm.R")[k % 4]
    attach(fl, held, bone, loc=(rnd.uniform(-0.16, 0.16), rnd.uniform(-0.1, 0.05), rnd.uniform(-0.26, -0.14)),
           rot=(-125 - rnd.uniform(0, 25), rnd.uniform(-20, 20), 0))
    fl.visible_shadow = False
    for t in frange(FIRE, END, 0.08):
        s = 0.001 if t < FIRE + k * 0.05 else rnd.uniform(0.7, 1.35) * min(1.0, (t - FIRE) / 0.4 + 0.3)
        key(fl, t, scale=(s, s, s * rnd.uniform(0.8, 1.4)))
    key(fl, FIRE - 0.05, scale=0.001)

# ---------------------------------------------------------------- camera (staand)
S.cam(S.t0, ((START.x + 3.4, START.y - 3.2, 1.1), (START.x, START.y, 0.85), 30), ((START.x + 3.0, START.y - 2.8, 1.0), (START.x, START.y, 0.8), 32))
S.cam(l3[0] + 1.6, ((START.x + 2.2, START.y - 1.2, 0.3), (START.x, START.y, 0.6), 24))
S.cam(GO + 0.5, ((START.x + 4, START.y - 3.5, 1.2), (START.x + 30, START.y + 1.5, 2.0), 20))
S.cam(BOOM - 0.15, ((BX - 4, -1.5, 1.3), (BX + 6, 9.0, 3.2), 18), ((BX - 4.5, -1.8, 1.2), (BX + 6, 9.0, 3.2), 19),
      shake=lambda t: 3.0 * max(0, 1 - (t - BOOM) / 1.0))
S.cam(l4[0] + 2.8, ((BX + 5, 3.5, 2.6), (BX + 8, 13.0, 3.0), 26), ((BX + 3, 3.0, 2.4), (BX + 8, 13.0, 3.0), 26))
# dag 3: tracking naast hem, laag
S.cam(RUN0, None, fn=lambda t: (V((rx(t) + 2.6, RY - 3.4, 0.9)), V((rx(t) + 0.3, RY, 1.0)), 26))
S.cam(l5[0] + 3.8, None, fn=lambda t: (V((rx(t) + 2.3, RY + 0.6, 1.5)), V((rx(t), RY, 1.25)), 30))
S.cam(SMOKE, None, fn=lambda t: (V((rx(t) + 1.7, RY - 2.1, 0.45)), V((rx(t) - 0.2, RY, 0.45)), 26))
S.cam(FIRE - 0.1, None, fn=lambda t: (V((rx(t) + 2.4, RY - 2.4, 1.6)), V((rx(t), RY, 1.2)), 28))
S.cam(l7[0] + 0.4, None, fn=lambda t: (V((rx(t) + 2.3, RY - 1.1, 1.3)), V((rx(t), RY, 1.3)), 34),
      shake=lambda t: 0.6 + 1.2 * smooth(l7[0], l7[1], t))

S.card("", l7[1] - 0.12, l7[1] + 0.25, dim=1.0, bg=(1, 1, 1), fin=1, fout=6)
S.done()
