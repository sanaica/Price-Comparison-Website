import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import time
import random

# Amazon headers
headers_amazon = {
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

# eBay headers
headers_ebay = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept-Language': 'en-US,en;q=0.9',
}

# eBay exclusion terms
EXCLUDE_TERMS = ["accessories", "parts", "case", "cover", "repair", "kit", "tool", "lace", "laces", "polish", "sole", "soles", "insole", "insert", "cleaner", "replacement", "pad", "heel",
                 "component", "manual", "guide", "charger", "cable", "adapter", "screen protector", "strap", "band"]

# Currency conversion rate
USD_TO_INR = 83

def search_cheapest_amazon_product(product_name):
    formatted_name = product_name.replace(" ", "+")
    url = f'https://www.amazon.in/s?k={formatted_name}'
    
    time.sleep(random.uniform(10, 15))
    response = requests.get(url, headers=headers_amazon)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    product_list = soup.select('.s-result-item')
    
    cheapest_product = None
    cheapest_price = float('inf')
    
    for product in product_list:
        try:
            name = product.select_one('h2 a span').get_text(strip=True)
            if product_name.lower() not in name.lower():
                continue
        except AttributeError:
            name = "N/A"
        
        try:
            price = product.select_one('.a-price-whole').get_text(strip=True)
            price_float = float(price.replace(",", ""))
        except (AttributeError, ValueError):
            price = "N/A"
            price_float = float('inf')
        
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

def fetch_cheapest_product(search_term):
    query = search_term.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sacat=0"
    
    time.sleep(random.uniform(2, 5))
    response = requests.get(url, headers=headers_ebay)
    
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select('.s-item')
    
    if not items:
        return None
    
    cheapest = None
    lowest_price = float('inf')
    search_lower = search_term.lower()
    search_variants = [search_lower, search_lower + "s"] if not search_lower.endswith("s") else [search_lower, search_lower[:-1]]
    
    for item in items:
        name_tag = item.select_one('.s-item__title')
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        name_lower = name.lower()
        name_words = name_lower.split()
        
        if any(exclude_term in name_lower for exclude_term in EXCLUDE_TERMS):
            continue
        
        if not any(variant in name_words for variant in search_variants):
            continue
        
        price_tag = item.select_one('.s-item__price')
        price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
        try:
            price_value = float(price_text.replace("$", "").replace(",", "").split()[0])
        except (ValueError, AttributeError):
            price_value = float('inf')
        
        brand_tag = item.select_one('.s-item__subtitle')
        brand = brand_tag.get_text(strip=True) if brand_tag else "N/A"
        description = brand
        
        image = item.select_one('.s-item__image-img') or item.select_one('.s-item__image img')
        image_url = image.get('src') or image.get('data-src') or "N/A" if image else "N/A"
        
        if price_value < lowest_price:
            lowest_price = price_value
            cheapest = {
                "Name": name,
                "Price": price_text,
                "Brand": brand,
                "Description": description,
                "Image URL": image_url
            }
    
    return cheapest

def display_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        image.show()
    except Exception as e:
        print(f"⚠️ Error loading image: {e}")

def compare_and_show_details(product_name):
    # Fetch cheapest from Amazon
    amazon_result = search_cheapest_amazon_product(product_name)
    a = float(amazon_result["Price"].replace("₹", "").replace(",", "")) if amazon_result else float('inf')
    
    # Fetch cheapest from eBay
    ebay_result = fetch_cheapest_product(product_name)
    e = float(ebay_result["Price"].replace("$", "").replace(",", "")) * USD_TO_INR if ebay_result else float('inf')
    
    # Compare prices in INR
    print(f"\nPrice Comparison (in INR):")
    if a != float('inf'):
        print(f"Amazon India: ₹{a}")
    else:
        print("Amazon India: Not found or unavailable")
    
    if e != float('inf'):
        print(f"eBay: ${ebay_result['Price']} (₹{e:.2f})")
    else:
        print("eBay: Not found or unavailable")
    
    # Determine cheapest and show details
    if a < e:
        print(f"\nCheapest is on Amazon India by ₹{e - a:.2f}")
        print("\n📌 Cheapest Product Details:")
        for key, value in amazon_result.items():
            print(f"{key}: {value}")
    elif e < a:
        print(f"\nCheapest is on eBay by ₹{a - e:.2f}")
        print("\nCheapest Product Details:")
        for key, value in ebay_result.items():
            print(f"{key}: {value}")
    else:
        print("\nNo clear cheapest product found or prices are equal.")

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    compare_and_show_details(product_name)