document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Navbar show/hide toggle
    const toggleNavbarBtn = document.getElementById('toggleNavbarBtn');
    if (toggleNavbarBtn) {
        toggleNavbarBtn.addEventListener('click', function () {
            navbar.classList.toggle('navbar-hidden');

            // Ganti ikon tombol sesuai status
            const icon = toggleNavbarBtn.querySelector('i');
            if (navbar.classList.contains('navbar-hidden')) {
                icon.classList.remove('bi-eye-slash-fill');
                icon.classList.add('bi-eye-fill');
                toggleNavbarBtn.title = 'Tampilkan Navbar';
            } else {
                icon.classList.remove('bi-eye-fill');
                icon.classList.add('bi-eye-slash-fill');
                toggleNavbarBtn.title = 'Sembunyikan Navbar';
            }
        });
    }
});
