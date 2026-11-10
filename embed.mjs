import {sceneState} from './time.mjs';

const image = document.querySelector('#city');
let pending = null;
let loadedKey = '';
let sequence = 0;

function update() {
  const {scene, day} = sceneState();
  const key = `${scene}-${day}`;
  if (key === loadedKey) {pending = null; return;}
  if (key === pending?.key) return;
  const request = {key};
  pending = request;
  const next = new Image();
  const timeout = setTimeout(() => {
    next.onload = next.onerror = null;
    next.src = ''; // Cancel a hung image so the browser can retry independently.
    if (pending === request) pending = null;
  }, 12_000);
  next.onload = () => {
    clearTimeout(timeout);
    if (pending !== request) return;
    image.src = next.src;
    image.dataset.scene = scene;
    image.dataset.day = day;
    loadedKey = key;
    pending = null;
  };
  next.onerror = () => {
    clearTimeout(timeout);
    if (pending === request) pending = null; // Keep the displayed image and retry.
  };
  next.src = new URL(`${scene}.svg?d=${day}&r=${++sequence}`, import.meta.url).href;
}

update();
setInterval(() => {if (!document.hidden) update();}, 15_000);
document.addEventListener('visibilitychange', () => {if (!document.hidden) update();});
window.addEventListener('pageshow', update);
