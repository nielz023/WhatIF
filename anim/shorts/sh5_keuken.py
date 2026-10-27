"""SH5 · What if you shrank 10x every hour? · keukenvloer: kleren te groot, de mok als wolkenkrabber, een mier als
een paard. Daarna de 'macro-vloer' (los gebouwd, schaal 1000x en 10.000x): stofkorrels als rotsblokken, een
waterdruppel die je vasthoudt, en dan gaat de stofzuiger aan.

    blender -b -P anim/shorts/sh5_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh5", "a", "keuken", "ochtend", lines=(1, 2, 3, 4, 5, 6, 7, 8))
l1, l2, l3, l4, l5, l6, l7, l8 = (S.L[n] for n in range(1, 9))
END = S.t1
for n in ("Krant", "Ontbijt_broertje", "Ontbijt_bord"):
    o = S.obj(n)
    if o:
        o.hide_render = True

HP = V(1.25, 0.45, 0)                           # waar hij krimpt (open stuk keukenvloer)
CUT = l4[0]                                     # snede naar de macro-vloer
held = S.actor("hoofdpersonage", HP, 0)
rig = held.rig


# ---------------------------------------------------------------- schaal: 1 -> 0,1 -> 0,01, daarna macro (1)
def scale_at(t):
    if t >= CUT:
        return 1.0
    a = smooth(0.3, 4.4, t)                     # uur 0 -> 1
    b = smooth(l3[0] + 0.2, l3[0] + 1.5, t)     # uur 1 -> 2
    return 10 ** (-(a + b))


fr = list(range(1, F(CUT)))
bake(rig, "scale", fr, [(scale_at((f - 1) / FPS),) * 3 for f in fr])
key(rig, CUT, scale=1.0, interp="CONSTANT")
for fc in A._fcurves(rig):
    if fc.data_path == "scale":
        for kp in fc.keyframe_points:
            if kp.co.x >= F(CUT) - 1.5:
                kp.interpolation = "CONSTANT"

# ---------------------------------------------------------------- kleren, mok, mier
hoodie = S.mat("hoodie_hoop", (0.84, 0.19, 0.03))
jeans = S.mat("broek_hoop", (0.06, 0.08, 0.14))
pile = []
pile.append(T.sphere("Kleren_hoodie", tuple(HP + V(0.02, 0.42, 0)), 0.3, hoodie, scale=(1.25, 1.0, 0.32), ol=0.006))
pile.append(T.sphere("Kleren_broek", tuple(HP + V(-0.22, 0.62, 0)), 0.22, jeans, scale=(1.4, 0.8, 0.28), ol=0.006))
pile.append(T.cyl("Kleren_kraag", tuple(HP + V(0.05, 0.34, 0.088)), 0.075, 0.01, S.mat("kraag_gat", (0.12, 0.04, 0.02)),
                  seg=20, ol=0.003))
for k, s_ in enumerate((-1, 1)):
    pile.append(T.box(f"Kleren_schoen_{k}", tuple(HP + V(0.3 * s_, 0.66 + 0.06 * k, 0)), (0.11, 0.26, 0.09),
                      S.mat("schoen", (0.95, 0.95, 0.95)), bevel=0.03, ol=0.005, rot=(0, 0, 20 * s_)))
for k, o in enumerate(pile):
    s0 = o.scale.copy()
    key(o, 0, scale=0.001)
    key(o, 1.3 + k * 0.08, scale=0.001)
    key(o, 2.0 + k * 0.08, scale=tuple(s0))
MUG = HP + V(0.2, -0.06, 0)
mug_m = S.mat("mok_wit", (0.93, 0.92, 0.88))
mug = T.cyl("Mok", (0, 0, 0), 0.05, 0.13, mug_m, seg=28, ol=0.003)
T.cyl("Mok_koffie", (0, 0, 0.12), 0.046, 0.004, S.mat("koffie", (0.25, 0.13, 0.05)), seg=28, ol=0).parent = mug
ear = T.torus("Mok_oor", (0.057, 0, 0.068), 0.032, 0.007, mug_m, rot=(90, 0, 0), ol=0.002)
ear.parent = mug
key(mug, 0, loc=tuple(HP + V(0.24, -0.16, 0.78)))
key(mug, 1.0, loc=tuple(HP + V(0.22, -0.12, 0.62)))
key(mug, 1.38, loc=tuple(MUG), interp="LINEAR")
S.puff(MUG + V(0, 0, 0.02), 1.4, n=4, r=(0.02, 0.04), grow=1.6, dur=0.6, color=(0.45, 0.28, 0.12), rise=0.05, spread=0.12)

# de mier: gebouwd op 1,6 m lang, daarna 0,01 (1,6 cm)
ant = bpy.data.objects.new("Mier", None)
T._link(ant)
ant_m = S.mat("mier", (0.28, 0.1, 0.06))
eye_m = S.mat("mier_oog", (0.03, 0.03, 0.03))
parts = [T.sphere("Mier_achterlijf", (-0.55, 0, 0.42), 0.38, ant_m, scale=(1.3, 1.0, 0.9), ol=0.03),
         T.sphere("Mier_borst", (0.05, 0, 0.42), 0.18, ant_m, scale=(1.6, 0.9, 0.9), ol=0.03)]
head = bpy.data.objects.new("Mier_kop", None)
T._link(head)
head.location = (0.42, 0, 0.5)
hp = [T.sphere("Mier_kopbol", (0.12, 0, 0), 0.2, ant_m, scale=(1.1, 1.1, 0.95), ol=0.03),
      T.sphere("Mier_oog_L", (0.2, 0.15, 0.06), 0.06, eye_m, ol=0.0),
      T.sphere("Mier_oog_R", (0.2, -0.15, 0.06), 0.06, eye_m, ol=0.0)]
for s_ in (-1, 1):
    hp.append(T.tube(f"Mier_voelspriet_{s_}", [(0.2, 0.06 * s_, 0.12), (0.36, 0.2 * s_, 0.42), (0.62, 0.3 * s_, 0.5)],
                     0.018, ant_m, ol=0.01))
    hp.append(T.tube(f"Mier_kaak_{s_}", [(0.28, 0.08 * s_, -0.08), (0.42, 0.04 * s_, -0.1), (0.46, -0.02 * s_, -0.06)],
                     0.025, ant_m, ol=0.01))
for o in hp:
    o.parent = head
legs = []
for k, x in enumerate((-0.1, 0.05, 0.2)):
    for s_ in (-1, 1):
        lg = bpy.data.objects.new(f"Mier_poot_{k}_{s_}", None)
        T._link(lg)
        lg.location = (x, 0.1 * s_, 0.4)
        lg.parent = ant
        T.tube(f"Mier_poot_mesh_{k}_{s_}", [(0, 0, 0), ((k - 1) * 0.25, 0.4 * s_, 0.18), ((k - 1) * 0.5, 0.75 * s_, -0.4)],
               0.025, ant_m, ol=0.01).parent = lg
        legs.append((lg, k, s_))
for o in parts + [head]:
    o.parent = ant
ant.scale = (0.01,) * 3
A0, A1 = HP + V(0.09, 0.05, 0), HP + V(0.026, 0.004, 0)
ANT_GO, ANT_STOP, ANT_LOOK = l3[0] + 1.2, l3[0] + 3.4, l3[1] - 1.6
key(ant, 0, loc=tuple(A0), rot=(0, 0, 200))
key(ant, ANT_GO, loc=tuple(A0), rot=(0, 0, 200))
key(ant, ANT_STOP, loc=tuple(A1), rot=(0, 0, 186))
for t in frange(ANT_GO, ANT_STOP, 0.09):
    k = int(round((t - ANT_GO) / 0.09))
    for lg, i, s_ in legs:
        ph = 1 if (k + i + (s_ > 0)) % 2 else -1
        key(lg, t, rot=(0, 0, 14 * ph))
for lg, i, s_ in legs:
    key(lg, ANT_STOP + 0.05, rot=(0, 0, 0))
key(head, 0, rot=(0, 0, 0))
key(head, ANT_LOOK - 0.3, rot=(0, 0, 0))
key(head, ANT_LOOK, rot=(0, -12, -18))
show(ant, l3[0] - 0.05, CUT)

# ---------------------------------------------------------------- de macro-vloer (x = 80): 1 m = 1 mm
MX = V(80.0, 0, 0)
macro = bpy.data.objects.new("Macro", None)
T._link(macro)
macro.location = MX
mobj = []
floor_m = S.mat("macro_tegel", (0.8, 0.74, 0.64))
mobj.append(T.box("Macro_vloer", tuple(MX + V(0, 0, -0.5)), (600, 600, 0.5), floor_m, bevel=0, ol=0))
mobj.append(T.box("Macro_voeg", tuple(MX + V(0, 14, -0.02)), (600, 4.0, 0.03), S.mat("macro_voeg", (0.5, 0.46, 0.4)),
                  bevel=0, ol=0))
rnd = random.Random(11)
dust_cols = [(0.55, 0.52, 0.5), (0.62, 0.58, 0.52), (0.45, 0.4, 0.36), (0.7, 0.66, 0.6)]
grains = []
for k in range(46):
    a, d = rnd.uniform(0, 6.283), rnd.uniform(2.2, 26)
    p = MX + V(d * math.cos(a), d * math.sin(a) + 3, 0)
    if abs(p.y - MX.y) < 2.0 and p.x > MX.x - 3 and p.x < MX.x + 8:
        continue                                   # zijn looppad vrij
    if MX.x - 8 < p.x < MX.x + 4 and p.y < MX.y + 1.2:
        continue                                   # en het zicht van de camera's
    r = rnd.uniform(0.25, 1.5) * (1 + d / 20)
    g = rock(f"Stofkorrel_{k}", p + V(0, 0, r * 0.45), r, S.mat(f"stof_{k % 4}", dust_cols[k % 4]), seed=k)
    grains.append(g)
mobj += grains
mobj.append(rock("Kruimel", MX + V(-6, 7, 1.4), 3.0, S.mat("kruimel", (0.86, 0.62, 0.3)), seed=99, squash=0.6))
hair_m = S.mat("haar_macro", (0.18, 0.11, 0.06))
mobj.append(T.tube("Haar_1", [tuple(MX + V(x, 9 + 3 * math.sin(x / 9), 0.08)) for x in range(-60, 61, 6)], 0.08, hair_m, ol=0.02))
mobj.append(T.tube("Haar_2", [tuple(MX + V(-8 + 2 * math.sin(y / 7), y, 0.08)) for y in range(-40, 50, 6)], 0.06, hair_m, ol=0.02))
# achtergrond: een warme, wazige keuken (binnenkant van een grote bol) en reuzenpoten van stoel en tafel
bg = T.sphere("Macro_lucht", tuple(MX), 2600, T.glow("macro_lucht", (0.86, 0.8, 0.7), 1.0), seg=32, ol=0)
bg.visible_shadow = False
for k, (dx, dy, r) in enumerate(((260, 500, 26), (-320, 620, 26), (90, 900, 40), (-700, 300, 34))):
    T.cyl(f"Reuzenpoot_{k}", tuple(MX + V(dx, dy, 0)), r, 2400, S.mat("reuzenpoot", (0.55, 0.36, 0.2)), seg=24,
          ol=0).visible_shadow = False
# waterdruppel (r 1,6 m = 1,6 mm)
water = T.glass("water", (0.55, 0.78, 0.98), 0.32)
DROP = MX + V(1.45, -0.15, 0)
drop = T.sphere("Druppel", (0, 0, 0), 1.6, water, seg=40, ol=0.008)
DROP_HIT = l5[0] + 0.9
key(drop, 0, loc=tuple(DROP + V(0, 0, 40)), scale=(0.85, 0.85, 1.25))
key(drop, DROP_HIT - 0.45, loc=tuple(DROP + V(0, 0, 40)), scale=(0.85, 0.85, 1.25))
key(drop, DROP_HIT, loc=tuple(DROP + V(0, 0, 1.0)), scale=(0.85, 0.85, 1.25), interp="LINEAR")
key(drop, DROP_HIT + 0.12, loc=tuple(DROP + V(0, 0, 0.55)), scale=(1.35, 1.35, 0.5))
key(drop, DROP_HIT + 0.35, loc=tuple(DROP + V(0, 0, 0.9)), scale=(1.1, 1.1, 0.75))
key(drop, DROP_HIT + 0.6, loc=tuple(DROP + V(0, 0, 0.8)), scale=(1.18, 1.18, 0.68))
show(drop, DROP_HIT - 0.45, l6[0])
S.debris(DROP + V(0, 0, 0.3), DROP_HIT + 0.05, n=14, size=(0.08, 0.2), color=(0.7, 0.88, 1.0), speed=(3, 6), up=1.3,
         floor=0.0, life=1.2, name="Spat")
mobj.append(drop)
parent_keep(mobj, macro)
# uur 4: alles 10x groter (hij is weer 10x kleiner)
key(macro, 0, scale=1.0)
key(macro, l6[0] - 0.02, scale=1.0)
key(macro, l6[0], scale=10.0)
for fc in A._fcurves(macro):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"

# de stofzuigermond: een donkere spleet die op hem af komt (uur 4: 3 cm = 300 m)
VAC0, VAC1 = l7[0] - 0.4, END
vac = bpy.data.objects.new("Stofzuiger", None)
T._link(vac)
vm = S.mat("stofzuiger", (0.2, 0.21, 0.24))
blk = S.mat("stofzuiger_gat", (0.0, 0.0, 0.0))
vparts = [T.box("Zuigmond_boven", (0, 0, 70), (120, 1400, 110), vm, bevel=6, ol=0),
          T.box("Zuigmond_gat", (-55, 0, 2), (20, 1300, 68), blk, bevel=0, ol=0),
          T.box("Zuigmond_rand", (-58, 0, 0), (8, 1380, 6), S.mat("stofzuiger_rand", (0.35, 0.36, 0.4)), bevel=1, ol=0),
          T.cyl("Zuigbuis", (40, 0, 120), 70, 900, vm, rot=(0, -30, 0), seg=32, ol=0)]
for k in range(60):
    vparts.append(T.box(f"Borstel_{k}", (-68, -640 + k * 22, 0), (3, 3, 10), S.mat("borstel", (0.15, 0.15, 0.16)), bevel=0, ol=0))
for o in vparts:
    o.parent = vac
    o.visible_shadow = False
VX = lambda t: MX.x + 1700 - 1450 * smooth(VAC0, VAC1, t) ** 0.8
for t in frange(VAC0, VAC1 + 0.05, 0.2):
    key(vac, t, loc=(VX(t), MX.y + 40, 0))
key(vac, VAC0, rot=(0, 0, 0))
show(vac, VAC0)

# stof dat naar de mond wordt gezogen
rnd = random.Random(21)
SUCK = l7[0] + 1.0
for k in range(36):
    r = rnd.uniform(0.5, 3.0)
    p0 = MX + V(rnd.uniform(-60, 40), rnd.uniform(-40, 50), r * 0.4)
    g = rock(f"Zuigstof_{k}", p0, r, S.mat(f"stof_{k % 4}", dust_cols[k % 4]), seed=200 + k)
    t0 = SUCK + rnd.uniform(0, 3.5)
    key(g, 0, loc=tuple(p0), rot=(0, 0, 0))
    key(g, t0, loc=tuple(p0), rot=(0, 0, 0))
    for j, dt in enumerate((0.6, 1.2, 1.8, 2.4)):
        t = t0 + dt
        u = (dt / 2.4) ** 2.2
        tgt = V(VX(t) - 60, MX.y + 40, 30)
        p = p0.lerp(tgt, u) + V(0, 0, 20 * u * (1 - u) * 4)
        key(g, t, loc=tuple(p), rot=(rnd.uniform(-1, 1) * 400 * u, rnd.uniform(-1, 1) * 400 * u, 0))
    show(g, l6[0])

# ---------------------------------------------------------------- muziek, geluid, tellers
S.music_all("pizz_spanning", vol=0.22)
S.music("drone", l6[0] - 0.4, END, vol=0.22, fade_in=1.0)
S.ambience("sfx_binnen_sfeer", 0.0, CUT, vol=0.12)
S.sfx("sfx_krimp", 0.3, 0.5)
S.sfx("sfx_mok_breekt", 1.36, 0.25)
S.sfx("sfx_krimp", l3[0] + 0.15, 0.45)
S.sfx("sfx_krimp", l4[0] - 0.05, 0.45)
S.sfx("sfx_krimp", l6[0] - 0.05, 0.45)
S.sfx("sfx_dreun", DROP_HIT, 0.4)
S.sfx("sfx_aardbeving", l6[1] - 1.6, 0.3)
S.sfx("sfx_stofzuiger", l7[0] - 0.3, 0.42, loop_to=END)
S.sfx("sfx_cliffhanger", l7[1] - 2.0, 0.7)
S.counter("HOUR 1", l2[0] + 0.05, l3[0] + 0.1, sub="18 cm")
S.counter("HOUR 2", l3[0] + 0.2, CUT, sub="1.8 cm")
S.counter("HOUR 3", CUT + 0.05, l6[0], sub="1.8 mm")
S.counter("HOUR 4", l6[0] + 0.05, l8[0], color=RED, sub="0.18 mm")
S.real(l5[0] + 0.1, l5[1] - 2.0)

# ---------------------------------------------------------------- acteren in de keuken
S.beat(held, 0.0, "staan", face="neutraal", look=(0, -0.2))
S.reach(held, 0.0, "R", HP + V(0.24, -0.16, 0.86))
S.reach(held, 0.95, "R", None, 0.0)
S.beat(held, 0.6, "schrik", amount=0.7, face="geschrokken", face_amt=1.0, look=(0, -0.7), mouth=0.5)
S.beat(held, 2.4, "armen_omhoog", amount=0.7, face="geschrokken", face_amt=1.0, look=(0.2, 0.6), mouth=0.6)
S.beat(held, l1[1] - 1.5, "handen_hoofd", face="verbaasd", face_amt=1.0, look=(0, 0.6), mouth=0.3)
S.beat(held, l2[0] + 0.4, "staan", face="verbaasd", face_amt=1.0, look=(0.6, 0.9), mouth=0.35,
       body={"head": (-24, 0, -20)})                      # omhoog naar de mok
S.beat(held, l2[1] - 1.2, "schouders_op", face="nerveus", face_amt=0.9, look=(0.4, 0.5), mouth=0.1,
       body={"head": (-14, 0, -12)})
S.beat(held, l3[0] + 0.25, "schrik", amount=0.6, face="geschrokken", face_amt=1.0, look=(0, 0.5), mouth=0.4)
S.beat(held, ANT_GO + 0.5, "staan", face="bang", face_amt=0.9, look=(0.8, 0), mouth=0.25, body={"head": (0, 0, -30)})
S.beat(held, ANT_STOP, "schrik", amount=0.9, face="bang", face_amt=1.0, look=(0.9, 0.1), mouth=0.35,
       body={"head": (-6, 0, -40)})
S.beat(held, ANT_LOOK + 0.2, "schrik", amount=1.0, face="geschrokken", face_amt=1.0, look=(0.9, 0.2), mouth=0.6,
       body={"head": (-8, 0, -45)})
S.hold(held, CUT - 0.05)

# ---------------------------------------------------------------- macro: uur 3 en 4
S.teleport(held, CUT, MX + V(-2.5, 0, 0), 90)
W0, W1 = CUT + 0.6, CUT + 4.6
S.walk(held, W0, W1, [MX + V(-2.5, 0, 0), MX + V(-0.8, -0.4, 0), MX], stride=0.4, arms=0.6, end_rot=60)
S.beat(held, CUT, "staan", face="verbaasd", face_amt=1.0, look=(0.5, 0.6), mouth=0.3, body={"head": (-18, 0, 0)})
S.beat(held, W0 + 0.5, "staan", face="verbaasd", face_amt=0.8, look=(0.6, 0.4), feet="keep", mouth=0.1)
S.beat(held, W1, "staan", face="nerveus", face_amt=0.7, look=(0.5, 0.3), mouth=0.0)
# de druppel valt half over hem heen; hij trekt en trekt
S.beat(held, DROP_HIT + 0.05, "schrik", amount=1.0, face="geschrokken", face_amt=1.0, look=(0.9, 0), mouth=0.6)
for k, t in enumerate(frange(DROP_HIT + 0.9, l5[1] + 0.2, 0.5)):
    S.beat(held, t, "duwen" if k % 2 else "schrap", face="inspanning", face_amt=1.0, look=(-0.6, 0), mouth=0.2,
           body={"chest": (0, 0, 14 if k % 2 else 4), "spine": (0, 0, 10)}, crouch=(0.06, 6))
S.beat(held, l6[0] + 0.1, "staan", face="nerveus", face_amt=1.0, look=(0.3, 0.2), mouth=0.05, body={"head": (-10, 0, 0)})
S.beat(held, l6[1] - 0.4, "schrap", face="bang", face_amt=1.0, look=(-0.9, 0.1), mouth=0.25, body={"head": (0, 0, 40)})
S.turn(held, l7[0] + 0.2, l7[0] + 0.8, 90)
S.beat(held, l7[0] + 0.8, "schrap", face="geschrokken", face_amt=1.0, look=(0, 0.3), mouth=0.7, crouch=(0.12, 10),
       body={"chest": (-10, 0, 0)})
LIFT = l7[1] - 0.6
S.beat(held, LIFT + 0.3, "armen_omhoog", face="schreeuw", face_amt=1.0, look=(-0.5, -0.3), mouth=1.0)
S.hold(held, END)
fr2 = list(range(F(LIFT), F(END) + 1))


def fly(t):
    """Opgetild en naar de zuigmond getrokken: komt daar precies op het eind aan."""
    u = min(1.0, max(0.0, (t - LIFT) / (END - LIFT)))
    w = u ** 2.4
    return MX + V((VX(END) - 70 - MX.x) * w, 40 * w, 2.5 * u + 30 * w)


bake(rig, "location", fr2, [tuple(fly((f - 1) / FPS)) for f in fr2])
for f in fr2:
    u = max(0.0, (f - 1) / FPS - LIFT)
    rig.rotation_euler = (math.radians(-20 * min(1, u) - 12 * u), math.radians(25 * math.sin(u * 2.0)), math.radians(90 + 25 * u))
    rig.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- camera's
CL_K = (0.0004, 30)                           # dichtbij voor de kleine shots in de keuken
CL_M = (0.05, 6000)


def follow(off, tgt, lens):
    def fn(t):
        k = scale_at(t)
        return HP + off * k, HP + tgt * k, lens
    return fn


S.cam(0.0, None, fn=follow(V(0.35, -2.3, 1.2), V(0, 0, 0.85), 28))
S.cams[-1]["clip"] = CL_K
S.cam(l1[1] - 1.8, None, fn=lambda t: (HP + V(0.06, -0.62, 0.05), HP + V(0.02, 0, 0.12), 26))
S.cams[-1]["clip"] = CL_K
S.cam(l2[0] + 0.2, (HP + V(-0.02, -0.33, 0.012), HP + V(0.1, 0.05, 0.16), 16), (HP + V(-0.04, -0.3, 0.012), HP + V(0.1, 0.05, 0.18), 16))
S.cams[-1]["clip"] = CL_K
S.cam(l2[0] + 2.4, (HP + V(0.06, -0.3, 0.08), HP + V(0.03, 0, 0.12), 34), (HP + V(0.05, -0.27, 0.08), HP + V(0.03, 0, 0.12), 36))
S.cams[-1]["clip"] = CL_K
S.cam(l3[0], None, fn=follow(V(0.45, -2.6, 0.6), V(0.1, 0, 0.9), 30))
S.cams[-1]["clip"] = CL_K
S.cam(ANT_GO - 0.2, (HP + V(0.012, -0.07, 0.006), HP + V(0.03, 0.02, 0.008), 20), (HP + V(0.01, -0.062, 0.006), HP + V(0.03, 0.02, 0.008), 20))
S.cams[-1]["clip"] = CL_K
S.cam(ANT_LOOK - 0.4, (HP + V(-0.03, -0.035, 0.012), HP + V(0.02, 0.004, 0.006), 30), (HP + V(-0.028, -0.032, 0.011), HP + V(0.02, 0.004, 0.006), 32))
S.cams[-1]["clip"] = CL_K
# macro
S.cam(CUT, (MX + V(-4.6, -3.9, 1.5), MX + V(-2.0, 0.3, 1.0), 22), (MX + V(-3.6, -3.6, 1.4), MX + V(-0.8, 0.2, 1.0), 22))
S.cams[-1]["clip"] = CL_M
S.cam(l5[0] + 0.3, (MX + V(0.3, -6.5, 1.6), MX + V(0.9, 0, 1.0), 26), (MX + V(0.4, -6.0, 1.5), MX + V(0.9, 0, 1.0), 28))
S.cams[-1]["clip"] = CL_M
S.cam(DROP_HIT + 1.2, S.shot(held, DROP_HIT + 1.5, "med", az=-55, lens=28), S.shot(held, l5[1], "med", az=-50, lens=30))
S.cams[-1]["clip"] = CL_M
S.cam(l6[0], (MX + V(-2.6, -3.8, 0.9), MX + V(4, 9, 7), 18), (MX + V(-2.3, -3.4, 0.9), MX + V(4, 9, 7), 18),
      shake=lambda t: 0.5 * smooth(l6[1] - 1.8, l6[1], t))
S.cams[-1]["clip"] = CL_M
S.cam(l7[0], (MX + V(-5, -2.5, 1.5), MX + V(30, 20, 20), 20), (MX + V(-5.5, -3, 1.4), MX + V(30, 20, 25), 20),
      shake=lambda t: 0.8 + 0.6 * smooth(l7[0], l7[1], t))
S.cams[-1]["clip"] = CL_M
S.cam(l7[0] + 1.7, S.shot(held, l7[0] + 2.0, "mcu", az=-20, lens=30), S.shot(held, LIFT, "mcu", az=-16, lens=32),
      shake=lambda t: 1.2)
S.cams[-1]["clip"] = CL_M
S.cam(LIFT, None, fn=lambda t: (fly(t) + V(-5.5, -4.0, 1.2), fly(t) + V(12, 4, 2), 22), shake=lambda t: 1.6)
S.cams[-1]["clip"] = CL_M

S.done()
