
function cleanText(value) {
  return (value || "").replace(/\s+/g, " ").trim();
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function extractVisibleReddit() {
  const title =
    cleanText(document.querySelector("h1")?.innerText) ||
    cleanText(document.querySelector("shreddit-post")?.getAttribute("post-title")) ||
    document.title;

  const postSelectors = [
    "shreddit-post [slot='text-body']",
    "[data-testid='post-content']",
    ".usertext-body"
  ];
  let postText = "";
  for (const selector of postSelectors) {
    const node = document.querySelector(selector);
    if (node && node.innerText) {
      postText = cleanText(node.innerText);
      break;
    }
  }

  const commentSelectors = [
    "shreddit-comment [slot='comment']",
    "shreddit-comment",
    "[data-testid='comment']",
    ".comment .md"
  ];
  const comments = [];
  for (const selector of commentSelectors) {
    document.querySelectorAll(selector).forEach(node => {
      const text = cleanText(node.innerText);
      if (text.length >= 2 && text.length <= 5000) comments.push(text);
    });
    if (comments.length) break;
  }

  return {
    thread_url: location.href,
    thread_title: title,
    post_text: postText,
    comments: unique(comments).slice(0, 200),
    captured_from_visible_tab: true
  };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CAPTURE_VISIBLE_REDDIT") {
    sendResponse({ok: true, payload: extractVisibleReddit()});
  }
});
