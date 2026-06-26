import { getImages } from "./upload.js";
import { showMaterials } from "./materials.js";


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
    const materials = document.getElementById("materials");

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
        data.body = formData;
        fetch(url, data).then(response => response.json()).then(
            data => {
                showMaterials(materials, data)
            }
        )})

    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});
        
    });