
import xlsxwriter
from fpdf import FPDF
import os
import sqlite3

def fetch_all_properties():
    conn = sqlite3.connect("realty.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE status = 'active' ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def generate_excel(properties, filename="export.xlsx"):
    filepath = os.path.join("media", filename)
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet("Объекты")

    headers = ["ID", "Название", "Адрес", "Цена", "Комнат", "Площадь", "Контакт"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    for row_num, prop in enumerate(properties, start=1):
        worksheet.write(row_num, 0, prop["id"])
        worksheet.write(row_num, 1, prop["title"])
        worksheet.write(row_num, 2, prop["address"])
        worksheet.write(row_num, 3, prop["price"])
        worksheet.write(row_num, 4, prop["rooms"])
        worksheet.write(row_num, 5, prop["area"])
        worksheet.write(row_num, 6, prop["contact"])

    workbook.close()
    return filepath

def generate_pdf(properties, filename="export.pdf"):
    filepath = os.path.join("media", filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for prop in properties:
        pdf.cell(200, 10, txt=f"Объект #{prop['id']}", ln=True)
        pdf.multi_cell(0, 8, txt=(
            f"🏷 {prop['title']}
"
            f"📍 Адрес: {prop['address']}
"
            f"💰 Цена: {prop['price']} сомони
"
            f"🛏 Комнат: {prop['rooms']}  |  📐 Площадь: {prop['area']} м²
"
            f"📞 Контакт: {prop['contact']}
"
            f"{'-'*50}"
        ))
    pdf.output(filepath)
    return filepath
