import sys
import os
import requests
import base64

############################################################################################################
"""
Konfiguration / Settings
"""
############################################################################################################

# Konfiguration

#Standard Endpoint für Chat
#Durch Model gpt-4o aber ohne direkten Call an Vision API
chatgpt_endpoint = 'https://api.openai.com/v1/chat/completions'
model_name = 'gpt-4o'
num_images = 3  # Anzahl Bilder im Verzeichnis, die eingelesen werden sollen
image_src_name = 'sample'  # Name des Bildes -> eure Bilder sollten sample-1.jpg, sample-3.jpg, ... heißen (oder png)
img_type = 'png' # Dateityp der Bilder (png oder jpg)
base_url = 'http://youtube.thewhykiki.de/2024-05-14__GPT-4o_WebUI_Generator/source-images/'  # Pfad zum Verzeichnis mit den Bildern
output_folder_base = 'generator_output'  # Basisverzeichnis für die Ausgabe
output_folder_images = f'{output_folder_base}/images'  # Verzeichnis für die Ausgabe der generierten Bilder

#Endpoint für Image Generation
image_gen_endpoint = 'https://api.openai.com/v1/images/generations'
image_model_name = 'dall-e-3'


############################################################################################################
"""
Das eigentlich wichtigste: Die jeweiligen System Prompts.
analysis_prompt ist der System Prompt für die Analyse der Bilder und Erstellung des HTML Codes
image_gen_prompt ist der System Prompt für die Generierung der Bilder basierend auf Textbeschreibungen
Noch ist der Python Code hier wichtig, damit das ganze funktioniert. Aber das wird sich ändern...
Function Calling wird es möglich machen, dass ein LLM schon bald eigentlich alle Programme selber ausführen kann.
"""
############################################################################################################

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
    "Beschreibe die Bilder ausschließlich in Stichpunkten. Du darfst nicht vom Thema abweichen, wiederhole keine Informationen und vermeide unnötige Details. Du bist ausschließlich auf die Analyse des Screenshots und Code-Erstellung fokussiert. Füge am Ende des HTML-Codes einen Script-Block hinzu, der die Beschreibungen der identifizierten Bilder im JSON-Format enthält."
    "Du analysierst genau und Schritt für Schritt wie der Inhalt und die UI der Webseite auf dem Screenshot aussehen und erstellst genau das als HTML. Du kennst dir keine eigenen Dummy-Inhalte aus und du wirst auch keine Bereiche auslassen. Dein Ziel und deine Aufgabe ist es, den Inhalt des Screenshots so exakt wie möglich in valides HTML umzuwandeln. Erfinde keine FLiesstexte oder Headlines, sondern gib exakt das wieder, das du in einer detailierten Betrachtung des Webseiten-Screenshots gesehen hast."
    "Du antwortest ausschließlich in validem HTML, deine Antwort muss immer mit <html> beginnen und mit </html> enden. Ekläre nichts, deine Antwort besteht nur aus dem gewünschten Code."
)

image_gen_prompt = (
    "Du bist ImageGenerator GPT, spezialisiert auf die Erstellung hochwertiger Bilder basierend auf Textbeschreibungen. "
    "Deine Aufgabe ist es, ein Bild zu generieren, das präzise die Elemente der gegebenen Beschreibung visualisiert. "
    "Stelle sicher, dass das Bild kreativ, klar und thematisch genau auf die Beschreibung abgestimmt ist. "
    "Vermeide jegliche unscharfe oder irrelevante Darstellung und konzentriere dich ausschließlich auf die gegebene Beschreibung."
)



############################################################################################################
"""
Überprüft, ob das angegebene Verzeichnis existiert und erstellt es, falls es nicht vorhanden ist.
:param directory: Der Pfad des zu überprüfenden Verzeichnisses.
"""
############################################################################################################
def check_and_create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Verzeichnis erstellt: {directory}")
    else:
        print(f"Verzeichnis existiert bereits: {directory}")


############################################################################################################
"""
Generiert ein Dictionary mit den Bild-URLs basierend auf der Anzahl der Bilder und dem Bildnamen'-URL.
und der Basis-URL.
"""
############################################################################################################
def get_image_urls():
    image_urls = []
    for i in range(1, num_images + 1):
        image_url = f"{base_url}{image_src_name}-{i}.{img_type}"
        print(f"Generierte URL: {image_url}")
        image_urls.append(image_url)
    return image_urls


############################################################################################################
"""
Sendet die Bild-URL an die ChatGPT-API zur Verarbeitung und gibt die Antwort zurück.
:param image_url: Die URL des zu analysierenden Bildes.
:return: Die Antwort der ChatGPT-API.
"""
############################################################################################################
def send_image_to_chatgpt(image_url):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": analysis_prompt + " " + image_url}
        ],
        "max_tokens": 300
    }
    response = requests.post(chatgpt_endpoint, headers=headers, json=data)
    print("Antwort von der ChatGPT-API erhalten:")
    print(response.json())
    return response.json()



############################################################################################################
"""
Erstellt eine HTML-Datei basierend auf dem erhaltenen Inhalt.
:param html_content: Der HTML-Inhalt, der in die Datei geschrieben werden soll.
:param file_number: Die Nummer der Datei, die zur Benennung der Datei verwendet wird.
:return: Der Pfad der erstellten HTML-Datei.
"""
############################################################################################################
def create_html_file(html_content, file_number):
    file_path = f"{output_folder_base}/sample-{file_number:02}.html"
    with open(file_path, "w") as file:
        file.write(html_content)
    print(f"HTML-Datei gespeichert: {file_path}")
    return file_path



############################################################################################################
"""
Generiert ein Bild basierend auf dem gegebenen Prompt und speichert es.
:param prompt: Der Prompt, der zur Generierung des Bildes verwendet wird.
:param file_number: Die Nummer der Datei, die zur Benennung der Datei verwendet wird.
:return: Der Pfad des generierten Bildes oder None, wenn kein Bild generiert wurde.
"""
############################################################################################################
def generate_image_from_prompt(prompt, file_number):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {"model": image_model_name, "prompt": f"{image_gen_prompt} {prompt}"}
    response = requests.post(image_gen_endpoint, headers=headers, json=data)
    print("Antwort von der Bildgenerierungs-API erhalten:")
    print(response.json())
    if response.status_code == 200 and 'image' in response.json():
        image_data = response.json()['image']
        image_path = f"{output_folder_images}/sample-{file_number:02}-image-{file_number:02}.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(image_data))
        print(f"Bild generiert und gespeichert: {image_path}")
        return image_path
    else:
        print("Fehler: Kein Bild in der Antwort.")
        return None



############################################################################################################
"""
Hauptfunktion zur Steuerung des Prozesses. Sie startet das Skript, überprüft und erstellt erforderliche Verzeichnisse,
sendet Bild-URLs zur Verarbeitung an die ChatGPT-API und generiert HTML-Dateien basierend auf den erhaltenen Antworten.
"""
############################################################################################################
def main():
    print("Starte das Skript...")
    check_and_create_directory(output_folder_base)
    check_and_create_directory(output_folder_images)
    image_urls = get_image_urls()
    print(f"Image URLs: {image_urls}")
    if not image_urls:
        print("Keine Bilder gefunden. Bitte überprüfen Sie die Liste 'image_urls'.")
        sys.exit()
    for idx, image_url in enumerate(image_urls):
        print(f"Verarbeite Bild-URL: {image_url}")
        response = send_image_to_chatgpt(image_url)
        if 'choices' in response and response['choices']:
            html_content = response['choices'][0]['message']['content']
            print("HTML-Inhalt erhalten. Erstelle HTML-Datei...")
            html_file_path = create_html_file(html_content, idx)
        else:
            print("Keine valide Antwort für Bild. Überprüfe die API-Antwort und -Anfrage.")

if __name__ == "__main__":
    main()