// =============================================
// YouTube Hover — Content Script
// Injected into every youtube.com page.
// Adds a floating PiP button on the player,
// and handles toggle messages from background.
// =============================================

(function () {
  'use strict';

  // ── Constants ──────────────────────────────
  const BTN_ID    = 'yt-hover-pip-btn';
  const TOAST_ID  = 'yt-hover-toast';
  let   toastTimer = null;
  let   observerAttached = false;

  // ── Get the main video element ─────────────
  function getVideo() {
    return document.querySelector('video.html5-main-video') ||
           document.querySelector('ytd-player video') ||
           document.querySelector('video');
  }

  // ── Toggle PiP ────────────────────────────
  async function togglePiP() {
    const video = getVideo();
    if (!video) {
      showToast('⚠️ No video found — play a video first');
      return;
    }

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
        showToast('✕  Exited hover mode');
        updateButtonState(false);
      } else {
        if (!document.pictureInPictureEnabled) {
          showToast('⚠️ Picture-in-Picture not supported');
          return;
        }
        if (video.paused) await video.play().catch(() => {});
        await video.requestPictureInPicture();
        showToast('🎬 Hovering above all apps');
        updateButtonState(true);
      }
    } catch (err) {
      console.warn('[YouTube Hover] PiP error:', err.message);
      if (err.name === 'NotAllowedError') {
        showToast('Click the video first, then try again');
      } else {
        showToast('⚠️ ' + err.message);
      }
    }
  }

  // ── Update button appearance ───────────────
  function updateButtonState(isPiP) {
    const btn = document.getElementById(BTN_ID);
    if (!btn) return;
    const label = btn.querySelector('.yt-hover-label');
    if (isPiP) {
      btn.classList.add('yt-hover-active');
      if (label) label.textContent = 'Exit Hover';
    } else {
      btn.classList.remove('yt-hover-active');
      if (label) label.textContent = 'Hover';
    }
  }

  // ── Show toast ────────────────────────────
  function showToast(msg) {
    let toast = document.getElementById(TOAST_ID);
    if (!toast) {
      toast = document.createElement('div');
      toast.id = TOAST_ID;
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('yt-hover-toast-show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove('yt-hover-toast-show');
    }, 2500);
  }

  // ── Inject the floating button ─────────────
  function injectButton(player) {
    if (document.getElementById(BTN_ID)) return; // already there

    const btn = document.createElement('button');
    btn.id = BTN_ID;
    btn.title = 'Hover above all apps (⌘⇧P)';
    btn.setAttribute('aria-label', 'Toggle Picture-in-Picture');
    btn.innerHTML = `
      <span class="yt-hover-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="4" width="20" height="14" rx="2"/>
          <rect x="12" y="11" width="9" height="7" rx="1.5" fill="currentColor" stroke="none"/>
        </svg>
      </span>
      <span class="yt-hover-label">Hover</span>
    `;

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePiP();
    });

    player.style.position = 'relative';
    player.appendChild(btn);

    // Show button on player hover
    player.addEventListener('mouseenter', () => btn.classList.add('yt-hover-visible'));
    player.addEventListener('mouseleave', () => {
      if (!btn.classList.contains('yt-hover-active')) {
        btn.classList.remove('yt-hover-visible');
      }
    });

    // Track PiP events from the browser (e.g. exiting via browser UI)
    const video = getVideo();
    if (video) {
      video.addEventListener('enterpictureinpicture', () => updateButtonState(true));
      video.addEventListener('leavepictureinpicture', () => updateButtonState(false));
    }
  }

  // ── Find the player and inject ─────────────
  function tryInject() {
    // Try various YouTube player selectors
    const player =
      document.getElementById('movie_player') ||
      document.querySelector('ytd-player') ||
      document.querySelector('.html5-video-player');

    if (player && getVideo()) {
      injectButton(player);
      return true;
    }
    return false;
  }

  // ── Wait for player with MutationObserver ──
  function waitForPlayer() {
    if (tryInject()) return;
    if (observerAttached) return;
    observerAttached = true;

    const observer = new MutationObserver(() => {
      if (tryInject()) {
        observer.disconnect();
        observerAttached = false;
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Fallback: disconnect after 30s
    setTimeout(() => {
      observer.disconnect();
      observerAttached = false;
    }, 30_000);
  }

  // ── Re-inject on YouTube SPA navigation ───
  let lastUrl = location.href;
  const navObserver = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      // Clean up old button
      document.getElementById(BTN_ID)?.remove();
      observerAttached = false;
      // Wait briefly for new page content
      setTimeout(waitForPlayer, 800);
    }
  });
  navObserver.observe(document.body, { childList: true, subtree: true });

  // ── Listen for messages from background ───
  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === 'toggle-pip') {
      togglePiP();
    }
  });

  // ── Boot ──────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForPlayer);
  } else {
    waitForPlayer();
  }

  // Also try again after a short delay (YouTube loads async)
  setTimeout(waitForPlayer, 1500);
  setTimeout(waitForPlayer, 3000);
})();
