export const socketPromise = new Promise((resolve) => {
    function initSocket() {
        const id = document.querySelector(".chat-detail").id;

        const chatSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/chat/' +
            id +
            '/'
        );

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);

            if (data.channel_id) {
                resolve(data.channel_id);
            }

        };

        chatSocket.onclose = function () {
            console.error("Chat socket closed unexpectedly");
        };
    }


    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initSocket
        );
    } else {
        initSocket();
    }
});