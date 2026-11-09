/**
 * IDEEËNBUS (verbeterlijst punt 13): snel een idee intypen; het gaat als opdracht naar Claude met de vraag
 * het te beoordelen tegen de niche en de cijfers. Het antwoord komt terug onder Mijn opdrachten.
 */
import { useState } from 'react';
import { Lightbulb } from 'lucide-react';
import { order, openOpdracht } from '../../services/real';
import { useGame } from '../../store/useGame';

export default function Ideeenbus() {
  const [idee, setIdee] = useState('');
  const toast = useGame((s) => s.toast);
  const stuur = (e: React.FormEvent) => {
    e.preventDefault();
    const t = idee.trim(); if (!t) return;
    order(`Ideeënbus: beoordeel dit idee tegen de niche (3D What If, IFOLOGY-stijl) en mijn cijfers (welke shorts en video's het goed doen): "${t}". Geef een cijfer van 1 tot 10, een Engelse werktitel, de twist, wat sterk en zwak is, en of het een lange video, een short of allebei wordt.`, toast, { doel: 'Onderzoek' });
    setIdee('');
  };
  return (
    <section className="panel glow-blue mb-4 p-4">
      <div className="mb-1 flex items-center gap-2 font-display text-[18px] font-bold text-white"><Lightbulb size={17} className="text-amber-300" />Ideeënbus</div>
      <p className="mb-2 text-[13px] text-slate-400">Schiet je iets te binnen? Typ het hier. Claude beoordeelt het tegen je niche en je cijfers; het antwoord zie je onder Mijn opdrachten.</p>
      <form onSubmit={stuur} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="ideeenbus" className="sr-only">Jouw idee</label>
        <input id="ideeenbus" className="input min-w-0 flex-1" value={idee} onChange={(e) => setIdee(e.target.value)} placeholder="Bijvoorbeeld: wat als je elke nacht 10 jaar ouder wordt" />
        <button className="btn-primary text-[14px]" type="submit" disabled={!idee.trim()}>Laat Claude beoordelen</button>
      </form>
      <button className="mt-2 text-[13px] text-sky-300 hover:text-white" onClick={() => openOpdracht({ tab: 'mijn' })}>Mijn opdrachten bekijken →</button>
    </section>
  );
}
