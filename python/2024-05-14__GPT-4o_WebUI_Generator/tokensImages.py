import base64
import tiktoken

def get_base64_image_data(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Pfade zu den hochgeladenen Bildern
image_path_1 = 'source-images-tests/orig/sample-1.png'
image_path_2 = 'source-images-tests/orig/sample-3.png'

# Base64-Daten der Bilder
image_data_1 = get_base64_image_data(image_path_1)
image_data_2 = get_base64_image_data(image_path_2)

# Längen der base64-Daten ausgeben
print(f"Length of base64 data for sample-1.png: {len(image_data_1)}")
print(f"Length of base64 data for sample-3.png: {len(image_data_2)}")

# Token-Anzahl der base64-Daten berechnen
encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(encoder.encode(text))

tokens_image_data_1 = count_tokens(image_data_1)
tokens_image_data_2 = count_tokens(image_data_2)

print(f"Token count for base64 data of sample-1.png: {tokens_image_data_1}")
print(f"Token count for base64 data of sample-3.png: {tokens_image_data_2}")