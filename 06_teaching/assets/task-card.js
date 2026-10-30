"use strict";
// On wide screens, keep the unit's task and its "Try it yourself" command in
// the empty right margin. The card copies what the page already says, and it
// appears only when the original task has scrolled out of view.
(() => {
  const brief = () => {
    // Unit 04: the task of the lesson on screen. Other units: the unit's task.
    const lesson = [...document.querySelectorAll("dl.lesson-task")].find(dl => dl.getClientRects().length);
    return lesson || document.querySelector("dl.task-brief, .task-brief dl");
  };
  const command = document.querySelector("pre.try-it-command:not(.try-it-output) code");
  const tryIt = command?.closest("section");
  const tryItTarget = tryIt?.id ? tryIt : tryIt?.querySelector("h2[id], h3[id]");
  if (!brief() && !command) return;

  const card = document.createElement("aside");
  card.className = "task-card";
  card.setAttribute("aria-label", "Your task, repeated");
  const tasks = document.createElement("div");
  card.append(tasks);
  if (command) {
    const block = document.createElement("div");
    block.className = "task-card-try";
    const label = document.createElement("p");
    label.className = "task-card-title";
    label.textContent = "Try it yourself";
    const code = document.createElement("code");
    code.textContent = command.textContent;
    block.append(label, code);
    if (tryItTarget) {
      const link = document.createElement("a");
      link.href = `#${tryItTarget.id}`;
      link.textContent = "What to expect ↓";
      block.append(link);
    }
    card.append(block);
  }
  document.body.append(card);

  let watched = null;
  const observer = new IntersectionObserver(entries => {
    const onScreen = entries.some(entry => entry.isIntersecting);
    card.classList.toggle("is-shown", !onScreen && Boolean(tasks.childElementCount || command));
  });
  function update() {
    const source = brief();
    tasks.replaceChildren();
    if (source) {
      const title = document.createElement("p");
      title.className = "task-card-title";
      title.textContent = source.matches(".lesson-task") ? "This lesson" : "Your task";
      const copy = source.cloneNode(true);
      copy.removeAttribute("id");
      copy.querySelectorAll("[id]").forEach(node => node.removeAttribute("id"));
      copy.className = "task-card-list";
      tasks.append(title, copy);
    }
    if (watched) observer.unobserve(watched);
    watched = source || tryIt;
    if (watched) observer.observe(watched);
  }
  update();
  // Units 02 and 04 show one lesson at a time; follow the lesson on screen.
  document.addEventListener("lessonreveal", () => requestAnimationFrame(update));
})();
