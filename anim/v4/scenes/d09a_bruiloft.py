"""D09a · De bruiloft, 2051 (script scène 9a-9c2). Bruiloftstuin, middag.
9a  WIDE 5,2 s, trage push: de beste vriend (grijze slapen) trouwt; hij staat ernaast als getuige, in een te groot pak,
    met het ringkussentje.  VO: "Your best friend gets married. You're the best man. Everyone thinks you're the ring boy."
9b  MEDIUM 2,6 s: een oude tante knijpt in zijn wang.  TANTE: "Aren't you adorable!"
9c  CLOSE 5,3 s: mama en papa aan een tafel, allebei grijs. Mama zwaait naar hem, ze ziet er moe uit.
    VO: "And for the first time, you notice it. Mom gets tired faster than you do."
9c2 MEDIUM 6 s: papa staat op voor een speech, zoekt een woord, glimlacht verontschuldigend. Mama legt haar hand op zijn arm.
    VO: "Twenty-five years. For them, that's half a life. For you, it's a long weekend."

    python3 anim/v4/scenes/d09a_bruiloft.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d09a", "kleine_nd", "bruiloft", exposure=0.15)
sh = S.cuts([5.2, 2.6, 5.3, 6.0])
END = sh[-1][1]
t_b, t_c, t_c2 = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- bij de boog: bruidegom, bruid, getuige
ARCH_Y = 5.2
groom = S.actor("beste_vriend_40", (0.42, ARCH_Y, 0), -12)
bride = S.actor("figurant_f", (-0.42, ARCH_Y, 0), 12, label="bruid")
held = S.actor("hoofdpersonage_pak", (1.25, ARCH_Y - 0.55, 0), -20)
HH = S.head(held)
# ringkussentje in beide handen
kus = T.box("Ringkussen", (0, 0, 0), (0.16, 0.16, 0.05), S.mat("kussen_satijn", (0.95, 0.93, 0.98)), bevel=0.02, ol=0)
ring = T.torus("Ringkussen_ring", (0, 0, 0.035), 0.018, 0.004, S.mat("goud_ring", (1.0, 0.8, 0.3), 0.2), rot=(90, 0, 0), seg=16, seg2=6, ol=0)
ring.parent = kus
grab(S, kus, held, 0.0, "hand.R", loc=(-0.06, 0.07, 0.04), rot=(0, 0, 0))
CUSH = arms(arm("L", (0.25, 0.55, -0.80), (-0.35, 0.92, 0.10)), arm("R", (0.25, 0.55, -0.80), (-0.35, 0.92, 0.10)))

S.beat(groom, 0.0, "staan", face="blij", face_amt=0.9, at=S.head(bride) + V(0, 0, -0.05))
S.beat(groom, 2.6, "staan", face="lach", face_amt=0.8, at=S.head(bride))
S.hold(groom, END)
S.beat(bride, 0.0, "staan", face="blij", face_amt=1.0, at=S.head(groom))
S.hold(bride, END)
A.blink_at(groom, F(1.5))
A.blink_at(bride, F(3.2))

S.beat(held, 0.0, "staan", arms=CUSH, face="zelfverzekerd", face_amt=0.7, at=V(0.0, -3.0, 1.4))
S.beat(held, 2.8, "staan", arms=CUSH, face="twijfel", face_amt=0.6, at=V(-1.5, 1.0, 1.0))      # gasten wijzen naar zijn kussentje
S.teleport(held, t_b, (1.25, ARCH_Y - 0.55, 0), 35)                         # draait naar de tante (snede)
S.beat(held, t_b, "staan", arms=CUSH, face="twijfel", face_amt=0.5, at=V(2.4, 4.0, 1.6))
S.beat(held, t_b + 0.7, "staan", arms=CUSH, face="geschrokken", face_amt=0.7, at=V(2.4, 4.0, 1.7), body={"head": (0, 0, -10)})
S.beat(held, t_b + 1.6, "staan", arms=CUSH, face="nerveus", face_amt=0.8, at=V(2.3, 4.1, 1.7), body={"head": (0, 0, -14)})
S.hold(held, t_c)

# gasten op de voorste stoelen (rug naar de camera)
for k, (name, x, y) in enumerate((("figurant_a", -1.2, 3.0), ("figurant_b", 1.8, 3.0), ("figurant_c", -2.4, 2.0),
                                  ("figurant_d", 1.2, 2.0))):
    g = S.actor(name, (x, y, 0), 180)
    gs, gz = sit(g, seat_top=0.45)
    S.place(g, 0, V(x, y - 0.05, gz), 180)
    S.beat(g, 0.0, **gs, face="blij", face_amt=0.7, at=V(0, ARCH_Y, 1.5))
    S.beat(g, 2.8 + 0.2 * k, **gs, face="lach", face_amt=0.8, at=HH + V(0, 0, -0.3))
    S.hold(g, t_b)
    show(g.rig, 0.0, t_b)
    S.qc_skip.add(g.name)

# ---------------------------------------------------------------- 9b: de oude tante
tante = S.actor("tante", (1.92, ARCH_Y - 0.92, 0), -120)
show(tante.rig, t_b, t_c)
TF = S.head(tante)
S.beat(tante, t_b, "staan", face="blij", face_amt=1.0, at=HH, crouch=(0.03, 7))
CHEEK = HH + V(0.20, -0.18, -0.10)
S.reach(tante, t_b + 0.1, "R", None, 0.0)
S.reach(tante, t_b + 0.45, "R", CHEEK)
for k, t in enumerate(frange(t_b + 0.6, t_c - 0.3, 0.18)):
    S.reach(tante, t, "R", CHEEK + V(0.0, 0.0, 0.025 if k % 2 else -0.02))
S.reach(tante, t_c - 0.05, "R", CHEEK)
S.hold(tante, t_c)

# ---------------------------------------------------------------- 9c/9c2: mama en papa aan tafel (tafel x -6, y -6)
TX, TY = -6.0, -6.0
cm = S.mat("hout_stoel_wit", (0.95, 0.95, 0.93))
for k, dx in enumerate((-0.5, 0.5)):
    T.box(f"Tafelstoel_{k}", (TX + dx, TY + 1.15, 0), (0.45, 0.45, 0.45), cm, bevel=0.02, ol=0)
mama = S.actor("mama_grijs", (TX - 0.5, TY + 1.15, 0), 0)
ms, mz = sit(mama, seat_top=0.45)
S.place(mama, 0, V(TX - 0.5, TY + 1.12, mz), 0)
papa = S.actor("papa_grijs", (TX + 0.5, TY + 1.15, 0), 0)
ps, pz = sit(papa, seat_top=0.45)
S.place(papa, 0, V(TX + 0.5, TY + 1.12, pz), 0)
for ch in (mama, papa):
    show(ch.rig, t_c)
glas = T.cyl("Champagneglas", (TX + 0.55, TY + 0.75, 0.76), 0.03, 0.17, T.glass("glas_champagne", (0.95, 0.9, 0.7), 0.3), seg=12, ol=0)
HERO_FAR = V(TX + 2.6, TY - 3.6, 1.2)           # waar hij staat (buiten beeld, aan onze kant)
REST = arms(arm("L", (0.35, 0.55, -0.76), (0.10, 0.95, 0.10)), arm("R", (0.35, 0.55, -0.76), (0.10, 0.95, 0.10)))
WAVE_A = arms(arm("L", (0.35, 0.55, -0.76), (0.10, 0.95, 0.10)), arm("R", (0.50, 0.35, -0.10), (0.15, 0.25, 0.95)))
WAVE_B = arms(arm("L", (0.35, 0.55, -0.76), (0.10, 0.95, 0.10)), arm("R", (0.50, 0.35, -0.10), (0.55, 0.25, 0.80)))
S.beat(mama, t_c, **ms, arms=REST, face="blij", face_amt=0.7, at=HERO_FAR)
for k, t in enumerate(frange(t_c + 0.6, t_c + 2.2, 0.3)):
    S.beat(mama, t, **ms, arms=WAVE_A if k % 2 else WAVE_B, face="blij", face_amt=0.8, at=HERO_FAR)
S.beat(mama, t_c + 2.6, **dict(ms, crouch=(ms["crouch"][0], 10)), arms=REST, face="verdrietig", face_amt=0.35, at=HERO_FAR + V(0, 0, -0.6),
       body={"head": (8, 0, 6)})                                                       # moe: zakt een beetje in
S.eyes_closed(mama, t_c + 3.4, t_c + 3.9)
S.beat(mama, t_c + 4.3, **dict(ms, crouch=(ms["crouch"][0], 10)), arms=REST, face="blij", face_amt=0.4, at=HERO_FAR)
S.beat(papa, t_c, **ps, arms=REST, face="blij", face_amt=0.6, at=S.head(mama))
S.beat(papa, t_c + 1.5, **ps, arms=REST, face="lach", face_amt=0.6, at=HERO_FAR)
# 9c2: papa staat (snede), glas in de hand, zoekt een woord
S.teleport(papa, t_c2, V(TX + 0.25, TY + 1.05, 0), 0)
S.beat(papa, t_c2, "staan", arms=arms(arm("R", (0.35, 0.40, -0.85), (-0.05, 0.75, 0.66))), face="blij", face_amt=0.7,
       at=V(TX + 0.5, TY - 4.0, 1.8))
grab(S, glas, papa, t_c2, "hand.R", loc=(0, 0.06, 0.02), rot=(0, 0, 0))
S.beat(papa, t_c2 + 1.4, "staan", arms=arms(arm("R", (0.35, 0.40, -0.85), (-0.05, 0.75, 0.66))), face="twijfel", face_amt=0.8,
       at=V(TX + 1.5, TY - 3.0, 3.2), body={"head": (-10, 0, 8)})                           # zoekt naar een woord
S.beat(papa, t_c2 + 2.8, "staan", arms=arms(arm("R", (0.35, 0.40, -0.85), (-0.05, 0.75, 0.66))), face="nerveus", face_amt=0.7,
       at=V(TX, TY - 4.0, 1.7), body={"head": (6, 0, -6)})
S.beat(papa, t_c2 + 4.0, "staan", arms=arms(arm("R", (0.35, 0.40, -0.85), (-0.05, 0.75, 0.66))), face="blij", face_amt=0.6,
       at=S.head(mama, t_c2), body={"head": (8, 0, 0)})                                   # verontschuldigende glimlach
S.hold(papa, END)
S.beat(mama, t_c2, **ms, arms=REST, face="blij", face_amt=0.5, at=S.head(papa, t_c2 + 1.0))
S.reach(mama, t_c2 + 2.6, "R", None, 0.0)
S.reach(mama, t_c2 + 3.2, "R", S.bone_world(papa, "forearm.R", t_c2 + 3.2) + V(0.04, -0.05, 0.0))
S.reach(mama, END, "R", S.bone_world(papa, "forearm.R", t_c2 + 3.2) + V(0.04, -0.05, 0.0))
S.beat(mama, t_c2 + 3.2, **ms, face="verdrietig", face_amt=0.3, at=S.head(papa, t_c2 + 3.2))
S.hold(mama, END)
A.blink_at(papa, F(t_c + 1.0))

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(0.0, -3.0, 1.7), V(0.3, 6.0, 1.3), 28), (V(0.05, 0.3, 2.0), V(0.4, 6.0, 1.15), 28))
S.cam(t_b, (V(0.75, 3.0, 1.4), (HH + TF) * 0.5 + V(0, 0, -0.15), 32), (V(0.8, 3.1, 1.39), (HH + TF) * 0.5 + V(0, 0, -0.15), 32))
MP = (S.head(mama, t_c) + S.head(papa, t_c)) * 0.5
S.cam(t_c, (MP + V(-0.6, -1.9, -0.05), MP + V(0, 0, -0.1), 35), (MP + V(-0.5, -1.7, -0.05), MP + V(0, 0, -0.1), 35))
PP = S.head(papa, t_c2 + 2.0)
S.cam(t_c2, (V(TX - 1.35, TY - 0.45, 1.6), V(TX - 0.05, TY + 1.15, 1.2), 30), (V(TX - 1.25, TY - 0.4, 1.6), V(TX - 0.05, TY + 1.15, 1.2), 30))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2051, t0=0.0, big=True)
S.jump(0.0)
S.say("D09-01", at=0.3)
S.say("D09-02", who=tante, at=t_b + 0.35)
S.say("D09-03", at=t_c + 0.2)
S.say("D09-04", at=t_c2 + 0.1)
S.sfx("sfx_glas_klink", t_c2 + 0.3, 0.25)
S.ambience("sfx_bruiloft_sfeer", 0.0, END, vol=0.1)
S.music("strijkers_warm", 0.0, END, vol=0.16, fade_in=0.4, fade_out=0.4)
S.finish(length=END, tail=0.0)
