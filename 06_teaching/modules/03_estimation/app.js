"use strict";
// Select saved Python results only. No model, objective, ranking or statistics
// are evaluated in the browser.
(() => {
  const data = window.TASK12_DATA;
  const steps = window.TASK12_STEPS;
  const byId = id => document.getElementById(id);
  if (!data || data.schema_version !== 1) {
    byId("search-status").textContent = "Saved search unavailable. The Python download and tables remain available below.";
    ["best-fit", "reset", "candidate-slider", "candidate-input", "year-slider", "year-select"].forEach(id => { byId(id).disabled = true; });
    return;
  }
  const mobile = window.matchMedia("(max-width: 700px)");
  const svgNS = "http://www.w3.org/2000/svg";
  const years = data.year_order;
  let year = String(data.meta.default_year);
  let candidateIndex = data.years[year].initial_index;
  let overview = "fit";

  function setText(id, value) { byId(id).textContent = value; }
  function setPicture(imageId, sourceId, paths, alt) {
    byId(sourceId).srcset = paths.mobile;
    byId(imageId).src = paths.desktop;
    if (alt) byId(imageId).alt = alt;
  }
  function currentYear() { return data.years[year]; }
  function currentCandidate() { return currentYear().candidates[candidateIndex]; }
  function savedWidth(element, value) { element.style.width = String(value) + "%"; }
  function currentSteps() {
    const point = steps?.schema_version === 1 ? steps.years?.[year]?.candidates?.[candidateIndex] : null;
    return point?.row_id === currentCandidate().row_id ? point : null;
  }

  function renderInputs() {
    setText("input-year", year);
    const targets = document.createDocumentFragment();
    data.moments.forEach((moment, index) => {
      const div = document.createElement("div");
      const term = document.createElement("dt"); term.textContent = moment.label;
      const value = document.createElement("dd"); value.textContent = currentYear().target_display[index];
      div.append(term, value); targets.appendChild(div);
    });
    byId("target-inputs").replaceChildren(targets);
    const bounds = document.createDocumentFragment();
    [["sigma", "Dispersion σ"], ["N", "Continuous count N"], ["zeta", "Overhead control ζ"]].forEach(([key, label], index) => {
      const div = document.createElement("div");
      const term = document.createElement("dt"); term.textContent = label;
      const value = document.createElement("dd");
      const saved = steps?.schema_version === 1 ? steps.years?.[year]?.bounds_display?.[index] : null;
      value.textContent = saved ? `${saved[0]} → ${saved[1]}` : `${currentYear().box[key + "_lo"]} → ${currentYear().box[key + "_hi"]}`;
      div.append(term, value); bounds.appendChild(div);
    });
    byId("bound-inputs").replaceChildren(bounds);
  }

  function renderProcess() {
    const point = currentCandidate();
    const saved = currentSteps();
    const winner = currentYear().candidates[currentYear().best_index];
    setText("winner-summary", candidateIndex === currentYear().best_index
      ? `You are viewing the ${year} winner: candidate ${candidateIndex + 1}, with total loss ${point.display.loss}. Its three contributions are shown above.`
      : `Current candidate ${candidateIndex + 1}: loss ${point.display.loss}. The ${year} winner is candidate ${currentYear().best_index + 1}: loss ${winner.display.loss}. Both use the same targets and weights.`);
    setText("loss-addition", `${point.display.components.join(" + ")} ≈ ${point.display.loss} total loss`);
    setText("economy-bridge", `For this candidate, N ≈ ${point.display.N}; the solver uses M = floor(N) = ${point.display.M} potential firms per market. Its saved equilibrium has ${point.display.operating_firms} operating firms per market on average and φ = ${point.display.phi} in model labor units (1e−6 is one millionth). The solver's three moments appear below.`);
    const fragment = document.createDocumentFragment();
    if (!saved) {
      byId("mapping-rows").replaceChildren();
      setText("mapping-substitution", "");
      setText("process-status", "The saved arithmetic supplement is unavailable. The existing candidates, moments and scores remain available.");
      return;
    }
    const bounds = steps.years[year].bounds_display;
    const coordinates = steps.unit_coordinates[point.sobol_index];
    [["sigma", "σ"], ["N", "N"], ["zeta", "ζ"]].forEach(([key, label], index) => {
      const row = document.createElement("tr"); row.dataset.parameter = key;
      const term = document.createElement("th"); term.scope = "row"; term.textContent = label; row.appendChild(term);
      [["Lower lo", bounds[index][0]], ["Sobol u", coordinates[index]], ["Upper hi", bounds[index][1]], ["Mapped x", point.display[key]]].forEach(([name, value]) => {
        const cell = document.createElement("td"); cell.dataset.label = name; cell.textContent = value; row.appendChild(cell);
      });
      fragment.appendChild(row);
    });
    byId("mapping-rows").replaceChildren(fragment);
    setText("mapping-substitution", `For σ: ${bounds[0][0]} + ${coordinates[0]} × (${bounds[0][1]} − ${bounds[0][0]}) ≈ ${point.display.sigma}`);
    setText("process-status", "All arithmetic uses this same saved candidate. Changing the controls selects another completed calculation.");
  }

  byId("year-select").replaceChildren();
  years.forEach(value => {
    const option = document.createElement("option");
    option.value = String(value); option.textContent = String(value);
    if (String(value) === year) option.selected = true;
    byId("year-select").appendChild(option);
  });

  function renderMomentRows() {
    const point = currentCandidate();
    const yearData = currentYear();
    const fragment = document.createDocumentFragment();
    data.moments.forEach((moment, index) => {
      const tr = document.createElement("tr");
      tr.dataset.moment = moment.key;
      const th = document.createElement("th"); th.scope = "row";
      const label = document.createElement("span"); label.textContent = moment.label;
      const mini = document.createElement("span"); mini.className = "moment-mini";
      if (point.display.bar_aria && point.display.bar_aria[index]) mini.setAttribute("aria-label", point.display.bar_aria[index]);
      else mini.setAttribute("aria-hidden", "true");
      const targetBar = document.createElement("span"); targetBar.className = "target-bar";
      const modelBar = document.createElement("span"); modelBar.className = "model-bar";
      savedWidth(targetBar, point.bars[index].target); savedWidth(modelBar, point.bars[index].model);
      mini.append(targetBar, modelBar); th.append(label, mini); tr.appendChild(th);
      [["Data", yearData.target_display[index]], ["Model", point.display.moments[index]], ["Model − data", point.display.gaps[index]]].forEach(([name, value]) => {
        const td = document.createElement("td"); td.dataset.label = name; td.textContent = value; tr.appendChild(td);
      });
      const td = document.createElement("td"); td.dataset.label = "Weighted loss contribution";
      const cell = document.createElement("div"); cell.className = "loss-cell";
      const track = document.createElement("span"); track.className = "component-track"; track.setAttribute("aria-hidden", "true");
      const fill = document.createElement("span"); savedWidth(fill, point.bars[index].component); track.appendChild(fill);
      const contribution = document.createElement("strong"); contribution.textContent = point.display.components[index];
      cell.append(track, contribution); td.appendChild(cell);
      const saved = currentSteps();
      if (saved) {
        const arithmetic = document.createElement("span"); arithmetic.className = "loss-arithmetic";
        arithmetic.textContent = `${steps.weights_display[index]} × (${saved.objective_gaps[index]})²`;
        arithmetic.setAttribute("aria-label", `Weight ${steps.weights_display[index]} times the squared gap ${saved.objective_gaps[index]}, in objective units`);
        td.appendChild(arithmetic);
      }
      tr.appendChild(td); fragment.appendChild(tr);
    });
    byId("moment-rows").replaceChildren(fragment);
  }

  function renderPointOverlay() {
    const mode = mobile.matches ? "mobile" : "desktop";
    const yearData = currentYear();
    const chart = yearData.scatter[mode];
    byId("search-overlay").setAttribute("viewBox", `0 0 ${chart.width} ${chart.height}`);
    const fragment = document.createDocumentFragment();
    yearData.candidates.forEach((point, index) => {
      const circle = document.createElementNS(svgNS, "circle");
      circle.setAttribute("cx", point.point[mode].x); circle.setAttribute("cy", point.point[mode].y);
      circle.setAttribute("r", mobile.matches ? "10" : "7");
      circle.setAttribute("class", "point-target"); circle.dataset.index = String(index);
      const title = document.createElementNS(svgNS, "title"); title.textContent = `Candidate ${index + 1} · rank ${point.display.rank} · loss ${point.display.loss}`;
      circle.appendChild(title); fragment.appendChild(circle);
    });
    byId("point-targets").replaceChildren(fragment);
    positionRing();
  }

  function positionRing() {
    const mode = mobile.matches ? "mobile" : "desktop";
    const point = currentCandidate().point[mode];
    byId("selected-ring").setAttribute("cx", point.x);
    byId("selected-ring").setAttribute("cy", point.y);
    byId("selected-ring").setAttribute("r", mobile.matches ? "10" : "9");
  }

  function renderCandidate() {
    const point = currentCandidate();
    const yearData = currentYear();
    const display = point.display;
    [["sigma-value", "sigma"], ["N-value", "N"], ["M-value", "M"], ["zeta-value", "zeta"], ["phi-value", "phi"], ["firms-value", "operating_firms"], ["loss-value", "loss"], ["rank-value", "rank"]].forEach(([id, key]) => setText(id, display[key]));
    byId("candidate-slider").value = String(candidateIndex);
    byId("candidate-input").value = String(candidateIndex + 1);
    byId("candidate-slider").setAttribute("aria-valuetext", `Candidate ${candidateIndex + 1} of 512, rank ${display.rank}`);
    setText("candidate-label", `Candidate ${candidateIndex + 1} / 512`);
    const isBest = candidateIndex === yearData.best_index;
    setText("selected-status", isBest ? "Best of 512" : "Saved result");
    byId("selected-status").classList.toggle("is-best", isBest);
    setText("search-status", isBest ? yearData.best_note : "Compare the three gaps below, then try the best saved candidate.");
    byId("search").dataset.year = year;
    byId("search").dataset.candidateIndex = String(candidateIndex);
    byId("search").dataset.rowId = String(point.row_id);
    document.querySelectorAll("#top15-list button").forEach(button => button.setAttribute("aria-pressed", button.dataset.candidateIndex === String(candidateIndex) ? "true" : "false"));
    positionRing(); renderMomentRows(); renderProcess();
  }

  function selectCandidate(index) {
    if (!Number.isInteger(index) || index < 0 || index >= currentYear().candidates.length) return;
    candidateIndex = index; renderCandidate();
  }

  function renderShortlist() {
    const fragment = document.createDocumentFragment();
    currentYear().top15_indices.forEach((index, position) => {
      const point = currentYear().candidates[index];
      const button = document.createElement("button"); button.type = "button";
      button.dataset.candidateIndex = String(index);
      button.setAttribute("aria-pressed", index === candidateIndex ? "true" : "false");
      button.setAttribute("aria-label", `Rank ${position + 1}: candidate ${index + 1}, loss ${point.display.loss}`);
      const rank = document.createElement("strong"); rank.textContent = `#${position + 1}`;
      const value = document.createElement("span"); value.textContent = point.display.loss;
      button.append(rank, value); fragment.appendChild(button);
    });
    byId("top15-list").replaceChildren(fragment);
  }

  function renderYear() {
    const yearData = currentYear();
    byId("year-select").value = year;
    byId("year-slider").value = String(years.indexOf(Number(year)));
    byId("year-slider").setAttribute("aria-valuetext", year);
    setText("year-value", year);
    byId("search-mobile").srcset = yearData.scatter.mobile.src;
    byId("search-image").src = yearData.scatter.desktop.src;
    byId("search-image").width = yearData.scatter.desktop.width;
    byId("search-image").height = yearData.scatter.desktop.height;
    byId("search-image").alt = `${year}: 512 evaluated parameter candidates. Color shows loss; the diamond marks the best saved point. Each point also has a zeta value.`;
    setText("boundary-note", yearData.boundary_note);
    renderInputs(); renderShortlist(); renderPointOverlay(); renderCandidate();
  }

  function selectYear(value) {
    if (!data.years[String(value)]) return;
    year = String(value); candidateIndex = currentYear().initial_index; renderYear();
  }

  function renderOverview() {
    byId("annual-fit-figure").hidden = overview !== "fit";
    byId("annual-parameters-figure").hidden = overview !== "parameters";
    document.querySelectorAll("[data-overview]").forEach(button => button.setAttribute("aria-pressed", button.dataset.overview === overview ? "true" : "false"));
  }

  byId("year-select").addEventListener("change", event => selectYear(event.target.value));
  byId("year-slider").addEventListener("input", event => selectYear(years[Number(event.target.value)]));
  byId("candidate-slider").addEventListener("input", event => selectCandidate(Number(event.target.value)));
  byId("candidate-input").addEventListener("change", event => {
    const index = Number(event.target.value) - 1;
    if (Number.isInteger(index) && index >= 0 && index < currentYear().candidates.length) selectCandidate(index);
    else event.target.value = String(candidateIndex + 1);
  });
  byId("best-fit").addEventListener("click", () => selectCandidate(currentYear().best_index));
  byId("reset").addEventListener("click", () => selectYear(data.meta.default_year));
  byId("search-overlay").addEventListener("click", event => {
    const target = event.target.closest("[data-index]");
    if (target) selectCandidate(Number(target.dataset.index));
  });
  byId("top15-list").addEventListener("click", event => {
    const target = event.target.closest("button[data-candidate-index]");
    if (target) selectCandidate(Number(target.dataset.candidateIndex));
  });
  document.querySelectorAll("[data-overview]").forEach(button => button.addEventListener("click", () => { overview = button.dataset.overview; renderOverview(); }));
  mobile.addEventListener("change", renderPointOverlay);
  setPicture("annual-fit-image", "annual-fit-mobile", data.figures.fit);
  setPicture("annual-parameters-image", "annual-parameters-mobile", data.figures.parameters);
  setPicture("fresh-draws-image", "fresh-draws-mobile", data.figures.stability);
  const fresh = data.summary.fresh_draws;
  setText("holdout-reallocation", fresh.reallocation_rmse);
  setText("holdout-markup", fresh.markup_rmse);
  setText("holdout-sga", fresh.sga_rmse);
  renderYear(); renderOverview();
})();

