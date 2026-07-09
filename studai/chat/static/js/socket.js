export const socketPromise = new Promise((resolve) => {
    function initSocket() {
        const id = document.querySelector(".chat-detail").id;
        const btn_class = document.querySelector(".send-button");
        const btn = btn_class.querySelector("button");

        const chatSocket = new WebSocket(
            'ws://' +
            window.location.host +
            '/ws/chat/' +
            id +
            '/'
        );
        console.log("WebSocket connection established.");

        chatSocket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            console.log(data);

            if (data.channel_id) {
                resolve(data.channel_id);
            }

            if (data["button-locked"] === false) {
                const p = document.createElement("p");
                p.textContent = "Uploading images...";
                btn.style.display = "none";      
                btn_class.appendChild(p);
            } 
            else if (data["button-locked"] === true) {
                alert("Wait for previous images to upload before sending new ones.");
            }
            else if (data["button-finished"] === true) {
                btn_class.removeChild(btn_class.querySelector("p"));
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