"""S13a · Dag 12 · straat: lopen is nu een vaardigheid. Eén onvoorzichtige stap en je staat op het dak van een bus.

    blender -b -P anim/scenes/s13a_straat.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s13a", "straat", "zonnig")

WALK_Y, Z0 = 7.0, 0.12                          # stoep
BUS_Y, ROOF = 2.6, 3.05
V_BUS = 8.3
X_START, X_JUMP, X_LAND = -7.0, 0.0, 1.6
for n in ("Auto_geparkeerd_2", "Auto_geparkeerd_3"):
    S.obj(n).hide_render = True                # ruimte voor de bus

held = S.actor("hoofdpersonage", (X_START, WALK_Y, Z0), 90)
vriend = S.actor("beste_vriend", (X_START - 1.4, WALK_Y + 0.4, Z0), 90)
bus = prop_bus(S)

# ---------------------------------------------------------------- tijdlijn
S.hud(12, "4,096x STRONGER", t0=0.4)
S.music("speels", 0.0, 60, vol=0.26, fade_in=0.4, fade_out=0.3, start=10.0)
PLAY = S.sounds[-1]
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.14)
l1 = S.say("S13-01", gap=0.6)
l2 = S.say("S13-02", gap=0.4)
JUMP = l2[0] + 4.25                             # 'One careless step...'
LAND = JUMP + 0.95
S.sfx("sfx_sprong_dak", JUMP - 0.05, 0.7)
S.sfx("sfx_fiets_bus", LAND - 2.5, 0.35)
S.sfx("sfx_dreun", LAND - 0.02, 0.4)
S.sfx("sfx_whoosh", JUMP, 0.4)
l3 = S.say("S13-03", gap=1.0)
S.wait(0.8)
END = S.t
PLAY["loop_to"] = END + 0.2
S.text("NEWTON'S 3RD LAW", l2[0] + 0.4, JUMP - 0.3, loc=(0.965, 0.22), size=46, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("PUSH 4,096x  →  FLY 4,096x", l2[0] + 1.6, JUMP - 0.3, loc=(0.965, 0.14), size=46, color=GOLD, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- voorzichtig lopen, armen uit voor balans
BAL = arms(arm("L", (0.9, 0.1, -0.35), (0.95, 0.15, -0.05)), arm("R", (0.9, 0.1, -0.35), (0.95, 0.15, -0.05)))
S.walk(held, 0.2, JUMP - 0.4, [V(X_START, WALK_Y, Z0), V(X_JUMP, WALK_Y, Z0)], stride=0.22, arms=None)
S.beat(held, 0.0, "staan", face="vastberaden", face_amt=0.6, look=(0, -0.5), arms=BAL, body={"head": (14, 0, 0)}, feet="keep")
for k, t in enumerate((1.4, 3.0, l2[0] + 0.5, l2[0] + 2.2)):
    S.beat(held, t, "staan", face="inspanning" if k % 2 else "vastberaden", face_amt=0.5, look=(0, -0.5), arms=BAL,
           body={"head": (14, 0, 0), "chest": (0, 6 if k % 2 else -6, 0)}, feet="keep")
# de onvoorzichtige stap
S.beat(held, JUMP - 0.4, "staan", face="blij", face_amt=0.6, look=(0.3, 0.2), body={"head": (-4, 0, 0)})
S.beat(held, JUMP - 0.1, "staan", face="blij", face_amt=0.5, crouch=(0.06, 6))
S.beat(held, JUMP + 0.1, "armen_omhoog", amount=0.8, face="geschrokken", face_amt=1.0, look=(0, 0.4))
S.beat(held, LAND - 0.2, "schrap", face="bang", face_amt=1.0, look=(0, -0.6))
S.beat(held, LAND + 0.1, "schrap", face="bang", face_amt=1.0, crouch=(0.22, 20), look=(0, -0.4), arms=BAL)
S.beat(held, LAND + 1.2, "schrap", face="geschrokken", face_amt=0.9, crouch=(0.2, 16), at=S.head(vriend, LAND), arms=BAL)
S.beat(held, l3[0] + 0.4, "schrap", face="nerveus", face_amt=0.8, crouch=(0.2, 16), look=(-0.6, 0), arms=BAL)
S.hold(held, END)

bus_x = lambda t: X_LAND + V_BUS * (t - LAND)
T0B = LAND - 4.5
bfr = list(range(F(T0B), F(END) + 1))
key(bus, T0B - 1 / FPS, loc=(-500, BUS_Y, 0), interp="CONSTANT")
bake(bus, "location", bfr, [(bus_x((f - 1) / FPS), BUS_Y, 0.0) for f in bfr])
# de sprong: een boog van de stoep naar het rijdende busdak, daarna rijdt hij mee
jfr = list(range(F(JUMP), F(END) + 1))
rows = []
for f in jfr:
    t = (f - 1) / FPS
    if t <= LAND:
        u = (t - JUMP) / (LAND - JUMP)
        x = lerp(X_JUMP, bus_x(LAND), u)
        y = lerp(WALK_Y, BUS_Y + 0.2, u)
        z = lerp(Z0, ROOF, u) + 4 * 1.6 * u * (1 - u)
    else:
        x, y, z = bus_x(t), BUS_Y + 0.2, ROOF
    rows.append((x, y, z))
bake(held.rig, "location", jfr, rows)

# vriend loopt mee, blijft staan, kijkt de bus na
S.walk(vriend, 0.2, JUMP - 0.2, [V(X_START - 1.4, WALK_Y + 0.4, Z0), V(X_JUMP - 1.6, WALK_Y + 0.4, Z0)], stride=0.3, arms=0.4)
S.beat(vriend, 0.0, "ontspannen", face="lach", face_amt=0.5, at=S.head(held, 0))
S.beat(vriend, l2[0] + 1.0, "ontspannen", face="grijns", face_amt=0.6, at=S.head(held, l2[0]))
S.beat(vriend, JUMP + 0.2, "schrik", face="geschrokken", face_amt=1.0, at=V(X_LAND, BUS_Y, 3.6))
S.turn(vriend, LAND + 0.3, LAND + 0.9, heading((X_JUMP - 1.6, WALK_Y + 0.4), (14, BUS_Y)), V(X_JUMP - 1.6, WALK_Y + 0.4, Z0))
S.beat(vriend, LAND + 1.0, "handen_hoofd", amount=0.6, face="verbaasd", face_amt=1.0, at=V(14, BUS_Y, 3.6))
S.beat(vriend, l3[0] + 0.3, "armen_over", face="zelfverzekerd", face_amt=0.7, look=(0, 0), body={"head": (0, 0, 10)})
S.beat(vriend, l3[1], "armen_over", face="grijns", face_amt=0.8, look=(0, 0), body={"head": (0, 0, 10)}, wenkbrauw_op=0.7)
S.hold(vriend, END)

# ---------------------------------------------------------------- camera
hx = lambda t: S.frame_of(held, t)[0].x
S.cam(0.0, None, fn=lambda t: (V((hx(t) + 1.8, 4.3, 1.05)), V((hx(t) - 0.2, WALK_Y, 0.75)), 28))
S.cam(l1[1] - 0.2, None, fn=lambda t: (V((hx(t) + 0.9, WALK_Y - 0.9, 0.35)), V((hx(t) - 0.1, WALK_Y, 0.25)), 28))
S.cam(l2[0] + 1.8, ((7.0, -1.2, 1.7), (-2.0, 5.8, 1.1), 24), ((6.6, -1.0, 1.7), (-1.0, 5.8, 1.2), 26))
S.cam(JUMP - 0.3, ((3.0, -6.5, 2.3), (1.2, 4.0, 2.2), 20), ((3.0, -6.5, 2.3), (2.2, 4.0, 2.6), 20))
S.cam(LAND + 0.5, None, fn=lambda t: (V((bus_x(t) + 3.5, -2.2, 3.6)), V((bus_x(t) - 0.1, BUS_Y, 3.6)), 30))
S.cam(l3[0] - 0.2, S.shot(vriend, l3[0], "mcu", az=-25, lens=30), S.shot(vriend, END, "mcu", az=-20, lens=34))

S.finish(length=END)
