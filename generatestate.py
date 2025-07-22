from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) # Must be non-headless to log in
    context = browser.new_context()
    page = context.new_page()

    print("Opening LeetCode login page...")
    page.goto("https://leetcode.com/accounts/login/")
    
    print("\n>>> Please log in to your LeetCode account in the browser window.")
    print(">>> After you have successfully logged in, close the browser window to continue.")

    page.on("close", lambda: print("Browser closed, saving state..."))
    page.wait_for_event("close")

    context.storage_state(path="auth.json")
    print("\nAuthentication state saved to 'auth.json'! You can now run the main scraper.")