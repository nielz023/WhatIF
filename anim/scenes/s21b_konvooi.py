"""S21b · Dag 20 · de straat vol legertrucks, de officier ('Safe for everyone else'), en het konvooi de stad uit:
het gezin in het busje erachter, het broertje dat zwaait, de vriend aan de telefoon. 'And you can't hold your mom's hand.'

    blender -b -P anim/scenes/s21b_konvooi.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s21b", "straat", "konvooi")

LANE = -1.2
V_DRIVE = 4.5
HOME = V(-1.4, 10.4, 0.12)                     # hij op het tuinpad voor de deur
OFF_AT = V(-1.15, 8.75, 0.12)
G = S.mat("legergroen", (0.24, 0.30, 0.16))
G2 = S.mat("legergroen_doek", (0.32, 0.36, 0.22))
BLACK = P.m("zwart")
RUIT = S.mat("autoruit_donker", (0.12, 0.18, 0.26))

for o in bpy.data.objects:
    if o.name.startswith(("Gezinsauto", "Legerjeep_")):
        o.hide_render = True


# ---------------------------------------------------------------- zijn truck: open laadbak met bogen, een bank, de telefoon
def open_truck(name):
    p = [T.box(name + "_chassis", (0, 0, 0.6), (8.0, 2.4, 0.35), BLACK, bevel=0.03, ol=0),
         T.box(name + "_cabine", (3.0, 0, 0.9), (2.0, 2.4, 1.9), G, bevel=0.1, ol=0),
         T.box(name + "_voorruit", (4.0, 0, 1.9), (0.04, 2.0, 0.75), RUIT, bevel=0, ol=0),
         T.box(name + "_bak", (-1.0, 0, 0.95), (5.6, 2.5, 0.12), G, bevel=0.02, ol=0),
         T.box(name + "_bank", (1.25, 0, 1.07), (0.5, 2.2, 0.45), G2, bevel=0.03, ol=0)]
    for y in (1.21, -1.21):
        p.append(T.box(f"{name}_zijbord{y}", (-1.0, y, 1.07), (5.6, 0.08, 0.5), G, bevel=0.01, ol=0))
    p.append(T.box(name + "_achterklep", (-3.77, 0, 1.07), (0.08, 2.5, 0.5), G, bevel=0.01, ol=0))
    for k, x in enumerate((3.0, -0.4, -2.6)):
        for y in (1.15, -1.15):
            p.append(T.cyl(f"{name}_wiel{k}{y}", (x, y, 0.6), 0.6, 0.45, BLACK, rot=(90, 0, 0), seg=18, ol=0))
    o = T.merge(name, p, ol=0.03)
    for k in range(5):
        a = T.torus(f"{name}_boog{k}", (-3.5 + k * 1.25, 0, 1.55), 1.22, 0.03, G, rot=(90, 0, 0), seg=24, seg2=6, ol=0)
        a.parent = o
    return o


def van(name, color=(0.15, 0.45, 0.80)):
    """Gezinsbusje met open ramen, zodat je de familie binnen ziet."""
    body = S.mat("busje", color)
    p = [T.box(name + "_onder", (0, 0, 0.32), (4.8, 2.0, 0.85), body, bevel=0.12, ol=0),
         T.box(name + "_dak", (-0.35, 0, 2.2), (3.7, 2.0, 0.12), body, bevel=0.05, ol=0),
         T.box(name + "_dashboard", (1.3, 0, 1.1), (0.3, 1.9, 0.12), BLACK, bevel=0.02, ol=0)]
    for x in (1.45, 0.0, -2.15):
        for y in (0.96, -0.96):
            p.append(T.box(f"{name}_stijl{x}{y}", (x, y, 1.15), (0.1, 0.08, 1.06), body, bevel=0.02, ol=0, rot=(0, -20 if x > 1 else 0, 0)))
    for x, y in ((0.35, 0.45), (0.35, -0.45)):
        p.append(T.box(f"{name}_stoel{y}", (x, y, 0.6), (0.5, 0.5, 0.25), S.mat("bekleding", (0.25, 0.25, 0.3)), bevel=0.04, ol=0))
        p.append(T.box(f"{name}_leuning{y}", (x - 0.28, y, 0.85), (0.1, 0.5, 0.7), S.mat("bekleding", (0.25, 0.25, 0.3)), bevel=0.04, ol=0))
    p.append(T.box(name + "_achterbank", (-1.0, 0, 0.6), (0.55, 1.8, 0.25), S.mat("bekleding", (0.25, 0.25, 0.3)), bevel=0.04, ol=0))
    p.append(T.box(name + "_achterleuning", (-1.32, 0, 0.85), (0.1, 1.8, 0.7), S.mat("bekleding", (0.25, 0.25, 0.3)), bevel=0.04, ol=0))
    for i, (x, y) in enumerate([(1.5, 0.85), (-1.5, 0.85), (1.5, -0.85), (-1.5, -0.85)]):
        p.append(T.cyl(f"{name}_wiel{i}", (x, y, 0.38), 0.38, 0.26, BLACK, rot=(90, 0, 0), seg=16, ol=0))
    for y in (0.65, -0.65):
        p.append(T.sphere(f"{name}_koplamp{y}", (2.4, y, 0.75), 0.13, S.mat("koplamp", (1, 0.97, 0.85), 2.0), scale=(0.4, 1, 0.7), seg=10, ol=0))
    o = T.merge(name, p, ol=0.02)
    wheel = T.torus(name + "_stuur", (1.0, 0.45, 1.2), 0.17, 0.02, BLACK, rot=(0, 60, 0), seg=20, seg2=6, ol=0)
    wheel.parent = o
    return o


truck = open_truck("Konvooitruck_held")
bus = van("Gezinsbusje")
phone = prop_phone(S, "Telefoon_konvooi", screen=(0.3, 0.85, 0.45))
phone.rotation_euler = (math.radians(-90), 0, math.radians(90))
T.text("Telefoon_naam", "BEST FRIEND", (0, -0.0075, 0.045), 0.012, S.mat("scherm_wit", (1, 1, 1), 3.0), extrude=0.0).parent = phone
call = T.text("Telefoon_tijd", "1:47:12", (0, -0.0075, 0.02), 0.014, S.mat("scherm_wit", (1, 1, 1), 3.0), extrude=0.0)
call.parent = phone
phone.scale = (1.7, 1.7, 1.7)

# de stad die ze achterlaten: torens aan de horizon
rt = random.Random(21)
for k in range(14):
    h = rt.uniform(70, 190)
    T.box(f"Wolkenkrabber_{k}", (rt.uniform(-330, -230), rt.uniform(-70, 70), 0), (rt.uniform(18, 34), rt.uniform(18, 34), h),
          S.mat(f"toren{k % 3}", ((0.55, 0.60, 0.68), (0.62, 0.66, 0.72), (0.48, 0.53, 0.60))[k % 3]), bevel=0.2, ol=0.05)

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", HOME, 0)
officer = S.actor("officier", OFF_AT, heading(OFF_AT, HOME), energy=1.0)
mama = S.actor("mama", V(-1.85, 12.3, 0.3), 0, energy=0.9)
papa = S.actor("papa", V(-0.85, 12.35, 0.3), 0, energy=0.9)
bro = S.actor("broertje", V(-1.35, 12.0, 0.3), 0, energy=0.9)
SOLDIER = dict(shirt=(0.30, 0.36, 0.20), broek=(0.26, 0.30, 0.18))
soldiers = []
for k, (x, y) in enumerate([(-3.3, 8.1), (0.9, 8.0), (-8.0, 6.0), (5.5, 6.0), (-14.0, -3.0), (9.0, -3.1)]):
    ch = S.actor("officier", (x, y, 0.12), 0 if y > 0 else 180, energy=0.6, label=f"soldaat_{k}", outfit=SOLDIER,
                 drop=("officier_lintje", "officier_rang", "officier_epaulet", "officier_pet_embleem"))
    soldiers.append(ch)
buren = [S.extra(k, (x, y, 0.12), heading((x, y), (x, 0)), energy=0.6) for k, (x, y) in
         enumerate([(-9.5, 10.6), (7.2, 10.9), (-6.0, -8.3), (4.0, -8.5)])]

# ---------------------------------------------------------------- tijdlijn
S.hud(20, "1,048,576x STRONGER", t0=0.0, color=(1.0, 0.25, 0.2, 1), tick=False)
S.ambience("sfx_konvooi", 0.0, 60, vol=0.12)
S.music("militair", 0.0, 0, vol=0.26, fade_in=0.4, fade_out=1.8)
DRUMS = S.sounds[-1]
l3 = S.say("S21-03", gap=0.4)
l4 = S.say("S21-04", who=officer, gap=0.6, gain=1.15)
SAFE2 = l4[0] + 3.36                           # 'Safe for everyone else.'
l5 = S.say("S21-05", gap=0.9)
DRIVE = l5[0] - 0.3
FAMILY = l5[0] + 2.6                           # 'Your family in the car behind you.'
BRO = l5[0] + 4.4                              # 'Your little brother waving...'
FRIEND = l5[0] + 6.67                          # 'Your best friend on the phone...'
l6 = S.say("S21-06", gap=0.7)
HANDS = l6[0]
SKY = l6[0] + 1.56                             # 'You could lift a skyscraper...'
MOM = l6[0] + 5.24                             # 'And you can't hold your mom's hand.'
S.wait(2.0)
END = S.t
DRUMS["loop_to"] = MOM - 0.6
S.music("strijk_noot", MOM - 1.0, END + 0.4, vol=0.28, fade_in=1.0, fade_out=1.2)
S.sfx("sfx_suvs", DRIVE + 0.2, 0.2)
S.gauge("A SKYSCRAPER: ~300,000 TONS", SKY + 0.3, MOM - 0.3, color=WHITE)
S.text("YOU: EASY", SKY + 1.6, MOM - 0.3, loc=(0.035, 0.68), size=56, color=(1.0, 0.25, 0.2, 1), anchor=("LEFT", "TOP"))
S.text("YOUR MOM'S HAND: NO", MOM + 0.4, END, loc=(0.035, 0.76), size=56, color=(1.0, 0.25, 0.2, 1), anchor=("LEFT", "TOP"))

# ---------------------------------------------------------------- voertuigen: eerst geparkeerd, dan het konvooi
CONVOY = [(S.obj("Legertruck_5"), -21.0), (S.obj("Legertruck_1"), -33.0), (truck, -45.0), (bus, -54.5),
          (S.obj("Legertruck_2"), -65.0), (S.obj("Legertruck_3"), -77.0)]
PARK = {truck: ((1.0, 2.2, 0), 180), bus: ((9.5, 2.2, 0), 180)}
fr = list(range(F(DRIVE), F(END) + 2))
xs = lambda x0, t: x0 + V_DRIVE * max(0.0, t - DRIVE)
for veh, x0 in CONVOY:
    if veh in PARK:
        (px, py, pz), pr = PARK[veh]
        veh.location = (px, py, pz)
        veh.rotation_euler.z = math.radians(pr)
    key(veh, DRIVE - 1 / FPS, loc=tuple(veh.location), rot=tuple(math.degrees(a) for a in veh.rotation_euler), interp="CONSTANT")
    key(veh, DRIVE, rot=(0, 0, 0), interp="CONSTANT")
    bake(veh, "location", fr, [(xs(x0, (f - 1) / FPS), LANE, 0.0) for f in fr])
TX = lambda t: xs(-45.0, t)                    # zijn truck
BX = lambda t: xs(-54.5, t)                    # het busje
heli = S.obj("Helikopter")
h0 = heli.location.copy()
hfr = list(range(1, F(END) + 2))
bake(heli, "location", hfr, [tuple(h0 + V(0, 0, 0.6 * math.sin((f - 1) / FPS * 1.3))) if (f - 1) / FPS < DRIVE else
                             (TX((f - 1) / FPS) + 14, -14.0, 30 + 0.6 * math.sin((f - 1) / FPS * 1.3)) for f in hfr])

# ---------------------------------------------------------------- de officier bij de voordeur
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.6, at=S.head(officer, 0))
S.beat(held, l4[0] + 0.5, "staan", face="nerveus", face_amt=0.8, at=S.head(officer, l4[0]))
S.beat(held, SAFE2 + 0.3, "staan", face="verdrietig", face_amt=0.8, look=(0, -0.5), body={"head": (14, 0, 0)})
S.beat(officer, 0.0, "staan", face="neutraal", face_amt=0.8, at=S.head(held, 0), body={"chest": (-3, 0, 0)})
S.beat(officer, l4[0] + 0.2, "handen_zij", amount=0.5, face="neutraal", face_amt=1.0, at=S.head(held, l4[0]))
S.beat(officer, SAFE2 - 0.1, "armen_over", face="twijfel", face_amt=0.4, at=S.head(held, l4[0]), body={"head": (6, 0, 0)})
S.hold(officer, END)
for ch, side in ((mama, 1), (papa, -1)):
    S.beat(ch, 0.0, "staan", face="verdrietig", face_amt=0.7, at=S.head(held, 0))
    S.beat(ch, SAFE2 + 0.2, "armen_over" if ch is papa else "staan", face="boos" if ch is papa else "verdrietig", face_amt=0.7,
           at=S.head(officer, SAFE2))
    S.hold(ch, DRIVE - 0.05)
S.beat(bro, 0.0, "staan", face="nerveus", face_amt=0.8, at=S.head(officer, 0))
S.hold(bro, DRIVE - 0.05)
for k, ch in enumerate(soldiers):
    S.beat(ch, 0.0, "staan", face="neutraal", face_amt=0.8, look=(0, 0), body={"chest": (-4, 0, 0)})
    S.beat(ch, DRIVE + 0.5 + k * 0.2, "staan", face="neutraal", face_amt=0.8, at=V(TX(DRIVE + 3), LANE, 2.0))
    S.hold(ch, END)
for k, ch in enumerate(buren):
    S.beat(ch, 0.0, "armen_over" if k % 2 else "staan", face="bang" if k % 2 else "nerveus", face_amt=0.7, at=S.head(held, 0))
    S.beat(ch, DRIVE + 0.5, "staan", face="nerveus", face_amt=0.7, at=V(TX(DRIVE + 4), LANE, 2.0))
    S.hold(ch, END)

# ---------------------------------------------------------------- in het konvooi: iedereen rijdt mee
BED_Z = 1.07
SIT_H, zh = sit(held, seat_top=0.45, lean=8, spread=0.2)
HERO_L = V(0.95, -0.2, BED_Z + zh)             # op de bank, rug naar de cabine, gezicht naar achteren
PHONE_L = V(0.5, 0.5, BED_Z + 0.01)           # op de vloer van de laadbak, voor zijn voeten
SIT_M, zm = sit(mama, seat_top=0.85 - 0.0, lean=-4)
SIT_P, zpa = sit(papa, seat_top=0.85, lean=-4)
SIT_B, zb = sit(bro, seat_top=0.85, lean=4)
RIDERS = [(held, lambda t: V(TX(t), LANE, 0) + HERO_L, -90),
          (papa, lambda t: V(BX(t), LANE, 0) + V(0.3, 0.45, zpa), 90),
          (mama, lambda t: V(BX(t), LANE, 0) + V(0.3, -0.45, zm), 90),
          (bro, lambda t: V(BX(t), LANE, 0) + V(-0.75, 0.05, zb), 90)]
for ch, pos, rot in RIDERS:
    M = S._root_matrix(ch, DRIVE - 1 / FPS)
    key(ch.rig, DRIVE - 1 / FPS, loc=tuple(M.translation), rot=(0, 0, math.degrees(S._rot_now(ch, DRIVE - 1 / FPS))), interp="CONSTANT")
    key(ch.rig, DRIVE, rot=(0, 0, rot), interp="CONSTANT")
    bake(ch.rig, "location", fr, [tuple(pos((f - 1) / FPS)) for f in fr])
pfr = list(range(1, F(END) + 2))
bake(phone, "location", pfr, [tuple(V(TX((f - 1) / FPS), LANE, 0) + PHONE_L) if (f - 1) / FPS >= DRIVE else (0, 0, -50) for f in pfr])

# hij: zit, kijkt naar het busje, naar de telefoon, naar zijn handen, steekt zijn hand op naar mama
BUS_FACE = lambda t: V(BX(t) + 0.6, LANE - 0.3, 1.75)
S.beat(held, DRIVE, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.6, at=BUS_FACE(DRIVE + 1))
S.beat(held, FAMILY + 0.3, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=BUS_FACE(FAMILY))
S.beat(held, BRO + 0.4, **SIT_H, pose="ontspannen", face="blij", face_amt=0.35, at=BUS_FACE(BRO), mond_verdrietig=0.4)
S.beat(held, FRIEND + 0.3, **SIT_H, pose="ontspannen", face="blij", face_amt=0.3, at=V(TX(FRIEND), LANE, 0) + PHONE_L, body={"head": (10, 0, 0)})
S.beat(held, FRIEND + 2.6, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=V(TX(FRIEND + 2.6), LANE, 0) + PHONE_L)
S.beat(held, HANDS + 0.1, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.7, arms=LOOK_HANDS, look=(0, -0.6), body={"head": (18, 0, 0)})
S.beat(held, SKY + 1.0, **SIT_H, pose="ontspannen", face="nerveus", face_amt=0.6, arms=LOOK_HANDS, look=(0, -0.6), body={"head": (18, 0, 0)})
REACH_R = arm("R", (0.3, 0.85, 0.15), (0.15, 0.75, 0.62))
S.beat(held, MOM - 0.2, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.8, at=BUS_FACE(MOM))
S.beat(held, MOM + 0.8, **SIT_H, pose="ontspannen", face="verdrietig", face_amt=1.0, at=BUS_FACE(MOM + 0.8), arms=REACH_R, mond_verdrietig=0.7)
S.hold(held, END)

# het busje: papa rijdt, mama kijkt naar hem, het broertje zwaait, mama's hand omhoog
S.beat(papa, DRIVE, **SIT_P, pose="zitten_beugel", face="neutraal", face_amt=0.8, look=(0, 0))
S.beat(papa, FAMILY + 0.5, **SIT_P, pose="zitten_beugel", face="verdrietig", face_amt=0.5, look=(0, 0.1))
S.hold(papa, END)
S.beat(mama, DRIVE, **SIT_M, pose="ontspannen", face="verdrietig", face_amt=0.7, at=V(TX(DRIVE + 1), LANE, 2.1))
S.beat(mama, BRO + 0.5, **SIT_M, pose="ontspannen", face="blij", face_amt=0.3, at=V(TX(BRO), LANE, 2.1), mond_verdrietig=0.5)
S.beat(mama, MOM - 0.4, **SIT_M, pose="ontspannen", face="verdrietig", face_amt=0.8, at=V(TX(MOM), LANE, 2.1))
MOM_HAND = arm("L", (0.25, 0.85, 0.2), (0.05, 0.7, 0.7))
S.beat(mama, MOM + 0.5, **SIT_M, pose="ontspannen", face="verdrietig", face_amt=1.0, at=V(TX(MOM), LANE, 2.1), arms=MOM_HAND, mond_verdrietig=0.8)
S.hold(mama, END)
S.beat(bro, DRIVE, **SIT_B, pose="ontspannen", face="blij", face_amt=0.6, at=V(TX(DRIVE + 1), LANE, 2.1))
for k, t in enumerate(frange(BRO - 0.6, FRIEND + 1.0, 0.32)):
    S.beat(bro, t, **SIT_B, pose="zwaaien_a" if k % 2 == 0 else "zwaaien_b", face="lach", face_amt=0.8, at=V(TX(t), LANE, 2.1),
           body={"spine": (8, 0, 0)})
S.beat(bro, FRIEND + 1.5, **SIT_B, pose="ontspannen", face="blij", face_amt=0.5, at=V(TX(FRIEND), LANE, 2.1))
S.beat(bro, MOM, **SIT_B, pose="ontspannen", face="verdrietig", face_amt=0.4, at=V(TX(MOM), LANE, 2.1))
S.hold(bro, END)

# ---------------------------------------------------------------- camera
# 1 · de straat vol legertrucks, helikopter erboven
S.cam(0.0, ((-34, 0.5, 8.0), (2, 2.5, 1.8), 24), ((-31, 0.5, 7.5), (2, 2.5, 2.0), 26))
# 2 · de officier en hem bij de voordeur
HO = S.head(officer, l4[0])
S.cam(l4[0] - 0.2, ((-0.35, 11.4, 1.85), HO + V(0, 0, -0.1), 32), ((-0.4, 11.25, 1.85), HO + V(0, 0, -0.1), 34))
S.cam(SAFE2 - 0.2, S.shot(officer, SAFE2, "mcu", az=-20, lens=32), S.shot(officer, l4[1], "mcu", az=-18, lens=35))
# 3 · het konvooi de stad uit, van hoog en opzij
S.cam(DRIVE, None, fn=lambda t: (V(TX(t) + 18, 1.0, 8.0), V(TX(t) - 4, LANE, 1.5), 26))      # boven de weg, niet in de bomen
# 4 · vanuit de laadbak: hij, en het busje erachter
S.cam(FAMILY - 0.1, None, fn=lambda t: (V(TX(t) + 1.6, LANE + 0.9, 2.6), BUS_FACE(t) + V(0, 0, -0.3), 32))
# 5 · het broertje zwaait
S.cam(BRO - 0.1, None, fn=lambda t: (V(TX(t) - 3.6, LANE - 0.3, 2.0), V(BX(t) + 0.3, LANE + 0.0, 1.55), 42), handheld=0.6)
# 6 · de telefoon in de laadbak: hij hangt niet op
S.cam(FRIEND - 0.1, None, fn=lambda t: (V(TX(t), LANE, 0) + PHONE_L + V(0.45, 0.45, 0.7), V(TX(t), LANE, 0) + PHONE_L + V(0, 0, 0.02), 40))
S.cam(FRIEND + 2.5, None, fn=lambda t: (S.head(held, t) + V(-1.25, -0.6, -0.55), S.head(held, t) + V(0, 0, -0.35), 24))      # laag: hij kijkt omlaag
# 7 · zijn handen
S.cam(HANDS - 0.1, None, fn=lambda t: (S.head(held, t) + V(-1.5, 0.4, 0.0), S.head(held, t) + V(-0.1, 0, -0.5), 30))
# 8 · de stad die ze achterlaten
S.cam(SKY - 0.1, None, fn=lambda t: (V(TX(t) + 30, -7.5, 1.6), V(TX(t) - 60, -12, 22), 26))
# 9 · zijn hand omhoog, mama's hand omhoog: van opzij, allebei in beeld
S.cam(MOM - 0.3, None, fn=lambda t: (V((TX(t) + BX(t)) / 2 + 0.6, LANE - 1.5, 9.0), V((TX(t) + BX(t)) / 2 + 0.6, LANE, 1.6), 20))
S.cam(MOM + 1.7, None, fn=lambda t: (V(BX(t) + 3.2, LANE - 0.6, 1.8), V(BX(t) + 0.3, LANE - 0.45, 1.65), 40))

S.finish(length=END)
