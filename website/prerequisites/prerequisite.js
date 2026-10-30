"use strict";
// The browser selects saved Python outputs. It does not solve the pricing or
// entry game, enumerate equilibria, or calculate numerical display values.
(() => {
  const data = window.PREREQ_DATA;
  const byId = id => document.getElementById(id);
  const page = document.body.dataset.prerequisite;
  const setText = (id, value) => { byId(id).textContent = value; };
  const cell = (row, value, field, className = "") => {
    const td = document.createElement("td");
    td.textContent = value;
    td.dataset.field = field;
    if (className) td.className = className;
    row.appendChild(td);
    return td;
  };
  const firmRow = firm => {
    const row = document.createElement("tr");
    row.dataset.firm = firm.id;
    const head = document.createElement("th");
    head.scope = "row";
    head.textContent = firm.id;
    row.appendChild(head);
    return row;
  };
  if (!data || data.schema_version !== 1) {
    const status = byId(page === "ab08" ? "ab-status" : "entry-status");
    if (status) status.textContent = "Saved Python examples are unavailable. Use the source download below.";
    document.querySelectorAll("main select").forEach(control => { control.disabled = true; });
    return;
  }

  if (page === "ab08") {
    const settings = data.ab08;
    byId("ab-productivity").value = settings.defaults.productivity;
    byId("ab-conduct").value = settings.defaults.conduct;
    byId("ab-theta").value = settings.defaults.theta;
    function renderSector() {
      const key = [byId("ab-productivity").value, byId("ab-conduct").value, byId("ab-theta").value].join("|");
      const selected = settings.cases[key];
      const rows = document.createDocumentFragment();
      const detailRows = document.createDocumentFragment();
      selected.firms.forEach(firm => {
        const row = firmRow(firm);
        const share = document.createElement("td");
        share.className = "share-cell";
        share.dataset.field = "share";
        const value = document.createElement("span");
        value.className = "share-value";
        value.textContent = firm.share;
        const track = document.createElement("span");
        track.className = "share-track";
        track.setAttribute("aria-hidden", "true");
        const bar = document.createElement("span");
        bar.style.width = firm.bar_width;
        track.appendChild(bar);
        share.append(value, track);
        row.appendChild(share);
        cell(row, firm.markup, "markup", "markup-cell");
        rows.appendChild(row);
        const detail = firmRow(firm);
        cell(detail, firm.productivity, "productivity");
        cell(detail, firm.elasticity, "elasticity");
        cell(detail, firm.price, "price");
        detailRows.appendChild(detail);
      });
      byId("ab-firm-rows").replaceChildren(rows);
      byId("ab-detail-rows").replaceChildren(detailRows);
      setText("ab-status", "Share consistency check passed. Saved Python result.");
      byId("ab-lab").dataset.savedCase = key;
    }
    ["ab-productivity", "ab-conduct", "ab-theta"].forEach(id => byId(id).addEventListener("change", renderSector));
    renderSector();
  }

  if (page === "berry92") {
    const settings = data.berry;
    byId("entry-delta").value = settings.defaults.delta;
    const first = settings.cases[settings.defaults.delta];
    first.profiles.forEach(profile => {
      const option = document.createElement("option");
      option.value = String(profile.mask);
      option.textContent = profile.label;
      byId("entry-profile").appendChild(option);
    });
    byId("entry-profile").value = String(settings.defaults.profile);
    function renderEntry() {
      const delta = byId("entry-delta").value;
      const selected = settings.cases[delta];
      const profile = selected.profiles[byId("entry-profile").value];
      setText("entry-count", selected.display.count);
      setText("entry-equilibria", selected.display.equilibria);
      setText("entry-ranked", selected.display.ranked);
      const rows = document.createDocumentFragment();
      const board = document.createDocumentFragment();
      profile.firms.forEach(firm => {
        const row = firmRow(firm);
        cell(row, firm.action, "action");
        cell(row, firm.gain, "gain", "gain-" + firm.gain_class);
        rows.appendChild(row);
        const card = document.createElement("div");
        card.className = "entry-firm" + (firm.active ? " is-active" : "");
        card.dataset.firm = firm.id;
        card.dataset.active = String(firm.active);
        const name = document.createElement("strong");
        name.textContent = firm.id;
        const state = document.createElement("span");
        state.textContent = firm.active ? "Operating" : "Outside";
        card.append(name, state);
        board.appendChild(card);
      });
      byId("entry-firm-rows").replaceChildren(rows);
      byId("entry-board").replaceChildren(board);
      setText("entry-status", profile.status);
      byId("entry-status").classList.toggle("is-invalid", !profile.valid);
      byId("entry-lab").dataset.delta = delta;
      byId("entry-lab").dataset.profile = String(profile.mask);
    }
    ["entry-delta", "entry-profile"].forEach(id => byId(id).addEventListener("change", renderEntry));
    renderEntry();
  }
})();
