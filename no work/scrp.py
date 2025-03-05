import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        # Launch browser in headless mode.
        browser = await p.chromium.launch(headless=True)
        # Create a new browser context with geolocation set to Tacoma, WA
        # (latitude: 47.2529, longitude: -122.4443) and grant geolocation permission.
        context = await browser.new_context(
            geolocation={"latitude": 47.2529, "longitude": -122.4443},
            permissions=["geolocation"]
        )
        page = await context.new_page()
        
        captured_json = []  # List to store responses matching our pattern
        total_json_responses = 0  # Counter for all JSON responses intercepted

        async def handle_response(response):
            nonlocal total_json_responses
            try:
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    total_json_responses += 1
                    url = response.url
                    print(f"[DEBUG] Intercepted JSON response from: {url}")
                    try:
                        data = await response.json()
                    except Exception as e:
                        print(f"[ERROR] Could not convert response from {url} to JSON: {e}")
                        return

                    # For debugging, if the JSON has a "response" key, print its keys and a snippet.
                    if isinstance(data, dict) and "response" in data:
                        keys = list(data.keys())
                        print(f"[DEBUG] JSON from {url} has keys: {keys}")
                        snippet = json.dumps(data, indent=2)[:200]
                        print(f"[DEBUG] Snippet from {url}: {snippet}...")
                    
                    # Check for our expected pattern: a JSON object with a top-level "response"
                    # key that contains both "docs" and "numFound"
                    if (
                        isinstance(data, dict)
                        and "response" in data
                        and isinstance(data["response"], dict)
                        and "docs" in data["response"]
                        and "numFound" in data["response"]
                    ):
                        print(f"[INFO] Found matching JSON response at: {url}")
                        captured_json.append({"url": url, "data": data})
            except Exception as e:
                print(f"[ERROR] Exception in handling response: {e}")

        # Register the response handler
        page.on("response", handle_response)

        print("[DEBUG] Navigating to target URL...")
        # Include storeid=1431 in the URL (adjust if necessary)
        target_url = "https://www.safeway.com/shop/deals/sale-prices.html"
        await page.goto(target_url)
        print("[DEBUG] Page loaded. Simulating scrolling to trigger lazy-loaded content...")

        # Simulate scrolling to trigger lazy-loaded requests.
        for i in range(3):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(3000)

        print("[DEBUG] Finished scrolling. Waiting for additional network requests...")
        await page.wait_for_timeout(5000)

        await browser.close()
        
        print(f"[SUMMARY] Total JSON responses intercepted: {total_json_responses}")
        if captured_json:
            for entry in captured_json:
                url = entry['url']
                num_found = entry['data']['response'].get("numFound", "N/A")
                print(f"[RESULT] Captured matching JSON from: {url} with numFound: {num_found}")
        else:
            print("[SUMMARY] No matching JSON responses captured.")

        # Write the matching responses to a text file, line-by-line formatted.
        with open("captured_responses.txt", "w", encoding="utf-8") as f:
            if captured_json:
                for entry in captured_json:
                    f.write(f"URL: {entry['url']}\n")
                    f.write(json.dumps(entry["data"], indent=2))
                    f.write("\n" + "-"*80 + "\n")
            else:
                f.write("No matching JSON responses captured.\n")

        print("[INFO] Output written to captured_responses.txt")

asyncio.run(main())
