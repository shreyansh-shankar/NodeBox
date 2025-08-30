const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
});

document.addEventListener("DOMContentLoaded", () => {
  const featureCards = document.querySelectorAll(".feature-card");

  const observer = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
          observer.unobserve(entry.target); // animate only once
        }
      });
    },
    { threshold: 0.2 }
  );

  featureCards.forEach(card => {
    card.classList.add("hidden"); // start hidden
    observer.observe(card);
  });
});

// Select all scroll-animated elements
const scrollElements = document.querySelectorAll('.section-title, .section-subtitle, .community-links');

const elementInView = (el, offset = 0) => {
  const elementTop = el.getBoundingClientRect().top;
  return (
    elementTop <= (window.innerHeight || document.documentElement.clientHeight) - offset
  );
};

const displayScrollElement = (element) => {
  element.classList.add('scroll-visible');
};

const hideScrollElement = (element) => {
  element.classList.remove('scroll-visible');
};

const handleScrollAnimation = () => {
  scrollElements.forEach((el) => {
    if (elementInView(el, 100)) {
      displayScrollElement(el);
    } else {
      hideScrollElement(el);
    }
  })
};

window.addEventListener('scroll', () => {
  handleScrollAnimation();
});

// Trigger once on page load
handleScrollAnimation();

window.addEventListener('scroll', handleScrollAnimation);