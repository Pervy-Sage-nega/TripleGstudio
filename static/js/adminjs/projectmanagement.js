document.addEventListener('DOMContentLoaded', function() {
    // View containers and buttons
    const formBtn = document.getElementById('formBtn');
    const formContainer = document.getElementById('formContainer');
    const projectsContainer = document.getElementById('projectsContainer');
    const projectsTableView = document.getElementById('projectsTableView');
    const projectsGridView = document.getElementById('projectsGridView');
    const projectsTableBtn = document.getElementById('projectsTableViewBtn');
    const projectsGridBtn = document.getElementById('projectsGridViewBtn');

    // Helper: Scroll to selected section and update button states
    function scrollToSection(section) {
        let targetElement;
        
        if (section === 'form') {
            targetElement = formContainer;
        } else if (section === 'projects') {
            targetElement = projectsContainer;
        }
        
        if (targetElement) {
            targetElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start',
                inline: 'nearest'
            });
        }
        
        // Update button states - check if elements exist before accessing classList
        if (formBtn) {
            formBtn.classList.toggle('btn-primary', section === 'form');
            formBtn.classList.toggle('btn-secondary', section !== 'form');
            formBtn.classList.toggle('active', section === 'form');
        }
        
        const draftsBtn = document.getElementById('draftsBtn');
        if (draftsBtn) {
            draftsBtn.classList.toggle('btn-primary', section === 'drafts');
            draftsBtn.classList.toggle('btn-secondary', section !== 'drafts');
            draftsBtn.classList.toggle('active', section === 'drafts');
        }
        
        const tableBtn = document.getElementById('tableBtn');
        if (tableBtn) {
            tableBtn.classList.toggle('btn-primary', section === 'table');
            tableBtn.classList.toggle('btn-secondary', section !== 'table');
            tableBtn.classList.toggle('active', section === 'table');
        }
    }

    // Initial state: form button is active (no scroll needed) - only if formBtn exists
    if (formBtn) {
        scrollToSection('form');
    }

    // Button event listeners
    if (formBtn) {
        formBtn.addEventListener('click', function() {
            scrollToSection('form');
            if (typeof resetFormForNew === 'function') resetFormForNew();
        });
    }

    // Projects view toggle (Table/Grid)
    function showTableView() {
        if (projectsTableView && projectsGridView) {
            projectsTableView.style.display = 'block';
            projectsGridView.style.display = 'none';
            if (projectsTableBtn) projectsTableBtn.classList.add('active');
            if (projectsGridBtn) projectsGridBtn.classList.remove('active');
        }
    }
    
    function showGridView() {
        if (projectsTableView && projectsGridView) {
            projectsTableView.style.display = 'none';
            projectsGridView.style.display = 'grid';
            if (projectsGridBtn) projectsGridBtn.classList.add('active');
            if (projectsTableBtn) projectsTableBtn.classList.remove('active');
        }
    }
    
    if (projectsTableBtn && projectsGridBtn) {
        projectsTableBtn.addEventListener('click', showTableView);
        projectsGridBtn.addEventListener('click', showGridView);
    }

    // Summary card click handlers for filtering (redirect to table page)
    document.querySelectorAll('.summary-card').forEach(card => {
        card.addEventListener('click', function() {
            // Extract filter type from onclick attribute or data attribute
            const onclickAttr = this.getAttribute('onclick');
            if (onclickAttr) {
                const match = onclickAttr.match(/filterProjects\('([^']+)'\)/);
                if (match) {
                    const filter = match[1];
                    // Redirect to table page with filter parameter
                    window.location.href = `/portfolio/projecttable/?filter=${filter}`;
                }
            }
        });
    });

    // Get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Publish draft project
    function publishDraft(projectId) {
        if (!confirm('Are you sure you want to publish this draft project?')) {
            return;
        }
        
        // Update project status to 'planned' (or another appropriate status)
        fetch(`/portfolio/update-project-status/${projectId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'status': 'planned'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Draft project published successfully!');
                location.reload(); // Refresh the page to update the lists
            } else {
                alert('Error: ' + (data.message || 'Failed to publish draft'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while publishing the draft');
        });
    }

    // Basic JavaScript functions to prevent errors
    function editProject(projectId) {
        console.log('Edit project:', projectId);
        
        
        // Fetch project data
        fetch(`/portfolio/get-project/${projectId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error loading project: ' + data.error);
                    return;
                }
                
                // Update form action for editing
                document.getElementById('projectForm').action = `/portfolio/edit/${projectId}/`;
                
                // Populate form fields
                document.getElementById('title').value = data.title || '';
                document.getElementById('description').value = data.description || '';
                document.getElementById('category').value = data.category || '';
                document.getElementById('year').value = data.year || '';
                document.getElementById('location').value = data.location || '';
                document.getElementById('size').value = data.size || '';
                document.getElementById('duration').value = data.duration || '';
                document.getElementById('completion_date').value = data.completion_date || '';
                document.getElementById('lead_architect').value = data.lead_architect || '';
                document.getElementById('status').value = data.status || '';
                document.getElementById('featured').checked = data.featured || false;
                
                // Populate SEO fields
                document.getElementById('seo_meta_title').value = data.seo_meta_title || '';
                document.getElementById('seo_meta_description').value = data.seo_meta_description || '';
                document.getElementById('hero_image_alt').value = data.hero_image_alt || '';
                
                // Update character counts
                updateCharacterCount('seo_meta_title', 'seo_title_count');
                updateCharacterCount('seo_meta_description', 'seo_desc_count');
                
                // Clear existing milestones and add loaded ones
                document.getElementById('milestoneList').innerHTML = '';
                if (data.milestones && data.milestones.length > 0) {
                    data.milestones.forEach((milestone, index) => {
                        addMilestone();
                        const milestoneCards = document.querySelectorAll('.milestone-card');
                        const lastCard = milestoneCards[milestoneCards.length - 1];
                        
                        lastCard.querySelector('input[name="milestone_title[]"]').value = milestone.title;
                        lastCard.querySelector('input[name="milestone_date[]"]').value = milestone.date;
                        lastCard.querySelector('textarea[name="milestone_description[]"]').value = milestone.description;
                    });
                }
                
                // Scroll to form
                document.getElementById('formContainer').scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading project data');
            });
    }
    
    function deleteProject(projectId) {
        console.log('Delete project:', projectId);
        if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            // Create a form to submit DELETE request
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/portfolio/delete/${projectId}/`;
            
            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            // Submit form
            document.body.appendChild(form);
            form.submit();
        }
    }
    
    function addMilestone() {
        const milestoneList = document.getElementById('milestoneList');
        const milestoneCount = milestoneList.children.length;
        
        const milestoneCard = document.createElement('div');
        milestoneCard.className = 'milestone-card';
        milestoneCard.style.cssText = `
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        `;
        
        milestoneCard.innerHTML = `
            <div style="background: #fff; border-radius: 6px; padding: 1.25rem; border: 1px solid #e9ecef;">
                <div style="margin-bottom: 1.25rem;">
                    <h4 style="margin: 0; color: #495057; font-size: 1rem; font-weight: 600;">Milestone ${milestoneCount + 1}</h4>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500; color: #495057;">Title</label>
                    <input type="text" name="milestone_title[]" style="width: 100%; padding: 0.75rem; border: 1px solid #ced4da; border-radius: 4px; font-size: 0.9rem;" placeholder="e.g., Foundation Complete">
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500; color: #495057;">Date</label>
                    <input type="date" name="milestone_date[]" style="width: 100%; padding: 0.75rem; border: 1px solid #ced4da; border-radius: 4px; font-size: 0.9rem;">
                </div>
                
                <div style="margin-bottom: 1.25rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500; color: #495057;">Description</label>
                    <textarea name="milestone_description[]" rows="3" style="width: 100%; padding: 0.75rem; border: 1px solid #ced4da; border-radius: 4px; resize: vertical; font-size: 0.9rem;" placeholder="Brief description of this milestone..."></textarea>
                </div>
                
                <div style="border-top: 1px solid #e9ecef; padding-top: 1rem; display: flex; justify-content: flex-end;">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-milestone" onclick="removeMilestone(this)" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
        
        milestoneList.appendChild(milestoneCard);
    }
    
    function removeMilestone(button) {
        const milestoneCard = button.closest('.milestone-card');
        milestoneCard.remove();
        
        // Renumber remaining milestones
        const milestoneCards = document.querySelectorAll('.milestone-card');
        milestoneCards.forEach((card, index) => {
            const header = card.querySelector('h4');
            header.textContent = `Milestone ${index + 1}`;
        });
    }
    
    function saveAsDraft() {
        document.getElementById('publish').checked = false;
        document.getElementById('projectForm').submit();
    }
    
    function closeModal() {
        document.getElementById('actionModal').style.display = 'none';
    }
    
    // Function to reset form for new project
    function resetFormForNew() {
        const form = document.getElementById('projectForm');
        form.action = '/portfolio/create/';
        form.reset();
        document.getElementById('milestoneList').innerHTML = '';
    }

    // Video preview functionality
    document.getElementById('video').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const preview = document.getElementById('videoPreview');
        
        if (file) {
            const video = document.createElement('video');
            video.src = URL.createObjectURL(file);
            video.controls = true;
            video.style.maxWidth = '100%';
            video.style.height = 'auto';
            
            preview.innerHTML = '';
            preview.appendChild(video);
        } else {
            preview.innerHTML = '';
        }
    });

    // Refresh button functionality
    document.getElementById('refreshBtn').addEventListener('click', function() {
        location.reload();
    });

    // Delete draft function
    function deleteDraft(projectId) {
        if (!confirm('Are you sure you want to delete this draft project? This action cannot be undone.')) {
            return;
        }
        
        fetch(`/portfolio/delete-project/${projectId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Draft project deleted successfully!');
                location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to delete draft'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the draft');
        });
    }

    // SEO character counting
    function updateCharacterCount(inputId, counterId) {
        const input = document.getElementById(inputId);
        const counter = document.getElementById(counterId);
        if (input && counter) {
            counter.textContent = input.value.length;
        }
    }
    const seoTitleInput = document.getElementById('seo_meta_title');
    if (seoTitleInput) {
        seoTitleInput.addEventListener('input', function() {
            updateCharacterCount('seo_meta_title', 'seo_title_count');
        });
    }
    const seoDescInput = document.getElementById('seo_meta_description');
    if (seoDescInput) {
        seoDescInput.addEventListener('input', function() {
            updateCharacterCount('seo_meta_description', 'seo_desc_count');
        });
    }
    updateCharacterCount('seo_meta_title', 'seo_title_count');
    updateCharacterCount('seo_meta_description', 'seo_desc_count');
    
    // Form submission handler
    const projectForm = document.getElementById('projectForm');
    const publishBtn = document.getElementById('publishBtn');
    
    if (projectForm && publishBtn) {
        let isPublishClick = false;
        
        publishBtn.addEventListener('click', function() {
            isPublishClick = true;
        });
        
        projectForm.addEventListener('submit', function(e) {
            const publishCheckbox = document.getElementById('publish');
            const statusDropdown = document.getElementById('status');
            const hiddenStatus = document.getElementById('hiddenStatus');
            
            // Always use dropdown status, checkbox only controls publish_status
            if (hiddenStatus) hiddenStatus.removeAttribute('name');
            if (statusDropdown) statusDropdown.setAttribute('name', 'status');
        });
    }
    
    // Expose functions to global scope immediately
    window.addMilestone = addMilestone;
    window.removeMilestone = removeMilestone;
    window.saveAsDraft = saveAsDraft;
    
    // Also expose createMilestoneCard if it exists in the template
    if (typeof createMilestoneCard !== 'undefined') {
        window.createMilestoneCard = createMilestoneCard;
    }
});