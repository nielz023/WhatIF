"""S20b · Dag 19 · het klaslokaal: iedereen staart, twee leerlingen lopen weg. Een kluisje slaat dicht, hij schrikt,
en de hele buitenmuur valt naar buiten op het lege schoolplein. Dan staat de pestkop op: 'Everybody calm down.'
Hij is degene die hem naar buiten brengt.

    blender -b -P anim/scenes/s20b_klas.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s20b", "school", "klaslokaal")

WALL_Y = 4.12                                  # buitenkant van de achtermuur (scharnier)
SLAB = 0.13                                    # de omgevallen muur ligt zo dik op het plein
DOOR = V(3.75, -4.6, 0)                        # deuropening in de voorwand (rechts)
WIN = V(3.4, 3.52, 0)                          # bij het raam rechtsachter, naar het plein
SILL_L = V(3.15, 3.86, 0.92)
SILL_R = V(3.65, 3.86, 0.92)
CLASS_C = V(0.0, -0.5, 1.0)


def seat(r, c, s):
    return V(-1.6 + 1.5 * r + 0.48, -2.4 + 2.2 * c + 0.38 * s, 0)


# stoelen met de rugleuning van het bord af (ze stonden achterstevoren)
for o in bpy.data.objects:
    if o.name.startswith("Schoolstoel_"):
        o.rotation_euler.z = math.radians(-90)

# voorwand met deuropening, en een stukje gang erachter
wm = bpy.data.materials.get("Klaslokaal_muur") or S.mat("muur_klas", (0.86, 0.88, 0.80))
for nm, loc, size in (("Voorwand_a", (-0.6, -4.06, 0), (7.8, 0.12, 3.2)), ("Voorwand_b", (4.35, -4.06, 0), (0.3, 0.12, 3.2)),
                      ("Voorwand_c", (3.75, -4.06, 2.05), (0.9, 0.12, 1.15))):
    T.box(nm, loc, size, wm, bevel=0, ol=0.01)
km = S.mat("kozijn_deur", (0.95, 0.95, 0.93))
for nm, loc, size in (("Deurkozijn_l", (3.27, -4.06, 0), (0.06, 0.16, 2.1)), ("Deurkozijn_r", (4.23, -4.06, 0), (0.06, 0.16, 2.1)),
                      ("Deurkozijn_b", (3.75, -4.06, 2.05), (1.02, 0.16, 0.06))):
    T.box(nm, loc, size, km, bevel=0.005, ol=0.006)
T.box("Lokaaldeur_open", (4.2, -4.58, 0), (0.05, 0.9, 2.04), S.mat("deur_lokaal", (0.80, 0.55, 0.30)), bevel=0.01, ol=0.008)
T.box("Gang_vloer", (3.75, -5.3, -0.1), (4.4, 2.4, 0.1), S.mat("gangvloer", (0.60, 0.62, 0.66)), bevel=0, ol=0)
T.box("Gang_muur", (3.75, -6.45, 0), (4.4, 0.1, 3.2), wm, bevel=0, ol=0.01)
T.box("Gang_plafond", (3.75, -5.3, 3.2), (4.4, 2.4, 0.1), S.mat("plafond_gang", (0.93, 0.92, 0.9)), bevel=0, ol=0)
for k in range(9):
    T.box(f"Gang_kluisje_{k}", (1.9 + k * 0.44, -6.18, 0.1), (0.42, 0.42, 1.9),
          S.mat(f"kluisje_gang{k // 3 % 2}", ((0.15, 0.40, 0.80), (0.85, 0.20, 0.15))[k // 3 % 2]), bevel=0.01, ol=0.006)
T.area_light("Ganglicht_klas", (3.75, -5.3, 3.1), (0, 0, 0), size=(3.5, 1.8), color=(0.95, 0.98, 1.0), energy=250)

# de achtermuur met ramen en plint scharniert om de onderkant aan de buitenkant
back = S.obj("Klaslokaal_muur_back")
kids_wall = [o for o in (S.obj("Klaslokaal_plint_back"),) if o]
kids_wall += [bpy.data.objects[n] for n in ("Lokaalraam_0.8", "Lokaalraam_2.9", "Lokaalraam_5.0", "Lokaalraam_7.1") if n in bpy.data.objects]
wall = hinge(back, (0, WALL_Y, 0), kids_wall)
glass = [o for o in bpy.data.objects if o.name.startswith("Lokaalraam_") and o.name.endswith("_glas")]

# ---------------------------------------------------------------- figuren
held = S.actor("hoofdpersonage", DOOR, 0)
BULLY_SEAT = seat(2, 1, 1)
pest = S.actor("pestkop", BULLY_SEAT, -90, energy=1.0)
SEATS = [(0, 0, -1), (0, 1, 1), (0, 2, -1), (1, 0, 1), (1, 1, -1), (1, 2, 1), (2, 0, -1), (2, 2, -1), (3, 1, 1), (3, 2, -1)]
LEAVE = [(3, 0, -1), (2, 0, 1)]
klas, leavers = [], []
for k, rcs in enumerate(SEATS + LEAVE):
    ch = S.extra(k, seat(*rcs), -90, energy=0.8)
    (klas if k < len(SEATS) else leavers).append(ch)
SIT_OF = {}
for ch in klas + leavers + [pest]:
    spec, z = sit(ch)
    SIT_OF[ch.rig.name] = spec
    S.place(ch, 0, ch.rig.location.copy() + V(0, 0, z), -90)


def twist(ch, t, target, base=None):
    """Lichaam meedraaien als het doel achter hen is (zittend achterom kijken)."""
    M = S._root_matrix(ch, t)
    p = M.inverted() @ V(target) - ch.J["head_c"]
    yaw = math.degrees(math.atan2(p.x, -p.y))
    extra = max(-70.0, min(70.0, math.copysign(max(0.0, abs(yaw) - 55.0), yaw)))
    b = dict(base or {})
    b["spine"] = (0, extra * 0.4, 0)
    b["chest"] = (0, extra * 0.6, 0)
    return b


def seated(ch, t, face, amt=0.8, at=None, pose="ontspannen", body=None, **kw):
    S.beat(ch, t, **SIT_OF[ch.rig.name], pose=pose, face=face, face_amt=amt, at=at,
           body=twist(ch, t, at, body) if at is not None else body, **kw)


# ---------------------------------------------------------------- tijdlijn
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.07)
S.ambience("sfx_klas_geroezemoes", 0.0, 1.1, vol=0.05)      # stil zodra hij binnenkomt
S.music("piano_hol", 0.0, 0, vol=0.2, fade_in=0.6, fade_out=1.5)
PIANO = S.sounds[-1]
l2 = S.say("S20-02", gap=0.5)
STARE = l2[0]
KIDS_GO = l2[0] + 1.6                          # 'A few kids leave the room...'
T2 = l2[1] + 0.35                              # snede: verder naar achteren
l3 = S.say("S20-03", gap=1.4)
SLAM = l3[0] + 1.75                            # na 'A locker slams behind you.'
FLINCH = SLAM + 0.08
JUST = l3[0] + 4.68                            # 'Just a flinch.'
FALL = l3[1] + 0.25
LAND = FALL + 1.1
l4 = S.say("S20-04", at=LAND + 1.1)
GONE = l4[0] + 0.19
HURT = l4[0] + 3.2                             # 'Nobody's hurt.'
MATTER = l4[0] + 5.5                           # 'It doesn't matter.'
FACES = l4[0] + 7.0                            # 'You can see it on every face.'
l5 = S.say("S20-05", gap=0.6)
STANDS = l5[0] + 0.35
HIM = l5[0] + 3.0                              # 'It's him.'
PIANO["loop_to"] = HIM - 0.2
S.music("strijkers_warm", HIM - 0.4, 0, vol=0.2, fade_in=1.6, fade_out=1.4)
STR = S.sounds[-1]
l6 = S.say("S20-06", who=pest, gap=0.35, gain=1.2)
HEY2 = l6[0] + 0.86
COASTER = l6[0] + 2.0
SAW = l6[0] + 5.38                             # 'You all saw it.'
CALM = l6[0] + 6.73                            # 'So everybody calm down.'
l7 = S.say("S20-07", gap=0.7)
OUT = l7[0] + 3.0                              # 'He's the one who walks you out.'
l8 = S.say("S20-08", who=pest, at=l7[0] + 8.4, gain=1.1)
S.t = l8[1]
S.wait(1.5)
END = S.t
STR["loop_to"] = END + 0.3

S.sfx("sfx_kluisje", SLAM - 0.05, 0.3)
S.sfx("sfx_vloer_kraak", FLINCH + 0.02, 0.22)
S.sfx("sfx_vloer_kraak", FALL - 0.35, 0.25)
S.sfx("sfx_muur_valt", FALL + 0.2, 0.36)
S.sfx("sfx_glasdeur", LAND - 0.02, 0.18)
S.sfx("sfx_schuiven", STANDS, 0.22)

# ---------------------------------------------------------------- de muur: een barst bij de schrik, dan valt hij naar buiten
key(wall, 0.0, rot=(0, 0, 0))
key(wall, FLINCH, rot=(0, 0, 0))
key(wall, FLINCH + 0.12, rot=(-2.5, 0, 0))
key(wall, FALL, rot=(-3.5, 0, 0))
fall_fr = list(range(F(FALL), F(LAND) + 1))
bake(wall, "rotation_euler", fall_fr, [(math.radians(-3.5 - 86.5 * min(1.0, ((f - F(FALL)) / max(1, F(LAND) - F(FALL)))) ** 2), 0, 0)
                                        for f in fall_fr])
key(wall, LAND + 0.14, rot=(-86.5, 0, 0))
key(wall, LAND + 0.28, rot=(-90, 0, 0))
key(wall, END, rot=(-90, 0, 0))
S.puff(V(3.0, 4.05, 3.05), FLINCH + 0.05, n=5, r=(0.08, 0.16), grow=2.0, dur=1.4, rise=-0.4, spread=0.8)
for x in (-3.5, -1.8, 0.0, 1.8, 3.5):
    S.puff(V(x, 6.6, 0.1), LAND, n=6, r=(0.12, 0.25), grow=2.0, dur=2.2, color=(0.82, 0.80, 0.76), rise=0.5, spread=2.0)
    S.debris(V(x, 7.2, 0.1), LAND, n=10, size=(0.03, 0.08), color=(0.86, 0.88, 0.80), speed=(1.0, 3.0), up=1.0, floor=0.0)
for g in glass:
    visible(g, 0.0, True)
    visible(g, LAND, False)
for x in (-2.9, -0.8, 1.3, 3.4):
    S.shatter(V(x, 5.9, 0.2), (1.5, 0.3), LAND + 0.02, n=10, normal=(0, 0, 1), speed=(0.8, 2.2), floor=0.0)

# ---------------------------------------------------------------- hij komt binnen, loopt naar het raam
S.beat(held, 0.0, "ontspannen", face="verdrietig", face_amt=0.4, look=(0, -0.2), body={"head": (6, 0, 0)})
S.walk(held, 0.0, T2 - 0.05, [DOOR, V(3.85, -3.2, 0), V(3.85, -0.6, 0)], stride=0.5, arms=0.3)
S.beat(held, STARE + 0.4, "ontspannen", face="nerveus", face_amt=0.5, look=(0.6, -0.1), face_only=True)
S.beat(held, KIDS_GO + 0.6, "ontspannen", face="verdrietig", face_amt=0.6, look=(0.5, -0.3), face_only=True)
S.teleport(held, T2, V(3.85, 1.4, 0), 180)
ARR = T2 + 2.0
S.walk(held, T2, ARR, [V(3.85, 1.4, 0), V(3.85, 2.8, 0), WIN], stride=0.5, arms=0.3, end_rot=180)
S.beat(held, ARR - 0.3, "ontspannen", face="verdrietig", face_amt=0.5, look=(0, 0.1), face_only=True)
S.beat(held, ARR + 0.3, "staan", face="verdrietig", face_amt=0.5, look=(0, 0.05), body={"spine": (8, 0, 0)})
for side, p in (("L", SILL_L), ("R", SILL_R)):
    S.reach(held, ARR, side, None, inf=0.0)
    S.reach(held, ARR + 0.5, side, p, inf=1.0)
    S.reach(held, FALL, side, p, inf=1.0)
    S.reach(held, FALL + 0.15, side, None, inf=0.0)
S.beat(held, SLAM - 0.1, "staan", face="verdrietig", face_amt=0.6, look=(0, 0.05), body={"spine": (8, 0, 0)})
S.beat(held, FLINCH, "schrik", amount=0.5, face="geschrokken", face_amt=0.9, body={"spine": (10, 0, 0), "chest": (6, 0, 0), "head": (-8, 0, 0)},
       ogen_knijp=0.8)
S.beat(held, FLINCH + 0.5, "staan", face="nerveus", face_amt=0.9, look=(0, -0.5), body={"spine": (8, 0, 0), "head": (16, 0, 0)})
S.beat(held, JUST - 0.2, "staan", face="nerveus", face_amt=0.7, look=(0, -0.5), body={"spine": (8, 0, 0), "head": (14, 0, 0)},
       mond_verdrietig=0.4)
S.beat(held, FALL - 0.35, "staan", face="verbaasd", face_amt=0.8, look=(0, 0.4), body={"spine": (6, 0, 0), "head": (-10, 0, 0)})
S.beat(held, FALL + 0.3, "staan", face="geschrokken", face_amt=1.0, look=(0, 0.2), arms=arms(HAND_OUT_R, HAND_OUT_L),
       body={"spine": (10, 0, 0), "head": (-4, 0, 0)})
S.beat(held, LAND + 0.2, "schrik", amount=0.5, face="geschrokken", face_amt=1.0, look=(0, -0.3))
S.beat(held, LAND + 1.6, "staan", face="bang", face_amt=0.9, look=(0, -0.4), body={"head": (12, 0, 0)})
S.hold(held, MATTER)
TURNED = heading(WIN, CLASS_C)
S.turn(held, MATTER, MATTER + 0.9, TURNED)
S.beat(held, MATTER + 1.0, "staan", face="verdrietig", face_amt=0.8, at=CLASS_C + V(0, 0, 0.2))
S.beat(held, FACES + 1.0, "staan", face="verdrietig", face_amt=0.9, at=V(0.5, -1.6, 1.1), mond_verdrietig=0.6)
S.beat(held, STANDS + 0.4, "staan", face="nerveus", face_amt=0.8, at=S.head(pest, STANDS + 1.0))
S.beat(held, HIM, "staan", face="nerveus", face_amt=1.0, at=S.head(pest, HIM))

# ---------------------------------------------------------------- de pestkop
S.beat(pest, 0.0, **SIT_OF[pest.rig.name], pose="armen_over", face="twijfel", face_amt=0.5, look=(0, 0))
S.beat(pest, STARE + 0.5, **SIT_OF[pest.rig.name], pose="armen_over", face="boos", face_amt=0.4, at=S.head(held, STARE + 0.5),
       body=twist(pest, STARE, S.head(held, STARE + 0.5)))
for t in frange(STARE + 1.5, T2, 1.0):
    S.beat(pest, t, **SIT_OF[pest.rig.name], pose="armen_over", face="boos", face_amt=0.4, at=S.head(held, t), body=twist(pest, t, S.head(held, t)))
S.beat(pest, ARR, **SIT_OF[pest.rig.name], pose="armen_over", face="twijfel", face_amt=0.5, at=S.head(held, ARR), body=twist(pest, ARR, S.head(held, ARR)))
S.beat(pest, FALL + 0.4, **SIT_OF[pest.rig.name], pose="schrik", amount=0.6, face="geschrokken", face_amt=1.0, at=S.head(held, FALL),
       body=twist(pest, FALL, S.head(held, FALL)))
S.beat(pest, LAND + 1.0, **SIT_OF[pest.rig.name], pose="ontspannen", face="verbaasd", face_amt=0.8, at=S.head(held, LAND),
       body=twist(pest, LAND, S.head(held, LAND)))
S.hold(pest, STANDS)
# hij staat op, de stoel schuift naar achteren
chair = S.obj("Schoolstoel_2_1_0.38")
key(chair, STANDS, loc=chair.location.copy())
key(chair, STANDS + 0.4, loc=chair.location + V(0.24, 0.05, 0))
UP = BULLY_SEAT + V(0.2, 0.02, 0)
S.place(pest, STANDS, BULLY_SEAT, -90)
S.place(pest, STANDS + 0.5, UP, -90)
S.beat(pest, STANDS + 0.55, "staan", face="vastberaden", face_amt=0.7, look=(0, 0))
S.turn(pest, STANDS + 1.0, STANDS + 1.6, heading(UP, WIN))
S.beat(pest, STANDS + 1.7, "vuisten", amount=0.6, face="vastberaden", face_amt=0.8, at=S.head(held, HIM))
S.beat(pest, HIM + 0.2, "vuisten", amount=0.6, face="boos", face_amt=0.5, at=S.head(held, HIM), body={"head": (6, 0, 0)})
# 'Hey! HEY!' tegen de klas
TO_CLASS = heading(UP, V(-1.0, -0.6, 0))
S.turn(pest, l6[0] - 0.3, l6[0] + 0.15, TO_CLASS)
S.beat(pest, l6[0] + 0.05, "vuisten", face="boos", face_amt=0.9, at=CLASS_C, mouth=0.5)
S.beat(pest, HEY2, "handen_zij", face="schreeuw", face_amt=0.9, at=CLASS_C + V(0, 0, 0.2), body={"chest": (-6, 0, 0)})
STAND = V(2.7, 3.05, 0)
S.walk(pest, l6[0] + 1.45, l6[0] + 3.6, [UP, V(2.33, 0.55, 0), V(2.33, 2.85, 0), STAND], stride=0.6, arms=0.6,
       end_rot=heading(STAND, WIN))
S.beat(pest, l6[0] + 1.6, "vuisten", face="boos", face_amt=0.8, look=(0.5, 0), face_only=True)
S.beat(pest, l6[0] + 3.75, "wijzen", face="boos", face_amt=0.8, at=CLASS_C + V(0, 0, 0.3), body={"chest": (0, 10, 0)})
S.beat(pest, SAW - 0.3, "wijzen", face="boos", face_amt=0.8, at=CLASS_C + V(0, 0, 0.3), body={"chest": (0, 10, 0)})
S.turn(pest, SAW - 0.2, SAW + 0.3, heading(STAND, CLASS_C))
S.beat(pest, SAW + 0.35, "handen_zij", face="boos", face_amt=0.7, at=V(-1.2, 1.6, 1.0))
S.beat(pest, SAW + 0.95, "handen_zij", face="boos", face_amt=0.7, at=V(0.8, -2.4, 1.0))
CALM_A = arms(arm("L", (0.35, 0.6, -0.7), (0.15, 0.95, -0.2)), arm("R", (0.35, 0.6, -0.7), (0.15, 0.95, -0.2)))
CALM_B = arms(arm("L", (0.35, 0.55, -0.75), (0.15, 0.85, -0.45)), arm("R", (0.35, 0.55, -0.75), (0.15, 0.85, -0.45)))
for k, t in enumerate(frange(CALM, l6[1] + 0.2, 0.42)):
    S.beat(pest, t, "staan", face="vastberaden", face_amt=0.6, at=CLASS_C, arms=CALM_A if k % 2 == 0 else CALM_B)
S.beat(pest, l6[1] + 0.5, "staan", face="neutraal", face_amt=0.5, at=CLASS_C)
# naar hem toe, knikje naar het gat in de muur
S.turn(pest, l7[0] + 0.3, l7[0] + 0.8, heading(STAND, WIN))
S.beat(pest, l7[0] + 0.9, "ontspannen", face="neutraal", face_amt=0.6, at=S.head(held, l7[0] + 0.9))
S.beat(pest, l7[0] + 2.1, "ontspannen", face="neutraal", face_amt=0.6, at=V(2.3, 6.0, 1.2), body={"head": (10, 0, 0)})
S.beat(pest, l7[0] + 2.6, "ontspannen", face="blij", face_amt=0.2, at=S.head(held, l7[0] + 2.6))

# hij: kijkt naar de pestkop, ongelovig, een beetje ontroerd
S.beat(held, l6[0] + 0.2, "staan", face="verbaasd", face_amt=0.6, at=S.head(pest, l6[0] + 0.2))
S.beat(held, COASTER + 1.8, "staan", face="verbaasd", face_amt=0.8, at=S.head(pest, COASTER + 1.8))
S.beat(held, CALM, "staan", face="verdrietig", face_amt=0.4, at=S.head(pest, CALM), wenkbrauw_op=0.4)
S.beat(held, l7[0] + 1.0, "staan", face="blij", face_amt=0.25, at=S.head(pest, l7[0] + 1.0), mond_verdrietig=0.3)

# samen naar buiten, over de omgevallen muur
BOUT = V(2.2, 9.0, 0)
HOUT = V(2.85, 8.55, 0)
S.walk(pest, OUT, OUT + 4.4, [STAND, V(2.35, 3.8, 0), V(2.35, 4.3, SLAB), V(2.35, 7.15, SLAB), V(2.35, 7.7, 0), BOUT],
       stride=0.55, arms=0.5, end_rot=195)
S.walk(held, OUT + 0.9, OUT + 5.4, [WIN, V(2.4, 3.85, 0), V(2.4, 4.3, SLAB), V(2.4, 7.15, SLAB), V(2.45, 7.7, 0), HOUT],
       stride=0.5, arms=0.35, end_rot=165)
S.beat(pest, OUT + 0.2, "ontspannen", face="neutraal", face_amt=0.5, look=(0, -0.2), face_only=True)
S.beat(held, OUT + 1.0, "staan", face="verdrietig", face_amt=0.4, look=(0, -0.3), face_only=True)
# 'You still owe me lunch, by the way.'
S.beat(pest, l8[0] - 0.4, "ontspannen", face="neutraal", face_amt=0.5, at=S.head(held, l8[0]))
S.beat(pest, l8[0] + 0.3, "ontspannen", face="grijns", face_amt=0.5, at=S.head(held, l8[0]))
S.beat(pest, l8[1] + 0.2, "ontspannen", face="grijns", face_amt=0.8, look=(0, 0), body={"head": (0, 20, 0)})
S.hold(pest, END)
S.beat(held, l8[0] - 0.2, "ontspannen", face="neutraal", face_amt=0.4, at=S.head(pest, l8[0]))
S.beat(held, l8[1] - 0.1, "ontspannen", face="verbaasd", face_amt=0.5, at=S.head(pest, l8[1]))
S.beat(held, l8[1] + 0.6, "ontspannen", face="lach", face_amt=0.6, at=S.head(pest, l8[1]), body={"head": (6, 0, 0)})
S.hold(held, END)

# ---------------------------------------------------------------- de klas
FACE_IN = ["nerveus", "bang", "nerveus", "twijfel", "bang", "nerveus", "geschrokken", "bang", "nerveus", "twijfel"]
FALL_F = ["geschrokken", "bang", "geschrokken", "bang", "geschrokken", "bang", "geschrokken", "bang", "geschrokken", "bang"]
for k, ch in enumerate(klas):
    seated(ch, 0.0, "neutraal", 0.5, look=(0.1 * (k % 3 - 1), -0.1))
    for t in frange(STARE + 0.1 + 0.07 * k, T2 + 2.0, 0.9):
        seated(ch, t, FACE_IN[k], 0.7, at=S.head(held, t))
    seated(ch, SLAM + 0.15, FACE_IN[k], 0.8, at=S.head(held, SLAM), wenkbrauw_op=0.4)
    seated(ch, FALL + 0.3 + 0.05 * k, FALL_F[k], 1.0, at=S.head(held, FALL), pose="schrik" if k % 3 else "handen_hoofd", amount=0.7)
    seated(ch, LAND + 0.8, FALL_F[k], 0.9, at=S.head(held, LAND), pose="handen_hoofd" if k % 4 == 0 else "ontspannen")
    seated(ch, FACES - 0.6, FACE_IN[k], 1.0, at=S.head(held, FACES), mond_verdrietig=0.4)
    seated(ch, STANDS + 0.6, "verbaasd", 0.7, at=S.head(pest, STANDS + 0.6))
    seated(ch, HEY2, "geschrokken", 0.6, at=S.head(pest, HEY2))
    for t in frange(COASTER, l6[1], 1.1):
        seated(ch, t, "verbaasd" if t < CALM else "twijfel", 0.6, at=S.head(pest, t))
    seated(ch, l6[1] + 0.4 + 0.1 * k, "neutraal" if k % 2 else "twijfel", 0.6, at=S.head(pest, l6[1]), body={"head": (8, 0, 0)})
    for t in frange(OUT + 0.5, OUT + 6.0, 1.2):
        seated(ch, t, "neutraal", 0.6, at=S.head(held, t))
    S.hold(ch, END)

# twee leerlingen staan op en lopen weg
for k, (ch, path, t0) in enumerate(zip(leavers,
                                       ([seat(*LEAVE[0]), V(3.7, -3.3, 0), V(3.75, -4.5, 0), V(3.0, -5.3, 0)],
                                        [seat(*LEAVE[1]), V(2.2, -3.45, 0), V(3.55, -3.65, 0), V(3.75, -4.6, 0), V(5.0, -5.2, 0)]),
                                       (KIDS_GO, KIDS_GO + 0.35))):
    seated(ch, 0.0, "neutraal", 0.5, look=(0, -0.1))
    seated(ch, STARE + 0.2, "bang", 0.8, at=S.head(held, STARE + 0.2))
    S.place(ch, t0, path[0] + V(0, 0, 0), -90)
    S.beat(ch, t0 + 0.3, "staan", face="bang", face_amt=0.8, at=S.head(held, t0 + 0.3))
    S.walk(ch, t0 + 0.45, t0 + 0.45 + 2.1 + k * 0.5, path, stride=0.55, arms=0.5)
    S.beat(ch, t0 + 0.6, "staan", face="nerveus", face_amt=0.8, look=(0.5, 0), face_only=True)
    S.hold(ch, END)

# ---------------------------------------------------------------- camera
# 1 · vanaf het bord: de klas, en hij in de deur
S.cam(0.0, ((-3.9, -0.3, 2.25), (3.5, -3.2, 1.05), 24), ((-3.8, -0.4, 2.2), (3.6, -2.0, 1.1), 26))
# 2 · twee leerlingen glippen langs hem de deur uit
S.cam(KIDS_GO - 0.1, ((-0.5, 3.6, 2.4), (3.6, -3.6, 1.1), 26), ((-0.3, 3.5, 2.35), (3.6, -3.0, 1.1), 28))
# 3 · naar het raam, het lege plein
S.cam(T2, ((0.9, 3.6, 1.7), (3.6, 2.4, 1.25), 26), ((1.0, 3.65, 1.7), (3.5, 3.0, 1.3), 28))
# 4 · door het raam: zijn gezicht als het kluisje dichtslaat
HW = S.headpos(held, ARR + 0.6)
S.cam(SLAM - 0.6, ((HW.x + 0.15, 5.2, HW.z + 0.02), HW + V(0, 0, -0.08), 40), ((HW.x + 0.12, 5.0, HW.z + 0.02), HW + V(0, 0, -0.06), 44),
      shake=lambda t: max(0.0, 0.8 - (t - FLINCH) * 2.0) if t > FLINCH else 0.0)
# 5 · buiten op het plein: de muur valt
S.cam(FALL - 0.25, ((9.5, 12.0, 2.6), (1.0, 4.6, 1.3), 24), ((9.0, 11.4, 2.4), (1.0, 4.6, 1.2), 26),
      shake=lambda t: max(0.0, 1.0 - (t - LAND) * 1.2) if t > LAND else 0.0)
# 6 · 'Nobody's hurt.' de klas, bevroren
S.cam(HURT, ((-3.9, 0.7, 1.7), (2.8, 1.8, 1.0), 22), ((-3.8, 0.8, 1.65), (2.8, 1.8, 1.0), 24))
# 7 · hij draait zich om
S.cam(MATTER - 0.2, (S.headpos(held, MATTER + 1.2) + V(-0.8, -1.3, -0.05), S.headpos(held, MATTER + 1.2) + V(0, 0, -0.1), 34),
      (S.headpos(held, MATTER + 1.2) + V(-0.7, -1.15, -0.05), S.headpos(held, MATTER + 1.2) + V(0, 0, -0.08), 36))
# 8 · zijn blik over elk gezicht
HV = S.headpos(held, FACES)
fwd = V(math.sin(math.radians(TURNED)), -math.cos(math.radians(TURNED)), 0)
S.cam(FACES - 0.1, ((3.1, 3.5, 2.45), (-1.2, 2.0, 0.85), 28), ((3.1, 3.5, 2.45), (1.0, -2.6, 0.85), 28))
# 9 · iemand staat op
S.cam(l5[0] - 0.2, ((0.6, 2.9, 1.95), (1.9, 0.2, 1.1), 28), ((0.7, 2.85, 1.95), (2.0, 0.2, 1.25), 30))
# 10 · 'It's him.'
S.cam(HIM - 0.2, S.shot(pest, HIM, "mcu", az=10, lens=34), S.shot(pest, HIM + 0.9, "mcu", az=8, lens=38))
# 11 · 'Hey! HEY!' iets van onderen
S.cam(l6[0] - 0.1, ((-0.2, -1.6, 2.2), (1.95, 0.2, 1.3), 28), ((-0.1, -1.5, 2.15), (1.95, 0.2, 1.35), 30))
# 12 · hij loopt naar achteren, naast hem
S.cam(l6[0] + 1.4, ((-2.6, -2.4, 1.8), (2.7, 2.6, 1.2), 26), ((-2.4, -2.2, 1.75), (2.8, 2.8, 1.25), 28))
# 13 · 'You all saw it. So everybody calm down.' de twee, vanuit de klas
S.cam(SAW - 0.2, ((0.3, 1.0, 2.0), (2.9, 3.1, 1.3), 28), ((0.5, 1.2, 1.95), (2.9, 3.1, 1.3), 30))
# 14 · de klas ontspant, over zijn schouder
S.cam(l6[1] + 0.2, ((4.0, 3.0, 2.0), (-1.5, -1.0, 0.85), 26), ((3.9, 2.9, 1.95), (-1.5, -1.0, 0.85), 28))
# 15 · 'The guy who took your lunch money...' samen in beeld
S.cam(l7[0] + 0.2, S.shot(held, l7[0] + 0.8, "mcu", az=-25, lens=32), S.shot(held, OUT, "mcu", az=-22, lens=35))
# 16 · buiten: ze lopen samen naar buiten, de klas kijkt
S.cam(OUT + 0.6, ((6.0, 12.8, 1.8), (2.3, 5.0, 1.2), 26), ((5.6, 12.4, 1.7), (2.3, 6.5, 1.2), 28))
# 17 · 'You still owe me lunch.'
S.cam(l8[0] - 0.5, ((2.55, 11.4, 1.35), (2.5, 8.75, 1.35), 32), ((2.55, 11.1, 1.35), (2.5, 8.75, 1.38), 36))

S.finish(length=END)
