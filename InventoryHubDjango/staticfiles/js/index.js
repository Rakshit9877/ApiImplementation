// Common functionality for all pages
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });

    // Initialize alert message auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }

    // Active navigation highlighting
    highlightActiveNavItem();
    
    // Initialize dynamic form fields
    initFormsets();
    
    // Initialize delete confirmations
    initDeleteConfirmations();
});

// Show tooltip
function showTooltip(e) {
    const tooltipText = this.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = this.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.top = `${rect.top - tooltipRect.height - 10}px`;
    tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
    tooltip.style.opacity = '1';
    
    this._tooltip = tooltip;
}

// Hide tooltip
function hideTooltip() {
    if (this._tooltip) {
        document.body.removeChild(this._tooltip);
        this._tooltip = null;
    }
}

// Toggle mobile menu
function toggleMobileMenu() {
    const navItems = document.querySelector('.nav-items');
    navItems.classList.toggle('active');
}

// Highlight active navigation item based on current URL
function highlightActiveNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const link = item.getAttribute('href');
        if (link && currentPath.includes(link)) {
            item.classList.add('active');
        }
    });
}

// Initialize formsets for dynamic form fields
function initFormsets() {
    const addButtons = document.querySelectorAll('.add-formset-row');
    addButtons.forEach(button => {
        button.addEventListener('click', addFormsetRow);
    });

    const removeButtons = document.querySelectorAll('.remove-formset-row');
    removeButtons.forEach(button => {
        button.addEventListener('click', removeFormsetRow);
    });
}

// Add new formset row
function addFormsetRow(e) {
    e.preventDefault();
    
    const formsetContainer = this.closest('.formset-container');
    const template = formsetContainer.querySelector('.formset-template');
    const totalFormsInput = formsetContainer.querySelector('[name$="-TOTAL_FORMS"]');
    
    const newRow = template.cloneNode(true);
    newRow.classList.remove('formset-template');
    newRow.classList.add('formset-row');
    newRow.style.display = 'block';
    
    const formIndex = parseInt(totalFormsInput.value);
    const rowHtml = newRow.innerHTML.replace(/__prefix__/g, formIndex);
    newRow.innerHTML = rowHtml;
    
    const formsetRows = formsetContainer.querySelector('.formset-rows');
    formsetRows.appendChild(newRow);
    
    totalFormsInput.value = formIndex + 1;
    
    // Attach event listener to new remove button
    const removeButton = newRow.querySelector('.remove-formset-row');
    if (removeButton) {
        removeButton.addEventListener('click', removeFormsetRow);
    }
}

// Remove formset row
function removeFormsetRow(e) {
    e.preventDefault();
    
    const row = this.closest('.formset-row');
    row.style.display = 'none';
    
    // Find and mark the DELETE input if it exists
    const deleteInput = row.querySelector('input[name$="-DELETE"]');
    if (deleteInput) {
        deleteInput.value = 'on';
    } else {
        // If no DELETE input, completely remove the row
        row.parentNode.removeChild(row);
    }
}

// Initialize delete confirmations
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-btn, .btn-danger');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
} 