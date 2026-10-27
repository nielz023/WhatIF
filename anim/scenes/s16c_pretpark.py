"""S16c · het weekend: een normale dag, een familiedag. Het pretpark. 'And you already know how that goes.'

    blender -b -P anim/scenes/s16c_pretpark.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s16c", "pretpark", "dag")

Y0, Y1 = -38.5, -31.5
cast = [("hoofdpersonage", 0.9, 0.0), ("mama", 0.0, 0.25), ("beste_vriend", 1.8, 0.35), ("broertje", -0.8, 0.5)]
acts = {}
for name, dx, dy in cast:
    acts[name] = S.actor(name, V(dx, Y0 + dy, 0), 180, energy=1.0)
held, mama, vriend, bro = (acts[n] for n, _, _ in cast)
visitors = [S.extra(k, V(x, y, 0), r, energy=0.6) for k, (x, y, r) in enumerate(((4.5, -26.0, 200), (-3.5, -24.5, 150), (6.5, -22.5, 90), (-2.2, -33.0, -20)))]

# ---------------------------------------------------------------- tijdlijn
S.music("piano_zacht", 0.0, 60, vol=0.24, fade_in=0.6, fade_out=0.3)
PIANO = S.sounds[-1]
S.ambience("sfx_pretpark_sfeer", 0.0, 60, vol=0.14)
l7 = S.say("S16-07", gap=0.6)
PARK = l7[0] + 5.0                              # 'The theme park.'
l8 = S.say("S16-08", gap=0.5)
S.wait(1.4)
END = S.t
PIANO["loop_to"] = l8[0] - 0.1
S.sfx("sfx_riser", l8[0] - 0.4, 0.45)
S.music("strijk_noot", l8[0] - 0.1, END + 0.2, vol=0.28, fade_in=0.2, fade_out=0.8)

# ---------------------------------------------------------------- de familie loopt het park in
for name, dx, dy in cast:
    ch = acts[name]
    S.walk(ch, 0.2, END, [V(dx, Y0 + dy, 0), V(dx + 0.3, Y1 + dy, 0)], stride=0.5 if name != "broertje" else 0.4,
           arms=0.5 if name in ("hoofdpersonage", "mama") else None)
S.beat(held, 0.0, "ontspannen", face="blij", face_amt=0.6, at=S.head(mama, 0), face_only=True)
S.beat(held, l7[0] + 2.2, "ontspannen", face="lach", face_amt=0.6, at=S.head(vriend, 0), face_only=True)
S.beat(held, PARK + 0.2, "ontspannen", face="blij", face_amt=0.8, look=(0, 0.4), face_only=True)
S.beat(held, l8[0] + 0.6, "ontspannen", face="twijfel", face_amt=0.4, look=(-0.3, 0.5), face_only=True)
S.beat(mama, 0.0, "ontspannen", face="blij", face_amt=0.8, at=S.head(held, 0), face_only=True)
S.beat(mama, l7[0] + 1.6, "ontspannen", face="lach", face_amt=0.7, at=S.head(held, 0), face_only=True)
S.beat(vriend, 0.0, "ontspannen", face="lach", face_amt=0.7, look=(0.3, 0.3), feet="keep")
S.beat(vriend, PARK, "zwaaien_a", amount=0.5, face="lach", face_amt=1.0, look=(0, 0.4), feet="keep")
S.beat(vriend, PARK + 0.4, "zwaaien_b", amount=0.5, face="lach", face_amt=1.0, look=(0, 0.4), feet="keep")
S.beat(bro, 0.0, "ontspannen", face="lach", face_amt=0.9, look=(0.2, 0.4), feet="keep")
S.beat(bro, PARK + 0.2, "armen_omhoog", amount=0.7, face="lach", face_amt=1.0, look=(0, 0.6), feet="keep")
for v in visitors:
    S.beat(v, 0.0, "ontspannen", face="blij", face_amt=0.6)
    S.hold(v, END)

# ---------------------------------------------------------------- camera
fam = lambda t: S.frame_of(held, t)[0]
S.cam(0.0, None, fn=lambda t: (fam(t) + V(-0.9, 3.4, 1.35), fam(t) + V(-0.2, 0, 1.0), 26))
S.cam(PARK - 0.15, ((3.2, -44.0, 2.2), (-6.0, -6.0, 9.0), 24), ((3.0, -43.0, 2.3), (-6.0, -6.0, 10.0), 26))
S.cam(l8[0] - 0.2, ((-1.0, -30.0, 1.6), (-10.0, 6.0, 22.0), 26), ((-2.0, -26.0, 2.0), (-10.0, 6.0, 22.0), 34))

S.finish(length=END)
