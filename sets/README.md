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
- **Kraai en vogels** in de straat zijn stilstaande props. De kraai die met zijn vleugels slaat komt uit de cast
  (`anim/lib/glans.py`, `G.crow()`); vervang de set-kraai daarmee als hij moet bewegen.

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

## Video 3: What IF There Were NO RULES?

Alle uitvoer komt standaard in `/mnt/project-files/videos/geen-regels/sets/`. Nieuwe props en stadsonderdelen
staan in `lib/stad.py` (verkeerslichten, reclameborden, gebouwen per blok, lantaarns per blok, fiets met lamp en
jerrycan, slagboom, regelborden, troon, kroon, pillendoosje, HOUSE RULES enzovoort).

| Script | Varianten | Scènes |
|---|---|---|
| `build_stad.py` | `nacht`, `middag`, `ochtend`, `stroom`, `winkelstraat` | 0, 1, 3e-f, 6, 7a-c, 10, 12d-f |
| `build_park.py` | `ochtend`, `dag2`, `dag3`, `jaar1` | 3a-b, 7k, 8g, 9f-g, 18a-c |
| `build_strand.py` | `middag`, `jaar5`, `leeg` | 3c-d, 19d-e |
| `build_snelweg.py` | `snelweg`, `tankstation` | 8b, 12a-c |
| `build_brug.py` | `brug`, `lab_buiten`, `lab_binnen` | 13 |
| `build_stadsplein.py` | `jaar1`, `jaar10`, `middernacht` | 18f, 20, 21 |
| `build_koninkrijk.py` | `ingang`, `troon` | 15e-g |
| `build_props_nr.py` | (overzicht van alle props) | |
| `build_keuken.py` | `nr_diner`, `nr_kaarsen`, `nr_oud` | 4a-d, 10d-k, 11a, 22a |
| `build_slaapkamer.py` | `nr_nacht` (wekker 23:59, seconden schakelbaar) | 4e-g, 5, 6 |
| `build_supermarkt.py` | `nr_normaal`, `nr_leeg` | 3g, 7d-e, 8a |
| `build_straat.py` | `nr_stroomuit`, `nr_vuurkorf`, `nr_slagboom`, `nr_eerste_licht`, `nr_sneeuw` | 0d, 10c3-i, 14, 15a-d, 16, 17 |
| `build_school.py` | `nr_no_school`, `nr_jaar1` | 9, 18d-e |

Schakelbare onderdelen voor de animatie (zichtbaarheid of Emission Strength keyframen):

- reclameborden `Billboard_N_reclame` / `_alarm` (omklappen naar rood), schermen op het plein `Scherm_N_tekst_test/_result/_phase`
- verkeerslichten: materialen `VKL_*_rood/_oranje/_groen` (0 = uit, ~9 = aan)
- stroomuitval per blok: materialen `ramen_A`..`ramen_H` en `lantaarn_A`..`H`, lampen in collectie `Lantaarnlicht_A`..`H`
- slagboom-arm `Slagboom_arm` (rotation y), dekseltjes `Pillendoosje_opa_deksel_MON`..`SUN`, laatjes `Apotheek_la_N`
- prijsbord `Prijsbord_prijs_oud` / `_nieuw` (1.89 naar 18.90), wekker `Wekker_sec_57`..`00`

Kwaliteitscheck: `toon.finish` waarschuwt nu als een camera in een groot object staat (`WAARSCHUWING: camera ... staat in object ...`).
Snel testen: `SET_PCT=40 SET_SAMPLES=12 SET_MAXCAMS=1` (alleen de eerste camera). Teksten op borden gebruiken
Inter Display Bold (`fonts/`, OFL) en worden in de .blend ingepakt.

## Video 4: What IF You Could Never Die?

Alle uitvoer komt standaard in `/mnt/project-files/videos/nooit-dood/sets/`. Nieuwe props en decorstukken staan in
`lib/nooitdood.py` (opa's zakhorloge, horlogedoosje, oude foto, politiepenning, rolstoel, eik per seizoen, banken,
glazen torens, vliegende auto, grazer, kolonieschip, loopplank, sterrenveld, sterrenstelsel, zwart gat).

| Script | Varianten | Scènes |
|---|---|---|
| `build_heuvel.py` | `2032`, `2051`, `2086`, `2110`, `3026`, `ijs`, `1mln`, `dood`, `super`, `zout` | 0, 2, 11-12, 15-19 (vaste tijdsprong-plek) |
| `build_toekomst.py` | `toren2200`, `straat2200`, `museum` | 13, 14b |
| `build_ruimte_nd.py` | `sterren`, `aarde`, `rode_reus`, `zwarte_gaten`, `donker` | 1d-f, 19a2, 19g, 20-22 |
| `build_kleine_nd.py` | `schuur`, `skate`, `club`, `bruiloft`, `brand`, `vliegtuig`, `maisveld` | 4, 6, 8, 9, 10 |
| `build_props_nd.py` | `horloge` (vier toestanden), `overzicht` | |

De heuvel heeft in elke variant dezelfde camera `CAM_HEUVEL` (zelfde plek en lens), zodat een harde cut tussen
tijdperken werkt. De hoofdpersoon is in elke set een stand-in voor schaal; de juiste tijdperk-variant komt uit de cast.

Schakelbare onderdelen voor de animatie:

- zakhorloge: `<naam>_klep` (rotation y, 0 = dicht, -160 graden = open), wijzers `_wijzer_uur/_min/_sec`, kroon `_kroon`,
  ketting `_ketting`; `_barst` en `_rijp` (zichtbaarheid); materialen `<naam>_lume` en `<naam>_gravure` (Emission Strength)
- oude foto: nodes `Vergeling` en `Verbleking` (0..1); de foto zelf is `00_props/gezinsfoto_14e_verjaardag.png`
- sterrenveld: node `Sterren uit` in `Sterrenveld_mat` (0..1 zet de sterren één voor één uit); `Laatste_ster_gloed`,
  `Zwart_gat_N_ring` en `Lichtpuntje_gloed` (Emission Strength); `Stelsel_N` (location)
- dode aarde: `Vuurmuur` (scale x/y van 1 naar ~0.01 = de vuurmuur komt op hem af); eclips: `Maan` (location),
  zonlicht keyframen van 1.2 naar 0.3 tijdens de verduistering
- toren 2200: `Schuifdeur_blad` (location x, 0 = dicht), materiaal `alarm_gang` (rood alarm), `Eindraam_glas` /
  `Eindraam_scherven` (wisselen bij de sprong)
- kolonieschip: `<naam>_vlam` (Emission Strength), `Loopplank_plank` (rotation x)

Let op: een render in de cloud met de bloom-compositor heeft `libegl1 libgl1 libegl-mesa0 libgles2` nodig.
`check_cameras` meldt bij de heuvel "camera staat in Heuvel_grond"; dat komt door de bounding box van het terrein en
mag je negeren.
