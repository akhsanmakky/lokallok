document.addEventListener('DOMContentLoaded', () => {
    // Initialize AOS animation library
    AOS.init({
        once: true,
        easing: 'ease-in-out',
        duration: 800,
    });

    // Navbar toggle logic
    const showNavbarBtn = document.getElementById('showNavbarBtn');
    const navbar = document.querySelector('nav.navbar'); // sesuaikan selector navbar

    function toggleNavbarVisibility() {
        if (navbar.classList.contains('d-none') || navbar.style.display === 'none') {
            showNavbarBtn.style.display = 'block';
        } else {
            showNavbarBtn.style.display = 'none';
        }
    }
    toggleNavbarVisibility();

    showNavbarBtn.addEventListener('click', () => {
        navbar.style.display = 'block';
        showNavbarBtn.style.display = 'none';
    });

    // Back to Top button
    const backToTopBtn = document.getElementById('backToTopBtn');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Smooth scrolling for anchor links with .btn-scroll class
    document.querySelectorAll('a.btn-scroll[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
