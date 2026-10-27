"""Acteren: gezichtsuitdrukkingen, lichaamshoudingen, knipperen, ademen en lipsync.

Alle functies werken op een `rig.Character` en zetten keyframes op een frame.
Houdingen zijn rotaties in graden per bot voor de linkerkant; de rechterkant
wordt gespiegeld (Y- en Z-rotatie omgekeerd), tenzij een bot met '.R' expliciet
in de houding staat.

Bot-assen (zie rig.py): +X buigt een bot naar voren. Knie buigen = negatieve X.
Arm zijwaarts omhoog (abductie) = +Z voor links. Hoofd draaien naar zijn linkerkant = +Y.
"""
import math
import random
import subprocess

import bpy
from mathutils import Vector, Euler, Matrix

# ---------------------------------------------------------------------------
# Gezichtsuitdrukkingen: waarden voor de gezichtsknoppen (rest = 0)
# ---------------------------------------------------------------------------
EXPR = {
    "neutraal": {},
    "blij": dict(mond_lach=0.7, wenkbrauw_op=0.2, ogen_knijp=0.15),
    "lach": dict(mond_lach=0.6, mond_open=0.45, wenkbrauw_op=0.35, ogen_knijp=0.3),
    "grijns": dict(mond_grijns=1.0, wenkbrauw_op_L=0.5, wenkbrauw_boos=0.15),
    "zelfverzekerd": dict(mond_grijns=0.7, mond_lach=0.2, wenkbrauw_boos=0.25, ogen_knijp=0.2),
    "vastberaden": dict(wenkbrauw_boos=0.65, ogen_knijp=0.35, mond_breed=0.25, mond_verdrietig=0.2),
    "inspanning": dict(wenkbrauw_boos=0.9, ogen_knijp=0.75, mond_breed=0.9, mond_open=0.15),
    "bang": dict(wenkbrauw_op=0.7, wenkbrauw_boos=-0.6, ogen_wijd=0.8, pupil_klein=0.6, mond_breed=0.55, mond_open=0.25),
    "geschrokken": dict(wenkbrauw_op=1.0, ogen_wijd=1.0, pupil_klein=0.8, mond_O=0.8, mond_open=0.5),
    "verbaasd": dict(wenkbrauw_op=0.9, ogen_wijd=0.6, mond_O=0.6, mond_open=0.2),
    "nerveus": dict(wenkbrauw_op=0.35, wenkbrauw_boos=-0.5, mond_breed=0.45, mond_verdrietig=0.3, ogen_wijd=0.25),
    "verdrietig": dict(wenkbrauw_boos=-0.8, wenkbrauw_op=0.1, mond_verdrietig=0.9, ogen_knijp=0.2, kijk_y=-0.4),
    "boos": dict(wenkbrauw_boos=1.0, ogen_knijp=0.4, mond_verdrietig=0.6, mond_breed=0.3),
    "schreeuw": dict(wenkbrauw_op=0.6, wenkbrauw_boos=0.2, ogen_wijd=0.5, mond_open=1.0, mond_breed=0.3),
    "twijfel": dict(wenkbrauw_op_L=0.7, wenkbrauw_op_R=-0.3, mond_grijns=0.4, mond_verdrietig=0.3, kijk_x=0.4, kijk_y=0.3),
}
FACE_KEYS = ["ogen_wijd", "ogen_knijp", "pupil_klein", "kijk_x", "kijk_y", "wenkbrauw_op", "wenkbrauw_boos",
             "wenkbrauw_op_L", "wenkbrauw_op_R", "mond_lach", "mond_verdrietig", "mond_O", "mond_breed", "mond_grijns"]
# mond_open en knipper worden door lipsync/knipperen beheerd; uitdrukking geeft een basis-opening mee
LIPSYNC_BASE = {}


def key_prop(rig, prop, value, frame):
    rig[prop] = value
    rig.keyframe_insert(f'["{prop}"]', frame=frame)


def expr(ch, frame, name, amount=1.0, hold=None, look=None, **extra):
    """Zet uitdrukking `name` op `frame` (alle gezichtsknoppen gekeyd). look=(x, y) kijkrichting."""
    vals = {k: 0.0 for k in FACE_KEYS}
    for k, v in EXPR[name].items():
        if k != "mond_open":
            vals[k] = v * amount
    if look:
        vals["kijk_x"], vals["kijk_y"] = look
    vals.update(extra)
    for k, v in vals.items():
        key_prop(ch.rig, k, v, frame)
    LIPSYNC_BASE.setdefault(ch.name, []).append((frame, EXPR[name].get("mond_open", 0.0) * amount))
    if hold:
        for k, v in vals.items():
            key_prop(ch.rig, k, v, frame + hold)


def look(ch, frame, x, y):
    key_prop(ch.rig, "kijk_x", x, frame)
    key_prop(ch.rig, "kijk_y", y, frame)


def blinks(ch, start, end, seed=1, every=(55, 110)):
    """Natuurlijk knipperen: 2 frames dicht, soms dubbel."""
    rnd = random.Random(seed + hash(ch.name) % 1000)
    f = start + rnd.randint(5, 30)
    key_prop(ch.rig, "knipper", 0.0, start)
    while f < end - 6:
        key_prop(ch.rig, "knipper", 0.0, f)
        key_prop(ch.rig, "knipper", 1.0, f + 2)
        key_prop(ch.rig, "knipper", 1.0, f + 3)
        key_prop(ch.rig, "knipper", 0.0, f + 5)
        if rnd.random() < 0.15:
            key_prop(ch.rig, "knipper", 1.0, f + 7)
            key_prop(ch.rig, "knipper", 0.0, f + 9)
        f += rnd.randint(*every)


def blink_at(ch, frame, closed=2):
    key_prop(ch.rig, "knipper", 0.0, frame - 2)
    key_prop(ch.rig, "knipper", 1.0, frame)
    key_prop(ch.rig, "knipper", 1.0, frame + closed)
    key_prop(ch.rig, "knipper", 0.0, frame + closed + 2)


# ---------------------------------------------------------------------------
# Houdingen. Armen worden gericht met richtingen in het lichaam van het personage:
# x = zijn linkerkant, y = naar voren, z = omhoog. Per arm (bovenarm, onderarm,
# hand); de rechterarm spiegelt de linker, tenzij 'R' apart is gegeven.
# Romp/nek/hoofd zijn Euler-rotaties in graden (+X = voorover/knikken).
# ---------------------------------------------------------------------------
REST = "rust"
POSES = {
    "staan": dict(L=((0.22, 0.04, -1), (0.10, 0.12, -1), None)),
    "ontspannen": dict(L=((0.18, -0.02, -1), (0.12, 0.25, -1), None), body={"spine": (-2, 0, 0), "head": (-3, 0, 2)}),
    "vuisten": dict(L=((0.35, 0.10, -0.95), (0.15, 0.75, -0.55), None), body={"chest": (4, 0, 0)}),
    "schrap": dict(L=((0.40, 0.60, -0.70), (0.05, 0.95, -0.15), None),
                   body={"spine": (14, 0, 0), "chest": (10, 0, 0), "head": (-18, 0, 0)}),
    "schrik": dict(L=((0.55, 0.40, -0.30), (-0.25, 0.35, 0.90), None), body={"spine": (-8, 0, 0), "chest": (-6, 0, 0)}),
    "armen_omhoog": dict(L=((0.40, 0.10, 0.92), (0.30, 0.05, 0.96), None)),
    "zwaaien_a": dict(L=((0.85, 0.20, 0.35), (0.35, 0.10, 0.95), None), R=REST),
    "zwaaien_b": dict(L=((0.85, 0.20, 0.35), (-0.15, 0.10, 0.98), None), R=REST),
    "wijzen": dict(L=((0.15, 0.95, 0.10), (0.05, 1.0, 0.12), None), R=REST),
    "handen_hoofd": dict(L=((0.75, 0.30, 0.55), (-0.60, 0.15, 0.60), None)),
    "filmen": dict(L=((0.20, 0.60, -0.55), (-0.35, 0.80, 0.50), None), R=REST),
    "filmen_R": dict(L=REST, R=((0.20, 0.60, -0.55), (-0.35, 0.80, 0.50), None)),
    "zitten_beugel": dict(L=((0.25, 0.75, -0.62), (0.05, 0.98, 0.10), None), body={"spine": (4, 0, 0)}),
    "kraken": dict(L=((0.28, 0.50, -0.75), (-0.75, 0.60, 0.20), None)),
    "duwen": dict(L=((0.25, 0.95, 0.00), (0.05, 1.0, 0.10), None), body={"spine": (12, 0, 0), "chest": (6, 0, 0)}),
    "armen_over": dict(L=((0.22, 0.30, -0.90), (-0.90, 0.40, 0.10), None)),
    "schouders_op": dict(L=((0.45, 0.15, -0.85), (0.60, 0.50, 0.15), None), body={"head": (-4, 0, 6)}),
    "juichen": dict(L=((0.70, 0.10, 0.70), (0.30, 0.0, 0.95), None), body={"chest": (-8, 0, 0), "head": (-12, 0, 0)}),
    "handen_zij": dict(L=((0.55, -0.10, -0.80), (-0.60, 0.15, -0.35), None)),
}
BODY_BONES = ("hips", "spine", "chest", "neck", "head")
ARM_BONES = ("upper_arm", "forearm", "hand")


def _char_to_arm(v, side):
    """Lichaamsrichting (x links, y voor, z op) -> armatuurruimte (personage kijkt naar -y)."""
    x, y, z = v
    if side == "R":
        x = -x
    return Vector((x, -y, z)).normalized()


def _rest_dir(rig, bone):
    b = rig.data.bones[bone]
    return (b.tail_local - b.head_local).normalized(), b.matrix_local.to_3x3()


def aim_arm(ch, frame, side, upper, fore, hand=None, twist=(0, 0, 0)):
    """Richt bovenarm, onderarm en hand in lichaamsrichtingen (relatief aan de romp)."""
    rig = ch.rig
    q_parent = Matrix.Identity(3)
    dirs = (upper, fore, hand)
    for k, bn in enumerate(ARM_BONES):
        bone = f"{bn}.{side}"
        pb = ch.pb[bone]
        pb.rotation_mode = "QUATERNION"
        d_rest, M = _rest_dir(rig, bone)
        cur = q_parent @ d_rest            # waar het bot nu naartoe wijst (armatuurruimte)
        if dirs[k] is None:
            target = cur
        else:
            target = _char_to_arm(dirs[k], side)
        # gewenste rotatie in armatuurruimte, uitgedrukt t.o.v. de ouder
        want_local_arm = q_parent.inverted() @ target
        rot_arm = d_rest.rotation_difference(want_local_arm).to_matrix()
        basis = (M.inverted() @ rot_arm @ M).to_quaternion()
        if twist[k]:
            from mathutils import Quaternion
            basis = basis @ Quaternion((0, 1, 0), math.radians(twist[k] * (1 if side == "L" else -1)))
        prev = pb.rotation_quaternion.copy()
        if prev.dot(basis) < 0:
            basis.negate()
        pb.rotation_quaternion = basis
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        q_parent = q_parent @ (M @ basis.to_matrix() @ M.inverted())


def pose(ch, frame, name, amount=1.0, extra=None, arms=True, twist=None):
    """Keyframe een houding. extra = {bot: (x, y, z)} graden voor romp/hoofd."""
    P = POSES[name]
    body = {b: (0, 0, 0) for b in ("spine", "chest", "neck", "head")}
    body.update(P.get("body", {}))
    if extra:
        body.update(extra)
    for b, r in body.items():
        pb = ch.pb[b]
        pb.rotation_euler = Euler([math.radians(a * amount) for a in r])
        pb.keyframe_insert("rotation_euler", frame=frame)
    if not arms:
        return
    for side in "LR":
        spec = P.get(side, P["L"])
        if spec == REST:
            spec = POSES["staan"]["L"]
        u, f, h = spec
        if amount != 1.0:
            ru, rf, _ = POSES["staan"]["L"]
            u = tuple(a + (b - a) * amount for a, b in zip(ru, u))
            f = tuple(a + (b - a) * amount for a, b in zip(rf, f))
        aim_arm(ch, frame, side, u, f, h, twist=(twist or {}).get(side, (0, 0, 0)))


def bone_rot(ch, frame, bone, rot):
    pb = ch.pb[bone]
    pb.rotation_euler = Euler([math.radians(a) for a in rot])
    pb.keyframe_insert("rotation_euler", frame=frame)


def bone_loc(ch, frame, bone, loc):
    pb = ch.pb[bone]
    pb.location = loc
    pb.keyframe_insert("location", frame=frame)


def _set_interp(obj, path, frame, interp):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    for fc in _fcurves(obj):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.5:
                    kp.interpolation = interp


def _fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


# ---------------------------------------------------------------------------
# Lichaam: heupen omlaag (door de knieën), voeten verplaatsen
# ---------------------------------------------------------------------------
def crouch(ch, frame, depth=0.0, lean=0.0, shift=(0, 0)):
    """Heupen omlaag in meters (voeten blijven staan door IK). lean = graden voorover."""
    pb = ch.pb["hips"]
    # 'hips' wijst omhoog: lokale Y = omhoog, lokale Z = naar voren, X = opzij
    pb.location = (shift[0], -depth, shift[1])
    pb.keyframe_insert("location", frame=frame)
    pb.rotation_euler = Euler((math.radians(lean), 0, 0))
    pb.keyframe_insert("rotation_euler", frame=frame)


def foot(ch, frame, side, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Verplaats een IK-voet (wereldas-achtig: x opzij, y vooruit = -y figuur, z omhoog), relatief aan rust."""
    pb = ch.pb["foot_ik." + side]
    # foot_ik: Y wijst naar de tenen (voor/omlaag), Z grotendeels omhoog; gebruik matrix_basis-vertaling via armatuurruimte
    rest = ch.rig.data.bones["foot_ik." + side].matrix_local.to_3x3()
    d = rest.inverted() @ Vector((loc[0], -loc[1], loc[2]))
    pb.location = d
    pb.keyframe_insert("location", frame=frame)
    pb.rotation_euler = Euler([math.radians(a) for a in rot])
    pb.keyframe_insert("rotation_euler", frame=frame)


def hand_ik(ch, frame, side, influence, world_target=None, rot=None):
    """Zet de hand-IK aan/uit; world_target = wereldpositie van de pols."""
    pb = ch.pb["hand_ik." + side]
    c = ch.pb["forearm." + side].constraints["Hand_IK"]
    cr = ch.pb["hand." + side].constraints["Hand_IK_rot"]
    c.influence = influence
    c.keyframe_insert("influence", frame=frame)
    cr.influence = influence
    cr.keyframe_insert("influence", frame=frame)
    if world_target is not None:
        rig = ch.rig
        # matrix_basis klopt altijd met loc/rot/schaal; matrix_world pas na een depsgraph-update
        mw = rig.matrix_world if rig.parent else rig.matrix_basis
        local = mw.inverted() @ Vector(world_target)
        rest = rig.data.bones["hand_ik." + side].matrix_local
        pb.location = rest.to_3x3().inverted() @ (local - rest.translation)
        pb.keyframe_insert("location", frame=frame)
    if rot is not None:
        pb.rotation_euler = Euler([math.radians(a) for a in rot])
        pb.keyframe_insert("rotation_euler", frame=frame)


def place(ch, frame, loc=None, rot_z=None):
    if loc is not None:
        ch.rig.location = loc
        ch.rig.keyframe_insert("location", frame=frame)
    if rot_z is not None:
        ch.rig.rotation_euler = (0, 0, math.radians(rot_z))
        ch.rig.keyframe_insert("rotation_euler", frame=frame)


# ---------------------------------------------------------------------------
# Leven: ademen en lichte bewegingen (bovenop houdingen, via NLA-vrije ruis)
# ---------------------------------------------------------------------------
def alive(ch, start, end, energy=1.0, seed=3):
    """Ademhaling op de borst en lichte hoofd-/romp-ruis via F-curve-modifiers."""
    rig = ch.rig
    for b, idx, amp, scale in (("chest", 0, 1.2, 70), ("head", 0, 2.0, 55), ("head", 1, 2.5, 80), ("head", 2, 1.5, 65),
                               ("spine", 2, 0.8, 90)):
        path = f'pose.bones["{b}"].rotation_euler'
        fc = None
        for f in _fcurves(rig):
            if f.data_path == path and f.array_index == idx:
                fc = f
        if fc is None:
            pb = ch.pb[b]
            pb.keyframe_insert("rotation_euler", index=idx, frame=start)
            for f in _fcurves(rig):
                if f.data_path == path and f.array_index == idx:
                    fc = f
        if fc is None:
            continue
        m = fc.modifiers.new("NOISE")
        m.scale = scale
        m.strength = math.radians(amp * energy) * 2
        m.phase = seed * 7 + idx * 13 + len(b)
        m.blend_type = "ADD"
        m.use_restricted_range = True             # na `end` staat hij stil (bevroren figuren in de shorts)
        m.frame_start, m.frame_end = start, end
    # ademhaling: borst schaal
    pb = ch.pb["chest"]
    pb.keyframe_insert("scale", frame=start)
    for f in _fcurves(rig):
        if f.data_path == 'pose.bones["chest"].scale' and f.array_index in (0, 2):
            m = f.modifiers.new("GENERATOR") if False else f.modifiers.new("FNGENERATOR")
            m.function_type = "SIN"
            m.amplitude = 0.012 * energy
            m.phase_multiplier = 2 * math.pi / (3.8 * 24)
            m.use_additive = True
            m.use_restricted_range = True
            m.frame_start, m.frame_end = start, end


# ---------------------------------------------------------------------------
# Lipsync uit een audiobestand
# ---------------------------------------------------------------------------
def _envelope(path, fps):
    """RMS-energie per frame, plus 'hoge' (s/f/ie) en 'lage' (oe/o) banden."""
    import numpy as np
    try:
        # audaspace zit in Blender zelf: geen ffmpeg nodig
        import aud
        snd = aud.Sound(path)
        sr = int(snd.specs[0])
        x = np.asarray(snd.data(), dtype=np.float32).mean(axis=1)
    except Exception:
        sr = 16000
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    hop = sr / fps
    n = int(len(x) / hop) + 1
    rms, hi, lo = [], [], []
    for i in range(n):
        seg = x[int(i * hop):int((i + 1) * hop + hop)]
        if len(seg) < 32:
            rms.append(0.0); hi.append(0.0); lo.append(0.0)
            continue
        rms.append(float(np.sqrt(np.mean(seg ** 2))))
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        fr = np.fft.rfftfreq(len(seg), 1 / sr)
        tot = sp.sum() + 1e-9
        hi.append(float(sp[fr > 3000].sum() / tot))
        lo.append(float(sp[(fr > 150) & (fr < 700)].sum() / tot))
    return rms, hi, lo


def lipsync(ch, audio, start_frame, fps=24, gain=1.0, base_open=0.0):
    """Mond open/dicht op de stem, met O-vormen (lage klanken) en brede vormen (s, ie)."""
    rms, hi, lo = _envelope(audio, fps)
    peak = max(rms) or 1.0
    rig = ch.rig
    prev = None
    n = len(rms)
    key_prop(rig, "mond_open", base_open, start_frame - 2)
    for i in range(n):
        f = start_frame + i
        a = min(1.0, (rms[i] / peak) * 1.35 * gain)
        a = 0.0 if a < 0.08 else a
        # vloeiend: half vorige
        if prev is not None:
            a = prev * 0.35 + a * 0.65
        if i % 2 == 0 or a < 0.05:
            key_prop(rig, "mond_open", base_open + a * 0.85, f)
            o = max(0.0, min(1.0, (lo[i] - 0.45) * 2.5)) * a
            w = max(0.0, min(1.0, (hi[i] - 0.15) * 3.0)) * (1 - a * 0.5)
            key_prop(rig, "mond_O", o * 0.7, f)
            key_prop(rig, "mond_breed", w * 0.5, f)
        prev = a
    key_prop(rig, "mond_open", base_open, start_frame + n + 2)
    key_prop(rig, "mond_O", 0.0, start_frame + n + 2)
    key_prop(rig, "mond_breed", 0.0, start_frame + n + 2)
    return n
