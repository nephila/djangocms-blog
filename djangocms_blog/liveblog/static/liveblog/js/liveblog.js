document.addEventListener("DOMContentLoaded", function() {
  // Correctly decide between ws:// and wss://
  const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const ws_path = ws_scheme + '://' + window.location.host + "/liveblog/liveblog/" + liveblog_apphook + "/" + liveblog_language + "/" + liveblog_post + "/";
  const socket = new ReconnectingWebSocket(ws_path);
  // Handle incoming messages
  socket.onmessage = function (message) {
    // Decode the JSON
    const data = JSON.parse(message.data);
    // See if there's a div to replace it in, or if we should add a new one
    const existing = document.querySelectorAll("div[data-post-id*='" + data.id + "']");
    const postContainer = document.getElementById("liveblog-posts")
    const item = document.createElement('div');
    item.innerHTML = data.content.replace(/\"/g, "'")
    if (existing.length) {
      existing[0].parentNode.replaceChild(item.children[0], existing[0]);
    } else {
      postContainer.insertBefore(
        item.children[0], postContainer.children[0]
      );
    }
  };

}, false);
