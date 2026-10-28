# Sets voor video 1: "What if you got 2x stronger every day?"

Alle achtergronden, meubels en props voor de 22 locaties uit het script, gebouwd met Python in Blender.
Elke set is één script dat een `.blend` bouwt en per camera een render maakt. De renders en `.blend`-bestanden
staan in de projectmap `sets/` (genummerd in volgorde van de video).

## Stijl

Sinds video 2 renderen alle sets standaard in de **glans-look** (`SET_LOOK=glans`, de standaard): dezelfde
scripts en kleuren, maar in Cycles met glimmende vinyl-materialen met een coatlaag, kleuren iets voller, AgX
"Punchy" en een oranje en blauw randlicht op het hoofdpersonage (alleen op hem, via light linking). Metalen
(materialen met *metaal*, *rvs*, *chroom* ... in de naam) worden echt metaal. Contourlijnen vallen weg.
De node group `ToonLicht` bestaat nog steeds, maar bevat nu een Principled BSDF met de ingangen *Kleur*,
*Ruwheid* en *Metaal*. Met `SET_LOOK=toon` krijg je de oude look van video 1 terug (hieronder beschreven).

Renderen op de pc met de videokaart: `SET_GPU=1`. In de cloudcontainer (alleen CPU) kost een camera op
1920x1080 met 64 samples ~10 minuten; testen met `SET_PCT=25 SET_SAMPLES=24` (~25 s).

### Oude look (video 1, `SET_LOOK=toon`)

- **Toon-shading in EEVEE**: drie lichtbanden (schaduw, midden, licht) via Shader to RGB, matte kleuren, afgeronde randen.
  Render altijd met EEVEE, want in Cycles werkt de toon-shader niet.
- **Contourlijnen**: dunne donkere randen via een Solidify-modifier met de naam `Contour` (inverted hull). Dikte
  aanpassen of uitzetten kan per object in het modifier-paneel.
- **Lichtstemming per set**: de node group `ToonLicht` (in elk materiaal) bevat de lichtbanden (`Lichtbanden`)
  en de waas op afstand (`Waas afstand`). Eén keer aanpassen verandert de hele set.
- **Kleurbeheer**: View Transform staat op *Standard*, zodat de kleuren precies zo uitkomen als ze zijn ingesteld.
- **Hoofdpersonage**: in elke set staat het model uit `hoofdpersonage/hoofdpersonage.glb` als schaal- en stijlreferentie,
  in de collectie *Hoofdpersonage (schaal)*. Zet die collectie uit als je je eigen geanimeerde versie inlaadt.

## Sets

| # | Set | Script en variant | Dagen |
|---|-----|-------------------|-------|
| 01 | Pretpark met achtbaan THE TITAN | `build_pretpark.py zonsondergang` / `dag` | cold open, 16 |
| 02 | Slaapkamer | `build_slaapkamer.py ochtend` / `nacht` | 1, 4 (bureau 's nachts), 7 |
| 03 | Badkamer | `build_badkamer.py` | 1 |
| 04 | Keuken en eettafel | `build_keuken.py ochtend` / `zondagsdiner` | 1, 2, 10 |
| 05 | Straat en woonwijk met het huis | `build_straat.py zonnig` / `avond` / `suvs` / `lente` / `scherven` / `konvooi` | 2, 10, 12, 15, 18, 20 |
| 06 | Gymzaal | `build_gymzaal.py` | 3 |
| 07 | Achtertuin en dak | `build_tuin.py zonsondergang` | 4 |
| 08 | Winkelcentrum en parkeergarage | `build_winkelcentrum.py winkelcentrum` / `parkeergarage` | 5 |
| 09 | Bowlingbaan | `build_bowling.py` | 6 |
| 10 | Supermarkt | `build_supermarkt.py` | 9 |
| 11 | Voordeur en veranda | `build_straat.py avond` (staat in map 05_straat) | 10 |
| 12 | Tv-studio | `build_tvstudio.py` | 11 |
| 13 | Garagewerkplaats van de beste vriend | `build_kleine_interieurs.py werkplaats` | 12 |
| 14 | Dokterspraktijk | `build_kleine_interieurs.py dokter` | 13 |
| 15 | Honkbalstadion | `build_stadion.py` | 14 |
| 16 | Lab met hydraulische pers | `build_lab.py` | 15 |
| 17 | Kelder | `build_kleine_interieurs.py kelder` | 17 |
| 18 | School: klaslokaal en gang | `build_school.py klaslokaal` / `gang` | 19 |
| 19 | Bunker | `build_woestijn.py bunker` | 22 |
| 20 | Woestijnbasis en testterrein | `build_woestijn.py basis_dag` / `testterrein` / `basis_schemer` | 24, 27, 35, 37 |
| 21 | Nachtlucht boven de woestijn | `build_woestijn.py nachtlucht` | 30 |
| 22 | Hangar met drukpak, ruimte en baan om de aarde | `build_ruimte.py hangar` / `ruimte` | 40, outro |

De voordeur en veranda (dag 10) zitten in de straat-set (variant `avond`), de zwarte SUV's (dag 15) in variant `suvs`
en het konvooi met de gezinsauto (dag 20) in variant `konvooi`.

## Sets voor video 2: "What IF You Got 10x FASTER Every Day?"

Alle locaties zijn hergebruik; nieuw zijn de varianten en de props (`lib/huis.py` en onderaan `lib/street.py`).
Renders en `.blend`-bestanden staan in de projectmap `videos/10x-sneller/sets/`.

| Map | Script en variant | Waar in de video |
|-----|-------------------|------------------|
| 00_props | `build_props_10x.py klein` / `voertuigen` | overzicht van alle nieuwe props in de glans-studio |
| 02_slaapkamer | `build_slaapkamer.py ochtend` (glans) / `dag2` / `broertje` | titel dag 1, dag 2 om 06:20 (wekker, glas water), kamer van het broertje (origami, dinoposter) |
| 04_keuken | `build_keuken.py dag1` / `dageraad` / `kraanvogels` / `natuurkundige` / `knal` / `verjaardag` | bijna alles vanaf dag 1 |
| 05_straat | `build_straat.py zonnig` (glans) / `dageraad` / `grijs` | dag 1 bus, dag 2 hardlopen langs de bestelbus en de bus, cold open en dag 3-4 met de vuilniswagen |
| 06_gymzaal | `build_gymzaal.py` (glans) | dag 1, de sprint |
| 07_achtertuin | `build_tuin.py regen` | dag 2, de regen die stilhangt |

Handig voor de animatie:

- **Whiteboard**: elke regel tekst is een eigen object (`Whiteboard_voor_regel1a`, ..., `Whiteboard_achter_regel3`),
  zodat hij letter voor letter of regel voor regel kan verschijnen. De ouder `Whiteboard` draait 180 graden om de
  achterkant te tonen. Lettertype: Permanent Marker (`sets/fonts`, Apache 2.0).
- **Taart**: de vlammetjes heten `Verjaardagstaart_vlam_1..9`; het licht `Verjaardagstaart_kaarslicht`.
- **Kraanvogels**: elke kraanvogel is een los object dat een mesh deelt met de andere van dezelfde kleur
  (`kraanvogel_mesh_0..7`). In `knal` hangen er 1.000 in de lucht; in `verjaardag` liggen er 249 in een krans
  rond de taart en heet de laatste `Kraanvogel_de_laatste`.
- **Vuilniswagen**: koplampen zijn echte spotlampen; voorkant wijst naar +x. Rijdt in `grijs` op y = 1.5 naar het huis.
- **Markeringen** in `straat grijs`: `Markering_broertje_oversteek` en `Markering_stoeprand_dag3` (lege objecten).
- **Regen**: `Regendruppels` (één mesh met ~8.000 druppels) en `Gesplitste_druppel_1/2`.

## Zelf bouwen of aanpassen

```sh
# met Blender (4.2 of nieuwer; gebouwd en getest met 5.2)
blender -b -P sets/build_pretpark.py -- zonsondergang /pad/naar/uitvoer

# of met het Python-pakket bpy
pip install bpy
python3 sets/build_pretpark.py zonsondergang /pad/naar/uitvoer

# meerdere sets na elkaar
sh sets/render_queue.sh "pretpark dag" "straat lente"
```

Handige omgevingsvariabelen:

- `SET_PCT=25` rendert op 25% van 1920x1080 (snel testen)
- `SET_SAMPLES=16` past het aantal EEVEE-samples aan
- `SET_RENDER=0` bouwt en bewaart alleen de `.blend`, zonder te renderen

## Opbouw van de code

- `lib/toon.py`: scène, lichtstemmingen (`MOODS`), toon-materialen, patronen (tegels, planken, schaakbord), contourlijnen,
  basisvormen, camera's, het hoofdpersonage en opslaan/renderen.
- `lib/props.py`: algemene props (bomen, lantaarnpalen, bankjes, auto's, lichtsnoeren, hekken).
- `lib/interior.py`: kamers met muren, ramen, deuren en meubels. De voorste muur blokkeert wel licht, maar de camera kijkt erdoorheen.
- `lib/street.py`: rijtjeshuizen, voortuinen, brievenbus, bushalte, legertruck, helikopter, springkussen, ballonnen.

Elke set zet objecten in duidelijke collecties (bijvoorbeeld *Titan achtbaan*, *Titan trein*, *Reuzenrad*), met
Nederlandse namen, zodat je in de Outliner snel vindt wat je zoekt. De achtbaan heeft een verborgen curve
*Titan_pad (voor animatie)* voor een Follow Path-constraint op de trein.
