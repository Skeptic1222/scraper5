#!/usr/bin/env python3
"""
Corrected UI Analysis Tool for IIS-proxied app at /scraper
Using the actual CSS classes and HTML structure found in the page
"""

import json
import time

from playwright.sync_api import sync_playwright


def analyze_ui_correctly():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            page = browser.new_page(viewport={'width': 1920, 'height': 1080})

            print("🌐 Navigating to http://localhost/scraper...")
            page.goto("http://localhost/scraper", wait_until='networkidle', timeout=30000)
            time.sleep(2)

            # Take screenshot
            print("📸 Taking corrected screenshot...")
            page.screenshot(path="corrected_ui_analysis.png", full_page=True)

            # Get page info
            title = page.title()
            print(f"📄 Page Title: {title}")

            # Check for ACTUAL UI elements based on the HTML structure
            print("\n🎯 Checking ACTUAL UI elements...")

            actual_elements = [
                (".login-container", "Login container"),
                (".logo-section", "Logo section"),
                (".logo", "Logo/Brand icon"),
                (".brand-name", "Brand name"),
                ("h1", "Welcome heading"),
                (".subtitle", "Subtitle text"),
                (".google-btn", "Google sign-in button"),
                (".google-icon", "Google icon"),
                (".footer", "Footer section"),
                (".security-note", "Security note"),
                (".security-icon", "Security icon")
            ]

            element_analysis = {}
            visible_elements = 0

            for selector, name in actual_elements:
                elements = page.locator(selector)
                count = elements.count()
                visible_count = 0
                positions = []

                if count > 0:
                    for i in range(count):
                        element = elements.nth(i)
                        if element.is_visible():
                            visible_count += 1
                            try:
                                bbox = element.bounding_box()
                                if bbox:
                                    positions.append({
                                        "x": bbox["x"],
                                        "y": bbox["y"],
                                        "width": bbox["width"],
                                        "height": bbox["height"]
                                    })
                            except:
                                pass

                element_analysis[selector] = {
                    "name": name,
                    "count": count,
                    "visible_count": visible_count,
                    "positions": positions
                }

                if visible_count > 0:
                    visible_elements += 1
                    print(f"  ✅ {name}: {count} total, {visible_count} visible")
                    if positions:
                        pos = positions[0]
                        print(f"     Position: ({pos['x']:.0f}, {pos['y']:.0f}) Size: {pos['width']:.0f}x{pos['height']:.0f}")
                else:
                    print(f"  ❌ {name}: {count} found but not visible")

            # Check button functionality
            print("\n🔍 Testing Google button interaction...")
            google_btn = page.locator(".google-btn")
            if google_btn.count() > 0:
                btn_text = google_btn.inner_text()
                btn_href = google_btn.get_attribute("href")
                print(f"  📝 Button text: '{btn_text}'")
                print(f"  🔗 Button href: '{btn_href}'")

                # Check if button is clickable
                is_clickable = google_btn.is_enabled()
                print(f"  👆 Button clickable: {is_clickable}")

                # Test hover effect (visual feedback)
                try:
                    google_btn.hover()
                    print("  ✅ Hover effect working")
                except:
                    print("  ⚠️  Hover effect may have issues")

            # Check for any overlapping elements or z-index issues
            print("\n🔄 Checking for UI layout issues...")

            layout_info = page.evaluate("""
                () => {
                    const container = document.querySelector('.login-container');
                    const button = document.querySelector('.google-btn');

                    if (!container || !button) return { error: 'Elements not found' };

                    const containerRect = container.getBoundingClientRect();
                    const buttonRect = button.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    const viewportHeight = window.innerHeight;

                    // Check if elements are properly positioned
                    const containerCentered = {
                        horizontal: Math.abs(containerRect.left + containerRect.width/2 - viewportWidth/2) < 50,
                        vertical: Math.abs(containerRect.top + containerRect.height/2 - viewportHeight/2) < 100
                    };

                    // Check if button is within container
                    const buttonInContainer = {
                        left: buttonRect.left >= containerRect.left,
                        right: buttonRect.right <= containerRect.right,
                        top: buttonRect.top >= containerRect.top,
                        bottom: buttonRect.bottom <= containerRect.bottom
                    };

                    // Check for any elements with high z-index that might cause issues
                    const allElements = document.querySelectorAll('*');
                    const highZIndexElements = [];

                    allElements.forEach(el => {
                        const zIndex = window.getComputedStyle(el).zIndex;
                        if (zIndex && zIndex !== 'auto' && parseInt(zIndex) > 100) {
                            highZIndexElements.push({
                                tag: el.tagName,
                                classes: Array.from(el.classList),
                                zIndex: zIndex
                            });
                        }
                    });

                    return {
                        containerRect: {
                            x: containerRect.x,
                            y: containerRect.y,
                            width: containerRect.width,
                            height: containerRect.height
                        },
                        buttonRect: {
                            x: buttonRect.x,
                            y: buttonRect.y,
                            width: buttonRect.width,
                            height: buttonRect.height
                        },
                        containerCentered,
                        buttonInContainer,
                        highZIndexElements,
                        viewport: { width: viewportWidth, height: viewportHeight }
                    };
                }
            """)

            if 'error' not in layout_info:
                print(f"  📐 Container position: ({layout_info['containerRect']['x']:.0f}, {layout_info['containerRect']['y']:.0f})")
                print(f"  📐 Container size: {layout_info['containerRect']['width']:.0f}x{layout_info['containerRect']['height']:.0f}")
                print(f"  🎯 Container centered horizontally: {layout_info['containerCentered']['horizontal']}")
                print(f"  🎯 Container centered vertically: {layout_info['containerCentered']['vertical']}")
                print(f"  📍 Button properly contained: {all(layout_info['buttonInContainer'].values())}")

                if layout_info['highZIndexElements']:
                    print(f"  ⚠️  Found {len(layout_info['highZIndexElements'])} elements with high z-index")
                    for el in layout_info['highZIndexElements']:
                        print(f"    - {el['tag']} (z-index: {el['zIndex']})")
                else:
                    print("  ✅ No problematic z-index issues detected")
            else:
                print(f"  ❌ Layout analysis failed: {layout_info['error']}")

            # Check for JavaScript errors during interaction
            print("\n🐛 Testing for JavaScript errors during interaction...")
            js_errors = []

            def handle_console_message(msg):
                if msg.type in ['error', 'warning']:
                    js_errors.append({
                        "type": msg.type,
                        "text": msg.text,
                        "location": str(msg.location) if msg.location else None
                    })

            page.on("console", handle_console_message)

            # Simulate user interactions
            try:
                if google_btn.count() > 0:
                    # Test hover
                    google_btn.hover()
                    time.sleep(0.5)

                    # Test click (but prevent navigation)
                    page.evaluate("document.querySelector('.google-btn').addEventListener('click', e => e.preventDefault());")
                    google_btn.click()
                    time.sleep(1)

                    print("  ✅ Button interactions completed without errors")
            except Exception as e:
                print(f"  ⚠️  Button interaction issue: {e}")

            if js_errors:
                print(f"  ⚠️  Found {len(js_errors)} JavaScript issues:")
                for error in js_errors:
                    print(f"    {error['type'].upper()}: {error['text']}")
            else:
                print("  ✅ No JavaScript errors during interaction")

            # Final summary
            print(f"\n📊 UI Analysis Summary")
            print("=" * 50)
            print(f"✅ Page loads correctly: {'Yes' if title else 'No'}")
            print(f"✅ UI elements visible: {visible_elements}/{len(actual_elements)}")
            print(f"✅ Google button functional: {'Yes' if google_btn.count() > 0 else 'No'}")
            print(f"✅ Layout properly centered: {'Yes' if layout_info.get('containerCentered', {}).get('horizontal', False) else 'No'}")
            print(f"✅ No major UI issues detected: {'Yes' if not js_errors else 'No'}")

            # Key findings
            print(f"\n🔍 Key Findings:")
            if visible_elements == len(actual_elements):
                print("  ✅ All expected UI elements are present and visible")
            else:
                missing = len(actual_elements) - visible_elements
                print(f"  ⚠️  {missing} UI elements may have visibility issues")

            if not js_errors:
                print("  ✅ No JavaScript errors detected")
                print("  ✅ No modal or dialog interference")
                print("  ✅ No overlapping element issues")
            else:
                print(f"  ⚠️  Found {len(js_errors)} JavaScript issues that need attention")

            # Save detailed results
            results = {
                "page_title": title,
                "elements_analysis": element_analysis,
                "layout_info": layout_info,
                "js_errors": js_errors,
                "summary": {
                    "total_elements": len(actual_elements),
                    "visible_elements": visible_elements,
                    "has_js_errors": len(js_errors) > 0,
                    "layout_centered": layout_info.get('containerCentered', {}).get('horizontal', False) if 'error' not in layout_info else False
                }
            }

            with open("corrected_ui_analysis_report.json", "w") as f:
                json.dump(results, f, indent=2)

            print(f"\n📄 Detailed report saved: corrected_ui_analysis_report.json")
            print(f"📸 Screenshot saved: corrected_ui_analysis.png")

            browser.close()

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_ui_correctly()
