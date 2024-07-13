"""
Module for WooCommerce API interactions and image processing.
"""

import json
import os
import base64
import tempfile
import pprint
from tkinter import messagebox
from cryptography.fernet import Fernet
import requests
from woocommerce import API
from utils.image_processing import ImageProcessor

CREDENTIALS_FILE = "credentials.json"

# Hardcoded key (replace with your generated key)
KEY = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="


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
    credentials_str = json.dumps(credentials)
    fernet = Fernet(KEY)
    encrypted = fernet.encrypt(credentials_str.encode())
    with open("config.enc", "wb") as file:
        file.write(encrypted)


def load_credentials():
    """
    Load WooCommerce and WordPress credentials from an encrypted file.

    Returns:
        dict: The decrypted credentials, or None if the file does not exist.
    """
    if not os.path.exists("config.enc"):
        return None
    fernet = Fernet(KEY)
    with open("config.enc", "rb") as file:
        encrypted = file.read()
    decrypted = fernet.decrypt(encrypted).decode()
    return json.loads(decrypted)


def get_wcapi():
    """
    Get a WooCommerce API client instance.

    Returns:
        woocommerce.API: The WooCommerce API client instance, or None if credentials are missing.
    """
    credentials = load_credentials()
    if not credentials:
        messagebox.showerror(
            "Error",
            "No WooCommerce credentials found. Please set them in the settings.",
        )
        return None
    return API(
        url=credentials["url"],
        consumer_key=credentials["consumer_key"],
        consumer_secret=credentials["consumer_secret"],
        version="wc/v3",
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

    image_paths = {}
    product = result.json()
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
            else:
                print(f"Failed to download image {index + 1}/{len(images)}")
    else:
        if product.get("name"):
            print(f"No images found for {product.get('name')}")
        else:
            print("No images found")
    return image_paths, product


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


def update_product(image_ids, product_id):
    """
    Update a WooCommerce product with new image IDs.

    Args:
        image_ids (list): A list of new image IDs.
        product_id (int): The ID of the WooCommerce product.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return

    product = wcapi.get(f"products/{product_id}").json()
    product["images"] = [{"id": image_id} for image_id in image_ids]
    response = wcapi.put(f"products/{product_id}", data=product)
    if response.status_code == 200:
        print(
            f"Product with ID {product_id} updated successfully with new image IDs.")
    else:
        print(
            f"Failed to update product with ID {product_id}. Error: {response.text}")


def process_product_images(product_id, name_template, canvas_width, canvas_height):
    """
    Process images for a WooCommerce product by resizing and uploading them.

    Args:
        product_id (int): The ID of the WooCommerce product.
        name_template (str): The template for generating image filenames.
        canvas_width (int): The width of the canvas for resizing images.
        canvas_height (int): The height of the canvas for resizing images.
    """
    print(name_template)
    image_paths, product = get_product(product_id)
    if not image_paths:
        return

    with tempfile.TemporaryDirectory() as temp_output_directory:
        print(f"Using temporary directory: {temp_output_directory}")

        old_list = []
        new_list = []

        for image_id, file_path in image_paths.items():
            output_path = generate_output_path(
                temp_output_directory,
                file_path,
                name_template,
                product,
                canvas_width,
                canvas_height,
            )
            resize_image(file_path, output_path, "")
            new_id = upload_image(output_path)
            if new_id:
                old_list.append(image_id)
                new_list.append(new_id)

        update_product(new_list, product_id)
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
    pprint.pprint(product)
    new_filename = template.format(
        name=name, sku=sku, width=width, height=height, slug=slug, title=title
    )
    return os.path.join(temp_output_directory, new_filename + ext)


def process_all_products(name_template, canvas_width, canvas_height):
    """
    Process images for all WooCommerce products by resizing and uploading them.

    Args:
        name_template (str): The template for generating image filenames.
        canvas_width (int): The width of the canvas for resizing images.
        canvas_height (int): The height of the canvas for resizing images.
    """
    wcapi = get_wcapi()
    if not wcapi:
        return

    page = 1
    while True:
        products = wcapi.get("products", params={
                             "per_page": 100, "page": page}).json()
        if not products:
            break

        for product in products:
            process_product_images(
                product["id"], name_template, canvas_width, canvas_height
            )

        page += 1

    messagebox.showinfo(
        "Process Complete", "All product images processing is complete."
    )
