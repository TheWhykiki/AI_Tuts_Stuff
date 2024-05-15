import sys
import os
import requests
import base64
from IPython.display import Image as IPythonImage, display
import tiktoken

# Konfiguration


chatgpt_endpoint = "https://api.openai.com/v1/chat/completions"
model_name = 'gpt-4o'
images_folder = 'source-images'
output_folder_base = 'generator_output'  # Basisverzeichnis für die Ausgabe
output_folder_images = f'{output_folder_base}/images'  # Verzeichnis für die Ausgabe der generierten Bilder
image_gen_endpoint = 'https://api.openai.com/v1/images/generations'
image_model_name = 'dall-e-3'

analysis_prompt = (
    "Du bist WebUIAnalyzer GPT, ein Fachmann in der Erstellung und Analyse von Webseiten. Deine Expertise umfasst HTML, JS und CSS. Du bist angehalten, Webseiten-Screenshots präzise zu analysieren. Erstelle auf Basis des bereitgestellten Bildes sauber formatierten HTML-Code. Analysiere das Bild gründlich und erstelle HTML, das der Struktur und dem Inhalt des Bildes entspricht. "
    "Du darfst keine externen Quellen konsultieren und sollst keine unsicheren oder ungenauen Daten verwenden. Stelle sicher, dass der HTML-Code gut strukturiert ist und den modernen Webstandards entspricht. Das benötigte CSS wird als Inline-CSS im Head des HTML eingefügt."
    "Deine Antwort ist immer valides HTML, das immer mit <html> beginnt und mit </html> endet. Du darfst auf keinen Fall gegen diese Regel verstossen."
    "Du analysierst genau und Schritt für Schritt wie der Inhalt und die UI der Webseite auf dem Screenshot aussehen und erstellst genau das als HTML. Du kennst dir keine eigenen Dummy-Inhalte aus und du wirst auch keine Bereiche auslassen. Dein Ziel und deine Aufgabe ist es, den Inhalt des Screenshots so exakt wie möglich in valides HTML umzuwandeln. Erfinde keine FLiesstexte oder Headlines, sondern gib exakt das wieder, das du in einer detailierten Betrachtung des Webseiten-Screenshots gesehen hast."
    "Du antwortest ausschließlich in validem HTML, deine Antwort muss immer mit <html> beginnen und mit </html> enden. Ekläre nichts, deine Antwort besteht nur aus dem gewünschten Code."
)

encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text):
    return len(encoder.encode(text))

def log_token_count(step, text):
    token_count = count_tokens(text)
    with open("token_counts.log", "a") as log_file:
        log_file.write(f"{step}: {token_count} tokens\n")
    print(f"{step}: {token_count} tokens")
    return token_count

def create_required_directories():
    # Überprüft und erstellt das Basisverzeichnis für die Ausgabe
    if not os.path.exists(output_folder_base):
        os.makedirs(output_folder_base)
        print(f"Basisverzeichnis erstellt: {output_folder_base}")
    else:
        print(f"Basisverzeichnis existiert bereits: {output_folder_base}")

    # Überprüft und erstellt das Verzeichnis für die Ausgabe der generierten Bilder
    if not os.path.exists(output_folder_images):
        os.makedirs(output_folder_images)
        print(f"Bilderverzeichnis erstellt: {output_folder_images}")
    else:
        print(f"Bilderverzeichnis existiert bereits: {output_folder_images}")

def load_image(image_path):
    # Bild zur Kontextdarstellung öffnen und anzeigen
    display(IPythonImage(filename=image_path))
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_image_to_chatgpt(image_data):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": analysis_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
            ]}
        ],
        "max_tokens": 300
    }
    print(f"Image data length: {len(image_data)}")
    log_token_count("Request before sending to API", str(data))
    response = requests.post(chatgpt_endpoint, headers=headers, json=data)
    log_token_count("Response from API", str(response.json()))
    print("Erhaltene Antwort von ChatGPT API:")
    print(response.json())
    return response.json()

def create_html_file(html_content, file_number):
    file_path = f"{output_folder_base}/sample-{file_number:02}.html"
    with open(file_path, "w") as file:
        file.write(html_content)
    print(f"HTML-Datei gespeichert: {file_path}")
    return file_path

def main():
    print("Starte das Skript...")
    create_required_directories()

    images = os.listdir(images_folder)
    if not images:
        print("Keine Bilder im Ordner source-images gefunden. Bitte Bilder in den Ordner legen und das Skript erneut starten.")
        sys.exit()

    for idx, image_name in enumerate(images):
        image_path = os.path.join(images_folder, image_name)
        print(f"Lade und verarbeite Bild {image_name}...")
        image_data = load_image(image_path)

        print(f"Sende Bild {image_name} zur Analyse...")
        token_count_before = log_token_count("Token count before sending image to API", image_data)
        result = send_image_to_chatgpt(image_data)
        token_count_after = log_token_count("Token count after receiving response from API", str(result))

        print(f"Token count before sending to API: {token_count_before}")
        print(f"Token count after receiving response: {token_count_after}")

        if 'choices' in result and result['choices']:
            html_content = result['choices'][0]['message']['content']
            print(f"HTML-Inhalt für {image_name} erhalten. Erstelle HTML-Datei...")
            html_file_path = create_html_file(html_content, idx)
            print(f"HTML-Datei gespeichert: {html_file_path}")
        else:
            print(f"Keine valide Antwort für {image_name}. Überprüfe die API-Antwort und -Anfrage.")

        print(f"Verarbeitung für {image_name} abgeschlossen.")

if __name__ == "__main__":
    main()
