from cryptography.fernet import Fernet
import json
import os
import requests
import base64
from woocommerce import API
from tkinter import messagebox
import tempfile
from utils.image_processing import resize_image
import pprint
credentials_file = 'credentials.json'

# Hardcoded key (replace with your generated key)
key = b'u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI='

def save_credentials(url, consumer_key, consumer_secret, username, password):
    credentials = {
        'url': url,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'username': username,
        'password': password
    }
    credentials_str = json.dumps(credentials)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(credentials_str.encode())
    with open('config.enc', 'wb') as file:
        file.write(encrypted)

def load_credentials():
    if not os.path.exists('config.enc'):
        return None
    fernet = Fernet(key)
    with open('config.enc', 'rb') as file:
        encrypted = file.read()
    decrypted = fernet.decrypt(encrypted).decode()
    return json.loads(decrypted)


def get_wcapi():
    credentials = load_credentials()
    if not credentials:
        messagebox.showerror("Error", "No WooCommerce credentials found. Please set them in the settings.")
        return None
    return API(
        url=credentials['url'],
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        version="wc/v3"
    )

def get_product(id):
    wcapi = get_wcapi()
    if not wcapi:
        return None
    result = wcapi.get("products/"+str(id))

    image_paths = {}
    product = result.json()
    if product.get('images'):
        images = product.get('images')
        
        if not os.path.exists('temp'):
            os.makedirs('temp')

        for index, image in enumerate(images):
            image_url = image.get('src')
            image_id = image.get('id')
            response = requests.get(image_url)
            if response.status_code == 200:
                file_name = image_url.split('/')[-1]
                file_path = os.path.join('temp', file_name)
                image_paths[image_id] = file_path
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Image {index + 1}/{len(images)} downloaded and saved: {file_path}")
            else:
                print(f"Failed to download image {index + 1}/{len(images)}")
    else:
        if product.get('name'):
            print(f"No images found for {product.get('name')}")
        else:
            print("No images found")
    return image_paths, product

def upload_image(imgPath):
    data = open(imgPath, 'rb').read()
    fileName = os.path.basename(imgPath)
    credentials = load_credentials()
    if not credentials:
        messagebox.showerror("Error", "No WordPress credentials found. Please set them in the settings.")
        return None

    username = credentials['username']
    password = credentials['password']
    credentials_base64 = base64.b64encode(f"{username}:{password}".encode())
    credentials_base64 = base64.b64encode(f"{username}:{password}".encode())
    url = f"{credentials['url']}/wp-json/wp/v2/media"
    headers = {
        'Content-Type': 'image/jpg',
        'Content-Disposition': f'attachment; filename={fileName}',
        'Authorization': f'basic {credentials_base64.decode()}'
    }

    try:
        res = requests.post(url=url, data=data, headers=headers)
        res.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        newDict = res.json()
        newID = newDict.get('id')
        link = newDict.get('guid').get("rendered") if newDict.get('guid') else None
        print(newID, link)
        return newID if newID else False
    except requests.exceptions.RequestException as e:
        print(f"Error uploading image: {e}")
        return False

def delete_img(image_id):
    credentials = load_credentials()
    if not credentials:
        messagebox.showerror("Error", "No WordPress credentials found. Please set them in the settings.")
        return None

    url = f"{credentials['url']}/wp-json/wp/v2/media/{image_id}"
    username = credentials['username']
    password = credentials['password']
    credentials_base64 = base64.b64encode(f"{username}:{password}".encode())

    res = requests.delete(url=url,
                          headers={'Authorization': f'basic {credentials_base64.decode()}'},
                          params={'force': 'true'})

    if res.status_code == 200:
        print(f"Image with ID {image_id} deleted successfully.")
    else:
        print(f"Failed to delete image with ID {image_id}. Error: {res.text}")

def update_product(image_ids, old_image_ids, product_id):
    wcapi = get_wcapi()
    if not wcapi:
        return

    product = wcapi.get(f"products/{product_id}").json()
    product['images'] = [{'id': image_id} for image_id in image_ids]
    response = wcapi.put(f"products/{product_id}", data=product)
    if response.status_code == 200:
        print(f"Product with ID {product_id} updated successfully with new image IDs.")
    else:
        print(f"Failed to update product with ID {product_id}. Error: {response.text}")

def process_product_images(id, name_template, canvas_width, canvas_height):
    print(name_template)
    image_paths, product = get_product(id)
    if not image_paths:
        return

    with tempfile.TemporaryDirectory() as temp_output_directory:
        print(f"Using temporary directory: {temp_output_directory}")

        old_list = []
        new_list = []

        for image_id, file_path in image_paths.items():
            output_path = generate_output_path(temp_output_directory, file_path, name_template, product, canvas_width, canvas_height)
            resize_image(file_path, output_path, '')
            new_id = upload_image(output_path)
            if new_id:
                old_list.append(image_id)
                new_list.append(new_id)

        update_product(new_list, old_list, id)
        print("Temporary files processed and uploaded successfully.")

def generate_output_path(temp_output_directory, file_path, template, product, canvas_width, canvas_height):
    # Generate the new filename based on the template
    name, ext = os.path.splitext(os.path.basename(file_path))
    width = canvas_width
    height = canvas_height
    sku = product.get('sku', '')
    slug = product.get('name', '')
    title = product.get('slug', '')
    pprint.pprint(product)
    # Here you can add more attributes to the template if needed
    new_filename = template.format(name=name, sku=sku, width=width, height=height, slug=slug, title=title)
    return os.path.join(temp_output_directory, new_filename + ext)

def process_all_products(name_template):
    wcapi = get_wcapi()
    if not wcapi:
        return
    
    page = 1
    while True:
        products = wcapi.get("products", params={"per_page": 100, "page": page}).json()
        if not products:
            break

        for product in products:
            process_product_images(product['id'], name_template)

        page += 1

    messagebox.showinfo("Process Complete", "All product images processing is complete.")
