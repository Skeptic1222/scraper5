// DASHBOARD DIAGNOSTIC SCRIPT
// Paste this into browser console to diagnose invisible dashboard issue
// Usage: Copy entire script and paste into F12 Developer Console

(function() {
    console.log('%c=== DASHBOARD DIAGNOSTIC REPORT ===', 'background: #222; color: #0f0; font-size: 16px; font-weight: bold; padding: 10px;');
    console.log('Timestamp:', new Date().toISOString());
    console.log('');

    // =================================================================
    // 1. ELEMENT EXISTENCE CHECK
    // =================================================================
    console.log('%c1. ELEMENT EXISTENCE', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const section = document.getElementById('dashboard-section');
    const container = document.getElementById('dashboard-dynamic-content');
    const allSections = document.querySelectorAll('section[id$="-section"]');

    console.log('Dashboard Section:', section ? '✓ EXISTS' : '✗ NOT FOUND');
    console.log('Dashboard Container:', container ? '✓ EXISTS' : '✗ NOT FOUND');
    console.log('All Sections Found:', allSections.length);
    console.log('Section IDs:', Array.from(allSections).map(s => s.id));
    console.log('');

    if (!section || !container) {
        console.error('%cCRITICAL: Required elements not found in DOM!', 'color: red; font-size: 14px; font-weight: bold;');
        return;
    }

    // =================================================================
    // 2. HTML CONTENT ANALYSIS
    // =================================================================
    console.log('%c2. HTML CONTENT ANALYSIS', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const innerHTML = container.innerHTML;
    const innerText = container.innerText;
    const textContent = container.textContent;

    console.log('innerHTML length:', innerHTML.length, 'characters');
    console.log('innerText length:', innerText.length, 'characters');
    console.log('textContent length:', textContent.length, 'characters');
    console.log('Has child elements:', container.children.length, 'children');
    console.log('Child element tags:', Array.from(container.children).map(c => c.tagName));

    console.log('\nFirst 500 chars of innerHTML:');
    console.log(innerHTML.substring(0, 500));

    console.log('\nExpected dashboard elements:');
    console.log('- .dashboard-header:', container.querySelector('.dashboard-header') ? '✓' : '✗');
    console.log('- .stats-grid:', container.querySelector('.stats-grid') ? '✓' : '✗');
    console.log('- .stat-card:', container.querySelectorAll('.stat-card').length, 'found');
    console.log('- .recent-activity:', container.querySelector('.recent-activity') ? '✓' : '✗');
    console.log('');

    // =================================================================
    // 3. COMPUTED STYLES - CONTAINER
    // =================================================================
    console.log('%c3. COMPUTED STYLES - CONTAINER', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const containerStyles = window.getComputedStyle(container);
    const criticalStyles = {
        display: containerStyles.display,
        visibility: containerStyles.visibility,
        opacity: containerStyles.opacity,
        position: containerStyles.position,
        zIndex: containerStyles.zIndex,
        overflow: containerStyles.overflow,
        height: containerStyles.height,
        width: containerStyles.width,
        maxHeight: containerStyles.maxHeight,
        maxWidth: containerStyles.maxWidth,
        minHeight: containerStyles.minHeight,
        minWidth: containerStyles.minWidth,
        top: containerStyles.top,
        left: containerStyles.left,
        right: containerStyles.right,
        bottom: containerStyles.bottom,
        transform: containerStyles.transform,
        clip: containerStyles.clip,
        clipPath: containerStyles.clipPath
    };

    console.table(criticalStyles);

    // Check for problematic values
    const issues = [];
    if (containerStyles.display === 'none') issues.push('❌ display: none (HIDDEN!)');
    if (containerStyles.visibility === 'hidden') issues.push('❌ visibility: hidden (HIDDEN!)');
    if (parseFloat(containerStyles.opacity) === 0) issues.push('❌ opacity: 0 (INVISIBLE!)');
    if (parseFloat(containerStyles.height) === 0) issues.push('❌ height: 0 (NO HEIGHT!)');
    if (parseFloat(containerStyles.width) === 0) issues.push('❌ width: 0 (NO WIDTH!)');
    if (containerStyles.maxHeight === '0px') issues.push('❌ max-height: 0 (COLLAPSED!)');
    if (containerStyles.overflow === 'hidden' && parseFloat(containerStyles.height) === 0) {
        issues.push('⚠️ overflow: hidden + height: 0 (CONTENT CLIPPED!)');
    }

    console.log('\n%cContainer Issues Found:', 'font-weight: bold;');
    if (issues.length > 0) {
        issues.forEach(issue => console.log(issue));
    } else {
        console.log('✓ No obvious CSS issues detected');
    }
    console.log('');

    // =================================================================
    // 4. COMPUTED STYLES - SECTION
    // =================================================================
    console.log('%c4. COMPUTED STYLES - SECTION', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const sectionStyles = window.getComputedStyle(section);
    const sectionCriticalStyles = {
        display: sectionStyles.display,
        visibility: sectionStyles.visibility,
        opacity: sectionStyles.opacity,
        position: sectionStyles.position,
        zIndex: sectionStyles.zIndex,
        height: sectionStyles.height,
        width: sectionStyles.width,
        overflow: sectionStyles.overflow
    };

    console.table(sectionCriticalStyles);

    const sectionIssues = [];
    if (sectionStyles.display === 'none') sectionIssues.push('❌ display: none (HIDDEN!)');
    if (sectionStyles.visibility === 'hidden') sectionIssues.push('❌ visibility: hidden (HIDDEN!)');
    if (parseFloat(sectionStyles.opacity) === 0) sectionIssues.push('❌ opacity: 0 (INVISIBLE!)');

    console.log('\n%cSection Issues Found:', 'font-weight: bold;');
    if (sectionIssues.length > 0) {
        sectionIssues.forEach(issue => console.log(issue));
    } else {
        console.log('✓ No obvious CSS issues detected');
    }
    console.log('');

    // =================================================================
    // 5. POSITIONING & BOUNDING RECTANGLES
    // =================================================================
    console.log('%c5. POSITIONING & BOUNDING', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const containerRect = container.getBoundingClientRect();
    const sectionRect = section.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    console.log('Container BoundingClientRect:');
    console.table({
        top: containerRect.top,
        left: containerRect.left,
        right: containerRect.right,
        bottom: containerRect.bottom,
        width: containerRect.width,
        height: containerRect.height,
        x: containerRect.x,
        y: containerRect.y
    });

    console.log('\nSection BoundingClientRect:');
    console.table({
        top: sectionRect.top,
        left: sectionRect.left,
        right: sectionRect.right,
        bottom: sectionRect.bottom,
        width: sectionRect.width,
        height: sectionRect.height
    });

    console.log('\nViewport:', viewportWidth, 'x', viewportHeight);

    const positionIssues = [];
    if (containerRect.width === 0 || containerRect.height === 0) {
        positionIssues.push('❌ Container has ZERO dimensions!');
    }
    if (containerRect.bottom < 0) positionIssues.push('⚠️ Container is ABOVE viewport');
    if (containerRect.top > viewportHeight) positionIssues.push('⚠️ Container is BELOW viewport');
    if (containerRect.right < 0) positionIssues.push('⚠️ Container is LEFT of viewport');
    if (containerRect.left > viewportWidth) positionIssues.push('⚠️ Container is RIGHT of viewport');

    console.log('\n%cPositioning Issues:', 'font-weight: bold;');
    if (positionIssues.length > 0) {
        positionIssues.forEach(issue => console.log(issue));
    } else {
        console.log('✓ Container is within viewport bounds');
    }
    console.log('');

    // =================================================================
    // 6. CLASS LIST ANALYSIS
    // =================================================================
    console.log('%c6. CLASS LIST ANALYSIS', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    console.log('Section Classes:', Array.from(section.classList));
    console.log('Container Classes:', Array.from(container.classList));
    console.log('\nActive state:');
    console.log('- Section has "active":', section.classList.contains('active') ? '✓ YES' : '✗ NO');
    console.log('- Section has "d-none":', section.classList.contains('d-none') ? '❌ YES (HIDDEN!)' : '✓ NO');
    console.log('- Section has "hidden":', section.classList.contains('hidden') ? '❌ YES (HIDDEN!)' : '✓ NO');
    console.log('- Container has "d-none":', container.classList.contains('d-none') ? '❌ YES (HIDDEN!)' : '✓ NO');
    console.log('- Container has "hidden":', container.classList.contains('hidden') ? '❌ YES (HIDDEN!)' : '✓ NO');
    console.log('');

    // =================================================================
    // 7. PARENT ELEMENT CHAIN
    // =================================================================
    console.log('%c7. PARENT ELEMENT CHAIN', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    let element = container;
    let depth = 0;
    const maxDepth = 10;

    console.log('Walking up the DOM tree from container:');
    while (element && depth < maxDepth) {
        const styles = window.getComputedStyle(element);
        const tag = element.tagName.toLowerCase();
        const id = element.id ? `#${element.id}` : '';
        const classes = element.className ? `.${element.className.split(' ').join('.')}` : '';

        const parentInfo = {
            depth: depth,
            element: `<${tag}${id}${classes}>`,
            display: styles.display,
            visibility: styles.visibility,
            opacity: styles.opacity,
            overflow: styles.overflow,
            height: styles.height,
            position: styles.position,
            zIndex: styles.zIndex
        };

        console.table(parentInfo);

        // Check for hiding styles
        if (styles.display === 'none') {
            console.error(`❌ PARENT IS HIDDEN! <${tag}${id}${classes}> has display: none`);
        }
        if (styles.visibility === 'hidden') {
            console.error(`❌ PARENT IS HIDDEN! <${tag}${id}${classes}> has visibility: hidden`);
        }
        if (parseFloat(styles.opacity) === 0) {
            console.warn(`⚠️ PARENT IS TRANSPARENT! <${tag}${id}${classes}> has opacity: 0`);
        }

        element = element.parentElement;
        depth++;
    }
    console.log('');

    // =================================================================
    // 8. CSS RULES INSPECTION
    // =================================================================
    console.log('%c8. CSS RULES INSPECTION', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const matchingRules = [];
    const sheets = Array.from(document.styleSheets);

    try {
        sheets.forEach(sheet => {
            try {
                const rules = Array.from(sheet.cssRules || []);
                rules.forEach(rule => {
                    if (rule.selectorText) {
                        try {
                            if (container.matches(rule.selectorText) || section.matches(rule.selectorText)) {
                                matchingRules.push({
                                    selector: rule.selectorText,
                                    display: rule.style.display || '',
                                    visibility: rule.style.visibility || '',
                                    opacity: rule.style.opacity || '',
                                    height: rule.style.height || '',
                                    maxHeight: rule.style.maxHeight || '',
                                    overflow: rule.style.overflow || ''
                                });
                            }
                        } catch (e) {
                            // Ignore invalid selectors
                        }
                    }
                });
            } catch (e) {
                console.warn('Could not access stylesheet:', sheet.href);
            }
        });

        console.log('Matching CSS Rules:', matchingRules.length);
        if (matchingRules.length > 0) {
            console.table(matchingRules.filter(r =>
                r.display || r.visibility || r.opacity || r.height || r.maxHeight || r.overflow
            ));
        }
    } catch (e) {
        console.warn('CSS rules inspection failed:', e.message);
    }
    console.log('');

    // =================================================================
    // 9. Z-INDEX STACKING CONTEXT
    // =================================================================
    console.log('%c9. Z-INDEX STACKING', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const allElements = document.querySelectorAll('*');
    const zIndexElements = Array.from(allElements)
        .map(el => ({
            element: el,
            zIndex: window.getComputedStyle(el).zIndex,
            position: window.getComputedStyle(el).position
        }))
        .filter(item => item.zIndex !== 'auto' && parseInt(item.zIndex) > 0)
        .sort((a, b) => parseInt(b.zIndex) - parseInt(a.zIndex))
        .slice(0, 10);

    console.log('Top 10 elements by z-index:');
    zIndexElements.forEach(item => {
        const tag = item.element.tagName.toLowerCase();
        const id = item.element.id ? `#${item.element.id}` : '';
        const className = item.element.className ? `.${item.element.className.split(' ').join('.')}` : '';
        console.log(`z-index: ${item.zIndex}, position: ${item.position} - <${tag}${id}${className}>`);
    });

    const sectionZIndex = parseInt(sectionStyles.zIndex) || 0;
    const containerZIndex = parseInt(containerStyles.zIndex) || 0;
    console.log(`\nDashboard section z-index: ${sectionZIndex}`);
    console.log(`Dashboard container z-index: ${containerZIndex}`);

    if (zIndexElements.length > 0 && zIndexElements[0].zIndex > Math.max(sectionZIndex, containerZIndex)) {
        console.warn(`⚠️ Other elements have higher z-index and may be covering dashboard`);
    }
    console.log('');

    // =================================================================
    // 10. EVENT LISTENERS
    // =================================================================
    console.log('%c10. EVENT LISTENERS', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const getEventListeners = window.getEventListeners;
    if (getEventListeners) {
        const sectionListeners = getEventListeners(section);
        const containerListeners = getEventListeners(container);

        console.log('Section Event Listeners:');
        console.log(Object.keys(sectionListeners).length > 0 ? sectionListeners : 'None');

        console.log('\nContainer Event Listeners:');
        console.log(Object.keys(containerListeners).length > 0 ? containerListeners : 'None');
    } else {
        console.log('⚠️ getEventListeners not available in this browser');
        console.log('(Available in Chrome DevTools but not in standard JavaScript)');
    }
    console.log('');

    // =================================================================
    // 11. CHILD ELEMENTS VISIBILITY
    // =================================================================
    console.log('%c11. CHILD ELEMENTS VISIBILITY', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    const children = Array.from(container.children);
    console.log('Inspecting', children.length, 'direct children:');

    children.forEach((child, index) => {
        const childStyles = window.getComputedStyle(child);
        const childRect = child.getBoundingClientRect();
        const tag = child.tagName.toLowerCase();
        const id = child.id ? `#${child.id}` : '';
        const className = child.className ? `.${child.className.split(' ').join('.')}` : '';

        console.log(`\nChild ${index}: <${tag}${id}${className}>`);
        console.table({
            display: childStyles.display,
            visibility: childStyles.visibility,
            opacity: childStyles.opacity,
            width: `${childRect.width}px`,
            height: `${childRect.height}px`
        });

        if (childStyles.display === 'none') console.error('  ❌ HIDDEN!');
        if (childRect.width === 0 || childRect.height === 0) console.warn('  ⚠️ ZERO SIZE!');
    });
    console.log('');

    // =================================================================
    // 12. COMPARISON WITH OTHER SECTIONS
    // =================================================================
    console.log('%c12. OTHER SECTIONS COMPARISON', 'background: #00f; color: #fff; font-size: 14px; padding: 5px;');

    allSections.forEach(sec => {
        const secStyles = window.getComputedStyle(sec);
        const secRect = sec.getBoundingClientRect();
        const isActive = sec.classList.contains('active');
        const isDashboard = sec.id === 'dashboard-section';

        console.log(`\nSection: ${sec.id}`);
        console.table({
            active: isActive,
            display: secStyles.display,
            visibility: secStyles.visibility,
            opacity: secStyles.opacity,
            height: `${secRect.height}px`,
            width: `${secRect.width}px`
        });
    });
    console.log('');

    // =================================================================
    // 13. FINAL DIAGNOSIS
    // =================================================================
    console.log('%c13. FINAL DIAGNOSIS', 'background: #f00; color: #fff; font-size: 16px; font-weight: bold; padding: 10px;');

    const allIssues = [...issues, ...sectionIssues, ...positionIssues];

    if (allIssues.length > 0) {
        console.log('%cISSUES FOUND:', 'color: red; font-size: 14px; font-weight: bold;');
        allIssues.forEach(issue => console.log(issue));
    } else {
        console.log('%cNO OBVIOUS ISSUES - Dashboard should be visible!', 'color: green; font-size: 14px;');
        console.log('Check for:');
        console.log('- Browser zoom level');
        console.log('- Browser extensions interfering');
        console.log('- Custom user stylesheets');
        console.log('- Viewport meta tag issues');
    }

    // Provide direct object references for manual inspection
    console.log('\n%cDirect object references for manual inspection:', 'font-weight: bold;');
    console.log('window.dashboardSection =', section);
    console.log('window.dashboardContainer =', container);
    window.dashboardSection = section;
    window.dashboardContainer = container;

    console.log('\n%cYou can now inspect these in console:', 'font-weight: bold;');
    console.log('- window.dashboardSection');
    console.log('- window.dashboardContainer');
    console.log('- window.getComputedStyle(window.dashboardContainer)');

    console.log('\n%c=== END DIAGNOSTIC REPORT ===', 'background: #222; color: #0f0; font-size: 16px; font-weight: bold; padding: 10px;');

    // Return summary object
    return {
        section: section,
        container: container,
        sectionRect: sectionRect,
        containerRect: containerRect,
        sectionStyles: {
            display: sectionStyles.display,
            visibility: sectionStyles.visibility,
            opacity: sectionStyles.opacity
        },
        containerStyles: {
            display: containerStyles.display,
            visibility: containerStyles.visibility,
            opacity: containerStyles.opacity,
            height: containerStyles.height,
            width: containerStyles.width
        },
        issues: allIssues,
        innerHTML: innerHTML,
        contentLength: innerHTML.length
    };
})();
