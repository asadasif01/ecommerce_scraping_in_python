import requests
from bs4 import BeautifulSoup
import mysql.connector

# Function to check if a product with the given product_id exists in the database
def product_exists(cursor, product_id):
    check_query = "SELECT product_id FROM products WHERE product_id = %s"
    cursor.execute(check_query, (product_id,))
    return cursor.fetchone() is not None

# Function to get the current maximum 'No' value in the database
def get_max_no(cursor):
    cursor.execute("SELECT MAX(No) FROM products")
    max_no = cursor.fetchone()[0]
    return max_no if max_no else 0

# Function to scrape product data from ebuy.pk and insert it into a MySQL database
def scrape_and_insert_ebuy_product(product_query):
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
            # Create a MySQL connection
            conn = mysql.connector.connect(
                host="localhost",
                user="Your username of db",
                password="Your password of database",
                port="port number",
                database="database name"
            )

            cursor = conn.cursor()

            existing_count = 0  # To count the number of existing products
            inserted_count = 0  # To count the number of inserted products
            max_no = get_max_no(cursor)  # Get the current maximum 'No' value

            for product in product_data:
                product_id = product.get("product_id")
                product_url = product.get("product_url")

                # Check if the product already exists
                if product_exists(cursor, product_id):
                    print(f"Product with ID {product_id} already exists in the database.")
                    existing_count += 1
                else:
                    # Increment 'No' value
                    max_no += 1
                    insert_product_query = "INSERT INTO products (No, product_id, name, original_price, discount, sale_price, image_url, product_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    data = (max_no, product_id, product.get("name"), product.get("original_price"), product.get("discount"), product.get("sale_price"), product.get("image_url"), product_url)
                    cursor.execute(insert_product_query, data)
                    inserted_count += 1

            # Commit the changes and close the database connection
            conn.commit()
            conn.close()

            print(f"{existing_count} product(s) already exist in the database.")
            print(f"{inserted_count} product(s) inserted.")

        else:
            print("No products found on ebuy.")
    else:
        print("Failed to retrieve the page.")

# Function to extract specific key-value pairs from messy data
def extract_specific_data(soup):
    extracted_data = []
    product_elements = soup.find("div", class_="products")

    if product_elements:
        for product in product_elements:
            product_data = {}

            # Extract product_id from the class attribute
            class_attr = product.get("class")
            for attr in class_attr:
                if attr.startswith("post-"):
                    product_data["product_id"] = attr

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
            
            # Extract product URL
            product_link = product.find("a", class_="woocommerce-LoopProduct-link")
            if product_link:
                product_data["product_url"] = product_link["href"]

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
    scrape_and_insert_ebuy_product(product_query)
