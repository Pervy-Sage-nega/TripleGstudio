document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu functionality
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');

  if (mobileMenuBtn && navLinks) {
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

  // Load saved user data from localStorage
  loadUserData();
  
  // Initialize toggle switches
  initializeToggleSwitches();

  // Profile Form handling
  const profileForm = document.getElementById('profileForm');
  const emailInput = document.getElementById('id_email');
  const emailError = document.getElementById('emailError');
  const phoneInput = document.getElementById('id_phone');
  const phoneError = document.getElementById('phoneError');

  if (profileForm) {
    // Email validation
    if (emailInput && emailError) {
      emailInput.addEventListener('input', function() {
        validateEmail(this);
      });
      
      emailInput.addEventListener('blur', function() {
        validateEmail(this);
      });
    }

    // Phone validation
    if (phoneInput && phoneError) {
      phoneInput.addEventListener('input', function() {
        validatePhone(this);
      });
      
      phoneInput.addEventListener('blur', function() {
        validatePhone(this);
      });
    }

    // Form submission - Let Django handle it, don't prevent default
    profileForm.addEventListener('submit', function(e) {
      // Validate all fields before submission
      let isValid = true;
      
      if (emailInput && !validateEmail(emailInput)) {
        isValid = false;
      }
      
      if (phoneInput && !validatePhone(phoneInput)) {
        isValid = false;
      }
      
      if (!isValid) {
        e.preventDefault(); // Only prevent if validation fails
        return false;
      }
      
      // If validation passes, let Django handle the form submission
      console.log('[DEBUG] Form validation passed, submitting to Django backend...');
    });
  }

  // Notifications Form handling
  const notificationsForm = document.getElementById('notificationsForm');
  const notificationsSuccess = document.getElementById('notificationsSuccess');

  if (notificationsForm) {
    notificationsForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Save notification preferences
      saveNotificationPreferences();
      
      // Show success message
      if (notificationsSuccess) {
        notificationsSuccess.style.display = 'flex';
        setTimeout(() => {
          notificationsSuccess.style.display = 'none';
        }, 3000);
      }
    });
  }

  // Security Form handling
  const securityForm = document.getElementById('securityForm');
  const currentPasswordInput = document.getElementById('currentPassword');
  const newPasswordInput = document.getElementById('newPassword');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  const passwordMatchError = document.getElementById('passwordMatchError');
  const strengthBar = document.getElementById('passwordStrength');
  const securitySuccess = document.getElementById('securitySuccess');

  if (securityForm) {
    // Password strength meter
    if (newPasswordInput && strengthBar) {
      newPasswordInput.addEventListener('input', function() {
        const password = this.value;
        updatePasswordStrength(password);
        
        // Check password match if confirm password has value
        if (confirmPasswordInput && confirmPasswordInput.value) {
          checkPasswordMatch();
        }
      });
    }

    // Password match validation
    if (confirmPasswordInput && passwordMatchError && newPasswordInput) {
      confirmPasswordInput.addEventListener('input', checkPasswordMatch);
      confirmPasswordInput.addEventListener('blur', checkPasswordMatch);
    }

    // Form submission
    securityForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Simple validation (in a real app you'd verify current password with backend)
      let isValid = true;
      
      if (!currentPasswordInput.value) {
        currentPasswordInput.setCustomValidity('Please enter your current password');
        isValid = false;
      } else {
        currentPasswordInput.setCustomValidity('');
      }
      
      if (newPasswordInput.value && !checkPasswordMatch()) {
        isValid = false;
      }
      
      if (isValid) {
        // In a real app, you would send data to server
        // For now, just show success message
        if (securitySuccess) {
          securitySuccess.style.display = 'flex';
          setTimeout(() => {
            securitySuccess.style.display = 'none';
          }, 3000);
          
          // Reset form
          securityForm.reset();
          strengthBar.style.width = '0';
        }
      }
    });
  }

  // Delete account modal
  const deleteAccountBtn = document.getElementById('deleteAccountBtn');
  const deleteModal = document.getElementById('deleteModal');
  const cancelDelete = document.getElementById('cancelDelete');
  const confirmDelete = document.getElementById('confirmDelete');
  const closeModal = document.querySelector('.close-modal');

  if (deleteAccountBtn && deleteModal) {
    deleteAccountBtn.addEventListener('click', function() {
      deleteModal.classList.add('active');
    });

    // Close modal functions
    const closeDeleteModal = function() {
      deleteModal.classList.remove('active');
    };

    if (cancelDelete) {
      cancelDelete.addEventListener('click', closeDeleteModal);
    }

    if (closeModal) {
      closeModal.addEventListener('click', closeDeleteModal);
    }

    // Outside click to close
    window.addEventListener('click', function(e) {
      if (e.target === deleteModal) {
        closeDeleteModal();
      }
    });

    // Confirm delete
    if (confirmDelete) {
      confirmDelete.addEventListener('click', function() {
        // In a real app, you would send delete request to server
        // For demo, just show alert and redirect
        alert('Account deletion request submitted. You will be logged out.');
        window.location.href = 'index.html';
      });
    }
  }

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function() {
      // In a real app, you would clear session data
      window.location.href = 'index.html';
    });
  }

  // Profile image upload - Using HTML label functionality
  console.log('[DEBUG] Profile upload using HTML label for attribute...');
  
  const profileImage = document.getElementById('profileImage');
  const fileInput = document.getElementById('id_profile_pic_debug');
  
  // Make the profile image clickable as additional option
  if (profileImage) {
    profileImage.addEventListener('click', function(e) {
      console.log('[DEBUG] Profile image clicked - triggering label click');
      const changePhotoBtn = document.getElementById('changePhotoBtn');
      if (changePhotoBtn) {
        changePhotoBtn.click();
      }
    });
    profileImage.style.cursor = 'pointer';
  }
  
  // Handle file selection and preview
  if (fileInput && profileImage) {
    fileInput.addEventListener('change', function(event) {
      const file = event.target.files[0];
      if (file) {
        console.log('[DEBUG] File selected:', file.name);
        const reader = new FileReader();
        reader.onload = function(e) {
          profileImage.src = e.target.result;
          console.log('[DEBUG] Profile image preview updated');
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Validation functions
  function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(input.value);
    
    if (!isValid) {
      input.setCustomValidity('Please enter a valid email address');
      emailError.style.display = 'block';
      return false;
    } else {
      input.setCustomValidity('');
      emailError.style.display = 'none';
      return true;
    }
  }

  function validatePhone(input) {
    const phoneRegex = /^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    const isValid = phoneRegex.test(input.value);
    
    if (!isValid) {
      input.setCustomValidity('Please enter a valid phone number');
      phoneError.style.display = 'block';
      return false;
    } else {
      input.setCustomValidity('');
      phoneError.style.display = 'none';
      return true;
    }
  }

  function checkPasswordMatch() {
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    if (newPassword !== confirmPassword) {
      confirmPasswordInput.setCustomValidity('Passwords do not match');
      passwordMatchError.style.display = 'block';
      return false;
    } else {
      confirmPasswordInput.setCustomValidity('');
      passwordMatchError.style.display = 'none';
      return true;
    }
  }

  function updatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 20;
    if (password.match(/[a-z]+/)) strength += 20;
    if (password.match(/[A-Z]+/)) strength += 20;
    if (password.match(/[0-9]+/)) strength += 20;
    if (password.match(/[^a-zA-Z0-9]+/)) strength += 20;
    
    strengthBar.style.width = strength + '%';
    
    if (strength < 40) {
      strengthBar.style.backgroundColor = '#F44336'; // Danger
    } else if (strength < 70) {
      strengthBar.style.backgroundColor = '#FF9800'; // Warning
    } else {
      strengthBar.style.backgroundColor = '#4CAF50'; // Success
    }
  }

  // Save data functions
  function saveProfileData() {
    const userData = {
      firstName: document.getElementById('id_first_name')?.value || '',
      lastName: document.getElementById('id_last_name')?.value || '',
      email: document.getElementById('id_email')?.value || '',
      phone: document.getElementById('id_phone')?.value || '',
    };
    
    localStorage.setItem('userData', JSON.stringify(userData));
    
    // Update display elements
    updateDisplayElements(userData);
  }

  function saveNotificationPreferences() {
    const notificationPrefs = {
      emailNotifications: document.getElementById('emailNotifications').checked,
      smsNotifications: document.getElementById('smsNotifications').checked,
      milestoneNotifications: document.getElementById('milestoneNotifications').checked,
      newsletterNotifications: document.getElementById('newsletterNotifications').checked,
      frequency: document.getElementById('notificationFrequency').value
    };
    
    localStorage.setItem('notificationPrefs', JSON.stringify(notificationPrefs));
  }

  // Load saved data from localStorage
  function loadUserData() {
    // Load profile data
    const savedUserData = localStorage.getItem('userData');
    if (savedUserData) {
      const userData = JSON.parse(savedUserData);
      
      if (document.getElementById('id_first_name')) document.getElementById('id_first_name').value = userData.firstName || '';
      if (document.getElementById('id_last_name')) document.getElementById('id_last_name').value = userData.lastName || '';
      if (document.getElementById('id_email')) document.getElementById('id_email').value = userData.email || '';
      if (document.getElementById('id_phone')) document.getElementById('id_phone').value = userData.phone || '';
      
      // Update display elements
      updateDisplayElements(userData);
    }
    
    // Load profile image
    const savedProfileImage = localStorage.getItem('userProfileImage');
    if (savedProfileImage && document.getElementById('profileImage')) {
      document.getElementById('profileImage').src = savedProfileImage;
    }
    
    // Load notification preferences
    const savedNotificationPrefs = localStorage.getItem('notificationPrefs');
    if (savedNotificationPrefs) {
      const prefs = JSON.parse(savedNotificationPrefs);
      
      if (document.getElementById('emailNotifications')) 
        document.getElementById('emailNotifications').checked = prefs.emailNotifications;
      if (document.getElementById('smsNotifications')) 
        document.getElementById('smsNotifications').checked = prefs.smsNotifications;
      if (document.getElementById('milestoneNotifications')) 
        document.getElementById('milestoneNotifications').checked = prefs.milestoneNotifications;
      if (document.getElementById('newsletterNotifications')) 
        document.getElementById('newsletterNotifications').checked = prefs.newsletterNotifications;
      if (document.getElementById('notificationFrequency')) 
        document.getElementById('notificationFrequency').value = prefs.frequency;
    }
  }

  function updateDisplayElements(userData) {
    // Update display name and email
    const displayName = document.getElementById('displayName');
    const displayEmail = document.getElementById('displayEmail');
    
    if (displayName && userData.firstName && userData.lastName) {
      displayName.textContent = userData.firstName + ' ' + userData.lastName;
    }
    
    if (displayEmail && userData.email) {
      displayEmail.textContent = userData.email;
    }
  }
  
  // Initialize toggle switches functionality
  function initializeToggleSwitches() {
    const toggleSwitches = document.querySelectorAll('.toggle-switch input[type="checkbox"]');
    
    toggleSwitches.forEach(toggle => {
      // Add click event listener
      toggle.addEventListener('change', function() {
        console.log(`[DEBUG] Toggle ${this.id} changed to: ${this.checked}`);
        
        // Add visual feedback
        const toggleContainer = this.closest('.toggle-container');
        if (toggleContainer) {
          if (this.checked) {
            toggleContainer.classList.add('toggle-active');
          } else {
            toggleContainer.classList.remove('toggle-active');
          }
        }
        
        // Save toggle state to localStorage
        saveToggleState(this.id, this.checked);
        
        // Show a brief feedback message
        showToggleFeedback(this);
      });
      
      // Load saved state
      const savedState = localStorage.getItem(`toggle_${toggle.id}`);
      if (savedState !== null) {
        toggle.checked = savedState === 'true';
      }
    });
  }
  
  function saveToggleState(toggleId, state) {
    localStorage.setItem(`toggle_${toggleId}`, state.toString());
  }
  
  function showToggleFeedback(toggle) {
    const container = toggle.closest('.toggle-container');
    if (container) {
      // Create temporary feedback element
      const feedback = document.createElement('div');
      feedback.className = 'toggle-feedback';
      feedback.textContent = toggle.checked ? '✓ Enabled' : '✗ Disabled';
      feedback.style.cssText = `
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
        background: ${toggle.checked ? '#4CAF50' : '#f44336'};
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
      `;
      
      container.style.position = 'relative';
      container.appendChild(feedback);
      
      // Animate in
      setTimeout(() => {
        feedback.style.opacity = '1';
      }, 10);
      
      // Remove after 2 seconds
      setTimeout(() => {
        feedback.style.opacity = '0';
        setTimeout(() => {
          if (feedback.parentNode) {
            feedback.parentNode.removeChild(feedback);
          }
        }, 300);
      }, 2000);
    }
  }
});
