// Inventory-specific JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle item filtering
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        // Auto-submit form on select change
        const selectFields = filterForm.querySelectorAll('select');
        selectFields.forEach(select => {
            select.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
    
    // Handle group attributes in forms
    const addAttributeBtn = document.getElementById('add-attribute');
    if (addAttributeBtn) {
        addAttributeBtn.addEventListener('click', function() {
            // This is now handled in the template
        });
        
        // Attach remove handlers to existing remove buttons
        const removeButtons = document.querySelectorAll('.remove-attribute');
        removeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // This is now handled in the template
            });
        });
    }
    
    // Item quantity increment/decrement
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(control => {
        const minusBtn = control.querySelector('.minus-btn');
        const plusBtn = control.querySelector('.plus-btn');
        const input = control.querySelector('input');
        
        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 0;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    // Trigger change event
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
            
            plusBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 0;
                input.value = currentValue + 1;
                // Trigger change event
                input.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }
    });
    
    // Handle dynamic attribute fields for item form
    const itemForm = document.querySelector('form.item-form');
    if (itemForm) {
        const groupSelect = itemForm.querySelector('#id_group');
        const attributesContainer = itemForm.querySelector('#attributes-container');
        
        if (groupSelect && attributesContainer) {
            groupSelect.addEventListener('change', function() {
                const groupId = this.value;
                if (!groupId) {
                    attributesContainer.innerHTML = '';
                    return;
                }
                
                // Fetch attributes for the selected group
                fetch(`/inventory/api/group/${groupId}/attributes/`)
                    .then(response => response.json())
                    .then(data => {
                        attributesContainer.innerHTML = '';
                        
                        if (data.length === 0) {
                            attributesContainer.innerHTML = '<p>No attributes defined for this group.</p>';
                            return;
                        }
                        
                        data.forEach(attr => {
                            const formGroup = document.createElement('div');
                            formGroup.className = 'form-group';
                            
                            const label = document.createElement('label');
                            label.textContent = attr.name;
                            label.setAttribute('for', `attr_${attr.id}`);
                            
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.name = `attribute_${attr.id}`;
                            input.id = `attr_${attr.id}`;
                            input.className = 'form-control';
                            input.value = attr.value || '';
                            
                            formGroup.appendChild(label);
                            formGroup.appendChild(input);
                            attributesContainer.appendChild(formGroup);
                        });
                    })
                    .catch(error => {
                        console.error('Error fetching group attributes:', error);
                        attributesContainer.innerHTML = '<p class="text-danger">Error loading attributes.</p>';
                    });
            });
            
            // Trigger change event on load if a group is already selected
            if (groupSelect.value) {
                groupSelect.dispatchEvent(new Event('change'));
            }
        }
    }
    
    // Item table row actions
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (button.classList.contains('delete-btn') && !confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
    
    // Item search functionality
    const searchInput = document.querySelector('.search-input');
    const itemTable = document.querySelector('.data-table');
    
    if (searchInput && itemTable) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = itemTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}); 