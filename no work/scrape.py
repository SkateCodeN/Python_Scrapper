import asyncio
from playwright.async_api import async_playwright
import json
#testing

async def main():
    async with async_playwright() as p:
        # Launch a browser instance (you can choose chromium, firefox, or webkit)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # List to store intercepted JSON responses that match our criteria
        captured_json = []

        # Handler function for responses
        async def handle_response(response):
            try:
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    json_data = await response.json()
                    # You can add additional checks here to ensure this is the data you need
                    # For example, if the JSON data includes a specific key:
                    if "deals" in json_data or "specials" in json_data:
                        captured_json.append({
                            "url": response.url,
                            "data": json_data
                        })
            except Exception as e:
                print("Error processing JSON response:", e)

        # Register the response handler
        page.on("response", handle_response)
        
        # Navigate to the target page
        target_url = "https://www.safeway.com/shop/deals/sale-prices.html"
        await page.goto(target_url)
        
        # Wait to allow time for all network requests to complete
        await page.wait_for_timeout(15000)  # Wait for 5 seconds; adjust if needed
        
        # Close the browser
        await browser.close()
        
        # Process the captured JSON responses
        for entry in captured_json:
            print("URL:", entry["url"])
            print("Data:", json.dumps(entry["data"], indent=4))
            print("-----")

# Run the async function
asyncio.run(main())
