"""D18 · Een miljard jaar: de oceanen koken (script scène 18a-18e). Witte zoutvlakte, wrak, scheve vuurtoren.
18a  WIDE crane 4 s: eindeloze witte vlakte, hittetrilling, een kolossaal wrak.  VO: "Every billion years, the Sun gets about ten percent brighter."
18b  MEDIUM 3 s: hij loopt langs het wrak, zijn kleren zijn rafels.  VO: "So the oceans boil away."
18c  DETAIL 3 s: de laatste plas borrelt, damp, en dan is hij weg. Zoutkorst.  VO: "The last puddle on Earth takes three seconds to disappear."
18c2 WIDE track 5 s: hij loopt langs een oude, scheve vuurtoren.  VO: "Somewhere under here are the oceans you swam in. They're just... gone."
18d  WIDE 4 s (hier 2 shots): geen dier, geen plant. Hij alleen.  VO: "No plants. No animals. No bacteria. You are the last living thing on Earth."
18e  CLOSE 3 s: hij houdt het horloge tegen zijn oor. Tik.  VO: "And the clock is still ticking."

    python3 anim/v4/scenes/d18_zout.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d18", "heuvel", "zout", exposure=0.05)
sh = S.cuts([4.2, 3.0, 3.8, 5.2, 3.2, 3.2, 2.8])
END = sh[-1][1]
t_b, t_c, t_c2, t_d, t_d2, t_e = (s[0] for s in sh[1:])
S.hide("Personage_marker", "Character_marker")


def ground(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = bpy.context.scene.ray_cast(dg, Vector((x, y, 300.0)), Vector((0, 0, -1)))
    return loc.z if hit and loc.z < 1.0 else 0.0


def face(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


# ---------------------------------------------------------------- 18b: langs het wrak
AXW = V(math.cos(math.radians(25)), math.sin(math.radians(25)), 0)
PW = V(-AXW.y, AXW.x, 0)
WB = V(34.0, 120.0, 0.0) - PW * 17.5
w0, w1 = WB - AXW * 3.0, WB + AXW * 0.5
wrak = S.actor("hoofdpersonage_rafels", w0, face(w0, w1), label="hoofdpersonage_wrak")
show(wrak.rig, t_b - 0.05, t_c)
S.walk(wrak, t_b, t_c, [w0, w1], stride=0.36)
S.beat(wrak, t_b, "staan", face="nerveus", face_amt=0.5, body={"spine": (8, 0, 0)}, look=(0.4, 0.2))

# ---------------------------------------------------------------- 18c: de laatste plas verdampt
PL = V(2.5, 3.0, 0.0)
plas = bpy.data.objects.get("Plas_0")
damp = bpy.data.objects.get("Damp_0")
if plas:
    key(plas, 0.0, scale=(1, 1, 1))
    key(plas, t_c + 0.4, scale=(1, 1, 1))
    key(plas, t_c + 3.0, scale=(0.02, 0.02, 1))
    show(plas, 0.0, t_c + 3.05)
if damp:
    key(damp, t_c, loc=tuple(damp.location), scale=(1, 1, 1))
    key(damp, t_c + 3.2, loc=tuple(damp.location + V(0, 0, 0.8)), scale=(0.3, 0.3, 0.6))
korst = T.cyl("Zoutkorst_plas", tuple(PL + V(0, 0, -0.01)), 0.9, 0.02, S.mat("zoutkorst_plas", (0.97, 0.96, 0.92)), seg=32, ol=0)
key(korst, 0.0, scale=(0.02, 0.02, 1))
key(korst, t_c + 0.6, scale=(0.02, 0.02, 1))
key(korst, t_c + 3.0, scale=(1, 1, 1))
rb = random.Random(18)
bub_m = S.mat("plas_bubbel", (0.75, 0.85, 0.88))
for k in range(14):
    t0 = t_c + 0.1 + k * 0.17
    r_ = 0.75 * max(0.05, 1 - (t0 - t_c - 0.4) / 2.6)
    a, d = rb.uniform(0, 6.28), rb.uniform(0, r_ * 0.8)
    b = T.sphere(f"Plas_bubbel_{k}", tuple(PL + V(math.cos(a) * d, math.sin(a) * d, 0.0)), 0.035, bub_m, seg=8, ol=0)
    key(b, 0.0, scale=0.001)
    key(b, t0, scale=0.001)
    key(b, t0 + 0.12, scale=1.0)
    key(b, t0 + 0.24, scale=0.001)
for t in frange(t_c, t_c + 3.0, 0.4):
    S.puff(PL + V(0, 0, 0.05), t, n=2, r=(0.15, 0.3), grow=2.0, dur=1.0, color=(0.95, 0.96, 0.97), rise=0.8, spread=0.4)

# ---------------------------------------------------------------- 18c2: langs de vuurtoren
VT = V(-38.0, 70.0, 0.0)
v0, v1 = VT + V(9.0, -10.0, 0.0), VT + V(5.0, -4.0, 0.0)
vtl = S.actor("hoofdpersonage_rafels", v0, face(v0, v1), label="hoofdpersonage_vuurtoren")
show(vtl.rig, t_c2 - 0.05, t_d)
S.walk(vtl, t_c2, t_d, [v0, v1], stride=0.36)
S.beat(vtl, t_c2, "staan", face="verdrietig", face_amt=0.4, body={"spine": (6, 0, 0)}, at=VT + V(0, 0, 18))

# ---------------------------------------------------------------- 18d-18e: hij alleen (bij de heuvelplek), horloge bij zijn oor
HP = V(0.6, -1.0, 0.0)
held = S.actor("hoofdpersonage_rafels", HP, 10)
show(held.rig, t_d - 0.05)
S.beat(held, t_d, "staan", face="neutraal", face_amt=0.4, at=V(0, 80, 2))
S.beat(held, t_d2, "staan", face="verdrietig", face_amt=0.4, at=V(-20, 80, 2))
S.beat(held, t_e, "staan", face="neutraal", face_amt=0.4, look=(-0.5, -0.1), body={"head": (0, 0, -10)})
S.hold(held, END)
HD = S.headpos(held, t_e + 0.6)
FW = V(math.sin(math.radians(10)), -math.cos(math.radians(10)), 0)
SD = V(FW.y, -FW.x, 0)
EAR = HD + SD * 0.36 + V(0, 0, -0.04)
hw = S.watch(held, t_e - 0.1, side="R", name="Zakhorloge_zout", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3, oud=True)
for o in [hw] + list(hw.children_recursive):
    show(o, t_e - 0.1)
S.watch_hands("Zakhorloge_zout", t_e, END, every=1.0)
S.reach(held, t_e, "R", EAR)
S.reach(held, END, "R", EAR)
S.eyes_closed(held, t_e + 0.7, END)

# ---------------------------------------------------------------- camera's
WR = V(34.0, 120.0, 0.0)
S.cam(0.0, (V(-14.0, -24.0, 2.5), WR + V(0, 0, 6), 24), (V(-12.0, -22.0, 9.0), WR + V(0, 0, 3), 24))
S.cam(t_b, None, fn=lambda t: (S._root_matrix(wrak, t).translation - PW * 4.2 - AXW * 1.0 + V(0, 0, 1.4),
                                S._root_matrix(wrak, t).translation + V(0, 0, 1.0), 30))
S.cam(t_c, (PL + V(1.4, -1.6, 0.7), PL + V(0, 0, 0.1), 35), (PL + V(1.25, -1.45, 0.65), PL + V(0, 0, 0.1), 35))
S.cam(t_c2, None, fn=lambda t: (S._root_matrix(vtl, t).translation + V(6.5, -5.0, 1.6),
                                 S._root_matrix(vtl, t).translation + V(-3.0, 3.0, 4.0), 24))
S.cam(t_d, (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22), (V(-3.4, -9.1, 2.3), V(0.8, 8.0, -0.6), 22))
S.cam(t_d2, (V(-6.0, -14.0, 10.0), HP + V(0, 0, 0.8), 24), (V(-7.0, -16.0, 14.0), HP + V(0, 0, 0.8), 24))
S.cam(t_e, (HD + FW * 1.2 + SD * 0.7 + V(0, 0, -0.1), HD + SD * 0.15 + V(0, 0, -0.1), 38),
      (HD + FW * 1.1 + SD * 0.64 + V(0, 0, -0.1), HD + SD * 0.15 + V(0, 0, -0.1), 38))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(1000000000, t0=0.0, big=True)
S.jump(0.0)
S.say("D18-01", at=0.2)
S.say("D18-02", at=t_b + 0.2)
S.say("D18-03", at=t_c + 0.1)
S.say("D18-04", at=t_c2 + 0.15)
S.say("D18-05", at=t_d + 0.1)
S.say("D18-06", at=t_e + 0.3)
S.sfx("sfx_rook_sis", t_c + 0.2, 0.18)
S.tick(t_e + 1.6, 0.5)
S.ambience("sfx_wind_hoog", 0.0, END, vol=0.07)
S.music("drone", 0.0, END, vol=0.15, fade_in=0.6, fade_out=0.6)
S.finish(length=END, tail=0.0)
