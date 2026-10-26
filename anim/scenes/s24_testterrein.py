"""S24 · Dag 27 · het testterrein. 'How hard can you hit?' Eén zachte stoot op de woestijnbodem, en een seismograaf
in een ander land meet een aardbeving van 3. Dit stuk is echt: elke stap op de schaal is ~32x meer energie.

    blender -b -P anim/scenes/s24_testterrein.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s24", "woestijn", "testterrein")

HERO_AT = V(0.0, 0.0, 0.0)
FIST = V(0.05, -0.55, 0.02)                    # waar zijn vuist de grond raakt
TABLE = V(-5.5, 2.8, 0.0)
DK = V(0.0, -260.0, 0.0)                       # station in een ander land
RED = (1.0, 0.25, 0.2, 1)

held = S.actor("hoofdpersonage", HERO_AT, 0)
prof = S.actor("wetenschapper", TABLE + V(0.9, -0.7, 0), heading(TABLE + V(0.9, -0.7, 0), HERO_AT), energy=1.0)
LABCOAT = dict(shirt=(0.95, 0.95, 0.93), broek=(0.30, 0.32, 0.40))
helper = S.actor("wetenschapper", TABLE + V(-0.4, -0.75, 0), heading(TABLE + V(-0.4, -0.75, 0), TABLE), energy=0.7, label="onderzoeker_0",
                 outfit=dict(LABCOAT, haar=(0.15, 0.1, 0.07)), drop=("bril",))
sold = S.actor("officier", V(-9.0, -1.5, 0), heading((-9.0, -1.5), HERO_AT), energy=0.6)

# ---------------------------------------------------------------- het station ver weg
T.box("Station_vloer", (DK.x, DK.y, -0.1), (6, 5, 0.1), S.mat("station_vloer", (0.42, 0.40, 0.38)), bevel=0, ol=0)
T.box("Station_muur", (DK.x, DK.y + 1.4, 0), (6, 0.15, 3.0), S.mat("station_muur", (0.72, 0.76, 0.80)), bevel=0, ol=0.01)
T.box("Station_raam", (DK.x + 1.6, DK.y + 1.31, 1.1), (1.4, 0.02, 1.0), S.mat("station_nacht", (0.10, 0.14, 0.30), 1.0), bevel=0, ol=0.006)
T.box("Station_kaart", (DK.x - 1.6, DK.y + 1.31, 1.0), (1.6, 0.02, 1.1), S.mat("station_kaart", (0.35, 0.55, 0.75)), bevel=0, ol=0.006)
T.text("Station_bord", "SEISMIC STATION 7", (DK.x - 1.6, DK.y + 1.29, 2.25), 0.13, S.mat("krijt", (0.95, 0.95, 0.9)), extrude=0.0)
T.box("Station_tafel", (DK.x, DK.y + 0.8, 0), (2.2, 0.9, 0.78), S.mat("station_tafel", (0.3, 0.3, 0.33)), bevel=0.01, ol=0.008)
drum = T.cyl("Station_trommel", (0, 0, 0), 0.13, 0.62, S.mat("seismo_papier", (0.97, 0.96, 0.92)), rot=(0, 90, 0), seg=28, ol=0.004)
drum.location = (DK.x - 0.41, DK.y + 0.85, 1.0)
paper = T.box("Station_strook", tuple(DK + V(-0.1, 0.25, 0.87)), (0.55, 0.9, 0.003), S.mat("seismo_papier", (0.97, 0.96, 0.92)), base=False, bevel=0, ol=0.003)
arm_o = T.box("Station_naald", (0, -0.16, 0), (0.012, 0.32, 0.012), S.mat("naald", (0.15, 0.15, 0.18)), base=False, bevel=0, ol=0.003)
T.sphere("Station_punt", (0, -0.32, 0), 0.012, S.mat("inkt", (0.85, 0.1, 0.1)), seg=8, ol=0).parent = arm_o
needle = hinge(arm_o, tuple(DK + V(-0.1, 1.0, 0.9)))
T.area_light("Station_licht", (DK.x, DK.y - 0.6, 2.8), (0, 0, 0), size=(3, 2), color=(0.85, 0.9, 1.0), energy=260)
T.point_light("Station_lamp", tuple(DK + V(0.8, 0.6, 1.4)), color=(1.0, 0.8, 0.55), energy=40, radius=0.2)

# ---------------------------------------------------------------- tijdlijn
S.hud(27, "134,217,728x STRONGER", t0=0.4)
S.ambience("sfx_wind_hoog", 0.0, 60, vol=0.07)
S.music("subbas", 0.2, 60, vol=0.24, fade_in=1.2, fade_out=1.5)
l1 = S.say("S24-01", gap=0.7)
WANT = l1[0] + 4.03
HOW = l1[0] + 6.37                             # 'How hard can you hit?'
l2 = S.say("S24-02", gap=0.8)
ONCE = l2[0] + 2.01
GENTLY = l2[0] + 2.82
HIT = ONCE + 0.15
l3 = S.say("S24-03", gap=0.9)
l4 = S.say("S24-04", gap=0.8)
ENERGY = l4[0] + 1.87
STEP = l4[0] + 3.91                            # 'Every step up the scale...'
SMALL = l4[0] + 8.83                           # 'Your gentle punch is a small earthquake.'
TOMORROW = l4[0] + 11.2                        # 'And tomorrow, it's twice as big.'
S.wait(1.8)
END = S.t
S.sfx("sfx_dreun", HIT, 0.3)
S.sfx("sfx_aardbeving", HIT + 0.05, 0.22)
S.sfx("sfx_seismograaf", l3[0] - 0.2, 0.22)
S.text("SEISMIC STATION · 1,400 KM AWAY", l3[0] + 0.1, l3[1] + 0.3, loc=(0.965, 0.22), size=48, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("MAGNITUDE 3.0", l3[0] + 2.0, l3[1] + 0.3, loc=(0.965, 0.14), size=60, color=RED, anchor=("RIGHT", "BOTTOM"))
S.real(l4[0] + 0.1, SMALL - 0.2)
S.gauge("EACH STEP: ~32x MORE ENERGY", STEP + 0.3, SMALL - 0.2, color=WHITE)
S.gauge("TOMORROW: x2", TOMORROW + 0.6, END, color=RED)

# ---------------------------------------------------------------- hij: knielt, legt zijn vuist heel zacht op de grond
KNEEL = dict(pose="staan", crouch=(0.5, 22), feet=((0.18, -0.3, 0.25), (-0.18, 0.3, 0)))
PUNCH_UP = arm("R", (0.2, 0.75, -0.3), (0.05, 0.7, 0.4))
PUNCH_DN = arm("R", (0.15, 0.55, -0.82), (0.05, 0.35, -0.94))
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.6, at=S.head(prof, 0))
S.beat(held, HOW - 0.3, "staan", face="twijfel", face_amt=0.6, look=(0, -0.5), body={"head": (14, 0, 0)}, arms=LOOK_HANDS)
S.beat(held, l2[0] - 0.4, **KNEEL, face="vastberaden", face_amt=0.5, look=(0, -0.7), body={"head": (20, 0, 0), "spine": (10, 0, 0)})
S.beat(held, l2[0] + 1.0, **KNEEL, face="vastberaden", face_amt=0.6, look=(0, -0.7), body={"head": (20, 0, 0), "spine": (12, 0, 0)}, arms=PUNCH_UP)
S.beat(held, ONCE - 0.2, **KNEEL, face="inspanning", face_amt=0.3, look=(0, -0.8), body={"head": (24, 0, 0), "spine": (16, 0, 0)}, arms=PUNCH_UP)
S.beat(held, HIT, **KNEEL, face="inspanning", face_amt=0.4, look=(0, -0.8), body={"head": (24, 0, 0), "spine": (20, 0, 0)}, arms=PUNCH_DN)
S.beat(held, HIT + 0.5, **KNEEL, face="geschrokken", face_amt=0.8, look=(0, -0.4), body={"head": (8, 0, 0), "spine": (6, 0, 0)}, arms=PUNCH_DN)
S.beat(held, l3[0] + 0.3, **KNEEL, face="nerveus", face_amt=0.8, look=(0.5, 0.3), body={"head": (-4, 30, 0)})
S.beat(held, l4[0] + 0.4, "staan", face="nerveus", face_amt=0.6, look=(0, -0.3))
S.beat(held, SMALL + 0.2, "staan", face="verdrietig", face_amt=0.7, arms=arm("R", (0.2, 0.4, -0.85), (-0.1, 0.7, 0.7)), look=(0, -0.4),
       body={"head": (14, 0, 0)})
S.beat(held, TOMORROW + 0.5, "staan", face="bang", face_amt=0.7, look=(0, 0.1), body={"head": (0, 0, 0)})
S.hold(held, END)
S.beat(prof, 0.0, "staan", face="neutraal", face_amt=0.7, at=S.head(held, 0), arms=HOLD_FRONT_R)
S.beat(prof, WANT, "staan", face="vastberaden", face_amt=0.6, at=S.head(held, WANT), arms=HOLD_FRONT_R)
S.beat(prof, HIT + 0.3, "schrik", amount=0.8, face="geschrokken", face_amt=1.0, at=S.head(held, HIT))
S.beat(prof, l3[0] + 0.5, "handen_hoofd", amount=0.6, face="verbaasd", face_amt=0.9, at=TABLE + V(0, 0, 0.9))
S.hold(prof, END)
S.beat(helper, 0.0, "staan", face="neutraal", face_amt=0.6, at=TABLE + V(0, 0, 0.9))
S.beat(helper, HIT + 0.35, "schrik", amount=0.7, face="geschrokken", face_amt=0.9, at=TABLE + V(0, 0, 0.9))
S.hold(helper, END)
S.beat(sold, 0.0, "staan", face="neutraal", face_amt=0.7, at=S.head(held, 0))
S.beat(sold, HIT + 0.3, "schrik", amount=0.6, face="bang", face_amt=0.8, at=S.head(held, HIT))
S.hold(sold, END)

# de stoot: een golf door het zand, sensoren knipperen, palen trillen, de jeep springt op
S.ring(FIST + V(0, 0, 0.05), HIT, r0=0.2, r1=40.0, dur=1.6, color=(1.0, 0.85, 0.6), strength=1.6, thick=0.1)
S.ring(FIST + V(0, 0, 0.05), HIT + 0.25, r0=0.2, r1=60.0, dur=2.2, color=(1.0, 0.85, 0.6), strength=1.0, thick=0.08)
S.puff(FIST, HIT, n=6, r=(0.15, 0.3), grow=2.2, dur=1.4, color=(0.90, 0.75, 0.52), rise=0.4, spread=0.6)
for k in range(10):
    p = S.obj(f"Sensorpaal_{k}")
    s = S.obj(f"Sensor_{k}")
    led = S.obj(f"Sensorlampje_{k}")
    if not p:
        continue
    d = p.location.length
    tk = HIT + d / 40.0                        # de golf komt aan
    for o in (p, s, led):
        r0 = o.rotation_euler.copy()
        key(o, tk - 0.02, rot=tuple(math.degrees(a) for a in r0))
        key(o, tk + 0.08, rot=(math.degrees(r0.x) + 6, 0, math.degrees(r0.z)))
        key(o, tk + 0.25, rot=(math.degrees(r0.x) - 3, 0, math.degrees(r0.z)))
        key(o, tk + 0.45, rot=tuple(math.degrees(a) for a in r0))
    if led:
        visible(led, 0.0, False)
        for j, t in enumerate(frange(tk, END, 0.3)):
            visible(led, t, j % 2 == 0)
jeep = S.obj("Jeep_test")
if jeep:
    j0 = jeep.location.copy()
    tk = HIT + j0.length / 40.0
    key(jeep, tk - 0.02, loc=j0)
    key(jeep, tk + 0.1, loc=j0 + V(0, 0, 0.18))
    key(jeep, tk + 0.25, loc=j0)
S.debris(FIST + V(0, 0, 0.05), HIT, n=30, size=(0.02, 0.06), color=(0.86, 0.68, 0.45), speed=(1.0, 3.5), up=1.6, floor=0.0, life=1.6)

# de naald in het station slaat van het papier
amp = lambda t: 0.01 + 0.5 * smooth(l3[0] + 0.6, l3[0] + 1.0, t) * (1 - 0.7 * smooth(l3[1], l3[1] + 1.5, t))
fr = list(range(1, F(END) + 2))
bake(needle, "rotation_euler", fr, [(0, 0, amp((f - 1) / FPS) * math.sin(f * 2.1)) for f in fr])
bake(drum, "rotation_euler", fr, [((f - 1) / FPS * 1.2, math.radians(90), 0) for f in fr])

# energie per stap: drie blokken (M1, M2, M3), elk ~32x zoveel (volume), naast hem in het zand
gm = S.mat("energieblok", (1.0, 0.55, 0.15), 1.6)
for k, (lbl, sz) in enumerate((("M1", 0.35), ("M2", 0.35 * 32 ** (1 / 3)), ("M3", 0.35 * 1024 ** (1 / 3)))):
    x = 3.0 + [0, 1.2, 4.0][k]
    b = T.box(f"Energieblok_{lbl}", (x, 2.0, 0), (sz, sz, sz), gm, bevel=0.02, ol=0.02)
    t0 = STEP + 0.4 + k * 0.9
    key(b, t0 - 1 / FPS, scale=0.001)
    key(b, t0 + 0.25, scale=1.0)
    lab = T.text(f"Energieblok_tekst_{lbl}", lbl, (x, 2.0 - sz / 2 - 0.05, sz + 0.25), 0.35, S.mat("blok_tekst", (1, 1, 1), 2.0), extrude=0.0)
    show(lab, t0 + 0.1)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-14, -16, 3.0), (10, 3, 1.0), 24), ((-12, -15, 2.8), (8, 2, 1.0), 26))
S.cam(WANT - 0.2, ((-3.2, -1.6, 1.6), (-5.4, 2.4, 1.2), 30), ((-3.4, -1.4, 1.6), (-5.4, 2.4, 1.2), 32))
S.cam(HOW - 0.1, S.shot(held, HOW, "mcu", az=15, lens=34), S.shot(held, l1[1], "mcu", az=12, lens=38))
S.cam(l2[0] - 0.2, ((1.5, -2.6, 0.5), (0.0, -0.4, 0.55), 28), ((1.3, -2.3, 0.45), (0.0, -0.4, 0.5), 30))
S.cam(HIT - 0.4, (FIST + V(0.9, -0.5, 0.25), FIST + V(0, 0, 0.1), 34), (FIST + V(0.85, -0.45, 0.22), FIST + V(0, 0, 0.1), 36),
      shake=lambda t: max(0.0, 1.4 - (t - HIT) * 1.4) if t > HIT else 0.0)
S.cam(GENTLY + 0.2, ((-10, -28, 9), (12, 6, 0), 24), ((-10, -30, 10), (12, 6, 0), 24),
      shake=lambda t: max(0.0, 0.8 - (t - HIT) * 0.6) if t > HIT else 0.0)
S.cam(l3[0] - 0.2, ((DK.x + 0.7, DK.y - 0.6, 1.4), (DK.x - 0.1, DK.y + 0.45, 0.9), 32), ((DK.x + 0.55, DK.y - 0.4, 1.3), (DK.x - 0.1, DK.y + 0.45, 0.9), 40),
      shake=lambda t: 0.6 * smooth(l3[0] + 0.6, l3[0] + 0.9, t))
S.cam(l4[0] - 0.2, ((-4.0, -6.5, 1.8), (3.5, 1.5, 1.0), 24), ((-3.5, -6.0, 1.9), (4.5, 1.8, 1.2), 26))
S.cam(SMALL - 0.2, S.shot(held, SMALL, "mcu", az=20, lens=34), S.shot(held, TOMORROW, "mcu", az=16, lens=38))
S.cam(TOMORROW + 0.4, ((0.0, -6.0, 1.2), (0, 0, 1.1), 30), ((0.0, -40, 18), (0, 0, 1.0), 26))

S.finish(length=END)
