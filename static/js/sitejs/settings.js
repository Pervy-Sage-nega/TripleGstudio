
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if(mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Settings menu navigation
    const menuItems = document.querySelectorAll('.settings-menu-item');
    const settingsSections = document.querySelectorAll('.settings-section');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all menu items
            menuItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Hide all sections
            settingsSections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Show selected section
            const sectionId = this.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Email validation
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('emailError');
    
    if(emailInput && emailError) {
        emailInput.addEventListener('input', function() {
            validateEmail(this);
        });
        
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
    }
    
    function validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if(!emailRegex.test(input.value)) {
            input.setCustomValidity('Invalid email format');
            emailError.style.display = 'block';
        } else {
            input.setCustomValidity('');
            emailError.style.display = 'none';
        }
    }
    
    // Phone validation
    const phoneInput = document.getElementById('phone');
    const phoneError = document.getElementById('phoneError');
    
    if(phoneInput && phoneError) {
        phoneInput.addEventListener('input', function() {
            validatePhone(this);
        });
        
        phoneInput.addEventListener('blur', function() {
            validatePhone(this);
        });
    }
    
    function validatePhone(input) {
        const phoneRegex = /^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        if(!phoneRegex.test(input.value)) {
            input.setCustomValidity('Invalid phone format');
            phoneError.style.display = 'block';
        } else {
            input.setCustomValidity('');
            phoneError.style.display = 'none';
        }
    }
    
    // Password strength meter
    const passwordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthBar = document.getElementById('passwordStrength');
    const passwordMatchError = document.getElementById('passwordMatchError');
    
    if(passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            
            if(password.length >= 8) strength += 20;
            if(password.match(/[a-z]+/)) strength += 20;
            if(password.match(/[A-Z]+/)) strength += 20;
            if(password.match(/[0-9]+/)) strength += 20;
            if(password.match(/[^a-zA-Z0-9]+/)) strength += 20;
            
            strengthBar.style.width = strength + '%';
            
            if(strength < 40) {
                strengthBar.style.backgroundColor = '#f44336';
            } else if(strength < 70) {
                strengthBar.style.backgroundColor = '#ff9800';
            } else {
                strengthBar.style.backgroundColor = '#4caf50';
            }
            
            // Check password match if confirm password has value
            if(confirmPasswordInput && confirmPasswordInput.value) {
                checkPasswordMatch();
            }
        });
    }
    
    // Password match validation
    if(confirmPasswordInput && passwordMatchError) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
        confirmPasswordInput.addEventListener('blur', checkPasswordMatch);
    }
    
    function checkPasswordMatch() {
        if(passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('Passwords do not match');
            passwordMatchError.style.display = 'block';
        } else {
            confirmPasswordInput.setCustomValidity('');
            passwordMatchError.style.display = 'none';
        }
    }
    
    // Profile image upload with validation
    const avatarUpload = document.getElementById('avatar-upload');
    const profileImage = document.getElementById('profileImage');
    
    if(avatarUpload && profileImage) {
        avatarUpload.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if(file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
                    this.value = '';
                    return;
                }
                
                // Validate file size (max 5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB in bytes
                if (file.size > maxSize) {
                    alert('Image file size must be less than 5MB');
                    this.value = '';
                    return;
                }
                
                // Show loading state
                profileImage.style.opacity = '0.5';
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    profileImage.src = e.target.result;
                    profileImage.style.opacity = '1';
                    
                    // Show success message
                    const uploadBtn = document.querySelector('.upload-btn');
                    if (uploadBtn) {
                        const originalText = uploadBtn.innerHTML;
                        uploadBtn.innerHTML = '<i class="fas fa-check"></i> Image Selected';
                        uploadBtn.style.backgroundColor = '#28a745';
                        
                        // Reset button after 2 seconds
                        setTimeout(() => {
                            uploadBtn.innerHTML = originalText;
                            uploadBtn.style.backgroundColor = '';
                        }, 2000);
                    }
                };
                
                reader.onerror = function() {
                    profileImage.style.opacity = '1';
                    alert('Error reading the image file. Please try again.');
                    event.target.value = '';
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Form reset functionality
    const resetButtons = document.querySelectorAll('.btn-secondary');
    
    resetButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Find the parent form
            const form = this.closest('form');
            
            if(form) {
                form.reset();
            } else {
                // If no form, just reload the section
                location.reload();
            }
        });
    });
    
    // Handle specific form submissions instead of generic .btn-primary
    // This prevents conflicts between different save buttons
    
    // Add form submit listener for debugging
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            console.log('DEBUG: Form submit event triggered');
            console.log('DEBUG: Form action:', this.action);
            console.log('DEBUG: Form method:', this.method);
            console.log('DEBUG: Form data:', new FormData(this));
        });
    }
    
    // Direct button click handler for profile form
    const saveAccountBtn = document.getElementById('saveAccount');
    if (saveAccountBtn) {
        saveAccountBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default to handle validation first
            console.log('DEBUG: Direct save account button clicked');
            
            const form = document.getElementById('profileForm');
            if (form) {
                // Validate form fields
                const firstName = document.getElementById('firstName');
                const lastName = document.getElementById('lastName');
                const email = document.getElementById('email');
                
                if (firstName && lastName && email) {
                    if (!firstName.value.trim() || !lastName.value.trim() || !email.value.trim()) {
                        alert('Please fill in all required fields (First Name, Last Name, Email)');
                        return;
                    }
                    
                    // Email validation
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(email.value.trim())) {
                        alert('Please enter a valid email address');
                        return;
                    }
                }
                
                // Add loading state to button
                const originalText = this.textContent;
                this.textContent = 'Saving...';
                this.disabled = true;
                
                console.log('DEBUG: Manually submitting form');
                form.submit();
            }
        });
    }
    
    // Two-factor authentication toggle
    const twoFactorToggle = document.getElementById('twoFactorToggle');
    
    if(twoFactorToggle) {
        twoFactorToggle.addEventListener('change', function() {
            if(this.checked) {
                // Simulate 2FA setup - in a real app, this would open a modal or redirect
                alert('Two-factor authentication setup would be initiated here.');
            }
        });
    }
    
    // Data export functionality (for demonstration)
    const exportButtons = document.querySelectorAll('.backup-btn-download');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const exportType = this.textContent.trim() || 'Data';
            const backupSuccess = document.getElementById('backupSuccess');
            
            if(backupSuccess) {
                backupSuccess.innerHTML = `<i class="fas fa-check-circle"></i> ${exportType} export has been initiated successfully.`;
                backupSuccess.style.display = 'block';
                
                setTimeout(() => {
                    backupSuccess.style.display = 'none';
                }, 3000);
            }
        });
    });
    
    // Set the first menu item as active by default
    if(menuItems.length > 0) {
        menuItems[0].click();
    }
    
    // Custom scrollbar style (preserved from original)
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
    
    // Mobile menu functionality (again, as it appeared twice in original code)
    if(mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
}); 