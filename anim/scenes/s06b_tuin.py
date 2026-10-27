"""S06b · Dag 4 · achtertuin bij zonsondergang: hij springt, zes meter hoog, en staat op het dak.

    blender -b -P anim/scenes/s06b_tuin.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s06b", "tuin", "zonsondergang")

G = 9.81
START = V(0.3, 5.4, 0)                       # op het gazon, kijkt naar het huis (-y)
ROOF_Y = -0.35
ROOF = V(0.3, ROOF_Y, 6.0 + (0.35 - ROOF_Y) * 0.66)    # net boven de dakgoot (dakhelling 33 graden)
APEX = 6.8
DOOR = V(1.4, 1.0, 0)                        # achterdeur (gevel op y = 0)
MOM_AT = V(1.25, 3.3, 0)
BRO_AT = V(-0.15, 3.0, 0)

S.obj("Barbecue").hide_render = True                  # stond steeds als zwarte bol voor de camera
held = S.actor("hoofdpersonage", START, 0, energy=1.0)
mama = S.actor("mama", DOOR, 180, energy=0.9)
broer = S.actor("broertje", DOOR + V(0, 0.1, 0), 180, energy=1.4)

# ---------------------------------------------------------------- tijdlijn
S.hud(4, "16x STRONGER", t0=0.3, tick=False)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.08)
l5 = S.say("S06-05", gap=0.6)
JUMP = l5[0] + 3.05                          # '...you jump.'
l6 = S.say("S06-06", gap=0.3)
LAND = l6[0] + 6.9                           # na 'about six meters'
GREAT = l6[0] + 7.65
DOWN = l6[0] + 8.7                           # 'Until you realize...'
S.sfx("sfx_whoosh", JUMP - 0.2, 0.8)
S.sfx("sfx_dreun", JUMP - 0.05, 0.5)
S.sfx("sfx_sprong_dak", LAND - 0.7, 1.0)
MUSIC_END = l6[1] + 0.5
S.music("opbouw_vliegen", 0.0, MUSIC_END, vol=0.3, fade_in=0.6, fade_out=0.25)
l7 = S.say("S06-07", who=mama, gap=0.7, gain=1.2)        # muziek is stil voor mama
LOOKUP = l7[0] + 1.6
l8 = S.say("S06-08", who=broer, gap=0.25, gain=1.3)
S.wait(1.6)
END = S.t
S.music("speels", l8[0] - 0.1, END + 0.2, vol=0.22, fade_in=0.4, fade_out=0.6, start=8.0)

# de wetenschap
S.real(l6[0] + 0.2, l6[0] + 7.4)
S.text("NORMAL JUMP: 40 cm", l6[0] + 0.6, l6[0] + 7.4, loc=(0.965, 0.30), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("16x STRONGER, SAME WEIGHT", l6[0] + 3.0, l6[0] + 7.4, loc=(0.965, 0.22), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("= ABOUT 6 METERS", l6[0] + 5.65, l6[0] + 7.4, loc=(0.965, 0.14), size=58, color=GOLD, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- de sprong (vertraagd in het midden)
vz0 = math.sqrt(2 * G * APEX)
T_UP = vz0 / G
T_PHYS = T_UP + math.sqrt(2 * (APEX - ROOF.z) / G)
VY = (ROOF.y - START.y) / T_PHYS
DUR = LAND - JUMP
K = 0.86


def tau(t):
    s = min(1.0, max(0.0, (t - JUMP) / DUR))
    return T_PHYS * (s + K * math.sin(2 * math.pi * s) / (2 * math.pi))


def body_at(t):
    u = tau(t)
    return V(START.x, START.y + VY * u, vz0 * u - 0.5 * G * u * u)


frames = list(range(F(JUMP), F(LAND) + 1))
S.place(held, JUMP - 1 / FPS, START, 0)
bake(held.rig, "location", frames, [tuple(body_at((f - 1) / FPS)) for f in frames], interp="LINEAR")
S.place(held, LAND, ROOF, 0)

# hoogtemeter tijdens de vlucht
marks = []
for m in range(1, 7):
    # eerste moment waarop hij m meter haalt
    t = JUMP
    while t < LAND and body_at(t).z < m:
        t += 1 / FPS
    marks.append((m, t))
for k, (m, t) in enumerate(marks):
    S.gauge(f"HEIGHT: {m} m", t, marks[k + 1][1] if k + 1 < len(marks) else LAND + 1.5, color=WHITE if m < 6 else GOLD)

# ---------------------------------------------------------------- hij: aanloop, sprong, landing
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.6, at=ROOF + V(0, 0, 1.0))
S.beat(held, l5[0] + 0.8, "handen_zij", amount=0.6, face="twijfel", face_amt=0.6, at=ROOF + V(0, 0, 1.2))
S.beat(held, l5[0] + 2.0, "staan", face="grijns", face_amt=0.7, at=ROOF + V(0, 0, 1.0))
S.beat(held, JUMP - 0.45, "schrap", face="vastberaden", at=ROOF + V(0, 0, 1.0), crouch=(0.2, 18),
       arms=arms(arm("L", (0.25, -0.6, -0.75), (0.2, -0.7, -0.6)), arm("R", (0.25, -0.6, -0.75), (0.2, -0.7, -0.6))))
S.hold(held, JUMP - 0.02)
S.beat(held, JUMP + 0.12, "armen_omhoog", face="geschrokken", face_amt=0.8, at=ROOF + V(0, 0, 3.0), crouch=(0.0, -6),
       feet=((0, 0.05, -0.04), (0, -0.05, -0.08)))
S.beat(held, JUMP + 0.9, "juichen", face="lach", face_amt=0.9, at=ROOF + V(0, 0, 2.0), crouch=(0.06, 0),
       feet=((0, 0.08, 0.06), (0, -0.04, 0.1)))
S.beat(held, l6[0] + 3.0, "juichen", face="blij", face_amt=0.9, look=(0, 0.3), body={"head": (-15, 0, 0)}, crouch=(0.08, 4),
       feet=((0, 0.1, 0.12), (0, -0.02, 0.15)))
S.beat(held, LAND - 0.35, "schrap", face="geschrokken", at=ROOF + V(0, -0.5, 0.3), crouch=(0.08, 10),
       feet=((0, 0.06, 0.04), (0, 0.0, 0.04)))
S.beat(held, LAND, "schrap", face="inspanning", face_amt=0.8, at=ROOF + V(0, -1.0, 0.0), crouch=(0.26, 24))
S.hold(held, LAND + 0.3)
# opstaan, omdraaien naar de tuin: 'Which is great.'
S.turn(held, LAND + 0.4, LAND + 1.0, 180, ROOF)
S.beat(held, LAND + 0.9, "staan", face="blij", face_amt=0.7, look=(0, 0.2), crouch=(0.04, 0))
S.beat(held, GREAT, "juichen", face="lach", look=(0, 0.3), crouch=(0.02, -4))
S.beat(held, GREAT + 0.5, "vuisten", face="zelfverzekerd", look=(0, 0.1))
S.hold(held, DOWN - 0.1)
# ...en dan kijkt hij naar beneden
S.beat(held, DOWN + 0.4, "staan", face="verbaasd", face_amt=0.7, at=V(0.3, 3.5, 0.0), body={"chest": (6, 0, 0)})
S.beat(held, DOWN + 1.4, "schrap", amount=0.6, face="bang", face_amt=0.9, at=V(0.3, 2.5, 0.0), crouch=(0.12, 14))
S.beat(held, l6[1] - 0.3, "schrap", amount=0.7, face="bang", at=V(0.3, 2.0, 0.0), crouch=(0.18, 20), body={"head": (0, 0, 6)})
S.hold(held, l7[0] + 0.4)
# hoort mama, kijkt naar haar
S.beat(held, l7[0] + 0.7, "schrap", amount=0.5, face="nerveus", face_amt=0.8, at=S.head(mama, 0) + V(MOM_AT.x - DOOR.x, MOM_AT.y - DOOR.y, 0), crouch=(0.14, 14))
S.hold(held, l8[1])
S.beat(held, l8[1] + 0.3, "zwaaien_a", amount=0.8, face="nerveus", face_amt=0.7, look=(0, -0.4), crouch=(0.1, 10))
S.beat(held, l8[1] + 0.6, "zwaaien_b", amount=0.8, face="grijns", face_amt=0.5, look=(0, -0.4), crouch=(0.1, 10))
S.beat(held, l8[1] + 0.9, "zwaaien_a", amount=0.8, face="nerveus", face_amt=0.6, look=(0, -0.4), crouch=(0.1, 10))
S.hold(held, END)

# afzet: kuil in het gras, aarde en gras
S.debris(START + V(0, 0, 0.05), JUMP, n=18, size=(0.03, 0.08), color=(0.35, 0.25, 0.15), speed=(1.5, 4.0), up=1.5, floor=0.0, life=2.0, name="Aarde")
S.debris(START + V(0, 0, 0.05), JUMP, n=14, size=(0.02, 0.06), color=(0.3, 0.6, 0.2), speed=(1.0, 3.0), up=1.2, floor=0.0, life=2.0, name="Gras")
S.puff(START + V(0, 0, 0.1), JUMP, n=6, r=(0.08, 0.16), grow=1.8, dur=1.0, color=(0.55, 0.48, 0.38), rise=0.3, spread=0.5)
S.ring(START + V(0, 0, 0.05), JUMP, r0=0.3, r1=2.2, dur=0.5, color=(0.9, 0.85, 0.7), strength=1.5)
kuil = T.cyl("Kuil_gazon", tuple(START + V(0, 0, 0.004)), 0.42, 0.006, S.mat("kuil_aarde", (0.28, 0.2, 0.12)), seg=16, ol=0.004)
kuil.scale = (1.0, 0.8, 1.0)
show(kuil, JUMP)
# landing: dakpannen springen op
S.debris(ROOF + V(0, 0, 0.05), LAND, n=12, size=(0.05, 0.12), color=(0.35, 0.2, 0.17), speed=(1.0, 2.5), up=1.0, floor=ROOF.z - 0.6, life=1.5, name="Dakpan")
S.puff(ROOF + V(0, 0, 0.1), LAND, n=6, r=(0.12, 0.25), grow=2.0, dur=1.0, color=(0.6, 0.5, 0.45), rise=0.3, spread=0.4)

# ---------------------------------------------------------------- mama en broertje komen naar buiten
show(mama.rig, l7[0] - 0.9)
S.beat(mama, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0, 0))
S.walk(mama, l7[0] - 0.9, l7[0] + 1.0, [DOOR, DOOR + V(0, 0.9, 0), MOM_AT])
S.beat(mama, l7[0] - 0.1, "staan", face="blij", face_amt=0.4, look=(-0.4, 0), body={"head": (0, -25, 0)})
S.beat(mama, l7[0] + 1.0, "staan", face="twijfel", face_amt=0.6, look=(0.5, 0), body={"head": (0, 30, 0)})
S.turn(mama, l7[0] + 1.2, LOOKUP, 0, MOM_AT)
S.beat(mama, LOOKUP, "handen_zij", face="geschrokken", face_amt=0.7, at=ROOF + V(0, 0, 1.0), body={"chest": (-10, 0, 0), "spine": (-6, 0, 0)})
S.beat(mama, LOOKUP + 0.6, "handen_zij", face="boos", face_amt=0.5, at=ROOF + V(0, 0, 1.0), body={"chest": (-10, 0, 0), "spine": (-6, 0, 0)})
S.beat(mama, l8[0] + 0.5, "handen_zij", face="twijfel", face_amt=0.7, at=S.head(broer, 0) + V(BRO_AT.x - DOOR.x, BRO_AT.y - DOOR.y - 0.1, 0))
S.beat(mama, l8[1] + 0.3, "handen_zij", face="boos", face_amt=0.4, at=ROOF + V(0, 0, 1.0), body={"chest": (-10, 0, 0)})
S.hold(mama, END)

BRO_IN = l7[1] - 0.6
show(broer.rig, BRO_IN)
S.beat(broer, 0.0, "staan", face="blij", face_amt=0.5)
S.walk(broer, BRO_IN, l8[0] + 0.15, [DOOR + V(0, 0.1, 0), DOOR + V(-0.4, 0.9, 0), BRO_AT], stride=0.45, arms=1.0, end_rot=0)
t = l8[0] + 0.2
k = 0
while t < END - 0.3:                     # springt op en neer, armen omhoog
    up = BRO_AT + V(0, 0, 0.0)
    S.place(broer, t, up, 0)
    S.place(broer, t + 0.16, up + V(0, 0, 0.22), 0)
    S.place(broer, t + 0.32, up, 0)
    S.beat(broer, t, "juichen", face="lach", at=ROOF + V(0, 0, 1.0), crouch=(0.08, 6))
    S.beat(broer, t + 0.16, "juichen", face="lach", at=ROOF + V(0, 0, 1.0), crouch=(0.0, -4), feet=((0, 0, -0.03), (0, 0, -0.03)))
    t += 0.36
    k += 1
S.beat(broer, END - 0.2, "juichen", face="blij", at=ROOF + V(0, 0, 1.0))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-0.5, 9.0, 1.5), (0.3, 2.0, 3.0), 22), ((-0.4, 8.5, 1.5), (0.3, 2.0, 3.2), 24))
S.cam(l5[0] + 1.4, S.shot(held, l5[0] + 1.6, "mcu", az=22, lens=28, h=-0.35, up=0.05),
      S.shot(held, JUMP - 0.4, "mcu", az=18, lens=30, h=-0.35, up=0.05))
S.cam(JUMP - 0.4, ((1.7, 6.6, 0.35), (0.3, 5.2, 1.2), 18), ((1.7, 6.6, 0.35), (0.3, 4.6, 2.6), 18),
      shake=lambda t: max(0.0, 1.6 - (t - JUMP) * 2.5) if t > JUMP else 0.0)
# meevliegen: naast hem, iets hoger, het huis en de zonsondergang erachter
S.cam(JUMP + 1.4, None, fn=lambda t: (body_at(t) + V(3.4, 1.2, 0.9), body_at(t) + V(0, -0.3, 0.9), 30))
S.cam(LAND - 1.3, ((-3.2, 3.0, 8.6), ROOF + V(0, 0, 0.6), 26), ((-3.0, 2.8, 8.5), ROOF + V(0, 0, 0.6), 28),
      shake=lambda t: max(0.0, 1.2 - (t - LAND) * 2.5) if t > LAND else 0.0)
S.cam(LAND + 1.0, S.shot(held, GREAT, "med", az=8, lens=30, h=-0.6), S.shot(held, DOWN, "med", az=4, lens=34, h=-0.6))
# zijn blik naar beneden (over zijn schouder, met een kleine duizeling)
S.cam(DOWN + 0.2, ((0.75, -1.25, 7.9), (0.4, 4.0, 0.0), 22), ((0.7, -1.15, 7.85), (0.4, 4.0, 0.0), 30))
S.cam(DOWN + 1.9, S.shot(held, DOWN + 2.2, "cu", az=6, lens=30, h=-0.9), S.shot(held, l6[1], "cu", az=4, lens=34, h=-0.9))
# mama
S.cam(l7[0] - 0.6, ((-1.2, 7.6, 0.9), (0.6, 1.5, 3.4), 17), ((-1.1, 7.3, 0.9), (0.6, 1.5, 3.5), 18))
S.cam(LOOKUP - 0.2, S.shot(mama, LOOKUP + 0.3, "mcu", az=-15, lens=30, h=0.25, up=0.05),
      S.shot(mama, l7[1], "mcu", az=-12, lens=34, h=0.25, up=0.05))
# broertje, dan de held die zwaait
S.cam(l8[0] - 0.1, ((-1.6, 7.6, 0.7), (0.4, 1.0, 3.6), 16), ((-1.5, 7.3, 0.7), (0.4, 1.0, 3.7), 17))
S.cam(l8[1] + 0.1, S.shot(held, l8[1] + 0.5, "med", az=10, lens=28, h=-0.8), S.shot(held, END, "med", az=8, lens=30, h=-0.8))

S.finish(length=END)
