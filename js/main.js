// Axiom LLC - Main JavaScript

(function() {
    'use strict';
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu-container');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('nav-menu-opened');
            const isExpanded = navMenu.classList.contains('nav-menu-opened');
            menuToggle.setAttribute('aria-expanded', isExpanded);
        });
    }
    
    // Close mobile menu on link click
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navMenu && navMenu.classList.contains('nav-menu-opened')) {
                navMenu.classList.remove('nav-menu-opened');
                if (menuToggle) {
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 70; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Update copyright year
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
    
    // Active nav link on scroll
    const sections = document.querySelectorAll('section[id]');
    
    function highlightNavOnScroll() {
        const scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    window.addEventListener('scroll', highlightNavOnScroll);
    
    // Add active class CSS
    const style = document.createElement('style');
    style.textContent = `
        .nav-link.active {
            color: var(--color-text-headings);
            background-color: rgba(var(--color-primary-rgb), 0.1);
        }
    `;
    document.head.appendChild(style);
})();
