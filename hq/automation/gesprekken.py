#!/usr/bin/env python3
"""Threadstanden en gesprekken voor Driftmark HQ (vervangt de connector Claude Code Remote, v35).

De HQ-pagina leest deze bestanden via de files-capability:
  driftmark-hq/gesprekken/threads.json        stand van elke thread (uit hearthbot list_threads)
  driftmark-hq/gesprekken/<threadId>.json     laatste berichten van één thread (uit hearthbot read_thread)
  driftmark-hq/gesprekken/projectchat.json    de projectchat (uit hearthbot read_project_chat)

Gebruik:
  python3 gesprekken.py threads <bestand>
      <bestand>: één regel per thread:  thread_id|state|last_activity_at|resolved(0/1)|titel
      Schrijft threads.json en print JSON {"ophalen": [...]}: actieve threads (working, blocked,
      review_ready) waarvan het gesprek nog niet of niet meer actueel is opgehaald, plus altijd de
      projectchat, elk met vanaf_at = tijd van het laatst opgehaalde bericht (alleen nieuwere omzetten).
  python3 gesprekken.py berichten <threadId|projectchat> <bestand> [--meer] [--titel "..."] [--cursor C]
      <bestand>: berichten in dit formaat (volgorde maakt niet uit):
        @@ <id> | <wie> | <iso-tijd> | <auteur>
        tekst (Markdown, mag meerdere regels zijn)
        => keuzeoptie            (alleen bij wie = keuze)
      wie: niels, claude, keuze, checklist, systeem.  --meer: er zijn oudere berichten dan deze.
      --cursor: (projectchat) de cursor waarmee de laatste pagina van read_project_chat is gelezen.
      Voegt samen met het bestaande bestand (op id), houdt de laatste 150 berichten.
  python3 gesprekken.py stand
      Print per gesprekbestand: id, aantal berichten, laatste bericht (id, tijd), bron_last.
"""
import json, os, re, sys, datetime as dt

DIR = '/mnt/project-files/driftmark-hq/gesprekken'
THREADS = os.path.join(DIR, 'threads.json')
MAX_MSGS = 150
MAX_TEXT = 6000
ACTIEF = {'working', 'blocked', 'review_ready'}
WIE = {'niels', 'claude', 'keuze', 'checklist', 'systeem'}
ID_RE = re.compile(r'^(cmsg_[A-Za-z0-9]+|projectchat)$')


def nu() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def lees(p, leeg):
    try:
        with open(p) as f:
            return json.load(f)
    except (OSError, ValueError):
        return leeg


def schrijf(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def gesprek_pad(tid: str) -> str:
    if not ID_RE.match(tid):
        sys.exit(f'ongeldig thread-id: {tid}')
    return os.path.join(DIR, f'{tid}.json')


def cmd_threads(bron: str):
    oud = {t['id']: t for t in lees(THREADS, {}).get('threads', [])}
    rijen = []
    for regel in open(bron, encoding='utf-8'):
        regel = regel.strip()
        if not regel or regel.startswith('#'):
            continue
        delen = regel.split('|', 4)
        if len(delen) < 5:
            print(f'regel overgeslagen (te weinig velden): {regel[:80]}', file=sys.stderr)
            continue
        tid, state, last, resolved, titel = (x.strip() for x in delen)
        if not ID_RE.match(tid):
            print(f'regel overgeslagen (geen thread-id): {regel[:80]}', file=sys.stderr)
            continue
        g = lees(gesprek_pad(tid), None)
        rijen.append({
            'id': tid, 'title': titel, 'state': state, 'last': last, 'resolved': resolved in ('1', 'true', 'ja'),
            'msgs': len(g['msgs']) if g else 0, 'file': bool(g),
            'opgehaald': (g or {}).get('at') or (oud.get(tid) or {}).get('opgehaald'),
        })
    rijen.sort(key=lambda t: t['last'] or '', reverse=True)
    schrijf(THREADS, {'at': nu(), 'threads': rijen})
    def item(tid, titel):
        g = lees(gesprek_pad(tid), None)
        laatste = (g or {}).get('msgs', [])[-1:] or [{}]
        return {'id': tid, 'title': titel, 'vanaf_at': laatste[0].get('at')}

    ophalen = []
    for t in rijen:
        if t['state'] not in ACTIEF:
            continue
        g = lees(gesprek_pad(t['id']), None)
        if g and g.get('bron_last') == t['last']:
            continue
        ophalen.append(item(t['id'], t['title']))
    # de projectchat heeft geen stand in list_threads: altijd meenemen. read_project_chat leest van oud naar
    # nieuw; met de bewaarde cursor komen alleen de nieuwere pagina's (zie gesprek-export.md)
    pc = item('projectchat', 'Projectchat')
    pc['cursor'] = (lees(gesprek_pad('projectchat'), None) or {}).get('cursor')
    ophalen.append(pc)
    print(json.dumps({'threads': len(rijen), 'ophalen': ophalen}, ensure_ascii=False))


def parse_berichten(bron: str):
    msgs, cur, buf = [], None, []

    def af():
        if cur is None:
            return
        opts = [l[3:].strip() for l in buf if l.startswith('=> ')]
        tekst = '\n'.join(l for l in buf if not l.startswith('=> ')).strip()
        if len(tekst) > MAX_TEXT:
            tekst = tekst[:MAX_TEXT].rstrip() + ' …'
        m = dict(cur, text=tekst)
        if opts:
            m['options'] = opts
        msgs.append(m)

    for regel in open(bron, encoding='utf-8').read().splitlines():
        if regel.startswith('@@ '):
            af()
            delen = [x.strip() for x in regel[3:].split('|')]
            delen += [''] * (4 - len(delen))
            mid, wie, at, auteur = delen[:4]
            if wie not in WIE:
                sys.exit(f'onbekende afzender "{wie}" bij {mid} (kies uit {sorted(WIE)})')
            cur = {'id': mid, 'who': wie, 'at': at}
            if auteur:
                cur['author'] = auteur
            buf = []
        elif cur is not None:
            buf.append(regel)
    af()
    return msgs


def cmd_berichten(tid: str, bron: str, meer: bool, titel: str | None, cursor: str | None = None):
    pad = gesprek_pad(tid)
    g = lees(pad, {'id': tid, 'title': titel or tid, 'msgs': []})
    alle = {m['id']: m for m in g.get('msgs', [])}
    sig = lambda m: (m.get('at'), m.get('who'), (m.get('text') or '')[:60])
    per_sig = {sig(m): k for k, m in alle.items()}
    nieuw = parse_berichten(bron)
    for m in nieuw:
        oud_id = per_sig.get(sig(m))
        if oud_id and oud_id != m['id']:
            alle.pop(oud_id, None)
        alle[m['id']] = m
        per_sig[sig(m)] = m['id']
    msgs = sorted(alle.values(), key=lambda m: (m.get('at') or '', m['id']))
    afgekapt = len(msgs) > MAX_MSGS
    msgs = msgs[-MAX_MSGS:]
    t = next((x for x in lees(THREADS, {}).get('threads', []) if x['id'] == tid), None)
    g.update({
        'id': tid, 'title': titel or (t or {}).get('title') or g.get('title') or tid, 'at': nu(),
        'hasMore': bool(meer or afgekapt or g.get('hasMore')), 'msgs': msgs,
        'bron_last': (t or {}).get('last') if t else g.get('bron_last'),
    })
    if cursor:
        g['cursor'] = cursor
    schrijf(pad, g)
    # stand in threads.json bijwerken (aantal berichten, bestand bestaat)
    th = lees(THREADS, None)
    if th:
        for x in th.get('threads', []):
            if x['id'] == tid:
                x.update(msgs=len(msgs), file=True, opgehaald=g['at'])
        schrijf(THREADS, th)
    print(json.dumps({'id': tid, 'nieuw': len(nieuw), 'totaal': len(msgs), 'hasMore': g['hasMore']}, ensure_ascii=False))


def cmd_stand():
    th = {t['id']: t for t in lees(THREADS, {}).get('threads', [])}
    for naam in sorted(os.listdir(DIR)) if os.path.isdir(DIR) else []:
        if not naam.endswith('.json') or naam == 'threads.json':
            continue
        g = lees(os.path.join(DIR, naam), {})
        laatste = (g.get('msgs') or [{}])[-1]
        tid = naam[:-5]
        print(f"{tid} | {len(g.get('msgs', []))} berichten | laatste {laatste.get('id')} {laatste.get('at')} | bron_last {g.get('bron_last')} | thread_last {(th.get(tid) or {}).get('last')}")


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == 'threads' and len(a) == 2:
        cmd_threads(a[1])
    elif a[0] == 'berichten' and len(a) >= 3:
        titel = a[a.index('--titel') + 1] if '--titel' in a else None
        cursor = a[a.index('--cursor') + 1] if '--cursor' in a else None
        cmd_berichten(a[1], a[2], '--meer' in a, titel, cursor)
    elif a[0] == 'stand':
        cmd_stand()
    else:
        sys.exit(__doc__)
