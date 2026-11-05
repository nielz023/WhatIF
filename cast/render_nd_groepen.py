"""Video 4: glans-renders van de cast in groepjes (hele figuur, iets van opzij), zodat je leeftijdsvarianten
naast elkaar ziet. Gebruik: python cast/render_nd_groepen.py --blend .../cast_never_die.blend --out map [--samples 64]"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
import render_glans as RG  # noqa: E402

GROEPEN = [
    ("01_hoofdpersonage_per_tijdperk", ["hoofdpersonage_kind", "hoofdpersonage_pak", "hoofdpersonage_2200",
                                        "hoofdpersonage_ijs", "hoofdpersonage_zwerver", "hoofdpersonage_rafels"]),
    ("02_gezin_2026_en_later", ["opa", "oma", "mama", "papa", "mama_oud", "papa_oud", "broertje", "broertje_oud"]),
    ("03_vriend_en_pestkop", ["beste_vriend", "beste_vriend_20", "beste_vriend_40", "pestkop", "pestkop_agent",
                              "pestkop_oud", "verpleger"]),
    ("04_2026_tot_2066", ["wetenschapper", "nieuwslezeres", "vuilnisman", "agent", "portier", "tante", "brandweerman",
                          "meisje_brand", "moeder_meisje"]),
    ("05_toekomst", ["directeur", "bewaker_a", "bewaker_b", "mens_2200_a", "mens_2200_b", "toekomst_a", "toekomst_b",
                     "kind_holo", "museumkind_a", "museumkind_b", "museumkind_c", "toekomstvrouw"]),
]
# de gezinsfoto van zijn 14e verjaardag (prop: oude foto in 2086/2110/1 mln jaar): gezin recht naar voren, dicht op elkaar
GEZINSFOTO = ["opa", "papa", "broertje", "hoofdpersonage_kind", "mama", "oma"]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    o = dict(zip(argv[::2], argv[1::2]))
    out = o.get("--out", "renders")
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=o["--blend"])
    sc = bpy.context.scene
    studio = RG.setup_look(int(o.get("--samples", 64)), int(o.get("--pct", 100)))
    cam = sc.camera
    for lc in bpy.context.view_layer.layer_collection.children["cast"].children:
        lc.exclude = True
    tmp = bpy.data.collections.new("glans_tmp")
    sc.collection.children.link(tmp)
    for ob in studio.objects:
        if ob.type == "LIGHT" and ob.name != "kruin":
            ob.light_linking.receiver_collection = tmp
            ob.data.size *= 2.0
            ob.location.x *= 1.8
            ob.data.energy *= 1.8
    cast = bpy.data.collections["cast"]
    only = o.get("--only", "")
    groepen = GROEPEN + [("gezinsfoto_14e_verjaardag", GEZINSFOTO)]
    for naam, keys in groepen:
        if (only and only not in naam) or (not only and naam.startswith("gezinsfoto")):
            continue
        for ob in list(tmp.objects):
            bpy.data.objects.remove(ob)
        foto = naam.startswith("gezinsfoto")
        gap = 0.62 if foto else 0.85
        x0 = -(len(keys) - 1) * gap / 2
        for k, key in enumerate(keys):
            c = cast.children.get(key)
            if c:
                # foto: de kinderen iets naar voren, iedereen naar de camera
                y = -0.35 if foto and key in ("broertje", "hoofdpersonage_kind") else 0.0
                RG.instance(c, (x0 + k * gap, y, 0), 0.0 if foto else math.radians(-18), tmp)
        W = len(keys) * gap
        if foto:
            RG.aim(cam, (0, -5.4, 1.3), (0, 0, 0.92), lens=42)
            RG.render(os.path.join(out, f"{naam}.png"), 1500, 1000)
        else:
            RG.aim(cam, (0, -max(4.2, W * 1.45), 1.25), (0, 0, 0.85), lens=50)
            RG.render(os.path.join(out, f"{naam}.png"), 2400, 1100)


main()
