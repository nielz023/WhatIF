"""D17a · Het supercontinent: globe-animatie (script scène 17a-17a2).
17a  DETAIL globe 4 s: de continenten schuiven naar elkaar toe.  VO: "This part is real. In about two hundred and fifty million years..."
17a2 DETAIL globe 4 s: de laatste continenten klappen tegen elkaar, bergketens schieten omhoog.
     VO: "...all the continents crash back together into one giant supercontinent."

    python3 anim/v4/scenes/d17a_globe.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d17a", "ruimte_nd", "aarde", exposure=0.1)
sh = S.cuts([4.8, 5.0])
END = sh[-1][1]
t_b = sh[1][0]
S.hide("Personage_marker", "Character_marker", "Aarde", "Continent")

G = V(0.0, 40.0, 0.0)
R = 10.0
T.sphere("Globe_oceaan", tuple(G), R, S.mat("globe_oceaan", (0.05, 0.25, 0.70)), seg=64, ol=0)
land = [S.mat("globe_land_groen", (0.25, 0.55, 0.20)), S.mat("globe_land_bruin", (0.55, 0.42, 0.22))]
berg = S.mat("globe_berg", (0.62, 0.55, 0.48))
rnd = random.Random(250)


def surf_dir(lon, lat):
    lo, la = math.radians(lon), math.radians(lat)
    return V(math.sin(lo) * math.cos(la), -math.cos(lo) * math.cos(la), math.sin(la))


# continenten: elk een draaipunt in het midden van de globe, de vlek op het oppervlak naar -Y (naar de camera)
STARTS = [(-70, 35), (-55, -25), (10, 45), (5, 0), (60, 30), (75, -20), (40, -55)]
ENDS = [(-14, 18), (-12, -8), (4, 26), (2, 2), (16, 16), (18, -10), (6, -24)]
pivots = []
for k, ((lo0, la0), (lo1, la1)) in enumerate(zip(STARTS, ENDS)):
    piv = bpy.data.objects.new(f"Globe_continent_draai_{k}", None)
    T._link(piv)
    piv.location = G
    blobs = []
    for j in range(4):
        dx, dz = rnd.uniform(-2.2, 2.2), rnd.uniform(-1.8, 1.8)
        blobs.append(T.sphere(f"Globe_continent_{k}_{j}", (dx, -R + 0.15, dz), rnd.uniform(1.6, 2.6), land[(k + j) % 2],
                              scale=(1.0, 0.18, 0.8), seg=16, ol=0))
    for b in blobs:
        b.parent = piv
    for t, (lo, la) in ((0.0, (lo0, la0)), (0.4, (lo0, la0)), (t_b + 1.6, (lo1, la1))):
        piv.rotation_euler = (math.radians(la), 0, math.radians(lo))
        piv.keyframe_insert("rotation_euler", frame=F(t))
    pivots.append(piv)
for p in pivots:
    for fc in A._fcurves(p):
        for kp in fc.keyframe_points:
            kp.interpolation = "QUAD"
            kp.easing = "EASE_IN"
# bergketens schieten omhoog waar ze botsen (17a2)
for k in range(14):
    lo, la = rnd.uniform(-12, 16), rnd.uniform(-14, 22)
    n = surf_dir(lo, la)
    c = T.cyl(f"Globe_bergketen_{k}", tuple(G + n * (R + 0.05)), rnd.uniform(0.35, 0.6), rnd.uniform(0.6, 1.2), berg, r2=0.05,
              seg=6, ol=0)
    c.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    t0 = t_b + 1.4 + 0.08 * k
    key(c, 0.0, scale=0.001)
    key(c, t0, scale=0.001)
    key(c, t0 + 0.35, scale=1.0)
# een paar wolkenslierten die meedraaien
wolk = S.mat("globe_wolk", (0.95, 0.96, 0.98))
wp = bpy.data.objects.new("Globe_wolken_draai", None)
T._link(wp)
wp.location = G
for k in range(10):
    n = surf_dir(rnd.uniform(-90, 90), rnd.uniform(-60, 60))
    w = T.sphere(f"Globe_wolk_{k}", tuple(n * (R + 0.4)), rnd.uniform(0.8, 1.6), wolk, scale=(1.8, 0.6, 0.12), seg=10, ol=0)
    w.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    w.parent = wp
key(wp, 0.0, rot=(0, 0, 0))
key(wp, END, rot=(0, 0, 25))

# ---------------------------------------------------------------- camera's
S.cam(0.0, (G + V(-6.0, -36.0, 8.0), G, 40), (G + V(-3.0, -33.0, 6.5), G, 40))
S.cam(t_b, (G + V(1.0, -27.0, 5.0), G + V(0, 0, 1.0), 40), (G + V(1.0, -23.0, 4.0), G + V(0, 0, 1.0), 40), handheld=0.04)

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(250000000, t0=0.0, big=True)
S.jump(0.0)
S.say("D17-01", at=0.2)
S.say("D17-02", at=t_b + 0.1)
S.sfx("sfx_aardbeving", t_b + 1.2, 0.22)
S.sfx("sfx_dreun", t_b + 1.6, 0.25)
S.music("m_spanning_puls", 0.0, END, vol=0.14, fade_in=0.4, fade_out=0.4)
S.finish(length=END, tail=0.0)
