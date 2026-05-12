from playwright.sync_api import sync_playwright
import os

screenshot_dir = r"d:\agent开发项目\RAG智能文档检索助手\screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    console_messages = []
    page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))

    page.on("pageerror", lambda err: console_messages.append({"type": "pageerror", "text": str(err)}))

    print("Navigating...")
    page.goto("http://127.0.0.1:5173", timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    page.wait_for_timeout(5000)

    print(f"\nAll console messages ({len(console_messages)}):")
    for msg in console_messages:
        print(f"  [{msg['type']}] {msg['text'][:500]}")

    html = page.content()
    print(f"\nFull page HTML:\n{html}")

    browser.close()
