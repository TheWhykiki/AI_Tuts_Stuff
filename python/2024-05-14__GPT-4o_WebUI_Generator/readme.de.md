# WebUI Generator Installation and Usage Guide

## Installation

# Installations- und Benutzerhandbuch für den WebUI Generator

## Installation

1. **Klonen Sie das Repository oder laden Sie die Dateien herunter:**
   Stellen Sie sicher, dass Sie das Python-Skript und `requirements.txt` in Ihrem Arbeitsverzeichnis haben.


2. **Einrichten einer virtuellen Umgebung:**

   Für macOS/Linux:
   ```bash
   # Erstellen der virtuellen Umgebung
   python3 -m venv webui-generator

   # Aktivieren der virtuellen Umgebung
   source webui-generator/bin/activate
    ```
   
    For Windows:
    ```bash
    # Erstellen der virtuellen Umgebung
    python -m venv webui-generator
    
    # Aktivieren der virtuellen Umgebung
    webui-generator\Scripts\activate
   ```
   
3. Abhängigkeiten installieren:
    ```bash
    pip install -r requirements.txt
    ```

4. Um den WebUI Generator zu starten, verwenden Sie den folgenden Befehl in Ihrem Terminal oder Eingabeaufforderung:
    ```bash
    python WebUI-Generator-v2.py
    ```
   
### Hinweise:


Stellen Sie sicher, dass Sie die virtuelle Umgebung aktiviert haben, in der die Abhängigkeiten installiert sind, bevor Sie das Skript ausführen. Wenn Probleme mit fehlenden Modulen auftreten, überprüfen Sie nochmals, ob die virtuelle Umgebung aktiviert ist und alle Abhängigkeiten korrekt installiert sind.

Das Skript erwartet, dass die Bilder über die im Code angegebenen URLs zugänglich sind. Wenn die Bilder nicht zugänglich sind, funktioniert das Skript nicht korrekt. Passen Sie die base_url und andere Konfigurationen im Skript nach Bedarf an, um sie an Ihr Projektsetup anzupassen.