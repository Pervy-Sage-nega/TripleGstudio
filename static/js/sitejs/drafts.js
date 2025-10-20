/**
 * Triple G BuildHub - Blog Draft Management JavaScript
 * Handles draft functionality for Django-rendered content including:
 * - Displaying drafts in card and table views
 * - Draft preview in modal
 * - Draft actions (edit, delete, submit)
 * - Filtering and searching drafts
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initMobileMenu();
    initViewToggle();
    initDrafts();
    initModalHandlers();
});

/**
 * Initialize mobile menu toggle
 */
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar') && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            }
        });
    }
}

/**
 * Initialize the view toggle (card vs. table)
 */
function initViewToggle() {
    const viewBtns = document.querySelectorAll('.view-btn');
    const cardView = document.getElementById('drafts-card-view');
    const tableView = document.getElementById('drafts-table-view');
    
    if (viewBtns.length && cardView && tableView) {
        viewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                viewBtns.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const viewType = this.getAttribute('data-view');
                
                if (viewType === 'card') {
                    cardView.style.display = 'grid';
                    tableView.style.display = 'none';
                } else if (viewType === 'table') {
                    cardView.style.display = 'none';
                    tableView.style.display = 'block';
                }
                
                // Save view preference to localStorage
                localStorage.setItem('preferredDraftsView', viewType);
            });
        });
        
        // Load saved view preference
        const savedView = localStorage.getItem('preferredDraftsView');
        if (savedView) {
            const viewBtn = document.querySelector(`.view-btn[data-view="${savedView}"]`);
            if (viewBtn) {
                viewBtn.click();
            }
        }
    }
}

/**
 * Initialize drafts display
 */
function initDrafts() {
    // Initialize search and filter functionality for Django-rendered content
    initSearchAndFilter();
    
    // Initialize action buttons for Django-rendered cards and table rows
    initDjangoActionButtons();
}

/**
 * Initialize action buttons for Django-rendered content
 */
function initDjangoActionButtons() {
    // Initialize card action buttons
    const draftCards = document.querySelectorAll('.draft-card');
    draftCards.forEach(card => {
        setupDjangoCardActions(card);
    });
    
    // Initialize table row action buttons
    const tableRows = document.querySelectorAll('#drafts-table-body tr');
    tableRows.forEach(row => {
        setupDjangoTableRowActions(row);
    });
}

/**
 * Set up action buttons for Django-rendered cards
 */
function setupDjangoCardActions(card) {
    // Get blog data from card elements
    const blogData = extractBlogDataFromCard(card);
    
    // Preview button - handle various selectors
    const previewBtn = card.querySelector('.preview-btn, .action-btn[title="Preview"], .action-btn.view');
    if (previewBtn) {
        previewBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showPreviewModal(blogData);
            return false;
        });
    }
    
    // Delete button - add confirmation
    const deleteBtn = card.querySelector('.delete-btn, .action-btn[title="Delete"], .action-btn.delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showDeleteModal(blogData);
            return false;
        });
    }
    
    // Submit button
    const submitBtn = card.querySelector('.submit-btn, .action-btn[title="Submit"], .action-btn.submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showSubmitModal(blogData);
            return false;
        });
    }
}

/**
 * Set up action buttons for Django-rendered table rows
 */
function setupDjangoTableRowActions(row) {
    // Get blog data from table row
    const blogData = extractBlogDataFromTableRow(row);
    
    // Preview button - handle various selectors
    const previewBtn = row.querySelector('.action-btn[title="Preview"], .action-btn.view, .preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showPreviewModal(blogData);
            return false;
        });
    }
    
    // Delete button - add confirmation
    const deleteBtn = row.querySelector('.action-btn[title="Delete"], .action-btn.delete, .delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showDeleteModal(blogData);
            return false;
        });
    }
    
    // Submit button
    const submitBtn = row.querySelector('.action-btn[title="Submit"], .action-btn.submit, .submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showSubmitModal(blogData);
            return false;
        });
    }
}

/**
 * Extract blog data from Django-rendered card
 */
function extractBlogDataFromCard(card) {
    const titleElement = card.querySelector('.draft-title, .card-title');
    const categoryElement = card.querySelector('.draft-category, .card-category');
    const excerptElement = card.querySelector('.draft-excerpt, .card-excerpt');
    const tagsElements = card.querySelectorAll('.draft-tag, .tag');
    const dateElement = card.querySelector('.date-value, .card-date');
    const imageElement = card.querySelector('.card-image img, .draft-image img, img');
    const statusElement = card.querySelector('.status-label, .card-status');
    
    // Get the blog ID from data attributes or edit button URL
    let blogId = card.getAttribute('data-id') || card.getAttribute('data-blog-id');
    
    if (!blogId) {
        const editBtn = card.querySelector('.action-btn[title="Edit"], .edit-btn');
        if (editBtn && editBtn.href) {
            const urlMatch = editBtn.href.match(/edit=(\d+)/);
            if (urlMatch) {
                blogId = urlMatch[1];
            }
        }
    }
    
    return {
        id: blogId,
        title: titleElement ? titleElement.textContent.trim() : 'Untitled',
        category: categoryElement ? categoryElement.textContent.trim() : 'Uncategorized',
        content: excerptElement ? excerptElement.textContent : '',
        excerpt: excerptElement ? excerptElement.textContent : '',
        tags: Array.from(tagsElements).map(tag => tag.textContent.trim()),
        readingTime: '5', // Default reading time
        lastModified: dateElement ? dateElement.textContent.trim() : new Date().toLocaleDateString(),
        featuredImage: imageElement ? imageElement.src : null,
        imageAlt: imageElement ? imageElement.alt : '',
        status: statusElement ? statusElement.textContent.trim() : 'Draft'
    };
}

/**
 * Extract blog data from Django-rendered table row
 */
function extractBlogDataFromTableRow(row) {
    const cells = row.cells;
    
    // Get the blog ID from data attributes
    let blogId = row.getAttribute('data-id') || row.getAttribute('data-blog-id');
    
    if (!blogId) {
        const editBtn = row.querySelector('.action-btn[title="Edit"], .edit-btn');
        if (editBtn && editBtn.href) {
            const urlMatch = editBtn.href.match(/edit=(\d+)/);
            if (urlMatch) {
                blogId = urlMatch[1];
            }
        }
    }
    
    return {
        id: blogId,
        title: cells[0] ? cells[0].textContent.trim() : 'Untitled',
        category: cells[1] ? cells[1].textContent.trim() : 'Uncategorized',
        content: '', // Table doesn't have content preview
        excerpt: '', // Table doesn't have excerpt
        tags: [], // Table doesn't show tags
        readingTime: '5', // Default reading time
        lastModified: cells[2] ? cells[2].textContent.trim() : new Date().toLocaleDateString(),
        featuredImage: null, // Table doesn't show images
        imageAlt: '',
        status: cells[3] ? cells[3].textContent.trim() : 'Draft'
    };
}

/**
 * Initialize search and filter functionality for Django-rendered content
 */
function initSearchAndFilter() {
    const categoryFilter = document.querySelector('#category-filter, select[name="category"]');
    const statusFilter = document.querySelector('#status-filter, select[name="status"]');
    const searchInput = document.querySelector('#search-input, input[type="search"], input[placeholder*="Search"]');
    
    if (categoryFilter || statusFilter || searchInput) {
        const filterAndSearch = () => {
            const category = categoryFilter ? categoryFilter.value : '';
            const status = statusFilter ? statusFilter.value : '';
            const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
            
            // Map filter values to Django's get_status_display values (capitalized)
            const statusDisplayMap = {
                'published': 'published',
                'archived': 'archived', 
                'draft': 'draft',
                'rejected': 'rejected'
            };
            

            
            // Get all draft cards and table rows
            const draftCards = document.querySelectorAll('.draft-card');
            const tableRows = document.querySelectorAll('#drafts-table-body tr');
            
            let visibleCount = 0;
            
            // Filter cards
            draftCards.forEach(card => {
                const title = card.querySelector('.draft-title, .card-title')?.textContent.toLowerCase() || '';
                const excerpt = card.querySelector('.draft-excerpt, .card-excerpt')?.textContent.toLowerCase() || '';
                const cardCategory = card.querySelector('.draft-category, .card-category')?.textContent || '';
                const cardStatusElement = card.querySelector('.status-badge');
                const cardStatus = cardStatusElement ? cardStatusElement.textContent.toLowerCase().trim() : '';
                
                const tags = Array.from(card.querySelectorAll('.draft-tag, .tag')).map(tag => tag.textContent.toLowerCase());
                

                
                // For category: if filter has value, find matching category by name
                let categoryMatch = !category || category === '';
                if (category && category !== '') {
                    // Get category name from dropdown option text
                    const selectedOption = categoryFilter.querySelector(`option[value="${category}"]`);
                    const categoryName = selectedOption ? selectedOption.textContent.trim() : '';
                    categoryMatch = cardCategory.toLowerCase() === categoryName.toLowerCase();
                }
                const statusMatch = !status || status === '' || cardStatus === statusDisplayMap[status];
                const searchMatch = !searchTerm || 
                    title.includes(searchTerm) || 
                    excerpt.includes(searchTerm) ||
                    tags.some(tag => tag.includes(searchTerm));
                
                if (categoryMatch && statusMatch && searchMatch) {
                    card.style.display = '';
                    visibleCount++;
                    console.log('Showing card:', title);
                } else {
                    card.style.display = 'none';
                    console.log('Hiding card:', title, 'Category:', categoryMatch, 'Status:', statusMatch, 'Search:', searchMatch);
                }
            });
            
            // Filter table rows
            tableRows.forEach(row => {
                if (row.cells.length < 4) return;
                
                const title = row.cells[0]?.textContent.toLowerCase() || '';
                const rowCategory = row.cells[1]?.textContent.trim() || '';
                const rowStatusElement = row.cells[3]?.querySelector('.status-badge');
                const rowStatus = rowStatusElement ? rowStatusElement.textContent.toLowerCase().trim() : '';
                
                // For category: if filter has value, find matching category by name
                let categoryMatch = !category || category === '';
                if (category && category !== '') {
                    // Get category name from dropdown option text
                    const selectedOption = categoryFilter.querySelector(`option[value="${category}"]`);
                    const categoryName = selectedOption ? selectedOption.textContent.trim() : '';
                    categoryMatch = rowCategory.toLowerCase() === categoryName.toLowerCase();
                }
                
                const statusMatch = !status || status === '' || rowStatus === statusDisplayMap[status];
                const searchMatch = !searchTerm || title.includes(searchTerm);
                
                if (categoryMatch && statusMatch && searchMatch) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Show/hide no results message
            console.log('Total visible cards:', visibleCount);
            updateNoResultsMessage(visibleCount);
        };
        
        // Add event listeners
        if (categoryFilter) {
            categoryFilter.addEventListener('change', filterAndSearch);
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', filterAndSearch);
        }
        if (searchInput) {
            searchInput.addEventListener('input', filterAndSearch);
            searchInput.addEventListener('keyup', filterAndSearch);
        }
        
        // Initial filter
        filterAndSearch();
    }
}

/**
 * Update no results message visibility
 */
function updateNoResultsMessage(visibleCount) {
    const noResults = document.querySelector('.no-results, .no-drafts-message, .empty-state');
    if (noResults) {
        if (visibleCount === 0) {
            noResults.style.display = 'flex';
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
        }
    }
}

/**
 * Show preview modal for a draft
 */
function showPreviewModal(draft) {
    const modal = document.getElementById('previewModal');
    
    if (!modal) {
        console.warn('Preview modal not found');
        return;
    }
    
    console.log('Showing preview for draft:', draft); // Debug log
    
    // Fill in preview content
    const titleElement = document.getElementById('preview-title');
    const categoryElement = document.getElementById('preview-category');
    const readingTimeElement = document.getElementById('preview-reading-time');
    const contentElement = document.getElementById('preview-content');
    const dateElement = document.getElementById('preview-date');
    const imageElement = document.getElementById('preview-image');
    const statusElement = document.getElementById('preview-status');
    
    if (titleElement) titleElement.textContent = draft.title || 'Untitled Post';
    if (categoryElement) categoryElement.textContent = draft.category || 'Uncategorized';
    if (readingTimeElement) readingTimeElement.textContent = draft.readingTime || '5';
    if (dateElement) dateElement.textContent = draft.lastModified || new Date().toLocaleDateString();
    if (statusElement) statusElement.textContent = draft.status || 'Draft';
    
    // Handle featured image
    if (imageElement) {
        if (draft.featuredImage) {
            imageElement.src = draft.featuredImage;
            imageElement.alt = draft.imageAlt || draft.title || 'Blog post image';
            imageElement.style.display = 'block';
            imageElement.parentElement.style.display = 'block';
        } else {
            imageElement.style.display = 'none';
            imageElement.parentElement.style.display = 'none';
        }
    }
    
    // Handle content display with scroll support
    if (contentElement) {
        // Add scroll styling
        contentElement.style.maxHeight = '400px';
        contentElement.style.overflowY = 'auto';
        contentElement.style.padding = '15px';
        contentElement.style.border = '1px solid #e0e0e0';
        contentElement.style.borderRadius = '8px';
        contentElement.style.backgroundColor = '#fafafa';
        
        if (draft.excerpt && draft.excerpt.trim()) {
            contentElement.innerHTML = `<div class="preview-text">${formatContentForPreview(draft.excerpt)}</div>`;
        } else if (draft.content && draft.content.trim()) {
            contentElement.innerHTML = `<div class="preview-text">${formatContentForPreview(draft.content)}</div>`;
        } else {
            contentElement.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #7f8c8d;">
                    <i class="fas fa-file-alt" style="font-size: 48px; margin-bottom: 20px; opacity: 0.5;"></i>
                    <h3>Preview Not Available</h3>
                    <p>No content preview available for this blog post.</p>
                    <p><em>Click "Edit Post" to view and edit the full content.</em></p>
                </div>
            `;
        }
    }
    
    // Populate tags
    const tagsContainer = document.getElementById('preview-tags');
    if (tagsContainer) {
        tagsContainer.innerHTML = '';
        
        if (draft.tags && draft.tags.length > 0) {
            const tagsHeader = document.createElement('h4');
            tagsHeader.textContent = 'Tags:';
            tagsHeader.style.marginBottom = '10px';
            tagsHeader.style.color = '#2c3e50';
            tagsHeader.style.fontSize = '1rem';
            tagsContainer.appendChild(tagsHeader);
            
            draft.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'preview-tag';
                tagSpan.textContent = tag;
                tagsContainer.appendChild(tagSpan);
            });
        } else {
            tagsContainer.innerHTML = '<p style="color: #7f8c8d; font-style: italic;">No tags assigned to this post.</p>';
        }
    }
    
    // Set up edit button action
    const editBtn = document.getElementById('preview-edit-btn');
    if (editBtn && draft.id) {
        editBtn.onclick = () => {
            closeModal(modal);
            // Use Django URL pattern for editing
            window.location.href = `/blog/createblog/?edit=${draft.id}`;
        };
    }
    
    // Add modal scroll styling
    const modalBody = modal.querySelector('.modal-body');
    if (modalBody) {
        modalBody.style.maxHeight = '70vh';
        modalBody.style.overflowY = 'auto';
        modalBody.style.padding = '20px';
    }
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Show delete confirmation modal
 */
function showDeleteModal(draft) {
    if (!draft.id) {
        console.error('No draft ID provided for deletion');
        return;
    }
    
    if (confirm(`Are you sure you want to delete "${draft.title}"? This action cannot be undone.`)) {
        // Use Django delete URL - adjust based on your URL pattern
        window.location.href = `/blog/delete-blog/${draft.id}/`;
    }
}

/**
 * Show submit confirmation modal
 */
function showSubmitModal(draft) {
    if (!draft.id) {
        console.error('No draft ID provided for submission');
        return;
    }
    
    if (confirm(`Submit "${draft.title}" for admin approval?`)) {
        // Use Django submit URL - adjust based on your URL pattern
        window.location.href = `/blog/submit-blog/${draft.id}/`;
    }
}

/**
 * Initialize modal handlers
 */
function initModalHandlers() {
    // Close modal when clicking on close buttons
    document.addEventListener('click', function(e) {
        // Handle close buttons
        if (e.target.closest('.close-modal, .modal-close, [data-dismiss="modal"]')) {
            const modal = e.target.closest('.modal');
            closeModal(modal);
        }
        
        // Handle clicking outside modal content
        if (e.target.classList.contains('modal')) {
            closeModal(e.target);
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
}

/**
 * Close modal helper function
 */
function closeModal(modal) {
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    // Create toast element if it doesn't exist
    let toast = document.getElementById('toast-notification');
    
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        document.body.appendChild(toast);
        
        // Add styles to toast
        Object.assign(toast.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            backgroundColor: type === 'success' ? '#27ae60' : '#e74c3c',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '4px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
            zIndex: '9999',
            transition: 'opacity 0.3s, transform 0.3s',
            opacity: '0',
            transform: 'translateY(20px)'
        });
    }
    
    // Set message and style based on type
    toast.textContent = message;
    toast.style.backgroundColor = type === 'success' ? '#27ae60' : '#e74c3c';
    
    // Show toast
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
    }, 3000);
}

/**
 * Format content for preview display
 */
function formatContentForPreview(content) {
    if (!content) return '';
    
    // Remove HTML tags but preserve line breaks
    let formatted = content.replace(/<[^>]*>/g, '');
    
    // Convert line breaks to paragraphs
    formatted = formatted.split('\n').filter(line => line.trim()).map(line => `<p>${line.trim()}</p>`).join('');
    
    // If content is too long, truncate it
    if (formatted.length > 1000) {
        formatted = formatted.substring(0, 1000) + '... <em>(Content truncated for preview)</em>';
    }
    
    return formatted || '<p><em>No content available</em></p>';
}

// Utility function to debounce rapid calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Make functions available globally
window.showPreviewModal = showPreviewModal;
window.showDeleteModal = showDeleteModal;
window.showSubmitModal = showSubmitModal;
window.closeModal = closeModal;