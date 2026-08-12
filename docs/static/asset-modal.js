/* ============================================================
   Fenêtre modale actif : description + graphique agrandi navigable
   Aucune dépendance externe, SVG dessiné à la volée.
   ============================================================ */

(function () {
  function openAssetModal(symbol) {
    const data = window.ASSET_DATA && window.ASSET_DATA[symbol];
    if (!data) return;

    const overlay = document.getElementById('asset-modal-overlay');
    const titleEl = document.getElementById('asset-modal-title');
    const descEl = document.getElementById('asset-modal-desc');
    const chartEl = document.getElementById('asset-modal-chart');
    const tooltipEl = document.getElementById('asset-modal-tooltip');

    titleEl.textContent = data.name;
    descEl.textContent = data.description;
    chartEl.innerHTML = '';
    tooltipEl.style.opacity = '0';

    const history = data.history || [];
    if (history.length > 1) {
      drawChart(chartEl, tooltipEl, history);
    } else {
      chartEl.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">Historique insuffisant pour afficher un graphique.</p>';
    }

    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeAssetModal() {
    document.getElementById('asset-modal-overlay').classList.remove('open');
    document.body.style.overflow = '';
  }

  function drawChart(container, tooltipEl, history) {
    const w = 640, h = 260, padL = 40, padR = 12, padT = 12, padB = 28;
    const values = history.map(function (p) { return p.v; });
    const lo = Math.min.apply(null, values);
    const hi = Math.max.apply(null, values);
    const span = (hi - lo) || 1;
    const stepX = (w - padL - padR) / (history.length - 1);

    function xAt(i) { return padL + i * stepX; }
    function yAt(v) { return h - padB - ((v - lo) / span) * (h - padT - padB); }

    const first = values[0], last = values[values.length - 1];
    const positive = last >= first;
    const color = positive ? 'var(--positive)' : 'var(--negative)';

    const points = history.map(function (p, i) { return xAt(i) + ',' + yAt(p.v); }).join(' ');

    const areaPoints = points + ' ' + xAt(history.length - 1) + ',' + (h - padB) + ' ' + xAt(0) + ',' + (h - padB);

    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('class', 'asset-modal-svg');

    // Ligne horizontale de référence (première valeur de la période)
    const refLine = document.createElementNS(svgNS, 'line');
    refLine.setAttribute('x1', padL); refLine.setAttribute('x2', w - padR);
    refLine.setAttribute('y1', yAt(first)); refLine.setAttribute('y2', yAt(first));
    refLine.setAttribute('stroke', 'var(--border)');
    refLine.setAttribute('stroke-dasharray', '3,3');
    svg.appendChild(refLine);

    const area = document.createElementNS(svgNS, 'polygon');
    area.setAttribute('points', areaPoints);
    area.setAttribute('fill', color);
    area.setAttribute('opacity', '0.08');
    svg.appendChild(area);

    const line = document.createElementNS(svgNS, 'polyline');
    line.setAttribute('points', points);
    line.setAttribute('fill', 'none');
    line.setAttribute('stroke', color);
    line.setAttribute('stroke-width', '2');
    svg.appendChild(line);

    // Curseur de navigation (ligne verticale + point) mis à jour au survol
    const cursorLine = document.createElementNS(svgNS, 'line');
    cursorLine.setAttribute('y1', padT); cursorLine.setAttribute('y2', h - padB);
    cursorLine.setAttribute('stroke', 'var(--text-muted)');
    cursorLine.setAttribute('stroke-width', '1');
    cursorLine.setAttribute('opacity', '0');
    svg.appendChild(cursorLine);

    const cursorDot = document.createElementNS(svgNS, 'circle');
    cursorDot.setAttribute('r', '4');
    cursorDot.setAttribute('fill', color);
    cursorDot.setAttribute('opacity', '0');
    svg.appendChild(cursorDot);

    // Zone invisible qui capte les mouvements de souris/doigt sur tout le graphique
    const hitArea = document.createElementNS(svgNS, 'rect');
    hitArea.setAttribute('x', 0); hitArea.setAttribute('y', 0);
    hitArea.setAttribute('width', w); hitArea.setAttribute('height', h);
    hitArea.setAttribute('fill', 'transparent');
    svg.appendChild(hitArea);

    function updateCursor(clientX) {
      const rect = svg.getBoundingClientRect();
      const relX = ((clientX - rect.left) / rect.width) * w;
      let i = Math.round((relX - padL) / stepX);
      i = Math.max(0, Math.min(history.length - 1, i));
      const px = xAt(i), py = yAt(history[i].v);

      cursorLine.setAttribute('x1', px); cursorLine.setAttribute('x2', px);
      cursorLine.setAttribute('opacity', '1');
      cursorDot.setAttribute('cx', px); cursorDot.setAttribute('cy', py);
      cursorDot.setAttribute('opacity', '1');

      tooltipEl.style.opacity = '1';
      tooltipEl.style.left = (px / w * 100) + '%';
      tooltipEl.style.top = (py / h * 100) + '%';
      tooltipEl.innerHTML = '<strong>' + history[i].v + '</strong><br>' + history[i].d;
    }

    hitArea.addEventListener('mousemove', function (e) { updateCursor(e.clientX); });
    hitArea.addEventListener('touchmove', function (e) {
      if (e.touches[0]) updateCursor(e.touches[0].clientX);
    }, { passive: true });
    hitArea.addEventListener('mouseleave', function () {
      cursorLine.setAttribute('opacity', '0');
      cursorDot.setAttribute('opacity', '0');
      tooltipEl.style.opacity = '0';
    });

    container.appendChild(svg);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-asset-symbol]').forEach(function (row) {
      row.style.cursor = 'pointer';
      row.addEventListener('click', function () {
        openAssetModal(row.getAttribute('data-asset-symbol'));
      });
    });
    const overlay = document.getElementById('asset-modal-overlay');
    if (overlay) {
      overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeAssetModal();
      });
    }
    const closeBtn = document.getElementById('asset-modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeAssetModal);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeAssetModal();
    });
  });
})();
