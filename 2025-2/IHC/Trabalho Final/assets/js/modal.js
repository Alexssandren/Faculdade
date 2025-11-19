/**
 * Modal/Popup Component - UFSC IHC Redesign
 * Funcionalidade para abrir e fechar modais com versões corrigidas
 */

(function() {
    'use strict';

    // ============================================
    // Criação de Modal
    // ============================================
    
    function createModal(title, content, footerContent = null) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-labelledby', 'modal-title');
        overlay.setAttribute('aria-hidden', 'true');
        
        const container = document.createElement('div');
        container.className = 'modal-container';
        
        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        
        const titleElement = document.createElement('h2');
        titleElement.id = 'modal-title';
        titleElement.className = 'modal-title';
        titleElement.textContent = title;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'modal-close';
        closeBtn.setAttribute('aria-label', 'Fechar modal');
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = () => closeModal(overlay);
        
        header.appendChild(titleElement);
        header.appendChild(closeBtn);
        
        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        
        // Se content for string, insere como HTML
        if (typeof content === 'string') {
            body.innerHTML = content;
        } else if (content instanceof HTMLElement) {
            body.appendChild(content);
        } else if (content instanceof NodeList || Array.isArray(content)) {
            content.forEach(node => body.appendChild(node.cloneNode(true)));
        }
        
        container.appendChild(header);
        container.appendChild(body);
        
        // Footer (opcional)
        if (footerContent) {
            const footer = document.createElement('div');
            footer.className = 'modal-footer';
            
            if (typeof footerContent === 'string') {
                footer.innerHTML = footerContent;
            } else if (footerContent instanceof HTMLElement) {
                footer.appendChild(footerContent);
            }
            
            container.appendChild(footer);
        }
        
        overlay.appendChild(container);
        
        // Event listeners
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
        
        // Fechar com ESC
        const escapeHandler = function(e) {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                closeModal(overlay);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        // Trap de foco
        trapFocus(container);
        
        return overlay;
    }
    
    // ============================================
    // Abrir Modal
    // ============================================
    
    function openModal(modal) {
        if (!modal) return;
        
        document.body.appendChild(modal);
        document.body.classList.add('modal-open');
        
        // Força reflow para animação
        modal.offsetHeight;
        
        modal.setAttribute('aria-hidden', 'false');
        modal.classList.add('active');
        
        // Foca no primeiro elemento focável
        const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }
    }
    
    // ============================================
    // Fechar Modal
    // ============================================
    
    function closeModal(modal) {
        if (!modal) return;
        
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
        
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
            document.body.classList.remove('modal-open');
        }, 300); // Aguarda animação
    }
    
    // ============================================
    // Trap de Foco (Acessibilidade)
    // ============================================
    
    function trapFocus(container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        container.addEventListener('keydown', function(e) {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
    }
    
    // ============================================
    // Carregar Conteúdo de Arquivo HTML
    // ============================================
    
    function loadModalContent(url, title) {
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Extrai apenas o conteúdo do body
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const bodyContent = doc.body.innerHTML;
                
                const modal = createModal(title, bodyContent);
                openModal(modal);
            })
            .catch(error => {
                console.error('Erro ao carregar conteúdo do modal:', error);
                alert('Erro ao carregar a versão corrigida. Por favor, tente novamente.');
            });
    }
    
    // ============================================
    // API Pública
    // ============================================
    
    window.Modal = {
        create: createModal,
        open: openModal,
        close: closeModal,
        loadContent: loadModalContent
    };
    
    // ============================================
    // Inicialização - Botões com data-modal
    // ============================================
    
    function initModalButtons() {
        document.querySelectorAll('[data-modal]').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const modalUrl = this.getAttribute('data-modal');
                const modalTitle = this.getAttribute('data-modal-title') || 'Versão Corrigida';
                
                if (modalUrl) {
                    loadModalContent(modalUrl, modalTitle);
                } else {
                    console.error('data-modal attribute não encontrado');
                }
            });
        });
    }
    
    // ============================================
    // Inicialização quando DOM estiver pronto
    // ============================================
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModalButtons);
    } else {
        initModalButtons();
    }
    
})();

