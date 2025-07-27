
from flask import Flask, request, jsonify, send_file
import sqlite3
import json
from utils.export import generate_pdf, generate_excel, fetch_all_properties

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect("../realty.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else [dict(row) for row in rv]

@app.route("/login")
def login():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    return jsonify({"status": "ok", "user_id": user_id})

@app.route("/properties")
def all_properties():
    sort = request.args.get("sort", "new")
    order = {
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "old": "id ASC",
        "new": "id DESC"
    }.get(sort, "id DESC")
    props = query_db(f"SELECT * FROM properties WHERE status = 'active' ORDER BY {order}")
    return jsonify(props)

@app.route("/my-properties")
def my_properties():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    props = query_db("SELECT * FROM properties WHERE status = 'active' AND owner_id = ? ORDER BY id DESC", (user_id,))
    return jsonify(props)

@app.route("/export/pdf")
def export_pdf_web():
    props = fetch_all_properties()
    path = generate_pdf(props, filename="web_export.pdf")
    return send_file(path, as_attachment=True)

@app.route("/export/excel")
def export_excel_web():
    props = fetch_all_properties()
    path = generate_excel(props, filename="web_export.xlsx")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
