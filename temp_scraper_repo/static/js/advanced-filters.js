/**
 * ============================================================================
 * ADVANCED FILTERS FUNCTIONALITY
 * ============================================================================
 * 
 * Handles advanced search filter interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Setting up advanced filters...');
    
    // Enable/disable filter sections
    setupFilterToggles();
    
    // Set up tooltips
    setupTooltips();
    
    // Set up filter validation
    setupFilterValidation();
    
    console.log('✅ Advanced filters ready');
});

function setupFilterToggles() {
    // Image size filter toggle
    const imageToggle = document.getElementById('enable-image-size-filter');
    const imageFilters = document.getElementById('image-size-filters');
    
    if (imageToggle && imageFilters) {
        imageToggle.addEventListener('change', function() {
            imageFilters.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Video size filter toggle
    const videoToggle = document.getElementById('enable-video-size-filter');
    const videoFilters = document.getElementById('video-size-filters');
    
    if (videoToggle && videoFilters) {
        videoToggle.addEventListener('change', function() {
            videoFilters.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Audio size filter toggle
    const audioToggle = document.getElementById('enable-audio-size-filter');
    const audioFilters = document.getElementById('audio-size-filters');
    
    if (audioToggle && audioFilters) {
        audioToggle.addEventListener('change', function() {
            audioFilters.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Duration filter toggle
    const durationToggle = document.getElementById('enable-duration-filter');
    const durationFilters = document.getElementById('duration-filter-inputs');
    
    if (durationToggle && durationFilters) {
        durationToggle.addEventListener('change', function() {
            durationFilters.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Resolution filter toggle
    const resolutionToggle = document.getElementById('enable-resolution-filter');
    const resolutionFilters = document.getElementById('resolution-filter-inputs');
    
    if (resolutionToggle && resolutionFilters) {
        resolutionToggle.addEventListener('change', function() {
            resolutionFilters.style.display = this.checked ? 'block' : 'none';
        });
    }
}

function setupTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function setupFilterValidation() {
    // Size input validation
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.value = 0;
            }
        });
    });
    
    // Min/Max validation
    const sizeInputs = [
        { min: 'min-image-size', max: 'max-image-size' },
        { min: 'min-video-size', max: 'max-video-size' },
        { min: 'min-audio-size', max: 'max-audio-size' },
        { min: 'min-duration', max: 'max-duration' }
    ];
    
    sizeInputs.forEach(({ min, max }) => {
        const minInput = document.getElementById(min);
        const maxInput = document.getElementById(max);
        
        if (minInput && maxInput) {
            function validateRange() {
                const minVal = parseFloat(minInput.value) || 0;
                const maxVal = parseFloat(maxInput.value) || 0;
                
                if (minVal > maxVal && maxVal > 0) {
                    maxInput.value = minVal;
                }
            }
            
            minInput.addEventListener('change', validateRange);
            maxInput.addEventListener('change', validateRange);
        }
    });
}

// Export functions for global access
window.setupAdvancedFilters = function() {
    setupFilterToggles();
    setupTooltips();
    setupFilterValidation();
};