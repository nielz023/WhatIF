"""N07b · Dag 1 in de supermarkt (script scène 7d-7j).
7d WIDE trage dolly: rustige winkel, de jongen en mama met een mandje, de agent (uit dienst, in uniform) in de rij.
7e MEDIUM: een man pakt een reep bij de kassa, kijkt naar de kassière en loopt achteruit naar buiten zonder te betalen.
7f CLOSE kassière: "Well? Do something!"   7g CLOSE agent kijkt naar zijn badge, haalt zijn schouders op:
"Arrest him for what? There's no law I can enforce."
7h WIDE: iedereen kijkt naar elkaar, 2 s stilte, een vrouw pakt een fles... en dan rent iedereen met karren.
7i MEDIUM handheld: mama grijpt de jongen bij zijn pols en trekt hem mee. VO N07-05 (Montreal 1969).
7j WIDE drone + 7k laag: mensen rennen naar buiten met volle karren. VO N07-06.

    blender -b -P anim/v3/scenes/n07b_supermarkt.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403

S = Scene3("n07b", "supermarkt", "nr_normaal", exposure=0.2)
sh = S.cuts([3.5, 3.4, 2.6, 4.4, 4.2, 3.6, 4.2, 4.2])
END = sh[-1][1]
t_d, t_e, t_f, t_g, t_h, t_i, t_j, t_k = (s[0] for s in sh)
rnd = random.Random(3)
T.use_collection(T.collection("N07b_props"))

# ---------------------------------------------------------------- helpers: karren die met iemand mee rennen
CART_SRC = S.obj("Winkelwagen_held")


def new_cart(name, loc, rot=0.0, full=True):
    c = CART_SRC.copy()
    c.data = CART_SRC.data
    c.name = name
    bpy.context.scene.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (0, 0, math.radians(rot))
    if full:
        for k in range(5):
            b = T.box(f"{name}_waar{k}", (rnd.uniform(-0.15, 0.15), rnd.uniform(-0.3, 0.3), 0.58 + 0.1 * (k // 3)),
                      (rnd.uniform(0.14, 0.24), rnd.uniform(0.12, 0.22), rnd.uniform(0.18, 0.32)),
                      S.mat(f"waar_{k}", [(0.85, 0.2, 0.15), (0.2, 0.5, 0.85), (0.95, 0.8, 0.2), (0.3, 0.7, 0.35), (0.9, 0.5, 0.15)][k]),
                      rot=(0, 0, rnd.uniform(-30, 30)), bevel=0.01, ol=0.004)
            b.parent = c
    return c


def push_cart(ch, cart, t0, t1, ahead=0.78):
    """Kar volgt de figuur (voor hem uit, zelfde richting); beide handen aan het handvat."""
    S.reach(ch, 0.0, "R", inf=0.0)
    S.reach(ch, 0.0, "L", inf=0.0)
    S.reach(ch, t0 - 0.15, "R", inf=0.0)               # IK pas vlak voor het duwen aan (geen trage aanloop vanaf 0)
    S.reach(ch, t0 - 0.15, "L", inf=0.0)
    for t in frange(t0, t1 + 0.01, 0.1):
        M = S._root_matrix(ch, t)
        R3 = M.to_3x3().normalized()
        fwd = R3 @ V(0, -1, 0)
        fwd.z = 0
        fwd.normalize()
        p = M.translation.copy()
        cart.location = V(p.x, p.y, 0) + fwd * ahead
        cart.rotation_euler = (0, 0, math.atan2(fwd.y, fwd.x) + math.pi / 2)
        cart.keyframe_insert("location", frame=F(t))
        cart.keyframe_insert("rotation_euler", frame=F(t))
        side = V(-fwd.y, fwd.x, 0)
        handle = V(p.x, p.y, 1.05) + fwd * (ahead - 0.5)
        S.reach(ch, t, "R", handle - side * 0.2)
        S.reach(ch, t, "L", handle + side * 0.2)
    for fc in A._fcurves(cart):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


# ---------------------------------------------------------------- de cast bij kassa 1
CASH = V(-10.65, -12.3, 0)
kas = S.actor("kassiere", CASH, 90)
dief = S.actor("figurant_d", (-9.05, -11.95, 0), 0)     # vlak voor het chocoladerek (korte armen)
agent = S.actor("agent", (-9.05, -9.7, 0), 0)
mama = S.actor("mama", (-8.0, -8.3, 0), 0)
held = S.actor("hoofdpersonage_kind", (-8.67, -8.5, 0), 10)
mandje = T.box("Mandje", (0, 0, 0), (0.42, 0.3, 0.22), S.mat("mandje_rood", (0.85, 0.12, 0.1)), base=False, bevel=0.03, ol=0.004)
grab(S, mandje, mama, 0.0, "hand.R", loc=(0, 0.12, -0.12), rot=(0, 0, 0), release=t_i - 0.05)
reep = T.box("Reep_dief", (-9.25, -12.45, 1.0), (0.05, 0.16, 0.02), S.mat("reep_paars", (0.45, 0.15, 0.55)), base=False, bevel=0.005, ol=0.003)
reep.rotation_euler = (math.radians(90), 0, 0)
S.beat(kas, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(-9.0, -11.6, 1.5))
S.beat(agent, 0.0, "staan", face="neutraal", face_amt=0.5, look=(0.2, -0.2))
S.beat(mama, 0.0, "staan", face="neutraal", face_amt=0.5, at=V(-9.0, -11.0, 1.4))
S.beat(held, 0.0, "staan", face="neutraal", face_amt=0.4, look=(0.4, 0.1))
S.beat(dief, 0.0, "staan", face="neutraal", face_amt=0.4, look=(0.0, -0.2))

# ---- 7e: de man pakt de reep, houdt hem omhoog en loopt achteruit naar de deur
S.reach(dief, 0.0, "R", inf=0.0)
S.reach(dief, t_e + 0.2, "R", inf=0.0)
S.reach(dief, t_e + 0.55, "R", reep.location + V(0.05, 0.05, 0.0))
grab(S, reep, dief, t_e + 0.6, "hand.R", loc=(0, 0.06, 0.0), rot=(0, 0, 90))
S.reach(dief, t_e + 0.7, "R", inf=0.0)
S.beat(dief, t_e + 0.8, "staan", arms=arms(arm("R", (0.35, 0.5, 0.2), (0.1, 0.4, 0.9))), face="twijfel", face_amt=0.8, at=S.head(kas, 0.0))
S.turn(dief, t_e + 1.0, t_e + 1.4, -70)
S.beat(dief, t_e + 1.3, "staan", arms=arms(arm("R", (0.35, 0.5, 0.2), (0.1, 0.4, 0.9))), face="grijns", face_amt=0.7,
       at=S.head(kas, 0.0), feet="keep")
BACK = [V(-9.05, -11.95, 0), V(-8.7, -13.6, 0), V(-6.0, -15.6, 0), V(-2.2, -17.6, 0), V(-1.0, -20.5, 0)]
S.walk(dief, t_e + 1.6, t_e + 6.2, BACK, stride=0.32, turn=False)
S.beat(dief, t_e + 2.2, "staan", arms=arms(arm("R", (0.3, 0.3, -0.3), (0.0, 0.5, 0.8))), face="grijns", face_amt=0.8,
       at=S.head(kas, 0.0), feet="keep")
S.hold(dief, t_h)
visible(dief.body, t_h, False)                     # hij is de winkel uit: niet meer in de weg bij de uitgang

# ---- 7f: de kassière kijkt naar de agent
S.beat(kas, t_e + 0.7, "staan", face="verbaasd", face_amt=0.8, at=S.head(dief, t_e + 0.7))
S.beat(kas, t_e + 2.0, "handen_zij", amount=0.8, face="boos", face_amt=0.6, at=S.head(dief, t_e + 2.0))
S.beat(kas, t_f + 0.1, "handen_zij", amount=0.9, face="boos", face_amt=0.9, at=S.head(agent, t_f))
S.say("N07-03", who=kas, at=t_f + 0.2)
S.beat(kas, t_f + 2.3, "handen_zij", amount=0.9, face="boos", face_amt=0.7, at=S.head(agent, t_f))

# ---- 7g: de agent kijkt naar zijn badge en haalt zijn schouders op
S.beat(agent, t_e + 0.9, "staan", face="verbaasd", face_amt=0.6, at=S.head(dief, t_e + 0.9))
S.beat(agent, t_g + 0.1, "staan", face="neutraal", face_amt=0.6, look=(0.15, -0.8), body={"head": (14, 0, 0)})
S.beat(agent, t_g + 0.9, "staan", face="verdrietig", face_amt=0.4, look=(0.15, -0.8), body={"head": (14, 0, 0)})
S.beat(agent, t_g + 1.3, "schouders_op", amount=0.6, face="twijfel", face_amt=0.6, at=S.head(kas, t_g))
S.beat(agent, t_g + 1.7, "schouders_op", amount=1.15, face="twijfel", face_amt=0.8, at=S.head(kas, t_g))
S.beat(agent, t_g + 2.6, "schouders_op", amount=0.9, face="verdrietig", face_amt=0.5, at=S.head(kas, t_g))
S.beat(agent, t_g + 3.8, "staan", face="verdrietig", face_amt=0.5, at=S.head(kas, t_g))
S.say("N07-04", who=agent, at=t_g + 0.25)
S.beat(mama, t_e + 1.0, "staan", face="verbaasd", face_amt=0.6, at=S.head(dief, t_e + 1.0))
S.beat(held, t_e + 1.1, "staan", face="verbaasd", face_amt=0.8, at=S.head(dief, t_e + 1.1))
S.beat(mama, t_g + 1.0, "staan", face="nerveus", face_amt=0.6, at=S.head(agent, t_g))
S.beat(held, t_g + 1.2, "staan", face="nerveus", face_amt=0.6, at=S.head(agent, t_g))

# ---------------------------------------------------------------- 7h: de winkel kijkt elkaar aan... en breekt los
SHOP = [("figurant_a", (-6.8, -6.8), 30), ("figurant_e", (-3.45, -4.75), -20), ("figurant_f", (2.3, -6.6), 40),
        ("figurant_b", (6.8, -7.0), -30), ("buurman", (-2.3, -3.2), 180), ("figurant_c", (2.2, -2.0), 150)]
shoppers = []
for k, (nm, (x, y), r) in enumerate(SHOP):
    e = S.actor(nm, (x, y, 0), r)
    S.beat(e, 0.0, "staan", face="neutraal", face_amt=0.4, look=(0.3 if k % 2 else -0.3, -0.1))
    S.beat(e, t_h + 0.2 + 0.25 * k, "staan", face="nerveus", face_amt=0.6,
           at=S.head(shoppers[k - 1], 0.0) if k else S.head(agent, 0.0), feet="keep")
    shoppers.append(e)
# de vrouw strekt langzaam haar hand uit naar het schap (fles) ... en pakt hem
woman = shoppers[1]
FLES = V(-3.92, -4.6, 1.2)
fles = T.cyl("Fles", FLES + V(0, 0, -0.14), 0.04, 0.28, S.mat("fles_groen", (0.2, 0.55, 0.3)), seg=12, ol=0.003)
S.turn(woman, t_h + 1.0, t_h + 1.4, -90)                  # naar het schap (fles naast haar)
S.reach(woman, 0.0, "R", inf=0.0)
S.reach(woman, t_h + 1.4, "R", inf=0.0)
S.reach(woman, t_h + 2.4, "R", FLES + V(0.06, -0.08, 0.0))
grab(S, fles, woman, t_h + 2.45, "hand.R", loc=(0, 0.05, 0.0), rot=(0, 0, 0))
S.reach(woman, t_h + 2.6, "R", inf=0.0)
# en dan rent iedereen (met karren) naar de kassa's en de deur
T_GO = t_h + 2.6
LANES = [-6.2, -4.0, 0.0, 4.0]                      # baan 0 niet langs mama (-8.0, -8.3)
for k, e in enumerate(shoppers):
    lx = LANES[k % 4]
    x0, y0 = SHOP[k][1]
    path = [V(x0, y0, 0), V(lx, -9.0, 0), V(lx, -14.2, 0), V(-3.0 + 1.2 * k, -17.4, 0), V((-8.5, -3.6, 3.0, 6.6, 9.5, 12.0)[k], -22.0, 0)]   # uitgang gespreid, eindplek tussen de karbanen buiten
    t0 = T_GO + 0.12 * k
    S.run(e, t0, t0 + 5.2, path, stride=1.0, lean=12, arms=0.0 if k % 2 == 0 else 1.0)
    if k % 2 == 0:
        c = new_cart(f"Kar_{k}", path[0] + V(0, -0.8, 0))
        push_cart(e, c, t0, t0 + 5.2)
    S.beat(e, t0 + 0.2, "staan", face="inspanning", face_amt=0.8, look=(0.0, 0.0), feet="keep")
    S.hold(e, END)
    if k >= 4:                                     # buiten (7j/7k) niet meer in beeld: geen botsingen met de karren
        visible(e.body, t_j - 0.05, False)

# ---------------------------------------------------------------- 7i: mama grijpt de jongen bij zijn pols
S.beat(mama, t_h + 0.6, "staan", face="bang", face_amt=0.7, at=S.head(shoppers[0], 0.0))
S.beat(held, t_h + 1.0, "staan", face="bang", face_amt=0.6, at=S.head(shoppers[1], 0.0))
MPATH = [V(-8.0, -8.3, 0), V(-7.6, -9.6, 0), V(-7.6, -14.0, 0), V(-1.4, -17.4, 0), V(-1.0, -23.0, 0)]
HPATH = []                                         # hij rent 0,55 m rechts naast haar (zij houdt zijn pols vast)
for k, p in enumerate(MPATH):
    a = MPATH[max(0, k - 1)]
    b = MPATH[min(len(MPATH) - 1, k + 1)]
    d = (b - a).normalized()
    HPATH.append(p + V(d.y, -d.x, 0) * 0.55)
S.run(mama, t_i + 0.4, t_i + 6.6, MPATH, stride=0.95, lean=14)
S.run(held, t_i + 0.4, t_i + 6.6, HPATH, stride=0.8, lean=18)
# hand in hand: haar rechterhand (hij loopt rechts van haar) pakt zijn linkerpols, zijn arm wordt meegetrokken
S.reach(mama, 0.0, "R", inf=0.0)
S.reach(mama, t_i + 0.1, "R", inf=0.0)
for t in frange(t_i + 0.35, t_i + 6.8, 0.15):
    wrist = S.bone_world(held, "hand.L", t, tail=False)
    S.reach(mama, t, "R", wrist + V(0, 0, 0.02))
S.beat(mama, t_i + 0.3, "staan", face="vastberaden", face_amt=0.9, look=(0.0, 0.0), feet="keep")
S.beat(held, t_i + 0.5, "schrik", amount=0.5, face="geschrokken", face_amt=0.8, at=S.head(mama, t_i + 0.5), feet="keep")
S.beat(held, t_i + 1.6, "staan", face="bang", face_amt=0.8, look=(0.4, 0.0), feet="keep")
S.hold(mama, END)
S.hold(held, END)
S.beat(agent, t_h + 2.8, "staan", face="verdrietig", face_amt=0.6, at=S.head(shoppers[0], t_h + 3.0))
S.hold(agent, END)
S.beat(kas, t_h + 2.8, "handen_hoofd", amount=0.8, face="geschrokken", face_amt=0.9, at=S.head(shoppers[2], t_h + 3.0))
S.hold(kas, END)

# ---------------------------------------------------------------- 7j/7k: buiten, karren de parkeerplaats op
OUT = []
for k in range(5):
    nm = ["figurant_a", "figurant_d", "figurant_e", "figurant_f", "figurant_b"][k]
    e = S.actor(nm, (-5.0 + 2.5 * k, -19.6, 0), 0, label=f"buiten_{k}")
    p0 = V(-5.0 + 2.5 * k, -19.6 - 0.9 * (k % 2), 0)     # verder van de deur, ruim uit elkaar
    lane = (-13.5, -7.5, 2.2, 5.2, 10.5)[k]                                   # tussen de geparkeerde auto's door, op volgorde: niemand kruist
    p1 = V(lane, -33.0 - 1.5 * (k % 2), 0)
    t0 = t_j - 0.3 + 0.35 * k
    S.teleport(e, t0 - 0.05, p0, 0)
    pm = V(lane, -23.0, 0)
    S.run(e, t0, END, [p0, pm, p1], stride=1.0, lean=12, arms=0.0)
    c = new_cart(f"Kar_buiten_{k}", p0 + V(0, -0.8, 0))
    push_cart(e, c, t0, END)
    S.beat(e, t0 + 0.2, "staan", face="inspanning", face_amt=0.8, feet="keep")
    S.hold(e, END)
    visible(e.body, 0.0, False)
    visible(e.body, t_j - 0.05, True)
    OUT.append(e)

# ---------------------------------------------------------------- camera's
S.cam(t_d, ((-3.6, -15.8, 2.3), (-9.0, -10.0, 1.2), 26), ((-4.2, -15.4, 2.2), (-9.2, -10.2, 1.15), 28))
HK = S.headpos(kas, t_f + 1.0)
HDF = S.headpos(dief, t_e + 0.8)
S.cam(t_e, ((-8.0, -14.2, 1.5), V(-9.85, -12.0, 1.2), 28), ((-11.3, -15.3, 1.65), V(-7.0, -14.6, 1.1), 26))
S.cam(t_f, (HK + V(0.95, 1.45, 0.0), HK + V(0, 0, 0.0), 36), (HK + V(0.88, 1.35, 0.0), HK + V(0, 0, 0.0), 38))
HA = S.headpos(agent, t_g + 1.5)
S.cam(t_g, (HA + V(0.6, -1.75, 0.05), HA + V(0, 0, 0.02), 38), (HA + V(0.5, -1.4, 0.04), HA + V(0, 0, 0.02), 40))
S.cam(t_h, ((5.5, -14.5, 3.0), (-3.0, -6.5, 1.0), 22), ((5.4, -14.3, 3.0), (-3.0, -6.5, 1.0), 22), shake=lambda t: 0.0 if t < T_GO else 0.9,
      ease=False)
S.cam(t_i, None, fn=S.follow(mama, (2.3, -2.8, 1.55), lens=26, look_offset=(-0.4, 0.0, -0.3)), shake=S.shake(0.8))
S.cam(t_j, ((0.0, -44.0, 15.0), (0.0, -20.0, 0.5), 26), ((0.0, -42.0, 13.0), (0.0, -22.0, 0.5), 26))
S.cam(t_k, ((15.0, -36.5, 0.7), (0.0, -27.0, 1.2), 24), ((14.8, -36.2, 0.7), (-1.0, -28.0, 1.2), 24), handheld=0.6)

# ---------------------------------------------------------------- HUD, geluid, stemmen
S.counter("DAY 1", 0)
S.ambience("sfx_supermarkt_sfeer", 0.0, t_h, vol=0.16)
S.sfx("sfx_kassa_piep", t_d + 0.8, 0.25)
S.sfx("sfx_kassa_piep", t_d + 2.3, 0.25)
S.sfx("sfx_schuiven", t_e + 0.6, 0.2)
S.sfx("sfx_glasdeur", t_e + 3.2, 0.2)
S.sfx("sfx_hartslag", t_h + 0.1, 0.25, cut=(0.0, 2.4))
S.sfx("sfx_paniek_karren", T_GO, 0.5, loop_to=t_j)
S.sfx("sfx_menigte_mompel", T_GO + 0.3, 0.3, loop_to=END)
S.sfx("sfx_paniek_karren", t_j, 0.35, loop_to=END)
S.say("N07-05", at=t_h + 3.0)
S.say("N07-06", at=t_j + 1.75)
S.finish(length=END, tail=0.0)
