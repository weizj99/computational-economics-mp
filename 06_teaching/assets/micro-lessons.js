"use strict";
// Optional media controls only. No lesson data or model output is changed here.
(() => {
  const lessons = [...document.querySelectorAll("details[data-micro-lesson]")];
  const videos = lessons.map(lesson => lesson.querySelector("video")).filter(Boolean);
  // One playback speed for every film on the page, remembered in this browser.
  const SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];
  const SPEED_KEY = "computational-economics-film-speed";
  let speed = 1;
  try {
    const saved = Number(localStorage.getItem(SPEED_KEY));
    if (SPEEDS.includes(saved)) speed = saved;
  } catch (_) { /* no storage: every film starts at normal speed */ }
  const speedMenus = [];
  const useSpeed = value => {
    speed = value;
    videos.forEach(video => { video.defaultPlaybackRate = value; video.playbackRate = value; });
    speedMenus.forEach(menu => { menu.value = String(value); });
    try { localStorage.setItem(SPEED_KEY, String(value)); } catch (_) { /* the choice holds on this page */ }
  };
  const speedControl = video => {
    const control = document.createElement("label");
    control.className = "micro-speed";
    const name = document.createElement("span");
    name.textContent = "Speed";
    const menu = document.createElement("select");
    menu.className = "micro-speed-select";
    SPEEDS.forEach(value => {
      const option = document.createElement("option");
      option.value = String(value);
      option.textContent = `${value}×`;
      menu.append(option);
    });
    menu.value = String(speed);
    menu.addEventListener("change", () => useSpeed(Number(menu.value)));
    video.addEventListener("ratechange", () => {
      if (SPEEDS.includes(video.playbackRate)) menu.value = String(video.playbackRate);
    });
    speedMenus.push(menu);
    control.append(name, menu);
    return control;
  };
  lessons.forEach(lesson => {
    const video = lesson.querySelector("video");
    if (!video) return;
    video.defaultPlaybackRate = speed;
    video.playbackRate = speed;
    const trackElement = video.querySelector('track[kind="captions"][srclang="en"]');
    if (trackElement && video.textTracks) {
      const track = trackElement.track;
      let enabled = true;
      let nativeFullscreen = false;
      let expectedMode = null;
      let reservedCues = null;
      let reservedCueCount = -1;
      const panel = document.createElement("div");
      panel.className = "micro-caption-panel";
      const toolbar = document.createElement("div");
      toolbar.className = "micro-caption-toolbar";
      const label = document.createElement("span");
      label.className = "micro-caption-label";
      label.textContent = "English captions";
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "micro-caption-toggle";
      toggle.setAttribute("aria-label", "English captions");
      const region = document.createElement("div");
      region.id = `${lesson.id}-captions`;
      region.className = "micro-caption-region";
      region.setAttribute("role", "region");
      region.setAttribute("aria-label", "English captions");
      region.setAttribute("aria-live", "off");
      toggle.setAttribute("aria-controls", region.id);
      const text = document.createElement("p");
      text.className = "micro-caption-text";
      const reserve = document.createElement("div");
      reserve.className = "micro-caption-reserve";
      reserve.setAttribute("aria-hidden", "true");
      region.append(reserve, text);
      toolbar.append(speedControl(video), label, toggle);
      panel.append(toolbar, region);
      video.after(panel);

      const inFullscreen = () => nativeFullscreen || document.fullscreenElement === video ||
        document.webkitFullscreenElement === video || Boolean(video.webkitDisplayingFullscreen);
      const paint = () => {
        // Hidden, overlapping cue copies reserve the tallest caption at the
        // current width, including when captions are off or between cues.
        if (track.cues && (reservedCues !== track.cues || reservedCueCount !== track.cues.length)) {
          reservedCues = track.cues;
          reservedCueCount = track.cues.length;
          reserve.replaceChildren(...Array.from(track.cues, cue => {
            const line = document.createElement("span");
            line.textContent = cue.text;
            return line;
          }));
        }
        const fullscreen = inFullscreen();
        panel.dataset.captionMode = fullscreen ? "native" : "inline";
        toggle.setAttribute("aria-pressed", String(enabled));
        toggle.textContent = enabled ? "Captions on" : "Captions off";
        const content = enabled && !fullscreen
          ? Array.from(track.activeCues || [], cue => cue.text).join("\n") : "";
        if (text.textContent !== content) text.textContent = content;
      };
      const apply = () => {
        // hidden keeps cues available to the external caption band without
        // drawing a second subtitle layer over the lesson diagram.
        expectedMode = inFullscreen() ? (enabled ? "showing" : "disabled") : "hidden";
        if (track.mode !== expectedMode) track.mode = expectedMode;
        paint();
      };
      toggle.addEventListener("click", () => { enabled = !enabled; apply(); });
      track.addEventListener("cuechange", paint);
      trackElement.addEventListener("load", paint);
      video.addEventListener("timeupdate", paint);
      video.addEventListener("loadedmetadata", apply);
      video.textTracks.addEventListener("change", () => {
        if (track.mode !== expectedMode) {
          // Honor native CC choices too. Inline "showing" becomes external
          // captions; native "disabled" turns them off. Our own mode changes
          // already equal expectedMode and cannot overwrite the preference.
          if (track.mode === "showing") enabled = true;
          else if (track.mode === "disabled") enabled = false;
          apply();
        } else paint();
      });
      document.addEventListener("fullscreenchange", apply);
      document.addEventListener("webkitfullscreenchange", apply);
      video.addEventListener("webkitbeginfullscreen", () => { nativeFullscreen = true; apply(); });
      video.addEventListener("webkitendfullscreen", () => { nativeFullscreen = false; apply(); });
      apply();
    }
    lesson.addEventListener("toggle", () => {
      if (!lesson.open) video.pause();
    });
    video.addEventListener("play", () => {
      videos.forEach(other => { if (other !== video) other.pause(); });
    });
    video.addEventListener("error", () => {
      const status = lesson.querySelector(".micro-lesson-status");
      if (status) status.textContent = "Playback is unavailable in this browser. Read the transcript or download the captioned video below.";
    });
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) videos.forEach(video => video.pause());
  });
  // Method-page links can point directly to an explanation. Opening a targeted
  // card reveals its poster and controls; it never starts playback.
  const revealTarget = () => {
    const target = document.getElementById(location.hash.slice(1));
    if (target?.matches("details[data-micro-lesson]")) target.open = true;
  };
  window.addEventListener("hashchange", revealTarget);
  revealTarget();
})();
