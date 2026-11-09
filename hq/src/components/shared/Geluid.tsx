import { useEffect, useState } from 'react';
import { Volume1, Volume2, VolumeX } from 'lucide-react';
import { soundOn, setSound, onSoundChange, volume, setVolume, onVolume } from '../../world/sound';

/** Huidige geluidsstand (aan/uit en volume), blijft gelijk met elke andere geluidsknop. */
export function useGeluid() {
  const [on, setOn] = useState(soundOn());
  const [vol, setVol] = useState(volume());
  useEffect(() => onSoundChange(setOn), []);
  useEffect(() => onVolume(setVol), []);
  return { on, vol, stil: !on || vol <= 0.001 };
}

export function GeluidIcoon({ size = 18 }: { size?: number }) {
  const { vol, stil } = useGeluid();
  return stil ? <VolumeX size={size} /> : vol < 0.45 ? <Volume1 size={size} /> : <Volume2 size={size} />;
}

/**
 * Geluid met één knop (verbeterlijst punt 37): dempen + één volumeschuif voor alles
 * (klikjes, meldingen en het kantoorgeluid). Wordt bewaard in deze browser.
 */
export default function Geluid({ breed }: { breed?: boolean }) {
  const { on, vol, stil } = useGeluid();
  const pct = Math.round(vol * 100);
  return (
    <div className={`flex items-center gap-3 ${breed ? 'w-full' : ''}`}>
      <button onClick={() => setSound(!on)} aria-pressed={!on} aria-label={on ? 'Geluid dempen' : 'Geluid aanzetten'} title={on ? 'Dempen' : 'Geluid aan'}
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border transition ${stil ? 'border-white/10 bg-white/5 text-slate-400' : 'border-orange-400/40 bg-orange-500/15 text-orange-200'}`}>
        <GeluidIcoon size={17} />
      </button>
      <input type="range" min={0} max={1} step={0.05} value={on ? vol : 0} onChange={(e) => setVolume(parseFloat(e.target.value))}
        className="dm-volume min-w-0 flex-1" style={{ ['--v' as string]: `${on ? pct : 0}%` }} aria-label="Volume" />
      <span className="w-10 shrink-0 text-right text-[13px] font-semibold text-slate-300">{on ? `${pct}%` : 'uit'}</span>
    </div>
  );
}
