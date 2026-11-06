#!/usr/bin/env python3
"""Echte videocijfers van Driftmark in status.json (youtube.videos).

Twee bronnen:
- feed (gratis, elk uur): de openbare YouTube-feed van het kanaal geeft voor de 15 nieuwste uploads
  de weergaven en likes. Nieuwe uploads komen er vanzelf bij, ingeplande shorts worden 'public' zodra
  ze online staan, en ontbrekende thumbnails worden opgehaald (driftmark-hq/thumbs/<id>.jpg).
- vidIQ (5 credits, 1x per dag, akkoord niels 2026-11-06): vidiq_channel_analytics met dimension 'video'
  geeft per video de gemiddelde kijkduur, het percentage bekeken, reacties, gedeeld en nieuwe abonnees.
  Die JSON wordt met `python3 videos.py vidiq <bestand.json>` in status.json gezet.

Gebruik:  python3 videos.py feed            (ook vanuit ronde.py, elk uur)
          python3 videos.py vidiq <json>    (antwoord van vidiq_channel_analytics, dimension video; als ronde.py
                                             "vidiq_dag": true meldt, de eerste ronde na 07:00 Amsterdam)
"""
import json, os, subprocess, sys, datetime as dt
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

STATUS = '/mnt/project-files/driftmark-hq/status.json'
THUMBS = '/mnt/project-files/driftmark-hq/thumbs'
REPO_THUMBS = '/home/user/WhatIF/hq/public/thumbs'
CHANNEL = 'UCJhUg9hdXlhRRc7GBU_nRgg'
FEED = f'https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}'
AMS = ZoneInfo('Europe/Amsterdam')
NS = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'm': 'http://search.yahoo.com/mrss/'}


def _now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _iso(t):
    return t.isoformat().replace('+00:00', 'Z')


def _curl(url, out=None, timeout=20):
    args = ['curl', '-sS', '-f', '-m', str(timeout), '-L', url]
    if out:
        args += ['-o', out]
    r = subprocess.run(args, capture_output=True, timeout=timeout + 5)
    if r.returncode != 0:
        raise RuntimeError(f'curl {url}: {r.stderr.decode(errors="ignore")[:200]}')
    return r.stdout


def read_feed():
    """[{id, title, type, published (UTC datetime), views, likes, url}] voor de nieuwste uploads."""
    root = ET.fromstring(_curl(FEED))
    out = []
    for e in root.findall('a:entry', NS):
        vid = e.findtext('yt:videoId', namespaces=NS)
        link = e.find('a:link', NS).get('href', '')
        g = e.find('m:group', NS)
        st = g.find('m:community/m:statistics', NS) if g is not None else None
        rt = g.find('m:community/m:starRating', NS) if g is not None else None
        pub = dt.datetime.fromisoformat(e.findtext('a:published', namespaces=NS))
        out.append({
            'id': vid, 'title': e.findtext('a:title', namespaces=NS) or vid,
            'type': 'short' if '/shorts/' in link else 'long', 'published': pub.astimezone(dt.timezone.utc),
            'views': int(st.get('views')) if st is not None else None,
            'likes': int(rt.get('count')) if rt is not None else None,
            'url': f'https://youtu.be/{vid}',
        })
    return out


def _thumb(vid):
    """Thumbnail (320x180, zoals de rest) naar de projectbestanden, als hij er nog niet is."""
    dst = f'{THUMBS}/{vid}.jpg'
    if os.path.exists(dst) or os.path.exists(f'{REPO_THUMBS}/{vid}.jpg'):
        return False
    os.makedirs(THUMBS, exist_ok=True)
    tmp = dst + '.tmp'
    _curl(f'https://i.ytimg.com/vi/{vid}/mqdefault.jpg', tmp)
    os.replace(tmp, dst)
    return True


def apply_feed(d, feed, now=None):
    """Werk youtube.videos bij met de feed. Geeft het aantal bijgewerkte en nieuwe video's terug."""
    now = now or _now()
    yt = d.setdefault('youtube', {})
    vids = yt.setdefault('videos', [])
    by_id = {v.get('id'): v for v in vids if v.get('id')}
    upd = new = 0
    for f in feed:
        local = f['published'].astimezone(AMS)
        v = by_id.get(f['id'])
        if v is None:
            v = {'id': f['id'], 'title': f['title'], 'type': f['type']}
            vids.append(v); by_id[f['id']] = v; new += 1
        v.update(status='public', datum=local.strftime('%Y-%m-%d'), tijd=local.strftime('%H:%M'), url=f['url'])
        v.setdefault('type', f['type'])
        if not v.get('title'):
            v['title'] = f['title']
        if f['views'] is not None:
            # de feed is live; vidIQ/Analytics loopt achter, dus nooit terug naar een lager getal
            v['views'] = max(f['views'], int(v.get('views') or 0))
        if f['likes'] is not None:
            v['likes'] = max(f['likes'], int(v.get('likes') or 0))
        v['viewsAt'] = _iso(now)
        upd += 1
    # nieuwste bovenaan (ingeplande shorts met een datum in de toekomst eerst): de schermen pakken de eerste lange video
    vids.sort(key=lambda v: (str(v.get('datum') or v.get('date') or ''), str(v.get('tijd') or '')), reverse=True)
    yt['feedAt'] = _iso(now)
    return upd, new


def apply_vidiq(d, res, now=None):
    """Zet het antwoord van vidiq_channel_analytics (dimension video) per video in youtube.videos."""
    now = now or _now()
    heads = [h['name'] for h in res.get('columnHeaders', [])]
    vids = d.setdefault('youtube', {}).setdefault('videos', [])
    by_id = {v.get('id'): v for v in vids if v.get('id')}
    n = 0
    for row in res.get('rows', []):
        r = dict(zip(heads, row))
        v = by_id.get(r.get('video'))
        if v is None:
            continue
        num = lambda k: r.get(k) if isinstance(r.get(k), (int, float)) else None
        if num('views') is not None:
            v['views'] = max(int(r['views']), int(v.get('views') or 0))
        if num('likes') is not None:
            v['likes'] = max(int(r['likes']), int(v.get('likes') or 0))
        for src, dst in (('engagedViews', 'engaged'), ('estimatedMinutesWatched', 'minuten'), ('averageViewDuration', 'avd'),
                         ('comments', 'comments'), ('shares', 'shares'), ('subscribersGained', 'subs')):
            if num(src) is not None:
                v[dst] = int(r[src])
        if num('averageViewPercentage') is not None:
            v['avp'] = round(float(r['averageViewPercentage']), 1)
        v['statsAt'] = _iso(now)
        n += 1
    yt = d['youtube']
    yt['vidiqAt'] = _iso(now)
    yt['vidiqTot'] = res.get('endDate')
    return n


def feed_update(d):
    """Voor ronde.py: feed toepassen en thumbnails ophalen. Gooit niets; geeft een korte notitie terug."""
    try:
        feed = read_feed()
    except Exception as e:  # geen internet of YouTube even weg: de oude cijfers blijven staan
        return False, f'YouTube-feed niet bereikbaar ({str(e)[:80]})'
    upd, new = apply_feed(d, feed)
    th = 0
    for f in feed:
        try:
            th += _thumb(f['id'])
        except Exception:
            pass
    return True, f'{upd} video\'s bijgewerkt uit YouTube' + (f', {new} nieuw' if new else '') + (f', {th} thumbnails' if th else '')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'feed'
    d = json.load(open(STATUS))
    if cmd == 'feed':
        ok, note = feed_update(d)
        print(note)
    elif cmd == 'vidiq':
        res = json.load(open(sys.argv[2]))
        print(f'{apply_vidiq(d, res)} video\'s met vidIQ-cijfers bijgewerkt')
    else:
        sys.exit(__doc__)
    json.dump(d, open(STATUS, 'w'), ensure_ascii=False, indent=1)
    # na ronde.py: ook de kopie voor de database bijwerken, zodat de batch van deze ronde de nieuwe cijfers meeneemt
    if cmd == 'vidiq' and os.path.isdir('/tmp/hq-ronde'):
        json.dump(d, open('/tmp/hq-ronde/state.json', 'w'), ensure_ascii=False)
