"""SH8c · 1.000.000x zwaarder · straat: de weg barst om zijn voeten, auto's glijden naar hem toe. Echte wetenschap:
de grond draagt een wolkenkrabber omdat het gewicht verdeeld is. Bij 1.000.000x opent het asfalt zich als water en
zakt hij weg... naar het middelpunt van de aarde (doorsnede: aardlagen die steeds heter gloeien).

    blender -b -P anim/shorts/sh8c_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

S = Short("sh8", "c", "straat", "zonnig", lines=(4, 5, 6, 7, 8))
l4, l5, l6, l7, l8 = (S.L[n] for n in (4, 5, 6, 7, 8))
T0, END = S.t0, S.t1
S.clip = (0.05, 3000)
for o in bpy.data.objects:                      # de boom staat voor de hoge shots
    if o.name.startswith("Straatboom_-3_-5.4"):
        o.hide_render = True

HP = V(0.0, 0.6, 0)
held = S.actor("hoofdpersonage", HP, 10)
UNDER = l7[0] + 2.2                              # snede naar de doorsnede


def sink(t):
    return (0.14 * smooth(l4[0] + 0.3, l4[1], t) + 0.32 * smooth(l5[0], l5[1], t) + 0.55 * smooth(l6[0], l6[1], t)
            + 1.2 * smooth(l7[0], UNDER, t))


fr = list(range(F(T0), F(UNDER)))
bake(held.rig, "location", fr, [(HP.x, HP.y, -sink((f - 1) / FPS)) for f in fr])

# ---------------------------------------------------------------- barsten, ringen, auto's
crack_m = S.mat("barst_asfalt", (0.05, 0.05, 0.06))
for j in range(16):
    a = j / 16 * 6.283 + 0.2
    ln = 2.5 + 3.0 * ((j * 5) % 7) / 7
    c = T.box(f"Asfaltbarst_{j}", (0, 0, 0), (ln, 0.05, 0.004), crack_m, bevel=0, ol=0)
    c.rotation_euler.z = a
    c.location = HP + V(math.cos(a) * ln / 2, math.sin(a) * ln / 2, 0.004)
    t0 = l4[0] + 0.5 + 0.08 * j
    key(c, 0, scale=(0.001, 1, 1))
    key(c, t0, scale=(0.001, 1, 1))
    key(c, t0 + 0.6, scale=(0.6, 1, 1))
    key(c, l5[1], scale=(1.0, 1.5, 1))
pit = T.cyl("Kuil", tuple(HP + V(0, 0, 0.003)), 0.6, 0.004, S.mat("kuil", (0.09, 0.09, 0.1)), seg=24, ol=0)
key(pit, 0, scale=(0.3, 0.3, 1))
key(pit, l4[0] + 0.5, scale=(0.3, 0.3, 1))
key(pit, l6[1], scale=(2.2, 2.2, 1))
for k, t in enumerate(frange(l6[0] + 0.2, UNDER, 0.55)):
    S.ring(HP + V(0, 0, 0.02), t, r0=0.4, r1=6.0, dur=1.4, color=(0.1, 0.1, 0.12), strength=1.0, thick=0.05)
SLIDE0, SLIDE1 = l4[0] + 3.0, UNDER
for n, to, tilt in (("Auto_geparkeerd_2", V(-3.6, 2.4, -0.05), (-8, 0, 25)), ("Auto_overkant_2", V(3.4, -0.9, -0.05), (6, 0, -20))):
    car = S.obj(n)
    if not car:
        continue
    p0 = car.location.copy()
    r0 = tuple(math.degrees(a) for a in car.rotation_euler)
    key(car, 0, loc=tuple(p0), rot=r0)
    key(car, SLIDE0, loc=tuple(p0), rot=r0)
    key(car, SLIDE1, loc=tuple(to), rot=(r0[0] + tilt[0], r0[1] + tilt[1], r0[2] + tilt[2]))
lamp = S.obj("Lantaarn_n_0")
if lamp:
    key(lamp, 0, rot=(0, 0, 0))
    key(lamp, l5[0], rot=(0, 0, 0))
    key(lamp, UNDER, rot=(-24, 0, 0))

# ---------------------------------------------------------------- acteren op straat
S.beat(held, T0, "schrap", face="bang", face_amt=0.9, look=(0, -0.6), mouth=0.2, crouch=(0.06, 6))
S.beat(held, l4[0] + 2.4, "handen_zij", face="geschrokken", face_amt=1.0, look=(-0.7, 0.2), mouth=0.4)
S.beat(held, l5[0] + 0.5, "staan", face="nerveus", face_amt=1.0, look=(0, -0.8), mouth=0.1, body={"head": (20, 0, 0)})
S.beat(held, l6[0] + 0.3, "armen_omhoog", amount=0.6, face="bang", face_amt=1.0, look=(0, 0.2), mouth=0.4)
S.beat(held, l7[0] + 0.2, "armen_omhoog", amount=1.0, face="schreeuw", face_amt=1.0, look=(0, 0.6), mouth=1.0,
       body={"head": (-20, 0, 0)})

# ---------------------------------------------------------------- de doorsnede: naar het middelpunt van de aarde
UX = 300.0
LAYERS = [(0.0, 0.3, (0.22, 0.22, 0.25), 0), (0.3, 3.0, (0.45, 0.3, 0.18), 0), (3.0, 15.0, (0.32, 0.22, 0.15), 0),
          (15.0, 40.0, (0.42, 0.42, 0.45), 0), (40.0, 60.0, (0.55, 0.25, 0.12), 0.6), (60.0, 120.0, (1.0, 0.45, 0.1), 2.5)]
for k, (a, b, col, glow) in enumerate(LAYERS):
    m = S.mat(f"aardlaag_{k}", col, glow) if glow else S.mat(f"aardlaag_{k}", col)
    T.box(f"Aardlaag_{k}", (UX, 2.0, -b), (60, 1.0, b - a), m, bevel=0, ol=0)
rnd = random.Random(31)
for k in range(40):
    z = -rnd.uniform(3, 40)
    rock(f"Aardsteen_{k}", V(UX + rnd.uniform(-8, 8), 1.45, z), rnd.uniform(0.2, 0.9),
         S.mat(f"aardsteen_{k % 3}", ((0.3, 0.28, 0.27), (0.4, 0.36, 0.33), (0.22, 0.2, 0.2))[k % 3]), seed=300 + k)
for k in range(10):
    z = -rnd.uniform(45, 70)
    rock(f"Gloeisteen_{k}", V(UX + rnd.uniform(-6, 6), 1.45, z), rnd.uniform(0.4, 1.2),
         S.mat("gloeisteen", (1.0, 0.35, 0.05), 3.0), seed=400 + k)


def fall_z(t):
    u = max(0.0, t - UNDER)
    return -1.6 - 3.5 * u - 2.6 * u * u


fr2 = list(range(F(UNDER), F(END) + 1))
bake(held.rig, "location", fr2, [(UX, 0.6, fall_z((f - 1) / FPS)) for f in fr2])
for f in fr2:
    u = max(0.0, (f - 1) / FPS - UNDER)
    held.rig.rotation_euler = (math.radians(8 * math.sin(u * 1.3)), math.radians(14 * math.sin(u * 0.9)), math.radians(10 + 25 * u))
    held.rig.keyframe_insert("rotation_euler", frame=f)
heat = T.point_light("Hitte", (UX, -1.0, -2), color=(1.0, 0.5, 0.15), energy=0, radius=0.3)
for t in frange(UNDER, END + 0.1, 0.25):
    heat.location = (UX, -1.2, fall_z(t) + 0.5)
    heat.keyframe_insert("location", frame=F(t))
    heat.data.energy = 30 + 900 * smooth(UNDER, END, t)
    heat.data.keyframe_insert("energy", frame=F(t))
S.beat(held, UNDER, "armen_omhoog", face="schreeuw", face_amt=1.0, look=(0, -0.6), mouth=1.0)
S.beat(held, UNDER + 1.5, "armen_omhoog", amount=0.8, face="bang", face_amt=1.0, look=(0, -0.9), mouth=0.6,
       body={"head": (24, 0, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- muziek, geluid, tellers
S.ambience("sfx_straat_sfeer", T0, l6[0], vol=0.1)
S.sfx("sfx_aardbeving", l4[0] + 0.4, 0.4)
S.sfx("sfx_grond_kruimelt", l4[0] + 1.0, 0.35)
S.sfx("sfx_autoalarm", SLIDE0 + 0.5, 0.25, loop_to=l6[0])
S.sfx("sfx_remmen", SLIDE0 + 0.2, 0.3)
S.sfx("sfx_seismograaf", l6[0], 0.3)
S.sfx("sfx_dreun", l6[0] + 0.1, 0.5)
S.sfx("sfx_wind_hoog", UNDER, 0.4, loop_to=END)
S.sfx("sfx_cliffhanger", l7[1] - 1.2, 0.75)
S.counter("10,000x", l4[0] + 0.05, l6[0], sub="450 TONS")
S.real(l5[0] + 0.1, l5[1] - 0.3)
S.counter("1,000,000x", l6[0] + 0.05, None, color=RED, sub="45,000 TONS")
for k, (t, d) in enumerate(((UNDER, "DEPTH: 10 m"), (UNDER + 1.0, "DEPTH: 1 km"), (UNDER + 2.0, "DEPTH: 30 km"),
                            (UNDER + 3.2, "DEPTH: 2,900 km"))):
    S.texts.append(dict(body=d, t0=t, t1=(UNDER + 1.0, UNDER + 2.0, UNDER + 3.2, END)[k], loc=(0.5, 0.68), size=70,
                        color=WHITE if k < 3 else RED, anchor=("CENTER", "CENTER"), pop=True))

# ---------------------------------------------------------------- camera
S.cam(T0, ((2.6, -2.8, 0.45), (0.0, 0.6, 0.8), 22), ((2.4, -2.6, 0.45), (0.0, 0.6, 0.7), 22),
      shake=lambda t: 0.8 * smooth(l4[0], l4[0] + 1.0, t))
S.cam(l4[0] + 2.6, ((0.4, -6.5, 4.5), (-1.0, 1.2, 0.0), 20), ((0.4, -6.3, 4.4), (-1.0, 1.2, 0.0), 20), shake=lambda t: 0.6)
S.cam(l5[0], ((0.9, -0.6, 0.12), (0.0, 0.6, 0.15), 22), ((0.85, -0.55, 0.12), (0.0, 0.6, 0.1), 22))
S.cam(l5[0] + 3.2, S.shot(held, l5[0] + 3.4, "mcu", az=12, lens=30, h=-0.1), S.shot(held, l5[1], "mcu", az=8, lens=34, h=-0.25))
S.cam(l6[0], ((0.0, -9.0, 7.5), (0.0, 0.6, 0.0), 20), ((0.0, -8.0, 8.5), (0.0, 0.6, 0.0), 20), shake=lambda t: 1.0)
S.cam(l7[0], None, fn=lambda t: (V((1.3, -1.4, 0.4)), V((0.0, 0.6, max(0.2, 1.1 - sink(t)))), 26), shake=lambda t: 1.4)
S.cam(UNDER, None, fn=lambda t: (V((UX + 0.4, -4.2, fall_z(t) + 0.7)), V((UX, 0.6, fall_z(t) + 0.1)), 28), shake=lambda t: 0.9)

S.done()
