import { socketPromise } from "./socket.js";

document.addEventListener("DOMContentLoaded", function () {
    let generateButton = document.querySelector(".generate-button");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = generateButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const postData = {
        method: 'POST',
        headers: {'X-CSRFToken': csrfToken},
        mode: 'same-origin'
    }
    
    generateButton.addEventListener('click', (e)=>{
        e.preventDefault();
        let buttonDiv = e.target.parentElement;
        let p = document.createElement("p");
        p.innerText = "Generating questions...";
        buttonDiv.innerHTML = "";
        buttonDiv.appendChild(p);
        socketPromise.then(value =>{
            let formData = new FormData()
            formData.append('socket_id', value)
            postData['body'] = formData
            fetch(url, postData)
        })
    });
});