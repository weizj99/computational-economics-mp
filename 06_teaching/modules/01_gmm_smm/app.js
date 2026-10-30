"use strict";
// Display only: every economic value, estimate, curve and marker is precomputed.
(() => {
  const data = window.TASK10_GALLERY;
  const status = document.getElementById("asset-status");
  if (!data) {
    status.textContent = "The computed gallery is unavailable. The Python source and explanation remain available.";
    document.getElementById("walkthrough-status").textContent = "The saved calculation cannot be selected while the computed gallery is unavailable.";
    document.querySelectorAll(".lab input,.lab select,.lab button").forEach(element => { element.disabled = true; });
    return;
  }
  const sigma = document.getElementById("sigma");
  const simulations = document.getElementById("simulations");
  const draws = document.getElementById("draws");
  const walkthrough = window.MOMENT_WALKTHROUGH;
  const walkthroughStatus = document.getElementById("walkthrough-status");
  const walkthroughValues = document.getElementById("walkthrough-values");
  const showNumber = value => value.toFixed(4);
  function setText(id, value) {
    document.getElementById(id).textContent = value;
  }
  function showSavedList(id, values) {
    const list = document.getElementById(id);
    list.replaceChildren();
    values.forEach(value => {
      const item = document.createElement("li");
      item.textContent = showNumber(value);
      list.appendChild(item);
    });
  }
  function updateWalkthrough() {
    const frame = walkthrough?.by_seed?.[draws.value]?.frames?.[sigma.value];
    const selected = frame?.by_count?.[simulations.value];
    if (!frame || !selected) {
      walkthroughValues.hidden = true;
      walkthroughStatus.textContent = "The saved numerical walkthrough is unavailable. The formulas above and the computed curves remain available.";
      return;
    }
    const sector = frame.first_sector;
    const dataset = frame.first_dataset;
    // These are saved statistics. The browser only selects and formats them.
    setText("walkthrough-context", "Candidate σA = " + showNumber(frame.sigma) + " · stream " + (draws.value === "2" ? "A" : "B") + " (seed " + draws.value + ") · S = " + simulations.value + ".");
    setText("walk-sector-mean", showNumber(sector.mean));
    const rows = document.getElementById("walk-firm-rows");
    rows.replaceChildren();
    sector.values.forEach((value, index) => {
      const row = document.createElement("tr");
      const label = document.createElement("th");
      label.scope = "row";
      label.textContent = String(index + 1);
      row.appendChild(label);
      [value, sector.deviations[index], sector.squared_deviations[index]].forEach(savedValue => {
        const cell = document.createElement("td");
        cell.textContent = showNumber(savedValue);
        row.appendChild(cell);
      });
      rows.appendChild(row);
    });
    setText("walk-sum-squares", showNumber(sector.sum_squares));
    setText("walk-sector-variance", showNumber(sector.variance));
    setText("walk-sector-sum", showNumber(dataset.sum_sector_variances));
    setText("walk-dataset-moment", showNumber(dataset.moment));
    showSavedList("walk-sector-list", dataset.sector_variances);
    setText("walk-s-count", simulations.value);
    setText("walk-s-divisor", simulations.value);
    setText("walk-moment-sum", showNumber(selected.sum_moments));
    setText("walk-simulated-mean", showNumber(selected.mean));
    const displayedMoments = simulations.value === "1" ? frame.simulation_moments.slice(0, 1) : frame.simulation_moments;
    setText("walk-simulation-list-title", simulations.value === "1" ? "Inspect the selected data-set moment" : "Inspect the first " + displayedMoments.length + " data-set moments");
    showSavedList("walk-simulation-list", displayedMoments);
    setText("walk-observed", showNumber(walkthrough.observed));
    walkthroughValues.hidden = false;
    walkthroughStatus.textContent = "";
  }
  function addTableRows(id, rows, columns) {
    const body = document.getElementById(id);
    rows.forEach(row => {
      const tr = document.createElement("tr");
      columns.forEach((key, index) => {
        const cell = document.createElement(index === 0 ? "th" : "td");
        if (index === 0) cell.scope = "row";
        cell.textContent = row[key];
        tr.appendChild(cell);
      });
      body.appendChild(tr);
    });
  }
  addTableRows("estimate-table", data.estimate_rows, ["S_label", "stream_A_label", "stream_B_label"]);
  addTableRows("repetition-table", data.repetition_rows, ["method", "mean_label", "sd_label", "approximation_label"]);
  function update() {
    const group = data.groups[draws.value + "_" + simulations.value];
    const frame = group.frames[sigma.value];
    document.getElementById("sigma-value").value = frame.sigma_label;
    sigma.setAttribute("aria-valuetext", frame.sigma_label);
    document.getElementById("plot-mobile").srcset = frame.mobile_image;
    const image = document.getElementById("plot-image");
    image.src = frame.image;
    image.alt = frame.alt;
    document.getElementById("observed-value").textContent = data.observed_label;
    document.getElementById("direct-value").textContent = frame.direct_label;
    document.getElementById("simulated-value").textContent = frame.simulated_label;
    document.getElementById("direct-loss").textContent = frame.direct_loss_label;
    document.getElementById("simulated-loss").textContent = frame.simulated_loss_label;
    document.getElementById("gmm-estimate").textContent = data.gmm_label;
    document.getElementById("smm-estimate").textContent = group.smm_label;
    document.getElementById("plot-caption").textContent = group.caption;
    updateWalkthrough();
    status.textContent = data.display_note;
  }
  sigma.addEventListener("input", update);
  simulations.addEventListener("change", update);
  draws.addEventListener("change", update);
  document.getElementById("reset").addEventListener("click", () => {
    sigma.value = "25";
    simulations.value = "10";
    draws.value = "2";
    update();
  });
  update();
})();
