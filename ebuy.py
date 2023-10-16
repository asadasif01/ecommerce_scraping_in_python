import requests
from bs4 import BeautifulSoup

# Function to scrape product data from ebuy.pk
def scrape_ebuy_product(product_query):
    if len(product_query.strip()) < 3:
        print("Please enter a more specific product query.")
        return

    # URL of the ebuy.pk search results page for the given product query
    url = f"https://ebuy.pk/?product_cat=&s={product_query}&post_type=product"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product information
        product_data = extract_specific_data(soup)

        if product_data:
            print("Extracted product data:")
            for i, product in enumerate(product_data, start=1):
                print(f"Product {i}:")
                for key, value in product.items():
                    print(f"{key}: {value}")
                print("\n---\n")
        else:
            print("No products found in ebuy.")

    else:
        print("Failed to retrieve the page.")

# Function to extract specific key-value pairs from messy data
def extract_specific_data(soup):
    extracted_data = []
    product_elements = soup.find("div", class_="products")
    
    if product_elements:
        for product in product_elements:
            product_data = {}

            # Extract product name
            product_name = product.find("a", class_="woocommerce-LoopProduct-link")
            if product_name:
                product_data["name"] = product_name.text.strip()

            # Extract original price
            original_price = product.find("span", class_="woocommerce-Price-amount")
            if original_price:
                product_data["original_price"] = original_price.text.strip()

            # Extract discount (if available)
            discount = product.find("span", class_="onsale")
            if discount:
                product_data["discount"] = discount.text.strip()
            else:
                product_data["discount"] = "No discount"

            # Extract image URL
            image_container = product.find("div", class_="image-fade_in_back")
            if image_container:
                image_tag = image_container.find("img", src=True)
                if image_tag:
                    product_data["image_url"] = image_tag["data-src"]

            # Check if the product is on sale
            is_on_sale = product.find("span", class_="woocommerce-Price-currencySymbol")
            if is_on_sale:
                # Extract sale price from the "bdi" tag
                sale_price = is_on_sale.find_next("bdi").text.strip()
                if sale_price:
                    product_data["sale_price"] = sale_price
                else:
                    product_data["sale_price"] = None
            else:
                product_data["sale_price"] = None

            extracted_data.append(product_data)

    return extracted_data

if __name__ == "__main__":
    product_query = input("Enter the product query: ")
    scrape_ebuy_product(product_query)
