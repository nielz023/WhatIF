"""D14b · Tienduizend jaar: het museum (script scène 14b-a t/m 14b-d).
14b-a WIDE trage dolly 4 s: museumzaal; vitrines met telefoon, sneaker, fiets, en in de grootste: hij, op een krukje.
      VO: "Ten thousand years. Nobody speaks your language anymore."
14b-b DETAIL 3 s: het bordje: THE LAST OLD HUMAN. PLEASE DO NOT TAP THE GLASS.
14b-c MEDIUM 3,5 s: toekomstkinderen tikken tegen het glas. Hij zwaait. Ze gillen en rennen weg.  VO: "To them, you're basically a dinosaur."
14b-c2 MEDIUM 9,5 s (script v1.2, ~60%): ABONNEEROPROEP. Hij zit weer op zijn krukje (vlak achter het glas), kijkt in de
      camera, tikt zacht tegen het glas met een scheve grijns; een strak abonneer-hologram verschijnt op het glas.
      VO: "Quick thing, while you're stuck behind the glass with him: if you're enjoying this, hit subscribe. ..."
14b-d CLOSE 4 s: hij leunt met zijn wang tegen het glas en zucht; zijn adem maakt een wolkje.
      VO: "So you're the only person on the planet who remembers what a Tuesday was."  SFX: tik.

    python3 anim/v4/scenes/d14b_museum.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403
from lib import stad as SD  # noqa: E402

S = Scene4("d14b", "toekomst", "museum", exposure=0.1)
sh = S.cuts([4.4, 3.0, 3.6, 9.5, 4.9])                     # 14b-c2 = abonneeroproep (~60% van de video)
END = sh[-1][1]
t_b, t_c, t_s, t_d = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

GLAS_Y = 1.0 - 1.2                                         # voorkant van de grote vitrine
VX = 4.0
SEAT = 0.35 + 0.5                                          # sokkel + krukje

# ---------------------------------------------------------------- hij: op het krukje, zwaait, staat op en leunt tegen het glas
held = S.actor("hoofdpersonage_2200", (VX, 1.1, 0.35), 0)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, V(VX, 1.1, hz_), 0)
REST = arms(arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)), arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)))
S.beat(held, 0.0, **hs, arms=REST, face="neutraal", face_amt=0.4, look=(0.0, -0.2))
S.beat(held, t_b, **hs, arms=REST, face="neutraal", face_amt=0.4, look=(0.0, -0.2))
S.beat(held, t_c, **hs, arms=REST, face="verbaasd", face_amt=0.5, at=V(VX, -0.6, 1.0))
S.beat(held, t_c + 0.9, **hs, arms=arms(arm("R", (0.85, 0.20, 0.35), (0.35, 0.10, 0.95))), face="blij", face_amt=0.7,
       at=V(VX - 0.6, -0.6, 1.0))                                                       # zwaait
S.beat(held, t_c + 1.2, **hs, arms=arms(arm("R", (0.85, 0.20, 0.35), (-0.15, 0.10, 0.98))), face="blij", face_amt=0.8,
       at=V(VX - 0.6, -0.6, 1.0))
S.beat(held, t_c + 1.5, **hs, arms=arms(arm("R", (0.85, 0.20, 0.35), (0.35, 0.10, 0.95))), face="blij", face_amt=0.8,
       at=V(VX - 0.6, -0.6, 1.0))
S.beat(held, t_c + 2.2, **hs, arms=REST, face="twijfel", face_amt=0.7, at=V(VX - 2.5, -3.0, 1.0))
S.hold(held, t_s - 0.04)
# 14b-c2 abonneeroproep: krukje (harde cut) vlak achter het glas, hij kijkt in de camera en tikt tegen het glas
SY = GLAS_Y + 0.42
kruk = S.obj("Krukje")
K0 = tuple(kruk.location)
for t, y in ((0.0, K0[1]), (t_s, SY), (t_d, K0[1])):
    kruk.location = (K0[0], y, K0[2])
    kruk.keyframe_insert("location", frame=F(t))
for fc in kruk.animation_data.action.fcurves if hasattr(kruk.animation_data.action, "fcurves") else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
S.teleport(held, t_s, V(VX, SY, hz_), 0)
CAMS = V(VX + 0.1, GLAS_Y - 1.6, 1.45)
TAP = V(VX + 0.1, GLAS_Y + 0.04, 1.32)
S.beat(held, t_s, **hs, arms=REST, face="grijns", face_amt=0.5, at=CAMS)
S.reach(held, t_s + 0.6, "R", None, 0.0)
for j, t in enumerate(frange(t_s + 1.1, t_s + 1.75, 0.22)):
    S.reach(held, t, "R", TAP + V(0, 0.05 if j % 2 else 0.0, 0))
S.reach(held, t_s + 2.3, "R", None, 0.0)
S.beat(held, t_s + 0.9, **hs, arms=REST, face="grijns", face_amt=0.8, at=CAMS, body={"head": (0, 0, -6), "spine": (16, 0, 0)})
S.beat(held, t_s + 1.9, **hs, arms=REST, face="grijns", face_amt=0.8, at=CAMS, body={"head": (0, 0, -6), "spine": (16, 0, 0)})
S.beat(held, t_s + 3.0, **hs, arms=REST, face="blij", face_amt=0.6, at=CAMS)
S.beat(held, t_s + 4.6, **hs, arms=REST, face="blij", face_amt=0.8, at=CAMS, body={"head": (0, 0, 6)})
S.beat(held, t_s + 6.6, **hs, arms=REST, face="zelfverzekerd", face_amt=0.7, at=CAMS, body={"spine": (-4, 0, 0)})
S.beat(held, t_s + 8.4, **hs, arms=REST, face="grijns", face_amt=0.7, at=CAMS)
S.hold(held, t_d - 0.04)
# hologram-abonneerknop op het glas (0,3 s infade via schaal, geen flikkering)
HOLO_P = V(VX - 0.62, GLAS_Y - 0.02, 1.22)
holo_mat = T.glow("holo_abonneer", (0.95, 0.12, 0.10), 2.2)
holo = T.box("Holo_abonneer", tuple(HOLO_P), (0.5, 0.012, 0.14), holo_mat, bevel=0.06, ol=0, base=False)
holo_t = SD.label("Holo_abonneer_tekst", "SUBSCRIBE", (HOLO_P.x, HOLO_P.y - 0.045, HOLO_P.z - 0.03), 0.08,
                  col=(1, 1, 1), glow=2.5, extrude=0.002)
T_HOLO = t_s + 4.1
key(holo, 0.0, loc=tuple(HOLO_P), scale=0.001)
key(holo, T_HOLO, loc=tuple(HOLO_P), scale=0.001)
key(holo, T_HOLO + 0.3, loc=tuple(HOLO_P), scale=1.0)
key(holo, t_s + 9.1, loc=tuple(HOLO_P), scale=1.0)
key(holo, t_s + 9.4, loc=tuple(HOLO_P), scale=0.001)
HT = tuple(holo_t.location)
key(holo_t, 0.0, loc=HT, scale=0.001)
key(holo_t, T_HOLO, loc=HT, scale=0.001)
key(holo_t, T_HOLO + 0.3, loc=HT, scale=1.0)
key(holo_t, t_s + 9.1, loc=HT, scale=1.0)
key(holo_t, t_s + 9.4, loc=HT, scale=0.001)
show(holo, T_HOLO - 0.02, t_s + 9.42)
show(holo_t, T_HOLO - 0.02, t_s + 9.42)
# 14b-d: staat tegen het glas (eigen houding, harde cut)
LEAN = V(VX - 0.35, 0.25, 0.35)
S.teleport(held, t_d, LEAN, 0)
S.beat(held, t_d, "staan", face="verdrietig", face_amt=0.4, look=(0.6, -0.1), body={"head": (0, 0, 24), "spine": (8, 0, 0)})
S.hold(held, END)
HD = S.head(held, t_d + 0.2)
shift = (HD.y - 0.30) - (GLAS_Y + 0.03)                   # wang tegen de binnenkant van het glas
S.teleport(held, t_d, LEAN - V(0, shift, 0), 0)
S.beat(held, t_d, "staan", face="verdrietig", face_amt=0.4, look=(0.6, -0.1), body={"head": (0, 0, 24), "spine": (8, 0, 0)})
S.beat(held, t_d + 1.6, "staan", face="verdrietig", face_amt=0.5, look=(0.6, -0.1), mouth=0.5,
       body={"head": (0, 0, 24), "spine": (12, 0, 0)})                                     # zucht
S.beat(held, t_d + 2.4, "staan", face="verdrietig", face_amt=0.4, look=(0.6, -0.1), mouth=0.05,
       body={"head": (0, 0, 24), "spine": (8, 0, 0)})
S.hold(held, END)
HD = S.head(held, t_d + 1.6)
S.eyes_closed(held, t_d + 1.4, t_d + 2.3)
# het wolkje adem op het glas
adem = T.cyl("Adem_wolkje", (0, 0, 0), 0.09, 0.002, ND.pbr("adem_glas", (0.92, 0.95, 0.98)), seg=24, ol=0)
adem.rotation_euler = (math.radians(90), 0, 0)
AP = V(HD.x + 0.05, GLAS_Y + 0.005, HD.z - 0.12)
key(adem, 0.0, loc=tuple(AP), scale=0.001)
key(adem, t_d + 1.6, loc=tuple(AP), scale=0.001)
key(adem, t_d + 2.0, loc=tuple(AP), scale=1.0)
key(adem, END, loc=tuple(AP), scale=0.7)

# ---------------------------------------------------------------- toekomstkinderen tikken tegen het glas
KIDS = [("museumkind_a", V(VX - 1.05, GLAS_Y - 0.36, 0)), ("museumkind_b", V(VX + 1.05, GLAS_Y - 0.36, 0)),
        ("museumkind_c", V(VX - 0.4, GLAS_Y - 1.05, 0))]
kids = []
for k, (name, p) in enumerate(KIDS):
    ch = S.actor(name, p, 180)
    show(ch.rig, t_c - 0.04, t_s)
    kids.append(ch)
    S.beat(ch, 0.0, "staan", face="blij", face_amt=0.7, at=V(VX, 1.1, 1.3))
    if k < 2:                                                                    # tik tik tegen het glas
        side = "R" if k == 0 else "L"
        G = V(p.x + (0.12 if k == 0 else -0.12), GLAS_Y - 0.03, 0.95)
        for j, t in enumerate(frange(t_c + 0.1, t_c + 0.9, 0.18)):
            S.reach(ch, t, side, G + V(0, -0.06 if j % 2 else 0.0, 0))
        S.reach(ch, t_c + 1.05, side, None, 0.0)
    S.beat(ch, t_c + 1.0, "staan", face="blij", face_amt=0.9, at=S.head(held, t_c + 1.0))
    S.beat(ch, t_c + 1.35, "schrik", face="schreeuw", face_amt=1.0, at=S.head(held, t_c + 1.35))
    away = [p, p + V(-2.4 - 0.4 * k, -0.9, 0), p + V(-6.0 - 0.6 * k, -2.2, 0)]
    S.run(ch, t_c + 1.6, t_c + 3.4, away, stride=0.5)
    S.hold(ch, t_s)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-9.5, -6.2, 2.4), V(3.0, 1.5, 1.4), 22), (V(-4.0, -4.0, 2.0), V(3.8, 1.0, 1.4), 24))
S.cam(t_b, (V(4.0, -1.6, 0.85), V(4.0, -0.25, 0.65), 45), (V(4.0, -1.35, 0.82), V(4.0, -0.25, 0.65), 45))
S.cam(t_c, (V(1.2, -3.5, 1.4), V(4.0, 0.2, 1.2), 30), (V(1.3, -3.3, 1.4), V(4.0, 0.2, 1.2), 30))
HS = S.headpos(held, t_s + 0.5)
S.cam(t_s, (V(VX - 0.05, GLAS_Y - 2.3, HS.z - 0.1), HS + V(0, 0, -0.3), 30),
      (V(VX - 0.05, GLAS_Y - 1.95, HS.z - 0.1), HS + V(0, 0, -0.28), 30))
S.cam(t_d, (HD + V(0.4, -1.6, -0.02), HD + V(0, -0.15, -0.12), 28), (HD + V(0.35, -1.42, -0.02), HD + V(0, -0.15, -0.12), 30))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(10000, t0=0.0, big=True)
S.jump(0.0)
S.say("D14b-01", at=0.2)
S.say("D14b-02", at=t_c + 0.4)
S.say("D14b-04", at=t_s + 0.3)                            # abonneeroproep (script v1.2, vervangt D14b-00)
S.say("D14b-03", at=t_d + 0.2)
for t in frange(t_c + 0.1, t_c + 0.9, 0.18):
    S.sfx("sfx_hout_klop", t, 0.12)
S.sfx("sfx_kinderen_spelen", t_c + 1.35, 0.15)
for t in frange(t_s + 1.1, t_s + 1.75, 0.22):
    S.sfx("sfx_hout_klop", t + 0.06, 0.08)
S.sfx("sfx_adem_hijgen", t_d + 1.5, 0.12)
S.tick(END - 0.3, 0.45)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.06)
S.music("speels", 0.0, END, vol=0.13, fade_in=0.4, fade_out=0.6)
S.finish(length=END, tail=0.0)
