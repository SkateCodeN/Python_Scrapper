import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_deals():
    async with async_playwright() as p:
        # Launch Firefox (you can also choose chromium or webkit)
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.safeway.com/shop/deals/sale-prices.html")
        
        # Wait for necessary elements to load (adjust the selector as needed)
        await page.wait_for_selector("div.deal-item")
        
        # Get the page content
        content = await page.content()
        await browser.close()
        
        # Process with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        deals = []
        
        for item in soup.find_all("div", class_="deal-item"):
            title_element = item.find("span", class_="deal-title")
            price_element = item.find("span", class_="deal-price")
            title = title_element.get_text(strip=True) if title_element else "N/A"
            price = price_element.get_text(strip=True) if price_element else "N/A"
            
            deals.append({
                "title": title,
                "price": price
            })
        
        print(json.dumps(deals, indent=4))

asyncio.run(scrape_deals())
