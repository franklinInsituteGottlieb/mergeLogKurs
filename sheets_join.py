#!/usr/bin/env python3
"""
Google Sheets Left Join Script

Führt einen Left Join zwischen zwei Google Sheets durch:
- Datei 1 Sheet 1: Kursdaten (uuid, title_meinnow)
- Datei 2 Sheet 1: Tracking-Daten (course_id, brand, received_at, meinnow_course_type)
- Ergebnis: Datei 2 Sheet 2 mit joined Daten

Kann lokal oder auf Render als Cron-Job ausgeführt werden.
"""

import gspread
import sys
import os
import json
import logging
from datetime import datetime
from config import (
    SHEET1_ID,
    SHEET2_ID,
    CREDENTIALS_PATH,
    SHEET1_NAME,
    SHEET2_SOURCE_NAME,
    SHEET2_TARGET_NAME
)

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_google_sheets_client(credentials_path=None):
    """
    Erstellt einen Google Sheets Client mit Service Account Credentials.
    
    Unterstützt zwei Methoden:
    1. Umgebungsvariable GOOGLE_CREDENTIALS_JSON (für Render/Cloud)
    2. JSON-Datei (für lokale Ausführung)
    """
    try:
        # Methode 1: Umgebungsvariable (für Render/Cloud)
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            logger.info("Verwende Credentials aus Umgebungsvariable GOOGLE_CREDENTIALS_JSON")
            creds_dict = json.loads(credentials_json)
            client = gspread.service_account_from_dict(creds_dict)
            return client
        
        # Methode 2: JSON-Datei (für lokale Ausführung)
        if credentials_path is None:
            credentials_path = CREDENTIALS_PATH
        
        if os.path.exists(credentials_path):
            logger.info(f"Verwende Credentials aus Datei: {credentials_path}")
            client = gspread.service_account(filename=credentials_path)
            return client
        else:
            logger.error(f"Credentials-Datei nicht gefunden: {credentials_path}")
            logger.error("Bitte setze GOOGLE_CREDENTIALS_JSON als Umgebungsvariable oder platziere credentials.json im Projektverzeichnis")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        logger.error(f"Fehler beim Parsen der JSON-Credentials: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fehler beim Authentifizieren: {e}")
        sys.exit(1)


def read_sheet_data(client, sheet_id, sheet_name):
    """Liest alle Daten aus einem Google Sheet."""
    try:
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        return data, worksheet
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Spreadsheet mit ID {sheet_id} nicht gefunden.")
        logger.error("Stelle sicher, dass die Sheet-ID korrekt ist.")
        sys.exit(1)
    except PermissionError:
        logger.error(f"Keine Berechtigung für Spreadsheet {sheet_id}")
        logger.error("Teile das Google Sheet mit dem Service Account:")
        logger.error("1. Öffne das Google Sheet in deinem Browser")
        logger.error("2. Klicke auf 'Teilen' (oben rechts)")
        logger.error("3. Füge die Service Account E-Mail hinzu (siehe README)")
        logger.error("4. Wähle Berechtigung: 'Editor'")
        logger.error("5. Klicke auf 'Senden'")
        logger.error(f"Datei 1: https://docs.google.com/spreadsheets/d/{SHEET1_ID}")
        logger.error(f"Datei 2: https://docs.google.com/spreadsheets/d/{SHEET2_ID}")
        sys.exit(1)
    except gspread.exceptions.APIError as e:
        error_msg = str(e)
        if "PERMISSION_DENIED" in error_msg or "permission" in error_msg.lower():
            logger.error(f"Keine Berechtigung für Spreadsheet {sheet_id}")
            logger.error("Teile das Google Sheet mit dem Service Account (siehe README)")
            logger.error(f"Datei 1: https://docs.google.com/spreadsheets/d/{SHEET1_ID}")
            logger.error(f"Datei 2: https://docs.google.com/spreadsheets/d/{SHEET2_ID}")
        else:
            logger.error(f"API Fehler: {error_msg}")
        sys.exit(1)
    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"Worksheet '{sheet_name}' nicht gefunden in Spreadsheet {sheet_id}.")
        logger.error(f"Verfügbare Sheets: {[ws.title for ws in spreadsheet.worksheets()]}")
        sys.exit(1)
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else "Unbekannter Fehler"
        logger.error(f"Fehler beim Lesen des Sheets ({error_type}): {error_msg}", exc_info=True)
        sys.exit(1)


def find_column_index(headers, column_name):
    """Findet den Index einer Spalte in den Headers."""
    try:
        return headers.index(column_name)
    except ValueError:
        logger.warning(f"Spalte '{column_name}' nicht gefunden.")
        return None


def perform_left_join(data1, data2, key1, key2, join_column):
    """
    Führt einen Left Join durch.
    
    Args:
        data1: Daten aus Datei 1 (Kursdaten)
        data2: Daten aus Datei 2 (Tracking-Daten)
        key1: Spaltenname für Join-Key in data1 (uuid)
        key2: Spaltenname für Join-Key in data2 (course_id)
        join_column: Spaltenname aus data1, der hinzugefügt werden soll (title_meinnow)
    
    Returns:
        Liste von Dictionaries mit joined Daten
    """
    # Erstelle ein Dictionary für schnellen Lookup
    lookup_dict = {}
    for row in data1:
        key_value = row.get(key1)
        if key_value:
            lookup_dict[str(key_value)] = row.get(join_column, '')
    
    # Führe Left Join durch
    result = []
    for row in data2:
        key_value = str(row.get(key2, ''))
        joined_value = lookup_dict.get(key_value, '')
        
        result.append({
            'id': row.get(key2, ''),
            'date': row.get('received_at', ''),
            'brand': row.get('brand', ''),
            'course_type': row.get('meinnow_course_type', ''),
            'title': joined_value,
            'vertical': row.get('meinnow_course_type', '')
        })
    
    return result


def write_to_sheet(client, sheet_id, sheet_name, data):
    """Schreibt Daten in ein Google Sheet."""
    try:
        spreadsheet = client.open_by_key(sheet_id)
        
        # Prüfe ob Sheet bereits existiert
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Erstelle neues Sheet
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        
        if not data:
            logger.warning("Keine Daten zum Schreiben.")
            return
        
        # Header vorbereiten
        headers = ['id', 'date', 'brand', 'course_type', 'title', 'vertical']
        
        # Alle Daten als Liste von Listen vorbereiten (Batch-Write)
        all_rows = [headers]  # Header zuerst
        for row in data:
            all_rows.append([
                row.get('id', ''),
                row.get('date', ''),
                row.get('brand', ''),
                row.get('course_type', ''),
                row.get('title', ''),
                row.get('vertical', '')
            ])
        
        # Nur Spalten A-F leeren (nicht die ganze Tabelle, damit Spalte G erhalten bleibt)
        logger.info("Lösche nur Spalten A-F...")
        worksheet.batch_clear(["A:F"])
        
        # Daten in A-F schreiben
        logger.info(f"Schreibe {len(data)} Zeilen in einem Batch...")
        worksheet.update(values=all_rows, range_name="A1", value_input_option="RAW")
        
        # Formel in Spalte G setzen (nur wenn noch nicht vorhanden)
        try:
            # Prüfe ob G1 bereits einen Header hat
            g1_value = worksheet.acell('G1').value
            if not g1_value:
                worksheet.update("G1", [["date_int"]], value_input_option="RAW")
                logger.info("Header 'date_int' in Spalte G gesetzt")
        except:
            worksheet.update("G1", [["date_int"]], value_input_option="RAW")
            logger.info("Header 'date_int' in Spalte G gesetzt")
        
        try:
            # Prüfe ob G2 bereits eine Formel hat
            g2_value = worksheet.acell('G2').value
            if not g2_value or not g2_value.startswith('='):
                worksheet.update("G2", [["=ARRAYFORMULA(IF(LEN(B2:B)=0,,INT(B2:B)))"]], value_input_option="USER_ENTERED")
                logger.info("Formel in Spalte G gesetzt")
        except:
            worksheet.update("G2", [["=ARRAYFORMULA(IF(LEN(B2:B)=0,,INT(B2:B)))"]], value_input_option="USER_ENTERED")
            logger.info("Formel in Spalte G gesetzt")
        
        logger.info(f"✓ {len(data)} Zeilen erfolgreich in '{sheet_name}' geschrieben (Spalten A-F).")
        
    except Exception as e:
        logger.error(f"Fehler beim Schreiben in das Sheet: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Hauptfunktion."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Google Sheets Left Join Script gestartet")
    logger.info(f"Startzeit: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # Google Sheets Client erstellen
        logger.info("Authentifiziere mit Google Sheets API...")
        client = get_google_sheets_client()
        logger.info("✓ Authentifizierung erfolgreich")
        
        # Daten aus Datei 1 Sheet 1 lesen (Kursdaten)
        logger.info(f"Lese Daten aus Datei 1 Sheet 1 (ID: {SHEET1_ID}, Sheet: '{SHEET1_NAME}')...")
        data1, _ = read_sheet_data(client, SHEET1_ID, SHEET1_NAME)
        logger.info(f"✓ {len(data1)} Zeilen aus Datei 1 gelesen")
        
        # Daten aus Datei 2 Sheet 1 lesen (Tracking-Daten)
        logger.info(f"Lese Daten aus Datei 2 Sheet 1 (ID: {SHEET2_ID}, Sheet: '{SHEET2_SOURCE_NAME}')...")
        data2, _ = read_sheet_data(client, SHEET2_ID, SHEET2_SOURCE_NAME)
        logger.info(f"✓ {len(data2)} Zeilen aus Datei 2 gelesen")
        
        # Left Join durchführen
        logger.info("Führe Left Join durch (course_id = uuid)...")
        result = perform_left_join(
            data1=data1,
            data2=data2,
            key1='uuid',
            key2='course_id',
            join_column='title_meinnow'
        )
        logger.info(f"✓ {len(result)} Zeilen nach Join")
        
        # Ergebnisse in Datei 2 Sheet 2 schreiben
        logger.info(f"Schreibe Ergebnisse in Datei 2 Sheet 2 (Sheet: '{SHEET2_TARGET_NAME}')...")
        write_to_sheet(client, SHEET2_ID, SHEET2_TARGET_NAME, result)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("✓ Prozess erfolgreich abgeschlossen!")
        logger.info(f"Endzeit: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Dauer: {duration:.2f} Sekunden")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
