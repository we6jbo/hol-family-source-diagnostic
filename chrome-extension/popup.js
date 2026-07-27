const defaults = {
  serverUrl: "http://127.0.0.1:2526",
  subreddit: "Genealogy",
  token: ""
};

const $ = id => document.getElementById(id);
const status = text => $("status").textContent = text;

async function load() {
  const cfg = await chrome.storage.local.get(defaults);
  $("serverUrl").value = cfg.serverUrl;
  $("subreddit").value = cfg.subreddit;
  $("token").value = cfg.token;
}

async function saveSettings() {
  await chrome.storage.local.set({
    serverUrl: $("serverUrl").value.trim(),
    subreddit: $("subreddit").value.trim(),
    token: $("token").value.trim()
  });
}

$("save").addEventListener("click", async () => {
  await saveSettings();
  status("Settings saved.");
});

$("openGenealogy").addEventListener("click", async () => {
  await saveSettings();
  await chrome.tabs.create({url: "https://www.reddit.com/r/Genealogy/"});
  status("Opened r/Genealogy. Click Join yourself, then read the rules and FAQ before posting.");
});

$("testOllama").addEventListener("click", async () => {
  try {
    await saveSettings();
    const cfg = await chrome.storage.local.get(defaults);
    if (!cfg.token) throw new Error("Paste the bridge token first.");
    const response = await fetch(`${cfg.serverUrl}/ollama-test`, {
      headers: {"X-HOL-Token": cfg.token}
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || `HTTP ${response.status}`);
    status(`Ollama test succeeded using ${data.model}.\nResponse:\n${data.response}`);
  } catch (error) {
    status(`Ollama test failed: ${String(error)}`);
  }
});

$("capture").addEventListener("click", async () => {
  try {
    await saveSettings();
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    if (!tab || !/^https:\/\/(www|old)\.reddit\.com\//.test(tab.url || "")) {
      throw new Error("Open a Reddit thread in the active tab first.");
    }
    const capture = await chrome.tabs.sendMessage(tab.id, {type: "CAPTURE_VISIBLE_REDDIT"});
    if (!capture?.ok) throw new Error("Could not capture the visible thread.");
    const response = await chrome.runtime.sendMessage({
      type: "SEND_OBSERVATION",
      payload: capture.payload
    });
    if (!response?.ok) throw new Error(response?.error || "Bridge rejected the capture.");
    status(
      `Sent ${capture.payload.comments.length} visible comments.\n` +
      `Encrypted timestamp:\n${response.data.encrypted_timestamp}`
    );
  } catch (error) {
    status(String(error));
  }
});

$("timestamp").addEventListener("click", async () => {
  try {
    await saveSettings();
    const response = await chrome.runtime.sendMessage({type: "GET_ENCRYPTED_TIMESTAMP"});
    if (!response?.ok) throw new Error(response?.error || "Timestamp request failed.");
    await navigator.clipboard.writeText(response.data.encrypted_timestamp);
    status("Encrypted timestamp copied.");
  } catch (error) {
    status(String(error));
  }
});

load();
