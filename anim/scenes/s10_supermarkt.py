"""S10 · Dag 9 · supermarkt: het soepblik knapt, het winkelwagentje gaat door de dichte schuifdeuren.
Newtons derde wet, en hij gaat naar huis met twee paar enkelgewichten.

    blender -b -P anim/scenes/s10_supermarkt.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s10", "supermarkt", None)

DOOR_Y = -18.0
AISLE = V(-3.55, -2.2, 0)                     # soepgang, voor het schap op x = -4.5
CAN = V(-4.12, -2.2, 1.02)
CART0 = V(-2.4, -4.3, 0)
CART_END = V(0.6, -24.3, 0)                   # rolt uit tot vlak voor een geparkeerde auto
CART_DOOR = V(0.15, DOOR_Y, 0)
LAUNCH_AT = V(0.0, -6.0, 0)                   # tegen het eind van schap 3

held = S.actor("hoofdpersonage", AISLE, -90)
cart = S.obj("Winkelwagen_held")
cart_rot = heading(CART0, CART_DOOR)
cart.location = CART0
cart.rotation_euler.z = math.radians(cart_rot)
HANDLE = lambda p: p + V(math.sin(math.radians(cart_rot)), -math.cos(math.radians(cart_rot)), 0) * -0.5 + V(0, 0, 1.05)
staff = S.extra(2, (-6.0, -12.6, 0), 0)                   # kassamedewerker
shopper = S.extra(3, (5.2, -9.0, 0), -60)

can = T.cyl("Soepblik", tuple(CAN), 0.042, 0.11, S.mat("soepblik_rood", (0.88, 0.15, 0.12)), seg=20, ol=0.003)
T.cyl("Soepblik_etiket", (0, 0, 0.03), 0.0425, 0.05, S.mat("soepblik_wit", (0.97, 0.95, 0.9)), seg=20, ol=0, cap=False).parent = can
soup = S.mat("soep", (0.95, 0.45, 0.12))
splat = [T.sphere(f"Soepvlek_{k}", (0, 0, 0), 0.03 + 0.01 * (k % 3), soup, scale=(1, 0.3, 1), seg=8, ol=0.002) for k in range(5)]
weights = []
for side in ("L", "R"):
    for k, off in enumerate((-0.05, -0.12)):
        w = T.torus(f"Enkelgewicht_{side}{k}", (0, 0, 0), 0.085, 0.04, S.mat("enkelgewicht", (0.12, 0.12, 0.14)), seg=20, seg2=8, ol=0.004)
        attach(w, held, "shin." + side, (0, off, 0), (90, 0, 0))
        weights.append(w)

# ---------------------------------------------------------------- tijdlijn
S.hud(9, "512x STRONGER", t0=0.4)
S.ambience("sfx_binnen_sfeer", 0.0, 80, vol=0.1)
S.music("speels", 0.0, 0.0, vol=0.28, fade_in=0.4, start=2.0)
PLAY = S.sounds[-1]
l1 = S.say("S10-01", gap=0.6)
l2 = S.say("S10-02", gap=0.4)
l3 = S.say("S10-03", gap=0.4)
POP = l3[0] + 2.5
PUSH = l3[0] + 4.1
CRASH = l3[0] + 5.55
OPEN = l3[0] + 7.0                            # 'Before they open.'
STOP = l3[0] + 10.2
S.sfx("sfx_blik_plop", POP - 0.05, 0.9)
S.sfx("sfx_whoosh", PUSH - 0.1, 0.6)
S.sfx("sfx_glasdeur", CRASH - 0.1, 1.0)
S.sfx("sfx_schuiven", OPEN - 0.1, 0.5)
l4 = S.say("S10-04", gap=0.3)
l5 = S.say("S10-05", gap=0.5)
NEWTON = l5[0] + 5.1
NOW = l5[0] + 9.15
LAUNCH = l5[0] + 10.6
S.sfx("sfx_whoosh", LAUNCH - 0.15, 0.7)
PLAY["loop_to"] = l5[0] - 0.2
S.music("drums_build", l5[0] - 0.3, l5[1] + 0.3, vol=0.22, fade_in=0.6, fade_out=0.5)
l6 = S.say("S10-06", gap=0.5)
WEIGHTS = l6[0] + 5.94
S.music("speels", l6[0] - 0.2, 80, vol=0.24, fade_in=0.5, start=30.0)
S.wait(1.3)
END = S.t

# boodschappenlijstje
S.text("LIST:", l2[0] + 2.1, l2[1] + 0.5, loc=(0.965, 0.80), size=46, color=CYAN, anchor=("RIGHT", "TOP"))
for k, (w, t) in enumerate((("MILK", 3.2), ("BREAD", 3.8), ("EGGS", 4.4))):
    S.text(w, l2[0] + t, l2[1] + 0.5, loc=(0.965, 0.73 - k * 0.065), size=46, color=WHITE, anchor=("RIGHT", "TOP"))
for k, (w, t) in enumerate((("NO MILK", 0.0), ("NO BREAD", 1.98), ("NO EGGS", 3.1))):
    S.text(w, l6[0] + t, END, loc=(0.965, 0.80 - k * 0.065), size=46, color=(1.0, 0.35, 0.3, 1), anchor=("RIGHT", "TOP"))
S.text("+ 2 PAIRS OF ANKLE WEIGHTS", WEIGHTS, END, loc=(0.965, 0.60), size=46, color=GOLD, anchor=("RIGHT", "TOP"))
S.real(l5[0] + 0.1, l5[1] + 0.2)
S.text("YOU PUSH  →", l5[0] + 1.6, l5[1] + 0.2, loc=(0.965, 0.30), size=48, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("←  IT PUSHES BACK", l5[0] + 3.0, l5[1] + 0.2, loc=(0.965, 0.22), size=48, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("NEWTON'S THIRD LAW", NEWTON, l5[1] + 0.2, loc=(0.965, 0.14), size=52, color=GOLD, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- l1-l2: in de soepgang, mama's lijstje
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.6, at=CAN + V(0, 1.0, 0.1))
S.beat(held, l2[0] + 0.3, "ontspannen", face="twijfel", face_amt=0.5, at=CAN + V(0, -0.5, 0.2))
S.beat(held, l2[0] + 2.2, "staan", face="zelfverzekerd", face_amt=0.6, at=CAN + V(0, 0.3, 0.1))
# l3: blik pakken... en pop
S.reach(held, l3[0] + 0.2, "R", None, 0.0)
S.reach(held, l3[0] + 0.9, "R", CAN + V(0.08, 0.0, 0.03))
grab(S, can, held, l3[0] + 0.95, "hand.R", (0, 0.05, 0.0), mode="loc", release=POP)
S.reach(held, l3[0] + 1.7, "R", AISLE + V(-0.32, 0.05, 1.05))
S.beat(held, l3[0] + 1.6, "staan", face="neutraal", face_amt=0.6, at=AISLE + V(-0.4, 0.05, 1.1))
S.reach(held, POP, "R", AISLE + V(-0.3, 0.05, 1.04))
key(can, POP - 0.06, scale=(1, 1, 1))
key(can, POP - 0.01, scale=(1.35, 1.35, 1.2))
key(can, POP, scale=(0.001, 0.001, 0.001))
S.beat(held, POP + 0.05, "schrik", face="geschrokken", at=AISLE + V(-0.4, 0, 1.1), crouch=(0.0, -8))
S.beat(held, POP + 0.7, "staan", face="twijfel", face_amt=0.8, look=(0.5, 0.2), body={"head": (0, 30, 0)})
S.debris(AISLE + V(-0.3, 0.05, 1.1), POP, n=22, size=(0.015, 0.04), color=(0.95, 0.45, 0.12), speed=(1.0, 3.0), up=0.8, floor=0.0, life=2.0, shape="sphere", name="Soep")
S.debris(AISLE + V(-0.3, 0.05, 1.1), POP, n=6, size=(0.02, 0.05), color=(0.88, 0.15, 0.12), speed=(1.0, 2.5), up=1.0, floor=0.0, life=2.0, name="Blikstuk")
# soepvlekken op zijn gezicht en hoodie
hc = S.head(held, POP)
for k, o in enumerate(splat):
    attach(o, held, "head" if k < 3 else "chest", ((k % 3 - 1) * 0.12, -0.05 * k, 0.0), (0, 0, 0))
    o.location = ((k % 3 - 1) * 0.11, -0.12 + 0.05 * k, -0.27) if k < 3 else ((k - 3.5) * 0.12, 0.12, -0.18)
    show(o, POP + 0.04)

# naar de kar (snede) en duwen
H_CART = CART0 + V(0, 0, 0) - V(math.sin(math.radians(cart_rot)), -math.cos(math.radians(cart_rot)), 0) * 0.95
CUT_CART = l3[0] + 3.25
S.teleport(held, CUT_CART, H_CART, cart_rot)
S.beat(held, CUT_CART, "staan", face="twijfel", face_amt=0.6, at=CART_DOOR + V(0, 0, 1.0))
S.reach(held, CUT_CART, "L", HANDLE(CART0) + V(0.18, 0, 0))
S.reach(held, CUT_CART, "R", HANDLE(CART0) + V(-0.18, 0, 0))
S.reach(held, PUSH - 0.2, "L", HANDLE(CART0) + V(0.18, 0, 0))
S.reach(held, PUSH - 0.2, "R", HANDLE(CART0) + V(-0.18, 0, 0))
S.reach(held, PUSH + 0.1, "L", HANDLE(CART0) + V(0.18, -0.4, 0.05))
S.reach(held, PUSH + 0.1, "R", HANDLE(CART0) + V(-0.18, -0.4, 0.05))
S.reach(held, PUSH + 0.5, "L", None, 0.0)
S.reach(held, PUSH + 0.5, "R", None, 0.0)
S.beat(held, PUSH - 0.1, "duwen", amount=0.5, face="neutraal", face_amt=0.5, at=CART_DOOR + V(0, 0, 1.0))
S.beat(held, PUSH + 0.15, "duwen", amount=0.6, face="geschrokken", at=CART_DOOR + V(0, 0, 1.0))
S.beat(held, CRASH + 0.2, "handen_hoofd", face="geschrokken", face_amt=1.0, at=CART_DOOR + V(0, 0, 1.0))
S.beat(held, OPEN + 0.2, "staan", face="twijfel", face_amt=0.9, at=CART_DOOR + V(0, 0, 1.0))
S.hold(held, l4[0] + 0.2)
# de kar: weg als een kogel, door het glas, over de parkeerplaats
key(cart, PUSH, loc=CART0, rot=(0, 0, cart_rot))
key(cart, CRASH, loc=CART_DOOR, rot=(0, 0, cart_rot))
cf = list(range(F(CRASH), F(STOP) + 1))
rows = []
for f in cf:
    u = min(1.0, ((f - 1) / FPS - CRASH) / (STOP - CRASH))
    e = 1 - (1 - u) ** 2.2
    p = CART_DOOR.lerp(CART_END, e)
    rows.append((p.x, p.y, 0.0))
bake(cart, "location", cf, rows)
key(cart, STOP, rot=(0, 0, cart_rot + 25))
for fc in A._fcurves(cart):
    if fc.data_path == "location":
        for kp in fc.keyframe_points:
            if kp.co.x <= F(CRASH):
                kp.interpolation = "LINEAR"
S.sfx("sfx_hud_tik", STOP - 0.05, 0.5)            # tikje tegen de bumper
for k in range(2):
    d = S.obj(f"Schuifdeur_{k}")
    S.shatter(V(d.location.x, DOOR_Y, 1.5), (2.3, 2.95), CRASH, n=40, normal=(0, -1, 0), speed=(2.0, 5.0), floor=0.0)
    visible(d, CRASH, False)
    # te laat: de (lege) deursponningen schuiven alsnog open
    rail = T.box(f"Deurframe_{k}", (d.location.x, DOOR_Y, 0), (2.3, 0.06, 0.06), P.m("metaal"), bevel=0, ol=0.004)
    rail2 = T.box(f"Deurframe_top_{k}", (d.location.x, DOOR_Y, 2.9), (2.3, 0.06, 0.06), P.m("metaal"), bevel=0, ol=0.004)
    for r in (rail, rail2):
        key(r, OPEN, loc=(d.location.x, DOOR_Y, r.location.z))
        key(r, OPEN + 0.9, loc=(d.location.x + (1 if k else -1) * 2.2, DOOR_Y, r.location.z))

# l4: hij loopt naar het gat, kijkt naar buiten
DOORSTAND = V(0.1, DOOR_Y + 1.1, 0)
S.walk(held, l4[0] + 0.2, l4[0] + 2.6, [H_CART, H_CART + V(0.6, -4.0, 0), DOORSTAND], end_rot=0)
S.beat(held, l4[1] - 0.6, "staan", face="nerveus", face_amt=0.8, at=CART_END + V(0, 0, 0.6))
S.hold(held, l5[0] + 0.3)
# l5: Newton; dan een duwtje tegen het schap en hij schiet achteruit
S.teleport(held, l5[0] + 6.6, LAUNCH_AT, 180)
S.beat(held, l5[0] + 6.6, "staan", face="neutraal", face_amt=0.6, at=V(0, -5.0, 1.0))
S.reach(held, NOW, "R", V(0.05, -5.08, 1.0))
S.beat(held, NOW, "staan", face="zelfverzekerd", face_amt=0.5, at=V(0, -5.0, 1.0))
S.hold(held, LAUNCH)
S.place(held, LAUNCH, LAUNCH_AT, 180)
S.place(held, LAUNCH + 0.9, LAUNCH_AT + V(0, -3.4, 0), 180)
S.place(held, LAUNCH + 1.3, LAUNCH_AT + V(0, -3.6, 0), 180)
S.reach(held, LAUNCH + 0.05, "R", None, 0.0)
S.beat(held, LAUNCH + 0.05, "schrik", face="geschrokken", at=V(0, -5.0, 1.2), crouch=(0.05, -16), feet=((0, 0.12, 0), (0, 0.08, 0)))
S.beat(held, LAUNCH + 0.9, "armen_omhoog", amount=0.7, face="bang", at=V(0, -5.0, 1.2), crouch=(0.12, 8))
S.beat(held, LAUNCH + 1.4, "staan", face="twijfel", face_amt=0.8, at=V(0, -5.0, 1.2))
S.hold(held, l6[0] - 0.1)
# l6: naar buiten, langzaam en zwaar, met enkelgewichten
OUT_A, OUT_B = V(0.2, DOOR_Y + 1.5, 0), V(0.8, DOOR_Y - 4.5, 0)
S.teleport(held, l6[0], OUT_A, 0)
S.beat(held, l6[0], "staan", face="verdrietig", face_amt=0.6, look=(0, -0.2))
S.walk(held, l6[0] + 0.1, END, [OUT_A, OUT_B], stride=0.35, arms=0.3)
for w in weights:
    show(w, l6[0])
S.beat(held, WEIGHTS + 0.5, "staan", face="grijns", face_amt=0.5, look=(0, -0.3))

# figuranten
S.beat(staff, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(-6.0, -10.0, 1.2))
S.beat(staff, CRASH + 0.2, "schrik", face="geschrokken", at=CART_DOOR + V(0, 0, 1.0))
S.beat(staff, OPEN + 0.5, "handen_hoofd", face="geschrokken", face_amt=0.8, at=CART_DOOR + V(0, 0, 1.0))
S.beat(shopper, 0.0, "ontspannen", face="neutraal", face_amt=0.5, at=V(4.5, -6.0, 1.2))
S.beat(shopper, CRASH + 0.25, "schrik", face="geschrokken", at=CART_DOOR + V(0, 0, 1.0))
S.beat(shopper, l5[0], "armen_over", face="boos", face_amt=0.6, at=S.head(held, l5[0]))

# ---------------------------------------------------------------- camera
S.cam(0.0, ((10.5, -14.5, 3.4), (-3.0, 0.0, 0.9), 22), ((9.5, -13.5, 3.2), (-3.0, 0.0, 0.9), 24))
S.cam(l2[0] - 0.1, ((AISLE.x - 0.1, AISLE.y - 2.7, 1.45), AISLE + V(-0.2, 0, 1.0), 28), ((AISLE.x - 0.1, AISLE.y - 2.3, 1.4), AISLE + V(-0.2, 0, 1.05), 32))
S.cam(l3[0] + 0.6, (AISLE + V(0.45, -2.4, 1.5), CAN + V(0.35, 0.0, 0.1), 32), (AISLE + V(0.4, -2.1, 1.45), CAN + V(0.3, 0.0, 0.1), 38))
S.cam(POP + 0.4, ((AISLE.x - 0.25, AISLE.y - 1.6, 1.35), S.head(held, POP) + V(-0.05, 0, -0.1), 34), ((AISLE.x - 0.25, AISLE.y - 1.45, 1.33), S.head(held, POP) + V(-0.05, 0, -0.1), 40))
S.cam(CUT_CART, ((CART0.x + 1.5, CART0.y - 3.0, 1.1), (CART0.x - 0.2, CART0.y + 0.4, 0.8), 24), ((CART0.x + 1.5, CART0.y - 3.0, 1.1), (CART0.x + 0.9, CART0.y - 4.6, 0.6), 24),
      shake=lambda t: max(0.0, 0.8 - (t - PUSH) * 2) if t > PUSH else 0.0)
S.cam(PUSH + 0.6, ((3.4, DOOR_Y - 5.5, 1.3), (0.2, DOOR_Y, 1.0), 24), ((3.2, DOOR_Y - 5.2, 1.3), (0.2, DOOR_Y, 1.0), 26),
      shake=lambda t: max(0.0, 1.5 - (t - CRASH) * 2.5) if t > CRASH else 0.0)
S.cam(CRASH + 1.0, ((-2.2, DOOR_Y + 5.5, 1.6), (0.1, DOOR_Y, 1.3), 24), ((-2.0, DOOR_Y + 5.0, 1.6), (0.1, DOOR_Y, 1.3), 26))
S.cam(OPEN + 1.5, ((4.6, DOOR_Y - 2.6, 1.8), CART_END + V(0, 0, 0.5), 28), ((4.3, DOOR_Y - 2.9, 1.7), CART_END + V(0, 0, 0.5), 32))
S.cam(l4[0] + 2.4, ((2.2, DOOR_Y - 3.0, 1.2), DOORSTAND + V(0, 0, 1.3), 30), ((2.0, DOOR_Y - 2.8, 1.2), DOORSTAND + V(0, 0, 1.3), 34))
S.cam(l5[0] + 0.1, ((4.0, DOOR_Y - 9.0, 2.0), V(0.4, DOOR_Y - 2.5, 0.6), 22), ((3.6, DOOR_Y - 8.0, 2.0), V(0.4, DOOR_Y - 2.5, 0.6), 24))
S.cam(l5[0] + 6.6, ((2.6, -8.2, 1.4), (0.0, -6.6, 1.0), 24), ((2.6, -8.4, 1.4), (0.0, -7.6, 1.0), 24),
      shake=lambda t: max(0.0, 0.8 - (t - LAUNCH) * 2) if t > LAUNCH else 0.0)
S.cam(l6[0], ((3.0, DOOR_Y - 7.0, 1.6), (0.4, DOOR_Y - 1.0, 1.0), 26), ((2.6, DOOR_Y - 7.2, 1.5), (0.6, DOOR_Y - 3.0, 1.0), 28))
S.cam(WEIGHTS - 0.2, None, fn=lambda t: (S.frame_of(held, t)[0] + V(0.7, -0.6, 0.3), S.frame_of(held, t)[0] + V(0, 0, 0.18), 30))
S.cam(WEIGHTS + 1.6, S.shot(held, WEIGHTS + 2.0, "med", az=10, lens=28), S.shot(held, END, "med", az=10, lens=28))

S.finish(length=END)
