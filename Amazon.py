import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import time
import random

# Headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Expanded list of irrelevant terms
EXCLUDE_TERMS = ["accessories", "parts", "case", "cover", "repair", "kit", "tool", "lace", "laces", "polish", "sole", "soles", "insole", "insert", "cleaner", "replacement", "pad", "heel",
                  "component", "manual", "guide", "charger", "cable", "adapter", "screen protector", "strap", "band"]

# Common product-indicating words (to ensure it’s a whole item)
PRODUCT_TERMS = ["men’s", "women’s", "kids", "running", "casual", "athletic", "dress", "boots", "sandals", "sneakers", "shirt", "laptop", "phone", "headphones",
                  "computer", "monitor", "keyboard", "mouse", "speaker", "camera", "watch", "book", "toy", "game", "furniture", "table", "chair",
                  "sofa", "bed", "light", "fan", "blender", "toaster", "refrigerator", "tv", "television", "remote", "controller"]

def fetch_cheapest_product(search_term):
    """Search eBay for the cheapest relevant product matching the user input."""
    query = search_term.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sacat=0"

    time.sleep(random.uniform(2, 5))
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to load page (Status: {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select('.s-item')

    if not items:
        print("No items found!")
        return None

    cheapest = None
    lowest_price = float('inf')
    search_lower = search_term.lower()
    search_variants = [search_lower, search_lower + "s"] if not search_lower.endswith("s") else [search_lower, search_lower[:-1]]

    for item in items:
        # Name
        name_tag = item.select_one('.s-item__title')
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        name_lower = name.lower()
        name_words = name_lower.split()

        # Exclude irrelevant items first
        if any(exclude_term in name_lower for exclude_term in EXCLUDE_TERMS):
            # print(f"Excluded: {name} (contains excluded term)")  # Debug line
            continue

        # Relevance check: must match a variant
        if not any(variant in name_words for variant in search_variants):
            # print(f"Skipped: {name} (no variant match)")  # Debug line
            continue

        # Check if it’s likely a whole product
        is_likely_product = any(term in name_lower for term in PRODUCT_TERMS)

        # If the search term itself suggests a product, be less strict
        search_is_product_like = any(term in search_lower for term in PRODUCT_TERMS)

        if not is_likely_product and not search_is_product_like:
            # print(f"Skipped: {name} (doesn't seem like a whole product)") # Debug line
            continue

        # Price
        price_tag = item.select_one('.s-item__price')
        price_text = price_tag.get_text(strip=True) if price_tag else "N/A"
        try:
            price_value = float(price_text.replace("$", "").replace(",", "").split()[0])
        except (ValueError, AttributeError):
            price_value = float('inf')

        # Brand/Description
        brand_tag = item.select_one('.s-item__subtitle')
        brand = brand_tag.get_text(strip=True) if brand_tag else "N/A"
        description = brand

        # Image URL
        image = item.select_one('.s-item__image-img') or item.select_one('.s-item__image img')
        image_url = image.get('src') or image.get('data-src') or "N/A" if image else "N/A"
        if image_url.endswith('.webp') or image_url == "N/A":
            link = item.select_one('.s-item__link')
            if link and link.get('href'):
                image_url = fetch_item_image(link['href']) or image_url

        # Update cheapest
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

def fetch_item_image(item_url):
    """Fetch a PNG/JPG image from an item page if available."""
    try:
        response = requests.get(item_url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image and og_image.get('content', '').endswith(('.png', '.jpg', '.jpeg')):
            return og_image['content']
        return None
    except Exception:
        return None

def show_image(url):
    """Display the image in a pop-up window if it's PNG or JPG."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        if image.format in ['PNG', 'JPEG']:
            image.show()
    except Exception as e:
        print(f"Error displaying image: {e}")

def main():
    search_term = input("Enter product to search: ")
    product = fetch_cheapest_product(search_term)

    if product:
        print("\nCheapest Product:")
        print(f"Name: {product['Name']}")
        print(f"Price: {product['Price']}")
        print(f"Brand: {product['Brand']}")
        print(f"Description: {product['Description']}")
        print(f"Image URL: {product['Image URL']}")

        if product["Image URL"] != "N/A":
            show_image(product["Image URL"])
        else:
            print("No image available to display.")
    else:
        print(f"No relevant products found for '{search_term}'.")

if __name__ == "__main__":
    main()