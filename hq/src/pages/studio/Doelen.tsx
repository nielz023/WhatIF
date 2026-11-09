/**
 * DOELEN MET VOORTGANG EN PROGNOSE (verbeterlijst punt 43): 100 en 1.000 abonnees, 4.000 kijkuren en
 * 10 miljoen shortsweergaven (de twee routes naar het YouTube Partner Programma), met "in dit tempo haal je dit rond …".
 * Het tempo van abonnees komt uit de meetpunten in de database; dat van kijkuren en shortsweergaven is een
 * gemiddelde sinds de eerste upload en heet daarom "schatting".
 */
import { useDb } from '../../services/db';
import { useLive } from '../../services/live';
import { perDag, sindsEerste, haalDatum } from '../../services/studio';
import Bron from '../../components/shared/Bron';
import { KLEUR } from '../../lib/status';

interface D { naam: string; nu: number; doel: number; tempo: number | null; eenheid: string; bron: string; at?: string | null; schatting: boolean; uitleg: string }

function Rij({ d }: { d: D }) {
  const pct = Math.min(100, (d.nu / d.doel) * 100);
  const wanneer = haalDatum(d.nu, d.doel, d.tempo);
  const kl = pct >= 100 ? KLEUR.klaar : KLEUR.bezig;
  const fmt = (n: number) => n.toLocaleString('nl-NL', { maximumFractionDigits: n < 100 ? 1 : 0 });
  return (
    <div className="rounded-xl bg-white/[.03] p-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-display text-[16px] font-bold text-white" title={d.uitleg}>{d.naam}</span>
        <span className="text-[14px] font-semibold" style={{ color: kl }}>{fmt(d.nu)} / {d.doel.toLocaleString('nl-NL')} {d.eenheid}</span>
      </div>
      <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full" style={{ width: `${Math.max(1, pct)}%`, background: `linear-gradient(90deg, ${KLEUR.wacht}, ${kl})` }} /></div>
      <div className="mt-1 text-[13px] text-slate-300">
        {wanneer === 'gehaald' ? 'Gehaald!'
          : wanneer ? <>In dit tempo ({fmt(d.tempo!)} {d.eenheid} per dag) haal je dit rond <b className="text-white">{wanneer}</b>.</>
          : 'Nog te weinig meetpunten om te zeggen wanneer je dit haalt.'}
      </div>
      <Bron bron={d.bron} at={d.at} schatting={d.schatting && wanneer !== 'gehaald'} />
    </div>
  );
}

export default function Doelen() {
  const stats = useDb((s) => s.stats);
  const yt = useLive((s) => s.data.youtube);
  const vids = yt?.videos ?? [];
  const laatste = [...stats].reverse().find((r) => typeof r.subscribers === 'number');
  const subs = laatste?.subscribers ?? yt?.subscribers ?? 0;
  const subsAt = laatste?.at ?? yt?.vidiqAt ?? null;
  const subTempo = perDag(stats, 'subscribers');
  const uren = sindsEerste(vids, 'long', (v) => v.minuten);
  const nu90 = Date.now() - 90 * 864e5;
  const shorts90 = vids.filter((v) => v.type === 'short' && (v.status ?? 'public') === 'public' && Date.parse(`${(v.datum ?? v.date ?? '').slice(0, 10)}T12:00:00`) >= nu90).reduce((a, v) => a + (v.views ?? 0), 0);
  const shortTempo = sindsEerste(vids, 'short', (v) => v.views);
  const vq = vids.map((v) => v.statsAt).filter(Boolean).sort().pop() ?? yt?.vidiqAt;
  const lijst: D[] = [
    { naam: '100 abonnees', nu: subs, doel: 100, tempo: subTempo, eenheid: 'abonnees', bron: laatste ? 'database (uurronde)' : 'vidIQ', at: subsAt, schatting: false, uitleg: 'Eerste mijlpaal' },
    { naam: '1.000 abonnees', nu: subs, doel: 1000, tempo: subTempo, eenheid: 'abonnees', bron: laatste ? 'database (uurronde)' : 'vidIQ', at: subsAt, schatting: false, uitleg: 'Nodig voor het YouTube Partner Programma' },
    { naam: '4.000 kijkuren', nu: uren.som / 60, doel: 4000, tempo: uren.perDag != null ? uren.perDag / 60 : null, eenheid: 'uur', bron: 'vidIQ, alleen lange video\'s', at: vq, schatting: true, uitleg: 'Route 1 naar het Partner Programma: 4.000 openbare kijkuren uit lange video\'s in 12 maanden' },
    { naam: '10 miljoen shortsweergaven', nu: shorts90, doel: 10_000_000, tempo: shortTempo.perDag, eenheid: 'weergaven', bron: 'YouTube-feed, laatste 90 dagen', at: yt?.feedAt, schatting: true, uitleg: 'Route 2 naar het Partner Programma: 10 miljoen shortsweergaven in 90 dagen' },
  ];
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-2 font-display text-[18px] font-bold text-white">🎯 Doelen</div>
      <div className="grid gap-2 lg:grid-cols-2">{lijst.map((d) => <Rij key={d.naam} d={d} />)}</div>
      <p className="mt-2 text-[12px] text-slate-500">Het tempo van abonnees komt uit de meetpunten van de afgelopen 14 dagen. Kijkuren en shortsweergaven hebben nog geen geschiedenis per dag; daar is het tempo het gemiddelde sinds je eerste upload (schatting). Voor het Partner Programma heb je 1.000 abonnees nodig plus één van de twee andere doelen.</p>
    </section>
  );
}
