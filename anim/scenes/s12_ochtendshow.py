"""S12 · Dag 11 · ochtendshow: 'Can you crush a diamond?' Hij knijpt, de diamant ontploft in glitter. Live.

    blender -b -P anim/scenes/s12_ochtendshow.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s12", "tvstudio", "studio")

FLOOR = 0.35                                   # podium
HOST_AT = V(-0.62, 2.35, FLOOR)
HERO_AT = V(0.42, 2.2, FLOOR)
anchor = S.actor("nieuwslezeres", HOST_AT, 45, energy=1.1)
held = S.actor("hoofdpersonage", HERO_AT, -50)

# de ring: gouden band met een diamant
gold = S.mat("ring_goud", (1.0, 0.78, 0.25), 0.6)
ring = T.torus("Verlovingsring", (0, 0, 0), 0.022, 0.005, gold, seg=24, seg2=8, ol=0.0015)
ring.rotation_euler = (math.radians(90), 0, 0)
gem = T.sphere("Diamant", (0, 0, 0.028), 0.013, S.mat("diamant", (0.85, 0.95, 1.0), 4.0), scale=(1, 1, 1.25), seg=6, ol=0.0015)
gem.parent = ring
gem.matrix_parent_inverse = ring.matrix_world.inverted()

# ---------------------------------------------------------------- tijdlijn
S.hud(11, "2,048x STRONGER", t0=0.4)
S.music("jingle", 0.0, 60, vol=0.3, fade_in=0.2, fade_out=0.05)
JINGLE = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.08)
S.sfx("sfx_publiek", 0.1, 0.35)
l1 = S.say("S12-01", gap=0.6)
l2 = S.say("S12-02", who=anchor, gap=0.35, gain=1.15)
GIVE = l2[1] - 0.2
l3 = S.say("S12-03", gap=0.5)
HARD = l3[0] + 1.7
TOUGH = l3[0] + 5.0
GLASS = l3[0] + 7.6
l4 = S.say("S12-04", gap=0.4)
SQUEEZE = l4[0] + 0.1
EXPLODE = l4[0] + 3.35                          # 'It explodes.'
GLITTER = l4[0] + 4.7
LIVE = l4[0] + 6.05
JINGLE["loop_to"] = EXPLODE - 0.05
S.sfx("sfx_diamant", EXPLODE - 0.02, 0.9)
l5 = S.say("S12-05", who=anchor, gap=0.6, gain=1.15)
MY = l5[0] + 2.95                               # '...my engagement ring.'
l6 = S.say("S12-06", gap=0.5)
S.wait(1.0)
END = S.t

S.real(l3[0] + 0.05, l3[1] + 0.2)
S.text("HARDNESS: 10/10", HARD, l3[1] + 0.2, loc=(0.965, 0.30), size=48, color=WHITE, anchor=("RIGHT", "BOTTOM"))
S.text("TOUGHNESS: LOW", TOUGH, l3[1] + 0.2, loc=(0.965, 0.22), size=48, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.text("= SPLITS LIKE GLASS", GLASS, l3[1] + 0.2, loc=(0.965, 0.14), size=48, color=(1.0, 0.45, 0.4, 1), anchor=("RIGHT", "BOTTOM"))
S.text("● LIVE", LIVE, END, loc=(0.965, 0.94), size=60, color=(1.0, 0.25, 0.2, 1), anchor=("RIGHT", "TOP"))

# ---------------------------------------------------------------- de ring wisselt van hand en ontploft
grab(S, ring, anchor, 0.0, "hand.R", loc=(0, 0.06, 0.0), mode="loc", release=GIVE)
grab(S, ring, held, GIVE, "hand.R", loc=(0, 0.05, 0.0), mode="loc", release=EXPLODE)
show(ring, 0.0, EXPLODE)
show(gem, 0.0, EXPLODE)

# ---------------------------------------------------------------- presentatrice
RING_UP = arm("R", (0.25, 0.35, -0.2), (0.0, 0.45, 0.9))            # ring omhoog voor de camera
OFFER = arm("R", (0.15, 0.85, -0.45), (0.0, 1.0, 0.1))
S.beat(anchor, 0.0, "staan", face="lach", face_amt=0.8, look=(0, 0), arms=RING_UP)
S.beat(anchor, l1[0] + 2.0, "staan", face="blij", face_amt=0.9, at=S.head(held, 0), arms=RING_UP)
S.beat(anchor, l2[0] + 0.1, "staan", face="lach", face_amt=0.7, look=(0, 0), body={"head": (0, 0, -6)}, arms=RING_UP)
S.beat(anchor, l2[0] + 1.6, "staan", face="zelfverzekerd", face_amt=0.8, at=S.head(held, l2[0]), arms=OFFER)
S.hold(anchor, GIVE + 0.1)
S.beat(anchor, GIVE + 0.5, "handen_zij", amount=0.4, face="blij", face_amt=0.8, at=S.head(held, GIVE))
S.beat(anchor, SQUEEZE + 0.6, "staan", face="verbaasd", face_amt=0.5, at=S.head(held, SQUEEZE), arms=CLAP_A)
S.beat(anchor, EXPLODE + 0.05, "schrik", face="geschrokken", face_amt=1.0, at=S.head(held, EXPLODE))
S.beat(anchor, GLITTER, "handen_hoofd", amount=0.7, face="geschrokken", face_amt=1.0, look=(0.3, 0.3))
S.beat(anchor, LIVE, "staan", face="nerveus", face_amt=0.9, look=(-0.4, -0.1), body={"head": (0, 0, -20)})
S.beat(anchor, l5[0] - 0.2, "staan", face="nerveus", face_amt=1.0, at=S.head(held, l5[0]), arms=arm("R", (0.2, 0.5, -0.8), (0.0, 0.8, 0.5)))
S.beat(anchor, MY - 0.3, "staan", face="verdrietig", face_amt=1.0, look=(0, -0.4), arms=arm("R", (0.2, 0.5, -0.8), (0.0, 0.8, 0.5)), body={"head": (14, 0, 0)})
S.beat(anchor, l6[0] + 0.3, "staan", face="verdrietig", face_amt=0.8, at=S.head(held, l6[0]))
S.hold(anchor, END)

# ---------------------------------------------------------------- hij
HOLD_UP = arm("R", (0.3, 0.55, -0.6), (-0.25, 0.55, 0.8))         # ring tussen de vingers, voor zijn gezicht
TAKE = arm("R", (0.2, 0.85, -0.4), (-0.05, 1.0, 0.15))
S.beat(held, 0.0, "staan", face="blij", face_amt=0.6, look=(0.2, 0.0))
S.beat(held, l1[0] + 2.2, "staan", face="nerveus", face_amt=0.5, at=S.head(anchor, 0), body={"head": (0, 0, -10)})
S.beat(held, l2[0] + 0.4, "staan", face="blij", face_amt=0.5, at=S.head(anchor, l2[0]))
S.beat(held, GIVE - 0.4, "staan", face="blij", face_amt=0.6, at=S.head(anchor, GIVE), arms=TAKE)
S.beat(held, GIVE + 0.6, "staan", face="neutraal", face_amt=0.5, at=S.head(held, 0) + V(0.15, -0.35, -0.1), arms=HOLD_UP)
S.beat(held, HARD, "staan", face="verbaasd", face_amt=0.5, at=S.head(held, 0) + V(0.15, -0.35, -0.1), arms=HOLD_UP, wenkbrauw_op=0.5)
S.beat(held, TOUGH, "staan", face="twijfel", face_amt=0.6, at=S.head(held, 0) + V(0.15, -0.35, -0.1), arms=HOLD_UP)
S.beat(held, GLASS, "staan", face="nerveus", face_amt=0.6, at=S.head(anchor, GLASS), arms=HOLD_UP)
# knijpen: twee handen eromheen
PINCH = arms(arm("R", (0.25, 0.75, -0.55), (-0.45, 0.8, 0.35)), arm("L", (0.25, 0.75, -0.55), (-0.45, 0.8, 0.35)))
S.beat(held, SQUEEZE, "staan", face="vastberaden", face_amt=0.7, at=S.head(held, 0) + V(0.1, -0.45, -0.3), arms=PINCH)
S.beat(held, SQUEEZE + 1.0, "staan", face="inspanning", face_amt=0.4, at=S.head(held, 0) + V(0.1, -0.45, -0.3), arms=PINCH, ogen_knijp=0.3)
S.beat(held, EXPLODE - 0.3, "staan", face="inspanning", face_amt=0.2, at=S.head(held, 0) + V(0.1, -0.45, -0.3), arms=PINCH)
S.beat(held, EXPLODE + 0.05, "schrik", face="geschrokken", face_amt=1.0, at=S.head(held, 0) + V(0.1, -0.45, -0.1))
S.beat(held, GLITTER + 0.2, "staan", face="verbaasd", face_amt=1.0, look=(0, 0.6), arms=LOOK_HANDS)
S.beat(held, LIVE, "staan", face="nerveus", face_amt=1.0, look=(0, 0), arms=LOOK_HANDS)
S.beat(held, l5[0] + 0.4, "staan", face="nerveus", face_amt=0.8, at=S.head(anchor, l5[0]))
S.beat(held, MY + 0.2, "staan", face="geschrokken", face_amt=0.8, at=S.head(anchor, MY), arms=arms(arm("L", (0.1, 0.3, -0.95), (0.1, 0.5, -0.8))))
S.beat(held, l6[0] + 0.2, "schouders_op", amount=0.5, face="grijns", face_amt=0.6, look=(0, 0))
S.hold(held, END)

# glitter: de diamant spat uiteen en dwarrelt langzaam omlaag
bpy.context.scene.frame_set(F(EXPLODE - 0.04))
bpy.context.view_layer.update()
BOOM = ring.matrix_world.translation.copy()
sparkle = S.mat("glitter", (0.85, 0.95, 1.0), 6.0)
gold_g = S.mat("glitter_goud", (1.0, 0.8, 0.3), 4.0)
S.debris(BOOM, EXPLODE, n=70, size=(0.004, 0.012), speed=(0.6, 2.4), up=0.9, floor=FLOOR + 0.01, life=3.5, mat=sparkle, name="Glitter")
S.debris(BOOM, EXPLODE, n=30, size=(0.004, 0.01), speed=(0.4, 1.6), up=1.2, floor=FLOOR + 0.01, life=3.5, mat=gold_g, name="Glitter_goud")
S.puff(BOOM, EXPLODE, n=5, r=(0.04, 0.12), grow=3.0, dur=1.0, color=(0.92, 0.96, 1.0), rise=0.2, spread=0.2)
flash = T.point_light("Diamantflits", tuple(BOOM), color=(0.9, 0.95, 1.0), energy=0, radius=0.02)
for t, e in ((EXPLODE - 0.04, 0), (EXPLODE, 400), (EXPLODE + 0.3, 0)):
    flash.data.energy = e
    flash.data.keyframe_insert("energy", frame=F(t))
# dwarrelende glitter in de lucht (langzaam vallende puntjes)
rnd = random.Random(12)
drift = [V(rnd.uniform(-1.4, 1.4), rnd.uniform(1.4, 3.2), rnd.uniform(1.2, 2.6)) for _ in range(140)]
dm = P.points_mesh("Glitter_dwarrel", [tuple(p) for p in drift], 0.006, sparkle, seg=4)
key(dm, 0, loc=(0, 0, 0))
key(dm, GLITTER - 0.6, loc=(0, 0, 0.3))
key(dm, END, loc=(0, 0, -0.9))
show(dm, GLITTER - 0.6)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.3, -9.0, 3.2), (0.0, 3.0, 1.4), 22), ((0.2, -7.5, 2.8), (0.0, 3.0, 1.35), 26))
S.cam(l2[0] - 0.1, S.shot(anchor, l2[0], "mcu", az=-25, lens=32), S.shot(anchor, l2[1], "mcu", az=-20, lens=36))
S.cam(GIVE - 0.6, ((-0.05, -0.9, 1.6), (-0.1, 2.3, 1.45), 30), ((-0.05, -0.6, 1.6), (-0.1, 2.3, 1.45), 32))
HC3 = S.headpos(held, l3[0] + 1.0)
S.cam(l3[0] + 0.9, (HC3 + V(-0.5, -1.0, 0.02), HC3 + V(0, 0, -0.04), 34), (HC3 + V(-0.42, -0.86, 0.02), HC3 + V(0, 0, -0.04), 40))
S.cam(TOUGH + 0.4, ((-0.05, -0.4, 1.6), (-0.1, 2.3, 1.45), 30), ((-0.05, -0.2, 1.6), (-0.1, 2.3, 1.45), 32))
HC4 = S.headpos(held, SQUEEZE)
S.cam(SQUEEZE - 0.1, (HC4 + V(-0.75, -1.55, -0.05), HC4 + V(0, 0, -0.2), 34), (HC4 + V(-0.45, -0.95, 0.0), HC4 + V(0, 0, -0.08), 40))
S.cam(EXPLODE, ((0.1, -0.2, 1.6), (-0.05, 2.3, 1.45), 28), ((0.1, -0.4, 1.6), (-0.05, 2.3, 1.45), 26),
      shake=lambda t: max(0.0, 2.0 - (t - EXPLODE) * 3.0) if t > EXPLODE else 0.0)
S.cam(LIVE - 0.2, ((1.0, -4.9, 1.75), (0.0, 2.3, 1.15), 34), ((0.9, -4.7, 1.75), (0.0, 2.3, 1.15), 40))
S.cam(l5[0] - 0.1, S.shot(anchor, l5[0], "mcu", az=-20, lens=34), S.shot(anchor, l5[1], "cu", az=-16, lens=40))
S.cam(l6[0] - 0.1, S.shot(held, l6[0], "cu", az=-20, lens=36), S.shot(held, END, "cu", az=-16, lens=40))

S.finish(length=END)
