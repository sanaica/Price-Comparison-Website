import requests  # Import the 'requests' module to fetch data from websites
from bs4 import BeautifulSoup  # Import BeautifulSoup to parse HTML
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
} # Bot blocking
def search_amazon(product_name, num_products):
    # For searching on amazon
    formatted_name = product_name.replace(" ", "+")
    url = f'https://www.amazon.in/s?k={formatted_name}'
    print(f"Searching Amazon: {url}")
    response = requests.get(url) #Get request from the website
    response = requests.get(url, headers=headers)
# Check if the request was successful
    if response.status_code == 200:  # HTTP status 200 means success
        print("Successfully fetched the page!")  
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    exit()  # Stop execution if fetching failed
# Extract the webpage content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")  
# Find product listings
    product_list = soup.select('.s-result-item')
    items = soup.find_all("span", class_="text")
# Loop through the found items and print them
    product_list = soup.select('.s-result-item')
    for i, product in enumerate(product_list[:num_products]):
        try:
            name = product.select_one('.a-color-base.a-text-normal').get_text(strip=True).upper()
        except AttributeError:
            name = "N/A"
        try:
            price = product.select_one('.a-price-whole').get_text(strip=True).upper()
        except AttributeError:
            price = "N/A"
        try:
            description = product.select_one('.aok-align-bottom').get_text(strip=True).upper()
        except AttributeError:
            description = "N/A"
        try:
            delivery = product.select_one('.s-align-children-center').get_text(strip=True).upper()
        except AttributeError:
            delivery = "N/A"
    print(f"\nAmazon Product {i+1}:")
    print(f"Name: {name}")
    print(f"Price: {price}")
    print(f"Description: {description}")
    print(f"Delivery: {delivery}")
    product_name = input("Enter product name: ")
    num_products = int(input("How many products to fetch? "))
    search_amazon(product_name, num_products)




