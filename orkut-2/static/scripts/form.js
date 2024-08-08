const togglePasswordButtons = document.querySelectorAll(".toggle-password")


const eye_open = '<i class="ph ph-eye"></i>'
const eye_closed = '<i class="ph ph-eye-slash"></i>'

togglePasswordButtons.forEach(container => {
    container.addEventListener("click", ()=>{
        if (container.innerHTML === eye_closed){
            container.innerHTML = eye_open
            container.previousElementSibling.type = "password"
        }else{
            container.innerHTML = eye_closed
            container.previousElementSibling.type = "text"
        }
    })
})





