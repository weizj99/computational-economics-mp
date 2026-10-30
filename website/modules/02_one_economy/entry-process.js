"use strict";
// Replay labels, decisions and geometry exported from saved model traces.
// No model, profit rule, aggregate statistic or interpolation is evaluated here.
(() => {
  const root = document.getElementById("entry-process");
  if (!root) return;
  const data = window.ENTRY_PROCESS_DATA;
  const byId = id => document.getElementById(id);
  const status = byId("entry-data-status");
  const periodSelect = byId("entry-period");
  const slider = byId("entry-round");
  const previous = byId("entry-prev");
  const next = byId("entry-next");
  const play = byId("entry-play");
  const viewButtons = [...root.querySelectorAll("[data-entry-view]")];
  let periodIndex = 0;
  let roundIndex = 0;
  let timer = null;
  let view = "rounds";

  const text = (id, value) => { byId(id).textContent = value ?? ""; };
  const cell = (field, value, label, role = "cell") => {
    const node = document.createElement("div");
    node.setAttribute("role", role);
    node.dataset.entryField = field;
    node.dataset.label = label;
    node.textContent = value;
    return node;
  };
  const shareCell = (field, label, percent, column, barKey = "share") => {
    const node = cell(field, "", column);
    const amount = document.createElement("span");
    amount.className = "entry-share-value";
    amount.textContent = label;
    const track = document.createElement("span");
    track.className = "entry-share-track";
    track.setAttribute("aria-hidden", "true");
    const bar = document.createElement("span");
    bar.dataset.entryBar = barKey;
    bar.style.width = `${percent}%`;
    track.appendChild(bar);
    node.append(amount, track);
    return node;
  };
  function stop() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
    play.setAttribute("aria-pressed", "false");
    play.textContent = data?.periods?.[periodIndex]?.rounds && roundIndex === data.periods[periodIndex].rounds.length - 1 ? "Replay rounds" : "Play rounds";
  }
  function setView(key) {
    if (!new Set(["rounds", "transitions"]).has(key)) return;
    if (key !== view) stop();
    view = key;
    root.dataset.entryView = key;
    viewButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.entryView === key)));
    root.querySelectorAll("[data-entry-panel]").forEach(panel => { panel.hidden = panel.dataset.entryPanel !== key; });
  }
  viewButtons.forEach(button => button.addEventListener("click", () => setView(button.dataset.entryView)));
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
  document.addEventListener("lessonreveal", event => {
    if (!new Set(["entry", "all"]).has(event.detail.view)) stop();
    const target = event.detail.target;
    if (target?.closest("#entry-across-periods")) setView("transitions");
    else if (target?.id === "entry-process") setView("rounds");
  });
  const revealFragment = () => {
    if (location.hash === "#entry-across-periods") setView("transitions");
  };
  window.addEventListener("hashchange", revealFragment);
  revealFragment();

  if (!data || !Array.isArray(data.periods) || !data.periods.length || data.periods.some(period => !Array.isArray(period.rounds) || !period.rounds.length) || !data.transitions || !Array.isArray(data.transitions.rows)) {
    status.textContent = "The saved entry and exit replay is unavailable. The explanation remains available; the other lessons still work.";
    root.dataset.entryReady = "false";
    viewButtons.forEach(button => { button.disabled = true; });
    return;
  }
  periodSelect.replaceChildren();
  data.periods.forEach((period, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = period.label;
    periodSelect.appendChild(option);
  });
  periodSelect.disabled = false;
  slider.disabled = false;
  play.disabled = false;
  const caseLabels = [data.case_label, data.market_label].filter(Boolean);
  text("entry-case-label", caseLabels.length ? caseLabels.join(" · ") : data.subtitle);
  text("entry-scope", data.scope);

  function render() {
    const period = data.periods[periodIndex];
    const round = period.rounds[roundIndex];
    root.dataset.entryPeriod = String(periodIndex);
    root.dataset.entryRound = String(roundIndex);
    root.dataset.deletionApplied = String(round.deletion_applied);
    slider.max = String(period.rounds.length - 1);
    slider.value = String(roundIndex);
    slider.setAttribute("aria-valuetext", `${period.label}; ${round.round_label}; ${round.status_label}`);
    text("entry-round-label", round.round_label);
    text("entry-round-title", round.title);
    text("entry-round-note", round.note);
    text("entry-decision-status", round.status_label);
    text("entry-cutoff-value", round.threshold_label ?? "—");
    text("entry-wage", round.wage_label);
    text("entry-output", round.output_label);
    text("entry-global-active", round.global_active_label);
    text("entry-global-proposed", round.global_proposed_label);
    text("entry-global-actual", round.global_actual_label);
    const rows = document.createDocumentFragment();
    round.rows.forEach(firm => {
      const row = document.createElement("div");
      row.className = "entry-firm-row";
      row.setAttribute("role", "row");
      row.dataset.firmId = firm.id;
      row.dataset.status = firm.status;
      row.dataset.active = String(firm.active);
      row.dataset.proposedDrop = String(firm.proposed_drop);
      row.dataset.removed = String(firm.removed);
      row.append(cell("label", firm.label, "Firm", "rowheader"), cell("status_label", firm.status_label, "Decision"), cell("profit_label", firm.profit_label, "Profit · millionths"), shareCell("share_label", firm.share_label, firm.share_percent, "Market share"));
      rows.appendChild(row);
    });
    byId("entry-firm-rows").replaceChildren(rows);
    previous.disabled = roundIndex === 0;
    next.disabled = roundIndex === period.rounds.length - 1;
    if (timer === null) play.textContent = next.disabled ? "Replay rounds" : "Play rounds";
  }
  const jump = index => { stop(); roundIndex = index; render(); };
  previous.addEventListener("click", () => { if (roundIndex > 0) jump(roundIndex - 1); });
  next.addEventListener("click", () => { if (roundIndex < data.periods[periodIndex].rounds.length - 1) jump(roundIndex + 1); });
  slider.addEventListener("input", () => jump(Number(slider.value)));
  periodSelect.addEventListener("change", () => { stop(); periodIndex = Number(periodSelect.value); roundIndex = 0; render(); });
  play.addEventListener("click", () => {
    if (timer !== null) { stop(); return; }
    if (roundIndex === data.periods[periodIndex].rounds.length - 1) { roundIndex = 0; render(); }
    play.setAttribute("aria-pressed", "true");
    play.textContent = "Pause rounds";
    timer = window.setInterval(() => {
      if (roundIndex < data.periods[periodIndex].rounds.length - 1) { roundIndex += 1; render(); }
      if (roundIndex === data.periods[periodIndex].rounds.length - 1) stop();
    }, 1600);
  });

  const transitions = data.transitions;
  text("entry-transition-title", transitions.title);
  text("entry-transition-note", transitions.note);
  const summary = document.createDocumentFragment();
  (transitions.summary || []).forEach(item => {
    const group = document.createElement("div");
    const name = document.createElement("dt");
    name.textContent = item.label;
    const value = document.createElement("dd");
    value.textContent = item.value;
    group.append(name, value);
    summary.appendChild(group);
  });
  byId("entry-transition-summary").replaceChildren(summary);
  const rows = document.createDocumentFragment();
  transitions.rows.forEach(firm => {
    const row = document.createElement("div");
    row.className = "entry-transition-row";
    row.setAttribute("role", "row");
    row.dataset.firmId = firm.id;
    row.dataset.classification = firm.classification;
    row.append(cell("label", firm.label, "Firm", "rowheader"), cell("classification_label", firm.classification_label, "Across periods"), shareCell("period0_share_label", firm.period0_share_label, firm.period0_share_percent, "Period 1 share", "period0"), shareCell("period1_share_label", firm.period1_share_label, firm.period1_share_percent, "Period 2 share", "period1"));
    rows.appendChild(row);
  });
  byId("entry-transition-rows").replaceChildren(rows);
  root.dataset.entryReady = "true";
  status.textContent = "";
  render();
})();
