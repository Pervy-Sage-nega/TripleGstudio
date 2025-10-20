// Registration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get form and fields
    const registerForm = document.getElementById('registerForm');
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const emailInput = document.getElementById('email');
    // const roleInput = document.getElementById('role'); // Not used in Site Manager registration
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const termsCheckbox = document.getElementById('terms');
    const successModal = document.getElementById('registrationSuccessModal');
    const goToLoginBtn = document.getElementById('goToLoginBtn');
    const passwordToggles = document.querySelectorAll('.password-toggle');
    const modalCloseBtn = document.querySelector('.modal-close');
    
    // Password strength meter elements
    const meterSections = document.querySelectorAll('.meter-section');
    const strengthText = document.querySelector('.strength-text');
    
    // Add event listeners
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('input', checkPasswordStrength);
    }
    
    if (passwordToggles) {
        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', togglePasswordVisibility);
        });
    }
    
    if (goToLoginBtn) {
        goToLoginBtn.addEventListener('click', goToLogin);
    }
    
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }
    
    // Click outside modal to close
    window.addEventListener('click', function(e) {
        if (e.target === successModal) {
            closeModal();
        }
    });
    
    // Handle registration form submission
    function handleRegistration(e) {
        e.preventDefault();
        
        // Get field values
        const firstName = firstNameInput.value.trim();
        const lastName = lastNameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const termsAccepted = termsCheckbox.checked;
        
        // Validate form
        if (!firstName || !lastName || !email || !password || !confirmPassword) {
            alert('Please fill out all required fields');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        
        if (!termsAccepted) {
            alert('Please accept the Terms of Service and Privacy Policy');
            return;
        }
        
        // Check password strength
        const strengthScore = calculatePasswordStrength(password);
        if (strengthScore < 2) {
            alert('Please choose a stronger password');
            return;
        }
        
        // If validation passes, submit the form
        registerForm.submit();
    }
    
    // Calculate password strength score (0-4)
    function calculatePasswordStrength(password) {
        let score = 0;
        // Length check
        if (password.length >= 8) {
            score++;
        }
        
        // Contains lowercase
        if (/[a-z]/.test(password)) {
            score++;
        }
        
        // Contains uppercase
        if (/[A-Z]/.test(password)) {
            score++;
        }
        
        // Contains number
        if (/[0-9]/.test(password)) {
            score++;
        }
        
        // Contains special character
        if (/[^a-zA-Z0-9]/.test(password)) {
            score++;
        }
        
        return Math.min(4, score);
    }
    
    // Update password strength meter
    function checkPasswordStrength() {
        const password = passwordInput.value;
        const score = calculatePasswordStrength(password);
        
        // Update visual meter
        meterSections.forEach((section, index) => {
            section.className = 'meter-section';
            
            if (password.length > 0 && index < score) {
                if (score === 1) {
                    section.classList.add('weak');
                } else if (score === 2) {
                    section.classList.add('fair');
                } else if (score === 3) {
                    section.classList.add('good');
                } else if (score === 4) {
                    section.classList.add('strong');
                }
            }
        });
        
        // Update text
        if (password.length === 0) {
            strengthText.textContent = 'Password strength';
        } else if (score === 1) {
            strengthText.textContent = 'Weak';
        } else if (score === 2) {
            strengthText.textContent = 'Fair';
        } else if (score === 3) {
            strengthText.textContent = 'Good';
        } else if (score === 4) {
            strengthText.textContent = 'Strong';
        }
    }
    
    // Toggle password visibility
    function togglePasswordVisibility() {
        const icon = this.querySelector('i');
        const inputField = this.parentElement.querySelector('input');
        
        if (inputField.type === 'password') {
            inputField.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            inputField.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
    
    // Show registration success modal
    function showSuccessModal() {
        successModal.classList.add('active');
    }
    
    // Close modal
    function closeModal() {
        successModal.classList.remove('active');
        registerForm.reset();
    }
    
    // Redirect to login page
    function goToLogin() {
        window.location.href = 'login.html';
    }
}); 