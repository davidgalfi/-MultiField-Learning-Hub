class MathEditor {
    constructor() {
        this.input = null;
        this.preview = null;
        this.debounceTimer = null;
        this.cursorPosition = 0;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.input = document.getElementById('mathInput');
            this.preview = document.getElementById('mathPreview');
            this.setupEventListeners();
            this.loadMathJax();
        });
    }

    loadMathJax() {
        // Load MathJax if not already loaded
        if (!window.MathJax) {
            const script = document.createElement('script');
            script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6';
            document.head.appendChild(script);

            const mathJaxScript = document.createElement('script');
            mathJaxScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
            mathJaxScript.async = true;
            document.head.appendChild(mathJaxScript);

            // Configure MathJax
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
                }
            };
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
        this.input.addEventListener('selectionchange', () => {
            this.cursorPosition = this.input.selectionStart;
        });

        this.input.addEventListener('click', () => {
            this.cursorPosition = this.input.selectionStart;
        });

        this.input.addEventListener('keyup', () => {
            this.cursorPosition = this.input.selectionStart;
        });

        // Keyboard shortcuts
        this.input.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + B for bold math
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            this.insertMath('\\mathbf{}');
        }
        
        // Ctrl/Cmd + I for italic math
        if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
            e.preventDefault();
            this.insertMath('\\mathit{}');
        }
        
        // Ctrl/Cmd + F for fraction
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            this.insertMath('\\frac{}{}');
        }
        
        // Ctrl/Cmd + R for square root
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            this.insertMath('\\sqrt{}');
        }
    }

    updateCharCount() {
        const charCount = document.getElementById('charCount');
        if (charCount && this.input) {
            charCount.textContent = this.input.value.length;
        }
    }

    debouncePreview() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.updatePreview();
        }, 300);
    }

    updatePreview() {
        if (!this.preview || !this.input) return;

        const latex = this.input.value;
        
        if (latex.trim() === '') {
            this.preview.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-eye fa-2x mb-2"></i>
                    <p>Preview will appear here</p>
                </div>
            `;
            return;
        }

        // Wrap content for MathJax processing
        this.preview.innerHTML = `<div class="tex2jax_process">${latex}</div>`;

        // Re-render MathJax
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([this.preview]).catch((err) => {
                console.log('MathJax error:', err);
                this.preview.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        LaTeX syntax error. Please check your input.
                    </div>
                `;
            });
        }
    }

    insertMath(latex) {
        if (!this.input) return;

        const start = this.input.selectionStart;
        const end = this.input.selectionEnd;
        const text = this.input.value;
        
        // Find cursor position within braces
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
            fourier: '\\[ \\mathcal{F}\\{f(t)\\} = \\int_{-\\infty}^{\\infty} f(t) e^{-2\\pi i \\xi t} dt \\]',
            binomial: '\\[ (x + y)^n = \\sum_{k=0}^{n} \\binom{n}{k} x^{n-k} y^k \\]',
            definite_integral: '\\[ \\int_a^b f(x) \\, dx = F(b) - F(a) \\]'
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
            // Show success notification
            this.showNotification('LaTeX copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            this.showNotification('Failed to copy to clipboard', 'error');
        });
    }

    insertIntoPost() {
        if (!this.input) return;

        const latex = this.input.value;
        
        // Find active text editor (could be TinyMCE, CodeMirror, or plain textarea)
        const editors = [
            document.querySelector('.blog-editor textarea'),
            document.querySelector('.content-editor'),
            document.querySelector('#post-content'),
            document.querySelector('#problem-text')
        ];

        for (let editor of editors) {
            if (editor && editor.offsetParent !== null) { // Check if visible
                if (editor.tagName === 'TEXTAREA') {
                    const start = editor.selectionStart;
                    const end = editor.selectionEnd;
                    const text = editor.value;
                    
                    editor.value = text.substring(0, start) + latex + text.substring(end);
                    editor.selectionStart = editor.selectionEnd = start + latex.length;
                    editor.focus();
                    
                    this.showNotification('LaTeX inserted into editor!', 'success');
                    
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('mathEditorModal'));
                    if (modal) modal.hide();
                    
                    return;
                }
            }
        }
        
        this.showNotification('No active editor found', 'warning');
    }

    showNotification(message, type = 'info') {
        // Create notification element
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
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Global functions for button onclick events
function insertMath(latex) {
    window.mathEditor.insertMath(latex);
}

function insertMatrix(rows, cols) {
    window.mathEditor.insertMatrix(rows, cols);
}

function insertVector() {
    window.mathEditor.insertVector();
}

function insertTemplate(templateName) {
    window.mathEditor.insertTemplate(templateName);
}

function clearInput() {
    window.mathEditor.clearInput();
}

function copyToClipboard() {
    window.mathEditor.copyToClipboard();
}

function insertIntoPost() {
    window.mathEditor.insertIntoPost();
}

// Initialize math editor
window.mathEditor = new MathEditor();

// Function to open math editor modal
function openMathEditor() {
    const modal = new bootstrap.Modal(document.getElementById('mathEditorModal'));
    modal.show();
}
