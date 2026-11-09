# Script video 5: What IF You Could See How Many Days Everyone Has Left?

Versie 1.1, 9 november 2026: revisie op de feedback van niels (zie "Wat is er nieuw in v1.1"). Gebaseerd op het onderwerpenonderzoek van 9 nov (`ideeen/onderwerpen_onderzoek_9nov.md`), het productiehandboek, de cursusregels en alle lessen en fouten uit video 1-4.

- **Lengte:** ongeveer 14:15 (de som van alle shotlengtes), circa 1.330 gesproken woorden (voice-over plus dialoog). In v1.0 stond 11:50, maar daar pasten veel zinnen niet in hun shot. In v1.1 is elk shot getimed op 2,6 woorden per seconde + 0,6 s uitloop (zie G.9), daardoor is de video eerlijker en langer.
- **Taal:** alles wat gesproken of op beeld getoond wordt is Engels. Regie, shots en bewegingen staan in het Nederlands.
- **Kern:** op een ochtend ziet hij boven ieders hoofd een getal: hoeveel dagen die persoon nog heeft. Eerst grappig, dan heldhaftig, dan gevaarlijk, dan onomkeerbaar.
- **Emotionele lijn:** opa heeft 34 dagen, en dat getal beweegt niet, wat hij ook doet.
- **Twist:** opa kon de getallen zelf ook zien, zijn hele leven al. Elk getal dat je verandert, betaal je met dagen van jezelf. Daarom was opa's getal zo laag: hij heeft zijn jaren weggegeven, te beginnen met oma. Slotbeeld: zijn broertje kan ze nu ook zien, en kijkt naar het getal boven zíjn hoofd.
- **Toon:** geen bloed, geen geweld, geen lijken in beeld. Opa sterft vredig buiten beeld (lege stoel). Ongelukken worden altijd nét voorkomen.

---

## Hoe je dit script leest

Elke scène heeft een kop met set, tijd, HUD, licht en geluid, gevolgd door genummerde shots:

`3a · MEDIUM · push-in · 3,5 s` = shot 3a, medium framing, trage camera naar voren, 3,5 seconden.

Framings: **WIDE** (hele set), **MEDIUM** (heup tot hoofd), **CLOSE** (gezicht), **DETAIL** (hand of prop). Geen over-the-shoulder met een achterhoofd vlak voor de lens; minstens 0,75 m tot elk hoofd (chibi-hoofden zijn 60 cm).

- **Beweging:** wat elk personage doet, in volgorde, met tijden binnen het shot waar dat belangrijk is.
- **VO:** voice-over (de vaste vertellerstem).
- **NAAM:** dialoog.
- **SFX / Muziek:** geluid.
- **Let op:** shot-specifieke valkuilen (clipping, contact, set).

Alle algemene bewegings- en kwaliteitsregels staan in **Bijlage G** en gelden voor elk shot zonder dat ze per shot herhaald worden. De animatiethread leest Bijlage G vóór de eerste scène.

---

## Stem (regel van niels, 9 nov)

**Nooit fluisteren**, niet bij de verteller en niet bij personages. Wel expressief met de stem werken: tempo, pauzes, warmte, spanning, een brok in de keel. Waar het script "rustig" of "warm" zegt, betekent dat: gewone stemsterkte, alleen langzamer en zachter van toon. In ElevenLabs geen [whispers]-tags gebruiken.

## De getallen (belangrijkste visuele element)

- **Wat:** boven het hoofd van elk levend wezen zweeft een getal: de dagen die het nog heeft. Mensen, de kraai, de hond van de buren, de goudvis.
- **Stijl:** dezelfde ronde, vette letter als de HUD. Wit met een zachte gloed (emissie 2, bloom aan) en een dunne donkere rand, zodat het op elke achtergrond leesbaar is. Grote getallen met komma's: `25,550`.
- **Kleur:** 100 of meer = wit. 10-99 = amber. 0-9 = rood, met een trage puls (1 per seconde, schaal 1,0 → 1,06 → 1,0). **Nooit flikkeren.**
- **Plek:** 22 cm boven de kruin, gecentreerd, hoogte van de cijfers 14 cm (bij volwassenen en kinderen hetzelfde). Altijd naar de camera gedraaid.
- **Techniek (verplicht):** een 3D-tekstobject per personage, niet in de compositor. Positie volgt het hoofdbot via een gesmoothde volger (zie G.7), rotatie via Track To naar de actieve camera. Het getal mag niet schokken, trillen of achterlopen. Bij snelle hoofdbewegingen loopt het hooguit 2 frames na.
- **Wanneer:** vanaf het moment dat hij ze ziet (scène 3a) in elk shot waar hij aanwezig is of waar het verhaal ze nodig heeft. In flash-forwards en de cold open ook.
- **Hijzelf:** boven zijn eigen hoofd staat nooit iets, ook niet in een spiegel. Alleen in het allerlaatste shot (scène 19) zien we via het broertje dat er bij hem wél iets staat, en dat getal tonen we niet.
- **Verandering:** als iemands toekomst verandert, rolt het getal als een gokkast-teller naar het nieuwe getal (0,8 s, ease-out), met een zachte "tik-tik-tik". Nooit een harde wissel.
- **Middernacht:** om 00:00 springen alle getallen één omlaag met een korte zachte pop (alleen getoond in scène 7 en 15).

## HUD

- **Teller rechtsboven:** `DAY 1`. Wit met donkere rand, zelfde letter. Springt bij een nieuwe dag met een korte pop (schaal 1,0 → 1,15 → 1,0 in 8 frames).
- **Klok:** alleen in scène 0 en 18 een extra regel eronder: `3:58 PM`, die echt doortelt.
- **Geen HUD** in de flash-forwards, de titelkaart, de brief van opa (17c-17h) en het slotbeeld.
- De teller loopt nooit achteruit tussen scènes. De cold open is een flash-forward naar DAY 41 en toont `DAY 41`.
- HUD en getallen botsen nooit: geen getal boven een hoofd in de rechterbovenhoek van het beeld (kadreer zo dat hoofden onder de HUD blijven, check TEKST_ONDER_HUD).

## Wat is er nieuw in v1.1

Alles wat werkte blijft: het concept, de cold open, opa met 34, de hartslag, de brief, de keuze bij het kruispunt en het broertje. De uitvoering is aangescherpt op de 13 punten van niels' checklist:

| # | Checklistpunt | Wat er veranderd is |
|---|---|---|
| 1 | Regels van de kracht logisch en consequent | Nieuwe sectie "De regels van de kracht": zes regels, elk eerst als beeld, daarna pas benoemd. Nieuwe regel 4 (*de getallen zijn een voorspelling*) verklaart waarom getallen soms vanzelf dalen (pestkop, school, vriend), en regel 5 (*een moment, geen klok*) waarom opa niet te redden is. |
| 2 | Kosten van elke redding subtiel opgebouwd | Vaste trap van de hartslag: 8h één overslag, 9b twee overslagen, 9d3 moet hij gaan zitten, 13k zakt hij in elkaar. Hij verklaart het steeds weg ("probably nothing", "the running", "stress"). Opa ziet het en reageert (9g, 14e). |
| 3 | Opa's geheim maximale impact | Eerdere aanwijzingen: dezelfde hand-op-de-borst als de jongen (9g), "plenty of time" bij het visje (10h), de foto van het meisje op de fiets (15d), "Go easy on that heart" (14e). De brief heeft meer ruimte (6 shots, stiltes ertussen) en verklaart waarom zijn getal zo laag was. |
| 4 | Tijdlijn van opa's laatste dagen klopt | Nieuwe sectie "Getallen-tijdlijn". Elk shot in scène 15 heeft nu een eigen DAY-teller. Nieuw persoonlijk moment (16a2: de knoop lukt eindelijk) en een zachte overgang naar de begrafenis (16g). |
| 5 | Elke redding een eigen functie | Man in pak = ontdekken. Montage = zelfvertrouwen. Pestkop = iemand redden die je niet mag + regel 4. Gymzaal = veel mensen tegelijk, kan niet alleen. Vriend = bewuste keuze met open ogen. |
| 6 | Schoolplein-ramp geloofwaardig | Nieuw onderzoek (11e-11h): emmer onder een lek, waterplek, conciërge over verstopte afvoeren, weerbericht + agenda. De directeur heeft nu een echte reden: keuring in maart, en "a feeling" is geen bewijs. |
| 7 | CTA onderbreekt de emotie niet | De tekening krijgt zijn eigen moment zonder stem. De oproep (18 woorden) komt daarna op een rustig shot. |
| 8 | Laatste twist subtiel voorbereid | Het broertje kijkt drie keer kort naar iets boven een hoofd (3c, 9e2, 17a), zonder uitleg. In de brief: "It skipped your father. It didn't skip you." Het slot is één zin. |
| 9 | Getallen, dagen en tijden gecontroleerd | Fouten uit v1.0 hersteld: kraai (2 → 1 → 0), baby en oude man (eerst 0), vriend op DAY 10 (3, niet 2), papa op DAY 11. Zie "Getallen-tijdlijn". |
| 10 | Voice-overs passen in de shots | Elk shot is opnieuw getimed: woorden ÷ 2,6 per seconde + 0,6 s uitloop. 94 shots waren te kort en zijn verlengd (afgerond op 0,5 s); de video is daardoor 14:15 in plaats van 11:50. Lange praatshots (> 6 s) staan in G.9. |
| 11 | Engelse dialogen natuurlijk | Zinnen nagelopen en waar nodig korter en spreektaliger gemaakt. |
| 12 | Animaties en camera haalbaar | Emotionele shots staan stil (geen camerabeweging). Nieuwe bijlage J met proefshots vóór de productie en een vaste kwaliteitscheck per shot. |
| 13 | Begin, midden en finale houden de aandacht | Cold open ingekort tot één zin per shot. In het midden elke 60-90 s een nieuwe vraag (zie bijlage I). Finale: de keuze wordt hardop gemaakt, en het slot is stil. |

## De regels van de kracht (vast, in deze volgorde)

De kijker leert elke regel eerst door wat hij **ziet**, en pas daarna hoort hij hem. Er komt na scène 10 geen nieuwe regel meer bij: de brief (scène 17) bevestigt alleen wat de kijker al heeft gezien.

| Regel | Eerst gezien | Benoemd |
|---|---|---|
| 1. Alles wat leeft heeft een getal: de dagen die het nog heeft. | goudvis, broertje (3a-3c) | 3d |
| 2. Je eigen getal zie je nooit, ook niet in een spiegel of op een foto. | 1d, 6a | 6a |
| 3. Je kunt een getal veranderen door te veranderen wat er gebeurt. | 8d-8f | 8f |
| 4. Het getal is een voorspelling, geen lot. Verandert de toekomst, dan verandert het getal, soms ineens. | het getal van de pestkop zakt live naar 0 (9d1) | 9d1 (terug in 11a en 18a) |
| 5. Een ongeluk is een moment, en daar kun je voor springen. Ouderdom is een klok, en die kun je niet tegenhouden. | opa's getal beweegt niet (10-0, 10c) | opa 10f ("Some numbers aren't a problem to fix"), brief 17f2 |
| 6. Elk getal dat je verandert, betaal je met dagen van jezelf. | hartslag 8h → 9b → 9d3 → 13k | brief 17f (bevestiging) |

**Hartslag-trap (de prijs, steeds iets erger):**

| Redding | Wat hij voelt | Wat hij denkt (VO) |
|---|---|---|
| 8 man in pak | 1 overslag, 0,5 s grimas | "Probably nothing." |
| 9a kinderwagen (9b) | 2 overslagen, hij stopt even en ademt uit | "You tell yourself it's the running." |
| 9d1-9d2 pestkop (9d3) | 3 overslagen, hij moet in het gras gaan zitten, hand trilt | "This time you have to sit down." |
| 13 gymzaal, 300 mensen (13k) | hartslag te snel, hij zakt door zijn knieën | — (dokter in 14a: "Probably stress.") |
| 18 vriend (18k) | twee enorme slagen, dan rust | "Worth it." |

## Getallen-tijdlijn (continuïteit, verplicht aanhouden)

Elk getal daalt om middernacht met 1. Daarbuiten verandert een getal **alleen** door een redding (rolt omhoog) of doordat de toekomst verandert (rolt omlaag, regel 4). Elke verandering is in beeld te zien of wordt uitgelegd.

| Wie | DAY 1 | Verloop |
|---|---|---|
| **Opa** | 34 | Verandert nooit anders dan om middernacht: DAY 7 = 28 · DAY 8 = 27 · DAY 14 = 21 · DAY 16 = 19 · DAY 17 = 18 · DAY 20 = 15 · DAY 22 = 13 · DAY 24 = 11 · DAY 26 = 9 · DAY 28 = 7 · DAY 32 = 3 · DAY 33 = 2 · DAY 34 = 1 · **DAY 35 = 0** (de laatste avond; hij sterft die nacht). DAY 36: lege stoel. DAY 40: begrafenis. 34 dagen na de eerste ochtend, precies. |
| **Beste vriend** | 25,550 | −1 per nacht. DAY 9: valt naar **4** (de school). DAY 10 = 3 · DAY 11 = 2 · DAY 12 = 1 · DAY 13 = 0 → na de redding **25,538**. DAY 41: 25,510 → valt in 18a live naar **0** → na de redding weer **25,510**. |
| **Pestkop** | 25,915 | DAY 7: zakt live naar **0** als hij de helling af gaat (9d2) → na de redding **25,909**. DAY 9: 4 (de school). DAY 13 na de redding: **25,903**. |
| **Man in pak** | — | DAY 5: 0 → **14,611**. DAY 19: 14,597. |
| **Kraai** | 2 | DAY 2 = 1 · DAY 3 = 0 (om middernacht, 7b). |
| **Goudvis** | 212 | |
| **Mama** | 17,840 | DAY 14 = 17,827. |
| **Papa** | 15,226 | DAY 11 = 15,216. |
| **Oma** | 6,102 | DAY 40 = 6,063. |
| **Broertje** | 29,931 | |
| **Hele school** (300) | verschillend | DAY 9: iedereen **4** · DAY 10 = 3 · DAY 13 = **0** → na de ramp de eigen getallen terug. Directeur DAY 10 = 3. |
| **Redding-montage** | — | baby 0 → 31,025 · jongen bij het zwembad 0 → 24,800 · oude man 0 → 2,190 · visje in het net: 900. |

---

# DEEL 0 · COLD OPEN (0:00-0:38)

## Scène 0 · Het kruispunt (0:00-0:13) · DAY 41 · 3:58 PM

**Set:** kruispunt bij school (straat-set video 2, uitgebreid met zebrapad, verkeerslichten, bushokje, bomen en gevels aan alle vier de kanten). Late middag, warm laag zonlicht, lange schaduwen. **HUD:** `DAY 41` met eronder `3:58 PM`. **Muziek:** geen. Alleen stadsgeluid dat wegzakt, en een hartslag.

**0a · CLOSE · trage push-in · 3,5 s**
Frame 1: zijn gezicht, groot, ogen wijd open, mond half open. Hij kijkt langs de camera naar iets aan de overkant. Rood licht van het voetgangerslicht op zijn wang. Hij hijgt.
- **Beweging:** borst gaat snel op en neer, slikt, zijn pupillen volgen iets van links naar rechts.
- **VO (op frame 1):** "Your best friend has zero days left."
- **SFX:** hartslag, dichtbij.

**0b · MEDIUM · statisch met lichte drift · 2,5 s**
Zijn beste vriend stapt van de stoep op het zebrapad, koptelefoon op, kijkt op zijn telefoon. Boven zijn hoofd: een rood, pulserend **0**.
- **Beweging:** vriend loopt rustig (echte loopcyclus, voeten vast op het asfalt), knikt op de muziek.
- **Let op:** telefoon zit ín zijn hand, duim op het scherm. Koptelefoonband op het hoofd, niet erdoorheen.

**0c · WIDE · laag, langs de stoeprand · 2,5 s**
Van rechts komt een bestelwagen de hoek om, te hard. **De chauffeur is zichtbaar** achter de voorruit, kijkt opzij naar een navigatiescherm.
- **SFX:** motor die optrekt, een claxon zet in.

**0d · CLOSE · 3,5 s**
Hij zet zich af. Anticipatie: gewicht naar achter, knieën buigen, dan schiet hij naar voren.
- **VO:** "And you know what it'll cost you."

**0e · ZWART · 1 s**
Hard naar zwart vlak voor het contact. Eén hartslag. Stilte.

## Scène 1 · De belofte (0:13-0:33)

**HUD:** geen. **Muziek:** pulserende sub-beat, elke cut op de hartslag. Shots van 2 s, harde cuts, geen witte flitsen (voorkomt FLITS-meldingen).

- **1a · WIDE · drone die zakt · 4 s:** een vol schoolplein, honderden kinderen, boven iedereen hetzelfde amber getal: **4**. **VO:** "One morning, there's a number above every head."
- **1b · MEDIUM · push-in · 3 s:** opa op een steiger bij een meer, hengel in de hand, lacht. Boven hem: **27** (amber). **VO:** "Days. How many they have left."
- **1c · DETAIL · 2 s:** een tv in een etalage: nieuwslezeres, onderbalk **MYSTERY KID SAVES 300**.
- **1d · MEDIUM · 3 s:** hij in de badkamerspiegel, zoekend naar boven zijn eigen hoofd. Daar staat niets. **VO:** "Everyone's... except yours."
- **1e · CLOSE · 2 s:** een getal boven een man in pak rolt van **0** naar **14,611**. Tik-tik-tik.
- **1f · CLOSE · statisch · 2,5 s:** zijn broertje kijkt omhoog naar iets boven de camera, zijn gezicht valt stil. (Plant voor het slot; niet uitleggen.)
- **1g · ZWART · 3,5 s · VO:** "So... would you want to know?"

## Scène 2 · Titel (0:33-0:38)

**2a · TITELKAART · 3 s**
**WHAT IF YOU COULD SEE HOW MANY DAYS EVERYONE HAS LEFT?** in witte letters op nachtblauw. Het woord **DAYS** gloeit amber. Rechts van de tekst rolt een teller van 27,000 naar 0 en stopt.
- **SFX:** één zware hartslag.

**2b · zwart naar slaapkamer · 2 s** (match cut, zie 3a)

---

# DEEL 1 · LEUK (0:38-2:50) · DAY 1-3

## Scène 3 · Wakker worden (0:38-1:00) · DAY 1

**Set:** slaapkamer (hergebruik, glans-look). Ochtend, zon door de lamellen, stofjes in de lichtbundel. Alle vier de muren en het plafond aanwezig (camera kijkt in 3c omhoog). **HUD:** `DAY 1` verschijnt in 3a. **Muziek:** licht, nieuwsgierig: pizzicato en felt piano.

**3a · CLOSE · statisch met drift · 4 s**
Hij doet zijn ogen open. Knippert twee keer. Kijkt naar zijn nachtkastje, waar zijn goudvis in een kom zwemt. Boven de vis zweeft: **212**.
- **Beweging:** hoofd draait langzaam opzij (eerst ogen, dan hoofd, dan schouders: G.3).
- **VO:** "It's a Wednesday. Nothing about it is special."

**3b · MEDIUM · 3 s**
Hij gaat rechtop zitten, wrijft in zijn ogen (handen echt tegen de ogen, niet erdoor), kijkt opnieuw. Het getal staat er nog.
- **JONGEN:** "...what?"

**3c · LOW MEDIUM · camera onder ooghoogte · 4 s**
De deur vliegt open. Het broertje (7) springt in een dinopyjama op het bed. Boven hem: **29,931**.
- **Beweging:** broertje landt op zijn knieën op het matras (matras deukt zichtbaar in, geen knieën door het bed), stuitert één keer na.
- **BROERTJE:** "Mom says pancakes!"
- **Beweging (plant 1 voor het slot, 0,5 s):** voor hij wegrent, blijft de blik van het broertje heel even hangen bóven de goudviskom. Hij knijpt zijn ogen samen, schudt zijn hoofd, rent weg. Niet uitleggen, geen geluid, geen close-up.
- **Let op:** het getal van het broertje komt niet in de HUD-hoek; kadreer hem links.

**3d · CLOSE · push-in · 3,5 s**
Hij staart naar de lucht boven het hoofd van zijn broertje. Zwaait er met zijn hand doorheen. De hand gaat er gewoon doorheen (getal reageert niet, geen clipping-probleem: het getal is niet fysiek).
- **VO:** "Rule one. Everything alive has a number."

**3e · MEDIUM · 6 s**
Het broertje rent weer weg. Hij stapt uit bed (voeten eerst op de vloer, gewicht verplaatsen, opstaan: G.4), loopt naar de deur.
- **VO:** "It's how many days they have left. You just don't know that yet."

**3f · DETAIL · 2 s**
De goudvis. **212.** Hij zwemt een rondje.
- **SFX:** blub.

## Scène 4 · Het ontbijt (1:00-1:30) · DAY 1

**Set:** keuken met eettafel (hergebruik, glans), ochtend. Pannenkoeken, sap, borden. Opa en oma zijn op bezoek. **Muziek:** speels, valt stil bij 4g.

**4a · WIDE · trage dolly langs de tafel · 5 s**
Het gezin aan tafel. Boven iedereen een getal: mama **17,840**, papa **15,226**, oma **6,102**, broertje **29,931**. Opa zit aan het hoofd van de tafel, leest de krant.
- **Beweging:** mama schept pannenkoeken op (spatel ín de hand, pannenkoek glijdt echt op het bord), papa schenkt sap in (straal sap, glas vult zich), oma schudt de kleine hand van het broertje heen en weer. Iedereen beweegt, niemand staat stil (G.1).
- **Let op:** iedereen zit echt op de stoel (billen op de zitting, voeten op de vloer of op de sport van de stoel, geen buik door de tafel: G.5).

**4b · MEDIUM · 3 s**
Hij komt binnen, blijft in de deuropening staan. Zijn ogen schieten van getal naar getal.
- **VO:** "Big numbers. Normal numbers. Fine."

**4c · CLOSE · 3 s**
Hij kijkt naar opa. Camera blijft op zíjn gezicht. De glimlach zakt langzaam weg.

**4d · MEDIUM · trage push-in · 4,5 s**
Opa laat de krant zakken. Boven hem: **34**, amber.
- **OPA:** "Morning, champ. You look like you've seen a ghost."

**4e · CLOSE · 3 s · opa**
Opa kijkt hem een seconde te lang aan. Een kleine, wetende glimlach. Dan gaat de krant weer omhoog.
- **Let op:** dit is de plant voor de twist. Subtiel: geen knipoog, alleen de blik en de glimlach, 1 s.

**4f · MEDIUM · 3,5 s**
Hij gaat zitten (stoel achteruit schuiven, zitten, stoel aanschuiven: met contact). Prikt in een pannenkoek, eet niet.
- **MAMA:** "Honey? You okay?"
- **JONGEN:** "Yeah. Just... tired."

**4g · CLOSE · 6 s**
Zijn gezicht. Achter hem, onscherp, opa die lacht om iets van oma.
- **VO:** "Thirty-four. You don't know what it means yet. But you already hate it."
- **Muziek:** stopt. Eén lage pianotoon.

**4h · DETAIL · 2 s**
Opa's hand pakt een pannenkoek van het bord van het broertje. Het broertje gilt van het lachen.
- **SFX:** gelach, warm.

## Scène 5 · Naar school (1:30-1:59) · DAY 1

**Set:** straat met huizen, stoep, bushokje (hergebruik video 2, beide straatkanten bebouwd, achter elk huis een volgende rij of bomen; geen lege horizon). Zonnig. **Muziek:** terug, licht en snel.

**5a · WIDE · camera loopt mee (dolly) · 5,5 s**
Hij loopt naar school, rugzak op (rugzakbanden op de schouders, rugzak wiebelt na bij elke stap). Overal getallen: een vrouw met hond (vrouw **20,113**, hond **3,650**), een postbode op de fiets (**11,002**, trapt echt, voeten op de pedalen).
- **VO:** "On the way to school, you start reading people like price tags."

**5b · MEDIUM · 3 s**
Een kraai op een hek. Boven hem: **2**, rood.
- **Beweging:** de kraai hipt, kijkt hem met één oog aan, poetst een veer.
- **JONGEN:** "Sorry, buddy."

**5c · MEDIUM · 5 s**
De pestkop staat bij het hek van school, duwt een jonger kind opzij (duw met contact: handen op de schouder, kind stapt achteruit, valt niet). Boven de pestkop: **25,915**.
- **JONGEN (rustig, gewone stem):** "Oh, come on."
- **VO:** "Of course he lives to be eighty-five."

**5c2 · WIDE · bushalte · 6 s**
Een oma van in de tachtig (figuur: oma-model met andere kleren en een boodschappentas) rent de bus achterna, springt over een plas en haalt hem. Boven haar: **9,800**.
- **VO:** "That old lady? Twenty-seven more years. She's going to outlive the bus."
- **Let op:** echte renncyclus voor een oude vrouw: korte passen, gebogen rug. De bus heeft een zichtbare chauffeur en wacht met open deuren.

**5c3 · CLOSE · 3 s**
Hij moet lachen, schudt zijn hoofd.
- **JONGEN:** "Okay. This is kind of awesome."

**5d · MEDIUM · camera volgt · 6 s**
De beste vriend komt naast hem lopen, slaat een arm om zijn schouder (arm rust op de schouder, niet erin). Boven de vriend: **25,550**.
- **VRIEND:** "Dude. Why are you staring at my hair?"
- **JONGEN:** "No reason. It's... great hair."
- **Let op:** het getal telt elke nacht één af (DAY 41 = 25,510). In scène 18 valt het naar 0.

## Scène 6 · De regels testen (1:59-2:36) · DAY 1-2

**Set:** schoolwc met spiegels (nieuw, klein: tegels, wastafels, spiegels, deuren, plafond met tl-buizen) en klaslokaal (school-set video 1). **Muziek:** spannend-speels.

**6a · MEDIUM · camera schuin naast de spiegel · 8 s**
In de wc. Hij kijkt in de spiegel, gaat op zijn tenen staan, draait zijn hoofd. Boven zijn spiegelbeeld: niets.
- **VO:** "Rule two. You can't see your own number. Not in a mirror. Not in a photo. Not anywhere."
- **Let op:** spiegel met echte reflectie (screen space reflections of een gespiegelde camera). Camera nooit in de reflectie zichtbaar.

**6b · DETAIL · 2,5 s**
Hij maakt een selfie met zijn telefoon. Op het scherm: hij, zonder getal.
- **JONGEN:** "Great."

**6c · WIDE · klaslokaal · 6 s**
Wiskundeles. Dertig leerlingen, dertig getallen. De leraar (gymleraar-model in overhemd) schrijft op het bord (krijt ín de hand, tegen het bord, krijtlijn verschijnt mee met de hand).
- **VO:** "This part is real. The average human gets about twenty-seven thousand days."

**6d · CLOSE · trage pan langs de rijen · 4,5 s**
Getallen: 24,301 · 26,870 · 22,019 · 28,402. Hij telt op zijn vingers.
- **VO:** "Twenty-seven thousand. That's it. That's the whole deal."

**6e · CLOSE · 3 s**
Hij kijkt naar zijn vriend, twee tafels verder. 25,550. Hij lacht opgelucht.
- **VO:** "Seventy years. Plenty."

**6f · MEDIUM · 7,5 s · klaslokaal, DAY 2**
- **HUD:** `DAY 2`.
De vriend draait zich om op zijn stoel en zegt het rustig, met gewone stem (stoel kantelt op twee poten, hand op de tafel om in evenwicht te blijven).
- **VRIEND:** "You've been weird for two days. Did you get a girlfriend? Superpowers?"
- **JONGEN:** "...sort of the second one."

**6g · CLOSE · 5,5 s**
De vriend trekt een wenkbrauw op. Wacht. De jongen zegt niets meer.
- **VO:** "You want to tell him. But how do you tell someone that?"

## Scène 7 · De kraai (2:36-2:50) · DAY 2 → DAY 3

**Set:** straat bij het hek (zelfde als 5b), avond en daarna ochtend. **Muziek:** één lange strijkerstoon.

**7a · WIDE · statisch · 3 s · avond**
Het hek, oranje straatlicht. De kraai zit er nog. **1**. Hij staat stil, rugzak in de hand.

**7b · DETAIL · 2,5 s · klok op zijn telefoon**
23:59 → 00:00. Alle getallen springen één omlaag met een korte pop. De kraai: **0**.
- **SFX:** zachte pop.
- **HUD:** `DAY 3`.

**7c · MEDIUM · 5 s · ochtend**
De kraai vliegt op en verdwijnt over de daken. Hij volgt hem met zijn ogen. Achter een schoorsteen: stilte. Er komt geen kraai meer terug. (Geen dode vogel in beeld.)
- **VO:** "Day three. The crow is gone. And you finally get it."

**7d · CLOSE · push-in · 3 s**
Zijn gezicht. Hij draait zich om, kijkt in de richting van opa's huis.
- **VO:** "They're not just numbers."
- **SFX:** hartslag, één keer.

---

# DEEL 2 · INDRUKWEKKEND (2:50-5:28) · DAY 5-8

## Scène 8 · Nul (2:50-3:36) · DAY 5

**Set:** het kruispunt uit scène 0 (zelfde set, nu ochtend, grijs weer). Druk: voetgangers, een fietser, een vrachtwagen bij het stoplicht (chauffeur zichtbaar). **Muziek:** spanning bouwt op.

**8a · WIDE · 5 s**
Hij wacht bij het zebrapad. Naast hem, op de stoep, een man in pak met een koffiebeker. Boven de man: **0**, rood, pulserend.
- **VO:** "Day five. And for the first time, you see a zero."

**8b · CLOSE · 2 s**
Zijn ogen. Van het getal, naar de man, naar het stoplicht.

**8b2 · CLOSE · 5 s**
Hij kijkt om zich heen. Niemand anders ziet het. Zijn hand gaat half omhoog, en weer omlaag.
- **VO:** "Zero means today. Maybe the next minute. Maybe the next second."

**8b3 · MEDIUM · 3 s**
- **JONGEN:** "Uh... sir? Nice... tie?"
- **Beweging:** de man kijkt niet eens op, steekt zijn duim op zonder van zijn telefoon weg te kijken.

**8c · MEDIUM · 3 s**
Het licht voor de voetgangers springt op groen. De man stapt van de stoep, kijkt op zijn telefoon. Links: een scooter die door rood rijdt (bestuurder met helm zichtbaar, handen aan het stuur).
- **SFX:** scooter, hoog en snel.

**8d · MEDIUM · handheld · 2,5 s**
Hij grijpt de man bij zijn kraag en trekt hem terug (anticipatie, ruk, man stapt struikelend achteruit, beide voeten maken echte stappen). De koffie valt.
- **Let op:** hand echt om de kraag, geen arm door het pak.

**8e · WIDE · 2 s**
De scooter schiet rakelings voorbij waar de man had gestaan. Wind. Papier dwarrelt op.

**8f · CLOSE · 3 s · het getal**
Boven de man rolt het getal: 0 → 3 → 112 → 14,611. Tik-tik-tik.
- **VO:** "Rule three. The numbers can change."

**8g · MEDIUM · 4,5 s**
De man kijkt hem aan, hijgend, koffie over zijn schoenen.
- **MAN:** "You... you just..."
- **JONGEN:** "You're welcome. Watch the road."

**8h · CLOSE · statisch · 4 s**
Hij loopt weg en krimpt even ineen. Hand op zijn borst. Eén overgeslagen hartslag, alleen voor hem (trap 1 van de hartslag).
- **Let op:** plant voor de prijs. Kort: 0,5 s grimas, dan schudt hij het van zich af.
- **VO:** "A little skip in your chest. Probably nothing."

**8i · DETAIL · 8,5 s**
- **VO:** "Here's the crazy part. In 1961, a scientist rounded one number in a weather model. And the whole forecast changed."
- **Beeld:** een klein kaartje met een weerkaart die verspringt (2D-overlay in glans-stijl).

**8j · CLOSE · 4,5 s**
- **VO:** "Tiny changes. Huge futures. And you just changed one."

## Scène 9 · Held (3:36-4:30) · DAY 6-7

**Muziek:** opzwepend, hoopvol. Montage, elk shot 2,5-3 s. **HUD:** springt `DAY 6`, `DAY 7`.

Functie van deze scène: **zelfvertrouwen**. Hij wordt er goed in, en het voelt geweldig. Maar de prijs groeit mee (trap 2 en 3).

- **9a · MEDIUM · park · 4 s · DAY 6:** een moeder duwt een kinderwagen (moeder duwt echt, handen aan de duwstang). Baby **0** (rood). Een losgeraakte tak boven het pad kraakt. Hij trekt de kinderwagen opzij (hand op de stang, naast die van de moeder). De tak valt op het lege pad. Baby: **31,025**. **VO:** "So you start saving people."
- **9b · CLOSE · hij · statisch · 4,5 s:** twee overslagen. Hij blijft even staan, hand op de borst, ademt uit door zijn mond, lacht het weg (trap 2). **VO:** "Two skips this time. You tell yourself it's the running."
- **9c · MEDIUM · zwembad-buitenrand · 3 s:** een jongen glijdt uit aan de rand, **0**. Hij grijpt zijn pols. Jongen: **24,800**.
- **9d · WIDE · supermarkt (video 3-set) · 3,5 s:** een oude man reikt naar een hoge plank, een stapel blikken wankelt (zichtbaar: hij reikt zelf, zijn hand duwt de stapel). Man **0**. Hij duwt de stapel recht. Man: **2,190**. **VO:** "Seven people. In two days."
- **9d1 · MEDIUM · skatepark (video 3-set) · 5 s · DAY 7:** de pestkop staat boven aan de helling met zijn fiets, boven hem **25,909**. Hij laat zijn stuur los en roept naar zijn vrienden "Watch this!". Op dat moment rolt zijn getal live omlaag: 25,909 → 112 → **0**. Tik-tik-tik, dan stil. **VO:** "Rule four. The numbers aren't fate. They're a forecast."
- **9d2 · WIDE · 4 s:** de pestkop rijdt zonder handen de helling af, richting de weg. Een auto komt aanrijden (chauffeur zichtbaar). Hij sprint, grijpt de bagagedrager en trekt de fiets het gras in. Ze vallen allebei in het gras (zachte val, rollen). **VO:** "And yes. Even him."
- **9d3 · CLOSE · statisch · 7,5 s:** de pestkop zit in het gras, hijgt, kijkt hem aan. Getal: 0 → **25,909**. Naast hem moet de jongen gaan zitten, hand op zijn borst, hand trilt (trap 3). **PESTKOP:** "Why would you... I shoved you into a locker last week." **JONGEN:** "Yeah. Don't do that again."
- **9d4 · MEDIUM · 3,5 s:** de pestkop staat op en steekt na een seconde zijn hand uit. Hij pakt hem (echte handdruk) en laat zich omhoogtrekken. **VO:** "This time, you have to sit down."
- **9e · MEDIUM · keuken thuis · 6 s:** het broertje zit met grote ogen, hij doet de redding na met een pannenkoekenspatel als zwaard. **BROERTJE:** "You're like a superhero!" **JONGEN:** "I'm more like... a guy who reads numbers."
- **9e2 · CLOSE · broertje · statisch · 2 s:** plant 2 voor het slot. Het broertje kijkt even naar iets boven papa's hoofd (buiten beeld), wrijft in zijn ogen, eet door. Geen geluid, geen uitleg.
- **9f · DETAIL · tv in de woonkamer · 4 s:** nieuwslezeres. Onderbalk **MYSTERY KID SAVES 7**. **NIEUWSLEZERES:** "Who is the mystery kid of Maple Street?"
- **9g · CLOSE · hij voor de tv · 4 s:** hij grijnst, en wrijft dan over zijn borst. Op de achtergrond, in de stoel bij het raam, opa: hij kijkt níet naar de tv, maar naar hem. Boven opa: **28** (DAY 7). **VO:** "Everyone's watching the news. Grandpa is watching you."
- **9g2 · CLOSE · opa · statisch · 2,5 s:** opa ziet de hand op de borst van de jongen. Zijn eigen hand gaat, zonder dat hij erbij nadenkt, naar zijn eigen borst: precies hetzelfde gebaar. Dan pakt hij de krant weer. (Plant voor de brief: hij kent dat gevoel.)

## Scène 10 · Opa (4:30-5:28) · DAY 8

**Set:** dokterspraktijk (hergebruik video 1, set 14), daarna de steiger aan het meer (nieuw: houten steiger, riet, meer met kleine golfjes, bos rondom, vogels; geen lege horizon). **Muziek:** zacht, piano.

**10-0a · MEDIUM · keuken · 3,5 s**
Hij haalt opa's autosleutels van het haakje en verstopt ze in de koektrommel (deksel eraf, sleutels erin, deksel erop, met contact).
- **VO:** "So you try everything."

**10-0b · MEDIUM · 4 s**
Opa aan tafel voor een bord met alleen broccoli. Hij kijkt de jongen aan. De jongen knikt streng.
- **OPA:** "What is this?"
- **JONGEN:** "Vegetables. You love vegetables now."

**10-0c · WIDE · gang · 3,5 s**
Opa wil de trap op. De jongen staat al boven aan de trap met zijn armen gespreid.
- **JONGEN:** "Elevator."
- **OPA:** "We don't have an elevator."

**10-0d · CLOSE · getal · 5 s**
Boven opa: **27**. Het beweegt niet. Geen tik.
- **VO:** "No car. No stairs. No bacon. The number doesn't even blink."

**10a · MEDIUM · 5 s · praktijk**
Opa op de onderzoekstafel (zit echt op de tafel, papier kreukt). De dokter (wetenschapper-model, man, witte jas) luistert met een stethoscoop (stethoscoop echt op de rug, oordopjes in de oren). Boven opa: **27**.
- **VO:** "If the numbers can change, then you can fix this one."

**10b · MEDIUM · 4 s**
- **DOKTER:** "Honestly? He's in great shape for seventy-six."
- **Beweging:** dokter haalt de stethoscoop van zijn nek en hangt hem over zijn schouders.

**10c · CLOSE · 2,5 s · getal**
**27.** Het beweegt niet. Geen tik.

**10d · WIDE · steiger · trage dolly achteruit · 5 s · middag**
Opa en hij op de steiger. Opa zit op een klapkrukje, hengel tussen zijn knieën. Hij zit op de rand, benen boven het water (voeten bungelen en bewegen, niet door het water heen).
- **Beweging:** opa gooit uit: hengel naar achteren, pauze, zwiep naar voren, lijn vliegt, dobber landt met een klein plonsje en kringen. (Lijn is een echte curve, geen rechte staaf.)

**10e · MEDIUM · 7,5 s**
- **JONGEN:** "Grandpa... if you could know how much time you had left... would you want to?"
- **Beweging:** hij plukt aan een splinter van de steiger, kijkt opa niet aan.

**10f · CLOSE · opa · 4 s**
Opa kijkt naar de dobber. Glimlacht.
- **OPA:** "Some numbers aren't a problem to fix, kiddo."
- **Beweging:** opa geeft hem zachtjes een duw tegen zijn schouder met de knokkels. Statisch shot.

**10g · CLOSE · hij · 3 s**
Hij kijkt op. Fronst. *Numbers?*
- **SFX:** de dobber gaat onder. Plons.

**10h · MEDIUM · 4 s**
- **OPA:** "Whoa, whoa! Grab the net!"
- **Beweging:** opa staat op (krukje kantelt, valt niet om), hengel krom, hij grijpt het schepnet. Ze lachen allebei. Een kleine vis spartelt in het net, boven hem **900**.

**10h2 · CLOSE · opa · 6,5 s**
Opa kijkt even naar de lucht boven het visje (een halve tel, alleen zijn ogen) en laat hem terug in het water glijden.
- **OPA:** "Let him go. He's got plenty of time."
- **VO:** "He almost said something. You almost noticed."

---

# DEEL 3 · GEVAARLIJK (5:28-8:15) · DAY 9-13

## Scène 11 · Vier (5:28-6:08) · DAY 9

**Set:** schoolplein (school-set video 1, uitgebreid: hekken, bomen, gevel aan drie kanten, gymzaal met plat dak zichtbaar). Ochtend, licht bewolkt. **Muziek:** valt weg. Alleen schoolplein-geroezemoes.

**11a · WIDE · drone die zakt (= 1a) · 5 s**
Het volle schoolplein. Honderden kinderen. Boven iedereen: **4**.
- **VO:** "Day nine. Overnight, every number at your school dropped to four."

**11b · MEDIUM · trage pan · 4 s**
Langs gezichten: de pestkop **4**, de leraar **4**, de conciërge met een bezem **4**, de vriend **4** (tijdelijk: na de redding wordt het weer 25,538).
- **Let op:** het getal van de vriend is hier ook 4, dat klopt (hij zit op dezelfde school).

**11c · CLOSE · 3 s**
Hij draait langzaam rond. Ademt sneller.
- **VO:** "Four days. Three hundred people."

**11c2 · MEDIUM · 8 s**
De vriend tikt hem aan, met een zak chips in zijn hand (zak kraakt, hand erin).
- **VRIEND:** "Dude. You're doing the staring thing again."
- **VO:** "Not a fire. Not a crash. Something that takes everyone at once."

**11d · WIDE · laag · 3 s**
De gymzaal met het platte dak. Een plas water staat op de dakrand. Een regenpijp druppelt.
- **SFX:** druppel. Druppel.

Functie van scène 11-13: **veel mensen tegelijk, en dat kan hij niet alleen.** Eerst moet hij uitzoeken wát er gebeurt, zodat de kijker begrijpt waarom hij zo zeker is.

**11e · MEDIUM · gymzaal binnen, leeg, pauze · 4 s**
Hij glipt de lege gymzaal in. Midden op de vloer staat een gele emmer onder een lek. Plink. Plink.
- **VO:** "You don't know what's coming. So you look."

**11f · CLOSE · plafond · statisch · 3 s**
Zijn telefoonlamp schijnt omhoog: een bruine waterplek op een plafondpaneel, het paneel hangt een paar centimeter door.

**11g · MEDIUM · 6 s**
De conciërge komt binnen met een bezem, ziet waar hij naar kijkt.
- **CONCIËRGE:** "Roof drains are full of leaves. Since September. I've put in a ticket. Twice."

**11h · DETAIL · telefoon · 5 s**
Twee schermen na elkaar: de weer-app (**MONDAY: RECORD RAINFALL**) en de schoolagenda (**MONDAY 9:00 · ASSEMBLY · GYM**).
- **VO:** "Clogged drains. Record rain. Three hundred people under one flat roof."

## Scène 12 · Niemand gelooft je (6:08-7:11) · DAY 10-12

**Set:** kamer van de directeur (klein, nieuw: bureau, kast, raam met uitzicht op het schoolplein, plafond), kantine (hergebruik video 3 schoolkantine of gymzaal-variant). **HUD:** `DAY 10` … `DAY 12`.

**12a · MEDIUM · 9,5 s**
Hij staat voor het bureau van de directeur (nieuwe figuur: vrouw, bril, vest). Boven haar: **3**.
- **JONGEN:** "The roof drains are clogged. There's a stain, the ceiling's sagging... Please. Move Monday's assembly."
- **DIRECTEUR:** "That roof passed inspection in March."

**12a2 · CLOSE · directeur · statisch · 6 s**
- **DIRECTEUR:** "I can't cancel an assembly for three hundred kids because of a feeling."
- **Beweging:** ze zet haar bril af, wrijft over haar neus. Niet boos, wel moe. Boven haar: **3**.

**12b · CLOSE · statisch · 4 s**
Hij opent zijn mond. Klapt hem dicht. Wat moet hij zeggen? *Your number is three?*
- **VO:** "And you can't tell her how you know."

**12c · MEDIUM · 10 s**
- **VO:** "Here's the thing. Insurance companies already guess your number. They've done it since 1693, when the astronomer Edmond Halley built the first life table."
- **Beeld:** een oud perkament-tabel (2D-overlay) met jaartallen, die vervaagt in de kantine.

**12d · MEDIUM · kantine · 5,5 s**
Hij zit tegenover zijn vriend en praat rustig, met gewone stem. De vriend legt zijn sandwich neer.
- **VRIEND:** "Okay. Say I believe you. What's my number?"
- **JONGEN:** "...Three."
- **VRIEND:** "I'm in."

**12d2 · MEDIUM · gang · 5,5 s · DAY 11**
De vriend en hij hangen zelfgemaakte posters op (plakband echt tussen de vingers, poster strak tegen de muur): **STAY OUT OF THE GYM ON MONDAY**. Een leraar trekt er meteen eentje af.
- **VO:** "You try posters. Teachers. The internet. Every day, the numbers get smaller."

**12d3 · CLOSE · 3 s · telefoon**
Zijn bericht in een schoolgroepsapp: *The gym roof is going to fall on Monday.* Eronder: *lol*, *ok prophet*, een lachende emoji.

**12d4 · MEDIUM · 8,5 s · thuis, DAY 11**
Papa zet zijn telefoon op tafel.
- **PAPA:** "Your principal called. Buddy... what's going on with you?"
- **JONGEN:** "If I told you, you wouldn't believe me."
- **PAPA:** "Try me."
- **Beweging:** papa gaat op zijn hurken zitten, op ooghoogte (knieën buigen, hielen omhoog, evenwicht).

**12d5 · CLOSE · 3 s**
Hij kijkt naar papa's getal. **15,216.** Hij schudt zijn hoofd.
- **JONGEN:** "Just... trust me on Monday."

**12e · WIDE · 7,5 s · avond**
Thuis, de regen tikt op het raam. Op de tv: weerkaart, een dikke storm. **NIEUWSLEZERES:** "Record rainfall expected on Monday."
- **HUD:** `DAY 12`.
- **VO:** "Monday is day thirteen. And Monday is the assembly in the gym."

## Scène 13 · De storm (7:11-8:15) · DAY 13

**Set:** gymzaal (hergebruik 06_gymzaal, aangevuld: tribunes, 300 stoelen in rijen, podium, microfoon, plafond met balken en lichtkoepels; het dak is de breekbare laag). Buiten stortregen. **Muziek:** strakke tik-tik-ostinato die versnelt.

**13a · WIDE · hoog vanaf de tribune · 4 s**
De zaal loopt vol. Driehonderd stoelen, driehonderd keer **0**, rood, pulserend. Op het podium tikt de directeur op de microfoon.
- **Let op:** figuranten lopen naar stoelen en gaan zitten met echte loop- en zitbewegingen (G.4). Niemand glijdt. Instancing mag, maar elk figuur heeft een eigen beginframe (offset 0-2 s) zodat niemand synchroon beweegt.

**13b · DETAIL · plafond · 9,5 s**
Een lichtkoepel. Water staat erop. Het plafondpaneel ernaast buigt een paar centimeter door. Een druppel valt.
- **VO:** "This part is real. Every two and a half centimeters of rain on a flat roof adds twenty-five kilos per square meter."

**13c · CLOSE · 4 s**
Hij kijkt omhoog. Kijkt naar de rode wandknop BRANDALARM bij de deur.
- **VO:** "That roof has been holding a swimming pool."

**13d · MEDIUM · 4,5 s**
Zijn vriend houdt de directeur aan de praat bij het podium ("Ma'am, quick question about the, uh... the thing").
- **Beweging:** vriend gebaart druk, gaat steeds net vóór haar staan.

**13e · MEDIUM · camera volgt laag · 3 s**
Hij rent langs de muur (echte renncyclus, armen pompen, voorovergebogen) naar de knop. Glas tikken, knop indrukken.
- **Let op:** hand raakt het glaasje echt, knop gaat zichtbaar in.

**13f · WIDE · 3 s**
Het alarm. Rode zwaailichten. Kinderen staan op, leraren wijzen naar de nooduitgangen. Iedereen loopt (niet rent) naar buiten, in rijen.
- **SFX:** alarm, maar gedempt en onder de stem (geluidsmix: nooit harder dan de VO).

**13f2 · MEDIUM · 4 s**
Maar de directeur grijpt de microfoon.
- **DIRECTEUR:** "Everyone sit down! It's a prank! Sit. Down."
- **Beweging:** kinderen aarzelen, halverwege opgestaan, sommigen gaan weer zitten.

**13f3 · CLOSE · 2 s · plafond**
Het paneel buigt verder. Een scheur kruipt door het pleisterwerk. Water sijpelt.

**13f4 · MEDIUM · 6 s**
Achterin springt de pestkop op een stoel (stoel wiebelt, hij houdt zijn evenwicht met zijn armen).
- **PESTKOP:** "EVERYBODY OUT! NOW!"
- **VO:** "The one guy everybody listens to. The one you saved."

**13f5 · WIDE · 3 s**
Iedereen staat op en loopt naar de uitgangen. De pestkop kijkt naar hem, knikt kort.

**13g · WIDE · schoolplein in de regen · 4 s**
Driehonderd kinderen in de regen, mopperend. De directeur kijkt hem woedend aan, wijst naar hem.
- **DIRECTEUR:** "You. My office. Now."

**13h · WIDE · laag vanaf het plein · 3 s**
Achter haar zakt het gymdak in. Langzaam eerst: een knik in het midden, dan valt een stuk naar binnen. Water stort de lege zaal in.
- **SFX:** een diep, langgerekt gekraak, opbouwend (nooit een plotse piek: fade-in over 1 s).
- **Let op:** het dak breekt in vooraf gemodelleerde stukken (cell fracture of handgemaakt), met rigid body-simulatie of keyframes. Geen stukken die door de muren gaan. Geen mensen in de zaal.

**13h2 · MEDIUM · binnen in de lege zaal · 3 s**
De lege stoelen. Water en stukken dak storten neer precies waar de rijen stonden. Stoelen kantelen weg.
- **Let op:** geen figuren in de zaal. Stof en spetters, geen schokkende camera.

**13i · CLOSE · 3 s · gezichten**
Stilte. De directeur draait zich om. Mond open.

**13j · WIDE · trage push-in · 4 s**
Boven alle hoofden tegelijk rollen de getallen: 0 → 9,104 · 21,550 · 26,002 · 25,903 (pestkop) · 25,538 (vriend). Een golf van tik-tik-tik over het plein.
- **VO:** "Three hundred numbers. Back."

**13k · CLOSE · 3 s**
Hij wankelt. Hand op zijn borst. Een zware hartslag, dan nog een, dan te snel achter elkaar. Hij zakt door zijn knieën (gecontroleerd: knieën eerst op de grond, hand op de natte tegels, valt niet hard).
- **SFX:** hartslagen, het beeld wordt kort wazig aan de randen (vignet + lichte blur, 1 s), geen witte flits.

**13l · ZWART · 1 s**

---

# DEEL 4 · SCHOKKEND (8:15-12:36) · DAY 14-40

## Scène 14 · Wakker in de ziekenboeg (8:15-9:04) · DAY 14 · met abonneeroproep

**Set:** ziekenhuiskamer (nieuw, klein: bed, monitor, raam met stad, gordijn, stoel, plafond). Ochtend. **Muziek:** zacht.

**14a · MEDIUM · 4,5 s**
Hij in het ziekenhuisbed. Mama zit naast hem, houdt zijn hand vast (vingers verstrengeld). Monitor piept rustig. In de hoek speelt een tv zonder geluid het nieuws: **MYSTERY KID SAVES 300**.
- **DOKTER (off):** "His heart skipped a few beats. Probably stress. He's fine."

**14b · CLOSE · 9 s**
Hij kijkt naar mama's getal. **17,827.** Opgelucht. Dan naar zijn eigen borst.
- **VO:** "This part is real too. Your heart beats about a hundred thousand times a day. You never notice. Until it skips."

**14b2 · CLOSE · 2,5 s**
Hij kijkt naar de monitor. Het lijntje loopt rustig.
- **VO:** "Stress. Sure."

**14c · MEDIUM · statisch · 4,5 s**
Het broertje komt binnen met een zelfgemaakte tekening: een superheld met een cape en een groot getal. Hij geeft hem aan hem (papier echt in beide handen, overdracht met contact).
- **BROERTJE:** "It's you."
- **Let op:** geen verteller over dit moment. Alleen de stem van het broertje en het papier.

**14d · DETAIL · 3 s**
De tekening. Boven de held heeft het broertje een getal getekend: **1,000,000**.
- **JONGEN:** "Accurate."

**14d2 · MEDIUM · trage push-in · 8 s · abonneeroproep (~61%)**
De tekening hangt met plakband aan de monitor. Het broertje zit op het voeteneind en bungelt met zijn benen.
- **VO:** "If you want to see how this ends, subscribe. It's free. It won't cost you a single day."
- **Let op:** warm en in de verteltoon, geen reclamestem, 18 woorden. Het shot loopt tot 0,6 s na de laatste zin (G.9).

**14e · MEDIUM · 6 s**
Opa staat in de deuropening, hoed in zijn hand. Boven hem: **21**. Hij komt naast het bed zitten.
- **OPA:** "Heard you pulled a fire alarm."
- **JONGEN:** "Heard it was a good one."
- **OPA:** "The best." (opa woelt door zijn haar, hand echt op het hoofd)

**14e2 · CLOSE · opa · statisch · 5 s**
Opa kijkt naar de monitor, dan naar hem. Even niet grappig.
- **OPA:** "Go easy on that heart, champ. You only get the one."

**14f · CLOSE · 6 s**
Hij kijkt naar opa's getal. 21. Dan naar het raam.
- **VO:** "Twenty-one days. You can't fix his. So you do the only thing left."

## Scène 15 · De laatste weken (9:04-10:09) · DAY 15-35

**Set:** steiger aan het meer (scène 10), steeds een ander seizoensdetail: eind van de zomer, eerste gele blaadjes, mist. **Muziek:** warme, droeve piano met strijkers. Montage. Elk shot 3-4 s. Het getal boven opa telt zichtbaar af in elk shot.

Elk shot heeft een eigen HUD-dag, zodat de kijker de weken ziet verstrijken. Opa's getal klopt per dag met de getallen-tijdlijn.

- **15a · WIDE · steiger · 5,5 s · DAY 16:** opa en hij vissen. Opa **19**. **VO:** "You stop saving the world. And you spend every day with him."
- **15a2 · MEDIUM · steiger · statisch · 5 s · DAY 17:** opa leert hem de lijn knopen, grote vingers over kleine vingers. **OPA:** "Over, under, through. Pull." De knoop schiet los. Ze lachen. Opa **18**. **VO:** "He teaches you knots you can't tie."
- **15a3 · MEDIUM · straat · 6 s · DAY 19:** de man in pak uit scène 8 komt hem tegemoet, met een kinderwagen. Boven hem **14,597**, boven de baby **30,412**. Hij knikt de jongen toe, zonder te weten waarom. **VO:** "Some of the numbers you changed walk right past you. They don't even know."
- **15b · MEDIUM · keuken · 3,5 s · DAY 20:** opa leert hem pannenkoeken omdraaien: zwiep, de pannenkoek draait echt door de lucht, landt half op de rand. Gelach. Opa **15**.
- **15b2 · WIDE · eettafel · avond · 5,5 s · DAY 22:** mama's verjaardag. Kaarsjes op een taart. Opa staat op met een glas (glas echt in de hand, sap klotst). **OPA:** "To time. The one thing nobody gets more of. So, no speeches." Iedereen lacht en proost (glazen raken elkaar echt, geen glas door glas). Opa **13**.
- **15b3 · CLOSE · statisch · 6 s · DAY 22:** hij kijkt naar opa door de kaarsvlammen. Hij proost niet. Dan toch. **VO:** "You make every day count. Even the boring ones. Especially the boring ones."
- **15c · WIDE · straat · 3,5 s · DAY 24:** opa op een oude fiets, hij ernaast, beiden trappen (voeten op de pedalen, knieën gaan op en neer, geen schokken: ride-fix uit video 3). Opa **11**.
- **15c2 · WIDE · ijssalon (klein: toonbank, raam, twee krukjes) · 4 s · DAY 26:** opa bestelt drie bollen voor hen allebei. **OPA:** "Doctor's orders." **JONGEN:** "Which doctor?" **OPA:** "Me." Opa **9**.
- **15d · CLOSE · woonkamer · statisch · 6 s · DAY 28:** opa laat oude foto's zien. Een zwart-witfoto: een meisje van 14 op een fiets, lachend, haar wapperend. Opa tikt er met zijn vinger op. **OPA:** "Your grandma. Summer of '66. She nearly rode straight into a milk truck." Opa **7** (rood).
- **15d2 · CLOSE · statisch · 3,5 s · DAY 28:** **JONGEN:** "What happened?" **OPA** (glimlacht, legt de foto weg)**:** "I was in the way." (Plant voor 17g2.)
- **15e · MEDIUM · steiger · mist · 4,5 s · DAY 32:** ze zitten naast elkaar, zwijgend. Opa legt zijn hand op zijn schouder. Opa **3**. **VO:** "You don't tell him. And somehow... he never asks."
- **15e2 · CLOSE · statisch · 3,5 s · DAY 32:** hij kijkt opzij naar opa. Opa kijkt naar het water, ogen vochtig, glimlacht. **VO:** "It's almost like he already knows."
- **15e3 · MEDIUM · opa's slaapkamerdeur · nacht · statisch · 6 s · DAY 33:** hij staat in de deuropening en kijkt naar de slapende opa. Boven opa: **2**. Op zijn telefoon een zoekscherm: *how to stop a heart from getting old*. Hij doet het scherm uit. **VO:** "There's nothing to step in front of. It's not a moment. It's a clock."
- **15f · DETAIL · 3 s · DAY 34 → 35:** zijn telefoon: 23:59 → 00:00. Opa **1 → 0**. HUD `DAY 35`.

## Scène 16 · De laatste avond (10:09-11:04) · DAY 35

**Set:** opa's woonkamer (nieuw: leunstoel, staande lamp, boekenkast, open haard met een klein vuur, raam met avondlucht, plafond, vloerkleed; alle muren dicht). Warm lamplicht. **Muziek:** alleen een cello.

**16a · WIDE · statisch met drift · 4 s**
Opa in zijn leunstoel bij het vuur, deken over zijn benen. Hij zit op de grond naast de stoel. Boven opa: **0**, rood. Het pulseert heel langzaam.

**16a2 · DETAIL · statisch · 5 s**
Opa geeft hem een stukje vislijn. Zijn handen zijn te moe om zelf te knopen. De jongen knoopt, langzaam. Over, under, through. Pull. Deze keer houdt de knoop.
- **OPA:** "There it is."
- **Let op:** callback naar 15a2. Geen muziek, alleen het vuur.

**16b · CLOSE · opa · statisch · 4,5 s**
- **OPA:** "You know what I liked best about this month?"
- **Beweging:** opa's stem is warm en rustig (niet fluisteren), ogen half dicht, kleine glimlach.

**16c · CLOSE · hij · 2,5 s**
- **JONGEN:** "The fishing?"

**16d · CLOSE · opa · 4,5 s**
- **OPA:** "That you were there. Every single day. Like you knew."
- **Beweging:** opa knijpt in zijn hand. Zijn duim beweegt over de knokkels van de jongen.

**16d2 · CLOSE · opa · 8 s**
- **OPA:** "When I was your age, I thought time was something you had. It's not. It's something you give."
- **Beweging:** opa kijkt in het vuur, oranje licht op zijn gezicht, langzaam knipperen.

**16d3 · CLOSE · hij · 4 s**
- **JONGEN:** "Grandpa... I don't want you to go."
- **Beweging:** zijn kin trilt, hij slikt.

**16d4 · CLOSE · opa · 3 s**
- **OPA:** "I know, champ. I know."

**16e · DETAIL · 3 s**
Hun handen. Opa's grote hand met levervlekken, zijn hand erin.
- **VO:** (geen. 3 s stilte, alleen het vuur.)

**16e2 · CLOSE · 3 s**
Opa's ogen gaan dicht. Een kleine glimlach. Het rode getal boven hem dooft langzaam uit, als een kaars (1,5 s fade, geen flits).
- **VO:** (geen)

**16e3 · CLOSE · hij · 3 s**
Hij blijft zijn hand vasthouden. Legt zijn hoofd tegen de armleuning.
- **VO:** "You stay. All night."

**16f · WIDE · zelfde camerastandpunt als 16a · statisch · 5 s · ochtend**
Grijs ochtendlicht. De leunstoel is leeg. De deken ligt opgevouwen op de zitting. Het vuur is uit. Hij staat in de deuropening.
- **HUD:** `DAY 36`.
- **SFX:** een klok tikt. Geen muziek.

**16g · WIDE · steiger · statisch · 5 s · DAY 38**
Hij zit alleen op de steiger. Naast hem staat opa's klapkrukje, leeg, met opa's vissershoed erop. Wind in het riet. Hij knoopt een lijn aan de hengel: over, under, through. Pull.
- **VO:** (geen)
- **Muziek:** één cello-toon die overloopt in scène 17.

## Scène 17 · De brief (11:04-12:36) · DAY 40

**Set:** begraafplaats (nieuw: grasheuvel, bomen, hek, grafstenen, bloemen; stad op de achtergrond, alle richtingen gevuld), daarna zijn slaapkamer (nacht, bureaulamp). **HUD:** `DAY 40`, uit vanaf 17c. **Muziek:** strijkers, ingetogen.

**17a · WIDE · trage crane omlaag · 5,5 s**
Het gezin bij een graf met bloemen. Paraplu's, motregen. Iedereen in het zwart, getallen boven alle hoofden. Oma houdt het broertje vast.
- **VO:** "Thirty-four days. From the first morning to the last night. Exactly."
- **Beweging (plant 3 voor het slot):** het broertje kijkt even naar iets boven oma's hoofd en fronst. Oma trekt hem tegen zich aan onder haar jas. Niet uitleggen.

**17b · MEDIUM · 4 s**
Oma geeft hem een envelop (overdracht met contact, envelop echt tussen de vingers). Op de envelop, in opa's handschrift: *For the one who can see them.*
- **OMA:** "He said to give you this. Only you."

**17b2 · CLOSE · oma · 4 s**
Oma kijkt hem aan met dezelfde blik als opa in 4e.
- **OMA:** "He always said you two were the same."

**17c · CLOSE · slaapkamer · nacht · 3 s**
Hij opent de envelop aan zijn bureau (vinger onder de flap, scheurt, haalt de brief eruit). Geen HUD.

**17d · DETAIL · brief · trage pan langs de regels · 9,5 s**
Opa's stem leest voor (OPA, warm en rustig, als voice-over; niet fluisteren). De regels verschijnen op het papier in zijn handschrift, Engels. **Muziek:** geen, alleen kamergeluid, tot 17g2.
- **OPA:** "I saw it in your eyes at breakfast. That look, just above my head. I've had that look since I was fourteen."

**17e · CLOSE · 3 s**
Zijn gezicht. Hij stopt met ademen. Leest verder.

**17f · DETAIL · 7,5 s**
- **OPA:** "Here's what nobody told me. Every number you change... you pay for. With days of your own."

**17f2 · DETAIL · 9,5 s**
- **OPA:** "And some numbers aren't a moment you can step in front of. Mine was a clock. Don't blame yourself for that one."

**17g · CLOSE · trage push-in · 4 s**
Zijn hand gaat naar zijn borst. De hartslag uit 8h, 9b en 13k: nu begrijpt hij het.
- **VO:** "The skips. Every single one."

**17g2 · DETAIL · 12 s**
- **OPA:** "The first one was a girl on a bicycle. Summer of '66. She had a zero. I grabbed her handlebars, and she called me the rudest boy in town."
- **Beeld:** in de brief zit dezelfde zwart-witfoto als in 15d: het meisje op de fiets, lachend. **Muziek:** hier komt de piano zacht binnen.

**17g3 · CLOSE · 4,5 s**
Hij kijkt op, naar de deur. Beneden hoor je oma zachtjes neuriën.
- **VO:** "Sixty years with Grandma. He paid for every one."

**17h · DETAIL · 7,5 s**
- **OPA:** "Forty-three people. I should have had twenty more years. I spent them. Every one on purpose."

**17h1 · CLOSE · statisch · 3 s**
Hij legt de brief even neer. Zijn schouders trillen. Stilte.
- **VO:** (geen)

**17h2 · DETAIL · 9,5 s**
- **OPA:** "It skipped your father. It didn't skip you. You don't owe the world all of it, champ. Spend your days on purpose."
- **Beeld:** onder de brief zijn handtekening, *Grandpa*, en een klein getekend visje.

**17i · WIDE · statisch · 6 s**
Hij zit in het donker met de brief. Buiten gaat een straatlantaarn aan.
- **VO:** "So now you know the price. And why his number was so small."

---

# DEEL 5 · DE KEUZE EN DE TWIST (12:36-14:00) · DAY 41

## Scène 18 · Drie uur achtenvijftig (12:36-13:36) · DAY 41 · 3:51 PM → 3:58 PM

**Set:** schoolhek en het kruispunt (scène 0), late middag, zelfde licht als 0. **HUD:** `DAY 41` met de klok `3:51 PM` die doortelt. **Muziek:** hartslag + lage synth, versnellend.

**18a · MEDIUM · 3,5 s · schoolhek**
De bel. Hij loopt met zijn vriend naar buiten. Boven de vriend: **25,510**. Dan, midden in een stap, rolt het getal: 25,510 → 6,000 → 41 → **0**.
- **SFX:** tik-tik-tik, steeds sneller, dan stil.

**18b · CLOSE · 4,5 s**
Hij blijft staan. Kijkt.
- **VO:** "Day forty-one. A forecast. And it just changed."

**18c · MEDIUM · 3,5 s**
- **VRIEND:** "You coming? I gotta catch the bus."
- **Beweging:** de vriend zet zijn koptelefoon op en loopt alvast vooruit, achterstevoren lopend, zwaaiend. Draait zich om.

**18d · CLOSE · 5 s**
Hij legt zijn hand op zijn borst.
- **VO:** "You know what it costs now. Nobody tells you how much."

**18d2 · MEDIUM · camera volgt · 6 s · 3:54 PM**
Hij rent hem achterna, grijpt zijn arm.
- **JONGEN:** "Walk with me. Take the long way."
- **VRIEND:** "Dude, the bus is right there!"
- **Beweging:** de vriend trekt zich los, lachend, en rent naar de overkant van het plein.

**18d3 · CLOSE · 4,5 s · getal**
Boven de vriend: **0**. Het pulseert sneller.
- **VO:** "You could let it go. Keep every day you have."

**18d3b · CLOSE · statisch · 3 s**
Hij kijkt naar zijn handen. Op de achtergrond (onscherp) gaat het licht op groen.
- **JONGEN** (tegen zichzelf)**:** "On purpose."

**18d4 · CLOSE · 2,5 s**
Hij kijkt omhoog, naar de vriend.
- **VO:** "Grandpa didn't."

**18e · WIDE · 3 s · kruispunt (= 0b-standpunt)**
`3:58 PM`. De vriend stapt op het zebrapad, kijkt op zijn telefoon. **0.**

**18f · LOW WIDE · 2,5 s (= 0c)**
De bestelwagen komt de hoek om, chauffeur kijkt opzij.

**18g · CLOSE · 3 s (= 0d, nu met het vervolg)**
Hij zet zich af.
- **VO:** "And you don't even slow down."

**18h · MEDIUM · slow motion 40% · 3 s**
Hij springt, grijpt zijn vriend met beide armen om zijn middel en duwt hem door naar de overkant. Beiden rollen over de stoep (echte rol over de schouder, niet door de tegels, koptelefoon vliegt af en schuift over de grond).
- **SFX:** remmen piepen (gedempt), claxon, dan stilte.

**18h2 · CLOSE · slow motion 40% · 2,5 s**
Zijn gezicht, vlak bij de grond, ogen dicht. De koplamp van de bestelwagen schuift door het beeld. Eén hartslag die blijft hangen.

**18i · WIDE · 3 s**
De bestelwagen staat stil, een halve meter achter hen, schuin op het zebrapad. De chauffeur springt eruit, handen op zijn hoofd.

**18j · CLOSE · 3 s · getal**
Boven de vriend rolt het getal terug: 0 → 25,510.
- **SFX:** tik-tik-tik.

**18j2 · MEDIUM · 4 s**
De vriend zit rechtop op de stoep, koptelefoon scheef, staart hem aan. Mensen komen aanrennen.
- **VRIEND:** "How did you... how did you KNOW?"

**18k · CLOSE · 4 s**
Hij ligt op zijn rug op de stoep, hijgt, kijkt naar de lucht. Eén enorme hartslag. Dan nog één. Hij lacht. Tranen.
- **VRIEND (off):** "...dude. DUDE."
- **VO:** "Worth it."

## Scène 19 · Het slotbeeld (13:36-14:00) · DAY 41 · avond

**Set:** keuken thuis (scène 4), avond, warm licht. Het gezin, minus opa. Opa's stoel aan het hoofd van de tafel staat leeg, met zijn krant erop. **HUD:** uit vanaf 19c. **Muziek:** warm, dan weg.

**19a · WIDE · 4 s**
Hij komt binnen met een pleister op zijn wang (geen bloed, gewoon een pleister). Mama vliegt op hem af en knuffelt hem (armen om hem heen, geen armen door de rugzak).
- **MAMA:** "You could have been killed!"

**19a2 · MEDIUM · 5 s**
Papa slaat een arm om hen allebei heen. Oma zet een bord pannenkoeken op tafel, bij opa's lege stoel.
- **OMA:** "He would have been proud. He'd also be eating your pancake."
- Iedereen lacht zachtjes.

**19b · MEDIUM · 3 s**
Het broertje zit aan tafel met een pannenkoek. Hij kijkt op naar zijn grote broer. Glimlacht.

**19c · CLOSE · broertje · statisch · 4 s**
Dan valt de glimlach weg. Zijn ogen gaan langzaam omhoog, naar de lucht boven het hoofd van zijn broer. Hij knippert. Hij kijkt nog een keer. (Dezelfde blik als in 1f, 3c en 17a.)
- **Muziek:** weg. Alleen de klok.

**19d · CLOSE · hij · statisch · 3 s**
Hij verstijft. Kijkt naar zijn broertje. Dan naar opa's lege stoel.

**19e · CLOSE · broertje · statisch · 3,5 s**
- **BROERTJE (stil verbaasd, gewone stem, niet fluisteren):** "...why is your number so small?"
- **Let op:** het getal boven de held tonen we níet. Alleen het gezicht van het broertje, kijkend omhoog.

**19f · ZWART · 1 s**
Hard naar zwart. Eén hartslag.

# OUTRO (14:00-14:15)

## Scène 20 · Eindvraag (14:00-14:15)

**20a · ZWART met witte tekst · 8 s**
- **VO:** "If you could see your number... would you want to know? Tell me in the comments. And subscribe."
- **Beeld:** in het midden verschijnt **???**, wit, gloeiend, pulseert één keer.

**20b · EINDSCHERM · 7 s**
Nachtblauwe achtergrond met de glans-gloed, ruimte voor 2 eindschermelementen (video + abonneer-knop). Muziek: het thema, zacht. Geen verwijzing naar een volgende video.

---

# Bijlagen

## A. Sets

Elke set is **dicht**: vier muren, vloer en plafond binnen (ook als de camera niet omhoog kijkt, ivm reflecties en licht), buiten in elke kijkrichting gebouwen, bomen of een achtergrondkaart. Ramen hebben een buitenbeeld. Zie G.10 voor de setcheck.

| Set | Status | Scènes | Aandachtspunten |
|---|---|---|---|
| **Kruispunt bij school** (zebrapad, verkeerslichten met werkende rood/groen, bushokje, bomen, 4 hoeken bebouwd) | variant van straat video 2 + nieuwe hoek | 0, 8, 18 | Twee lichtstanden: late middag (0, 18) en grijze ochtend (8). Zelfde camerastandpunten 0b/18e en 0c/18f. |
| Slaapkamer | hergebruik | 3, 17 | Ochtend + nacht met bureaulamp. Plafond nodig (3c kijkt omhoog). |
| Keuken met eettafel voor 7 | hergebruik | 4, 9e, 15b, 19 | Opa's vaste stoel aan het hoofd. Pannenkoekenpan, spatel, bord, sap. |
| Straat met huizen + hek | hergebruik video 2 | 5, 7 | Hek met kraai, avond en ochtend. |
| Schoolwc met spiegels | **nieuw, klein** | 6 | Echte spiegels, tegels, plafond met tl. |
| Klaslokaal | hergebruik video 1 | 6 | 30 leerlingen, bord met krijt. |
| Park met pad en boom met losse tak | hergebruik video 3 | 9a | Tak als los object. |
| Zwembadrand (buiten) | **nieuw, klein** | 9c | Tegels, water, hek, ligstoelen. |
| Supermarkt | hergebruik video 3 | 9d | Stapel blikken als rigid body. |
| Woonkamer met tv | hergebruik | 9f-g | Tv-scherm met nieuwsbeeld (emissie). |
| TV-studio | hergebruik video 1 | 9f, 12e (op de tv) | Onderbalk MYSTERY KID SAVES 7 / 300. |
| Dokterspraktijk | hergebruik video 1 | 10a-c | |
| **Steiger aan het meer** (riet, bos rondom, water met golfjes) | **nieuw** | 1b, 10, 15a, 15e | Zomer, eind zomer, mist. Vaste camera voor 10d/15a. |
| Schoolplein + gymzaal van buiten (plat dak) | variant school video 1 | 1a, 11, 13g-j | Dak moet kunnen instorten (los gemodelleerd). |
| Gymzaal binnen (300 stoelen, podium, plafond met lichtkoepels, brandalarm) | variant 06_gymzaal | 13a-f | Doorbuigend plafondpaneel. |
| Kamer directeur | **nieuw, klein** | 12a-b | Raam met uitzicht op het plein. |
| Kantine | hergebruik video 3 | 12d | |
| Ziekenhuiskamer | **nieuw, klein** | 14 | Bed, monitor, gordijn, raam. |
| Opa's woonkamer | **nieuw** | 15d, 16 | Leunstoel, haardvuur, lamp, boeken. Avond en ochtend. |
| Begraafplaats | **nieuw** | 17a-b | Motregen, paraplu's. |
| Etalage met tv | klein | 1c | Mag een detail van de straat-set zijn. |
| Skatepark met helling naar de weg | hergebruik video 3 | 9d1-9d4 | Auto met zichtbare chauffeur. Gras naast het pad voor de zachte val. |
| Gymzaal binnen, leeg (overdag) | variant van gymzaal | 11e-11f | Gele emmer onder een lek, waterplek en doorgezakte plafondplaat. Zelfde set als 13a, zonder stoelen. |
| Gang bij opa's slaapkamer | klein, in het huis | 15e3 | Deur op een kier, gang donker, telefoonlicht op zijn gezicht. |
| Steiger, leeg (DAY 38) | zelfde set als 10 | 16g | Opa's klapkrukje met zijn vissershoed erop. Grijs weer, geen hengel. |

## B. Cast

- **Hoofdpersonage** (14): hoodie, rugzak. Variant met pleister (19), ziekenhuishemd (14), zwart pak (17a).
- **Gezin:** mama, papa, oma, **opa** (76, grotere rol dan ooit: vissershoed en bodywarmer voor de steiger, vest voor binnen), **broertje** (7, dinopyjama in 3c, daarna gewone kleren).
- **Vaste cast:** beste vriend (koptelefoon, telefoon), pestkop, nieuwslezeres, wetenschapper als **dokter** (man, witte jas, stethoscoop), gymleraar als **wiskundeleraar** (overhemd).
- **Nieuw:** schooldirecteur (vrouw, bril, vest), man in pak met koffie (8), moeder met kinderwagen + baby (9a), jongen bij het zwembad (9c), oude man in de supermarkt (9d), conciërge met bezem (11b), bestelwagenchauffeur (0, 18), scooterbestuurder met helm (8), vrouw met hond, postbode op fiets (5a).
- **Dieren:** goudvis in kom, kraai (video 2), hond (video 3), visje in het net.
- **Figuranten:** 300 leerlingen voor schoolplein/gymzaal (instancing van figurant_a-f met kleurvariatie, schooltassen, verschillende lengtes; elke figuur een eigen tijdsverschuiving).

## C. Props en attributen

| Prop | Waar | Bijzonder |
|---|---|---|
| **Getallen boven hoofden** | overal | zie "De getallen"; per personage een tekstobject met smoothing |
| Goudviskom + goudvis | 3 | glas met breking, water |
| Pannenkoekenpan, spatel, pannenkoeken, borden, sapkan, glazen | 4, 9e, 15b | pannenkoek die echt flipt |
| Krant van opa | 4, 19 | ligt in 19 op de lege stoel |
| Koptelefoon + telefoon van de vriend | 0, 5, 18 | koptelefoon vliegt af in 18h |
| Rugzak | 3-5, 18 | wiebelt na (secundaire beweging) |
| Koffiebeker | 8 | valt, deksel springt eraf, plas koffie |
| Kinderwagen + losse tak | 9a | |
| Stapel blikken | 9d | rigid body |
| Vishengel met lijn, dobber, schepnet, klapkrukje | 10, 15 | lijn als curve (G.6) |
| Stethoscoop | 10 | |
| Brandalarmknop met glaasje | 13 | |
| Instortend dak in delen | 13h | vooraf gebroken |
| Zelfgemaakte tekening van het broertje | 14 | papier buigt |
| Oude foto's (zwart-wit opa op zijn 14e) | 15d | **plant:** dezelfde jongen als in de brief |
| Leunstoel + gevouwen deken | 16 | |
| Envelop + brief in handschrift | 17 | tekst Engels, regel voor regel zichtbaar |
| Paraplu's, bloemen, grafsteen | 17a | grafsteen zonder naam in beeld |
| Bestelwagen (chauffeur!), scooter (bestuurder!) | 0, 8, 18 | nooit rijden zonder zichtbare bestuurder |
| Pleister | 19 | |
| Foto van een meisje op een fiets (kleur, vergeeld, 1966) | 15d | **plant:** komt terug in de brief (17g2) |
| Gele emmer + doorgezakte plafondplaat | 11e-11f | water druppelt in een vaste cyclus, geen spetters door de emmer heen |
| Telefoonschermen: weerbericht RECORD RAINFALL + schoolagenda ASSEMBLY DAY 13 | 11h, 15e3 | Engelse tekst, strak, niet flikkeren |
| Stukje vislijn met de knoop | 16a2 | lijn als curve (G.6) |
| Opa's vissershoed op het krukje | 16g | dezelfde hoed als in 10 |

## D. Planten en oogsten

| Geplant | Terug |
|---|---|
| Cold open: vriend 0, 3:58 PM, "what it's going to cost you" (0a-0d) | 18e-18k |
| Opa's wetende blik bij het ontbijt (4e) | 17d ("I saw it in your eyes at breakfast") |
| Hartslag-trap: 8h, 9b, 9d3, 13k | 14b, 17f-17g, 18k |
| "Some numbers aren't a problem to fix" + bijna-onthulling (10f-10h) | 17d-17h |
| Zwart-witfoto van opa op zijn 14e (15d) | 17d ("since I was fourteen") |
| "Like you knew" (16d) | 17d |
| Broertje kijkt geschrokken omhoog (1f) | 19c-19e |
| Superheld-tekening "1,000,000" (14d) | 19e (het getal is juist klein) |
| Opa's lege stoel + krant (19) | slotbeeld |
| Opa's hand naar zijn eigen borst (9g2), "Go easy on that heart, champ" (14e2) | 17f ("I know that skip") |
| "Let him go. He's got plenty of time." bij het visje (10h2) | 17h ("I spent them. Every one on purpose.") |
| Foto van het meisje op de fiets, "I was in the way" (15d-15d2) | 17g2 (de stuurbocht van oma, 1966) |
| De knoop die eindelijk lukt (16a2), lege krukje met hoed (16g) | 17h2 ("Spend your days on purpose") en 18d3b ("On purpose.") |
| Broertje kijkt boven hoofden: goudviskom (3c), papa (9e2), oma (17a) | 19 (hij kan het ook) |
| "It skipped your father. It didn't skip you." (17h2) | 19 (het slaat niet over: ook het broertje) |
| Regel 4, de pestkop zakt live naar 0 (9d1) | 11a (iedereen 4) en 18a (de vriend valt live naar 0) |

## E. Wetenschapsmomenten (4x, elk met een andere inleiding, elk met 2 bronnen)

1. **Een mens heeft gemiddeld ongeveer 27.000 dagen** (6c, "This part is real."). Wereldwijde levensverwachting 73,3 jaar in 2024 = 26.770 dagen. Bronnen: VN World Population Prospects 2024; WHO World Health Statistics.
2. **Vlindereffect: in 1961 rondde meteoroloog Edward Lorenz één getal af in een weermodel en de hele voorspelling veranderde** (8i, "Here's the crazy part."). Bronnen: Lorenz (1963) "Deterministic Nonperiodic Flow", J. Atmos. Sci.; MIT Technology Review / MIT News over Lorenz en de chaostheorie.
3. **Sinds 1693 schatten verzekeraars je levensduur: Edmond Halley maakte de eerste sterftetabel** (12c, "Here's the thing."). Bronnen: Halley (1693), Philosophical Transactions of the Royal Society; Royal Society / Institute and Faculty of Actuaries over de geschiedenis van sterftetabellen.
4. **Elke 2,5 cm regen op een plat dak = ongeveer 25 kg per m²** (13b, "This part is real."). 1 mm water op 1 m² = 1 liter = 1 kg. Bronnen: ASCE 7 (regenbelasting en "ponding" op platte daken); FEMA P-424/FM Global over daken die instorten door water.
5. **Je hart klopt ongeveer 100.000 keer per dag** (14b, "This part is real too."). 70 slagen/min × 1.440 min = 100.800. Bronnen: American Heart Association; Cleveland Clinic.

## F. Titel, thumbnail en hoofdstukken

- **Titel:** *What IF You Could See How Many Days Everyone Has Left?* (55 tekens)
- **Testvarianten:** *What IF Everyone Had A Countdown Above Their Head?* · *What IF You Could See Everyone's Days Left? (Day 1 to Day 41)*
- **Thumbnail (3 varianten voor Test & compare), altijd = shot 0a/0b:**
  1. Links zijn gezicht groot, doodsbang, rood licht. Rechts de vriend op het zebrapad met een groot rood gloeiend **0** boven zijn hoofd. Tekst: **0 DAYS LEFT**.
  2. Zelfde compositie, maar met opa en een amber **34**. Tekst: **34 DAYS**.
  3. Schoolplein van boven met overal **4**, zijn gezicht klein in het midden. Tekst: **4 DAYS LEFT**.
  Fel, hoog contrast, valt op in donkere modus, max 3 elementen, 1280x720, < 2 MB.
- **Hoofdstukken:**
  - 0:00 Zero Days Left
  - 0:38 Day 1
  - 1:00 Grandpa's Number
  - 2:49 The First Zero
  - 3:36 Mystery Kid
  - 4:30 Trying To Fix It
  - 5:27 Everyone Has 4 Days
  - 7:11 The Storm
  - 9:03 The Last Weeks
  - 10:09 The Last Night
  - 11:03 The Letter
  - 12:36 3:58 PM

## G. Bewegings- en kwaliteitsregels (voor de animatiethread, geldt voor elk shot)

niels' wens 9 nov: soepelere en realistischere bewegingen, voeten vast als je staat, geen stotteren, geen incomplete sets, en alle eerder gemaakte fouten vermijden. Elke regel hieronder heeft een **meetbare check**, zodat hij vóór de render automatisch in `qc.txt` komt.

**G.1 Leven (nooit bevroren)**
- Iedereen in beeld ademt (borst/schouders, cyclus 3-4 s), knippert om de 2-5 s (onregelmatig, niet synchroon met anderen), en verplaatst om de 3-6 s het gewicht of kantelt het hoofd.
- Wie praat: lipsync met mondvormen, plus kleine hoofdknikjes op de klemtonen.
- *Check:* STIL_PERSONAGE (een figuur in beeld beweegt > 2 s minder dan 2 mm).

**G.2 Bogen, timing en overgangen (soepel)**
- Alle sleutels met Bezier ease-in/ease-out; geen lineaire interpolatie behalve bij voertuigen op constante snelheid.
- Elk gebaar heeft anticipatie (2-4 frames de andere kant op), actie, overshoot (5-10%) en uitrijden (6-10 frames).
- Bewegingen volgen bogen (polsen en hoofd bewegen in een boog, niet in een rechte lijn).
- Overlap: hoofd, romp, armen en handen beginnen niet tegelijk; handen lopen 2-4 frames na.
- *Check:* SCHOK (bestaande check, drempel 200 m/s²) op elk bot, niet alleen op de wortel.

**G.3 Kijken en draaien**
- Eerst de ogen (2 frames), dan het hoofd (4-6 frames), dan de schouders/romp. Bij een draai van > 90° stapt het figuur mee met de voeten.
- Ogen knipperen bij een grote hoofddraai.

**G.4 Voeten (nieuw, belangrijkste punt)**
- **Staan:** beide voeten staan plat op de vloer en **blijven op hun plek** (foot lock). Voet-IK-doelen worden in wereldruimte vastgezet zolang de voet draagt. Gewichtsverplaatsing gebeurt in de heup, niet door de voeten te laten schuiven.
- **Lopen/rennen:** staplengte × stapfrequentie = snelheid van de wortel. Elke voet staat tijdens de standfase stil op de grond (geen glijden). Knieën altijd gebogen (geen stokbenen), hiel-teen-afwikkeling, heup gaat op en neer (2-4 cm) en draait mee.
- **Zitten/opstaan:** voeten eerst plaatsen, gewicht naar voren, dan pas omhoog. Billen raken de zitting.
- **Hoogte:** de vloer wordt per set gemeten (raycast omlaag), niet aangenomen. Trap, stoep en matras krijgen hun eigen hoogte.
- *Checks (nieuw):* **VOET_ZWEEFT** (dragende voet > 1,5 cm boven de grond), **VOET_DOOR_VLOER** (> 1 cm eronder), **VOET_GLIJDT** (dragende voet beweegt > 1 cm over de grond), **STOKBEEN** (kniehoek > 172° tijdens lopen).

**G.5 Contact en clipping**
- Handen pakken echt vast (vingers om het object, object aan de hand via Child Of met sleutel op het moment van pakken). Niets zweeft, niets valt door een tafel.
- Geen arm door een lijf, hoofd of tafel; geen buik door een tafel; geen figuur door een ander figuur, voertuig of meubel.
- **Nooit** uitgerekte armen of meegroeiende props (arm-stretch uit). Zet figuren dichtbij genoeg om te reiken. `S.reach(ch, t-0.4, side, None, 0.0)` vóór de eerste echte reach (valkuil video 4).
- *Checks:* BOTSING, DOOR_ELKAAR, ARM_DOOR_HOOFD, PROP_ZONDER_PERSOON (bestaand).

**G.6 Secundaire beweging**
- Haar, capuchon, rugzak, koptelefoondraad, opa's deken, de vislijn en papier lopen na (spring-bones of een simpele lag-constraint, 3-6 frames vertraging).
- Kleding plooit bij zitten en buigen (bestaande stofplooien glans 2).

**G.7 Getallen boven de hoofden (nieuw)**
- Tekstobject niet direct aan het hoofdbot hangen, maar aan een lege volger die het hoofd volgt met smoothing (bv. gemiddelde over 3 frames of een damped spring), zodat kleine trillingen van het hoofd het getal niet laten schokken.
- Track To naar de actieve camera; bij een camerawissel geen draaisprong (de rotatie hoort bij de nieuwe camera vanaf frame 1 van het shot).
- *Checks (nieuw):* **GETAL_SCHOKT** (getal versnelt > 150 m/s²), **GETAL_UIT_BEELD** (getal van het hoofdpersonage in focus valt buiten beeld), **GETAL_ONDER_HUD** (overlapt met de HUD-hoek).

**G.8 Camera**
- Niet elk shot hoeft te bewegen. Shots met **statisch** in de kop staan echt stil (statief, geen drift): dat zijn de emotionele momenten, de stiltes en de brief, daar werkt stilte beter dan beweging. Alle andere shots mogen licht bewegen (drift, push-in, dolly), altijd met ease-in/out, nooit een plotse start of stop.
- **Muziek** volgt het beeld, niet andersom: geen muziek forceren. Stille shots (0e, 10c, 13i, 16e, 16f, 17h1, 19d) zonder of met heel zachte muziek; de piano begint pas bij 17g2.
- Nooit door een muur, paal of object (CAMERA_DOOR_OBJECT). Minimaal 0,75 m tot een hoofd. Hoofden volledig in beeld.
- Handheld = lichte, gesmoothde ruis (amplitude 1-2 cm, frequentie < 2 Hz), geen trillende stap-ruis.
- Motion blur aan (EEVEE, 1 stap, shutter 0,5), zodat snelle bewegingen vloeiend ogen in plaats van te haperen.

**G.9 Timing en stem**
- Shots meestal 2-5 s. Een shot is nooit korter dan de tekst die erin gesproken wordt: **woorden ÷ 2,6 + 0,35 s per pauze ("..." of " -- ") + 0,6 s uitloop**. Controle: `timing.py` (in v1.1 nagerekend, 0 shots te kort).
- Praatshots langer dan 6 s (6a, 6f, 8i, 9d3, 10e, 10h2, 11c2, 12a, 12c, 12d4, 12e, 13b, 14b, 14d2, 16d2, de brief 17d-17h2, 20a-b) krijgen een trage camerabeweging óf een tussenshot (cutaway) dat de animatiethread zelf mag toevoegen, zolang de stem niet verschuift. De brief en 9d3 blijven statisch.
- Een shot loopt altijd door tot minstens 0,6 s na de laatste zin (Scene4.finish verlengt automatisch, QC STEM_AFGEKAPT).
- Alles 30 fps, één framerate voor de hele video.

**G.10 Sets compleet (nieuw: automatische setcheck)**
- Voor elke camera in elke scène: raycast een raster van 64×36 stralen door het beeld. Raakt een straal niets (lege wereld) of de binnenkant van een vlak (achterkant/normaal verkeerd), dan **SET_GAT** met een still waarop het gat rood is.
- Coplanaire vlakken (stoepen op weg, kleed op vloer) altijd 2-5 mm hoger zetten (zwarte vlakken in video 3).
- Elke set heeft een plafond binnen en een achtergrond in alle richtingen buiten. Ramen hebben een buitenbeeld.

**G.11 Licht en beeld**
- Belichting 0 tot +0,3, bloom aan, vignet licht. Hoogste luma in elk shot boven 230 (geen dof beeld).
- Randlicht beweegt mee met het personage (meereizend licht uit video 3), nooit een stilstaand randlicht waar iemand doorheen loopt (LICHT_IN_HOOFD).
- Geen witte flitsen tussen shots (FLITS/WIT in videocheck).

**G.12 Geluid**
- Stem altijd centraal. Muziek en sfx eronder (ducking), nooit een plotse piek: alarm (13f), dak (13h) en remmen (18h) met een fade-in van 0,3-1 s en onder de stem.
- Eindmix -14 LUFS, piek -1 dBTP.

**G.13 Volgorde per scène (vast)**
script → bouw → `qc.txt` schoon (inclusief de nieuwe checks) → kijkversie (WORKBENCH) bekijken op beweging → echte render → `videocheck.py` → pas dan naar de montage.

## H. Verbeteringen ten opzichte van video 1-4 (voorstel, nieuw)

1. **Foot lock + voetchecks** (G.4): de grootste zichtbare winst; lost "zwevende" en "schaatsende" voeten op.
2. **Echte loop- en renncycli als basis:** één goede, handgemaakte loop- en renncyclus per bouw (kind, volwassene, oud) als NLA-actie, aangepast op snelheid, in plaats van per scène opnieuw sleutelen. Optioneel: gratis motion-capture-cycli (bijv. Mixamo, royaltyvrij) hertargeten naar de chibi-rig en dan bijwerken.
3. **Bewegingssmoothing als laatste stap:** na het bouwen van een scène een automatische F-curve-pass (Bezier, auto-clamped handles, dubbele of te dicht op elkaar staande sleutels samenvoegen). Dat haalt het meeste stotteren weg.
4. **Motion blur standaard aan** (G.8).
5. **Setcheck met raycasts** (G.10) vóór er één frame gerenderd wordt.
6. **Getallen als gesmoothde 3D-billboards** (G.7) in plaats van compositor-overlays, zodat ze nooit glitchen.
7. **Een emotionele kernrelatie** (opa) in plaats van alleen spektakel; elke 60-90 s nog steeds een nieuw probleem.
8. **Figuranten met tijdsverschuiving** in menigtes (13a), zodat niemand synchroon beweegt.

## I. Controle tegen de checklist

- Frame 1 = gevaar + hoofdpersoon (zijn gezicht, vriend met 0, aanstormende wagen), eerste woord op frame 1. Thumbnail en titel beloven precies dat beeld.
- De titel in andere woorden in de eerste 15 s ("see a number above everyone's head... Days. How many they have left."). Titelkaart op 0:30.
- Geen uitleg in de eerste minuut: de regels komen als beelden (goudvis, broertje, spiegel).
- Inzet al op ~1:16: opa heeft 34 dagen.
- Elke 60-90 s een nieuw probleem: kraai (2:36), eerste nul (2:49), pestkop live naar 0 (3:51), opa's getal beweegt niet (4:30), iedereen 4 (5:27), niemand gelooft je (6:08), storm (7:11), ziekenhuis en de prijs (8:15), opa's laatste weken (9:03), de laatste avond (10:09), de brief (11:03), vriend 0 (12:36), broertje (13:36). Langste gat: 72 s.
- Abonneeroproep op 8:38 van 14:15 (61%), in de verteltoon, na het stille moment van de tekening (14c), niet erdoorheen.
- Outro: eindvraag + één abonneeroproep, minder dan 20 woorden. Geen verwijzing naar de volgende video.
- 5 wetenschapsmomenten met verschillende inleidingen, elk met 2 bronnen.
- Geen bloed, geen geweld, geen lichamen in beeld. Elk voertuig heeft een zichtbare bestuurder.
- Elke zin past in zijn shot (`timing.py`, 0 te kort). Lange praatshots: zie G.9.
- Grote momenten zonder verteller: 0e, 10c, 13i, 14c (alleen het broertje), 16e, 16f (5 s), 17h1, 19d.
- HUD: DAY-teller, nooit achteruit (cold open = flash-forward naar 41), weg bij flash-forwards, titel, brief en slot.
- Engelse tekst in beeld (geen OPA/OMA: GRANDPA/GRANDMA als er al namen in beeld komen).

## J. Proefshots en vaste kwaliteitscheck (nieuw in v1.1)

**J.1 Proefshots vóór de productie.** Deze vijf shots zijn het moeilijkst. De animatiethread maakt ze eerst als losse proef (kijkversie + één echte render) en pas als ze goed zijn begint de rest:

| Proef | Wat testen | Goed als |
|---|---|---|
| 13j: 300 getallen die tegelijk omhoog rollen | snelheid van de render en leesbaarheid | Getallen alleen bij figuren binnen ~25 m van de camera; verder weg een zachte gloed zonder cijfers. Rendertijd per frame niet meer dan 2x een gewoon shot. |
| 18h: de redding op het zebrapad | timing van sprint, greep en remmende bestelwagen | Voeten vast tijdens de afzet, de hand pakt echt de capuchon/arm, chauffeur zichtbaar, geen clipping met de wagen. |
| 1e en 8f: snel rollende getallen | leesbaarheid | Het eindgetal staat minstens 1 s stil en scherp, geen flikkeren, geen trillen. |
| 11b: getallen tijdens een camerapan | getallen blijven naar de camera gedraaid | Geen schokken of springen (GETAL_SCHOKT 0). |
| 13h: het dak dat instort | brokstukken en stof | Geen stukken door de vloer, niemand geraakt, geluid met fade-in onder de stem. |

**J.2 Vaste check per shot (altijd, ook als `qc.txt` schoon is).** Kijk elk shot één keer op halve snelheid en vink af:

1. **Handen:** pakken echt vast, geen vingers door objecten, geen uitgerekte armen.
2. **Voeten:** staan stil als iemand staat, geen glijden, zweven of door de vloer.
3. **Gezichten:** knipperen, kijkrichting klopt (ogen eerst, dan hoofd), lipsync op de klemtonen.
4. **Getallen:** juiste waarde volgens de Getallen-tijdlijn, juiste kleur, niet schokken, niet onder de HUD. Nooit een getal boven het hoofdpersonage.
5. **HUD:** juiste DAY, weg in flash-forwards, brief en slot.
6. **Set:** geen gaten, camera niet door muren (setcheck SCHOON).
7. **Stem:** zin past, 0,6 s uitloop, niet afgekapt, niet fluisteren.
8. **Stil shot = stil:** shots met "statisch" hebben echt geen camerabeweging.

