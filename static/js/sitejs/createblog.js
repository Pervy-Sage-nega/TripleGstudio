/**
 * Triple G BuildHub - Blog Creation JavaScript
 * Handles blog form functionality including:
 * - Rich text editor (with inline image uploads)
 * - Image upload and preview
 * - Live content preview
 * - Form submission and validation
 * - Draft saving (localStorage)
 */

document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initRichTextEditor();
    initImageUpload();
    initFormPreview();
    initFormActions();
    loadSavedDraft();
});

/**
 * Initialize mobile menu toggle
 */
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (!mobileMenuBtn || !navLinks) {
        return;
    }

    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.navbar') && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        }
    });
}

/**
 * Initialize rich text editor functionality
 */
function initRichTextEditor() {
    const toolbarButtons = document.querySelectorAll('.toolbar-btn');
    const editor = document.getElementById('blogContentEditor');
    const hiddenField = document.getElementById('blogContent');
    const contentImageInput = document.getElementById('contentImageInput');
    const previewContent = document.getElementById('previewContent');
    let savedRange = null;

    if (!toolbarButtons.length || !editor || !hiddenField) {
        return;
    }

    const syncEditorContent = () => {
        hiddenField.value = editor.innerHTML;
        if (previewContent) {
            previewContent.innerHTML = editor.innerHTML;
        }
    };

    const saveSelectionRange = () => {
        const selection = window.getSelection();
        if (selection && selection.rangeCount > 0) {
            savedRange = selection.getRangeAt(0);
        }
    };

    const restoreSelectionRange = () => {
        const selection = window.getSelection();
        if (!selection) {
            return;
        }

        selection.removeAllRanges();

        if (savedRange) {
            selection.addRange(savedRange);
        } else {
            const range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(false);
            selection.addRange(range);
            savedRange = range;
        }
    };

    editor.addEventListener('input', syncEditorContent);
    editor.addEventListener('keyup', saveSelectionRange);
    editor.addEventListener('mouseup', saveSelectionRange);
    editor.addEventListener('focus', saveSelectionRange);

    const editorContainer = document.querySelector('.content-editor');
    if (editorContainer) {
        editorContainer.addEventListener('click', (event) => {
            if (event.target === editorContainer || event.target.classList.contains('editor-content')) {
                editor.focus();
                saveSelectionRange();
            }
        });
    }

    toolbarButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();

            const command = button.dataset.command;
            if (!command) {
                return;
            }

            editor.focus();
            restoreSelectionRange();

            if (command === 'h2' || command === 'h3') {
                document.execCommand('formatBlock', false, command);
                syncEditorContent();
                saveSelectionRange();
                return;
            }

            if (command === 'createLink') {
                const url = prompt('Enter the link URL:');
                if (url) {
                    document.execCommand('createLink', false, url);
                    syncEditorContent();
                    saveSelectionRange();
                }
                return;
            }

            if (command === 'insertImage') {
                if (contentImageInput) {
                    contentImageInput.value = '';
                    contentImageInput.click();
                } else {
                    const url = prompt('Enter the image URL:');
                    if (url) {
                        const html = `<img src="${url}" alt="Blog image" class="editor-inline-image"><br>`;
                        document.execCommand('insertHTML', false, html);
                        syncEditorContent();
                        saveSelectionRange();
                    }
                }
                return;
            }

            document.execCommand(command, false, null);
            syncEditorContent();
            saveSelectionRange();
        });
    });

    if (contentImageInput) {
        contentImageInput.addEventListener('change', async (event) => {
            const [file] = event.target.files || [];
            if (!file) {
                return;
            }

            if (!file.type.match(/^image\//)) {
                showNotification('Please select a valid image file.', 'error');
                contentImageInput.value = '';
                return;
            }

            showNotification('Uploading image...', 'info');
            
            try {
                const formData = new FormData();
                formData.append('image', file);
                formData.append('alt_text', 'Blog content image');
                
                const editIdInput = document.querySelector('input[name="edit_id"]');
                if (editIdInput && editIdInput.value) {
                    formData.append('blog_post_id', editIdInput.value);
                }
                
                const response = await fetch('/blog/upload-content-image/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    editor.focus();
                    restoreSelectionRange();
                    
                    const html = `<img src="${result.image_url}" alt="Blog image" class="editor-inline-image"><br>`;
                    document.execCommand('insertHTML', false, html);
                    
                    syncEditorContent();
                    saveSelectionRange();
                    showNotification('Image uploaded successfully!', 'success');
                } else {
                    throw new Error(result.message || 'Upload failed');
                }
            } catch (error) {
                const reader = new FileReader();
                reader.onload = (loadEvent) => {
                    const dataUrl = loadEvent.target.result;
                    editor.focus();
                    restoreSelectionRange();
                    
                    const html = `<img src="${dataUrl}" alt="Blog image" class="editor-inline-image"><br>`;
                    document.execCommand('insertHTML', false, html);
                    
                    syncEditorContent();
                    saveSelectionRange();
                };
                reader.readAsDataURL(file);
                showNotification('Using local preview - save post to upload image', 'info');
            }
            
            contentImageInput.value = '';
        });
    }

    syncEditorContent();
    saveSelectionRange();
}

/**
 * Initialize image upload and preview
 */
function initImageUpload() {
    const imageInput = document.getElementById('featuredImage');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');

    if (!imageInput || !imagePreview || !previewImage) {
        return;
    }

    imageInput.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) {
            return;
        }

        if (!file.type.match('image/jpeg') && !file.type.match('image/png')) {
            showNotification('Please select a valid image file (JPG or PNG)', 'error');
            return;
        }

        if (file.size > 2 * 1024 * 1024) {
            showNotification('Image size exceeds 2MB limit', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            imagePreview.innerHTML = `<img src="${event.target.result}" alt="Selected image">`;
            previewImage.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });

    imagePreview.addEventListener('click', () => {
        imageInput.click();
    });
}

/**
 * Initialize live preview of form data
 */
function initFormPreview() {
    const titleInput = document.getElementById('blogTitle');
    const previewTitle = document.getElementById('previewTitle');
    const categorySelect = document.getElementById('blogCategory');
    const previewCategory = document.getElementById('previewCategory');
    const tagsInput = document.getElementById('blogTags');
    const previewTags = document.getElementById('previewTags');
    const previewReadingTime = document.getElementById('previewReadingTime');
    
    // Title preview
    if (titleInput && previewTitle) {
        titleInput.addEventListener('input', function () {
            previewTitle.textContent = this.value || 'Your Blog Title Will Appear Here';
        });
    }
    
    // Category preview
    if (categorySelect && previewCategory) {
        categorySelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            previewCategory.textContent = selectedOption && selectedOption.text !== 'Select a category'
                ? selectedOption.text
                : 'Category';
        });
    }
    
    // Tags preview
    if (tagsInput && previewTags) {
        tagsInput.addEventListener('input', function () {
            if (!this.value.trim()) {
                previewTags.innerHTML = `
                    <span class="preview-tag">architecture</span>
                    <span class="preview-tag">design</span>
                    <span class="preview-tag">construction</span>
                `;
                return;
            }
            
            const tags = this.value.split(',').filter((tag) => tag.trim());
            const tagsHTML = tags.map((tag) => `<span class="preview-tag">${tag.trim()}</span>`).join('');
            previewTags.innerHTML = tagsHTML;
        });
    }
    
    // Content preview with reading time calculation
    const editor = document.getElementById('blogContentEditor');
    const previewContent = document.getElementById('previewContent');
    
    if (editor && previewContent && previewReadingTime) {
        const updatePreview = () => {
            const content = editor.innerHTML.trim();
            const textContent = editor.textContent.trim();
            
            if (textContent) {
                previewContent.innerHTML = content;
                
                // Calculate reading time (200 words per minute)
                const wordCount = textContent.split(/\s+/).filter(word => word.length > 0).length;
                const readingTime = Math.max(1, Math.ceil(wordCount / 200));
                previewReadingTime.textContent = readingTime;
            } else {
                previewContent.innerHTML = '<p>Your blog content will appear here as you type. This preview helps you see how your post will look when published.</p>';
                previewReadingTime.textContent = '5';
            }
        };
        
        editor.addEventListener('input', updatePreview);
        editor.addEventListener('paste', () => setTimeout(updatePreview, 100));
    }
}

/**
 * Initialize form action buttons
 */
function initFormActions() {
    const saveDraftBtn = document.getElementById('saveDraftBtn');
    const clearFormBtn = document.getElementById('clearFormBtn');
    const modal = document.getElementById('notificationModal');
    const closeModalBtn = document.querySelector('.close-modal');
    const modalConfirmBtn = document.querySelector('.modal-confirm');
    
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', (event) => {
            event.preventDefault();
            saveDraft();
            showNotification('Blog post saved as draft', 'success');
        });
    }
    
    if (clearFormBtn) {
        clearFormBtn.addEventListener('click', (event) => {
            event.preventDefault();
            if (confirm('Are you sure you want to clear all form fields? This cannot be undone.')) {
                clearForm();
                showNotification('Form cleared', 'info');
            }
        });
    }
    
    if (closeModalBtn && modalConfirmBtn) {
        closeModalBtn.addEventListener('click', closeModal);
        modalConfirmBtn.addEventListener('click', closeModal);
    }
    
    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }
}

/**
 * Save current form data as draft
 */
function saveDraft() {
    const blogData = {
        title: document.getElementById('blogTitle').value,
        category: document.getElementById('blogCategory').value,
        content: document.getElementById('blogContentEditor').innerHTML,
        tags: document.getElementById('blogTags').value,
        lastSaved: new Date().toISOString(),
    };
    
    const imagePreview = document.getElementById('imagePreview');
    const img = imagePreview.querySelector('img');
    if (img) {
        blogData.image = img.src;
    }
    
    try {
        localStorage.setItem('blogDraft', JSON.stringify(blogData));
    } catch (error) {
        showNotification('Could not save draft. Local storage may be full.', 'error');
    }
}

/**
 * Load saved draft from localStorage
 */
function loadSavedDraft() {
    try {
        const savedDraft = localStorage.getItem('blogDraft');
        if (!savedDraft) return;
        
        const blogData = JSON.parse(savedDraft);
        const lastSaved = new Date(blogData.lastSaved || Date.now());
        const daysElapsed = (Date.now() - lastSaved.getTime()) / (1000 * 60 * 60 * 24);
        
        if (daysElapsed > 7) {
            if (!confirm(`A draft from ${lastSaved.toLocaleDateString()} was found. Do you want to load it?`)) {
                localStorage.removeItem('blogDraft');
                return;
            }
        }
        
        if (blogData.title) document.getElementById('blogTitle').value = blogData.title;
        if (blogData.category) document.getElementById('blogCategory').value = blogData.category;
        if (blogData.content) {
            document.getElementById('blogContentEditor').innerHTML = blogData.content;
            document.getElementById('blogContent').value = blogData.content;
        }
        if (blogData.tags) document.getElementById('blogTags').value = blogData.tags;
        
        if (blogData.image) {
            document.getElementById('imagePreview').innerHTML = `<img src="${blogData.image}" alt="Selected image">`;
            document.getElementById('previewImage').src = blogData.image;
        }
        
        showNotification('Draft loaded successfully', 'info');
    } catch (error) {
        console.error('Error loading draft:', error);
    }
}

/**
 * Clear all form fields
 */
function clearForm() {
    document.getElementById('blogForm').reset();
    document.getElementById('blogContentEditor').innerHTML = '';
    document.getElementById('blogContent').value = '';
    document.getElementById('imagePreview').innerHTML = '<i class="fas fa-image"></i><span>No image selected</span>';
    
    document.getElementById('previewTitle').textContent = 'Your Blog Title Will Appear Here';
    document.getElementById('previewCategory').textContent = 'Category';
    document.getElementById('previewContent').innerHTML = '<p>Your blog content will appear here as you type.</p>';
    document.getElementById('previewTags').innerHTML = `
        <span class="preview-tag">architecture</span>
        <span class="preview-tag">design</span>
        <span class="preview-tag">construction</span>
    `;
    
    localStorage.removeItem('blogDraft');
}

/**
 * Show notification modal
 */
function showNotification(message, type = 'success') {
    const modal = document.getElementById('notificationModal');
    const modalIcon = document.querySelector('.modal-icon i');
    const modalTitle = document.querySelector('.modal-title');
    const modalMessage = document.querySelector('.modal-message');
    
    if (!modal || !modalIcon || !modalTitle || !modalMessage) return;
    
    if (type === 'success') {
        modalIcon.className = 'fas fa-check-circle';
        modalTitle.textContent = 'Success!';
        modalIcon.style.color = 'var(--success-color)';
    } else if (type === 'error') {
        modalIcon.className = 'fas fa-exclamation-circle';
        modalTitle.textContent = 'Error';
        modalIcon.style.color = 'var(--danger-color)';
    } else {
        modalIcon.className = 'fas fa-info-circle';
        modalTitle.textContent = 'Information';
        modalIcon.style.color = 'var(--info-color)';
    }
    
    modalMessage.textContent = message;
    modal.classList.add('active');
    
    if (type !== 'error') {
        setTimeout(closeModal, 3000);
    }
}

/**
 * Close notification modal
 */
function closeModal() {
    const modal = document.getElementById('notificationModal');
    if (modal) {
        modal.classList.remove('active');
    }
}
function initFormPreview() {
    const titleInput = document.getElementById('blogTitle');
    const previewTitle = document.getElementById('previewTitle');
    if (titleInput && previewTitle) {
        titleInput.addEventListener('input', function () {
            previewTitle.textContent = this.value || 'Your Blog Title Will Appear Here';
        });
    }

    const categorySelect = document.getElementById('blogCategory');
    const previewCategory = document.getElementById('previewCategory');
    if (categorySelect && previewCategory) {
        categorySelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            previewCategory.textContent = selectedOption && selectedOption.text !== 'Select a category'
                ? selectedOption.text
                : 'Category';
        });
    }

    const tagsInput = document.getElementById('blogTags');
    const previewTags = document.getElementById('previewTags');
    if (tagsInput && previewTags) {
        tagsInput.addEventListener('input', function () {
            if (!this.value.trim()) {
                previewTags.innerHTML = `
                    <span class="preview-tag">architecture</span>
                    <span class="preview-tag">design</span>
                    <span class="preview-tag">construction</span>
                `;
                return;
            }

            const tags = this.value.split(',').filter((tag) => tag.trim());
            const tagsHTML = tags.map((tag) => `<span class="preview-tag">${tag.trim()}</span>`).join('');
            previewTags.innerHTML = tagsHTML;
        });
    }
}

/**
 * Initialize form action buttons
 */
function initFormActions() {
    const blogForm = document.getElementById('blogForm');
    const saveDraftBtn = document.getElementById('saveDraftBtn');
    const clearFormBtn = document.getElementById('clearFormBtn');
    const modal = document.getElementById('notificationModal');
    const closeModalBtn = document.querySelector('.close-modal');
    const modalConfirmBtn = document.querySelector('.modal-confirm');

    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', (event) => {
            event.preventDefault();
            saveDraft();
            showNotification('Blog post saved as draft', 'success');
        });
    }

    if (clearFormBtn) {
        clearFormBtn.addEventListener('click', (event) => {
            event.preventDefault();
            if (confirm('Are you sure you want to clear all form fields? This cannot be undone.')) {
                clearForm();
                showNotification('Form cleared', 'info');
            }
        });
    }

    if (closeModalBtn && modalConfirmBtn) {
        closeModalBtn.addEventListener('click', closeModal);
        modalConfirmBtn.addEventListener('click', closeModal);
    }

    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });
}

/**
 * Validate form before submission
 */
function validateForm() {
    const title = document.getElementById('blogTitle').value.trim();
    const category = document.getElementById('blogCategory').value;
    const content = document.getElementById('blogContentEditor').innerHTML.trim();

    if (!title) {
        showNotification('Please enter a blog title', 'error');
        document.getElementById('blogTitle').focus();
        return false;
    }

    if (!category) {
        showNotification('Please select a blog category', 'error');
        document.getElementById('blogCategory').focus();
        return false;
    }

    if (!content || content === '<br>') {
        showNotification('Please add content to your blog post', 'error');
        document.getElementById('blogContentEditor').focus();
        return false;
    }

    return true;
}

/**
 * Save current form data as draft in localStorage
 */
function saveDraft() {
    const blogData = {
        title: document.getElementById('blogTitle').value,
        category: document.getElementById('blogCategory').value,
        content: document.getElementById('blogContentEditor').innerHTML,
        tags: document.getElementById('blogTags').value,
        lastSaved: new Date().toISOString(),
    };

    const imagePreview = document.getElementById('imagePreview');
    const img = imagePreview.querySelector('img');
    if (img) {
        blogData.image = img.src;
    }

    try {
        localStorage.setItem('blogDraft', JSON.stringify(blogData));
    } catch (error) {
        console.error('Error saving draft to localStorage:', error);
        showNotification('Could not save draft. Local storage may be full.', 'error');
    }
}

/**
 * Load saved draft from localStorage
 */
function loadSavedDraft() {
    try {
        const savedDraft = localStorage.getItem('blogDraft');
        if (!savedDraft) {
            return;
        }

        const blogData = JSON.parse(savedDraft);
        const lastSaved = new Date(blogData.lastSaved || Date.now());
        const daysElapsed = (Date.now() - lastSaved.getTime()) / (1000 * 60 * 60 * 24);

        if (daysElapsed > 7) {
            const shouldLoad = confirm(`A draft from ${lastSaved.toLocaleDateString()} was found. Do you want to load it?`);
            if (!shouldLoad) {
                localStorage.removeItem('blogDraft');
                return;
            }
        }

        if (blogData.title) {
            document.getElementById('blogTitle').value = blogData.title;
        }
        if (blogData.category) {
            document.getElementById('blogCategory').value = blogData.category;
        }
        if (blogData.content) {
            document.getElementById('blogContentEditor').innerHTML = blogData.content;
            document.getElementById('blogContent').value = blogData.content;
        }
        if (blogData.tags) {
            document.getElementById('blogTags').value = blogData.tags;
        }

        if (blogData.image) {
            document.getElementById('imagePreview').innerHTML = `<img src="${blogData.image}" alt="Selected image">`;
            document.getElementById('previewImage').src = blogData.image;
        }

        showNotification('Draft loaded successfully', 'info');
    } catch (error) {
        console.error('Error loading draft from localStorage:', error);
    }
}

/**
 * Clear all form fields
 */
function clearForm() {
    document.getElementById('blogForm').reset();
    document.getElementById('blogContentEditor').innerHTML = '';
    document.getElementById('blogContent').value = '';
    document.getElementById('imagePreview').innerHTML = '<i class="fas fa-image"></i><span>No image selected</span>';

    document.getElementById('previewTitle').textContent = 'Your Blog Title Will Appear Here';
    document.getElementById('previewCategory').textContent = 'Category';
    document.getElementById('previewContent').innerHTML = '<p>Your blog content will appear here as you type. This preview helps you see how your post will look when published.</p>';
    document.getElementById('previewImage').src = '../userside/css/images/image1.jpg';
    document.getElementById('previewTags').innerHTML = `
        <span class="preview-tag">architecture</span>
        <span class="preview-tag">design</span>
        <span class="preview-tag">construction</span>
    `;

    localStorage.removeItem('blogDraft');
}

/**
 * Show notification modal
 */
function showNotification(message, type = 'success') {
    const modal = document.getElementById('notificationModal');
    const modalIcon = document.querySelector('.modal-icon i');
    const modalTitle = document.querySelector('.modal-title');
    const modalMessage = document.querySelector('.modal-message');

    if (!modal || !modalIcon || !modalTitle || !modalMessage) {
        return;
    }

    if (type === 'success') {
        modalIcon.className = 'fas fa-check-circle';
        modalTitle.textContent = 'Success!';
        modalIcon.style.color = 'var(--success-color)';
    } else if (type === 'error') {
        modalIcon.className = 'fas fa-exclamation-circle';
        modalTitle.textContent = 'Error';
        modalIcon.style.color = 'var(--danger-color)';
    } else {
        modalIcon.className = 'fas fa-info-circle';
        modalTitle.textContent = 'Information';
        modalIcon.style.color = 'var(--info-color)';
    }

    modalMessage.textContent = message;
    modal.classList.add('active');

    if (type !== 'error') {
        setTimeout(closeModal, 3000);
    }
}

/**
 * Close notification modal
 */
function closeModal() {
    const modal = document.getElementById('notificationModal');
    if (modal) {
        modal.classList.remove('active');
    }
}