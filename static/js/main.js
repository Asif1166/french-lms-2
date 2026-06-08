// Main JavaScript for French LMS

document.addEventListener('DOMContentLoaded', function() {
    // ========== Navbar Scroll Effect ==========
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        let lastScroll = 0;
        
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }
    
    // ========== Auto-dismiss Alerts ==========
    const alerts = document.querySelectorAll('.custom-alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // ========== Video Progress Tracking ==========
    const videoPlayer = document.querySelector('video');
    if (videoPlayer) {
        let lastUpdateTime = 0;
        const updateInterval = 10; // Update every 10 seconds
        
        videoPlayer.addEventListener('timeupdate', function() {
            const currentTime = Math.floor(videoPlayer.currentTime);
            if (currentTime - lastUpdateTime >= updateInterval) {
                updateVideoProgress(currentTime);
                lastUpdateTime = currentTime;
            }
        });
        
        videoPlayer.addEventListener('ended', function() {
            markVideoComplete();
        });
    }
    
    // ========== Smooth Scroll for Anchor Links ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ========== Animate on Scroll ==========
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards and sections
    document.querySelectorAll('.course-card, .feature-card, .stat-card, .level-card').forEach(el => {
        observer.observe(el);
    });
    
    // ========== Form Validation Enhancement ==========
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // ========== Loading States ==========
    const buttons = document.querySelectorAll('.btn[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.closest('form').checkValidity()) {
                this.classList.add('loading');
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            }
        });
    });
    
    // ========== Tooltip Initialization ==========
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ========== Dropdown Enhancement ==========
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function() {
            const menu = this.nextElementSibling;
            if (menu) {
                menu.style.animation = 'slideInRight 0.3s ease';
            }
        });
    });
});

// ========== Video Progress Functions ==========
function updateVideoProgress(currentTime) {
    // This would send an AJAX request to update progress
    // Implementation depends on your backend endpoint
    console.log('Video progress:', currentTime);
}

function markVideoComplete() {
    // This would mark the video as completed
    // Implementation depends on your backend endpoint
    console.log('Video completed');
}

// ========== Utility Functions ==========
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

// ========== Search Debounce ==========
const searchInputs = document.querySelectorAll('input[type="search"], #courseSearch');
searchInputs.forEach(input => {
    if (input) {
        const debouncedSearch = debounce(function() {
            // Trigger search functionality
            const event = new Event('input');
            input.dispatchEvent(event);
        }, 300);
        
        input.addEventListener('input', debouncedSearch);
    }
});

// ========== Lazy Loading Images ==========
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ========== Copy to Clipboard ==========
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        console.log('Copied to clipboard');
    }, function(err) {
        console.error('Failed to copy:', err);
    });
}

// ========== Format Currency ==========
function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// ========== Format Date ==========
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// ========== Show Toast Notification ==========
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// ========== Export Functions ==========
window.FrenchLMS = {
    showToast,
    formatCurrency,
    formatDate,
    copyToClipboard
};
