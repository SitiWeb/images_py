Image Processing Application Documentation
Overview

This Image Processing Application provides a GUI for selecting directories containing image files, setting canvas sizes, adding suffixes to filenames, and processing images. It logs all found images, displays how many images were found, and provides previews of the first image before and after processing.
Prerequisites

    Python 3.10+: Ensure Python is installed on your machine.
    Tkinter: This should come with Python, but ensure it's installed.
    Pillow: For image handling. Install via pip:

    sh

    pip install pillow

    Additional Libraries: Ensure you have any additional libraries your utility functions (file_operations, image_processing) depend on.

Application Setup

    Install Required Packages:

    sh

pip install pillow

Directory Structure:
Ensure your project directory looks something like this:

arduino

    image-processor/
    ├── ui/
    │   └── local_processing_tab.py
    ├── utils/
    │   ├── file_operations.py
    │   └── image_processing.py
    └── main.py

    Script Files:
        main.py: The main entry point of the application containing the script provided above.
        file_operations.py: Contains browse_directory and other directory-related utility functions.
        image_processing.py: Contains set_canvas_size and other image processing utility functions.

Running the Application

To run the application, navigate to the project directory and execute:

sh

python main.py

Creating an Executable

To create an executable for this application, you can use pyinstaller. Follow the steps below:

    Install PyInstaller:

    sh

pip install pyinstaller

Create the Executable:
Navigate to the directory containing your main.py script and run:

sh

pyinstaller --onefile --windowed main.py

    --onefile: Packages everything into a single executable file.
    --windowed: Ensures the console window does not appear when running the GUI application.

Locate the Executable:
After running the command, you will find the executable in the dist folder within your project directory.