"""D11 · Little brother, 2086 (script scène 11a-11h). Heuvel, winter, sneeuw.
11a  WIDE CAM_HEUVEL 3,5 s: op de bank hij (14) en een oude man van bijna 70 (broertje). Aan het eind van de bank twee
     bosjes bloemen in de sneeuw.  VO: "Mom and Dad are gone now."
11b  MEDIUM 3,8 s: de oude man legt een hand op zijn hoofd en woelt.  BROERTJE: "Look at you. Still my little brother."
11c  CLOSE 4,2 s: JONGEN: "I'm older than you."  BROERTJE: "Not where it counts."
11c2 WIDE CAM_HEUVEL 4,3 s: het broertje haalt een papieren zak snoep tevoorschijn en geeft hem de helft.
     VO: "Sixty years ago, he wanted you to get his football off the roof."
11d  DETAIL 4 s: de oude man geeft hem een vergeelde foto van zijn 14e verjaardag.  VO: "He kept it for sixty years. Just for you."
11e  CLOSE trage push-in 4 s: hij kijkt naar de foto, zijn duim gaat over mama's gezicht. Geen VO: tik en wind.
11f  CLOSE broertje 2,6 s: "Don't forget us, okay?"
11g  CLOSE 5 s: JONGEN: "Never."  VO: "That's a promise you can't keep. You just don't know it yet."
11h  DETAIL 2 s: sneeuw valt op het horloge in zijn hand. Tik.

    python3 anim/v4/scenes/d11_heuvel.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d11", "heuvel", "2086", exposure=0.15)
sh = S.cuts([3.5, 3.8, 4.2, 4.3, 4.0, 4.0, 2.6, 5.0, 2.0])
END = sh[-1][1]
t_b, t_c, t_c2, t_d, t_e, t_f, t_g, t_h = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True
REPO_ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

SEAT = 0.50                                            # zitting met sneeuw
H_AT = V(0.62, -0.02, 0.0)
B_AT = V(-0.18, -0.04, 0.0)
held = S.actor("hoofdpersonage_kind", H_AT, 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, H_AT + V(0, 0, hz_), 180)
broer = S.actor("broertje_oud", B_AT, 180)
bs, bz = sit(broer, seat_top=SEAT)
S.place(broer, 0, B_AT + V(0, 0, bz), 180)
HH = S.head(held)
BH = S.head(broer)
CITY = V(0.0, 60.0, 5.0)
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST_R = arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST = arms(REST_L, REST_R)

# ---------------------------------------------------------------- vallende sneeuw rond de bank (cyclisch)
rnd = random.Random(86)
sm = S.mat("sneeuwvlok", (0.97, 0.98, 1.0))
flakes = []
for k in range(220):
    x, y = rnd.uniform(-2.2, 2.4), rnd.uniform(-2.0, 2.2)
    f = T.sphere(f"Sneeuwvlok_{k}", (x, y, 0), rnd.uniform(0.008, 0.016), sm, seg=6, ol=0)
    per = rnd.uniform(4.5, 7.0)
    off = rnd.uniform(0, per)
    for t, z in ((0.0, 3.2), (per, 0.0)):
        f.location = (x + 0.15 * math.sin(k), y, z)
        f.keyframe_insert("location", index=2, frame=F(t - off))
    for fc in A._fcurves(f):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.modifiers.new("CYCLES")

# ---------------------------------------------------------------- 11a-11c: samen op de bank
S.beat(held, 0.0, **hs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(broer, 0.0, **bs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(broer, t_b, **bs, arms=REST, face="blij", face_amt=0.7, at=HH)
TOP = HH + V(-0.02, 0.0, 0.27)
S.reach(broer, t_b + 0.1, "R", None, 0.0)
S.reach(broer, t_b + 0.6, "R", TOP)
for k, t in enumerate(frange(t_b + 0.8, t_b + 2.4, 0.2)):
    S.reach(broer, t, "R", TOP + V(0.05 if k % 2 else -0.05, 0.03, 0.0))
S.reach(broer, t_b + 2.8, "R", None, 0.0)
S.beat(broer, t_b + 1.2, **bs, arms=REST, face="lach", face_amt=0.8, at=HH)
S.beat(held, t_b + 0.5, **hs, arms=REST, face="twijfel", face_amt=0.6, at=BH, body={"head": (6, 0, -8)})
S.beat(held, t_b + 1.8, **hs, arms=REST, face="grijns", face_amt=0.6, at=BH)
S.beat(held, t_c, **hs, arms=REST, face="zelfverzekerd", face_amt=0.6, at=BH)          # "I'm older than you."
S.beat(broer, t_c + 1.9, **bs, arms=REST, face="lach", face_amt=0.6, at=HH, body={"head": (0, 0, 6)})
S.beat(held, t_c + 2.6, **hs, arms=REST, face="blij", face_amt=0.5, at=BH)

# ---------------------------------------------------------------- 11c2: de zak snoep (staat in de set op de bank)
zak = bpy.data.objects["Snoepzak"]
BAG = V(-0.55, 0.05, 0.55)
S.beat(broer, t_c2, **bs, arms=REST, face="blij", face_amt=0.6, at=CITY)
S.reach(broer, t_c2 + 0.2, "L", None, 0.0)
S.reach(broer, t_c2 + 0.8, "L", BAG + V(0, 0, 0.1))
grab(S, zak, broer, t_c2 + 0.9, "hand.L", loc=(0, 0.07, -0.08), rot=(0, 0, 0), release=t_d)
GIVE = (HH + BH) * 0.5 + V(0, 0.38, -0.75)
S.reach(broer, t_c2 + 1.8, "L", GIVE + V(-0.12, 0, 0))
S.reach(held, t_c2 + 2.2, "L", None, 0.0)
S.reach(held, t_c2 + 2.7, "L", GIVE + V(0.04, 0, 0.12))
S.reach(held, t_c2 + 3.4, "L", GIVE + V(0.04, 0, 0.12))
S.reach(held, t_c2 + 3.9, "L", None, 0.0)
S.reach(broer, t_c2 + 3.9, "L", None, 0.0)
S.beat(held, t_c2 + 2.0, **hs, arms=REST, face="blij", face_amt=0.7, at=GIVE)
S.beat(broer, t_c2 + 2.0, **bs, arms=REST, face="blij", face_amt=0.7, at=HH)
for o in [zak] + list(zak.children_recursive):
    show(o, 0.0, t_d)                                   # daarna weggelegd (buiten beeld)

# ---------------------------------------------------------------- 11d-11e: de vergeelde foto
img = os.path.join(REPO_, "assets", "props", "gezinsfoto_14e_verjaardag.png")
foto = ND.oude_foto("Gezinsfoto", (0, 0, 0), rot=(0, 0, 0), image=img if os.path.exists(img) else None, vergeling=0.5)
foto.scale = (1.6,) * 3
PH = HH + V(0.0, 0.42, -0.58)                          # voor zijn borst, schuin naar zijn gezicht
FROT = (36, 0, 0)                                     # vlak naar zijn gezicht gekanteld
key(foto, 0.0, loc=tuple(PH + V(-0.32, 0.05, 0.0)), rot=FROT, scale=1.6)
key(foto, t_d, loc=tuple(PH + V(-0.32, 0.05, 0.0)), rot=FROT)
key(foto, t_d + 1.2, loc=tuple(PH), rot=FROT)
S.reach(broer, t_d, "R", PH + V(-0.32 + 0.12, 0.05, 0.0))
S.reach(broer, t_d + 1.2, "R", PH + V(0.12 - 0.05, 0.0, 0.0))
S.reach(broer, t_d + 1.8, "R", None, 0.0)
S.reach(held, t_d + 0.9, "L", PH + V(-0.12, 0, 0))
S.reach(held, t_d + 0.9, "R", PH + V(0.12, 0, 0))
S.reach(held, t_e + 1.2, "R", PH + V(0.12, 0, 0))
S.reach(held, t_e + 2.2, "R", PH + V(0.02, 0.0, 0.02))          # duim over mama's gezicht
S.reach(held, t_e + 3.2, "R", PH + V(0.04, 0.0, 0.02))
S.reach(held, t_f, "L", PH + V(-0.12, 0, 0))
S.reach(held, t_f + 0.4, "L", None, 0.0)
S.reach(held, t_f, "R", PH + V(0.04, 0.0, 0.02))
S.reach(held, t_f + 0.4, "R", None, 0.0)
show(foto, t_d, t_f + 0.2)
S.beat(held, t_d, **hs, arms=REST, face="verbaasd", face_amt=0.6, at=PH)
S.beat(held, t_e, **hs, arms=REST, face="verdrietig", face_amt=0.5, at=PH)
S.beat(held, t_e + 2.5, **hs, arms=REST, face="verdrietig", face_amt=0.7, at=PH)
S.beat(broer, t_d, **bs, arms=REST, face="blij", face_amt=0.5, at=PH)
S.beat(broer, t_e, **bs, arms=REST, face="blij", face_amt=0.5, at=HH)

# ---------------------------------------------------------------- 11f-11h
S.beat(broer, t_f, **bs, arms=REST, face="verdrietig", face_amt=0.4, at=HH)
S.beat(broer, t_f + 1.0, **bs, arms=REST, face="blij", face_amt=0.4, at=HH, body={"head": (4, 0, 5)})   # "Don't forget us"
S.hold(broer, END)
A.blink_at(broer, F(t_f + 1.8))
S.beat(held, t_f, **hs, arms=REST, face="verdrietig", face_amt=0.5, at=BH)
S.beat(held, t_g, **hs, arms=REST, face="zelfverzekerd", face_amt=0.5, at=BH)          # "Never."
S.beat(held, t_g + 1.4, **hs, arms=REST, face="blij", face_amt=0.4, at=BH)
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
S.beat(held, t_g + 3.4, **hs, arms=arms(REST_L, LOOKH), face="neutraal", face_amt=0.5, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.hold(held, END)
A.blink_at(held, F(t_g + 0.6))
hw = S.watch(held, t_g + 3.0, side="R", name="Zakhorloge", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3)
for o in [hw] + list(hw.children_recursive):
    show(o, t_g + 3.0)
S.watch_hands("Zakhorloge", t_g + 3.0, END, every=1.0)
# een paar vlokken die op het horloge landen
WP = S.bone_world(held, "hand.R", t_h + 0.5) + V(0, 0, 0.06)
for k in range(5):
    f = T.sphere(f"Vlok_horloge_{k}", (0, 0, 0), 0.007, sm, seg=6, ol=0)
    p = WP + V(rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03), 0.0)
    tl = t_h + 0.2 + k * 0.3
    key(f, 0.0, loc=tuple(p + V(0, 0, 1.2)), scale=1.0)
    key(f, tl - 0.9, loc=tuple(p + V(0, 0, 1.2)))
    key(f, tl, loc=tuple(p))
    key(f, END, loc=tuple(p), scale=0.6)

# ---------------------------------------------------------------- camera's
CAMH = (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22)
S.cam(0.0, CAMH)
MID = (HH + BH) * 0.5
S.cam(t_b, (MID + V(0.1, 2.5, -0.55), MID + V(0, 0, -0.25), 32), (MID + V(0.08, 2.35, -0.55), MID + V(0, 0, -0.25), 32))
S.cam(t_c, (MID + V(0.15, 1.8, -0.35), MID + V(0, 0, -0.12), 32), (MID + V(0.13, 1.7, -0.35), MID + V(0, 0, -0.12), 32))
S.cam(t_c2, CAMH)
HPd = S.headpos(held, t_d + 1.5)
CF = PH + V(0.5, 0.05, 0.3)
if (CF - HPd).length < 0.55:
    CF = HPd + (CF - HPd).normalized() * 0.55
print("DBG11", tuple(round(x, 2) for x in HH), tuple(round(x, 2) for x in HPd), tuple(round(x, 2) for x in PH), tuple(round(x, 2) for x in CF))
S.cam(t_d, (CF, PH, 32), (CF + (PH - CF) * 0.08, PH, 32))
S.cam(t_e, (HH + V(0.35, 1.25, -0.30), HH + V(0, 0, -0.15), 35), (HH + V(0.28, 0.95, -0.26), HH + V(0, 0, -0.15), 35))
S.cam(t_f, (BH + V(0.55, 0.95, -0.15), BH + V(0, 0, -0.12), 35), (BH + V(0.52, 0.88, -0.15), BH + V(0, 0, -0.12), 35))
S.cam(t_g, (HH + V(-0.5, 0.95, -0.15), HH + V(0, 0, -0.12), 35), (HH + V(-0.47, 0.88, -0.15), HH + V(0, 0, -0.12), 35))
S.cam(t_h, (WP + V(0.15, 0.40, 0.30), WP, 45), (WP + V(0.14, 0.37, 0.28), WP, 45))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(2086, t0=0.0, big=True)
S.jump(0.0)
S.say("D11-01", at=0.4)
S.say("D11-02", who=broer, at=t_b + 0.2)
S.say("D11-03", who=held, at=t_c + 0.1)
S.say("D11-04", who=broer, at=t_c + 2.2)
S.say("D11-05", at=t_c2 + 0.2)
S.say("D11-06", at=t_d + 0.3)
S.ticks(t_e + 0.3, t_f, every=1.0, vol=0.3)
S.say("D11-07", who=broer, at=t_f + 0.2)
S.say("D11-08", who=held, at=t_g + 0.15)
S.say("D11-09", at=t_g + 1.25)
S.tick(t_h + 0.9, 0.5)
S.ambience("sfx_wind_heuvel", 0.0, END, vol=0.14)
S.music("cello", 0.0, END, vol=0.15, fade_in=0.6, fade_out=0.6)
S.finish(length=END, tail=0.0)
