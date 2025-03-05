#This gets us closer as it actually works giving us a JSON output

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json, time

# Configuration: adjust these as needed
STORE_ID = 1431  # Safeway store ID for pricing (example ID; use your local store’s ID)
OUTPUT_FILE = "safeway_sales.json"

# Playwright script to fetch sale prices
with sync_playwright() as p:
    # Launch headless browser (Chromium is used here; can also use firefox/webkit)
    browser = p.chromium.launch(headless=True)  
    context = browser.new_context()
    page = context.new_page()

    # Define a container to hold captured data
    captured_data = []

    # Define a response handler to intercept JSON XHR responses
    def handle_response(response):
        url = response.url
        # We look for JSON responses (XHR calls) that likely contain product data
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = response.json()  # parse JSON directly
            except Exception:
                # Fallback to text then JSON parse (in case of any weird JSON parsing issues)
                try:
                    text_data = response.text()
                    data = json.loads(text_data)
                except Exception:
                    data = None
            if data:
                # Optionally filter to ensure it's the deals data.
                # For example, Safeway's deals API might have a key like 'cards' or 'offers' in the JSON.
                # Here we include all JSON for inspection; later we can filter if needed.
                captured_data.append({"url": url, "data": data})
                # (We store URL too, in case we want to distinguish multiple JSON responses.)

    # Attach the response handler to the page
    page.on("response", handle_response)

    # Step 1: Set the store context by navigating to the special set-store URL.
    # This ensures the session is tied to a specific store, so prices are correct for that location.
    set_store_url = f"https://www.safeway.com/set-store.html?storeId={STORE_ID}&target=weeklyad"
    page.goto(set_store_url, timeout=60000)  # go to the set-store page (with a 60s timeout for safety)
    # The above will set a cookie for the chosen store and redirect (target=weeklyad).
    # We can wait a moment for the redirect to complete and cookies to be set.
    time.sleep(3)  # small delay to ensure store selection is applied

    # Step 2: Navigate to the Sale Prices deals page.
    deals_url = "https://www.safeway.com/shop/deals/sale-prices.html"
    page.goto(deals_url, timeout=60000)
    # Wait for network activity to calm down or a specific element that indicates content is loaded.
    # If the site dynamically loads items, ensure we give it time:
    try:
        # Example: wait for a product listing element to appear (replace with an actual selector from the site if known)
        page.wait_for_selector("div.product-tile, div.product-card, ul.products-list", timeout=15000)
    except Exception:
        # If we don't know an exact selector, use a fixed sleep as fallback
        time.sleep(5)
    
    # At this point, our handler should have captured the JSON responses containing sale data.

    # Step 3: Extract the relevant data from captured JSON.
    # (Depending on the structure, you might need to drill down into the JSON. 
    # Here we assume the JSON is already a structured dict or list of products.)
    extracted_items = []  # will hold the final list of sale items
    for entry in captured_data:
        data = entry["data"]
        # If the JSON has a top-level list of products:
        if isinstance(data, list):
            for item in data:
                extracted_items.append(item)
        elif isinstance(data, dict):
            # If data is a dict, it might contain the list under some key
            # We try common keys or inspect structure:
            for key in ["products", "items", "offers", "deals"]:
                if key in data and isinstance(data[key], list):
                    extracted_items.extend(data[key])
            # If the structure is nested differently, additional parsing logic would go here.
        else:
            # If data is another type (unlikely), skip or handle accordingly
            continue

    # Step 4: (Optional) Use BeautifulSoup to parse any additional info from the page HTML if needed.
    # For example, perhaps to verify the number of items or to extract an element not present in JSON.
    soup = BeautifulSoup(page.content(), "html.parser")
    # As an example, get the page title or header:
    page_header = soup.find("h1") or soup.find("h2")
    if page_header:
        print("Page header:", page_header.get_text().strip())

    # (If needed, one could cross-verify that len(extracted_items) matches count of items on page, etc.)

    # Step 5: Save the extracted sale items data to a JSON file.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(extracted_items, f, indent=2)
    print(f"Saved {len(extracted_items)} sale items to {OUTPUT_FILE}")

    # Close browser context
    browser.close()
