$(function () {
  // Correctly decide between ws:// and wss://
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var ws_path = ws_scheme + '://' + window.location.host + "/liveblog/liveblog/" + liveblog_apphook + "/" + liveblog_language + "/" + liveblog_post + "/";
  console.log("Connecting to " + ws_path);
  var socket = new ReconnectingWebSocket(ws_path);
  // Handle incoming messages
  socket.onmessage = function (message) {
    // Decode the JSON
    console.log("Got message " + message.data);
    var data = JSON.parse(message.data);
    // See if there's a div to replace it in, or if we should add a new one
    var existing = $("div[data-post-id=" + data.id + "]");
    if (existing.length) {
      existing.replaceWith(data.content);
    } else {
      $("#liveblog-posts").prepend(data.content);
    }
  };
  // Helpful debugging
  socket.onopen = function () {
    console.log("Connected to notification socket");
  }
  socket.onclose = function () {
    console.log("Disconnected to notification socket");
  }
});
