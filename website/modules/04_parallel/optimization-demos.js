"use strict";
// Replay stored illustrations only. No scheduler, model solver, benchmark or
// speed-up calculation runs in the browser. Coordinates are display geometry.
(() => {
  const root = document.getElementById("process-demos");
  if (!root) return;
  const tabs = [...root.querySelectorAll("[data-process-topic]")];
  const panels = [...root.querySelectorAll("[data-process-panel]")];
  const tablist = root.querySelector(".process-tabs");
  const continuous = root.dataset.processLayout === "continuous" || !tablist;
  const topicNames = panels.map(panel => panel.dataset.processPanel);
  let stopReplay = () => {};
  if (!continuous) {
    tablist.setAttribute("role", "tablist");
    tabs.forEach(tab => {
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", `process-${tab.dataset.processTopic}`);
    });
    panels.forEach(panel => panel.setAttribute("role", "tabpanel"));
  }

  const selectTopic = (topic, focus = false) => {
    if (!topicNames.includes(topic)) return;
    stopReplay();
    tabs.forEach(tab => {
      const active = tab.dataset.processTopic === topic;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    panels.forEach(panel => {
      const active = panel.dataset.processPanel === topic;
      panel.hidden = continuous ? false : !active;
      if (!continuous && !active) panel.querySelectorAll("video").forEach(video => video.pause());
    });
    root.dataset.activeProcess = topic;
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", event => {
      event.preventDefault();
      selectTopic(tab.dataset.processTopic);
      history.replaceState(null, "", tab.getAttribute("href"));
    });
    tab.addEventListener("keydown", event => {
      let next = null;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next === null) return;
      event.preventDefault();
      selectTopic(tabs[next].dataset.processTopic, true);
      history.replaceState(null, "", tabs[next].getAttribute("href"));
    });
  });
  const revealTarget = target => {
    if (!target) return false;
    if (window.CTLessonSections) return window.CTLessonSections.reveal(target);
    const panel = target?.closest("[data-process-panel]");
    const ancestors = [];
    for (let node = target; node; node = node.parentElement) {
      if (node.matches("details")) ancestors.push(node);
    }
    if (!panel && !ancestors.length) return false;
    if (panel) selectTopic(panel.dataset.processPanel);
    ancestors.reverse().forEach(details => { details.open = true; });
    // A direct reference into the optional architecture map must also select
    // that layer before scrolling. Its existing button handler owns the view.
    const layer = target.closest("[data-opt-panel]");
    if (layer?.hidden) {
      const button = document.querySelector(`#optimization [data-opt="${layer.dataset.optPanel}"]`);
      button?.click();
    }
    target.scrollIntoView({ block: "start", behavior: "instant" });
    return true;
  };
  const revealHash = () => revealTarget(document.getElementById(location.hash.slice(1)));
  // Native fragment navigation may try to scroll while the target's topic is
  // still hidden. Reveal same-page film links during the click itself rather
  // than relying on the later hashchange event (which also does not fire when
  // a reader clicks the same fragment again).
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target instanceof Element ? event.target.closest("a[href]") : null;
    if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
    const href = link.getAttribute("href");
    if (!href.startsWith("#")) return;
    const target = document.getElementById(href.slice(1));
    if (!target || (!target.closest("[data-process-panel]") && !target.closest("details"))) return;
    event.preventDefault();
    if (location.hash !== href) history.pushState(null, "", href);
    revealTarget(target);
  });
  const initialTopic = window.CTLessonSections?.current();
  selectTopic(topicNames.includes(initialTopic) ? initialTopic : "parallel_workers");
  document.addEventListener("lessonsectionchange", event => {
    if (topicNames.includes(event.detail?.view)) selectTopic(event.detail.view);
  });
  revealHash();
  window.addEventListener("hashchange", revealHash);
  window.addEventListener("popstate", revealHash);
  // Later deferred media enhancements can change the height above a fragment.
  window.addEventListener("load", revealHash, { once: true });

  const data = window.OPTIMIZATION_DEMO_DATA?.parallel;
  const status = document.getElementById("demo-status");
  if (!data?.schedules || !Array.isArray(data.jobs)) {
    status.textContent = "The saved illustration could not load. The films and transcripts remain available.";
    return;
  }
  const workers = document.getElementById("demo-workers");
  const serial = document.getElementById("demo-serial");
  const slider = document.getElementById("demo-clock");
  const play = document.getElementById("demo-play");
  const reset = document.getElementById("demo-reset");
  const scheduleView = document.getElementById("demo-schedule");
  const taskStates = document.getElementById("demo-task-states");
  const output = id => document.getElementById(id);
  let current = null;
  let baseline = null;
  let frameIndex = 0;
  let raf = null;
  let lastAdvance = 0;
  let playing = false;
  let rows = [];
  const taskViews = new Map();

  const stop = () => {
    playing = false;
    if (raf !== null) cancelAnimationFrame(raf);
    raf = null;
    play.setAttribute("aria-pressed", "false");
    play.textContent = "Play illustration";
  };
  stopReplay = stop;

  data.jobs.forEach(job => {
    const item = document.createElement("div");
    item.className = "demo-task";
    item.dataset.task = job.id;
    const name = document.createElement("strong");
    name.textContent = job.id;
    const length = document.createElement("small");
    length.textContent = `${job.duration} ${job.duration === 1 ? "unit" : "units"} of work`;
    const state = document.createElement("span");
    item.append(name, length, state);
    taskStates.append(item);
    taskViews.set(job.id, { item, state });
  });

  const addLane = (name, events, isBaseline = false) => {
    const lane = document.createElement("div");
    lane.className = "demo-lane";
    lane.dataset.baseline = String(isBaseline);
    const label = document.createElement("span");
    label.className = "demo-lane-name";
    label.textContent = name;
    const track = document.createElement("div");
    track.className = "demo-lane-track";
    const bars = events.map(event => {
      const bar = document.createElement("span");
      const isTask = event.kind === "task";
      bar.className = "demo-job";
      bar.dataset.task = event.id;
      bar.dataset.kind = isTask ? "task" : "serial";
      bar.dataset.short = String(event.end - event.start < 2);
      bar.style.left = `${event.start / data.axis_max * 100}%`;
      bar.style.width = `${(event.end - event.start) / data.axis_max * 100}%`;
      const title = isTask ? `Task ${event.id}` : (event.label || event.id);
      bar.title = `${title}: ${event.start}–${event.end} illustrative units`;
      bar.setAttribute("role", "img");
      bar.setAttribute("aria-label", bar.title);
      const text = document.createElement("span");
      text.className = "demo-job-label";
      text.textContent = event.id;
      text.setAttribute("aria-hidden", "true");
      bar.append(text);
      track.append(bar);
      return { bar, event, isTask };
    });
    const cursor = document.createElement("span");
    cursor.className = "demo-cursor";
    cursor.setAttribute("aria-hidden", "true");
    track.append(cursor);
    lane.append(label, track);
    scheduleView.append(lane);
    rows.push({ bars, cursor, isBaseline });
  };

  const paint = () => {
    const frame = current.frames[frameIndex];
    const baselineFrame = baseline.frames[frameIndex];
    slider.value = String(frameIndex);
    slider.setAttribute("aria-valuetext", `${frame.time_label}, illustrative work`);
    output("demo-time").textContent = frame.time_label;
    output("demo-done").textContent = String(frame.completed);
    output("demo-queue").textContent = String(frame.queued);
    rows.forEach(row => {
      const view = row.isBaseline ? baselineFrame : frame;
      row.cursor.style.left = `${frame.time / data.axis_max * 100}%`;
      row.bars.forEach(({ bar, event, isTask }) => {
        // Non-task setup/join bars are display segments, not economic work.
        bar.dataset.state = isTask ? view.status[event.id]
          : (view.time < event.start ? "queued" : view.time < event.end ? "running" : "done");
      });
    });
    taskViews.forEach(({ item, state }, id) => {
      item.dataset.state = frame.status[id];
      state.textContent = frame.status[id];
    });
    const phase = frame.time >= current.makespan ? "The selected schedule is complete."
      : `${frame.running} running; ${frame.queued} waiting.`;
    status.textContent = `${phase} Both timelines use the same clock.`;
  };

  const chooseSchedule = () => {
    stop();
    const selected = data.schedules[workers.value];
    const serialBaseline = data.schedules["1"];
    current = serial.checked ? selected.with_serial : selected;
    baseline = serial.checked ? serialBaseline.with_serial : serialBaseline;
    frameIndex = 0;
    slider.max = String(current.frames.length - 1);
    scheduleView.replaceChildren();
    rows = [];
    addLane("1 worker", baseline.events, true);
    if (serial.checked) addLane("Serial steps", current.events.filter(event => event.kind !== "task"));
    for (let lane = 0; lane < Number(workers.value); lane += 1) {
      addLane(`Worker ${lane + 1}`, current.events.filter(event => event.kind === "task" && event.worker === lane));
    }
    output("demo-makespan").textContent = current.makespan_label;
    output("demo-speedup").textContent = current.speedup_label;
    output("demo-baseline").textContent = baseline.makespan_label;
    paint();
  };

  const tick = timestamp => {
    if (!playing) return;
    if (timestamp - lastAdvance >= 85) {
      frameIndex = Math.min(frameIndex + 1, current.frames.length - 1);
      lastAdvance = timestamp;
      paint();
    }
    if (frameIndex >= current.frames.length - 1) { stop(); return; }
    raf = requestAnimationFrame(tick);
  };
  workers.addEventListener("change", chooseSchedule);
  serial.addEventListener("change", chooseSchedule);
  slider.addEventListener("input", () => {
    stop();
    frameIndex = Number(slider.value);
    paint();
  });
  play.addEventListener("click", () => {
    if (playing) { stop(); return; }
    document.querySelectorAll("details[data-micro-lesson] video").forEach(video => video.pause());
    if (frameIndex >= current.frames.length - 1) frameIndex = 0;
    playing = true;
    play.textContent = "Pause illustration";
    play.setAttribute("aria-pressed", "true");
    lastAdvance = performance.now();
    paint();
    raf = requestAnimationFrame(tick);
  });
  reset.addEventListener("click", () => { stop(); frameIndex = 0; paint(); });
  document.querySelectorAll("details[data-micro-lesson] video").forEach(video => video.addEventListener("play", stop));
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
  document.addEventListener("lessonsectionchange", stop);
  [workers, serial, slider, play, reset].forEach(control => { control.disabled = false; });
  root.dataset.scheduleReady = "true";
  chooseSchedule();
})();
