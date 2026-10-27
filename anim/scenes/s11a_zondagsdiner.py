"""S11a · Dag 10 · zondagsdiner met opa en oma: de hand die hij niet schudt, de knuffel met de ellebogen.

    blender -b -P anim/scenes/s11a_zondagsdiner.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s11a", "keuken", "zondagsdiner")

TX, TY, TZ = 0.2, -0.6, 0.76
DOOR = V(-2.2, 0.95, 0)
OMA_AT = V(TX - 1.72, TY, 0)                  # kopse kant links, kijkt naar +x
OPA_AT = V(TX - 0.7, TY + 0.62, 0)            # achter de tafel, links
PAPA_AT = V(TX + 0.0, TY + 0.62, 0)
BRO_AT = V(TX + 1.72, TY, 0)                  # kopse kant rechts
HERO_AT = V(-1.22, -0.02, 0)                  # tussen oma en opa in, achter de tafelhoek
HUG_AT = V(-1.3, -0.2, 0)

# de stoelen vooraan weg (open voor de camera), de kopse stoelen naar de tafel
for k in (1, 2, 3):
    S.obj(f"Stoel_{k}").hide_render = True
    for o in bpy.data.objects:
        if o.name.startswith(f"Bord_{k}_"):
            o.hide_render = True
S.obj("Stoel_kop_1").rotation_euler.z = math.radians(90)
S.obj("Stoel_kop_2").rotation_euler.z = math.radians(-90)
chair = S.obj("Stoel_4")                      # opa's stoel: hij draait hem naar ons toe

# ---------------------------------------------------------------- figuren
oma = S.actor("oma", OMA_AT, 90, energy=1.0)
opa = S.actor("opa", OPA_AT, -20, energy=1.0)
papa = S.actor("papa", PAPA_AT, 0, energy=0.9)
bro = S.actor("broertje", BRO_AT, -90, energy=0.9)
held = S.actor("hoofdpersonage", DOOR, 120)
SIT_OMA, zo = sit(oma)
SIT_OPA, zp = sit(opa)
SIT_PAPA, zpa = sit(papa)
SIT_BRO, zb = sit(bro)
S.place(oma, 0, (OMA_AT.x, OMA_AT.y, zo), 90)
S.place(opa, 0, (OPA_AT.x, OPA_AT.y, zp), -20)
S.place(papa, 0, (PAPA_AT.x, PAPA_AT.y, zpa), 0)
S.place(bro, 0, (BRO_AT.x, BRO_AT.y, zb), -90)
chair.hide_render = False
chair.rotation_euler.z = math.radians(-20)

# ---------------------------------------------------------------- tijdlijn
S.hud(10, "1,024x STRONGER", t0=0.4)
S.music("piano_warm", 0.0, 60, vol=0.26, fade_in=0.8, fade_out=0.6)
PIANO = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.08)
l1 = S.say("S11-01", gap=0.6)
l2 = S.say("S11-02", gap=0.4)
l3 = S.say("S11-03", gap=0.5)
OFFER = l3[0] + 2.5                           # 'Grandpa holds out his hand.'
NOSHAKE = l3[0] + 4.7
WAVE = l3[0] + 6.9
l4 = S.say("S11-04", who=opa, gap=0.3, gain=1.15)
l5 = S.say("S11-05", gap=0.3)
l6 = S.say("S11-06", who=oma, gap=0.4, gain=1.15)
l7 = S.say("S11-07", gap=0.3)
HUG = l7[0] + 1.2
ELBOWS = l7[0] + 3.65
S.wait(0.9)
END = S.t
PIANO["loop_to"] = END + 0.3
S.sfx("sfx_hud_tik", WAVE - 0.05, 0.3)            # klein komisch tikje bij het zwaaitje

S.gauge("GRIP: 46 TONS", l2[0] + 0.8, l2[1] + 0.3)
S.text("= A FULLY LOADED TRUCK", l2[0] + 3.0, l2[1] + 0.3, loc=(0.965, 0.14), size=48, color=GOLD, anchor=("RIGHT", "BOTTOM"))
S.gauge("FINGERS SAVED: 5", l5[0] + 1.3, l5[1] + 0.4)
S.gauge("HUG FORCE: 0.0001%", ELBOWS - 0.2, END)

# ---------------------------------------------------------------- de familie aan tafel
S.beat(papa, 0.0, **SIT_PAPA, pose="ontspannen", face="blij", face_amt=0.5, at=S.head(opa, 0))
S.beat(papa, l1[0] + 2.2, **SIT_PAPA, pose="ontspannen", face="blij", face_amt=0.6, at=HERO_AT + V(0, 0, 1.0))
S.beat(papa, l4[0] + 0.4, **SIT_PAPA, pose="ontspannen", face="lach", face_amt=0.5, at=S.head(opa, 0))
S.beat(papa, HUG + 0.3, **SIT_PAPA, pose="ontspannen", face="lach", face_amt=0.7, at=HUG_AT + V(0, 0, 0.9))
S.hold(papa, END)
S.beat(bro, 0.0, **SIT_BRO, pose="ontspannen", face="blij", face_amt=0.4, at=V(TX, TY, TZ + 0.1))
S.beat(bro, l1[0] + 2.5, **SIT_BRO, pose="ontspannen", face="grijns", face_amt=0.6, at=HERO_AT + V(0, 0, 1.0))
S.beat(bro, WAVE + 0.4, **SIT_BRO, pose="ontspannen", face="lach", face_amt=0.9, at=HERO_AT + V(0, 0, 1.0), body={"chest": (-6, 0, 0)})
S.beat(bro, l5[1], **SIT_BRO, pose="ontspannen", face="grijns", face_amt=0.6, at=S.head(opa, 0))
S.beat(bro, HUG + 0.4, **SIT_BRO, pose="ontspannen", face="lach", face_amt=0.8, at=HUG_AT + V(0, 0, 0.9))
S.hold(bro, END)

# ---------------------------------------------------------------- hij komt binnen, kijkt naar zijn hand
S.beat(held, 0.0, "ontspannen", face="blij", face_amt=0.5, at=S.head(oma, 0))
S.walk(held, 0.2, l1[0] + 2.6, [DOOR, V(-1.75, 0.55, 0), HERO_AT], end_rot=-15)
S.beat(held, l2[0] + 0.2, "staan", face="nerveus", face_amt=0.5, at=None, look=(0.1, -0.3),
       arms=arms(arm("R", (0.2, 0.4, -0.85), (-0.1, 0.7, 0.7)), arm("L", (0.1, 0.0, -1.0), (0.05, 0.1, -1.0))))
for k in range(3):                            # langzaam vuist maken en weer open
    t = l2[0] + 1.0 + k * 1.6
    S.beat(held, t, "staan", face="nerveus", face_amt=0.6, look=(0.1, -0.3), hold=0.5,
           arms=arms(arm("R", (0.2, 0.4, -0.85), (-0.1, 0.7, 0.7)), arm("L", (0.1, 0.0, -1.0), (0.05, 0.1, -1.0))))
S.beat(held, l2[1] - 0.2, "staan", face="neutraal", face_amt=0.5, at=S.head(opa, l2[1]))

# opa steekt zijn hand uit
S.beat(opa, 0.0, **SIT_OPA, pose="ontspannen", face="blij", face_amt=0.4, at=S.head(oma, 0))
S.beat(opa, l1[0] + 2.2, **SIT_OPA, pose="ontspannen", face="blij", face_amt=0.7, at=S.head(held, l1[1]))
S.beat(opa, OFFER - 0.3, **SIT_OPA, pose="ontspannen", face="blij", face_amt=0.8, at=S.head(held, OFFER), body={"chest": (0, -14, 0)},
       arms=HAND_OUT_R)
S.hold(opa, NOSHAKE + 1.4)
S.beat(opa, WAVE + 0.2, **SIT_OPA, pose="ontspannen", face="twijfel", face_amt=0.9, at=S.head(held, WAVE), body={"chest": (0, -14, 0)},
       arms=arm("R", (0.15, 0.7, -0.6), (0.0, 0.8, -0.2)))
S.beat(opa, l4[0] - 0.1, **SIT_OPA, pose="armen_over", face="boos", face_amt=0.6, at=S.head(held, l4[0]), body={"head": (6, 0, 0)})
S.beat(opa, l4[0] + 1.6, **SIT_OPA, pose="armen_over", face="boos", face_amt=0.8, look=(0.3, 0.2), body={"head": (8, -20, 0)})
S.beat(opa, l5[1], **SIT_OPA, pose="armen_over", face="twijfel", face_amt=0.6, at=S.head(held, l5[1]))
S.beat(opa, HUG + 0.5, **SIT_OPA, pose="ontspannen", face="verbaasd", face_amt=0.6, at=HUG_AT + V(0, 0, 0.9))
S.hold(opa, END)

# hij schudt hem niet: kijkt naar de hand, het rare zwaaitje
S.beat(held, OFFER, "staan", face="blij", face_amt=0.4, at=S.head(opa, OFFER))
S.beat(held, NOSHAKE - 0.3, "staan", face="nerveus", face_amt=0.9, at=S.head(opa, OFFER) + V(0.35, -0.25, -0.45), body={"chest": (-4, 0, 0)})
S.beat(held, NOSHAKE + 0.8, "staan", face="nerveus", face_amt=1.0, at=S.head(opa, OFFER), arms=arm("R", (0.12, 0.2, -0.95), (0.1, 0.25, -0.95)))
S.beat(held, WAVE, "staan", face="grijns", face_amt=0.7, at=S.head(opa, WAVE), arms=WAVE_SMALL_R)
S.beat(held, WAVE + 0.35, "staan", face="grijns", face_amt=0.8, at=S.head(opa, WAVE), arms=WAVE_SMALL_R2)
S.beat(held, WAVE + 0.7, "staan", face="grijns", face_amt=0.8, at=S.head(opa, WAVE), arms=WAVE_SMALL_R)
S.beat(held, WAVE + 1.05, "staan", face="grijns", face_amt=0.8, at=S.head(opa, WAVE), arms=WAVE_SMALL_R2)
S.beat(held, l4[0] + 0.6, "staan", face="nerveus", face_amt=0.7, at=S.head(opa, l4[0]))
S.beat(held, l5[0] + 0.5, "schouders_op", amount=0.6, face="grijns", face_amt=0.6, at=S.head(opa, l5[0]))
S.beat(held, l6[0] + 0.3, "staan", face="blij", face_amt=0.5, at=S.head(oma, l6[0]))
S.turn(held, l6[0] + 0.5, l6[0] + 1.2, heading(HERO_AT, OMA_AT), HERO_AT)

# oma: 'Then come give your grandma a hug, sweetheart.'
OPEN_L = arm("L", (0.75, 0.55, -0.2), (0.55, 0.75, 0.25))
OPEN_R = arm("R", (0.75, 0.55, -0.2), (0.55, 0.75, 0.25))
S.beat(oma, 0.0, **SIT_OMA, pose="ontspannen", face="blij", face_amt=0.5, at=S.head(opa, 0))
S.beat(oma, l1[0] + 2.0, **SIT_OMA, pose="ontspannen", face="blij", face_amt=0.8, at=S.head(held, l1[1]))
S.beat(oma, l4[0] + 0.5, **SIT_OMA, pose="ontspannen", face="twijfel", face_amt=0.5, at=S.head(opa, l4[0]), wenkbrauw_op=0.5)
S.beat(oma, l6[0] - 0.1, **SIT_OMA, pose="ontspannen", face="lach", face_amt=0.8, at=S.head(held, l6[0]), body={"chest": (0, 25, 0)},
       arms=arms(OPEN_L, OPEN_R))
S.hold(oma, HUG - 0.2)
# de zachtste knuffel ooit, met de ellebogen
ELB_L = arm("L", (0.55, 0.8, 0.05), (-0.15, -0.3, 0.94))
ELB_R = arm("R", (0.55, 0.8, 0.05), (-0.15, -0.3, 0.94))
S.walk(held, l6[1] - 0.3, HUG - 0.1, [HERO_AT, HUG_AT], end_rot=heading(HUG_AT, OMA_AT))
HUG_CAM = V(0.0, -1.9, 1.35)
S.beat(held, HUG, "staan", face="nerveus", face_amt=1.0, at=HUG_CAM, crouch=(0.12, 18), arms=arms(ELB_L, ELB_R))
S.beat(held, ELBOWS, "staan", face="inspanning", face_amt=0.6, at=HUG_CAM, crouch=(0.14, 22), arms=arms(ELB_L, ELB_R),
       ogen_knijp=0.6)
S.hold(held, END - 0.5)
S.beat(held, END, "staan", face="grijns", face_amt=0.6, at=HUG_CAM, crouch=(0.1, 14), arms=arms(ELB_L, ELB_R))
S.beat(oma, HUG, **SIT_OMA, pose="ontspannen", face="lach", face_amt=1.0, at=S.head(held, HUG), body={"chest": (0, 35, 0)},
       arms=arms(arm("L", (0.6, 0.6, 0.1), (-0.2, 0.9, 0.3)), arm("R", (0.6, 0.6, 0.1), (-0.2, 0.9, 0.3))))
S.beat(oma, ELBOWS + 0.3, **SIT_OMA, pose="ontspannen", face="blij", face_amt=1.0, at=S.head(held, HUG), body={"chest": (0, 35, 0)},
       arms=arms(arm("L", (0.6, 0.6, 0.1), (-0.2, 0.9, 0.3)), arm("R", (0.6, 0.6, 0.1), (-0.2, 0.9, 0.3))), ogen_knijp=0.8)
S.hold(oma, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-0.3, -4.4, 1.75), (-0.5, 0.2, 0.95), 22), ((-0.5, -4.1, 1.7), (-0.8, 0.2, 0.95), 24))
HC = S.head(held, l2[0])
S.cam(l2[0] - 0.1, ((-0.85, -1.6, 1.45), HC + V(0, 0, -0.2), 34), ((-0.9, -1.45, 1.42), HC + V(0, 0, -0.22), 40))
S.cam(l3[0] - 0.1, ((-0.6, -3.0, 1.3), (-0.95, 0.0, 0.95), 30), ((-0.65, -2.8, 1.3), (-0.95, 0.0, 0.95), 32))
S.cam(NOSHAKE - 0.4, ((-0.85, -1.6, 1.45), HC + V(0, 0, -0.1), 38), ((-0.88, -1.5, 1.45), HC + V(0, 0, -0.1), 42))
S.cam(WAVE - 0.3, ((-0.75, -2.6, 1.25), (-0.95, 0.0, 0.95), 30), ((-0.78, -2.55, 1.25), (-0.95, 0.0, 0.95), 30))
S.cam(l4[0] - 0.1, S.shot(opa, l4[0], "mcu", az=25, lens=32), S.shot(opa, l4[1], "mcu", az=20, lens=36))
S.cam(l5[0] - 0.1, ((-0.8, -1.9, 1.4), HC + V(0, 0, -0.25), 32), ((-0.82, -1.8, 1.4), HC + V(0, 0, -0.25), 34))
S.cam(l6[0] - 0.1, S.shot(oma, l6[0], "mcu", az=-50, lens=32), S.shot(oma, l6[1], "mcu", az=-45, lens=36))
S.cam(HUG - 0.4, (tuple(HUG_CAM), (-1.35, -0.35, 1.15), 32), ((-0.05, -1.8, 1.33), (-1.35, -0.35, 1.15), 36))

S.finish(length=END)
