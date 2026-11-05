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

d['updated'] = ams.isoformat()
json.dump(d, open(STATUS, 'w'), ensure_ascii=False, indent=1)

json.dump(d, open(f'{OUT}/state.json', 'w'), ensure_ascii=False)
nxt = (now + dt.timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
json.dump({'lastRun': iso, 'nextRun': nxt, 'status': 'ok' if all(c['ok'] for c in checks) else 'let op', 'checks': checks}, open(f'{OUT}/engine.json', 'w'), ensure_ascii=False)
stat_id = now.strftime('%Y%m%d%H')
json.dump({'at': iso, 'subscribers': subs, 'views': views, 'videoCount': vids}, open(f'{OUT}/stat.json', 'w'))
if not logs:
    logs.append(('info', 'Ronde klaar, alles in orde.'))
for i, (k, t) in enumerate(logs):
    json.dump({'at': iso, 'kind': k, 'text': t}, open(f'{OUT}/log{i}.json', 'w'), ensure_ascii=False)
print(json.dumps({'stat_id': stat_id, 'log_ids': [f'{now.strftime("%Y%m%d%H%M")}-{i}' for i in range(len(logs))], 'checks': checks, 'logs': logs}, ensure_ascii=False))
