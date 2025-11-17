document.addEventListener('DOMContentLoaded', function() {
    // ===== TAB SWITCHING =====
    initTabs();

    // ===== BUDGET TRACKING VARIABLES =====
    let dailyMaterials = [];
    let dailyEquipment = [];
    let dailyOtherCosts = [];
    let dailyDelays = [];
    let dailyOvertime = [];
    let dailySubcontractors = [];
    window.projectData = window.projectData || [];

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

        // Calculate costs when items are added - functions defined in template
        // Removed duplicate event listeners to avoid conflicts
    }

    // Material and equipment functions moved to template to avoid conflicts
    // These are now handled by inline JavaScript in the HTML template

    // Other cost function moved to template to avoid conflicts

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
    
    // ===== BUDGET AND FORM FUNCTIONS =====
    function updateBudgetSummary() {
        let dailyTotal = 0;
        
        // Calculate labor costs from worker type inputs
        document.querySelectorAll('.count-input').forEach(countInput => {
            const count = parseInt(countInput.value) || 0;
            const rateInputId = countInput.id.replace('Count', 'Rate');
            const rateInput = document.getElementById(rateInputId);
            const rate = parseFloat(rateInput?.value) || 0;
            dailyTotal += count * rate;
        });
        
        // Calculate overtime costs
        dailyTotal += dailyOvertime.reduce((sum, item) => sum + (item.personnel * item.hours * item.rate), 0);
        
        // Calculate subcontractor costs
        dailyTotal += dailySubcontractors.reduce((sum, item) => sum + item.cost, 0);
        
        // Calculate from stored arrays
        dailyTotal += dailyMaterials.reduce((sum, item) => sum + item.cost, 0);
        dailyTotal += dailyEquipment.reduce((sum, item) => sum + item.cost, 0);
        dailyTotal += dailyOtherCosts.reduce((sum, item) => sum + item.cost, 0);
        
        const dailyCostElement = document.getElementById('dailyCost');
        if (dailyCostElement) {
            dailyCostElement.value = dailyTotal.toLocaleString('en-PH', {minimumFractionDigits: 2});
        }
        
        // Get project budget and calculate remaining
        const projectSelect = document.querySelector('select[name="project"]');
        if (projectSelect?.value && window.projectData) {
            const selectedProject = window.projectData.find(p => p.id == projectSelect.value);
            if (selectedProject) {
                const runningCost = selectedProject.spent + dailyTotal;
                const remainingBudget = selectedProject.budget - runningCost;
                
                const runningCostElement = document.getElementById('runningCost');
                const remainingBudgetElement = document.getElementById('remainingBudget');
                
                if (runningCostElement) {
                    runningCostElement.value = runningCost.toLocaleString('en-PH', {minimumFractionDigits: 2});
                }
                if (remainingBudgetElement) {
                    remainingBudgetElement.value = remainingBudget.toLocaleString('en-PH', {minimumFractionDigits: 2});
                }
            }
        }
    }
    
    // Material functions
    window.addMaterial = function() {
        const name = document.getElementById('materialName').value;
        const quantity = parseFloat(document.getElementById('materialQuantity').value) || 0;
        const unit = document.getElementById('materialUnit').value;
        const cost = parseFloat(document.getElementById('materialCost').value) || 0;
        const supplier = document.getElementById('materialSupplier').value;
        const delivery_time = document.getElementById('materialDeliveryTime').value;
        
        if (name && quantity && unit && cost) {
            const material = { name, quantity, unit, cost, supplier, delivery_time };
            dailyMaterials.push(material);
            
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content">
                    <strong>${name}</strong> - ${quantity} ${unit} - ₱${cost.toLocaleString('en-PH', {minimumFractionDigits: 2})}<br>
                    ${supplier ? `Supplier: ${supplier}` : ''}${delivery_time ? ` | Delivery: ${delivery_time}` : ''}
                </div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeMaterial(this, ${dailyMaterials.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('materialsList').appendChild(listItem);
            
            // Clear inputs
            ['materialName', 'materialQuantity', 'materialUnit', 'materialCost', 'materialSupplier', 'materialDeliveryTime'].forEach(id => {
                document.getElementById(id).value = '';
            });
            
            updateBudgetSummary();
        }
    }
    
    // Equipment functions
    window.addEquipment = function() {
        const name = document.getElementById('equipmentName').value;
        const operator = document.getElementById('equipmentOperator').value;
        const hours = parseFloat(document.getElementById('equipmentHours').value) || 0;
        const fuel = parseFloat(document.getElementById('equipmentFuel').value) || 0;
        const cost = parseFloat(document.getElementById('equipmentCost').value) || 0;
        
        if (name && hours && cost) {
            const equipment = { name, operator, hours, fuel, cost };
            dailyEquipment.push(equipment);
            
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content">
                    <strong>${name}</strong>${operator ? ` (${operator})` : ''} - ${hours} hours${fuel ? ` - ${fuel}L fuel` : ''} - ₱${cost.toLocaleString('en-PH', {minimumFractionDigits: 2})}
                </div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeEquipment(this, ${dailyEquipment.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('equipmentList').appendChild(listItem);
            
            // Clear inputs
            ['equipmentName', 'equipmentOperator', 'equipmentHours', 'equipmentFuel', 'equipmentCost'].forEach(id => {
                document.getElementById(id).value = '';
            });
            
            updateBudgetSummary();
        }
    }
    
    // Other cost functions
    window.addOtherCost = function() {
        const name = document.getElementById('otherCostName').value;
        const cost = parseFloat(document.getElementById('otherCostAmount').value) || 0;
        
        if (name && cost) {
            const otherCost = { name, cost };
            dailyOtherCosts.push(otherCost);
            
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content">
                    <strong>${name}</strong> - ₱${cost.toLocaleString('en-PH', {minimumFractionDigits: 2})}
                </div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeOtherCost(this, ${dailyOtherCosts.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('otherCostsList').appendChild(listItem);
            
            // Clear inputs
            ['otherCostName', 'otherCostAmount'].forEach(id => {
                document.getElementById(id).value = '';
            });
            
            updateBudgetSummary();
        }
    }
    
    // Overtime functions
    window.addOvertime = function() {
        const personnel = parseInt(document.getElementById('overtimePersonnel').value) || 0;
        const role = document.getElementById('overtimeRole').value;
        const hours = parseInt(document.getElementById('overtimeHours').value) || 0;
        const rate = parseFloat(document.getElementById('overtimeRate').value) || 0;
        
        if (personnel && role && hours && rate) {
            const overtime = { personnel, role, hours, rate };
            dailyOvertime.push(overtime);
            
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content">
                    <strong>${personnel} ${role} personnel</strong> - ${hours} hours @ ₱${rate}/hr = ₱${(personnel * hours * rate).toLocaleString('en-PH', {minimumFractionDigits: 2})}
                </div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeOvertime(this, ${dailyOvertime.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('overtimeList').appendChild(listItem);
            
            // Clear inputs
            ['overtimePersonnel', 'overtimeRole', 'overtimeHours', 'overtimeRate'].forEach(id => {
                document.getElementById(id).value = '';
            });
            
            updateBudgetSummary();
        }
    }
    
    // Subcontractor functions
    window.addSubcontractor = function() {
        console.log('DEBUG: addSubcontractor called');
        const selectElement = document.getElementById('subcontractorSelect');
        const customInput = document.getElementById('subcontractorCustom');
        const workInput = document.getElementById('subcontractorWork');
        const costInput = document.getElementById('subcontractorCost');
        
        console.log('DEBUG: Input values:', {
            select: selectElement?.value,
            custom: customInput?.value,
            work: workInput?.value,
            cost: costInput?.value
        });
        
        let subcontractorName = '';
        let subcontractorType = '';
        let contactInfo = '';
        const workDescription = workInput.value.trim();
        const cost = parseFloat(costInput.value) || 0;
        
        // Check if dropdown is selected
        if (selectElement.value) {
            const selectedOption = selectElement.options[selectElement.selectedIndex];
            subcontractorName = selectedOption.text.split(' - ')[0];
            subcontractorType = selectedOption.getAttribute('data-type');
            const contact = selectedOption.getAttribute('data-contact');
            const phone = selectedOption.getAttribute('data-phone');
            if (contact || phone) {
                contactInfo = ` (${contact || 'Contact'}${phone ? ': ' + phone : ''})`;
            }
        } else if (customInput.value.trim()) {
            subcontractorName = customInput.value.trim();
            subcontractorType = 'Custom';
        }
        
        console.log('DEBUG: Processed values:', {
            name: subcontractorName,
            type: subcontractorType,
            work: workDescription,
            cost: cost
        });
        
        if (subcontractorName && (workDescription || cost > 0)) {
            const subcontractor = {
                name: subcontractorName,
                company: subcontractorType,
                work: workDescription || `${subcontractorType} work`,
                cost: cost
            };
            dailySubcontractors.push(subcontractor);
            console.log('DEBUG: Added subcontractor to array:', subcontractor);
            console.log('DEBUG: dailySubcontractors now contains:', dailySubcontractors);
            
            const displayText = workDescription ? 
                `${subcontractorName}${contactInfo} - ${workDescription}` : 
                `${subcontractorName}${contactInfo} - ${subcontractorType} work`;
            
            const costText = cost > 0 ? `<br>Daily Cost: ₱${cost.toLocaleString('en-PH', {minimumFractionDigits: 2})}` : '';
                
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content"><strong>${displayText}</strong>${costText}</div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeSubcontractor(this, ${dailySubcontractors.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('subcontractorList').appendChild(listItem);
            
            // Clear inputs
            selectElement.value = '';
            customInput.value = '';
            workInput.value = '';
            costInput.value = '';
            
            updateBudgetSummary();
        } else {
            console.log('DEBUG: Validation failed - missing name or work/cost');
            if (window.globalModal) {
                window.globalModal.error(
                    'Missing Information',
                    'Please provide either a work description or daily cost for the subcontractor.'
                );
            } else {
                alert('Please provide either a work description or daily cost for the subcontractor.');
            }
        }
    }
    
    // Delay functions
    window.addDelay = function() {
        const type = document.getElementById('delayType').value;
        const impact = document.getElementById('delayImpact').value;
        const description = document.getElementById('delayDescription').value.trim();
        const start_time = document.getElementById('delayStartTime').value;
        const end_time = document.getElementById('delayEndTime').value;
        const duration = parseFloat(document.getElementById('delayDuration').value) || 0;
        const solution = document.getElementById('delaySolution').value.trim();
        
        if (type && impact && description) {
            const delay = { type, impact, description, start_time, end_time, duration, solution };
            dailyDelays.push(delay);
            
            const listItem = document.createElement('div');
            listItem.className = 'entry-item';
            listItem.innerHTML = `
                <div class="entry-content">
                    <strong>${type} - ${impact}</strong><br>
                    ${description}<br>
                    ${start_time && end_time ? `Time: ${start_time} - ${end_time} (${duration}h)` : ''}
                </div>
                <div class="entry-actions">
                    <button type="button" class="entry-action-btn delete" onclick="removeDelay(this, ${dailyDelays.length - 1})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            document.getElementById('delayList').appendChild(listItem);
            
            // Clear inputs
            ['delayType', 'delayImpact', 'delayDescription', 'delayStartTime', 'delayEndTime', 'delayDuration', 'delaySolution'].forEach(id => {
                document.getElementById(id).value = '';
            });
        }
    }
    
    // Remove functions
    window.removeMaterial = function(button, index) {
        dailyMaterials.splice(index, 1);
        button.closest('.entry-item').remove();
        updateBudgetSummary();
    }
    
    window.removeEquipment = function(button, index) {
        dailyEquipment.splice(index, 1);
        button.closest('.entry-item').remove();
        updateBudgetSummary();
    }
    
    window.removeOtherCost = function(button, index) {
        dailyOtherCosts.splice(index, 1);
        button.closest('.entry-item').remove();
        updateBudgetSummary();
    }
    
    window.removeOvertime = function(button, index) {
        dailyOvertime.splice(index, 1);
        button.closest('.entry-item').remove();
        updateBudgetSummary();
    }
    
    window.removeSubcontractor = function(button, index) {
        console.log('DEBUG: Removing subcontractor at index:', index);
        dailySubcontractors.splice(index, 1);
        console.log('DEBUG: dailySubcontractors after removal:', dailySubcontractors);
        button.closest('.entry-item').remove();
        updateBudgetSummary();
    }
    
    window.removeDelay = function(button, index) {
        dailyDelays.splice(index, 1);
        button.closest('.entry-item').remove();
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
        const signatureCanvas = document.getElementById('signatureCanvas');
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
        
        function clearSignature() {
            if (signaturePad) {
                signaturePad.clear();
            }
        }
        
        const clearBtn = document.getElementById('clearSupervisorSignature');
        if (clearBtn) {
            clearBtn.addEventListener('click', clearSignature);
        }
        
        // Handle form submission for canvas signatures
        const form = document.getElementById('siteEntryForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                console.log('Form submission - checking signature');
                if (signaturePad && !signaturePad.isEmpty()) {
                    console.log('Signature found, adding to form data');
                    // Remove any existing signature data input
                    const existingInput = form.querySelector('input[name="signature_data"]');
                    if (existingInput) {
                        existingInput.remove();
                    }
                    // Create hidden input for signature data
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'signature_data';
                    hiddenInput.value = signatureCanvas.toDataURL();
                    form.appendChild(hiddenInput);
                    console.log('Signature data added to form');
                } else {
                    console.log('No signature found or signature pad is empty');
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
                const signatureCanvas = document.getElementById('signatureCanvas');
                let hasSignature = false;
                
                // Check if canvas has signature
                if (signatureCanvas && window.signaturePad) {
                    hasSignature = !window.signaturePad.isEmpty();
                    console.log('Signature validation - hasSignature:', hasSignature);
                }
                
                if (!hasSignature) {
                    event.preventDefault();
                    console.log('Form submission prevented - missing signature');
                    const sigFeedback = document.querySelector('.signature-container .invalid-feedback');
                    if (sigFeedback) sigFeedback.style.display = 'block';
                    if (window.__focusTabForElement) window.__focusTabForElement(signatureCanvas);
                } else {
                    console.log('Signature validation passed');
                    const sigFeedback = document.querySelector('.signature-container .invalid-feedback');
                    if (sigFeedback) sigFeedback.style.display = 'none';
                }
            });
        }
    }

    function initDynamicLists() {
        setupDynamicList('addTask', 'taskInput', 'taskList');
        
        // Setup all button event listeners
        setTimeout(() => {
            const buttonMappings = [
                { id: 'addMaterial', func: window.addMaterial },
                { id: 'addEquipment', func: window.addEquipment },
                { id: 'addOtherCost', func: window.addOtherCost },
                { id: 'addOvertime', func: window.addOvertime },
                { id: 'addSubcontractor', func: window.addSubcontractor },
                { id: 'addDelay', func: window.addDelay }
            ];
            
            buttonMappings.forEach(mapping => {
                const btn = document.getElementById(mapping.id);
                if (btn && mapping.func) {
                    btn.addEventListener('click', mapping.func);
                }
            });
            
            // Auto-calculate delay duration
            ['delayStartTime', 'delayEndTime'].forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.addEventListener('change', function() {
                        const start = document.getElementById('delayStartTime').value;
                        const end = document.getElementById('delayEndTime').value;
                        if (start && end) {
                            const startTime = new Date('1970-01-01T' + start + ':00');
                            const endTime = new Date('1970-01-01T' + end + ':00');
                            const diff = (endTime - startTime) / (1000 * 60 * 60);
                            const durationElement = document.getElementById('delayDuration');
                            if (durationElement) {
                                durationElement.value = diff > 0 ? diff.toFixed(1) : '';
                            }
                        }
                    });
                }
            });
            
            // Update budget when labor inputs change
            document.querySelectorAll('.count-input').forEach(input => {
                input.addEventListener('input', updateBudgetSummary);
            });
            
            document.querySelectorAll('input[id$="Rate"]').forEach(input => {
                input.addEventListener('input', updateBudgetSummary);
            });
            
            // Update budget when project changes
            const projectSelect = document.querySelector('select[name="project"]');
            if (projectSelect) {
                projectSelect.addEventListener('change', updateBudgetSummary);
            }
        }, 100);
        
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
        
        function setupExistingItemActions(list) {
            const items = list.querySelectorAll('.entry-item');
            items.forEach(item => setupItemActions(item));
        }
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

    // ===== FORM SUBMISSION HANDLING =====
    const form = document.getElementById('siteEntryForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('DEBUG: Form submission - dailySubcontractors:', dailySubcontractors);
            console.log('DEBUG: Form submission - dailyMaterials:', dailyMaterials);
            console.log('DEBUG: Form submission - dailyEquipment:', dailyEquipment);
            
            // Ensure signature is captured
            const signatureCanvas = document.getElementById('signatureCanvas');
            if (signatureCanvas && window.signaturePad && !window.signaturePad.isEmpty()) {
                // Remove any existing signature data input
                const existingSignatureInput = form.querySelector('input[name="signature_data"]');
                if (existingSignatureInput) {
                    existingSignatureInput.remove();
                }
                // Create hidden input for signature data
                const signatureInput = document.createElement('input');
                signatureInput.type = 'hidden';
                signatureInput.name = 'signature_data';
                signatureInput.value = signatureCanvas.toDataURL();
                this.appendChild(signatureInput);
                console.log('DEBUG: Signature data captured and added to form');
            }
            
            // Add JSON data for all dynamic content
            const jsonData = [
                { name: 'materials_json', data: dailyMaterials },
                { name: 'equipment_json', data: dailyEquipment },
                { name: 'delays_json', data: dailyDelays },
                { name: 'overtime_json', data: dailyOvertime },
                { name: 'subcontractor_json', data: dailySubcontractors },
                { name: 'other_costs_json', data: dailyOtherCosts }
            ];
            
            jsonData.forEach(item => {
                if (item.data.length > 0) {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = item.name;
                    input.value = JSON.stringify(item.data);
                    console.log(`DEBUG: Adding ${item.name} with data:`, item.data);
                    this.appendChild(input);
                } else {
                    console.log(`DEBUG: Skipping ${item.name} - no data (length: ${item.data.length})`);
                }
            });
        });
    }
    
    // Make functions globally accessible
    window.updateBudgetSummary = updateBudgetSummary;
    window.dailyMaterials = dailyMaterials;
    window.dailyEquipment = dailyEquipment;
    window.dailyOtherCosts = dailyOtherCosts;
    window.dailyDelays = dailyDelays;
    window.dailyOvertime = dailyOvertime;
    window.dailySubcontractors = dailySubcontractors;
});