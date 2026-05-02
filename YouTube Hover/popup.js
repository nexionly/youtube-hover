// =============================================
// YouTube Hover — Popup Script
// =============================================

const ytContent    = document.getElementById('yt-content');
const notYtContent = document.getElementById('not-yt-content');
const pipBtn       = document.getElementById('pip-btn');
const pipBtnLabel  = document.getElementById('pip-btn-label');
const statusDot    = document.getElementById('status-dot');
const statusText   = document.getElementById('status-text');
const cardMode     = document.getElementById('card-mode');
const openYtBtn    = document.getElementById('open-yt-btn');

function applyPiPState(isPiP) {
  if (isPiP) {
    statusDot.className = 'status-dot pip';
    statusText.textContent = 'Floating above your apps';
    statusText.classList.add('active');
    pipBtn.classList.add('is-pip');
    pipBtnLabel.textContent = 'Exit Hover';
    cardMode.textContent = 'Hovering 🟥';
  } else {
    statusDot.className = 'status-dot active';
    statusText.textContent = 'Ready — video detected';
    statusText.classList.add('active');
    pipBtn.classList.remove('is-pip');
    pipBtnLabel.textContent = 'Hover Video';
    cardMode.textContent = 'Inline';
  }
}

// Query current tab state
chrome.runtime.sendMessage({ action: 'get-pip-status' }, (response) => {
  if (chrome.runtime.lastError) return;
  if (!response) return;

  if (!response.isYouTube) {
    ytContent.style.display = 'none';
    notYtContent.style.display = 'block';
    return;
  }

  ytContent.style.display = 'block';
  notYtContent.style.display = 'none';
  pipBtn.disabled = false;
  applyPiPState(response.isPiP);
});

// Button click → trigger PiP in content script
pipBtn.addEventListener('click', () => {
  pipBtn.disabled = true;
  pipBtn.style.opacity = '0.7';

  chrome.runtime.sendMessage({ action: 'trigger-pip' }, () => {
    // Brief delay then refresh state
    setTimeout(() => {
      chrome.runtime.sendMessage({ action: 'get-pip-status' }, (response) => {
        if (!response) return;
        pipBtn.disabled = false;
        pipBtn.style.opacity = '';
        applyPiPState(response.isPiP);
      });
    }, 400);
  });
});

// Open YouTube
openYtBtn?.addEventListener('click', () => {
  chrome.tabs.create({ url: 'https://www.youtube.com' });
  window.close();
});
