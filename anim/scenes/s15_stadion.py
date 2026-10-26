"""S15 · Dag 14 · honkbalstadion: de eerste worp, 'zachtjes'. Mach 11. De bal verbrandt als een meteoor.

    blender -b -P anim/scenes/s15_stadion.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s15", "stadion", "middag")

B = 27.4
MOUND = V(B / 2, B / 2, 0.25)
HOME = V(0.0, 0.0, 0.0)
ROT_H = heading(MOUND, HOME)
CATCH_AT = V(-0.55, -0.55, 0.0)
held = S.actor("hoofdpersonage", MOUND, ROT_H)
catcher = S.extra(0, CATCH_AT, heading(CATCH_AT, MOUND), energy=1.0)
S.place(held, 0, MOUND, ROT_H)
S.obj("Scorebord_tekst").data.body = "FIRST PITCH: 16,384x"

# pet en handschoen
cap_m = S.mat("pet_blauw", (0.12, 0.25, 0.65))
cap = T.sphere("Pet", (0, 0, 0), 0.315, cap_m, scale=(1.0, 0.6, 1.0), seg=20, ol=0.005)
attach(cap, held, "head", (0, -0.13, -0.02))   # bot-assen: y = op, z = voor
brim = T.cyl("Pet_klep", (0, 0, 0), 0.17, 0.015, cap_m, seg=20, ol=0.003)
brim.scale = (1.0, 0.7, 1.0)
attach(brim, held, "head", (0, -0.17, 0.25), (90, 0, 0))
mitt = T.sphere("Handschoen", (0, 0, 0), 0.11, S.mat("handschoen", (0.55, 0.32, 0.15)), scale=(1, 0.6, 1.1), seg=12, ol=0.004)
attach(mitt, catcher, "hand.L", (0, 0.06, 0.03))

ball = T.sphere("Honkbal", (0, 0, 0), 0.037, P.m("wit"), seg=12, ol=0.002)
grab(S, ball, held, 0.0, "hand.R", loc=(0, 0.05, 0.02), mode="loc")

# ---------------------------------------------------------------- tijdlijn
S.hud(14, "16,384x STRONGER", t0=0.4)
S.music("stadion", 0.0, 60, vol=0.26, fade_in=0.5, fade_out=0.4)
ORGAN = S.sounds[-1]
S.ambience("sfx_publiek", 0.0, 60, vol=0.2)
CROWD = S.sounds[-1]
l1 = S.say("S15-01", gap=0.6)
l2 = S.say("S15-02", gap=0.5)
SOFT = l2[0] + 4.6                              # 'You throw it softly.'
THROW = l2[0] + 6.1
ORGAN["loop_to"] = l2[0] + 1.8
S.music("drums_build", l2[0] + 1.6, THROW - 0.02, vol=0.3, fade_in=0.5, fade_out=0.02)
CROWD["loop_to"] = THROW - 0.02
S.sfx("sfx_donderslag", THROW - 0.02, 1.0)
S.sfx("sfx_whoosh", THROW - 0.15, 0.5)
S.t = THROW + 1.4                               # stilte na de knal
l3 = S.say("S15-03", gap=0.0)
ROOT = l3[0] + 6.6
X128 = l3[0] + 8.7
NORMAL = l3[0] + 11.7
MACH = l3[0] + 15.1
l4 = S.say("S15-04", gap=0.6)
RE0, RE1 = l4[0] + 0.3, l4[0] + 5.9            # herhaling in slow motion tot de bal opbrandt
FINE = l4[0] + 7.95
S.sfx("sfx_slowmo", RE0 - 0.1, 0.5)
S.music("episch_slowmo", RE0 - 0.2, l4[1] + 0.2, vol=0.22, fade_in=0.6, fade_out=0.5)
l5 = S.say("S15-05", gap=0.6)
QUIET = l5[0]
CRAZY = l5[0] + 3.6
S.sfx("sfx_menigte_juicht", CRAZY - 0.1, 0.9)
S.wait(2.0)
END = S.t
S.music("orkest_held", CRAZY - 0.1, END + 0.2, vol=0.32, fade_in=0.15, fade_out=0.8)

S.real(l3[0] + 0.05, l3[1] + 0.2)
S.text("STRENGTH: x16,384", l3[0] + 2.0, l3[1] + 0.2, loc=(0.965, 0.38), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("SPEED = √STRENGTH  →  x128", ROOT, l3[1] + 0.2, loc=(0.965, 0.30), size=44, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("NORMAL THROW: 108 km/h", NORMAL, l3[1] + 0.2, loc=(0.965, 0.22), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.gauge("SPEED: MACH 11", MACH, l3[1] + 1.0, color=(1.0, 0.45, 0.2, 1))
S.text("REPLAY", RE0, RE1 + 0.3, loc=(0.035, 0.30), size=46, color=WHITE, anchor=("LEFT", "BOTTOM"))

# ---------------------------------------------------------------- de worp (zachtjes, onderhands)
DOWN = arm("R", (0.15, 0.0, -1.0), (0.1, 0.15, -1.0))
BACK = arm("R", (0.12, -0.6, -0.78), (0.05, -0.55, -0.83))
FWD = arm("R", (0.1, 0.8, -0.55), (0.0, 0.97, -0.15))
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.5, look=(0.3, 0.3), arms=DOWN)
S.beat(held, l1[0] + 4.0, "zwaaien_a", amount=0.6, face="blij", face_amt=0.7, look=(0.5, 0.3))
S.beat(held, l1[0] + 4.6, "zwaaien_b", amount=0.6, face="blij", face_amt=0.8, look=(0.5, 0.3))
S.beat(held, l1[0] + 5.2, "zwaaien_a", amount=0.6, face="lach", face_amt=0.7, look=(0.4, 0.3))
S.beat(held, l1[1] - 0.5, "staan", face="nerveus", face_amt=0.6, at=V(0, 0, 1.0), arms=DOWN)
S.beat(held, l2[0] + 0.8, "staan", face="vastberaden", face_amt=0.5, at=V(0, 0, 1.0), arms=DOWN, body={"head": (6, 0, 0)})
S.beat(held, l2[0] + 2.4, "staan", face="vastberaden", face_amt=0.8, at=V(0, 0, 1.0), arms=DOWN, ogen_knijp=0.4)
S.beat(held, SOFT, "staan", face="zelfverzekerd", face_amt=0.6, at=V(0, 0, 1.0), arms=DOWN, crouch=(0.03, 4))
S.beat(held, THROW - 0.55, "staan", face="vastberaden", face_amt=0.6, at=V(0, 0, 1.0), arms=BACK, crouch=(0.08, 10))
S.beat(held, THROW, "staan", face="vastberaden", face_amt=0.6, at=V(0, 0, 1.0), arms=FWD, crouch=(0.06, 14))
S.beat(held, THROW + 0.5, "staan", face="geschrokken", face_amt=1.0, at=V(0, 0, 1.0), arms=FWD, crouch=(0.02, 6))
S.beat(held, l3[0] + 1.2, "handen_hoofd", amount=0.6, face="geschrokken", face_amt=0.9, at=V(0, 0, 1.0))
S.beat(held, l3[0] + 5.0, "staan", face="nerveus", face_amt=0.8, at=V(0, 0, 1.0))
S.beat(held, QUIET, "staan", face="nerveus", face_amt=1.0, look=(0.5, 0.3))
S.beat(held, QUIET + 1.5, "staan", face="nerveus", face_amt=1.0, look=(-0.5, 0.3))
S.beat(held, CRAZY + 0.3, "juichen", amount=0.7, face="lach", face_amt=0.8, look=(0.3, 0.4))
S.beat(held, CRAZY + 1.3, "armen_omhoog", face="lach", face_amt=1.0, look=(-0.3, 0.4))
S.hold(held, END)

# vangertje
S.beat(catcher, 0.0, "staan", face="blij", face_amt=0.5, at=S.head(held, 0), crouch=(0.3, 25),
       arms=arms(arm("L", (0.3, 0.85, -0.2), (0.1, 0.9, 0.4))))
S.beat(catcher, THROW - 0.3, "staan", face="vastberaden", face_amt=0.6, at=S.head(held, 0), crouch=(0.32, 28),
       arms=arms(arm("L", (0.3, 0.85, -0.2), (0.1, 0.9, 0.4))))
S.beat(catcher, THROW + 0.1, "staan", face="geschrokken", face_amt=1.0, at=S.head(held, 0), crouch=(0.32, 10),
       arms=arms(arm("L", (0.3, 0.85, -0.2), (0.1, 0.9, 0.4))))
S.hold(catcher, FINE - 0.2)
S.beat(catcher, FINE, "staan", face="verbaasd", face_amt=1.0, look=(0, -0.3), crouch=(0.32, 10),
       arms=arms(arm("L", (0.3, 0.6, -0.5), (-0.3, 0.7, 0.3))))
S.hold(catcher, END)

# ---------------------------------------------------------------- de bal: weg in een lichtstreep, dan de herhaling
bpy.context.scene.frame_set(F(THROW))
bpy.context.view_layer.update()
P0 = ball.matrix_world.translation.copy()
P1 = HOME + V(0.25, 0.25, 0.85)
Pm = P0.lerp(P1, 0.55)
c = ball.constraints[-1]
c.influence = 1.0
c.keyframe_insert("influence", frame=F(THROW) - 1)
c.influence = 0.0
c.keyframe_insert("influence", frame=F(THROW))
show(ball, 0.0, THROW)
dirv = (P1 - P0)
streak = T.cyl("Lichtstreep", (0, 0, 0), 0.05, dirv.length, S.mat("streep", (1.0, 0.75, 0.35), 25.0), seg=10, ol=0)
streak.rotation_mode = "QUATERNION"
streak.rotation_quaternion = V(0, 0, 1).rotation_difference(dirv.normalized())
streak.location = P0
key(streak, THROW - 0.02, scale=(1, 1, 0.02))
key(streak, THROW + 0.06, scale=(1, 1, 1))
key(streak, THROW + 0.3, scale=(0.2, 0.2, 1))
show(streak, THROW, THROW + 0.35)
flash = T.point_light("Knalflits", tuple(P0.lerp(P1, 0.3)), color=(1.0, 0.75, 0.45), energy=0, radius=0.3)
for t, e in ((THROW - 0.02, 0), (THROW + 0.02, 30000), (THROW + 0.4, 0)):
    flash.data.energy = e
    flash.data.keyframe_insert("energy", frame=F(t))
for k in range(9):
    S.puff(P0.lerp(P1, (k + 0.5) / 9), THROW + 0.03 * k, n=3, r=(0.08, 0.16), grow=3.0, dur=4.0, color=(0.75, 0.72, 0.7), rise=0.4, spread=0.15)
S.puff(P1 + V(0, 0, -0.4), THROW + 0.3, n=6, r=(0.2, 0.4), grow=2.5, dur=2.5, color=(0.70, 0.6, 0.48), rise=0.4, spread=0.6)

# herhaling: een vuurbal die halverwege opbrandt
fire = T.sphere("Vuurbal", (0, 0, 0), 0.05, S.mat("vuurbal", (1.0, 0.55, 0.15), 12.0), seg=12, ol=0)
tail = T.cyl("Vuurstaart", (0, 0, 0), 0.05, 1.0, S.mat("vuurstaart", (1.0, 0.4, 0.1), 6.0), r2=0.002, seg=10, ol=0)
tail.parent = fire
tail.rotation_mode = "QUATERNION"
tail.rotation_quaternion = V(0, 0, 1).rotation_difference(-dirv.normalized())
tail.scale = (1, 1, 1.6)
fire_pos = lambda t: P0.lerp(Pm, smooth(RE0, RE1, t) ** 0.8)
fr = list(range(F(RE0), F(RE1) + 1))
bake(fire, "location", fr, [tuple(fire_pos((f - 1) / FPS)) for f in fr])
bake(fire, "scale", fr, [(s, s, s) for s in (1.0 - 0.7 * smooth(RE1 - 1.5, RE1, (f - 1) / FPS) for f in fr)])
show(fire, RE0, RE1)
S.debris(Pm, RE1, n=26, size=(0.01, 0.025), mat=S.mat("sintel", (1.0, 0.5, 0.15), 8.0), speed=(0.3, 1.2), up=0.4, floor=0.0, life=2.0, name="Sintel")
S.puff(Pm, RE1, n=6, r=(0.1, 0.22), grow=3.0, dur=3.0, color=(0.35, 0.33, 0.32), rise=0.3, spread=0.3)
S.sfx("sfx_vloer_kraak", RE1 - 0.05, 0.25)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-14, -14, 9), (30, 30, 3), 22), ((-11, -11, 7.5), (30, 30, 3), 24))
S.cam(l1[0] + 3.8, S.shot(held, l1[0] + 4.2, "med", az=10, lens=30), S.shot(held, l1[1], "med", az=6, lens=34))
S.cam(l2[0] + 1.0, ((-3.0, -3.0, 1.15), MOUND + V(0, 0, 1.0), 70), ((-3.0, -3.0, 1.15), MOUND + V(0, 0, 1.0), 85))
S.cam(SOFT - 0.2, S.shot(held, SOFT, "cu", az=12, lens=36), S.shot(held, THROW - 0.7, "cu", az=10, lens=40))
S.cam(THROW - 0.6, (MOUND + V(5.0, 5.0, 2.3), HOME + V(0, 0, 0.8), 45), (MOUND + V(5.0, 5.0, 2.3), HOME + V(0, 0, 0.8), 45),
      shake=lambda t: max(0.0, 3.0 - (t - THROW) * 2.5) if t > THROW else 0.0)
S.cam(THROW + 1.0, (CATCH_AT + V(3.0, 0.4, 1.0), CATCH_AT + V(0, 0, 0.75), 32), (CATCH_AT + V(2.6, 0.5, 1.0), CATCH_AT + V(0, 0, 0.75), 36))
S.cam(l3[0] + 2.5, S.shot(held, l3[0] + 3.0, "mcu", az=20, lens=32, lr=0.35), S.shot(held, l3[1], "mcu", az=15, lens=34, lr=0.35))
S.cam(RE0 - 0.1, None, fn=lambda t: (fire_pos(min(t, RE1)) + V(1.6, -1.6, 0.4), fire_pos(min(t, RE1)), 30))
S.cam(FINE - 0.2, (CATCH_AT + V(1.4, 0.2, 0.95), CATCH_AT + V(0, 0, 0.75), 36), (CATCH_AT + V(1.3, 0.25, 0.95), CATCH_AT + V(0, 0, 0.75), 40))
S.cam(QUIET - 0.1, (MOUND + V(1.0, 1.0, 1.6), V(-10, -10, 4.0), 24), (MOUND + V(1.0, 1.0, 1.7), V(-10, -10, 4.5), 24))
S.cam(CRAZY - 0.1, S.shot(held, CRAZY, "med", az=15, lens=28), S.shot(held, END, "med", az=30, lens=26))

S.finish(length=END)
