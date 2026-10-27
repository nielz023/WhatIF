"""S08 · Dag 6 · bowlingbaan: verjaardag van de vriend. De bal gaat door de kegels, de machine en de muur.

    blender -b -P anim/scenes/s08_bowling.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s08", "bowling", None)
rnd = random.Random(8)

PITCH = 1.64
X0 = -5.74
LX = X0 + 3 * PITCH                         # baan 4
Y0, Y1 = -6.0, 12.4                          # foutlijn, kegels
HERO = V(LX, Y0 - 0.9, 0)
FRIEND = V(LX - 1.5, Y0 - 1.9, 0)
MACH_Y = 12.76                               # voorkant van de pinsetter
WALL_Y = 14.97                               # achtermuur
BALL_Z = 0.19

held = S.actor("hoofdpersonage", HERO, 180)
vriend = S.actor("beste_vriend", FRIEND, 150)
staff = S.extra(4, (8.0, -12.6, 0), 0)                    # medewerker achter de schoenenbalie
guests = [S.extra(1, (X0 + 0.0, Y0 - 1.0, 0), 180), S.extra(6, (X0 + 6 * PITCH, Y0 - 1.2, 0), 190), S.extra(2, (X0 + 7 * PITCH - 0.6, Y0 - 2.6, 0), 160)]

# feesthoedje voor de jarige
hat = T.cyl("Feesthoedje", (0, 0, 0), 0.11, 0.3, S.mat("feesthoed", (0.98, 0.3, 0.6)), r2=0.008, seg=16, ol=0.004)
for k in range(3):
    T.torus(f"Feesthoedje_streep{k}", (0, 0, 0.06 + k * 0.08), 0.1 - k * 0.028, 0.008, S.mat("feesthoed_geel", (1.0, 0.85, 0.2)), seg=16, seg2=6, ol=0).parent = hat
T.sphere("Feesthoedje_pompon", (0, 0, 0.31), 0.03, S.mat("feesthoed_geel", (1.0, 0.85, 0.2)), seg=8, ol=0.002).parent = hat
attach(hat, vriend, "head", (0, 0.0, 0), (0, 0, 0))

ball = T.sphere("Zijn_bowlingbal", (HERO.x + 0.2, HERO.y + 0.1, 0.62), 0.11, S.mat("bal_paars", (0.55, 0.2, 0.9)), seg=18, ol=0.004)
for k, (dx, dz) in enumerate(((-0.03, 0.06), (0.03, 0.06), (0.0, 0.025))):
    T.sphere(f"Bal_gat{k}", (dx, -0.1, dz), 0.016, P.m("zwart"), scale=(1, 0.4, 1), seg=8, ol=0).parent = ball
ticket = T.box("Gouden_kaart", (0, 0, 0), (0.16, 0.01, 0.1), S.mat("goud", (1.0, 0.8, 0.2), 1.2), base=False, bevel=0.006, ol=0.003)
attach(ticket, vriend, "hand.R", (0, 0.07, 0.0), (90, 0, 0))

# ---------------------------------------------------------------- tijdlijn
S.hud(6, "64x STRONGER", t0=0.4)
S.ambience("sfx_klas_geroezemoes", 0.0, 60, vol=0.12)
FUNK1 = len(S.sounds)
S.music("retrofunk", 0.0, 0.0, vol=0.3, fade_in=0.3, fade_out=0.05)
l1 = S.say("S08-01", gap=0.6)
l2 = S.say("S08-02", gap=0.5)
SWING = l2[0] + 0.25
REL = l2[0] + 1.0
PINHIT = REL + 0.22
MACHHIT = PINHIT + 0.05
WALLHIT = MACHHIT + 0.05
S.sounds[FUNK1]["loop_to"] = PINHIT
S.sfx("sfx_bowling_crash", PINHIT - 1.2, 1.0)
S.sfx("sfx_muur_valt", WALLHIT + 0.05, 0.6)
P_PINS = l2[0] + 3.57
P_MACH = l2[0] + 5.0
P_WALL = l2[0] + 6.9
l3 = S.say("S08-03", who=vriend, gap=0.4, gain=1.2)
S.music("retrofunk", l3[0] - 0.3, 60, vol=0.26, fade_in=0.05, start=6.0)
l4 = S.say("S08-04", gap=0.5)
l5 = S.say("S08-05", gap=0.5)
FREE = l5[0] + 2.2
EMO = l5[0] + 5.19
S.wait(1.3)
END = S.t
for snd in S.sounds:
    if snd["file"] == "muziek/retrofunk" and snd["loop_to"] == 60:
        snd["loop_to"] = END + 0.2
        snd["fade_out"] = 0.8

S.real(l4[0] + 0.1, l4[1] + 0.2)
S.text("BOWLING BALL: 7 kg", l4[0] + 1.4, l4[1] + 0.2, loc=(0.965, 0.30), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("THROWN 64x HARDER", l4[0] + 3.7, l4[1] + 0.2, loc=(0.965, 0.22), size=44, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("= SCOOTER CRASH AT 40 km/h", l4[0] + 6.6, l4[1] + 0.2, loc=(0.965, 0.14), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.card("BANNED FOR LIFE", l5[0] + 0.3, l5[0] + 2.0, size=130, dim=0.35, color=(1.0, 0.25, 0.2, 1))
S.gauge("FREE BOWLING: 1 YEAR", FREE + 0.6, END, color=GOLD)

# ---------------------------------------------------------------- l1: verjaardag
S.beat(held, 0.0, "staan", face="blij", face_amt=0.6, at=S.head(vriend, 0))
S.beat(vriend, 0.0, "juichen", face="lach", face_amt=0.9, at=S.head(held, 0))
S.beat(vriend, l1[0] + 1.6, "zwaaien_a", face="lach", at=S.head(held, 0))
S.beat(vriend, l1[0] + 2.0, "zwaaien_b", face="lach", at=S.head(held, 0))
S.beat(vriend, l1[0] + 2.8, "juichen", face="lach", face_amt=1.0, look=(0, 0.2))
S.beat(vriend, l1[1], "staan", face="blij", face_amt=0.8, at=V(LX, Y1, 0.4))
for k, g in enumerate(guests):
    S.beat(g, 0.0, "ontspannen" if k != 1 else "armen_over", face="blij", face_amt=0.4, at=V(g.rig.location.x, Y1, 0.5))
S.beat(staff, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(LX, Y0, 1.0))
# hij pakt de bal en stelt zich op
S.beat(held, l1[0] + 2.4, "staan", face="lach", face_amt=0.6, at=S.head(vriend, 0))
S.reach(held, l1[0] + 3.2, "R", None, 0.0)
S.reach(held, l1[0] + 3.8, "R", ball.location + V(0, 0.02, 0.06))
grab(S, ball, held, l1[0] + 3.85, "hand.R", (0, 0.06, 0.0), release=REL)
S.reach(held, l1[0] + 4.6, "R", None, 0.0)
S.beat(held, l1[1], "staan", face="vastberaden", face_amt=0.6, at=V(LX, Y1, 0.4), arms=HOLD_FRONT_R)

# ---------------------------------------------------------------- l2: nauwelijks zwaaien
BACK = arm("R", (0.1, -0.5, -0.85), (0.05, -0.6, -0.8))
FWD = arm("R", (0.05, 0.75, -0.65), (0.0, 0.9, -0.3))
S.beat(held, SWING, "staan", face="neutraal", face_amt=0.6, at=V(LX, Y1, 0.4), arms=BACK, crouch=(0.08, 14), feet=((0.0, 0.12, 0), (0.0, -0.1, 0)))
S.beat(held, REL, "staan", face="blij", face_amt=0.4, at=V(LX, Y1, 0.3), arms=FWD, crouch=(0.12, 18), feet=((0.0, 0.14, 0), (0.0, -0.14, 0)))
S.hold(held, PINHIT)
S.beat(held, PINHIT + 0.3, "schrik", face="geschrokken", at=V(LX, Y1, 0.4), crouch=(0.06, -6))
S.beat(held, l2[0] + 3.0, "handen_hoofd", face="geschrokken", face_amt=0.9, at=V(LX, WALL_Y, 0.4))
S.hold(held, l2[1])
S.beat(vriend, REL - 0.2, "staan", face="blij", face_amt=0.6, at=V(LX, Y1, 0.4))
S.beat(vriend, PINHIT + 0.25, "schrik", face="geschrokken", at=V(LX, Y1, 0.4))
S.beat(vriend, l2[0] + 3.4, "staan", face="verbaasd", face_amt=1.0, at=V(LX, WALL_Y, 0.4))
for k, g in enumerate(guests):
    S.beat(g, PINHIT + 0.3 + 0.1 * k, "schrik", face="geschrokken", at=V(LX, Y1, 0.6))
    S.beat(g, l3[0], "staan", face="verbaasd", face_amt=0.8, at=S.head(held, l3[0]))
S.beat(staff, PINHIT + 0.4, "schrik", face="geschrokken", at=V(LX, Y1, 0.6))
S.beat(staff, l3[1], "armen_over", face="boos", face_amt=0.8, at=S.head(held, l3[0]))

# de bal: harde lijn over de baan, door alles heen
p_rel = HERO + V(0.12, 0.55, BALL_Z)
key(ball, REL, loc=p_rel)
key(ball, PINHIT, loc=V(LX, Y1 - 0.9, BALL_Z))
key(ball, MACHHIT, loc=V(LX, MACH_Y, BALL_Z + 0.15))
key(ball, WALLHIT, loc=V(LX, WALL_Y, BALL_Z + 0.2))
key(ball, WALLHIT + 0.1, loc=V(LX, WALL_Y + 4.0, BALL_Z + 0.25))
for fc in A._fcurves(ball):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
visible(ball, WALLHIT + 0.1, False)
# kegels vliegen alle kanten op en blijven liggen
for k in range(10):
    pin = S.obj(f"Kegel_baan4_{k + 1}")
    p0 = pin.location.copy()
    t0 = PINHIT + 0.02 * (k % 4)
    side = rnd.uniform(-1, 1)
    land = V(LX + side * 1.6, Y1 - rnd.uniform(0.2, 2.8), 0.08 + 0.06)
    top = (p0 + land) * 0.5 + V(0, 0.4, rnd.uniform(0.8, 1.7))
    key(pin, t0 - 1 / FPS, loc=p0, rot=(0, 0, 0))
    key(pin, t0 + 0.25, loc=top, rot=(rnd.uniform(-200, 200), rnd.uniform(-200, 200), rnd.uniform(-90, 90)))
    key(pin, t0 + 0.55, loc=land, rot=(90, 0, rnd.uniform(-180, 180)))
    if k % 3 == 0:
        key(pin, t0 + 0.75, loc=land + V(side * 0.3, -0.2, 0), rot=(90, 0, rnd.uniform(-180, 180)))
S.debris(V(LX, Y1 - 0.7, 0.3), PINHIT, n=14, size=(0.02, 0.05), color=(0.95, 0.95, 0.95), speed=(2.0, 5.0), up=1.0, floor=0.08, life=2.0, name="Kegelsplinter")
# gat in de machine en in de muur (met daglicht erachter)
dark = S.mat("gat_donker", (0.02, 0.02, 0.03))
hole_m = T.cyl("Gat_machine", (LX, MACH_Y - 0.02, BALL_Z + 0.18), 0.26, 0.04, dark, rot=(90, 0, 0), seg=10, ol=0.006)
show(hole_m, MACHHIT)
day = S.mat("daglicht", (1.0, 0.95, 0.8), 6.0)
hole_w = T.cyl("Gat_muur", (LX, WALL_Y - 0.02, BALL_Z + 0.2), 0.3, 0.04, day, rot=(90, 0, 0), seg=11, ol=0.008)
show(hole_w, WALLHIT)
beam = T.point_light("Daglicht_gat", (LX, WALL_Y - 0.4, 0.5), color=(1.0, 0.92, 0.75), energy=0, radius=0.3)
beam.data.keyframe_insert("energy", frame=1)
beam.data.keyframe_insert("energy", frame=F(WALLHIT))
beam.data.energy = 250
beam.data.keyframe_insert("energy", frame=F(WALLHIT) + 2)
S.debris(V(LX, MACH_Y - 0.05, 0.4), MACHHIT, n=16, size=(0.03, 0.08), color=(0.32, 0.32, 0.38), speed=(1.5, 4.0), up=0.8, floor=0.08, life=2.2, name="Machinedeel")
S.debris(V(LX, MACH_Y - 0.05, 0.4), MACHHIT, n=14, size=(0.008, 0.02), color=(1.0, 0.8, 0.3), speed=(1.5, 3.5), up=1.2, floor=0.08, life=0.7, name="Vonk")
S.debris(V(LX, WALL_Y - 0.05, 0.45), WALLHIT, n=18, size=(0.05, 0.12), color=(0.2, 0.15, 0.32), speed=(0.8, 2.5), up=0.6, floor=0.0, life=2.5, name="Muurbrok")
S.puff(V(LX, MACH_Y - 0.1, 0.45), MACHHIT, n=6, r=(0.12, 0.25), grow=2.4, dur=2.0, color=(0.45, 0.42, 0.5), rise=0.5, spread=0.5)
S.puff(V(LX, WALL_Y - 0.2, 0.45), WALLHIT, n=6, r=(0.15, 0.3), grow=2.4, dur=2.5, color=(0.55, 0.5, 0.6), rise=0.5, spread=0.6)
# scorescherm: STRIKE
strike = T.text("Scorescherm_strike", "X  STRIKE!", (0, -0.085, 0.36), 0.28, S.mat("strike_goud", (1.0, 0.75, 0.15), 1.6), rot=(90, 0, 0), extrude=0.0)
plate = T.box("Scorescherm_strike_plaat", (0, -0.075, 0.07), (1.36, 0.004, 0.76), S.mat("strike_plaat", (0.05, 0.03, 0.12)), bevel=0, ol=0)
for o in (strike, plate):
    o.parent = S.obj("Scorescherm_2")
    show(o, l3[0] + 0.3)

# ---------------------------------------------------------------- l3: 'That's a strike, right?'
S.beat(vriend, l3[0], "wijzen", face="lach", face_amt=1.0, at=V(LX - 0.8, Y0 - 0.3, 3.0))
S.beat(vriend, l3[0] + 1.9, "juichen", face="lach", face_amt=1.0, at=S.head(held, l3[0]))
S.beat(vriend, l3[1] + 0.3, "staan", face="lach", face_amt=0.7, at=S.head(held, l3[0]))
S.beat(held, l3[0] + 0.4, "schouders_op", face="nerveus", face_amt=0.8, at=S.head(vriend, l3[0]))
S.beat(held, l3[1], "staan", face="grijns", face_amt=0.6, at=S.head(vriend, l3[0]))
S.hold(held, l4[0] + 4.0)
S.beat(held, l4[0] + 5.0, "handen_zij", amount=0.5, face="nerveus", face_amt=0.8, look=(0.3, -0.1))
S.hold(held, l4[1])
S.hold(vriend, l4[1])
# ---------------------------------------------------------------- l5: levenslang verbannen, vriend krijgt gratis bowlen
S.beat(held, l5[0] + 0.2, "staan", face="verdrietig", face_amt=0.8, at=S.head(staff, l5[0]))
S.beat(held, FREE + 0.5, "armen_over", face="twijfel", face_amt=0.8, at=S.head(vriend, FREE))
S.hold(held, END)
S.beat(staff, l5[0], "wijzen", face="boos", face_amt=0.9, at=S.head(held, l5[0]))
S.hold(staff, END)
S.beat(vriend, FREE - 0.3, "staan", face="blij", face_amt=0.6, at=S.head(held, FREE))
S.reach(vriend, FREE + 0.2, "R", S.head(vriend, FREE) + V(0.15, -0.45, -0.25))
S.beat(vriend, FREE + 0.5, "staan", face="lach", face_amt=1.0, at=S.head(held, FREE))
show(ticket, FREE + 0.2)
# 'emotional damages': nep-traantje wegvegen, dan een grijns
S.reach(vriend, EMO, "R", None, 0.0)
S.reach(vriend, EMO + 0.3, "L", S.head(vriend, EMO) + V(0.1, -0.22, 0.0))
S.beat(vriend, EMO + 0.3, "staan", face="verdrietig", face_amt=1.0, look=(0, -0.3), ogen_knijp=0.6)
S.reach(vriend, EMO + 1.6, "L", None, 0.0)
S.beat(vriend, EMO + 1.6, "staan", face="grijns", face_amt=1.0, at=S.head(held, EMO))
S.hold(vriend, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((LX + 4.0, Y0 - 6.2, 2.4), (LX - 1.0, Y0 + 4.0, 0.9), 22), ((LX + 3.6, Y0 - 5.8, 2.3), (LX - 1.0, Y0 + 4.0, 0.9), 24))
S.cam(l1[0] + 2.6, S.shot(vriend, l1[0] + 3.0, "mcu", az=10, lens=30, up=0.08), S.shot(vriend, l1[1], "mcu", az=6, lens=34, up=0.08))
S.cam(l1[1], ((LX + 2.7, HERO.y - 0.9, 1.15), (LX, HERO.y + 0.4, 0.8), 24), ((LX + 2.6, HERO.y - 0.7, 1.1), (LX, HERO.y + 0.6, 0.7), 26))
S.cam(REL + 0.08, ((LX + 0.35, Y1 - 4.0, 0.32), (LX, Y1 - 0.5, 0.25), 32), ((LX + 0.35, Y1 - 4.0, 0.32), (LX, Y1 - 0.5, 0.25), 32),
      shake=lambda t: max(0.0, 2.0 - (t - PINHIT) * 2.5) if t > PINHIT else 0.0)
S.cam(PINHIT + 0.8, S.shot(held, PINHIT + 1.2, "mcu", az=0, lens=32, h=0.0), S.shot(held, P_PINS, "mcu", az=0, lens=36, h=0.0))
S.cam(P_PINS, ((LX - 1.7, Y1 - 3.4, 1.4), (LX, Y1 - 1.2, 0.2), 26), ((LX - 1.3, Y1 - 2.6, 1.2), (LX, Y1 - 0.9, 0.2), 28))
S.cam(P_MACH, ((LX + 1.1, MACH_Y - 2.2, 0.8), (LX, MACH_Y, 0.4), 30), ((LX + 0.7, MACH_Y - 1.4, 0.6), (LX, MACH_Y, 0.4), 34))
S.cam(P_WALL, ((LX + 0.3, MACH_Y - 1.3, 0.5), (LX, MACH_Y, 0.4), 30), ((LX + 0.1, MACH_Y - 0.45, 0.42), (LX, WALL_Y, 0.42), 34))
S.cam(l3[0] - 0.1, S.shot(vriend, l3[0], "mcu", az=-12, lens=30, up=0.08), S.shot(vriend, l3[0] + 1.6, "mcu", az=-8, lens=32, up=0.08))
S.cam(l3[0] + 1.7, ((LX - 0.82, Y0 - 2.6, 2.3), (LX - 0.82, Y0 - 0.3, 3.0), 30))
S.cam(l3[0] + 2.5, ((LX + 2.2, Y0 - 4.4, 1.5), (LX - 0.6, Y0 - 1.2, 1.1), 24), ((LX + 2.0, Y0 - 4.2, 1.5), (LX - 0.6, Y0 - 1.2, 1.1), 26))
S.cam(l4[0] + 0.1, ((LX - 0.4, Y0 - 2.4, 1.9), (LX, Y1 + 1.5, 0.4), 24), ((LX - 0.4, Y0 + 3.0, 1.5), (LX, Y1 + 1.5, 0.4), 28))
S.cam(l4[0] + 5.0, S.shot(held, l4[0] + 5.5, "mcu", az=-20, lens=30), S.shot(held, l4[1], "mcu", az=-16, lens=34))
S.cam(l5[0] - 0.1, S.shot(held, l5[0] + 0.5, "mcu", az=12, lens=30), S.shot(held, l5[0] + 2.0, "mcu", az=10, lens=34))
S.cam(FREE - 0.1, S.shot(vriend, FREE + 0.5, "med", az=-10, lens=30), S.shot(vriend, END, "med", az=-6, lens=34))

S.finish(length=END)
