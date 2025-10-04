/**
 * Comprehensive Diagnostic and Fix Script
 * Paste this into browser console at http://localhost/scraper
 */

console.log('=== SCRAPER DIAGNOSTIC STARTING ===\n');

// 1. Check if search options row exists
const optionsRow = document.querySelector('#search-form .row.g-2');
console.log('1. Search Options Row:');
console.log('   Exists:', !!optionsRow);
if (optionsRow) {
    const computedStyle = window.getComputedStyle(optionsRow);
    console.log('   Display:', computedStyle.display);
    console.log('   Visibility:', computedStyle.visibility);
    console.log('   Opacity:', computedStyle.opacity);
    console.log('   Height:', computedStyle.height);
    console.log('   Children count:', optionsRow.children.length);
}

// 2. Check individual option elements
const optionElements = {
    'content-images': 'Content Type - Images',
    'content-videos': 'Content Type - Videos',
    'total-file-limit': 'Total Files Limit',
    'total-size-limit': 'Total Size Limit',
    'image-size': 'Image Size Quality',
    'video-quality': 'Video Quality',
    'adult-only-mode': 'Adult Only Toggle'
};

console.log('\n2. Individual Option Elements:');
Object.entries(optionElements).forEach(([id, label]) => {
    const elem = document.getElementById(id);
    console.log(`   ${label}:`, elem ? '✅ EXISTS' : '❌ NOT FOUND');
});

// 3. Check for debug overlays or fixed position elements
console.log('\n3. Fixed Position Elements:');
const fixedElements = Array.from(document.querySelectorAll('*')).filter(el => {
    const style = window.getComputedStyle(el);
    return style.position === 'fixed' && style.display !== 'none';
});

fixedElements.forEach((el, index) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    console.log(`   [${index + 1}] ${el.id || el.className || el.tagName}:`);
    console.log(`       Position: bottom=${style.bottom}, right=${style.right}, top=${style.top}, left=${style.left}`);
    console.log(`       Size: ${rect.width}x${rect.height}`);
    console.log(`       Z-index: ${style.zIndex}`);
    console.log(`       Text content: "${el.textContent.substring(0, 50)}..."`);
});

// 4. Check section visibility
console.log('\n4. Section Visibility:');
['dashboard-section', 'search-section'].forEach(sectionId => {
    const section = document.getElementById(sectionId);
    if (section) {
        const computed = window.getComputedStyle(section);
        const hasActive = section.classList.contains('active');
        console.log(`   ${sectionId}:`);
        console.log(`       Has 'active' class: ${hasActive}`);
        console.log(`       Display: ${computed.display}`);
    }
});

// 5. Check for CSS conflicts
console.log('\n5. Checking for CSS that might hide options...');
const stylesheets = Array.from(document.styleSheets);
let foundHidingRules = false;
try {
    stylesheets.forEach(sheet => {
        try {
            const rules = Array.from(sheet.cssRules || []);
            rules.forEach(rule => {
                if (rule.selectorText && rule.cssText.includes('display: none')) {
                    if (rule.selectorText.includes('.row') || rule.selectorText.includes('.col-md') ||
                        rule.selectorText.includes('search-form') || rule.selectorText.includes('.g-2')) {
                        console.log('   ⚠️ Found:', rule.cssText.substring(0, 100));
                        foundHidingRules = true;
                    }
                }
            });
        } catch (e) {
            // CORS error, skip
        }
    });
} catch (e) {
    console.log('   Unable to check all stylesheets (CORS)');
}
if (!foundHidingRules) {
    console.log('   ✅ No obvious CSS hiding rules found');
}

// 6. FIXES
console.log('\n=== APPLYING FIXES ===\n');

// Fix 1: Force show options row
if (optionsRow) {
    optionsRow.style.display = 'flex';
    optionsRow.style.visibility = 'visible';
    optionsRow.style.opacity = '1';
    console.log('✅ Fix 1: Forced options row to be visible');
} else {
    console.log('❌ Fix 1: Options row not found - cannot fix');
}

// Fix 2: Remove all debug/fixed position elements except safe search indicator
console.log('\nFix 2: Removing unwanted fixed position elements...');
fixedElements.forEach(el => {
    const text = el.textContent.toLowerCase();
    const shouldRemove = (
        text.includes('fix sources') ||
        text.includes('debug') ||
        text.includes('test') ||
        (el.style.bottom && el.style.right && !el.id.includes('safe-search'))
    );

    if (shouldRemove && !el.id.includes('safe-search')) {
        console.log(`   Removing: ${el.id || el.className || 'unnamed element'}`);
        el.remove();
    }
});

// Fix 3: Ensure only one section is visible
console.log('\nFix 3: Fixing section visibility...');
const allSections = document.querySelectorAll('.content-section');
allSections.forEach(section => {
    if (section.id === 'dashboard-section') {
        section.classList.remove('active');
        section.style.display = 'none';
    }
});
const searchSection = document.getElementById('search-section');
if (searchSection) {
    searchSection.classList.add('active');
    searchSection.style.display = 'block';
    console.log('✅ Made search section active');
}

// Fix 4: Force reload sources UI
console.log('\nFix 4: Reloading sources...');
if (window.enhancedSearchUI && typeof window.enhancedSearchUI.loadSources === 'function') {
    window.enhancedSearchUI.loadSources();
    console.log('✅ Reloaded sources');
} else {
    console.log('⚠️ Sources UI not available yet');
}

console.log('\n=== DIAGNOSTIC COMPLETE ===');
console.log('\nPlease check:');
console.log('1. Are the 6 option columns now visible above the sources?');
console.log('2. Is the debug overlay gone?');
console.log('3. Is only the Search & Download section visible?');
console.log('\nIf issues persist, please send a screenshot.');
