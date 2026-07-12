export const socketPromise = new Promise((resolve) => {
    function initSocket() {
        const chatDetail = document.querySelector(".chat-detail")
        const id = chatDetail.id;
        const userId = chatDetail.dataset.user_id;
        const btnClass = document.querySelector(".send-button");
        const btn = btnClass.querySelector("button");

        const chatSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/chat/' +
            userId +
            '/' +
            id +
            '/'
        );
        console.log("WebSocket connection established.");

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);

            if (data.socket_id) {
                resolve(data.socket_id);
            }

            if (data["button-locked"] === false) {
                const p = document.createElement("p");
                p.textContent = "Uploading images...";
                btn.style.display = "none";      
                btnClass.appendChild(p);
            } 
            else if (data["button-locked"] === true) {
                alert("Wait for previous images to upload before sending new ones.");
            }
            else if (data["button-finished"] === true) {
                btnClass.removeChild(btnClass.querySelector("p"));
                btn.style.display = "block";
            }
            else if (data["is_ready"] === true){
                
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