from playwright.sync_api import sync_playwright
import os

screenshot_dir = r"d:\agent开发项目\RAG智能文档检索助手\screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

    page.goto("http://127.0.0.1:5173", timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    page.wait_for_timeout(3000)

    page.screenshot(path=os.path.join(screenshot_dir, "04_full_render.png"), full_page=True)
    print("Screenshot saved: 04_full_render.png")

    app_html = page.locator("#app").inner_html()
    print(f"#app HTML length: {len(app_html)}")
    if app_html:
        print(f"#app preview: {app_html[:500]}")
    else:
        print("#app is still empty!")

    vue_errors = page.evaluate("""() => {
        const errors = [];
        const origError = console.error;
        console.error = function() { errors.push(Array.from(arguments).join(' ')); origError.apply(console, arguments); };
        return document.querySelector('#app')?.innerHTML?.length || 0;
    }""")
    print(f"Vue app content length: {vue_errors}")

    browser.close()
