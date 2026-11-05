// Laadt het 3D-kantoor op dezelfde manier als het grote HQ (module-script met relatief pad).
import * as K from './kantoor.js';
window.__DM_KANTOOR__ = K;
window.dispatchEvent(new Event('dm-kantoor'));
