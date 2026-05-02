// Background service worker - handles keyboard shortcuts and cross-tab messaging

chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'toggle-pip') {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && tab.url.includes('youtube.com')) {
      chrome.tabs.sendMessage(tab.id, { action: 'toggle-pip' });
    }
  }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'get-pip-status') {
    chrome.tabs.query({ active: true, currentWindow: true }, async ([tab]) => {
      if (tab && tab.url && tab.url.includes('youtube.com')) {
        try {
          const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => !!document.pictureInPictureElement
          });
          sendResponse({ isYouTube: true, isPiP: results[0]?.result ?? false });
        } catch {
          sendResponse({ isYouTube: true, isPiP: false });
        }
      } else {
        sendResponse({ isYouTube: false, isPiP: false });
      }
    });
    return true; // keep channel open for async
  }

  if (message.action === 'trigger-pip') {
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (tab) {
        chrome.tabs.sendMessage(tab.id, { action: 'toggle-pip' });
        sendResponse({ ok: true });
      }
    });
    return true;
  }
});
