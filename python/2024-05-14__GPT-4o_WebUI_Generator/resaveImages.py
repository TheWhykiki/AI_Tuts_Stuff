from PIL import Image
import base64
import tiktoken
import os

# Konfiguration
source_folder = 'source-images'

# Pfade zu den hochgeladenen Bildern
image_path_1 = os.path.join(source_folder, 'sample-1.jpg')
image_path_2 = os.path.join(source_folder, 'sample-3.jpg')

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

# Pfade zu den optimierten und neu gespeicherten Bildern
optimized_image_path_1 = os.path.join(source_folder, 'optimized-sample-1.jpg')
optimized_image_path_2 = os.path.join(source_folder, 'optimized-sample-3.jpg')
resaved_image_path_1 = os.path.join(source_folder, 'resaved-sample-1.jpg')
resaved_image_path_2 = os.path.join(source_folder, 'resaved-sample-3.jpg')
no_exif_image_path_1 = os.path.join(source_folder, 'no-exif-sample-1.jpg')
no_exif_image_path_2 = os.path.join(source_folder, 'no-exif-sample-3.jpg')

# Optimieren der Bilder
optimize_image(image_path_1, optimized_image_path_1)
optimize_image(image_path_2, optimized_image_path_2)

# Bild neu speichern
resave_image(image_path_1, resaved_image_path_1)
resave_image(image_path_2, resaved_image_path_2)

# Entfernen der EXIF-Daten
remove_exif(image_path_1, no_exif_image_path_1)
remove_exif(image_path_2, no_exif_image_path_2)

# Base64-Daten der Originalbilder
image_data_1 = get_base64_image_data(image_path_1)
image_data_2 = get_base64_image_data(image_path_2)

# Base64-Daten der optimierten Bilder
optimized_image_data_1 = get_base64_image_data(optimized_image_path_1)
optimized_image_data_2 = get_base64_image_data(optimized_image_path_2)

# Base64-Daten der neu gespeicherten Bilder
resaved_image_data_1 = get_base64_image_data(resaved_image_path_1)
resaved_image_data_2 = get_base64_image_data(resaved_image_path_2)

# Base64-Daten der Bilder ohne EXIF-Daten
no_exif_image_data_1 = get_base64_image_data(no_exif_image_path_1)
no_exif_image_data_2 = get_base64_image_data(no_exif_image_path_2)

# Längen der base64-Daten ausgeben
print(f"Length of base64 data for sample-1.jpg: {len(image_data_1)}")
print(f"Length of base64 data for sample-3.jpg: {len(image_data_2)}")
print(f"Length of base64 data for optimized sample-1.jpg: {len(optimized_image_data_1)}")
print(f"Length of base64 data for optimized sample-3.jpg: {len(optimized_image_data_2)}")
print(f"Length of base64 data for resaved sample-1.jpg: {len(resaved_image_data_1)}")
print(f"Length of base64 data for resaved sample-3.jpg: {len(resaved_image_data_2)}")
print(f"Length of base64 data for no-exif sample-1.jpg: {len(no_exif_image_data_1)}")
print(f"Length of base64 data for no-exif sample-3.jpg: {len(no_exif_image_data_2)}")

# Token-Anzahl der base64-Daten berechnen
tokens_image_data_1 = count_tokens(image_data_1)
tokens_image_data_2 = count_tokens(image_data_2)
tokens_optimized_image_data_1 = count_tokens(optimized_image_data_1)
tokens_optimized_image_data_2 = count_tokens(optimized_image_data_2)
tokens_resaved_image_data_1 = count_tokens(resaved_image_data_1)
tokens_resaved_image_data_2 = count_tokens(resaved_image_data_2)
tokens_no_exif_image_data_1 = count_tokens(no_exif_image_data_1)
tokens_no_exif_image_data_2 = count_tokens(no_exif_image_data_2)

# Token-Anzahl der base64-Daten ausgeben
print(f"Token count for base64 data of sample-1.jpg: {tokens_image_data_1}")
print(f"Token count for base64 data of sample-3.jpg: {tokens_image_data_2}")
print(f"Token count for base64 data of optimized sample-1.jpg: {tokens_optimized_image_data_1}")
print(f"Token count for base64 data of optimized sample-3.jpg: {tokens_optimized_image_data_2}")
print(f"Token count for base64 data of resaved sample-1.jpg: {tokens_resaved_image_data_1}")
print(f"Token count for base64 data of resaved sample-3.jpg: {tokens_resaved_image_data_2}")
print(f"Token count for base64 data of no-exif sample-1.jpg: {tokens_no_exif_image_data_1}")
print(f"Token count for base64 data of no-exif sample-3.jpg: {tokens_no_exif_image_data_2}")
