// Modern Mobile UI/UX JavaScript - Material Design 3 Implementation

document.addEventListener('DOMContentLoaded', function() {
    
    // Mobile-specific initialization
    if (window.innerWidth <= 768) {
        initializeMobileFeatures();
    }
    
    // Responsive handling
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            initializeMobileFeatures();
        }
    });
    
    function initializeMobileFeatures() {
        initializeBottomNavigation();
        initializeAppBar();
        initializeRippleEffects();
        initializeTouchGestures();
        initializeMaterialComponents();
        initializeSearchFunctionality();
        initializeChatFeatures();
        initializeFormEnhancements();
    }
    
    // Bottom Navigation
    function initializeBottomNavigation() {
        const bottomNavItems = document.querySelectorAll('.mobile-bottom-nav-item');
        
        bottomNavItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // Remove active class from all items
                bottomNavItems.forEach(navItem => navItem.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Add ripple effect
                createRipple(this, e);
            });
        });
    }
    
    // App Bar functionality
    function initializeAppBar() {
        const backBtn = document.getElementById('mobileBackBtn');
        const menuBtn = document.getElementById('mobileMenuBtn');
        
        // Back button functionality
        if (backBtn) {
            backBtn.addEventListener('click', function() {
                if (window.history.length > 1) {
                    window.history.back();
                } else {
                    window.location.href = '/';
                }
            });
            
            // Show back button on non-home pages
            if (window.location.pathname !== '/') {
                backBtn.style.visibility = 'visible';
            }
        }
        
        // Menu button functionality
        if (menuBtn) {
            menuBtn.addEventListener('click', function() {
                // Toggle search or menu functionality
                toggleMobileSearch();
            });
        }
    }
    
    // Ripple Effects
    function initializeRippleEffects() {
        const rippleElements = document.querySelectorAll('.md-button, .md-card, .mobile-bottom-nav-item, .md-chip');
        
        rippleElements.forEach(element => {
            element.addEventListener('click', function(e) {
                createRipple(this, e);
            });
        });
    }
    
    function createRipple(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            z-index: 1000;
        `;
        
        // Ensure element has relative positioning
        if (getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }
        
        element.appendChild(ripple);
        
        // Remove ripple after animation
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
    
    // Touch Gestures
    function initializeTouchGestures() {
        let startY = 0;
        let startX = 0;
        let isScrolling = false;
        
        // Pull to refresh
        document.addEventListener('touchstart', function(e) {
            startY = e.touches[0].pageY;
            startX = e.touches[0].pageX;
            isScrolling = false;
        }, { passive: true });
        
        document.addEventListener('touchmove', function(e) {
            if (!isScrolling) {
                const currentY = e.touches[0].pageY;
                const currentX = e.touches[0].pageX;
                const diffY = Math.abs(currentY - startY);
                const diffX = Math.abs(currentX - startX);
                
                if (diffY > diffX) {
                    isScrolling = true;
                    
                    // Pull to refresh logic
                    if (window.pageYOffset === 0 && currentY > startY && diffY > 100) {
                        showPullToRefreshIndicator();
                    }
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', function() {
            hidePullToRefreshIndicator();
        }, { passive: true });
        
        // Swipe gestures for navigation
        initializeSwipeNavigation();
    }
    
    function initializeSwipeNavigation() {
        let startX = 0;
        let startTime = 0;
        
        document.addEventListener('touchstart', function(e) {
            startX = e.touches[0].pageX;
            startTime = Date.now();
        }, { passive: true });
        
        document.addEventListener('touchend', function(e) {
            const endX = e.changedTouches[0].pageX;
            const endTime = Date.now();
            const diffX = endX - startX;
            const diffTime = endTime - startTime;
            
            // Swipe detection (minimum distance and maximum time)
            if (Math.abs(diffX) > 100 && diffTime < 300) {
                if (diffX > 0) {
                    // Swipe right - go back
                    if (window.history.length > 1) {
                        window.history.back();
                    }
                } else {
                    // Swipe left - could implement forward navigation
                    // or other functionality
                }
            }
        }, { passive: true });
    }
    
    // Material Components
    function initializeMaterialComponents() {
        initializeTextFields();
        initializeChips();
        initializeFAB();
        initializeCards();
    }
    
    function initializeTextFields() {
        const textFields = document.querySelectorAll('.md-text-field-input');
        
        textFields.forEach(input => {
            // Handle focus and blur for floating labels
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                if (!this.value) {
                    this.parentElement.classList.remove('filled');
                } else {
                    this.parentElement.classList.add('filled');
                }
            });
            
            // Check initial state
            if (input.value) {
                input.parentElement.classList.add('filled');
            }
        });
    }
    
    function initializeChips() {
        const chips = document.querySelectorAll('.md-chip');
        
        chips.forEach(chip => {
            chip.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Toggle active state for filter chips
                if (this.dataset.toggle === 'filter') {
                    this.classList.toggle('active');
                } else {
                    // For navigation chips, remove active from siblings
                    const siblings = this.parentElement.querySelectorAll('.md-chip');
                    siblings.forEach(sibling => sibling.classList.remove('active'));
                    this.classList.add('active');
                }
                
                // Trigger filter event
                const filterEvent = new CustomEvent('chipFilter', {
                    detail: {
                        chip: this,
                        value: this.dataset.value,
                        active: this.classList.contains('active')
                    }
                });
                document.dispatchEvent(filterEvent);
            });
        });
    }
    
    function initializeFAB() {
        const fab = document.querySelector('.md-fab');
        
        if (fab) {
            fab.addEventListener('click', function() {
                // Add scale animation
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);
                
                // Trigger FAB action
                const fabEvent = new CustomEvent('fabClick');
                document.dispatchEvent(fabEvent);
            });
            
            // Hide/show FAB on scroll
            let lastScrollTop = 0;
            window.addEventListener('scroll', function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    fab.style.transform = 'translateY(100px)';
                } else {
                    // Scrolling up
                    fab.style.transform = 'translateY(0)';
                }
                
                lastScrollTop = scrollTop;
            }, { passive: true });
        }
    }
    
    function initializeCards() {
        const cards = document.querySelectorAll('.md-card, .md-service-card, .md-category-card');
        
        cards.forEach(card => {
            // Add hover effect for touch devices
            card.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            }, { passive: true });
            
            card.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            }, { passive: true });
        });
    }
    
    // Search Functionality
    function initializeSearchFunctionality() {
        const searchInputs = document.querySelectorAll('.md-search-input, .modern-search-input');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                
                // Show loading state
                showSearchLoading(this);
                
                // Debounced search
                searchTimeout = setTimeout(() => {
                    performSearch(this.value);
                    hideSearchLoading(this);
                }, 500);
            });
            
            // Voice search (if supported)
            if ('webkitSpeechRecognition' in window) {
                addVoiceSearchButton(input);
            }
        });
    }
    
    function performSearch(query) {
        // Implement search logic
        const searchEvent = new CustomEvent('mobileSearch', {
            detail: { query: query }
        });
        document.dispatchEvent(searchEvent);
    }
    
    function showSearchLoading(input) {
        const container = input.parentElement;
        container.classList.add('loading');
    }
    
    function hideSearchLoading(input) {
        const container = input.parentElement;
        container.classList.remove('loading');
    }
    
    function addVoiceSearchButton(input) {
        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'md-voice-search-btn';
        voiceBtn.innerHTML = '<i class=\"fas fa-microphone\"></i>';
        voiceBtn.style.cssText = `
            position: absolute;
            right: 16px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--md-secondary);
            font-size: 16px;
            cursor: pointer;
        `;
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(voiceBtn);
        
        voiceBtn.addEventListener('click', function() {
            startVoiceSearch(input);
        });
    }
    
    function startVoiceSearch(input) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            input.placeholder = 'Listening...';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            performSearch(transcript);
        };
        
        recognition.onerror = function() {
            input.placeholder = 'Voice search failed';
        };
        
        recognition.onend = function() {
            input.placeholder = 'Search services...';
        };
        
        recognition.start();
    }
    
    // Chat Features
    function initializeChatFeatures() {
        const chatContainer = document.querySelector('.md-chat-container');
        
        if (chatContainer) {
            initializeChatInput();
            initializeChatScroll();
            initializeTypingIndicator();
        }
    }
    
    function initializeChatInput() {
        const chatInput = document.querySelector('.md-chat-input');
        const sendButton = document.querySelector('.md-chat-send-button');
        
        if (chatInput && sendButton) {
            // Auto-resize textarea
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 100) + 'px';
            });
            
            // Send on Enter (but not Shift+Enter)
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            sendButton.addEventListener('click', sendMessage);
        }
    }
    
    function sendMessage() {
        const chatInput = document.querySelector('.md-chat-input');
        const message = chatInput.value.trim();
        
        if (message) {
            // Add message to chat
            addMessageToChat(message, 'sent');
            
            // Clear input
            chatInput.value = '';
            chatInput.style.height = 'auto';
            
            // Scroll to bottom
            scrollChatToBottom();
            
            // Show typing indicator
            showTypingIndicator();
            
            // Simulate response (in real app, this would be WebSocket)
            setTimeout(() => {
                hideTypingIndicator();
                // Add simulated response
            }, 2000);
        }
    }
    
    function addMessageToChat(message, type) {
        const chatMessages = document.querySelector('.md-chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `md-chat-message ${type}`;
        messageElement.innerHTML = `
            ${message}
            <div class=\"md-chat-timestamp\">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        messageElement.classList.add('md-fade-in');
    }
    
    function initializeChatScroll() {
        const chatMessages = document.querySelector('.md-chat-messages');
        
        if (chatMessages) {
            // Scroll to bottom on load
            scrollChatToBottom();
            
            // Handle keyboard appearance on mobile
            window.addEventListener('resize', function() {
                setTimeout(scrollChatToBottom, 300);
            });
        }
    }
    
    function scrollChatToBottom() {
        const chatMessages = document.querySelector('.md-chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    function initializeTypingIndicator() {
        // Create typing indicator element
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'md-typing-indicator';
        typingIndicator.style.display = 'none';
        typingIndicator.innerHTML = `
            <div class=\"md-chat-message received\">
                <div class=\"typing-dots\">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        const chatMessages = document.querySelector('.md-chat-messages');
        if (chatMessages) {
            chatMessages.appendChild(typingIndicator);
        }
    }
    
    function showTypingIndicator() {
        const indicator = document.querySelector('.md-typing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
            scrollChatToBottom();
        }
    }
    
    function hideTypingIndicator() {
        const indicator = document.querySelector('.md-typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    // Form Enhancements
    function initializeFormEnhancements() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add loading states
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('button[type=\"submit\"], .md-button');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                    
                    // Add spinner
                    const spinner = document.createElement('div');
                    spinner.className = 'md-spinner';
                    submitBtn.appendChild(spinner);
                }
            });
            
            // Validate on blur
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateField(this);
                });
            });
        });
    }
    
    function validateField(field) {
        const isValid = field.checkValidity();
        const container = field.closest('.md-text-field') || field.parentElement;
        
        if (!isValid) {
            container.classList.add('error');
            showFieldError(field, field.validationMessage);
        } else {
            container.classList.remove('error');
            hideFieldError(field);
        }
    }
    
    function showFieldError(field, message) {
        let errorElement = field.parentElement.querySelector('.md-field-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'md-field-error';
            field.parentElement.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.cssText = `
            color: var(--md-error);
            font-size: 12px;
            margin-top: 4px;
            animation: mdFadeIn 0.2s ease-out;
        `;
    }
    
    function hideFieldError(field) {
        const errorElement = field.parentElement.querySelector('.md-field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    // Utility Functions
    function toggleMobileSearch() {
        const searchContainer = document.querySelector('.md-search-bar, .modern-search-container');
        
        if (searchContainer) {
            searchContainer.style.display = searchContainer.style.display === 'none' ? 'block' : 'none';
            
            if (searchContainer.style.display !== 'none') {
                const searchInput = searchContainer.querySelector('input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        }
    }
    
    function showPullToRefreshIndicator() {
        // Create or show pull to refresh indicator
        let indicator = document.querySelector('.pull-to-refresh-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-to-refresh-indicator';
            indicator.innerHTML = '<div class=\"md-spinner\"></div>';
            indicator.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--md-surface);
                padding: 16px;
                border-radius: 50%;
                box-shadow: var(--md-elevation-2);
                z-index: 1001;
            `;
            document.body.appendChild(indicator);
        }
        
        indicator.style.display = 'block';
    }
    
    function hidePullToRefreshIndicator() {
        const indicator = document.querySelector('.pull-to-refresh-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--md-secondary);
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .md-text-field.error .md-text-field-input {
            border-color: var(--md-error);
        }
        
        .md-text-field.error .md-text-field-label {
            color: var(--md-error);
        }
    `;
    document.head.appendChild(style);
});

// Export utility functions for use in other scripts
window.MobileMaterial = {
    showToast: function(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `md-toast md-toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--md-surface);
            color: var(--md-on-surface);
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: var(--md-elevation-3);
            z-index: 1002;
            animation: mdSlideUp 0.3s ease-out;
            max-width: 90%;
            text-align: center;
        `;
        
        if (type === 'error') {
            toast.style.background = 'var(--md-error)';
            toast.style.color = 'var(--md-on-primary)';
        } else if (type === 'success') {
            toast.style.background = 'var(--md-success)';
            toast.style.color = 'var(--md-on-primary)';
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'mdFadeIn 0.3s ease-out reverse';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    },
    
    showBottomSheet: function(content, title = '') {
        const overlay = document.createElement('div');
        overlay.className = 'md-bottom-sheet-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1003;
            animation: mdFadeIn 0.3s ease-out;
        `;
        
        const bottomSheet = document.createElement('div');
        bottomSheet.className = 'md-bottom-sheet';
        bottomSheet.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--md-surface);
            border-radius: 16px 16px 0 0;
            padding: 24px;
            max-height: 80vh;
            overflow-y: auto;
            animation: mdSlideUp 0.3s ease-out;
        `;
        
        if (title) {
            bottomSheet.innerHTML = `
                <h3 style="margin: 0 0 16px 0; font-family: var(--md-font-display);">${title}</h3>
                ${content}
            `;
        } else {
            bottomSheet.innerHTML = content;
        }
        
        overlay.appendChild(bottomSheet);
        document.body.appendChild(overlay);
        
        // Close on overlay click
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.style.animation = 'mdFadeIn 0.3s ease-out reverse';
                bottomSheet.style.animation = 'mdSlideUp 0.3s ease-out reverse';
                setTimeout(() => {
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 300);
            }
        });
        
        return overlay;
    }
};

