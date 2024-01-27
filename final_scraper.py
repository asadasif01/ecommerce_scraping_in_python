import requests
from bs4 import BeautifulSoup
import re
import json
import os

# List to store details for all products
all_products_data = []

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

        # Check if 'productUrl' is present in the extracted data
        for product in product_data:
            if 'productUrl' in product:
                product_url = product['productUrl']
                print(f"Product URL: {product_url}")
                scrape_reviews(product_url, product)  # Call scrape_reviews function for the product URL and pass product details

        # Append the product details to the list
        all_products_data.extend(product_data)

        return product_data

    else:
        print("Failed to retrieve the page.")
        return None

# Function to extract specific key-value pairs from messy data
def extract_specific_data(data):
    extracted_data = []
    regex_pattern = r'"(name|price|brandName|sellerName|originalPrice|discount|ratingScore|image|productUrl|itemId)"\s*:\s*"(.*?)"'

    matches = re.findall(regex_pattern, data)

    # Create a dictionary for the current product
    current_product = {}

    for match in matches:
        key, value = match
        if key == 'name':
            # If it's a 'name' key, it's the start of a new product, so save the previous product and start a new one
            if current_product and all(key in current_product for key in ["name", "price", "brandName", "sellerName", "originalPrice", "discount", "ratingScore", "image", "productUrl", "itemId"]):
                extracted_data.append(current_product)
            current_product = {}  # Start a new product dictionary
        current_product[key] = value

    # Append the last product
    if current_product and all(key in current_product for key in ["name", "price", "brandName", "sellerName", "originalPrice", "discount", "ratingScore", "image","productUrl", "itemId"]):
        extracted_data.append(current_product)

    return extracted_data

# Function to scrape reviews
def scrape_reviews(product_url, product_details):
    # Check if the product_url starts with //
    if product_url.startswith('//'):
        product_url = 'https:' + product_url  # Assuming the website uses HTTPS, adjust if it uses HTTP

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    response = requests.get(product_url, headers=headers)

    if response.status_code == 200:
        # Extract the JSON-like data from the HTML
        start_index = response.text.find('app.run(') + len('app.run(')
        end_index = response.text.find(');', start_index)
        json_data_str = response.text[start_index:end_index]

        # Extract valid JSON string from the extracted data
        json_match = re.search(r'{.*}', json_data_str)
        if json_match:
            json_data = json_match.group()

            # Load the JSON data
            try:
                data = json.loads(json_data)

                # Extract the relevant information from the JSON structure
                reviews_data = data.get('data', {}).get('root', {}).get('fields', {}).get('pc_reviews_v3', {}).get('reviews', [])

                # Combine product details and reviews in a single dictionary
                combined_data = {"productDetails": product_details, "reviews": reviews_data}

                # Append the combined data to the list
                all_products_data.append(combined_data)

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON data: {e}")

        else:
            print("No valid JSON data found in the HTML.")

    else:
        print(f"Failed to fetch the page. Status Code: {response.status_code}")

# Function to store combined data in a JSON file
def store_data():
    # Path to the JSON file
    json_file_path = "product_details.json"

    # Check if the file already exists
    if os.path.exists(json_file_path):
        # Load existing data from the file
        with open(json_file_path, 'r', encoding='utf-8') as existing_file:
            try:
                existing_data = json.load(existing_file)
            except json.JSONDecodeError as e:
                print(f"Failed to load existing JSON data: {e}")
                existing_data = []

        # Append new data to existing data
        existing_data.extend(all_products_data)

        # Write the updated data back to the file
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(existing_data, jsonfile, ensure_ascii=False, indent=4)

    else:
        # If the file doesn't exist, create a new one and write the current data
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(all_products_data, jsonfile, ensure_ascii=False, indent=4)

    # Print the message in the console
    print(f"All product details appended to {json_file_path}.")

# Main program
if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    product_data = scrape_daraz_product(product_name)

    if product_data:
        # Call the store_data function to append all product details to the existing or new JSON file
        store_data()
        print("Product details and reviews extracted.")
    else:
        print("No product data found.")
