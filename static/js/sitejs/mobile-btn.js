// Site Diary Menu Toggle Functionality - Mobile + Desktop (click-based dropdowns)
document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuBtn = document.getElementById("mobileMenuBtn") || document.querySelector(".mobile-menu-btn");
    const navLinks = document.getElementById("navLinks") || document.querySelector(".nav-links");

    if (mobileMenuBtn && navLinks) {
        // Reset previous event listeners
        const newBtn = mobileMenuBtn.cloneNode(true);
        mobileMenuBtn.parentNode.replaceChild(newBtn, mobileMenuBtn);

        // Toggle mobile menu
        newBtn.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            navLinks.classList.toggle("active");
            const icon = this.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-bars");
                icon.classList.toggle("fa-times");
            }
        });

        // Close menu when clicking outside
        document.addEventListener("click", function (event) {
            if (!event.target.closest(".navbar") && navLinks.classList.contains("active")) {
                navLinks.classList.remove("active");
                const icon = newBtn.querySelector("i");
                if (icon) {
                    icon.classList.add("fa-bars");
                    icon.classList.remove("fa-times");
                }
                // Close all dropdowns
                document.querySelectorAll('.dropdown.open').forEach(dd => dd.classList.remove('open'));
            }
        });

        // Dropdown setup (desktop + mobile → click only)
        function setupDropdowns() {
            document.querySelectorAll('.dropdown').forEach(function (dropdown) {
                const btn = dropdown.querySelector('.dropbtn');
                if (btn) {
                    btn.onclick = function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        // Close other dropdowns
                        document.querySelectorAll('.dropdown.open').forEach(dd => {
                            if (dd !== dropdown) dd.classList.remove('open');
                        });
                        dropdown.classList.toggle('open');
                    };
                }
            });
        }

        setupDropdowns();
        window.addEventListener('resize', setupDropdowns);
    } else {
        console.warn('Site Diary menu elements not found:', {
            mobileMenuBtn: !!mobileMenuBtn,
            navLinks: !!navLinks
        });
    }
});
