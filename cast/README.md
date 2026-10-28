# Cast van video 1: "What if you got 2x stronger every day?"

Alle bijfiguren zijn gebouwd op het model van het hoofdpersonage
(`hoofdpersonage.glb`). Hoofd, ogen, handen, materialen en belichting zijn dus
precies dezelfde stijl; per figuur verschillen lichaamsbouw, huidskleur, haar,
gezichtsuitdrukking, kleding en accessoires.

## De figuren

| Bestand | Figuur | Stem in het script | Kenmerken |
|---|---|---|---|
| `mama` | Mama | MOM | Paardenstaart met schuine pony, groene ogen, petrol trui, spijkerbroek, gouden oorbelletjes |
| `papa` | Papa (de grappenmaker) | DAD | Volle baard, kuif, buikje, vrolijk blauw hawaïhemd met stippen, kakibroek, brede grijns |
| `broertje` | Broertje (8) | BROTHER | Piekhaar, sproeten, gestreept T-shirt, korte broek, rode sneakers |
| `opa` | Opa (ouderwets, mopperig) | GRANDPA | Flatcap, wit haar opzij, borstelige witte wenkbrauwen, snor, bril, overhemd met das, vest, wandelstok, strakke mond |
| `oma` | Oma (lief, knuffelig) | GRANDMA | Witte krullen met knotje, rond gouden brilletje, blosjes, lila vest, parelketting, lange rok |
| `beste_vriend` | Beste vriend | FRIEND | Krullen, groen T-shirt, rode sneakers, telefoon in de hand (hij filmt alles) |
| `pestkop` | Pestkop | BULLY | Breed en groot, kort stekeltjeshaar, boze wenkbrauwen, scheve grijns, zwart leren jack |
| `zusje_pestkop` | Zusje van de pestkop | (geen tekst) | Klein meisje met twee staartjes en gele strikjes, roze jurkje, suikerspin (pretpark) |
| `gymleraar` | Gymleraar | (geen tekst) | Wijkende haarlijn, snor, blauw trainingspak met witte strepen, fluitje |
| `wetenschapper` | Wetenschapper | SCIENTIST | Knot, zwarte bril, witte labjas met pen en pasje, klembord |
| `nieuwslezeres` | Nieuwslezeres | NEWS | Bob met scheiding, rode blazer, microfoon met zenderblokje |
| `officier` | Legerofficier | OFFICER | Olijfgroen uniform met pet, epauletten, lintjes en riem, strak gezicht |

Het hoofdpersonage blijft naamloos en kaal; de bijfiguren hebben haar zodat ze in
een drukke scène meteen herkenbaar zijn.

## Bestanden (projectmap `cast/`)

- `cast_video1.blend`: alle figuren, elk in een eigen collectie onder `cast`, plus het
  hoofdpersonage als referentie en een studio met licht en camera.
- `glb/<figuur>.glb`: elke figuur los, om in een scène te importeren.
- `renders/00_overzicht_cast.png`: de hele cast naast het hoofdpersonage.
- `renders/NN_<figuur>_drie_kanten.png` en `NN_<figuur>_close-up.png`.

## Opnieuw bouwen of aanpassen

```
blender -b -P cast/build_cast.py -- --base pad/naar/hoofdpersonage.glb --out pad/naar/uitvoer
```

Handige opties: `--only mama,papa` (alleen deze figuren), `--no-render` (alleen
.blend en .glb), `--samples 48`.

Elke figuur is één blok in de lijst `CAST` bovenin `build_cast.py`. Kleuren,
lichaamsbouw (`body`: lengte van benen en romp, breedte, buik, grootte van het
hoofd), kapsel, wenkbrauwen, mond en accessoires zijn daar per figuur in te stellen.

De figuren zijn nog niet geriged, net als het hoofdpersonage. Elk onderdeel (arm,
hand, hoofd) is een los object, dus voor poses en animatie kun je in Blender een
armature toevoegen of de onderdelen aan bones koppelen.

---

# Cast van video 2: "What IF You Got 10x FASTER Every Day?"

De vaste cast van video 1 speelt weer mee (gezin, beste vriend, pestkop, wetenschapper,
gymleraar). Nieuw voor deze video, gebouwd met `build_cast.py --cast 10x` (lijst
`CAST_10X`):

| Bestand | Figuur | Kenmerken |
|---|---|---|
| `broertje_dino` | Broertje in dinopyjama (cold open, dag 4) | Groene onesie met capuchon, dino-oogjes en tandjes, oranje stekels over kruin en rug, lichte buik, staart |
| `bezorger` | Bestelbusbestuurder (dag 2) | Bruin uniform met logo, pet met gele klep, snor |
| `vuilnisman` | Vuilniswagenchauffeur (cold open, dag 4) | Oranje veiligheidshesje met reflectiebanden, muts, snor |
| `klasgenoot_a/b/c` | Klasgenoten in de gymles (dag 1) | Wit gymshirt met schoollogo, donkerblauwe short, elk eigen haar en huid |

De .glb's staan ook in `assets/cast/`, zodat `rig.load("broertje_dino")` ze vindt.

## Glans-look, houdingen en effecten

`cast_10x_poses.py` laadt iedereen geriggd (`anim/lib/rig.py`), zet ze om naar de
glans-look en zet elke figuur in een houding uit het script:

```
python cast/cast_10x_poses.py --out pad/uitvoer [--only papa,kraai] [--samples 64] [--pct 100]
```

Bruikbaar in elke scène via `anim/lib/glans.py`:

- `G.character(ch)`: toon-materialen en contourlijn van een `rig.load()`-figuur omzetten naar glans.
- `G.crow(naam, loc, rot_z, wing=35)`: de kraai (~45 cm, zwart met blauw-paarse weerschijn).
  `G.flap(kraai, frame, hoek)` keyframet de vleugels; voor de cold open één vaste hoek.
- `G.smoke(ch, "foot.L", t0, t1)`: rookpluimpjes van een bot (rokende schoenen, `forearm.R` voor de mouw op dag 5).
- `G.ghosts(ch, frame, offsets)`: snelheidsspoor, doorzichtige gloeiende kopieën achter de figuur.
- `G.studio()`: de donkere glans-studio voor losse stills.
