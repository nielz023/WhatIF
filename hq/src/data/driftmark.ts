// ───────────────────────────────────────────────────────────────
// DRIFTMARK — de ECHTE stand van het project "3D What If Channel".
// Bron: projectgeheugen, /mnt/project-files en repo nielz023/WhatIF.
// Stand: 4 november 2026. Werk dit bestand bij als er iets verandert.
// ───────────────────────────────────────────────────────────────

export const UPDATED = 'donderdag 5 november 2026, 00:15';
const PROJ = 'https://claude.ai/code/project/chan_01LkmukDuDNkj8pXsDu4v8WG';
export const threadUrl = (id: string) => `${PROJ}?thread=${id}`;

export const CHANNEL = {
  name: 'Driftmark',
  handle: '@driftmark3d',
  url: 'https://youtube.com/@driftmark3d',
  slogan: 'A NEW 3D WHAT IF EVERY WEEK',
  format: 'Eén lange 3D What If-video per week (15-18 min) + teaser-shorts (30-45 s)',
  stats: [
    { label: 'Weergaven (28 dagen)', value: '10,4K', note: 'stand 2 nov' },
    { label: 'Nieuwe abonnees (28 dagen)', value: '+16', note: 'stand 2 nov' },
    { label: 'Views per short', value: '1,1-1,5K', note: '10 shorts online' },
    { label: 'Video 1 views', value: '48', note: 'gem. kijkduur 6:40 (26,3%)' },
  ],
  insight: 'Shorts trekken kijkers, maar sturen nog weinig door naar de lange video. In de eerste 30-60 s van video 1 haakt ~2/3 af; daarna blijft 25-35% tot het eind.',
};

export type VideoStatus = 'Online' | 'Klaar' | 'In productie' | 'Idee';
export interface RealStep { label: string; done: boolean; active?: boolean }
export interface RealVideo {
  nr: number; title: string; werktitel: string; status: VideoStatus; lengte: string;
  kern: string; twist: string; youtube?: string; folder: string; script: string; repoBranch: string;
  threads: { title: string; id: string }[]; steps: RealStep[]; notes: string[];
}

const S = (labels: string[], doneUntil: number, active = -1): RealStep[] =>
  labels.map((l, i) => ({ label: l, done: i < doneUntil, active: i === active }));
export const STEPS = ['Idee', 'Verloop', 'Script', 'Stemmen', 'Cast', 'Sets', 'Animatie', 'Render', 'Montage', 'Upload-tekst', 'Shorts', 'Online'];

export const VIDEOS: RealVideo[] = [
  {
    nr: 1, title: 'What IF You Got 2x STRONGER Every Day for 40 Days?', werktitel: 'Elke dag 2x sterker',
    status: 'Online', lengte: '25:24', youtube: 'https://youtu.be/9xSou5t37nk',
    kern: 'Dag 1-5 grappig, dag 10 1000x (geen hand meer schudden), dag 20 een miljoen keer (kraters, nies als schokgolf).',
    twist: 'Rond dag 40 sterker dan de zwaartekracht: je springt en komt nooit meer terug.',
    folder: 'videos/2x-sterker/', script: 'videos/2x-sterker/script_2x_stronger.md', repoBranch: 'claude/project-thread-fd4epr',
    threads: [
      { title: 'Script: elke dag 2x sterker', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WG9VGTvMrkr1r8Ub1qVc4sF3' },
      { title: 'Animeer video 1', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGHoJN16bfuxJYzWRDbGoAtV' },
      { title: 'Analyseer video 1', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGC9FZ2NQY5sy1pnC2J5cgdC' },
      { title: 'Maak 7 shorts uit video 1', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGWQCGZvuCwwBd3cBDe1CZev' },
    ],
    steps: S(STEPS, 12),
    notes: ['Bestand: WHAT IF\\WHAT_IF_2x_STRONGER.mp4', 'Cold open ingekort naar ~23 s', 'Titel mist nog het slot-haakje "(Day 1 to Day 40"', '22 sets, 13 cast-figuren'],
  },
  {
    nr: 2, title: 'What IF You Got 10x FASTER Every Day?', werktitel: 'Elke dag 10x sneller',
    status: 'Klaar', lengte: '12:55',
    kern: 'Elke keer dat hij wakker wordt is hij 10x sneller. Al zijn dagen passen vóór dinsdag 09:00:00, als zijn broertje de kaarsjes uitblaast.',
    twist: 'Wakker blijven is de enige weg ernaartoe. "So… can you stay awake?"',
    folder: 'videos/10x-sneller/', script: 'videos/10x-sneller/script_10x_faster.md', repoBranch: 'claude/project-thread-fdaxoy',
    threads: [
      { title: 'Script: elke dag 10x sneller', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGTcYDSw9V7u6i1kCtSxA2kj' },
      { title: 'Animeer video 2', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WG5C7m5zPrEbj5TGD66gKUQY' },
      { title: 'Titel, beschrijving en tags video 2', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGFt2jvrzboJ4GbK8fbcasKv' },
      { title: 'Maak 7 shorts uit video 2', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGMQM7kDpE2gpgLgMAovYDUq' },
      { title: 'Analyseer video 2', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGRmJDkcSLjBnCebSWiTjgHW' },
    ],
    steps: S(STEPS, 11),
    notes: ['Render klaar (1 nov); niels vindt hem top', 'Upload-tekst: videos/10x-sneller/youtube_upload.md', 'Blijft ongewijzigd; lessen gelden vanaf video 3', '7 shorts V2S1-V2S7 klaar (uploadvolgorde 1,2,7,3,6,5,4)'],
  },
  {
    nr: 3, title: 'What IF There Were NO RULES?', werktitel: 'Geen regels meer',
    status: 'In productie', lengte: '~16:30',
    kern: 'Vredige dag, om 00:00 nucleair alarm op alle schermen: "er zijn geen regels meer". Dag 1, 2, 3… tot jaar 10. Teller "DAY X · RULES: N".',
    twist: 'Jaar 10, middernacht: "TEST COMPLETE … PHASE 2" (twist A).',
    folder: 'videos/geen-regels/', script: 'videos/geen-regels/script_no_rules.md', repoBranch: 'claude/project-thread-maefml',
    threads: [
      { title: 'Verloop video: wat als er geen regels zijn', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WG8Td6Q42bhkx3TbQHgnSwbh' },
      { title: 'Bouw cast en sets voor geen-regels-video', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGCHT43zJaABsdPF4uv4swV5' },
      { title: 'Animeer video 3: geen regels meer', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGTfi8z2mFAQH5Qa5zaASKk1' },
    ],
    steps: S(STEPS, 6, 6),
    notes: ['Scène 1 en 3-9 gebouwd en in de renderwachtrij op de pc', 'Nu bezig: scène 10 (dag 4, de stroom valt uit)', 'Nog te doen: scènes 11-22, teaser, flash-forwards, montage', 'Stemmen in ElevenLabs v4; wetenschapper is een man (Wyatt)'],
  },
];

export interface ShortGroup { title: string; status: string; items: string[]; where: string }
export const SHORTS: ShortGroup[] = [
  { title: 'Teaser-shorts (eigen ideeën)', status: '7 klaar', where: 'WHAT IF\\shorts\\', items: ['SH1 10x sneller per dag', 'SH2 Tijd stopt', 'SH3 1 jaar vooruit kijken', 'SH4 Word wat je aanraakt', 'SH5 10x kleiner per uur', 'SH7 Teleport-kopieën', 'SH8 1.000.000x zwaarder'] },
  { title: 'Shorts uit video 1', status: '7 klaar', where: '/mnt/project-files/v1_0*.mp4', items: ['Titan', 'Sneeze', 'Mug', 'No off switch', 'Catch', 'Lab', 'Space'] },
  { title: 'Shorts uit video 2', status: '7 klaar', where: 'WHAT IF\\shorts\\video2\\', items: ['V2S1 De vuilniswagen', 'V2S2 De sonische knal', 'V2S3 De zwevende regen', 'V2S4', 'V2S5', 'V2S6', 'V2S7'] },
  { title: 'Shorts uit video 3', status: 'Nog niet gestart', where: '-', items: ['Na de montage van video 3'] },
];

export interface Rule { title: string; items: string[] }
export const RULES: Rule[] = [
  { title: 'Retentie (elke video)', items: ['Spannendste beeld binnen 5 s, eerste woord op frame 1', 'Geen rustige opbouw of uitleg in de eerste minuut', 'Thumbnail + titel = wat de eerste seconden tonen', 'Teller/tijdlijn op beeld (Dag 7, 1000x, 10 km)', 'Echte wetenschap ("this part is real") en "jij"', 'Elke 60-90 s een nieuw probleem', 'Twist of donkere kant aan het eind', 'NIET verwijzen naar de volgende video'] },
  { title: 'Kwaliteitscheck animatie', items: ['Tekst/HUD strak, niet flikkeren; weg bij flashbacks', 'Props niet in elkaar, niets zweeft', 'Sets dicht, camera nooit door muren', 'Geen clipping van armen, handen of objecten', 'Bestek echt en goed vast; geen gestrekte arm', 'Rennen met gebogen knieën', 'Shots 3-4 s, max 6 s, ook in de climax', 'Belichting 0 tot +0,3, -14 LUFS'] },
  { title: 'Geluid & render', items: ['Voice-over altijd centraal, sfx/muziek zacht eronder', 'Geen plotselinge harde pieken', 'Renderen in 30 fps (niels maakt er 60 van in CapCut)', 'Glans-look: vinyl-materialen, warm hoofdlicht, oranje/blauw randlicht', 'Eindrenders op niels\' pc (Blender, sneller)'] },
  { title: 'Shorts', items: ['Begin op het moment dat het effect net begint', '30-45 s, cliffhanger aan het eind', 'Nieuwe voice-over, niet letterlijk uit de video', 'Koppelen aan de lange video ("Gerelateerde video")'] },
];

export const CAST = {
  hoofd: 'Naamloos hoofdpersonage (oranje hoodie). Alles overkomt hem. Model: hoofdpersonage/hoofdpersonage.glb',
  gezin: ['Mama', 'Papa', 'Broertje', 'Opa', 'Oma'],
  vast: ['Beste vriend', 'Pestkop', 'Zusje pestkop', 'Wetenschapper', 'Nieuwslezeres', 'Agent/officier', 'Gymleraar'],
};

export const VOICES = [
  ['Verteller', 'zfc8CJQpe8Kqyl0vvCzo'], ['Broertje', 'MeDfWn0QGAwSljXBLc2G'], ['Mama', 'ogwqBH5bbF03DSbNiRNN'],
  ['Papa', 'cCYjmrGZaI86GUJ7F2Nn'], ['Vriend', '3XOBzXhnDY98yeWQ3GdM'], ['Pestkop', 'rHWSYoq8UlV0YIBKMryp'],
  ['Opa', 'HAvvFKatz0uu0Fv55Riy'], ['Oma', 'kkPJzQOWz2Oz9cUaEaQd'], ['Wetenschapper (man)', 'YXpFCvM1S3JbWEJhoskW'],
  ['Agent', '9B2Vd5yQ7rKaqNmzGdy1'], ['Nieuwslezer', 'JJCR1UICgHnHljtvu5uF'],
];

export const TOOLS = [
  { name: 'Blender', use: 'Alle 3D, cast, sets en animatie. Renderen op niels\' pc via Remote Control.' },
  { name: 'ElevenLabs v4', use: 'Alle stemmen. Op ÉÉN plek genereren (kost ~2 credits per teken).' },
  { name: 'Higgsfield', use: 'In Blender op de pc, om cast en sets mooier te maken.' },
  { name: 'CapCut', use: 'Van 30 naar 60 fps en laatste afwerking.' },
  { name: 'NexLev / vidIQ', use: 'Kanaalstats en titels/tags (vidIQ hangt aan een ander Google-account).' },
  { name: 'GitHub nielz023/WhatIF', use: 'Alle bouw- en animatiescripts, per thread een branch.' },
];

export const LINKS = [
  { title: 'Productiehandboek (idee → upload)', url: 'https://claude.ai/artifact/L8mdYWg5dxBJMPSyqgj8j3' },
  { title: 'Afvinklijst volgende video', url: 'https://claude.ai/artifact/C3d9ZTfm2oUG3Cn3g3ebgM' },
  { title: 'Analyse video 2', url: 'https://claude.ai/artifact/EaRkosZvmiP1S64J1n34QQ' },
  { title: 'Verloop video 3', url: 'https://claude.ai/artifact/JGxd7EcrYfWDmDdbZVpWdo' },
  { title: 'Kijkers van shorts naar lange video', url: 'https://claude.ai/artifact/FjDq5ekayWynRHW6NLvJ8R' },
  { title: 'YouTube-kanaal Driftmark', url: 'https://youtube.com/@driftmark3d' },
  { title: 'Repo nielz023/WhatIF', url: 'https://github.com/nielz023/WhatIF' },
  { title: 'Stijlvoorbeeld IFOLOGY', url: 'https://youtube.com/@IFOLOGYFILMS' },
];

export const IDEAS: { title: string; groep: string }[] = [
  { title: 'Teleporteren (ben jij het nog?)', groep: 'Superkracht' },
  { title: 'Vliegen tot 30 km hoog', groep: 'Superkracht' },
  { title: 'Onzichtbaar (en dus blind)', groep: 'Superkracht' },
  { title: 'Tijd 10 seconden terugspoelen', groep: 'Superkracht' },
  { title: 'Elke dag 2x kleiner', groep: 'Jij verandert' },
  { title: 'Elke dag 2x groter', groep: 'Jij verandert' },
  { title: 'Nooit meer slapen', groep: 'Jij verandert' },
  { title: 'Alle gedachten om je heen horen', groep: 'Jij verandert' },
  { title: 'Aarde draait 10x sneller', groep: 'Wereld verandert' },
  { title: 'Zwaartekracht valt 1 seconde uit', groep: 'Wereld verandert' },
  { title: 'Maan 2x zo dichtbij', groep: 'Wereld verandert' },
  { title: 'Zon verdwijnt 1 minuut', groep: 'Wereld verandert' },
  { title: 'Onsterfelijk voor altijd', groep: 'Duister' },
  { title: 'Elke dag 1 jaar jonger', groep: 'Duister' },
  { title: 'Wakker worden en iedereen is weg', groep: 'Duister' },
  { title: 'Tijd stilzetten', groep: 'Kandidaat (sterke short)' },
];

export const NEXT: string[] = [
  'Video 3: scènes 10-22 animeren en renderen op de pc',
  'Video 3: teaser, flash-forwards en eindmontage (-14 LUFS)',
  'Video 3: titel, thumbnail, beschrijving en 7 shorts',
  'Video 2 openbaar zetten en de shorts eraan koppelen',
  'Video 1: slot-haakje in de titel fixen',
  'Onderwerp video 4 kiezen uit de ideeënlijst',
];

// Laatst bekende threads (fallback als de live stand niet te lezen is)
export const ACTIVITY: { title: string; id: string; state: string; last: string; doing?: string }[] = [
 {
  "title": "Animeer video 3: geen regels meer",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGTfi8z2mFAQH5Qa5zaASKk1",
  "state": "working",
  "last": "5 nov 00:42",
  "doing": "Animeert scène 13 (de brug), stills checken"
 },
 {
  "title": "Maak thumbnail voor video 3",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGTs2SxpLDEpFBKs9hyAGKot",
  "state": "working",
  "last": "5 nov 00:38",
  "doing": "Eerste echte opdracht uit Driftmark HQ. Eigen thread start: jongen in rood licht, kruispunt bij nacht, tekst NO MORE RULES."
 },
 {
  "title": "Driftmark HQ (dit hoofdscherm)",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGD3kJS5r6nXrqiC2f5NfjRQ",
  "state": "working",
  "last": "5 nov 00:17",
  "doing": "Live data, echte tijd en alles in het Nederlands."
 },
 {
  "title": "Bouw cast en sets voor geen-regels-video",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGCHT43zJaABsdPF4uv4swV5",
  "state": "blocked",
  "last": "5 nov 00:25",
  "doing": "Cast (37 figuren), dieren en 36 set-varianten klaar in videos/geen-regels/ (cast, dieren, sets + overzicht_sets_no_rules.jpg). Wacht op jouw akkoord."
 },
 {
  "title": "Schrijf titel, beschrijving en tags video 2",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGFt2jvrzboJ4GbK8fbcasKv",
  "state": "blocked",
  "last": "31 okt 15:23",
  "doing": "Wacht op jouw reactie."
 },
 {
  "title": "Bedenk ideeën voor teaser-shorts",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WGS9PSyyns39jsYw5hE9SySp",
  "state": "blocked",
  "last": "28 okt 12:30",
  "doing": "Wacht op jouw reactie."
 },
 {
  "title": "Schrijf werkwijze-document",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WG3mkzfMZCLNKhwkm4CN7Tss",
  "state": "done",
  "last": "4 nov 21:49"
 },
 {
  "title": "Verloop video 3",
  "id": "cmsg_01LkmukDuDNkj8pXsDu4v8WG8Td6Q42bhkx3TbQHgnSwbh",
  "state": "done",
  "last": "4 nov 15:33"
 }
];
