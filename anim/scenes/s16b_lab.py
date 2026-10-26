"""S16b · Dag 15 · het lab: duizend ton in de hydraulische pers, met één hand open, terwijl hij een appje beantwoordt.
'Does it stop?' 'We don't know.'

    blender -b -P anim/scenes/s16b_lab.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s16b", "lab", "lab")

PX, PY = 0.0, 3.5
TOP = 1.05                                      # perstafel
HERO_AT = V(PX, PY - 0.15, TOP)
SCI_AT = V(2.15, 1.6, 0.0)
GY0 = 1.0 - 14.0 / 2

# ---------------------------------------------------------------- de pers opnieuw opbouwen met een bewegende plaat
for n in ("Hydraulische_pers", "Pers_label"):
    S.obj(n).hide_render = True
grey = S.mat("pers_grijs", (0.55, 0.58, 0.64))
blue = S.mat("pers_blauw", (0.12, 0.40, 0.85))
chrome = S.mat("pers_chroom", (0.85, 0.88, 0.92))
steel = S.mat("pers_staal", (0.75, 0.78, 0.82))
T.box("Pers2_voet", (PX, PY, 0), (3.2, 2.4, 0.8), grey, bevel=0.05, ol=0.02)
T.box("Pers2_tafel", (PX, PY, 0.8), (2.4, 1.8, 0.25), steel, bevel=0.03, ol=0.02)
T.box("Pers2_kop", (PX, PY, 4.2), (3.4, 2.4, 1.0), blue, bevel=0.08, ol=0.02)
for x in (-1.45, 1.45):
    for y in (-0.95, 0.95):
        T.cyl(f"Pers2_kolom_{x}_{y}", (PX + x, PY + y, 0.8), 0.16, 3.5, chrome, seg=16, ol=0.02)
T.box("Pers2_waarschuwing", (PX, PY - 1.21, 4.4), (2.6, 0.02, 0.4), S.mat("waarschuwing", (0.98, 0.80, 0.08)), bevel=0, ol=0)
lbl = T.text("Pers2_label", "1,000 TON", (PX, PY - 1.25, 4.5), 0.3, S.mat("zwart_label", (0.05, 0.05, 0.05)), extrude=0.01)
plate = T.box("Pers2_plaat", (0, 0, 0), (2.0, 1.5, 0.2), steel, bevel=0.02, ol=0.02)
piston = T.cyl("Pers2_zuiger", (0, 0, 0), 0.45, 1.0, chrome, seg=24, ol=0.02)
piston.rotation_euler.x = math.radians(180)    # hangt omlaag vanaf de kop
piston.location = (PX, PY, 4.2)
HIGH, HELD = 3.1, 2.08                          # onderkant plaat: open, en op zijn hand


def plate_at(t, z):
    key(plate, t, loc=(PX, PY, z))
    key(piston, t, scale=(1, 1, 4.2 - (z + 0.2)))


held = S.actor("hoofdpersonage", HERO_AT, 0)
sci = S.actor("wetenschapper", SCI_AT, heading(SCI_AT, HERO_AT), energy=1.1)
SIT, _ = sit(held, seat_top=0.0, lean=-4, spread=0.14)
phone = prop_phone(S, "Zijn_telefoon", (0, 0, 0), screen=(0.5, 0.75, 1.0))
phone.scale = (1.7,) * 3
attach(phone, held, "hand.R", (0, 0.06, 0.02), (90, 0, 0))

# ---------------------------------------------------------------- tijdlijn
S.hud(15, "32,768x STRONGER", t0=0.0, tick=False)
S.music("drone", 0.0, 60, vol=0.26, fade_in=0.3, fade_out=0.05)
DRONE = S.sounds[-1]
S.ambience("sfx_binnen_sfeer", 0.0, 60, vol=0.06)
l3 = S.say("S16-03", gap=0.4)
PRESS0 = l3[0] + 1.9
TONS = l3[0] + 4.55                             # 'A thousand tons.'
CONTACT = l3[0] + 5.6
ONEHAND = l3[0] + 7.6                           # 'You hold it open. With one hand.'
TEXT = l3[0] + 8.85                             # 'While answering a text.'
S.sfx("sfx_pers", PRESS0 - 0.1, 0.6)
S.sfx("sfx_dreun", CONTACT - 0.03, 0.3)
S.sfx("sfx_meldingen", TEXT + 0.2, 0.3)
l4 = S.say("S16-04", who=sci, gap=0.6, gain=1.15)
HEART = l4[0] + 6.5
l5 = S.say("S16-05", gap=0.6)
ASK = l5[0] + 4.05                              # 'Does it stop?'
l6 = S.say("S16-06", who=sci, gap=1.4, gain=1.15)
DRONE["loop_to"] = l6[0] - 0.9                  # stilte op 'We don't know.'
S.wait(1.6)
END = S.t

S.gauge("PRESS: 1,000 TONS", TONS, l3[1] + 0.4, color=(1.0, 0.45, 0.2, 1))
S.text("BONE DENSITY ↑", l4[0] + 1.0, l4[1] + 0.2, loc=(0.965, 0.30), size=46, color=CYAN, anchor=("RIGHT", "BOTTOM"))
S.text("MUSCLE · SKIN · BLOOD VESSELS ↑", l4[0] + 3.6, l4[1] + 0.2, loc=(0.965, 0.22), size=44, color=CYAN, anchor=("RIGHT", "BOTTOM"))

# ---------------------------------------------------------------- de pers
plate_at(0.0, HIGH)
plate_at(PRESS0, HIGH)
plate_at(CONTACT, HELD)
for k in range(int((END - CONTACT) / 0.7)):
    plate_at(CONTACT + 0.35 + k * 0.7, HELD + (0.004 if k % 2 else -0.002))

# ---------------------------------------------------------------- hij: zit op de perstafel, één hand omhoog, appt
UP_L = arm("L", (0.25, 0.05, 0.97), (0.15, 0.05, 0.99))
TEXTING = arm("R", (0.15, 0.45, -0.88), (-0.35, 0.75, 0.55))
S.beat(held, 0.0, **SIT, pose="ontspannen", face="neutraal", face_amt=0.5, look=(0, 0.5), arms=TEXTING)
S.beat(held, PRESS0 + 0.4, **SIT, pose="ontspannen", face="twijfel", face_amt=0.5, look=(0, 0.7), arms=TEXTING, body={"head": (-12, 0, 0)})
S.beat(held, CONTACT - 0.5, **SIT, pose="ontspannen", face="neutraal", face_amt=0.4, look=(0, 0.7), body={"head": (-12, 0, 0)},
       arms=arms(UP_L, TEXTING))
S.beat(held, CONTACT + 0.4, **SIT, pose="ontspannen", face="neutraal", face_amt=0.3, look=(0.2, -0.5), arms=arms(UP_L, TEXTING), body={"head": (10, 0, 0)})
S.beat(held, TEXT, **SIT, pose="ontspannen", face="blij", face_amt=0.4, look=(0.2, -0.5), arms=arms(UP_L, TEXTING), body={"head": (12, 0, 0)})
t = TEXT + 0.2
while t < l4[0]:                                # duimen tikken
    S.beat(held, t, **SIT, pose="ontspannen", face="blij", face_amt=0.4, look=(0.2, -0.5), arms=arms(UP_L, arm("R", (0.15, 0.45, -0.88), (-0.33, 0.77, 0.55))), body={"head": (12, 0, 0)})
    t += 0.35
S.beat(held, l4[0] + 0.5, **SIT, pose="ontspannen", face="neutraal", face_amt=0.5, at=S.head(sci, l4[0]), arms=arms(UP_L, TEXTING))
S.beat(held, HEART, **SIT, pose="ontspannen", face="nerveus", face_amt=0.7, at=S.head(sci, l4[0]), arms=arms(UP_L, TEXTING))
S.beat(held, l5[0] + 0.4, **SIT, pose="ontspannen", face="verdrietig", face_amt=0.5, look=(0, -0.4), arms=arms(UP_L, TEXTING), body={"head": (8, 0, 0)})
S.beat(held, ASK - 0.3, **SIT, pose="ontspannen", face="bang", face_amt=0.6, at=S.head(sci, ASK), arms=arms(UP_L, TEXTING))
S.beat(held, l6[1], **SIT, pose="ontspannen", face="bang", face_amt=0.9, at=S.head(sci, ASK), arms=arms(UP_L, TEXTING))
S.hold(held, END)

# wetenschapper
S.beat(sci, 0.0, "staan", face="zelfverzekerd", face_amt=0.6, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.beat(sci, CONTACT + 0.3, "staan", face="verbaasd", face_amt=0.8, at=S.head(held, 0) + V(0, 0, 0.6), arms=HOLD_FRONT_L, wenkbrauw_op=0.8)
S.beat(sci, TEXT + 0.4, "staan", face="geschrokken", face_amt=0.6, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.beat(sci, l4[0] + 0.2, "staan", face="nerveus", face_amt=0.8, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.beat(sci, l4[0] + 3.5, "handen_zij", amount=0.4, face="nerveus", face_amt=0.9, at=S.head(held, 0))
S.beat(sci, HEART, "staan", face="bang", face_amt=0.5, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.beat(sci, l5[1], "staan", face="verdrietig", face_amt=0.5, look=(0, -0.4), arms=HOLD_FRONT_L, body={"head": (10, 0, 0)})
S.beat(sci, l6[0] + 0.3, "staan", face="verdrietig", face_amt=0.8, at=S.head(held, 0), arms=HOLD_FRONT_L)
S.hold(sci, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((-5.0, -4.2, 2.3), (PX, PY, 1.7), 22), ((-4.4, -3.6, 2.2), (PX, PY, 1.7), 24))
S.cam(PRESS0 - 0.3, ((5.5, -5.0, 2.6), (PX, PY, 2.0), 22), ((5.0, -4.4, 2.5), (PX, PY, 2.0), 24))
S.cam(CONTACT - 0.3, ((PX + 1.1, PY - 2.6, 1.9), (PX + 0.1, PY - 0.1, 1.8), 32), ((PX + 1.0, PY - 2.4, 1.9), (PX + 0.1, PY - 0.1, 1.8), 34),
      shake=lambda t: max(0.0, 0.8 - (t - CONTACT) * 2.0) if t > CONTACT else 0.0)
S.cam(TEXT - 0.2, S.shot(held, TEXT, "mcu", az=-20, lens=32, up=0.15), S.shot(held, l3[1] + 0.4, "mcu", az=-14, lens=36, up=0.15))
S.cam(l4[0] - 0.2, S.shot(sci, l4[0], "mcu", az=-25, lens=32, lr=-0.3), S.shot(sci, HEART, "mcu", az=-20, lens=36, lr=-0.3))
S.cam(HEART, ((2.5, 4.5, 1.6), (4.3, 7.9, 1.6), 30), ((2.6, 5.0, 1.6), (4.3, 7.9, 1.6), 34))
S.cam(l5[0] - 0.2, S.shot(held, l5[0], "cu", az=-25, lens=34), S.shot(held, l5[1], "cu", az=-20, lens=40))
S.cam(l6[0] - 1.0, S.shot(sci, l6[0], "cu", az=-25, lens=36), S.shot(sci, END, "cu", az=-20, lens=42))

S.finish(length=END)
