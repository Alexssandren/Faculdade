/**
 * Script principal do protótipo UFSC IHC Redesign
 * Funcionalidades de interatividade e acessibilidade
 */

(function() {
    'use strict';

    // ============================================
    // Navegação Mobile (Menu Hambúrguer)
    // ============================================
    
    function initMobileMenu() {
        const navMenu = document.querySelector('.nav-menu');
        if (!navMenu) return;

        // Criar botão hambúrguer se não existir
        let hamburgerBtn = document.querySelector('.hamburger-btn');
        if (!hamburgerBtn && window.innerWidth <= 768) {
            hamburgerBtn = document.createElement('button');
            hamburgerBtn.className = 'hamburger-btn';
            hamburgerBtn.setAttribute('aria-label', 'Abrir menu de navegação');
            hamburgerBtn.setAttribute('aria-expanded', 'false');
            hamburgerBtn.innerHTML = `
                <span class="hamburger-icon">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
            `;
            
            const navbar = document.querySelector('.navbar .container');
            if (navbar) {
                navbar.appendChild(hamburgerBtn);
            }
        }

        if (hamburgerBtn) {
            hamburgerBtn.addEventListener('click', function() {
                const isExpanded = hamburgerBtn.getAttribute('aria-expanded') === 'true';
                hamburgerBtn.setAttribute('aria-expanded', !isExpanded);
                navMenu.classList.toggle('nav-menu-open');
                hamburgerBtn.classList.toggle('hamburger-active');
            });
        }
    }

    // ============================================
    // Validação de Formulários em Tempo Real
    // ============================================
    
    function initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Validação em tempo real
                input.addEventListener('blur', function() {
                    validateField(input);
                });
                
                // Feedback visual durante digitação
                input.addEventListener('input', function() {
                    if (input.classList.contains('is-invalid')) {
                        validateField(input);
                    }
                });
            });
            
            // Validação no submit
            form.addEventListener('submit', function(e) {
                let isValid = true;
                inputs.forEach(input => {
                    if (!validateField(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    // Focar no primeiro campo inválido
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
            });
        });
    }
    
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let errorMessage = '';
        
        // Validação de campo obrigatório
        if (required && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        }
        
        // Validação de email
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Digite um email válido';
            }
        }
        
        // Validação de CPF
        if (field.hasAttribute('data-cpf') && value) {
            const cpf = value.replace(/\D/g, '');
            if (cpf.length !== 11 || !isValidCPF(cpf)) {
                isValid = false;
                errorMessage = 'Digite um CPF válido';
            }
        }
        
        // Validação de telefone
        if (field.hasAttribute('data-phone') && value) {
            const phone = value.replace(/\D/g, '');
            if (phone.length < 10 || phone.length > 11) {
                isValid = false;
                errorMessage = 'Digite um telefone válido';
            }
        }
        
        // Atualizar estado visual
        updateFieldState(field, isValid, errorMessage);
        
        return isValid;
    }
    
    function updateFieldState(field, isValid, errorMessage) {
        const feedback = field.parentElement.querySelector('.form-feedback');
        
        field.classList.remove('is-valid', 'is-invalid');
        
        if (field.value.trim()) {
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }
        
        if (feedback) {
            feedback.textContent = errorMessage;
            feedback.className = 'form-feedback ' + (isValid ? 'form-feedback-success' : 'form-feedback-error');
        }
    }
    
    function isValidCPF(cpf) {
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let digit = 11 - (sum % 11);
        if (digit >= 10) digit = 0;
        if (digit !== parseInt(cpf.charAt(9))) return false;
        
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        digit = 11 - (sum % 11);
        if (digit >= 10) digit = 0;
        if (digit !== parseInt(cpf.charAt(10))) return false;
        
        return true;
    }

    // ============================================
    // Máscaras de Entrada
    // ============================================
    
    function initInputMasks() {
        // Máscara de CPF
        document.querySelectorAll('[data-cpf]').forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                    e.target.value = value;
                }
            });
        });
        
        // Máscara de telefone
        document.querySelectorAll('[data-phone]').forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length <= 11) {
                    if (value.length <= 10) {
                        value = value.replace(/(\d{2})(\d)/, '($1) $2');
                        value = value.replace(/(\d{4})(\d)/, '$1-$2');
                    } else {
                        value = value.replace(/(\d{2})(\d)/, '($1) $2');
                        value = value.replace(/(\d{5})(\d)/, '$1-$2');
                    }
                    e.target.value = value;
                }
            });
        });
    }

    // ============================================
    // Tooltips Explicativos
    // ============================================
    
    function initTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltipText = element.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            tooltip.setAttribute('role', 'tooltip');
            tooltip.setAttribute('aria-hidden', 'true');
            
            element.appendChild(tooltip);
            element.setAttribute('aria-describedby', 'tooltip-' + Math.random().toString(36).substr(2, 9));
            
            element.addEventListener('mouseenter', function() {
                tooltip.setAttribute('aria-hidden', 'false');
                tooltip.classList.add('tooltip-visible');
            });
            
            element.addEventListener('mouseleave', function() {
                tooltip.setAttribute('aria-hidden', 'true');
                tooltip.classList.remove('tooltip-visible');
            });
        });
    }

    // ============================================
    // Navegação por Teclado Aprimorada
    // ============================================
    
    function initKeyboardNavigation() {
        // Skip link para conteúdo principal
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link sr-only';
        skipLink.textContent = 'Pular para conteúdo principal';
        skipLink.addEventListener('focus', function() {
            this.classList.remove('sr-only');
        });
        skipLink.addEventListener('blur', function() {
            this.classList.add('sr-only');
        });
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Trap de foco em modais
        document.querySelectorAll('[role="dialog"]').forEach(modal => {
            const focusableElements = modal.querySelectorAll(
                'a[href], button:not([disabled]), textarea:not([disabled]), ' +
                'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            
            if (focusableElements.length > 0) {
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                modal.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab') {
                        if (e.shiftKey) {
                            if (document.activeElement === firstElement) {
                                e.preventDefault();
                                lastElement.focus();
                            }
                        } else {
                            if (document.activeElement === lastElement) {
                                e.preventDefault();
                                firstElement.focus();
                            }
                        }
                    }
                    if (e.key === 'Escape') {
                        modal.setAttribute('aria-hidden', 'true');
                        modal.classList.remove('modal-visible');
                    }
                });
            }
        });
    }

    // ============================================
    // Inicialização
    // ============================================
    
    function init() {
        // Aguardar DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        initMobileMenu();
        initFormValidation();
        initInputMasks();
        initTooltips();
        initKeyboardNavigation();
        
        // Ajustar menu mobile em resize
        window.addEventListener('resize', function() {
            const navMenu = document.querySelector('.nav-menu');
            const hamburgerBtn = document.querySelector('.hamburger-btn');
            
            if (window.innerWidth > 768) {
                navMenu?.classList.remove('nav-menu-open');
                hamburgerBtn?.classList.remove('hamburger-active');
                hamburgerBtn?.setAttribute('aria-expanded', 'false');
            }
        });
    }
    
    init();
})();

