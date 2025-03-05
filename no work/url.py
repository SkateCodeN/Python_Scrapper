import requests
import json

# This is the full URL for the product search endpoint.
url = (
    "https://www.safeway.com/abs/pub/xapi/search/products?"
    "request-id=8461741053784694819&url=https://www.safeway.com"
    "&pageurl=https://www.safeway.com&pagename=deals&rows=30&start=0"
    "&search-type=keyword&storeid=1437&featured=false&q=&sort=&userid="
    "&dvid=web-4.1search&visitorId=&channel=instore&banner=safeway"
    "&fq=promoType:%22P%22&fq=instoreInventory:%221%22"
)

# Set a user-agent header to mimic a browser.
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

print("Requesting data from endpoint...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Data retrieved successfully.")

    # Write the entire JSON response to a text file with indentation.
    with open("captured_response.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))
    print("Entire JSON response written to captured_response.txt")

    # If the response contains the expected structure,
    # write each product from the 'docs' list on a separate line.
    if "response" in data and "docs" in data["response"]:
        with open("products_line_by_line.txt", "w", encoding="utf-8") as f:
            for product in data["response"]["docs"]:
                # Write each product as a compact JSON string on one line.
                f.write(json.dumps(product) + "\n")
        print("Products written line by line to products_line_by_line.txt")
    else:
        print("The expected 'docs' field was not found in the response.")
else:
    print("Request failed with status code", response.status_code)
