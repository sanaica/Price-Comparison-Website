import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import time
import random

# Updated headers to better mimic a real browser and avoid blocking
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.amazon.in/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'document'
}

def search_cheapest_amazon_product(product_name):
    # Format product name for the search URL
    formatted_name = product_name.replace(" ", "+")
    url = f'https://www.amazon.in/s?k={formatted_name}'
    
    print(f"Searching Amazon: {url}")
    time.sleep(random.uniform(10, 15))  # Increased delay to mimic human behavior
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Successfully fetched the page!")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None
    
    # Extract the webpage content
    soup = BeautifulSoup(response.text, "html.parser")
    product_list = soup.select('.s-result-item')
    
    cheapest_product = None
    cheapest_price = float('inf')
    
    # Loop through all product listings to find the cheapest relevant one
    for product in product_list:
        try:
            name = product.select_one('h2 a span').get_text(strip=True)
            # Filter out irrelevant results
            if product_name.lower() not in name.lower():
                continue  # Skip if product name doesn't match the query closely
        except AttributeError:
            name = "N/A"
        
        try:
            price = product.select_one('.a-price-whole').get_text(strip=True)
            # Convert price to a float for comparison
            price_float = float(price.replace(",", ""))
        except (AttributeError, ValueError):
            price = "N/A"
            price_float = float('inf')  # If price is not available, set to infinity
        
        try:
            brand = product.select_one('.s-line-clamp-1').get_text(strip=True)
        except AttributeError:
            brand = "N/A"
        
        try:
            description = product.select_one('.a-size-base-plus').get_text(strip=True)
        except AttributeError:
            description = "N/A"
        
        try:
            delivery = product.select_one('.s-align-children-center').get_text(strip=True)
        except AttributeError:
            delivery = "N/A"
        
        try:
            image_url = product.select_one('img.s-image')['src']
        except (AttributeError, TypeError):
            image_url = "N/A"
        
        # Check if the current product is the cheapest so far
        if price_float < cheapest_price:
            cheapest_price = price_float
            cheapest_product = {
                "Name": name,
                "Price": f"₹{price}",
                "Brand": brand,
                "Description": description,
                "Delivery": delivery,
                "Image URL": image_url
            }
    
    return cheapest_product

def display_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        image.show()  # Open the image in the default image viewer
    except Exception as e:
        print(f"⚠️ Error loading image: {e}")

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    cheapest_product = search_cheapest_amazon_product(product_name)
    if cheapest_product:
        print("\n📌 Cheapest Product Details:")
        for key, value in cheapest_product.items():
            print(f"{key}: {value}")
        # Display the product image
        if cheapest_product["Image URL"] != "N/A":
            display_image(cheapest_product["Image URL"])
    else:
        print("No relevant products found.")