"""OR1 · What if your reflection stopped copying you? · badkamer, één deel.

Echte spiegel (Cycles): het hoofdpersonage zelf is onzichtbaar in spiegelingen, een tweeling ('Spiegelbeeld')
staat op precies dezelfde plek en is alleen in spiegelingen te zien. Zolang ze hetzelfde doen klopt het
spiegelbeeld; waar ze verschillen doet het spiegelbeeld iets anders dan jij.

    python3 anim/shorts/or1a_badkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orshort import *  # noqa: E402,F401,F403

S = ORShort("or1", "a", "badkamer", "binnen", lines=(1, 2, 3, 4, 5, 6))
L = S.L
END = S.t1
W = lambda n, i: L[n][0] + S.words[f"OR1-{n:02d}"][i]["s"]      # start van woord i in regel n
WE = lambda n, i: L[n][0] + S.words[f"OR1-{n:02d}"][i]["e"]

SX = -0.55
GLASS_Y = 1.185
SPOT = V(-0.45, 0.62, 0)

# -- echte spiegel, groter dan in de set (anders vult je hoofd het hele glas) -------------------------
mirror_mat = bpy.data.materials.new("echte_spiegel")
mirror_mat.use_nodes = True
pb = mirror_mat.node_tree.nodes.get("Principled BSDF")
pb.inputs["Base Color"].default_value = (0.86, 0.88, 0.9, 1)
pb.inputs["Metallic"].default_value = 1.0
pb.inputs["Roughness"].default_value = 0.02
for nm in ("Grote_spiegel", "Spiegellamp", "Handdoek", "Handdoek_streep", "Haak"):
    o = S.obj(nm)
    o.hide_render = o.hide_viewport = True
MX0, MX1, MZ0, MZ1 = -1.25, 0.35, 0.98, 2.22
MCX = (MX0 + MX1) / 2
T.box("Spiegel_lijst_groot", (MCX, GLASS_Y + 0.035, MZ0 - 0.03), (MX1 - MX0 + 0.06, 0.04, MZ1 - MZ0 + 0.06),
      S.mat("spiegellijst_chroom", (0.8, 0.8, 0.82)), bevel=0.01, ol=0)
T.box("Spiegel_glas_groot", (MCX, GLASS_Y + 0.005, MZ0), (MX1 - MX0, 0.01, MZ1 - MZ0), mirror_mat, bevel=0, ol=0)
T.box("Spiegellamp_groot", (MCX, GLASS_Y - 0.03, MZ1 + 0.05), (0.9, 0.08, 0.05), T.glow("spiegellamp2", (1.0, 0.95, 0.85), 3),
      bevel=0.01, ol=0)

# -- deur in de voormuur (achter jou, zichtbaar in de spiegel) -------------------------------------
front = S.obj("Badkamer_muur_front")
wall_mat = front.material_slots[0].material
front.hide_render = True
front.hide_viewport = True
DX0, DX1, DH = -0.45, 0.35, 2.0
for nm, x0, x1, z0, z1 in (("links", -1.4, DX0, 0, 2.5), ("rechts", DX1, 1.4, 0, 2.5), ("boven", DX0, DX1, DH, 2.5)):
    T.box(f"Voormuur_{nm}", ((x0 + x1) / 2, -1.31, z0), (x1 - x0, 0.12, z1 - z0), wall_mat, bevel=0, ol=0)
door_mat = S.mat("deur_wit", (0.86, 0.84, 0.8))
door = T.box("Badkamerdeur", ((DX0 + DX1) / 2, -1.27, 0.0), (DX1 - DX0 - 0.02, 0.04, DH - 0.02), door_mat, bevel=0.01, ol=0.004)
knob = T.sphere("Deurklink", (DX1 - 0.1, -1.23, 1.0), 0.03, S.mat("klink_chroom", (0.8, 0.8, 0.82)))
for k, (z0, h) in enumerate(((0.25, 0.7), (1.1, 0.75))):
    T.box(f"Deurpaneel{k}", ((DX0 + DX1) / 2, -1.245, z0), (0.6, 0.012, h), door_mat, bevel=0.01, ol=0.003)
door_parts = [o for o in bpy.data.objects if o.name.startswith(("Deurpaneel", "Deurklink"))]
hng = hinge(door, (DX0 + 0.01, -1.27, 0), door_parts)
# donkere gang achter de deur
dark = S.mat("gang_donker", (0.015, 0.015, 0.02))
T.box("Gang_vloer", ((DX0 + DX1) / 2, -2.4, -0.1), (2.0, 2.2, 0.1), dark, bevel=0, ol=0)
T.box("Gang_achter", ((DX0 + DX1) / 2, -3.5, 0), (2.0, 0.1, 2.5), dark, bevel=0, ol=0)
T.box("Gang_l", (DX0 - 0.45, -2.4, 0), (0.1, 2.2, 2.5), dark, bevel=0, ol=0)
T.box("Gang_r", (DX1 + 0.45, -2.4, 0), (0.1, 2.2, 2.5), dark, bevel=0, ol=0)
T.box("Gang_plafond", ((DX0 + DX1) / 2, -2.4, 2.5), (2.0, 2.2, 0.1), dark, bevel=0, ol=0)

# -- jij en je spiegelbeeld ----------------------------------------------------------------------
held = S.actor("hoofdpersonage", SPOT, 180)
refl = S.actor("hoofdpersonage", SPOT, 180, label="Spiegelbeeld")
# jij bent alleen voor de camera zichtbaar (geen schaduw, geen spiegeling, geen indirect licht); het spiegelbeeld
# alleen in spiegelingen en schaduw. Zo zitten ze elkaar op dezelfde plek nooit in de weg.
for o in held.rig.children_recursive:
    if o.type == "MESH":
        o.visible_glossy = False
        o.visible_shadow = os.environ.get("OR1_SH") == "1"
        o.visible_diffuse = os.environ.get("OR1_DIFF") == "1"        # anders blokkeert jouw huid het indirecte licht op het spiegelbeeld
for o in refl.rig.children_recursive:
    if o.type == "MESH":
        o.visible_camera = os.environ.get("OR1_DEBUG") == "1"
        o.visible_diffuse = False
if os.environ.get("OR1_DEBUG") == "2":
    for o in refl.rig.children_recursive:
        o.hide_render = True
if os.environ.get("OR1_DEBUG") == "1":
    for o in held.rig.children_recursive:
        o.hide_render = True
        o.visible_transmission = False
# geen automatisch knipperen/ademen (zou per figuur anders zijn): zelf, voor allebei gelijk
held.frozen = refl.frozen = 0.0
for ch in (held, refl):
    A.alive(ch, F(0), F(END), energy=0.7, seed=11)

HEAD = S.head(held, 0.0)
MIR_HEAD = V(HEAD.x, 2 * GLASS_Y - HEAD.y, HEAD.z)       # waar het spiegelbeeld 'staat'
print("HOOFD", tuple(round(x, 2) for x in HEAD), "straal", round(held.J["head_r"].z, 2))


def both(t, **kw):
    for ch in (held, refl):
        S.beat(ch, t, "staan", **kw)


def blink(ch, t):
    A.blink_at(ch, F(t))


# hook (0 - L1 eind): spiegelbeeld grijnst al, jij niet
S.beat(held, 0.0, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(refl, 0.0, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(refl, 0.7, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(refl, 1.5, "staan", face="grijns", face_amt=1.0, look=(0, 0.05), mouth=0.0, body={"head": (-4, 0, 6)})
S.beat(refl, L[1][1] - 0.02, "staan", face="grijns", face_amt=1.0, look=(0, 0.05), mouth=0.0, body={"head": (-4, 0, 6)})
S.beat(held, L[1][1] - 0.02, "staan", face="nerveus", face_amt=0.5, look=(0, 0.05), mouth=0.0)
# dag 1: alles normaal, alleen het knipperen is te laat
d1 = L[2][0] + 0.03
both(d1, face="neutraal", look=(0, 0.05), mouth=0.0)
both(W(2, 3) - 0.1, face="neutraal", look=(0, 0.05), mouth=0.0)
blink(held, W(2, 3) + 0.1)
blink(refl, W(2, 3) + 1.15)
both(L[2][1], face="neutraal", face_amt=1.0, look=(0, 0.05), mouth=0.0, body={"head": (3, 0, 0)})
# dag 2: het spiegelbeeld lacht, jij niet
d2 = L[3][0] + 0.03
both(d2, face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(held, W(3, 3), "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(refl, W(3, 3) - 0.1, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(refl, W(3, 3) + 0.5, "staan", face="blij", face_amt=1.0, look=(0, 0.05), mouth=0.0, body={"head": (0, 0, -5)})
S.beat(held, W(3, 4) + 0.3, "staan", face="nerveus", face_amt=0.8, look=(0, 0.05), mouth=0.0)
S.beat(refl, L[3][1], "staan", face="blij", face_amt=1.0, look=(0, 0.05), mouth=0.0, body={"head": (0, 0, -5)})
S.beat(held, L[3][1], "staan", face="nerveus", face_amt=0.8, look=(0, 0.05), mouth=0.0)
# dag 3: vinger op de lippen (alleen het spiegelbeeld)
d3 = L[4][0] + 0.03
both(d3, face="bang", face_amt=0.5, look=(0, 0.05), mouth=0.0)
S.reach(refl, d3, "R", None, 0.0)
lips = S.head(refl, 0.0) + V(0.0, 0.33, -0.13)        # voor zijn mond (hij kijkt naar +y)
S.beat(refl, W(4, 3) - 0.2, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.reach(refl, W(4, 3) - 0.2, "R", None, 0.0)
S.reach(refl, W(4, 5) + 0.15, "R", lips + V(0.08, 0.05, -0.2))
S.reach(refl, W(4, 7), "R", lips)
S.beat(refl, W(4, 7), "staan", face="neutraal", look=(0, 0.05), mouth=0.0, body={"head": (6, 0, 0)})
S.reach(refl, L[4][1], "R", lips)
S.beat(held, W(4, 6), "staan", face="bang", face_amt=1.0, look=(0, 0.05), mouth=0.0)
S.beat(held, L[4][1], "staan", face="bang", face_amt=1.0, look=(0, 0.05), mouth=0.0)
# dag 4: het spiegelbeeld leunt naar het glas en schrijft RUN
d4 = L[5][0] + 0.03
S.reach(refl, d4, "R", None, 0.0)
both(d4, face="bang", face_amt=0.7, look=(0, 0.05), mouth=0.0)
S.beat(refl, W(5, 3) - 0.3, "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
LEAN = {"spine": (14, 0, 0), "chest": (10, 0, 0), "head": (-12, 0, 0)}
S.beat(refl, W(5, 3) + 0.2, "staan", face="neutraal", look=(0, 0.05), mouth=0.0, body=LEAN)
# letters R, U, N op het glas (vanaf jouw kant leesbaar), op borsthoogte van het spiegelbeeld
fog = S.mat("wasem_letters", (0.92, 0.95, 1.0), 1.2)
LX, LZ = HEAD.x - 0.36, HEAD.z - 0.2
letters = []
for k, ch_ in enumerate("RUN"):
    o = T.text(f"Letter_{ch_}", ch_, (LX - 0.16 + k * 0.16, GLASS_Y - 0.004, LZ), 0.2, fog, rot=(90, 0, 180), extrude=0.0)
    o.rotation_euler = (math.radians(90), 0, math.radians(180))
    o.scale = (-1, 1, 1)                                       # gespiegeld: leesbaar vanaf de camera-kant
    letters.append(o)
tw = [W(5, 4) + 0.1, W(5, 6) + 0.05, W(5, 8) + 0.0]
for o, t in zip(letters, tw):
    show(o, t)
# vinger volgt de letters (de hand van het spiegelbeeld 'raakt' het glas)
REACH_Y = GLASS_Y - 0.08
S.reach(refl, tw[0] - 0.6, "L", None, 0.0)
S.reach(refl, tw[0] - 0.25, "L", V(LX + 0.2, REACH_Y, LZ + 0.12))
for k, t in enumerate(tw):
    x = LX + 0.16 - k * 0.16
    S.reach(refl, t - 0.05, "L", V(x + 0.05, REACH_Y, LZ + 0.14))
    S.reach(refl, t + 0.3, "L", V(x - 0.04, REACH_Y, LZ + 0.02))
S.reach(refl, W(5, 9) - 0.2, "L", V(LX - 0.25, REACH_Y - 0.05, LZ - 0.05))
S.reach(refl, W(5, 9) + 0.25, "L", None, 0.0)
S.beat(refl, W(5, 9), "staan", face="neutraal", look=(0, 0.05), mouth=0.0)
S.beat(held, W(5, 9), "staan", face="geschrokken", face_amt=1.0, look=(0, 0.05), mouth=0.0)
S.sfx("sfx_krijt", tw[0] - 0.05, 0.25, cut=tw[2] + 0.4)
S.sfx("sfx_brass_hit", W(5, 9) - 0.03, 0.4)
# regel 6: achter je gaat de deur open; jij verstijft, het spiegelbeeld glimlacht
d6 = L[6][0]
S.beat(held, d6, "staan", face="geschrokken", face_amt=0.8, look=(0, 0.05), mouth=0.0)
S.beat(refl, d6 + 0.3, "staan", face="blij", face_amt=0.7, look=(0, 0.05), mouth=0.0)
S.beat(held, W(6, 4), "staan", face="bang", face_amt=1.0, look=(0.5, 0.05), mouth=0.0, body={"head": (0, 0, -18)})
S.beat(refl, L[6][1] - 0.5, "staan", face="grijns", face_amt=1.0, look=(0, 0.05), mouth=0.0)
S.beat(refl, END, "staan", face="grijns", face_amt=1.0, look=(0, 0.05), mouth=0.0)
S.hold(held, END)
key(hng, 0.0, rot=(0, 0, 0))
key(hng, W(6, 3) - 0.2, rot=(0, 0, 0))
key(hng, L[6][1] + 0.4, rot=(0, 0, 48))
S.sfx("sfx_vloer_kraak", W(6, 3) - 0.1, 0.5)
S.sfx("sfx_deurklink", W(6, 3) - 0.35, 0.35)

# -- licht: dag 3 en 4 flikkert de lamp ------------------------------------------------------------
lamp = S.obj("Plafondvul")
e0 = lamp.data.energy
for t, f in ((0, 1), (d3 - 0.01, 1), (d3 + 0.4, 0.25), (d3 + 0.48, 1), (d3 + 1.3, 0.3), (d3 + 1.36, 0.95),
             (d4, 0.7), (d4 + 2.0, 0.2), (d4 + 2.06, 0.7), (d6, 0.55), (END, 0.45)):
    lamp.data.energy = e0 * f
    lamp.data.keyframe_insert("energy", frame=F(t))
S.sfx("sfx_lantaarn_flikker", d3 + 0.35, 0.3)
# zacht warm licht op het gezicht (vanaf de spiegelkant, zelf niet zichtbaar in de spiegel)
fill = T.area_light("Gezichtslicht", (HEAD.x + 0.1, GLASS_Y - 0.12, 2.15), tuple(HEAD + V(0, 0, -0.1)), size=(0.6, 0.3),
                    color=(1.0, 0.9, 0.8), energy=45)
fill.visible_glossy = False
fill.visible_camera = False
for t, f in ((0, 1), (d3 - 0.01, 1), (d3 + 0.4, 0.25), (d3 + 0.48, 1), (d3 + 1.3, 0.3), (d3 + 1.36, 0.95),
             (d4, 0.7), (d4 + 2.0, 0.2), (d4 + 2.06, 0.7), (d6, 0.55), (END, 0.45)):
    fill.data.energy = 45 * f
    fill.data.keyframe_insert("energy", frame=F(t))

# -- teller, geluid, muziek -------------------------------------------------------------------------
S.counter("DAY 1", d1, L[2][1])
S.counter("DAY 2", d2, L[3][1])
S.counter("DAY 3", d3, L[4][1])
S.counter("DAY 4", d4, L[5][1], color=RED)
S.ambience("sfx_binnen_sfeer", 0.0, END, vol=0.05)
S.music_all("m_nacht_angst", vol=0.26)
S.sfx("sfx_hartslag", d4, 0.25, cut=END)

# -- camera's ----------------------------------------------------------------------------------------
# over je schouder naar de spiegel; het spiegelbeeld vult het glas
# naast je hoofd, schuin de spiegel in: het spiegelbeeld (driekwart) groot in beeld, jij net buiten beeld
def MIRCAM(side=0.62, back=0.0, up=0.03, lens=34, tgt=MIR_HEAD):
    return ((HEAD.x + side, HEAD.y - back, HEAD.z + up), tuple(tgt), lens)


def WIDE(side, back, up, lens, tgt):
    return ((HEAD.x + side, HEAD.y - back, HEAD.z + up), tuple(tgt), lens)


S.cam(0.0, MIRCAM(0.62, 0.05, 0.02, 34), MIRCAM(0.55, 0.0, 0.02, 40))
S.cam(d1, MIRCAM(0.68, 0.12, 0.04, 30), MIRCAM(0.58, 0.04, 0.02, 38))
# dag 2: eerst het spiegelbeeld, dan jouw gezicht (camera boven de wastafel)
S.cam(d2, MIRCAM(0.6, 0.1, 0.02, 36), MIRCAM(0.55, 0.05, 0.02, 40))
FACE = HEAD + V(0, 0, -0.02)
FACEPT = HEAD + V(0.0, 0.3, -0.04)       # het gezicht zelf (voorkant van het hoofd)
S.cam(W(3, 4) - 0.15, ((HEAD.x + 0.42, GLASS_Y - 0.04, HEAD.z + 0.02), tuple(FACEPT), 15),
      ((HEAD.x + 0.4, GLASS_Y - 0.05, HEAD.z + 0.02), tuple(FACEPT), 17))
# dag 3: dichtbij in de spiegel
S.cam(d3, MIRCAM(0.6, 0.1, -0.08, 34, MIR_HEAD + V(0, 0, -0.18)), MIRCAM(0.56, 0.05, -0.08, 38, MIR_HEAD + V(0, 0, -0.16)))
# dag 4: wijder, het schrijven op het glas
S.cam(d4, WIDE(-0.62, 1.25, 0.1, 26, V(LX + 0.05, GLASS_Y, LZ + 0.1)), WIDE(-0.58, 1.05, 0.08, 28, V(LX + 0.05, GLASS_Y, LZ + 0.08)))
S.cam(W(5, 9) - 0.05, ((LX - 0.12, GLASS_Y - 0.55, LZ + 0.12), (LX - 0.02, GLASS_Y, LZ + 0.08), 24),
      ((LX - 0.1, GLASS_Y - 0.48, LZ + 0.12), (LX - 0.02, GLASS_Y, LZ + 0.08), 27))
# regel 6: wijd over de schouder, de deur achter je in de spiegel
DOOR_MIR = V((DX0 + DX1) / 2, 2 * GLASS_Y + 1.27, 1.2)
S.cam(d6, WIDE(0.75, 1.3, 0.2, 26, (MIR_HEAD + DOOR_MIR) / 2 + V(0, 0, 0.1)),
      WIDE(0.68, 1.0, 0.18, 30, (MIR_HEAD * 0.6 + DOOR_MIR * 0.4) + V(0, 0, 0.1)))

S.done()
