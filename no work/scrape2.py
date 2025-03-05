import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        # Launch the browser (Chromium, Firefox, or WebKit)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # List to store captured JSON responses that match our pattern
        captured_json = []

        # Define a response handler
        async def handle_response(response):
            try:
                # Check for JSON content-type
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = await response.json()
                    # Check if the JSON matches the pattern:
                    # It should be a dict with a key "response" that contains a "docs" list.
                    if isinstance(data, dict) and "response" in data and isinstance(data["response"], dict) and "docs" in data["response"]:
                        captured_json.append({
                            "url": response.url,
                            "data": data
                        })
                        print("Captured JSON from:", response.url)
            except Exception as e:
                print("Error processing JSON response:", e)

        # Register the response handler
        page.on("response", handle_response)
        
        # Navigate to the target page
        target_url = "https://www.safeway.com/shop/deals/sale-prices.html"
        await page.goto(target_url)
        
        # Wait enough time for network requests to complete (adjust as needed)
        await page.wait_for_timeout(15000)  # 10 seconds
        
        # Close the browser
        await browser.close()
        
        # Print the captured JSON data that match the pattern
        for entry in captured_json:
            print("URL:", entry["url"])
            print("Data:", json.dumps(entry["data"], indent=4))

# Run the async function
asyncio.run(main())
