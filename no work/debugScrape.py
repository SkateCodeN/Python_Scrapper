import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        # Launch the browser (you can change to firefox or webkit if desired)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        captured_json = []  # To store responses matching our pattern
        total_json_responses = 0  # Counter for all JSON responses intercepted

        async def handle_response(response):
            nonlocal total_json_responses
            try:
                content_type = response.headers.get("content-type", "")
                # Check if the response is JSON
                if "application/json" in content_type:
                    total_json_responses += 1
                    print(f"[DEBUG] Intercepted JSON response from: {response.url}")
                    try:
                        data = await response.json()
                    except Exception as e:
                        print(f"[ERROR] Could not convert response from {response.url} to JSON: {e}")
                        return

                    # Check if the JSON matches the pattern we expect
                    if (
                        isinstance(data, dict)
                        and "response" in data
                        and isinstance(data["response"], dict)
                        and "docs" in data["response"]
                    ):
                        print(f"[INFO] Found matching JSON response at: {response.url}")
                        captured_json.append({
                            "url": response.url,
                            "data": data
                        })
                    else:
                        # If it doesn't match, print the top-level keys for troubleshooting
                        keys = list(data.keys()) if isinstance(data, dict) else "Not a dict"
                        print(f"[DEBUG] JSON from {response.url} does not match pattern. Keys: {keys}")
            except Exception as e:
                print(f"[ERROR] Exception in handling response: {e}")

        # Register the response handler
        page.on("response", handle_response)

        print("[DEBUG] Navigating to target URL...")
        target_url = "https://www.safeway.com/shop/deals/sale-prices.html"
        await page.goto(target_url)
        print("[DEBUG] Page loaded. Waiting for additional network requests...")

        # Wait for enough time for dynamic content to load (adjust timeout as needed)
        await page.wait_for_timeout(10000)  # Wait for 10 seconds
        print("[DEBUG] Finished waiting.")

        await browser.close()
        
        print(f"[SUMMARY] Total JSON responses intercepted: {total_json_responses}")
        if captured_json:
            for entry in captured_json:
                print(f"[RESULT] Captured matching JSON from: {entry['url']}")
                docs = entry["data"].get("response", {}).get("docs", [])
                print(f"         Number of docs: {len(docs)}")
        else:
            print("[SUMMARY] No matching JSON responses captured.")

asyncio.run(main())
