// Login JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get form and fields
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.querySelector('.password-toggle');
    const errorModal = document.getElementById('errorModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const modalCloseBtn = document.querySelector('.modal-close');
    
    // Add event listeners
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Add event listeners for all password toggle buttons
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', togglePasswordVisibility);
    });
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }
    
    // Click outside modal to close
    window.addEventListener('click', function(e) {
        if (e.target === errorModal) {
            closeModal();
        }
    });
    
    // Handle login form submission
    
    
    
    // Toggle password visibility
    function togglePasswordVisibility() {
        const icon = this.querySelector('i');
        const input = this.parentElement.querySelector('input[type="password"], input[type="text"]');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
    
    // Redirect functions based on user role
    function redirectToAdminDashboard() {
        window.location.href = 'adminusers.html';
    }
    
    function redirectToArchitectDashboard() {
        window.location.href = 'admindiary.html';
    }
    
    function redirectToClientDashboard() {
        window.location.href = 'adminclientproject.html';
    }
    
    // Show error modal for invalid credentials
    function showErrorModal() {
        errorModal.classList.add('active');
    }
    
    // Close modal
    function closeModal() {
        errorModal.classList.remove('active');
    }
}); 