document.addEventListener("DOMContentLoaded", function () {
    let generateButton = document.querySelector(".generate-button");
    const csrfToken = Cookies.get('csrftoken');
    const apiUrl = generateButton.dataset.url;
    const url = new URL(apiUrl, window.location.origin);
    
    generateButton.addEventListener('click', (e)=>{
        e.preventDefault();
        fetch(url);
        let buttonDiv = e.target.parentElement;
        let p = document.createElement("p");
        p.innerText = "Generating questions...";
        buttonDiv.innerHTML = "";
        buttonDiv.appendChild(p);
    });
});