import { getImages } from "./upload.js";

function addTextElement(textContent){
    const messageArea = document.getElementById("materials");
    const newMessage = document.createElement("p");
    if (messageArea.dataset.status === "shown"){
        newMessage.textContent = textContent;
        messageArea.appendChild(newMessage);
    }
}

function getFormData(textContent, images){
    const formData = new FormData()
        formData.append('text_content', textContent);
        images.forEach(image =>{
            formData.append('image_content', image)
    })
    return formData
}

document.addEventListener("DOMContentLoaded", function () {
    let sendButton = document.querySelector(".send-button");
    let textArea = document.getElementById("id_text_content");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = sendButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const data = {'method':'POST', 'headers': {'X-CSRFToken': csrfToken}};

    sendButton.addEventListener('click', (e)=>{
        e.preventDefault();
        const textContent = textArea.value;
        const images = getImages()
        textArea.value = "";
        if(!textContent.trim() && !images.length){
            alert("Enter a message or upload an image")
            return
        }
        const formData = getFormData(textContent, images);
        addTextElement(textContent);
        data.body = formData;
        fetch(url, data).then(async response => {
            const text = await response.json();
            if (!response.ok) {
                throw new Error(text);
            }
            return text;
        }).catch(error => {
            console.error("Error:", error);
        });
    });


    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});

    });