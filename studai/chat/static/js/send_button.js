import { getFiles } from "./upload.js";

function addTextElement(textContent){
    const messageArea = document.getElementById("materials");
    const newMessage = document.createElement("p");
    if (messageArea.dataset.status === "shown"){
        newMessage.textContent = textContent;
        messageArea.appendChild(newMessage);
    }
}

function getFormData(textContent, files){
    const formData = new FormData()
        formData.append('text_content', textContent);
        files.forEach(file =>{
            formData.append('files', file)
    })
    return formData
}

document.addEventListener("DOMContentLoaded", function () {
    let sendButton = document.querySelector(".send-button");
    let textArea = document.getElementById("id_text_content");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = sendButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const data = {'method':'POST', 'headers': {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken}};

    sendButton.addEventListener('click', (e)=>{
        e.preventDefault();
        const textContent = textArea.value;
        textArea.value = "";
        const formData = getFormData(textContent, getFiles());
        addTextElement(textContent);
        data.body = FormData;
        fetch(url, data);
    });


    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});

    });