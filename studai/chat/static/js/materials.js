document.addEventListener('DOMContentLoaded', e=>{
    const materials = document.getElementById("materials")
    const materialsButton = document.getElementById("materials-button");
    materialsButton.addEventListener('click', e=>{
        let status = materials.dataset.status; 
        let apiUrl = materialsButton.dataset.url;
        let url = new URL(apiUrl, window.location.origin);
        if (status === 'shown'){
            materials.dataset.status = 'hidden'
            materials.innerHTML = "";
        } else{
            materials.dataset.status = 'shown'
            fetch(url).then((response) =>{
                return response.json()
            }).then((data)=>{
                const fragment = document.createDocumentFragment()
                data.forEach(element => {
                    let p = document.createElement('p');
                    p.innerText = element.content;
                    fragment.appendChild(p);
                });
                materials.appendChild(fragment);
            })
            
        }
        e.preventDefault();
    })
})