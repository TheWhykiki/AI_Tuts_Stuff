# WebUI Generator Installation and Usage Guide

## Installation

1. **Klonen Sie das Repository oder laden Sie die Dateien herunter:**
   Ensure you have the Python script and `requirements.txt` in your working directory.

2. **Setup Virtual Environment:**

   For macOS/Linux:
   ```bash
   # Create the virtual environment
   python3 -m venv webui-generator

   # Activate the virtual environment
   source webui-generator/bin/activate
   ```
    
   For Windows:
    ```
    bash
    # Create the virtual environment
    python -m venv webui-generator
    # Activate the virtual environment
    webui-generator\Scripts\activate
   
3. Install Dependencies:
    ```
    bash
    pip install -r requirements.txt
    ```

4. To run the WebUI Generator, use the following command in your terminal or command prompt:
    ```
    bash
    python WebUI-Generator-v2.py
    ```
### Notes:


Ensure that you have activated the virtual environment where the dependencies are installed before running the script. If you encounter any issues with missing modules, double-check that the virtual environment is activated and all dependencies are installed correctly.

The script expects the images to be accessible via URLs specified in the code. If the images are not accessible, the script will not function correctly.
Adjust the base_url and other configurations in the script as needed to match your project setup.