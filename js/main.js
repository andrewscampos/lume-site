var menu  = document.querySelector('.menu-icon')
function openCLose(){
    let item = document.querySelector('.menu') 
    if(!item.classList.contains('ativo')){
        item.classList.add('ativo')
        document.querySelector('.menu-icon img').src = 'img/close.png'
    } else {
        item.classList.remove('ativo')
        document.querySelector('.menu-icon img').src = 'img/menu.png'

    }
}
menu.addEventListener('click', () => {
    openCLose()
})

document.addEventListener("DOMContentLoaded", function () {
    const elements = document.querySelectorAll(".load-up, .load-down, .load-to-left, .load-to-right");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
            } else {
                entry.target.classList.remove("show"); // Remove quando sai da tela
            }
        });
    }, { threshold: 0.01 }); // 30% visível já ativa a animação

    elements.forEach((element) => {
        observer.observe(element);
    });
}); 

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (event) {
            event.preventDefault(); // Impede o comportamento padrão do link

            const targetId = this.getAttribute("href").substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                if(targetId != 'home'){
                    openCLose()
                }
                const offset = 110; // Ajuste de 30px
                const targetPosition = targetElement.getBoundingClientRect().top + window.scrollY - offset;

                window.scrollTo({
                    top: targetPosition,
                    behavior: "smooth" // Rolagem suave
                });
            }
        });
    });
});
