document.addEventListener("DOMContentLoaded", function () {
    let sendButton = document.querySelector(".send-button");
    sendButton.addEventListener('click', (e)=>{
        e.preventDefault();
        textarea = document.getElementById("id_text_content");
        console.log(textarea.value);
    })
});