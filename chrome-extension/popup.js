
const defaults = {
  serverUrl: "http://127.0.0.1:2526",
  subreddit: "LocalLLaMA",
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

$("save").addEventListener("click", async () => {
  await chrome.storage.local.set({
    serverUrl: $("serverUrl").value.trim(),
    subreddit: $("subreddit").value.trim(),
    token: $("token").value.trim()
  });
  status("Settings saved.");
});

$("capture").addEventListener("click", async () => {
  try {
    await $("save").click();
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
    await $("save").click();
    const response = await chrome.runtime.sendMessage({type: "GET_ENCRYPTED_TIMESTAMP"});
    if (!response?.ok) throw new Error(response?.error || "Timestamp request failed.");
    await navigator.clipboard.writeText(response.data.encrypted_timestamp);
    status("Encrypted timestamp copied.");
  } catch (error) {
    status(String(error));
  }
});

load();
