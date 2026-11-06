"""D13a · Opgesloten, 2200 (script scène 13a-13i). De witte EVERGREEN-toren, verdieping 200.
13a  WIDE trage push 4,2 s (van buiten): een glazen kamer hoog in de toren, hij zit op een bed; vliegende auto's.
     VO: "By 2200, a company called EVERGREEN has a plan."
13b  DETAIL 2,5 s: hologram van zijn cellen met $40,000,000 PER DOSE.
13c  MEDIUM 4,1 s: de directeur achter het glas, glimlachend.  DIRECTEUR: "Forever is a product. You're the factory."
13d  CLOSE 3,4 + 3,4 s: VO "They want your cells. Every day. Forever. So the richest people on Earth never die."
     Hij kijkt naar het glas, dan naar de deur, kaak strak.
13e  MEDIUM 2,8 s: een bewaker komt binnen met een dienblad. Hij duikt eronderdoor en rent.
     VO: "So you do what any fourteen-year-old would do."
13f  WIDE track 3 s: lange witte gang, alarmlichten worden rood, bewakers achter hem. Gebogen knieën, armen pompend.
13f2 MEDIUM handheld 3 + 2,6 s: de schuifdeur schuift dicht; hij duikt er net door, zijn hoodie blijft hangen en scheurt.
     VO: "You're fast. They're faster. And they've got two hundred floors of security."
13g  MEDIUM 2 s: doodlopend: een enorm raam, 200 verdiepingen boven de stad.
13h  CLOSE 2,5 s: hij kijkt achterom naar de bewakers, dan naar het raam.  JONGEN: "This is gonna hurt."
13i  WIDE slow motion 4 s: hij springt door het raam (grote ronde schilfers); vliegende auto's schieten onder hem door.

    python3 anim/v4/scenes/d13a_toren.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v4 import *  # noqa: E402,F401,F403

S = Scene4("d13a", "toekomst", "toren2200", exposure=0.15)
sh = S.cuts([4.2, 2.5, 4.1, 3.4, 3.4, 2.8, 3.0, 3.0, 2.6, 2.0, 2.5, 4.0])
END = sh[-1][1]
t_b, t_c, t_d, t_d1, t_e, t_f, t_f2, t_f3, t_g, t_h, t_i = (s[0] for s in sh[1:])
for o in bpy.data.objects:
    if o.name.startswith("Personage_marker") or o.name.startswith("Character_marker"):
        o.hide_render = o.hide_viewport = True
Z = 600.0
GY0 = -2.6
EY = GY0 - 30.0                                          # het eindraam
DOOR_Y = GY0 - 14.0                                      # de schuifdeur

# ---------------------------------------------------------------- alarm en deuren
emission_key("alarm_gang", 0.0, 0.0)
for k, t in enumerate(frange(t_f, END, 0.35)):
    emission_key("alarm_gang", t, 9.0 if k % 2 == 0 else 2.5)
emission_key("ganglicht_wit", 0.0, 5.0)
emission_key("ganglicht_wit", t_f, 1.2)
glas = S.obj("Observatieglas")                          # schuift open als de bewaker binnenkomt
key(glas, 0.0, loc=(0.0, -2.55, Z + 0.6))
key(glas, t_e + 0.1, loc=(0.0, -2.55, Z + 0.6))
key(glas, t_e + 0.5, loc=(2.1, -2.55, Z + 0.6))
blad = S.obj("Schuifdeur_blad")
for t, x in ((0.0, 1.3), (t_f2 + 0.4, 1.3), (t_f2 + 2.1, 0.0), (t_f3 + 1.4, 0.0), (t_f3 + 2.2, 1.3)):
    key(blad, t, loc=(x, DOOR_Y, Z))
# stuk hoodie dat aan de deur blijft hangen
lap = T.box("Hoodie_lap", (0, 0, 0), (0.05, 0.06, 0.16), S.mat("jas_lap_wit", (0.91, 0.93, 0.95)), bevel=0.01, ol=0)
lap.parent = blad
lap.location = (-0.72, 0.0, 1.0)
show(lap, t_f2 + 1.65)

# ---------------------------------------------------------------- hij: op het bed, dan ontsnapping
SEAT = V(-0.95, 0.2, Z)
held = S.actor("hoofdpersonage_2200", SEAT, 90)
hs, hz_ = sit(held, seat_top=0.61)
S.place(held, 0, SEAT + V(0, 0, hz_), 90)
REST = arms(arm("L", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)), arm("R", (0.35, 0.15, -0.92), (0.20, 0.75, -0.62)))
GLASS_C = V(0.0, -2.55, Z + 1.4)
S.beat(held, 0.0, **hs, arms=REST, face="verdrietig", face_amt=0.4, at=V(8.0, 4.0, Z + 1.0))
S.beat(held, t_c, **hs, arms=REST, face="boos", face_amt=0.4, at=GLASS_C)
S.beat(held, t_d, **hs, arms=REST, face="boos", face_amt=0.6, at=GLASS_C)
S.beat(held, t_d1 + 0.4, **hs, arms=REST, face="boos", face_amt=0.8, at=V(0.0, -2.6, Z + 1.0))          # naar de deur
S.beat(held, t_d1 + 2.2, **hs, arms=REST, face="zelfverzekerd", face_amt=0.7, at=V(0.0, -2.6, Z + 1.0))
# 13e: staat al (snede), duikt onder het dienblad door
S.teleport(held, t_e, V(-0.45, -0.7, Z), 165)
S.beat(held, t_e, "staan", face="zelfverzekerd", face_amt=0.7, at=V(0.0, -2.6, Z + 1.2), crouch=(0.06, 10))
S.beat(held, t_e + 0.75, "staan", face="inspanning", face_amt=0.9, at=V(0.0, -3.0, Z + 0.8), crouch=(0.22, 30))
STOP = V(0.0, -30.6, Z)
S.run(held, t_e + 0.8, t_f2, [V(-0.45, -0.7, Z), V(0.15, -1.9, Z), V(0.1, -3.4, Z), V(-0.2, DOOR_Y + 3.6, Z)],
      stride=0.8, ease_out=0.0)
S.run(held, t_f2, t_g + 0.9, [V(-0.2, DOOR_Y + 3.6, Z), V(-0.55, DOOR_Y + 0.6, Z), V(-0.5, DOOR_Y - 0.8, Z), STOP],
      stride=0.8, ease_in=0.0, end_rot=0)
S.beat(held, t_f2 + 1.4, "staan", face="inspanning", face_amt=1.0, crouch=(0.12, 24))
S.beat(held, t_f2 + 1.9, "staan", face="geschrokken", face_amt=0.8, body={"head": (0, 60, 0)})       # rukt zich los
S.beat(held, t_g + 1.0, "staan", face="nerveus", face_amt=0.8, at=V(0, EY - 40, Z - 80))
S.beat(held, t_h, "staan", face="nerveus", face_amt=0.9, body={"head": (0, 70, 0)})                    # kijkt achterom
S.beat(held, t_h + 0.9, "staan", face="nerveus", face_amt=0.8, at=V(0, EY - 40, Z - 60))
S.beat(held, t_h + 1.5, "staan", face="zelfverzekerd", face_amt=0.8, at=V(0, EY - 40, Z - 30), crouch=(0.08, 12))
S.hold(held, t_i)
show(held.rig, 0.0, t_i)
A.blink_at(held, F(t_h + 1.1))

# ---------------------------------------------------------------- de directeur achter het glas
dir_ = S.actor("directeur", (0.0, -3.35, Z), 180)
S.beat(dir_, 0.0, "staan", face="grijns", face_amt=0.7, at=S.head(held, 2.0))
S.beat(dir_, t_c, "staan", face="grijns", face_amt=0.9, at=S.head(held, t_c))
S.beat(dir_, t_c + 2.0, "staan", face="zelfverzekerd", face_amt=0.9, at=S.head(held, t_c), body={"head": (0, 0, 6)})
S.hold(dir_, t_e)
show(dir_.rig, 0.0, t_e)

# ---------------------------------------------------------------- bewakers
bw = S.actor("bewaker_a", (0.0, -3.6, Z), 180)
show(bw.rig, t_e - 0.05)
tray = T.box("Dienblad", (0, 0, 0), (0.42, 0.30, 0.02), S.mat("dienblad_wit", (0.92, 0.93, 0.95)), bevel=0.005, ol=0)
cup = T.cyl("Dienblad_beker", (0.08, 0.0, 0.01), 0.035, 0.09, S.mat("beker_groen", (0.25, 0.7, 0.45)), seg=12, ol=0)
cup.parent = tray
grab(S, tray, bw, t_e - 0.05, "hand.R", loc=(-0.12, 0.10, 0.05), rot=(0, 0, 0), release=t_e + 1.0)
TRAY = arms(arm("L", (0.25, 0.55, -0.80), (-0.35, 0.92, 0.10)), arm("R", (0.25, 0.55, -0.80), (-0.35, 0.92, 0.10)))
S.walk(bw, t_e, t_e + 0.8, [V(0.0, -3.6, Z), V(0.0, -2.0, Z)], stride=0.5)
S.beat(bw, t_e, "staan", arms=TRAY, face="neutraal", face_amt=0.5)
S.beat(bw, t_e + 1.0, "schrik", face="geschrokken", face_amt=1.0, at=V(0.2, -4.0, Z + 0.8))
key(tray, t_e + 1.0, loc=(0.0, -2.1, Z + 0.95))
key(tray, t_e + 1.35, loc=(0.1, -2.0, Z + 0.01), rot=(20, 10, 40))                     # dienblad valt
bw2 = S.actor("bewaker_b", (0.6, -5.5, Z), 180)
show(bw2.rig, t_f - 0.05)
for ch, dx, dt in ((bw, -0.3, 0.0), (bw2, 0.5, 0.3)):
    S.run(ch, t_f + dt, t_f2 + 2.2, [S._root_matrix(ch, t_f).translation, V(dx, DOOR_Y + 1.2, Z)], stride=0.9, end_rot=0)
    S.beat(ch, t_f + dt, "staan", face="boos", face_amt=0.9)
    S.beat(ch, t_f2 + 2.3, "staan", face="boos", face_amt=1.0, crouch=(0.04, 10))
    S.run(ch, t_f3 + 2.0, t_h + 2.4, [V(dx, DOOR_Y + 1.2, Z), V(dx, DOOR_Y - 1.0, Z), V(dx * 1.4, -26.5 - dt * 2, Z)], stride=0.9, end_rot=0)
    S.hold(ch, END)
    S.qc_skip.add(ch.name)

# ---------------------------------------------------------------- 13i: de sprong (eigen figuur, draait om de heup)
jh = S.actor("hoofdpersonage_2200", STOP, 0, label="hoofdpersonage_sprong")
show(jh.rig, t_i)
S.qc_skip.add(jh.name)
jb = Body(S, jh, STOP + V(0, 0, 0.7), 0)
for t, p, tl in ((t_i, STOP + V(0, -0.6, 0.65), -20), (t_i + 0.6, V(0, EY + 0.2, Z + 1.2), -35), (t_i + 1.8, V(0, EY - 2.6, Z + 1.7), -55),
                 (t_i + 3.0, V(0, EY - 4.8, Z + 1.2), -70), (END, V(0, EY - 6.6, Z + 0.1), -80)):
    jb.key(t, p, tilt=tl)
S.beat(jh, t_i, "staan", face="inspanning", face_amt=1.0, arms=arms(arm("L", (0.6, 0.6, 0.5), (0.2, 0.9, 0.4)), arm("R", (0.6, 0.6, 0.5), (0.2, 0.9, 0.4))),
       feet=((0.16, -0.30, 0.30), (-0.16, -0.10, 0.10)))
S.beat(jh, t_i + 1.2, "staan", face="schreeuw", face_amt=1.0, arms=arms(arm("L", (0.95, 0.15, 0.25), (0.90, 0.30, 0.30)), arm("R", (0.95, 0.15, 0.25), (0.90, 0.30, 0.30))),
       feet=((0.20, -0.15, 0.12), (-0.20, -0.15, 0.12)))
S.hold(jh, END)
gl = S.obj("Eindraam_glas")
show(gl, 0.0, t_i + 0.55)
sco = S.obj("Eindraam_scherven")
sco.hide_render = sco.hide_viewport = False
show(sco, t_i + 0.55)
key(sco, t_i + 0.55, loc=(0, 1.8, 0.0), scale=0.7)
key(sco, END, loc=(0, -1.2, -1.6), scale=1.0)

# ---------------------------------------------------------------- camera's
for o in [o for o in bpy.data.objects if o.name.startswith("Hologram_cellen")]:     # hologram valt uit bij het alarm
    show(o, 0.0, t_e - 0.1)
S.cam(0.0, (V(12.0, 14.0, Z + 2.5), V(-0.5, 0.0, Z + 1.0), 28), (V(8.5, 10.0, Z + 2.0), V(-0.6, 0.1, Z + 1.0), 28))
S.cam(t_b, (V(0.1, -2.3, Z + 1.55), V(1.0, -0.4, Z + 1.45), 30), (V(0.15, -2.1, Z + 1.53), V(1.0, -0.4, Z + 1.45), 30))
S.cam(t_c, (V(0.35, -0.6, Z + 1.45), V(0.0, -3.35, Z + 1.4), 32), (V(0.3, -0.8, Z + 1.45), V(0.0, -3.35, Z + 1.4), 32))
S.cam(t_d, S.shot(held, t_d + 1.0, size="cu", az=-25, lens=40), S.shot(held, t_d + 1.0, size=0.55, az=-23, lens=40))
S.cam(t_d1, (V(-1.75, 1.0, Z + 1.3), V(0.0, -2.5, Z + 1.1), 30), (V(-1.7, 0.95, Z + 1.28), V(0.0, -2.5, Z + 1.1), 30))
S.cam(t_e, (V(1.9, 0.9, Z + 1.55), V(-0.2, -1.8, Z + 0.9), 26), (V(1.85, 0.8, Z + 1.55), V(-0.1, -2.2, Z + 0.9), 26))
S.cam(t_f, None, fn=lambda t: (S._root_matrix(held, t).translation + V(0.7, -3.6, 1.45),
                               S._root_matrix(held, t).translation + V(0, 1.2, 0.85), 26), handheld=0.12)
S.cam(t_f2, (V(1.0, DOOR_Y - 2.6, Z + 1.2), V(-0.3, DOOR_Y + 0.5, Z + 1.0), 26), (V(0.95, DOOR_Y - 2.5, Z + 1.2), V(-0.3, DOOR_Y, Z + 1.0), 26),
      handheld=0.15)
S.cam(t_f3, None, fn=lambda t: (S._root_matrix(held, t).translation + V(0.6, -3.4, 1.4),
                                S._root_matrix(held, t).translation + V(0, 1.0, 0.85), 26), handheld=0.12)
S.cam(t_g, (V(0.9, -27.6, Z + 2.1), V(0.0, EY - 20, Z - 12), 22), (V(0.85, -27.8, Z + 2.05), V(0.0, EY - 20, Z - 13), 22))
S.cam(t_h, (V(0.25, EY + 0.75, Z + 1.2), STOP + V(0, 0, 1.3), 32), (V(0.22, EY + 0.8, Z + 1.21), STOP + V(0, 0, 1.3), 32))
S.cam(t_i, (V(14.0, EY - 18.0, Z - 6.0), V(0.0, EY - 2.0, Z + 1.0), 22), (V(13.6, EY - 17.5, Z - 6.2), V(0.0, EY - 3.5, Z + 0.8), 22))

# ---------------------------------------------------------------- HUD, stem en geluid
S.year_rattle(2110, 2200, 0.0, 1.0)
S.say("D13-01", at=1.1)
S.say("D13-02", who=dir_, at=t_c + 0.2)
S.say("D13-03", at=t_d + 0.15)
S.say("D13-04", at=t_e + 0.05)
S.say("D13-05", at=t_f2 + 0.1)
S.say("D13-06", who=held, at=t_h + 0.6)
S.sfx("sfx_hologram", t_b, 0.25)
S.sfx("sfx_schuifdeur", t_e + 0.1, 0.3)
S.sfx("sfx_mok_breekt", t_e + 1.35, 0.25)
S.sfx("sfx_alarm_toekomst", t_f, 0.12, loop_to=t_i)
S.sfx("sfx_schuifdeur", t_f2 + 0.4, 0.35)
S.sfx("sfx_raam_breekt", t_i + 0.5, 0.45)
S.sfx("sfx_slowmo", t_i + 0.4, 0.3)
S.ambience("sfx_stroom_zoem", 0.0, t_f, vol=0.06)
S.music("m_spanning_puls", 0.0, END, vol=0.16, fade_in=0.4, fade_out=0.4)
S.finish(length=END, tail=0.0)
