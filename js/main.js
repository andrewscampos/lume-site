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

        try {
            // Enviar dados via POST em formato JSON
            const response = await fetch("https://seu-endpoint.com/api/formulario", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                alert("Mensagem enviada com sucesso!");
                form.reset(); // Limpar o formulário após o envio
            } else {
                alert("Erro ao enviar a mensagem. Tente novamente mais tarde.");
            }
        } catch (error) {
            console.error("Erro ao enviar formulário:", error);
            alert("Ocorreu um erro. Verifique sua conexão e tente novamente.");
        }
    });
});
