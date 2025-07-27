
import sqlite3
import xlsxwriter
import openpyxl
import json
import os

def import_from_excel(filepath, owner_id):
    wb = openpyxl.load_workbook(filepath)
    sheet = wb.active
    rows = list(sheet.iter_rows(min_row=2, values_only=True))  # пропускаем заголовки

    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()

    added = 0
    for row in rows:
        try:
            title, address, price, rooms, area, contact = row
            if not title or not address:
                continue
            cursor.execute("""
                INSERT INTO properties (title, address, price, rooms, area, photos, contact, status, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                address,
                int(price),
                int(rooms),
                float(area),
                json.dumps([]),  # без фото
                contact,
                'active',
                owner_id
            ))
            added += 1
        except Exception as e:
            print("❌ Ошибка:", e)
            continue

    conn.commit()
    conn.close()
    return added
