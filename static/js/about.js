document.addEventListener("DOMContentLoaded", function() {
  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navLinks = document.getElementById("navLinks");
  
  // Apply custom scrollbar styles
  const style = document.createElement('style');
  style.textContent = `
    /* Webkit browsers (Chrome, Safari, newer versions of Opera) */
    ::-webkit-scrollbar {
      width: 5px;
      background-color: transparent;
    }
    
    ::-webkit-scrollbar-track {
      background-color: transparent;
      border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
      background-color: rgba(255, 255, 255, 0);
      border-radius: 5px;
      border: 2px solid transparent;
      background-clip: content-box;
      transition: background-color 0.3s;
    }
    
    ::-webkit-scrollbar-thumb:hover {
      background-color: rgba(255, 255, 255, 0);
    }
    
    /* For Firefox */
    * {
      scrollbar-width: thin;
      scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
    }
    
    /* Hide scrollbar when not scrolling (optional) */
    body:not(:hover)::-webkit-scrollbar-thumb {
      background-color: rgba(255, 255, 255, 0);
    }
  `;
    document.head.appendChild(style);
  
   
   // ===== SMOOTH SCROLLING CORE IMPLEMENTATION =====
let isScrolling = false;
let lastScrollTime = 0;
const SCROLL_THROTTLE_TIME = 100;

// Unified easing function
function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}

function smoothScrollTo(targetPosition, duration = 10000) {
    if (isScrolling) return;
    isScrolling = true;
    
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const startTime = performance.now();

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeInOutCubic(progress);
        
        window.scrollTo(0, startPosition + distance * easedProgress);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isScrolling = false;
        }
    }
    
    requestAnimationFrame(animate);
}

// ===== EVENT HANDLERS =====
function handleWheel(e) {
    if (Date.now() - lastScrollTime < SCROLL_THROTTLE_TIME) return;
    lastScrollTime = Date.now();

    if (Math.abs(e.deltaY) < 20) return;
    
    e.preventDefault();
    
    const direction = Math.sign(e.deltaY);
    const pageHeight = window.innerHeight;
    const targetPosition = Math.max(0, 
        Math.min(document.documentElement.scrollHeight - pageHeight,
        window.pageYOffset + (direction * pageHeight))
    );
    
    smoothScrollTo(targetPosition, 800);
}

function handleKeyboard(e) {
    let targetPosition;
    const currentPosition = window.pageYOffset;
    const pageHeight = window.innerHeight;
    const docHeight = document.documentElement.scrollHeight;
    
    switch(e.key) {
        case 'ArrowDown':
            targetPosition = currentPosition + pageHeight * 0.25;
            break;
        case 'ArrowUp':
            targetPosition = currentPosition - pageHeight * 0.25;
            break;
        case 'PageDown':
            targetPosition = currentPosition + pageHeight * 0.9;
            break;
        case 'PageUp':
            targetPosition = currentPosition - pageHeight * 0.9;
            break;
        case 'Home':
            targetPosition = 0;
            break;
        case 'End':
            targetPosition = docHeight - pageHeight;
            break;
        default:
            return;
    }
    
    e.preventDefault();
    targetPosition = Math.max(0, Math.min(docHeight - pageHeight, targetPosition));
    smoothScrollTo(targetPosition, 700);
}

// ===== ANCHOR LINK HANDLING =====
function handleAnchorClick(e) {
    e.preventDefault();
    const targetId = this.hash;
    if (!targetId || targetId === '#') return;
    
    const targetElement = document.querySelector(targetId);
    if (!targetElement) return;

    const navbar = document.querySelector('.navbar');
    const navbarHeight = navbar ? navbar.offsetHeight : 0;
    const targetPosition = targetElement.getBoundingClientRect().top + 
                         window.pageYOffset - 
                         (navbarHeight + 20); // 20px buffer
    
    smoothScrollTo(targetPosition, 1000);
    
    // Update URL without jumping
    history.replaceState(null, null, targetId);
}

// ===== INITIALIZATION =====
function initSmoothScroll() {
    // Event Listeners
    window.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('keydown', handleKeyboard);
    window.addEventListener('scrollend', () => isScrolling = false);
    
    // Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', handleAnchorClick);
    });

    // Mobile Menu Integration
    const mobileMenu = document.getElementById('navLinks');
    if (mobileMenu) {
        document.addEventListener('click', (e) => {
            if (mobileMenu.classList.contains('active') && 
                !e.target.closest('.navbar')) {
                mobileMenu.classList.remove('active');
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", initSmoothScroll);

  mobileMenuBtn.addEventListener("click", function() {
    navLinks.classList.toggle("active");
    this.querySelector("i").classList.toggle("fa-bars");
    this.querySelector("i").classList.toggle("fa-times");
  });
  
  // Close mobile menu when clicking outside
  document.addEventListener("click", function(event) {
    if (!event.target.closest(".navbar") && navLinks.classList.contains("active")) {
      navLinks.classList.remove("active");
      mobileMenuBtn.querySelector("i").classList.add("fa-bars");
      mobileMenuBtn.querySelector("i").classList.remove("fa-times");
    }
  });
  
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        const targetPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = targetPosition + window.pageYOffset - navbarHeight;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Reveal animations on scroll
  const revealElements = document.querySelectorAll('.reveal');
  
  function checkReveal() {
    const windowHeight = window.innerHeight;
    const revealPoint = 150;
    
    revealElements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top;
      
      if (elementTop < windowHeight - revealPoint) {
        element.classList.add('active');
      }
    });
  }
  
  // Check on initial load
  checkReveal();
  
  // Check on scroll
  window.addEventListener('scroll', checkReveal);
  
  // Team member bio toggle
  const readMoreBtns = document.querySelectorAll('.read-more');
  
  readMoreBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const teamMember = this.closest('.team-member');
      const memberBio = teamMember.querySelector('.member-bio');
      
      teamMember.classList.toggle('active');
      
      if (teamMember.classList.contains('active')) {
        this.textContent = 'Read Less';
        memberBio.style.maxHeight = memberBio.scrollHeight + 'px';
      } else {
        this.textContent = 'Read More';
        memberBio.style.maxHeight = '0';
      }
    });
  });
  
  // Sticky navbar
  const navbar = document.getElementById('navbar');
  const sticky = navbar.offsetTop;
  
  function stickyNavbar() {
    if (window.pageYOffset > sticky) {
      navbar.classList.add('sticky-navbar');
    } else {
      navbar.classList.remove('sticky-navbar');
    }
  }
  
  window.addEventListener('scroll', stickyNavbar);
  
  // Button hover effect
  let btns = document.querySelectorAll("a[data-color]");
  btns.forEach((btn) => {
    btn.onmousemove = function(e) {
      let x = e.pageX - btn.offsetLeft;
      let y = e.pageY - btn.offsetTop;
      
      btn.style.setProperty("--x", x + "px");
      btn.style.setProperty("--y", y + "px");
      btn.style.setProperty("--clr", btn.getAttribute("data-color"));
    };
  });
});
