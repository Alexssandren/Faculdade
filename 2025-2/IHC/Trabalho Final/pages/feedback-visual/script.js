/**
 * Script específico da página de Feedback Visual
 */

document.addEventListener('DOMContentLoaded', function() {
    // Função para mostrar toast de feedback
    window.showToast = function() {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    };
    
    // Função para validar campos com feedback visual
    window.validateFeedbackField = function(field) {
        const value = field.value.trim();
        const type = field.type;
        
        field.classList.remove('is-valid', 'is-invalid');
        
        if (value) {
            if (type === 'email') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                field.classList.add(emailRegex.test(value) ? 'is-valid' : 'is-invalid');
            } else {
                field.classList.add('is-valid');
            }
        }
    };
    
    // Adicionar feedback tátil em dispositivos touch
    document.querySelectorAll('.interactive-card, .btn-demo').forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        element.addEventListener('touchend', function() {
            this.style.transform = '';
        });
    });
    
    // Verificar se imagens foram carregadas corretamente
    const images = document.querySelectorAll('.comparison-image-container img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const placeholder = this.nextElementSibling;
            if (placeholder && placeholder.classList.contains('image-placeholder')) {
                placeholder.classList.add('show');
            }
        });
        
        img.addEventListener('load', function() {
            const placeholder = this.nextElementSibling;
            if (placeholder && placeholder.classList.contains('image-placeholder')) {
                placeholder.classList.remove('show');
            }
        });
    });
    
    // Smooth scroll para links internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

