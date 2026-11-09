# PROMPT VOOR DE ANIMATOR: 3D-animatievideo's voor het YouTube-kanaal

> Kopieer dit hele document naar de animator (een mens of een AI-agent die Blender via Python bestuurt).
> Alles wat hierin staat is getest in Blender 5.2 op een RTX 4060 Ti, en het levert precies de look op
> van de testvideo's `bram_praattest.mp4`, `bram_loopt.mp4` en `bram_vecht.mp4`.

---

## 0. Jouw rol en opdracht

Je bent de 3D-animator van een Nederlandstalig YouTube-kanaal met longform verhaalvideo's (in de stijl van
"Wat als...?"). Je maakt van een **script + stemopname** een **gerenderde 3D-animatie** met:

1. **Speelgoed/Pixar-achtige look**: glanzende figuurtjes in een zonnige wereld (stenen richel, bolle
   bomen met blaadjes, blauwe lucht met zonnegloed), zachte schaduwen en scherptediepte.
2. **Lipsync**: de mond beweegt automatisch mee met de stem (Rhubarb Lip Sync), met tanden en tong.
3. **Gezichtsuitdrukkingen**: wenkbrauwen, ooggrootte, knipperen, lach/boos-mond, per zin een emotie.
4. **Vloeiende lichaamstaal**: elk gebaar heeft anticipatie, overshoot en squash & stretch, met knikjes op
   de klemtonen in de audio. Luisteraars ademen, knipperen en knikken mee.
5. **Actie**: lopen, draaien, juichen, cartoon-gevechten (kindvriendelijk, niet gewelddadig) en vallen.

Werk **altijd via de Python-scripts** in `scenes/`, niet met de hand in de UI. Zo is elke scène
herhaalbaar en kun je hem in batches renderen.

**Definition of done per scène:** een `.mp4` (1920×1080, 24 fps, H.264 + AAC) mét stem, plus het
bijbehorende `.blend`-bestand. Controleer eerst 3 tot 5 testbeelden (zie §12) voordat je de hele scène rendert.

---

## 1. Benodigdheden (eenmalig installeren)

| Tool | Versie | Waarvoor | Bron |
|---|---|---|---|
| Blender | 5.2 | modelleren, animeren, renderen (Cycles + OptiX) | blender.org |
| Rhubarb Lip Sync | 1.14.0 | audio → mondvormen (JSON) | github.com/DanielSWolf/rhubarb-lip-sync/releases (Windows-zip, ~87 MB) |
| FFmpeg | 7+ | audio omzetten, frames → mp4, stem eronder | `winget install Gyan.FFmpeg` |
| Stem | ElevenLabs (of eigen opname) | Nederlandse voice-over | zie §5 |
| GPU | NVIDIA RTX (OptiX) | renderen | getest: RTX 4060 Ti |

Pad naar Blender (Windows): `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`

---

## 2. Projectstructuur

```
kanaal_animatie/
├─ cast/
│  └─ glans_hoofdpersonage_volledig.blend   ← ALLE personages (nooit overschrijven!)
├─ scenes/
│  ├─ scene_lib.py          ← gedeelde bibliotheek: rig, mond, lipsync, emoties, gebaren, wereld, render
│  ├─ praat_en_beweeg.py    ← SJABLOON: praten + gebaren + emoties + luisteraars (hiermee begin je)
│  ├─ loop_bram.py          ← voorbeeld: looppas, stoppen, draaien, zwaaien
│  └─ vecht_bram.py         ← voorbeeld: cartoon-gevecht met vallen en weer opstaan
├─ audio/
│  ├─ sc012_bram.mp3 / .wav ← stem per scène per personage
│  └─ sc012_bram_mond.json  ← Rhubarb-uitvoer
├─ tools/rhubarb/rhubarb.exe
└─ renders/sc012/f_0001.png ... → sc012.mp4
```

Naamgeving: `scNNN_<personage>` per scène (bijvoorbeeld `sc012_bram.wav`). Eén scène is één shot van 3 tot 15 seconden.

---

## 3. Het cast-bestand: wat zit erin

`glans_hoofdpersonage_volledig.blend` bevat:

- **Collectie `cast`** met 13 personages, elk in een eigen sub-collectie:
  `hoofdpersonage` (= **Bram**), `beste_vriend`, `pestkop`, `zusje_pestkop`, `mama`, `papa`, `broertje`,
  `opa`, `oma`, `gymleraar`, `wetenschapper`, `nieuwslezeres`, `officier`.
  Ze staan standaard allemaal **op de oorsprong** en zijn **uitgesloten** (exclude) in de view layer.
- **Collectie `studio`**: oude camera, lampen en een donker decor. Altijd **uitsluiten**.
- **Collectie `glans_tmp`**: een collection-instance van Bram. Altijd **uitsluiten**, anders zie je hem dubbel.
- **Geen skeletten (armatures).** Elk personage bestaat uit losse mesh-onderdelen onder één lege ouder
  (EMPTY met dezelfde naam als de collectie). Animeren gaat met **draaipunten (empties)**, zie §4.

**Bram** (collectie `hoofdpersonage`, ouder-empty `hoofdpersonage`, onderdelen `Bram_part_0..54`):

| Onderdelen | Wat | | Onderdelen | Wat |
|---|---|---|---|---|
| 0 / 2 | broekspijp links (−x) / rechts (+x) | | 27 | nek |
| 1 / 3 | schoen links / rechts | | 28 | hoofd (bol, middelpunt (0,0,1.47), straal 0.30) |
| 4 | romp (hoodie) | | 29–32 | oren + binnenkant |
| 5 | capuchon | | 33–39 / 40–46 | oog links / rechts (7 platte lagen) |
| 6–11 | koordjes + eindjes | | 47–49 / 50–52 | wenkbrauw links / rechts |
| 12 | buidelzak | | 53 / 54 | oude platte mond + tong (wordt verborgen en vervangen) |
| 13/14/15/16 + `Node_20` | arm links: boven, onder, elleboog, manchet, hand | | 20/21/22/23 + `Node_28` | arm rechts |

Hoogte Bram ≈ 1.77 m, gezicht kijkt naar **−y**.

**Overige personages** hebben leesbare namen: `<naam>_been_L`, `_schoen_R`, `_romp`, `_jas`, `_bovenarm_R`,
`_onderarm_R`, `_elleboog_R`, `_manchet_R`, `_hand_R`, `_duim_R`, `_vingers_R`, `_nek`, `_hoofd`, `_oor_R`,
`_oog_R_*`, `_wenkbrauw_R*`, `_mond`, `_tong`, `_haar`, `_krul0..N`, `_telefoon`...
**Let op:** `_R` ligt bij deze personages aan de **−x**-kant (hun eigen rechterhand). De bibliotheek bepaalt de kant
daarom altijd op basis van de positie (bbox), nooit op basis van de naam.

---

## 4. Het rig-systeem (draaipunten)

`scene_lib.rig_bram()` en `scene_lib.rig_named("<collectie>")` bouwen voor elk personage deze hiërarchie:

```
<personage-empty>          ← positie in de wereld + draaiing (yaw).  rotation_mode MOET 'XYZ' zijn
 └─ _Beweging (mover)      ← hele lijf incl. benen: springen, vallen, op/neer veren, achterover kantelen
     ├─ _HeupGewricht_-1/+1 ← benen + schoenen (zwaaien = lopen/schoppen/zitten)
     └─ _Heup (root, z≈0.64) ← romp: voorover/achterover leunen, squash & stretch (scale)
         ├─ _Schouder_±1 → bovenarm   └─ _Elleboog_±1 → onderarm, manchet, hand
         └─ _Nek (head)    ← houding van het hoofd per zin (kijken, scheef)
             └─ _Knik (nod) ← ALLEEN de automatische knikjes op klemtonen
                 ├─ hoofd, oren, mond, blosjes
                 ├─ _Oog_±1        ← knipperen / ooggrootte (scale z)
                 └─ _Wenkbrauw_±1  ← hoogte (location z) + kanteling (rotation y)
```

**Waarom zo veel lagen?** Elk soort beweging heeft een eigen kanaal, zodat lipsync, knikjes, gebaren,
houding en loopcyclus elkaar nooit overschrijven. Dit is de kern van "praten en bewegen combineren".

### 4.1 Assen en tekens (lokaal per personage; gezicht = −y). DIT ALTIJD AANHOUDEN

| Kanaal | Waarde | Effect |
|---|---|---|
| personage `rotation_euler.z` | 0° / +90° / −90° | kijkt naar camera (−y) / naar +x / naar −x |
| `_Schouder_s` rot X | **negatief** | arm naar voren (−90 = horizontaal vooruit). Positief = naar achteren |
| `_Schouder_s` rot Y | **−s × a** | arm a graden opzij/omhoog (a=90 horizontaal, a≈110 schuin omhoog) |
| `_Schouder_s` rot Z | **−s × a** | arm draait naar binnen (hand naar de borst) |
| `_Elleboog_s` rot X | negatief | onderarm naar voren/omhoog buigen (−95 = horizontaal vooruit) |
| `_Elleboog_s` rot Y | −s × a | onderarm verder omhoog/opzij (bij een geheven arm) |
| `_HeupGewricht_s` rot X | negatief | been naar voren (−85 = zitten, benen gestrekt vooruit) |
| `_Heup` rot X | positief | voorover leunen. Negatief = achterover (ontwijken) |
| `_Beweging` rot X | negatief | hele figuur kantelt achterover (vallen) |
| `_Nek` rot X | negatief | omhoog kijken. Positief = naar beneden (knikje) |
| `_Nek` rot Y / Z | ± | hoofd scheef / draaien |
| `_Wenkbrauw_s` rot Y | −s × tilt | tilt>0 = boos (binnenkant omlaag), tilt<0 = bezorgd/verbaasd |

`s = −1` is de arm/het been aan de −x-kant in rustpose, `s = +1` aan de +x-kant.
Welke arm aan de camerakant zit hangt van de yaw af: bij yaw −90° is dat s=+1, bij yaw +90° is dat s=−1.

---

## 5. Stem maken

**Optie A, eigen opname:** spreek per scène per personage een los bestand in (droog, zonder muziek).
**Optie B, ElevenLabs** (getest): stem *Devin* (`awkQxhhcMytABHFHH3TX`, jong, vriendelijk, Nederlands),
model `eleven_v4`. Kosten ≈ 77 credits (~1,4 cent) per zin van 5–6 s. Geef elk personage een vaste stem.

Zet de audio om naar mono WAV (Rhubarb en de knikjes-detectie verwachten 16-bit PCM):

```bash
ffmpeg -y -i audio/sc012_bram.mp3 -ac 1 -ar 44100 audio/sc012_bram.wav
```

---

## 6. Lipsync met Rhubarb

```bash
tools/rhubarb/rhubarb.exe -r phonetic -f json --extendedShapes GHX -o audio/sc012_bram_mond.json audio/sc012_bram.wav
```

- `-r phonetic` is **verplicht voor Nederlands**: de standaardherkenner is alleen Engels.
- Uitvoer: een lijst `mouthCues` met `start`, `end` en `value` ∈ {A,B,C,D,E,F,G,H,X}.

### 6.1 De mond van Bram (wordt door `rig_bram()` gebouwd)

De oude platte mond (part 53/54) wordt verborgen. Er komt een nieuwe mond voor in de plaats, die over het bolle gezicht
geprojecteerd is: een donkere binnenkant met **boventanden** en een **tong**. Hij heeft 12 vormen (shape keys,
**basis = A = dicht**):

| Vorm | Klank / gebruik | breedte w | boven uh | onder lh | mondhoek | tanden | tong |
|---|---|---|---|---|---|---|---|
| A (basis) | M, B, P (lippen op elkaar) | .044 | .0015 | .0005 | +.006 | 0 | 0 |
| B | K, S, T, EE (tanden op elkaar) | .048 | .004 | .013 | +.006 | .007 | 0 |
| C | E, Æ (half open) | .047 | .007 | .030 | +.005 | .007 | .35 |
| D | AA (wijd open) | .049 | .010 | .048 | +.004 | .008 | .45 |
| E | O, ER (rond) | .034 | .011 | .030 | 0 | .005 | .30 |
| F | OE, W (getuit) | .021 | .008 | .014 | −.001 | 0 | 0 |
| G | F, V (tanden op onderlip) | .044 | .003 | .007 | +.004 | .009 | 0 |
| H | L (tong omhoog) | .047 | .007 | .030 | +.005 | .006 | .85 |
| X | rust: open glimlach (zoals op de originele render) | .050 | .005 | .030 | +.008 | .006 | .45 |
| **Lach** | emotielaag: breder, mondhoeken omhoog | .057 | .0015 | .002 | +.015 | 0 | 0 |
| **Boos** | emotielaag: mondhoeken omlaag | .040 | −.004 | −.006 | −.012 | 0 | 0 |
| **Schreeuw** | actie: wijd open, hoeken omlaag | .046 | .016 | .050 | −.004 | .008 | .40 |

De vormen tellen **op** (relatief aan A): klankvorm + Lach/Boos kunnen tegelijk aan staan.

### 6.2 Zo worden de keys gezet (`scene_lib.lipsync`)

- Per cue twee keys: op `start + 0,75 frame` en op `eind − 0,75 frame`. Bij korte cues één key in het midden.
  Daardoor duurt elke overgang ±1,5 frame: snel genoeg om scherp te ogen, maar zonder geflikker.
- Per key staat de actieve vorm op **0,92**, alle andere klankvormen op 0.
- Audio-offset: frame = `LEAD + seconde × 24 + 1`. Gebruik `LEAD = 10` frames stilte vóór de eerste klank.
- De functie geeft de **zinnen** terug: een stilte X van ≥ 0,3 s scheidt twee zinnen. Daaraan koppel je
  gebaren en emoties.

---

## 7. Gezichtsuitdrukkingen

`scene_lib.emotion(rig, frame, naam, eye_track)` zet wenkbrauwen, de Lach/Boos-mond en de ooggrootte:

| Emotie | wenkbrauw hoogte | kanteling | Lach | Boos | ogen (scale z) |
|---|---|---|---|---|---|
| neutraal | 0 | 0 | .35 | 0 | 1.00 |
| blij | +.010 | −4 | .95 | 0 | 0.85 (lachende ogen) |
| heel_blij | +.020 | −6 | 1.0 | 0 | 0.80 |
| boos | −.005 | +16 | 0 | 1.0 | 1.00 |
| verbaasd | +.020 | −10 | 0 | 0 | 1.15 (grote ogen) |
| bezorgd | +.010 | −15 | 0 | .3 | 1.00 |
| nieuwsgierig | +.012 | −6 | .2 | 0 | 1.05 |
| trots | +.006 | +4 | .8 | 0 | 0.90 |

Regels:
- Zet de emotie **3–4 frames vóór** de zin begint. Het gezicht reageert eerst, daarna komen de woorden.
- Een asymmetrische wenkbrauw (één omhoog) is een sterk "nieuwsgierig"/"wat als"-signaal. Zet daarvoor één
  wenkbrauw-empty apart: +0,016 omhoog en −10° gekanteld, de andere −0,003 en +6°.
- **Knipperen:** in elke pauze tussen zinnen, plus ongeveer elke 3 seconden, en altijd na een schrikmoment.
  Profiel over 5 frames: 1 → 0,85 → 0,4 → 0,05 → 0,4 → 0,85 → 1 (`blink_bake`).
- De ooggrootte en het knipperen worden **per frame gebakken** in één curve (`blink_bake(rig, frames, END, base=eye_track)`).
- Personages zonder mond-shape-keys (iedereen behalve Bram) laten emotie zien via wenkbrauwen, ogen en houding.
  Wil je dat zij ook praten, bouw dan hun mond na met dezelfde functie (`_bram_face` als voorbeeld) op hun
  eigen hoofdmiddelpunt en -straal.

---

## 8. Lichaamstaal en gebaren

### 8.1 Gebarenbibliotheek (`scene_lib.gesture(rig, naam, startframe, s, lengte)`)

Waarden zijn (schouder X,Y,Z) / (elleboog X,Y,Z) in graden, s = kant:

| Gebaar | Wanneer | Sleutelposes (frames na start) |
|---|---|---|
| `zwaai` | groeten, "Hé!" | +6: (−10, −s·100, 0)/(0, −s·38, 0) overshoot → +10: (−8, −s·86, 0)/(0, −s·24, 0), daarna wisselt de elleboog elke 6 frames tussen −s·50 en −s·24 |
| `hand_op_borst` | "ik", "mijn" | +8: (−18, −s·10, −s·28)/(−95, 0, 0) |
| `uitleggen` | uitleg, "stel je voor" | +7: (−8, −s·14, 0)/(−75, 0, 0), daarna elke 7 frames een kleine tel-beweging |
| `armen_omhoog` | climax, juichen, "vliegen!" | +6: (0, −s·25, 0) aanloop → +11: (0, −s·112, 0) overshoot → +15: (0, −s·98, 0) → houden (0, −s·104, 0). Bij arm=0 doen beide armen mee |
| `wijzen` | "daar!", "kijk" | +6: (−84, −s·8, 0)/(−6, 0, 0) |
| `vuisten` | ruzie, vechthouding | (−30, −s·12, 0)/(−115, 0, 0) |
| `handen_in_zij` | eigenwijs, wachten | (0, −s·35, 0)/(−40, s·60, 0) |
| `rest()` | terug naar rust | alles op 0 |

Houding: `body_keys(rig, f, lean, side, dz, squash)` en `head_keys(rig, f, up, tilt, turn)`.

### 8.2 Animatieprincipes (deze getallen werken bij deze figuurtjes)

- **Anticipatie:** 4–6 frames vóór elke grote beweging eerst de andere kant op. Inveren met dz −0,012 en squash 0,975,
  of de arm eerst +5° naar achteren.
- **Overshoot:** een geheven arm gaat 10–15° te ver en veert in 4–8 frames terug.
- **Squash & stretch** (op `_Heup` scale): landing (1,12 / 1,12 / 0,86), afzet (0,97 / 0,97 / 1,04), na 6 frames weer 1.
- **Timing bij 24 fps:** arm heffen 6–10 frames, klap of duw 3–5 frames, terugveren 6–8 frames, emotiewissel 4–6 frames.
- **Nooit stilstaan:** ook een "stil" personage ademt (scale z ±0,006, periode ~2 s) en knippert.
- **Geen botsingen:** houd minstens **1,2 m** tussen personages die naast elkaar staan te gebaren. Een geheven arm
  komt ±0,6 m opzij. Een arm die vlak naast het hoofd omhoog gaat, prikt door het oor; houd de onderarm 15–35° naar buiten.

### 8.3 Lopen (`loop_bram.py`)

Stijve benen (er zijn geen knieën), daarom een omgekeerde-slinger-gang:
- Cyclus `T = 20` frames (2 stappen), beenzwaai `θ = 22°`. Standfase lineair van +θ naar −θ (de voet blijft
  staan), zwaaifase met smoothstep van −θ naar +θ, plus het been 0,05 m optillen (`sin(π·s)`).
- Snelheid = `2 · beenlengte · sin θ` per halve cyclus (≈ 0,98 m/s). Integreer die per frame naar `personage.location`.
- Lijf omlaag: `_Beweging.z = −beenlengte · (1 − cos φ_stand)`, zodat de standvoet precies op de grond blijft.
- Armen tegengesteld aan de benen: `schouder X = +1,1 · φ_zelfde_kant`, elleboog −18° tot −32°.
- Romp 4° voorover, ±4° draaien (Z) op het ritme, knikje van 2° op elke stap.
- Starten en stoppen: amplitude in 10 frames van 0 naar 1 (en terug), met een kleine inveer-landing na het stoppen.
- Draaien: yaw in ±16 frames met 2 kleine stapjes (been 0,04 m optillen).
- Praten tijdens het lopen kan gewoon: lipsync en knikjes zitten op eigen kanalen.

### 8.4 Actie en gevecht (`vecht_bram.py`): kindvriendelijk, slapstick

Draaiboek dat werkt (24 fps):
1. **0–30** vechthouding (`vuisten`), boze wenkbrauwen, beide figuren veren om de 12 frames 0,012 m (in tegenfase).
2. **30–43** aanvaller: uithalen (schouder +35° naar achteren) en uitvallen (−92°, elleboog −4°), romp +14°, 0,18 m naar voren.
   Verdediger: achterover ontwijken (`_Heup` X −30°, lijf −0,05 m), verbaasde ogen en wenkbrauwen, mond E.
3. **43–58** aanvaller verliest zijn evenwicht (romp +24°, struikelstapje met been −26°) en herstelt.
4. **56–66** tegenactie: duw met twee handen (anticipatie +28°, daarna −90°), stap naar voren, mond `Schreeuw`.
5. **66–80** de ander vliegt weg: boog z +0,22 → landt zittend op z −0,62, `_Beweging` X −28° in de lucht,
   benen naar −88°, armen naar achteren (+38°) als steun, squash bij de landing, camera schudt (0,04–0,06 m, 9 frames).
6. **84+** duizelig: hoofd wiebelt met `10° · e^(−t/45) · sin(2πt/16)`, ogen half dicht (0,55).
7. **Afloop:** de winnaar juicht (sprongetje +0,18 m, armen omhoog) en **helpt de ander overeind** (arm −58° vooruit).
   Houd het vriendelijk: geen bloed, geen schoppen tegen iemand die ligt, geen wapens.

---

## 9. Praten en bewegen combineren: het sjabloon `praat_en_beweeg.py`

Dit is het **standaard-startpunt voor elke dialoogscène**. Je past alleen het blok `SCÈNE-INSTELLINGEN` aan:

```python
AUDIO = "audio/sc012_bram.wav"
CUES  = "audio/sc012_bram_mond.json"
LEAD, STAART = 10, 18
SPREKER_POS = (0.32, 0.0, 0.0)
LUISTERAARS = [("beste_vriend", (-0.9, 0.3, 0.0), 32)]      # collectie, positie, yaw
ZINNEN = [   # één regel per zin uit Rhubarb
    dict(emotie="heel_blij",   gebaar="zwaai",        arm=1, hoofd=dict(up=6, tilt=5),  lijf=dict(lean=-2)),
    dict(emotie="nieuwsgierig", gebaar="uitleggen",   arm=1, hoofd=dict(tilt=-8, turn=6), lijf=dict(lean=3)),
    dict(emotie="verbaasd", eind_emotie="heel_blij", gebaar="armen_omhoog", arm=0,
         hoofd=dict(up=9, tilt=3), lijf=dict(dz=0.02, squash=1.03)),
]
CAMERA = dict(van=((0.9, -9.5, 0.75), (-0.15, 0, 0.85)), naar=((0.6, -6.2, 0.9), (0.15, 0, 1.1)))
```

Wat het script automatisch doet, in deze volgorde:
1. Alleen de benodigde personages zichtbaar maken en riggen.
2. Audio-envelop berekenen: **klemtonen** (pieken > 45 %, minstens 7 frames uit elkaar) → knikjes van 3,5° op `_Knik`.
3. Lipsync uit Rhubarb, plus de zinnen detecteren.
4. Per zin: anticipatie 4 frames ervoor, dan emotie, gebaar, hoofdhouding en lichaamshouding. Tussen zinnen
   (pauze > 8 frames) terug naar rust.
5. Knipperen in elke pauze. Ooggrootte volgt de emoties.
6. Luisteraars: ademen, knipperen, knikje aan het eind van elke zin van de spreker, en richting het eind een
   kleine wenkbrauwreactie.
7. Camera: langzaam inzoomen van de "van"- naar de "naar"-positie.
8. **Pas daarna** de buitenwereld bouwen en de render-instellingen zetten.

> **Belangrijk (snelheid):** bouw de wereld (`build_outdoor`) **altijd als laatste**. Als de bomen met
> duizenden blaadjes al bestaan, rekent Blender bij elke keyframe de scène opnieuw door:
> 10 minuten in plaats van 16 seconden voorbereiding.

Gesprek tussen twee sprekers: maak per spreker een eigen WAV en JSON, roep `lipsync()` per personage aan met hun
eigen `LEAD` (het moment waarop ze beginnen te praten), en laat de ander in die tijd de luisteraar-routine doen.
Bram is het enige personage met praatmond-shape-keys; zie §7 als een ander personage ook moet praten.

---

## 10. De look: wereld, licht en camera (`build_outdoor`, `camera`, `render_settings`)

- **Richel:** kubus 11,2 × 5 × 1,6 m met de bovenkant op z=0, voorkant op y=−1. Lichtgrijs steen (170,170,176) met
  een subtiele noise-bump en een bevel van 3 cm.
- **Grond:** grasvlak op z=−1,6 met 4 afgeplatte heuvels in de verte.
- **Bomen:** bol (r 1,9–2,4) met een geometry-nodes-modifier: `Distribute Points on Faces` (dichtheid 75),
  `Instance on Points` met een blad (ellips 0,26 × 0,18), uitgelijnd op de normaal met willekeurige draaiing
  (±0,6 / ±0,6 / ±π) en schaal 0,75–1,3. Bladkleur via `Object Info → Random` tussen (95,170,45) en (175,225,80),
  met subsurface 0,15. Binnenbol donkergroen.
- **Lucht:** world-shader. `Generated.z` (0–0,4) gaat via een ColorRamp van (125,180,240) naar (38,100,205),
  plus een zonnegloed: `dot(richting, (−0.42,0.78,0.46))`, gemapt van 0,78–1 naar 0–1, ^3, opgeteld in (255,236,190).
  Sterkte 0,85.
- **Licht:** zon 4,5 W/m² warm (1,0,88,72), hoek 3°, richting van linksvoor-boven `(−0.6,−0.35,0.72)`.
  Vullicht (area 4 m, 260 W, warm, rechtsvoor). Koel vullicht (3 m, 120 W, links). Randlicht (1,5 m, 250 W, achter).
- **Speelgoed-materialen:** huid subsurface 0,18 + coat 0,3. Hoodie sheen 0,45. Schoenen coat 0,4. Blosjes
  (roze, zachte radiale alpha) op de wangen.
- **Camera:** 50 mm. Totaalshot op ~9,5 m, medium op ~6 m, close-up op ~3,5 m. Iets onder ooghoogte (z 0,75–0,95),
  zodat je tegen het figuurtje opkijkt. Track-To naar een kijkpunt-empty. Scherptediepte f/2,8, scherpgesteld op het
  gezicht van de spreker (empty op `_Knik`).
- **Kleur en render:** Cycles + OptiX, AgX "Punchy", denoise, adaptive sampling, motion blur 0,5, compositor
  `Glare` type Bloom (threshold 0,9, strength 0,35, size 0,6), persistent data aan, 1920×1080, 24 fps.

### Shotgrammatica voor YouTube
- Elke 3–8 s een nieuw shot. Wissel totaal, medium en close-up af. Close-ups bij emotie en clou.
- Langzaam inzoomen (5–15 % per shot) houdt het beeld levend. Camera-schok alleen bij klappen en landingen.
- Spreker op 1/3 van het beeld, met de kijkrichting naar de lege kant.

---

## 11. Renderen en exporteren

```bash
# 1) testbeelden (halve resolutie, 16 samples, ~2–5 s per beeld)
blender.exe -b --disable-autoexec cast/glans_hoofdpersonage_volledig.blend -P scenes/praat_en_beweeg.py -- stills renders/sc012_test

# 2) volledige scène (1080p, 28 samples)
blender.exe -b --disable-autoexec cast/glans_hoofdpersonage_volledig.blend -P scenes/praat_en_beweeg.py -- anim renders/sc012

# 3) frames + stem → mp4  (adelay in ms = LEAD / 24 * 1000; LEAD 10 → 417)
ffmpeg -y -framerate 24 -i renders/sc012/f_%04d.png -i audio/sc012_bram.wav ^
  -filter_complex "[1:a]adelay=417,apad[a]" -map 0:v -map "[a]" -shortest ^
  -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow -c:a aac -b:a 192k renders/sc012.mp4
```

- Het script slaat altijd een **kopie** op als `<scène>.blend`. Het cast-bestand wordt nooit aangepast.
- Gemeten op een RTX 4060 Ti: **8–11 s per frame** (1080p, 28–32 samples, met bomen). Draai nooit twee renders
  tegelijk op dezelfde GPU, want dan wordt alles trager.

### Renderbudget voor longform (belangrijk!)

Een video van 10 minuten is 14.400 frames. Bij ~9 s per frame is dat **±36 uur rendertijd**. Daarom:
- Render 's nachts in een batch (een `.bat` met alle scènes achter elkaar).
- Hergebruik shots: een totaalshot met alleen een luisterende reactie kan vaak twee keer gebruikt worden.
- Zet niet-sprekende achtergrondshots op 16 samples. Denoise vangt het grootste deel op. *Niet gemeten:
  controleer dit eerst met testbeelden.*
- Probeer voor drukke scènes eventueel EEVEE (veel sneller). *Niet getest in deze opzet:* controleer de look
  vóór je ermee doorgaat.

---

## 12. Kwaliteitscontrole (vóór elke volledige render)

Render met `stills` één beeld per zin en controleer:

- [ ] De mond hoort bij de klank (open bij A/AA, rond bij O, dicht bij M/B/P) en is **geen** lange verticale vlek
      (zie valkuil 1).
- [ ] Het personage kijkt de goede kant op (zie valkuil 2).
- [ ] Geen armen door hoofden, oren of andere personages. Voeten staan op de richel en zakken er niet doorheen.
- [ ] De emotie past bij de zin. Het gezicht reageert vóór het woord.
- [ ] Er knippert binnen elke 4 seconden iemand. Niemand staat helemaal stil.
- [ ] Lucht blauw (niet grijs/paars), zonnegloed linksboven, gezicht goed belicht.
- [ ] Scherpte op het gezicht van de spreker.
- [ ] Na de mp4-export: geluid en mond lopen synchroon (eerste klank op frame LEAD+1).

---

## 13. Bekende valkuilen (allemaal al opgelost in `scene_lib.py`, maar weet waarom)

1. **Nieuwe shape keys staan in Blender 5 op waarde 1.0.** Zet ze na `shape_key_add` direct op 0. Anders staan alle
   mondvormen tegelijk aan en krijg je een lange verticale mond.
2. **`hoofdpersonage` gebruikt quaternion-rotatie** (glTF-import). Zet `rotation_mode = 'XYZ'` vóór je
   `rotation_euler` keyt. Anders draait Bram niet en blijft hij naar de camera kijken.
3. **Wereld als laatste bouwen** (§9). Anders wordt de voorbereiding 10× trager.
4. **Herouderen zonder verspringen:** `matrix_parent_inverse = ouder.matrix_world.inverted()` en daarna
   `matrix_basis = oude matrix_world` (functie `reparent`).
5. **Random Value-node** verbergt sockets per datatype: kies sockets op naam én `enabled` (functie `sock`).
6. **Video Sequencer:** in Blender 5 heet het `sequence_editor.strips` (niet meer `.sequences`).
7. **Kanten:** bij de benoemde personages zit `_R` aan −x. Bepaal de kant op basis van de bbox, nooit op de naam.
8. **`Material.use_nodes` / `World.use_nodes`** zijn verouderd in Blender 5. Node-trees bestaan standaard al, dus zet ze niet.
9. **Rhubarb + Nederlands:** altijd `-r phonetic`.
10. **Origineel cast-bestand nooit overschrijven:** sla op met `save_as_mainfile(..., copy=True)`.

---

## 14. Werkwijze per video (stappenplan)

1. **Script → scènelijst.** Knip het script in shots van 3–15 s. Noteer per shot: locatie, personages, wie praat,
   actie (lopen/gevecht/gebaar), emotie per zin en shottype.
2. **Stem** per shot per spreker (§5) → WAV.
3. **Rhubarb** per WAV (§6) → JSON.
4. **Scènescript** maken: kopieer `praat_en_beweeg.py` (dialoog), `loop_bram.py` (lopen) of `vecht_bram.py`
   (actie) naar `scNNN.py` en vul de instellingen in. Combineer gerust: lopen + praten = de loopcyclus uit §8.3
   plus `lipsync()` + `nods()`.
5. **Stills** renderen en controleren (§12). Corrigeer en render opnieuw.
6. **Volledige render** in de nachtbatch, daarna mp4 met stem (§11).
7. **Montage** (buiten Blender): shots achter elkaar, muziek, geluidseffecten (woosh bij een duw, plof bij een landing),
   titels zoals "YEAR 2026".
8. Lever per shot `scNNN.mp4` + `scNNN.blend` aan, met een korte notitie van afwijkingen.

---

## 15. Snelle referentie: start een nieuwe dialoogscène in 5 minuten

```text
1. ffmpeg -i stem.mp3 -ac 1 -ar 44100 audio/sc020_bram.wav
2. rhubarb -r phonetic -f json --extendedShapes GHX -o audio/sc020_bram_mond.json audio/sc020_bram.wav
3. kopieer scenes/praat_en_beweeg.py → scenes/sc020.py
4. pas AUDIO, CUES, ZINNEN (emotie + gebaar per zin), LUISTERAARS en CAMERA aan
5. blender ... -P scenes/sc020.py -- stills renders/sc020_test   → controleren
6. blender ... -P scenes/sc020.py -- anim renders/sc020
7. ffmpeg frames + stem → renders/sc020.mp4
```
