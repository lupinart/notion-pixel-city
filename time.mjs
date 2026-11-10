const taipei = new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', hourCycle: 'h23',
});

export function sceneState(date = new Date()) {
  const parts = Object.fromEntries(taipei.formatToParts(date).map(p => [p.type, p.value]));
  const hour = Number(parts.hour);
  return {
    scene: hour >= 5 && hour < 8 ? 'dawn' : hour >= 8 && hour < 17 ? 'day' : hour >= 17 && hour < 19 ? 'dusk' : 'night',
    day: `${parts.year}-${parts.month}-${parts.day}`,
  };
}
