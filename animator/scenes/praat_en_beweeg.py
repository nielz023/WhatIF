# SJABLOON: praten + bewegen gecombineerd.
# Pas alleen het blok "SCÈNE-INSTELLINGEN" aan; de rest (lipsync, knikjes, gebaren, emoties,
# knipperen, luisteraars, camera, render) gaat automatisch.
#
#   blender -b --disable-autoexec <glans_hoofdpersonage_volledig.blend> -P praat_en_beweeg.py -- <stills|anim> <uitvoermap>
import bpy, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene_lib as L
from scene_lib import R, key, curve, smoothstep

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "stills"
OUT = argv[1] if len(argv) > 1 else os.path.join(HERE, "render_praat_beweeg")

# ======================================================================== SCÈNE-INSTELLINGEN
AUDIO = os.path.join(HERE, "..", "praattest", "bram_zin.wav")          # mono WAV van de zin
CUES = os.path.join(HERE, "..", "praattest", "bram_zin_mond.json")     # Rhubarb-uitvoer
LEAD = 10                         # frames stilte vóór de eerste klank
STAART = 18                       # frames na de laatste klank
SPREKER_POS = (0.32, 0.0, 0.0)    # Bram
LUISTERAARS = [                   # (collectienaam, positie, draaiing in graden)
    ("beste_vriend", (-0.9, 0.3, 0.0), 32),
]
# Eén regel per zin (Rhubarb splitst zinnen op stiltes van >= 0,3 s). Ontbreekt een regel, dan neutraal.
#   gebaar: zwaai | hand_op_borst | uitleggen | armen_omhoog | wijzen | vuisten | handen_in_zij | None
#   arm: 1 = rechts in beeld, -1 = links, 0 = beide
#   emotie: neutraal | blij | heel_blij | boos | verbaasd | bezorgd | nieuwsgierig | trots
ZINNEN = [
    dict(emotie="heel_blij", gebaar="zwaai", arm=1, hoofd=dict(up=6, tilt=5), lijf=dict(lean=-2)),
    dict(emotie="nieuwsgierig", gebaar="uitleggen", arm=1, hoofd=dict(tilt=-8, turn=6), lijf=dict(lean=3)),
    dict(emotie="verbaasd", eind_emotie="heel_blij", gebaar="armen_omhoog", arm=0,
         hoofd=dict(up=9, tilt=3), lijf=dict(dz=0.02, squash=1.03)),
]
CAMERA = dict(van=((0.9, -9.5, 0.75), (-0.15, 0, 0.85)),      # (camera, kijkpunt) aan het begin
              naar=((0.6, -6.2, 0.9), (0.15, 0, 1.1)))          # ... en aan het eind (langzaam inzoomen)
# ==========================================================================================

shown = {"hoofdpersonage"} | {c for c, _, _ in LUISTERAARS}
scene, buiten = L.setup(shown)
bram = L.rig_bram()
listeners = [(L.rig_named(c), pos, yaw) for c, pos, yaw in LUISTERAARS]
# LET OP: de buitenwereld (met duizenden blaadjes) pas aan het eind bouwen;
# anders rekent Blender bij elke mond-keyframe de hele scène opnieuw door (10x trager).
cam, aim = L.camera(buiten, lens=50, fstop=2.8, focus_parent=bram.nod, focus_loc=(0, -0.3, 1.45))

peaks, dur = L.audio_peaks(AUDIO, LEAD)
END = int(LEAD + dur * 24 + STAART)
phrases = L.lipsync(bram, CUES, LEAD, end=END)
L.nods(bram, peaks)
L.add_sound(AUDIO, LEAD)
print("zinnen (frames):", phrases, "klemtonen:", peaks, "einde:", END)

bram.char.location = SPREKER_POS
for rig, pos, yaw in listeners:
    rig.char.location = pos
    rig.char.rotation_euler = (0, 0, R(yaw))

# ---------------------------------------------------------------- spreker: per zin gebaar + emotie + houding
eye_track = [(1, 1.0)]
L.emotion(bram, 1, "neutraal", eye_track)
L.rest(bram, 1)
L.body_keys(bram, 1)
L.head_keys(bram, 1)
for i, (fs, fe) in enumerate(phrases):
    z = ZINNEN[i] if i < len(ZINNEN) else dict(emotie="neutraal", gebaar=None)
    start = max(2, int(fs) - 4)                         # 4 frames anticipatie
    L.emotion(bram, start, z["emotie"], eye_track)
    if z.get("eind_emotie"):
        L.emotion(bram, int(fe), z["eind_emotie"], eye_track)
    # anticipatie: even inveren, dan in de houding
    L.body_keys(bram, start, lean=1, dz=-0.012, squash=0.975)
    lijf = z.get("lijf", {})
    L.body_keys(bram, start + 6, **lijf)
    L.body_keys(bram, int(fe), **lijf)
    hoofd = z.get("hoofd", {})
    L.head_keys(bram, start + 6, **hoofd)
    L.head_keys(bram, int(fe), **{k: v * 0.8 for k, v in hoofd.items()})
    if z.get("gebaar"):
        sides = (-1, 1) if z.get("arm", 1) == 0 else (z.get("arm", 1),)
        for s in sides:
            L.gesture(bram, z["gebaar"], start, s=s, length=max(12, int(fe - start)))
    # in de pauze naar rust (behalve na de laatste zin)
    nxt = phrases[i + 1][0] if i + 1 < len(phrases) else None
    if nxt is not None and nxt - fe > 8:
        L.rest(bram, int(fe + (nxt - fe) * 0.6))
        L.body_keys(bram, int(fe + (nxt - fe) * 0.6))
        L.head_keys(bram, int(fe + (nxt - fe) * 0.6))

# knipperen: in elke pauze + om de ~3 s
blinks = [int((a[1] + b[0]) / 2) for a, b in zip(phrases, phrases[1:])] + [END - 6]
eye_track.sort()
L.blink_bake(bram, blinks, END, base=eye_track)

# ---------------------------------------------------------------- luisteraars: ademen, knipperen, meeknikken
for n, (rig, pos, yaw) in enumerate(listeners):
    for f in range(1, END + 1, 12):
        key(rig.root, "scale", f, Vector((1, 1, 1 + 0.006 * math.sin(f / 12 * math.pi + n))))
    key(rig.nod, "rotation_euler", 1, (0, 0, 0))
    for fs, fe in phrases:
        key(rig.nod, "rotation_euler", int(fe) - 1, (0, 0, 0))
        key(rig.nod, "rotation_euler", int(fe) + 3, (R(4), 0, 0))
        key(rig.nod, "rotation_euler", int(fe) + 8, (0, 0, 0))
    L.head_keys(rig, 1, tilt=3)
    L.head_keys(rig, END, tilt=-2)
    L.brow_keys(rig, 1, 0.0, 0)
    L.brow_keys(rig, END, 0.008, -4)
    L.blink_bake(rig, [24 + 7 * n, 88 + 5 * n, END - 14], END)

# ---------------------------------------------------------------- camera
(c0, a0), (c1, a1) = CAMERA["van"], CAMERA["naar"]
key(cam, "location", 1, Vector(c0))
key(cam, "location", END, Vector(c1))
key(aim, "location", 1, Vector(a0))
key(aim, "location", END, Vector(a1))

L.build_outdoor(buiten)
L.render_settings(samples=28)
mid = [int((fs + fe) / 2) for fs, fe in phrases]
L.run(MODE, OUT, os.path.join(HERE, "praat_en_beweeg.blend"), mid, END)
