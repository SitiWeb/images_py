import json
import os
import base64
import tempfile
import requests
from tkinter import messagebox
from woocommerce import API
from utils.image_processing import ImageProcessor
from config.encrypt_config import ConfigEncryptor
from utils.file_operations import FileProcessor
import hashlib
import pprint



def save_credentials(url, consumer_key, consumer_secret, username, password):
    """
    Save WooCommerce and WordPress credentials to an encrypted file.

    Args:
        url (str): The base URL for the WooCommerce store.
        consumer_key (str): The consumer key for WooCommerce API.
        consumer_secret (str): The consumer secret for WooCommerce API.
        username (str): The username for WordPress.
        password (str): The password for WordPress.
    """
    credentials = {
        "url": url,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "username": username,
        "password": password,
    }

    ConfigEncryptor().save_credentials(credentials)


def load_credentials():
    """
    Load WooCommerce and WordPress credentials from an encrypted file.

    Returns:
        dict: The decrypted credentials, or None if the file does not exist.
    """
    creds = ConfigEncryptor().load_credentials()
    return creds


def get_wcapi():
    """
    Get a WooCommerce API client instance using the active credentials.

    Returns:
        woocommerce.API: The WooCommerce API client instance, or None if credentials are missing.
    """
    active_credentials = load_credentials()

    if not active_credentials:
        messagebox.showerror(
            "Missing credentials",
            "No active credentials found. Please configure them in Settings first.",
        )
        return None

    pprint.pprint(active_credentials)

    return API(
        url=active_credentials["url"],
        consumer_key=active_credentials["consumer_key"],
        consumer_secret=active_credentials["consumer_secret"],
        version="wc/v3",
        timeout=30,
    )



def get_product(product_id):
    """
    Get a WooCommerce product and download its images.

    Args:
        product_id (int): The ID of the WooCommerce product.

    Returns:
        tuple: A dictionary of image paths and the product data.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return None
    result = wcapi.get(f"products/{product_id}")

    
    product = result.json()
    
    return product

def get_images(product, limit = 0):
    image_paths = {}
    if product.get("images"):
        images = product.get("images")

        if not os.path.exists("temp"):
            os.makedirs("temp")

        for index, image in enumerate(images):
            image_url = image.get("src")
            image_id = image.get("id")
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                file_name = image_url.split("/")[-1]
                file_path = os.path.join("temp", file_name)
                image_paths[image_id] = file_path
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(
                    f"Image {index + 1}/{len(images)} downloaded and saved: {file_path}"
                )
                if limit and limit >= index +1:
                    break
            else:
                print(f"Failed to download image {index + 1}/{len(images)}")

        return image_paths
    
    else:
        if product.get("name"):
            print(f"No images found for {product.get('name')}")
        else:
            print("No images found")
        return []


def upload_image(img_path):
    """
    Upload an image to WordPress.

    Args:
        img_path (str): The path to the image file.

    Returns:
        int: The ID of the uploaded image, or False if the upload failed.
    """
    with open(img_path, "rb") as img_file:
        data = img_file.read()
    file_name = os.path.basename(img_path)
    file_name = file_name.replace("–", "-")

    credentials = load_credentials()
    if not credentials:
        messagebox.showerror(
            "Error", "No WordPress credentials found. Please set them in the settings."
        )
        return None

    username = credentials["username"]
    password = credentials["password"]
    credentials_base64 = base64.b64encode(f"{username}:{password}".encode())
    url = f"{credentials['url']}/wp-json/wp/v2/media"
    headers = {
        "Content-Type": "image/jpg",
        "Content-Disposition": f"attachment; filename={file_name}",
        "Authorization": f"basic {credentials_base64.decode()}",
    }
    print(f"Uploading image {img_path}")
    try:
        res = requests.post(url=url, data=data, headers=headers, timeout=10)
        res.raise_for_status()
        response_dict = res.json()
        new_id = response_dict.get("id")
        link = (
            response_dict.get("guid").get("rendered")
            if response_dict.get("guid")
            else None
        )
        print(new_id, link)
        return new_id if new_id else False
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image: {e}")
        return False


def delete_img(image_id):
    """
    Delete an image from WordPress.

    Args:
        image_id (int): The ID of the image to delete.
    """
  
    credentials = load_credentials()
    if not credentials:
        messagebox.showerror(
            "Error", "No WordPress credentials found. Please set them in the settings."
        )
        return None

    url = f"{credentials['url']}/wp-json/wp/v2/media/{image_id}"
    username = credentials["username"]
    password = credentials["password"]
    credentials_base64 = base64.b64encode(f"{username}:{password}".encode())

    res = requests.delete(
        url=url,
        headers={"Authorization": f"basic {credentials_base64.decode()}"},
        params={"force": "true"},
        timeout=10,
    )

    if res.status_code == 200:
        print(f"Image with ID {image_id} deleted successfully.")
    else:
        print(f"Failed to delete image with ID {image_id}. Error: {res.text}")






def update_product(product_id, new_list, old_list, options):
    """
    Update the images and meta data of a WooCommerce product.

    Args:
        image_ids (list): A list of new image IDs.
        product_id (int): The ID of the WooCommerce product.
    """
    
    wcapi = get_wcapi()
    if not wcapi:
        return

    # Prepare the data with images and meta data fields
    product_data = {
        "images": [{"id": image_id} for image_id in new_list],
        "meta_data": [
            {
                "key": "_image_processed",
                "value": options['hash_string']
            },
            {
                "key": "_old_image_ids",
                "value": [{"id": image_id} for image_id in old_list]
            }

        ]
    }

    # Print product data for debugging
    print(f"Updating product {product_id} with the following data:")
    print(json.dumps(product_data, indent=2))

    # Send the update request with images and meta data fields
    response = wcapi.put(f"products/{product_id}", data=product_data)  # Using 'json' to pass data
    
    if response.status_code == 200:
        print(f"Product with ID {product_id} updated successfully with new image IDs and meta data.")
    else:
        print(f"Failed to update product with ID {product_id}. Error: {response.text}")



def process_product_images(options):
    """
    Process images for a WooCommerce product by resizing and uploading them.

    Args:
        options (dict): Contains options such as product_id, name_template, canvas_width, canvas_height.
    """
    
    # Concatenate the values into a string
    hash_input = f"{options['background_color']}_{options['canvas_height']}_{options['canvas_width']}_{options['image_format']}_{options['image_size']}"

    # Create a SHA256 hash from the concatenated string
    hash_object = hashlib.sha256(hash_input.encode())
    hash_string = hash_object.hexdigest()
    options['hash_string'] = hash_string
    pprint.pprint(hash_string)
    product_id = options.get("product_id")
    if not product_id:
        print("No product ID")
        return
    product = options.get("product")
    # Check if the product meta_data contains _image_processed with the current hash
    if product['meta_data']:
        for meta in product['meta_data']:
            if meta['key'] == '_image_processed' and meta['value'] == hash_string:
                print(f"Skipping product {product_id}, already processed with the current hash.")
                return
    image_paths = get_images(product)
    if not image_paths:
        return
    
   

    
   
    with tempfile.TemporaryDirectory() as temp_output_directory:
        print(f"Using temporary directory: {temp_output_directory}")

        old_list = []
        new_list = []
        pprint.pprint ( list(image_paths.values()))
        file = FileProcessor()
        log = options.get("log_message", None)
        
        
        for image_id, file_path in image_paths.items():
            
            processed = file.process_images([file_path], temp_output_directory, options, log, product)

            
            new_id = upload_image(processed[0])

            if new_id:
                old_list.append(image_id)
                new_list.append(new_id)

        if new_list:
            options["image_ids"] = new_list  # Store new image IDs in options
            update_product(product_id, new_list, old_list, options)  # Pass new image IDs here
            for old in old_list:
                delete_img(old)
        print("Temporary files processed and uploaded successfully.")


def generate_output_path(
    temp_output_directory, file_path, template, product, canvas_width, canvas_height
):
    """
    Generate the output path for resized images based on a template.

    Args:
        temp_output_directory (str): The path to the temporary output directory.
        file_path (str): The original file path.
        template (str): The template for generating the new filename.
        product (dict): The WooCommerce product data.
        canvas_width (int): The width of the canvas for resizing images.
        canvas_height (int): The height of the canvas for resizing images.

    Returns:
        str: The generated output path.
    """
    name, ext = os.path.splitext(os.path.basename(file_path))
    width = canvas_width
    height = canvas_height
    sku = product.get("sku", "")
    slug = product.get("name", "")
    title = product.get("slug", "")
    new_filename = template.format(
        name=name, sku=sku, width=width, height=height, slug=slug, title=title
    )
    return os.path.join(temp_output_directory, new_filename + ext)

def get_first_image_path(product):
    images = get_images(product, 1)
    # Loop through the dictionary
    if images:
        for image_id, file_path in images.items():
            print(f"Processing Image ID: {image_id}")
            print(f"File Path: {file_path}")
            return file_path
def get_first_image():
    """
    Process images for all WooCommerce products by resizing and uploading them.

    Args:
        options (dict): Contains options such as name_template, canvas_width, canvas_height.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return

    page = 1
    total_products = 0  # Initialize the counter for total products


    products = wcapi.get("products", params={"per_page": 5, "page": page}).json()
    if not products:
        return
    for product in products:
        total_products += 1  # Update the total count
        return get_first_image_path(product)
            
def search_product(search):
    """
    Process images for all WooCommerce products by resizing and uploading them.

    Args:
        options (dict): Contains options such as name_template, canvas_width, canvas_height.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return

    page = 1
    total_products = 0  # Initialize the counter for total products

    log = options.get("log_message", None)

    while True:
        products = wcapi.get("products", params={"per_page": 100, "page": page, "search": search}).json()
        if not products:
            break
        return products

def process_all_products(options):
    """
    Process images for all WooCommerce products by resizing and uploading them.

    Args:
        options (dict): Contains options such as name_template, canvas_width, canvas_height.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return

    page = 1
    total_products = 0  # Initialize the counter for total products

    while True:
        products = wcapi.get("products", params={"per_page": 100, "page": page}).json()
        if not products:
            break

        product_count = len(products)  # Get the count of products on the current page
        

        for product in products:
            total_products += 1  # Update the total count
            options["product_id"] = product["id"]
            options["product"] = product
            if log:
                if product:
                    name = product.get("name", "")
                    log.log_message(f"#{total_products} Processing {name} ")  # Log the product name
            process_product_images(options)

        page += 1

    # Log the total number of products processed
    if log:
        log.log_message(f"Total products processed: {total_products}")

    # Show completion message
    messagebox.showinfo(
        "Process Complete", f"All product images processing is complete. Total products processed: {total_products}"
    )
