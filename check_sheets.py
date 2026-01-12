#!/usr/bin/env python3
"""Hilfsskript zum Prüfen der verfügbaren Sheets und Spalten"""

import gspread
from config import SHEET1_ID, SHEET2_ID, CREDENTIALS_PATH

def check_sheets():
    client = gspread.service_account(filename=CREDENTIALS_PATH)
    
    print("=" * 60)
    print("DATEI 1 - Verfügbare Sheets:")
    print("=" * 60)
    spreadsheet1 = client.open_by_key(SHEET1_ID)
    for ws in spreadsheet1.worksheets():
        print(f"\n📊 Sheet: '{ws.title}'")
        try:
            headers = ws.row_values(1)
            print(f"   Spalten ({len(headers)}): {', '.join(headers[:10])}")
            if 'uuid' in headers:
                print("   ✓ Enthält 'uuid'")
            if 'title_meinnow' in headers:
                print("   ✓ Enthält 'title_meinnow'")
        except Exception as e:
            print(f"   Fehler beim Lesen: {e}")
    
    print("\n" + "=" * 60)
    print("DATEI 2 - Verfügbare Sheets:")
    print("=" * 60)
    spreadsheet2 = client.open_by_key(SHEET2_ID)
    for ws in spreadsheet2.worksheets():
        print(f"\n📊 Sheet: '{ws.title}'")
        try:
            headers = ws.row_values(1)
            print(f"   Spalten ({len(headers)}): {', '.join(headers[:10])}")
            if 'course_id' in headers:
                print("   ✓ Enthält 'course_id'")
            if 'brand' in headers:
                print("   ✓ Enthält 'brand'")
            if 'received_at' in headers:
                print("   ✓ Enthält 'received_at'")
            if 'meinnow_course_type' in headers:
                print("   ✓ Enthält 'meinnow_course_type'")
        except Exception as e:
            print(f"   Fehler beim Lesen: {e}")

if __name__ == "__main__":
    check_sheets()
