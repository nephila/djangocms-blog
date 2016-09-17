document.addEventListener("DOMContentLoaded", function() {
  // Correctly decide between ws:// and wss://
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var ws_path = ws_scheme + '://' + window.location.host + "/liveblog/liveblog/" + liveblog_apphook + "/" + liveblog_language + "/" + liveblog_post + "/";
  var socket = new ReconnectingWebSocket(ws_path);
  // Handle incoming messages
  socket.onmessage = function (message) {
    // Decode the JSON
    var data = JSON.parse(message.data);
    // See if there's a div to replace it in, or if we should add a new one
    var existing = document.querySelectorAll("div[data-post-id*='" + data.id + "']");
    var item = document.createElement('div');
    item.innerHTML = data.content;
    if (existing.length > 0) {
      existing[0].parentNode.replaceChild(item.children[0], existing[0]);
    } else {
      document.getElementById("liveblog-posts").insertBefore(
        item.children[0], document.getElementById("liveblog-posts").children[0]
      );
    }
  };

}, false);

