"""Bouwt de kennisbank van de coach: hq/public/kennis.json.

Bronnen:
- /mnt/project-files/kennis/  (hier komt de YouTube A-Z Guide NL/EN: .pdf, .md of .txt)
- vaste Driftmark-documenten (werkwijze, checklist, lessen uit video 1-3)
Elk fragment krijgt metadata: doc, taal, hoofdstuk, onderwerp, tekst.
Gebruik: python3 hq/automation/kennis.py
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public', 'kennis.json')
MEM = '/tmp/claude/memory/team/silo'
PF = '/mnt/project-files'

# (pad, documentnaam, onderwerp)
VAST = [
    (f'{PF}/werkwijze/werkwijze_3d_youtube_kanaal.md', 'Driftmark werkwijze', 'productie'),
    (f'{PF}/uploads/hearth/0e5daf08-8038-4efc-ae83-0aee5be3656c', 'Checklist volgende video', 'kwaliteit'),
    (f'{MEM}/veelgemaakte-fouten.md', 'Veelgemaakte fouten video 1-3', 'kwaliteit'),
    (f'{MEM}/lessen-video1.md', 'Lessen video 1', 'retentie'),
    (f'{MEM}/lessen-video2.md', 'Lessen video 2', 'retentie'),
    (f'{MEM}/retentie-video1.md', 'Retentie video 1', 'retentie'),
    (f'{MEM}/ifology-analyse.md', 'Analyse IFOLOGY (voorbeeldkanaal)', 'nicheonderzoek'),
    (f'{MEM}/kanaal-groei.md', 'Kanaalgroei Driftmark', 'groei'),
    (f'{MEM}/tags-vidiq.md', 'Tags en vidIQ', 'titels'),
    (f'{MEM}/shorts-pipeline.md', 'Shorts-werkwijze', 'shorts'),
    (f'{MEM}/geluidsmix.md', 'Geluidsmix', 'voice-over'),
    (f'{MEM}/stijl-en-voice.md', 'Stijl en voice', 'voice-over'),
    (f'{MEM}/render-look-glans.md', 'Render-look glans', 'editing'),
    (f'{MEM}/muziek-voorkeur.md', 'Muziek', 'editing'),
    (f'{MEM}/thumbnail-video3.md', 'Thumbnail video 3', 'thumbnails'),
]

ONDERWERPEN = {
    'niche': 'nicheonderzoek', 'doelgroep': 'doelgroep', 'audience': 'doelgroep', 'idee': 'video-ideeën', 'idea': 'video-ideeën',
    'titel': 'titels', 'title': 'titels', 'hook': 'titels', 'thumbnail': 'thumbnails', 'script': 'scripts', 'story': 'scripts',
    'voice': 'voice-over', 'stem': 'voice-over', 'edit': 'editing', 'montage': 'editing', 'retentie': 'retentie', 'retention': 'retentie',
    'ctr': 'statistieken', 'analytics': 'statistieken', 'monet': 'monetisatie', 'rpm': 'monetisatie', 'sponsor': 'monetisatie',
    'short': 'shorts', 'team': 'teammanagement', 'agent': 'teammanagement',
}


def lees(pad):
    if not os.path.exists(pad):
        return None
    with open(pad, 'rb') as f:
        kop = f.read(5)
    if kop.startswith(b'%PDF'):
        try:
            return subprocess.run(['pdftotext', '-layout', pad, '-'], capture_output=True, text=True, timeout=120).stdout
        except Exception:
            return None
    with open(pad, encoding='utf-8', errors='ignore') as f:
        t = f.read()
    return re.sub(r'^---\n.*?\n---\n', '', t, flags=re.S)  # frontmatter eraf


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


def knip(doc, tekst, taal_, standaard, soort='driftmark'):
    stukken, hoofdstuk, buf = [], 'Algemeen', []

    def klaar():
        t = re.sub(r'\s+\n', '\n', '\n'.join(buf)).strip()
        if len(t) > 60:
            for i in range(0, len(t), 1100):
                deel = t[i:i + 1200]
                stukken.append({'doc': doc, 'soort': soort, 'taal': taal_, 'hoofdstuk': hoofdstuk, 'onderwerp': onderwerp(hoofdstuk + ' ' + deel, standaard), 'tekst': deel})
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


def main():
    alles, bronnen = [], []
    cursus = os.path.join(PF, 'kennis')
    if os.path.isdir(cursus):
        for naam in sorted(os.listdir(cursus)):
            t = lees(os.path.join(cursus, naam))
            if t and t.strip():
                tl = taal(naam, t)
                doc = os.path.splitext(naam)[0]
                s = knip(doc, t, tl, 'algemeen', 'cursus')
                alles += s
                bronnen.append({'doc': doc, 'taal': tl, 'soort': 'cursus', 'fragmenten': len(s)})
    for pad, doc, ond in VAST:
        t = lees(pad)
        if t and t.strip():
            s = knip(doc, t, 'nl', ond)
            alles += s
            bronnen.append({'doc': doc, 'taal': 'nl', 'soort': 'driftmark', 'fragmenten': len(s)})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'gemaakt': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'bronnen': bronnen, 'fragmenten': alles}, f, ensure_ascii=False)
    print(json.dumps({'bronnen': bronnen, 'totaal': len(alles)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    sys.exit(main())
