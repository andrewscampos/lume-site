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
    const elements = document.querySelectorAll(".load-up, .load-down,   .load-to-right");

    
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
    const elements = document.querySelectorAll(".load-to-left");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {

                if (entry.isIntersecting) {
                                        //entry.target.classList.remove('animate__animated', 'animate__backInRight');

                    entry.target.classList.add('animate__animated','animate__backInRight');
                    setTimeout(() => {
                        entry.target.classList.remove('animate__animated','animate__backInRight');
                    }, 1500);
                }else{
                    setTimeout(() => {
                        entry.target.classList.remove('animate__animated','animate__backInRight');
                    }, 1500);
                }
        });
    }, { threshold: 0.1 }); // Ativa quando 50% do elemento estiver visível

    elements.forEach((element) => observer.observe(element));
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


const tiposSites = document.getElementById('tipos-sites');

tiposSites.addEventListener('click', function() {
    window.location.href = "tipos-sites.html";

});

const adicionais = document.getElementById('adicionais');

adicionais.addEventListener('click', function() {
    window.location.href = "adicionais.html";

});

const prazos = document.getElementById('prazos');

prazos.addEventListener('click', function() {
    window.location.href = "prazos.html";

});


document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Impede o recarregamento da página

        // Capturar valores do formulário
        const formData = {
            nome: form.querySelector("input[placeholder='Nome*']").value.trim(),
            email: form.querySelector("input[placeholder='E-mail*']").value.trim(),
            empresa: form.querySelector("input[placeholder='Empresa*']").value.trim(),
            cargo: form.querySelector("input[placeholder='Cargo*']").value.trim(),
            telefone: form.querySelector("input[placeholder='Telefone*']").value.trim(),
            mensagem: form.querySelector("textarea[placeholder='Mensagem']").value.trim()
        };

        // Validação básica
        if (!formData.nome || !formData.email || !formData.telefone || !formData.mensagem) {
            alert("Por favor, preencha todos os campos obrigatórios!");
            return;
        }

        if (!formData.nome || !formData.email || !formData.telefone || !formData.mensagem) {
            alert("Por favor, preencha todos os campos obrigatórios!");
            return;
        }
    
        // Montar a mensagem formatada para o WhatsApp
        const mensagem = `Olá! Tenho interesse e gostaria de mais informações.
    
        🔹 Nome: ${formData.nome}
        📧 E-mail: ${formData.email}
        🏢 Empresa: ${formData.empresa}
        💼 Cargo: ${formData.cargo}
        📞 Telefone: ${formData.telefone}
        📝 Mensagem: ${formData.mensagem}`;
    
        // Codificar a mensagem para URL
        const urlWhatsapp = `https://wa.me/551699865-3237?text=${encodeURIComponent(mensagem)}`;
    
        // Abrir o WhatsApp
        window.open(urlWhatsapp, "_blank");
    
        // Limpar o formulário
        form.reset();
    });
});
