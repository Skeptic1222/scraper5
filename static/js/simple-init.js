/**
 * Simple initialization to hide dropdown on load
 * This runs immediately without waiting for other modules
 */

(function() {
    'use strict';
    
    // Hide dropdown immediately
    function hideDropdown() {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(menu => {
            menu.classList.remove('show');
            menu.style.display = 'none';
        });
    }
    
    // Run immediately
    hideDropdown();
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideDropdown);
    }
    
    // Run after a delay to catch late-loading elements
    setTimeout(hideDropdown, 100);
    setTimeout(hideDropdown, 500);
    setTimeout(hideDropdown, 1000);
    
    // Setup click handler for dropdown
    function setupDropdown() {
        const userBtn = document.getElementById('user-dropdown');
        if (userBtn && !userBtn.hasAttribute('data-init')) {
            userBtn.setAttribute('data-init', 'true');
            userBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const menu = document.querySelector('.dropdown-menu');
                if (menu) {
                    if (menu.style.display === 'none' || !menu.classList.contains('show')) {
                        menu.style.display = 'block';
                        menu.classList.add('show');
                    } else {
                        menu.style.display = 'none';
                        menu.classList.remove('show');
                    }
                }
            });
        }
    }
    
    // Setup dropdown when ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupDropdown);
    } else {
        setupDropdown();
    }
    
    // Close dropdown on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            const dropdowns = document.querySelectorAll('.dropdown-menu');
            dropdowns.forEach(menu => {
                menu.style.display = 'none';
                menu.classList.remove('show');
            });
        }
    });
})();