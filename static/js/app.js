class LearningHub {
    constructor() {
        this.currentField = null;
        this.theme = localStorage.getItem('hub-theme') || 'light';
        this.init();
    }

    init() {
        this.initTheme();
        this.initNavigation();
        this.initAnimations();
        this.initSearchFunctionality();
        this.initProgressTracking();
        this.bindEvents();
    }

    // Theme Management
    initTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('hub-theme', this.theme);
        this.updateThemeIcon();
        
        // Animate theme transition
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    updateThemeIcon() {
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    // Navigation Enhancement
    initNavigation() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // Active navigation highlighting
        this.highlightActiveNavigation();
    }

    highlightActiveNavigation() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // Animation System
    initAnimations() {
        // Initialize AOS (Animate On Scroll)
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true,
                offset: 100
            });
        }

        // Card hover animations
        this.initCardAnimations();
        
        // Loading animations
        this.initLoadingAnimations();
    }

    initCardAnimations() {
        document.querySelectorAll('.card, .field-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px) scale(1.02)';
                card.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
                card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
                card.style.boxShadow = '';
            });
        });
    }

    initLoadingAnimations() {
        // Add loading states to buttons
        document.querySelectorAll('button[type="submit"], .btn-loading').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!btn.disabled) {
                    this.showButtonLoading(btn);
                }
            });
        });
    }

    showButtonLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        button.disabled = true;

        // Reset after 3 seconds (fallback)
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 3000);
    }

    // Search Functionality
    initSearchFunctionality() {
        const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
        
        searchInputs.forEach(input => {
            let debounceTimer;
            
            input.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.performSearch(e.target.value, e.target);
                }, 300);
            });

            // Add search shortcuts
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    e.target.value = '';
                    this.performSearch('', e.target);
                }
            });
        });

        // Global search shortcut (Ctrl/Cmd + K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-input, input[type="search"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
        });
    }

    performSearch(query, inputElement) {
        const container = inputElement.closest('.search-container') || document;
        const searchableItems = container.querySelectorAll('.searchable-item, .card');
        let visibleCount = 0;

        searchableItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const isVisible = text.includes(query.toLowerCase());
            
            item.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;

            // Highlight search terms
            if (query && isVisible) {
                this.highlightSearchTerm(item, query);
            } else {
                this.removeHighlight(item);
            }
        });

        // Show/hide no results message
        this.toggleNoResultsMessage(container, visibleCount === 0 && query !== '');
    }

    highlightSearchTerm(element, term) {
        // Remove existing highlights
        this.removeHighlight(element);
        
        if (!term) return;

        const regex = new RegExp(`(${term})`, 'gi');
        this.highlightInElement(element, regex);
    }

    highlightInElement(element, regex) {
        element.querySelectorAll('*').forEach(child => {
            if (child.children.length === 0) {
                const text = child.textContent;
                if (regex.test(text)) {
                    child.innerHTML = text.replace(regex, '<mark class="search-highlight">$1</mark>');
                }
            }
        });
    }

    removeHighlight(element) {
        element.querySelectorAll('.search-highlight').forEach(highlight => {
            highlight.outerHTML = highlight.innerHTML;
        });
    }

    toggleNoResultsMessage(container, show) {
        let noResultsMsg = container.querySelector('.no-results-message');
        
        if (show && !noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'no-results-message text-center py-5';
            noResultsMsg.innerHTML = `
                <div class="text-muted">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <h4>No results found</h4>
                    <p>Try adjusting your search terms</p>
                </div>
            `;
            container.appendChild(noResultsMsg);
        } else if (!show && noResultsMsg) {
            noResultsMsg.remove();
        }
    }

    // Progress Tracking
    initProgressTracking() {
        this.trackTimeOnPage();
        this.trackInteractions();
    }

    trackTimeOnPage() {
        this.pageStartTime = Date.now();
        
        window.addEventListener('beforeunload', () => {
            const timeSpent = Date.now() - this.pageStartTime;
            this.saveProgressData('time_spent', { 
                page: window.location.pathname, 
                time: timeSpent 
            });
        });
    }

    trackInteractions() {
        // Track button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn, a')) {
                this.saveProgressData('interaction', {
                    type: 'click',
                    element: e.target.className,
                    page: window.location.pathname
                });
            }
        });
    }

    saveProgressData(type, data) {
        const progressData = JSON.parse(localStorage.getItem('learning-progress') || '[]');
        progressData.push({
            type,
            data,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 100 entries
        if (progressData.length > 100) {
            progressData.splice(0, progressData.length - 100);
        }
        
        localStorage.setItem('learning-progress', JSON.stringify(progressData));
    }

    // Utility Functions
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Copied to clipboard!', 'success', 2000);
            });
        } else {
            // Fallback
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showNotification('Copied to clipboard!', 'success', 2000);
            } catch (err) {
                this.showNotification('Failed to copy', 'error', 2000);
            }
            
            document.body.removeChild(textArea);
        }
    }

    // Event Binding
    bindEvents() {
        // Theme toggle
        const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }

        // Copy code buttons
        document.querySelectorAll('.copy-code-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const codeElement = btn.parentElement.querySelector('code');
                if (codeElement) {
                    this.copyToClipboard(codeElement.textContent);
                }
            });
        });

        // Form enhancements
        this.enhanceForms();
    }

    enhanceForms() {
        document.querySelectorAll('form').forEach(form => {
            // Add loading state on submit
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    this.showButtonLoading(submitBtn);
                }
            });

            // Real-time validation
            form.querySelectorAll('input[required], textarea[required]').forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        field.classList.toggle('is-valid', isValid);
        field.classList.toggle('is-invalid', !isValid);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.learningHub = new LearningHub();
});

// Global functions for backward compatibility
function toggleTheme() {
    window.learningHub?.toggleTheme();
}

function copyCode(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const code = element.querySelector('code') || element;
        window.learningHub?.copyToClipboard(code.textContent);
    }
}
