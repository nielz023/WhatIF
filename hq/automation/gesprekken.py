#!/usr/bin/env python3
"""Threadstanden en gesprekken voor Driftmark HQ (vervangt de connector Claude Code Remote, v35).

De HQ-pagina leest deze bestanden via de files-capability:
  driftmark-hq/gesprekken/threads.json        stand van elke thread (uit hearthbot list_threads)
  driftmark-hq/gesprekken/<threadId>.json     laatste berichten van één thread (uit hearthbot read_thread)
  driftmark-hq/gesprekken/projectchat.json    de projectchat (uit hearthbot read_project_chat)

Gebruik:
  python3 gesprekken.py threads <bestand>
      <bestand>: één regel per thread:  thread_id|state|last_activity_at|resolved(0/1)|titel
      (mag een deel zijn, bv. list_threads met 'since': de andere threads blijven zoals ze waren)
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
  python3 gesprekken.py importeer [--recent MIN] [transcript.jsonl ...]
      Leest de ruwe resultaten van hearthbot read_thread / read_project_chat uit de transcripten van
      hulpagents (standaard: alle subagent-transcripten van de laatste MIN minuten, standaard 120) en zet
      ze zelf om, letterlijk en met de echte id's. Een volledig gelezen thread (eerste pagina zonder cursor
      tot has_more false) vervangt het bestand helemaal; een deel wordt samengevoegd.
  python3 gesprekken.py stand
      Print per gesprekbestand: id, aantal berichten, laatste bericht (id, tijd), bron_last.
"""
import glob, json, os, re, sys, time, datetime as dt

DIR = os.environ.get('HQ_GESPREKKEN_DIR', '/mnt/project-files/driftmark-hq/gesprekken')
THREADS = os.path.join(DIR, 'threads.json')
MAX_MSGS = 3000
MAX_TEXT = 30000
ACTIEF = {'working', 'blocked', 'review_ready'}
WIE = {'niels', 'claude', 'keuze', 'checklist', 'systeem'}
ID_RE = re.compile(r'^(cmsg_[A-Za-z0-9]+|projectchat)$')
MSG_RE = re.compile(r'^cmsg_[A-Za-z0-9]+$')
TRANSCRIPTEN = ('/root/.claude/projects/*/*/subagents/agent-*.jsonl', '/root/.claude/projects/*/*/subagents/workflows/*/agent-*.jsonl')
LEES = ('read_thread', 'read_project_chat', 'list_project_artifacts')
ARTIFACTS = os.environ.get('HQ_ARTIFACTS', '/mnt/project-files/driftmark-hq/kennis/artifacts.json')


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
    nieuw = {}
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
        nieuw[tid] = {'id': tid, 'title': titel, 'state': state, 'last': last, 'resolved': resolved in ('1', 'true', 'ja')}
    # samenvoegen: threads die niet in het bestand staan (list_threads met 'since') blijven zoals ze waren
    rijen = []
    for tid in {**oud, **nieuw}:
        t = {**(oud.get(tid) or {}), **(nieuw.get(tid) or {})}
        g = lees(gesprek_pad(tid), None)
        t.update(msgs=len(g['msgs']) if g else 0, file=bool(g), opgehaald=(g or {}).get('at') or t.get('opgehaald'))
        rijen.append(t)
    rijen.sort(key=lambda t: t.get('last') or '', reverse=True)
    schrijf(THREADS, {'at': nu(), 'threads': rijen})
    def item(tid, titel):
        g = lees(gesprek_pad(tid), None)
        laatste = (g or {}).get('msgs', [])[-1:] or [{}]
        return {'id': tid, 'title': titel, 'vanaf_at': laatste[0].get('at')}

    ophalen = []
    for t in rijen:
        # sinds v35 (alles in de HQ) ook klare threads: elke thread waarvan het gesprek nog niet of niet meer klopt
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


def _resultaten(pad):
    """(tool, input, resultaat) voor elk hearthbot-leesresultaat in een transcript, in volgorde."""
    dec, uses = json.JSONDecoder(), {}
    try:
        f = open(pad, encoding='utf-8', errors='replace')
    except OSError:
        return
    with f:
        for regel in f:
            try:
                d = json.loads(regel)
            except ValueError:
                continue
            inhoud = (d.get('message') or {}).get('content') if isinstance(d, dict) else None
            if not isinstance(inhoud, list):
                continue
            for b in inhoud:
                if not isinstance(b, dict):
                    continue
                if b.get('type') == 'tool_use':
                    naam = str(b.get('name') or '')
                    kort = naam.split('__')[-1]
                    if naam.startswith('mcp__hearthbot__') and kort in LEES:
                        uses[b.get('id')] = (kort, b.get('input') or {})
                elif b.get('type') == 'tool_result' and b.get('tool_use_id') in uses and not b.get('is_error'):
                    c = b.get('content')
                    txt = c if isinstance(c, str) else ''.join(x.get('text', '') for x in (c or []) if isinstance(x, dict))
                    i = txt.find('{"messages"')
                    if i < 0:
                        i = txt.find('{"artifacts"')
                    if i < 0:
                        i = txt.find('{"')
                    if i < 0:
                        continue
                    try:
                        obj, _ = dec.raw_decode(txt[i:])
                    except ValueError:
                        continue
                    if isinstance(obj, dict) and (isinstance(obj.get('messages'), list) or isinstance(obj.get('artifacts'), list)):
                        yield uses[b['tool_use_id']] + (obj,)


def _bijlagen(m):
    out = []
    for o in m.get('attached_outputs') or []:
        if not isinstance(o, dict):
            continue
        naam = str(o.get('filename') or o.get('title') or o.get('name') or '').strip()
        href = str(o.get('href') or o.get('url') or '').strip()
        if not (naam or href):
            continue
        b = {'name': naam or href, 'kind': str(o.get('kind') or '')}
        if href.startswith('https://'):
            b['href'] = href
        out.append(b)
    return out


def zet_om(m, titels):
    """Eén ruw bericht naar het formaat van de HQ, of None (ruis), of een keuze-uitslag {'_besluit': ...}."""
    body = m.get('body') if isinstance(m.get('body'), str) else ''
    j = None
    if body.startswith('{'):
        try:
            j = json.loads(body)
        except ValueError:
            j = None
    who, text, opts, extra = None, '', [], {}
    if m.get('author') == 'user':
        who, text = 'niels', body
        extra['author'] = str(m.get('author_name') or 'niels')
    elif not isinstance(j, dict):
        who, text = 'claude', body
    else:
        k = j.get('kind')
        if k == 'status':
            who, text = 'checklist', str(j.get('text') or '')
        elif k == 'onboarding':
            who, text = 'claude', str(j.get('text') or '')
        elif k == 'thread_started':
            t = titels.get(j.get('thread_root_id')) or ''
            who, text = 'systeem', 'Er is een nieuwe thread gestart' + (f': {t}' if t else '.')
            if j.get('thread_root_id'):
                extra['thread'] = str(j['thread_root_id'])
        elif k == 'activity':
            tool, inhoud = j.get('tool'), str(j.get('content') or '').strip()
            if tool == 'ask_decision' and isinstance(j.get('decision'), dict):
                dd = j['decision']
                who = 'keuze'
                text = str(dd.get('question') or '').strip()
                if dd.get('reason'):
                    text += '\n' + str(dd['reason']).strip()
                labels = []
                for o in dd.get('options') or []:
                    if not isinstance(o, dict):
                        continue
                    lab, gev = str(o.get('label') or '').strip(), str(o.get('consequence') or '').strip()
                    labels.append(lab)
                    if lab:
                        opts.append(f'{lab}: {gev}' if gev else lab)
                extra['_labels'] = labels
            elif tool == 'decide' and j.get('decision_id'):
                return {'_besluit': str(j['decision_id']), 'index': j.get('option_index')}
            elif tool == 'send_message' and j.get('direction') == 'received' and inhoud:
                van = 'Bericht van de coördinator' if 'coordinator' in str(j.get('text') or '').lower() else 'Bericht van een andere thread'
                who, text = 'systeem', f'{van}: {inhoud[:1500]}'
            elif tool == 'start_rc_session' and inhoud:
                who, text = 'systeem', f"Opdracht aan de sessie op niels' pc: {inhoud[:1500]}"
            elif tool == 'artifact_comment':
                who, text = 'systeem', 'Er kwam een opdracht binnen via een opmerking in Driftmark HQ.'
            else:
                return None
        elif isinstance(j.get('question'), str) and isinstance(j.get('options'), list):
            who, text = 'keuze', j['question'].strip()
            for o in j['options']:
                lab = str(o.get('label') if isinstance(o, dict) else o).strip()
                if lab:
                    opts.append(lab)
        else:
            return None  # doorgestuurd, sessie, apparaat: ruis
    files = _bijlagen(m)
    text = (text or '').strip()
    if files:
        regels = [f"📎 [{b['name']}]({b['href']})" if b.get('href') else f"📎 {b['name']}" for b in files]
        text = (text + '\n\n' if text else '') + '\n'.join(regels)
    if not text and not opts:
        return None
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT].rstrip() + ' …'
    uit = {'id': m['id'], 'who': who, 'at': str(m.get('created_at') or ''), 'text': text}
    uit.update({k: v for k, v in extra.items() if v not in (None, '', [])})
    if opts:
        uit['options'] = opts
    if files:
        uit['files'] = files
    return uit


def cmd_importeer(paden, recent_min=120):
    if not paden:
        grens = time.time() - recent_min * 60
        paden = sorted({p for pat in TRANSCRIPTEN for p in glob.glob(pat) if os.path.getmtime(p) >= grens})
    paden = sorted(paden, key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)
    th = lees(THREADS, {})
    titels = {t['id']: t.get('title') or '' for t in th.get('threads', [])}
    per, artifacts = {}, None
    for pad in paden:
        ketens = {}
        for tool, inp, obj in _resultaten(pad):
            if tool == 'list_project_artifacts':
                if isinstance(obj.get('artifacts'), list):
                    artifacts = obj['artifacts']   # de laatste lijst wint
                continue
            if not isinstance(obj.get('messages'), list):
                continue
            tid = 'projectchat' if tool == 'read_project_chat' else str(inp.get('thread_id') or obj.get('thread_id') or '')
            if not ID_RE.match(tid):
                continue
            k = ketens.setdefault(tid, {'begin': False, 'eind': False, 'msgs': {}, 'cursor': None})
            if not inp.get('cursor'):
                k['begin'] = True
            if obj.get('has_more') is False:
                k['eind'] = True
                if tool == 'read_project_chat' and inp.get('cursor'):
                    k['cursor'] = inp['cursor']
            for m in obj['messages']:
                if isinstance(m, dict) and isinstance(m.get('id'), str) and MSG_RE.match(m['id']):
                    k['msgs'][m['id']] = m
        for tid, k in ketens.items():
            p = per.setdefault(tid, {'msgs': {}, 'volledig': False, 'cursor': None})
            if k['begin'] and k['eind']:
                p['msgs'], p['volledig'] = dict(k['msgs']), True   # volledig gelezen: dit is het hele gesprek
            else:
                p['msgs'].update(k['msgs'])
            p['cursor'] = k['cursor'] or p['cursor']
    verslag = []
    for tid, p in per.items():
        conv, besluiten = [], []
        for m in sorted(p['msgs'].values(), key=lambda m: (m.get('created_at') or '', m['id'])):
            r = zet_om(m, titels)
            if r is None:
                continue
            (besluiten if '_besluit' in r else conv).append(r)
        op_id = {m['id']: m for m in conv}
        for b in besluiten:
            kaart, i = op_id.get(b['_besluit']), b.get('index')
            labels = (kaart or {}).get('_labels') or []
            if kaart and isinstance(i, int) and 0 <= i < len(labels) and labels[i] and 'Gekozen:' not in kaart['text']:
                kaart['text'] += f'\nGekozen: {labels[i]}'
                kaart['chosen'] = i
        for m in conv:
            m.pop('_labels', None)
        pad = gesprek_pad(tid)
        oud = lees(pad, None)
        if p['volledig'] or oud is None:
            msgs, meer = conv, not p['volledig']
        else:
            alle = {m['id']: m for m in oud.get('msgs', [])}
            sig = {(m['at'], m['who'], m['text'][:40]) for m in conv}
            tijd = {(m['at'], m['who']) for m in conv}
            for mid, m in list(alle.items()):
                if mid in op_id:
                    continue
                # oude, met de hand overgetypte berichten die nu letterlijk binnenkomen (ander of fout id)
                if (m.get('at'), m.get('who'), (m.get('text') or '')[:40]) in sig or (not MSG_RE.match(mid) and (m.get('at'), m.get('who')) in tijd):
                    alle.pop(mid)
            alle.update(op_id)
            msgs, meer = sorted(alle.values(), key=lambda m: (m.get('at') or '', m['id'])), bool(oud.get('hasMore'))
        afgekapt = len(msgs) > MAX_MSGS
        msgs = msgs[-MAX_MSGS:]
        t = next((x for x in th.get('threads', []) if x['id'] == tid), None)
        g = {
            'id': tid, 'title': (t or {}).get('title') or (oud or {}).get('title') or ('Projectchat' if tid == 'projectchat' else tid),
            'at': nu(), 'hasMore': bool(meer or afgekapt), 'volledig': bool(p['volledig'] or (oud or {}).get('volledig')) and not afgekapt,
            'msgs': msgs, 'bron_last': (t or {}).get('last') if t else (oud or {}).get('bron_last'),
        }
        cursor = p['cursor'] or (oud or {}).get('cursor')
        if cursor:
            g['cursor'] = cursor
        schrijf(pad, g)
        for x in th.get('threads', []):
            if x['id'] == tid:
                x.update(msgs=len(msgs), file=True, opgehaald=g['at'])
        verslag.append({'id': tid, 'berichten': len(msgs), 'volledig': g['volledig'], 'nieuw_gelezen': len(p['msgs'])})
    if th and verslag:
        schrijf(THREADS, th)
    if artifacts:
        schrijf(ARTIFACTS, {'at': nu(), 'artifacts': [a for a in artifacts if isinstance(a, dict)]})
    print(json.dumps({'transcripten': len(paden), 'gesprekken': verslag, 'artifacts': len(artifacts or [])}, ensure_ascii=False))


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
    elif a[0] == 'importeer':
        rest = a[1:]
        recent = 120
        if '--recent' in rest:
            i = rest.index('--recent')
            recent = int(rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        cmd_importeer(rest, recent)
    elif a[0] == 'stand':
        cmd_stand()
    else:
        sys.exit(__doc__)
