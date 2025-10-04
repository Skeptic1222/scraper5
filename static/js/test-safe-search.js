/**
 * Safe Search Test Script
 * Run this in browser console to test safe search functionality
 */

(function testSafeSearch() {
    console.log('='.repeat(60));
    console.log('SAFE SEARCH FUNCTIONALITY TEST');
    console.log('='.repeat(60));

    // Test 1: Find all safe search toggles
    console.log('\n1. SEARCHING FOR SAFE SEARCH TOGGLES...');
    const toggles = {
        'safe-search-toggle': document.getElementById('safe-search-toggle'),
        'safe-search': document.getElementById('safe-search'),
        'settings-safe-search-toggle': document.getElementById('settings-safe-search-toggle')
    };

    let foundCount = 0;
    Object.entries(toggles).forEach(([id, element]) => {
        if (element) {
            console.log(`   ✅ Found: ${id} (checked: ${element.checked})`);
            foundCount++;
        } else {
            console.log(`   ❌ NOT FOUND: ${id}`);
        }
    });

    if (foundCount === 0) {
        console.error('   ⚠️ NO SAFE SEARCH TOGGLES FOUND!');
        return;
    }

    // Test 2: Check which toggle is used in search handler
    console.log('\n2. CHECKING SEARCH HANDLER INTEGRATION...');
    const activeToggle = document.getElementById('safe-search-toggle') ||
                         document.getElementById('safe-search') ||
                         document.querySelector('input[name="safe-search"]');

    if (activeToggle) {
        console.log(`   ✅ Active toggle ID: ${activeToggle.id || 'unnamed'}`);
        console.log(`   ✅ Current state: ${activeToggle.checked ? 'ENABLED' : 'DISABLED'}`);
    } else {
        console.error('   ❌ No active toggle found by search handler!');
        return;
    }

    // Test 3: Simulate toggle change
    console.log('\n3. TESTING TOGGLE BEHAVIOR...');
    const originalState = activeToggle.checked;
    console.log(`   Initial state: ${originalState ? 'ON' : 'OFF'}`);

    // Toggle OFF
    activeToggle.checked = false;
    activeToggle.dispatchEvent(new Event('change', { bubbles: true }));
    console.log(`   After toggle OFF: ${activeToggle.checked ? 'ON' : 'OFF'}`);

    // Toggle ON
    setTimeout(() => {
        activeToggle.checked = true;
        activeToggle.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`   After toggle ON: ${activeToggle.checked ? 'ON' : 'OFF'}`);

        // Restore original
        activeToggle.checked = originalState;
        activeToggle.dispatchEvent(new Event('change', { bubbles: true }));
        console.log(`   Restored to: ${activeToggle.checked ? 'ON' : 'OFF'}`);
    }, 1000);

    // Test 4: Check if search handler reads the value
    console.log('\n4. VERIFYING SEARCH HANDLER CODE...');
    if (window.searchHandler) {
        console.log('   ✅ searchHandler object found');

        // Mock search to capture safe_search parameter
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            const [url, options] = args;
            if (url.includes('/api/comprehensive-search') || url.includes('/api/bulletproof-search')) {
                try {
                    const body = JSON.parse(options.body);
                    console.log('   📡 API Call Intercepted:');
                    console.log(`      URL: ${url}`);
                    console.log(`      safe_search parameter: ${body.safe_search}`);
                    console.log(`      safeSearch parameter: ${body.safeSearch}`);
                } catch (e) {
                    console.log('   📡 API Call (non-JSON body)');
                }
            }
            return originalFetch.apply(this, args);
        };
        console.log('   ✅ Fetch interceptor installed - try a search now!');
    } else {
        console.warn('   ⚠️ searchHandler not found - may not be initialized yet');
    }

    // Test 5: Enhanced search handler
    if (window.enhancedSearchHandler) {
        console.log('   ✅ enhancedSearchHandler object found');
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('TEST SUMMARY:');
    console.log(`   Toggles found: ${foundCount}`);
    console.log(`   Active toggle: ${activeToggle ? activeToggle.id : 'NONE'}`);
    console.log(`   Current state: ${activeToggle ? (activeToggle.checked ? 'ENABLED' : 'DISABLED') : 'N/A'}`);
    console.log('\nTO TEST:');
    console.log('1. Toggle safe search ON/OFF and watch console');
    console.log('2. Perform a search and check API call logs');
    console.log('3. Verify backend receives correct safe_search value');
    console.log('='.repeat(60));

})();
