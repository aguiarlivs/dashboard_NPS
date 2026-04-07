(() => {
  const dataElement = document.getElementById("dashboard-data");

  if (!dataElement) {
    return;
  }

  const payload = JSON.parse(dataElement.textContent || "{}");
  const sentRecords = Array.isArray(payload.sentRecords) ? payload.sentRecords : [];
  const responseRecords = Array.isArray(payload.responseRecords) ? payload.responseRecords : [];

  const zoneMetas = [
    { label: "Crítica", start: -100, end: 0, color: "#ef4444", badgeClass: "status-badge--critical", valueClass: "nps-value--critical" },
    { label: "Aperfeiçoamento", start: 0, end: 50, color: "#ff8a3d", badgeClass: "status-badge--improvement", valueClass: "nps-value--improvement" },
    { label: "Qualidade", start: 50, end: 75, color: "#f2ba14", badgeClass: "status-badge--quality", valueClass: "nps-value--quality" },
    { label: "Excelência", start: 75, end: 100, color: "#4fbe6e", badgeClass: "status-badge--excellence", valueClass: "nps-value--excellence" },
  ];

  const classStyles = {
    Promotor: "pill--promoter",
    Neutro: "pill--neutral",
    Detrator: "pill--detractor",
  };

  const legendStyles = {
    promoter: "legend-dot--promoter",
    neutral: "legend-dot--neutral",
    detractor: "legend-dot--detractor",
  };

  const slots = {
    gauge: document.getElementById("slot-gauge"),
    respondents: document.getElementById("slot-respondents"),
    rate: document.getElementById("slot-rate"),
    distribution: document.getElementById("slot-distribution"),
    ranking: document.getElementById("slot-ranking"),
    table: document.getElementById("slot-table"),
    summary: document.getElementById("active-filter-summary"),
  };

  const controls = {
    csm: document.getElementById("filter-csm"),
    classification: document.getElementById("filter-classificacao"),
    score: document.getElementById("filter-nota"),
    query: document.getElementById("filter-busca"),
    reset: document.getElementById("reset-filters"),
    print: document.getElementById("print-dashboard"),
  };

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatNumber(value, decimals = 0) {
    return new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  }

  function formatPercent(value, decimals = 1) {
    return `${formatNumber(value, decimals)}%`;
  }

  function pluralizeResponses(total) {
    return total === 1 ? "1 resp." : `${total} resp.`;
  }

  function classifyScore(score) {
    if (score === null || score === undefined || Number.isNaN(Number(score))) {
      return "-";
    }

    if (score >= 9) {
      return "Promotor";
    }
    if (score >= 7) {
      return "Neutro";
    }
    return "Detrator";
  }

  function normalizeText(value, fallback = "-") {
    const text = String(value ?? "").trim();
    return text || fallback;
  }

  function getZoneMeta(npsScore) {
    if (npsScore <= 0) {
      return zoneMetas[0];
    }
    if (npsScore <= 50) {
      return zoneMetas[1];
    }
    if (npsScore <= 75) {
      return zoneMetas[2];
    }
    return zoneMetas[3];
  }

  function scoreToAngle(score) {
    const clamped = Math.max(-100, Math.min(100, Number(score)));
    return 180 - ((clamped + 100) / 200) * 180;
  }

  function polarToCartesian(cx, cy, radius, angleDeg) {
    const angleRad = (angleDeg * Math.PI) / 180;
    return {
      x: cx + radius * Math.cos(angleRad),
      y: cy - radius * Math.sin(angleRad),
    };
  }

  function arcPath(cx, cy, radius, startAngle, endAngle) {
    const start = polarToCartesian(cx, cy, radius, startAngle);
    const end = polarToCartesian(cx, cy, radius, endAngle);
    const largeArcFlag = Math.abs(startAngle - endAngle) > 180 ? 1 : 0;
    const sweepFlag = endAngle < startAngle ? 1 : 0;
    return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${radius.toFixed(2)} ${radius.toFixed(2)} 0 ${largeArcFlag} ${sweepFlag} ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
  }

  function calculateNps(records) {
    const valid = records
      .map((record) => Number(record.nota_numerica))
      .filter((score) => !Number.isNaN(score) && score >= 0 && score <= 10);

    const total = valid.length;

    if (total === 0) {
      return {
        nps: 0,
        total: 0,
        promoters: 0,
        neutrals: 0,
        detractors: 0,
        promotersPct: 0,
        neutralsPct: 0,
        detractorsPct: 0,
      };
    }

    const promoters = valid.filter((score) => score >= 9).length;
    const neutrals = valid.filter((score) => score >= 7 && score <= 8).length;
    const detractors = valid.filter((score) => score <= 6).length;

    const promotersPct = (promoters / total) * 100;
    const neutralsPct = (neutrals / total) * 100;
    const detractorsPct = (detractors / total) * 100;

    return {
      nps: promotersPct - detractorsPct,
      total,
      promoters,
      neutrals,
      detractors,
      promotersPct,
      neutralsPct,
      detractorsPct,
    };
  }

  function buildDistribution(records) {
    const distribution = {};
    for (let score = 0; score <= 10; score += 1) {
      distribution[score] = 0;
    }

    records.forEach((record) => {
      const score = Number(record.nota_numerica);
      if (!Number.isNaN(score) && score >= 0 && score <= 10) {
        distribution[Math.round(score)] += 1;
      }
    });

    return distribution;
  }

  function buildRanking(records) {
    const grouped = new Map();
    let ignored = 0;

    records.forEach((record) => {
      if (record.csm === "Sem CSM") {
        ignored += 1;
        return;
      }

      const bucket = grouped.get(record.csm) || [];
      bucket.push(record);
      grouped.set(record.csm, bucket);
    });

    const ranking = Array.from(grouped.entries()).map(([csm, items]) => {
      const summary = calculateNps(items);
      return {
        csm,
        responses: items.length,
        nps: summary.nps,
      };
    });

    ranking.sort((left, right) => {
      if (right.nps !== left.nps) {
        return right.nps - left.nps;
      }
      if (right.responses !== left.responses) {
        return right.responses - left.responses;
      }
      return left.csm.localeCompare(right.csm, "pt-BR");
    });

    return { ranking, ignored };
  }

  function matchesQuery(record, query) {
    if (!query) {
      return true;
    }

    const haystack = `${record.cliente} ${record.nome_contato} ${record.csm}`.toLowerCase();
    return haystack.includes(query);
  }

  function getState() {
    return {
      csm: controls.csm?.value || "",
      classification: controls.classification?.value || "",
      score: controls.score?.value || "",
      query: (controls.query?.value || "").trim().toLowerCase(),
    };
  }

  function filterSentRecords(state) {
    return sentRecords.filter((record) => {
      const csmMatch = !state.csm || record.csm === state.csm;
      return csmMatch && matchesQuery(record, state.query);
    });
  }

  function filterResponseRecords(state) {
    return responseRecords.filter((record) => {
      const csmMatch = !state.csm || record.csm === state.csm;
      const classificationMatch = !state.classification || record.classificacao_nps === state.classification;
      const scoreMatch = !state.score || String(record.nota_numerica) === state.score;
      return csmMatch && classificationMatch && scoreMatch && matchesQuery(record, state.query);
    });
  }

  function renderStatusBadge(zoneMeta) {
    return `
      <span class="status-badge ${zoneMeta.badgeClass}">
        <span class="status-badge__dot" aria-hidden="true"></span>
        <span>${escapeHtml(zoneMeta.label)}</span>
      </span>
    `;
  }

  function renderGaugeSvg(summary, zoneMeta) {
    const cx = 340;
    const cy = 320;
    const radius = 248;
    const displayValue = Math.round(summary.nps);

    const segmentPaths = zoneMetas.map((segment) => {
      const startAngle = scoreToAngle(segment.start);
      const endAngle = scoreToAngle(segment.end);
      const path = arcPath(cx, cy, radius, startAngle, endAngle);
      return `<path d="${path}" class="gauge-arc" stroke="${segment.color}"></path>`;
    });

    const zoneLabels = zoneMetas.map((segment) => {
      const coords = polarToCartesian(cx, cy, radius - 82, scoreToAngle((segment.start + segment.end) / 2));
      return `<text x="${coords.x.toFixed(2)}" y="${coords.y.toFixed(2)}" class="gauge-zone-label">${escapeHtml(segment.label)}</text>`;
    });

    const tickSpecs = [
      [-100, "-100", "major"],
      [-50, "-50", "minor"],
      [0, "0", "major"],
      [50, "50", "major"],
      [75, "75", "minor"],
      [100, "100", "major"],
    ];

    const tickMarks = [];
    const tickLabels = [];
    tickSpecs.forEach(([tickValue, tickLabel, tickKind]) => {
      const tickAngle = scoreToAngle(tickValue);
      const dot = polarToCartesian(cx, cy, radius + 12, tickAngle);
      const label = polarToCartesian(cx, cy, radius + 34, tickAngle);
      const dotClass = tickKind === "major" ? "gauge-tick-dot" : "gauge-tick-dot gauge-tick-dot--minor";
      const labelClass = tickKind === "major" ? "gauge-tick-label" : "gauge-tick-label gauge-tick-label--minor";
      tickMarks.push(`<circle cx="${dot.x.toFixed(2)}" cy="${dot.y.toFixed(2)}" r="4" class="${dotClass}"></circle>`);
      tickLabels.push(`<text x="${label.x.toFixed(2)}" y="${label.y.toFixed(2)}" class="${labelClass}">${tickLabel}</text>`);
    });

    const needle = polarToCartesian(cx, cy, radius - 22, scoreToAngle(summary.nps));

    return `
      <svg viewBox="0 0 680 460" class="gauge-svg" role="img" aria-label="NPS final ${displayValue}">
        <g>${segmentPaths.join("")}</g>
        <g>${zoneLabels.join("")}</g>
        <g>${tickMarks.join("")}</g>
        <g>${tickLabels.join("")}</g>
        <line x1="${cx}" y1="${cy}" x2="${needle.x.toFixed(2)}" y2="${needle.y.toFixed(2)}" class="gauge-needle"></line>
        <circle cx="${cx}" cy="${cy}" r="14" class="gauge-pivot-outer"></circle>
        <circle cx="${cx}" cy="${cy}" r="6" class="gauge-pivot-inner"></circle>
        <text x="${cx}" y="382" class="gauge-value ${zoneMeta.valueClass}">${displayValue}</text>
        <text x="${cx}" y="409" class="gauge-base">Base NPS: ${summary.total} respostas com nota</text>
      </svg>
    `;
  }

  function renderGaugeCard(summary) {
    const zoneMeta = getZoneMeta(summary.nps);
    const legendItems = [
      ["promoter", "Prom.", summary.promoters, summary.promotersPct],
      ["neutral", "Neut.", summary.neutrals, summary.neutralsPct],
      ["detractor", "Det.", summary.detractors, summary.detractorsPct],
    ];

    const legendMarkup = legendItems.map(([key, label, count, percent]) => `
      <li class="gauge-legend__item">
        <span class="legend-dot ${legendStyles[key]}" aria-hidden="true"></span>
        <span><strong>${count}</strong> ${label} (${formatPercent(percent)})</span>
      </li>
    `).join("");

    return `
      <section class="card card-gauge">
        <div class="card-head">
          <div class="card-head__content">
            <p class="eyebrow">Indicador principal</p>
            <h2 class="card-title">NPS Final</h2>
          </div>
          ${renderStatusBadge(zoneMeta)}
        </div>
        <figure class="gauge-figure">
          ${renderGaugeSvg(summary, zoneMeta)}
        </figure>
        <ul class="gauge-legend" aria-label="Composição do NPS">
          ${legendMarkup}
        </ul>
        <p class="card-footnote">NPS = porcentagem de promotores (9-10) menos porcentagem de detratores (0-6).</p>
      </section>
    `;
  }

  function renderMetricCard(title, value, subtitle, modifierClass = "") {
    const extraClass = modifierClass ? ` ${modifierClass}` : "";
    return `
      <section class="card metric-card${extraClass}">
        <div class="card-head card-head--tight">
          <div class="card-head__content">
            <p class="eyebrow">Resumo</p>
            <h2 class="card-title">${escapeHtml(title)}</h2>
          </div>
        </div>
        <div class="metric-value">${escapeHtml(value)}</div>
        <p class="metric-subtitle">${escapeHtml(subtitle)}</p>
      </section>
    `;
  }

  function renderDistributionCard(distribution, totalScored) {
    if (!totalScored) {
      return `
        <section class="card card-wide card-distribution">
          <div class="card-head">
            <div class="card-head__content">
              <p class="eyebrow">Volume por nota</p>
              <h2 class="card-title">Distribuição por Nota (0-10)</h2>
            </div>
          </div>
          <p class="empty-state">Ainda não há respostas com nota válida para exibir o gráfico.</p>
        </section>
      `;
    }

    const maxCount = Math.max(...Object.values(distribution));
    const columns = Object.entries(distribution).map(([score, count]) => {
      const numericScore = Number(score);
      const height = maxCount ? (count / maxCount) * 100 : 0;
      const finalHeight = count > 0 ? Math.max(height, 8) : 0;
      const barClass = numericScore <= 6
        ? "bar-fill--detractor"
        : numericScore <= 8
          ? "bar-fill--neutral"
          : "bar-fill--promoter";

      return `
        <div class="bar-column">
          <div class="bar-value-label">${count}</div>
          <div class="bar-track">
            <div class="bar-fill ${barClass}" style="height: ${finalHeight.toFixed(2)}%"></div>
          </div>
          <div class="bar-score-label">${score}</div>
        </div>
      `;
    }).join("");

    return `
      <section class="card card-wide card-distribution">
        <div class="card-head">
          <div class="card-head__content">
            <p class="eyebrow">Volume por nota</p>
            <h2 class="card-title">Distribuição por Nota (0-10)</h2>
          </div>
          <p class="chart-caption">${totalScored} respostas com nota válida</p>
        </div>
        <div class="bar-chart" aria-label="Gráfico de distribuição por nota">
          ${columns}
        </div>
      </section>
    `;
  }

  function renderRankingCard(ranking, ignored) {
    let content = '<p class="empty-state">Ainda não há respostas com CSM para montar o ranking.</p>';

    if (ranking.length) {
      const items = ranking.map((item, index) => {
        const zoneMeta = getZoneMeta(item.nps);
        return `
          <li class="ranking-item">
            <div class="ranking-position">${index + 1}º</div>
            <div class="ranking-content">
              <div class="ranking-name">${escapeHtml(item.csm)}</div>
              <div class="ranking-meta">${pluralizeResponses(item.responses)}</div>
            </div>
            <div class="ranking-badge ${zoneMeta.badgeClass}">NPS ${Math.round(item.nps)}</div>
          </li>
        `;
      }).join("");

      content = `<ol class="ranking-list">${items}</ol>`;
    }

    const footnote = ignored > 0
      ? `<p class="card-footnote">${ignored} respostas com nota válida ficaram fora do ranking por não terem CSM preenchido.</p>`
      : "";

    return `
      <section class="card card-ranking">
        <div class="card-head">
          <div class="card-head__content">
            <p class="eyebrow">Performance por carteira</p>
            <h2 class="card-title">Ranking CSM por NPS</h2>
          </div>
        </div>
        ${content}
        ${footnote}
      </section>
    `;
  }

  function renderTableCard(rows) {
    if (!rows.length) {
      return `
        <section class="card card-wide card-table">
          <div class="card-head">
            <div class="card-head__content">
              <p class="eyebrow">Base completa</p>
              <h2 class="card-title">Todas as Respostas</h2>
            </div>
          </div>
          <p class="empty-state">Nenhuma resposta encontrada para os filtros atuais.</p>
        </section>
      `;
    }

    const ordered = [...rows].sort((left, right) => String(right.data_resposta).localeCompare(String(left.data_resposta)));
    const tableRows = ordered.map((row) => {
      const score = row.nota_numerica === null || row.nota_numerica === undefined ? "-" : String(row.nota_numerica);
      const classification = normalizeText(row.classificacao_nps, classifyScore(row.nota_numerica));
      const pillClass = classStyles[classification] || "";
      return `
        <tr>
          <td>${escapeHtml(row.cliente)}</td>
          <td>${escapeHtml(row.nome_contato)}</td>
          <td>${escapeHtml(row.csm)}</td>
          <td><span class="score-chip">${escapeHtml(score)}</span></td>
          <td><span class="pill ${pillClass}">${escapeHtml(classification)}</span></td>
          <td class="message-cell">${escapeHtml(row.mensagem_melhoria)}</td>
        </tr>
      `;
    }).join("");

    return `
      <section class="card card-wide card-table">
        <div class="card-head">
          <div class="card-head__content">
            <p class="eyebrow">Base completa</p>
            <h2 class="card-title">Todas as Respostas</h2>
          </div>
          <p class="chart-caption">${rows.length} respostas registradas</p>
        </div>
        <div class="table-shell">
          <table>
            <caption class="sr-only">Tabela com todas as respostas de NPS</caption>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Nome do contato</th>
                <th>CSM</th>
                <th>Nota</th>
                <th>Classificação</th>
                <th>Mensagem de melhoria</th>
              </tr>
            </thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>
      </section>
    `;
  }

  function renderFilterSummary(state, filteredResponses, baseSent) {
    const chips = [];

    if (state.csm) {
      chips.push(`<span class="filter-chip">CSM: ${escapeHtml(state.csm)}</span>`);
    }
    if (state.classification) {
      chips.push(`<span class="filter-chip">Classificação: ${escapeHtml(state.classification)}</span>`);
    }
    if (state.score) {
      chips.push(`<span class="filter-chip">Nota: ${escapeHtml(state.score)}</span>`);
    }
    if (state.query) {
      chips.push(`<span class="filter-chip">Busca: ${escapeHtml(state.query)}</span>`);
    }
    if (!chips.length) {
      chips.push('<span class="filter-chip filter-chip--muted">Visão consolidada</span>');
    }

    chips.push(`<span class="filter-chip filter-chip--soft">${filteredResponses.length} respondentes visíveis</span>`);
    chips.push(`<span class="filter-chip filter-chip--soft">${baseSent.length} envios na base filtrável</span>`);

    slots.summary.innerHTML = chips.join("");
  }

  function render() {
    const state = getState();
    const filteredResponses = filterResponseRecords(state);
    const baseSent = filterSentRecords(state);
    const summary = calculateNps(filteredResponses);
    const distribution = buildDistribution(filteredResponses);
    const { ranking, ignored } = buildRanking(filteredResponses.filter((record) => record.nota_numerica !== null));
    const responseRate = baseSent.length ? (filteredResponses.length / baseSent.length) * 100 : 0;

    slots.gauge.innerHTML = renderGaugeCard(summary);
    slots.respondents.innerHTML = renderMetricCard(
      "Total de Respondentes",
      formatNumber(filteredResponses.length),
      "Clientes com data_resposta preenchida na seleção atual.",
      "metric-card--respondents",
    );

    let rateSubtitle = `${formatNumber(filteredResponses.length)} respostas em ${formatNumber(baseSent.length)} envios filtráveis.`;
    if (state.classification || state.score) {
      rateSubtitle += " Nota/classificação refinam apenas os respondentes.";
    }

    slots.rate.innerHTML = renderMetricCard(
      "Taxa de Resposta",
      formatPercent(responseRate, 2),
      rateSubtitle,
      "metric-card--rate",
    );
    slots.distribution.innerHTML = renderDistributionCard(distribution, summary.total);
    slots.ranking.innerHTML = renderRankingCard(ranking, ignored);
    slots.table.innerHTML = renderTableCard(filteredResponses);
    renderFilterSummary(state, filteredResponses, baseSent);
  }

  function resetFilters() {
    controls.csm.value = "";
    controls.classification.value = "";
    controls.score.value = "";
    controls.query.value = "";
    render();
  }

  [controls.csm, controls.classification, controls.score].forEach((element) => {
    element?.addEventListener("change", render);
  });

  controls.query?.addEventListener("input", render);
  controls.reset?.addEventListener("click", resetFilters);
  controls.print?.addEventListener("click", () => window.print());

  render();
})();
