from PIL import Image
import base64
import tiktoken
import os

# Konfiguration
source_folder = '../source-images'
optimized_folder = '../optimized-sources'
resaved_folder = '../resaved-sources'
no_exif_folder = '../no-exif-sources'

# Stelle sicher, dass die Ordner existieren
os.makedirs(optimized_folder, exist_ok=True)
os.makedirs(resaved_folder, exist_ok=True)
os.makedirs(no_exif_folder, exist_ok=True)

# Encoder initialisieren
encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(encoder.encode(text))

def get_base64_image_data(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def optimize_image(image_path, optimized_path):
    img = Image.open(image_path)
    img.save(optimized_path, optimize=True, quality=85)

def resave_image(image_path, resaved_path):
    img = Image.open(image_path)
    img.save(resaved_path)

def remove_exif(image_path, output_path):
    img = Image.open(image_path)
    data = list(img.getdata())
    image_no_exif = Image.new(img.mode, img.size)
    image_no_exif.putdata(data)
    image_no_exif.save(output_path, "JPEG")

# Gehe durch alle Bilder im Quellordner
for filename in os.listdir(source_folder):
    if filename.endswith(".jpg"):
        image_path = os.path.join(source_folder, filename)
        optimized_image_path = os.path.join(optimized_folder, filename)
        resaved_image_path = os.path.join(resaved_folder, filename)
        no_exif_image_path = os.path.join(no_exif_folder, filename)

        # Optimieren der Bilder
        optimize_image(image_path, optimized_image_path)

        # Bild neu speichern
        resave_image(image_path, resaved_image_path)

        # Entfernen der EXIF-Daten
        remove_exif(image_path, no_exif_image_path)

        # Base64-Daten der Originalbilder
        image_data = get_base64_image_data(image_path)

        # Base64-Daten der optimierten Bilder
        optimized_image_data = get_base64_image_data(optimized_image_path)

        # Base64-Daten der neu gespeicherten Bilder
        resaved_image_data = get_base64_image_data(resaved_image_path)

        # Base64-Daten der Bilder ohne EXIF-Daten
        no_exif_image_data = get_base64_image_data(no_exif_image_path)

        # Längen der base64-Daten ausgeben
        print(f"Length of base64 data for {filename}: {len(image_data)}")
        print(f"Length of base64 data for optimized {filename}: {len(optimized_image_data)}")
        print(f"Length of base64 data for resaved {filename}: {len(resaved_image_data)}")
        print(f"Length of base64 data for no-exif {filename}: {len(no_exif_image_data)}")

        # Token-Anzahl der base64-Daten berechnen
        tokens_image_data = count_tokens(image_data)
        tokens_optimized_image_data = count_tokens(optimized_image_data)
        tokens_resaved_image_data = count_tokens(resaved_image_data)
        tokens_no_exif_image_data = count_tokens(no_exif_image_data)

        # Token-Anzahl der base64-Daten ausgeben
        print(f"Token count for base64 data of {filename}: {tokens_image_data}")
        print(f"Token count for base64 data of optimized {filename}: {tokens_optimized_image_data}")
        print(f"Token count for base64 data of resaved {filename}: {tokens_resaved_image_data}")
        print(f"Token count for base64 data of no-exif {filename}: {tokens_no_exif_image_data}")