const registerButton = document.getElementById('register');
const loginButton = document.getElementById('login');       
const container = document.getElementById('container');

registerButton.addEventListener('click', () => {
container.classList.add("right-panel-active");
});

loginButton.addEventListener('click', () => {
container.classList.remove("right-panel-active");
 });

 // Mobile navigation support
 const loginToRegisterBtn = document.getElementById('loginToRegisterBtn');
 const registerToLoginBtn = document.getElementById('registerToLoginBtn');
 
 if (loginToRegisterBtn) {
   loginToRegisterBtn.addEventListener('click', () => {
     container.classList.add("right-panel-active");
   });
 }
 
 if (registerToLoginBtn) {
   registerToLoginBtn.addEventListener('click', () => {
     container.classList.remove("right-panel-active");
   });
 }
 
 // Show/hide the appropriate mobile toggle button based on current state
 function updateMobileToggleVisibility() {
   const loginToggle = document.querySelector('.login-toggle');
   const registerToggle = document.querySelector('.register-toggle');
   
   if (container.classList.contains('right-panel-active')) {
     if (loginToggle) loginToggle.style.display = 'none';
     if (registerToggle) registerToggle.style.display = 'flex';
   } else {
     if (loginToggle) loginToggle.style.display = 'flex';
     if (registerToggle) registerToggle.style.display = 'none';
   }
 }
 
 // Initial call to set visibility
 document.addEventListener('DOMContentLoaded', updateMobileToggleVisibility);
 
 // Update visibility when switching forms
 registerButton.addEventListener('click', updateMobileToggleVisibility);
 loginButton.addEventListener('click', updateMobileToggleVisibility);
 if (loginToRegisterBtn) {
   loginToRegisterBtn.addEventListener('click', updateMobileToggleVisibility);
 }
 if (registerToLoginBtn) {
   registerToLoginBtn.addEventListener('click', updateMobileToggleVisibility);
 }

// Password visibility toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Login password toggle
    const loginPasswordToggle = document.getElementById('loginPasswordToggle');
    const loginPasswordInput = document.getElementById('login-password');
    
    if (loginPasswordToggle && loginPasswordInput) {
        loginPasswordToggle.addEventListener('click', function() {
            const type = loginPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            loginPasswordInput.setAttribute('type', type);
            
            if (type === 'text') {
                loginPasswordToggle.classList.remove('fa-eye');
                loginPasswordToggle.classList.add('fa-eye-slash');
            } else {
                loginPasswordToggle.classList.remove('fa-eye-slash');
                loginPasswordToggle.classList.add('fa-eye');
            }
        });
    }
    
    // Register password toggle
    const registerPasswordToggle = document.getElementById('registerPasswordToggle');
    const registerPasswordInput = document.getElementById('register-password');
    
    if (registerPasswordToggle && registerPasswordInput) {
        registerPasswordToggle.addEventListener('click', function() {
            const type = registerPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            registerPasswordInput.setAttribute('type', type);
            
            if (type === 'text') {
                registerPasswordToggle.classList.remove('fa-eye');
                registerPasswordToggle.classList.add('fa-eye-slash');
            } else {
                registerPasswordToggle.classList.remove('fa-eye-slash');
                registerPasswordToggle.classList.add('fa-eye');
            }
        });
    }
    
    // Form validation
    const loginForm = document.querySelector('.login-container form');
    const loginError = document.getElementById('loginError');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value;
            
            // Clear previous errors
            hideError();
            
            // Basic validation
            if (!username) {
                showError('Please enter your email or username');
                e.preventDefault();
                return;
            }
            
            if (!password) {
                showError('Please enter your password');
                e.preventDefault();
                return;
            }
            
            if (password.length < 6) {
                showError('Password must be at least 6 characters long');
                e.preventDefault();
                return;
            }
        });
    }
    
    function showError(message) {
        if (loginError) {
            loginError.textContent = message;
            loginError.style.display = 'block';
        }
    }
    
    function hideError() {
        if (loginError) {
            loginError.style.display = 'none';
        }
    }
});

// --- Modal Logic ---
document.addEventListener('DOMContentLoaded', function() {
    const modalOverlay = document.getElementById('messageModal');
    if (!modalOverlay) return;

    const modalContent = modalOverlay.querySelector('.modal-content');
    const closeButton = modalOverlay.querySelector('.modal-close');

    // Function to show the modal
    function showModal() {
        modalOverlay.style.display = 'flex';
        setTimeout(() => {
            modalOverlay.style.opacity = '1';
            modalContent.style.transform = 'translateY(0)';
        }, 10);
    }

    // Function to hide the modal
    function hideModal() {
        modalOverlay.style.opacity = '0';
        modalContent.style.transform = 'translateY(-50px)';
        setTimeout(() => {
            modalOverlay.style.display = 'none';
        }, 300);
    }

    // Show the modal immediately if it exists in the DOM
    showModal();

    // Event listeners to close the modal
    closeButton.addEventListener('click', hideModal);
    modalOverlay.addEventListener('click', function(event) {
        if (event.target === modalOverlay) {
            hideModal();
        }
    });
});