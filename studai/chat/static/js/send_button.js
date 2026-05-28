document.addEventListener("DOMContentLoaded", function () {
    let sendButton = document.querySelector(".send-button");
    let textArea = document.getElementById("id_text_content");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = sendButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const id = document.querySelector(".chat-detail").id;
    const data = {'method':'POST', 'headers': {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken}};
    const body = {'chat_id': id};

    sendButton.addEventListener('click', (e)=>{
        e.preventDefault();
        const textArea = document.getElementById("id_text_content");
        const textContent = textArea.value;
        textArea.value = "";

        const messageArea = document.querySelector(".chat-messages");
        const newMessage = document.createElement("p");
        newMessage.textContent = textContent;
        messageArea.appendChild(newMessage);
        body["text_content"] = textContent;
        data.body = JSON.stringify(body);
        fetch(url, data);
    });


    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});

    });