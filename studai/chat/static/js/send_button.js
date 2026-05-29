document.addEventListener("DOMContentLoaded", function () {
    let sendButton = document.querySelector(".send-button");
    let textArea = document.getElementById("id_text_content");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = sendButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const data = {'method':'POST', 'headers': {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken}};

    sendButton.addEventListener('click', (e)=>{
        e.preventDefault();
        const textArea = document.getElementById("id_text_content");
        const textContent = textArea.value;
        textArea.value = "";

        const messageArea = document.getElementById("materials");
        const newMessage = document.createElement("p");
        console.log(messageArea.dataset.status)
        if (messageArea.dataset.status === "shown"){
            newMessage.textContent = textContent;
            messageArea.appendChild(newMessage);
        }
        data.body = JSON.stringify({"text_content": textContent});
        fetch(url, data);
    });


    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});

    });