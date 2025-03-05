import requests
import json
import time

def main():
    # Generate a dynamic request-id based on the current time in nanoseconds.
    request_id = str(int(time.time() * 1e9))
    
    base_url = "https://www.safeway.com/abs/pub/xapi/search/products"
    # Construct the query parameters as a dictionary.
    params = {
        "request-id": request_id,
        "url": "https://www.safeway.com",
        "pageurl": "https://www.safeway.com",
        "pagename": "deals",
        "rows": "30",
        "start": "0",
        "search-type": "keyword",
        "storeid": "1437",
        "featured": "false",
        "q": "",
        "sort": "",
        "userid": "",
        "dvid": "web-4.1search",
        "visitorId": "",
        "channel": "instore",
        "banner": "safeway",
        "fq": ['promoType:"P"', 'instoreInventory:"1"']
    }
    
    print("Constructed base URL:", base_url)
    print("With parameters:")
    print(json.dumps(params, indent=2))
    
    try:
        response = requests.get(
            base_url, 
            params=params, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=15
        )
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return
    
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
            return
        
        print("Data retrieved successfully.")
        # Write the entire JSON response to a file.
        with open("captured_response.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))
        print("Full JSON response written to captured_response.txt")
        
        # If the response has the expected structure, write each product on its own line.
        if "response" in data and "docs" in data["response"]:
            with open("products_line_by_line.txt", "w", encoding="utf-8") as f:
                for product in data["response"]["docs"]:
                    f.write(json.dumps(product) + "\n")
            print("Products written line by line to products_line_by_line.txt")
        else:
            print("Expected structure not found in JSON response.")
    else:
        print("Request failed with status code:", response.status_code)

if __name__ == "__main__":
    main()
