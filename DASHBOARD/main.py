from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "dados_20260423.csv"
OUTPUT_PATH = BASE_DIR / "index.html"
STYLESHEET_PATH = BASE_DIR / "styles.css"
STYLESHEET_NAME = STYLESHEET_PATH.name
SCRIPT_PATH = BASE_DIR / "dashboard.js"
SCRIPT_NAME = SCRIPT_PATH.name
TABLE_VISIBLE_ROWS = 10
DISPLAY_TIMEZONE = ZoneInfo("America/Sao_Paulo")


@dataclass(frozen=True)
class ZoneMeta:
    label: str
    start: float
    end: float
    color: str
    badge_class: str
    value_class: str


ZONE_METAS = (
    ZoneMeta("Crítica", -100, 0, "#ef4444", "status-badge--critical", "nps-value--critical"),
    ZoneMeta("Aperfeiçoamento", 0, 50, "#ff8a3d", "status-badge--improvement", "nps-value--improvement"),
    ZoneMeta("Qualidade", 50, 75, "#f2ba14", "status-badge--quality", "nps-value--quality"),
    ZoneMeta("Excelência", 75, 100, "#4fbe6e", "status-badge--excellence", "nps-value--excellence"),
)

CLASS_STYLES = {
    "Promotor": "pill--promoter",
    "Neutro": "pill--neutral",
    "Detrator": "pill--detractor",
}

LEGEND_STYLES = {
    "promoter": "legend-dot--promoter",
    "neutral": "legend-dot--neutral",
    "detractor": "legend-dot--detractor",
}


def load_data(csv_path: Path) -> pd.DataFrame:
    dataframe = pd.read_csv(csv_path)

    for column in ("data_envio", "data_resposta"):
        if column in dataframe.columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce", utc=True)

    dataframe["nota_numerica"] = pd.to_numeric(dataframe["nota_numerica"], errors="coerce")
    return dataframe


def normalize_text(value: object, fallback: str = "-") -> str:
    if pd.isna(value):
        return fallback

    text = str(value).strip()
    return text or fallback


def normalize_csm(value: object) -> str:
    return normalize_text(value, "Sem CSM")


def format_number(value: float, decimals: int = 0) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{format_number(value, decimals)}%"


def format_datetime_local(value: object) -> str:
    if pd.isna(value):
        return "-"

    if isinstance(value, pd.Timestamp):
        timestamp = value
    else:
        parsed = pd.to_datetime(value, errors="coerce", utc=True)
        if pd.isna(parsed):
            return "-"
        timestamp = parsed

    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")

    localized = timestamp.tz_convert(DISPLAY_TIMEZONE)
    return localized.strftime("%d/%m/%Y %H:%M")


def format_response_datetime(value: object) -> str:
    return format_datetime_local(value)


def format_sent_datetime(value: object) -> str:
    return format_datetime_local(value)


def is_missing_wa_id(value: object) -> bool:
    if pd.isna(value):
        return True

    normalized = str(value).strip().lower()
    return normalized in {"", "undefined", "nan", "none", "null"}


def pluralize_responses(total: int) -> str:
    return "1 resp." if total == 1 else f"{total} resp."


def classify_score(score: float | None) -> str:
    if score is None or pd.isna(score):
        return "-"
    if score >= 9:
        return "Promotor"
    if score >= 7:
        return "Neutro"
    return "Detrator"


def get_zone_meta(nps_score: float) -> ZoneMeta:
    if nps_score <= 0:
        return ZONE_METAS[0]
    if nps_score <= 50:
        return ZONE_METAS[1]
    if nps_score <= 75:
        return ZONE_METAS[2]
    return ZONE_METAS[3]


def score_to_angle(score: float) -> float:
    clamped = max(-100.0, min(100.0, float(score)))
    return 180.0 - ((clamped + 100.0) / 200.0 * 180.0)


def polar_to_cartesian(cx: float, cy: float, radius: float, angle_deg: float) -> tuple[float, float]:
    angle_rad = math.radians(angle_deg)
    x = cx + radius * math.cos(angle_rad)
    y = cy - radius * math.sin(angle_rad)
    return x, y


def arc_path(cx: float, cy: float, radius: float, start_angle: float, end_angle: float) -> str:
    start_x, start_y = polar_to_cartesian(cx, cy, radius, start_angle)
    end_x, end_y = polar_to_cartesian(cx, cy, radius, end_angle)
    large_arc_flag = 1 if abs(start_angle - end_angle) > 180 else 0
    # O gauge deve sempre percorrer o semicírculo superior da esquerda para a direita.
    sweep_flag = 1 if end_angle < start_angle else 0
    return (
        f"M {start_x:.2f} {start_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc_flag} {sweep_flag} {end_x:.2f} {end_y:.2f}"
    )


def calculate_nps(scores: pd.Series) -> dict[str, float | int]:
    valid_scores = scores.dropna()
    total = int(len(valid_scores))

    if total == 0:
        return {
            "nps": 0.0,
            "total": 0,
            "promoters": 0,
            "neutrals": 0,
            "detractors": 0,
            "promoters_pct": 0.0,
            "neutrals_pct": 0.0,
            "detractors_pct": 0.0,
        }

    promoters = int(((valid_scores >= 9) & (valid_scores <= 10)).sum())
    neutrals = int(((valid_scores >= 7) & (valid_scores <= 8)).sum())
    detractors = int(((valid_scores >= 0) & (valid_scores <= 6)).sum())

    promoters_pct = promoters / total * 100
    neutrals_pct = neutrals / total * 100
    detractors_pct = detractors / total * 100
    nps_score = promoters_pct - detractors_pct

    return {
        "nps": float(nps_score),
        "total": total,
        "promoters": promoters,
        "neutrals": neutrals,
        "detractors": detractors,
        "promoters_pct": float(promoters_pct),
        "neutrals_pct": float(neutrals_pct),
        "detractors_pct": float(detractors_pct),
    }


def build_distribution(scored_responses: pd.DataFrame) -> dict[int, int]:
    counts = (
        scored_responses["nota_numerica"]
        .round()
        .astype(int)
        .value_counts()
        .reindex(range(11), fill_value=0)
        .sort_index()
    )
    return {int(score): int(total) for score, total in counts.items()}


def build_ranking(scored_responses: pd.DataFrame) -> tuple[list[dict[str, object]], int]:
    ranking_base = scored_responses.copy()
    ranking_base["csm"] = ranking_base["csm"].fillna("").astype(str).str.strip()
    ranking_base = ranking_base[ranking_base["csm"] != ""]

    ranking = []
    for csm_name, group in ranking_base.groupby("csm"):
        summary = calculate_nps(group["nota_numerica"])
        ranking.append(
            {
                "csm": csm_name,
                "responses": int(len(group)),
                "nps": float(summary["nps"]),
            }
        )

    ranking.sort(key=lambda item: (-item["nps"], -item["responses"], str(item["csm"]).lower()))
    ignored = int(len(scored_responses) - sum(item["responses"] for item in ranking))
    return ranking, ignored


def prepare_table_rows(responses: pd.DataFrame) -> list[dict[str, str]]:
    ordered = responses.sort_values("data_resposta", ascending=False).copy()
    rows = []

    for _, row in ordered.iterrows():
        score = row["nota_numerica"]
        classification = normalize_text(row["classificacao_nps"], classify_score(score))

        rows.append(
            {
                "cliente": normalize_text(row["cliente"], "Sem cliente"),
                "nome_contato": normalize_text(row["nome_contato"], "Sem contato"),
                "csm": normalize_csm(row["csm"]),
                "data_resposta": format_response_datetime(row["data_resposta"]),
                "nota_numerica": "-" if pd.isna(score) else str(int(round(float(score)))),
                "classificacao_nps": classification,
                "mensagem_melhoria": normalize_text(row["mensagem_melhoria"], "Sem comentário"),
            }
        )

    return rows


def serialize_sent_records(sent: pd.DataFrame) -> list[dict[str, str]]:
    records = []
    ordered = sent.sort_values("data_envio", ascending=False).copy()

    for _, row in ordered.iterrows():
        records.append(
            {
                "cliente": normalize_text(row["cliente"], "Sem cliente"),
                "nome_contato": normalize_text(row["nome_contato"], "Sem contato"),
                "csm": normalize_csm(row["csm"]),
            }
        )

    return records


def serialize_response_records(responses: pd.DataFrame) -> list[dict[str, object]]:
    records = []
    ordered = responses.sort_values("data_resposta", ascending=False).copy()

    for _, row in ordered.iterrows():
        score = row["nota_numerica"]
        classification = normalize_text(row["classificacao_nps"], classify_score(score))

        records.append(
            {
                "cliente": normalize_text(row["cliente"], "Sem cliente"),
                "nome_contato": normalize_text(row["nome_contato"], "Sem contato"),
                "csm": normalize_csm(row["csm"]),
                "nota_numerica": None if pd.isna(score) else int(round(float(score))),
                "classificacao_nps": classification,
                "mensagem_melhoria": normalize_text(row["mensagem_melhoria"], "Sem comentário"),
                "data_resposta": "" if pd.isna(row["data_resposta"]) else row["data_resposta"].isoformat(),
            }
        )

    return records


def prepare_undelivered_rows(undelivered: pd.DataFrame) -> list[dict[str, str]]:
    ordered = undelivered.sort_values("data_envio", ascending=False).copy()
    rows = []

    for _, row in ordered.iterrows():
        rows.append(
            {
                "cliente": normalize_text(row["cliente"], "Sem cliente"),
                "nome_contato": normalize_text(row["nome_contato"], "Sem contato"),
                "csm": normalize_csm(row["csm"]),
                "data_envio": format_sent_datetime(row["data_envio"]),
                "status_processamento": normalize_text(row["status_processamento"], "Sem status"),
            }
        )

    return rows


def serialize_undelivered_records(undelivered: pd.DataFrame) -> list[dict[str, str]]:
    records = []
    ordered = undelivered.sort_values("data_envio", ascending=False).copy()

    for _, row in ordered.iterrows():
        records.append(
            {
                "cliente": normalize_text(row["cliente"], "Sem cliente"),
                "nome_contato": normalize_text(row["nome_contato"], "Sem contato"),
                "csm": normalize_csm(row["csm"]),
                "data_envio": "" if pd.isna(row["data_envio"]) else row["data_envio"].isoformat(),
                "status_processamento": normalize_text(row["status_processamento"], "Sem status"),
            }
        )

    return records


def build_filter_options(sent: pd.DataFrame) -> dict[str, list[str]]:
    csm_options = sorted(
        {normalize_csm(value) for value in sent["csm"].tolist()},
        key=lambda item: (item == "Sem CSM", item.lower()),
    )

    return {
        "csm": csm_options,
        "classificacao": ["Promotor", "Neutro", "Detrator"],
        "nota": [str(score) for score in range(11)],
    }


def render_filter_options(options: list[str], all_label: str) -> str:
    items = [f'<option value="">{escape(all_label)}</option>']
    items.extend(f'<option value="{escape(option)}">{escape(option)}</option>' for option in options)
    return "".join(items)


def render_filters_card(filter_options: dict[str, list[str]]) -> str:
    csm_options = render_filter_options(filter_options["csm"], "Todos os CSMs")
    classification_options = render_filter_options(filter_options["classificacao"], "Todas as classificações")
    score_options = render_filter_options(filter_options["nota"], "Todas as notas")

    return f"""
    <section class="card card-filters">
      <div class="filters-head">
        <div class="filters-head__content">
          <p class="eyebrow">Leitura executiva</p>
          <h2 class="card-title">Filtros e Exportação</h2>
          <p class="filters-description">
            Refine a análise por responsável, classificação, nota ou texto e use a impressão para gerar uma versão limpa para board.
          </p>
        </div>
        <div class="filters-actions">
          <button type="button" class="toolbar-button toolbar-button--ghost" id="reset-filters">
            Limpar filtros
          </button>
          <button type="button" class="toolbar-button toolbar-button--primary" id="print-dashboard">
            Exportar / Imprimir
          </button>
        </div>
      </div>
      <form class="filters-grid" id="dashboard-filters" autocomplete="off">
        <label class="filter-field">
          <span class="filter-label">CSM</span>
          <select id="filter-csm" name="csm">
            {csm_options}
          </select>
        </label>
        <label class="filter-field">
          <span class="filter-label">Classificação</span>
          <select id="filter-classificacao" name="classificacao">
            {classification_options}
          </select>
        </label>
        <label class="filter-field">
          <span class="filter-label">Nota</span>
          <select id="filter-nota" name="nota">
            {score_options}
          </select>
        </label>
        <label class="filter-field filter-field--search">
          <span class="filter-label">Buscar cliente ou contato</span>
          <input id="filter-busca" name="busca" type="search" placeholder="Ex.: Rede Shopping, Patricia..." />
        </label>
      </form>
      <div class="filters-footer">
        <div class="filter-summary" id="active-filter-summary" aria-live="polite"></div>
        <p class="filters-note">
          A taxa de resposta usa a base filtrável por <strong>CSM</strong> e <strong>busca</strong>; classificação e nota refinam os respondentes exibidos.
        </p>
      </div>
      <noscript>
        <p class="filters-note">Ative JavaScript para usar os filtros e a exportação.</p>
      </noscript>
    </section>
    """


def render_status_badge(zone_meta: ZoneMeta) -> str:
    return f"""
    <span class="status-badge {zone_meta.badge_class}">
      <span class="status-badge__dot" aria-hidden="true"></span>
      <span>{escape(zone_meta.label)}</span>
    </span>
    """


def render_gauge_svg(summary: dict[str, float | int], zone_meta: ZoneMeta) -> str:
    cx = 340
    cy = 320
    radius = 248
    value = float(summary["nps"])
    display_value = int(round(value))

    segment_paths = []
    zone_labels = []

    for segment in ZONE_METAS:
        start_angle = score_to_angle(segment.start)
        end_angle = score_to_angle(segment.end)
        path = arc_path(cx, cy, radius, start_angle, end_angle)
        segment_paths.append(
            f'<path d="{path}" class="gauge-arc" stroke="{segment.color}"></path>'
        )

        label_x, label_y = polar_to_cartesian(
            cx,
            cy,
            radius - 82,
            score_to_angle((segment.start + segment.end) / 2),
        )
        zone_labels.append(
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" class="gauge-zone-label">{escape(segment.label)}</text>'
        )

    tick_specs = [
        (-100, "-100", "major"),
        (-50, "-50", "minor"),
        (0, "0", "major"),
        (50, "50", "major"),
        (75, "75", "minor"),
        (100, "100", "major"),
    ]

    tick_marks = []
    tick_labels = []
    for tick_value, tick_label, tick_kind in tick_specs:
        tick_angle = score_to_angle(tick_value)
        dot_x, dot_y = polar_to_cartesian(cx, cy, radius + 12, tick_angle)
        label_x, label_y = polar_to_cartesian(cx, cy, radius + 34, tick_angle)
        dot_class = "gauge-tick-dot" if tick_kind == "major" else "gauge-tick-dot gauge-tick-dot--minor"
        label_class = "gauge-tick-label" if tick_kind == "major" else "gauge-tick-label gauge-tick-label--minor"

        tick_marks.append(f'<circle cx="{dot_x:.2f}" cy="{dot_y:.2f}" r="4" class="{dot_class}"></circle>')
        tick_labels.append(f'<text x="{label_x:.2f}" y="{label_y:.2f}" class="{label_class}">{tick_label}</text>')

    needle_x, needle_y = polar_to_cartesian(cx, cy, radius - 22, score_to_angle(value))

    return f"""
    <svg viewBox="0 0 680 460" class="gauge-svg" role="img" aria-label="NPS final {display_value}">
      <g>{''.join(segment_paths)}</g>
      <g>{''.join(zone_labels)}</g>
      <g>{''.join(tick_marks)}</g>
      <g>{''.join(tick_labels)}</g>
      <line x1="{cx}" y1="{cy}" x2="{needle_x:.2f}" y2="{needle_y:.2f}" class="gauge-needle"></line>
      <circle cx="{cx}" cy="{cy}" r="14" class="gauge-pivot-outer"></circle>
      <circle cx="{cx}" cy="{cy}" r="6" class="gauge-pivot-inner"></circle>
      <text x="{cx}" y="382" class="gauge-value {zone_meta.value_class}">{display_value}</text>
      <text x="{cx}" y="409" class="gauge-base">Base NPS: {summary["total"]} respostas com nota</text>
    </svg>
    """


def render_gauge_card(summary: dict[str, float | int]) -> str:
    zone_meta = get_zone_meta(float(summary["nps"]))
    legend_items = [
        ("promoter", "Prom.", int(summary["promoters"]), float(summary["promoters_pct"])),
        ("neutral", "Neut.", int(summary["neutrals"]), float(summary["neutrals_pct"])),
        ("detractor", "Det.", int(summary["detractors"]), float(summary["detractors_pct"])),
    ]

    legend_markup = "".join(
        f"""
        <li class="gauge-legend__item">
          <span class="legend-dot {LEGEND_STYLES[key]}" aria-hidden="true"></span>
          <span><strong>{count}</strong> {label} ({format_percent(percent)})</span>
        </li>
        """
        for key, label, count, percent in legend_items
    )

    return f"""
    <section class="card card-gauge">
      <div class="card-head">
        <div class="card-head__content">
          <p class="eyebrow">Indicador principal</p>
          <h2 class="card-title">NPS Final</h2>
        </div>
        {render_status_badge(zone_meta)}
      </div>
      <figure class="gauge-figure">
        {render_gauge_svg(summary, zone_meta)}
      </figure>
      <ul class="gauge-legend" aria-label="Composição do NPS">
        {legend_markup}
      </ul>
      <p class="card-footnote">NPS = porcentagem de promotores (9-10) menos porcentagem de detratores (0-6).</p>
    </section>
    """


def render_metric_card(title: str, value: str, subtitle: str, modifier_class: str = "") -> str:
    extra_class = f" {modifier_class}" if modifier_class else ""
    return f"""
    <section class="card metric-card{extra_class}">
      <div class="card-head card-head--tight">
        <div class="card-head__content">
          <p class="eyebrow">Resumo</p>
          <h2 class="card-title">{escape(title)}</h2>
        </div>
      </div>
      <div class="metric-value">{escape(value)}</div>
      <p class="metric-subtitle">{escape(subtitle)}</p>
    </section>
    """


def render_distribution_card(distribution: dict[int, int], total_scored: int) -> str:
    if not distribution or total_scored == 0:
        return """
        <section class="card card-wide card-distribution">
          <div class="card-head">
            <div class="card-head__content">
              <p class="eyebrow">Volume por nota</p>
              <h2 class="card-title">Distribuição por Nota (0-10)</h2>
            </div>
          </div>
          <p class="empty-state">Ainda não há respostas com nota válida para exibir o gráfico.</p>
        </section>
        """

    max_count = max(distribution.values())
    chart_columns = []

    for score, count in distribution.items():
        height = (count / max_count) * 100 if max_count else 0
        min_height = 8 if count > 0 else 0
        final_height = max(height, min_height)

        if score <= 6:
            bar_class = "bar-fill--detractor"
        elif score <= 8:
            bar_class = "bar-fill--neutral"
        else:
            bar_class = "bar-fill--promoter"

        chart_columns.append(
            f"""
            <div class="bar-column">
              <div class="bar-value-label">{count}</div>
              <div class="bar-track">
                <div class="bar-fill {bar_class}" style="height: {final_height:.2f}%"></div>
              </div>
              <div class="bar-score-label">{score}</div>
            </div>
            """
        )

    return f"""
    <section class="card card-wide card-distribution">
      <div class="card-head">
        <div class="card-head__content">
          <p class="eyebrow">Volume por nota</p>
          <h2 class="card-title">Distribuição por Nota (0-10)</h2>
        </div>
        <p class="chart-caption">{total_scored} respostas com nota válida</p>
      </div>
      <div class="bar-chart" aria-label="Gráfico de distribuição por nota">
        {''.join(chart_columns)}
      </div>
    </section>
    """


def render_ranking_card(ranking: list[dict[str, object]], ignored: int) -> str:
    if not ranking:
        ranking_markup = '<p class="empty-state">Ainda não há respostas com CSM para montar o ranking.</p>'
    else:
        items = []
        for position, item in enumerate(ranking, start=1):
            nps_score = float(item["nps"])
            zone_meta = get_zone_meta(nps_score)
            items.append(
                f"""
                <li class="ranking-item">
                  <div class="ranking-position">{position}º</div>
                  <div class="ranking-content">
                    <div class="ranking-name">{escape(str(item["csm"]))}</div>
                    <div class="ranking-meta">{pluralize_responses(int(item["responses"]))}</div>
                  </div>
                  <div class="ranking-badge {zone_meta.badge_class}">NPS {int(round(nps_score))}</div>
                </li>
                """
            )
        ranking_markup = f'<ol class="ranking-list">{"".join(items)}</ol>'

    ignored_note = ""
    if ignored > 0:
        ignored_note = (
            f'<p class="card-footnote">{ignored} respostas com nota válida ficaram fora do ranking '
            "por não terem CSM preenchido.</p>"
        )

    return f"""
    <section class="card card-ranking">
      <div class="card-head">
        <div class="card-head__content">
          <p class="eyebrow">Performance por carteira</p>
          <h2 class="card-title">Ranking CSM por NPS</h2>
        </div>
      </div>
      {ranking_markup}
      {ignored_note}
    </section>
    """


def render_table_card(rows: list[dict[str, str]]) -> str:
    if not rows:
        return """
        <section class="card card-wide card-table">
          <div class="card-head">
            <div class="card-head__content">
              <p class="eyebrow">Base completa</p>
              <h2 class="card-title">Todas as Respostas</h2>
            </div>
          </div>
          <p class="empty-state">Ainda não há respostas registradas no arquivo.</p>
        </section>
        """

    table_rows = []
    for row in rows:
        classification = row["classificacao_nps"]
        pill_class = CLASS_STYLES.get(classification, "")
        table_rows.append(
            f"""
            <tr>
              <td>{escape(row["cliente"])}</td>
              <td>{escape(row["nome_contato"])}</td>
              <td>{escape(row["csm"])}</td>
              <td class="response-date-cell">{escape(row["data_resposta"])}</td>
              <td><span class="score-chip">{escape(row["nota_numerica"])}</span></td>
              <td><span class="pill {pill_class}">{escape(classification)}</span></td>
              <td class="message-cell">{escape(row["mensagem_melhoria"])}</td>
            </tr>
            """
        )

    table_shell_class = "table-shell table-shell--limited" if len(rows) > TABLE_VISIBLE_ROWS else "table-shell"
    table_shell_limit_attr = (
        f' data-row-limit="{TABLE_VISIBLE_ROWS}"'
        if len(rows) > TABLE_VISIBLE_ROWS
        else ""
    )

    return f"""
    <section class="card card-wide card-table">
      <div class="card-head">
        <div class="card-head__content">
          <p class="eyebrow">Base completa</p>
          <h2 class="card-title">Todas as Respostas</h2>
        </div>
        <p class="chart-caption">{len(rows)} respostas registradas</p>
      </div>
      <div class="{table_shell_class}"{table_shell_limit_attr}>
        <table>
          <caption class="sr-only">Tabela com todas as respostas de NPS</caption>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Nome do contato</th>
              <th>CSM</th>
              <th class="col-response-date">Data da resposta</th>
              <th>Nota</th>
              <th>Classificação</th>
              <th>Mensagem de melhoria</th>
            </tr>
          </thead>
          <tbody>
            {''.join(table_rows)}
          </tbody>
        </table>
      </div>
    </section>
    """


def render_undelivered_card(rows: list[dict[str, str]], total_sent: int) -> str:
    undelivered_total = len(rows)
    undelivered_rate = (undelivered_total / total_sent * 100) if total_sent else 0.0

    if not rows:
        return """
        <section class="card card-wide card-undelivered">
          <div class="card-head">
            <div class="card-head__content">
              <p class="eyebrow">Risco de entrega</p>
              <h2 class="card-title">Envios sem Conexão no WhatsApp</h2>
            </div>
            <p class="chart-caption">0 registros com wa_id ausente/indefinido</p>
          </div>
          <p class="empty-state">Nenhum cliente com falha de conexão no WhatsApp para os filtros atuais.</p>
          <p class="card-footnote">Critério aplicado: coluna <strong>wa_id</strong> ausente ou igual a <strong>undefined</strong>.</p>
        </section>
        """

    table_rows = []
    for row in rows:
        table_rows.append(
            f"""
            <tr>
              <td>{escape(row["cliente"])}</td>
              <td>{escape(row["nome_contato"])}</td>
              <td>{escape(row["csm"])}</td>
              <td class="send-date-cell">{escape(row["data_envio"])}</td>
              <td><span class="delivery-status-chip">{escape(row["status_processamento"])}</span></td>
            </tr>
            """
        )

    table_shell_class = "table-shell table-shell--limited" if undelivered_total > TABLE_VISIBLE_ROWS else "table-shell"
    table_shell_limit_attr = (
        f' data-row-limit="{TABLE_VISIBLE_ROWS}"'
        if undelivered_total > TABLE_VISIBLE_ROWS
        else ""
    )

    return f"""
    <section class="card card-wide card-undelivered">
      <div class="card-head">
        <div class="card-head__content">
          <p class="eyebrow">Risco de entrega</p>
          <h2 class="card-title">Envios sem Conexão no WhatsApp</h2>
        </div>
        <p class="chart-caption">
          {undelivered_total} registros ({format_percent(undelivered_rate, 2)} da base filtrável)
        </p>
      </div>
      <div class="{table_shell_class}"{table_shell_limit_attr}>
        <table>
          <caption class="sr-only">Tabela com clientes sem conexão ativa no WhatsApp</caption>
          <thead>
            <tr>
              <th>Cliente</th>
              <th>Nome do contato</th>
              <th>CSM</th>
              <th class="col-send-date">Data do envio</th>
              <th>Status processamento</th>
            </tr>
          </thead>
          <tbody>
            {''.join(table_rows)}
          </tbody>
        </table>
      </div>
      <p class="card-footnote">Critério aplicado: coluna <strong>wa_id</strong> ausente ou igual a <strong>undefined</strong>.</p>
    </section>
    """


def build_dashboard(dataframe: pd.DataFrame) -> str:
    sent = dataframe[dataframe["data_envio"].notna()].copy()
    responses = dataframe[dataframe["data_resposta"].notna()].copy()
    undelivered = (
        sent[sent["wa_id"].map(is_missing_wa_id)].copy()
        if "wa_id" in sent.columns
        else sent.iloc[0:0].copy()
    )
    scored_responses = responses[
        responses["nota_numerica"].notna()
        & (responses["nota_numerica"] >= 0)
        & (responses["nota_numerica"] <= 10)
    ].copy()

    nps_summary = calculate_nps(scored_responses["nota_numerica"])
    total_respondents = int(len(responses))
    total_sent = int(len(sent))
    response_rate = (total_respondents / total_sent * 100) if total_sent else 0.0

    distribution = build_distribution(scored_responses)
    ranking, ignored = build_ranking(scored_responses)
    table_rows = prepare_table_rows(responses)
    undelivered_rows = prepare_undelivered_rows(undelivered)
    sent_records = serialize_sent_records(sent)
    response_records = serialize_response_records(responses)
    undelivered_records = serialize_undelivered_records(undelivered)
    filter_options = build_filter_options(sent)
    generated_at = datetime.now().strftime("%d/%m/%Y às %H:%M")

    dashboard_payload = {
        "sentRecords": sent_records,
        "responseRecords": response_records,
        "undeliveredRecords": undelivered_records,
    }
    dashboard_payload_json = json.dumps(dashboard_payload, ensure_ascii=False).replace("</", "<\\/")

    hero_html = f"""
    <header class="page-head">
      <div class="page-head__content">
        <h1 class="page-title">Dashboard NPS</h1>
        <p class="page-subtitle">
          Painel gerado exclusivamente a partir do arquivo <strong>{escape(CSV_PATH.name)}</strong>.
          A taxa de resposta considera <strong>{format_number(total_sent)}</strong> envios válidos e o cálculo de NPS
          usa a coluna <strong>nota_numerica</strong> como base oficial.
        </p>
      </div>
      <p class="updated-at">Atualizado em {escape(generated_at)}</p>
    </header>
    """

    top_cards = f"""
    <section class="top-grid">
      <div class="dashboard-slot" id="slot-gauge">
        {render_gauge_card(nps_summary)}
      </div>
      <div class="dashboard-slot" id="slot-respondents">
        {render_metric_card('Total de Respondentes', format_number(total_respondents), 'Clientes com data_resposta preenchida.', 'metric-card--respondents')}
      </div>
      <div class="dashboard-slot" id="slot-rate">
        {render_metric_card('Taxa de Resposta', format_percent(response_rate, 2), f'{format_number(total_respondents)} respostas em {format_number(total_sent)} envios válidos.', 'metric-card--rate')}
      </div>
    </section>
    """

    lower_sections = f"""
    <section class="section-grid">
      <div class="dashboard-slot" id="slot-distribution">
        {render_distribution_card(distribution, int(nps_summary["total"]))}
      </div>
      <div class="dashboard-slot" id="slot-ranking">
        {render_ranking_card(ranking, ignored)}
      </div>
      <div class="dashboard-slot" id="slot-table">
        {render_table_card(table_rows)}
      </div>
      <div class="dashboard-slot" id="slot-undelivered">
        {render_undelivered_card(undelivered_rows, total_sent)}
      </div>
    </section>
    """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Dashboard de NPS gerado a partir do arquivo CSV de respostas.">
    <title>Dashboard NPS</title>
    <link rel="stylesheet" href="{escape(STYLESHEET_NAME)}">
  </head>
  <body>
    <main class="shell">
      {hero_html}
      {render_filters_card(filter_options)}
      {top_cards}
      {lower_sections}
    </main>
    <script id="dashboard-data" type="application/json">{dashboard_payload_json}</script>
    <script src="{escape(SCRIPT_NAME)}"></script>
  </body>
</html>
"""


def generate_dashboard(csv_path: Path = CSV_PATH) -> None:
    """
    Gera o HTML do dashboard a partir de um arquivo CSV.
    
    Args:
        csv_path: Caminho do arquivo CSV a usar (padrão: dados16abr.csv)
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado em: {csv_path}")
    if not STYLESHEET_PATH.exists():
        raise FileNotFoundError(f"Arquivo CSS não encontrado em: {STYLESHEET_PATH}")
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Arquivo JavaScript não encontrado em: {SCRIPT_PATH}")

    dataframe = load_data(csv_path)
    dashboard_html = build_dashboard(dataframe)
    OUTPUT_PATH.write_text(dashboard_html, encoding="utf-8")

    print(f"✅ Dashboard gerado com sucesso em: {OUTPUT_PATH}")


def main() -> None:
    generate_dashboard()


if __name__ == "__main__":
    main()
