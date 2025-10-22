document.addEventListener('DOMContentLoaded', function() {
    // ===== TAB SWITCHING =====
    initTabs();

    // ===== BUDGET TRACKING VARIABLES =====
    let dailyCost = 0;
    let runningCost = 0;
    let projectBudget = 0;
    let materialCosts = [];
    let equipmentCosts = [];
    let otherCosts = [];

    // ===== INITIALIZATION =====
    initBudgetTracking();
   
    initMobileMenu();
    initDatePickers();
    initSignaturePads();
    initPhotoUpload();
    initDynamicLists();
    setupTimeCalculation();
    setupFormValidation();

    function initTabs() {
        const tabButtons = Array.from(document.querySelectorAll('.tab-button'));
        const tabPanels = Array.from(document.querySelectorAll('.tab-panel'));

        if (tabButtons.length === 0) return;

        function activateTab(targetId) {
            tabButtons.forEach(btn => {
                const isActive = btn.getAttribute('aria-controls') === targetId;
                btn.classList.toggle('active', isActive);
                btn.setAttribute('aria-selected', String(isActive));
                btn.tabIndex = isActive ? 0 : -1;
            });

            tabPanels.forEach(panel => {
                const isActive = panel.id === targetId;
                panel.classList.toggle('active', isActive);
                panel.hidden = !isActive;
            });
        }

        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => activateTab(btn.getAttribute('aria-controls')));
            btn.addEventListener('keydown', (e) => {
                const currentIndex = tabButtons.indexOf(btn);
                if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    const next = tabButtons[(currentIndex + 1) % tabButtons.length];
                    next.focus();
                    activateTab(next.getAttribute('aria-controls'));
                } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prev = tabButtons[(currentIndex - 1 + tabButtons.length) % tabButtons.length];
                    prev.focus();
                    activateTab(prev.getAttribute('aria-controls'));
                } else if (e.key === 'Home') {
                    e.preventDefault();
                    tabButtons[0].focus();
                    activateTab(tabButtons[0].getAttribute('aria-controls'));
                } else if (e.key === 'End') {
                    e.preventDefault();
                    const last = tabButtons[tabButtons.length - 1];
                    last.focus();
                    activateTab(last.getAttribute('aria-controls'));
                }
            });
        });

        // Ensure only the first is visible initially
        const initiallyActive = document.querySelector('.tab-button.active');
        if (initiallyActive) activateTab(initiallyActive.getAttribute('aria-controls'));

        // Expose helper for focusing tab of an element
        window.__focusTabForElement = function(el) {
            const panel = el.closest('.tab-panel');
            if (!panel) return;
            const btn = tabButtons.find(b => b.getAttribute('aria-controls') === panel.id);
            if (btn) {
                activateTab(panel.id);
                btn.focus();
            }
        };
    }

    // ===== BUDGET TRACKING FUNCTIONS =====
    function initBudgetTracking() {
        // Update project budget when project is selected
        const projectSelect = document.getElementById('projectSelect');
        if (projectSelect) {
            projectSelect.addEventListener('change', function() {
                const projectCode = this.options[this.selectedIndex].value;
                // In a real app, this would fetch from server
                projectBudget = parseInt(localStorage.getItem(`project_budget_${projectCode}`)) || 0;
                const budgetElement = document.getElementById('projectBudget');
                if (budgetElement) {
                    budgetElement.value = formatCurrency(projectBudget);
                }
                
                // For demo, set a running cost (25% of budget)
                runningCost = Math.floor(projectBudget * 0.25);
                updateBudgetSummary();
            });
        }

        // Calculate costs when items are added
        document.getElementById('addMaterial')?.addEventListener('click', addMaterialCost);
        document.getElementById('addEquipment')?.addEventListener('click', addEquipmentCost);
        document.getElementById('addOtherCost')?.addEventListener('click', addOtherCost);
    }

    function addMaterialCost() {
        const name = document.getElementById('materialName').value.trim();
        const quantity = parseFloat(document.getElementById('materialQuantity').value) || 0;
        const unit = document.getElementById('materialUnit').value;
        const cost = parseFloat(document.getElementById('materialCost').value) || 0;
        
        if (name && quantity && unit && cost > 0) {
            const material = { name, quantity, unit, cost };
            materialCosts.push(material);
            dailyCost += cost;
            
            addItemToList(
                `<strong>${name}</strong> - ${quantity} ${unit} - ${formatCurrency(cost)}`,
                document.getElementById('materialsList')
            );
            
            clearInputs(['materialName', 'materialQuantity', 'materialUnit', 'materialCost']);
            updateBudgetSummary();
        }
    }

    function addEquipmentCost() {
        const name = document.getElementById('equipmentName').value.trim();
        const quantity = parseFloat(document.getElementById('equipmentQuantity').value) || 1;
        const hours = parseFloat(document.getElementById('equipmentHours').value) || 0;
        const cost = parseFloat(document.getElementById('equipmentCost').value) || 0;
        
        if (name && cost > 0) {
            const equipment = { name, quantity, hours, cost };
            equipmentCosts.push(equipment);
            dailyCost += cost;
            
            addItemToList(
                `<strong>${name}</strong> - ${quantity} unit${quantity > 1 ? 's' : ''}${hours ? ` - ${hours} hrs` : ''} - ${formatCurrency(cost)}`,
                document.getElementById('equipmentList')
            );
            
            clearInputs(['equipmentName', 'equipmentQuantity', 'equipmentHours', 'equipmentCost']);
            updateBudgetSummary();
        }
    }

    function addOtherCost() {
        const name = document.getElementById('otherCostName').value.trim();
        const amount = parseFloat(document.getElementById('otherCostAmount').value) || 0;
        
        if (name && amount > 0) {
            const cost = { name, amount };
            otherCosts.push(cost);
            dailyCost += amount;
            
            addItemToList(
                `<strong>${name}</strong> - ${formatCurrency(amount)}`,
                document.getElementById('otherCostsList')
            );
            
            clearInputs(['otherCostName', 'otherCostAmount']);
            updateBudgetSummary();
        }
    }

    function updateBudgetSummary() {
        const dailyCostElement = document.getElementById('dailyCost');
        if (dailyCostElement) {
            dailyCostElement.value = formatCurrency(dailyCost);
        }
        
        const totalUsed = runningCost + dailyCost;
        const runningCostElement = document.getElementById('runningCost');
        if (runningCostElement) {
            runningCostElement.value = formatCurrency(totalUsed);
        }
        
        if (projectBudget > 0) {
            const remaining = projectBudget - totalUsed;
            const remainingElement = document.getElementById('remainingBudget');
            if (remainingElement) {
                remainingElement.value = formatCurrency(remaining);
                
                // Visual feedback for budget status
                if (remaining < projectBudget * 0.1) {
                    remainingElement.classList.add('budget-warning');
                    remainingElement.classList.remove('budget-safe');
                } else {
                    remainingElement.classList.add('budget-safe');
                    remainingElement.classList.remove('budget-warning');
                }
            }
        }
    }

    function formatCurrency(amount) {
        return amount.toLocaleString('en-PH', {
            style: 'currency',
            currency: 'PHP',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function clearInputs(ids) {
        ids.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.value = element.tagName === 'SELECT' ? '' : (id.includes('Quantity') ? '1' : '');
        });
    }

    // ===== GLOBAL HELPER FUNCTIONS =====
    function addItemToList(value, list, formatFunction) {
        const item = document.createElement('div');
        item.className = 'entry-item';
        
        const content = formatFunction ? formatFunction(value) : value;
        
        item.innerHTML = `
            <div class="entry-content">${content}</div>
            <div class="entry-actions">
                <button type="button" class="entry-action-btn edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button type="button" class="entry-action-btn delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        list.appendChild(item);
        setupItemActions(item);
    }
    
    function setupItemActions(item) {
        const editBtn = item.querySelector('.edit');
        const deleteBtn = item.querySelector('.delete');
        const contentElem = item.querySelector('.entry-content');
        
        editBtn.addEventListener('click', function() {
            const newContent = prompt('Edit entry:', contentElem.textContent);
            if (newContent !== null) contentElem.textContent = newContent;
        });
        
        deleteBtn.addEventListener('click', function() {
            if (confirm('Remove this entry?')) item.remove();
        });
    }
    
    // Global function for subcontractor functionality (referenced in template)
    window.addSubcontractor = function() {
        const selectElement = document.getElementById('subcontractorSelect');
        const customInput = document.getElementById('subcontractorCustom');
        const workInput = document.getElementById('subcontractorWork');
        
        let subcontractorName = '';
        let subcontractorType = '';
        let contactInfo = '';
        const workDescription = workInput.value.trim();
        
        // Check if dropdown is selected
        if (selectElement.value) {
            const selectedOption = selectElement.options[selectElement.selectedIndex];
            subcontractorName = selectedOption.text.split(' - ')[0]; // Get company name only
            subcontractorType = selectedOption.getAttribute('data-type');
            const contact = selectedOption.getAttribute('data-contact');
            const phone = selectedOption.getAttribute('data-phone');
            if (contact || phone) {
                contactInfo = ` (${contact || 'Contact'}${phone ? ': ' + phone : ''})`;
            }
        } 
        // Check if custom input has value
        else if (customInput.value.trim()) {
            subcontractorName = customInput.value.trim();
            subcontractorType = 'Custom';
        }
        
        if (subcontractorName) {
            const displayText = workDescription ? 
                `${subcontractorName}${contactInfo} - ${workDescription}` : 
                `${subcontractorName}${contactInfo} - ${subcontractorType} work`;
                
            addItemToList(
                `<strong>${displayText}</strong>`,
                document.getElementById('subcontractorList')
            );
            
            // Clear inputs
            selectElement.value = '';
            customInput.value = '';
            workInput.value = '';
        }
    }

    // ===== EXISTING FUNCTIONALITY (UPDATED FOR BUDGET INTEGRATION) =====
    function initMobileMenu() {
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');
        
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', function() {
                navLinks.classList.toggle('active');
            });
        }
    }

    function initDatePickers() {
        flatpickr("#entryDate", {
            dateFormat: "Y-m-d",
            defaultDate: "today"
        });

        flatpickr("#startTime", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true
        });

        flatpickr("#endTime", {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true
        });
    }

    function initSignaturePads() {
        const supervisorUpload = document.getElementById('supervisorSignatureUpload');
        const supervisorPreview = document.getElementById('supervisorSignaturePreview');
        const uploadContainer = document.getElementById('uploadContainer');
        const canvasContainer = document.getElementById('canvasContainer');
        const signatureCanvas = document.getElementById('signatureCanvas');
        const uploadMethod = document.getElementById('uploadMethod');
        const drawMethod = document.getElementById('drawMethod');
        
        let signaturePad = null;
        
        // Initialize signature pad
        if (signatureCanvas && typeof SignaturePad !== 'undefined') {
            signaturePad = new SignaturePad(signatureCanvas, {
                backgroundColor: 'rgb(255, 255, 255)',
                penColor: 'rgb(0, 0, 0)'
            });
            // Make it globally accessible for validation
            window.signaturePad = signaturePad;
        }
        
        // Handle method switching
        function switchSignatureMethod() {
            if (uploadMethod.checked) {
                uploadContainer.style.display = 'block';
                canvasContainer.style.display = 'none';
            } else {
                uploadContainer.style.display = 'none';
                canvasContainer.style.display = 'block';
            }
        }
        
        if (uploadMethod && drawMethod) {
            uploadMethod.addEventListener('change', switchSignatureMethod);
            drawMethod.addEventListener('change', switchSignatureMethod);
        }
        
        function setupSignatureUpload(uploadInput, previewContainer) {
            previewContainer.addEventListener('click', function() {
                uploadInput.click();
            });
            
            uploadInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" alt="Signature">`;
                    };
                    
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
        
        function clearSignature() {
            if (uploadMethod.checked) {
                supervisorUpload.value = '';
                supervisorPreview.innerHTML = `
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">Click to upload signature image</div>
                `;
            } else if (signaturePad) {
                signaturePad.clear();
            }
        }
        
        if (supervisorUpload && supervisorPreview) {
            setupSignatureUpload(supervisorUpload, supervisorPreview);
        }
        
        document.getElementById('clearSupervisorSignature').addEventListener('click', clearSignature);
        
        // Handle form submission for canvas signatures
        const form = document.getElementById('siteEntryForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                const drawMethod = document.getElementById('drawMethod');
                if (drawMethod && drawMethod.checked && signaturePad && !signaturePad.isEmpty()) {
                    // Convert canvas to blob and create hidden input
                    const canvas = document.getElementById('signatureCanvas');
                    canvas.toBlob(function(blob) {
                        const formData = new FormData(form);
                        formData.append('signature_canvas', blob, 'signature.png');
                        
                        // Create hidden input for signature data
                        const hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = 'signature_data';
                        hiddenInput.value = canvas.toDataURL();
                        form.appendChild(hiddenInput);
                    });
                }
            });
        }
    }

    function initPhotoUpload() {
        const photoDropZone = document.getElementById('photoDropZone');
        const photoUpload = document.getElementById('photoUpload');
        const photoGallery = document.getElementById('photoGallery');
        
        if (photoDropZone && photoUpload) {
            photoDropZone.addEventListener('click', function() {
                photoUpload.click();
            });
            
            photoDropZone.addEventListener('dragover', function(e) {
                e.preventDefault();
                photoDropZone.style.borderColor = 'var(--primary-color)';
            });
            
            photoDropZone.addEventListener('dragleave', function() {
                photoDropZone.style.borderColor = 'var(--border-color)';
            });
            
            photoDropZone.addEventListener('drop', function(e) {
                e.preventDefault();
                photoDropZone.style.borderColor = 'var(--border-color)';
                
                if (e.dataTransfer.files.length) {
                    handleFiles(e.dataTransfer.files);
                }
            });
            
            photoUpload.addEventListener('change', function() {
                if (this.files.length) {
                    handleFiles(this.files);
                }
            });
            
            function handleFiles(files) {
                Array.from(files).forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        
                        reader.onload = function(e) {
                            addPhotoToGallery(e.target.result, file.name);
                        };
                        
                        reader.readAsDataURL(file);
                    }
                });
                photoUpload.value = '';
            }
            
            function addPhotoToGallery(src, filename) {
                const photoItem = document.createElement('div');
                photoItem.className = 'photo-item';
                
                photoItem.innerHTML = `
                    <img src="${src}" alt="Site Photo" class="photo-preview">
                    <div class="photo-overlay">
                        <div class="photo-description">${filename}</div>
                        <div class="photo-actions">
                            <button type="button" class="photo-action-btn edit-desc" title="Edit Description">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="photo-action-btn delete-photo" title="Remove Photo">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
                
                photoGallery.appendChild(photoItem);
                
                const editBtn = photoItem.querySelector('.edit-desc');
                const deleteBtn = photoItem.querySelector('.delete-photo');
                
                editBtn.addEventListener('click', function() {
                    const descElem = this.closest('.photo-overlay').querySelector('.photo-description');
                    const newDesc = prompt('Enter photo description:', descElem.textContent);
                    if (newDesc !== null) descElem.textContent = newDesc;
                });
                
                deleteBtn.addEventListener('click', function() {
                    if (confirm('Remove this photo?')) photoItem.remove();
                });
            }
        }
    }

    function setupFormValidation() {
        const form = document.getElementById('siteEntryForm');
        
        if (form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    const invalidElements = form.querySelectorAll(':invalid');
                    if (invalidElements.length > 0) {
                        const firstInvalid = invalidElements[0];
                        if (window.__focusTabForElement) {
                            window.__focusTabForElement(firstInvalid);
                        }
                        firstInvalid.focus();
                    }
                }
                
                form.classList.add('was-validated');
                
                // Check supervisor signature
                const uploadMethod = document.getElementById('uploadMethod');
                const supervisorUpload = document.getElementById('supervisorSignatureUpload');
                const signatureCanvas = document.getElementById('signatureCanvas');
                let hasSignature = false;
                
                if (uploadMethod && uploadMethod.checked) {
                    hasSignature = supervisorUpload && supervisorUpload.files.length > 0;
                } else {
                    // Check if canvas has signature
                    if (signatureCanvas && window.signaturePad) {
                        hasSignature = !window.signaturePad.isEmpty();
                    }
                }
                
                if (!hasSignature) {
                    event.preventDefault();
                    const sigFeedback = document.querySelector('.signature-container .invalid-feedback');
                    if (sigFeedback) sigFeedback.style.display = 'block';
                    if (window.__focusTabForElement) window.__focusTabForElement(supervisorUpload || signatureCanvas);
                } else {
                    const sigFeedback = document.querySelector('.signature-container .invalid-feedback');
                    if (sigFeedback) sigFeedback.style.display = 'none';
                }
            });
        }
    }

    function initDynamicLists() {
        setupDynamicList('addTask', 'taskInput', 'taskList');
        setupDynamicList('addSubcontractor', 'subcontractorInput', 'subcontractorList');
        
        function setupDynamicList(addBtnId, inputId, listId, formatFunction) {
            const addBtn = document.getElementById(addBtnId);
            const input = document.getElementById(inputId);
            const list = document.getElementById(listId);
            
            if (addBtn && input && list) {
                addBtn.addEventListener('click', function() {
                    const value = input.value.trim();
                    if (value) {
                        addItemToList(value, list, formatFunction);
                        input.value = '';
                        input.focus();
                    }
                });
                
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        addBtn.click();
                    }
                });
                
                setupExistingItemActions(list);
            }
        }
        
        // addItemToList function moved to global scope above
        
        function setupExistingItemActions(list) {
            const items = list.querySelectorAll('.entry-item');
            items.forEach(item => setupItemActions(item));
        }
        
        // setupItemActions function moved to global scope above
    }

    function setupTimeCalculation() {
        const startTimeInput = document.getElementById('startTime');
        const endTimeInput = document.getElementById('endTime');
        const totalHoursInput = document.getElementById('totalHours');

        function calculateHours() {
            if (startTimeInput.value && endTimeInput.value) {
                const startParts = startTimeInput.value.split(':');
                const endParts = endTimeInput.value.split(':');
                
                if (startParts.length === 2 && endParts.length === 2) {
                    const startHour = parseInt(startParts[0]);
                    const startMinute = parseInt(startParts[1]);
                    const endHour = parseInt(endParts[0]);
                    const endMinute = parseInt(endParts[1]);
                    
                    let totalMinutes = (endHour * 60 + endMinute) - (startHour * 60 + startMinute);
                    if (totalMinutes < 0) totalMinutes += 24 * 60;
                    
                    const totalHours = Math.round((totalMinutes / 60) * 10) / 10;
                    totalHoursInput.value = totalHours;
                }
            }
        }

        if (startTimeInput && endTimeInput) {
            startTimeInput._flatpickr.config.onChange.push(calculateHours);
            endTimeInput._flatpickr.config.onChange.push(calculateHours);
        }
    }

    // ===== DRAFT SAVING =====
    document.getElementById('saveAsDraft')?.addEventListener('click', function() {
        alert('Draft saved successfully. You can come back and complete this entry later.');
        const saveStatus = document.querySelector('.save-status span');
        if (saveStatus) {
            const now = new Date();
            const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            saveStatus.textContent = `Last saved: Today at ${timeString}`;
        }
    });
});