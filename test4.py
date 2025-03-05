from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json, time

# Configuration: adjust these as needed
OUTPUT_FILE = "target_sale_items.json"
TARGET_IDENTIFIER = "https://www.safeway.com/abs/pub/xapi/search/products"
TARGET_STORE_PARAM = "storeid=1431"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Container to hold responses matching the target URL
    targeted_responses = []

    def handle_response(response):
        url = response.url
        # Only capture responses from the target endpoint.
        if TARGET_IDENTIFIER in url and TARGET_STORE_PARAM in url:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    data = response.json()
                except Exception:
                    try:
                        data = json.loads(response.text())
                    except Exception:
                        data = None
                if data:
                    print(f"[INFO] Captured JSON response from: {url}")
                    targeted_responses.append({"url": url, "data": data})

    page.on("response", handle_response)

    # Set store context (if needed). Here you could set a store to ensure the session is valid.
    # (Optional: you can adjust the store ID or skip if not required.)
    set_store_url = "https://www.safeway.com/set-store.html?storeId=1431&target=weeklyad"
    page.goto(set_store_url, timeout=60000)
    time.sleep(3)

    # Navigate to the Sales page so that the target XHR is fired.
    deals_url = "https://www.safeway.com/shop/deals/sale-prices.html"
    page.goto(deals_url, timeout=60000)
    
    # Wait for the network activity to complete.
    try:
        page.wait_for_selector("div.product-tile, div.product-card, ul.products-list", timeout=15000)
    except Exception:
        time.sleep(5)
    
    # Give additional time for XHR requests to finish
    time.sleep(5)
    browser.close()

    if targeted_responses:
        # For demonstration, if more than one response is captured, we can choose the first.
        # Alternatively, you could merge or inspect them.
        target_data = targeted_responses[0]["data"]
        # Optionally, extract the "docs" field (which should contain your sale items).
        docs = target_data.get("response", {}).get("docs", [])
        print(f"[INFO] Extracted {len(docs)} sale items from the targeted response.")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(target_data, f, indent=2)
        print(f"[INFO] Saved targeted JSON response to {OUTPUT_FILE}")
    else:
        print("[WARNING] No targeted JSON responses were captured.")
