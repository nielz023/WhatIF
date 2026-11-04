"""N03a · De laatste normale dag: het park in de ochtend (script scène 3a-3b).
Kinderen op het klimrek, een man laat een hondje uit dat aan het bordje KEEP OFF THE GRASS snuffelt.
De jongen en zijn beste vriend fietsen langs en zwaaien naar het hondje. Aftelklok midden boven.

    blender -b -P anim/v3/scenes/n03a_park.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n03a", "park", "ochtend", exposure=0.2)
sh = S.cuts([4.0, 3.0])
END = sh[-1][1]
bpy.context.view_layer.update()

# ---------------------------------------------------------------- kinderen op het klimrek
C = V(-7.0, 7.0, 0)
u = V(0.81, 0.58, 0)                       # opzij t.o.v. de camera, zodat we ze en profil zien
kidA = S.actor("kind_a", C + u * 1.68 + V(0, 0, 0.67), -54)
S.beat(kidA, 0.0, "armen_omhoog", amount=0.8, face="lach", face_amt=0.7, crouch=(0.05, 10))
ring = lambda ang, z, r: C + V(math.cos(ang) * r, math.sin(ang) * r, z)
a0 = math.atan2(u.y, u.x)
for k, t in enumerate(frange(0.0, END, 0.7)):
    hi = k % 2
    S.reach(kidA, t, "L", ring(a0 + 0.18, 1.75 if hi else 1.27, 1.06 if hi else 1.46))
    S.reach(kidA, t, "R", ring(a0 - 0.18, 1.27 if hi else 1.75, 1.46 if hi else 1.06))
    A.crouch(kidA, F(t), 0.05 - 0.04 * hi, 10)
S.hold(kidA, END)
kidB = S.actor("kind_b", C + V(-0.75, -2.35, 0), 20)
S.beat(kidB, 0.0, "juichen", amount=0.7, face="lach", face_amt=0.8, at=S.head(kidA))
for k, t in enumerate(frange(0.6, END, 0.8)):
    S.beat(kidB, t, "juichen" if k % 2 else "staan", amount=0.8, face="lach", face_amt=0.8, at=S.head(kidA),
           crouch=(0.06 if k % 2 else 0.0, 4))
S.hold(kidB, END)

# ---------------------------------------------------------------- man met hondje bij het bordje
SIGN = V(2.8, -4.2, 0)
baas = S.actor("hondenbaas", (7.6, -1.0, 0), 130)
S.walk(baas, 0.0, 2.1, [V(7.6, -1.0, 0), V(5.6, -2.2, 0), V(4.1, -3.0, 0)], stride=0.5)
S.beat(baas, 2.2, "staan", face="blij", face_amt=0.5)
hond = animal(S, "hondje", (6.9, -1.7, 0), 125)
animal_path(hond, 0.0, 2.0, [V(6.9, -1.7, 0), V(4.6, -3.2, 0), V(3.25, -3.75, 0)], action="hond_loop")
animal_place(hond, 2.05, V(3.2, -3.8, 0), 140)
animal_act(hond, 2.05, 4.6, "hond_snuffel")
animal_act(hond, 4.6, END, "hond_kwispel")
S.beat(baas, 2.6, "staan", face="neutraal", face_amt=0.4, at=V(3.2, -3.8, 0.3))
# trekt zachtjes aan de lijn (anticipatie, ruk, uitrijden)
A.bone_rot(baas, F(3.1), "upper_arm.R", (0, 0, 0))
S.beat(baas, 3.2, "staan", face="twijfel", face_amt=0.5, at=V(3.2, -3.8, 0.3), body={"spine": (-3, 0, 0)})
S.beat(baas, 3.45, "staan", face="blij", face_amt=0.4, at=V(3.2, -3.8, 0.3), body={"spine": (2, 0, 0)})
S.beat(baas, sh[1][0] + 1.6, "zwaaien_a", amount=0.6, face="lach", face_amt=0.6, at=V(0, -1.4, 1.2))
S.beat(baas, sh[1][0] + 2.1, "zwaaien_b", amount=0.6, face="lach", face_amt=0.6, at=V(2.0, -1.4, 1.2))
S.hold(baas, END)
leash(S, baas, hond, 0.0, END)

# ---------------------------------------------------------------- jongen en beste vriend op de fiets (3b)
t_b = sh[1][0]
held = S.actor("hoofdpersonage_kind", (-26.0, -5.2, 0), -90)
vriend = S.actor("beste_vriend", (-27.6, -4.4, 0), -90)
_, crank_h = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen")
_, crank_v = bike(S, vriend, color=(0.85, 0.12, 0.12), name="Fiets_vriend")
# ze komen in 3a al in de verte aanfietsen (over het pad), in 3b rijden ze door het beeld
ride_path(S, held, crank_h, 0.0, END, [V(-26.0, -5.2, 0), V(-12.0, -2.4, 0), V(-3.0, -1.6, 0), V(2.6, -1.9, 0)],
          cadence=1.4, lean=14)
ride_path(S, vriend, crank_v, 0.0, END, [V(-27.6, -4.4, 0), V(-13.6, -1.6, 0), V(-4.5, -0.7, 0), V(1.2, -1.0, 0)],
          cadence=1.3, lean=10, sway=4)
S.face(held, t_b, "blij", 0.7, look=(0.4, 0.0))
S.face(held, t_b + 1.4, "lach", 0.9, look=(0.6, -0.1))
S.face(vriend, t_b, "lach", 0.9, look=(0.5, -0.1))
# vriend: laat zijn stuur met één hand los (de arm aan onze kant) en zwaait naar het hondje
S.reach(vriend, t_b + 0.9, "L", inf=1.0)
S.reach(vriend, t_b + 1.15, "L", inf=0.0)
S.reach(vriend, END, "L", inf=0.0)
for k, t in enumerate(frange(t_b + 1.15, END - 0.2, 0.28)):
    S.beat(vriend, t, "zwaaien_a" if k % 2 else "zwaaien_b", face="lach", face_amt=0.9, at=V(3.2, -3.8, 0.4),
           crouch=(0.07, 10))
# jongen grijpt zijn stuur strakker vast (schouders even op) en lacht naar de hond
A.bone_rot(held, F(t_b + 1.5), "spine", (0, 0, 0))
A.bone_rot(held, F(t_b + 1.7), "spine", (6, 0, 0))
A.bone_rot(held, F(t_b + 2.1), "spine", (2, 0, 0))
A.bone_rot(held, F(t_b + 0.8), "head", (0, 0, 0))
A.bone_rot(held, F(t_b + 1.5), "head", (-4, -20, 0))
A.blink_at(held, F(t_b + 0.6))
A.blink_at(vriend, F(t_b + 2.2))

# ---------------------------------------------------------------- camera's
# 3a WIDE crane naar beneden: het bordje vooraan rechts, de man en het hondje, het klimrek op de achtergrond
S.cam(sh[0][0], ((5.4, -10.4, 5.6), (-1.5, 3.0, 0.6), 22), ((4.9, -8.6, 1.05), (-1.2, 2.5, 1.25), 22), handheld=0.08)
# 3b MEDIUM track: de camera rijdt schuin voor ze uit (3/4 van voren, parkkant), het hondje op de achtergrond
S.cam(t_b, None, fn=S.follow(held, (2.7, 2.4, 1.05), lens=30, look_offset=(-0.9, -0.2, -0.3)), shake=S.shake(0.25))

# ---------------------------------------------------------------- HUD, geluid en stem
S.countdown(15 * 3600 + 24 * 60 + 10, 0.3, END, jumps=[(0.3, 15 * 3600 + 24 * 60 + 10), (t_b, 14 * 3600 + 58 * 60 + 30)])
S.ambience("sfx_park_ochtend", 0.0, END, vol=0.22)
S.sfx("sfx_klok_tik", 0.0, 0.12, loop_to=END)
S.sfx("sfx_hond_blaf", t_b + 2.0, 0.25)
S.sfx("sfx_fiets_snel", t_b - 0.2, 0.25)
S.say("N03-01", at=0.4)
S.say("N03-02", at=t_b + 0.5)
S.finish(length=END, tail=0.0)
