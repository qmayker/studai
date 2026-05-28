document.addEventListener("DOMContentLoaded", function () {
    const id = document.querySelector(".chat-detail").id;
    const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + id
            + '/'
    );

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data); 
        console.log(data);
    };

    chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };
});