# Google Sheets Left Join Script

Dieses Skript führt einen Left Join zwischen zwei Google Sheets durch und schreibt die Ergebnisse in ein neues Sheet.

## Funktionalität

- **Datei 1 Sheet 1**: Liest Kursdaten mit `uuid` und `title_meinnow`
- **Datei 2 Sheet 1**: Liest Tracking-Daten mit `course_id`, `brand`, `received_at`, `meinnow_course_type`
- **Join**: Verknüpft die Daten über `course_id` (Datei 2) = `uuid` (Datei 1)
- **Ergebnis**: Schreibt die joined Daten in **Datei 2 Sheet 2** mit folgenden Spalten:
  - `id` ← `course_id`
  - `date` ← `received_at`
  - `brand` ← `brand`
  - `course_type` ← `meinnow_course_type`
  - `title` ← `title_meinnow` (aus Datei 1 nach Join)
  - `vertical` ← `meinnow_course_type`

## Voraussetzungen

1. Python 3.7 oder höher
2. Google Cloud Projekt mit aktivierter Google Sheets API
3. Service Account Credentials (JSON-Datei)

## Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Python-Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Google Sheets API Credentials einrichten:**
   
   a. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Erstelle ein neues Projekt oder wähle ein bestehendes
   
   c. Aktiviere die **Google Sheets API** und **Google Drive API**:
      - Gehe zu "APIs & Services" > "Library"
      - Suche nach "Google Sheets API" und aktiviere sie
      - Suche nach "Google Drive API" und aktiviere sie
   
   d. Erstelle einen Service Account:
      - Gehe zu "APIs & Services" > "Credentials"
      - Klicke auf "Create Credentials" > "Service Account"
      - Gib einen Namen ein (z.B. "sheets-join-service")
      - Klicke auf "Create and Continue"
      - Überspringe die optionalen Schritte und klicke auf "Done"
   
   e. Erstelle einen Key für den Service Account:
      - Klicke auf den erstellten Service Account
      - Gehe zum Tab "Keys"
      - Klicke auf "Add Key" > "Create new key"
      - Wähle "JSON" und klicke auf "Create"
      - Die JSON-Datei wird heruntergeladen
   
   f. Benenne die heruntergeladene JSON-Datei um zu `credentials.json` und platziere sie im Projektverzeichnis
   
   g. **Wichtig**: Teile die Google Sheets mit dem Service Account:
      - Öffne die JSON-Datei und kopiere die E-Mail-Adresse aus dem Feld `client_email`
      - Öffne beide Google Sheets
      - Klicke auf "Teilen" (Share) in jedem Sheet
      - Füge die Service Account E-Mail-Adresse hinzu und gib "Editor"-Berechtigung
      - Klicke auf "Senden"

4. **Konfiguration anpassen (optional):**
   
   Falls die Sheet-Namen oder IDs anders sind, bearbeite `config.py`:
   ```python
   SHEET1_ID = 'deine-sheet-id-1'
   SHEET2_ID = 'deine-sheet-id-2'
   CREDENTIALS_PATH = 'pfad/zu/credentials.json'
   ```

## Verwendung

Führe das Skript aus:

```bash
python sheets_join.py
```

Das Skript:
1. Authentifiziert sich mit den Service Account Credentials
2. Liest Daten aus beiden Sheets
3. Führt den Left Join durch
4. Schreibt die Ergebnisse in Datei 2 Sheet 2

## Ausgabe

Das Skript gibt Fortschrittsinformationen aus:
```
Google Sheets Left Join Script
==================================================
Authentifiziere mit Credentials: credentials.json

Lese Daten aus Datei 1 Sheet 1 (ID: 1S8bfO0pbTy67SpVA9Q-7M_n3z2NcXRPaUwB3Lvb9mCY)...
✓ 10 Zeilen gelesen

Lese Daten aus Datei 2 Sheet 1 (ID: 1P9XHDYFStRo8B2cCN4aojkAdzhjzqON-i-tVVboxoG0)...
✓ 5 Zeilen gelesen

Führe Left Join durch (course_id = uuid)...
✓ 5 Zeilen nach Join

Schreibe Ergebnisse in Datei 2 Sheet 2...
✓ 5 Zeilen erfolgreich in 'Sheet2' geschrieben.

==================================================
✓ Prozess erfolgreich abgeschlossen!
```

## Fehlerbehebung

### "Credentials-Datei nicht gefunden"
- Stelle sicher, dass `credentials.json` im Projektverzeichnis liegt
- Oder passe `CREDENTIALS_PATH` in `config.py` an

### "Spreadsheet nicht gefunden"
- Überprüfe die Sheet-IDs in `config.py`
- Stelle sicher, dass der Service Account Zugriff auf die Sheets hat

### "Worksheet nicht gefunden"
- Überprüfe die Sheet-Namen in `config.py`
- Standardmäßig wird "Sheet1" verwendet

### "Permission denied"
- Stelle sicher, dass der Service Account "Editor"-Berechtigung auf beide Sheets hat
- Überprüfe, dass die Google Sheets API und Google Drive API aktiviert sind

## Dateistruktur

```
.
├── sheets_join.py          # Hauptskript
├── config.py               # Konfigurationsdatei
├── requirements.txt        # Python-Abhängigkeiten
├── credentials.json        # Service Account Credentials (nicht im Git!)
├── README.md              # Diese Datei
└── .env.example           # Beispiel für Umgebungsvariablen (optional)
```

## Hinweise

- Das Skript überschreibt **Datei 2 Sheet 2** bei jedem Ausführen
- Wenn kein Match gefunden wird, bleibt die `title`-Spalte leer
- Alle Zeilen aus Datei 2 Sheet 1 werden im Ergebnis behalten (Left Join)

## Deployment auf Render als Cron-Job

Das Skript kann auf [Render](https://render.com) als automatischer Cron-Job ausgeführt werden.

### Voraussetzungen

1. Render Account (kostenlos verfügbar)
2. GitHub Repository mit dem Code (oder Render Git Integration)

### Setup-Schritte

1. **Repository auf Render verbinden:**
   - Gehe zu [Render Dashboard](https://dashboard.render.com)
   - Klicke auf "New" > "Cron Job"
   - Verbinde dein GitHub Repository

2. **Cron-Job konfigurieren:**
   - **Name**: `sheets-join-cron` (oder beliebig)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 sheets_join.py`
   - **Schedule**: Wähle deine gewünschte Ausführungszeit
     - `0 * * * *` = Jede Stunde
     - `0 */6 * * *` = Alle 6 Stunden
     - `0 0 * * *` = Täglich um Mitternacht
     - `*/30 * * * *` = Alle 30 Minuten

3. **Umgebungsvariable setzen:**
   - In Render Dashboard: Gehe zu deinem Cron-Job > "Environment"
   - Füge eine neue Umgebungsvariable hinzu:
     - **Key**: `GOOGLE_CREDENTIALS_JSON`
     - **Value**: Der gesamte Inhalt deiner `credentials.json` Datei (als JSON-String)
   
   **Wichtig**: 
   - Kopiere den gesamten JSON-Inhalt aus deiner `credentials.json`
   - Entferne alle Zeilenumbrüche oder escape sie korrekt
   - Der Wert muss ein gültiger JSON-String sein
   
   **Beispiel** (vereinfacht):
   ```
   GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}
   ```

4. **Deploy:**
   - Klicke auf "Create Cron Job"
   - Render wird das Skript automatisch ausführen
   - Logs sind im Render Dashboard verfügbar

### Logs ansehen

- Gehe zu deinem Cron-Job im Render Dashboard
- Klicke auf "Logs" um die Ausgabe zu sehen
- Das Skript verwendet strukturiertes Logging mit Timestamps

### Schedule anpassen

Die `render.yaml` Datei enthält eine Standard-Konfiguration. Du kannst den Schedule direkt im Render Dashboard anpassen oder die `render.yaml` bearbeiten.

**Häufige Cron-Schedules:**
- `0 * * * *` - Jede Stunde
- `0 */6 * * *` - Alle 6 Stunden  
- `0 0 * * *` - Täglich um Mitternacht
- `*/15 * * * *` - Alle 15 Minuten
- `0 9 * * 1` - Jeden Montag um 9 Uhr

### Troubleshooting

**Problem**: "Credentials-Datei nicht gefunden"
- **Lösung**: Stelle sicher, dass `GOOGLE_CREDENTIALS_JSON` als Umgebungsvariable gesetzt ist

**Problem**: "Permission denied"
- **Lösung**: Teile beide Google Sheets mit der Service Account E-Mail-Adresse (siehe Installation)

**Problem**: Cron-Job läuft nicht
- **Lösung**: Überprüfe die Logs im Render Dashboard für Fehlermeldungen
- Stelle sicher, dass der Schedule korrekt formatiert ist (Cron-Syntax)
