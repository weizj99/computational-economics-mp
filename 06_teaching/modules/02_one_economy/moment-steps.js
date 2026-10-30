"use strict";
// Display-only: every value, contribution and check is exported in advance by Python.
(() => {
  const root = document.getElementById("moment-calculation");
  if (!root) return;
  const data = window.TASK11_MOMENT_STEPS;
  const status = document.getElementById("moment-data-status");
  const selector = document.getElementById("moment-firm-select");
  let current = null;
  let panel = "employment";
  function rows(id, values) {
    const body = document.getElementById(id);
    body.replaceChildren();
    values.forEach(valuesInRow => {
      const row = document.createElement("tr");
      valuesInRow.forEach((value, i) => {
        const cell = document.createElement(i === 0 ? "th" : "td");
        if (i === 0) cell.scope = "row";
        cell.textContent = value;
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
  }
  function values(id, pairs) {
    const list = document.getElementById(id);
    list.replaceChildren();
    pairs.forEach(([label, value]) => {
      const row = document.createElement("div");
      const term = document.createElement("dt");
      const detail = document.createElement("dd");
      term.textContent = label;
      detail.textContent = value;
      row.append(term, detail);
      list.appendChild(row);
    });
  }
  function firm() {
    const selected = current?.firms.find(item => item.id === selector.value);
    if (!selected) return;
    document.getElementById("moment-firm-status").textContent = selected.status;
    document.getElementById("moment-firm-flow").textContent = selected.flow_label;
    rows("moment-employment-rows", selected.employment_rows);
    values("moment-sales-values", selected.sales_rows);
  }
  function showPanel() {
    root.querySelectorAll("[data-moment-panel]").forEach(button => {
      button.setAttribute("aria-pressed", String(button.dataset.momentPanel === panel));
    });
    root.querySelectorAll("[data-moment-view]").forEach(view => {
      view.hidden = view.dataset.momentView !== panel;
    });
    document.getElementById("moment-firm-control").hidden = panel === "totals";
  }
  root.querySelectorAll("[data-moment-panel]").forEach(button => {
    button.addEventListener("click", () => { panel = button.dataset.momentPanel; showPanel(); });
  });
  selector.addEventListener("change", firm);
  window.Task11MomentSteps = {
    selectCase(key) {
      const next = data?.cases[key];
      if (!next) {
        current = null;
        status.textContent = "The saved intermediate values are unavailable. The formulas and original three moment readouts remain available.";
        selector.disabled = true;
        return;
      }
      current = next;
      const oldFirm = selector.value;
      selector.replaceChildren();
      current.firms.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.label} · ${item.status}`;
        selector.appendChild(option);
      });
      if (current.firms.some(item => item.id === oldFirm)) selector.value = oldFirm;
      else selector.value = (current.firms.find(item => item.status === "Continuing") || current.firms[0]).id;
      selector.disabled = false;
      status.textContent = "";
      document.getElementById("moment-case-label").textContent = current.case_label;
      values("moment-employment-totals", current.employment_total_rows);
      rows("moment-contribution-rows", current.contribution_rows);
      firm();
      showPanel();
    }
  };
})();
