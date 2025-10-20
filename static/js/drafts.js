/**
 * Triple G BuildHub - Blog Draft Management JavaScript
 * Handles draft functionality including:
 * - Loading drafts from localStorage
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
    updateStatistics();
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
    // Load drafts from localStorage
    const drafts = loadDrafts();
    
    // Initialize search and filter functionality
    initSearchAndFilter(drafts);
    
    // Display drafts
    displayDrafts(drafts);
}

/**
 * Load drafts from localStorage
 */
function loadDrafts() {
    let drafts = [];
    
    // Get all keys from localStorage
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        
        // Check if key matches the format for blog drafts
        if (key.startsWith('blogDraft_')) {
            try {
                const draft = JSON.parse(localStorage.getItem(key));
                draft.id = key.replace('blogDraft_', ''); // Extract ID from key
                drafts.push(draft);
            } catch (e) {
                console.error('Error parsing draft:', e);
            }
        }
    }
    
    // Sort drafts by last modified date (newest first)
    drafts.sort((a, b) => new Date(b.lastModified) - new Date(a.lastModified));
    
    return drafts;
}

/**
 * Initialize search and filter functionality
 */
function initSearchAndFilter(drafts) {
    const categoryFilter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');
    
    if (categoryFilter && searchInput) {
        // Combined filter & search function
        const filterAndSearch = () => {
            const category = categoryFilter.value;
            const searchTerm = searchInput.value.toLowerCase();
            
            // Filter drafts based on category and search term
            const filteredDrafts = drafts.filter(draft => {
                const categoryMatch = category === '' || draft.category === category;
                const titleMatch = draft.title.toLowerCase().includes(searchTerm);
                
                return categoryMatch && titleMatch;
            });
            
            // Display filtered drafts
            displayDrafts(filteredDrafts);
        };
        
        // Add event listeners
        categoryFilter.addEventListener('change', filterAndSearch);
        searchInput.addEventListener('input', filterAndSearch);
    }
}

/**
 * Display drafts in both card and table views
 */
function displayDrafts(drafts) {
    const cardView = document.getElementById('drafts-card-view');
    const tableBody = document.getElementById('drafts-table-body');
    const noContentMessage = document.getElementById('no-drafts-message');
    
    if (!cardView || !tableBody) return;
    
    // Clear existing content
    // Remove all cards except the template and no drafts message
    const existingCards = cardView.querySelectorAll('.draft-card:not(.template)');
    existingCards.forEach(card => card.remove());
    
    // Clear table rows
    tableBody.innerHTML = '';
    
    // Show/hide no content message
    if (drafts.length === 0) {
        if (noContentMessage) noContentMessage.style.display = 'flex';
    } else {
        if (noContentMessage) noContentMessage.style.display = 'none';
        
        // Get card template
        const cardTemplate = document.getElementById('draft-card-template');
        
        // Populate cards and table rows
        drafts.forEach(draft => {
            // Create card
            if (cardTemplate) {
                const card = cardTemplate.cloneNode(true);
                card.classList.remove('template');
                card.id = 'card-' + draft.id;
                
                // Populate card data
                card.querySelector('.draft-category').textContent = getCategoryName(draft.category);
                card.querySelector('.date-value').textContent = formatDate(draft.lastModified);
                card.querySelector('.draft-title').textContent = draft.title;
                
                // Create excerpt from content (strip HTML tags)
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = draft.content;
                const excerpt = tempDiv.textContent.substring(0, 100) + '...';
                card.querySelector('.draft-excerpt').textContent = excerpt;
                
                // Populate tags
                const tagsContainer = card.querySelector('.draft-tags');
                tagsContainer.innerHTML = '';
                
                if (draft.tags && draft.tags.length > 0) {
                    draft.tags.forEach(tag => {
                        const tagSpan = document.createElement('span');
                        tagSpan.className = 'draft-tag';
                        tagSpan.textContent = tag;
                        tagsContainer.appendChild(tagSpan);
                    });
                }
                
                // Set up action buttons
                setupCardActions(card, draft);
                
                // Add card to view
                cardView.appendChild(card);
            }
            
            // Create table row
            const row = document.createElement('tr');
            
            // Format the date
            const formattedDate = formatDate(draft.lastModified);
            
            row.innerHTML = `
                <td>${draft.title}</td>
                <td>${getCategoryName(draft.category)}</td>
                <td>${formattedDate}</td>
                <td><span class="status-label">Draft</span></td>
                <td class="table-actions">
                    <button class="action-btn preview-btn" title="Preview" data-id="${draft.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit-btn" title="Edit" data-id="${draft.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" title="Delete" data-id="${draft.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                    <button class="action-btn submit-btn" title="Submit for Approval" data-id="${draft.id}">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </td>
            `;
            
            // Set up table action buttons
            setupTableRowActions(row, draft);
            
            // Add row to table
            tableBody.appendChild(row);
        });
    }
}

/**
 * Set up action buttons for a card
 */
function setupCardActions(card, draft) {
    // Preview button
    const previewBtn = card.querySelector('.preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', () => showPreviewModal(draft));
    }
    
    // Edit button
    const editBtn = card.querySelector('.edit-btn');
    if (editBtn) {
        editBtn.addEventListener('click', () => {
            window.location.href = `createblog.html?edit=${draft.id}`;
        });
    }
    
    // Delete button
    const deleteBtn = card.querySelector('.delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => showDeleteModal(draft));
    }
    
    // Submit button
    const submitBtn = card.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', () => showSubmitModal(draft));
    }
}

/**
 * Set up action buttons for a table row
 */
function setupTableRowActions(row, draft) {
    // Preview button
    const previewBtn = row.querySelector('.preview-btn');
    if (previewBtn) {
        previewBtn.addEventListener('click', () => showPreviewModal(draft));
    }
    
    // Edit button
    const editBtn = row.querySelector('.edit-btn');
    if (editBtn) {
        editBtn.addEventListener('click', () => {
            window.location.href = `createblog.html?edit=${draft.id}`;
        });
    }
    
    // Delete button
    const deleteBtn = row.querySelector('.delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => showDeleteModal(draft));
    }
    
    // Submit button
    const submitBtn = row.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', () => showSubmitModal(draft));
    }
}

/**
 * Show preview modal for a draft
 */
function showPreviewModal(draft) {
    const modal = document.getElementById('previewModal');
    
    if (!modal) return;
    
    // Fill in preview content
    document.getElementById('preview-title').textContent = draft.title;
    document.getElementById('preview-category').textContent = getCategoryName(draft.category);
    document.getElementById('preview-reading-time').textContent = draft.readingTime || '5';
    document.getElementById('preview-content').innerHTML = draft.content;
    
    // Set featured image if available
    const previewImage = document.getElementById('preview-image');
    if (previewImage) {
        if (draft.featuredImage) {
            previewImage.src = draft.featuredImage;
            previewImage.style.display = 'block';
        } else {
            previewImage.src = '../userside/css/images/image1.jpg';
            previewImage.style.display = 'block';
        }
    }
    
    // Populate tags
    const tagsContainer = document.getElementById('preview-tags');
    if (tagsContainer) {
        tagsContainer.innerHTML = '';
        
        if (draft.tags && draft.tags.length > 0) {
            draft.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'preview-tag';
                tagSpan.textContent = tag;
                tagsContainer.appendChild(tagSpan);
            });
        }
    }
    
    // Set up edit button action
    const editBtn = document.getElementById('preview-edit-btn');
    if (editBtn) {
        editBtn.onclick = () => {
            window.location.href = `createblog.html?edit=${draft.id}`;
        };
    }
    
    // Show modal
    modal.classList.add('active');
}

/**
 * Show delete confirmation modal
 */
function showDeleteModal(draft) {
    const modal = document.getElementById('deleteModal');
    
    if (!modal) return;
    
    // Update modal message
    modal.querySelector('.modal-message').textContent = 
        `Are you sure you want to delete "${draft.title}"? This action cannot be undone.`;
    
    // Set up confirmation button
    const confirmBtn = document.getElementById('delete-confirm-btn');
    if (confirmBtn) {
        // Remove old event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        // Add new event listener
        newConfirmBtn.addEventListener('click', () => {
            deleteDraft(draft.id);
            closeModal('deleteModal');
        });
    }
    
    // Show modal
    modal.classList.add('active');
}

/**
 * Show submit confirmation modal
 */
function showSubmitModal(draft) {
    const modal = document.getElementById('submitModal');
    
    if (!modal) return;
    
    // Set up confirmation button
    const confirmBtn = modal.querySelector('.modal-confirm');
    if (confirmBtn) {
        // Remove old event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        // Add new event listener
        newConfirmBtn.addEventListener('click', () => {
            submitDraft(draft.id);
            closeModal('submitModal');
        });
    }
    
    // Show modal
    modal.classList.add('active');
}

/**
 * Delete a draft
 */
function deleteDraft(draftId) {
    // Remove from localStorage
    localStorage.removeItem(`blogDraft_${draftId}`);
    
    // Reload drafts
    const drafts = loadDrafts();
    displayDrafts(drafts);
    updateStatistics();
    
    // Show notification
    showToast('Draft deleted successfully');
}

/**
 * Submit a draft for approval
 */
function submitDraft(draftId) {
    // Mark as submitted in localStorage
    const draftKey = `blogDraft_${draftId}`;
    const draft = JSON.parse(localStorage.getItem(draftKey));
    
    if (draft) {
        draft.status = 'submitted';
        draft.submittedDate = new Date().toISOString();
        localStorage.setItem(draftKey, JSON.stringify(draft));
    }
    
    // Reload drafts
    const drafts = loadDrafts();
    displayDrafts(drafts);
    updateStatistics();
    
    // Show notification
    showToast('Draft submitted for admin approval');
}

/**
 * Initialize modal handlers
 */
function initModalHandlers() {
    // Close modal when clicking on X or cancel buttons
    const closeButtons = document.querySelectorAll('.close-modal, #preview-close-btn, #delete-cancel-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    // Close modal when clicking outside
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    });
}

/**
 * Close a modal by ID
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Update statistics counters
 */
function updateStatistics() {
    const drafts = loadDrafts();
    
    // Total drafts count
    document.getElementById('drafts-count').textContent = drafts.length;
    
    // Recent drafts (within last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const recentDrafts = drafts.filter(draft => {
        return new Date(draft.lastModified) >= sevenDaysAgo;
    });
    document.getElementById('recent-count').textContent = recentDrafts.length;
    
    // Submitted drafts
    const submittedDrafts = drafts.filter(draft => draft.status === 'submitted');
    document.getElementById('submitted-count').textContent = submittedDrafts.length;
}

/**
 * Get category display name from category ID
 */
function getCategoryName(categoryId) {
    const categories = {
        'industry-insights': 'Industry Insights',
        'expert-advice': 'Expert Advice',
        'case-study': 'Case Study',
        'design-trends': 'Design Trends',
        'sustainable-building': 'Sustainable Building',
        'technology': 'Construction Technology',
        'regulations': 'Regulations & Standards'
    };
    
    return categories[categoryId] || 'Uncategorized';
}

/**
 * Format date to display format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Show toast notification
 */
function showToast(message) {
    // Create toast element if it doesn't exist
    let toast = document.getElementById('toast-notification');
    
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        document.body.appendChild(toast);
        
        // Add styles to toast
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.backgroundColor = 'var(--primary-color)';
        toast.style.color = 'white';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '4px';
        toast.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
        toast.style.zIndex = '9999';
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
    }
    
    // Set message
    toast.textContent = message;
    
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