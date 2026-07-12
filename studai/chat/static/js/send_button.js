import { getImages } from "./upload.js";
import { showMaterials } from "./materials.js";
import { socketPromise } from "./socket.js";


function getFormData(textContent, images, socketID){
    const formData = new FormData()
        formData.append('text_content', textContent);
        formData.append('socket_id', socketID)
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
        console.log('test');
        if(!textContent.trim() && !images.length){
            alert("Enter a message or upload an image")
            return
        }
        socketPromise.then((value) => {
            console.log(value)
            const formData = getFormData(textContent, images, value);
            data.body = formData;
            fetch(url, data).then(response => response.json()).then(
                data => {
                    showMaterials(materials, data)
                }
            )})
        })  

    textArea.addEventListener('keypress', (e)=>{
        if(e.key === "Enter"){
            e.preventDefault();
            sendButton.click();
        }});
        
    });