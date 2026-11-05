"""N12d · Dag 6: de winkelstraat en de lege apotheek (script scène 12d-12g).
12d  WIDE push-in: etalages zonder glas, kledingrekken op straat, een papier waait over de weg.
     De jongens lopen naast hun fiets en kijken om zich heen.
12e  MEDIUM statisch (binnen): de jongen stapt de apotheek in, lege schappen, een omgevallen rek.
12e2 MEDIUM achter de toonbank: hij trekt een la open, nog een la, slaat de la dicht.
12f  CLOSE: JONGEN: "Empty. Everything's gone." Leunt met twee handen op de toonbank, hoofd zakt.
12g  CLOSE push-in, door de etalage zonder glas: de vriend kijkt naar buiten.
     BESTE VRIEND: "Uh... we've got company."  Harde cut.

    blender -b -P anim/v3/scenes/n12d_apotheek.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v3 import *  # noqa: E402,F401,F403
from lib import stad as ST3  # noqa: E402

S = Scene3("n12d", "stad", "winkelstraat", exposure=0.1)
sh = S.cuts([3.6, 3.2, 3.0, 3.0, 3.2])
END = sh[-1][1]
t_e, t_e2, t_f, t_g = [s[0] for s in sh[1:]]

for o in list(bpy.data.objects):
    if o.name.startswith(("Fiets_held", "Fiets_vriend")) and o.parent is None:
        for c in [o] + list(o.children_recursive):
            c.hide_render = c.hide_viewport = True

# apotheek: root op (10, 32), gevel kijkt naar -x, binnen loopt +x. lokale x -> wereld -y, lokale y -> wereld +x
AP = V(10.0, 32.0, 0.0)


def ap(lx, ly, z=0.0):
    return AP + V(ly, -lx, z)


COUNTER_STAFF_X = ap(0, 3.75).x                 # achterkant van de toonbank (personeelskant)
TOP_Z = 1.025

# ---------------------------------------------------------------- 12d: de jongens lopen naast hun fiets de straat in
held = S.actor("hoofdpersonage_kind", (-1.2, 24.0, 0), 0)
vr = S.actor("beste_vriend", (1.4, 24.8, 0), 0)
fh = ST3.fiets2("Fiets_jongen_lopend", (0, 0, 0), rot=-90, color=(0.15, 0.35, 0.75))
fv = ST3.fiets2("Fiets_vriend_lopend", (0, 0, 0), rot=-90, color=(0.85, 0.12, 0.10), sticker=True)
W_END = t_e
S.walk(held, 0.0, W_END, [V(-1.2, 24.0, 0), V(-1.2, 18.5, 0)], stride=0.36, turn=False)
S.walk(vr, 0.0, W_END, [V(1.4, 24.8, 0), V(1.4, 19.4, 0)], stride=0.38, turn=False)
for f in range(F(0.0), F(W_END) + 1):
    t = (f - 1) / FPS
    for ch, b, side in ((held, fh, 1.0), (vr, fv, -1.0)):
        M = S._root_matrix(ch, t)
        b.location = M @ V(-side * 0.5, -0.1, 0)                     # fiets naast hem (rechts van de jongen, links van de vriend), stuur binnen armbereik
        b.keyframe_insert("location", frame=f)
for t in frange(0.0, W_END + 0.01, 0.2):
    S.sc.frame_set(F(t))
    for ch, b, side, hand in ((held, fh, 1.0, "R"), (vr, fv, -1.0, "L")):
        st = S.obj(b.name + "_stuurdeel").matrix_world.translation
        to = S._root_matrix(ch, t).translation - st
        to.z = 0
        S.reach(ch, t, hand, st + to.normalized() * 0.24 + V(0, 0, 0.14))
for ch in (held, vr):
    S.reach(ch, 0.0, "L" if ch is held else "R", inf=0.0)
for b in (fh, fv):
    visible(b, 0.0, True)
    visible(b, t_e, False)
S.face(held, 0.0, "twijfel", 0.6, look=(-0.6, 0.1))
S.face(held, 1.6, "bang", 0.4, look=(0.6, 0.15))
S.face(vr, 0.0, "verbaasd", 0.6, look=(0.6, 0.2))
S.face(vr, 1.9, "twijfel", 0.6, look=(-0.5, 0.1))
A.bone_rot(held, F(0.4), "head", (0, -25, 0))
A.bone_rot(held, F(1.8), "head", (0, 30, 0))
A.bone_rot(held, F(W_END), "head", (0, 10, 0))

# een vel papier waait buitelend over de weg
pap = T.box("Papier_waait", (0, 0, 0), (0.21, 0.29, 0.003), S.mat("papier_wit", (0.97, 0.97, 0.95)), base=False, bevel=0, ol=0)
pap.rotation_mode = "XYZ"
for f in range(F(0.0), F(W_END) + 1):
    t = (f - 1) / FPS
    pap.location = (-6.0 + 3.6 * t, 16.5 + 0.6 * math.sin(t * 2.0), 0.15 + 0.6 * abs(math.sin(t * 2.6)))
    pap.rotation_euler = (t * 7.0, t * 4.0, t * 1.5)
    pap.keyframe_insert("location", frame=f)
    pap.keyframe_insert("rotation_euler", frame=f)

# ---------------------------------------------------------------- 12e: binnen in de apotheek. De jongen stapt binnen, de vriend blijft bij de etalage
DOOR_OUT = V(8.9, 34.5, 0)
IN = V(11.6, 34.2, 0)
S.teleport(held, t_e, DOOR_OUT, -90)
held.rig.location = tuple(DOOR_OUT)
held.rig.keyframe_insert("location", frame=F(t_e))
S.walk(held, t_e + 0.1, t_e + 2.0, [DOOR_OUT, IN], stride=0.4, turn=False)
S.reach(held, t_e, "R", inf=0.0)
S.beat(held, t_e + 2.1, "staan", face="bang", face_amt=0.5, at=ap(0, 5.7, 1.2), feet="keep")
S.beat(held, t_e + 2.9, "staan", face="twijfel", face_amt=0.7, at=ap(-2.0, 2.0, 0.3), feet="keep")
FR_AT = V(9.3, 31.4, 0)
S.teleport(vr, t_e, FR_AT, -90)
vr.rig.location = tuple(FR_AT)
vr.rig.keyframe_insert("location", frame=F(t_e))
S.reach(vr, t_e, "L", inf=0.0)
S.beat(vr, t_e, "staan", face="nerveus", face_amt=0.5, at=ap(0, 4, 1.4))

# ---------------------------------------------------------------- 12e2: achter de toonbank, de laatjes
BEHIND = V(COUNTER_STAFF_X + 0.62, 0, 0)
LA = {k: S.obj(f"Apotheek_la_{k}") for k in range(6)}
la0_y = LA[0].location.y
H_LA = V(BEHIND.x, ap(-1.2, 0).y, 0)                      # voor la 0 (boven, aan de deurkant)
S.teleport(held, t_e2, H_LA, -90)                          # kijkt naar -x, naar de toonbank
held.rig.location = tuple(H_LA)
held.rig.keyframe_insert("location", frame=F(t_e2))


def la_key(k, t, out):
    o = LA[k]
    base = o.get("_y0", None)
    if base is None:
        o["_y0"] = o.location.y
        base = o.location.y
    o.location.y = base + out
    o.keyframe_insert("location", index=1, frame=F(t))


def grip(k):
    S.sc.frame_set(S.sc.frame_current)
    return LA[k].matrix_world @ V(0, 0.06, 0.12)


la_key(0, 0.0, 0.0)
la_key(3, 0.0, 0.0)
T1, T2, T3 = t_e2 + 0.35, t_e2 + 1.2, t_e2 + 2.15
la_key(0, T1, 0.0)
la_key(0, T1 + 0.25, 0.32)                                # open
la_key(3, T2, 0.0)
la_key(3, T2 + 0.25, 0.3)                                 # nog een la
la_key(0, T3, 0.32)
la_key(0, T3 + 0.08, 0.0)                                 # dicht geslagen
la_key(3, T3 + 0.4, 0.3)
S.sc.frame_set(1)
G0 = LA[0].matrix_world @ V(0, 0.06, 0.12)
G3 = LA[3].matrix_world @ V(0, 0.06, 0.12)
S.reach(held, t_e2 - 1.0 / FPS, "R", inf=0.0)               # IK pas aan op de snede (geen trage overgang tijdens 12e)
S.reach(held, t_e2, "R", G0 + V(0.05, 0, 0.12))
S.reach(held, T1, "R", G0 + V(0.03, 0, 0))
S.reach(held, T1 + 0.25, "R", G0 + V(0.35, 0, 0))
S.reach(held, T2 - 0.2, "R", G3 + V(0.38, 0, 0.1))
S.reach(held, T2, "R", G3 + V(0.03, 0, 0))
S.reach(held, T2 + 0.25, "R", G3 + V(0.33, 0, 0))
S.reach(held, T3 - 0.25, "R", G0 + V(0.5, 0, 0.12))       # aanloop (anticipatie)
S.reach(held, T3 + 0.08, "R", G0 + V(0.02, 0, 0.02))      # klap
S.reach(held, t_f - 0.05, "R", G0 + V(0.2, 0, 0.15))
S.reach(held, t_e2, "L", inf=0.0)
S.reach(held, t_f - 0.05, "L", inf=0.0)
# hij staat stil: zonder feet="keep" werkt het door de knieën gaan echt (anders haalt hij de laatjes niet)
S.beat(held, t_e2 + 0.2, "staan", face="vastberaden", face_amt=0.6, at=G0 + V(0.3, 0, 0), body={"spine": (14, 0, 0)}, crouch=(0.18, 12))
S.beat(held, T2 - 0.1, "staan", face="nerveus", face_amt=0.7, at=G3 + V(0.3, 0, 0), body={"spine": (20, 0, 0)}, crouch=(0.33, 22))
S.beat(held, T3 + 0.1, "staan", face="boos", face_amt=0.8, at=G0 + V(-0.3, 0, 0.3), body={"spine": (8, 0, 0)}, crouch=(0.12, 8))

# ---------------------------------------------------------------- 12f: leunt met twee handen op het blad, hoofd zakt
H_F = V(COUNTER_STAFF_X + 0.48, ap(-0.2, 0).y, 0)
S.teleport(held, t_f, H_F, -90)
held.rig.location = tuple(H_F)
held.rig.keyframe_insert("location", frame=F(t_f))
for t in (t_f, END):
    S.reach(held, t, "L", V(COUNTER_STAFF_X - 0.12, H_F.y - 0.22, TOP_Z + 0.04))
    S.reach(held, t, "R", V(COUNTER_STAFF_X - 0.12, H_F.y + 0.22, TOP_Z + 0.04))
S.beat(held, t_f, "staan", face="boos", face_amt=0.5, at=V(10.0, H_F.y, 1.0), body={"spine": (10, 0, 0)})
S.beat(held, t_f + 1.6, "staan", face="twijfel", face_amt=0.9, at=V(12.6, H_F.y, 0.4), body={"spine": (16, 0, 0), "chest": (6, 0, 0)}, feet="keep")
S.beat(held, END, "staan", face="twijfel", face_amt=1.0, at=V(12.8, H_F.y, 0.2), body={"spine": (18, 0, 0), "chest": (8, 0, 0)}, feet="keep")
S.say("N12-03", who=held, at=t_f + 0.2)

# ---------------------------------------------------------------- 12g: de vriend bij de etalage kijkt naar buiten
FR_G = V(10.75, 30.6, 0)
S.teleport(vr, t_g, FR_G, -90)
vr.rig.location = tuple(FR_G)
vr.rig.keyframe_insert("location", frame=F(t_g))
S.beat(vr, t_g, "staan", face="verbaasd", face_amt=0.6, at=V(2.0, 27.0, 1.3))
S.beat(vr, t_g + 0.9, "staan", face="geschrokken", face_amt=0.8, at=V(2.0, 26.0, 1.3))
S.beat(vr, END, "staan", face="geschrokken", face_amt=1.0, at=V(2.0, 26.0, 1.3), body={"spine": (-4, 0, 0)})
S.say("N12-04", who=vr, at=t_g + 0.3)
for ch in (held, vr):
    S.hold(ch, END)

# ---------------------------------------------------------------- camera's
# 12d WIDE push-in van voren: de jongens komen met hun fiets door de lege winkelstraat naar ons toe
S.cam(0.0, ((0.4, 9.5, 1.7), (0.0, 34.0, 1.6), 26), ((0.3, 12.0, 1.6), (0.0, 34.0, 1.5), 28))
# 12e MEDIUM statisch, binnen in de hoek achter de toonbank: deur en lege schappen
S.cam(t_e, ((15.3, 29.0, 1.7), (10.2, 34.4, 1.1), 22), ((15.3, 29.05, 1.7), (10.2, 34.4, 1.1), 22))
# 12e2 MEDIUM langs de toonbank (personeelskant): de laatjes op de voorgrond, hij en profil
S.cam(t_e2, ((COUNTER_STAFF_X + 0.9, H_LA.y - 2.7, 1.15), (COUNTER_STAFF_X + 0.3, H_LA.y, 0.75), 28), ((COUNTER_STAFF_X + 0.88, H_LA.y - 2.5, 1.13), (COUNTER_STAFF_X + 0.3, H_LA.y, 0.75), 30))
# 12f CLOSE van schuin voor, over de toonbank
HF = S.headpos(held, t_f + 1.0)
S.cam(t_f, (HF + V(-1.55, -0.7, 0.1), HF + V(0, 0, -0.2), 30), (HF + V(-1.4, -0.62, 0.08), HF + V(0, 0, -0.2), 32))
# 12g CLOSE push-in van buiten, door de kapotte etalage
HG = S.headpos(vr, t_g + 1.0)
S.cam(t_g, (HG + V(-1.6, -0.35, 0.0), HG + V(0, 0, -0.08), 32), (HG + V(-1.2, -0.26, 0.0), HG + V(0, 0, -0.08), 36), handheld=0.3)

# ---------------------------------------------------------------- HUD, geluid en stem
S.counter("DAY 6", 0, t0=0.0)
S.music("m_reis", 0.0, t_e + 1.0, vol=0.18, fade_in=0.2, fade_out=0.8)
S.ambience("sfx_stad_nacht_wind", 0.0, END, vol=0.04)
S.sfx("sfx_la_dicht", T1, 0.25)
S.sfx("sfx_la_dicht", T2, 0.25)
S.sfx("sfx_la_dicht", T3 + 0.05, 0.6)
S.finish(length=END, tail=0.0)
