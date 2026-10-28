"""
Cast van video 2 "What IF You Got 10x FASTER Every Day?" in de glans-look, elke figuur
geriggd en in een houding uit het script. Maakt:

    cast_10x_faster_poses.blend   alle figuren (rig + glans) + kraai + effecten
    00_cast_10x_overzicht.png     iedereen naast elkaar
    NN_<figuur>.png               per figuur een still in zijn scriptmoment

Gebruik:
    python cast/cast_10x_poses.py --out pad/uitvoer [--only papa,kraai] [--samples 64] [--pct 100]
    (of: blender -b -P cast/cast_10x_poses.py -- --out ...)
De .glb's komen uit assets/ (of WHATIF_ASSETS): assets/hoofdpersonage.glb en assets/cast/.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "anim", "lib"))
sys.path.insert(0, os.path.join(REPO, "sets"))
import rig as R  # noqa: E402
import acting as A  # noqa: E402
import glans as G  # noqa: E402
from lib import toon as T  # noqa: E402

F = 1  # alles staat op frame 1 (stills); effecten lopen tot frame 48

# extra houdingen voor deze video (zie acting.POSES voor de notatie)
A.POSES.update({
    "rennen": dict(L=((0.12, 0.65, -0.55), (0.05, 0.75, 0.62), None),
                   R=((0.12, -0.55, -0.75), (0.08, 0.15, -0.95), None),
                   body={"spine": (12, 0, 0), "chest": (6, 0, 0), "head": (-14, 0, 0)}),
    "sprint": dict(L=((0.15, -0.6, -0.7), (0.1, 0.2, -0.95), None),
                   R=((0.12, 0.7, -0.45), (0.05, 0.6, 0.78), None),
                   body={"spine": (18, 0, 0), "chest": (8, 0, 0), "head": (-18, 0, 0)}),
    "schrijven": dict(L=((0.22, 0.85, -0.35), (0.0, 0.95, 0.2), None), R=A.REST,
                      body={"head": (-6, 0, 0)}),
    "stuur": dict(L=((0.25, 0.8, -0.45), (-0.05, 0.98, 0.15), None), body={"spine": (4, 0, 0)}),
    "cadeau": dict(L=((0.2, 0.6, -0.75), (-0.4, 0.9, 0.12), None), body={"head": (-4, 0, 0)}),
    "lachen_hol": dict(L=((0.35, 0.25, -0.85), (-0.7, 0.6, 0.1), None),
                       body={"spine": (-6, 0, 0), "chest": (-8, 0, 0), "head": (-16, 0, 6)}),
})


def run_legs(ch, front="L", lift=0.22, reach=0.2, back=0.26, hip=0.06):
    """Rennen: voorste voet naar voren en omhoog, achterste voet hoog achter."""
    rear = "R" if front == "L" else "L"
    A.foot(ch, F, front, loc=(0, reach, lift), rot=(-25, 0, 0))
    A.foot(ch, F, rear, loc=(0, -back, lift * 1.15), rot=(70, 0, 0))
    A.crouch(ch, F, depth=-hip * 0.3, lean=0)
    A.bone_loc(ch, F, "root", (0, 0, 0))


def sit(ch, seat_top=0.36, lean=-4.0):
    """Zitten (zelfde rekensom als scene.sit): heupen omlaag, voeten naar voren."""
    P_ = ch.J["pelvis"].z
    ank = ch.J["ankle.L"].z
    L = P_ - ank
    drop = P_ - (seat_top + 0.07)
    vert = P_ - drop - ank
    fwd = math.sqrt(max(0.0, (0.97 * L) ** 2 - vert ** 2))
    A.crouch(ch, F, depth=drop, lean=lean)
    A.foot(ch, F, "L", loc=(0.02, fwd, 0))
    A.foot(ch, F, "R", loc=(-0.02, fwd, 0))
    seat(ch.name, ch, seat_top)


def seat(name, ch, h):
    """Simpele kruk onder een zittende figuur (stand-in voor de bestuurdersstoel)."""
    m = bpy.data.materials.new("stoel_" + name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*G.lin("#2B2F3A"), 1)
    G.RG.glossify(m)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new("stoel_" + name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    ob = bpy.data.objects.new("stoel_" + name, me)
    ch.rig.users_collection[0].objects.link(ob)
    ob.scale = (0.42, 0.36, h)
    ob.location = ch.rig.location + Vector((0, ch.J["pelvis"].y + 0.08, h / 2))
    return ob


def gift(ch, side="L"):
    """Cadeautje tussen de handen (opa en oma in de deur)."""
    mt = []
    for nm, col in (("cadeau", "#2D6CDF"), ("lint", "#F6D04D")):
        m = bpy.data.materials.new(nm + "_" + ch.name)
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*G.lin(col), 1)
        G.RG.glossify(m)
        mt.append(m)
    bpy.context.scene.frame_set(F)
    pL = ch.rig.matrix_world @ ch.pb["hand.L"].tail
    pR = ch.rig.matrix_world @ ch.pb["hand.R"].tail
    c = (pL + pR) / 2 + Vector((0, -0.03, 0.02))
    w = max((pL - pR).length - 0.02, 0.18)
    objs = []
    for nm, size, m in (("doos", (w, 0.2, 0.18), mt[0]), ("lint_a", (w + 0.01, 0.04, 0.185), mt[1]),
                        ("lint_b", (0.04, 0.21, 0.185), mt[1])):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        me = bpy.data.meshes.new(f"{nm}_{ch.name}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        ob = bpy.data.objects.new(me.name, me)
        ch.rig.users_collection[0].objects.link(ob)
        ob.scale = size
        ob.location = c
        ob.rotation_euler = ch.rig.rotation_euler
        objs.append(ob)
    return objs


def talk(ch, amount=0.45):
    A.key_prop(ch.rig, "mond_open", amount, F)


# ---------------------------------------------------------------------------
# Wie, welke houding, en wat de still laat zien (scriptmoment)
# ---------------------------------------------------------------------------
def hero(ch):
    A.pose(ch, F, "rennen")
    run_legs(ch, "L")
    A.expr(ch, F, "vastberaden", look=(0.0, 0.1))
    G.smoke(ch, "foot.L", 1, 40, n=7, size=0.08, seed=2, rise=0.22)
    G.smoke(ch, "foot.R", 1, 40, n=7, size=0.08, seed=5, rise=0.22)
    G.smoke(ch, "forearm.R", 1, 40, n=6, size=0.06, seed=7, at="tail")
    a = ch.rig.rotation_euler.z
    back = Vector((-math.sin(a), math.cos(a), 0))   # tegen de looprichting in
    G.ghosts(ch, F, [back * d for d in (0.22, 0.46, 0.72)], alphas=(0.35, 0.22, 0.12))
    return "Rent met rokende schoenen en een snelheidsspoor (dag 3)"


def broertje_dino(ch):
    A.pose(ch, F, "rennen", amount=0.85)
    run_legs(ch, "R", lift=0.14, reach=0.12, back=0.16)
    A.expr(ch, F, "bang", look=(0.3, 0.1))
    return "Midden in een sprint over straat, in zijn dinopyjama (cold open)"


def mama(ch):
    A.pose(ch, F, "schrijven")
    A.expr(ch, F, "nerveus", amount=0.6, look=(0.2, 0.25))
    return "Schrijft 'Are you hurt?' op het whiteboard (dag 3)"


def papa(ch):
    A.pose(ch, F, "lachen_hol")
    A.expr(ch, F, "lach", amount=1.0)
    talk(ch, 0.8)
    return "Bevroren midden in een lach om zijn eigen slakkengrap (dag 10)"


def opa(ch):
    A.pose(ch, F, "cadeau")
    A.expr(ch, F, "blij", amount=0.6)
    talk(ch, 0.4)
    gift(ch)
    return "In de deur met een cadeau, midden in een zin (dag 10)"


def oma(ch):
    A.pose(ch, F, "zwaaien_a")
    A.expr(ch, F, "blij")
    talk(ch, 0.3)
    return "In de deur, zwaait (dag 10)"


def beste_vriend(ch):
    A.pose(ch, F, "sprint")
    run_legs(ch, "R", lift=0.26, reach=0.22, back=0.3)
    A.expr(ch, F, "inspanning", amount=0.7)
    return "Bij het hek, één voet in de lucht, al een week dezelfde stap (dag 10)"


def pestkop(ch):
    A.pose(ch, F, "wijzen")
    A.expr(ch, F, "grijns")
    talk(ch, 0.35)
    return "'Snail!' (dag 1)"


def wetenschapper(ch):
    A.pose(ch, F, "schrijven")
    A.expr(ch, F, "vastberaden", amount=0.6, look=(0.2, 0.2))
    return "Schrijft de rekensom en 'Unless you stay awake.' (dag 3)"


def gymleraar(ch):
    A.pose(ch, F, "wijzen")
    A.expr(ch, F, "schreeuw", amount=0.8)
    return "Gymles, fluit en wijst (dag 1)"


def bezorger(ch):
    A.pose(ch, F, "stuur")
    sit(ch)
    A.expr(ch, F, "verbaasd", look=(-0.3, 0.0))
    talk(ch, 0.55)
    return "Achter het stuur, zijn mond gaat heel langzaam open (dag 2)"


def vuilnisman(ch):
    A.pose(ch, F, "stuur")
    A.crouch(ch, F, depth=0.3, lean=-4)
    A.foot(ch, F, "L", loc=(0, 0.16, 0))
    A.foot(ch, F, "R", loc=(0, 0.2, 0.02), rot=(-15, 0, 0))
    A.expr(ch, F, "bang", amount=0.7)
    seat("vuilnisman", ch, 0.38)
    return "Achter het stuur van de vuilniswagen, remt (dag 4)"


def klasgenoot_a(ch):
    A.pose(ch, F, "juichen")
    A.expr(ch, F, "lach")
    return "Gymles (dag 1)"


def klasgenoot_b(ch):
    A.pose(ch, F, "handen_zij")
    A.expr(ch, F, "zelfverzekerd")
    return "Gymles (dag 1)"


def klasgenoot_c(ch):
    A.pose(ch, F, "ontspannen")
    A.expr(ch, F, "blij")
    return "Gymles (dag 1)"


# (sleutel, glb, weglaten, actie, draaiing voor de overzichtsfoto)
CAST = [
    ("hoofdpersonage", None, (), hero, 70),
    ("broertje_dino", None, (), broertje_dino, -25),
    ("mama", None, (), mama, -45),
    ("papa", None, (), papa, 0),
    ("broertje", None, (), None, 0),
    ("opa", None, ("wandelstok",), opa, 0),
    ("oma", None, (), oma, 0),
    ("beste_vriend", None, ("telefoon",), beste_vriend, -40),
    ("pestkop", None, (), pestkop, -10),
    ("wetenschapper", None, ("klembord",), wetenschapper, -45),
    ("gymleraar", None, (), gymleraar, 10),
    ("bezorger", None, (), bezorger, 0),
    ("vuilnisman", None, (), vuilnisman, 0),
    ("klasgenoot_a", None, (), klasgenoot_a, 0),
    ("klasgenoot_b", None, (), klasgenoot_b, 0),
    ("klasgenoot_c", None, (), klasgenoot_c, 0),
]


def broertje_plain(ch):
    A.pose(ch, F, "zwaaien_a")
    A.expr(ch, F, "lach")
    talk(ch, 0.3)
    return "'Don't be late for my candles.' (dag 1)"


def cam(name, loc, target, lens=50):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    G.RG.aim(ob, loc, target, lens)
    return ob


def render(path, rx, ry):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("render:", path, flush=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    opts = {"--out": os.path.join(REPO, "output", "cast_10x"), "--only": "", "--samples": "64",
            "--pct": "100"}
    flags = set()
    i = 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            flags.add(argv[i])
            i += 1
    out = opts["--out"]
    os.makedirs(out, exist_ok=True)
    only = [k for k in opts["--only"].split(",") if k]

    T.new_scene("cast_10x", T.MOODS["binnen"])
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, 48
    sc.render.use_compositing = False   # geen bloom uit de toon-sets; glans heeft dat niet nodig
    studio = G.studio(int(opts["--samples"]), int(opts["--pct"]))
    figs = bpy.data.collections.new("figuren")
    sc.collection.children.link(figs)

    todo = [c for c in CAST if not only or c[0] in only]
    gap = 1.0
    x0 = -(len(todo) - 1) * gap / 2
    built = []
    for k, (key, glb, drop, act, rz) in enumerate(todo):
        ch = R.load(key, glb=glb, loc=(x0 + k * gap, 0, 0), rot_z=rz, drop=drop)
        coll = ch.rig.users_collection[0]
        sc.collection.children.unlink(coll)
        figs.children.link(coll)
        G.character(ch)
        bpy.context.view_layer.update()
        what = (act or broertje_plain)(ch)
        built.append((key, ch, what))
        print("klaar:", key, "-", what, flush=True)

    crow = None
    if not only or "kraai" in only:
        crow = G.crow("kraai", (0, 0.4, 2.3), rot_z=-35, wing=38)
        cc = crow.users_collection[0]
        sc.collection.children.unlink(cc)
        figs.children.link(cc)
    STILL = 24   # houdingen staan stil; op frame 24 is de rook goed op gang
    sc.frame_set(STILL)

    # het studiolicht valt alleen op de figuren; de wand houdt zijn eigen gloed
    for ob in studio.objects:
        if ob.type == "LIGHT" and ob.name != "kruin":
            ob.light_linking.receiver_collection = figs

    c = cam("camera", (0, -6, 1.4), (0, 0, 0.9))
    sc.camera = c
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "cast_10x_faster_poses.blend"))
    if "--no-render" in flags:
        return

    lights = [(ob, ob.location.copy(), ob.data.energy, ob.data.size) for ob in studio.objects
              if ob.type == "LIGHT"]

    def light_at(x, wide=1.0):
        for ob, l0, e0, s0 in lights:
            ob.location = Vector((l0.x * wide + x, l0.y, l0.z))
            ob.data.energy = e0 * (wide if wide > 1 else 1)
            ob.data.size = s0 * wide

    # per figuur een still
    for n, (key, ch, what) in enumerate(built, start=1):
        x = ch.rig.location.x
        light_at(x)
        hc = ch.rig.matrix_world @ ch.pb["head"].head
        h = max(hc.z + 0.35, 1.0)
        G.RG.aim(c, (x + 0.6, -max(3.2, 2.4 * h), h * 0.62), (x, 0, h * 0.5), lens=50)
        # de buren niet in beeld
        for k2, ch2, _ in built:
            ch2.body.hide_render = ch2 is not ch
            for o in ch2.rig.users_collection[0].objects:
                if o not in (ch2.rig,):
                    o.hide_render = ch2 is not ch
        if crow:
            for o in crow.users_collection[0].objects:
                o.hide_render = True
        render(os.path.join(out, f"{n:02d}_{key}.png"), 1200, 1200)
    for k2, ch2, _ in built:
        for o in ch2.rig.users_collection[0].objects:
            o.hide_render = o is ch2.rig

    if crow:
        for o in crow.users_collection[0].objects:
            o.hide_render = o is crow
        cx = crow.location.x
        light_at(cx)
        G.RG.aim(c, (cx + 0.5, crow.location.y - 1.4, crow.location.z + 0.25), crow.location, lens=50)
        hide = [o for k2, ch2, _ in built for o in ch2.rig.users_collection[0].objects]
        for o in hide:
            o.hide_render = True
        render(os.path.join(out, f"{len(built) + 1:02d}_kraai.png"), 1200, 1200)
        for o in hide:
            o.hide_render = o.type == "ARMATURE"

    if not only:
        W = len(built) * gap
        light_at(0, wide=2.6)
        G.RG.aim(c, (0, -W * 1.5, 1.6), (0, 0, 0.95), lens=50)
        render(os.path.join(out, "00_cast_10x_overzicht.png"), 3600, 1200)


if __name__ == "__main__":
    main()
