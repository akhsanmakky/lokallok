// Inisialisasi AOS
AOS.init({
  duration: 700,
  once: true,
});

// Tombol Back to Top
const backToTopBtn = document.getElementById('backToTopBtn');
window.addEventListener('scroll', () => {
  if (window.scrollY > 150) {
    backToTopBtn.style.display = 'block';
  } else {
    backToTopBtn.style.display = 'none';
  }
});

backToTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Toggle Navbar (contoh, bisa dikembangkan)
const toggleNavbarBtn = document.getElementById('toggleNavbarBtn');
const navbar = document.querySelector('.navbar');
const showNavbarBtn = document.getElementById('showNavbarBtn');

toggleNavbarBtn.addEventListener('click', () => {
  if (navbar.style.display !== 'none') {
    navbar.style.display = 'none';
    showNavbarBtn.style.display = 'block';
  } else {
    navbar.style.display = 'flex';
    showNavbarBtn.style.display = 'none';
  }
});

showNavbarBtn.addEventListener('click', () => {
  navbar.style.display = 'flex';
  showNavbarBtn.style.display = 'none';
});
