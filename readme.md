Image Processing Application

This application is a graphical user interface (GUI) tool designed for processing images either from a local directory or from a WooCommerce product catalog. It supports resizing images, renaming them based on customizable templates, and uploading them to a WooCommerce site.
Features

    Resize images to specified dimensions.
    Rename images using customizable templates with placeholders for various attributes.
    Upload processed images to WooCommerce.
    Process images from a local directory or WooCommerce products.

Prerequisites

    Python 3.10 or later

    Required Python Packages

    You can install the required packages using pip:

    sh

    pip install -r requirements.txt

    ImageMagick

    ImageMagick is required for image processing. You can download and install it from ImageMagick's official website.

    WooCommerce API Credentials

    You need to have WooCommerce API credentials to interact with the WooCommerce site. These include the URL, consumer key, consumer secret, username, and password.

Setting Up

    Clone the Repository

    Clone this repository to your local machine:

    sh

git clone https://github.com/your-username/image-processing-app.git
cd image-processing-app

Install Dependencies

Install the required Python packages:

sh

    pip install -r requirements.txt

    Configure WooCommerce API Credentials

    Run the application and navigate to the Settings tab to enter and save your WooCommerce API credentials.

Running the Application

Run the main application script:

sh

python main.py

Creating an Executable

To create a standalone executable from this project, you can use PyInstaller. Follow the steps below:

    Install PyInstaller

    You can install PyInstaller using pip:

    sh

pip install pyinstaller

Generate the Executable

Navigate to the project directory and run PyInstaller:

sh

    pyinstaller --onefile --noconsole main.py

    Find the Executable

    After PyInstaller finishes, you can find the executable in the dist directory.

File Structure

    main.py: Entry point for the application.
    api/: Contains the woocommerce.py file for interacting with WooCommerce API.
    utils/: Contains utility scripts for file operations and image processing.
    ui/: Contains the UI components for the application.
    config.enc: Encrypted file storing WooCommerce API credentials.

Requirements

Create a requirements.txt file with the following content:

tk
Pillow
requests
woocommerce
cryptography
pyinstaller

Usage

    Select Source Type
        Choose between local directory and WooCommerce product.

    Set Canvas Size
        Specify the dimensions to resize the images.

    Filename Template
        Define a template for renaming the images using placeholders like {name}, {sku}, {width}, {height}.

    Start Processing
        Click the "Start Processing" button to process the images. The log will appear in a separate window.

Notes

    Ensure ImageMagick is correctly installed and added to your system's PATH.
    The application uses the cryptography library to encrypt WooCommerce API credentials for security.

Support

If you encounter any issues or have questions, feel free to open an issue in the repository or contact the maintainer.
License

This project is licensed under the MIT License.
Acknowledgements

    ImageMagick
    WooCommerce

With this information, you should be able to set up, run, and create an executable for the Image Processing Application. Enjoy processing your images with ease!