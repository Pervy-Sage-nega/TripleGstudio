document.addEventListener('DOMContentLoaded', function() {
  // Apply hover effects to form submit buttons
  const formButtons = document.querySelectorAll('.contact-form .form-actions button[type="submit"]');
  
  formButtons.forEach(button => {
    button.addEventListener('mousemove', function(e) {
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      this.style.setProperty('--x', `${x}px`);
      this.style.setProperty('--y', `${y}px`);
    });
    
    // Wrap text in span if not already
    if (!button.querySelector('span')) {
      const text = button.textContent;
      button.innerHTML = `<span>${text}</span>`;
    }
  });
}); 