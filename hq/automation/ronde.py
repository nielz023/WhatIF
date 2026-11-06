#!/usr/bin/env python3
"""Eén automatiseringsronde van Driftmark HQ.

Gebruik: python3 ronde.py <abonnees> <weergaven> <video's>
(cijfers van vidIQ vidiq_user_channels, kanaal DriftMark UCJhUg9hdXlhRRc7GBU_nRgg)

- werkt status.json bij (youtube-cijfers, updated)
- controleert de taken: 'working' zonder update > 6 uur = waarschuwing
- schrijft de documenten voor de database naar /tmp/hq-ronde/ (state, engine, stat, log)
  die daarna met ArtifactData batch (file_path) in het HQ-artifact gezet worden.
"""
import json, sys, os, datetime as dt

def _schrijf(pad, data):
    """In één keer wegschrijven (eerst een tijdelijk bestand), zodat de HQ nooit een half bestand leest."""
    tmp = pad + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, pad)


STATUS = '/mnt/project-files/driftmark-hq/status.json'
OUT = '/tmp/hq-ronde'
os.makedirs(OUT, exist_ok=True)
now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
iso = now.isoformat().replace('+00:00', 'Z')
ams = now.astimezone(dt.timezone(dt.timedelta(hours=1)))  # CET (nov-mrt)

subs, views, vids = (int(x) if x not in ('-', '') else None for x in (sys.argv[1:4] + ['-'] * 3)[:3])
d = json.load(open(STATUS))
logs, checks = [], []

# 1. kanaalcijfers
if subs is not None:
    yt = d.setdefault('youtube', {})
    old = yt.get('subscribers')
    yt.update(subscribers=subs, views=views, videoCount=vids, bron='vidIQ', datum=ams.strftime('%-d nov %H:%M'))
    checks.append({'naam': 'Kanaalcijfers', 'ok': True, 'notitie': f'{subs} abonnees, {views} weergaven'})
    if old is not None and subs > old:
        logs.append(('info', f'+{subs - old} abonnee(s): nu {subs}.'))
else:
    checks.append({'naam': 'Kanaalcijfers', 'ok': False, 'notitie': 'vidIQ niet bereikbaar'})
    logs.append(('fout', 'Kanaalcijfers ophalen via vidIQ mislukt.'))

# 1b. video's: weergaven en likes per video en short uit de openbare YouTube-feed (gratis, elk uur) + thumbnails
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import videos as V
ok, note = V.feed_update(d)
checks.append({'naam': "Video's", 'ok': ok, 'notitie': note})
if not ok:
    logs.append(('info', note))

# 2. taken controleren
stale = []
for a in d.get('activity', []):
    if a.get('state') != 'working' or not a.get('lastIso'):
        continue
    try:
        t = dt.datetime.fromisoformat(a['lastIso'].replace('Z', '+00:00'))
    except ValueError:
        continue
    if (now - t).total_seconds() > 6 * 3600:
        stale.append(a['title'])
wachten = [a['title'] for a in d.get('activity', []) if a.get('state') in ('blocked', 'review_ready')]
checks.append({'naam': 'Taken lopen', 'ok': not stale, 'notitie': ('Geen update >6 u: ' + ', '.join(stale)) if stale else 'Alle actieve taken recent bijgewerkt'})
for s in stale:
    logs.append(('waarschuwing', f'Taak "{s}" heeft al meer dan 6 uur niets gemeld.'))
checks.append({'naam': 'Wacht op jou', 'ok': True, 'notitie': f'{len(wachten)} ding(en)'})

# 3. blender-pc
bl = d.get('blender') or {}
fout = [(w.get('naam') if isinstance(w, dict) else str(w)) for w in bl.get('wachtrij', []) if any(x in json.dumps(w, ensure_ascii=False).lower() for x in ('fout', 'mislukt', 'crash'))]
checks.append({'naam': 'Blender-pc', 'ok': not fout, 'notitie': ('Mislukt: ' + ', '.join(fout)) if fout else (bl.get('stand') or 'geen meldingen')})
for f in fout:
    logs.append(('fout', f'Render mislukt op de pc: {f}.'))

# 4. doorschakelen: een video waarvan een stap klaar is, maar waar de volgende stap nog niet loopt
ENGINE_STATE = '/mnt/project-files/driftmark-hq/engine_state.json'
try:
    es = json.load(open(ENGINE_STATE))
except (OSError, ValueError):
    es = {'gemeld': []}
gemeld = set(es.get('gemeld', []))
nieuw = []  # dingen die de routine moet doorgeven (coordinator / niels)
for v in d.get('videos', []):
    steps = v.get('steps', [])
    if not steps or all(x.get('done') for x in steps):
        continue
    if any(x.get('active') for x in steps):
        continue
    werkt = any(a.get('video') == v.get('nr') and a.get('state') == 'working' for a in d.get('activity', []))
    i = next((k for k, x in enumerate(steps) if not x.get('done')), None)
    if i is None or i == 0 or werkt:
        continue
    key = f"door:{v['nr']}:{steps[i]['label']}"
    if key not in gemeld:
        nieuw.append({'soort': 'doorschakelen', 'video': v['nr'], 'klaar': steps[i - 1]['label'], 'volgende': steps[i]['label'], 'key': key})
        logs.append(('info', f"Video {v['nr']}: {steps[i - 1]['label']} is klaar. Volgende stap: {steps[i]['label']} (doorgegeven om te starten)."))
checks.append({'naam': 'Doorschakelen', 'ok': True, 'notitie': f'{len(nieuw)} nieuwe stap(pen) gestart' if nieuw else 'Alle video\'s lopen of wachten op jou'})

# 5. herinnering: iets wacht al meer dan een dag op niels
for a in d.get('activity', []):
    if a.get('state') not in ('blocked', 'review_ready') or not a.get('lastIso'):
        continue
    try:
        t = dt.datetime.fromisoformat(a['lastIso'].replace('Z', '+00:00'))
    except ValueError:
        continue
    # ouder dan 7 dagen = oude, afgeronde thread die nog op 'review' staat: na een week geen dagelijkse herinnering meer
    if 24 * 3600 < (now - t).total_seconds() < 7 * 24 * 3600:
        key = f"wacht:{a['id']}:{now.strftime('%Y%m%d')}"
        if key not in gemeld:
            nieuw.append({'soort': 'herinnering', 'taak': a['title'], 'thread': a['id'], 'key': key})
            logs.append(('waarschuwing', f'"{a["title"]}" wacht al meer dan een dag op jou.'))

# 6. cursus: 48 uur na een lange upload CTR, AVD en verkeersbronnen bekijken (Faceless YouTube Handboek, h. 9).
# De uurronde doet tussen 46 en 60 uur zelf de 48-uurcheck (1x vidIQ per lange video, akkoord niels 6 nov) en zet de
# video dan in engine_state 'vidiq48_gedaan'. Deze herinnering is alleen nog de reserve als die check er na 60 uur niet is.
from zoneinfo import ZoneInfo
gedaan48 = set(es.get('vidiq48_gedaan', []))
for v in (d.get('youtube') or {}).get('videos', []):
    if v.get('type') != 'long' or (v.get('status') or 'public') != 'public' or v.get('id') in gedaan48:
        continue
    ds = v.get('datum') or v.get('date')
    try:
        t = dt.datetime.fromisoformat(f"{str(ds)[:10]}T{v.get('tijd') or '16:00'}").replace(tzinfo=ZoneInfo('Europe/Amsterdam'))
    except ValueError:
        continue
    uren = (now - t).total_seconds() / 3600
    if 60 <= uren <= 108:
        key = f"cursus48:{v.get('id') or v['title']}"
        if key not in gemeld:
            nieuw.append({'soort': 'herinnering', 'tekst': f'"{v["title"]}" staat 2,5 dag online en de automatische 48-uurcheck is er niet. Cursus: bekijk in YouTube Studio de CTR (doel 5%+), AVD (doel 40%+) en verkeersbronnen, en stuur een screenshot. Lage CTR en weinig uit Aanbevolen = thumbnail vervangen.', 'key': key})
            logs.append(('info', f'Cursus-herinnering: CTR/AVD van "{v["title"]}" zelf bekijken (geen automatische 48-uurcheck).'))

# 7. elke ochtend (eerste ronde na 07:00 Amsterdam) 1x vidIQ-cijfers per video: kijkduur, reacties, gedeeld
# (5 credits per dag, akkoord niels 2026-11-06 12:14 "Vanaf nu elke dag"). Maximaal één poging per dag:
# de dag wordt hier al afgestreept, zodat een mislukte aanroep niet elk uur opnieuw credits kost.
dag = now.astimezone(ZoneInfo('Europe/Amsterdam'))
vidiq_dag = dag.hour >= 7 and es.get('vidiq_dag') != dag.strftime('%Y-%m-%d')
if vidiq_dag:
    es['vidiq_dag'] = dag.strftime('%Y-%m-%d')

# nieuwe fouten/waarschuwingen (voor de melding aan niels), elk maar één keer
for k, t in logs:
    if k in ('fout', 'waarschuwing'):
        key = f'log:{t}:{now.strftime("%Y%m%d")}'
        if key not in gemeld:
            nieuw.append({'soort': k, 'tekst': t, 'key': key})
es['gemeld'] = sorted(gemeld | {n['key'] for n in nieuw})[-500:]
_schrijf(ENGINE_STATE, es)

d['updated'] = ams.isoformat()
_schrijf(STATUS, d)

json.dump(d, open(f'{OUT}/state.json', 'w'), ensure_ascii=False)
nxt = (now + dt.timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
json.dump({'lastRun': iso, 'nextRun': nxt, 'status': 'ok' if all(c['ok'] for c in checks) else 'let op', 'checks': checks}, open(f'{OUT}/engine.json', 'w'), ensure_ascii=False)
stat_id = now.strftime('%Y%m%d%H')
json.dump({'at': iso, 'subscribers': subs, 'views': views, 'videoCount': vids}, open(f'{OUT}/stat.json', 'w'))
if not logs:
    logs.append(('info', 'Ronde klaar, alles in orde.'))
for i, (k, t) in enumerate(logs):
    json.dump({'at': iso, 'kind': k, 'text': t}, open(f'{OUT}/log{i}.json', 'w'), ensure_ascii=False)
print(json.dumps({'nieuw': nieuw, 'vidiq_dag': vidiq_dag, 'stat_id': stat_id, 'log_ids': [f'{now.strftime("%Y%m%d%H%M")}-{i}' for i in range(len(logs))], 'checks': checks, 'logs': logs}, ensure_ascii=False))
