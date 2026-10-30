"use strict";
// Reading navigation follows the visible section. Native anchors keep working
// without JavaScript and all links remain in the normal keyboard tab order.
(() => {
  const nav = document.querySelector(".lesson-navigation");
  if (!nav || document.body.hasAttribute("data-short-lessons")) return;
  const entries = [...nav.querySelectorAll('a[href^="#"]')].map(link => ({
    link, section: document.getElementById(link.hash.slice(1))
  })).filter(entry => entry.section);
  if (!entries.length) return;
  let pending = false;
  const update = () => {
    pending = false;
    const anchorInset = Number.parseFloat(window.getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
    // A vertical reading rail's height is unrelated to the scroll offset.
    const marker = document.body.classList.contains('learning-edition')
      ? Math.max(32, anchorInset + 8)
      : Math.max(nav.getBoundingClientRect().height + 28, anchorInset + 4);
    let current = entries[0];
    entries.forEach(entry => {
      if (entry.section.getBoundingClientRect().top <= marker) current = entry;
    });
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
      current = entries[entries.length - 1];
    }
    entries.forEach(entry => {
      if (entry === current) entry.link.setAttribute("aria-current", "location");
      else entry.link.removeAttribute("aria-current");
    });
  };
  const schedule = () => {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(update);
  };
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("load", schedule);
  schedule();
})();
// These switches select conceptual layouts. They do not run the model,
// root solver, precision experiment or a performance simulation.
(() => {
  const root = document.getElementById("optimization");
  if (!root) return;
  const buttons = root.querySelectorAll("[data-opt]");
  const set = (id, value) => { document.getElementById(id).textContent = value; };
  const copy = {
    loop: {
      source: "Starting market loop",
      title: "Call the solver market by market.",
      change: "None: this is the reference layout before vectorization.",
      save: "The baseline: it shows the repeated small calls.",
      wait: "Each market call iterates over that market’s firms."
    },
    matrix: {
      source: "Vectorized CPU implementation",
      title: "Organize the markets.",
      change: "Replace repeated market calls with M × J array operations.",
      save: "Small-call overhead; repeated setup can also be precomputed.",
      wait: "Firm sums within each market, share iterations and exit rounds."
    },
    root: {
      source: "Current Python scalar solver",
      title: "Use the equation’s structure.",
      change: "Bracket the upper positive output root; solve in log Y.",
      save: "Use a specialized one-variable method instead of a general solver.",
      wait: "Market totals come first. Root position and labor clearing must both pass."
    },
    workers: {
      source: "Current CPU parallel implementation",
      title: "Distribute independent economies.",
      change: "Run separate M × J solves on different CPU cores.",
      save: "Elapsed time when the queue contains enough independent work.",
      wait: "Input preparation, work balance and the final comparison."
    },
    batch: {
      source: "GPU batch structure + current solver checks",
      title: "Batch first. Then fuse.",
      change: "Stack economies as B × M × J; fuse a share update.",
      save: "GPU launch overhead and intermediate array traffic.",
      wait: "Local reductions, convergence checks and successive exit rounds."
    },
    precision: {
      source: "Measured results",
      title: "Measure precision and card count.",
      change: "Predict shares in FP32, correct in FP64 and distribute candidate batches.",
      save: "See the measured times for the whole workload in ",
      wait: "Check numerical errors, branch decisions, correction cost and dispatch overhead."
    }
  };
  const select = key => {
    root.dataset.optimization = key;
    buttons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.opt === key)));
    root.querySelectorAll("[data-opt-panel]").forEach(panel => { panel.hidden = panel.dataset.optPanel !== key; });
    ["source", "title", "change", "save", "wait"].forEach(field => set(`opt-${field}`, copy[key][field]));
    if (key === "precision") {
      const link = document.createElement("a");
      link.href = "#current-benchmark";
      link.textContent = "GPU measurements";
      document.getElementById("opt-save").append(link, ".");
    }
  };
  buttons.forEach(button => button.addEventListener("click", () => select(button.dataset.opt)));
  buttons.forEach((button, index) => button.addEventListener("keydown", event => {
    const keys = ["ArrowLeft", "ArrowRight", "Home", "End"];
    if (!keys.includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1
      : (index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
    buttons[next].focus();
    select(buttons[next].dataset.opt);
  }));
  document.getElementById("opt-next-market").addEventListener("click", () => {
    const index = (Number(root.dataset.loopMarket) + 1) % 4;
    root.dataset.loopMarket = String(index);
    set("opt-loop-status", `Call the share solver for market ${index + 1}.`);
  });
  const bracket = document.getElementById("opt-bracket-slider");
  const bracketLabels = ["Initial interval", "Narrower interval", "Closer to the root", "Final neighborhood"];
  bracket.addEventListener("input", () => {
    root.dataset.bracket = bracket.value;
    set("opt-bracket-label", bracketLabels[Number(bracket.value)]);
    bracket.setAttribute("aria-valuetext", `${bracketLabels[Number(bracket.value)]}; conceptual illustration`);
  });
  select("matrix");
})();
// Select measured outputs and recorded frames. No economy, timing analysis,
// speed-up calculation or statistics are evaluated here.
(() => {
  const data = window.SCALING_DATA;
  const byId = id => document.getElementById(id);
  if (!data || data.schema_version !== 1) {
    byId("run-note").textContent = "Saved measurements unavailable. The source and timing downloads remain available below.";
    ["workers-slider", "progress-slider", "play", "reset"].forEach(id => { byId(id).disabled = true; });
    return;
  }
  const counts = data.worker_counts;
  let workers = data.default_workers;
  let frameIndex = 100;
  let timer = null;
  const setText = (id, value) => { byId(id).textContent = value; };
  const trial = () => data.trials[String(workers)];

  function stopPlayback() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
    byId("play").setAttribute("aria-pressed", "false");
    byId("play").innerHTML = 'Play recording <span aria-hidden="true">▶</span>';
    setText("playback-status", frameIndex === 100 ? "Paused at the end" : "Paused");
  }

  function renderFrame() {
    const frame = trial().frames[frameIndex];
    setText("elapsed-value", frame.time_display);
    setText("completed-value", frame.completed);
    setText("busy-value", frame.busy);
    byId("progress-slider").value = String(frame.index);
    byId("progress-slider").setAttribute("aria-valuetext", `${frame.time_display}; ${frame.completed} economies finished; ${frame.busy} workers busy`);
    byId("timeline-cursor").style.left = String(frame.cursor_percent) + "%";
    byId("replay-fill").style.width = String(frame.cursor_percent) + "%";
    byId("timeline-stage").style.setProperty("--clip-right-desktop", String(frame.clip_right_percent_desktop) + "%");
    byId("timeline-stage").style.setProperty("--clip-right-mobile", String(frame.clip_right_percent_mobile) + "%");
    byId("parallel").dataset.frame = String(frame.index);
  }

  function renderTrial() {
    const selected = trial();
    const display = selected.display;
    byId("workers-slider").value = String(counts.indexOf(workers));
    byId("workers-slider").setAttribute("aria-valuetext", `${workers} workers`);
    setText("workers-value", workers);
    [["wall-time", "wall_time"], ["speedup", "speedup"], ["efficiency", "efficiency"], ["core-time", "core_time"]].forEach(([id, key]) => setText(id, display[key]));
    byId("timeline-mobile").srcset = selected.timeline.mobile.src;
    byId("timeline-mobile").setAttribute("width", selected.timeline.mobile.width);
    byId("timeline-mobile").setAttribute("height", selected.timeline.mobile.height);
    byId("timeline-background-mobile").srcset = selected.timeline.mobile.background;
    byId("timeline-background-mobile").setAttribute("width", selected.timeline.mobile.width);
    byId("timeline-background-mobile").setAttribute("height", selected.timeline.mobile.height);
    const background = byId("timeline-background-image");
    background.src = selected.timeline.desktop.background;
    background.width = selected.timeline.desktop.width;
    background.height = selected.timeline.desktop.height;
    const image = byId("timeline-image");
    image.src = selected.timeline.desktop.src;
    image.width = selected.timeline.desktop.width;
    image.height = selected.timeline.desktop.height;
    image.alt = `${workers} workers: recorded execution intervals for the same 256 candidate economies.`;
    setText("run-note", selected.note);
    byId("parallel").dataset.workers = String(workers);
    document.querySelectorAll("#timing-table tr").forEach(row => {
      const active = row.dataset.workers === String(workers);
      row.classList.toggle("is-active", active);
      row.querySelector("button").setAttribute("aria-pressed", active ? "true" : "false");
    });
    renderFrame();
  }

  function selectWorkers(value) {
    if (!counts.includes(value)) return;
    stopPlayback();
    workers = value;
    frameIndex = 100;
    renderTrial();
    stopPlayback();
  }

  function buildTable() {
    const fragment = document.createDocumentFragment();
    counts.forEach(count => {
      const item = data.trials[String(count)];
      const row = document.createElement("tr"); row.dataset.workers = String(count);
      const th = document.createElement("th"); th.scope = "row";
      const button = document.createElement("button"); button.type = "button"; button.dataset.workers = String(count);
      button.textContent = String(count); button.setAttribute("aria-label", `Show the measured run with ${count} workers`);
      th.appendChild(button); row.appendChild(th);
      [["Wall time", "wall_time"], ["Speed-up", "speedup"], ["Efficiency", "efficiency"], ["Worker core-time", "core_time"]].forEach(([label, key]) => {
        const td = document.createElement("td"); td.dataset.label = label; td.textContent = item.display[key]; row.appendChild(td);
      });
      fragment.appendChild(row);
    });
    byId("timing-table").replaceChildren(fragment);
  }

  byId("workers-slider").addEventListener("input", event => selectWorkers(counts[Number(event.target.value)]));
  byId("progress-slider").addEventListener("input", event => {
    const index = Number(event.target.value);
    if (!Number.isInteger(index) || index < 0 || index >= trial().frames.length) return;
    stopPlayback(); frameIndex = index; renderFrame(); stopPlayback();
  });
  byId("timing-table").addEventListener("click", event => {
    const button = event.target.closest("button[data-workers]");
    if (button) selectWorkers(Number(button.dataset.workers));
  });
  byId("play").addEventListener("click", () => {
    if (timer !== null) { stopPlayback(); return; }
    frameIndex = 0; renderFrame();
    byId("play").setAttribute("aria-pressed", "true");
    byId("play").innerHTML = 'Pause recording <span aria-hidden="true">Ⅱ</span>';
    setText("playback-status", "Playing · time compressed");
    timer = window.setInterval(() => {
      if (frameIndex >= trial().frames.length - 1) { stopPlayback(); return; }
      frameIndex += 1; renderFrame();
      if (frameIndex === trial().frames.length - 1) stopPlayback();
    }, 90);
  });
  byId("reset").addEventListener("click", () => selectWorkers(data.default_workers));
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopPlayback(); });
  document.addEventListener("lessonsectionchange", stopPlayback);
  byId("scaling-mobile").srcset = data.figures.scaling.mobile;
  byId("scaling-image").src = data.figures.scaling.desktop;
  setText("hardware-note", `${data.meta.cpu_model} · ${data.meta.physical_cores} physical cores allocated. ${data.meta.precision_note}`);
  setText("correctness-note", data.summary.correctness_note);
  setText("result-note", data.summary.headline);
  buildTable(); renderTrial(); stopPlayback();
})();

// Illustrate dependency structure only. No solver, clock or performance model runs here.
(() => {
  const root = document.getElementById("dependencies");
  if (!root) return;
  const choices = root.querySelectorAll("button[data-dependency]");
  const lanes = document.getElementById("dependency-lanes");
  const phase = document.getElementById("dependency-phase");
  const laneCounts = [1, 2, 4];
  const descriptions = {
    economies: {
      phases: ["Inputs fixed", "Solve together", "Moments returned", "Compare losses"],
      ticks: ["Inputs", "Solves", "Moments", "Compare"],
      capacity: "Four groups are shown. Each needs a free worker, not another row’s answer.",
      title: ["Inputs can be shared read-only.", "No cross-row dependency.", "Each solve returns its own moments.", "Comparison waits for the results."],
      reason: ["Fix parameters and stored draws before dispatch. Sharing a draw bank does not make one solve depend on another.", "Common draws can be shared read-only. No economy needs another economy’s solved result.", "A result can return as soon as its own economy is solved. Other candidates can still be running.", "The best-of-batch comparison uses completed candidate losses. No candidate solve needs that comparison."]
    },
    markets: {
      phases: ["Market states fixed", "Update firm weights", "Normalize each market", "Next share update"],
      ticks: ["States", "Weights", "Local sum", "Repeat"],
      capacity: "Four market groups are shown. Array operations can run on CPU or GPU; these are not four separate economies.",
      title: ["One state per market.", "Columns can update together.", "Firms inside a market interact.", "Each market needs its previous shares."],
      reason: ["The share block fixes common demand and technology parameters. Each column uses its own productivity, operating set and current shares.", "At this step, one market’s firm weights do not use another market’s weights. The array can be split across market blocks.", "Sum firm weights inside each column, then normalize. This local reduction does not require another market’s answer.", "Repeat from updated shares until the market settles. Converged markets freeze while others continue."]
    },
    rounds: {
      phases: ["Shares settle", "Aggregate solve", "Profit and exit", "Resolve with survivors"],
      ticks: ["Shares", "Totals", "Exit", "Resolve"],
      capacity: "More lanes cannot remove a dependency. Totals, profits and the next operating set still need earlier results.",
      title: ["Finish the market block first.", "The economy shares one aggregate condition.", "Exit uses solved profits.", "The next round has new inputs."],
      reason: ["Market share problems run in parallel. The price and aggregate calculations then use their settled solutions.", "Combine market quantities to solve output Y and wage W. Markets are linked through this economy-wide condition.", "Profit uses the current prices, output and wage. Only then can the exit rule decide which firms to remove.", "Applied exits change competition, so solve the remaining economy again. Period 2 also waits for period 1’s fixed-cost anchor."]
    }
  };
  let layer = "economies";
  const setText = (id, value) => { document.getElementById(id).textContent = value; };
  const styleStage = (element, active, done, waiting) => {
    element.classList.toggle("is-stage-active", active);
    element.classList.toggle("is-stage-done", done);
    element.classList.toggle("is-stage-waiting", waiting);
  };
  function render() {
    const current = Number(phase.value);
    const capacity = laneCounts[Number(lanes.value)];
    const copy = descriptions[layer];
    root.dataset.dependencyLayer = layer;
    root.dataset.laneCount = String(capacity);
    root.dataset.phase = String(current);
    choices.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.dependency === layer)));
    root.querySelectorAll("[data-dependency-panel]").forEach(panel => { panel.hidden = panel.dataset.dependencyPanel !== layer; });
    document.getElementById("dependency-capacity-control").hidden = layer === "rounds";
    setText("dependency-lanes-value", String(capacity));
    lanes.setAttribute("aria-valuetext", `${capacity} illustrative lanes; diagram only`);
    setText("dependency-capacity-note", copy.capacity);
    setText("dependency-phase-value", copy.phases[current]);
    phase.setAttribute("aria-valuetext", copy.phases[current]);
    root.querySelectorAll("#dependency-phase-ticks > span").forEach((tick, index) => { tick.textContent = copy.ticks[index]; });
    setText("dependency-reason-title", copy.title[current]);
    setText("dependency-reason", copy.reason[current]);
    root.querySelectorAll("[data-economy]").forEach((row, index) => {
      const working = current === 1 && index < capacity;
      styleStage(row.querySelector("[data-cell=input]"), current === 0, current > 0, false);
      styleStage(row.querySelector("[data-cell=work]"), working, current > 1, current === 1 && !working);
      styleStage(row.querySelector("[data-cell=output]"), current === 2, current === 3, current < 2);
    });
    document.getElementById("dependency-selection").classList.toggle("is-stage-active", current === 3);
    root.querySelectorAll("[data-market]").forEach((market, index) => {
      const working = current === 0 || index < capacity;
      styleStage(market, working, false, !working);
      market.classList.toggle("is-stage-reducing", working && current === 2);
      market.classList.toggle("is-stage-returning", working && current === 3);
    });
    root.querySelectorAll("[data-chain]").forEach((card, index) => { styleStage(card, current === index, current > index, current < index); });
  }
  choices.forEach(button => button.addEventListener("click", () => {
    layer = button.dataset.dependency;
    phase.value = layer === "rounds" ? "0" : "1";
    render();
  }));
  lanes.addEventListener("input", render);
  phase.addEventListener("input", render);
  render();
})();

// These values are exported after the complete CPU/CUDA checks pass.
// Switching cases only selects display strings; it performs no calculation.
(() => {
  const data = window.FULL_GPU_DATA;
  const selector = document.getElementById("full-gpu-case");
  if (!data || !selector) return;
  const cases = {};
  selector.replaceChildren();
  data.cases.forEach(item => {
    cases[item.id] = item;
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.label;
    selector.appendChild(option);
  });
  const update = () => {
    const item = cases[selector.value];
    document.getElementById("full-gpu-case-note").textContent = item.description;
    const body = document.getElementById("full-gpu-values");
    body.replaceChildren();
    item.rows.forEach(value => {
      const row = document.createElement("tr");
      const heading = document.createElement("th");
      heading.scope = "row";
      heading.textContent = value.label;
      row.appendChild(heading);
      ["cpu", "gpu"].forEach(backend => {
        const cell = document.createElement("td");
        cell.textContent = value[backend];
        cell.dataset.backend = backend;
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
    document.getElementById("full-gpu-case-status").textContent = item.status;
    document.getElementById("full-economy").dataset.caseId = item.id;
  };
  selector.value = data.default_case;
  selector.addEventListener("change", update);
  update();
})();
