"use strict";
// Optional lesson-page controls. Native video controls remain the fallback.
// The shared micro-lessons script still owns captions and mutual pausing.
(() => {
  if (!document.body.classList.contains("learning-edition")) return;

  const formatTime = value => {
    if (!Number.isFinite(value) || value < 0) return "—";
    const seconds = Math.floor(value);
    return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
  };
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const button = (action, icon, name) => {
    const element = make("button", `lesson-player-button lesson-player-${action}`);
    element.type = "button";
    element.dataset.playerAction = action;
    element.setAttribute("aria-label", name);
    element.title = name;
    const glyph = make("span", "lesson-player-icon", icon);
    glyph.setAttribute("aria-hidden", "true");
    element.append(glyph);
    return element;
  };

  document.querySelectorAll("details[data-micro-lesson]").forEach(lesson => {
    const video = lesson.querySelector("video");
    if (!video || lesson.dataset.playerEnhanced === "true") return;
    // The HTML controls attribute is the no-script guarantee. Keep it enabled
    // until every replacement control and its event handlers are installed.
    video.controls = true;
    if (video.error) return;
    let active = false;
    let strip = null;
    let captionToggle = null;
    let captionToolbar = null;
    let nativeFullscreen = false;
    let requestingFullscreen = false;
    let previousNonzeroVolume = video.volume > 0 ? video.volume : 1;
    const status = lesson.querySelector(".micro-lesson-status");

    const restoreNative = message => {
      const restoreFocus = strip?.contains(document.activeElement);
      active = false;
      requestingFullscreen = false;
      video.controls = true;
      lesson.dataset.playerEnhanced = "false";
      lesson.dataset.playerState = "native-fallback";
      lesson.removeAttribute("data-player-native-fullscreen");
      if (captionToggle && captionToolbar) captionToolbar.append(captionToggle);
      if (strip) strip.remove();
      if (status && message) status.textContent = message;
      if (restoreFocus) lesson.querySelector(":scope > summary")?.focus();
    };
    const safely = operation => (...args) => {
      if (!active) return;
      try {
        const result = operation(...args);
        if (result && typeof result.catch === "function") {
          return result.catch(() => {
            if (active) restoreNative("Native video controls are available. You can also read the transcript or download the captioned film below.");
          });
        }
        return result;
      }
      catch (_) {
        restoreNative("Native video controls are available. You can also read the transcript or download the captioned film below.");
      }
    };

    try {
      const captionPanel = lesson.querySelector(".micro-caption-panel");
      captionToolbar = captionPanel?.querySelector(".micro-caption-toolbar");
      captionToggle = captionToolbar?.querySelector(".micro-caption-toggle");
      // Do not replace the native UI if the shared caption enhancement failed.
      if (!captionPanel || !captionToolbar || !captionToggle) return;

      strip = make("div", "lesson-player-controls");
      strip.hidden = true;
      strip.dataset.playerFor = lesson.id;
      strip.setAttribute("role", "group");
      strip.setAttribute("aria-label", "Video playback controls");
      const play = button("play", "▶", "Play video");
      const seek = make("input", "lesson-player-seek");
      seek.type = "range";
      seek.min = "0";
      seek.max = "0";
      seek.step = "0.1";
      seek.value = "0";
      seek.disabled = true;
      seek.dataset.playerAction = "seek";
      seek.setAttribute("aria-label", "Seek video");
      const time = make("output", "lesson-player-time", "0:00 / —");
      time.setAttribute("aria-live", "off");
      time.setAttribute("aria-label", "Current time and duration");
      const fullscreen = button("fullscreen", "", "Full screen");
      const fullscreenSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      fullscreenSvg.setAttribute("viewBox", "0 0 24 24");
      fullscreenSvg.setAttribute("width", "20");
      fullscreenSvg.setAttribute("height", "20");
      fullscreenSvg.setAttribute("aria-hidden", "true");
      fullscreenSvg.setAttribute("focusable", "false");
      const fullscreenPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
      fullscreenPath.setAttribute("d", "M8 3H3v5 M16 3h5v5 M21 16v5h-5 M8 21H3v-5");
      fullscreenPath.setAttribute("fill", "none");
      fullscreenPath.setAttribute("stroke", "currentColor");
      fullscreenPath.setAttribute("stroke-width", "1.8");
      fullscreenSvg.append(fullscreenPath);
      fullscreen.querySelector(".lesson-player-icon").append(fullscreenSvg);
      const supportsFullscreen = typeof video.requestFullscreen === "function" ||
        typeof video.webkitEnterFullscreen === "function";
      fullscreen.disabled = !supportsFullscreen;
      if (!supportsFullscreen) fullscreen.title = "Full screen is not available in this browser";

      const options = make("details", "lesson-player-options");
      const optionsToggle = make("summary", "lesson-player-options-toggle", "···");
      // Playback speed sits below the film, with the shared speed menu of every unit.
      optionsToggle.setAttribute("aria-label", "Volume");
      optionsToggle.title = "Volume";
      const optionPanel = make("div", "lesson-player-option-panel");
      const volumeRow = make("div", "lesson-player-volume-row");
      const mute = button("mute", "Mute", "Mute audio");
      const volumeLabel = make("label", "lesson-player-volume-label");
      volumeLabel.append(make("span", "lesson-player-option-label", "Volume"));
      const volume = make("input", "lesson-player-volume");
      volume.type = "range";
      volume.min = "0";
      volume.max = "100";
      volume.step = "1";
      volume.value = String(Math.round(video.volume * 100));
      volume.dataset.playerAction = "volume";
      volumeLabel.append(volume);
      volumeRow.append(volumeLabel, mute);
      optionPanel.append(volumeRow);
      options.append(optionsToggle, optionPanel);

      const inNativeFullscreen = () => nativeFullscreen ||
        document.fullscreenElement === video || document.webkitFullscreenElement === video ||
        Boolean(video.webkitDisplayingFullscreen);
      const paintTime = () => {
        const duration = video.duration;
        const ready = Number.isFinite(duration) && duration > 0;
        const canSeek = Array.from({length: video.seekable.length}, (_, i) => i)
          .some(i => video.seekable.end(i) > video.seekable.start(i));
        seek.disabled = !ready || (video.readyState < 2 && !video.seeking) || !canSeek;
        seek.max = ready ? String(duration) : "0";
        seek.value = ready ? String(Math.min(duration, Math.max(0, video.currentTime))) : "0";
        time.textContent = `${formatTime(video.currentTime)} / ${formatTime(duration)}`;
        seek.setAttribute("aria-valuetext", `${formatTime(video.currentTime)} of ${formatTime(duration)}`);
      };
      const paintPlayback = () => {
        const paused = video.paused || video.ended;
        const name = video.ended ? "Replay video" : paused ? "Play video" : "Pause video";
        play.setAttribute("aria-label", name);
        play.title = name;
        play.setAttribute("aria-pressed", String(!paused));
        play.querySelector(".lesson-player-icon").textContent = video.ended ? "↻" : paused ? "▶" : "Ⅱ";
        lesson.dataset.playerState = video.ended ? "ended" : paused ? "paused" : "playing";
        paintTime();
      };
      const paintVolume = () => {
        const silent = video.muted || video.volume === 0;
        if (video.volume > 0) previousNonzeroVolume = video.volume;
        volume.value = String(Math.round(video.volume * 100));
        volume.setAttribute("aria-valuetext", `${volume.value} percent${video.muted ? ", muted" : ""}`);
        mute.setAttribute("aria-label", silent ? "Unmute audio" : "Mute audio");
        mute.setAttribute("aria-pressed", String(silent));
        mute.title = silent ? "Unmute audio" : "Mute audio";
        mute.querySelector(".lesson-player-icon").textContent = silent ? "Unmute" : "Mute";
      };
      const paintFullscreen = () => {
        const native = inNativeFullscreen();
        lesson.dataset.playerNativeFullscreen = String(native);
        video.controls = native || requestingFullscreen;
      };
      const requestPlay = async () => {
        try {
          if (video.ended && Number.isFinite(video.duration)) video.currentTime = 0;
          await video.play();
          if (status && !video.error) status.textContent = "";
        } catch (error) {
          // Pausing during buffering, or starting a different film, cancels the
          // pending play promise. This is a normal control action, not a fault.
          if (error?.name === "AbortError" && video.paused && !video.error) {
            if (active) paintPlayback();
            return;
          }
          if (active) restoreNative("Playback could not start here. Try the native controls, transcript or captioned download below.");
        }
      };

      play.addEventListener("click", safely(() => {
        if (video.paused || video.ended) void requestPlay();
        else video.pause();
      }));
      seek.addEventListener("input", safely(() => {
        if (!Number.isFinite(video.duration) || video.duration <= 0) return;
        video.currentTime = Math.min(video.duration, Math.max(0, Number(seek.value)));
        paintTime();
      }));
      mute.addEventListener("click", safely(() => {
        const silent = video.muted || video.volume === 0;
        if (silent && video.volume === 0) video.volume = previousNonzeroVolume;
        video.muted = !silent;
        paintVolume();
      }));
      volume.addEventListener("input", safely(() => {
        video.volume = Number(volume.value) / 100;
        video.muted = video.volume === 0;
        paintVolume();
      }));
      fullscreen.addEventListener("click", safely(async () => {
        options.open = false;
        requestingFullscreen = true;
        video.controls = true;
        try {
          if (typeof video.requestFullscreen === "function") await video.requestFullscreen();
          else video.webkitEnterFullscreen();
          requestingFullscreen = false;
          if (active) paintFullscreen();
        } catch (_) {
          if (active) restoreNative("Full screen could not open here. Native video controls, the transcript and the captioned download remain available.");
        }
      }));
      ["loadedmetadata", "loadeddata", "canplay", "progress", "durationchange", "timeupdate", "seeked"].forEach(event => {
        video.addEventListener(event, safely(paintTime));
      });
      ["play", "pause", "ended"].forEach(event => video.addEventListener(event, safely(paintPlayback)));
      video.addEventListener("volumechange", safely(paintVolume));
      document.addEventListener("fullscreenchange", safely(paintFullscreen));
      document.addEventListener("webkitfullscreenchange", safely(paintFullscreen));
      video.addEventListener("webkitbeginfullscreen", safely(() => {
        nativeFullscreen = true;
        requestingFullscreen = false;
        paintFullscreen();
      }));
      video.addEventListener("webkitendfullscreen", safely(() => {
        nativeFullscreen = false;
        requestingFullscreen = false;
        paintFullscreen();
      }));
      video.addEventListener("error", () => {
        if (active) restoreNative("Playback is unavailable. Native controls, the transcript and the captioned download remain available below.");
      });
      lesson.addEventListener("toggle", safely(() => { if (!lesson.open) options.open = false; }));
      document.addEventListener("click", safely(event => {
        if (options.open && !options.contains(event.target)) options.open = false;
      }));
      options.addEventListener("keydown", safely(event => {
        if (event.key === "Escape") {
          options.open = false;
          optionsToggle.focus();
        }
      }));

      captionToggle.title = "English captions";
      strip.append(play, seek, time, captionToggle, fullscreen, options);
      video.after(strip);
      paintPlayback();
      paintVolume();
      active = true;
      lesson.dataset.playerEnhanced = "true";
      strip.hidden = false;
      // This is deliberately the final enhancement step. Native controls stay
      // available throughout setup and return on any later enhancement error.
      paintFullscreen();
    } catch (_) {
      restoreNative("Native video controls are available. You can also read the transcript or download the captioned film below.");
    }
  });
})();
