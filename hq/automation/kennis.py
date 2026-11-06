"""Bouwt de kennis van Driftmark HQ: alles wat in het project is opgeslagen.

niels 6 nov 15:33: "Echt letterlijk alles wat in deze chat besproken wordt om goede video's te maken. Letterlijk alle
threads die gebruikt zijn. Ik wil gewoon dat alle informatie die is opgeslagen wordt gestopt in dit programmaatje."

Schrijft naar /mnt/project-files/driftmark-hq/kennis/ (de HQ leest die map via de files-capability):
  geheugen.json    het hele projectgeheugen: de index (MEMORY.md) en elke notitie, letterlijk
  documenten.json  alle artifacts en documenten, bijlagen uit de gesprekken, documentbestanden en beelden van niels
  kennis.json      zoekstukjes voor de coach en het zoekvak: cursus, geheugen, documenten en alle gesprekken
En hq/public/kennis.json: de kleine reserve in de bundel (alleen de cursus en vaste documenten, geen gesprekken
of geheugen, want de bundel staat ook in git).

Bronnen:
- /mnt/project-files/kennis/                    de cursus (pdf, md of txt)
- /tmp/claude/memory/team/silo/                 het projectgeheugen
- vaste documentmappen (scripts, uploadteksten, werkwijze, ideeen, analyses) en de pdf's die niels stuurde
- /mnt/project-files/driftmark-hq/gesprekken/   alle threads en de projectchat (gesprekken.py)
- driftmark-hq/kennis/artifacts.json            de artifacts van het project (gesprekken.py importeer)
Gebruik: python3 hq/automation/kennis.py   (elk uur in de uurronde, na gesprekken.py)
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_BUNDEL = os.path.join(ROOT, 'public', 'kennis.json')
MEM = os.environ.get('HQ_MEM_DIR', '/tmp/claude/memory/team/silo')
PF = '/mnt/project-files'
KENNIS = os.environ.get('HQ_KENNIS_DIR', f'{PF}/driftmark-hq/kennis')
GESPREKKEN = os.environ.get('HQ_GESPREKKEN_DIR', f'{PF}/driftmark-hq/gesprekken')

# vaste documenten die niet in het geheugen staan (pad, documentnaam, onderwerp)
VAST = [
    (f'{PF}/werkwijze/werkwijze_3d_youtube_kanaal.md', 'Driftmark werkwijze', 'productie'),
    (f'{PF}/uploads/hearth/0e5daf08-8038-4efc-ae83-0aee5be3656c', 'Checklist volgende video', 'kwaliteit'),
]
# voor de kleine bundel (zoals voor v35): deze geheugennotities gingen er al in
VAST_GEHEUGEN = [
    ('veelgemaakte-fouten.md', 'Veelgemaakte fouten video 1-3', 'kwaliteit'), ('lessen-video1.md', 'Lessen video 1', 'retentie'),
    ('lessen-video2.md', 'Lessen video 2', 'retentie'), ('retentie-video1.md', 'Retentie video 1', 'retentie'),
    ('ifology-analyse.md', 'Analyse IFOLOGY (voorbeeldkanaal)', 'nicheonderzoek'), ('kanaal-groei.md', 'Kanaalgroei Driftmark', 'groei'),
    ('tags-vidiq.md', 'Tags en vidIQ', 'titels'), ('shorts-pipeline.md', 'Shorts-werkwijze', 'shorts'), ('geluidsmix.md', 'Geluidsmix', 'voice-over'),
    ('stijl-en-voice.md', 'Stijl en voice', 'voice-over'), ('render-look-glans.md', 'Render-look glans', 'editing'),
    ('muziek-voorkeur.md', 'Muziek', 'editing'), ('thumbnail-video3.md', 'Thumbnail video 3', 'thumbnails'),
]
# documentbestanden (gerichte mappen, nooit de hele projectmap doorzoeken)
DOC_GLOBS = ['*.md', 'videos/*/*.md', 'shorts/*.md', 'shorts/*/*.md', 'ideeen/*.md', 'werkwijze/*.md', 'branding/*.md', 'driftmark-hq/*.md']
VIDEO_MAP = {'2x-sterker': 1, '10x-sneller': 2, 'geen-regels': 3, 'nooit-dood': 4}
BEELD = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

ONDERWERPEN = {
    'niche': 'nicheonderzoek', 'doelgroep': 'doelgroep', 'audience': 'doelgroep', 'idee': 'video-ideeën', 'idea': 'video-ideeën',
    'titel': 'titels', 'title': 'titels', 'hook': 'titels', 'thumbnail': 'thumbnails', 'script': 'scripts', 'story': 'scripts',
    'voice': 'voice-over', 'stem': 'voice-over', 'edit': 'editing', 'montage': 'editing', 'retentie': 'retentie', 'retention': 'retentie',
    'ctr': 'statistieken', 'analytics': 'statistieken', 'monet': 'monetisatie', 'rpm': 'monetisatie', 'sponsor': 'monetisatie',
    'short': 'shorts', 'team': 'teammanagement', 'agent': 'teammanagement', 'render': 'animatie', 'blender': 'animatie',
    'scène': 'animatie', 'scene': 'animatie', 'cast': 'cast en sets', 'set': 'cast en sets', 'upload': 'upload',
}
MND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']


def nu():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def lees_json(p, leeg):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return leeg


def schrijf(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    os.replace(tmp, p)


def is_pdf(pad):
    try:
        with open(pad, 'rb') as f:
            return f.read(5).startswith(b'%PDF')
    except OSError:
        return False


def pdf_titel(pad):
    try:
        uit = subprocess.run(['pdfinfo', pad], capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ''
    m = re.search(r'^Title:\s*(.+)$', uit, re.M)
    return m.group(1).strip() if m else ''


def lees(pad):
    if not os.path.exists(pad):
        return None
    if is_pdf(pad):
        try:
            return subprocess.run(['pdftotext', '-layout', pad, '-'], capture_output=True, text=True, timeout=120).stdout
        except Exception:
            return None
    with open(pad, encoding='utf-8', errors='ignore') as f:
        t = f.read()
    return re.sub(r'^---\n.*?\n---\n', '', t, flags=re.S)  # frontmatter eraf


def frontmatter(tekst):
    m = re.match(r'^---\n(.*?)\n---\n?', tekst, re.S)
    if not m:
        return {}, tekst
    kop, meta = m.group(1), {}
    for regel in kop.splitlines():
        mm = re.match(r'^\s*(name|description|type|modified):\s*(.*)$', regel)
        if mm:
            meta[mm.group(1)] = mm.group(2).strip().strip('"')
    return meta, tekst[m.end():]


def taal(naam, tekst):
    n = naam.lower()
    if re.search(r'\b(en|eng|english)\b', n):
        return 'en'
    if re.search(r'\b(nl|ned|dutch|nederlands)\b', n):
        return 'nl'
    nl = len(re.findall(r'\b(de|het|een|en|van|je|niet)\b', tekst[:3000]))
    en = len(re.findall(r'\b(the|and|you|of|to|is|not)\b', tekst[:3000]))
    return 'nl' if nl >= en else 'en'


def onderwerp(tekst, standaard):
    t = tekst.lower()
    tel = {}
    for k, v in ONDERWERPEN.items():
        tel[v] = tel.get(v, 0) + t.count(k)
    beste = max(tel.items(), key=lambda x: x[1])
    return beste[0] if beste[1] >= 2 else standaard


def knip(doc, tekst, taal_, standaard, soort='driftmark', bron=None):
    stukken, hoofdstuk, buf = [], 'Algemeen', []

    def klaar():
        t = re.sub(r'\s+\n', '\n', '\n'.join(buf)).strip()
        if len(t) > 60:
            for i in range(0, len(t), 1100):
                deel = t[i:i + 1200]
                f = {'doc': doc, 'soort': soort, 'taal': taal_, 'hoofdstuk': hoofdstuk, 'onderwerp': onderwerp(hoofdstuk + ' ' + deel, standaard), 'tekst': deel}
                if bron:
                    f['bron'] = bron
                stukken.append(f)
        buf.clear()

    for regel in tekst.splitlines():
        kop = re.match(r'^\s{0,3}(#{1,4}\s+|\d+(\.\d+)*[.)]?\s+)([A-ZÀ-Ý].{2,80})$', regel)
        if kop and len(regel) < 90:
            klaar()
            hoofdstuk = kop.group(3).strip(' #')
        else:
            buf.append(regel)
    klaar()
    return stukken


def mooi(slug):
    t = re.sub(r'[-_]+', ' ', slug).strip()
    return t[:1].upper() + t[1:]


def datum_nl(iso):
    try:
        d = dt.datetime.strptime(iso[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError):
        return ''
    d = d + dt.timedelta(hours=1)  # november: Nederland = UTC+1
    return f'{d.day} {MND[d.month - 1]} {d.year}'


def rel(pad):
    return os.path.relpath(pad, PF)


# ---------------------------------------------------------------- geheugen
def geheugen():
    notities = []
    for pad in sorted(glob.glob(os.path.join(MEM, '*.md'))):
        naam = os.path.basename(pad)
        if naam == 'MEMORY.md':
            continue
        try:
            ruw = open(pad, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        meta, body = frontmatter(ruw)
        slug = meta.get('name') or naam[:-3]
        notities.append({
            'naam': slug, 'bestand': naam, 'titel': mooi(slug), 'beschrijving': meta.get('description', ''),
            'soort': meta.get('type', ''), 'gewijzigd': meta.get('modified') or dt.datetime.fromtimestamp(os.path.getmtime(pad), dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'tekst': body.strip(),
        })
    index = ''
    try:
        index = open(os.path.join(MEM, 'MEMORY.md'), encoding='utf-8', errors='ignore').read().strip()
    except OSError:
        pass
    g = {'gemaakt': nu(), 'index': index, 'notities': notities}
    schrijf(os.path.join(KENNIS, 'geheugen.json'), g)
    return g


# ---------------------------------------------------------------- gesprekken
def gesprekken():
    uit = []
    for pad in sorted(glob.glob(os.path.join(GESPREKKEN, '*.json'))):
        if os.path.basename(pad) == 'threads.json':
            continue
        g = lees_json(pad, None)
        if isinstance(g, dict) and isinstance(g.get('msgs'), list):
            uit.append(g)
    return uit


# ---------------------------------------------------------------- documenten
def doc_naam(pad):
    r = rel(pad)
    stam = os.path.splitext(os.path.basename(pad))[0]
    delen = r.split('/')
    naam = mooi(re.sub(r'-\d{8}T\d{6}-[0-9a-f]+$', '', stam))
    if len(delen) >= 3 and delen[0] == 'videos' and delen[1] in VIDEO_MAP:
        naam += f' (video {VIDEO_MAP[delen[1]]})'
    return naam


def documenten(gespr):
    artifacts, gezien = [], set()
    for a in lees_json(os.path.join(KENNIS, 'artifacts.json'), {}).get('artifacts', []):
        url = str(a.get('url') or '')
        if url.startswith('https://') and url not in gezien:
            gezien.add(url)
            artifacts.append({'title': a.get('title') or url, 'url': url, 'at': a.get('updated_at') or ''})
    bijlagen = []
    for g in gespr:
        for m in g['msgs']:
            for b in m.get('files') or []:
                item = {'name': b.get('name') or '', 'kind': b.get('kind') or '', 'at': m.get('at') or '', 'thread': g.get('id'), 'threadTitle': g.get('title') or '', 'msg': m.get('id')}
                if b.get('href'):
                    item['href'] = b['href']
                    # een artifact- of documentlink uit een gesprek: ook in de lijst met documenten
                    if b['href'] not in gezien and b.get('kind') in ('frame', 'link'):
                        gezien.add(b['href'])
                        artifacts.append({'title': b.get('name') or b['href'], 'url': b['href'], 'at': m.get('at') or '', 'thread': g.get('id'), 'threadTitle': g.get('title') or ''})
                bijlagen.append(item)
    bestanden = []
    for pat in DOC_GLOBS:
        for pad in sorted(glob.glob(os.path.join(PF, pat))):
            if os.path.isfile(pad):
                st = os.stat(pad)
                bestanden.append({'path': rel(pad), 'name': doc_naam(pad), 'size': st.st_size, 'mtime': dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'soort': 'tekst'})
    for pad in sorted(glob.glob(os.path.join(PF, 'kennis', '*'))):
        if os.path.isfile(pad):
            st = os.stat(pad)
            bestanden.append({'path': rel(pad), 'name': os.path.splitext(os.path.basename(pad))[0], 'size': st.st_size, 'mtime': dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'soort': 'pdf' if is_pdf(pad) else 'tekst'})
    beelden, pdf_titels = [], set()
    for pad in sorted(glob.glob(os.path.join(PF, 'uploads', 'hearth', '*')), key=os.path.getmtime):
        if not os.path.isfile(pad):
            continue
        st = os.stat(pad)
        at = dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(pad, 'rb') as f:
            kop = f.read(12)
        if kop.startswith(b'%PDF'):
            t = pdf_titel(pad) or 'Pdf van niels'
            if t in pdf_titels:
                continue
            pdf_titels.add(t)
            bestanden.append({'path': rel(pad), 'name': t, 'size': st.st_size, 'mtime': at, 'soort': 'pdf', 'upload': True})
        elif kop.startswith(b'\x89PNG') or kop[:3] == b'\xff\xd8\xff':
            beelden.append({'path': rel(pad), 'size': st.st_size, 'mtime': at, 'type': 'image/png' if kop.startswith(b'\x89PNG') else 'image/jpeg'})
    d = {'gemaakt': nu(), 'artifacts': artifacts, 'bijlagen': bijlagen, 'bestanden': bestanden, 'beelden': beelden}
    schrijf(os.path.join(KENNIS, 'documenten.json'), d)
    return d


# ---------------------------------------------------------------- zoekstukjes
def cursus_en_vast():
    alles, bronnen = [], []
    cursus = os.path.join(PF, 'kennis')
    if os.path.isdir(cursus):
        for naam in sorted(os.listdir(cursus)):
            t = lees(os.path.join(cursus, naam))
            if t and t.strip():
                tl = taal(naam, t)
                doc = os.path.splitext(naam)[0]
                s = knip(doc, t, tl, 'algemeen', 'cursus', {'type': 'document', 'id': f'kennis/{naam}'})
                alles += s
                bronnen.append({'doc': doc, 'taal': tl, 'soort': 'cursus', 'fragmenten': len(s)})
    for pad, doc, ond in VAST:
        t = lees(pad)
        if t and t.strip():
            s = knip(doc, t, 'nl', ond, 'driftmark', {'type': 'document', 'id': rel(pad)})
            alles += s
            bronnen.append({'doc': doc, 'taal': 'nl', 'soort': 'driftmark', 'fragmenten': len(s)})
    return alles, bronnen


def bundel():
    """De kleine kennisbank in de bundel (zoals voor v35): cursus, vaste documenten en een paar geheugennotities."""
    alles, bronnen = cursus_en_vast()
    for naam, doc, ond in VAST_GEHEUGEN:
        t = lees(os.path.join(MEM, naam))
        if t and t.strip():
            s = knip(doc, t, 'nl', ond)
            alles += s
            bronnen.append({'doc': doc, 'taal': 'nl', 'soort': 'driftmark', 'fragmenten': len(s)})
    os.makedirs(os.path.dirname(OUT_BUNDEL), exist_ok=True)
    with open(OUT_BUNDEL, 'w', encoding='utf-8') as f:
        json.dump({'gemaakt': nu(), 'bronnen': bronnen, 'fragmenten': alles}, f, ensure_ascii=False)
    return len(alles)


WIE = {'niels': 'niels', 'claude': 'Claude', 'keuze': 'Keuze', 'checklist': 'Takenlijst', 'systeem': 'Melding'}


def alles(geh, gespr, docs):
    frag, bronnen = cursus_en_vast()
    # het hele geheugen
    if geh.get('index'):
        s = knip('Geheugen: overzicht', geh['index'], 'nl', 'algemeen', 'geheugen', {'type': 'geheugen', 'id': 'MEMORY'})
        frag += s
        bronnen.append({'doc': 'Geheugen: overzicht', 'taal': 'nl', 'soort': 'geheugen', 'fragmenten': len(s)})
    for n in geh.get('notities', []):
        doc = f"Geheugen: {n['titel']}"
        s = knip(doc, (n.get('beschrijving') or '') + '\n' + n['tekst'], 'nl', 'algemeen', 'geheugen', {'type': 'geheugen', 'id': n['naam']})
        frag += s
        bronnen.append({'doc': doc, 'taal': 'nl', 'soort': 'geheugen', 'fragmenten': len(s)})
    # documenten (scripts, uploadteksten, analyses, pdf's van niels)
    vast = {rel(p) for p, _, _ in VAST}
    for b in docs.get('bestanden', []):
        if b['path'] in vast or b['path'].startswith('kennis/'):
            continue
        t = lees(os.path.join(PF, b['path']))
        if t and t.strip():
            s = knip(b['name'], t, taal(b['name'], t), 'algemeen', 'document', {'type': 'document', 'id': b['path']})
            frag += s
            bronnen.append({'doc': b['name'], 'taal': taal(b['name'], t), 'soort': 'document', 'fragmenten': len(s)})
    # alle gesprekken: elk bericht een eigen stukje (lange berichten in delen), zodat het zoekvak naar dat bericht kan
    for g in gespr:
        titel = g.get('title') or g.get('id')
        doc = 'Projectchat' if g.get('id') == 'projectchat' else f'Thread: {titel}'
        laatste_lijst = max((i for i, m in enumerate(g['msgs']) if m.get('who') == 'checklist'), default=-1)
        n = 0
        for i, m in enumerate(g['msgs']):
            wie, t = m.get('who'), (m.get('text') or '').strip()
            if not t or (wie == 'checklist' and i != laatste_lijst) or (wie == 'systeem' and len(t) < 80):
                continue
            kop = f"{WIE.get(wie, wie)}{' (' + m['author'] + ')' if wie == 'niels' and m.get('author') and m['author'] != 'niels' else ''}, {datum_nl(m.get('at') or '')}"
            if m.get('options'):
                t += '\n' + '\n'.join('- ' + o for o in m['options'])
            for j in range(0, len(t), 1100):
                frag.append({'doc': doc, 'soort': 'gesprek', 'taal': 'nl', 'hoofdstuk': kop, 'onderwerp': onderwerp(t[j:j + 1200], 'gesprek'), 'tekst': t[j:j + 1200],
                             'bron': {'type': 'gesprek', 'id': g.get('id'), 'msg': m.get('id'), 'at': m.get('at')}})
                n += 1
        bronnen.append({'doc': doc, 'taal': 'nl', 'soort': 'gesprek', 'fragmenten': n})
    k = {'gemaakt': nu(), 'bronnen': bronnen, 'fragmenten': frag}
    schrijf(os.path.join(KENNIS, 'kennis.json'), k)
    return k


def main():
    geh = geheugen()
    gespr = gesprekken()
    docs = documenten(gespr)
    k = alles(geh, gespr, docs)
    nb = bundel()
    soorten = {}
    for f in k['fragmenten']:
        soorten[f['soort']] = soorten.get(f['soort'], 0) + 1
    print(json.dumps({
        'geheugen': len(geh['notities']), 'gesprekken': len(gespr), 'berichten': sum(len(g['msgs']) for g in gespr),
        'artifacts': len(docs['artifacts']), 'bijlagen': len(docs['bijlagen']), 'bestanden': len(docs['bestanden']), 'beelden': len(docs['beelden']),
        'fragmenten': len(k['fragmenten']), 'per_soort': soorten, 'bundel_fragmenten': nb,
        'kb': {n: round(os.path.getsize(os.path.join(KENNIS, n)) / 1024) for n in ('geheugen.json', 'documenten.json', 'kennis.json')},
    }, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
