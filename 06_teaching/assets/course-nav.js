"use strict";
// Navigation only. This script never reads or calculates model outputs.
(() => {
  const script = document.currentScript;
  if (!script) return;
  const root = new URL("../", script.src);
  const home = { id: "home", title: "Course home", path: "index.html" };
  const glossary = { id: "glossary", title: "Symbols and terms", path: "glossary.html" };
  // Same address as docs/project_links.json; tools/site/source_links.py --check compares them.
  const repository = "https://github.com/weizj99/computational-economics-mp";
  const lessons = [
    { id: "00", title: "Prerequisite", path: "prerequisites/index.html" },
    { id: "01", title: "Moment Matching", path: "modules/01_gmm_smm/index.html" },
    { id: "02", title: "One Economy", path: "modules/02_one_economy/index.html" },
    { id: "03", title: "Estimation", path: "modules/03_estimation/index.html" },
    { id: "04", title: "Parallel Computing and Acceleration", path: "modules/04_parallel/index.html" },
    { id: "05", title: "Untargeted Moment", path: "modules/05_untargeted/index.html" }
  ];
  const prerequisites = [
    { id: "ab08", title: "AB08 · Demand & markups", path: "prerequisites/ab08.html" },
    { id: "berry92", title: "Berry92 · Entry", path: "prerequisites/berry92.html" }
  ];
  document.querySelectorAll("nav.course-nav").forEach((nav, index) => {
    const current = nav.dataset.courseCurrent || "00";
    const selected = [...lessons, ...prerequisites].find(item => item.id === current);
    const prerequisitePage = current === "ab08" || current === "berry92";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "course-nav-trigger";
    button.id = `course-nav-trigger-${index}`;
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", `course-nav-menu-${index}`);
    button.innerHTML = '<span class="course-nav-label">Course</span><span class="course-nav-current"></span><svg class="course-nav-caret" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5 11 1.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>';
    button.querySelector(".course-nav-current").textContent = current === home.id ? home.title
      : current === glossary.id ? glossary.title
      : selected ? (prerequisitePage ? "00 Prerequisite" : `${selected.id} ${selected.title}`)
      : "Course contents";
    const menu = document.createElement("div");
    menu.id = `course-nav-menu-${index}`;
    menu.className = "course-nav-menu";
    menu.hidden = true;
    menu.setAttribute("aria-labelledby", button.id);
    const heading = document.createElement("span");
    heading.className = "course-nav-heading";
    heading.textContent = "Choose a lesson";
    menu.appendChild(heading);
    function link(item, numbered) {
      const anchor = document.createElement("a");
      anchor.href = new URL(item.path, root).href;
      anchor.dataset.courseLink = item.id;
      if (numbered) {
        const number = document.createElement("span");
        number.className = "course-nav-number";
        number.textContent = item.id;
        const title = document.createElement("span");
        title.textContent = item.title;
        anchor.append(number, title);
      } else anchor.textContent = item.title;
      if (item.id === current) anchor.setAttribute("aria-current", "page");
      if (item.id === "00" && prerequisitePage) anchor.classList.add("is-section-current");
      return anchor;
    }
    const homeLink = link(home, false);
    homeLink.classList.add("course-nav-home");
    menu.appendChild(homeLink);
    lessons.forEach(item => {
      menu.appendChild(link(item, true));
      if (item.id === "00") {
        const sublinks = document.createElement("div");
        sublinks.className = "course-nav-prerequisites";
        prerequisites.forEach(prerequisite => sublinks.appendChild(link(prerequisite, false)));
        menu.appendChild(sublinks);
      }
    });
    const glossaryLink = link(glossary, false);
    glossaryLink.classList.add("course-nav-glossary");
    menu.appendChild(glossaryLink);
    nav.replaceChildren(button, menu);
    // The repository link sits beside the nav, not in it, so pointing at it
    // does not open the menu. The wrapper keeps both at the masthead's end.
    const code = document.createElement("a");
    code.className = "course-repo-link";
    code.href = repository;
    code.innerHTML = '<span class="course-repo-extra">Code on</span><span>GitHub ↗</span>';
    const end = document.createElement("div");
    end.className = "masthead-end";
    nav.replaceWith(end);
    end.append(nav, code);
    let leaveTimer;
    let hoverOpened = false;
    const setOpen = value => {
      window.clearTimeout(leaveTimer);
      menu.hidden = !value;
      button.setAttribute("aria-expanded", value ? "true" : "false");
      if (!value) hoverOpened = false;
    };
    button.addEventListener("click", () => {
      const keepHoveredMenu = hoverOpened && !menu.hidden;
      hoverOpened = false;
      setOpen(keepHoveredMenu || menu.hidden);
    });
    nav.addEventListener("pointerenter", event => {
      if (event.pointerType === "mouse") {
        if (menu.hidden) hoverOpened = true;
        setOpen(true);
      }
    });
    nav.addEventListener("pointerleave", event => {
      if (event.pointerType === "mouse" && !nav.contains(document.activeElement)) {
        leaveTimer = window.setTimeout(() => setOpen(false), 160);
      }
    });
    nav.addEventListener("focusout", () => {
      window.setTimeout(() => {
        if (!nav.contains(document.activeElement)) setOpen(false);
      }, 0);
    });
    nav.addEventListener("keydown", event => {
      if (event.key === "Escape") {
        setOpen(false);
        button.focus();
      } else if (event.key === "ArrowDown" && event.target === button) {
        event.preventDefault();
        setOpen(true);
        menu.querySelector("a").focus();
      }
    });
    document.addEventListener("pointerdown", event => {
      if (!nav.contains(event.target)) setOpen(false);
    });
  });
})();
