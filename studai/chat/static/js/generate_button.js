document.addEventListener("DOMContentLoaded", function () {
    let generateButton = document.querySelector(".generate-button");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = generateButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    const id = document.querySelector(".chat-detail").id;
    const data = {'method':'POST', 'headers': {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken}};
    const body = {'chat_related_id': id};
    data.body = JSON.stringify(body);

    generateButton.addEventListener('click', (e)=>{
        e.preventDefault();
        fetch(url, data);
    });
});