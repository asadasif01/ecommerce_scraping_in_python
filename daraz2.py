import requests
from bs4 import BeautifulSoup
import re

# Function to scrape product data from Daraz.pk
def scrape_daraz_product(product_name):
    # URL-encode the product name to handle spaces
    encoded_product_name = product_name.replace(' ', '%20')

    # URL of Daraz.pk's search results page for the given product name
    url = f"https://www.daraz.pk/catalog/?q={encoded_product_name}"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product information
        product_data = extract_specific_data(str(soup))
        
        return product_data
        
    else:
        print("Failed to retrieve the page.")
        return None

# Function to extract specific key-value pairs from messy data
def extract_specific_data(data):
    extracted_data = []
    regex_pattern = r'"(name|price|brandName|sellerName|originalPrice|discount|ratingScore|image)"\s*:\s*"(.*?)"'

    matches = re.findall(regex_pattern, data)
    
    # Create a dictionary for the current product
    current_product = {}
    
    for match in matches:
        key, value = match
        if key == 'name':
            # If it's a 'name' key, it's the start of a new product, so save the previous product and start a new one
            if current_product and all(key in current_product for key in ["name", "price", "brandName", "sellerName", "originalPrice", "discount", "ratingScore", "image"]):
                extracted_data.append(current_product)
            current_product = {}  # Start a new product dictionary
        current_product[key] = value
    
    # Append the last product
    if current_product and all(key in current_product for key in ["name", "price", "brandName", "sellerName", "originalPrice", "discount", "ratingScore", "image"]):
        extracted_data.append(current_product)

    return extracted_data

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    product_data = scrape_daraz_product(product_name)
    
    if product_data:
        print("Extracted product data:")
        for i, product in enumerate(product_data, start=1):
            print(f"Product {i}:")
            for key, value in product.items():
                print(f"{key}: {value}")
            print("\n---\n")
    else:
        print("No product data found.")
