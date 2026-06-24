const files = []
document.addEventListener("DOMContentLoaded", (e)=>{
    const uploadButton = document.querySelector("#image-upload .upload")
    uploadButton.addEventListener('change', (e)=>{
        let uploadedFiles = uploadButton.files;
        for (const file of uploadedFiles) {
            files.push(file);
        }
        uploadButton.value = "";
        console.log(files);
    })
})

export function getFiles(){
    let copiedFiles = files.slice()
    files.length = 0
    return copiedFiles
}
