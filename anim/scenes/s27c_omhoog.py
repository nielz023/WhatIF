"""S27c · Dag 40 · hij zwemt omhoog. Tien kilometer, twintig, vijftig: elke slag is zwaarder, er is minder lucht om
tegen te duwen. Honderd kilometer, en dan is er niets. De sterkste mens ooit, en hij komt geen meter vooruit.

    blender -b -P anim/scenes/s27c_omhoog.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401
from ruimte import suit_actor, sky_dome, cloud_layer, follow_lights, soften_shadows  # noqa: E402

S = Scene("s27c", "ruimte", "ruimte")
S.clip = (0.05, 30000)                        # sterren en zon staan ver weg

for n in ("Mok_gelijmd",):                     # de mok uit de outro hoort hier nog niet
    o = S.obj(n)
    if o:
        for c in [o] + list(o.children_recursive):
            c.hide_render = True
P0 = V(0.0, 0.0, 6.0)                          # onder de wolken (de landschijven zijn bijna 2 m dik)
TOP = V(0.0, 0.0, 400.0)                       # 'honderd kilometer' (de set: de aarde onder je, de ruimte erboven)
held = suit_actor(S, P0, 180, energy=1.2)
follow_lights(S, held)

# ---------------------------------------------------------------- tijdlijn
S.hud(40, "1,099,511,627,776x STRONGER", t0=0.5)
S.ambience("sfx_wind_hoog", 0.0, 0, vol=0.08)
WIND = S.sounds[-1]
S.music("ruimte_koor", 0.3, 0, vol=0.2, fade_in=2.0, fade_out=3.0)
KOOR = S.sounds[-1]
l8 = S.say("S27-08", gap=0.8)
SWIM = l8[0] + 4.86                            # 'You swim up.'
l9 = S.say("S27-09", gap=0.4)
K10, K20, K50 = l9[0], l9[0] + 2.38, l9[0] + 4.25
l10 = S.say("S27-10", gap=0.5)
K100 = l10[0]
NOTHING = l10[0] + 4.09                        # 'And then there's nothing.'
l11 = S.say("S27-11", gap=0.6)
l12 = S.say("S27-12", gap=0.8)
ASTRO = l12[0] + 5.84                          # 'Astronauts know this.'
l13 = S.say("S27-13", gap=1.0)
CANT = l13[0] + 4.62                           # 'And you can't move one meter.'
S.wait(2.4)
END = S.t
WIND["loop_to"] = K50
WIND["keys"] = [(K20, 0.08), (K50, 0.0)]
KOOR["loop_to"] = K100 + 2.0
S.sfx("sfx_whoosh", SWIM - 0.05, 0.25)
S.sfx("sfx_ademhaling_helm", K100 + 0.4, vol=0.22, loop_to=END)
S.music("drone", NOTHING - 0.4, END + 0.5, vol=0.12, fade_in=2.5, fade_out=2.0)
for k, (t, alt) in enumerate(((K10, "ALTITUDE: 10 KM"), (K20, "ALTITUDE: 20 KM"), (K50, "ALTITUDE: 50 KM"), (K100, "ALTITUDE: 100 KM"))):
    nxt = (K20, K50, K100, NOTHING + 0.8)[k]
    S.gauge(alt, t, nxt - 0.05, color=WHITE, size=56)
S.gauge("AIR: 0", NOTHING, l11[1] + 0.5, color=RED, size=56)
S.real(l12[0] + 0.1, l12[1] + 0.3)
S.text("NOTHING TO PUSH = NO MOVEMENT", l12[0] + 2.1, ASTRO - 0.1, loc=(0.965, 0.22), size=52, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("ASTRONAUTS: NEVER LET GO", ASTRO + 0.2, l12[1] + 0.3, loc=(0.965, 0.22), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.gauge("DISTANCE MOVED: 0 M", CANT - 0.1, END, color=WHITE, size=56)

# ---------------------------------------------------------------- de hemel: blauw, donkerblauw, zwart, en dan weg
sky_dome(S, held.rig, [(0.0, (0.42, 0.66, 0.98), 1.0), (K10, (0.36, 0.58, 0.95), 1.0), (K20, (0.16, 0.30, 0.72), 1.0),
                       (K50, (0.04, 0.08, 0.30), 1.0), (K100, (0.008, 0.012, 0.04), 1.0), (K100 + 1.2, (0.0, 0.0, 0.0), 0.0)])
cloud_layer(S, V(0, 0, 0), 16.0)

# ---------------------------------------------------------------- omhoog zwemmen
z_keys = [(0.0, 6.0), (SWIM, 6.2), (SWIM + 1.6, 17.0), (K10, 34.0), (K20, 80.0), (K50, 200.0), (K100 - 0.3, 385.0), (K100 + 1.2, 400.0)]
for t, z in z_keys:
    key(held.rig, t, loc=V(0, 0, z), rot=(12 if t >= SWIM else 0, 0, 180))
# zweven in het niets: heel langzaam draaien, geen meter vooruit
for k, t in enumerate(frange(K100 + 1.2, END + 0.1, 2.0)):
    u = t - (K100 + 1.2)
    key(held.rig, t, loc=TOP + V(0.02 * u, 0.0, 0.01 * u), rot=(12 + u * 1.2, u * 0.6, 180 + u * 2.0))
A_FWD = arms(arm("L", (0.2, 0.15, 0.96), (0.1, 0.1, 0.99)), arm("R", (0.2, 0.15, 0.96), (0.1, 0.1, 0.99)))
A_OUT = arms(arm("L", (0.95, 0.15, 0.25), (0.85, 0.35, -0.3)), arm("R", (0.95, 0.15, 0.25), (0.85, 0.35, -0.3)))
A_IN = arms(arm("L", (0.5, 0.6, -0.55), (-0.45, 0.8, 0.35)), arm("R", (0.5, 0.6, -0.55), (-0.45, 0.8, 0.35)))
TREAD_A = arms(arm("L", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)), arm("R", (0.85, 0.3, -0.4), (0.8, 0.5, -0.2)))
TREAD_B = arms(arm("L", (0.8, 0.45, -0.35), (0.5, 0.8, -0.2)), arm("R", (0.8, 0.45, -0.35), (0.5, 0.8, -0.2)))
S.beat(held, 0.0, "staan", face="vastberaden", face_amt=0.5, arms=TREAD_A, look=(0, 0.6), body={"head": (-22, 0, 0)})
for k, t in enumerate(frange(0.6, SWIM - 0.2, 0.6)):
    S.beat(held, t, "staan", face="vastberaden", face_amt=0.5 + 0.1 * (k % 2), arms=TREAD_B if k % 2 else TREAD_A, look=(0, 0.6),
           body={"head": (-22, 0, 0)}, feet=((0.12, 0.05, 0.06), (-0.12, -0.05, 0.0)) if k % 2 else ((0.12, -0.05, 0.0), (-0.12, 0.05, 0.06)))
# slagen worden trager en zwaarder
t, k = SWIM, 0
while t < K100 + 0.6:
    step = 0.42 + 0.5 * max(0.0, min(1.0, (t - K10) / (K100 - K10)))
    eff = t > K20
    S.beat(held, t, "staan", face="inspanning" if eff else "vastberaden", face_amt=0.4 + 0.5 * min(1.0, max(0.0, (t - K10) / (K100 - K10))),
           arms=(A_FWD, A_OUT, A_IN)[k % 3], look=(0, 0.6), body={"head": (-26, 0, 0), "spine": (-4, 0, 0)},
           feet=(((0.12, 0.0, 0.0), (-0.12, -0.25, 0.1)), ((0.12, -0.25, 0.1), (-0.12, 0.0, 0.0)), ((0.12, 0.0, 0.0), (-0.12, 0.0, 0.0)))[k % 3])
    t += step
    k += 1
# boven: stil, kijken, dan proberen te zwemmen: er gebeurt niets
S.beat(held, K100 + 1.2, "staan", face="verbaasd", face_amt=0.7, arms=TREAD_A, look=(0, -0.3), body={"head": (10, 0, 0)})
S.beat(held, NOTHING, "staan", face="bang", face_amt=0.5, arms=TREAD_B, look=(0.4, -0.2), body={"head": (6, 20, 0)})
S.beat(held, l11[0] + 0.4, "staan", face="nerveus", face_amt=0.7, arms=A_OUT, look=(-0.4, -0.2), body={"head": (6, -20, 0)})
S.beat(held, l11[1], "staan", face="bang", face_amt=0.6, arms=TREAD_A, look=(0, -0.3))
S.beat(held, l12[0] + 2.0, "staan", face="neutraal", face_amt=0.6, arms=TREAD_B, look=(0, -0.5), body={"head": (12, 0, 0)})
S.beat(held, ASTRO, "staan", face="verdrietig", face_amt=0.5, arms=TREAD_A, look=(0.3, -0.5), body={"head": (12, 10, 0)})
for k, t in enumerate(frange(l13[0] + 0.4, CANT - 0.2, 0.38)):
    S.beat(held, t, "staan", face="inspanning", face_amt=0.9, arms=(A_FWD, A_OUT, A_IN)[k % 3], look=(0, 0.2),
           body={"spine": (-6 if k % 2 else 6, 0, 0)})
S.beat(held, CANT, "staan", face="bang", face_amt=0.8, arms=TREAD_B, look=(0, -0.4), body={"head": (10, 0, 0)})
S.beat(held, END - 0.4, "staan", face="verdrietig", face_amt=0.9, arms=TREAD_A, look=(0, -0.6), body={"head": (16, 0, 0)}, mond_verdrietig=0.7)
# lucht die hij omlaag duwt: steeds zwakker, boven 50 km niets meer
air = S.mat("lucht_wit", (0.75, 0.88, 1.0), 1.2)
for k, t in enumerate(frange(SWIM + 0.3, K50 + 0.5, 1.26)):
    M = S._root_matrix(held, t)
    w = max(0.15, 1.0 - (t - SWIM) / (K50 + 0.5 - SWIM))
    c = T.cyl(S._fxname("Luchtstoot"), (0, 0, 0), 0.05, 1.0, air, r2=0.7, seg=16, ol=0)
    c.rotation_euler = M.to_euler()
    p0 = M @ V(0, 0, 0.2)
    back = (M.to_3x3() @ V(0, 0, -1)).normalized()
    key(c, t - 1 / FPS, loc=p0, scale=0.001)
    key(c, t + 0.15, loc=p0 + back * 0.8, scale=(w, w, 1.6 * w))
    key(c, t + 0.5, loc=p0 + back * 2.5, scale=0.001)

# ---------------------------------------------------------------- camera
HP = lambda t: S._root_matrix(held, t).translation
S.cam(0.0, None, fn=lambda t: (HP(t) + V(2.0, -2.8, 0.5), HP(t) + V(0, 0, 1.2), 26))      # boven de landschijf (bovenkant z ~5)
S.cam(SWIM - 0.2, None, fn=lambda t: (V(4.5, -6.5, 6.8), HP(t) + V(0, 0, 1.0), 24 + min(30.0, (t - SWIM) * 6)))
S.cam(K10 - 0.1, None, fn=lambda t: (HP(t) + V(3.5, -5.0, -2.5), HP(t) + V(0, 0, 0.8), 26))
S.cam(K50 - 0.2, None, fn=lambda t: (HP(t) + V(1.2, -1.8, 4.5), HP(t) + V(0, 0, -1.0), 24))
S.cam(K100 + 0.6, None, fn=lambda t: (TOP + V(-1.6, -4.6, 1.0) + V(0, -(t - K100) * 0.08, 0), TOP + V(15.0, 55.0, -17.0), 18))
S.cam(NOTHING + 0.2, S.shot(held, NOTHING + 0.8, "mcu", az=15, lens=34), S.shot(held, l11[1], "mcu", az=10, lens=38))
S.cam(l12[0] - 0.1, ((3.0, -7.0, 401.5), (0.0, 30.0, 388.0), 18), ((2.6, -7.4, 401.3), (0.0, 30.0, 388.0), 18))
S.cam(ASTRO - 0.2, S.shot(held, ASTRO + 0.5, "med", az=-30, lens=32), S.shot(held, l12[1], "med", az=-36, lens=34))
S.cam(l13[0] - 0.1, ((2.5, -5.5, 401.2), (0.0, 0.0, 401.0), 30), ((2.7, -5.9, 401.2), (0.0, 0.0, 401.0), 30))
S.cam(CANT - 0.3, ((-6.0, -16.0, 404.0), (0.0, 0.0, 400.6), 40), ((-6.4, -17.5, 404.3), (0.0, 0.0, 400.6), 40))

soften_shadows(S)
S.finish(length=END)
