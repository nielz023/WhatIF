"""D15 · De ijstijd, 50.000 jaar (script scène 15a-15h). De heuvel onder het ijs, sneeuwstorm.
15a  WIDE drone 3,5 s: witte vlakte tot de horizon, één figuurtje loopt erover.  VO: "And this is where physics gets you."
15b  WIDE trage crane 7 s (hier 2 shots): een torenspits steekt een paar meter uit het ijs.
     VO: "Earth's orbit wobbles in long, slow cycles. And every hundred thousand years or so, the ice comes back."
15b2 WIDE crane omlaag 5 s: doorsnede: onder een kilometer blauw ijs ligt de stad, met de heuvel en de eik.
     VO: "Your city is down there. Under a kilometer of it."
15c  MEDIUM 3 s: hij loopt voorovergebogen in de storm, ijs in zijn wimpers, hij rilt.
     VO: "You can't freeze to death. But you can be cold for ten thousand years."
15d  DETAIL 3 s: het horloge in zijn want; de wijzers staan stil, rijp op het glas. Geen tik, alleen wind.
15e  CLOSE 3 s: hij schudt het horloge, houdt het bij zijn oor. Niets.
15f  DETAIL 3 s: hij haalt de oude foto tevoorschijn, verkleurd en gekreukt; mama's gezicht is bijna weg.
15g  CLOSE trage push-in 6,5 s (hier 2 shots): hij kijkt lang naar de foto, fronst.
     VO: "Here's what nobody warns you about. After fifty thousand years... you can't remember your mom's face."
15h  CLOSE 2,5 s: VO "Only the photo can." Hij stopt de foto heel voorzichtig terug, binnen in zijn jas, tegen zijn borst.

    python3 anim/v4/scenes/d15_ijs.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d15", "heuvel", "ijs", exposure=0.1)
sh = S.cuts([3.5, 3.6, 3.8, 5.0, 5.6, 3.0, 3.0, 3.0, 4.0, 3.4, 2.8])
END = sh[-1][1]
t_b, t_b1, t_b2, t_c, t_d, t_e, t_f, t_g, t_g1, t_h = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True


def ground(x, y, skip=("Eik", "Sneeuwstorm", "Vlok", "Puin", "Ruinetoren", "Hijsmachine", "Vogel", "Doorsnede")):
    dg = bpy.context.evaluated_depsgraph_get()
    z = 60.0
    for _ in range(12):
        hit, loc, nrm, idx, ob, mtx = bpy.context.scene.ray_cast(dg, Vector((x, y, z)), Vector((0, 0, -1)))
        if not hit:
            return 0.0
        if not ob.name.startswith(skip):
            return loc.z
        z = loc.z - 0.01
    return 0.0


# de storm waait (de strepen schuiven langzaam door het beeld)
storm = bpy.data.objects.get("Sneeuwstorm")
if storm:
    key(storm, 0.0, loc=(0, 0, 0), interp="LINEAR")
    key(storm, END, loc=(-14.0, 6.0, -1.0), interp="LINEAR")

# ---------------------------------------------------------------- 15a-15b: een figuurtje op de vlakte (eigen figuur)
ver = S.actor("hoofdpersonage_ijs", (-8.0, 28.0, ground(-8, 28)), -100, label="hoofdpersonage_ver")
S.qc_skip.add(ver.name)
show(ver.rig, 0.0, t_b)
S.walk(ver, 0.0, t_b, [V(-8.0, 28.0, ground(-8, 28)), V(-4.0, 29.0, ground(-4, 29))], stride=0.45)
SP = V(8.0, 180.0, 0.0)                                    # torenspits 4 (4 m boven het ijs)
spits = S.actor("hoofdpersonage_ijs", SP + V(-5.0, -4.0, ground(SP.x - 5, SP.y - 4)), -70, label="hoofdpersonage_spits")
S.qc_skip.add(spits.name)
show(spits.rig, t_b, t_b2)
S.walk(spits, t_b, t_b2, [SP + V(-5.0, -4.0, ground(SP.x - 5, SP.y - 4)), SP + V(-1.0, -5.2, ground(SP.x - 1, SP.y - 5.2)),
                          SP + V(3.5, -5.0, ground(SP.x + 3.5, SP.y - 5))], stride=0.42)
for t in (t_b, t_b1):
    S.beat(spits, t, "staan", face="nerveus", face_amt=0.6, at=SP + V(0, 0, 3.5), body={"spine": (10, 0, 0)})

# ---------------------------------------------------------------- 15b2: de doorsnede (diagram op een eigen plek)
X0 = V(3000.0, 0.0, 0.0)
T.box("Doorsnede_ijs", tuple(X0 + V(0, 0, 0)), (90.0, 30.0, 42.0), T.glass("ijs_doorsnede", (0.45, 0.70, 0.95), 0.30), bevel=0, ol=0)
T.box("Doorsnede_sneeuw", tuple(X0 + V(0, 0, 42.0)), (90.0, 30.0, 0.8), S.mat("sneeuw_doorsnede", (0.95, 0.97, 1.0)), bevel=0, ol=0)
T.box("Doorsnede_rots", tuple(X0 + V(0, 0, -6.0)), (90.0, 30.0, 6.0), S.mat("rots_doorsnede", (0.30, 0.27, 0.25)), bevel=0, ol=0)
T.sphere("Doorsnede_heuvel", tuple(X0 + V(-18.0, 0, -1.0)), 9.0, S.mat("heuvel_doorsnede", (0.26, 0.36, 0.22)),
         scale=(1.6, 1.2, 0.55), seg=24, ol=0)
T.cyl("Doorsnede_eik_stam", tuple(X0 + V(-21.0, 0, 3.6)), 0.5, 4.0, S.mat("eik_doorsnede", (0.25, 0.17, 0.11)), seg=10, ol=0)
T.sphere("Doorsnede_eik_kroon", tuple(X0 + V(-21.0, 0, 9.0)), 3.2, S.mat("kroon_doorsnede", (0.30, 0.32, 0.26)),
         scale=(1.3, 1.1, 0.9), seg=16, ol=0)
rd = random.Random(15)
for k in range(28):
    x = rd.uniform(-6, 42)
    h = rd.uniform(3, 16)
    w = rd.uniform(2.0, 4.5)
    T.box(f"Doorsnede_toren_{k}", tuple(X0 + V(x, rd.uniform(-8, 8), 0)), (w, w, h),
          S.mat(f"toren_doorsnede_{k % 3}", [(0.42, 0.46, 0.52), (0.55, 0.58, 0.62), (0.34, 0.38, 0.44)][k % 3]), bevel=0.05, ol=0)
S.text("1 KM OF ICE", t_b2 + 1.6, t_c - 0.1, loc=(0.80, 0.50), size=72, color=(0.85, 0.95, 1.0), anchor=("CENTER", "CENTER"))

# ---------------------------------------------------------------- 15c-15h: hij, dichtbij, in de storm (bij de bankvoet)
G0 = ground(0.6, -1.0)
held = S.actor("hoofdpersonage_ijs", (-1.4, 4.0, ground(-1.4, 4.0)), 160)
show(held.rig, t_c)
STOPP = V(0.6, -1.0, G0)
S.walk(held, t_c, t_d - 0.3, [V(-1.4, 4.0, ground(-1.4, 4.0)), V(-0.3, 1.2, ground(-0.3, 1.2)), STOPP], stride=0.32, end_rot=20)
COLD = arms(arm("L", (0.30, 0.45, -0.80), (-0.60, 0.70, 0.10)), arm("R", (0.30, 0.45, -0.80), (-0.60, 0.70, 0.10)))   # armen om zich heen
for k, t in enumerate(frange(t_c, t_d, 0.22)):
    S.beat(held, t, "staan", arms=COLD, face="nerveus", face_amt=0.8, look=(0.0, -0.3),
           body={"spine": (18, 0, 0), "chest": (8, 0, 0), "head": (6, 0, 3 if k % 2 else -3)})                      # rilt
HD = S.headpos(held, t_d + 0.5)
FW = V(math.sin(math.radians(20)), -math.cos(math.radians(20)), 0)    # zijn kijkrichting (rot 20)
SD = V(FW.y, -FW.x, 0)                                                   # zijn rechterkant
for t in frange(t_c + 0.3, t_d, 0.7):                       # ademwolkjes
    S.puff(S.head(held, t) + V(0, 0, -0.18) + V(0.3 * math.sin(math.radians(20)), -0.3 * math.cos(math.radians(20)), 0),
           t, n=2, r=(0.03, 0.06), grow=2.0, dur=0.7, color=(0.92, 0.95, 1.0), rise=0.15, spread=0.06)
# 15d: het horloge in zijn want (wijzers stil, rijp op het glas)
LOOKH = lambda ch, f: A.aim_arm(ch, f, "R", (0.30, 0.30, -0.90), (-0.25, 0.85, 0.45), None, (0, 160, 0))
S.beat(held, t_d, "staan", arms=arms(arm("L", (0.30, 0.45, -0.80), (-0.60, 0.70, 0.10)), LOOKH), face="nerveus", face_amt=0.6,
       look=(0.0, -0.8), body={"head": (18, 0, 0), "spine": (6, 0, 0)})
hw = S.watch(held, t_d - 0.2, side="R", name="Zakhorloge_ijs", open_=1.0, loc=(0, 0.058, 0.0), rot=(180, 0, 0), scale=1.3,
             rijp=True, tijd=(3, 41, 12))
for o in [hw] + list(hw.children_recursive):
    show(o, t_d - 0.2, t_f)
WH = S.bone_world(held, "hand.R", t_d + 0.8)
# 15e: schudden en bij zijn oor houden
S.beat(held, t_e, "staan", arms=arms(arm("L", (0.30, 0.45, -0.80), (-0.60, 0.70, 0.10)), LOOKH), face="twijfel", face_amt=0.7,
       look=(0.0, -0.8), body={"head": (14, 0, 0)})
S.reach(held, t_e - 0.3, "R", None, 0.0)
for k, t in enumerate(frange(t_e + 0.1, t_e + 1.0, 0.12)):
    S.reach(held, t, "R", WH + V(0.05 if k % 2 else -0.05, 0, 0.02 if k % 2 else -0.02))
EAR = HD + SD * 0.36 + V(0, 0, -0.04)
S.reach(held, t_e + 1.6, "R", EAR)
S.reach(held, t_f - 0.1, "R", EAR)
S.beat(held, t_e + 1.6, "staan", face="nerveus", face_amt=0.7, look=(-0.6, -0.1), body={"head": (0, 0, -10)})
S.eyes_closed(held, t_e + 1.8, t_f - 0.1)

# 15f-15h: de foto, verbleekt en gekreukt
S.reach(held, t_f, "R", None, 0.0)
img = os.path.join(REPO, "assets", "props", "gezinsfoto_14e_verjaardag.png")
foto = ND.oude_foto("Gezinsfoto_ijs", (0, 0, 0), rot=(0, 0, 0), image=img if os.path.exists(img) else None, vergeling=0.7,
                    verbleking=0.85, kreuk=0.7)
foto.scale = (1.6,) * 3
PH = HD + FW * 0.42 + V(0, 0, -0.62)
FROT = (36, 0, 20)
CHEST = HD + FW * 0.12 + V(0, 0, -0.75)
key(foto, 0.0, loc=tuple(CHEST), rot=(90, 0, 20), scale=0.001)
key(foto, t_f + 0.3, loc=tuple(CHEST), rot=(90, 0, 20), scale=0.001)
key(foto, t_f + 0.4, loc=tuple(CHEST), rot=(90, 0, 20), scale=1.6)
key(foto, t_f + 1.4, loc=tuple(PH), rot=FROT, scale=1.6)
key(foto, t_h + 0.6, loc=tuple(PH), rot=FROT, scale=1.6)
key(foto, t_h + 1.8, loc=tuple(CHEST), rot=(90, 0, 20), scale=1.6)
key(foto, t_h + 1.9, loc=tuple(CHEST), rot=(90, 0, 20), scale=0.001)
show(foto, t_f)
S.reach(held, t_f + 0.3, "R", CHEST + SD * 0.10)
S.reach(held, t_f + 1.4, "R", PH + SD * 0.12)
S.reach(held, t_f + 1.0, "L", None, 0.0)
S.reach(held, t_f + 1.4, "L", PH - SD * 0.12)
S.reach(held, t_h + 0.6, "R", PH + SD * 0.12)
S.reach(held, t_h + 0.6, "L", PH - SD * 0.12)
S.reach(held, t_h + 1.4, "L", None, 0.0)
S.reach(held, t_h + 1.8, "R", CHEST + SD * 0.10)
S.reach(held, END, "R", CHEST + SD * 0.10)
S.beat(held, t_f, "staan", face="neutraal", face_amt=0.5, at=PH)
S.beat(held, t_g, "staan", face="neutraal", face_amt=0.5, at=PH)
S.beat(held, t_g1, "staan", face="twijfel", face_amt=0.8, at=PH)                         # fronst
S.beat(held, t_h + 0.4, "staan", face="verdrietig", face_amt=0.6, at=PH)
S.beat(held, t_h + 1.9, "staan", face="verdrietig", face_amt=0.4, look=(0.0, -0.5))
S.hold(held, END)

# ---------------------------------------------------------------- camera's
S.cam(0.0, (V(-30.0, -60.0, 40.0), V(10.0, 120.0, 0.0), 24), (V(-29.0, -58.0, 39.5), V(10.0, 120.0, 0.0), 24))
S.cam(t_b, (SP + V(-7.0, -16.0, 1.5), SP + V(0, 0, 2.5), 26), (SP + V(-6.8, -15.0, 4.0), SP + V(0, 0, 2.5), 26))
S.cam(t_b1, (SP + V(4.0, -10.0, 0.9), SP + V(0, 0, 3.0), 30), (SP + V(3.6, -9.4, 1.2), SP + V(0, 0, 3.4), 30))
S.cam(t_b2, (X0 + V(4.0, -70.0, 52.0), X0 + V(4.0, 0, 40.0), 28), (X0 + V(4.0, -62.0, 14.0), X0 + V(4.0, 0, 8.0), 28))
S.cam(t_c, (V(3.5, -4.5, 1.3), V(0.0, 0.5, 1.0), 35), (V(3.3, -4.2, 1.3), V(0.3, -0.4, 1.0), 35))
S.cam(t_d, (WH + FW * 0.42 + SD * 0.1 + V(0, 0, 0.42), WH, 45), (WH + FW * 0.38 + SD * 0.09 + V(0, 0, 0.38), WH, 45))
S.cam(t_e, (HD + FW * 1.5 + SD * 0.6 + V(0, 0, -0.05), HD + V(0, 0, -0.12), 36),
      (HD + FW * 1.4 + SD * 0.55 + V(0, 0, -0.05), HD + V(0, 0, -0.12), 36))
HF = S.headpos(held, t_f + 2.0)
CF = PH + FW * 0.15 + V(0, 0, 0.42)          # over zijn linkerschouder, op ooghoogte: hij ziet de foto
S.cam(t_f, (CF, PH, 35), (CF + (PH - CF) * 0.08, PH, 35))
HG = S.headpos(held, t_g + 1.5)
S.cam(t_g, (HG + FW * 1.6 - SD * 0.45 + V(0, 0, -0.45), HG + V(0, 0, -0.2), 32),
      (HG + FW * 1.45 - SD * 0.4 + V(0, 0, -0.42), HG + V(0, 0, -0.2), 32))
HG1 = S.headpos(held, t_g1 + 1.5)
S.cam(t_g1, (HG1 + FW * 1.35 - SD * 0.3 + V(0, 0, -0.42), HG1 + V(0, 0, -0.15), 35),
      (HG1 + FW * 1.22 - SD * 0.27 + V(0, 0, -0.4), HG1 + V(0, 0, -0.15), 35))
HH_ = S.headpos(held, t_h + 1.2)
S.cam(t_h, (HH_ + FW * 1.8 + SD * 0.4 + V(0, 0, -0.1), HH_ + V(0, 0, -0.3), 30),
      (HH_ + FW * 1.7 + SD * 0.38 + V(0, 0, -0.1), HH_ + V(0, 0, -0.3), 30))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year(50000, t0=0.0, big=True)
S.jump(0.0)
S.no_hud.append((t_b2, t_c))
S.say("D15-01", at=0.3)
S.say("D15-02", at=t_b + 0.2)
S.say("D15-03", at=t_b2 + 0.4)
S.say("D15-04", at=t_c + 0.2)
S.say("D15-05", at=t_g + 0.2)
S.say("D15-06", at=t_h + 0.15)
S.ambience("sfx_sneeuwstorm", 0.0, END, vol=0.14)
S.music("m_winter", 0.0, END, vol=0.14, fade_in=0.8, fade_out=0.8)
S.finish(length=END, tail=0.0)
