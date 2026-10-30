"use strict";
// Display-only interface. The Python exporter supplies all values and artwork.
(() => {
  const data = window.TASK11_GALLERY;
  const status = document.getElementById("asset-status");
  const selector = document.getElementById("path-select");
  const point = document.getElementById("case-point");
  const stepButtons = document.querySelectorAll("[data-step]");
  if (!data) {
    status.textContent = "The computed illustrations are unavailable. The exercise remains accessible.";
    document.querySelectorAll(".economy select,.economy input,.economy button").forEach(element => { element.disabled = true; });
    return;
  }
  const controlNames = {sigma: "Dispersion σ", entrants: "Potential firms N", overhead: "Fixed-cost control ζ", seed: "Draw seed"};
  // In every saved case ζ picks φ from the economy's firms, as in the paper.
  let step = location.hash === "#moment-calculation" ? "4" : "0";
  const cases = {};
  data.cases.forEach(item => { cases[item.id] = item; });
  selector.replaceChildren();
  Object.entries(data.paths).forEach(([key, path]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = path.label;
    selector.appendChild(option);
  });
  selector.value = data.default_path || "sigma";
  point.value = data.default_point ?? 2;
  function update() {
    const path = data.paths[selector.value];
    const currentPoint = path.points[point.value];
    const item = cases[currentPoint.case_id];
    const view = item.steps[step];
    document.getElementById("path-control-label").textContent = controlNames[selector.value];
    document.getElementById("path-control-value").textContent = currentPoint.label;
    point.setAttribute("aria-valuetext", currentPoint.label);
    document.getElementById("path-low").textContent = path.points[0].label;
    document.getElementById("path-high").textContent = path.points[path.points.length - 1].label;
    document.getElementById("case-description").textContent = selector.value === "seed" ? "Parameters stay fixed; the economy draw changes." : "Other parameters and the economy draw stay fixed.";
    document.getElementById("sigma-value").textContent = item.sigma_label;
    document.getElementById("N-value").textContent = item.N_label;
    document.getElementById("M-value").textContent = item.M_label;
    document.getElementById("zeta-value").textContent = item.zeta_label;
    document.getElementById("seed-value").textContent = item.seed_label ?? item.seed;
    document.getElementById("phi-value").textContent = item.phi_label;
    document.getElementById("step-title").textContent = view.title;
    document.getElementById("step-explanation").textContent = view.explanation;
    document.getElementById("step-mobile").srcset = view.mobile_image;
    const image = document.getElementById("step-image");
    image.src = view.image;
    image.alt = view.alt;
    document.getElementById("step-caption").textContent = view.caption;
    document.getElementById("step-figure").hidden = false;
    document.getElementById("reallocation-value").textContent = item.moments.reallocation_label;
    document.getElementById("markup-value").textContent = item.moments.markup_label;
    document.getElementById("sga-value").textContent = item.moments.sga_label;
    document.getElementById("solution-status").textContent = item.status_label;
    status.textContent = data.display_note || "";
    stepButtons.forEach(button => { button.setAttribute("aria-pressed", button.dataset.step === step ? "true" : "false"); });
    window.Task11MomentSteps?.selectCase(item.id);
    document.getElementById("moment-calculation").hidden = step !== "4";
    document.getElementById("open-moment-steps").setAttribute("aria-expanded", String(step === "4"));
  }
  selector.addEventListener("change", () => {
    point.value = data.paths[selector.value].default_point ?? (selector.value === "seed" ? 0 : 2);
    update();
  });
  point.addEventListener("input", update);
  stepButtons.forEach(button => { button.addEventListener("click", () => { step = button.dataset.step; update(); }); });
  document.getElementById("open-moment-steps").addEventListener("click", () => {
    step = "4";
    update();
    const heading = document.getElementById("moment-calculation-title");
    heading.focus({ preventScroll: true });
    heading.scrollIntoView({ behavior: "instant", block: "start" });
  });
  document.addEventListener("lessonreveal", event => {
    if (event.detail.target?.closest("#moment-calculation")) { step = "4"; update(); }
  });
  document.getElementById("reset").addEventListener("click", () => {
    selector.value = data.default_path || "sigma";
    point.value = data.default_point ?? 2;
    step = "0";
    update();
  });
  update();
})();
