import { ArrowRight } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Drawer } from '../ui';
import { ROOMS } from '../../world/rooms';
import { useWorld } from '../../world/useWorld';
import { DeptTools } from '../../world/deptTools';
import Afdeling from './Afdeling';

/**
 * De afdelingslade in Team (Studio). Sinds verbeterlijst punt 50 heeft elke afdeling dezelfde opbouw als het
 * afdelingspaneel in het 3D-kantoor (components/shared/Afdeling.tsx): wat hij doet, wat loopt, wat op jou wacht,
 * wat klaar is en snelknoppen, met daaronder het eigen gereedschap. Alleen echte gegevens, geen spelcijfers.
 */
export default function DepartmentDrawer() {
  const s = useGame();
  const id = s.selectedDept;
  const r = id ? ROOMS.find((x) => x.game === id) : undefined;
  if (!id || !r || s.page !== 'hq') return <Drawer open={false} onClose={() => s.selectDept(null)}>{null}</Drawer>;
  const inKantoor = () => { s.selectDept(null); s.setPage('driftmark'); useWorld.getState().setFocus(r.id); };
  return (
    <Drawer open onClose={() => s.selectDept(null)} title={<span style={{ color: r.color }}>{r.icon} {r.naam}</span>} width={560}>
      <Afdeling r={r}>
        <DeptTools r={r} />
        <button onClick={inKantoor} className="flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-[14px] font-semibold text-white transition hover:brightness-125" style={{ borderColor: `${r.color}66`, background: `${r.color}1a` }}>
          Bekijk deze afdeling in het 3D-kantoor<ArrowRight size={16} />
        </button>
      </Afdeling>
    </Drawer>
  );
}
