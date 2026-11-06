"""
DRIFTMARK HQ — het neon-kantoor, gebouwd in Blender (niels 2026-11-06: "gebruik blender").
Bouwt het statische kantoor exact op de maten van hq/src/world/rooms.ts, bakt licht + schaduw
(Cycles) in één lightmap en exporteert hq/public/models/office.glb.txt.

Lagen in de export (de webapp herkent ze aan de naam):
  baked            alle vaste geometrie, materiaal = gebakken lightmap (UV 'lm')
  neon_<kamer>     lichtgevende randen per afdeling (pulseren bij 'wacht op jou')
  neon_hub         neon van receptie/ingang/rand
  glass            glaswanden (wordt in de browser doorzichtig gemaakt)
  scr_<n>          schermen; de browser zet er live dashboards op
  seat_<kamer>_<n> lege punten: waar een medewerker zit

Draaien:  blender -b -P hq/blender/office_build.py -- [--preview out.png] [--bake 4096] [--samples 64]
Coördinaten in dit script zijn die van de webapp (y omhoog, +z naar de camera); P() zet om naar Blender.
"""
import bpy, bmesh, math, sys, os, random
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d
PREVIEW = arg('--preview')
BAKE = int(arg('--bake', '0'))
SAMPLES = int(arg('--samples', '64'))
OUT = arg('--out', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'models', 'office.glb'))
random.seed(7)

# ---------- maten uit rooms.ts ----------
SLOTS = 10; SPAN = math.tau / SLOTS
R_HUB, R_IN, R_OUT, R_BASE = 5.9, 6.9, 15.2, 17.2
GAPA = 0.035
RM = (R_IN + R_OUT) / 2
ROOMS = [  # id, slot, kleur, props
    ('onderzoek', 6, '#20D9FF', 'research'), ('creatief', 7, '#A855F7', 'creative'), ('ceo', 5, '#FACC15', 'ceo'),
    ('publicatie', 4, '#398CFF', 'publishing'), ('script', 8, '#FF6A3D', 'script'), ('thumbnail', 2, '#FF7A24', 'thumbnail'),
    ('stem', 9, '#21D6C4', 'voice'), ('productie', 1, '#FF4DB8', 'production'), ('crisis', 3, '#FF3B4E', 'crisis'),
]
# bureaus per afdeling (u = langs de ring, v = naar buiten), gelijk aan NeonOffice.tsx
DESKS = [(-1.25, -2.5), (1.25, -2.5), (-1.25, -0.2), (1.25, -0.2)]

def hexc(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (a,)

def P(x, y, z):  # webapp -> Blender
    return Vector((x, -z, y))
def polar(r, a, y=0.0):
    return (math.sin(a) * r, y, math.cos(a) * r)

# ---------- scène leegmaken ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------- materialen ----------
MATS = {}
def mat(name, col, rough=0.5, metal=0.0, emit=None, strength=0.0, alpha=1.0, transmission=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(col)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = hexc(emit); b.inputs['Emission Strength'].default_value = strength
    if transmission:
        b.inputs['Transmission Weight'].default_value = transmission
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND'
    MATS[name] = m; return m

# ---------- geometrie-verzamelaar (alles per laag in één mesh, veel sneller dan losse objecten) ----------
class Layer:
    def __init__(self, name):
        self.name = name; self.bm = bmesh.new(); self.mats = []
    def mi(self, m):
        if m not in self.mats: self.mats.append(m)
        return self.mats.index(m)
    def poly(self, pts, m):
        vs = [self.bm.verts.new(P(*p)) for p in pts]
        f = self.bm.faces.new(vs); f.material_index = self.mi(m); f.smooth = False
        return f
    def finish(self, smooth=False):
        if self.name == 'baked': bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=0.0005)
        me = bpy.data.meshes.new(self.name); self.bm.normal_update(); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats: me.materials.append(m)
        ob = bpy.data.objects.new(self.name, me); scn.collection.objects.link(ob)
        return ob

LAYERS = {}
def L(name):
    if name not in LAYERS: LAYERS[name] = Layer(name)
    return LAYERS[name]

def tf(c, ry, p):  # punt p (lokaal) draaien om y en verschuiven naar c
    x, y, z = p; cs, sn = math.cos(ry), math.sin(ry)
    return (c[0] + x * cs + z * sn, c[1] + y, c[2] - x * sn + z * cs)

def box(layer, c, s, m, ry=0.0, rx=0.0):
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    corners = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    if rx:
        cr, sr = math.cos(rx), math.sin(rx); corners = [(x, y * cr - z * sr, y * sr + z * cr) for x, y, z in corners]
    v = [tf(c, ry, p) for p in corners]
    lay = L(layer)
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3)):
        lay.poly([v[i] for i in f], m)

def cyl(layer, c, r, h, m, seg=24, r2=None, cap=True, a0=0.0, a1=math.tau, ry=0.0):
    r2 = r if r2 is None else r2; lay = L(layer); full = abs(a1 - a0 - math.tau) < 1e-6
    n = seg if full else seg + 1
    bot = [tf(c, ry, (math.sin(a0 + (a1 - a0) * k / seg) * r2, 0, math.cos(a0 + (a1 - a0) * k / seg) * r2)) for k in range(n)]
    top = [tf(c, ry, (math.sin(a0 + (a1 - a0) * k / seg) * r, h, math.cos(a0 + (a1 - a0) * k / seg) * r)) for k in range(n)]
    for k in range(seg):
        k2 = (k + 1) % n
        lay.poly([bot[k], bot[k2], top[k2], top[k]], m)
    if cap and full:
        lay.poly(list(reversed(bot)), m); lay.poly(top, m)

def sector(layer, r0, r1, a0, a1, y0, y1, m, seg=24, sides=True):
    """ringsegment (vloer, wand, bank) van r0..r1, hoek a0..a1, hoogte y0..y1"""
    lay = L(layer); I0, I1, O0, O1 = [], [], [], []
    for k in range(seg + 1):
        a = a0 + (a1 - a0) * k / seg
        I0.append(polar(r0, a, y0)); I1.append(polar(r0, a, y1)); O0.append(polar(r1, a, y0)); O1.append(polar(r1, a, y1))
    for k in range(seg):
        lay.poly([I1[k], O1[k], O1[k + 1], I1[k + 1]], m)  # boven
        if sides:
            lay.poly([O0[k], O0[k + 1], O1[k + 1], O1[k]], m)
            lay.poly([I0[k + 1], I0[k], I1[k], I1[k + 1]], m)
    if sides:
        lay.poly([I0[0], O0[0], O1[0], I1[0]], m); lay.poly([O0[-1], I0[-1], I1[-1], O1[-1]], m)

def tube(layer, pts, rad, m, ring=6):
    lay = L(layer); pts = [Vector(p) for p in pts]; rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
        a = d.cross(up).normalized(); b = d.cross(a).normalized()
        rings.append([tuple(p + (a * math.cos(t) + b * math.sin(t)) * rad) for t in (math.tau * k / ring for k in range(ring))])
    for i in range(len(rings) - 1):
        for k in range(ring):
            k2 = (k + 1) % ring
            lay.poly([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]], m)

def arc(r, a0, a1, y, n=20):
    return [polar(r, a0 + (a1 - a0) * k / n, y) for k in range(n + 1)]

SCREENS = []
def screen(c, w, h, ry=0.0, rx=0.0, kind='d'):
    """los schermvlak (naar +z na draaien), eigen object zodat de browser er live beeld op zet"""
    n = len(SCREENS); lay = L(f'scr_{n:03d}_{kind}')
    hw, hh = w / 2, h / 2; pts = [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)]
    if rx:
        cr, sr = math.cos(rx), math.sin(rx); pts = [(x, y * cr - z * sr, y * sr + z * cr) for x, y, z in pts]
    f = lay.poly([tf(c, ry, p) for p in pts], M['screen'])
    uvl = lay.bm.loops.layers.uv.verify()
    for lp, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uv
    SCREENS.append(kind)

SEATS = []
def seat(room, p, ry=0.0):
    SEATS.append((room, p, ry))

M = {
    'floor': mat('floor', '#1a2246', 0.28, 0.35), 'corr': mat('corr', '#151b3a', 0.25, 0.4), 'carpet': mat('carpet', '#262f5e', 0.95),
    'wall': mat('wall', '#161f42', 0.45, 0.3), 'panel': mat('panel', '#1f2a58', 0.4, 0.3), 'trim': mat('trim', '#0f1530', 0.4, 0.5),
    'desk': mat('desk', '#eef1f7', 0.35), 'leg': mat('leg', '#c3cad8', 0.3, 0.6), 'mon': mat('mon', '#0c1020', 0.3, 0.4),
    'chair': mat('chair', '#262c48', 0.6), 'chairb': mat('chairb', '#4a5068', 0.35, 0.6), 'kbd': mat('kbd', '#d9dfeb', 0.4),
    'pot': mat('pot', '#eceff6', 0.3), 'soil': mat('soil', '#3b2a1e', 0.9), 'leaf': mat('leaf', '#2f9e4f', 0.55), 'leaf2': mat('leaf2', '#4cc46a', 0.55),
    'stem': mat('stem', '#5b3d22', 0.8), 'sofa': mat('sofa', '#323b78', 0.8), 'sofa2': mat('sofa2', '#5a3d8a', 0.8), 'wood': mat('wood', '#8a5a34', 0.6),
    'podium': mat('podium', '#141c3e', 0.25, 0.55), 'hubdesk': mat('hubdesk', '#1b2756', 0.3, 0.5), 'base': mat('base', '#0d1230', 0.35, 0.5),
    'step': mat('step', '#1a2350', 0.3, 0.4), 'white': mat('white', '#f4f6fb', 0.4), 'metal': mat('metal', '#8a93a8', 0.25, 0.9),
    'glass': mat('glass', '#a9e4ff', 0.05, 0.0, transmission=1.0), 'screen': mat('screen', '#000000', 0.2, 0, emit='#5aa8ff', strength=2.2),
    'book': [mat(f'book{i}', c, 0.6) for i, c in enumerate(['#d9534f', '#f0ad4e', '#5bc0de', '#5cb85c', '#9b59b6', '#ecf0f1'])],
}
def neon(col, s=7.0):
    return mat('neon' + col, col, 0.3, 0, emit=col, strength=s)

# ---------- meubels ----------
def chair(layer, c, ry=0.0):
    layer = 'props'
    box(layer, (c[0], 0.47, c[2]), (0.52, 0.09, 0.5), M['chair'], ry)
    box(layer, tf(c, ry, (0, 0.85, 0.24)), (0.5, 0.62, 0.08), M['chair'], ry, rx=-0.12)
    cyl(layer, (c[0], 0.08, c[2]), 0.04, 0.38, M['chairb'], 8)
    for k in range(5):
        a = ry + k * math.tau / 5
        box(layer, (c[0] + math.sin(a) * 0.17, 0.05, c[2] + math.cos(a) * 0.17), (0.06, 0.05, 0.34), M['chairb'], a)

def desk(layer, c, n=2, room=None, seat_ry=0.0):
    layer = 'props'
    """bureau met n schermen naar +z; stoel aan de camerakant"""
    box(layer, (c[0], 0.75, c[2]), (1.9, 0.06, 0.8), M['desk'])
    for sx in (-0.86, 0.86):
        box(layer, (c[0] + sx, 0.37, c[2]), (0.06, 0.72, 0.72), M['leg'])
    box(layer, (c[0], 0.5, c[2] - 0.36), (1.7, 0.42, 0.03), M['leg'])
    xs = [-0.62, 0, 0.62] if n == 3 else [-0.34, 0.34]
    for x in xs:
        ry = -x * (0.35 if n == 3 else 0.3)
        mc = tf((c[0], 0, c[2]), 0, (x, 0, -0.2))
        box(layer, (mc[0], 0.86, mc[2] - 0.02), (0.07, 0.2, 0.07), M['mon'])
        box(layer, (mc[0], 0.79, mc[2] - 0.02), (0.24, 0.02, 0.16), M['mon'])
        box(layer, (mc[0], 1.1, mc[2] - 0.035), (0.62, 0.38, 0.03), M['mon'], ry)
        screen(tf((mc[0], 1.1, mc[2] - 0.035), ry, (0, 0, 0.017)), 0.57, 0.33, ry)
    box(layer, (c[0], 0.79, c[2] + 0.12), (0.55, 0.02, 0.17), M['kbd'])
    box(layer, (c[0] + 0.4, 0.79, c[2] + 0.14), (0.07, 0.02, 0.11), M['kbd'])
    # koffiebeker
    cyl(layer, (c[0] - 0.62, 0.78, c[2] + 0.12), 0.045, 0.11, M['white'], 10)
    ch = (c[0], 0, c[2] + 0.72)
    chair(layer, ch, 0.0)
    if room: seat(room, (c[0], 0, c[2] + 0.66), seat_ry)

def plant(layer, c, s=1.0, kind=0):
    layer = 'props'
    box_pot = kind == 2
    if box_pot: box(layer, (c[0], 0.3 * s, c[2]), (0.62 * s, 0.6 * s, 0.62 * s), M['pot'])
    else: cyl(layer, (c[0], 0, c[2]), 0.33 * s, 0.55 * s, M['pot'], 16, r2=0.25 * s)
    cyl(layer, (c[0], 0.5 * s if not box_pot else 0.56 * s, c[2]), 0.28 * s, 0.03, M['soil'], 12)
    if kind == 1:  # vijgenboompje: stam + bolletjes
        cyl(layer, (c[0], 0.5 * s, c[2]), 0.04 * s, 1.1 * s, M['stem'], 6)
        for k in range(26):
            a = random.random() * math.tau; h = 1.1 + random.random() * 0.9; rr = 0.15 + random.random() * 0.45
            p = (c[0] + math.sin(a) * rr * s, h * s, c[2] + math.cos(a) * rr * s)
            box(layer, p, (0.28 * s, 0.04 * s, 0.18 * s), M['leaf2' if k % 2 else 'leaf'], random.random() * math.tau, rx=random.uniform(-0.7, 0.7))
        return
    # palm / monstera: lange gebogen bladeren
    cnt = 11 if kind == 0 else 9
    top = 0.55 * s
    if kind == 0: cyl(layer, (c[0], 0.5 * s, c[2]), 0.05 * s, 0.9 * s, M['stem'], 6); top = 1.35 * s
    for k in range(cnt):
        a = k * math.tau / cnt + random.uniform(-0.2, 0.2); ln = (0.85 + random.random() * 0.45) * s
        tilt = random.uniform(0.25, 0.9)
        prev = None
        segs = 5
        for j in range(segs):
            t0, t1 = j / segs, (j + 1) / segs
            def pt(t):
                d = t * ln; y = top + math.sin((1 - tilt) * 1.2 + 0.2) * d * 0.9 - (t ** 2) * ln * tilt * 0.9
                return (c[0] + math.sin(a) * d, y, c[2] + math.cos(a) * d)
            p0, p1 = pt(t0), pt(t1)
            w = 0.2 * s * math.sin(math.pi * (t0 + t1) / 2 + 0.15) + 0.03
            perp = (math.cos(a) * w, 0, -math.sin(a) * w)
            L(layer).poly([(p0[0] - perp[0], p0[1], p0[2] - perp[2]), (p0[0] + perp[0], p0[1], p0[2] + perp[2]),
                           (p1[0] + perp[0], p1[1], p1[2] + perp[2]), (p1[0] - perp[0], p1[1], p1[2] - perp[2])], M['leaf' if k % 2 else 'leaf2'])

def sofa(layer, c, ry=0.0, m=None):
    layer = 'props'
    m = m or M['sofa']
    box(layer, tf(c, ry, (0, 0.24, 0)), (2.0, 0.42, 0.85), m, ry)
    box(layer, tf(c, ry, (0, 0.62, -0.34)), (2.0, 0.55, 0.2), m, ry)
    for sx in (-0.95, 0.95): box(layer, tf(c, ry, (sx, 0.42, 0)), (0.16, 0.42, 0.85), m, ry)
    for sx in (-0.5, 0.5): box(layer, tf(c, ry, (sx, 0.5, 0.02)), (0.88, 0.1, 0.7), M['sofa2'], ry)

def table_round(layer, c, r=1.1, chairs=6, col='#ffffff'):
    layer = 'props'
    cyl(layer, (c[0], 0.72, c[2]), r, 0.06, M['white'], 32)
    cyl(layer, (c[0], 0, c[2]), 0.12, 0.72, M['metal'], 10)
    tube('neon_hub', [(c[0] + math.sin(t) * (r + 0.01), 0.75, c[2] + math.cos(t) * (r + 0.01)) for t in (math.tau * k / 40 for k in range(41))], 0.02, neon(col, 5))
    for k in range(chairs):
        a = k * math.tau / chairs + 0.3
        chair(layer, (c[0] + math.sin(a) * (r + 0.45), 0, c[2] + math.cos(a) * (r + 0.45)), a)

def bookshelf(layer, c, ry):
    layer = 'props'
    box(layer, tf(c, ry, (0, 1.1, 0)), (1.6, 2.2, 0.45), M['wood'], ry)
    for j in range(4):
        y = 0.35 + j * 0.5; x = -0.7
        while x < 0.65:
            w = random.uniform(0.06, 0.12); h = random.uniform(0.28, 0.4)
            box(layer, tf(c, ry, (x + w / 2, y + h / 2, 0.08)), (w * 0.9, h, 0.32), random.choice(M['book']), ry)
            x += w

def rack(layer, c, ry, col):
    layer = 'props'
    box(layer, tf(c, ry, (0, 1.05, 0)), (0.7, 2.1, 0.8), M['mon'], ry)
    for j in range(8):
        box('neon_hub', tf(c, ry, (-0.15 + (j % 2) * 0.3, 0.3 + j * 0.22, 0.41)), (0.12, 0.03, 0.01), neon(col if j % 3 else '#21D6A0', 6), ry)

def easel(layer, c, ry):
    layer = 'props'
    for sx in (-0.35, 0.35): box(layer, tf(c, ry, (sx, 0.8, 0)), (0.05, 1.6, 0.05), M['wood'], ry, rx=0.08)
    box(layer, tf(c, ry, (0, 0.65, 0.08)), (0.9, 0.05, 0.12), M['wood'], ry)
    box(layer, tf(c, ry, (0, 1.15, 0.02)), (1.0, 0.75, 0.04), M['white'], ry, rx=0.08)
    screen(tf(c, ry, (0, 1.15, 0.05)), 0.9, 0.66, ry, rx=0.08, kind='t')

def beanbag(layer, c, col):
    layer = 'props'
    cyl(layer, (c[0], 0, c[2]), 0.42, 0.42, mat('bb' + col, col, 0.85), 14, r2=0.5)

# ---------- de afdelingen ----------
for rid, slot, col, props in ROOMS:
    a = slot * SPAN; a0, a1 = a - SPAN / 2 + GAPA, a + SPAN / 2 - GAPA
    front = math.cos(a) > 0.35
    H = 3.0; HG = 1.1 if front else 2.6
    def at(u, v, y=0.0):
        rad = RM + v; ang = a + u / rad; return polar(rad, ang, y)
    lay = 'baked'; nl = f'neon_{rid}'; N = neon(col, 7.0)
    tint = mat('floor_' + rid, '#1a2246', 0.28, 0.35)
    tint.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = tuple(x * 0.82 + y * 0.18 for x, y in zip(hexc('#1a2246')[:3], hexc(col)[:3])) + (1,)
    # vloer + verhoogde rand + tapijt
    sector(lay, R_IN, R_OUT, a0, a1, 0.0, 0.06, tint, 30)
    sector(lay, R_IN + 1.0, R_OUT - 1.0, a0 + 0.05, a1 - 0.05, 0.06, 0.075, M['carpet'], 24, sides=False)
    tallR = R_IN if front else R_OUT
    glassR = R_OUT if front else R_IN
    # hoge wand met panelen (lichte kant naar binnen)
    tw0 = tallR - (0.0 if front else 0.18); tw1 = tallR + (0.18 if front else 0.0)
    sector(lay, tw0, tw1, a0, a1, 0.06, H, M['wall'], 28)
    pr = tallR + 0.19 if front else tallR - 0.19
    for k in range(6):
        t0 = a0 + (a1 - a0) * (k + 0.08) / 6; t1 = a0 + (a1 - a0) * (k + 0.92) / 6
        sector(lay, min(pr, pr + 0.02), max(pr, pr + 0.02), t0, t1, 0.35, H - 0.35, M['panel'], 4)
    # neon op de wanden en vloer
    tube(nl, arc(tallR + (0.2 if front else -0.2), a0, a1, H, 30), 0.055, N)
    tube(nl, arc(glassR + (-0.05 if front else 0.05), a0, a1, HG, 30), 0.04, N)
    tube(nl, arc(R_OUT - 0.06, a0, a1, 0.08, 30), 0.05, N)
    tube(nl, arc(R_IN + 0.06, a0, a1, 0.08, 30), 0.045, N)
    for ang in (a0, a1):
        tube(nl, [polar(R_IN + 0.06, ang, 0.08), polar(R_OUT - 0.06, ang, 0.08)], 0.035, N)
        tube(nl, [polar(tallR + (0.2 if front else -0.2), ang, 0.06), polar(tallR + (0.2 if front else -0.2), ang, H)], 0.05, N)
        tube(nl, [polar(glassR + (-0.05 if front else 0.05), ang, 0.06), polar(glassR + (-0.05 if front else 0.05), ang, HG)], 0.045, N)
        # glazen zijwanden met dunne stijlen
        g = L('glass'); hgt = 2.4
        p0, p1 = polar(R_IN + 0.1, ang), polar(R_OUT - 0.1, ang)
        g.poly([(p0[0], 0.06, p0[2]), (p1[0], 0.06, p1[2]), (p1[0], hgt, p1[2]), (p0[0], hgt, p0[2])], M['glass'])
        box(lay, polar((R_IN + R_OUT) / 2, ang, hgt), (0.06, 0.06, R_OUT - R_IN - 0.2), M['trim'], ang)
    # glaswand naar de gang/camera
    g = L('glass')
    for k in range(24):
        t0 = a0 + (a1 - a0) * k / 24; t1 = a0 + (a1 - a0) * (k + 1) / 24
        q0, q1 = polar(glassR + (-0.05 if front else 0.05), t0), polar(glassR + (-0.05 if front else 0.05), t1)
        g.poly([(q0[0], 0.06, q0[2]), (q1[0], 0.06, q1[2]), (q1[0], HG, q1[2]), (q0[0], HG, q0[2])], M['glass'])
    # groot wandscherm met lijst
    wr = tallR + (0.22 if front else -0.22); wry = a if front else a + math.pi
    wc = polar(wr, a, 1.75)
    box(lay, wc, (3.2, 1.55, 0.05), M['mon'], wry)
    tube(nl, [tf(wc, wry, p) for p in [(-1.62, -0.8, 0.03), (1.62, -0.8, 0.03), (1.62, 0.8, 0.03), (-1.62, 0.8, 0.03), (-1.62, -0.8, 0.03)]], 0.025, N)
    screen(tf(wc, wry, (0, 0, 0.03)), 3.0, 1.38, wry, kind='w')
    # plafondbalk (geeft diepte zoals op de foto)
    # bureaus
    nd = 2 if props in ('crisis',) else 4
    pts = [(-1.6, -2.4), (1.6, -2.4)] if props == 'crisis' else DESKS
    for i, (u, v) in enumerate(pts[:nd]):
        desk(lay, at(u, v), 3 if i == 0 else 2, rid)
    # planten
    plant(lay, at(-2.55, 3.4), 1.05, 0); plant(lay, at(2.55, 3.4), 0.9, 1)
    plant(lay, at(-2.6, -3.5), 0.8, 2); plant(lay, at(2.6, -3.5), 0.85, 0)
    # eigen inrichting
    face = a + math.pi  # naar het midden
    if props == 'research':
        sofa(lay, at(-1.3, 2.3), face + math.pi); box(lay, at(-1.3, 1.6, 0.22), (0.9, 0.44, 0.5), M['white'], a)
        cyl(lay, at(1.4, 2.4), 0.3, 0.9, M['mon'], 16)  # sokkel voor de draaiende wereldbol
    elif props == 'creative':
        for j, cc in enumerate(['#FF7A24', '#A855F7', '#20D9FF']): beanbag(lay, at(-1.6 + j * 1.0, 2.0), cc)
        easel(lay, at(1.5, 2.6), face + math.pi)
        for j in range(3): screen(at(-1.6 + j * 1.1, 3.95, 1.6), 0.8, 0.55, a + math.pi, kind='t')
    elif props == 'script':
        bookshelf(lay, at(-1.3, 3.55), a + math.pi); bookshelf(lay, at(1.3, 3.55), a + math.pi)
        sofa(lay, at(0, 2.0), a + math.pi, M['sofa2'])
    elif props == 'voice':
        bc = at(0.0, 2.3); s = (2.4, 2.4, 2.0)
        g = L('glass')
        for (dx, dz, w, ry2) in ((0, 1.0, 2.4, 0), (0, -1.0, 2.4, 0), (1.2, 0, 2.0, math.pi / 2), (-1.2, 0, 2.0, math.pi / 2)):
            cc = tf(bc, a, (dx, 0, dz))
            box('glass', (cc[0], 1.25, cc[2]), (w, 2.4, 0.03), M['glass'], a + ry2)
        box(lay, (bc[0], 2.5, bc[2]), (2.46, 0.08, 2.06), mat('booth', '#2a1650', 0.5), a)
        for (dx, dz) in ((-1.2, -1.0), (1.2, -1.0), (-1.2, 1.0), (1.2, 1.0)):
            cc = tf(bc, a, (dx, 0, dz)); tube(nl, [(cc[0], 0.06, cc[2]), (cc[0], 2.5, cc[2])], 0.04, neon('#A855F7', 7))
        tube(nl, [tf(bc, a, p) for p in [(-1.22, 2.52, -1.02), (1.22, 2.52, -1.02), (1.22, 2.52, 1.02), (-1.22, 2.52, 1.02), (-1.22, 2.52, -1.02)]], 0.045, neon('#A855F7', 7))
        cyl(lay, (bc[0], 0.06, bc[2]), 0.18, 0.03, M['metal'], 12); cyl(lay, (bc[0], 0.06, bc[2]), 0.02, 1.45, M['metal'], 6)
        cyl(lay, (bc[0], 1.45, bc[2]), 0.07, 0.22, M['metal'], 12)
        box(lay, tf(bc, a, (0, 1.4, -0.95)), (2.2, 1.6, 0.06), mat('foam', '#3a2370', 0.95), a)
    elif props == 'production':
        rack(lay, at(-2.0, 3.55), a + math.pi, col); rack(lay, at(-1.15, 3.55), a + math.pi, col)
        sofa(lay, at(1.3, 2.3), a + math.pi, M['sofa'])
        box(lay, at(1.3, 1.55, 0.22), (1.0, 0.44, 0.5), M['white'], a)
    elif props == 'thumbnail':
        easel(lay, at(-1.3, 2.4), face + math.pi); easel(lay, at(1.3, 2.4), face + math.pi)
        box(lay, at(0, 1.6, 0.4), (1.4, 0.8, 0.7), M['desk'], a)
    elif props == 'publishing':
        cyl(lay, at(1.2, 2.6), 0.5, 0.3, M['mon'], 20)  # lanceerplatform (raket draait in de browser)
        sofa(lay, at(-1.3, 2.4), a + math.pi, M['sofa'])
    elif props == 'ceo':
        tc = at(0, 2.3); box(lay, (tc[0], 0.72, tc[2]), (2.6, 0.06, 1.1), M['white'], a)
        box(lay, (tc[0], 0.36, tc[2]), (0.25, 0.72, 0.6), M['metal'], a)
        tube(nl, [tf((tc[0], 0.76, tc[2]), a, p) for p in [(-1.3, 0, -0.55), (1.3, 0, -0.55), (1.3, 0, 0.55), (-1.3, 0, 0.55), (-1.3, 0, -0.55)]], 0.02, N)
        for j in (-0.85, 0, 0.85):
            for sd in (-1, 1): chair(lay, tf(tc, a, (j, 0, sd * 0.85)), a + (0 if sd > 0 else math.pi))
    elif props == 'crisis':
        table_round(lay, at(0, 1.4), 1.15, 6, col)
        box(lay, at(0, 3.95, 1.7), (3.4, 1.7, 0.05), M['mon'], a + math.pi)
        screen(at(0, 3.92, 1.7), 3.2, 1.5, a + math.pi, kind='m')
        cyl(nl, at(2.6, 3.3, 2.9), 0.16, 0.25, neon('#FF3B4E', 9), 12)

# ---------- receptie ----------
b = 'baked'; NH = 'neon_hub'
cyl(b, (0, 0, 0), R_HUB, 0.5, M['podium'], 72, r2=R_HUB + 0.3)
tube(NH, arc(R_HUB - 0.04, 0, math.tau, 0.52, 96), 0.07, neon('#FF7A24', 8))
tube(NH, arc(3.66, 0, math.tau, 0.515, 80), 0.04, neon('#20D9FF', 6))
tube(NH, arc(4.73, 0, math.tau, 0.515, 80), 0.03, neon('#398CFF', 6))
tube(NH, arc(R_HUB + 0.32, 0, math.tau, 0.02, 96), 0.05, neon('#20D9FF', 6))
# ronde balie aan de voorkant van de zuil
for (r0, r1, y0, y1, m) in ((2.55, 2.85, 0.5, 1.55, M['hubdesk']), (2.45, 2.95, 1.55, 1.62, M['white'])):
    sector(b, r0, r1, -1.25, 1.25, y0, y1, m, 40)
tube(NH, arc(2.96, -1.25, 1.25, 1.6, 40), 0.045, neon('#FF7A24', 8))
tube(NH, arc(2.87, -1.25, 1.25, 0.62, 40), 0.04, neon('#20D9FF', 6))
for i, x in enumerate((-1.1, 0, 1.1)):
    zc = 2.35 - abs(x) * 0.25; ry = -x * 0.35
    box(b, (x, 2.0, zc), (0.92, 0.54, 0.04), M['mon'], ry); screen(tf((x, 2.0, zc), ry, (0, 0, 0.022)), 0.86, 0.48, ry)
    box(b, (x, 1.7, zc), (0.06, 0.12, 0.06), M['mon'])
# voet en kap van de hologramzuil
cyl(b, (0, 0.5, 0), 2.45, 0.25, M['podium'], 64)
tube(NH, arc(2.46, 0, math.tau, 0.76, 80), 0.05, neon('#20D9FF', 7))
cyl(b, (0, 8.45, 0), 2.5, 0.22, M['podium'], 64)
tube(NH, arc(2.52, 0, math.tau, 8.45, 80), 0.09, neon('#FF7A24', 8))
tube(NH, arc(2.52, 0, math.tau, 8.67, 80), 0.05, neon('#FF7A24', 6))
# banken en planten op het podium
sofa(b, (-4.2, 0.5, 1.4), math.pi / 2 + 0.5); sofa(b, (4.2, 0.5, 1.4), -math.pi / 2 - 0.5)
for sx in (-1, 1):
    for (px, pz, s, k) in ((3.9, -3.2, 1.15, 0), (4.6, -1.0, 0.8, 1), (3.0, 3.9, 0.75, 2)):
        plant(b, (sx * px, 0.5, pz), s, k)
# tweede trap aan de linkerkant naar achteren (zoals op de foto)
for i in range(9):
    x, z = -3.4 - i * 0.05, -1.0 - i * 0.55; y = 0.5 + i * 0.32
    box(b, (x, y, z), (1.5, 0.08, 0.5), M['step'], 0.0)
    box(NH, (x, y + 0.045, z + 0.24), (1.5, 0.02, 0.03), neon('#20D9FF', 6))
for sx in (-0.78, 0.78):
    tube(NH, [(-3.4 + sx, 1.4, -1.0), (-3.8 + sx, 4.3, -5.4)], 0.03, neon('#20D9FF', 6))

# ---------- ingang: trap naar voren ----------
n = 7; depth = (R_OUT - R_HUB - 1) / n
for i in range(n):
    z = R_HUB + 0.3 + i * depth + depth / 2; y = 0.5 - (i + 1) * (0.6 / n); w = 3.6 + i * 0.22
    box(b, (0, (y - 0.0) / 2 - 0.05, z), (w, y + 0.1, depth), M['step'])
    box(NH, (0, y + 0.01, z + depth / 2 - 0.02), (w, 0.03, 0.04), neon('#20D9FF', 7))
for sd in (-1, 1):
    tube(NH, [(sd * 1.9, 1.3, R_HUB + 0.2), (sd * 2.7, 0.8, R_OUT)], 0.04, neon('#20D9FF', 6))
    for k in range(5):
        t = k / 4; box(b, (sd * (1.9 + 0.8 * t), (1.3 - 0.5 * t) / 2 + 0.1 * (1 - t), R_HUB + 0.2 + t * (R_OUT - R_HUB - 0.2)), (0.05, (1.3 - 0.5 * t) - 0.1, 0.05), M['metal'])
    plant(b, (sd * 3.1, 0, R_OUT - 0.6), 1.15, 0)
# zeshoekig platform vooraan
hexr = 1.6
pts = [(math.sin(math.tau * k / 6 + math.pi / 6) * hexr, 0.05, R_OUT + 0.9 + math.cos(math.tau * k / 6 + math.pi / 6) * hexr) for k in range(7)]
tube(NH, pts, 0.05, neon('#20D9FF', 7))

# ---------- grondplaat (achthoek met afgeschuinde rand) ----------
def octa(r, y, rot=math.pi / 8):
    return [polar(r, rot + k * math.tau / 8, y) for k in range(8)]
top, mid, bot = octa(R_BASE - 0.2, 0.0), octa(R_BASE + 0.2, -0.5), octa(R_BASE + 0.45, -1.3)
lay = L(b)
lay.poly(list(reversed(top)), M['corr'])  # bovenkant (gang)
for k in range(8):
    k2 = (k + 1) % 8
    lay.poly([top[k], mid[k], mid[k2], top[k2]], M['base'])
    lay.poly([mid[k], bot[k], bot[k2], mid[k2]], M['trim'])
tube(NH, octa(R_BASE - 0.25, 0.03) + [octa(R_BASE - 0.25, 0.03)[0]], 0.06, neon('#FF7A24', 9))
tube(NH, octa(R_BASE + 0.32, -0.9) + [octa(R_BASE + 0.32, -0.9)[0]], 0.08, neon('#FF7A24', 9))
tube(NH, arc(R_IN - 0.38, 0, math.tau, 0.02, 120), 0.035, neon('#398CFF', 6))
# lichtstrepen in de gang tussen de kamers
for slot in range(1, SLOTS):
    ang = slot * SPAN + SPAN / 2
    tube(NH, [polar(R_IN, ang, 0.02), polar(R_BASE - 0.5, ang, 0.02)], 0.025, neon('#398CFF', 5))

# ---------- objecten maken ----------
objs = {k: l.finish() for k, l in LAYERS.items()}
for room, p, ry in SEATS:
    pass
seat_count = {}
for room, p, ry in SEATS:
    i = seat_count.get(room, 0); seat_count[room] = i + 1
    e = bpy.data.objects.new(f'seat_{room}_{i}', None); e.location = P(*p); scn.collection.objects.link(e)
print('LAGEN', len(objs), 'schermen', len(SCREENS), 'stoelen', len(SEATS))

# ---------- licht voor de bake / preview ----------
world = bpy.data.worlds.new('w'); scn.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = hexc('#1a2350'); world.node_tree.nodes['Background'].inputs[1].default_value = 0.9
def light(kind, p, energy, col, size=1.0, rot=None):
    ld = bpy.data.lights.new('L', kind); ld.energy = energy; ld.color = hexc(col)[:3]
    if kind == 'AREA': ld.size = size
    if kind in ('POINT', 'SPOT'): ld.shadow_soft_size = size
    o = bpy.data.objects.new('L', ld); o.location = P(*p); scn.collection.objects.link(o)
    if rot: o.rotation_euler = rot
    return o
for rid, slot, col, props in ROOMS:
    a = slot * SPAN; c = polar(RM, a, 4.6)
    warm = tuple(x * 0.55 + y * 0.45 for x, y in zip(hexc('#ffd8b0')[:3], hexc(col)[:3]))
    ld = light('AREA', c, 1700, '#ffffff', 5.5); ld.data.color = warm
light('AREA', (0, 14, 2), 6000, '#ffe6cc', 20)
light('POINT', (0, 4, 0), 1600, '#20D9FF', 1.5)
light('POINT', (0, 2.4, 3.2), 400, '#FFB070', 0.8)
sun = light('SUN', (0, 30, 0), 1.2, '#fff1e0', 0.5); sun.rotation_euler = (math.radians(40), 0, math.radians(25)); sun.data.angle = 0.2
light('AREA', (-26, 10, 4), 6000, '#FF7A24', 12, rot=(0, math.radians(-70), 0))
light('AREA', (26, 10, 4), 6000, '#398CFF', 12, rot=(0, math.radians(70), 0))

scn.render.engine = 'CYCLES'; scn.cycles.device = 'CPU'
scn.cycles.samples = SAMPLES; scn.cycles.use_denoising = True
scn.view_settings.view_transform = 'AgX'; scn.view_settings.look = 'AgX - Punchy' if 'AgX - Punchy' in [l.name for l in []] else 'None'

if PREVIEW:
    camd = bpy.data.cameras.new('cam'); camd.lens_unit = 'FOV'; camd.angle_y = math.radians(float(arg('--fov', '34')))
    camd.sensor_fit = 'VERTICAL'
    cam = bpy.data.objects.new('cam', camd); scn.collection.objects.link(cam); scn.camera = cam
    el = float(arg('--elev', '0.62')); d = float(arg('--dist', '48')); t = Vector(P(0, 0.5, float(arg('--tz', '0.5'))))
    cam.location = t + Vector(P(0, math.sin(el) * d, math.cos(el) * d))
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scn.render.resolution_x, scn.render.resolution_y = int(arg('--w', '1280')), int(arg('--h', '720'))
    scn.render.filepath = PREVIEW; scn.render.film_transparent = False
    world.node_tree.nodes['Background'].inputs[0].default_value = hexc('#0a0f2a')
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', PREVIEW)

if BAKE:
    bk = objs['baked']
    bpy.context.view_layer.objects.active = bk; bk.select_set(True)
    me = bk.data
    uv = me.uv_layers.new(name='lm'); me.uv_layers.active = uv
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0015, area_weight=0.0, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.0015, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('lightmap', BAKE, BAKE, float_buffer=True)
    for m in me.materials:
        nt = m.node_tree; nd = nt.nodes.new('ShaderNodeTexImage'); nd.image = img; nd.select = True; nt.nodes.active = nd
    scn.cycles.samples = SAMPLES
    scn.render.bake.use_pass_direct = True; scn.render.bake.use_pass_indirect = True
    scn.render.bake.margin = 4
    bpy.ops.object.select_all(action='DESELECT'); bk.select_set(True); bpy.context.view_layer.objects.active = bk
    print('BAKEN...', flush=True)
    bpy.ops.object.bake(type='COMBINED', pass_filter={'DIRECT', 'INDIRECT', 'DIFFUSE', 'EMIT', 'TRANSMISSION'}, use_clear=True)
    # ruis eruit via de compositor
    img.filepath_raw = '/tmp/lm_raw.exr'; img.file_format = 'OPEN_EXR'; img.save()
    scn.use_nodes = True; nt = scn.node_tree; [nt.nodes.remove(x) for x in list(nt.nodes)]
    i_n = nt.nodes.new('CompositorNodeImage'); i_n.image = img
    dn = nt.nodes.new('CompositorNodeDenoise'); dn.prefilter = 'NONE'
    out = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(i_n.outputs[0], dn.inputs[0]); nt.links.new(dn.outputs[0], out.inputs[0])
    scn.render.resolution_x = scn.render.resolution_y = BAKE; scn.render.resolution_percentage = 100
    scn.view_settings.view_transform = 'AgX'; scn.view_settings.look = 'None'
    scn.render.image_settings.file_format = 'JPEG'; scn.render.image_settings.quality = 88
    jpg = os.path.join(os.path.dirname(OUT), 'office_lightmap.jpg')
    scn.render.filepath = jpg
    scn.camera = scn.camera or bpy.data.objects.new('c', bpy.data.cameras.new('c'))
    if scn.camera.name not in scn.collection.objects: scn.collection.objects.link(scn.camera)
    bpy.ops.render.render(write_still=True)
    print('LIGHTMAP', jpg)
    # vervang materialen door één eenvoudig materiaal met de lightmap
    baked = bpy.data.materials.new('baked'); baked.use_nodes = True; nt = baked.node_tree
    bs = nt.nodes['Principled BSDF']; tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(jpg)
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'lm'; nt.links.new(uvn.outputs[0], tx.inputs[0])
    nt.links.new(tx.outputs[0], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = 1.0
    bs.inputs['Base Color'].default_value = (0, 0, 0, 1); bs.inputs['Roughness'].default_value = 0.42
    me.materials.clear(); me.materials.append(baked)
    # alleen de lightmap-UV houden
    for u in [u for u in me.uv_layers if u.name != 'lm']: me.uv_layers.remove(u)
    # export
    for o in scn.objects:
        o.select_set(o.type in ('MESH', 'EMPTY'))
    bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_apply=True, export_lights=False,
                              export_cameras=False, export_image_format='JPEG', export_jpeg_quality=88, export_draco_mesh_compression_enable=False)
    print('EXPORT', OUT, os.path.getsize(OUT))
