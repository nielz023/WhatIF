"""S17a · Dag 16 · het pretpark overdag: een paar uur is alles perfect. Suikerspin als glas,
botsauto's waar hij niet in mag, en in de rij voor de Titan: de pestkop en zijn zusje.

    blender -b -P anim/scenes/s17a_pretpark_dag.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from scene import *  # noqa: E402,F401

S = Scene("s17a", "pretpark", "dag")

WALK_Y = -26.4
X0, X1 = 15.0, 4.2
cast = [("hoofdpersonage", 0.0, 0.0), ("mama", 0.5, 0.75), ("beste_vriend", 0.3, -0.75)]
acts = {n: S.actor(n, V(X0 + dx, WALK_Y + dy, 0), -90, energy=1.0) for n, dx, dy in cast}
held, mama, vriend = (acts[n] for n, _, _ in cast)

# ---------------------------------------------------------------- suikerspinnen
pink = S.mat("suikerspin", (1.0, 0.62, 0.80))
blue = S.mat("suikerspin_blauw", (0.55, 0.80, 1.0))
stick_m = S.mat("stokje", (0.95, 0.92, 0.85))


def candy(name, mat, r=0.13):
    st = T.cyl(name + "_stokje", (0, 0, 0), 0.008, 0.36, stick_m, seg=6, ol=0.004)
    for k, (x, y, z, s) in enumerate(((0, 0, 0.36, 1.0), (0.05, 0.03, 0.30, 0.75), (-0.05, -0.02, 0.31, 0.7), (0.0, -0.05, 0.42, 0.65))):
        T.sphere(f"{name}_wolk_{k}", (x, y, z), r * s, mat, seg=12, ol=0.006).parent = st
    return st


c_held = candy("Suikerspin_held", pink)
attach(c_held, held, "hand.R", (0, 0.02, 0.03), (90, 0, 0))
c_vriend = candy("Suikerspin_vriend", blue, r=0.15)
attach(c_vriend, vriend, "hand.R", (0, 0.02, 0.03), (90, 0, 0))

# ---------------------------------------------------------------- tijdlijn
S.hud(16, "65,536x STRONGER", t0=0.4)
S.music("kermis_wals", 0.0, 60, vol=0.24, fade_in=0.4, fade_out=1.0)
WALTZ = S.sounds[-1]
S.ambience("sfx_pretpark_sfeer", 0.0, 60, vol=0.14)
l1 = S.say("S17-01", gap=0.6)
PERFECT = l1[0] + 3.9                           # 'And for a few hours, it's perfect.'
CANDY = l1[0] + 6.5                             # 'Cotton candy you hold like it's made of glass.'
BUMP = l1[0] + 8.85                             # 'Bumper cars you're not allowed on.'
QUEUE = l1[1] + 0.25
S.t = QUEUE + 2.9
END = S.t
WALTZ["loop_to"] = END
S.gauge("GRIP USED: 0.001%", CANDY + 0.3, BUMP - 0.15, color=CYAN)

# ---------------------------------------------------------------- de familie loopt over het hoofdpad
for name, dx, dy in cast:
    S.walk(acts[name], 0.2, BUMP - 0.1, [V(X0 + dx, WALK_Y + dy, 0), V(X1 + dx, WALK_Y + dy, 0)],
           stride=0.42 if name != "hoofdpersonage" else 0.3, arms=None if name != "mama" else 0.5)

GLASS_R = arm("R", (0.14, 0.45, -0.85), (-0.2, 0.85, 0.45))
CUP_L = arm("L", (0.14, 0.5, -0.85), (-0.3, 0.9, 0.2))
CANDY_R = arm("R", (0.14, 0.4, -0.88), (-0.25, 0.8, 0.5))
SWING_L = arm("L", (0.18, 0.1, -0.97), (0.08, 0.25, -0.9))
EAT_R = arm("R", (0.2, 0.55, -0.8), (-0.45, 0.6, 0.65))

# hij: houdt de suikerspin vast alsof hij van glas is
S.beat(held, 0.0, "staan", face="blij", face_amt=0.5, look=(0, -0.3), arms=arms(GLASS_R, CUP_L), feet="keep",
       body={"head": (8, 0, 0)})
S.beat(held, PERFECT - 0.4, "staan", face="lach", face_amt=0.6, at=S.head(mama, PERFECT), arms=arms(GLASS_R, CUP_L), feet="keep")
S.beat(held, PERFECT + 1.2, "staan", face="blij", face_amt=0.7, at=S.head(vriend, PERFECT), arms=arms(GLASS_R, CUP_L), feet="keep")
for k, t in enumerate(frange(CANDY - 0.2, BUMP - 0.2, 0.32)):
    S.beat(held, t, "staan", face="inspanning", face_amt=0.45 + 0.1 * (k % 2), look=(0.05 * (k % 2), -0.6),
           arms=arms(arm("R", (0.14, 0.45, -0.85), (-0.2 + 0.01 * (k % 2), 0.85, 0.45)), CUP_L), feet="keep",
           body={"head": (16, 0, 2 * (k % 2)), "chest": (4, 0, 0)}, ogen_knijp=0.2)

# vriend: eet de zijne gewoon op
S.beat(vriend, 0.0, "staan", face="lach", face_amt=0.8, look=(0.4, 0.2), arms=arms(SWING_L, CANDY_R), feet="keep")
for k, t in enumerate(frange(1.2, BUMP - 0.3, 0.55)):
    bite = k % 3 == 0
    S.beat(vriend, t, "staan", face="lach" if not bite else "blij", face_amt=0.9,
           look=(0.3, 0.2) if not bite else (0, 0), arms=arms(SWING_L, EAT_R if bite else CANDY_R), feet="keep",
           mouth=0.6 if bite else 0.15, body={"head": (10 if bite else -4, 0, 0)})

# mama
S.beat(mama, 0.0, "staan", face="blij", face_amt=0.8, at=S.head(held, 0))
S.beat(mama, PERFECT, "staan", face="lach", face_amt=0.9, at=S.head(held, PERFECT), face_only=True)
S.beat(mama, CANDY + 0.4, "staan", face="lach", face_amt=0.6, at=S.head(held, CANDY), face_only=True)

# ---------------------------------------------------------------- de botsauto's
BUMP_C = V(26, 6, 0)
ROT_B = math.radians(8)


def bw(x, y, z=0.0):
    """Lokale coördinaten van de botsauto-vloer naar de wereld."""
    c, s = math.cos(ROT_B), math.sin(ROT_B)
    return V(BUMP_C.x + x * c - y * s, BUMP_C.y + x * s + y * c, z)


HERO_B = V(27.1, -3.15, 0)
MOM_B = V(25.85, -3.45, 0)
S.teleport(held, BUMP - 0.1, HERO_B, 178)
S.teleport(mama, BUMP - 0.1, MOM_B, heading(MOM_B, HERO_B) - 25)
S.teleport(vriend, BUMP - 0.1, V(60, -60, 0), 0)

S.beat(held, BUMP - 0.1, "staan", face="verdrietig", face_amt=0.7, look=(0.2, 0.2), arms=arms(GLASS_R, arm("L", (0.2, 0.1, -0.97), (0.1, 0.2, -0.95))))
S.beat(held, BUMP + 0.9, "staan", face="verdrietig", face_amt=0.9, look=(-0.5, 0.1), body={"head": (6, -18, 0), "chest": (6, 0, 0)},
       arms=arms(GLASS_R, arm("L", (0.2, 0.1, -0.97), (0.1, 0.2, -0.95))))
S.beat(held, QUEUE - 0.2, "staan", face="verdrietig", face_amt=0.9, look=(-0.6, 0.0), body={"head": (8, -24, 0), "chest": (8, 0, 0)},
       arms=arms(GLASS_R, arm("L", (0.2, 0.1, -0.97), (0.1, 0.2, -0.95))))
WAG_A = arm("R", (0.35, 0.5, -0.6), (0.05, 0.25, 0.97))
WAG_B = arm("R", (0.35, 0.5, -0.6), (0.3, 0.25, 0.92))
for k, t in enumerate(frange(BUMP - 0.1, QUEUE, 0.22)):
    S.beat(mama, t, "staan", face="zelfverzekerd", face_amt=0.7, at=S.head(held, BUMP), arms=WAG_A if k % 2 else WAG_B,
           wenkbrauw_op=0.5)

# het bordje
sign_m = S.mat("bord_wit_b", (0.97, 0.96, 0.92))
red_m = S.mat("bord_rood_b", (0.85, 0.12, 0.10))
SIGN = V(28.55, -2.25, 0)
T.cyl("Bord_paal", tuple(SIGN), 0.04, 1.3, S.mat("paal_grijs", (0.5, 0.5, 0.55)), seg=8)
T.box("Bord_rand", tuple(SIGN + V(0, 0, 1.25)), (1.25, 0.05, 0.8), red_m, bevel=0.03)
T.box("Bord_vlak", tuple(SIGN + V(0, 0.01, 1.3)), (1.12, 0.05, 0.7), sign_m, bevel=0.02, ol=0)
T.text("Bord_tekst", "NO SUPER\nSTRENGTH", tuple(SIGN + V(0, 0.05, 1.72)), 0.2, red_m, rot=(90, 0, 180), extrude=0.005)

# rijdende botsauto's: de vriend zit erin en zwaait
cars_b = {k: S.obj(f"Botsauto_{k}") for k in (1, 2, 4, 5)}


def drive(car, t0, t1, pts, spin=0.0):
    """Botsauto (lokaal in de vloergroep) langs punten; draait mee met de rijrichting."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        d = (pts[min(i + 1, n)] - pts[max(i - 1, 0)])
        key(car, t, loc=(pts[i].x, pts[i].y, 0.25), rot=(0, 0, math.degrees(math.atan2(d.y, d.x)) + spin * i / n))


drive(cars_b[2], BUMP - 0.6, QUEUE + 0.2, [(-7.5, -4.6), (-3.5, -4.9), (0.5, -4.4), (3.2, -3.0), (4.6, -0.6)])
drive(cars_b[4], BUMP - 0.6, QUEUE + 0.2, [(6.5, -1.0), (4.0, -2.4), (2.8, -2.6), (1.6, -1.2), (0.0, 0.6)], spin=140)
drive(cars_b[5], BUMP - 0.6, QUEUE + 0.2, [(-2.0, 2.5), (-4.5, 0.8), (-6.5, -1.8), (-6.0, -4.0)])
vriend_b = S.actor("beste_vriend", (0, 0, 0), 0, energy=1.4, label="vriend_bots")
rider = S.extra(3, (0, 0, 0), 0, energy=1.2)
for ch, car in ((vriend_b, cars_b[2]), (rider, cars_b[4])):
    ch.rig.parent = car
    ch.rig.matrix_parent_inverse = Matrix.Identity(4)
    A.place(ch, 1, (-0.25, 0.0, 0.32), 90)
    SITB, _ = sit(ch, seat_top=0.0, lean=-8, spread=0.2)
    S.beat(ch, 0.0, **SITB, pose="ontspannen", face="lach", face_amt=1.0, look=(0.5, 0.2),
           arms=arms(arm("L", (0.1, 0.7, -0.7), (0.0, 1.0, -0.1)), arm("R", (0.1, 0.7, -0.7), (0.0, 1.0, -0.1))))
for k, t in enumerate(frange(BUMP, QUEUE, 0.3)):
    SITB, _ = sit(vriend_b, seat_top=0.0, lean=-8, spread=0.2)
    S.beat(vriend_b, t, **SITB, pose="ontspannen", face="lach", face_amt=1.0, look=(0.8, 0.1), body={"head": (0, 40, 0)},
           arms=arms(arm("L", (0.1, 0.7, -0.7), (0.0, 1.0, -0.1)), WAVE_SMALL_R if k % 2 else WAVE_SMALL_R2), mouth=0.5)

# ---------------------------------------------------------------- de rij voor de Titan: pestkop en zusje
BULLY = V(-9.1, -20.7, 0)
SIS = V(-9.8, -20.65, 0)
pest = S.actor("pestkop", BULLY, -90, energy=1.0)
zus = S.actor("zusje_pestkop", SIS, -90, energy=1.3)
S.beat(pest, 0.0, "armen_over", face="neutraal", face_amt=0.6, look=(0, 0.3))
S.beat(pest, QUEUE + 0.7, "armen_over", face="neutraal", face_amt=0.6, at=V(-2.0, -27.0, 1.3))
S.beat(pest, QUEUE + 1.4, "armen_over", face="grijns", face_amt=0.9, at=V(-2.0, -27.0, 1.3), wenkbrauw_op=0.4)
S.hold(pest, END)
S.beat(zus, 0.0, "staan", face="blij", face_amt=0.9, look=(0, 0.6))
UP_POINT = arm("R", (0.15, 0.55, 0.8), (0.1, 0.5, 0.86))
for k, t in enumerate(frange(QUEUE - 0.3, END, 0.4)):
    S.beat(zus, t, "staan", face="lach", face_amt=1.0, look=(0, 0.8), body={"head": (-24, 0, 0)}, arms=UP_POINT,
           crouch=(0.04 if k % 2 else 0.0, 0), mouth=0.4)

# ---------------------------------------------------------------- camera
fam = lambda t: S.frame_of(held, t)[0]
S.cam(0.0, ((22.0, -38.5, 9.0), (-40.0, -6.0, 20.0), 24), ((21.0, -37.6, 4.6), (-40.0, -6.0, 18.0), 24))
S.cam(PERFECT - 0.1, None, fn=lambda t: (fam(t) + V(-3.4, -0.9, 1.35), fam(t) + V(0.0, 0.25, 1.05), 30))
S.cam(CANDY - 0.1, None, fn=lambda t: (fam(t) + V(-1.25, 0.45, 1.0), fam(t) + V(-0.15, -0.02, 1.08), 42), dof=2.8)
S.cam(BUMP - 0.1, ((27.7, 0.1, 1.05), (26.9, -3.1, 1.2), 28), ((27.5, -0.2, 1.05), (26.9, -3.1, 1.25), 32))
S.cam(QUEUE, ((-5.6, -23.4, 1.25), (-9.3, -20.6, 1.15), 34), ((-6.0, -23.0, 1.25), (-9.3, -20.6, 1.2), 38))

S.finish(length=END)
