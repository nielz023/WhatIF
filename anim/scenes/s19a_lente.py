"""S19a · Dag 18 · de straat in de lente: pollen, het springkussen van de buren in één adem opgeblazen,
en tien minuten later de nies. Elk raam in de straat springt tegelijk.

    blender -b -P anim/scenes/s19a_lente.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s19a", "straat", "lente")

DOORSTEP = V(-1.4, 12.62, 0.30)
GATE = V(-1.4, 8.3, 0.12)
KNEEL = V(-7.4, 7.6, 0.12)                     # op de stoep bij het hek van de buren
SNEEZE_AT = V(-3.0, 7.35, 0.12)
FRIEND_AT = V(-4.6, 7.1, 0.12)
castle = S.obj("Springkussen_buren")
CASTLE = castle.location.copy()

held = S.actor("hoofdpersonage", DOORSTEP, 0)
vriend = S.actor("beste_vriend", V(-3.3, 7.0, 0.12), -30, energy=1.2)
kid1 = S.actor("broertje", V(-5.3, 7.35, 0.12), 170, energy=1.6, label="buurjongen",
               outfit=dict(shirt=(0.95, 0.75, 0.10), broek=(0.20, 0.35, 0.70), haar=(0.80, 0.55, 0.20)), drop=("streep", "sproet"))
kid2 = S.actor("zusje_pestkop", V(-4.7, 7.55, 0.12), 185, energy=1.6, label="buurmeisje",
               outfit=dict(shirt=(0.30, 0.75, 0.45), broek=(0.85, 0.40, 0.65), haar=(0.15, 0.10, 0.08)), drop=("suikerspin",))
buur = S.extra(5, V(-8.9, 7.35, 0.12), 150, energy=0.8)
pump = T.cyl("Fietspomp", (0, 0, 0), 0.03, 0.45, S.mat("pomp_rood", (0.85, 0.12, 0.10)), seg=10, ol=0.004)
attach(pump, buur, "hand.R", (0, 0.05, 0.03), (90, 0, 0))
tube = T.tube("Springkussen_slang", [(KNEEL.x, KNEEL.y + 0.3, 0.75), (KNEEL.x, 8.5, 0.2), (KNEEL.x - 0.1, 9.3, 0.18), (CASTLE.x - 1.9, 9.9, 0.3)],
              0.05, S.mat("slang_rood", (0.85, 0.15, 0.12)))

# ---------------------------------------------------------------- tijdlijn
S.hud(18, "262,144x STRONGER", t0=0.6)
S.music("lente", 0.0, 60, vol=0.24, fade_in=0.8, fade_out=0.6)
SPRING = S.sounds[-1]
S.ambience("sfx_straat_sfeer", 0.0, 60, vol=0.1)
AMB = S.sounds[-1]
l1 = S.say("S19-01", gap=0.6)
STEP_OUT = l1[0] + 4.4
POLLEN = l1[0] + 8.5                           # 'And it's pollen season.'
l2 = S.say("S19-02", gap=0.5)
BREATH = l2[0] + 7.5                           # 'In one breath.'
S.sfx("sfx_springkussen", BREATH - 0.1, 0.5)
l3 = S.say("S19-03", who=vriend, gap=0.6, gain=1.15)
l4 = S.say("S19-04", gap=0.6)
LATER = l4[0] - 0.3
l5 = S.say("S19-05", gap=0.3)
HOLD_IN = l5[0] + 1.3
l6 = S.say("S19-06", gap=0.3)
SPRING["loop_to"] = l5[0] - 0.2
S.music("pizz_spanning", l5[0] - 0.3, l6[1] - 0.2, vol=0.24, fade_in=0.3, fade_out=0.15)
AH = l6[1] + 0.2
BOOM = AH + 0.9
AMB["loop_to"] = AH
S.sfx("sfx_nies_boem", BOOM - 0.6, 0.6, cut=(0.0, 1.9))
S.sfx("sfx_glasdeur", BOOM + 0.05, 0.55)
S.ambience("sfx_autoalarm", BOOM + 0.9, 60, vol=0.16)
S.t = BOOM + 3.2
END = S.t
S.text("10 MINUTES LATER", LATER + 0.2, l4[1] + 0.3, loc=(0.5, 0.85), size=60, color=WHITE, anchor=("CENTER", "TOP"))

# ---------------------------------------------------------------- naar buiten
S.walk(held, STEP_OUT, l1[1] - 0.3, [DOORSTEP, V(-1.4, 11.3, 0.12), GATE], stride=0.4, arms=0.4)
S.beat(held, 0.0, "staan", face="nerveus", face_amt=0.5, look=(0, 0.2))
S.beat(held, POLLEN - 0.3, "staan", face="neutraal", face_amt=0.5, look=(0, 0.6), face_only=True)
S.beat(held, POLLEN + 0.5, "staan", face="twijfel", face_amt=0.8, look=(-0.4, 0.7), face_only=True, mond_O=0.3)
S.beat(held, l1[1], "staan", face="twijfel", face_amt=0.8, look=(-0.3, 0.6), body={"head": (-10, 0, 0)}, mond_O=0.3)

# naar het springkussen: knielen en blazen
S.teleport(held, l2[0] - 0.1, V(-4.2, 6.9, 0.12), -70)
S.walk(held, l2[0] + 1.6, BREATH - 1.2, [V(-4.2, 6.9, 0.12), KNEEL], stride=0.45, end_rot=180)
S.beat(held, l2[0] - 0.1, "staan", face="blij", face_amt=0.4, look=(-0.6, 0.3))
KNEELS = dict(crouch=(0.36, 22.0), feet=((0.14, -0.2, 0), (-0.14, 0.15, 0)))
S.beat(held, BREATH - 0.9, "staan", **KNEELS, face="neutraal", face_amt=0.6, look=(0, 0.2),
       arms=arms(arm("L", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5)), arm("R", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5))))
S.beat(held, BREATH - 0.3, "staan", **KNEELS, face="neutraal", face_amt=0.6, look=(0, 0.2), mouth=0.3, body={"chest": (-10, 0, 0)},
       arms=arms(arm("L", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5)), arm("R", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5))), ogen_knijp=0.6)
S.beat(held, BREATH + 0.9, "staan", **KNEELS, face="inspanning", face_amt=0.5, mond_O=1.0, look=(0, 0.2), body={"chest": (8, 0, 0)},
       arms=arms(arm("L", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5)), arm("R", (0.25, 0.6, -0.5), (-0.6, 0.6, 0.5))))
S.beat(held, l3[0] - 0.1, "staan", face="grijns", face_amt=0.7, at=S.head(vriend, l3[0]))
S.beat(held, l3[1], "schouders_op", amount=0.6, face="lach", face_amt=0.6, at=S.head(vriend, l3[0]))

# castle: plat -> in één adem vol
key(castle, 0.0, scale=(1.04, 1.04, 0.07))
key(castle, BREATH - 0.05, scale=(1.04, 1.04, 0.07))
key(castle, BREATH + 0.6, scale=(1.0, 1.0, 0.85))
key(castle, BREATH + 0.85, scale=(0.99, 0.99, 1.08))
key(castle, BREATH + 1.1, scale=(1.0, 1.0, 0.97))
key(castle, BREATH + 1.35, scale=(1.0, 1.0, 1.0))
show(tube, 0.0, l3[1])

# de buren
S.beat(buur, 0.0, "staan", face="inspanning", face_amt=0.6, look=(0, -0.5), arms=HOLD_FRONT_R, crouch=(0.06, 14))
S.beat(buur, l2[0] + 2.0, "handen_zij", face="verdrietig", face_amt=0.6, at=V(CASTLE.x, CASTLE.y, 0.3))
S.beat(buur, BREATH + 0.3, "staan", face="geschrokken", face_amt=1.0, at=V(CASTLE.x, CASTLE.y, 1.5), arms=HOLD_FRONT_R)
S.beat(buur, l3[0], "staan", face="lach", face_amt=0.8, at=S.head(held, l3[0]), arms=HOLD_FRONT_R)
S.hold(buur, END)
for k, ch in enumerate((kid1, kid2)):
    S.beat(ch, 0.0, "staan", face="verdrietig", face_amt=0.8, at=V(CASTLE.x, CASTLE.y, 0.2))
    S.beat(ch, BREATH + 0.2, "armen_omhoog", face="verbaasd", face_amt=1.0, at=V(CASTLE.x, CASTLE.y, 2.0))
    S.beat(ch, BREATH + 0.8, "juichen", face="lach", face_amt=1.0, at=V(CASTLE.x, CASTLE.y, 2.0), mouth=0.6)
    # tien minuten later: springen op het kussen
    TOP = CASTLE + V(0.3 - 0.8 * k, -0.4 + 0.5 * k, 0.6)
    S.teleport(ch, LATER, TOP, 160 + 40 * k)
    for j, t in enumerate(frange(LATER, END, 0.45)):
        up = (j + k) % 2 == 0
        key(ch.rig, t, loc=TOP + V(0, 0, 0.55 if up else 0.0))
        S.beat(ch, t, "armen_omhoog" if up else "juichen", face="lach", face_amt=1.0, mouth=0.5 if up else 0.2,
               crouch=(0.0, 0) if up else (0.12, 8))
    visible(ch.rig, 0.0, True)

# de vriend
S.beat(vriend, 0.0, "staan", face="blij", face_amt=0.6, at=DOORSTEP + V(0, 0, 1.3))
S.teleport(vriend, l2[0] - 0.1, V(-5.0, 6.7, 0.12), -40)
S.beat(vriend, l2[0] - 0.1, "staan", face="blij", face_amt=0.6, at=V(CASTLE.x, CASTLE.y, 0.3))
S.beat(vriend, BREATH + 0.3, "staan", face="verbaasd", face_amt=1.0, at=V(CASTLE.x, CASTLE.y, 1.8))
S.beat(vriend, l3[0], "staan", face="lach", face_amt=1.0, at=S.head(held, l3[0]), arms=CLAP_A)
S.beat(vriend, l3[0] + 0.3, "staan", face="lach", face_amt=1.0, at=S.head(held, l3[0]), arms=CLAP_B)
S.beat(vriend, l3[0] + 0.6, "staan", face="lach", face_amt=0.9, at=S.head(held, l3[0]), arms=CLAP_A)

# ---------------------------------------------------------------- tien minuten later: de nies
S.teleport(held, LATER, SNEEZE_AT, 0)
S.teleport(vriend, LATER, FRIEND_AT, heading(FRIEND_AT, SNEEZE_AT))
S.beat(held, LATER, "staan", face="blij", face_amt=0.5, look=(-0.6, 0.3))
S.beat(held, l4[1] - 0.2, "staan", face="twijfel", face_amt=0.9, look=(0, -0.3), mond_O=0.2, wenkbrauw_op=0.6)
S.beat(held, l5[0] + 0.3, "staan", face="inspanning", face_amt=0.5, look=(0, 0.2), body={"head": (-8, 0, 0)}, mond_O=0.4)
FINGER = arm("R", (0.2, 0.5, -0.4), (-0.75, 0.5, 0.45))
S.beat(held, HOLD_IN, "staan", face="inspanning", face_amt=0.9, look=(0, 0.1), arms=FINGER, body={"head": (-4, 0, 0)}, ogen_knijp=0.7)
S.beat(held, l6[0], "staan", face="inspanning", face_amt=1.0, arms=FINGER, body={"head": (-14, 0, 0), "chest": (-8, 0, 0)}, mond_O=0.5)
S.beat(held, AH, "schrik", amount=0.5, face="geschrokken", face_amt=0.6, body={"head": (-24, 0, 0), "chest": (-12, 0, 0)}, mouth=0.7,
       ogen_knijp=1.0)
S.beat(held, BOOM - 0.08, "schrik", amount=0.5, face="geschrokken", face_amt=0.6, body={"head": (-28, 0, 0), "chest": (-14, 0, 0)}, mouth=0.8,
       ogen_knijp=1.0)
S.beat(held, BOOM, "staan", crouch=(0.12, 30), face="inspanning", face_amt=1.0, body={"head": (30, 0, 0), "chest": (18, 0, 0)}, mouth=0.6,
       ogen_knijp=1.0)
S.beat(held, BOOM + 0.6, "staan", crouch=(0.06, 12), face="geschrokken", face_amt=0.9, look=(0, 0), body={"head": (6, 0, 0)},
       arms=arm("R", (0.2, 0.55, -0.5), (-0.7, 0.45, 0.55)))
S.beat(held, END, "staan", face="nerveus", face_amt=1.0, look=(0.6, 0.1), body={"head": (0, 25, 0)},
       arms=arm("R", (0.2, 0.55, -0.5), (-0.7, 0.45, 0.55)))
S.beat(vriend, LATER, "staan", face="blij", face_amt=0.5, at=S.head(held, LATER))
S.beat(vriend, l5[0] + 0.8, "staan", face="nerveus", face_amt=0.9, at=S.head(held, LATER), wenkbrauw_op=0.6)
S.beat(vriend, HOLD_IN + 0.3, "schrik", amount=0.6, face="bang", face_amt=1.0, at=S.head(held, LATER))
S.beat(vriend, BOOM + 0.1, "handen_hoofd", crouch=(0.3, 25), face="geschrokken", face_amt=1.0, ogen_knijp=0.8)
S.hold(vriend, END)
S.walk(vriend, HOLD_IN + 0.2, l6[1], [FRIEND_AT, FRIEND_AT + V(-1.2, -0.4, 0)], stride=0.35, turn=False, arms=None)

# ---------------------------------------------------------------- de klap: schokgolf, alle ramen tegelijk
FACE = SNEEZE_AT + V(0, -0.25, 1.45)
S.ring(FACE, BOOM, r0=0.2, r1=40.0, dur=0.9, rot=(90, 0, 0), thick=0.12, strength=3.0)
S.ring(SNEEZE_AT + V(0, 0, 0.15), BOOM + 0.04, r0=0.3, r1=30.0, dur=0.8, thick=0.08, strength=2.0)
S.flash(FACE + V(0, -0.2, 0), BOOM, size=0.4, color=(1, 1, 1), strength=5)
glass_mats = [m for m in bpy.data.materials if m.name.startswith(("raamglas", "autoruit"))]
for m in glass_mats:
    g = next(n for n in m.node_tree.nodes if n.type == "GROUP")
    sock = g.inputs["Kleur"]
    sock.keyframe_insert("default_value", frame=F(BOOM) - 1)
    sock.default_value = (0.07, 0.08, 0.11, 1)
    sock.keyframe_insert("default_value", frame=F(BOOM))
glass_shard = S.mat("glasscherf_v", (0.75, 0.9, 1.0), 1.2)
for x in (-12, -6, 0, 6):
    for wx, wz in ((-1.4, 4.3), (1.4, 4.3), (1.2, 1.8)):
        S.debris(V(x + wx, 12.85, wz), BOOM + 0.02 + abs(x) * 0.004, n=7, size=(0.03, 0.09), mat=glass_shard, speed=(1.5, 3.5),
                 direction=(0, -1, 0.2), spread=0.6, up=0.3, floor=0.12, life=1.8, name="Scherf")
for x in (-6, 0):
    for wx, wz in ((1.4, 4.3), (-1.4, 4.3), (-1.2, 1.8)):
        S.debris(V(x + wx, -10.35, wz), BOOM + 0.06, n=5, size=(0.03, 0.09), mat=glass_shard, speed=(1.5, 3.0),
                 direction=(0, 1, 0.2), spread=0.6, up=0.3, floor=0.12, life=1.8, name="Scherf")
rnd = random.Random(19)
shards = [(rnd.uniform(-20, 15), rnd.choice((rnd.uniform(6.2, 8.4), rnd.uniform(-6.0, -3.7))), 0.14) for _ in range(500)]
sh = P.points_mesh("Glasscherven_na", shards, 0.06, S.mat("glasscherf_g", (0.75, 0.90, 0.98)), seg=4)
sh.scale.z = 0.15
show(sh, BOOM + 0.5)
pol = S.obj("Pollen")
if pol:
    visible(pol, 0.0, True)
    visible(pol, BOOM + 0.05, False)
S.debris(SNEEZE_AT + V(0, 0, 2.5), BOOM + 0.05, n=40, size=(0.04, 0.07), mat=S.mat("bloesem_v", (0.98, 0.62, 0.78)), speed=(3, 7),
         direction=(0, -1, 0.3), spread=1.2, up=0.5, floor=0.0, life=2.5, shape="sphere", name="Bloesem")

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-22, -1.5, 2.0), (2, 7, 3.0), 24), ((-20, -0.8, 2.0), (2, 7, 3.0), 26))
S.cam(STEP_OUT - 0.1, ((0.5, 6.8, 1.3), (-1.4, 11.8, 1.3), 28), ((0.3, 6.4, 1.3), (-1.4, 10.5, 1.0), 30))
S.cam(POLLEN - 0.2, S.shot(held, POLLEN, "mcu", az=15, lens=34), S.shot(held, l1[1], "mcu", az=12, lens=37))
S.cam(l2[0] - 0.1, ((-9.4, 4.2, 1.5), (-5.4, 8.4, 1.1), 26), ((-9.3, 4.5, 1.5), (-5.8, 8.6, 1.0), 28))
S.cam(BREATH - 1.0, ((-9.8, 5.4, 1.3), (-6.6, 9.6, 1.0), 24), ((-9.7, 5.6, 1.4), (-6.6, 9.8, 1.3), 24))
S.cam(l3[0] - 0.2, ((-4.6, 4.5, 1.25), (-6.0, 7.2, 1.0), 30), ((-4.7, 4.7, 1.25), (-6.0, 7.2, 1.0), 32))
S.cam(LATER, ((-1.0, 4.2, 1.4), (-5.5, 10.2, 1.4), 26), ((-1.2, 4.4, 1.4), (-5.5, 10.2, 1.4), 28))
HS = S.head(held, l5[0])
S.cam(l5[0] - 0.1, S.shot(held, l5[0] + 0.3, "mcu", az=12, lens=34), S.shot(held, HOLD_IN + 0.6, "mcu", az=10, lens=37))
S.cam(l6[0] - 0.05, S.shot(held, l6[0] + 0.3, "cu", az=6, lens=30), S.shot(held, AH, "cu", az=5, lens=33))
S.cam(BOOM - 0.25, ((-2.4, -2.6, 1.3), (-2.6, 9.0, 3.2), 22), ((-2.6, -3.2, 1.25), (-2.6, 9.0, 3.2), 22),
      shake=lambda t: max(0.0, 2.6 - (t - BOOM) * 2.2) if t > BOOM else 0.0)
S.cam(BOOM + 1.3, ((-4.0, 4.4, 0.5), (-2.8, 7.6, 1.0), 24), ((-3.9, 4.6, 0.55), (-2.8, 7.6, 1.1), 26))

S.finish(length=END)
