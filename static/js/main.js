// Main JavaScript file for Apna Saathi

// Utility functions
const Utils = {
    // Show notification
    showNotification: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type} fade-in`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, duration);
    },

    // Format currency
    formatCurrency: function(amount, currency = '₹') {
        return currency + amount.toLocaleString('en-IN');
    },

    // Format date
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Validate email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate phone number (Indian format)
    validatePhone: function(phone) {
        const re = /^[6-9]\d{9}$/;
        return re.test(phone.replace(/\D/g, ''));
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// API functions
const API = {
    // Make API request
    request: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Upload file
    uploadFile: async function(file, url) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Upload failed! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }
};

// Form handling
const FormHandler = {
    // Initialize form validation
    init: function() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        });
    },

    // Handle form submission
    handleSubmit: function(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Validate form
        if (!this.validateForm(data)) {
            return false;
        }
        
        // Show loading state
        this.showLoading(form);
        
        // Submit form
        this.submitForm(form, data);
    },

    // Validate form data
    validateForm: function(data) {
        const errors = [];
        
        // Check required fields
        Object.keys(data).forEach(key => {
            if (data[key] === '' && document.querySelector(`[name="${key}"]`).hasAttribute('required')) {
                errors.push(`${key} is required`);
            }
        });
        
        // Validate email
        if (data.email && !Utils.validateEmail(data.email)) {
            errors.push('Please enter a valid email address');
        }
        
        // Validate phone
        if (data.phone && !Utils.validatePhone(data.phone)) {
            errors.push('Please enter a valid phone number');
        }
        
        if (errors.length > 0) {
            Utils.showNotification(errors.join(', '), 'error');
            return false;
        }
        
        return true;
    },

    // Show loading state
    showLoading: function(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        }
    },

    // Submit form
    submitForm: function(form, data) {
        // Simulate API call
        setTimeout(() => {
            Utils.showNotification('Form submitted successfully!', 'success');
            form.reset();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit';
            }
        }, 2000);
    }
};

// Search functionality
const SearchHandler = {
    // Initialize search
    init: function() {
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce(this.handleSearch.bind(this), 300));
        });
    },

    // Handle search
    handleSearch: function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const targetSelector = e.target.getAttribute('data-search');
        const items = document.querySelectorAll(targetSelector);
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
};

// Modal functionality
const ModalHandler = {
    // Initialize modals
    init: function() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', this.openModal.bind(this));
        });
        
        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
        
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.querySelector('.modal');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
    },

    // Open modal
    openModal: function(e) {
        const modalId = e.target.getAttribute('data-modal');
        const modal = document.getElementById(modalId);
        
        if (modal) {
            modal.classList.add('modal');
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    },

    // Close modal
    closeModal: function(modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
};

// Chart functionality (if needed)
const ChartHandler = {
    // Initialize charts
    init: function() {
        // Chart initialization code can be added here
        console.log('Charts initialized');
    }
};

// File upload functionality
const FileUploadHandler = {
    // Initialize file uploads
    init: function() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', this.handleFileSelect.bind(this));
        });
    },

    // Handle file selection
    handleFileSelect: function(e) {
        const file = e.target.files[0];
        if (file) {
            this.previewFile(file, e.target);
        }
    },

    // Preview file
    previewFile: function(file, input) {
        const previewContainer = input.parentElement.querySelector('.file-preview');
        if (previewContainer) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" alt="Preview" class="w-full h-32 object-cover rounded-lg">
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = `
                    <div class="p-4 bg-gray-100 rounded-lg">
                        <i class="fas fa-file text-2xl text-gray-400 mb-2"></i>
                        <p class="text-sm text-gray-600">${file.name}</p>
                    </div>
                `;
            }
        }
    }
};

// Local storage utilities
const Storage = {
    // Set item
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },

    // Get item
    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return null;
        }
    },

    // Remove item
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    },

    // Clear all
    clear: function() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
    }
};

// Theme handler
const ThemeHandler = {
    // Initialize theme
    init: function() {
        const savedTheme = Storage.get('theme') || 'light';
        this.setTheme(savedTheme);
        
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
            });
        }
    },

    // Set theme
    setTheme: function(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        Storage.set('theme', theme);
    }
};

// Initialize all handlers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all handlers
    FormHandler.init();
    SearchHandler.init();
    ModalHandler.init();
    ChartHandler.init();
    FileUploadHandler.init();
    ThemeHandler.init();
    
    // Add fade-in animation to elements
    const fadeElements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
    
    console.log('Apna Saathi application initialized');
});

// Export for use in other modules
window.ApnaSaathi = {
    Utils,
    API,
    FormHandler,
    SearchHandler,
    ModalHandler,
    ChartHandler,
    FileUploadHandler,
    Storage,
    ThemeHandler
}; 