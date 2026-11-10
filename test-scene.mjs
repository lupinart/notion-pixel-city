import assert from 'node:assert/strict';
import {sceneState} from './time.mjs';
for (const [at, scene, day] of [
  ['2026-11-09T21:59:59Z', 'night', '2026-11-10'],
  ['2026-11-09T22:00:00Z', 'day', '2026-11-10'],
  ['2026-11-10T08:59:59Z', 'day', '2026-11-10'],
  ['2026-11-10T09:00:00Z', 'dusk', '2026-11-10'],
  ['2026-11-10T10:59:59Z', 'dusk', '2026-11-10'],
  ['2026-11-10T11:00:00Z', 'night', '2026-11-10'],
  ['2026-12-31T16:00:00Z', 'night', '2027-01-01'],
]) assert.deepEqual(sceneState(new Date(at)), {scene, day});
console.log('PASS: Taiwan 06/17/19 boundaries and midnight/year rollover');
