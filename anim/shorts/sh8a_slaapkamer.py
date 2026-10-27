"""SH8a · What if you were 1,000,000x heavier? · slaapkamer: hij gaat rechtop zitten en het bed knakt doormidden.
10x: elke stap kraakt de vloer. 100x: de vloer kreunt... en hij zakt erdoorheen.

    blender -b -P anim/shorts/sh8a_slaapkamer.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from short import *  # noqa: E402,F401
import bmesh  # noqa: E402

FALL = timeline("sh8")[3][0] + 3.6              # '... and you drop straight through'
S = Short("sh8", "a", "slaapkamer", "ochtend", lines=(1, 2, 3), t1=FALL + 0.25)
l1, l2, l3 = S.L[1], S.L[2], S.L[3]
T0, END = S.t0, S.t1
for n in ("Telefoon", "Telefoon_scherm", "Laptop", "Vloerkleed"):
    o = S.obj(n)
    if o:
        o.hide_render = True

# ---------------------------------------------------------------- het bed in twee helften
MID_Y = 0.86


def unparent(o):
    M = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = M


def split(o, y):
    """Snij een mesh op wereld-y en geef (voet-helft, hoofd-helft)."""
    bpy.context.view_layer.update()
    loc = o.matrix_world.inverted() @ V(0, y, 0)
    halves = []
    for keep_head in (False, True):
        c = o.copy()
        c.data = o.data.copy()
        c.name = o.name + ("_hoofd" if keep_head else "_voet")
        for coll in o.users_collection:
            coll.objects.link(c)
        bm = bmesh.new()
        bm.from_mesh(c.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, loc.y, 0), plane_no=(0, 1, 0),
                               clear_inner=keep_head, clear_outer=not keep_head)
        bm.to_mesh(c.data)
        bm.free()
        halves.append(c)
    o.hide_render = True
    o.hide_viewport = True
    return halves


bed_root = S.obj("Bed (geheel)")
kids = list(bed_root.children)
for o in kids:
    unparent(o)
foot, head = [], []
for o in kids:
    if o.type != "MESH":
        continue
    bb = [o.matrix_world @ V(v) for v in o.bound_box]
    y0, y1 = min(p.y for p in bb), max(p.y for p in bb)
    if y0 < MID_Y < y1:
        a, b = split(o, MID_Y)
        foot.append(a)
        head.append(b)
    else:
        (head if y0 >= MID_Y else foot).append(o)
BX = -1.52
h_head = hinge(head[0], (BX, 1.92, 0.0), head[1:])
h_foot = hinge(foot[0], (BX, -0.2, 0.0), foot[1:])
SNAP = l1[1] - 1.0                               # '... snaps in half'
for h, s_ in ((h_head, 1), (h_foot, -1)):
    key(h, 0, rot=(0, 0, 0))
    key(h, SNAP - 0.02, rot=(0, 0, 0))
    key(h, SNAP + 0.12, rot=(17 * s_, 0, 0))
    key(h, SNAP + 0.3, rot=(14 * s_, 0, 0))
    key(h, SNAP + 0.45, rot=(16 * s_, 0, 0))
S.debris(V(BX, MID_Y, 0.4), SNAP, n=16, size=(0.03, 0.08), color=(0.55, 0.36, 0.2), speed=(1.0, 2.5), up=0.8, floor=0.0,
         life=1.5, name="Splinter")
S.puff(V(BX, MID_Y, 0.15), SNAP + 0.05, n=8, r=(0.15, 0.3), grow=2.0, dur=1.0, color=(0.8, 0.75, 0.7), rise=0.2, spread=0.6)

# ---------------------------------------------------------------- hij
BED = V(-1.52, 1.25, 0.6)
held = S.actor("hoofdpersonage", BED + V(0, 0, -0.12), 0)
SIT, _ = sit(held, seat_top=0.0, lean=-8, spread=0.12)
S.beat(held, 0.0, **SIT, pose="ontspannen", face="neutraal", look=(0, 0), mouth=0.0, body={"chest": (-30, 0, 0), "head": (-12, 0, 0)})
S.beat(held, l1[0] + 1.2, **SIT, pose="ontspannen", face="neutraal", look=(0, 0), mouth=0.0)
S.place(held, SNAP - 0.02, BED + V(0, 0, -0.12), 0)
S.place(held, SNAP + 0.14, BED + V(0, -0.1, -0.36), 0)
S.beat(held, SNAP + 0.1, **SIT, pose="schrik", amount=1.0, face="geschrokken", face_amt=1.0, look=(0, 0), mouth=0.6)
S.beat(held, l1[1] + 0.2, **SIT, pose="schrik", amount=0.7, face="verbaasd", face_amt=1.0, look=(0, -0.6), mouth=0.3)
# 10x: opstaan en lopen, elke stap een barst in de planken
P1 = V(-0.75, 0.45, 0)
P2 = V(0.55, -0.25, 0)
S.teleport(held, l2[0] + 0.1, P1, 120)
S.beat(held, l2[0] + 0.1, "staan", face="inspanning", face_amt=0.8, look=(0, -0.4), mouth=0.1, crouch=(0.05, 4))
WALK0, WALK1 = l2[0] + 0.8, l2[1] - 0.4
S.walk(held, WALK0, WALK1, [P1, P2], stride=0.3, arms=0.3, end_rot=60)
S.beat(held, WALK0, "staan", face="inspanning", face_amt=1.0, look=(0, -0.5), feet="keep", mouth=0.1, body={"chest": (8, 0, 0)})
crack_m = S.mat("barst_vloer", (0.12, 0.08, 0.05))
nst = 6
for k in range(1, nst + 1):
    u = k / (nst + 1)
    p = P1.lerp(P2, smooth(0, 1, u) * 0.5 + u * 0.5)
    t = WALK0 + (WALK1 - WALK0) * u
    side = (P2 - P1).normalized().cross(V(0, 0, 1)) * (0.09 if k % 2 else -0.09)
    for j in range(3):
        c = T.box(f"Plankbarst_{k}_{j}", tuple(p + side + V(0, 0, 0.001)), (0.25 + 0.06 * j, 0.01, 0.003), crack_m, bevel=0, ol=0)
        c.rotation_euler.z = j * 1.1 + k * 0.7
        show(c, t)
    S.sfx("sfx_vloer_kraak", t - 0.03, 0.3)
# 100x: de vloer kreunt, barsten groeien, en weg is hij
S.beat(held, l3[0] + 0.2, "schrap", face="bang", face_amt=1.0, look=(0, -0.7), mouth=0.3, crouch=(0.1, 8))
GROAN = l3[0] + 1.2
for j in range(12):
    a = j / 12 * 6.283 + 0.3
    ln = 0.6 + 0.5 * ((j * 7) % 5) / 5
    c = T.box(f"Vloerscheur_{j}", tuple(P2 + V(0, 0, 0.002)), (ln, 0.018, 0.004), crack_m, bevel=0, ol=0)
    c.rotation_euler.z = a
    c.location = P2 + V(math.cos(a) * ln / 2, math.sin(a) * ln / 2, 0.002)
    key(c, 0, scale=(0.001, 1, 1))
    key(c, GROAN + j * 0.12, scale=(0.001, 1, 1))
    key(c, GROAN + j * 0.12 + 0.5, scale=(1, 1, 1))
hole = T.cyl("Vloergat", tuple(P2 + V(0, 0, 0.003)), 0.55, 0.004, S.mat("gat", (0.02, 0.015, 0.01)), seg=20, ol=0)
show(hole, FALL - 0.02)
S.beat(held, FALL - 0.5, "armen_omhoog", amount=0.6, face="geschrokken", face_amt=1.0, look=(0, -0.8), mouth=0.6)
key(held.rig, FALL - 0.02, loc=tuple(P2))
key(held.rig, FALL + 0.25, loc=tuple(P2 + V(0, 0, -2.2)), interp="LINEAR")
S.debris(P2 + V(0, 0, 0.05), FALL, n=24, size=(0.04, 0.1), color=(0.62, 0.42, 0.25), speed=(1.5, 3.5), up=1.2, floor=-3.0,
         life=1.2, name="Planken")
S.puff(P2 + V(0, 0, 0.2), FALL, n=10, r=(0.2, 0.4), grow=2.2, dur=1.0, color=(0.8, 0.75, 0.7), rise=0.6, spread=0.8)

# ---------------------------------------------------------------- muziek, geluid, tellers
S.music_all("drums_build", vol=0.2)
S.music("subbas", 0.0, S.total, vol=0.22, fade_in=0.5)
S.sfx("sfx_tafel_breekt", SNAP - 0.05, 0.6)
S.sfx("sfx_vloer_kraak", GROAN, 0.5)
S.sfx("sfx_grond_kruimelt", GROAN + 0.8, 0.35)
S.sfx("sfx_muur_valt", FALL - 0.05, 0.6)
S.counter("10x", l2[0] + 0.05, l3[0], sub="450 kg")
S.counter("100x", l3[0] + 0.05, None, sub="4,500 kg")

# ---------------------------------------------------------------- camera
S.cam(0.0, ((0.3, -1.0, 1.4), (-1.52, 1.0, 0.75), 24), ((0.2, -0.85, 1.35), (-1.52, 1.0, 0.7), 26))
S.cam(SNAP - 0.15, ((0.45, 0.3, 0.6), (-1.52, 0.86, 0.4), 22), ((0.42, 0.28, 0.6), (-1.52, 0.86, 0.35), 22),
      shake=lambda t: 1.5 * max(0, 1 - (t - SNAP) / 0.5))
S.cam(l2[0], ((1.5, -1.4, 1.5), (-0.2, 0.2, 0.8), 24), ((1.45, -1.3, 1.45), (0.0, 0.0, 0.8), 26))
S.cam(WALK0 + 1.2, ((P2.x + 0.9, P2.y - 0.4, 0.25), (P1.x, P1.y, 0.15), 22), ((P2.x + 0.9, P2.y - 0.4, 0.25), (P2.x - 0.2, P2.y, 0.15), 22))
S.cam(l3[0], S.shot(held, l3[0] + 0.3, "mcu", az=10, lens=32), S.shot(held, GROAN, "mcu", az=6, lens=36))
S.cam(GROAN, ((P2.x + 1.6, P2.y - 1.6, 2.1), (P2.x, P2.y, 0.5), 22), ((P2.x + 1.5, P2.y - 1.5, 2.0), (P2.x, P2.y, 0.4), 22),
      shake=lambda t: 0.4 + 1.6 * smooth(GROAN, FALL, t))

S.done()
