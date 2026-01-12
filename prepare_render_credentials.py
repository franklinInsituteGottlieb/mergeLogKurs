#!/usr/bin/env python3
"""
Hilfsskript zum Vorbereiten der Credentials für Render

Konvertiert credentials.json in einen JSON-String, der als 
Umgebungsvariable GOOGLE_CREDENTIALS_JSON in Render verwendet werden kann.
"""

import json
import sys
import os

def prepare_credentials():
    """Liest credentials.json und gibt den JSON-String für Render aus."""
    
    credentials_path = 'credentials.json'
    
    if not os.path.exists(credentials_path):
        print(f"❌ Fehler: {credentials_path} nicht gefunden.")
        print("   Stelle sicher, dass credentials.json im aktuellen Verzeichnis liegt.")
        sys.exit(1)
    
    try:
        # Lese die JSON-Datei
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
        
        # Konvertiere zurück zu kompaktem JSON-String
        json_string = json.dumps(creds, separators=(',', ':'))
        
        print("=" * 70)
        print("GOOGLE_CREDENTIALS_JSON für Render:")
        print("=" * 70)
        print()
        print("Kopiere den folgenden Wert und füge ihn als Umgebungsvariable")
        print("in Render ein (Key: GOOGLE_CREDENTIALS_JSON):")
        print()
        print("-" * 70)
        print(json_string)
        print("-" * 70)
        print()
        print("⚠️  WICHTIG: Dieser Wert enthält sensible Daten!")
        print("   - Teile ihn nicht öffentlich")
        print("   - Verwende ihn nur in Render Environment Variables")
        print("=" * 70)
        
        # Optional: Speichere in Datei (nicht in Git!)
        output_file = 'credentials_for_render.txt'
        with open(output_file, 'w') as f:
            f.write(json_string)
        print(f"\n✓ Wert wurde auch in '{output_file}' gespeichert (nicht committen!)")
        
    except json.JSONDecodeError as e:
        print(f"❌ Fehler: Ungültiges JSON in {credentials_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    prepare_credentials()
