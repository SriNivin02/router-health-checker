/**
 * Chart & Circular Gauge Render Helpers.
 */
export function setCircleGauge(circleElementId, score) {
  const circle = document.getElementById(circleElementId);
  if (!circle) return;
  const circumference = 565.5;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${offset}`;
  
  let color = 'var(--bad)';
  if (clamped >= 80) color = 'var(--good)';
  else if (clamped >= 50) color = 'var(--warn)';
  
  circle.style.stroke = color;
}

export function animateCounter(elementId, targetValue, durationMs = 800) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const start = 0;
  const startTime = performance.now();
  
  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / durationMs, 1);
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (targetValue - start) * easeOut);
    el.textContent = current;
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = targetValue;
    }
  }
  requestAnimationFrame(update);
}
