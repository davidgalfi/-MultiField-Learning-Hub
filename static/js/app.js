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


// static/js/app.js - Final JavaScript enhancements
// Enhanced LearningHub class with recipe functionality
class LearningHub {
    constructor() {
        this.currentField = null;
        this.theme = localStorage.getItem('hub-theme') || 'light';
        this.notifications = [];
        this.init();
    }

    init() {
        this.initTheme();
        this.initNavigation();
        this.initAnimations();
        this.initSearchFunctionality();
        this.initProgressTracking();
        this.initMathEditor();
        this.initRecipeFeatures();
        this.bindEvents();
    }

    // Recipe-specific functionality
    initRecipeFeatures() {
        this.initRecipeRating();
        this.initMealPlanning();
        this.initNutritionCalculator();
    }

    initRecipeRating() {
        document.querySelectorAll('.recipe-rating').forEach(rating => {
            const stars = rating.querySelectorAll('.fa-star');
            const recipeId = rating.closest('[data-recipe-id]')?.dataset.recipeId;
            
            if (stars.length && recipeId) {
                stars.forEach((star, index) => {
                    star.addEventListener('click', () => {
                        this.rateRecipe(recipeId, index + 1);
                    });
                    
                    star.addEventListener('mouseenter', () => {
                        this.highlightStars(stars, index + 1);
                    });
                });
                
                rating.addEventListener('mouseleave', () => {
                    this.resetStars(stars, rating.dataset.currentRating || 0);
                });
            }
        });
    }

    rateRecipe(recipeId, rating) {
        fetch(`/recipes/api/recipes/${recipeId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rating: rating })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateRecipeRating(recipeId, data.new_rating, data.rating_count);
                this.showNotification('Rating saved!', 'success', 2000);
            } else {
                this.showNotification('Failed to save rating', 'error', 3000);
            }
        })
        .catch(error => {
            console.error('Error rating recipe:', error);
            this.showNotification('Failed to save rating', 'error', 3000);
        });
    }

    highlightStars(stars, rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.remove('text-muted');
                star.classList.add('text-warning');
            } else {
                star.classList.remove('text-warning');
                star.classList.add('text-muted');
            }
        });
    }

    resetStars(stars, currentRating) {
        stars.forEach((star, index) => {
            if (index < currentRating) {
                star.classList.remove('text-muted');
                star.classList.add('text-warning');
            } else {
                star.classList.remove('text-warning');
                star.classList.add('text-muted');
            }
        });
    }

    updateRecipeRating(recipeId, newRating, ratingCount) {
        const ratingElement = document.querySelector(`[data-recipe-id="${recipeId}"] .recipe-rating`);
        if (ratingElement) {
            const stars = ratingElement.querySelectorAll('.fa-star');
            this.resetStars(stars, newRating);
            
            const countElement = ratingElement.querySelector('.rating-count');
            if (countElement) {
                countElement.textContent = `(${ratingCount})`;
            }
            
            ratingElement.dataset.currentRating = newRating;
        }
    }

    initMealPlanning() {
        // Weekly meal plan generation
        const generatePlanBtn = document.getElementById('generate-meal-plan');
        if (generatePlanBtn) {
            generatePlanBtn.addEventListener('click', () => {
                this.generateWeeklyMealPlan();
            });
        }
    }

    generateWeeklyMealPlan() {
        const preferences = {
            include_breakfast: document.getElementById('include-breakfast')?.checked ?? true,
            include_lunch: document.getElementById('include-lunch')?.checked ?? true,
            include_dinner: document.getElementById('include-dinner')?.checked ?? true,
        };

        this.showButtonLoading(document.getElementById('generate-meal-plan'));

        fetch('/recipes/api/weekly-meal-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(preferences)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.displayMealPlan(data.meal_plan);
                this.showNotification('Meal plan generated!', 'success', 3000);
            }
        })
        .catch(error => {
            console.error('Error generating meal plan:', error);
            this.showNotification('Failed to generate meal plan', 'error', 3000);
        })
        .finally(() => {
            this.hideButtonLoading(document.getElementById('generate-meal-plan'));
        });
    }

    displayMealPlan(mealPlan) {
        const mealPlanContainer = document.getElementById('meal-plan-container');
        if (!mealPlanContainer) return;

        let html = '<div class="row g-3">';
        
        Object.keys(mealPlan).forEach(day => {
            const dayPlan = mealPlan[day];
            html += `
                <div class="col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">${day.charAt(0).toUpperCase() + day.slice(1)}</h6>
                        </div>
                        <div class="card-body">
            `;
            
            Object.keys(dayPlan).forEach(mealType => {
                const meal = dayPlan[mealType];
                html += `
                    <div class="meal-item mb-2">
                        <strong>${mealType.charAt(0).toUpperCase() + mealType.slice(1)}:</strong><br>
                        <small>${meal.title}</small>
                        ${meal.prep_time ? `<br><small class="text-muted">${meal.prep_time}min</small>` : ''}
                    </div>
                `;
            });
            
            html += '</div></div></div>';
        });
        
        html += '</div>';
        mealPlanContainer.innerHTML = html;
    }

    initNutritionCalculator() {
        // Nutrition calculation functionality
        const calcBtn = document.getElementById('calculate-nutrition');
        if (calcBtn) {
            calcBtn.addEventListener('click', () => {
                this.calculateNutrition();
            });
        }
    }

    // Math Editor Integration
    initMathEditor() {
        // Initialize MathJax if not already loaded
        if (!window.MathJax) {
            this.loadMathJax();
        }
    }

    loadMathJax() {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
        script.async = true;
        
        window.MathJax = {
            tex: {
                inlineMath: [['\\(', '\\)']],
                displayMath: [['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            },
            options: {
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
            },
            startup: {
                ready() {
                    MathJax.startup.defaultReady();
                    console.log('MathJax loaded successfully');
                }
            }
        };
        
        document.head.appendChild(script);
    }

    // Enhanced notification system
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible notification`;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        this.notifications.push(notification);
        
        // Auto-remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    notification.remove();
                    this.notifications = this.notifications.filter(n => n !== notification);
                }, 300);
            }
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Enhanced button loading states
    showButtonLoading(button) {
        if (!button) return;
        
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        button.disabled = true;
    }

    hideButtonLoading(button) {
        if (!button) return;
        
        button.innerHTML = button.dataset.originalText || button.innerHTML;
        button.disabled = false;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.learningHub = new LearningHub();
    
    // Initialize math rendering on existing content
    if (window.MathJax && window.MathJax.typesetPromise) {
        MathJax.typesetPromise().then(() => {
            console.log('Initial math rendering complete');
        });
    }
});

// Global functions for templates
function openMathEditor() {
    const modal = new bootstrap.Modal(document.getElementById('mathEditorModal'));
    modal.show();
}

function addRecipe() {
    window.location.href = '/recipes/create';
}

function createMathPost() {
    window.location.href = '/mathematics/blog/create';
}

function addProblem() {
    window.location.href = '/mathematics/problems/create';
}