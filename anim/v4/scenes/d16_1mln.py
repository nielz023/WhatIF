"""D16 · Een miljoen jaar: achtergelaten (script scène 16a-16h). Woeste groene vlakte, grazers, kolonieschepen.
16a  WIDE CAM_HEUVEL push 3,5 s: in de verte stijgen drie enorme schepen op.  VO: "A million years. Humans are leaving Earth for good."
16b  MEDIUM push-in 7 s (hier 2 shots): bij de loopplank een lange toekomstmens; ze schudt haar hoofd.
     VO: "You ask for a seat. Just one."  TOEKOMSTMENS: "Every seat is for someone with a lifetime. You have... all of them."
16c  CLOSE 3 s: JONGEN: "So you're just leaving me here?" De loopplank schuift omhoog voor hij antwoord krijgt.
16c2 DETAIL 4,5 s: scherm op het schip: GOODBYE, EARTH, aftelling springt op nul.
     VO: "Three hundred thousand years of human history. And they leave it with you."
16d  WIDE LOW 4 s: het laatste schip stijgt op; de luchtdruk blaast tegen hem aan. Geen VO.
16e  WIDE CAM_HEUVEL 3 s: hij alleen op de heuvel, dieren grazen beneden.  VO: "Now you're the only human on Earth."
16f  DETAIL 4 s: op de bankvoet repareert hij het horloge met een doorn en een plat steentje; tong tussen zijn tanden.
     VO: "So you sit down, and you fix the only thing you have left."
16g  DETAIL 2,5 s: de secondewijzer schokt. Tik. Het horlogethema komt terug.
16h  CLOSE 3 s: hij glimlacht voor het eerst in duizenden jaren.  VO: "Tick."

    python3 anim/v4/scenes/d16_1mln.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d16", "heuvel", "1mln", exposure=0.15)
sh = S.cuts([4.4, 3.0, 5.6, 3.2, 5.0, 4.0, 3.2, 4.3, 2.6, 3.0])
END = sh[-1][1]
t_b, t_b1, t_c, t_c2, t_d, t_e, t_f, t_g, t_h = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True

VALLEY = -44.05
# ---------------------------------------------------------------- de drie kolonieschepen stijgen op
for k in range(3):
    o = bpy.data.objects.get(f"Kolonieschip_{k}")
    if o is None:
        continue
    z0 = o.location.z
    key(o, 0.0, loc=tuple(o.location))
    key(o, t_d, loc=(o.location.x, o.location.y, z0 + 900 + 200 * k))
    key(o, END, loc=(o.location.x, o.location.y, z0 + 1600 + 200 * k))
    for fc in A._fcurves(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "QUAD"
            kp.easing = "EASE_IN"

# ---------------------------------------------------------------- het schip met de loopplank
SHIP = bpy.data.objects.get("Schip_loopplank")
plank = bpy.data.objects.get("Loopplank_plank")
ANG = math.atan2(3.5, 10.0)
d = V(math.sin(math.radians(-20)), -math.cos(math.radians(-20)), 0)        # van het schip naar de voet van de plank
B = V(32.5, 130.0, VALLEY) + d * (10.0 * math.cos(ANG))                     # voet van de loopplank
if plank:
    for t, a in ((0.0, -ANG), (t_c + 0.8, -ANG), (t_c + 2.8, math.radians(80))):
        plank.rotation_euler.x = a
        plank.keyframe_insert("rotation_euler", index=0, frame=F(t))
# aftelling op het scherm
w = 150 * 0.22
orig = bpy.data.objects.get("Schip_loopplank_scherm_tekst1")
if orig:
    orig.hide_render = orig.hide_viewport = True
tels = []
for k, txt in enumerate(["00:00:03", "00:00:02", "00:00:01", "00:00:00"]):
    lb = ND.S.label(f"Aftelling_{k}", txt, (0, -w * 0.47 - 0.2, 150 * 0.45 + w * (0.2 - 0.11)), w * 0.05, (0.9, 0.95, 1.0),
                    glow=6.0, extrude=0.05)
    lb.parent = SHIP
    t0 = t_c2 + 0.6 + k * 0.7
    show(lb, t0, None if k == 3 else t0 + 0.7)
# het schip stijgt op (16d), met een eigen vuurstaart
vm = ND.pbr("schip_loopplank_vlam", (1.0, 0.6, 0.2), emit=(1.0, 0.55, 0.18), strength=25.0)
vlam = T.cyl("Schip_loopplank_vlamstaart", (0, 0, -150 * 0.6), w * 0.12, 150 * 0.6, vm, r2=w * 0.3, seg=24, ol=0)
vlam.parent = SHIP
show(vlam, t_d + 0.3)
S0 = SHIP.location.copy()
key(SHIP, 0.0, loc=tuple(S0))
key(SHIP, t_d + 0.4, loc=tuple(S0))
key(SHIP, END, loc=tuple(S0 + V(0, 0, 700)))
for fc in A._fcurves(SHIP):
    for kp in fc.keyframe_points:
        kp.interpolation = "QUAD"
        kp.easing = "EASE_IN"
key(vlam, 0.0, scale=(1, 1, 0.05))
key(vlam, t_d + 0.3, scale=(1, 1, 0.05))
key(vlam, t_d + 1.2, scale=(1, 1, 1.0))

# ---------------------------------------------------------------- de toekomstmens en hij bij de loopplank
WP = B + d * 0.7
HP = B + d * 2.1
ROT_W = math.degrees(math.atan2(d.x, -d.y))
vrouw = S.actor("toekomstvrouw", WP, ROT_W)
show(vrouw.rig, t_b, t_c)
jong = S.actor("hoofdpersonage_zwerver", HP, ROT_W + 180, label="hoofdpersonage_schip")
show(jong.rig, t_b, t_e)
S.beat(jong, t_b, "staan", face="nerveus", face_amt=0.6, at=S.head(vrouw))
S.beat(jong, t_b + 0.8, "staan", arms=arms(arm("R", (0.40, 0.75, -0.40), (0.15, 0.95, 0.10))), face="nerveus", face_amt=0.7,
       at=S.head(vrouw))                                                     # vraagt om één plekje
S.beat(jong, t_b1, "staan", face="nerveus", face_amt=0.7, at=S.head(vrouw))
S.beat(vrouw, t_b, "staan", face="neutraal", face_amt=0.5, at=S.head(jong))
for k, t in enumerate(frange(t_b1 + 0.4, t_b1 + 2.0, 0.35)):
    S.beat(vrouw, t, "staan", face="verdrietig", face_amt=0.5, at=S.head(jong), body={"head": (0, 14 if k % 2 else -14, 0)})
S.beat(vrouw, t_b1 + 2.2, "staan", face="verdrietig", face_amt=0.6, at=S.head(jong))
S.hold(vrouw, t_c)
S.beat(jong, t_c, "staan", arms=arms(arm("L", (0.40, 0.60, -0.55), (0.30, 0.90, 0.05)), arm("R", (0.40, 0.60, -0.55), (0.30, 0.90, 0.05))),
       face="verdrietig", face_amt=0.8, at=B + V(0, 0, 3.0))                  # "So you're just leaving me here?"
S.beat(jong, t_c + 1.6, "staan", face="geschrokken", face_amt=0.7, at=V(32.5, 130.0, VALLEY + 6.0))
S.beat(jong, t_c2, "staan", face="verdrietig", face_amt=0.7, at=V(40, 150, 25))
S.beat(jong, t_d + 0.6, "staan", face="inspanning", face_amt=0.9, at=V(40, 150, 30),
       arms=arms(arm("R", (0.55, 0.40, 0.45), (-0.45, 0.30, 0.70))), body={"spine": (-10, 0, 0), "chest": (-6, 0, 0)})   # luchtdruk
S.beat(jong, t_d + 2.4, "staan", face="inspanning", face_amt=0.8, at=V(40, 150, 140),
       arms=arms(arm("R", (0.55, 0.40, 0.45), (-0.45, 0.30, 0.70))), body={"spine": (-12, 0, 0), "chest": (-6, 0, 0)})
S.beat(jong, t_d + 3.6, "staan", face="verdrietig", face_amt=0.6, at=V(40, 150, 300))
S.hold(jong, t_e)
for t in frange(t_d + 0.5, t_e, 0.25):                                      # stof waait langs hem
    S.puff(HP + d * -1.5 + V(0, 0, 0.3), t, n=2, r=(0.2, 0.5), grow=1.8, dur=1.0, color=(0.62, 0.58, 0.50), rise=0.6, spread=1.2)

# ---------------------------------------------------------------- 16e-16h: alleen op de heuvel, het horloge repareren
SEAT = 0.38
held = S.actor("hoofdpersonage_zwerver", (-0.35, -0.02, 0), 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, V(-0.35, -0.02, hz_), 180)
show(held.rig, t_e)
CITY = V(0.0, 60.0, -10.0)
REST_L = arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62))
REST = arms(REST_L, arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)))
S.beat(held, t_e, **hs, arms=REST, face="neutraal", face_amt=0.4, at=CITY)
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
S.beat(held, t_f, **hs, arms=arms(REST_L, LOOKH), face="inspanning", face_amt=0.5, mouth=0.25, look=(0.0, -0.8),
       body={"head": (18, 0, 0)})
hw = S.watch(held, t_f - 0.1, side="R", name="Zakhorloge_1mln", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3,
             oud=True, tijd=(3, 41, 12))
for o in [hw] + list(hw.children_recursive):
    show(o, t_f - 0.1)
S.watch_hands("Zakhorloge_1mln", t_g + 0.9, END, every=1.0, start=(3, 41, 12))
WH = S.bone_world(held, "hand.R", t_f + 0.5)
doorn = T.cyl("Doorn", (0, 0, 0), 0.004, 0.07, S.mat("doorn_bruin", (0.35, 0.24, 0.12)), r2=0.0005, seg=6, ol=0)
grab(S, doorn, held, t_f - 0.1, "hand.L", loc=(0, 0.06, 0.0), rot=(0, 0, 0))
show(doorn, t_f - 0.1)
S.reach(held, t_f - 0.1, "L", None, 0.0)
for k, t in enumerate(frange(t_f + 0.3, t_g + 0.8, 0.3)):                   # peutert in het horloge
    S.reach(held, t, "L", WH + V(-0.05 if k % 2 else -0.03, -0.02, 0.06 if k % 2 else 0.04))
S.reach(held, t_g + 1.0, "L", None, 0.0)
for k, t in enumerate(frange(t_f + 0.4, t_g, 0.5)):
    S.beat(held, t, **hs, arms=arms(REST_L, LOOKH), face="inspanning", face_amt=0.5, mouth=0.3 if k % 2 else 0.2,
           look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.beat(held, t_h, **hs, arms=arms(REST_L, LOOKH), face="verbaasd", face_amt=0.4, look=(0.0, -0.8), body={"head": (18, 0, 0)})
S.beat(held, t_h + 0.8, **hs, arms=arms(REST_L, LOOKH), face="blij", face_amt=0.9, look=(0.0, -0.8), body={"head": (16, 0, 0)})
S.hold(held, END)
HD = S.headpos(held, t_h + 1.0)

# ---------------------------------------------------------------- camera's
CAMH = (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22)
S.cam(0.0, CAMH, (V(-3.3, -8.8, 2.25), V(0.8, 8.0, -0.4), 22))
MID = (S.head(jong) + S.head(vrouw)) * 0.5
SIDE = V(d.y, -d.x, 0)
S.cam(t_b, (MID + SIDE * 3.2 + V(0, 0, -0.1), MID + V(0, 0, -0.2), 30), (MID + SIDE * 2.9 + V(0, 0, -0.1), MID + V(0, 0, -0.2), 30))
S.cam(t_b1, (S.head(jong) + SIDE * 0.5 - d * 0.2 + V(0, 0, 0.05), S.head(vrouw), 35),
      (S.head(jong) + SIDE * 0.45 - d * 0.1 + V(0, 0, 0.05), S.head(vrouw), 35))
S.cam(t_c, (S.head(jong) - d * 1.4 + SIDE * 0.5 + V(0, 0, 0.1), S.head(jong) + V(0, 0, 0.1), 32),
      (S.head(jong) - d * 1.25 + SIDE * 0.45 + V(0, 0, 0.1), S.head(jong) + V(0, 0, 0.1), 32))
SCR = S0 + V(0, 0, 150 * 0.45 + w * 0.15) + V(math.sin(math.radians(-20)), -math.cos(math.radians(-20)), 0) * (w * 0.47)
S.cam(t_c2, (SCR + d * 60 + V(0, 0, -4), SCR, 40), (SCR + d * 55 + V(0, 0, -4), SCR, 40))
S.cam(t_d, (HP + d * 3.0 - SIDE * 2.0 + V(0, 0, 0.4), S0 + V(0, 0, 60), 20), (HP + d * 3.0 - SIDE * 2.0 + V(0, 0, 0.35), S0 + V(0, 0, 160), 20),
      handheld=0.12)
S.cam(t_e, CAMH)
S.cam(t_f, (WH + V(0.15, 0.42, 0.5), WH, 40), (WH + V(0.13, 0.38, 0.45), WH, 40))
S.cam(t_g, (WH + V(0.08, 0.3, 0.42), WH, 50), (WH + V(0.07, 0.27, 0.38), WH, 50))
S.cam(t_h, (HD + V(0.4, 1.6, -0.1), HD + V(0, 0, -0.22), 32), (HD + V(0.36, 1.45, -0.1), HD + V(0, 0, -0.22), 32))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(1000000, t0=0.0, big=True)
S.jump(0.0)
S.no_hud.append((t_c2, t_d))
S.say("D16-01", at=0.2)
S.say("D16-02", at=t_b + 0.3)
S.say("D16-03", who=vrouw, at=t_b1 + 0.3)
S.say("D16-04", who=jong, at=t_c + 0.3)
S.say("D16-05", at=t_c2 + 0.2)
S.say("D16-06", at=t_e + 0.3)
S.say("D16-07", at=t_f + 0.2)
S.say("D16-08", at=t_h + 1.6)
S.sfx("sfx_schip_opstijgen", 0.0, 0.10)
S.sfx("sfx_schip_opstijgen", t_d + 0.2, 0.28)
S.sfx("sfx_horloge_opwinden", t_f + 0.4, 0.15)
S.tick(t_g + 0.9, 0.5)
S.ticks(t_g + 1.9, END, every=1.0, vol=0.3)
S.ambience("sfx_wind_heuvel", t_e, END, vol=0.06)
S.music("ruimte_koor", 0.0, t_e + 1.0, vol=0.15, fade_in=0.6, fade_out=1.0)
S.music("m_vredig_klok", t_g, END, vol=0.15, fade_in=0.3, fade_out=0.6)
S.finish(length=END, tail=0.0)
