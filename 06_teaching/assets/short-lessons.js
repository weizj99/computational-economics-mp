"use strict";
// Units 02 and 04: one short lesson at a time over a single document, with a
// contents page, a side rail and previous/next links. Each page lists its
// lessons in <script type="application/json" id="short-lessons">. Without
// JavaScript every section remains readable in order.
(() => {
  const body = document.body;
  const settings = document.getElementById("short-lessons");
  const directory = document.querySelector('[data-lesson-part="contents"]');
  const heading = document.getElementById("short-lesson-heading");
  if (!body.hasAttribute("data-short-lessons") || !settings || !directory || !heading) return;

  // lessons and references: [{ key, hash, title, optional }]. aliases send a
  // fragment to a lesson; chapterStarts are fragments that open their lesson at
  // the top; referenceLink is where the last lesson leads, if not the first
  // reference; guide is a reference list inside the contents.
  const config = JSON.parse(settings.textContent);
  const { unit, lessons } = config;
  const references = config.references || [];
  const aliases = config.aliases || {};
  const chapterStarts = config.chapterStarts || [];
  const guide = config.guide ? document.getElementById(config.guide) : null;
  const allViews = [...lessons, ...references];
  const parts = [...document.querySelectorAll("[data-lesson-part]")];
  const containers = [...document.querySelectorAll("[data-lesson-container]")];
  const title = document.getElementById("short-lesson-title");
  const position = document.getElementById("short-lesson-position");
  const pager = document.getElementById("lesson-pagination");
  const previous = document.getElementById("lesson-previous");
  const next = document.getElementById("lesson-next");
  const status = document.getElementById("lesson-navigation-status");
  const rail = document.querySelector(".learning-rail > .wrap");
  const unitTitle = document.title;
  const lessonCount = String(lessons.length).padStart(2, "0");
  let current = null;

  const targetFromHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch (_) { return null; }
    return id ? document.getElementById(id) : directory;
  };
  const viewFor = target => {
    if (!target) return "contents";
    if (target.id === "read-all") return "all";
    if (aliases[target.id]) return aliases[target.id];
    const part = target.closest("[data-lesson-part]");
    return part ? part.dataset.lessonPart.split(/\s+/)[0] : "contents";
  };
  const fillLink = (link, item, label) => {
    link.href = `#${item.hash}`;
    link.querySelector("span").textContent = label;
    link.querySelector("strong").textContent = item.title;
  };
  const contentsLink = { hash: directory.id, title: "Unit contents" };
  const referenceLink = config.referenceLink || references[0] || contentsLink;

  function keepCurrentLessonVisible() {
    if (!rail || getComputedStyle(rail).flexDirection !== "row" || rail.scrollWidth <= rail.clientWidth) return;
    const active = rail.querySelector('[aria-current="location"]');
    if (!active) return;
    const linkRect = active.getBoundingClientRect();
    const left = rail.getBoundingClientRect().left + rail.clientLeft;
    const right = left + rail.clientWidth;
    // Move only the horizontal rail, leaving the lesson's page position alone.
    if (linkRect.left < left) rail.scrollLeft -= left - linkRect.left;
    else if (linkRect.right > right) rail.scrollLeft += linkRect.right - right;
  }

  function show(view, target, announce) {
    const changed = view !== current;
    if (changed) {
      document.querySelectorAll("video").forEach(video => video.pause());
      document.dispatchEvent(new CustomEvent("lessonsectionchange", { detail: { previous: current, view, target } }));
    }
    current = view;
    body.dataset.lessonView = view;
    parts.forEach(part => {
      const visible = view === "all" || part.dataset.lessonPart.split(/\s+/).includes(view);
      part.toggleAttribute("data-lesson-visible", visible);
      part.inert = !visible;
    });
    containers.forEach(container => {
      const visible = Boolean(container.querySelector("[data-lesson-part][data-lesson-visible]"));
      container.toggleAttribute("data-lesson-visible", visible);
      container.inert = !visible;
    });
    heading.hidden = view === "contents" || view === "all";
    pager.hidden = heading.hidden;
    const lessonIndex = lessons.findIndex(item => item.key === view);
    const referenceIndex = references.findIndex(item => item.key === view);
    const item = allViews.find(candidate => candidate.key === view);
    if (item) {
      title.textContent = item.title;
      position.textContent = lessonIndex >= 0
        ? `${unit} · ${String(lessonIndex + 1).padStart(2, "0")} / ${lessonCount}${item.optional ? " · Optional" : ""}`
        : `${unit} · Reference`;
      document.title = `${item.title} · Unit ${unit} · Computational Economics`;
      if (lessonIndex >= 0) {
        fillLink(previous, lessons[lessonIndex - 1] || contentsLink, "Previous");
        fillLink(next, lessons[lessonIndex + 1] || referenceLink, "Next");
      } else {
        // Without a separate reference link, the first reference follows the last lesson.
        const afterLessons = referenceIndex === 0 && !config.referenceLink;
        const isLast = referenceIndex === references.length - 1;
        fillLink(previous, references[referenceIndex - 1] || (afterLessons ? lessons[lessons.length - 1] : referenceLink),
          afterLessons ? "Previous" : "Previous reference");
        fillLink(next, references[referenceIndex + 1] || contentsLink, isLast ? "Return to" : "Next reference");
      }
    } else document.title = unitTitle;
    const railKey = referenceIndex >= 0 || (guide && target && guide.contains(target)) ? "references" : view;
    document.querySelectorAll("[data-lesson-link]").forEach(link => {
      if (link.dataset.lessonLink === railKey) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    keepCurrentLessonVisible();
    if (announce && changed) status.textContent = item
      ? `${position.textContent}. ${item.title}.` : view === "all" ? "Complete unit displayed." : "Unit contents displayed.";
    // Every reveal, also within the current lesson, so a page can open the
    // part of a lesson that a link points to.
    document.dispatchEvent(new CustomEvent("lessonreveal", { detail: { view, target, changed } }));
  }

  function reveal(target, { scroll = true, focus = false, announce = false } = {}) {
    if (!target) target = directory;
    const view = viewFor(target);
    show(view, target, announce);
    // Open the disclosures around the target, and the panel that holds it.
    const disclosures = [];
    for (let node = target; node; node = node.parentElement) {
      if (node.matches("details")) disclosures.push(node);
    }
    disclosures.reverse().forEach(details => { details.open = true; });
    const layer = target.closest("[data-opt-panel]");
    if (layer?.hidden) document.querySelector(`#optimization [data-opt="${layer.dataset.optPanel}"]`)?.click();

    const canonical = allViews.find(item => item.key === view)?.hash;
    const chapterStart = target.id === canonical || chapterStarts.includes(target.id);
    const scrollTarget = view === "all" ? directory
      : chapterStart || target.getClientRects().length === 0 ? heading : target;
    if (focus) {
      const focusTarget = guide && guide.contains(target) ? guide.querySelector("h2")
        : view === "contents" || view === "all" ? directory.querySelector("h1")
        : target.matches("details") ? target.querySelector("summary")
        : target.closest("details[data-micro-lesson]")?.querySelector("summary") || title;
      focusTarget?.focus({ preventScroll: true });
    }
    if (scroll) scrollTarget.scrollIntoView({ block: "start", behavior: "instant" });
    return true;
  }

  // The capture phase reveals a destination before any older fragment handler
  // tries to scroll it. Modified clicks, downloads and external pages stay native.
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target instanceof Element ? event.target.closest("a[href]") : null;
    if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
    let id;
    try { id = decodeURIComponent(url.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    if (location.hash !== url.hash) history.pushState(null, "", url.hash);
    reveal(target, { focus: true, announce: true });
  }, true);
  const followLocation = () => reveal(targetFromHash(), { focus: true, announce: true });
  window.addEventListener("hashchange", followLocation);
  window.addEventListener("popstate", followLocation);
  window.addEventListener("resize", keepCurrentLessonVisible);
  window.addEventListener("load", () => reveal(targetFromHash()), { once: true });
  window.CTLessonSections = { reveal, current: () => current };
  body.classList.add("short-lessons");
  reveal(targetFromHash(), { scroll: false });
})();
