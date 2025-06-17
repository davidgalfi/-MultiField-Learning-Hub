class MathEditor {
    constructor() {
        this.input = null;
        this.preview = null;
        this.debounceTimer = null;
        this.cursorPosition = 0;
        this.isInitialized = false;
        this.mathJaxReady = false;
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeEditor());
        } else {
            this.initializeEditor();
        }
    }

    initializeEditor() {
        console.log('Initializing Math Editor...');
        
        const modal = document.getElementById('mathEditorModal');
        if (modal) {
            modal.addEventListener('shown.bs.modal', () => {
                this.setupElements();
                this.setupEventListeners();
                if (!this.isInitialized) {
                    this.ensureMathJax();
                    this.isInitialized = true;
                }
            });
        } else {
            console.warn('Math editor modal not found');
        }
    }

    setupElements() {
        this.input = document.getElementById('mathInput');
        this.preview = document.getElementById('mathPreview');
        
        if (!this.input || !this.preview) {
            console.error('Math editor elements not found');
            return false;
        }
        
        console.log('Math editor elements found and initialized');
        return true;
    }

    ensureMathJax() {
        if (window.MathJax && window.MathJax.typesetPromise) {
            console.log('MathJax already loaded and ready');
            this.mathJaxReady = true;
            this.renderInitialMath();
            return;
        }

        console.log('Loading/configuring MathJax...');
        
        // Enhanced MathJax configuration
        window.MathJax = {
            tex: {
                inlineMath: [['\\(', '\\)']],
                displayMath: [['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true,
                packages: {'[+]': ['ams', 'newcommand', 'configmacros', 'autoload', 'require']}
            },
            options: {
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
            },
            startup: {
                ready: () => {
                    MathJax.startup.defaultReady();
                    console.log('MathJax fully loaded and ready');
                    this.mathJaxReady = true;
                    this.renderInitialMath();
                    
                    // Test MathJax with a simple equation
                    this.testMathJaxRendering();
                }
            }
        };

        // Load MathJax if not already loaded
        if (!document.getElementById('MathJax-script')) {
            const script = document.createElement('script');
            script.id = 'MathJax-script';
            script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
            script.async = true;
            document.head.appendChild(script);
        }
    }

    testMathJaxRendering() {
        // Test if MathJax is working by rendering a simple equation
        const testDiv = document.createElement('div');
        testDiv.innerHTML = 'Test: \\(x^2 + y^2 = z^2\\)';
        testDiv.style.display = 'none';
        document.body.appendChild(testDiv);
        
        if (window.MathJax && window.MathJax.typesetPromise) {
            MathJax.typesetPromise([testDiv]).then(() => {
                console.log('MathJax test rendering successful');
                document.body.removeChild(testDiv);
            }).catch(err => {
                console.error('MathJax test rendering failed:', err);
                document.body.removeChild(testDiv);
            });
        }
    }

    renderInitialMath() {
        if (window.MathJax && window.MathJax.typesetPromise) {
            const toolbar = document.querySelector('.math-toolbar');
            if (toolbar) {
                MathJax.typesetPromise([toolbar]).then(() => {
                    console.log('Toolbar math symbols rendered');
                }).catch(err => {
                    console.error('Toolbar rendering error:', err);
                });
            }
        }
    }

    setupEventListeners() {
        if (!this.input) return;

        // Real-time preview update
        this.input.addEventListener('input', () => {
            this.updateCharCount();
            this.debouncePreview();
        });

        // Track cursor position
        ['click', 'keyup', 'selectionchange'].forEach(event => {
            this.input.addEventListener(event, () => {
                this.cursorPosition = this.input.selectionStart;
            });
        });

        // Keyboard shortcuts
        this.input.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        console.log('Math editor event listeners set up');
    }

    debouncePreview() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.updatePreview();
        }, 300);
    }

    updatePreview() {
        if (!this.preview || !this.input) {
            console.warn('Preview elements not available');
            return;
        }

        const latex = this.input.value.trim();
        console.log('Updating preview with:', latex);
        
        if (latex === '') {
            this.preview.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-eye fa-2x mb-2"></i>
                    <p>Preview will appear here</p>
                    <small>Try typing: \\frac{a}{b} or \\sqrt{x^2 + y^2}</small>
                </div>
            `;
            return;
        }

        // Wrap content for MathJax processing with proper delimiters
        let processedLatex = latex;
        
        // If the input doesn't have math delimiters, add them
        if (!latex.includes('\\(') && !latex.includes('\\[')) {
            // For display math (block)
            if (latex.includes('\\frac') || latex.includes('\\sum') || latex.includes('\\int')) {
                processedLatex = `\\[${latex}\\]`;
            } else {
                // For inline math
                processedLatex = `\\(${latex}\\)`;
            }
        }
        
        this.preview.innerHTML = `<div class="tex2jax_process">${processedLatex}</div>`;

        // Force MathJax re-rendering
        if (window.MathJax && window.MathJax.typesetPromise && this.mathJaxReady) {
            console.log('Rendering with MathJax...');
            
            MathJax.typesetPromise([this.preview]).then(() => {
                console.log('MathJax rendering completed successfully');
            }).catch((err) => {
                console.error('MathJax rendering error:', err);
                this.preview.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>LaTeX Error:</strong> ${err.message || 'Please check your syntax'}
                        <br><small class="text-muted">Input: ${latex}</small>
                    </div>
                `;
            });
        } else {
            console.warn('MathJax not ready yet');
            this.preview.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-spinner fa-spin me-2"></i>
                    Loading MathJax renderer...
                </div>
            `;
            
            // Retry after a short delay
            setTimeout(() => {
                if (this.mathJaxReady) {
                    this.updatePreview();
                }
            }, 1000);
        }
    }

    insertMath(latex) {
        if (!this.input) {
            console.warn('Math input not available');
            return;
        }

        const start = this.input.selectionStart;
        const end = this.input.selectionEnd;
        const text = this.input.value;
        
        const beforeCursor = text.substring(0, start);
        const afterCursor = text.substring(end);
        
        this.input.value = beforeCursor + latex + afterCursor;
        
        // Position cursor inside braces if they exist
        const braceIndex = latex.indexOf('{}');
        if (braceIndex !== -1) {
            this.input.selectionStart = this.input.selectionEnd = start + braceIndex + 1;
        } else {
            this.input.selectionStart = this.input.selectionEnd = start + latex.length;
        }
        
        this.input.focus();
        this.updateCharCount();
        this.debouncePreview();
    }

    updateCharCount() {
        const charCount = document.getElementById('charCount');
        if (charCount && this.input) {
            charCount.textContent = this.input.value.length;
        }
    }

    // Add test function for debugging
    testPreview() {
        console.log('Testing preview...');
        if (this.input) {
            this.input.value = '\\frac{a}{b}';
            this.updateCharCount();
            this.updatePreview();
        }
    }

    insertMatrix(rows, cols) {
        let matrix = '\\begin{pmatrix}\n';
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                matrix += 'a_{' + (i+1) + (j+1) + '}';
                if (j < cols - 1) matrix += ' & ';
            }
            if (i < rows - 1) matrix += ' \\\\\n';
        }
        
        matrix += '\n\\end{pmatrix}';
        this.insertMath(matrix);
    }

    insertVector() {
        const vector = '\\vec{v} = \\begin{pmatrix} v_1 \\\\ v_2 \\\\ v_3 \\end{pmatrix}';
        this.insertMath(vector);
    }

    insertTemplate(templateName) {
        const templates = {
            quadratic: '\\[ x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a} \\]',
            taylor: '\\[ f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n \\]',
            binomial: '\\[ (x + y)^n = \\sum_{k=0}^{n} \\binom{n}{k} x^{n-k} y^k \\]'
        };

        if (templates[templateName]) {
            this.insertMath(templates[templateName]);
        }
    }

    clearInput() {
        if (this.input) {
            this.input.value = '';
            this.updateCharCount();
            this.updatePreview();
            this.input.focus();
        }
    }

    copyToClipboard() {
        if (!this.input) return;

        navigator.clipboard.writeText(this.input.value).then(() => {
            this.showNotification('LaTeX copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            this.showNotification('Failed to copy to clipboard', 'error');
        });
    }

    insertIntoPost() {
        if (!this.input) return;

        const latex = this.input.value;
        
        // Try to find any active text editor
        const editors = [
            document.querySelector('#post-content'),
            document.querySelector('#problem-text'),
            document.querySelector('.content-editor'),
            document.querySelector('textarea[name="content"]')
        ];

        let inserted = false;
        for (let editor of editors) {
            if (editor && editor.offsetParent !== null) {
                if (editor.tagName === 'TEXTAREA') {
                    const start = editor.selectionStart || 0;
                    const end = editor.selectionEnd || 0;
                    const text = editor.value;
                    
                    editor.value = text.substring(0, start) + latex + text.substring(end);
                    editor.selectionStart = editor.selectionEnd = start + latex.length;
                    editor.focus();
                    
                    this.showNotification('LaTeX inserted into editor!', 'success');
                    
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('mathEditorModal'));
                    if (modal) modal.hide();
                    
                    inserted = true;
                    break;
                }
            }
        }
        
        if (!inserted) {
            this.showNotification('No active editor found', 'warning');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Global functions for button onclick events
function insertMath(latex) {
    if (window.mathEditor) {
        window.mathEditor.insertMath(latex);
    } else {
        console.warn('Math editor not initialized');
    }
}

function insertMatrix(rows, cols) {
    if (window.mathEditor) {
        window.mathEditor.insertMatrix(rows, cols);
    }
}

function insertVector() {
    if (window.mathEditor) {
        window.mathEditor.insertVector();
    }
}

function insertTemplate(templateName) {
    if (window.mathEditor) {
        window.mathEditor.insertTemplate(templateName);
    }
}

function clearInput() {
    if (window.mathEditor) {
        window.mathEditor.clearInput();
    }
}

function copyToClipboard() {
    if (window.mathEditor) {
        window.mathEditor.copyToClipboard();
    }
}

function insertIntoPost() {
    if (window.mathEditor) {
        window.mathEditor.insertIntoPost();
    }
}

// Function to open math editor modal
function openMathEditor() {
    console.log('Opening math editor...');
    const modal = document.getElementById('mathEditorModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        console.error('Math editor modal not found');
        alert('Math editor not available. Please check the page setup.');
    }
}

// Initialize math editor when the script loads
console.log('Math editor script loaded');
window.mathEditor = new MathEditor();
