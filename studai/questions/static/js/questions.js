document.addEventListener('DOMContentLoaded', e=>{
    const form = document.querySelector('form')
    const answers = document.querySelector('form .answers')
    const buttonDiv = document.getElementById('answerButton')
    const button = buttonDiv.querySelector('button')
    const chatRelatedId = buttonDiv.dataset.id
    const postData = {
        method:"POST",
        headers: {},
        mode: 'same-origin'
    }

    const url = buttonDiv.dataset.url
    
    button.addEventListener('click', e=>{
        e.preventDefault()
        let formData = new FormData(form)
        formData.append('chat', chatRelatedId)
        postData['body'] = formData
        postData['headers']['X-CSRFToken']=formData.get('csrfmiddlewaretoken')
        if (!form.reportValidity()) {
            return;
        }
        fetch(url, postData).then(async response =>{
            let data = await response.json()
            if (!response.ok){
                throw data;
            }
            return data
        }).then(data =>{
            if (data.redirect){
                let redirect_url = data.redirect;
                window.location.replace(redirect_url);
            } else if(data.form){
                let form = data.form;
                answers.innerHTML = form;
            }
            console.log(data)
        }).catch(errors => {
            console.log(errors)
        }
        )
    })
})