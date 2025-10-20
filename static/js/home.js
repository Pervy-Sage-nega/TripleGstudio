

document.addEventListener("DOMContentLoaded", function () {
    const recentProjects = document.getElementById("recentProjects");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const homeSection = document.getElementById("homeSection");
    const mainImage = document.getElementById("mainImage");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const navLinks = document.getElementById("navLinks");
    const images = [...recentProjects.getElementsByTagName("img")];
  
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
  
    // Mobile menu toggle
    mobileMenuBtn.addEventListener("click", function () {
      navLinks.classList.toggle("active");
      this.querySelector("i").classList.toggle("fa-bars");
      this.querySelector("i").classList.toggle("fa-times");
    });

    // Close mobile menu when clicking outside
    document.addEventListener("click", function (event) {
      if (!event.target.closest(".navbar") && navLinks.classList.contains("active")) {
        navLinks.classList.remove("active");
        mobileMenuBtn.querySelector("i").classList.add("fa-bars");
        mobileMenuBtn.querySelector("i").classList.remove("fa-times");
      }
    });
  
    // Function for ultra-smooth scrolling
    function smoothScroll(direction) {
      if (!recentProjects) return;
      
      // Recalculate dimensions each time
      const imgWidth = images.length > 0 ? images[0].offsetWidth + 10 : 160;
      const maxScroll = recentProjects.scrollWidth - recentProjects.clientWidth;
      
      let start = recentProjects.scrollLeft;
      let end = direction === "prev" ? start - imgWidth : start + imgWidth;
  
      // Prevent over-scrolling
      end = Math.max(0, Math.min(end, maxScroll));
      
      // If no scroll needed, return
      if (start === end) return;
  
      let startTime = null;
  
      function scrollAnimation(timestamp) {
        if (!startTime) startTime = timestamp;
        let progress = timestamp - startTime;
        let ease = Math.min(progress / 150, 1); // 150ms smooth transition
  
        recentProjects.scrollLeft = start + (end - start) * ease;
  
        if (ease < 1) {
          requestAnimationFrame(scrollAnimation);
        }
      }
  
      requestAnimationFrame(scrollAnimation);
    }
  
    // Previous Button: Smooth Scroll Left
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        smoothScroll("prev");
      });
    }
    
    // Next Button: Smooth Scroll Right
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        smoothScroll("next");
      });
    }
  
    // Track current active image index
    let currentImageIndex = 0;
    
    // Function to change main image and background with directional animation
    window.changeMainImage = function (imageSrc, clickedElement) {
      // Handle both Django media URLs and static image paths
      let imagePath;
      if (imageSrc.startsWith('/media/') || imageSrc.startsWith('/static/') || imageSrc.startsWith('http')) {
        // Django URL - use as is
        imagePath = imageSrc;
      } else if (imageSrc.includes("/images")) {
        // Static path with /images - use as is
        imagePath = imageSrc;
      } else {
        // Legacy path - add ./images/ prefix
        imagePath = "./images/" + imageSrc;
      }

      // Determine slide direction based on clicked image position
      let slideDirection = 'right'; // default
      if (clickedElement) {
        const clickedIndex = Array.from(images).indexOf(clickedElement);
        if (clickedIndex !== -1) {
          slideDirection = clickedIndex < currentImageIndex ? 'left' : 'right';
          currentImageIndex = clickedIndex;
        }
      }

      // Main image fades out smoothly
      mainImage.style.transition = "opacity 0.6s cubic-bezier(0.4, 0.0, 0.2, 1)";
      mainImage.style.opacity = "0";

      // Background slides directionally with more visible movement
      homeSection.style.transition = "background-position 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)";
      const slideDistance = slideDirection === 'left' ? '150% center' : '-50% center';
      homeSection.style.backgroundPosition = slideDistance;

      setTimeout(() => {
        // Change background image and position it off-screen in the slide direction
        homeSection.style.backgroundImage = `url('${imagePath}')`;
        mainImage.src = imagePath;
        
        // Position new background off-screen based on slide direction
        const offScreenPosition = slideDirection === 'left' ? '-100% center' : '200% center';
        homeSection.style.backgroundPosition = offScreenPosition;
        
        // Slide new background from off-screen to center
        setTimeout(() => {
          homeSection.style.transition = "background-position 1.0s cubic-bezier(0.16, 1, 0.3, 1)";
          homeSection.style.backgroundPosition = 'center center';
          mainImage.style.transition = "opacity 0.6s cubic-bezier(0.0, 0.0, 0.2, 1)";
          mainImage.style.opacity = "1";
        }, 50);
      }, 300);
    };

    // Clicking an image updates the main image with directional animation
    images.forEach((img, index) => {
      img.addEventListener("click", function () {
        changeMainImage(this.src, this);
      });
      
      // Set initial active image
      if (index === 0) {
        currentImageIndex = 0;
      }
    });

    // Button hover effect
    let btns = document.querySelectorAll("a[data-color]");
    btns.forEach((btn) => {
      btn.onmousemove = function (e) {
        let x = e.pageX - btn.offsetLeft;
        let y = e.pageY - btn.offsetTop;

        btn.style.setProperty("--x", x + "px");
        btn.style.setProperty("--y", y + "px");
        btn.style.setProperty("--clr", btn.getAttribute("data-color"));
      };
    });
  
    // Handle window resize
    window.addEventListener('resize', function() {
      // Update dimensions when window is resized
      if (images.length > 0) {
        const newImgWidth = images[0].clientWidth + 10;
        // Update max scroll limit
        const newMaxScroll = recentProjects.scrollWidth - recentProjects.clientWidth;
      }
    });

    // Homepage project filtering functionality
    const yearFilter = document.getElementById('year-filter');
    const categoryFilter = document.getElementById('category-filter');
    const projectCards = document.querySelectorAll('.project-card');

    // Function to filter projects
    function filterProjects() {
      const selectedYear = yearFilter ? yearFilter.value : 'all';
      const selectedCategory = categoryFilter ? categoryFilter.value : 'all';

      projectCards.forEach(card => {
        const cardYear = card.getAttribute('data-year');
        const cardCategory = card.getAttribute('data-category');
        const isFeatured = card.querySelector('.featured-badge') !== null;

        let showCard = true;

        // Filter by year
        if (selectedYear !== 'all' && cardYear !== selectedYear) {
          showCard = false;
        }

        // Filter by category
        if (selectedCategory !== 'all') {
          if (selectedCategory === 'featured' && !isFeatured) {
            showCard = false;
          } else if (selectedCategory !== 'featured' && cardCategory !== selectedCategory) {
            showCard = false;
          }
        }

        // Show/hide card with animation
        if (showCard) {
          card.style.display = 'block';
          card.style.opacity = '0';
          card.style.transform = 'translateY(20px)';
          
          setTimeout(() => {
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
          card.style.opacity = '0';
          card.style.transform = 'translateY(-20px)';
          
          setTimeout(() => {
            card.style.display = 'none';
          }, 300);
        }
      });

      // Update the "ALL" heading to show current filter
      const filterHeading = document.querySelector('.filter-container h2');
      if (filterHeading) {
        let headingText = 'ALL';
        if (selectedYear !== 'all' || selectedCategory !== 'all') {
          const yearText = selectedYear !== 'all' ? selectedYear : '';
          const categoryText = selectedCategory !== 'all' ? 
            (selectedCategory === 'featured' ? 'FEATURED' : selectedCategory.toUpperCase()) : '';
          headingText = [yearText, categoryText].filter(Boolean).join(' ') || 'FILTERED';
        }
        filterHeading.textContent = headingText;
      }
    }

    // Add event listeners to filters
    if (yearFilter) {
      yearFilter.addEventListener('change', filterProjects);
    }

    if (categoryFilter) {
      categoryFilter.addEventListener('change', filterProjects);
    }
  
    // Add smooth scrolling behavior for vertical page scrolling
    // Current scroll position
    let currentScroll = window.pageYOffset;
    // Target scroll position
    let targetScroll = currentScroll;
    // Flag to track if animation is running
    let ticking = false;
    
    // Smooth scroll animation function
    function smoothPageScroll() {
      // Calculate distance between current and target
      const diff = targetScroll - currentScroll;
      // If difference is very small, snap to target
      if (Math.abs(diff) < 0.5) {
        currentScroll = targetScroll;
        window.scrollTo(0, currentScroll);
        ticking = false;
        return;
      }
      
      // Calculate step with easing
      currentScroll += diff * 0.1;
      
      // Update scroll position
      window.scrollTo(0, currentScroll);
      
      // Continue animation
      if (currentScroll !== targetScroll) {
        requestAnimationFrame(smoothPageScroll);
      } else {
        ticking = false;
      }
    }
    
    // Handle wheel event
    function handleWheel(e) {
      e.preventDefault();
      
      // Update target scroll position
      targetScroll = Math.max(0,
        Math.min(
          document.body.scrollHeight - window.innerHeight,
          targetScroll + e.deltaY
        )
      );
      
      // Start animation if not already running
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(smoothPageScroll);
      }
    }
    
    // Add event listener for wheel event
    window.addEventListener('wheel', handleWheel, { passive: false });
    
    // Handle keyboard navigation
    window.addEventListener('keydown', function(e) {
      let scrollAmount = 0;
      
      // Arrow keys, Page Up/Down, Home/End
      switch(e.key) {
        case 'ArrowDown':
          scrollAmount = 40;
          break;
        case 'ArrowUp':
          scrollAmount = -40;
          break;
        case 'PageDown':
          scrollAmount = window.innerHeight * 0.9;
          break;
        case 'PageUp':
          scrollAmount = -window.innerHeight * 0.9;
          break;
        case 'Home':
          targetScroll = 0;
          break;
        case 'End':
          targetScroll = document.body.scrollHeight - window.innerHeight;
          break;
        default:
          return; // Exit for other keys
      }
      
      if (scrollAmount !== 0) {
        e.preventDefault();
        // Update target scroll position
        targetScroll = Math.max(0,
          Math.min(
            document.body.scrollHeight - window.innerHeight,
            targetScroll + scrollAmount
          )
        );
      }
      
      // Start animation if not already running
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(smoothPageScroll);
      }
    });
    
  });
  


  