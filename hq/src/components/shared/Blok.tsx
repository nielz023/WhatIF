import { Component, type ReactNode } from 'react';

/**
 * Vangt een fout in één blok op (verbeterlijst punt 49): alleen dat blok toont een melding met
 * "Opnieuw proberen", de rest van de pagina werkt gewoon door.
 */
export default class Blok extends Component<{ children: ReactNode; naam?: string }, { err: string | null; n: number }> {
  state = { err: null as string | null, n: 0 };
  static getDerivedStateFromError(e: unknown) { return { err: String((e as Error)?.message ?? e) }; }
  componentDidCatch(e: unknown) { console.error('[HQ] blok-fout', this.props.naam ?? '', e); }
  render() {
    if (!this.state.err) return <div key={this.state.n} className="contents">{this.props.children}</div>;
    return (
      <div className="panel flex flex-wrap items-center justify-between gap-2 border-amber-400/30 p-3 text-[13px] text-amber-100" role="alert">
        <span>⚠️ {this.props.naam ? `"${this.props.naam}" kon` : 'Dit blok kon'} niet laden. De rest werkt gewoon.</span>
        <button className="btn-ghost !py-1 text-[13px]" onClick={() => this.setState((s) => ({ err: null, n: s.n + 1 }))}>Opnieuw proberen</button>
      </div>
    );
  }
}
