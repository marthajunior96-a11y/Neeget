/* ============================================
   NEEGET ADMIN PANEL - INTERACTIVE FEATURES
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initSidebar();
    initUserDropdown();
    initAnimations();
    initTooltips();
    initSearch();
    initFilters();
    initModals();
});

/* ============================================
   SIDEBAR NAVIGATION
   ============================================ */

function initSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mainContent = document.getElementById('adminMain');

    // Toggle sidebar on mobile
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            
            // Add overlay
            if (sidebar.classList.contains('open')) {
                const overlay = document.createElement('div');
                overlay.className = 'sidebar-overlay';
                overlay.onclick = () => {
                    sidebar.classList.remove('open');
                    overlay.remove();
                };
                document.body.appendChild(overlay);
            }
        });
    }

    // Highlight active nav item
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
}

/* ============================================
   USER DROPDOWN MENU
   ============================================ */

function initUserDropdown() {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.querySelector('.user-dropdown');
    
    if (userMenu && dropdown) {
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenu.contains(e.target)) {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
            }
        });
    }
}

/* ============================================
   SMOOTH ANIMATIONS
   ============================================ */

function initAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe cards and stats
    document.querySelectorAll('.card, .stat-card').forEach(element => {
        observer.observe(element);
    });

    // Animate numbers (count up effect)
    animateNumbers();
}

function animateNumbers() {
    const numberElements = document.querySelectorAll('.stat-value');
    
    numberElements.forEach(element => {
        const target = parseFloat(element.textContent);
        if (isNaN(target)) return;
        
        let current = 0;
        const increment = target / 50;
        const duration = 1000;
        const stepTime = duration / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = formatNumber(target);
                clearInterval(timer);
            } else {
                element.textContent = formatNumber(Math.floor(current));
            }
        }, stepTime);
    });
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/* ============================================
   TOOLTIPS
   ============================================ */

function initTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const title = this.getAttribute('title');
            if (!title) return;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = title;
            tooltip.style.position = 'absolute';
            tooltip.style.background = 'rgba(0, 0, 0, 0.8)';
            tooltip.style.color = 'white';
            tooltip.style.padding = '0.5rem 0.75rem';
            tooltip.style.borderRadius = '8px';
            tooltip.style.fontSize = '0.8rem';
            tooltip.style.zIndex = '10000';
            tooltip.style.pointerEvents = 'none';
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this.tooltipElement = tooltip;
            
            // Remove title to prevent default tooltip
            this.setAttribute('data-title', title);
            this.removeAttribute('title');
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltipElement) {
                this.tooltipElement.remove();
                this.tooltipElement = null;
            }
            
            // Restore title
            const title = this.getAttribute('data-title');
            if (title) {
                this.setAttribute('title', title);
                this.removeAttribute('data-title');
            }
        });
    });
}

/* ============================================
   SEARCH FUNCTIONALITY
   ============================================ */

function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input, input[type="search"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.table-container')?.querySelector('table tbody');
            
            if (table) {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });
}

/* ============================================
   FILTER FUNCTIONALITY
   ============================================ */

function initFilters() {
    const filterSelects = document.querySelectorAll('.filter-select, select[data-filter]');
    
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const filterValue = this.value.toLowerCase();
            const filterColumn = this.getAttribute('data-filter-column') || 'status';
            const table = this.closest('.card')?.querySelector('table tbody');
            
            if (table) {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    if (filterValue === '' || filterValue === 'all') {
                        row.style.display = '';
                    } else {
                        const cell = row.querySelector(`[data-column="${filterColumn}"]`);
                        if (cell) {
                            const cellValue = cell.textContent.toLowerCase().trim();
                            row.style.display = cellValue.includes(filterValue) ? '' : 'none';
                        }
                    }
                });
            }
        });
    });
}

/* ============================================
   MODAL FUNCTIONALITY
   ============================================ */

function initModals() {
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

// Auto-hide alerts
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}, 100);

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    const container = document.querySelector('.flash-messages') || document.querySelector('.admin-content');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Format currency
function formatCurrency(amount, currency = '৳') {
    return `${currency}${parseFloat(amount).toFixed(2)}`;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce function
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

// Export functions to global scope
window.adminUtils = {
    scrollToTop,
    copyToClipboard,
    showNotification,
    formatCurrency,
    formatDate,
    debounce
};

/* ============================================
   NOTIFICATION DROPDOWN
   ============================================ */

function toggleNotifications(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('notificationDropdown');
    
    if (dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
    } else {
        dropdown.classList.add('show');
    }
}

// Close notification dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('notificationDropdown');
    const notificationWrapper = document.querySelector('.notification-wrapper');
    
    if (dropdown && notificationWrapper && !notificationWrapper.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});
