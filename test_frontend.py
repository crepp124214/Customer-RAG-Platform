from playwright.sync_api import sync_playwright
import os

screenshot_dir = r"d:\agent开发项目\RAG智能文档检索助手\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    print("1. Navigating to http://127.0.0.1:5173...")
    page.goto("http://127.0.0.1:5173", timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    page.screenshot(path=os.path.join(screenshot_dir, "01_homepage.png"), full_page=True)
    print("   Screenshot saved: 01_homepage.png")

    title = page.title()
    print(f"   Page title: {title}")

    body_text = page.locator("body").inner_text()
    print(f"   Body text preview: {body_text[:300]}...")

    h1_elements = page.locator("h1").all()
    print(f"   H1 elements: {[el.inner_text() for el in h1_elements]}")

    h2_elements = page.locator("h2").all()
    print(f"   H2 elements: {[el.inner_text() for el in h2_elements]}")

    buttons = page.locator("button").all()
    print(f"   Buttons: {[el.inner_text() for el in buttons[:10]]}")

    links = page.locator("a").all()
    print(f"   Links: {len(links)}")

    tabs = page.locator(".tab-btn").all()
    print(f"   Tab buttons: {[el.inner_text() for el in tabs]}")

    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.reload(wait_until="networkidle")
    page.wait_for_timeout(2000)

    if console_errors:
        print(f"\n   Console errors ({len(console_errors)}):")
        for err in console_errors[:5]:
            print(f"     - {err[:200]}")
    else:
        print("   No console errors!")

    page.screenshot(path=os.path.join(screenshot_dir, "02_after_reload.png"), full_page=True)
    print("   Screenshot saved: 02_after_reload.png")

    browser.close()
    print("\nDone! Check screenshots directory for visual output.")
