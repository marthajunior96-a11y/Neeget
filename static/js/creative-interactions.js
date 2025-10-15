// Creative Neeget Interactions

class CreativeNeeget {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollEffects();
        this.setupMobileInteractions();
        this.setupAnimations();
        this.setupFormEnhancements();
        this.setupSearchFunctionality();
        this.setupCardInteractions();
    }

    setupScrollEffects() {
        // Navbar scroll effect
        const navbar = document.querySelector('.creative-nav');
        if (navbar) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            });
        }

        // Parallax effect for hero section
        const hero = document.querySelector('.creative-hero');
        if (hero) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                hero.style.transform = `translateY(${rate}px)`;
            });
        }

        // Fade in animations on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.creative-card, .creative-category-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupMobileInteractions() {
        // Mobile menu toggle
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileBackBtn = document.getElementById('mobileBackBtn');

        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', () => {
                this.showMobileSearch();
            });
        }

        if (mobileBackBtn) {
            mobileBackBtn.addEventListener('click', () => {
                this.hideMobileSearch();
            });
        }

        // Touch gestures for mobile
        this.setupTouchGestures();

        // Mobile bottom nav active state
        this.updateMobileNavActiveState();
    }

    setupTouchGestures() {
        let startY = 0;
        let currentY = 0;
        let isScrolling = false;

        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            currentY = e.touches[0].clientY;
            isScrolling = true;
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (isScrolling) {
                const diffY = startY - currentY;
                
                // Pull to refresh (when at top of page)
                if (window.scrollY === 0 && diffY < -100) {
                    this.triggerPullToRefresh();
                }
            }
            isScrolling = false;
        }, { passive: true });
    }

    triggerPullToRefresh() {
        // Show refresh indicator
        const refreshIndicator = document.createElement('div');
        refreshIndicator.className = 'refresh-indicator';
        refreshIndicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
        refreshIndicator.style.cssText = `
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-gradient);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 1001;
            font-size: 14px;
        `;
        document.body.appendChild(refreshIndicator);

        // Simulate refresh
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    showMobileSearch() {
        const searchOverlay = document.createElement('div');
        searchOverlay.className = 'mobile-search-overlay';
        searchOverlay.innerHTML = `
            <div class="mobile-search-container">
                <div class="mobile-search-header">
                    <button class="mobile-search-back">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <input type="text" class="mobile-search-input" placeholder="Search services..." autofocus>
                </div>
                <div class="mobile-search-results">
                    <div class="mobile-search-suggestions">
                        <div class="search-suggestion">House Cleaning</div>
                        <div class="search-suggestion">Web Development</div>
                        <div class="search-suggestion">Graphic Design</div>
                        <div class="search-suggestion">Tutoring</div>
                    </div>
                </div>
            </div>
        `;

        searchOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: white;
            z-index: 1002;
            animation: slideInFromTop 0.3s ease-out;
        `;

        document.body.appendChild(searchOverlay);

        // Add event listeners
        searchOverlay.querySelector('.mobile-search-back').addEventListener('click', () => {
            this.hideMobileSearch();
        });

        searchOverlay.querySelectorAll('.search-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const query = suggestion.textContent;
                window.location.href = `/services/browse?q=${encodeURIComponent(query)}`;
            });
        });
    }

    hideMobileSearch() {
        const overlay = document.querySelector('.mobile-search-overlay');
        if (overlay) {
            overlay.style.animation = 'slideOutToTop 0.3s ease-out';
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }

    updateMobileNavActiveState() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.mobile-bottom-nav-item');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                item.classList.add('active');
            } else if (href === '/' && currentPath === '/') {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    setupAnimations() {
        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInFromTop {
                from { transform: translateY(-100%); }
                to { transform: translateY(0); }
            }
            
            @keyframes slideOutToTop {
                from { transform: translateY(0); }
                to { transform: translateY(-100%); }
            }
            
            .mobile-search-overlay {
                animation: slideInFromTop 0.3s ease-out;
            }
            
            .mobile-search-container {
                padding: 20px;
            }
            
            .mobile-search-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .mobile-search-back {
                background: none;
                border: none;
                font-size: 18px;
                color: var(--text-primary);
                padding: 10px;
                border-radius: 50%;
                transition: var(--transition-fast);
            }
            
            .mobile-search-back:hover {
                background: var(--border-color);
            }
            
            .mobile-search-input {
                flex: 1;
                border: none;
                font-size: 18px;
                padding: 15px 0;
                background: transparent;
                border-bottom: 2px solid var(--border-color);
                transition: var(--transition-fast);
            }
            
            .mobile-search-input:focus {
                outline: none;
                border-bottom-color: var(--primary-color);
            }
            
            .mobile-search-suggestions {
                margin-top: 20px;
            }
            
            .search-suggestion {
                padding: 15px 0;
                border-bottom: 1px solid var(--border-color);
                cursor: pointer;
                transition: var(--transition-fast);
            }
            
            .search-suggestion:hover {
                color: var(--primary-color);
                padding-left: 10px;
            }
        `;
        document.head.appendChild(style);
    }

    setupFormEnhancements() {
        // Enhanced form interactions
        document.querySelectorAll('.creative-form-control').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('focused');
            });

            // Floating label effect
            if (input.value) {
                input.parentElement.classList.add('has-value');
            }

            input.addEventListener('input', () => {
                if (input.value) {
                    input.parentElement.classList.add('has-value');
                } else {
                    input.parentElement.classList.remove('has-value');
                }
            });
        });
    }

    setupSearchFunctionality() {
        const searchInput = document.querySelector('.creative-search-input');
        const searchBtn = document.querySelector('.creative-search-btn');

        if (searchInput && searchBtn) {
            const performSearch = () => {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `/services/browse?q=${encodeURIComponent(query)}`;
                }
            };

            searchBtn.addEventListener('click', performSearch);
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });

            // Search suggestions
            searchInput.addEventListener('input', () => {
                this.showSearchSuggestions(searchInput.value);
            });
        }
    }

    showSearchSuggestions(query) {
        if (query.length < 2) return;

        const suggestions = [
            'House Cleaning',
            'Web Development',
            'Graphic Design',
            'Tutoring',
            'Photography',
            'Plumbing',
            'Electrical Work',
            'Landscaping'
        ].filter(item => item.toLowerCase().includes(query.toLowerCase()));

        // Create suggestions dropdown
        let dropdown = document.querySelector('.search-suggestions-dropdown');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.className = 'search-suggestions-dropdown';
            dropdown.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border-radius: 0 0 20px 20px;
                box-shadow: var(--shadow-lg);
                max-height: 200px;
                overflow-y: auto;
                z-index: 10;
            `;
            document.querySelector('.creative-search').appendChild(dropdown);
        }

        dropdown.innerHTML = suggestions.map(suggestion => `
            <div class="search-suggestion-item" style="
                padding: 12px 20px;
                cursor: pointer;
                transition: var(--transition-fast);
                border-bottom: 1px solid var(--border-color);
            " onmouseover="this.style.background='var(--light-bg)'" 
               onmouseout="this.style.background='white'"
               onclick="window.location.href='/services/browse?q=${encodeURIComponent(suggestion)}'">
                <i class="fas fa-search" style="margin-right: 10px; color: var(--text-light);"></i>
                ${suggestion}
            </div>
        `).join('');

        // Hide dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.creative-search')) {
                    dropdown.remove();
                }
            }, { once: true });
        }, 100);
    }

    setupCardInteractions() {
        // Enhanced card hover effects
        document.querySelectorAll('.creative-card, .creative-category-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Service card quick actions
        document.querySelectorAll('.service-card').forEach(card => {
            const quickActions = document.createElement('div');
            quickActions.className = 'service-quick-actions';
            quickActions.innerHTML = `
                <button class="quick-action-btn" title="Quick Book">
                    <i class="fas fa-calendar-plus"></i>
                </button>
                <button class="quick-action-btn" title="Message Provider">
                    <i class="fas fa-comment"></i>
                </button>
                <button class="quick-action-btn" title="Save Service">
                    <i class="fas fa-heart"></i>
                </button>
            `;
            quickActions.style.cssText = `
                position: absolute;
                top: 15px;
                right: 15px;
                display: flex;
                gap: 5px;
                opacity: 0;
                transition: var(--transition-normal);
            `;

            card.style.position = 'relative';
            card.appendChild(quickActions);

            card.addEventListener('mouseenter', () => {
                quickActions.style.opacity = '1';
            });

            card.addEventListener('mouseleave', () => {
                quickActions.style.opacity = '0';
            });
        });
    }

    // Utility methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : 'primary'}-gradient);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 1003;
            animation: slideInFromRight 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutToRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    addToFavorites(serviceId) {
        // Simulate adding to favorites
        this.showNotification('Service added to favorites!', 'success');
    }

    quickBook(serviceId) {
        // Redirect to booking page
        window.location.href = `/bookings/book/${serviceId}`;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.creativeNeeget = new CreativeNeeget();
});

// Add additional CSS animations
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes slideInFromRight {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes slideOutToRight {
        from { transform: translateX(0); }
        to { transform: translateX(100%); }
    }
    
    .quick-action-btn {
        background: rgba(255, 255, 255, 0.9);
        border: none;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary-color);
        transition: var(--transition-fast);
        box-shadow: var(--shadow-md);
    }
    
    .quick-action-btn:hover {
        background: var(--primary-color);
        color: white;
        transform: scale(1.1);
    }
    
    .creative-form-group.focused .creative-form-label {
        color: var(--primary-color);
        transform: translateY(-5px);
    }
    
    .creative-form-group.has-value .creative-form-label {
        transform: translateY(-5px);
        font-size: 0.9rem;
    }
`;
document.head.appendChild(additionalStyles);

