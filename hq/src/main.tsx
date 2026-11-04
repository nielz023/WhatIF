import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { startDutch } from './lib/nl';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

startDutch(document.getElementById('root')!);
