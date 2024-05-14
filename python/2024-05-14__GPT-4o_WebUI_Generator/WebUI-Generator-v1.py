import sys
import os
import requests
#import json
import base64
from IPython.display import Image as IPythonImage, display

# Konfiguration
api_key = "YOUR_API_KEY"
chatgpt_endpoint = "https://api.openai.com/v1/chat/completions"
model_name = 'gpt-4o'
images_folder = 'source-images'
output_folder = 'output-images'
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
    "Wenn es innerhalb des analysierten Screenshots einer Webseite keine Bilder gibt oder du keine erkennen kannst, dann soll das JSON Objekt nur den Ihalt 'Keine Bilder gefunden' haben."
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

def load_image(image_path):
    # Open and display the image for context
    display(IPythonImage(filename=image_path))
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_image_to_chatgpt(image_data):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": analysis_prompt
            },
            {
                "role": "user",
                "content": f"data:image/png;base64,{image_data}"  # Changed this line
            }
        ]
    }
    #print("Gesendete Daten an ChatGPT API:")
    #print(data)  # Zeige die gesendeten Daten für Debugging-Zwecke
    response = requests.post(chatgpt_endpoint, headers=headers, json=data)
    print("Erhaltene Antwort von ChatGPT API:")
    print(response.json())  # Zeige die komplette Antwort
    return response.json()

def create_html_file(html_content, file_number):
    file_path = f"sample-{file_number:02}.html"
    with open(file_path, "w") as file:
        file.write(html_content)
    print(f"HTML gespeichert: {file_path}")
    return file_path

def generate_image_from_prompt(prompt, file_number):
    print(f"Generiere Bild aus Prompt: {prompt}")
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        "model": image_model_name,
        "prompt": f"{image_gen_prompt} {prompt}"
    }
    print("Gesendete Daten für Bildgenerierung:")
    print(data)  # Zeige die gesendeten Daten
    response = requests.post(image_gen_endpoint, headers=headers, json=data)
    print("Erhaltene Antwort von der Bildgenerierungs-API:")
    print(response.json())  # Zeige die komplette Antwort
    if response.status_code == 200:
        image_data = response.json().get('image')
        if image_data:
            image_path = f"{output_folder}/sample-{file_number:02}-image-{file_number:02}.jpg"
            with open(image_path, "wb") as img_file:
                img_file.write(base64.b64decode(image_data))
            print(f"Bild generiert und gespeichert: {image_path}")
            return image_path
        else:
            print("Fehler: Kein Bild in der Antwort.")
    else:
        print(f"Fehler bei der Bildgenerierung: HTTP-Status {response.status_code}")
    return None

def create_required_directories():
    directories_created = False
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        directories_created = True
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        directories_created = True
    return directories_created

def main():
    print("Starte das Skript...")
    if create_required_directories():
        print("Ordner waren nicht vorhanden und wurden erzeugt. Bitte lade Bilder in das Verzeichnis und starte das Script neu.")
        sys.exit()

    images = os.listdir(images_folder)
    if not images:
        print("Keine Bilder im Ordner source-images gefunden. Bitte Bilder in den Ordner legen und das Skript erneut starten.")
        sys.exit()

    for idx, image_name in enumerate(images):
        image_path = os.path.join(images_folder, image_name)
        print(f"Lade und verarbeite Bild {image_name}...")
        image_data = load_image(image_path)

        print(f"Sende Bild {image_name} zur Analyse...")
        result = send_image_to_chatgpt(image_data)

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


#analysis_prompt = (
#    "Du bist WebUIAnalyzer GPT, ein Fachmann in der Erstellung und Analyse von Webseiten."
#    "Deine Expertise umfasst HTML und CSS. Du bist angehalten, Webseiten-Screenshots präzise zu analysieren. "
#    "Erstelle auf Basis des bereitgestellten Bildes sauber formatierten HTML-Code. "
#    "Analysiere das Bild gründlich und erstelle HTML, das der Struktur und dem Inhalt des Bildes entspricht. "
#    "Identifiziere außerdem alle darin enthaltenen Bilder und beschreibe diese in klaren, präzisen Stichpunkten. "
#    "Du darfst keine externen Quellen konsultieren und sollst keine unsicheren oder ungenauen Daten verwenden. "
#    "Stelle sicher, dass der HTML-Code gut strukturiert ist und den modernen Webstandards entspricht. "
#    "Beschreibe die Bilder ausschließlich in Stichpunkten. Du darfst nicht vom Thema abweichen, "
#    "wiederhole keine Informationen und vermeide unnötige Details. "
#    "Du bist ausschließlich auf die Analyse und Code-Erstellung fokussiert."
#)