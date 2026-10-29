"""F10a · Dag 4 · 1.000x · straat in de grijze ochtend. Mama komt naar het voorraam en schrijft er met de
whiteboardstift op, achterstevoren, zodat hij het buiten kan lezen. Eén letter per shot (een seconde voor haar,
zeventien minuten voor hem). Zeven uur later: COME INSIDE. WE'RE NOT SCARED. Hij gaat toch naar binnen.

    blender -b -P anim/v2/scenes/f10a_raam.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f10a", "straat", "grijs")

WIN = V(1.2, 12.93, 1.83)                        # midden van het grote voorraam (glas: x 0.1..2.3, z 1.08..2.58)
MOM_AT = V(1.2, 13.42, 0.15)                     # binnen, een halve meter achter het glas
H0 = V(0.85, 10.0, 0.12)                         # hij staat in de voortuin
DOOR = V(-1.4, 12.25, 0.15)                      # op het stoepje voor de voordeur

for nm in ("Vuilniswagen", "Kraai", "Plastic_zak"):
    o = S.obj(nm)
    o.hide_render = True
    for c in o.children_recursive:
        c.hide_render = True

# ---------------------------------------------------------------- het voorraam open: een kamer achter het glas
house = S.obj("Huis_hoofdpersonage")
glas = bpy.data.materials.new("voorraam_glas")
glas.use_nodes = True
b = glas.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.78, 0.86, 0.95, 1)
b.inputs["Roughness"].default_value = 0.05
b.inputs["Alpha"].default_value = 0.16
glas.surface_render_method = "BLENDED"
glas.diffuse_color = (0.7, 0.8, 0.9, 0.15)
for nm, loc, size in (("Voorraam_gat", (1.2, 13.06, 1.08), (2.2, 0.32, 1.5)), ("Voorraam_kamer", (1.2, 14.5, 0.15), (3.6, 2.9, 2.75))):
    cut = T.box(nm, loc, size, glas, bevel=0, ol=0)
    cut.hide_render = True
    cut.display_type = "WIRE"
    mod = house.modifiers.new(nm, "BOOLEAN")    # twee losse booleans: één samengevoegde snijvorm overlapt zichzelf
    mod.object = cut
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.use_self = True
    mod.use_hole_tolerant = True
T.box("Voorraam_ruit", (1.2, 12.925, 1.08), (2.2, 0.01, 1.5), glas, bevel=0, ol=0)
T.box("Voorkamer_vloer", (1.2, 14.5, 0.13), (3.58, 2.88, 0.02), S.mat("vloer_eiken", (0.62, 0.45, 0.30)), bevel=0, ol=0)
T.box("Voorkamer_bank", (1.6, 15.55, 0.15), (2.0, 0.75, 0.45), S.mat("bank_blauw", (0.25, 0.38, 0.62)), bevel=0.06, ol=0)
T.box("Voorkamer_bank_rug", (1.6, 15.82, 0.6), (2.0, 0.2, 0.45), S.mat("bank_blauw", (0.25, 0.38, 0.62)), bevel=0.06, ol=0)
T.box("Voorkamer_schilderij", (0.6, 15.93, 1.35), (0.8, 0.03, 0.6), S.mat("schilderij_lijst", (0.85, 0.75, 0.45)), bevel=0.01, ol=0)
T.box("Voorkamer_schilderij_doek", (0.6, 15.91, 1.4), (0.7, 0.02, 0.5), S.mat("schilderij_zee", (0.35, 0.6, 0.75)), bevel=0, ol=0)
T.cyl("Voorkamer_lamp_voet", (-0.3, 15.5, 0.15), 0.03, 1.5, P.m("zwart"), seg=8, ol=0)
T.cyl("Voorkamer_lamp_kap", (-0.3, 15.5, 1.55), 0.22, 0.3, S.mat("lampkap", (1.0, 0.9, 0.7), glow=2.0), r2=0.14, seg=16, ol=0)
lamp = bpy.data.lights.new("Voorkamer_licht", "POINT")
lamp.energy = 180
lamp.color = (1.0, 0.82, 0.6)
lamp.shadow_soft_size = 0.6
lo = bpy.data.objects.new("Voorkamer_licht", lamp)
lo.location = (1.0, 14.9, 2.3)
T._link(lo)
lamp2 = bpy.data.lights.new("Voorkamer_licht_raam", "POINT")   # zacht licht op haar gezicht
lamp2.energy = 70
lamp2.color = (1.0, 0.9, 0.8)
lamp2.shadow_soft_size = 0.5
lo2 = bpy.data.objects.new("Voorkamer_licht_raam", lamp2)
lo2.location = (1.2, 13.05, 2.45)
T._link(lo2)

# ---------------------------------------------------------------- de tekst op het raam (aan de binnenkant van het glas)
LINES = ["COME INSIDE.", "WE'RE NOT", "SCARED."]
ZS = -0.3                                        # iets lager dan in de set: op haar hoogte
bpy.context.view_layer.update()
src = [S.obj(f"Raamtekst_regel{k + 1}") for k in range(3)]
left_x, width = [], []
for o in src:
    xs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    left_x.append(min(p.x for p in xs))
    width.append(max(p.x for p in xs) - min(p.x for p in xs))
    o.hide_render = True
MARKS = [(i, j) for i, ln in enumerate(LINES) for j, ch in enumerate(ln) if ch != " "]   # 26 streken
prefix = {}
for i, o in enumerate(src):
    for j in range(len(LINES[i])):
        if LINES[i][j] == " ":
            continue
        p = o.copy()
        p.data = o.data.copy()
        p.data.body = LINES[i][:j + 1]
        p.data.align_x = "LEFT"
        p.name = f"Raamtekst_{i + 1}_{j + 1:02d}"
        p.location = (left_x[i], 12.94, o.location.z + ZS)
        p.hide_render = False
        T._link(p)
        prefix[(i, j)] = p


def mark_pos(n):
    """Wereldpunt van streek n (waar haar stift dan staat)."""
    i, j = MARKS[min(n, len(MARKS) - 1)]
    o = src[i]
    return V(left_x[i] + width[i] * (j + 0.5) / len(LINES[i]), 13.1, o.location.z + ZS + 0.05)


# ---------------------------------------------------------------- tijdlijn
l1 = S.say("F10-01", gap=0.6)
l2 = S.say("F10-02", gap=0.5)
LAPSE0 = l2[1] + 0.3                             # versneld: de rest van de letters
LAPSE = [LAPSE0 + 0.2 * k for k in range(19)]    # streken 7..25
l3 = S.say("F10-03", at=LAPSE[-1] + 0.6)
d3 = l3[1] - l3[0]
LIE = l3[0] + 0.55 * d3                          # 'She's lying.'
GO = l3[0] + 0.86 * d3                           # 'You go in anyway.'
END = l3[1] + 2.2

# (tijd, aantal streken op het raam, zijn minuten sinds hij bij het raam staat)
SHOTS = [(0.0, 0, 0)]
STEADY = [l1[0] + 2.3, l1[0] + 4.2, l2[0] + 0.1, l2[0] + 1.5, l2[0] + 2.9, l2[0] + 4.1]
for k, t in enumerate(STEADY):
    SHOTS.append((t, k + 1, 17 * (k + 1)))
for k, t in enumerate(LAPSE):
    SHOTS.append((t, k + 7, 17 * (k + 7)))
SHOTS.append((l3[0] - 0.3, 26, 7 * 60 + 25))
SHOTS.append((GO - 0.2, 26, 7 * 60 + 40))


def n_at(t):
    n = 0
    for ts, k, _ in SHOTS:
        if t >= ts:
            n = k
    return n


def his_min(t):
    m, base = 0.0, 0.0
    for ts, _, mm in SHOTS:
        if t >= ts:
            m, base = mm, ts
    return m + (t - base) / 60


# de tekst: per regel het stuk dat er al staat
for (i, j), p in prefix.items():
    k = MARKS.index((i, j))
    t0 = next(ts for ts, n, _ in SHOTS if n > k)
    later = [m for m in MARKS[k + 1:] if m[0] == i]
    t1 = None
    if later:
        k2 = MARKS.index(later[0])
        t1 = next(ts for ts, n, _ in SHOTS if n > k2)
    show(p, t0, t1)

START = 8 * 3600 + 58 * 60 + 44.0                # net na de redding (F09 eindigt rond 08:58:42)
S.hud2(4, "1,000x", clock=lambda t: hms(START + his_min(t) * 60 / 1000, 2, "TUE"), t0=0.3,
       awake=lambda t: awake(1.0, rate=1 / 60)(his_min(t)), awake_t0=0.5)
S.gauge2("1 LETTER = 17 MIN", l2[0] + 0.2, LAPSE0, color=GOLD, row=0)
S.gauge2(lambda t: f"LETTERS: {n_at(t)}/26", l2[0] + 0.2, l3[0] + 1.5, color=GOLD, row=1)
S.music("piano_zacht", 0.0, END, vol=0.15, fade_in=1.0, fade_out=2.0)
S.music("strijkers_warm", l3[0] + 1.2, END, vol=0.15, fade_in=1.5, fade_out=2.0)
S.ambience("sfx_straat_sfeer", 0.0, END, vol=0.05)
for t in STEADY:
    S.sfx("sfx_stift", t, 0.22, cut=(0, 0.35))
S.card("", END - 1.0, END + 0.5, dim=1.0, fin=20, fout=1)

# ---------------------------------------------------------------- mama achter het raam (bevroren; elke snede een letter verder)
mama = S.actor("mama", MOM_AT, 0, outfit=dict(shirt=(0.86, 0.62, 0.76), broek=(0.86, 0.62, 0.76)))
stift = T.cyl("Stift_mama", (0, 0, 0), 0.014, 0.15, S.mat("stift_blauw_huls", (0.15, 0.3, 0.85)), rot=(90, 0, 0), seg=10, ol=0)
grab(S, stift, mama, 0.0, "hand.R", mode="loc", offset=(0, 0.05, 0))   # wijst naar het glas
S.reach(mama, 0.0, "L", None, 0.0)
CHEST = V(mark_pos(25).x + 0.33, MOM_AT.y, MOM_AT.z) + V(0.1, -0.2, 1.22)              # haar linkerhand tegen haar borst
for ts, n, _ in SHOTS:
    tgt = mark_pos(n) if n < 26 else mark_pos(25) + V(0.08, 0.0, -0.06)
    body = V(min(2.0, max(0.45, tgt.x + 0.33)), MOM_AT.y, MOM_AT.z)   # ze schuift mee, de stift rechts van haar
    if ts > 0:
        S.reach(mama, ts - 1.0 / FPS, "R", prev)
        S.teleport(mama, ts, body, 0)
    else:
        S.place(mama, 0.0, body, 0)
    S.reach(mama, ts, "R", tgt)
    prev = tgt
S.reach(mama, LIE - 1.0 / FPS, "L", None, 0.0)
S.reach(mama, LIE, "L", CHEST)
S.beat(mama, 0.0, "staan", face="nerveus", face_amt=0.6, at=S.head(mama) + V(0, -3.0, -0.9))
S.beat(mama, l3[0] - 0.3, "staan", face="nerveus", face_amt=0.4, at=H0 + V(0, 0, 1.0), mouth=0.15)
S.hold(mama, END)

# ---------------------------------------------------------------- hij: tussen de sneden verstrijken minuten, dus hij staat steeds anders
held = S.actor("hoofdpersonage", H0, heading(H0, WIN))
SIT_H, zh = sit(held, seat_top=0.15)
S.reach(held, 0.0, "L", None, 0.0)
S.reach(held, 0.0, "R", None, 0.0)
SPOTS = [  # (positie, houding, armen)
    (H0, "staan", None),
    (H0 + V(-0.3, 0.3, 0), "armen_over", None),
    (H0 + V(0.25, 0.9, 0), "staan", None),
    (H0 + V(-0.5, -0.2, 0), "handen_zij", None),
]
S.beat(held, 0.0, "staan", face="verdrietig", face_amt=0.5, at=WIN)
S.beat(held, STEADY[1], "staan", face="neutraal", face_amt=0.5, at=mark_pos(2))
S.teleport(held, STEADY[3], SPOTS[1][0], heading(SPOTS[1][0], WIN))
S.beat(held, STEADY[3], "armen_over", face="verdrietig", face_amt=0.4, at=mark_pos(4))
S.teleport(held, LAPSE[0], SPOTS[2][0], heading(SPOTS[2][0], WIN))
S.beat(held, LAPSE[0], "staan", face="neutraal", face_amt=0.5, at=mark_pos(7))
S.teleport(held, LAPSE[4], DOOR + V(0, -0.05, zh - 0.15), 30)
S.beat(held, LAPSE[4], **SIT_H, pose="ontspannen", face="verdrietig", face_amt=0.5, at=WIN,
       arms=arms(arm("L", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3)), arm("R", (0.2, 0.6, -0.75), (0.0, 0.85, 0.3))))
S.teleport(held, LAPSE[9], SPOTS[3][0], heading(SPOTS[3][0], WIN))
S.beat(held, LAPSE[9], "handen_zij", face="neutraal", face_amt=0.4, at=WIN)
S.teleport(held, LAPSE[13], H0 + V(0.2, 1.4, 0), heading(H0 + V(0.2, 1.4, 0), WIN))
S.beat(held, LAPSE[13], "armen_over", face="verdrietig", face_amt=0.5, at=WIN)
S.teleport(held, LAPSE[17], H0, heading(H0, WIN))
S.beat(held, LAPSE[17], "staan", face="neutraal", face_amt=0.4, at=WIN)
S.beat(held, l3[0] + 0.5, "staan", face="verdrietig", face_amt=0.5, at=S.head(mama))
S.beat(held, LIE, "staan", face="verdrietig", face_amt=0.8, at=mark_pos(25))
S.beat(held, GO - 0.2, "staan", face="vastberaden", face_amt=0.5, at=DOOR + V(0, 0, 1.2))
S.walk(held, GO + 0.1, END - 0.6, [H0, V(-0.2, 10.4, 0.12), V(-1.4, 10.9, 0.12), V(-1.4, 11.85, 0.12)], stride=0.12)
S.hold(held, END)

# ---------------------------------------------------------------- camera
TXT = V(1.2, 12.9, 1.65)
S.cam(0.0, ((-0.8, 7.0, 1.5), (0.9, 12.5, 1.55), 30), ((-0.6, 7.4, 1.5), (0.95, 12.5, 1.6), 32))
S.cam(STEADY[0], ((0.75, 10.9, 1.75), (0.85, 13.1, 1.7), 30), ((0.75, 11.0, 1.75), (0.85, 13.1, 1.7), 32), dof=2.2)
HH = S.headpos(held, STEADY[1] + 0.2)
S.cam(STEADY[1], (HH + V(-0.7, -2.2, 0.3), WIN + V(-0.2, 0, 0.1), 34), (HH + V(-0.65, -2.1, 0.3), WIN + V(-0.2, 0, 0.1), 36))
S.cam(STEADY[2], ((2.6, 14.4, 1.9), (0.85, 10.0, 1.0), 30), ((2.55, 14.3, 1.9), (0.85, 10.0, 1.0), 32))
MH = S.headpos(mama, STEADY[3] + 0.2)
S.cam(STEADY[3], ((1.0, 11.9, MH.z - 0.1), MH, 45), ((1.0, 11.95, MH.z - 0.1), MH, 48), dof=0.9)
HF = S.headpos(held, STEADY[4] + 0.2)
S.cam(STEADY[4], (HF + V(0.12, 1.15, 0.0), HF, 40), (HF + V(0.1, 1.05, 0.0), HF, 42), dof=1.0)
S.cam(STEADY[5], ((1.6, 11.0, 1.4), (0.9, 12.9, 1.85), 34), ((1.55, 11.05, 1.4), (0.9, 12.9, 1.85), 36))
S.cam(LAPSE0, ((-1.9, 7.0, 2.7), (0.7, 12.6, 1.3), 27), handheld=0.0)
S.cam(l3[0] - 0.3, ((1.6, 8.7, 1.45), TXT, 36), ((1.55, 9.3, 1.5), TXT, 38))
HAND = mark_pos(25)
S.cam(LIE - 0.2, (HAND + V(-0.5, -0.9, -0.15), HAND + V(-0.15, 0.3, -0.12), 42),
      (HAND + V(-0.45, -0.85, -0.15), HAND + V(-0.15, 0.3, -0.12), 45), dof=0.9)
S.cam(GO - 0.2, ((2.4, 8.4, 1.7), (-0.6, 11.6, 1.1), 28), ((2.3, 8.6, 1.7), (-0.8, 11.8, 1.1), 30))

S.finish(length=END)
