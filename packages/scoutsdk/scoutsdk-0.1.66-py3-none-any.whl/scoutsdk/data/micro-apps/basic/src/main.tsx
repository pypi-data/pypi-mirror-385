import { ScoutApp } from '@mirego/scout-chat';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ScoutApp>
      <App />
    </ScoutApp>
  </StrictMode>
);
