"""OR1 · What if your reflection stopped copying you? · nieuwe stijl, speelgoedbadkamer ('s avonds).

Echte spiegel (Cycles): jij bent alleen voor de camera zichtbaar, je spiegelbeeld (een kopie van Bram op precies
dezelfde plek) alleen in spiegelingen. Waar ze hetzelfde doen klopt de spiegel; waar ze verschillen niet meer.

1  hook: in de spiegel grijnst je spiegelbeeld al; jij niet.
2  DAY 1: het knipperen komt een seconde te laat.
3  DAY 2: het spiegelbeeld lacht. Jij niet (close op jouw gezicht).
4  DAY 3: vinger op de lippen (alleen het spiegelbeeld); de lamp flikkert.
5  DAY 4: het spiegelbeeld leunt naar het glas en schrijft RUN.
6  Achter je (in de spiegel) gaat de deur open.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orstijl import *  # noqa: E402,F401,F403

S = Kort("or1")
b = S.bram
END = S.total
r = S.r
Wd = S.W

# ------------------------------------------------------------------------------------------------ badkamer
GY = -1.5                       # spiegelmuur (voor jou)
SPOT = V(0.0, -0.5, 0.0)
tile_m = tile_mat("Tegels_mint_y", (190, 228, 218), (178, 220, 210), axis="y", scale=5.0, row=0.5, width=0.5)
tile_x = tile_mat("Tegels_mint_x", (190, 228, 218), (178, 220, 210), axis="x", scale=5.0, row=0.5, width=0.5)
floor_m = mat("Badvloer", (235, 235, 240), rough=0.3, coat=0.4)
fn = floor_m.node_tree
ck = fn.nodes.new("ShaderNodeTexChecker")
ck.inputs["Color1"].default_value = srgb(240, 240, 244)
ck.inputs["Color2"].default_value = srgb(70, 120, 150)
ck.inputs["Scale"].default_value = 8.0
tc2 = fn.nodes.new("ShaderNodeTexCoord")
fn.links.new(tc2.outputs["Object"], ck.inputs["Vector"])
fn.links.new(ck.outputs["Color"], fn.nodes["Principled BSDF"].inputs["Base Color"])
room("Badkamer", (0, 0, 0), 3.4, 3.0, 2.7, open_side=None, wall_m=tile_m, floor_m=floor_m,
     window=("-x", 0.4, 1.7, 0.8, 0.9))
for o in bpy.data.objects:
    if o.name.startswith(("Badkamer_muur-x", "Badkamer_muur+x")):
        o.data.materials[0] = tile_x
# deur in de achtermuur (+y) is apart gebouwd: die muur vervangen door stukken met een opening
for o in [o for o in bpy.data.objects if o.name == "Badkamer_muur+y"]:
    bpy.data.objects.remove(o)
DX0, DX1, DH = 0.35, 1.2, 2.05
for nm, x0, x1, z0, z1 in (("l", -1.85, DX0, 0, 2.7), ("r", DX1, 1.85, 0, 2.7), ("b", DX0, DX1, DH, 2.7)):
    box(f"Achtermuur_{nm}", ((x0 + x1) / 2, 1.575, (z0 + z1) / 2), (x1 - x0, 0.15, z1 - z0), tile_m, bev=0)
door_m = mat("Deur_wit", (245, 240, 230), rough=0.4, coat=0.3)
hinge = bpy.data.objects.new("Deurscharnier", None)
bpy.context.scene.collection.objects.link(hinge)
hinge.location = (DX0 + 0.02, 1.53, 0)
door = box("Badkamerdeur", ((DX1 - DX0) / 2 - 0.02, 0, DH / 2), (DX1 - DX0 - 0.04, 0.05, DH - 0.03), door_m, bev=0.015)
door.parent = hinge
for k, (z, hh) in enumerate(((0.55, 0.7), (1.45, 0.7))):
    p_ = box(f"Deurpaneel{k}", ((DX1 - DX0) / 2 - 0.02, -0.03, z), (0.6, 0.02, hh), door_m, bev=0.01)
    p_.parent = hinge
kn = ball("Deurklink", (DX1 - DX0 - 0.15, -0.06, 1.0), 0.04, mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6))
kn.parent = hinge
dark = mat("Gang_donker", (8, 8, 12), rough=0.9, coat=0)
box("Gang", ((DX0 + DX1) / 2, 2.8, 1.3), (1.6, 2.2, 2.7), dark, bev=0)
# wastafelmeubel, spiegel, lamp en spulletjes
wood = mat("Kastje", (245, 240, 230), rough=0.4, coat=0.3)
box("Wastafelkast", (0, GY + 0.27, 0.42), (1.3, 0.5, 0.84), wood, bev=0.03)
for k in (-1, 1):
    box(f"Kastdeurtje{k}", (k * 0.32, GY + 0.53, 0.42), (0.6, 0.02, 0.7), mat("Kastdeurtje", (225, 215, 200)), bev=0.01)
    ball(f"Kastknop{k}", (k * 0.08, GY + 0.55, 0.62), 0.025, mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6))
box("Wastafel_blad", (0, GY + 0.27, 0.86), (1.4, 0.56, 0.06), mat("Wastafelblad", (250, 250, 252), rough=0.15, coat=0.7), bev=0.02)
cyl("Kraan", (0, GY + 0.08, 0.89), 0.025, 0.2, mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6))
cyl("Kraan_tuit", (0, GY + 0.08, 1.06), 0.022, 0.15, mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6), rot=(-90, 0, 0))
cyl("Bekertje", (0.45, GY + 0.2, 0.89), 0.045, 0.12, mat("Beker_geel", (250, 200, 60), rough=0.3, coat=0.5))
for k, c in enumerate(((60, 160, 230), (240, 90, 90))):
    cyl(f"Tandenborstel{k}", (0.43 + 0.03 * k, GY + 0.2, 0.95), 0.008, 0.2, mat(f"Borstel{k}", c), rot=(0, 8 - 16 * k, 0))
box("Zeepje", (-0.45, GY + 0.25, 0.9), (0.14, 0.09, 0.05), mat("Zeep_roze", (250, 170, 190), rough=0.3, sss=0.2), bev=0.02)
cyl("Plantpot", (-1.35, GY + 0.35, 0.0), 0.16, 0.3, mat("Pot", (210, 110, 70)), r2=0.13)
ball("Plant", (-1.35, GY + 0.35, 0.48), 0.24, mat("Plantblad", (90, 170, 70), rough=0.6, sheen=0.3), (1, 1, 1.2))
mirror_m = bpy.data.materials.new("Spiegelglas")
pb = mirror_m.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = (0.9, 0.92, 0.94, 1)
pb.inputs["Metallic"].default_value = 1.0
pb.inputs["Roughness"].default_value = 0.015
MX, MZ0, MZ1 = 0.85, 1.0, 2.3
box("Spiegellijst", (0, GY + 0.025, (MZ0 + MZ1) / 2), (2 * MX + 0.1, 0.05, MZ1 - MZ0 + 0.1),
    mat("Lijst_geel", (250, 205, 90), rough=0.3, coat=0.6), bev=0.03)
box("Spiegelglas", (0, GY + 0.055, (MZ0 + MZ1) / 2), (2 * MX, 0.01, MZ1 - MZ0), mirror_m, bev=0)
GLASS_Y = GY + 0.061
box("Handdoekrek", (1.45, GY + 0.08, 1.2), (0.5, 0.04, 0.04), mat("Chroom", (220, 222, 228), rough=0.12, coat=0.6), bev=0.01)
box("Handdoek", (1.45, GY + 0.12, 0.92), (0.42, 0.05, 0.6), mat("Handdoek", (250, 130, 110), rough=0.9, sheen=0.6), bev=0.02)
box("Badmat", (0, -0.45, 0.005), (0.9, 0.6, 0.02), mat("Badmat", (120, 170, 230), rough=0.9, sheen=0.6), bev=0.01)
lamp_m = glow("Plafondlamp_gloed", (255, 240, 210), 4.0)
ball("Plafondlamp", (0, -0.3, 2.62), 0.28, lamp_m, (1, 1, 0.35))
box("Spiegellamp", (0, GY + 0.1, MZ1 + 0.12), (1.0, 0.08, 0.07), glow("Spiegellamp_gloed", (255, 246, 225), 3.0), bev=0.02)

# ------------------------------------------------------------------------------------------------ jij + spiegelbeeld
twin = S.clone(b, "spiegel")
for rig in (b, twin):
    S.place(rig, 0.0, SPOT, 0)
for o in b.char.children_recursive:
    if o.type == "MESH":
        o.visible_glossy = False          # jij: niet in de spiegel
        o.visible_shadow = False
        o.visible_diffuse = False
face_in_mirror(twin.objs)
for o in twin.objs:
    if o.type == "MESH":
        o.visible_camera = False          # spiegelbeeld: alleen in de spiegel (en zijn schaduw)
        o.visible_diffuse = False
if os.environ.get("OR1_DEBUG") == "2":
    for o in b.char.children_recursive:
        o.hide_render = True
if os.environ.get("OR1_DEBUG") == "1":            # test: spiegelbeeld gewoon zichtbaar, jij weg
    for o in twin.objs:
        o.visible_camera = True
    for o in b.char.children_recursive:
        o.hide_render = True


def both(t, **kw):
    for rig in (b, twin):
        S.beat(rig, t, **kw)


# hook: het spiegelbeeld grijnst al, jij nog niet
both(0.0, face="neutraal", head=dict(up=-3))
S.beat(twin, 0.7, face="neutraal", head=dict(up=-3))
S.beat(twin, 1.5, face="grijns", head=dict(up=-1, tilt=6))
S.beat(twin, S.e(1) - 0.05, face="grijns", head=dict(up=-1, tilt=6))
S.beat(b, 1.2, face="neutraal", head=dict(up=-3))
S.beat(b, S.e(1) - 0.05, face="nerveus", amt=0.6, head=dict(up=-3))
# DAY 1: alles klopt, alleen het knipperen is te laat
d1 = r(2) + 0.03
both(d1, face="neutraal", head=dict(up=-3))
both(Wd(2, 3) - 0.1, face="neutraal", head=dict(up=-3))
S.blink(b, Wd(2, 3) + 0.1)
S.blink(twin, Wd(2, 3) + 1.15)
both(S.e(2), face="neutraal", head=dict(up=-2, tilt=-3))
# DAY 2: het spiegelbeeld lacht, jij niet
d2 = r(3) + 0.03
both(d2, face="neutraal", head=dict(up=-3))
S.beat(b, Wd(3, 3), face="neutraal", head=dict(up=-3))
S.beat(twin, Wd(3, 3) - 0.1, face="neutraal", head=dict(up=-3))
S.beat(twin, Wd(3, 3) + 0.45, face="heel_blij", head=dict(up=-2, tilt=-7))
S.beat(b, Wd(3, 4) + 0.25, face="nerveus", head=dict(up=-3, tilt=3))
S.beat(twin, S.e(3), face="heel_blij", head=dict(up=-2, tilt=-7))
S.beat(b, S.e(3), face="nerveus", head=dict(up=-3, tilt=3))
# DAY 3: vinger op de lippen
d3 = r(4) + 0.03
both(d3, face="bang", amt=0.5, head=dict(up=-3))
S.beat(twin, Wd(4, 3) - 0.25, face="neutraal", head=dict(up=-3))
S.beat(twin, Wd(4, 5) + 0.2, face="neutraal", r_arm=("lippen"), arms="rust", head=dict(up=-4, tilt=4))
S.beat(twin, S.e(4), face="neutraal", r_arm=("lippen"), arms="rust", head=dict(up=-5, tilt=4))
S.face(twin, Wd(4, 7), "neutraal", mouth=dict(F=0.8, Lach=0.0))
S.beat(b, Wd(4, 6), face="bang", head=dict(up=-3, tilt=-3), body=dict(lean=-3))
S.beat(b, S.e(4), face="bang", head=dict(up=-3, tilt=-3), body=dict(lean=-3))
# DAY 4: het spiegelbeeld leunt naar het glas en schrijft RUN
d4 = r(5) + 0.03
both(d4, face="bang", amt=0.7, head=dict(up=-3))
S.beat(twin, d4 + 0.02, face="neutraal", head=dict(up=-3), r_arm="rust")
S.beat(twin, Wd(5, 3) - 0.3, face="neutraal", head=dict(up=-3))
WRITE = ((-70, 6, 0), (-12, 0, 0))
LEAN = dict(lean=16)
S.beat(twin, Wd(5, 3) + 0.2, face="neutraal", r_arm=WRITE, body=LEAN, head=dict(up=4))
# letters op het glas, leesbaar vanaf jouw kant
fog = glow("Wasem_letters", (215, 235, 255), 1.6)
LZ = 1.2
tw = [Wd(5, 4) + 0.1, Wd(5, 6) + 0.05, Wd(5, 8)]
letters = []
for k, ch in enumerate("RUN"):
    o = text3d(f"Letter_{ch}", ch, (-0.2 + k * 0.2, GLASS_Y + 0.004, LZ), 0.26, fog, rot=(90, 0, 180), extrude=0.0)
    o.data.size = 0.19
    o.location.x = 0.25 - k * 0.15           # camera kijkt naar -y: +x is links in beeld, dus R op +x
    letters.append(o)
    show(o, tw[k])
# de vinger 'schrijft' (kleine bewegingen per letter)
for k, t in enumerate(tw):
    S.arms(twin, t - 0.08, "rust", ((-66, 6 + 10 * (k - 1), 0), (-10, 0, 0)))
    S.arms(twin, t + 0.22, "rust", ((-60, 4 + 10 * (k - 1), 0), (-14, 0, 0)))
S.beat(twin, Wd(5, 9) - 0.1, face="neutraal", r_arm=((-58, -6, 0), (-14, 0, 0)), body=LEAN, head=dict(up=4))
S.beat(twin, Wd(5, 9) + 0.35, face="grijns", amt=0.5, r_arm="rust", body=dict(lean=6), head=dict(up=0))
S.beat(b, Wd(5, 8), face="bang", head=dict(up=-3))
S.beat(b, Wd(5, 9) + 0.05, face="geschrokken", arms="hoofd", body=dict(lean=-6, dz=-0.01), head=dict(up=0))
S.blink(b, Wd(5, 9) + 0.2)
# regel 6: achter je gaat de deur open; jij verstijft, het spiegelbeeld grijnst
d6 = r(6)
S.beat(b, d6, face="geschrokken", arms="hoofd", body=dict(lean=-6, dz=-0.01))
S.beat(b, Wd(6, 4), face="bang", arms="schrik", head=dict(turn=18, up=-2), body=dict(lean=-4))
S.beat(b, END, face="bang", arms="schrik", head=dict(turn=24, up=-2), body=dict(lean=-4))
S.beat(twin, d6 + 0.3, face="blij", amt=0.7, body=dict(lean=4))
S.beat(twin, S.e(6) - 0.5, face="grijns", head=dict(tilt=8, up=-4), body=dict(lean=2))
S.beat(twin, END, face="grijns", head=dict(tilt=9, up=-5), body=dict(lean=2))
for t, a in ((0.0, 0), (Wd(6, 3) - 0.2, 0), (S.e(6) + 0.4, 50), (END, 56)):
    key(hinge, "rotation_euler", FR(t), (0, 0, R(a)))

# ------------------------------------------------------------------------------------------------ licht
HEADP = SPOT + V(0, 0, 1.47)
ceil = area("Plafond", (0, -0.2, 2.55), (0, -0.4, 0), 1.2, 140, (1.0, 0.9, 0.75))
face_l = area("Gezicht", (0.15, GY + 0.25, 2.2), HEADP + V(0, -0.3, -0.05), 0.6, 55, (1.0, 0.92, 0.82))
cool = area("Raamlicht", (-1.6, 0.4, 1.7), HEADP, 0.9, 25, (0.6, 0.75, 1.0))
rim = area("Rand", (0.9, 1.0, 2.2), HEADP, 0.6, 40, (1.0, 0.8, 0.6))
fl = [(0, 1), (d3 - 0.01, 1), (d3 + 0.4, 0.25), (d3 + 0.48, 1), (d3 + 1.3, 0.3), (d3 + 1.36, 0.95),
      (d4, 0.7), (d4 + 2.0, 0.2), (d4 + 2.06, 0.7), (d6, 0.55), (END, 0.45)]
key_energy(ceil, [(t, 110 * f) for t, f in fl])
key_energy(face_l, [(t, 35 * f) for t, f in fl])
key_value(lamp_m.node_tree.nodes["Emission"].inputs["Strength"], [(t, 4.0 * f) for t, f in fl])

# ------------------------------------------------------------------------------------------------ camera's
MIR_HEAD = V(HEADP.x, 2 * GLASS_Y - HEADP.y, HEADP.z)
FACE = HEADP + V(0, -0.3, -0.02)


def MIRCAM(side, back, up, lens, tgt=MIR_HEAD):
    return ((HEADP.x + side, HEADP.y + back, HEADP.z + up), tuple(tgt), lens)


S.shot(0.0, MIRCAM(0.62, 0.35, 0.08, 30), MIRCAM(0.55, 0.2, 0.06, 36), focus=MIR_HEAD)
S.shot(d1, MIRCAM(-0.62, 0.3, 0.05, 32), MIRCAM(-0.55, 0.2, 0.04, 38), focus=MIR_HEAD)
S.shot(d2, MIRCAM(0.6, 0.25, 0.03, 34), MIRCAM(0.55, 0.18, 0.03, 40), focus=MIR_HEAD)
S.shot(Wd(3, 4) - 0.15, ((0.3, GLASS_Y + 0.1, HEADP.z + 0.0), tuple(FACE + V(0, 0, -0.1)), 18),
       ((0.27, GLASS_Y + 0.1, HEADP.z + 0.0), tuple(FACE + V(0, 0, -0.1)), 20), focus=FACE)
S.shot(d3, MIRCAM(0.58, 0.25, -0.1, 36, MIR_HEAD + V(0, 0, -0.15)), MIRCAM(0.52, 0.1, -0.1, 50, MIR_HEAD + V(0, 0, -0.13)),
       focus=MIR_HEAD)
S.shot(d4, ((-0.72, -0.15, 1.52), (0.0, GLASS_Y, 1.4), 28), ((-0.68, -0.25, 1.5), (0.0, GLASS_Y, 1.38), 31),
       focus=V(0, GLASS_Y, 1.4))
S.shot(Wd(5, 9) - 0.05, ((-0.5, GLASS_Y + 1.15, LZ + 0.12), (0, GLASS_Y, LZ + 0.06), 30),
       ((-0.46, GLASS_Y + 1.0, LZ + 0.12), (0, GLASS_Y, LZ + 0.06), 33), focus=V(0, GLASS_Y, LZ))
DOOR_MIR = V((DX0 + DX1) / 2, 2 * GLASS_Y - 1.55, 1.2)
S.shot(d6, MIRCAM(0.5, 1.3, 0.2, 28, (MIR_HEAD + DOOR_MIR) / 2 + V(0, 0, 0.05)),
       MIRCAM(0.46, 1.1, 0.16, 31, MIR_HEAD * 0.6 + DOOR_MIR * 0.4 + V(0, 0, 0.05)), focus=MIR_HEAD)


def world():
    sky("nacht", strength=0.4)
    sun(0.0)


S.world_fn = world
S.done()
