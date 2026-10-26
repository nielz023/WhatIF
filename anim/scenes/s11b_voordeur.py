"""S11b · Dag 10 · voordeur, avond: mama struikelt over de stoep, hij vangt haar op, en laat te snel los.

    blender -b -P anim/scenes/s11b_voordeur.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s11b", "straat", "avond")

DX = -1.4                                      # voordeur
STEP2 = V(DX, 12.62, 0.30)                     # bovenste tree, vlak voor de deur
CATCH_AT = V(DX, 12.33, 0.15)                  # hij stapt een tree naar beneden
FOOT = V(DX + 0.55, 11.62, 0.0)                # waar haar voet blijft haken
MOM0 = V(DX + 0.45, 8.6, 0.0)
TILT = 30.0

held = S.actor("hoofdpersonage", STEP2, 0)
mama = S.actor("mama", MOM0, 180, energy=1.0)
S.place(held, 0, STEP2, 0)

# de tassen en appels van de set liggen er al: die laten we pas vallen
bags = [S.obj("Boodschappentas_1"), S.obj("Boodschappentas_2")]
apples = S.obj("Appels")

# ---------------------------------------------------------------- tijdlijn
S.hud(10, "1,024x STRONGER", t0=0.0, tick=False)
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.1)
AMB = S.sounds[-1]
S.music("piano_warm", 0.0, 60, vol=0.24, fade_in=0.5, fade_out=0.15, start=30.0)
PIANO = S.sounds[-1]
l8 = S.say("S11-08", gap=0.5)
TRIP = l8[0] + 0.95                            # 'trips on the front step'
REL = TRIP + 0.25                              # tassen los
LAND = TRIP + 2.7                              # tassen op de grond (slow motion)
CATCH = l8[0] + 4.95                           # 'You catch her.'
AMB["loop_to"] = TRIP + 0.4
PIANO["loop_to"] = TRIP + 0.3
S.sfx("sfx_struikelen", TRIP - 0.05, 0.7)
S.sfx("sfx_slowmo", TRIP + 0.15, 0.6)
S.music("strijk_noot", TRIP + 0.2, 0.0, vol=0.26, fade_in=0.6, fade_out=0.4)
STRING = S.sounds[-1]
S.t = l8[0] + 5.7                              # de stilte na 'You catch her' niet afwachten
l9 = S.say("S11-09", gap=0.0)
l10 = S.say("S11-10", gap=0.9)
STRING["loop_to"] = l10[0] + 0.2
RELEASE = l10[0] + 0.55                        # 'You let go so fast...'
S.ambience("sfx_straat_sfeer", RELEASE, 60, vol=0.1)
S.music("mok_thema", l10[1] + 0.2, 60, vol=0.2, fade_in=1.0, fade_out=1.2)
THEME = S.sounds[-1]
l11 = S.say("S11-11", who=mama, gap=0.5, gain=1.15)
l12 = S.say("S11-12", gap=0.5)
NIGHT = l12[1] + 0.6
l13 = S.say("S11-13", gap=1.0)
ZERO = l13[0] + 0.1
DOUBT = l13[0] + 7.3
S.wait(1.4)
END = S.t
THEME["loop_to"] = END + 0.2

S.gauge("EGGS BROKEN: 0", ZERO, l13[0] + 6.0, color=GOLD)
S.sfx("sfx_hud_tik", ZERO, 0.4)

# ---------------------------------------------------------------- mama komt aan met de boodschappen
HOLD_BAG_L = arm("L", (0.12, 0.05, -1.0), (0.05, 0.12, -1.0))
HOLD_BAG_R = arm("R", (0.12, 0.05, -1.0), (0.05, 0.12, -1.0))
S.beat(mama, 0.0, "staan", face="blij", face_amt=0.6, at=S.head(held, 0), arms=arms(HOLD_BAG_L, HOLD_BAG_R))
S.walk(mama, 0.1, TRIP, [MOM0, V(DX + 0.5, 10.4, 0), FOOT], arms=0.0)
S.beat(mama, TRIP - 0.6, "staan", face="blij", face_amt=0.8, at=S.head(held, 0), arms=arms(HOLD_BAG_L, HOLD_BAG_R))
grips = [grab(S, b, mama, 0.0, "hand." + s, loc=(0, 0.02, -0.12), mode="loc", release=REL) for b, s in zip(bags, "LR")]
rz = math.degrees(S._rot_now(mama, TRIP))
# de val: om haar voet naar voren kantelen, heel langzaam (slow motion)
key(mama.rig, TRIP, loc=FOOT, rot=(0, 0, rz))
key(mama.rig, TRIP + 0.6, loc=FOOT + V(0, 0.04, 0), rot=(8, 0, rz))
key(mama.rig, CATCH - 0.3, loc=FOOT + V(0, 0.1, 0), rot=(TILT - 2, 0, rz))
key(mama.rig, CATCH, loc=FOOT + V(0, 0.1, 0), rot=(TILT, 0, rz))
S.beat(mama, TRIP + 0.05, "schrik", face="geschrokken", face_amt=1.0, look=(0, -0.3))
S.beat(mama, TRIP + 1.4, "armen_omhoog", amount=0.5, face="bang", face_amt=1.0, look=(0, -0.2))
S.beat(mama, CATCH, "staan", face="bang", face_amt=0.8, ogen_knijp=0.8,
       arms=arms(arm("L", (0.3, 0.6, -0.4), (0.1, 0.8, 0.2)), arm("R", (0.3, 0.6, -0.4), (0.1, 0.8, 0.2))))
S.hold(mama, RELEASE)

# ---------------------------------------------------------------- hij vangt haar
S.beat(held, 0.0, "staan", face="blij", face_amt=0.5, at=S.head(mama, 0))
S.beat(held, TRIP - 0.5, "staan", face="blij", face_amt=0.6, at=FOOT + V(0, 0, 1.4))
S.beat(held, TRIP + 0.15, "schrik", amount=0.5, face="geschrokken", face_amt=1.0, at=FOOT + V(0, 0.3, 1.2))
S.place(held, TRIP + 0.3, STEP2, 0)
S.place(held, CATCH - 0.5, CATCH_AT, 0)
HL = FOOT + V(0.12, 0.42, 1.12)                # zijn handen op haar schouders en rug
HR = FOOT + V(-0.32, 0.36, 1.0)
S.beat(held, CATCH - 0.6, "staan", face="vastberaden", face_amt=1.0, at=S.head(mama, CATCH), crouch=(0.08, 12))
S.reach(held, CATCH - 0.6, "L", HL + V(0.05, -0.2, 0.1))
S.reach(held, CATCH - 0.6, "R", HR + V(-0.05, -0.2, 0.1))
S.reach(held, CATCH, "L", HL)
S.reach(held, CATCH, "R", HR)
S.sfx("sfx_dreun", CATCH - 0.05, 0.12)
# 'And for half a second, you feel how easy it would be.' (de armen sluiten, hij kijkt naar zijn handen)
S.beat(held, l9[0] + 0.3, "staan", face="neutraal", face_amt=0.5, at=HL, crouch=(0.08, 12))
S.reach(held, l9[0] + 1.6, "L", HL + V(-0.08, 0.04, 0.0))
S.reach(held, l9[0] + 1.6, "R", HR + V(0.06, 0.06, 0.0))
S.beat(held, l9[1] - 0.6, "staan", face="bang", face_amt=0.7, at=HL, crouch=(0.08, 12), ogen_knijp=0.0)
S.hold(held, RELEASE - 0.05)
# ...en laat te snel los: handen weg, stap terug
S.reach(held, RELEASE, "L", None, 0.0)
S.reach(held, RELEASE, "R", None, 0.0)
S.beat(held, RELEASE, "schrik", face="bang", face_amt=1.0, at=S.head(mama, RELEASE))
S.place(held, RELEASE, CATCH_AT, 0)
S.place(held, RELEASE + 0.35, STEP2, 0)
S.beat(held, RELEASE + 0.9, "handen_hoofd", amount=0.4, face="bang", face_amt=0.8, at=S.head(mama, RELEASE))

# mama valt bijna alsnog, vangt zichzelf op
key(mama.rig, RELEASE + 0.25, loc=FOOT + V(0, 0.12, 0), rot=(TILT + 6, 0, rz))
key(mama.rig, RELEASE + 0.6, loc=FOOT + V(0, 0.36, 0), rot=(12, 0, rz))
key(mama.rig, RELEASE + 1.0, loc=FOOT + V(0, 0.42, 0), rot=(-4, 0, rz))
MOM_UP = FOOT + V(0, 0.4, 0)
S.place(mama, RELEASE + 1.3, MOM_UP, rz)
S.beat(mama, RELEASE + 0.1, "armen_omhoog", amount=0.7, face="geschrokken", face_amt=1.0, look=(0, -0.4))
S.beat(mama, RELEASE + 0.7, "schrik", amount=0.6, face="verbaasd", face_amt=0.8, at=S.head(held, RELEASE))
S.turn(mama, RELEASE + 1.4, RELEASE + 1.9, heading(MOM_UP, STEP2), MOM_UP)
S.beat(mama, RELEASE + 1.9, "staan", face="verbaasd", face_amt=0.7, at=S.head(held, l11[0]))
# 'Hey... hey. You didn't hurt me.'
S.beat(mama, l11[0] + 0.2, "staan", face="blij", face_amt=0.5, at=S.head(held, l11[0]), wenkbrauw_op=0.6)
S.reach(mama, l11[0] + 0.5, "R", S.head(held, l11[0]) + V(-0.25, -0.15, -0.45))
S.beat(mama, l11[0] + 1.8, "staan", face="blij", face_amt=0.8, at=S.head(held, l11[0]), body={"head": (0, 0, 8)})
S.beat(mama, l12[0] + 0.4, "staan", face="verdrietig", face_amt=0.5, at=S.head(held, l12[0]))
S.reach(mama, l12[0] + 1.0, "R", None, 0.0)
S.hold(mama, NIGHT - 1 / FPS)
S.teleport(mama, NIGHT, (40, 40, 0))

# hij: kijkt naar zijn handen, bang om haar vast te houden
S.beat(held, l11[0] + 0.3, "staan", face="verdrietig", face_amt=0.6, at=S.head(mama, l11[0]))
S.beat(held, l11[0] + 2.2, "staan", face="verdrietig", face_amt=0.8, at=S.head(mama, l11[0]), body={"head": (6, 0, 0)})
S.beat(held, l12[0] + 0.2, "staan", face="verdrietig", face_amt=0.9, arms=LOOK_HANDS, look=(0, -0.5), body={"head": (18, 0, 0)})
S.beat(held, l12[0] + 1.8, "staan", face="bang", face_amt=0.7, arms=LOOK_HANDS, look=(0, -0.5), body={"head": (18, 0, 0)})
S.hold(held, NIGHT - 1 / FPS)

# 's avonds laat: alleen op de stoep
SIT, _ = sit(held, seat_top=0.15, lean=8)
S.teleport(held, NIGHT, STEP2 + V(0, 0, -0.15), 0)
S.beat(held, NIGHT, **SIT, pose="ontspannen", face="neutraal", face_amt=0.5, arms=LOOK_HANDS, look=(0, -0.5), body={"head": (14, 0, 0)})
S.beat(held, ZERO + 1.0, **SIT, pose="ontspannen", face="blij", face_amt=0.4, arms=LOOK_HANDS, look=(0, -0.5), body={"head": (14, 0, 0)})
S.beat(held, DOUBT - 0.3, **SIT, pose="ontspannen", face="twijfel", face_amt=0.7, look=(0.2, 0.4), body={"head": (-10, 0, 0)})
S.beat(held, DOUBT + 1.8, **SIT, pose="ontspannen", face="nerveus", face_amt=0.7, look=(0, 0.5), body={"head": (-14, 0, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- tassen vallen, appels rollen (slow motion)
bpy.context.scene.frame_set(F(REL))
bpy.context.view_layer.update()
rel_pos = [g.matrix_world.translation.copy() + V(0, 0.02, -0.12) for g in grips]
for b, p in zip(bags, rel_pos):
    end_loc, end_rot = b.location.copy(), b.rotation_euler.copy()
    key(b, 0, loc=p, rot=(0, 0, 0))
    key(b, REL, loc=p, rot=(0, 0, 0))
    mid = p.lerp(end_loc, 0.5) + V(0, 0.15, 0.35)
    key(b, (REL + LAND) / 2, loc=mid, rot=tuple(math.degrees(a) * 0.5 for a in end_rot))
    key(b, LAND, loc=end_loc, rot=tuple(math.degrees(a) for a in end_rot))
show(apples, LAND + 0.4)
rnd = random.Random(10)
red = S.mat("appel_rood_los", (0.85, 0.1, 0.08))
for k in range(6):
    a = T.sphere(f"Appel_los_{k}", (0, 0, 0), 0.045, red, seg=12, ol=0.002)
    src = rel_pos[k % 2]
    dst = V(DX + rnd.uniform(-0.9, 1.1), rnd.uniform(9.6, 11.6), 0.045)
    key(a, 0, loc=src)
    key(a, REL + 0.1, loc=src)
    key(a, REL + 0.9, loc=src.lerp(dst, 0.4) + V(0, 0, 0.45))
    key(a, LAND, loc=src.lerp(dst, 0.75) + V(0, 0, 0.0))
    key(a, LAND + 0.5, loc=src.lerp(dst, 0.85) + V(0, 0, 0.12))
    key(a, LAND + 2.4, loc=dst)
    show(a, REL + 0.1)
S.sfx("sfx_vloer_kraak", LAND - 0.05, 0.2)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((1.2, 7.6, 1.5), (-1.1, 12.4, 1.1), 26), ((1.0, 8.2, 1.45), (-1.1, 12.4, 1.1), 28))
S.cam(TRIP + 0.2, ((-5.4, 10.9, 1.05), (DX + 0.4, 11.95, 0.9), 28), ((-5.1, 11.0, 1.05), (DX + 0.4, 11.95, 0.95), 30))
S.cam(CATCH - 0.35, ((0.3, 10.6, 1.35), (DX + 0.1, 12.2, 1.2), 32), ((0.15, 10.9, 1.35), (DX + 0.05, 12.25, 1.25), 38))
HP9 = S.headpos(held, l9[0] + 0.5)
S.cam(l9[0] + 0.4, ((-2.7, 10.5, 1.75), (-1.1, 12.2, 1.3), 32), ((-2.5, 10.75, 1.72), (-1.1, 12.2, 1.32), 36))
S.cam(RELEASE - 0.1, ((1.7, 11.3, 1.2), (DX + 0.2, 12.1, 0.95), 26), ((1.6, 11.2, 1.2), (DX + 0.2, 12.1, 0.95), 26),
      shake=lambda t: max(0.0, 0.6 - (t - RELEASE) * 1.2) if t > RELEASE else 0.0)
HM = S.head(mama, l11[0])
S.cam(l11[0] - 0.2, ((-2.75, 11.45, 1.6), HM + V(0, 0, -0.06), 34), ((-2.6, 11.5, 1.6), HM + V(0, 0, -0.06), 38))
S.cam(l12[0] - 0.1, S.shot(held, l12[0], "mcu", az=-15, lens=32), S.shot(held, l12[1], "cu", az=-10, lens=38))
S.cam(NIGHT, ((-0.3, 9.6, 0.95), (DX, 12.5, 0.75), 28), ((-0.8, 10.6, 0.9), (DX, 12.5, 0.8), 36))
S.cam(DOUBT - 0.2, S.shot(held, DOUBT, "cu", az=-12, lens=36), S.shot(held, END, "cu", az=-8, lens=44))

S.finish(length=END)
