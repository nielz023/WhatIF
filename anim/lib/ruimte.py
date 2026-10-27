"""Gedeelde stukken voor de ruimtescènes (S27c, S27d, S28): het drukpak met glazen helm, een hemelkoepel die
meereist en van blauw naar zwart gaat, en de gelijmde mok."""
from scene import *  # noqa: F401,F403

SUIT_WHITE = (0.93, 0.93, 0.91)
SUIT_ORANGE = (0.98, 0.45, 0.10)


def glass(name="helmglas", edge=(0.75, 0.88, 1.0), strength=0.9):
    """Glas: in het midden doorzichtig, aan de randen een lichte blauwe glans."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    lw = N.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.25
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.04, 0.04, 0.04, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1)
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*edge, 1)
    em.inputs["Strength"].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    L.new(ramp.outputs["Color"], mx.inputs[0])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = True
    return m


def suit_actor(S, loc=(0, 0, 0), rot=0.0, energy=1.0):
    """Het hoofdpersonage in het witte drukpak: wit pak, oranje borstplaat, rugzak, halsring en een glazen helm."""
    ch = S.actor("hoofdpersonage", loc, rot, energy=energy, outfit=dict(shirt=SUIT_WHITE, broek=SUIT_WHITE))
    J = ch.J
    wit = S.mat("drukpak_wit", SUIT_WHITE)
    oranje = S.mat("drukpak_oranje", SUIT_ORANGE)
    metaal = S.mat("drukpak_metaal", (0.62, 0.64, 0.68))
    # helm: bol rond het hoofd (bot-assen: y = op, z = voor; oorsprong = botuiteinde = bovenkant hoofd)
    hr = max(J["head_r"].x, J["head_r"].z) * 1.22
    c = J["head_c"] - J["head_top"]
    helm = T.sphere("Helm_glas", (0, 0, 0), hr, glass(), seg=40, ol=0)
    helm.visible_shadow = False
    attach(helm, ch, "head", (c.x, c.z, -c.y))
    ring = T.torus("Helm_ring", (0, 0, 0), J["head_r"].x * 0.62, 0.035, metaal, rot=(90, 0, 0), seg=32, seg2=10, ol=0.004)
    neck = J["neck_top"] - J["head_top"]
    attach(ring, ch, "head", (0, neck.z - 0.04, -neck.y))
    # borstplaat en rugzak op de borst (oorsprong = bovenkant borstbot)
    plate = T.box("Pak_borstplaat_held", (0, 0, 0), (0.22, 0.05, 0.16), oranje, base=False, bevel=0.02, ol=0.004)
    attach(plate, ch, "chest", (0, -0.12, 0.17), (90, 0, 0))
    for k, col in enumerate(((1.0, 0.2, 0.15), (0.2, 1.0, 0.3), (0.3, 0.6, 1.0))):
        led = T.sphere(f"Pak_lampje_{k}", (0, 0, 0), 0.012, S.mat(f"pak_led_{k}", col, 4.0), seg=8, ol=0)
        attach(led, ch, "chest", (-0.06 + k * 0.06, -0.09, 0.2))
    pack = T.box("Pak_rugzak", (0, 0, 0), (0.34, 0.2, 0.42), wit, base=False, bevel=0.05, ol=0.006)
    attach(pack, ch, "chest", (0, -0.18, -0.24))
    return ch


def sky_dome(S, follow, keys, radius=650.0):
    """Hemelkoepel die met `follow` meereist. keys = [(t, (r, g, b), zichtbaarheid 0-1)]: kleur en dekking per tijd."""
    m = bpy.data.materials.new("hemelkoepel")
    m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    em = N.new("ShaderNodeEmission")
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    m.surface_render_method = "BLENDED"
    for t, col, a in keys:
        em.inputs["Color"].default_value = (*col, 1)
        em.inputs["Color"].keyframe_insert("default_value", frame=F(t))
        em.inputs["Strength"].default_value = 1.0
        mx.inputs[0].default_value = a
        mx.inputs[0].keyframe_insert("default_value", frame=F(t))
    dome = T.sphere("Hemelkoepel", (0, 0, 0), radius, m, seg=48, ol=0)
    dome.visible_shadow = False
    cl = dome.constraints.new("COPY_LOCATION")
    cl.target = follow
    return dome


def cloud_layer(S, center, z, n=26, spread=60.0, seed=7):
    """Een laag dikke wolken rond een punt, om doorheen te zwemmen."""
    rnd = random.Random(seed)
    wit = S.mat("wolk_dik", (0.97, 0.97, 1.0), 0.8)
    parts = []
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(1.5, spread) if k else 0.0
        s = rnd.uniform(4.0, 11.0)
        p = Vector(center) + Vector((math.cos(a) * d, math.sin(a) * d, z + rnd.uniform(-0.8, 0.8)))
        parts.append(T.sphere(f"Wolklaag_{k}", tuple(p), s, wit, scale=(1.4, 1.0, 0.28), seg=16, ol=0))
    return parts


def follow_lights(S, ch, key=(1.2, -2.6, 1.2), fill=(-2.0, -1.5, 0.4), rim=(0.5, 2.5, 2.0), energy=260):
    """Licht dat met hem meereist: in de ruimte is alleen de zon, en dan valt de schaduwkant helemaal weg."""
    for name, off, col, e in (("Volglicht_key", key, (1.0, 0.96, 0.9), energy), ("Volglicht_fill", fill, (0.75, 0.82, 1.0), energy * 0.45),
                              ("Volglicht_rim", rim, (0.85, 0.9, 1.0), energy * 0.6)):
        lt = T.point_light(name, tuple(off), color=col, energy=e, radius=0.6, shadow=False)
        cl = lt.constraints.new("COPY_LOCATION")
        cl.target = ch.rig
        cl.use_offset = True


def soften_shadows(S, shadow=(0.40, 0.44, 0.62), ambient=(0.30, 0.32, 0.42)):
    """De ruimte-mood heeft bijna zwarte schaduwen; op gezichten geeft dat ruis op de grens van licht en donker.
    Lichtere schaduwkleur in de toon-banden en wat meer omgevingslicht (de camera ziet de zwarte hemel nog steeds)."""
    for ng in bpy.data.node_groups:
        ramp = ng.nodes.get("Lichtbanden")
        if not ramp:
            continue
        els = ramp.color_ramp.elements
        li = tuple(els[len(els) - 1].color[:3])
        mid = tuple(shadow[i] * 0.35 + li[i] * 0.65 for i in range(3))
        for e in els:
            if e.position < 0.3:
                e.color = (*shadow, 1)
            elif e.position < 0.65:
                e.color = (*mid, 1)
    w = S.sc.world
    if w and w.use_nodes:
        for n in w.node_tree.nodes:
            if n.type == "BACKGROUND" and not n.inputs["Color"].is_linked:
                n.inputs["Color"].default_value = (*ambient, 1)
