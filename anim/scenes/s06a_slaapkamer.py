"""S06a · Dag 4 · slaapkamer, nacht: duim door het scherm, de telefoon, het bureau. Daarna de eieren.

    blender -b -P anim/scenes/s06a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s06a", "slaapkamer", "nacht")

# Het bureau staat voor deze scène midden in de kamer: hij zit erachter en kijkt naar ons (-y).
DESK_C = V(0.4, -0.25, 0)
SEAT = V(0.4, 0.45, 0)
PH = V(0.4, 0.1, 0.99)                     # telefoon in zijn handen
HIT = V(0.56, -0.02, 0.75)                  # waar zijn vuist door het blad gaat
BOWL = V(0.26, -0.02, 0.75)                 # later: kom op het bureau
EGG = V(0.27, 0.06, 1.04)

pivot = bpy.data.objects.new("Bureau_verplaatst", None)
T._link(pivot)
pivot.location = (1.76, 0.25, 0)
for o in list(bpy.data.objects):
    if o.parent is None and o.type == "MESH" and (o.name.startswith(("Bureau", "Laptop", "Schoolboek", "Pennenbak"))
                                                  and not o.name.startswith("Bureaustoel")):
        o.parent = pivot
        o.matrix_parent_inverse = Matrix.Translation(pivot.location).inverted()
pivot.location = DESK_C
pivot.rotation_euler.z = math.radians(-90)
chair = S.obj("Bureaustoel")
chair.location = (SEAT.x, SEAT.y, 0)
chair.rotation_euler.z = 0                  # rugleuning achter hem
for n in ("Telefoon", "Telefoon_scherm", "Sneaker_links", "Schoolboeken_stapel"):
    S.obj(n).hide_render = True
glow = S.obj("Telefoon_gloed")

held = S.actor("hoofdpersonage", SEAT, 0, energy=1.2)
SIT_D, zd = sit(held, seat_top=0.53, lean=6)
SIT_B, zb = sit(held, seat_top=0.53, lean=8, spread=0.25)
S.place(held, 0, (SEAT.x, SEAT.y, zd), 0)

# ---------------------------------------------------------------- rekwisieten
phone = prop_phone(S, "Zijn_telefoon", PH, screen=(0.45, 0.7, 1.0))
phone.rotation_euler = (math.radians(-50), 0, math.radians(180))
PSC = 1.7                                   # op maat van de grote figuurhanden
bubble = T.box("Chat_ballon", (0.008, -0.006, 0.03), (0.042, 0.001, 0.024), S.mat("chat_blauw", (0.2, 0.55, 1.0), 2.5), base=False, bevel=0.004, ol=0)
bubble.parent = phone
lol = T.text("Chat_lol", "lol", (0.008, -0.0075, 0.024), 0.018, S.mat("chat_tekst", (1, 1, 1), 3.0), rot=(90, 0, 0), extrude=0.0)
lol.parent = phone
crack = T.tube("Scherm_barst", [(-0.02, -0.0062, 0.05), (0.0, -0.0062, 0.02), (-0.012, -0.0062, -0.01), (0.015, -0.0062, -0.04),
                                (0.006, -0.0062, -0.06)], 0.0012, S.mat("barst_wit", (0.9, 0.95, 1.0), 1.0))
crack.parent = phone
crack2 = T.tube("Scherm_barst2", [(0.0, -0.0062, 0.02), (0.025, -0.0062, 0.035), (0.03, -0.0062, 0.06)], 0.001, S.mat("barst_wit", (0.9, 0.95, 1.0), 1.0))
crack2.parent = phone
# twee helften voor als hij doorbreekt
blk = S.mat("telefoon", (0.1, 0.1, 0.12))
halves = []
for k, dz in enumerate((0.063, -0.063)):
    h = T.box(f"Telefoon_helft{k}", (0, 0, 0), (0.07 * 1.7, 0.008 * 1.7, 0.07 * 1.7), blk, base=False, bevel=0.004, ol=0.003)
    s = T.box(f"Telefoon_helft{k}_scherm", (0, -0.0078, 0), (0.105, 0.001, 0.11), S.mat("scherm_kapot", (0.12, 0.2, 0.35), 0.6), base=False, bevel=0, ol=0)
    s.parent = h
    halves.append((h, dz))
# gat in het bureaublad
hole = T.cyl("Gat_bureau", tuple(HIT + V(0, 0, 0.002)), 0.11, 0.006, S.mat("gat_zwart", (0.03, 0.025, 0.02)), seg=10, ol=0.004)
hole.scale = (1.0, 0.8, 1.0)
spl = S.mat("splinter_licht", (0.85, 0.8, 0.7))
for k in range(7):
    a = k * 0.9
    o = T.box(f"Bureau_splinter{k}", tuple(HIT + V(0.12 * math.cos(a), 0.1 * math.sin(a), 0.004)), (0.08, 0.018, 0.01), spl,
              rot=(0, 15 * (k % 3 - 1), math.degrees(a)), base=False, bevel=0, ol=0.003)
for o in [S.obj("Laptop")] + list(S.obj("Laptop").children_recursive):
    o.hide_render = True
# laptop: zat steeds in beeld; hij zit op zijn telefoon

# eieren: doos op het bed, kom op de vloer
egg_mat = S.mat("ei", (0.98, 0.93, 0.85))
yolk_mat = S.mat("eigeel", (1.0, 0.72, 0.1))
white_mat = S.mat("eiwit", (1.0, 1.0, 0.95))
bowl = T.cyl("Kom", tuple(BOWL), 0.15, 0.09, S.mat("kom_blauw", (0.25, 0.5, 0.85)), r2=0.09, seg=24, ol=0.005, cap=False)
bowl_in = T.cyl("Kom_binnen", tuple(BOWL + V(0, 0, 0.004)), 0.088, 0.004, S.mat("kom_binnen", (0.9, 0.9, 0.92)), seg=24, ol=0)
goo = T.cyl("Kom_eigeel", tuple(BOWL + V(0, 0, 0.01)), 0.1, 0.01, yolk_mat, seg=24, ol=0.002)
carton = T.box("Eierdoos", (-1.18, 0.95, 0.66), (0.16, 0.3, 0.07), S.mat("eierdoos", (0.75, 0.68, 0.55)), bevel=0.01, ol=0.004)
for k in range(4):
    prop_egg(S, f"Ei_doos{k}", (-1.18 + (k % 2 - 0.5) * 0.07, 0.86 + (k // 2) * 0.09, 0.75))
egg = prop_egg(S, "Ei_training", EGG)
for o in list(bpy.data.objects):
    if o.name.startswith(("Kom", "Eierdoos", "Ei_")):
        visible(o, 0.0, False)

# ---------------------------------------------------------------- tijdlijn
S.hud(4, "16x STRONGER", t0=0.4)
S.music("piano_zacht", 0.0, 0.0, vol=0.26, fade_in=1.0)      # t1 wordt hieronder gezet
PIANO = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.05)
l1 = S.say("S06-01", gap=0.7)
l2 = S.say("S06-02", gap=0.5)
LOL = l2[0] + 1.55
SCREEN = l2[0] + 3.55
PHONE = l2[0] + 4.85
DESK = l2[0] + 6.3
S.sfx("sfx_hud_tik", LOL - 0.05, 0.4)
S.sfx("sfx_telefoon_bureau", SCREEN - 0.2, 0.9, cut=(0.8, 1.25))
S.sfx("sfx_telefoon_bureau", PHONE - 0.2, 0.9, cut=(2.2, 2.6))
S.sfx("sfx_telefoon_bureau", DESK - 0.15, 1.0, cut=(2.65, None))
S.sfx("sfx_mok_breekt", DESK + 0.35, 0.35, cut=(1.3, None))       # splinters op de vloer
S.wait(0.9)
BED = S.t                                     # snede: andere avond, op de rand van het bed
l3 = S.say("S06-03", gap=0.3)
HOLD = l3[0] + 3.0                            # 'Hold it.'
CRACK = l3[1] + 0.2
S.sfx("sfx_ei_krak", CRACK - 0.2, 1.0)
l4 = S.say("S06-04", gap=0.35)
COUNT = [CRACK] + [l4[0] + 0.12 + k * 0.1 for k in range(10)]
for k, tc in enumerate(COUNT[1:]):
    S.sfx("sfx_ei_krak", tc - 0.2, 0.25 + 0.03 * (k % 3))
S.wait(1.1)
END = S.t
PIANO["loop_to"] = BED + 0.4                                    # piano tot de snede
PIANO["fade_out"] = 0.6
S.music("pizz_spanning", BED - 0.1, END + 0.2, vol=0.28, fade_in=0.3, fade_out=0.6)

# EGGS BROKEN teller onder de HUD
for k, tc in enumerate(COUNT):
    S.gauge(f"EGGS BROKEN: {k + 1}", tc, COUNT[k + 1] if k + 1 < len(COUNT) else None, color=WHITE if k < 10 else GOLD)

# ---------------------------------------------------------------- de telefoon
PL = PH + V(0.085, 0.04, -0.04)             # hij kijkt naar -y: zijn links is +x
PR = PH + V(-0.085, 0.04, -0.04)
S.beat(held, 0.0, **SIT_D, pose="ontspannen", face="blij", face_amt=0.45, at=PH, body={"chest": (8, 0, 0)})
S.reach(held, 0.0, "L", PL)
S.reach(held, 0.0, "R", PR)
# tikken: rechterduim op en neer
t = 0.6
while t < LOL:
    S.reach(held, t, "R", PR + V(0.012, -0.01, 0.012))
    S.reach(held, t + 0.15, "R", PR)
    t += 0.42 if int(t * 2) % 3 else 0.9
S.beat(held, l1[0] + 2.2, **SIT_D, pose="ontspannen", face="grijns", face_amt=0.5, at=PH, body={"chest": (8, 0, 0)})
S.beat(held, LOL - 0.4, **SIT_D, pose="ontspannen", face="blij", face_amt=0.7, at=PH, body={"chest": (10, 0, 0)})
S.reach(held, LOL - 0.15, "R", PR + V(0.0, 0.0, 0.0))
S.reach(held, LOL, "R", PR + V(0.014, -0.012, 0.01))          # 'lol' versturen
S.reach(held, LOL + 0.2, "R", PR)
show(bubble, LOL)
show(lol, LOL)
S.hold(held, SCREEN - 0.3)
S.reach(held, SCREEN - 0.3, "R", PR + V(-0.01, 0.0, 0.015))
S.reach(held, SCREEN, "R", PR + V(0.04, -0.04, -0.005))     # de duim gaat erdoor
show(crack, SCREEN)
show(crack2, SCREEN)
S.debris(PH + V(0, -0.02, 0), SCREEN, n=8, size=(0.003, 0.009), color=(0.15, 0.15, 0.18), speed=(0.4, 1.0), up=0.5, floor=0.76, life=1.0, name="Telefoon_achterkant")
S.text('YOU: "lol"', LOL, SCREEN, loc=(0.5, 0.2), size=58, color=CYAN, anchor=("CENTER", "BOTTOM"))
S.beat(held, SCREEN + 0.08, **SIT_D, pose="ontspannen", face="geschrokken", face_amt=0.9, at=PH, body={"chest": (2, 0, 0)})
S.beat(held, SCREEN + 0.8, **SIT_D, pose="ontspannen", face="nerveus", face_amt=0.8, at=PH, body={"chest": (6, 0, 0)})
S.reach(held, PHONE - 0.35, "L", PL)
S.reach(held, PHONE - 0.35, "R", PR + V(0.04, -0.04, -0.005))
# voorzichtig vastpakken... en krak, in twee stukken
S.reach(held, PHONE, "L", PL + V(0.035, 0.0, 0.01))
S.reach(held, PHONE, "R", PR + V(-0.035, 0.0, 0.01))
S.beat(held, PHONE + 0.05, **SIT_D, pose="ontspannen", face="geschrokken", at=PH, body={"chest": (0, 0, 0), "head": (-6, 0, 0)})
phone.scale = (PSC,) * 3
key(phone, PHONE - 0.02, scale=PSC)
key(phone, PHONE, scale=0.001)
key(phone, 0, scale=PSC)
for fc in A._fcurves(phone):
    if fc.data_path == "scale":
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"
for k, (h, dz) in enumerate(halves):
    side = 1 if k == 0 else -1
    p0 = PH + V(0, 0, dz * 0.8)
    p1 = PH + V(0.06 * side, -0.06, dz * 0.8 - 0.03)
    land = V(0.4 + 0.12 * side, -0.02 - 0.05 * k, 0.758)
    key(h, 0, loc=(0, 0, -5), interp="CONSTANT")
    key(h, PHONE - 1 / FPS, loc=(0, 0, -5), interp="CONSTANT")
    key(h, PHONE, loc=p0, rot=(-50, 0, 180))
    key(h, PHONE + 0.2, loc=p1, rot=(-50 + 50 * side, 20 * side, 180 + 30 * side))
    key(h, PHONE + 0.45, loc=land, rot=(-90 + 3 * side, 0, 180 + 60 * side))
S.debris(PH, PHONE, n=12, size=(0.004, 0.012), color=(0.6, 0.8, 1.0), speed=(0.6, 1.6), up=0.8, floor=0.76, life=1.0, name="Scherm_splinter")
glow.location = PH + V(0.0, 0.1, 0.1)
glow.data.energy = 6
glow.data.keyframe_insert("energy", frame=1)
glow.data.keyframe_insert("energy", frame=F(PHONE) - 1)
glow.data.energy = 0.0
glow.data.keyframe_insert("energy", frame=F(PHONE))
# hij legt de handen neer... en de vuist gaat door het blad
S.reach(held, PHONE + 0.6, "L", V(0.6, 0.05, 0.78))
S.reach(held, PHONE + 0.6, "R", V(0.2, 0.05, 0.8))
S.beat(held, PHONE + 0.7, **SIT_D, pose="ontspannen", face="verbaasd", face_amt=0.8, at=V(0.4, -0.05, 0.76), body={"chest": (6, 0, 0)})
S.beat(held, DESK - 0.4, **SIT_D, pose="ontspannen", face="boos", face_amt=0.5, at=V(0.4, -0.05, 0.76), body={"chest": (4, 0, 0)})
S.reach(held, DESK - 0.4, "R", HIT + V(-0.05, 0.12, 0.25))      # gefrustreerd tikje op het bureau
S.reach(held, DESK, "R", HIT + V(-0.02, 0, -0.06))
S.beat(held, DESK + 0.05, **SIT_D, pose="ontspannen", face="geschrokken", at=HIT, body={"chest": (14, 0, 0)})
S.reach(held, DESK + 0.6, "R", HIT + V(-0.03, 0, -0.04))
S.beat(held, DESK + 0.6, **SIT_D, pose="ontspannen", face="nerveus", face_amt=0.9, at=HIT + V(0, -0.6, 0.45), body={"chest": (2, 0, 0)})
show(hole, DESK)
for o in bpy.data.objects:
    if o.name.startswith("Bureau_splinter"):
        show(o, DESK)
S.debris(HIT + V(0, 0, 0.02), DESK, n=16, size=(0.015, 0.05), color=(0.88, 0.85, 0.78), speed=(1.0, 2.6), up=1.0, floor=0.0, life=1.6, name="Bureau_brok")
S.puff(HIT + V(0, 0, 0.03), DESK, n=5, r=(0.03, 0.06), grow=1.8, dur=0.8, rise=0.15, spread=0.12)

# ---------------------------------------------------------------- eieren: een andere avond, zelfde bureau (met gat)
S.hold(held, BED - 1 / FPS)
S.teleport(held, BED, (SEAT.x, SEAT.y, zb), 0)
for o in list(bpy.data.objects):
    if o.name.startswith(("Kom", "Eierdoos", "Ei_")):
        visible(o, BED, True)
S.reach(held, BED, "L", None, 0.0)
S.reach(held, BED, "R", None, 0.0)
EH = EGG + V(0.0, 0.075, -0.02)                             # pols, ei in de vingertoppen
S.beat(held, BED, **SIT_B, pose="ontspannen", face="vastberaden", face_amt=0.6, at=EGG, body={"chest": (12, 0, 0)})
S.reach(held, BED + 0.01, "R", EH)
S.reach(held, BED + 0.01, "L", V(0.62, 0.05, 0.79))        # op het bureau
grab(S, egg, held, BED, "hand.R", (0, 0.03, 0.0), mode="loc", release=CRACK)
# trillen van de concentratie
t = BED + 0.4
k = 0
while t < CRACK - 0.1:
    a = 0.004 if t < HOLD else 0.008
    S.reach(held, t, "R", EH + V(a * ((k % 3) - 1), a * ((k * 7 % 3) - 1), a * ((k % 2) * 2 - 1)))
    t += 0.12
    k += 1
S.beat(held, l3[0] + 1.6, **SIT_B, pose="ontspannen", face="inspanning", face_amt=0.4, at=EGG, body={"chest": (14, 0, 0)})
S.beat(held, HOLD, **SIT_B, pose="ontspannen", face="inspanning", face_amt=0.8, at=EGG, body={"chest": (16, 0, 0)}, ogen_knijp=0.4)
S.hold(held, CRACK - 0.05)
S.reach(held, CRACK, "R", EH + V(0.0, 0, -0.04))
S.beat(held, CRACK + 0.04, **SIT_B, pose="ontspannen", face="geschrokken", face_amt=0.9, at=BOWL, body={"chest": (10, 0, 0)})
S.beat(held, CRACK + 0.7, **SIT_B, pose="ontspannen", face="verdrietig", face_amt=0.6, at=BOWL + V(0, 0, 0.1), body={"chest": (14, 0, 0)})
key(egg, CRACK - 0.02, scale=(1, 1, 1))
key(egg, CRACK, scale=(0.001, 0.001, 0.001))
# eigeel en schaal vallen in de kom
y0 = T.sphere("Eigeel_val", tuple(EGG), 0.016, yolk_mat, seg=10, ol=0.002)
key(y0, CRACK - 1 / FPS, loc=EGG, scale=0.001)
key(y0, CRACK, loc=EGG, scale=1.0)
key(y0, CRACK + 0.35, loc=BOWL + V(0, 0, 0.03), scale=(1.4, 1.4, 0.5))
key(y0, l4[1] + 2, loc=BOWL + V(0, 0, 0.03), scale=(1.4, 1.4, 0.5))
S.debris(EGG, CRACK, n=6, size=(0.008, 0.018), color=(0.98, 0.93, 0.85), speed=(0.3, 0.9), up=0.6, floor=0.76, life=2.5, name="Eierschaal")
S.debris(EGG, CRACK, n=6, size=(0.006, 0.012), color=(1.0, 1.0, 0.95), speed=(0.2, 0.6), up=0.3, floor=0.76, life=2.5, shape="sphere", name="Eiwit")
# de kom raakt voller: schalen en eigeel bij elke tik
key(goo, CRACK - 0.02, scale=(0.3, 0.3, 1.0))
key(goo, COUNT[-1] + 0.1, scale=(1.0, 1.0, 3.5))
for k in range(10):
    a = k * 2.3
    sh = T.sphere(f"Schaal_kom{k}", tuple(BOWL + V(0.06 * math.cos(a), 0.06 * math.sin(a), 0.05 + 0.004 * k)), 0.022, egg_mat,
                  scale=(1, 1, 0.45), rot=(30 * math.cos(a), 30 * math.sin(a), 0), seg=10, ol=0.002)
    show(sh, COUNT[k + 1])
    yk = T.sphere(f"Eigeel_kom{k}", tuple(BOWL + V(0.035 * math.cos(a + 1), 0.035 * math.sin(a + 1), 0.045 + 0.003 * k)), 0.016,
                  yolk_mat, scale=(1.2, 1.2, 0.5), seg=10, ol=0.002)
    show(yk, COUNT[k + 1])
# eigeel aan zijn vingers
drip = T.sphere("Eigeel_vinger", (0, 0, 0), 0.012, yolk_mat, scale=(1, 1, 1.6), seg=8, ol=0.002)
grab(S, drip, held, CRACK, "hand.R", (0, 0.035, -0.01), mode="loc")
show(drip, CRACK)
S.reach(held, l4[0] + 1.4, "R", V(0.22, 0.12, 1.05))      # bekijkt zijn plakkerige hand
S.beat(held, l4[0] + 1.4, **SIT_B, pose="ontspannen", face="twijfel", face_amt=0.8, at=V(0.22, 0.12, 1.05), body={"chest": (4, 0, 0)})
S.beat(held, l4[0] + 2.6, **SIT_B, pose="ontspannen", face="nerveus", face_amt=0.7, look=(0, 0.2), body={"chest": (2, 0, 0), "head": (0, 0, 6)})
S.hold(held, END)
# leeslamp aan op het nachtkastje
lamp = T.point_light("Leeslamp_licht", (0.0, 0.5, 1.6), color=(1.0, 0.75, 0.4), energy=0, radius=0.15)
lamp.data.keyframe_insert("energy", frame=1)
lamp.data.keyframe_insert("energy", frame=F(BED) - 1)
lamp.data.energy = 40
lamp.data.keyframe_insert("energy", frame=F(BED))
fill = T.point_light("Vul_bed", (0.4, -0.6, 1.6), color=(0.55, 0.6, 1.0), energy=0, radius=0.3)
fill.data.keyframe_insert("energy", frame=1)
fill.data.keyframe_insert("energy", frame=F(BED) - 1)
fill.data.energy = 25
fill.data.keyframe_insert("energy", frame=F(BED))
desk_fill = T.point_light("Vul_bureau", (0.9, -1.0, 1.6), color=(0.5, 0.6, 1.0), energy=25, radius=0.3)

# ---------------------------------------------------------------- camera
S.sc.frame_set(F(HOLD + 0.3))
EGG_AT = egg.matrix_world.translation.copy()
print("EGG_AT", EGG_AT, "hand", S.bone_world(held, "hand.R", HOLD + 0.3))
S.cam(0.0, ((1.4, -1.65, 1.5), (0.4, 0.3, 1.0), 24), ((1.25, -1.5, 1.48), (0.4, 0.3, 1.02), 26))
S.cam(l1[0] + 2.8, S.shot(held, l1[0] + 3, "mcu", az=14, lens=30, h=0.05), S.shot(held, l2[0], "mcu", az=10, lens=34, h=0.05))
S.cam(l2[0] + 1.0, ((0.66, -0.62, 0.95), PH + V(0, 0, 0.1), 30), ((0.63, -0.58, 0.95), PH + V(0, 0, 0.1), 34))
S.cam(SCREEN + 0.55, ((0.1, -0.8, 1.15), PH + V(0.0, 0.05, 0.18), 30), ((0.12, -0.75, 1.14), PH + V(0.0, 0.05, 0.18), 32),
      shake=lambda t: max(0.0, 0.8 - (t - PHONE) * 3) if t > PHONE else 0.0)
S.cam(DESK - 0.45, ((0.95, -0.95, 1.5), HIT + V(-0.12, 0.2, 0.22), 26), ((0.92, -0.9, 1.48), HIT + V(-0.12, 0.2, 0.22), 28),
      shake=lambda t: max(0.0, 1.4 - (t - DESK) * 3) if t > DESK else 0.0)
S.cam(DESK + 1.0, S.shot(held, DESK + 1.2, "cu", az=12, lens=30, h=-0.3), S.shot(held, BED - 0.1, "cu", az=8, lens=34, h=-0.3))
# eieren
S.cam(BED, ((-0.95, -0.85, 1.35), (0.35, 0.25, 0.95), 26), ((-0.85, -0.8, 1.33), (0.35, 0.25, 0.95), 28))
S.cam(HOLD - 0.3, (EGG_AT + V(-0.15, -0.4, 0.1), EGG_AT, 45), (EGG_AT + V(-0.13, -0.36, 0.1), EGG_AT, 52), dof=0.45)
S.cam(CRACK + 0.6, ((0.05, -0.35, 1.12), BOWL + V(0, 0, 0.05), 32), ((0.07, -0.32, 1.1), BOWL + V(0, 0, 0.05), 38))
S.cam(l4[0] + 1.3, S.shot(held, l4[0] + 2.0, "mcu", az=-16, lens=32, h=0.05), S.shot(held, END, "mcu", az=-12, lens=36, h=0.05))

S.finish(length=END)
