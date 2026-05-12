from playwright.sync_api import sync_playwright
import os, json

screenshot_dir = r"d:\agent开发项目\RAG智能文档检索助手\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    console_messages = []
    page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text[:500]}))

    print("Navigating to http://127.0.0.1:5173...")
    page.goto("http://127.0.0.1:5173", timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    page.wait_for_timeout(3000)

    page.screenshot(path=os.path.join(screenshot_dir, "03_debug.png"), full_page=True)

    html = page.content()
    with open(os.path.join(screenshot_dir, "page_source.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Page source saved ({len(html)} chars)")

    app_div = page.locator("#app").inner_html()
    print(f"#app inner HTML length: {len(app_div)}")
    print(f"#app content preview: {app_div[:1000]}")

    vue_app = page.locator(".app-shell")
    print(f".app-shell count: {vue_app.count()}")

    all_divs = page.locator("div").all()
    print(f"Total divs: {len(all_divs)}")

    errors = [m for m in console_messages if m["type"] == "error"]
    warnings = [m for m in console_messages if m["type"] == "warning"]
    print(f"\nConsole: {len(errors)} errors, {len(warnings)} warnings, {len(console_messages)} total")
    for err in errors[:10]:
        print(f"  ERROR: {err['text'][:300]}")
    for warn in warnings[:5]:
        print(f"  WARN: {warn['text'][:300]}")

    browser.close()
