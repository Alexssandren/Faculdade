/**
 * Script específico da Homepage Corrigida
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Homepage corrigida carregada');

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

    // Feedback visual para botões
    document.querySelectorAll('.btn, .service-card, .news-card').forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });

        element.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });

    // Menu mobile toggle (se houver)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMain = document.querySelector('.nav-main');

    if (mobileMenuToggle && navMain) {
        mobileMenuToggle.addEventListener('click', function() {
            navMain.classList.toggle('mobile-open');
        });
    }

    // Lazy loading para imagens
    const images = document.querySelectorAll('img[loading="lazy"]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Carrossel Hero
    class Carousel {
        constructor() {
            this.slides = document.querySelectorAll('.carousel-slide');
            this.indicators = document.querySelectorAll('.indicator');
            this.prevBtn = document.querySelector('.carousel-btn.prev');
            this.nextBtn = document.querySelector('.carousel-btn.next');
            this.currentSlide = 0;
            this.totalSlides = this.slides.length;
            this.autoplayInterval = null;
            this.autoplayDelay = 5000; // 5 segundos

            this.init();
        }

        init() {
            // Configurar eventos
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.prevSlide());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.nextSlide());
            }

            // Configurar indicadores
            this.indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', () => this.goToSlide(index));
            });

            // Iniciar autoplay
            this.startAutoplay();

            // Pausar autoplay no hover
            const carousel = document.querySelector('.hero-carousel');
            if (carousel) {
                carousel.addEventListener('mouseenter', () => this.stopAutoplay());
                carousel.addEventListener('mouseleave', () => this.startAutoplay());
            }

            // Suporte a teclado
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') {
                    this.prevSlide();
                } else if (e.key === 'ArrowRight') {
                    this.nextSlide();
                }
            });
        }

        showSlide(index) {
            // Esconder todos os slides
            this.slides.forEach(slide => {
                slide.classList.remove('active');
            });
            this.indicators.forEach(indicator => {
                indicator.classList.remove('active');
            });

            // Mostrar slide atual
            this.slides[index].classList.add('active');
            this.indicators[index].classList.add('active');
            this.currentSlide = index;
        }

        nextSlide() {
            const nextIndex = (this.currentSlide + 1) % this.totalSlides;
            this.showSlide(nextIndex);
            this.resetAutoplay();
        }

        prevSlide() {
            const prevIndex = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
            this.showSlide(prevIndex);
            this.resetAutoplay();
        }

        goToSlide(index) {
            this.showSlide(index);
            this.resetAutoplay();
        }

        startAutoplay() {
            this.autoplayInterval = setInterval(() => {
                this.nextSlide();
            }, this.autoplayDelay);
        }

        stopAutoplay() {
            if (this.autoplayInterval) {
                clearInterval(this.autoplayInterval);
                this.autoplayInterval = null;
            }
        }

        resetAutoplay() {
            this.stopAutoplay();
            this.startAutoplay();
        }
    }

    // Inicializar carrossel se existir
    if (document.querySelector('.hero-carousel')) {
        new Carousel();
    }
});