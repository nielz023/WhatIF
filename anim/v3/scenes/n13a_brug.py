"""N13a · Dag 7: de brug (script scène 13a-13h), schemer met warm tegenlicht en lichte mist.
13a WIDE trage push: midden op de brug de pestkop en drie volgelingen in een rij; de jongens 10 m verder met hun fietsen.
13b CLOSE: de pestkop, armen over elkaar. PESTKOP: "This bridge is mine. Want to cross? Pay."
13c CLOSE: de jongen. JONGEN: "We've got nothing."
13d MEDIUM statisch: de pestkop wijst met zijn kin naar de rode fiets; de vriend klemt zijn handen om het stuur.
13e CLOSE: de vriend kijkt naar de jongen, lange blik, knippert, laat het stuur langzaam los.
13f WIDE: de vriend duwt de fiets naar voren (wielen rollen), de pestkop pakt hem aan en stapt opzij, volgelingen ook.
13g MEDIUM track: de jongens steken de brug over, de vriend lopend, de jongen fietst langzaam naast hem.
    VO: "No laws to stop him. Only one rule left: whoever's strongest... wins."
13h WIDE: aan de overkant het lab (één zonnepaneel, één lamp). De deur op een kier, dan helemaal open: de wetenschapper (man).

    blender -b -P anim/v3/scenes/n13a_brug.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n13a", "brug", "lab_buiten", exposure=0.1)
sh = S.cuts([4.0, 4.2, 2.2, 3.0, 3.0, 4.6, 6.0, 4.2])
END = sh[-1][1]
t_b, t_c, t_d, t_e, t_f, t_g, t_h = [s[0] for s in sh[1:]]

for o in list(bpy.data.objects):
    if o.name.startswith(("Fiets_held", "Fiets_vriend")) or (o.name.startswith(("Bram", "Hoofdpersonage")) and o.type != "CAMERA"):
        o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- de bende op de brug (kijkt naar -y, naar de jongens)
P0 = V(0.0, 1.8, 0)
pest = S.actor("pestkop", P0, 0)
GANG = {"volgeling_a": V(-2.3, 2.3, 0), "volgeling_b": V(1.25, 2.2, 0), "volgeling_c": V(2.45, 2.7, 0)}
vol = {n: S.actor(n, p, 0) for n, p in GANG.items()}

# ---------------------------------------------------------------- de jongens met hun fietsen (kijken naar +y)
H0, V0 = V(-0.8, -8.0, 0), V(0.9, -8.2, 0)
held = S.actor("hoofdpersonage_kind", H0, 180)
vr = S.actor("beste_vriend", V0, 180)
no_phone(vr)
fh = ST3.fiets2("Fiets_jongen_staand", (-1.45, -8.25, 0), rot=90, color=(0.15, 0.35, 0.75))
fv = ST3.fiets2("Fiets_vriend_rood", (1.22, -8.36, 0), rot=90, color=(0.85, 0.12, 0.10), sticker=True)
visible(fh, 0.0, True)
visible(fh, t_g, False)
bpy.context.view_layer.update()


def grip(b, side):
    """Handvat van een fiets die naar +y kijkt: links = -x, rechts = +x."""
    return S.obj(b.name + "_stuurdeel").matrix_world @ V(0, 0.24 if side == "L" else -0.24, 0.1)


# de jongen: linkerhand aan zijn stuur
S.reach(held, 0.0, "L", grip(fh, "R"))
S.reach(held, t_g - 0.05, "L", grip(fh, "R"))
S.reach(held, 0.0, "R", inf=0.0)
S.beat(held, 0.0, "staan", face="vastberaden", face_amt=0.5, at=S.headpos(pest, 0.0), feet="keep")
S.beat(held, t_c, "staan", face="vastberaden", face_amt=0.7, at=S.headpos(pest, 0.0), feet="keep")
S.beat(held, t_e + 0.2, "staan", face="twijfel", face_amt=0.6, at=S.headpos(vr, 0.0), feet="keep")
S.beat(held, t_e + 1.6, "staan", face="vastberaden", face_amt=0.3, at=S.headpos(vr, 0.0), feet="keep")
S.say("N13-02", who=held, at=t_c + 0.3)

# de vriend: beide handen om het stuur, in 13d klemt hij ze vast, in 13e laat hij langzaam los
for side in ("L", "R"):
    S.reach(vr, 0.0, side, grip(fv, side))
    S.reach(vr, t_e + 1.3, side, grip(fv, side))
    S.reach(vr, t_e + 2.6, side, inf=0.0)
S.beat(vr, 0.0, "staan", face="nerveus", face_amt=0.5, at=S.headpos(pest, 0.0), feet="keep")
S.beat(vr, t_d + 0.9, "staan", face="geschrokken", face_amt=0.7, at=grip(fv, "L") + V(0.2, 0.3, 0), feet="keep")
S.beat(vr, t_e, "staan", face="twijfel", face_amt=0.8, at=S.headpos(held, 0.0), feet="keep")
A.blink_at(vr, F(t_e + 0.9))
S.beat(vr, t_e + 1.8, "staan", face="verdrietig", face_amt=0.6, at=S.headpos(held, 0.0), feet="keep")

# de pestkop: armen over elkaar, praat, dan de kin naar de rode fiets
S.beat(pest, 0.0, "armen_over", face="zelfverzekerd", face_amt=0.7, at=S.headpos(held, 0.0))
S.beat(pest, t_b + 0.3, "armen_over", face="grijns", face_amt=0.8, at=S.headpos(held, 0.0))
S.say("N13-01", who=pest, at=t_b + 0.25)
S.beat(pest, t_d, "armen_over", face="zelfverzekerd", face_amt=0.9, at=V(1.5, -8.1, 0.7), body={"head": (-14, 0, 0)})
S.beat(pest, t_d + 1.4, "armen_over", face="grijns", face_amt=0.9, at=V(1.5, -8.1, 0.7))
for n, ch in vol.items():
    S.beat(ch, 0.0, "armen_over" if n != "volgeling_b" else "handen_zij", face="grijns", face_amt=0.5, at=S.headpos(held, 0.0))

# ---------------------------------------------------------------- 13f: de vriend duwt de fiets naar de pestkop
F_START = V(0.9, -4.6, 0)                    # (na de close een stukje dichterbij; de wide begint met hem al lopend)
F_STOP = V(0.6, -0.2, 0)
T_WALK1 = t_f + 2.6
T_TAKE = t_f + 2.9
S.teleport(vr, t_f, F_START, 180)
vr.rig.location = tuple(F_START)
vr.rig.keyframe_insert("location", frame=F(t_f))
S.walk(vr, t_f + 0.1, T_WALK1, [F_START, F_STOP], stride=0.36, turn=False)
OFF_B = V(-0.32, 0.16, 0)                     # fiets rechts naast hem, stuur net voor hem
BIKE_TAKE = F_STOP + OFF_B
# de pestkop komt een stap naar voren en pakt het stuur
P1 = V(0.25, 1.15, 0)
S.walk(pest, t_f + 1.6, T_TAKE - 0.05, [P0, P1], stride=0.3, turn=False)
S.beat(pest, t_f + 1.2, "staan", face="grijns", face_amt=0.9, at=BIKE_TAKE + V(0, 0, 0.8), feet="keep")
# daarna stapt hij met de fiets opzij (naar -x), de volgelingen gaan ook opzij
P2 = V(2.5, 0.9, 0)
T_ASIDE0, T_ASIDE1 = T_TAKE + 0.4, t_f + 4.6
S.walk(pest, T_ASIDE0, T_ASIDE1, [P1, P2], stride=0.32)
S.turn(pest, T_ASIDE1, T_ASIDE1 + 0.5, 40)
GANG2 = {"volgeling_a": V(-3.4, 2.6, 0), "volgeling_b": V(3.7, 2.2, 0), "volgeling_c": V(3.2, 3.5, 0)}
for i, (n, ch) in enumerate(vol.items()):
    t0 = T_TAKE + 0.2 + 0.15 * i
    S.walk(ch, t0, t0 + 1.2, [GANG[n], GANG2[n]], stride=0.32)
    S.turn(ch, t0 + 1.25, t0 + 1.7, -50 if GANG2[n].x < 0 else 50)
    S.beat(ch, t0 + 1.8, "armen_over", face="grijns", face_amt=0.6, at=V(0, -1.0, 1.4))

# fiets: tot T_TAKE voor de vriend uit, daarna voor de pestkop uit (hij heeft hem aan het stuur, rechts van hem)
WR = 0.33
wv, wa = S.obj(fv.name + "_wiel_v"), S.obj(fv.name + "_wiel_a")
fv.rotation_mode = "XYZ"
prev, roll = None, 0.0
for f in range(F(0.0), F(END) + 1):
    t = (f - 1) / FPS
    if t < t_f:
        loc, yaw = V(1.22, -8.36, 0), 90.0
    elif t < T_TAKE:
        M = S._root_matrix(vr, t)
        loc, yaw = M @ OFF_B, 90.0
    else:
        M = S._root_matrix(pest, t)
        yaw = math.degrees(M.to_euler().z) - 90.0                  # pestkop kijkt (sin, -cos); fiets wijst dezelfde kant op
        loc = M @ V(-0.55, -0.4, 0)                                # rechts voor hem
        if t < T_TAKE + 0.25:                                      # zachte overgang van vriend naar pestkop
            u = (t - T_TAKE) / 0.25
            loc = (S._root_matrix(vr, T_TAKE) @ OFF_B).lerp(loc, u)
            yaw = 90.0 + (yaw - 90.0) * u
    if prev is not None:
        roll += (loc - prev).length / WR
    prev = loc.copy()
    fv.location = loc
    fv.rotation_euler = (0, 0, math.radians(yaw))
    fv.keyframe_insert("location", frame=f)
    fv.keyframe_insert("rotation_euler", frame=f)
    for w in (wv, wa):
        w.rotation_euler.y = roll
        w.keyframe_insert("rotation_euler", index=1, frame=f)
for t in frange(t_f, END, 0.2):
    S.sc.frame_set(F(t))
    if t < T_TAKE:
        for side in ("L", "R"):
            S.reach(vr, t, side, grip(fv, side))
    if t >= T_TAKE - 0.3:
        S.reach(pest, t, "L", grip(fv, "L"))
S.reach(pest, T_TAKE - 0.6, "L", inf=0.0)
S.reach(pest, 0.0, "L", inf=0.0)
S.reach(pest, 0.0, "R", inf=0.0)
S.reach(vr, T_TAKE + 0.15, "L", inf=0.0)
S.reach(vr, T_TAKE + 0.15, "R", inf=0.0)
S.beat(vr, t_f, "staan", face="verdrietig", face_amt=0.6, look=(0.0, -0.1), feet="keep")
S.beat(vr, T_TAKE + 0.3, "staan", face="verdrietig", face_amt=0.8, at=S.headpos(pest, T_TAKE), feet="keep")
S.beat(pest, T_TAKE + 0.1, "staan", face="grijns", face_amt=1.0, at=S.headpos(vr, T_TAKE), feet="keep")

# de jongen in 13f: blijft achter bij zijn fiets (achter de camera)
S.beat(held, t_f + 0.5, "staan", face="boos", face_amt=0.5, at=S.headpos(vr, t_f + 2.0), feet="keep")

# ---------------------------------------------------------------- 13g: de brug over, de vriend loopt, de jongen fietst langzaam naast hem
G_H0, G_H1 = V(-0.7, -1.6, 0), V(-0.7, 8.4, 0)
G_V0, G_V1 = V(0.55, -1.1, 0), V(0.55, 7.9, 0)
S.teleport(vr, t_g, G_V0, 180)
vr.rig.location = tuple(G_V0)
vr.rig.keyframe_insert("location", frame=F(t_g))
S.walk(vr, t_g, END, [G_V0, G_V1], stride=0.38, turn=False)
S.reach(vr, t_g, "L", inf=0.0)
S.reach(vr, t_g, "R", inf=0.0)
S.beat(vr, t_g, "staan", face="verdrietig", face_amt=0.7, look=(0.0, -0.15), feet="keep")
hb, crank_h = bike(S, held, color=(0.15, 0.35, 0.75), name="Fiets_jongen")
visible(hb, 0.0, False)
visible(hb, t_g, True)
S.teleport(held, t_g, G_H0, 180)
held.rig.location = tuple(G_H0)
held.rig.keyframe_insert("location", frame=F(t_g))
ride_path(S, held, crank_h, t_g, END, [G_H0, G_H1], cadence=0.6, lean=8, sway=2)
S.face(held, t_g, "boos", 0.5, look=(0.5, 0.0))           # kijkt opzij naar de pestkop
S.face(held, t_g + 2.6, "vastberaden", 0.6, look=(-0.4, 0.0))
# de pestkop staat met de fiets opzij en kijkt ze na, de volgelingen grijnzen
S.beat(pest, t_g, "staan", face="grijns", face_amt=0.9, at=S.headpos(vr, t_g + 2.0), feet="keep")

# ---------------------------------------------------------------- 13h: het lab aan de overkant, de deur gaat open
deur = S.obj("Labdeur")
deur.rotation_mode = "XYZ"
for t, a in ((0.0, -25), (t_h + 0.3, -25), (t_h + 0.7, -38), (t_h + 1.4, -38), (t_h + 2.0, -108), (END, -110)):
    deur.rotation_euler.z = math.radians(a)
    deur.keyframe_insert("rotation_euler", index=2, frame=F(t))
WI, WO = V(6.5, 78.4, 0), V(6.55, 76.7, 0)
wet = S.actor("wetenschapper", WI, 0)
male_scientist(S, wet)
for o in list(bpy.data.objects):
    if o.name.startswith("wetenschapper_klembord"):
        o.hide_render = o.hide_viewport = True
S.beat(wet, 0.0, "staan", face="twijfel", face_amt=0.5, look=(0.0, 0.0))
S.walk(wet, t_h + 1.7, t_h + 3.2, [WI, WO], stride=0.38, turn=False)
S.beat(wet, t_h + 3.3, "staan", face="vastberaden", face_amt=0.5, at=V(0.0, 58.0, 1.4), feet="keep")
S.hold(wet, END)
for ch in [pest, held, vr] + list(vol.values()):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 13a WIDE trage push: laag achter de jongens, de bende op de brug, de boog erboven, de zon erachter
S.cam(0.0, ((0.3, -14.5, 1.0), (0.1, 1.5, 1.6), 24), ((0.3, -12.8, 1.05), (0.1, 1.5, 1.6), 26))
# 13b CLOSE de pestkop, iets van onderen
PH = S.headpos(pest, t_b + 1.0)
S.cam(t_b, (PH + V(0.42, -1.55, -0.15), PH + V(0, 0, -0.04), 32), (PH + V(0.4, -1.42, -0.14), PH + V(0, 0, -0.04), 34))
# 13c CLOSE de jongen
HH = S.headpos(held, t_c + 0.8)
S.cam(t_c, (HH + V(-0.48, 1.5, -0.02), HH + V(0, 0, -0.04), 32), (HH + V(-0.45, 1.38, -0.02), HH + V(0, 0, -0.04), 34))
# 13d MEDIUM statisch: de pestkop links, de rode fiets met de vriend rechts voor, vanaf de zijkant
S.cam(t_d, ((2.55, -10.7, 1.55), (0.1, 1.6, 1.1), 40))   # over de schouder van de vriend: het rode stuur voor, de pestkop achter
# 13e CLOSE de vriend, over de schouder van de jongen
VH = S.headpos(vr, t_e + 1.0)
S.cam(t_e, (VH + V(-1.0, 1.5, 0.02), VH + V(0, 0, -0.12), 30), (VH + V(-0.95, 1.4, 0.02), VH + V(0, 0, -0.12), 32))
# 13f WIDE van opzij: de vriend duwt de fiets naar de bende
S.cam(t_f, ((-3.6, -2.6, 1.8), (0.8, -1.2, 0.95), 20), ((-3.5, -1.7, 1.8), (0.6, 0.1, 0.95), 20))
# 13g MEDIUM track: voor de jongens uit, de pestkop met de fiets aan de rand
S.cam(t_g, None, fn=S.follow(vr, (-0.4, 4.6, 1.5), lens=28, look_offset=(-0.5, -1.0, -0.4)), shake=S.shake(0.15))
# 13h WIDE: het lab aan de overkant
S.cam(t_h, ((3.4, 69.0, 1.8), (7.0, 78.0, 2.2), 28), ((3.7, 70.2, 1.75), (6.8, 78.0, 2.0), 30))

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 7", 0, t0=0.0)
S.ambience("sfx_wind_brug", 0.0, t_h, vol=0.05)
S.ambience("sfx_stad_nacht_wind", t_h, END, vol=0.04)
S.music("m_spanning_puls", t_f, END, vol=0.18, fade_in=0.8, fade_out=0.4)
S.say("N13-03", at=t_g + 0.2)
S.sfx("sfx_deurklink", t_h + 0.3, 0.3)
S.sfx("sfx_vloer_kraak", t_h + 1.4, 0.25)
S.finish(length=END, tail=0.0)
