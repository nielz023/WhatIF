import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { startDutch } from './lib/nl';
import { pasToe } from './lib/prefs';
import { useGame } from './store/useGame';

pasToe();
// testhaak, alleen lokaal (automatische test, verbeterlijst punt 69)
if (window.location?.hostname === 'localhost') (window as unknown as { __dmGame: typeof useGame }).__dmGame = useGame;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

startDutch(document.getElementById('root')!);
