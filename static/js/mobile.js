// Mobile-specific JavaScript enhancements for Neeget platform

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Touch-friendly table interactions
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(table => {
        if (window.innerWidth <= 576) {
            table.classList.add('table-mobile-stack');
            
            // Add data labels for mobile stacking
            const headers = table.querySelectorAll('thead th');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (headers[index]) {
                        cell.setAttribute('data-label', headers[index].textContent);
                    }
                });
            });
        }
    });
    
    // Mobile-friendly form enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Prevent zoom on input focus for iOS
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (window.innerWidth <= 768) {
                    // Scroll input into view
                    setTimeout(() => {
                        this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                }
            });
        });
        
        // Add loading state to form submissions
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Mobile-optimized modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            if (window.innerWidth <= 768) {
                document.body.style.overflow = 'hidden';
            }
        });
        
        modal.addEventListener('hide.bs.modal', function() {
            document.body.style.overflow = '';
        });
    });
    
    // Touch-friendly dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const menu = this.nextElementSibling;
                if (menu && menu.classList.contains('dropdown-menu')) {
                    menu.classList.toggle('show');
                }
            }
        });
    });
    
    // Mobile-specific chat enhancements
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        // Auto-scroll to bottom on mobile
        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Smooth scrolling for mobile
        chatMessages.style.scrollBehavior = 'smooth';
        
        // Handle keyboard appearance on mobile
        const messageInput = document.getElementById('messageInput');
        if (messageInput && window.innerWidth <= 768) {
            messageInput.addEventListener('focus', function() {
                setTimeout(() => {
                    scrollToBottom();
                }, 300);
            });
        }
    }
    
    // Mobile-friendly image handling
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            if (window.innerWidth <= 768) {
                // Ensure images don't overflow on mobile
                if (this.naturalWidth > window.innerWidth - 40) {
                    this.style.maxWidth = '100%';
                    this.style.height = 'auto';
                }
            }
        });
    });
    
    // Mobile pull-to-refresh simulation
    let startY = 0;
    let pullDistance = 0;
    const pullThreshold = 100;
    
    document.addEventListener('touchstart', function(e) {
        startY = e.touches[0].pageY;
    });
    
    document.addEventListener('touchmove', function(e) {
        if (window.pageYOffset === 0) {
            pullDistance = e.touches[0].pageY - startY;
            
            if (pullDistance > 0 && pullDistance < pullThreshold) {
                // Visual feedback for pull-to-refresh
                document.body.style.transform = `translateY(${pullDistance / 3}px)`;
            }
        }
    });
    
    document.addEventListener('touchend', function() {
        if (pullDistance > pullThreshold && window.pageYOffset === 0) {
            // Trigger refresh
            window.location.reload();
        }
        
        // Reset transform
        document.body.style.transform = '';
        pullDistance = 0;
    });
    
    // Mobile-specific search enhancements
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            // Debounce search on mobile
            searchTimeout = setTimeout(() => {
                // Trigger search functionality
                const event = new CustomEvent('mobileSearch', {
                    detail: { query: this.value }
                });
                document.dispatchEvent(event);
            }, 500);
        });
    });
    
    // Mobile-friendly date/time pickers
    const dateInputs = document.querySelectorAll('input[type="date"], input[type="datetime-local"]');
    dateInputs.forEach(input => {
        if (window.innerWidth <= 768) {
            // Ensure native mobile date picker is used
            input.setAttribute('pattern', '[0-9]{4}-[0-9]{2}-[0-9]{2}');
        }
    });
    
    // Mobile-specific error handling
    window.addEventListener('error', function(e) {
        if (window.innerWidth <= 768) {
            console.log('Mobile error:', e.error);
            // Could implement mobile-specific error reporting here
        }
    });
    
    // Mobile performance optimizations
    if (window.innerWidth <= 768) {
        // Lazy load images
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
        
        // Reduce animation on mobile for better performance
        const animations = document.querySelectorAll('.animate');
        animations.forEach(element => {
            element.style.animationDuration = '0.2s';
        });
    }
    
    // Mobile-specific accessibility enhancements
    if (window.innerWidth <= 768) {
        // Increase touch targets
        const buttons = document.querySelectorAll('button, .btn, a');
        buttons.forEach(button => {
            button.classList.add('touch-target');
        });
        
        // Add focus indicators for keyboard navigation
        const focusableElements = document.querySelectorAll('button, input, select, textarea, a');
        focusableElements.forEach(element => {
            element.addEventListener('focus', function() {
                this.style.outline = '2px solid #007bff';
                this.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', function() {
                this.style.outline = '';
                this.style.outlineOffset = '';
            });
        });
    }
    
    // Mobile viewport height fix for iOS
    function setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);
});

// Mobile-specific utility functions
const MobileUtils = {
    // Check if device is mobile
    isMobile: function() {
        return window.innerWidth <= 768;
    },
    
    // Check if device is touch-enabled
    isTouch: function() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },
    
    // Get device orientation
    getOrientation: function() {
        return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
    },
    
    // Vibrate device (if supported)
    vibrate: function(pattern = 100) {
        if (navigator.vibrate) {
            navigator.vibrate(pattern);
        }
    },
    
    // Show mobile-friendly toast notification
    showToast: function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} mobile-toast`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            min-width: 250px;
            text-align: center;
            border-radius: 6px;
            animation: slideDown 0.3s ease-out;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideUp 0.3s ease-in';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, duration);
    },
    
    // Handle mobile-specific form validation
    validateForm: function(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.style.borderColor = '#dc3545';
                isValid = false;
                
                // Show mobile-friendly error
                this.showToast(`Please fill in ${input.name || 'this field'}`, 'danger');
            } else {
                input.style.borderColor = '';
            }
        });
        
        return isValid;
    }
};

// Export for use in other scripts
window.MobileUtils = MobileUtils;

