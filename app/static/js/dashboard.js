(function () {
  function setupCanvas(canvas, height) {
    if (!canvas || !canvas.getContext) return null;
    const ratio = window.devicePixelRatio || 1;
    const width = canvas.clientWidth || 600;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    const ctx = canvas.getContext('2d');
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    return { ctx, width, height };
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  function paintCard(ctx, width, height) {
    ctx.save();
    roundedRect(ctx, 0, 0, width, height, 18);
    ctx.clip();
    ctx.fillStyle = '#07111a';
    ctx.fillRect(0, 0, width, height);
    for (let i = 0; i < 5; i++) {
      const y = 28 + i * ((height - 60) / 4);
      ctx.strokeStyle = 'rgba(255,255,255,0.08)';
      ctx.beginPath();
      ctx.moveTo(18, y);
      ctx.lineTo(width - 18, y);
      ctx.stroke();
    }
  }

  function drawTrendChart(canvas) {
    const area = setupCanvas(canvas, 260); if (!area) return;
    const { ctx, width, height } = area;
    const labels = JSON.parse(canvas.dataset.labels || '[]');
    const values = JSON.parse(canvas.dataset.values || '[]');
    paintCard(ctx, width, height);
    if (!values.length) {
      ctx.fillStyle = '#95a79f'; ctx.font = '14px Inter, Arial'; ctx.fillText('No scan trend yet', 22, 130); ctx.restore?.(); return;
    }
    const max = Math.max(...values, 1); const left = 26, right = width - 26, bottom = height - 38, top = 28; const stepX = values.length === 1 ? 0 : (right - left) / (values.length - 1);
    const gradient = ctx.createLinearGradient(0, 0, 0, height); gradient.addColorStop(0, 'rgba(0,255,156,0.25)'); gradient.addColorStop(1, 'rgba(77,231,255,0.02)');
    ctx.beginPath(); values.forEach((value, index) => { const x = left + stepX * index; const y = bottom - ((value / max) * (bottom - top)); if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.lineTo(right, bottom + 8); ctx.lineTo(left, bottom + 8); ctx.closePath(); ctx.fillStyle = gradient; ctx.fill();
    ctx.beginPath(); values.forEach((value, index) => { const x = left + stepX * index; const y = bottom - ((value / max) * (bottom - top)); if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.strokeStyle = '#00ff9c'; ctx.lineWidth = 3; ctx.stroke();
    values.forEach((value, index) => { const x = left + stepX * index; const y = bottom - ((value / max) * (bottom - top)); ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI * 2); ctx.fillStyle = '#eafff5'; ctx.fill(); ctx.beginPath(); ctx.arc(x, y, 3.4, 0, Math.PI * 2); ctx.fillStyle = '#00ff9c'; ctx.fill(); ctx.fillStyle = '#95a79f'; ctx.font = '11px Inter, Arial'; ctx.fillText(labels[index] || '', x - 12, height - 14); });
    ctx.restore();
  }

  function drawDonut(canvas) {
    const area = setupCanvas(canvas, 280); if (!area) return; const { ctx, width, height } = area;
    const values = JSON.parse(canvas.dataset.values || '[]'); const labels = JSON.parse(canvas.dataset.labels || '[]');
    paintCard(ctx, width, height);
    const total = values.reduce((a,b)=>a+b,0) || 1; const colors = ['#dc2626','#ea580c','#d97706','#64748b'];
    let angle = -Math.PI/2; const cx = width*0.32, cy = height*0.5, radius = 78;
    values.forEach((value, i) => { const slice = (value/total)*Math.PI*2; ctx.beginPath(); ctx.arc(cx, cy, radius, angle, angle+slice); ctx.lineWidth = 24; ctx.strokeStyle = colors[i]; ctx.stroke(); angle += slice; });
    ctx.beginPath(); ctx.arc(cx, cy, 46, 0, Math.PI*2); ctx.fillStyle = '#07111a'; ctx.fill();
    ctx.fillStyle = '#eafff5'; ctx.font = '700 28px Inter, Arial'; ctx.fillText(String(total), cx-14, cy+8); ctx.fillStyle='#95a79f'; ctx.font='12px Inter, Arial'; ctx.fillText('findings', cx-20, cy+28);
    labels.forEach((label, i) => { const y = 66 + i*42; ctx.fillStyle = colors[i]; ctx.fillRect(width*0.58, y, 16, 16); ctx.fillStyle = '#eafff5'; ctx.font='13px Inter, Arial'; ctx.fillText(label, width*0.58 + 26, y+12); ctx.fillStyle='#95a79f'; ctx.fillText(String(values[i] || 0), width - 42, y+12); });
    ctx.restore();
  }

  function drawBars(canvas) {
    const area = setupCanvas(canvas, 280); if (!area) return; const { ctx, width, height } = area;
    const labels = JSON.parse(canvas.dataset.labels || '[]'); const values = JSON.parse(canvas.dataset.values || '[]');
    paintCard(ctx, width, height);
    if (!values.length) { ctx.fillStyle='#95a79f'; ctx.font='14px Inter, Arial'; ctx.fillText('No categories yet', 22, 140); ctx.restore(); return; }
    const max = Math.max(...values, 1); const left = 34, bottom = height - 42, chartH = height - 90; const gap = 18; const barW = Math.max(26, (width - left*2 - gap*(values.length-1)) / values.length);
    values.forEach((value, i) => { const x = left + i * (barW + gap); const h = (value/max) * chartH; const y = bottom - h; const g = ctx.createLinearGradient(0, y, 0, bottom); g.addColorStop(0, '#4de7ff'); g.addColorStop(1, '#00ff9c'); ctx.fillStyle = g; roundedRect(ctx, x, y, barW, h, 10); ctx.fill(); ctx.fillStyle='#eafff5'; ctx.font='12px Inter, Arial'; ctx.fillText(String(value), x + barW/2 - 5, y - 8); const text = (labels[i] || '').slice(0, 10); ctx.fillStyle='#95a79f'; ctx.fillText(text, x - 4, bottom + 18); });
    ctx.restore();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const trend = document.getElementById('trendChart');
    const severity = document.getElementById('severityChart');
    const category = document.getElementById('categoryChart');
    function redraw(){ drawTrendChart(trend); drawDonut(severity); drawBars(category); }
    redraw(); window.addEventListener('resize', redraw);
  });
})();
