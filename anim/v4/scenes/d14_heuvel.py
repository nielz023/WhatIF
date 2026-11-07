"""D14 · 1.000 jaar: onder het puin, 3026 (script scène 14a-14i). De heuvel in ruïnes, de eik is een reus.
14a  WIDE CAM_HEUVEL drift 3,5 s: torens in de klimop, bomen uit de daken, vogels.  VO: "A thousand years. Year three thousand..."
14b  WIDE handheld 3 s: aardbeving; een oude toren zakt in elkaar, recht op hem.  VO: "And then, one quiet morning..."
14c  ZWART met één streep licht 4 s: hij ligt onder het beton, alleen zijn gezicht in een kier licht.  VO: "Buried. No way out."
14d  CLOSE 4 s: zijn lippen bewegen, hij telt.  VO: "Remember? You still feel everything."
14e  DETAIL 3 s: het zakhorloge bij zijn oor, net bereikbaar voor zijn vingers. Tik. Tik.  VO: "So you count..."
14e2 CLOSE 4 s: hij fluistert de namen.  JONGEN: "Mom. Dad. Opa. Oma..."  VO: "Names. Faces. Birthdays..."
14f  montage 4 s: de kier wordt dag, nacht, dag, nacht, steeds sneller; teller ratelt naar 3066.  VO: "Forty years."
14g  WIDE 3,5 s: een machine tilt het beton op, licht valt naar binnen, mensen in lichtgevende kleren om het gat.
14h  MEDIUM 3 s: een kind van een jaar of acht filmt hem met een zwevend hologramscherm.  KIND: "Do it again, I wasn't recording."
14i  CLOSE 3 s: hij staart naar het kind, en begint te lachen en te huilen tegelijk.  VO: "A thousand years later..."

    python3 anim/v4/scenes/d14_heuvel.py -- [--render] [--stills auto] [--pct 25]
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d14", "heuvel", "3026", exposure=0.15)
sh = S.cuts([4.6, 4.4, 3.6, 3.6, 3.4, 4.2, 4.8, 4.0, 3.6, 3.0, 4.3])
END = sh[-1][1]
t_b, t_c, t_d, t_e, t_e2, t_e3, t_f, t_g, t_h, t_i = (s[0] for s in sh[1:])
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


def face(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


CITY = V(0.0, 60.0, 5.0)
SEAT = 0.38                                                # de stenen voet van de bank
HOLE = V(-0.35, 0.25, ground(-0.35, 0.25))

# ---------------------------------------------------------------- donker onder het puin: zon en hemel uit (14c-14f)
DARK0, DARK1 = t_c, t_g
lights = [o for o in bpy.data.objects if o.type == "LIGHT"]
for o in lights:
    e = o.data.energy
    for t, v in ((DARK0 - 0.02, e), (DARK0, 0.0), (DARK1 - 0.02, 0.0), (DARK1, e)):
        o.data.energy = v
        o.data.keyframe_insert("energy", frame=F(t))
    o.data.energy = e
wd = bpy.context.scene.world
bg = [n for n in wd.node_tree.nodes if n.type == "BACKGROUND"] if wd and wd.node_tree else []
for n in bg:
    s0 = n.inputs["Strength"].default_value
    for t, v in ((DARK0 - 0.02, s0), (DARK0, 0.0), (DARK1 - 0.02, 0.0), (DARK1, s0)):
        n.inputs["Strength"].default_value = v
        n.inputs["Strength"].keyframe_insert("default_value", frame=F(t))
    n.inputs["Strength"].default_value = s0

# ---------------------------------------------------------------- de oude toren die omvalt
TB = V(8.5, 11.0, ground(8.5, 11.0) - 0.5)
TGT = HOLE + V(1.1, -0.3, 0.6)                             # waar de top neerkomt (naast hem)
dv = TGT - TB
L = dv.length
dh = V(dv.x, dv.y, 0).normalized()
TILT = math.degrees(math.acos(max(-1.0, min(1.0, dv.z / L))))
yaw = bpy.data.objects.new("Ruinetoren_draai", None)
T._link(yaw)
yaw.location = TB
yaw.rotation_euler = (0, 0, math.radians(face(TB, TB + dh)))
tilt = bpy.data.objects.new("Ruinetoren_kantel", None)
T._link(tilt)
tilt.parent = yaw
beton = S.mat("ruine_beton", (0.62, 0.60, 0.56))
raam = S.mat("ruine_raam_donker", (0.08, 0.09, 0.10))
klimop = S.mat("ruine_klimop", (0.20, 0.42, 0.14))
W = 3.2
parts = [T.box("Ruinetoren", (0, 0, 0), (W, W, L), beton, bevel=0.05, ol=0)]
for k in range(int(L // 2.2)):
    z = 1.2 + k * 2.2
    for sx in (-1, 1):
        parts.append(T.box(f"Ruinetoren_raam_{k}_{sx}", (sx * 0.75, W / 2 + 0.01, z), (0.9, 0.04, 1.0), raam, bevel=0, ol=0))
        parts.append(T.box(f"Ruinetoren_raamb_{k}_{sx}", (sx * 0.75, -W / 2 - 0.01, z), (0.9, 0.04, 1.0), raam, bevel=0, ol=0))
rr = random.Random(14)
for k in range(26):
    parts.append(T.sphere(f"Ruinetoren_klimop_{k}", (rr.choice((-1, 1)) * W / 2 * rr.uniform(0.6, 1.0), rr.uniform(-W / 2, W / 2),
                                                    rr.uniform(0.0, L * 0.8)), rr.uniform(0.4, 0.8), klimop,
                          scale=(0.5, 1.2, 1.4), seg=8, ol=0))
for p in parts:
    p.parent = tilt
T_FALL0, T_FALL1 = t_b + 1.2, t_b + 3.9
for t, a in ((0.0, 0.0), (T_FALL0, 0.0), (T_FALL0 + 0.5, 4.0), (T_FALL1, TILT)):
    tilt.rotation_euler = (math.radians(-a), 0, 0)
    tilt.keyframe_insert("rotation_euler", frame=F(t))
for fc in A._fcurves(tilt):
    for kp in fc.keyframe_points:
        kp.interpolation = "QUAD"
        kp.easing = "EASE_IN"
for t in frange(T_FALL0, T_FALL1, 0.4):                    # stof en brokken van de toren
    S.puff(TB + V(0, 0, 1.0), t, n=4, r=(0.8, 1.6), grow=1.8, dur=1.5, color=(0.66, 0.64, 0.60), rise=1.5, spread=2.5)
for t in (T_FALL1 - 0.1, T_FALL1):
    S.puff(HOLE + V(0.5, -0.4, 0.5), t, n=10, r=(0.6, 1.3), grow=2.2, dur=1.2, color=(0.66, 0.64, 0.60), rise=2.0, spread=2.4)

# ---------------------------------------------------------------- 14a-14b: hij zit op de bankvoet, staat op bij de aardbeving
held = S.actor("hoofdpersonage_2200", HOLE + V(0, -0.27, 0), 180)
hs, hz_ = sit(held, seat_top=SEAT)
S.place(held, 0, V(-0.35, -0.02, hz_), 180)
REST = arms(arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)), arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)))
S.beat(held, 0.0, **hs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(held, t_b, **hs, arms=REST, face="neutraal", face_amt=0.5, at=CITY)
S.beat(held, t_b + 0.6, **hs, arms=REST, face="verbaasd", face_amt=0.7, at=CITY + V(-20, 0, -10))
STAND = V(-0.35, -0.55, ground(-0.35, -0.55))
S.place(held, t_b + 1.0, V(-0.35, -0.02, hz_), 180)
S.place(held, t_b + 1.5, STAND, 180)
S.beat(held, t_b + 1.5, "schrik", face="geschrokken", face_amt=0.9, at=TB + V(0, 0, 14))
S.beat(held, t_b + 2.6, "schrik", face="geschrokken", face_amt=1.0, at=TB + V(-dh.x * 6, -dh.y * 6, 9))
S.beat(held, t_b + 3.6, "handen_hoofd", face="bang", face_amt=1.0, at=TGT + V(0, 0, 4))
S.hold(held, t_c)
show(held.rig, 0.0, t_c)
print("DBG14", tuple(round(x, 2) for x in S.headpos(held, t_b + 2.0)), tuple(round(x, 2) for x in STAND))

# ---------------------------------------------------------------- 14c-14i: hij ligt onder het puin (eigen figuur, gekanteld)
lig = S.actor("hoofdpersonage_2200", HOLE, 0, label="hoofdpersonage_puin")
show(lig.rig, t_c)
LROT = -35.0
lb = Body(S, lig, HOLE + V(0, 0, 0.14), LROT)
S.qc_skip.add(lig.name)
lb.key(0.0, HOLE + V(0, 0, 0.14), tilt=80)
lb.key(END, HOLE + V(0, 0, 0.14), tilt=80)
LEGS = lb.legs(80)
PINNED = arms(arm("L", (0.75, 0.05, -0.65), (0.75, 0.30, -0.55)), arm("R", (0.75, 0.05, -0.65), (0.75, 0.30, -0.55)))
S.beat(lig, t_c, "staan", arms=PINNED, face="inspanning", face_amt=0.5, look=(0.0, 0.3), **LEGS)
HD = S.headpos(lig, t_c + 0.5)
HIP = lb.at(t_c)
AX = V(HD.x - HIP.x, HD.y - HIP.y, 0).normalized()          # richting van heup naar hoofd
SIDE = V(AX.y, -AX.x, 0)
UP = V(0, 0, 1)

# het puin: grote platen over zijn lijf, een kier boven zijn gezicht
plaat = S.mat("puin_plaat", (0.55, 0.54, 0.51))
rotz = math.degrees(math.atan2(AX.y, AX.x))
slab_a = T.box("Puin_plaat_A", tuple(HIP - AX * 0.25 + UP * 0.62), (1.9, 1.7, 0.3), plaat, rot=(0, -7, rotz), bevel=0.04, ol=0)
slab_b = T.box("Puin_plaat_B", tuple(HD + AX * 0.95 + UP * 0.5), (1.0, 1.8, 0.3), plaat, rot=(0, 12, rotz), bevel=0.04, ol=0)
for k, (dx, ds, dz, sz) in enumerate([(0.2, 0.95, 0.25, (1.6, 0.4, 0.6)), (0.2, -0.95, 0.25, (1.6, 0.4, 0.6)),
                                      (-0.3, 0.75, 0.75, (1.2, 0.6, 0.3)), (0.9, -0.9, 0.55, (0.8, 0.8, 0.5))]):
    T.box(f"Puin_brok_{k}", tuple(HIP + AX * dx + SIDE * ds + UP * dz), sz, plaat, rot=(rr.uniform(-12, 12), rr.uniform(-12, 12), rotz + rr.uniform(-20, 20)),
          bevel=0.04, ol=0)
for o in [o for o in bpy.data.objects if o.name.startswith("Puin_")]:
    show(o, T_FALL1 - 0.1)
# het licht door de kier
kier = T.point_light("Kier_licht", tuple(HD + UP * 1.4 + AX * 0.1), color=(1.0, 0.92, 0.78), energy=0.0, radius=0.05)
for t, e, c in ((0.0, 0.0, (1.0, 0.92, 0.78)), (t_c - 0.02, 0.0, (1.0, 0.92, 0.78)), (t_c, 60.0, (1.0, 0.92, 0.78)),
                (t_f, 60.0, (1.0, 0.92, 0.78))):
    kier.data.energy = e
    kier.data.color = c
    kier.data.keyframe_insert("energy", frame=F(t))
    kier.data.keyframe_insert("color", frame=F(t))
# 14f: dag en nacht, steeds sneller
t = t_f + 0.25
step = 0.55
k = 0
while t < t_g - 0.15:
    night = k % 2 == 0
    kier.data.energy = 8.0 if night else 60.0
    kier.data.color = (0.45, 0.55, 1.0) if night else (1.0, 0.92, 0.78)
    kier.data.keyframe_insert("energy", frame=F(t))
    kier.data.keyframe_insert("color", frame=F(t))
    t += step
    step = max(0.12, step * 0.78)
    k += 1
kier.data.energy = 0.0
kier.data.keyframe_insert("energy", frame=F(t_g))

# 14d: lippen bewegen (tellen), 14e: het horloge bij zijn oor, 14e2: de namen
for k, t in enumerate(frange(t_d + 0.3, t_e - 0.2, 0.32)):
    S.beat(lig, t, "staan", arms=PINNED, face="vastberaden", face_amt=0.4, mouth=0.35 if k % 2 == 0 else 0.05,
           look=(0.0, 0.3), **LEGS)
WATCH = HD + SIDE * 0.55 - AX * 0.2 - UP * 0.12
w = S.watch(None, name="Zakhorloge_puin", open_=1.0, world=tuple(WATCH), rot=(0, 0, rotz + 90), scale=1.3)
S.watch_hands("Zakhorloge_puin", t_c, t_g, every=1.0)
S.reach(lig, t_e + 0.2, "R", None, 0.0)
S.reach(lig, t_e + 1.0, "R", WATCH + V(0, 0, 0.05))
S.reach(lig, t_g - 0.1, "R", WATCH + V(0, 0, 0.05))
S.reach(lig, t_g, "R", None, 0.0)
S.ticks(t_e + 0.5, t_e2, every=1.0, vol=0.35)
S.beat(lig, t_e2, "staan", arms=PINNED, face="verdrietig", face_amt=0.4, look=(0.0, 0.3), **LEGS)
S.eyes_closed(lig, t_e3 + 0.4, t_e3 + 4.2)
S.beat(lig, t_f, "staan", arms=PINNED, face="neutraal", face_amt=0.3, look=(0.0, 0.3), **LEGS)

# ---------------------------------------------------------------- 14g: een machine tilt het beton op
DR = slab_a.location.copy()
drone = T.box("Hijsmachine", (0, 0, 0), (2.4, 1.6, 0.6), S.mat("hijs_wit", (0.92, 0.93, 0.95)), bevel=0.2, ol=0)
gl = ND.pbr("hijs_gloed", (0.36, 0.92, 1.0), emit=(0.36, 0.92, 1.0), strength=5.0)
ring = T.cyl("Hijsmachine_ring", (0, 0, -0.32), 0.9, 0.06, gl, seg=32, ol=0)
ring.parent = drone
kabels = []
for sx in (-1, 1):
    for sy in (-1, 1):
        c = T.cyl(f"Hijsmachine_straal_{sx}_{sy}", (sx * 0.8, sy * 0.6, -1.6), 0.03, 2.6, gl, seg=6, ol=0)
        c.parent = drone
        kabels.append(c)
show(drone, t_g)
for c in kabels + [ring]:
    show(c, t_g)
key(drone, 0.0, loc=tuple(DR + V(0, 0, 3.0)))
key(drone, t_g, loc=tuple(DR + V(0, 0, 3.0)))
key(drone, t_g + 2.6, loc=tuple(DR + V(-0.6, 1.2, 5.0)))
key(slab_a, t_g, loc=tuple(DR))
key(slab_a, t_g + 2.6, loc=tuple(DR + V(-0.6, 1.2, 2.0)))
for t in (t_g + 0.2, t_g + 0.6):
    S.puff(DR, t, n=3, r=(0.2, 0.4), grow=1.4, dur=1.2, color=(0.70, 0.68, 0.64), rise=1.0, spread=1.0)

# mensen in lichtgevende kleren rond het gat
RING = [("toekomst_a", 125), ("toekomstvrouw", 200), ("toekomst_b", 260)]
mensen = []
for name, ang in RING:
    a = math.radians(ang)
    p = HIP + V(math.cos(a), math.sin(a), 0) * 2.9
    p.z = ground(p.x, p.y)
    ch = S.actor(name, p, face(p, HIP))
    show(ch.rig, t_g)
    S.beat(ch, t_g, "staan", face="verbaasd", face_amt=0.8, at=HD)
    S.hold(ch, END)
    mensen.append(ch)

# het kind met het zwevende hologramscherm
KP = HD + AX * 1.0 + SIDE * 1.1
KP.z = ground(KP.x, KP.y)
kind = S.actor("kind_holo", KP, face(KP, HD))
show(kind.rig, t_g)
S.beat(kind, t_g, "staan", face="blij", face_amt=0.7, at=HD)
S.beat(kind, t_h, "filmen", face="blij", face_amt=0.8, at=HD)
S.beat(kind, t_h + 1.2, "filmen", face="zelfverzekerd", face_amt=0.7, at=HD)
S.hold(kind, END)
KH = S.headpos(kind, t_h + 0.5)
scherm = T.box("Hologramscherm", (0, 0, 0), (0.42, 0.01, 0.28), ND.pbr("holo_scherm", (0.36, 0.92, 1.0), emit=(0.36, 0.92, 1.0),
                                                                      strength=3.0), bevel=0, ol=0)
TOW = (HD - KH)
TOW.z = 0
TOW.normalize()
SP = KH + TOW * 0.45 - V(0, 0, 0.35)
scherm.location = SP
scherm.rotation_euler = (math.radians(-35), 0, math.radians(face(KP, HD)))
show(scherm, t_g + 1.0)

# 14g-14i: hij kijkt omhoog, naar het kind; lachen en huilen
S.beat(lig, t_g, "staan", arms=PINNED, face="verbaasd", face_amt=0.6, look=(0.0, 0.3), **LEGS)
S.beat(lig, t_h, "staan", arms=PINNED, face="verbaasd", face_amt=0.8, look=(0.4, 0.6), **LEGS)
S.beat(lig, t_i + 0.4, "staan", arms=PINNED, face="neutraal", face_amt=0.5, look=(0.4, 0.6), **LEGS)
for k, t in enumerate(frange(t_i + 1.3, END, 0.35)):
    S.beat(lig, t, "staan", arms=PINNED, face="lach" if k % 2 == 0 else "verdrietig", face_amt=0.9 if k % 2 == 0 else 0.6,
           look=(0.4, 0.6), mouth=0.6 if k % 2 == 0 else 0.2, **LEGS)
S.hold(lig, END)
tear = S.mat("traan", (0.65, 0.85, 1.0))
for sx in (-1, 1):
    tr = T.sphere(f"Traan_{sx}", (0, 0, 0), 0.016, tear, scale=(1, 1, 1.4), seg=8, ol=0)
    e0 = HD + SIDE * (0.13 * sx) + UP * 0.22
    key(tr, 0.0, loc=tuple(e0), scale=0.001)
    key(tr, t_i + 1.6, loc=tuple(e0), scale=0.001)
    key(tr, t_i + 1.7, loc=tuple(e0), scale=1.0)
    key(tr, END, loc=tuple(e0 + SIDE * (0.18 * sx) - UP * 0.12), scale=1.0)

# ---------------------------------------------------------------- camera's
CAMH = (V(-3.6, -9.5, 2.3), V(0.8, 8.0, -0.6), 22)
S.cam(0.0, CAMH, (V(-3.45, -9.2, 2.3), V(0.8, 8.0, -0.6), 22))
S.cam(t_b, (V(1.6, -3.4, 1.1), V(0.6, 6.0, 4.0), 20), (V(1.5, -3.25, 1.1), V(0.8, 6.0, 4.6), 20), handheld=0.35)
IN = HD + UP * 0.75 + AX * 0.25                            # in de kier, boven zijn gezicht
S.cam(t_c, (IN + UP * 0.25, HD, 35), (IN, HD, 35))
S.cam(t_d, (HD + UP * 0.68 + AX * 0.22 - SIDE * 0.1, HD + UP * 0.05, 35), (HD + UP * 0.62 + AX * 0.2 - SIDE * 0.1, HD + UP * 0.05, 35))
S.cam(t_e, (WATCH + UP * 0.32 + SIDE * 0.1 + AX * 0.12, WATCH, 50), (WATCH + UP * 0.28 + SIDE * 0.08 + AX * 0.1, WATCH, 50))
S.cam(t_e2, (HD + UP * 0.68 + AX * 0.25 + SIDE * 0.12, HD + UP * 0.05, 35), (HD + UP * 0.62 + AX * 0.22 + SIDE * 0.1, HD + UP * 0.05, 35))
S.cam(t_e3, (HD + UP * 0.7 + AX * 0.3 + SIDE * 0.05, HD, 32), (HD + UP * 0.64 + AX * 0.27 + SIDE * 0.05, HD, 32))
S.cam(t_f, (IN + UP * 0.1, HD, 30))
S.cam(t_g, (HIP + SIDE * 4.2 - AX * 1.2 + UP * 2.8, HIP + UP * 0.6, 24), (HIP + SIDE * 3.9 - AX * 1.1 + UP * 2.6, HIP + UP * 0.8, 24))
S.cam(t_h, (HD + UP * 0.45, KH, 50), (HD + UP * 0.45 + (KH - HD) * 0.06, KH, 50))
S.cam(t_i, (HD + UP * 0.8 + AX * 0.2 + SIDE * 0.1, HD + UP * 0.05, 32),
      (HD + UP * 0.7 + AX * 0.18 + SIDE * 0.08, HD + UP * 0.05, 32))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year([(0.0, 3026), (t_f + 0.3, 3030), (t_f + 1.4, 3045), (t_f + 2.6, 3066)], t0=0.0, big=True)
S.jump(0.0)
S.say("D14-01", at=0.2)
S.say("D14-02", at=t_b + 0.1)
S.say("D14-03", at=t_c + 0.6)
S.say("D14-04", at=t_d + 0.3)
S.say("D14-05", at=t_e + 0.2)
S.say("D14-06", who=lig, at=t_e2 + 0.2)
S.say("D14-07", at=t_e3 + 0.15)
S.say("D14-08", at=t_f + 1.2)
S.say("D14-09", at=t_g + 0.2)
S.say("D14-10", who=kind, at=t_h + 0.25)
S.say("D14-11", at=t_i + 0.2)
S.ambience("sfx_wind_heuvel", 0.0, t_c, vol=0.08)
S.sfx("sfx_aardbeving", t_b + 0.1, 0.30)
S.sfx("sfx_muur_valt", T_FALL1 - 0.6, 0.30)
S.sfx("sfx_stroom_zoem", t_g, 0.12)
S.sfx("sfx_hologram", t_g + 1.0, 0.12)
S.ambience("sfx_park_ochtend", t_g, END, vol=0.06)
S.music("drone", 0.0, END, vol=0.14, fade_in=0.8, fade_out=0.6)
S.finish(length=END, tail=0.0)
