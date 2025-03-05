import json
import time
from playwright.sync_api import sync_playwright

def main():
    # List to hold any JSON responses matching our target structure.
    targeted_responses = []

    with sync_playwright() as p:
        # Launch the browser in headless mode.
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Define a response handler that checks for our desired JSON structure.
        def handle_response(response):
            try:
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                    # Check for our targeted structure:
                    # We expect a top-level "response" key with "miscInfo" and "docs"
                    if isinstance(data, dict) and "response" in data:
                        resp = data["response"]
                        if "miscInfo" in resp and "docs" in resp:
                            print(f"[INFO] Found targeted JSON response from: {response.url}")
                            targeted_responses.append(data)
            except Exception as e:
                print(f"[ERROR] Failed to process response from {response.url}: {e}")

        # Attach our response handler.
        page.on("response", handle_response)

        # Navigate to Safeway's sales price page.
        target_url = "https://www.safeway.com/shop/deals/sale-prices.html"
        print(f"[DEBUG] Navigating to {target_url} ...")
        page.goto(target_url, timeout=60000)
        
        # Wait for the page to fully load and for potential XHR requests to finish.
        # Adjust the sleep time as needed.
        time.sleep(10)

        browser.close()

    # Write the matching responses to a JSON file.
    output_file = "targeted_response.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(targeted_responses, f, indent=2)
    print(f"[INFO] Saved {len(targeted_responses)} targeted responses to {output_file}")

if __name__ == "__main__":
    main()
