// JavaScript personalizado para o VanGo

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Validação de formulários
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Animação de elementos ao scroll
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length > 0) {
        const animateOnScroll = function() {
            animateElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementPosition < windowHeight - 50) {
                    element.classList.add('animate-fade-in');
                }
            });
        };
        
        // Executar uma vez ao carregar a página
        animateOnScroll();
        
        // Executar ao scroll
        window.addEventListener('scroll', animateOnScroll);
    }

    // Funcionalidade para o formulário de busca na página inicial
    const searchForm = document.querySelector('#route-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const origin = document.querySelector('#origin').value;
            const destination = document.querySelector('#destination').value;
            const date = document.querySelector('#date').value;
            
            if (!origin || !destination || !date) {
                e.preventDefault();
                alert('Por favor, preencha todos os campos obrigatórios.');
            }
        });
    }

    // Funcionalidade para o cálculo de preço total em reservas
    const passengerSelect = document.querySelector('#num_passengers');
    const pricePerPerson = document.querySelector('#price_per_person');
    const totalPriceElement = document.querySelector('#total_price');
    
    if (passengerSelect && pricePerPerson && totalPriceElement) {
        const updateTotalPrice = function() {
            const numPassengers = parseInt(passengerSelect.value);
            const price = parseFloat(pricePerPerson.dataset.price);
            const totalPrice = numPassengers * price;
            
            totalPriceElement.textContent = totalPrice.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });
        };
        
        // Atualizar preço inicial
        updateTotalPrice();
        
        // Atualizar quando o número de passageiros mudar
        passengerSelect.addEventListener('change', updateTotalPrice);
    }
});
