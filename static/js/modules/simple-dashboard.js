/**
 * Simple Dashboard Test - Minimal version to debug blank dashboard issue
 */
console.log('Simple dashboard loading...');

window.simpleDashboard = {
    init: function() {
        console.log('Simple dashboard init called');
        const container = document.getElementById('dashboard-dynamic-content');
        
        if (!container) {
            console.error('Container not found!');
            return;
        }
        
        console.log('Container found:', container);
        
        // Try simplest possible content
        const simpleHTML = '<div style="padding: 20px; background: #f0f0f0; border: 2px solid red;"><h1>Dashboard Test</h1><p>If you can see this, the dashboard is working!</p></div>';
        
        console.log('Setting innerHTML...');
        container.innerHTML = simpleHTML;
        console.log('innerHTML set, content should be visible');
        
        // Verify it was set
        console.log('Container innerHTML after set:', container.innerHTML);
    }
};

// Auto-init on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOMContentLoaded - calling simple init');
        window.simpleDashboard.init();
    });
} else {
    console.log('DOM already ready - calling simple init');
    window.simpleDashboard.init();
}

console.log('Simple dashboard script loaded');