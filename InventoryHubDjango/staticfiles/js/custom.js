// Custom JavaScript for InventoryHub

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add confirmation dialogs to delete buttons
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Item search functionality
    const searchInput = document.getElementById('item-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const itemTable = document.querySelector('.item-table tbody');
            const rows = itemTable.querySelectorAll('tr');
            
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

    // Toggle mobile sidebar
    const sidebarToggler = document.querySelector('.sidebar-toggler');
    if (sidebarToggler) {
        sidebarToggler.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }

    // Quantity input validation
    document.querySelectorAll('input[type="number"].quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            if (parseInt(this.value) < 0) {
                this.value = 0;
            }
        });
    });

    // Item form dynamic attribute fields
    const addAttributeBtn = document.getElementById('add-attribute');
    if (addAttributeBtn) {
        addAttributeBtn.addEventListener('click', function() {
            const attributesContainer = document.getElementById('attributes-container');
            const attributeIndex = attributesContainer.children.length;
            
            const attributeRow = document.createElement('div');
            attributeRow.className = 'row mb-3 attribute-row';
            attributeRow.innerHTML = `
                <div class="col-5">
                    <input type="text" name="attribute_name_${attributeIndex}" class="form-control" placeholder="Attribute Name">
                </div>
                <div class="col-5">
                    <input type="text" name="attribute_value_${attributeIndex}" class="form-control" placeholder="Attribute Value">
                </div>
                <div class="col-2">
                    <button type="button" class="btn btn-danger remove-attribute"><i class="fas fa-times"></i></button>
                </div>
            `;
            
            attributesContainer.appendChild(attributeRow);
            
            // Add remove event listener to the new row
            attributeRow.querySelector('.remove-attribute').addEventListener('click', function() {
                attributeRow.remove();
            });
        });
    }

    // Initialize any existing remove attribute buttons
    document.querySelectorAll('.remove-attribute').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.attribute-row').remove();
        });
    });

    // Chart initialization for dashboard (if Chart.js is available)
    if (typeof Chart !== 'undefined') {
        const ctx = document.getElementById('inventoryChart');
        if (ctx) {
            // Sample data - would be replaced with actual data from backend
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Inventory Movement',
                        data: [12, 19, 3, 5, 2, 3],
                        backgroundColor: 'rgba(13, 110, 253, 0.5)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
});

// Confirmation dialogs for delete actions
function setupConfirmations() {
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

// Handle quantity changes
function setupQuantityHandlers() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const itemId = this.getAttribute('data-item-id');
            const newQuantity = this.value;
            
            // Update visual indicators
            updateStockStatus(itemId, newQuantity);
            
            // Optional: Update via AJAX to avoid page reload
            // updateQuantityAjax(itemId, newQuantity);
        });
    });
}

// Update stock status visual indicators
function updateStockStatus(itemId, quantity) {
    const statusElement = document.querySelector(`.status-indicator[data-item-id="${itemId}"]`);
    const threshold = statusElement ? parseInt(statusElement.getAttribute('data-threshold')) : 5;
    
    if (statusElement) {
        statusElement.classList.remove('status-in-stock', 'status-low-stock', 'status-out-of-stock');
        
        if (quantity <= 0) {
            statusElement.classList.add('status-out-of-stock');
            statusElement.textContent = 'Out of Stock';
        } else if (quantity <= threshold) {
            statusElement.classList.add('status-low-stock');
            statusElement.textContent = 'Low Stock';
        } else {
            statusElement.classList.add('status-in-stock');
            statusElement.textContent = 'In Stock';
        }
    }
}

// Setup search functionality
function setupSearch() {
    const searchInput = document.querySelector('#search-input');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const items = document.querySelectorAll('.searchable-item');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
}

// Optional: AJAX functions for future use
function updateQuantityAjax(itemId, quantity) {
    // Example function for future AJAX implementation
    fetch('/api/items/update-quantity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Get CSRF token from cookies
function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
} 