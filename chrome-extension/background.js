
const DEFAULTS = {
  serverUrl: "http://127.0.0.1:2526",
  subreddit: "LocalLLaMA",
  token: "",
  monitoring: false
};

chrome.runtime.onInstalled.addListener(async () => {
  const current = await chrome.storage.local.get(DEFAULTS);
  await chrome.storage.local.set(current);
});

async function sendObservation(payload) {
  const cfg = await chrome.storage.local.get(DEFAULTS);
  if (!cfg.token) throw new Error("Paste the bridge token in the extension popup.");
  const response = await fetch(`${cfg.serverUrl}/reddit-observation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-HOL-Token": cfg.token
    },
    body: JSON.stringify({...payload, subreddit: cfg.subreddit})
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SEND_OBSERVATION") {
    sendObservation(message.payload)
      .then(data => sendResponse({ok: true, data}))
      .catch(error => sendResponse({ok: false, error: String(error)}));
    return true;
  }
  if (message.type === "GET_ENCRYPTED_TIMESTAMP") {
    chrome.storage.local.get(DEFAULTS).then(async cfg => {
      if (!cfg.token) throw new Error("Paste the bridge token first.");
      const response = await fetch(`${cfg.serverUrl}/encrypted-timestamp`, {
        headers: {"X-HOL-Token": cfg.token}
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
      sendResponse({ok: true, data});
    }).catch(error => sendResponse({ok: false, error: String(error)}));
    return true;
  }
});
 