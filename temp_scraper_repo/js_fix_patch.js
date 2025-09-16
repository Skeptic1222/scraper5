// ============================================================================
// JavaScript Fix Patch - Include this at the TOP of your <head> section
// ============================================================================

// Define critical functions immediately so they're available for onclick handlers

function resetCreditsForTesting() {
    console.log('resetCreditsForTesting called');
    
    // Basic implementation that will work even if other functions aren't loaded yet
    fetch('/dev/reset-credits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credits: 50 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Credits reset successfully');
            alert('Credits reset to 50 for testing');
            // Try to reload user info if function exists
            if (typeof loadUserSubscriptionInfo === 'function') {
                loadUserSubscriptionInfo();
            }
        } else {
            console.error('Failed to reset credits:', data.error);
            alert('Failed to reset credits: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error resetting credits:', error);
        alert('Failed to reset credits: ' + error.message);
    });
}

function showSection(sectionName) {
    console.log('showSection called with:', sectionName);
    
    // Store current section in global variable if it exists
    if (typeof window.currentSection !== 'undefined') {
        window.currentSection = sectionName;
    }
    
    // Wait for DOM if not ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            showSection(sectionName);
        });
        return;
    }
    
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        if (section) section.style.display = 'none';
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionName + 'Section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Update navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item) item.classList.remove('active');
    });
    
    // Find and activate the corresponding nav item
    const activeNavItem = Array.from(navItems).find(item => 
        item.getAttribute('data-section') === sectionName
    );
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Call section-specific loading functions if they exist
    switch(sectionName) {
        case 'dashboard':
            if (typeof loadDashboard === 'function') loadDashboard();
            break;
        case 'assets':
            if (typeof loadAssets === 'function') loadAssets();
            break;
        case 'sources':
            if (typeof loadSources === 'function') loadSources();
            break;
        case 'search':
            if (typeof loadSearchSection === 'function') loadSearchSection();
            break;
        case 'settings':
        case 'account-settings':
            if (typeof loadSettings === 'function') loadSettings();
            break;
    }
}

// Basic notification functions that will be enhanced later
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Basic implementation using alert as fallback
    if (typeof window.showEnhancedNotification === 'function') {
        window.showEnhancedNotification(message, type);
    } else {
        // Fallback to console and simple alert for critical messages
        if (type === 'error') {
            alert('Error: ' + message);
        }
    }
}

function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showWarning(message) {
    showNotification(message, 'warning');
}

// Ensure functions are globally accessible
window.resetCreditsForTesting = resetCreditsForTesting;
window.showSection = showSection;
window.showNotification = showNotification;
window.showError = showError;
window.showSuccess = showSuccess;
window.showWarning = showWarning;

console.log('✅ Critical functions loaded and ready'); 