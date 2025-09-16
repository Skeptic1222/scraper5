#!/usr/bin/env python3
"""
Comprehensive UI Analysis Tool for IIS-proxied app at /scraper
Analyzes page structure, screenshots, accessibility, and potential UI issues
"""

import json
import time

from playwright.sync_api import sync_playwright


def analyze_ui():
    try:
        with sync_playwright() as p:
            # Launch browser with debugging options
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
            )

            # Create page with larger viewport for better analysis
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})

            print("🌐 Navigating to http://localhost/scraper...")
            page.goto("http://localhost/scraper", wait_until='networkidle', timeout=30000)

            # Wait a bit for any dynamic content
            time.sleep(2)

            # 1. Take full page screenshot
            print("📸 Taking full page screenshot...")
            page.screenshot(path="ui_analysis_full.png", full_page=True)

            # 2. Take viewport screenshot
            print("📱 Taking viewport screenshot...")
            page.screenshot(path="ui_analysis_viewport.png", full_page=False)

            # 3. Get page info
            title = page.title()
            url = page.url
            print(f"📄 Page Title: {title}")
            print(f"🔗 URL: {url}")

            # 4. Check for modals and dialogs
            print("\n🔍 Checking for modals and dialogs...")
            modal_selectors = [
                ".modal", ".dialog", ".popup", ".overlay", ".modal-dialog",
                "[role='dialog']", "[role='alertdialog']", ".swal-modal",
                ".bootstrap-modal", ".ui-dialog", ".fancybox-content"
            ]

            found_modals = []
            for selector in modal_selectors:
                elements = page.locator(selector)
                count = elements.count()
                if count > 0:
                    for i in range(count):
                        element = elements.nth(i)
                        is_visible = element.is_visible()
                        bounding_box = element.bounding_box() if is_visible else None
                        found_modals.append({
                            "selector": selector,
                            "index": i,
                            "visible": is_visible,
                            "bounding_box": bounding_box
                        })
                        print(f"  🎯 Found modal: {selector} (visible: {is_visible})")

            # 5. Check for overlapping elements
            print("\n🔄 Checking for overlapping elements...")
            overlapping_issues = []

            # Check common overlay indicators
            overlay_selectors = [
                ".overlay", ".backdrop", ".mask", "[style*='z-index']",
                "[style*='position: fixed']", "[style*='position: absolute']"
            ]

            for selector in overlay_selectors:
                elements = page.locator(selector)
                if elements.count() > 0:
                    print(f"  ⚠️  Found potential overlay: {selector} ({elements.count()} elements)")

            # 6. Get accessibility tree/snapshot
            print("\n♿ Getting accessibility snapshot...")
            try:
                accessibility_tree = page.accessibility.snapshot()

                # Save accessibility tree to file
                with open("accessibility_tree.json", "w") as f:
                    json.dump(accessibility_tree, f, indent=2)
                print("  ✅ Accessibility tree saved to accessibility_tree.json")

                # Analyze accessibility issues
                def analyze_accessibility_node(node, issues=None):
                    if issues is None:
                        issues = []

                    # Check for missing alt text on images
                    if node.get('role') == 'image' and not node.get('name'):
                        issues.append(f"Image without alt text: {node.get('description', 'unknown')}")

                    # Check for buttons without accessible names
                    if node.get('role') == 'button' and not node.get('name'):
                        issues.append(f"Button without accessible name")

                    # Check for form controls without labels
                    if node.get('role') in ['textbox', 'combobox', 'listbox'] and not node.get('name'):
                        issues.append(f"Form control without label: {node.get('role')}")

                    # Recursively check children
                    for child in node.get('children', []):
                        analyze_accessibility_node(child, issues)

                    return issues

                accessibility_issues = analyze_accessibility_node(accessibility_tree)
                if accessibility_issues:
                    print("  ⚠️  Accessibility issues found:")
                    for issue in accessibility_issues[:10]:  # Show first 10 issues
                        print(f"    - {issue}")
                else:
                    print("  ✅ No major accessibility issues detected")

            except Exception as e:
                print(f"  ❌ Could not get accessibility snapshot: {e}")

            # 7. Analyze page layout and structure
            print("\n🏗️  Analyzing page structure...")

            # Get DOM structure
            dom_info = page.evaluate("""
                () => {
                    const body = document.body;
                    const info = {
                        bodyClasses: Array.from(body.classList),
                        bodyStyles: window.getComputedStyle(body),
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        scrollWidth: document.documentElement.scrollWidth,
                        scrollHeight: document.documentElement.scrollHeight,
                        hasHorizontalScroll: document.documentElement.scrollWidth > window.innerWidth,
                        hasVerticalScroll: document.documentElement.scrollHeight > window.innerHeight
                    };

                    // Check for elements outside viewport
                    const elements = document.querySelectorAll('*');
                    const outsideElements = [];

                    elements.forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.left < 0 || rect.top < 0 ||
                            rect.right > window.innerWidth ||
                            rect.bottom > window.innerHeight) {
                            if (rect.width > 0 && rect.height > 0) {
                                outsideElements.push({
                                    tag: el.tagName,
                                    classes: Array.from(el.classList),
                                    rect: {
                                        left: rect.left,
                                        top: rect.top,
                                        right: rect.right,
                                        bottom: rect.bottom,
                                        width: rect.width,
                                        height: rect.height
                                    }
                                });
                            }
                        }
                    });

                    info.elementsOutsideViewport = outsideElements.slice(0, 20); // Limit to 20

                    return info;
                }
            """)

            print(f"  📐 Viewport: {dom_info['viewportWidth']}x{dom_info['viewportHeight']}")
            print(f"  📜 Content size: {dom_info['scrollWidth']}x{dom_info['scrollHeight']}")
            print(f"  ↔️ Horizontal scroll: {dom_info['hasHorizontalScroll']}")
            print(f"  ↕️ Vertical scroll: {dom_info['hasVerticalScroll']}")
            print(f"  🏷️  Body classes: {', '.join(dom_info['bodyClasses'])}")

            if dom_info['elementsOutsideViewport']:
                print(f"  ⚠️  Elements outside viewport: {len(dom_info['elementsOutsideViewport'])}")
                for elem in dom_info['elementsOutsideViewport'][:5]:  # Show first 5
                    print(f"    - {elem['tag']} at ({elem['rect']['left']}, {elem['rect']['top']})")

            # 8. Check for specific UI elements and their states
            print("\n🎯 Checking key UI elements...")

            ui_elements = [
                (".btn-google", "Google sign-in button"),
                (".login-card", "Login card"),
                (".app-title", "App title"),
                (".welcome-text", "Welcome text"),
                (".info-section", "Info section"),
                ("form", "Forms"),
                ("input", "Input fields"),
                ("button", "Buttons"),
                (".modal", "Modals"),
                (".alert", "Alerts"),
                (".error", "Error messages"),
                (".warning", "Warning messages"),
                (".navbar", "Navigation bar"),
                (".footer", "Footer")
            ]

            element_analysis = {}
            for selector, name in ui_elements:
                elements = page.locator(selector)
                count = elements.count()
                element_analysis[selector] = {
                    "name": name,
                    "count": count,
                    "visible_count": 0,
                    "positions": []
                }

                if count > 0:
                    for i in range(min(count, 10)):  # Check first 10 elements
                        element = elements.nth(i)
                        if element.is_visible():
                            element_analysis[selector]["visible_count"] += 1
                            try:
                                bbox = element.bounding_box()
                                if bbox:
                                    element_analysis[selector]["positions"].append(bbox)
                            except:
                                pass

                    visible = element_analysis[selector]["visible_count"]
                    print(f"  {'✅' if visible > 0 else '❌'} {name}: {count} total, {visible} visible")
                else:
                    print(f"  ❌ {name}: not found")

            # 9. Check for JavaScript errors
            print("\n🐛 Checking for JavaScript errors...")
            js_errors = []

            def handle_console_message(msg):
                if msg.type in ['error', 'warning']:
                    js_errors.append({
                        "type": msg.type,
                        "text": msg.text,
                        "location": msg.location
                    })

            page.on("console", handle_console_message)

            # Reload page to catch any errors during load
            page.reload(wait_until='networkidle')
            time.sleep(2)

            if js_errors:
                print(f"  ⚠️  Found {len(js_errors)} JavaScript issues:")
                for error in js_errors[:10]:  # Show first 10
                    print(f"    {error['type'].upper()}: {error['text']}")
            else:
                print("  ✅ No JavaScript errors detected")

            # 10. Generate summary report
            print("\n📊 UI Analysis Summary Report")
            print("=" * 50)

            report = {
                "page_info": {
                    "title": title,
                    "url": url,
                    "viewport": f"{dom_info['viewportWidth']}x{dom_info['viewportHeight']}",
                    "content_size": f"{dom_info['scrollWidth']}x{dom_info['scrollHeight']}"
                },
                "modals_found": len(found_modals),
                "modal_details": found_modals,
                "accessibility_issues": len(accessibility_issues) if 'accessibility_issues' in locals() else 0,
                "js_errors": len(js_errors),
                "elements_outside_viewport": len(dom_info['elementsOutsideViewport']),
                "element_analysis": element_analysis,
                "dom_info": dom_info
            }

            # Save detailed report
            with open("ui_analysis_report.json", "w") as f:
                json.dump(report, f, indent=2)

            print(f"✅ Analysis complete!")
            print(f"📸 Screenshots: ui_analysis_full.png, ui_analysis_viewport.png")
            print(f"📄 Detailed report: ui_analysis_report.json")
            print(f"♿ Accessibility tree: accessibility_tree.json")

            # Summary findings
            if found_modals:
                print(f"🎯 Found {len(found_modals)} modal/dialog elements")
            if dom_info['elementsOutsideViewport']:
                print(f"⚠️  Found {len(dom_info['elementsOutsideViewport'])} elements outside viewport")
            if js_errors:
                print(f"🐛 Found {len(js_errors)} JavaScript issues")

            browser.close()

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_ui()
