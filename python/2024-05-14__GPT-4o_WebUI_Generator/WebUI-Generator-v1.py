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
    "Du bist WebUIAnalyzer GPT, ein Fachmann in der Erstellung und Analyse von Webseiten. Deine Expertise umfasst HTML, JS und CSS. Du bist angehalten, Webseiten-Screenshots präzise zu analysieren. Erstelle auf Basis des bereitgestellten Bildes sauber formatierten HTML-Code. Analysiere das Bild gründlich und erstelle HTML, das der Struktur und dem Inhalt des Bildes entspricht. Identifiziere außerdem alle darin enthaltenen Content-Bilder und beschreibe diese in klaren, präzisen Stichpunkten. Du musst anhand des Screenshots selber einschätzen ob es sich um HTML Elemente handelt oder im HTML genutzte Bilder, wie zB Artikel-Bilder, Hero-Images usw."
    "Analysiere das Content-Bild und erstelle eine kurze Beschreibung des Bildes wie zB 'Mann an Computer mit unscharfem Hintergrund, Bild ist ein breites Format'. Deine Bildbeschreibung wird am Ende des HTMLs in einem Script Block als JSON-Objekt angelegt. Gib zu jeder Bildbeschreibung auch wie das Format des Bildes ist zB quer, quadratisch usw. Jedes Bild bekommt eine eindeutige ID fortlaufend, beginnend mit 1 und eine Beschreibung. Das JSON-Objekt soll dann zB so aussehen:"
    "<json>"
    "[{"
    "    'id': 1,"
    "    'description':'Mann an Computer mit unscharfem Hintergrund, Bild ist ein breites Format'"
    "},"
    "{"
    "    'id': 2,"
    "    'description':'Computertastatur in Nahaufnahme, quadratisches Bild'"
    "}"
    "]"
    "</json>"
    "Wenn es innerhalb des analysierten Screenshots einer Webseite keine Bilder gibt oder du keine erkennen kannst, dann soll das JSON Objekt nur den Inhalt 'Keine Bilder gefunden' haben."
    "Du darfst keine externen Quellen konsultieren und sollst keine unsicheren oder ungenauen Daten verwenden. Stelle sicher, dass der HTML-Code gut strukturiert ist und den modernen Webstandards entspricht. Das benötigte CSS wird als Inline-CSS im Head des HTML eingefügt."
    "Deine Antwort ist immer valides HTML, das immer mit <html> beginnt und mit </html> endet. Du darfst auf keinen Fall gegen diese Regel verstossen."
    "Beschreibe die Bilder ausschließlich in Stichpunkten. Du darfst nicht vom Thema abweichen, wiederhole keine Informationen und vermeide unnötige Details. Du bist ausschließlich auf die Analyse des Screenshots und Code-Erstellung fokussiert. Füge am Ende des HTML-Codes einen Script-Block hinzu, der die Beschreibungen der identifizierten Bilder im JSON-Format enthält. Du antwortest ausschließlich in validem HTML, deine Antwort muss immer mit <html> beginnen und mit </html> enden. Ekläre nichts, deine Antwort besteht nur aus dem gewünschten Code."
)

image_gen_prompt = (
    "Du bist ImageGenerator GPT, spezialisiert auf die Erstellung hochwertiger Bilder basierend auf Textbeschreibungen. "
    "Deine Aufgabe ist es, ein Bild zu generieren, das präzise die Elemente der gegebenen Beschreibung visualisiert. "
    "Stelle sicher, dass das Bild kreativ, klar und thematisch genau auf die Beschreibung abgestimmt ist. "
    "Vermeide jegliche unscharfe oder irrelevante Darstellung und konzentriere dich ausschließlich auf die gegebene Beschreibung."
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
            {"role": "system", "content": analysis_prompt},
            {"role": "user", "content": f"data:image/png;base64,{image_data}"}
        ]
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

def generate_image_from_prompt(prompt, file_number):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {"model": image_model_name, "prompt": f"{image_gen_prompt} {prompt}"}
    log_token_count("Generate Image Request", str(data))
    response = requests.post(image_gen_endpoint, headers=headers, json=data)
    log_token_count("Generate Image Response", str(response.json()))
    print("Antwort von der Bildgenerierungs-API erhalten:")
    print(response.json())
    if response.status_code == 200 and 'image' in response.json():
        image_data = response.json()['image']
        image_path = f"{output_folder_base}/sample-{file_number:02}-image-{file_number:02}.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(image_data))
        print(f"Bild generiert und gespeichert: {image_path}")
        return image_path
    else:
        print("Fehler: Kein Bild in der Antwort.")
        return None

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

            if 'image_descriptions' in result:
                print(f"Verarbeite Bildbeschreibungen für {image_name}...")
                for desc in result['image_descriptions']:
                    prompt = f"Erstelle ein Bild, das folgendes darstellt: {', '.join(desc['keywords'])}"
                    image_file_path = generate_image_from_prompt(prompt, idx)
                    print(f"Bild generiert und gespeichert: {image_file_path}")
        else:
            print(f"Keine valide Antwort für {image_name}. Überprüfe die API-Antwort und -Anfrage.")

        print(f"Verarbeitung für {image_name} abgeschlossen.")

if __name__ == "__main__":
    main()
