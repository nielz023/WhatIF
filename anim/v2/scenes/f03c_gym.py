"""F03c · Dag 1 · 1x · gymzaal. De sprint: zijn beste vriend wint, hij komt als laatste binnen.
Vriend: 'Race you tomorrow?' Pestkop: 'Nice run, Snail.'

    blender -b -P anim/v2/scenes/f03c_gym.py -- [--render] [--stills auto] [--pct 25]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from v2 import *  # noqa: E402,F401,F403

S = Scene2("f03c", "gymzaal")

for o in bpy.data.objects:
    if o.name.startswith(("Klaptafel", "Klapstoel")):
        o.hide_render = True

FIN = 6.0                                      # finishlijn bij x = 6 (zaal loopt van x = -14 tot 14)
T.plane("Finishlijn", (FIN, 0, 0.006), (0.14, 6.2), S.mat("finishtape", (0.98, 0.98, 0.95)))
for k, y in enumerate((-3.25, 3.25)):          # pionnen aan weerszijden van de finish
    T.cyl(f"Pion_{k}", (FIN, y, 0), 0.14, 0.4, S.mat("pion", (1.0, 0.45, 0.05)), r2=0.02, seg=16, ol=0)
LANES = [-2.4, -1.2, 0.0, 1.2, 2.4]           # y van de banen
# (figuur, baan, start-x, aankomsttijd)
# (de scène begint midden in de sprint: wie voor ligt, staat verder naar voren)
RUN = [("beste_vriend", 2, -5.0, 2.0), ("klasgenoot_a", 0, -6.0, 2.9), ("pestkop", 3, -6.0, 3.1),
       ("klasgenoot_b", 4, -7.0, 3.4), ("hoofdpersonage", 1, -12.0, 4.6)]

# ---------------------------------------------------------------- tijdlijn
S.hud2(1, "1x", clock=clock(10 * 3600 + 14 * 60, 1.0, hhmm=True, day="MON"), t0=0.25)
S.sfx("sfx_fluitje", 0.05, 0.45)
S.ambience("sfx_klas_geroezemoes", 0.0, 20, vol=0.10)
ARRIVE = 4.6
l1 = S.say("F03-08", at=ARRIVE + 0.9)
fr = {}
l2 = S.say("F03-09", gap=0.25)
l3 = S.say("F03-10", gap=0.3)
l4 = S.say("F03-11", gap=0.25)
END = l4[1] + 0.7
S.music("piano_warm", 0.0, END + 1, vol=0.15, fade_in=0.3, fade_out=0.6, start=6.0)

HP = V(FIN + 1.2, -1.2, 0)                      # hier komt hij tot stilstand
# na de finish lopen ze uit tot een halve kring om hem heen (ruim uit elkaar: grote hoofden)
STOPS = {"beste_vriend": V(FIN + 2.8, 0.1, 0), "klasgenoot_a": V(FIN + 3.4, -3.0, 0), "pestkop": V(FIN + 1.3, 1.7, 0),
         "klasgenoot_b": V(FIN + 3.6, 2.4, 0), "hoofdpersonage": HP}
cast = {}
for k, (name, lane, x0, tarr) in enumerate(RUN):
    p0 = V(x0, LANES[lane], 0)
    ch = S.actor(name, p0, 90)
    cast[name] = ch
    S.beat(ch, 0.0, "staan", face="inspanning", face_amt=0.6)
    stop = STOPS[name]
    if name == "hoofdpersonage":
        S.run(ch, 0.0, tarr, [p0, stop], stride=0.8, lift=0.13, lean=8, ease_in=0.05, ease_out=0.3)
    else:
        S.run(ch, 0.0, tarr, [p0, V(FIN + 0.6, LANES[lane], 0), stop], stride=1.1, lift=0.2, ease_in=0.05, ease_out=0.25)
held, vriend, pest = cast["hoofdpersonage"], cast["beste_vriend"], cast["pestkop"]
gym = S.actor("gymleraar", V(FIN - 1.2, -4.8, 0), 0)
kc = S.actor("klasgenoot_c", V(FIN - 0.4, 3.6, 0), 150)

# lipsync na het rennen
A.lipsync(vriend, voice_file("F03-08"), F(l1[0]), gain=1.2)
A.lipsync(pest, voice_file("F03-10"), F(l3[0]), gain=1.2)

# ---------------------------------------------------------------- na de finish
S.beat(held, ARRIVE + 0.05, "staan", face="inspanning", face_amt=0.9, crouch=(0.12, 30), body={"head": (-20, 0, 0)},
       arms=arms(arm("L", (0.25, 0.75, -0.6), (0.0, 0.2, -0.98)), arm("R", (0.25, 0.75, -0.6), (0.0, 0.2, -0.98))))
for k, t in enumerate((ARRIVE + 0.5, ARRIVE + 1.1, ARRIVE + 1.7, ARRIVE + 2.3, ARRIVE + 2.9)):   # hijgen
    A.key_prop(held.rig, "mond_open", 0.55 if k % 2 == 0 else 0.25, F(t))
S.beat(held, l1[0] + 0.3, "staan", face="nerveus", face_amt=0.7, at=S.head(vriend, l1[0]), crouch=(0.1, 26),
       arms=arms(arm("L", (0.25, 0.75, -0.6), (0.0, 0.2, -0.98)), arm("R", (0.25, 0.75, -0.6), (0.0, 0.2, -0.98))))
S.beat(held, l2[1] - 0.4, "handen_zij", face="verdrietig", face_amt=0.5, at=S.head(vriend, l1[0]), crouch=(0.04, 8))
S.beat(held, l3[0] + 0.6, "handen_zij", face="boos", face_amt=0.4, at=S.head(pest, l3[0]))
S.beat(held, l4[0] + 0.6, "ontspannen", face="verdrietig", face_amt=0.8, look=(0, -0.5), body={"head": (16, 0, 0)})
S.hold(held, END)

VP = STOPS["beste_vriend"]
S.turn(vriend, 2.3, 2.9, heading(VP, HP))
S.beat(vriend, 2.4, "juichen", amount=0.7, face="lach")
S.beat(vriend, 3.6, "handen_zij", face="blij", at=HP + V(0, 0, 1.0))
S.beat(vriend, l1[0], "wijzen", amount=0.5, face="grijns", face_amt=0.8, at=S.head(held, ARRIVE))
S.beat(vriend, l1[1] + 0.3, "handen_zij", face="lach", face_amt=0.7, at=S.head(held, ARRIVE))
S.hold(vriend, END)

PP = STOPS["pestkop"]
S.turn(pest, 3.4, 4.0, heading(PP, HP))
S.beat(pest, 3.6, "armen_over", face="zelfverzekerd", at=HP + V(0, 0, 1.0))
S.beat(pest, l3[0] - 0.2, "wijzen", face="grijns", at=S.head(held, ARRIVE))
S.beat(pest, l3[1] + 0.2, "armen_over", face="grijns", face_amt=0.8, at=S.head(held, ARRIVE))
S.hold(pest, END)
for name in ("klasgenoot_a", "klasgenoot_b"):
    ch = cast[name]
    S.beat(ch, 3.8, "handen_zij", face="blij", face_amt=0.5, at=HP + V(0, 0, 1.0))
    S.beat(ch, l3[1], "staan", face="lach", face_amt=0.8, at=S.head(held, ARRIVE))
    S.hold(ch, END)
S.beat(gym, 0.0, "wijzen", face="schreeuw", face_amt=0.6, at=V(FIN - 8, 0, 1.0))
S.beat(gym, 2.0, "staan", face="neutraal", at=V(FIN, 0, 1.0))
S.beat(gym, ARRIVE, "staan", face="twijfel", face_amt=0.5, at=S.head(held, ARRIVE))
S.hold(gym, END)
S.beat(kc, 0.0, "juichen", amount=0.6, face="blij", at=V(FIN - 6, 0, 1.0))
S.beat(kc, l3[1], "staan", face="lach", face_amt=0.6, at=S.head(held, ARRIVE))
S.hold(kc, END)

# ---------------------------------------------------------------- camera
S.cam(0.0, ((FIN + 5.0, -5.0, 1.3), (FIN - 8.0, 0.3, 0.8), 30), ((FIN + 4.6, -4.6, 1.3), (FIN - 4.0, 0.0, 0.8), 30))
S.cam(2.6, ((FIN + 0.2, -6.2, 1.0), (FIN - 1.0, -1.0, 0.8), 26), ((FIN + 0.6, -6.0, 1.0), (FIN + 1.0, -1.0, 0.8), 28))
S.cam(l1[0] - 0.15, S.ots(held, vriend, ARRIVE + 0.5, lens=36, side=-1, back=1.5, out=1.0, rise=0.2))
S.cam(l2[0] - 0.05, S.ots(vriend, held, l2[0], lens=34, side=-1, back=1.5, out=0.75, rise=0.1), S.ots(vriend, held, l2[1], lens=38, side=-1, back=1.4, out=0.72, rise=0.1))
S.cam(l3[0] - 0.15, S.ots(held, pest, l3[0], lens=36, side=-1, back=1.5, out=0.75, rise=0.2))
S.cam(l4[0] + 0.3, ((FIN + 6.5, -3.5, 1.6), (FIN + 1.8, 0.0, 0.8), 28), ((FIN + 6.2, -3.3, 1.6), (FIN + 1.6, -0.2, 0.8), 30))

S.finish(length=END)
