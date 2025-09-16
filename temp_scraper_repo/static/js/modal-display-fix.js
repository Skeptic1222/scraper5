/**
 * Modal Display Fix
 * Prevents modals from auto-showing and manages modal state properly
 */

(function() {
    'use strict';
    
    console.log('🔧 Modal Display Fix: Initializing...');
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModalFix);
    } else {
        initModalFix();
    }
    
    function initModalFix() {
        console.log('🔧 Modal Display Fix: DOM ready, applying fixes...');
        
        // ============ HIDE ALL MODALS ON LOAD ============
        
        // Hide Bootstrap modals
        const bootstrapModals = document.querySelectorAll('.modal');
        bootstrapModals.forEach(modal => {
            modal.classList.remove('show');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            console.log(`✓ Hidden modal: ${modal.id || modal.className}`);
        });
        
        // Hide modal backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            backdrop.remove();
            console.log('✓ Removed modal backdrop');
        });
        
        // Hide AI Assistant
        const aiAssistant = document.querySelectorAll('.enhanced-ai-assistant, #ai-assistant, .ai-assistant-container');
        aiAssistant.forEach(element => {
            element.classList.remove('show');
            element.style.display = 'none';
            console.log('✓ Hidden AI Assistant element');
        });
        
        // Hide Media Viewer
        const mediaViewer = document.querySelectorAll('#mediaViewerModal, .media-viewer-modal, .media-viewer-overlay');
        mediaViewer.forEach(element => {
            element.classList.remove('show', 'active');
            element.style.display = 'none';
            console.log('✓ Hidden Media Viewer element');
        });
        
        // Hide any dialog elements
        const dialogs = document.querySelectorAll('dialog[open]');
        dialogs.forEach(dialog => {
            dialog.close();
            console.log('✓ Closed dialog element');
        });
        
        // ============ REMOVE BODY MODAL CLASSES ============
        
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
        
        // ============ PREVENT AUTO-INITIALIZATION ============
        
        // Override Bootstrap modal auto-show
        if (window.bootstrap && window.bootstrap.Modal) {
            const originalModalConstructor = window.bootstrap.Modal;
            window.bootstrap.Modal = function(element, options) {
                // Force show: false in options
                const safeOptions = Object.assign({}, options, { show: false });
                return new originalModalConstructor(element, safeOptions);
            };
            // Copy static methods
            Object.setPrototypeOf(window.bootstrap.Modal, originalModalConstructor);
            Object.setPrototypeOf(window.bootstrap.Modal.prototype, originalModalConstructor.prototype);
        }
        
        // ============ FIX AI ASSISTANT INITIALIZATION ============
        
        // Delay AI Assistant initialization
        window.addEventListener('load', function() {
            setTimeout(function() {
                // Add loaded class to body to allow AI assistant button to show
                document.body.classList.add('loaded');
                console.log('✓ Page fully loaded, AI Assistant button can now be shown');
                
                // Ensure AI Assistant stays hidden until explicitly triggered
                const aiAssistantElements = document.querySelectorAll('.enhanced-ai-assistant, #ai-assistant');
                aiAssistantElements.forEach(el => {
                    if (!el.classList.contains('user-triggered')) {
                        el.style.display = 'none';
                    }
                });
            }, 1000); // Wait 1 second after page load
        });
        
        // ============ MODAL SHOW INTERCEPTOR ============
        
        // Intercept modal show attempts
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes') {
                    const target = mutation.target;
                    
                    // Check if a modal is trying to show itself
                    if (target.classList.contains('modal') && target.classList.contains('show')) {
                        // Check if this was user-triggered
                        if (!target.classList.contains('user-triggered')) {
                            console.warn(`⚠️ Preventing auto-show of modal: ${target.id}`);
                            target.classList.remove('show');
                            target.style.display = 'none';
                        }
                    }
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['class', 'style'],
            subtree: true
        });
        
        // ============ SAFE MODAL TRIGGER ============
        
        // Add safe modal show function
        window.safeShowModal = function(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('user-triggered');
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                console.log(`✓ User triggered modal: ${modalId}`);
                
                // Remove user-triggered class after modal is hidden
                modal.addEventListener('hidden.bs.modal', function() {
                    modal.classList.remove('user-triggered');
                }, { once: true });
            }
        };
        
        // ============ FIX EXISTING MODAL TRIGGERS ============
        
        // Fix AI Assistant trigger
        const aiTriggers = document.querySelectorAll('[data-bs-target="#ai-assistant"], [onclick*="ai-assistant"]');
        aiTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const aiModal = document.querySelector('#ai-assistant, .enhanced-ai-assistant');
                if (aiModal) {
                    aiModal.classList.add('user-triggered', 'show');
                    aiModal.style.display = 'block';
                }
            });
        });
        
        console.log('✅ Modal Display Fix: All fixes applied successfully');
    }
    
    // ============ GLOBAL ERROR PREVENTION ============
    
    // Prevent errors from breaking the page
    window.addEventListener('error', function(e) {
        if (e.message && e.message.includes('modal')) {
            console.error('Modal-related error caught:', e.message);
            e.preventDefault();
        }
    });
    
})();