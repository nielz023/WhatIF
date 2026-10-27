"""SH8b · 1.000.000x zwaarder · keuken: hij komt door het plafond naar beneden en landt in een krater van tegels.

    blender -b -P anim/shorts/sh8b_keuken.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401

FALL = timeline("sh8")[3][0] + 3.6
S = Short("sh8", "b", "keuken", "ochtend", lines=(), t0=FALL + 0.25, t1=timeline("sh8")[4][0] - 0.1)
T0, END = S.t0, S.t1
for n in ("Krant", "Ontbijt_broertje"):
    o = S.obj(n)
    if o:
        o.hide_render = True
LAND = V(1.3, 0.55, 0)
LT = T0 + 0.35
held = S.actor("hoofdpersonage", LAND + V(0, 0, 2.7), 30)
key(held.rig, T0, loc=tuple(LAND + V(0, 0, 2.7)))
key(held.rig, LT, loc=tuple(LAND + V(0, 0, -0.08)), interp="LINEAR")
S.beat(held, T0, "armen_omhoog", face="geschrokken", face_amt=1.0, look=(0, -0.5), mouth=0.7)
S.beat(held, LT, "schrap", face="inspanning", face_amt=1.0, look=(0, -0.3), mouth=0.2, crouch=(0.3, 20))
S.beat(held, LT + 0.9, "schrap", face="geschrokken", face_amt=1.0, look=(0, 0.6), mouth=0.4, crouch=(0.2, 12),
       body={"head": (-20, 0, 0)})
S.hold(held, END)
crack_m = S.mat("barst_tegel", (0.1, 0.08, 0.07))
T.cyl("Krater", tuple(LAND + V(0, 0, 0.002)), 0.7, 0.004, S.mat("krater", (0.25, 0.22, 0.2)), seg=20, ol=0)
for j in range(14):
    a = j / 14 * 6.283
    ln = 0.8 + 0.6 * ((j * 3) % 4) / 4
    c = T.box(f"Tegelscheur_{j}", (0, 0, 0), (ln, 0.02, 0.004), crack_m, bevel=0, ol=0)
    c.rotation_euler.z = a
    c.location = LAND + V(math.cos(a) * (0.6 + ln / 2), math.sin(a) * (0.6 + ln / 2), 0.003)
    show(c, LT)
show(S.obj("Krater"), LT)
S.debris(LAND + V(0, 0, 2.4), T0, n=30, size=(0.04, 0.12), color=(0.9, 0.88, 0.84), speed=(0.5, 1.5), up=0.0, floor=0.0,
         life=2.0, name="Plafondstuk")
S.debris(LAND + V(0, 0, 0.1), LT, n=20, size=(0.05, 0.1), color=(0.75, 0.7, 0.62), speed=(2.0, 4.0), up=1.0, floor=0.0,
         life=1.5, name="Tegel")
S.puff(LAND + V(0, 0, 0.3), LT, n=10, r=(0.15, 0.3), grow=1.8, dur=1.0, color=(0.85, 0.82, 0.78), rise=0.4, spread=0.6)
S.sfx("sfx_inslag", LT - 0.03, 0.6)
S.cam(T0, ((2.25, -0.9, 0.95), (LAND.x, LAND.y, 1.4), 18), ((2.2, -0.85, 0.95), (LAND.x, LAND.y, 0.8), 18),
      shake=lambda t: 2.5 * max(0, 1 - (t - LT) / 0.7) if t > LT else 0.0)
S.done()
