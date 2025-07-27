
import sqlite3
import json

def init_db():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        address TEXT,
        price INTEGER,
        rooms INTEGER,
        area REAL,
        photos TEXT,
        contact TEXT,
        status TEXT DEFAULT 'active'
    )
    """)
    conn.commit()
    conn.close()

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO properties (title, address, price, rooms, area, photos, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data["address"],
        data["price"],
        data["rooms"],
        data["area"],
        json.dumps(data["photos"]),
        data["contact"]
    ))
    conn.commit()
    conn.close()




def search_properties(address, min_price, max_price, rooms):
    conn = sqlite3.connect("realty.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM properties
        WHERE status = 'active'
        AND address LIKE ?
        AND price BETWEEN ? AND ?
        AND rooms = ?
        ORDER BY id DESC
    """, (f"%{address}%", min_price, max_price, rooms))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_property_by_id(property_id):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
    conn.commit()
    conn.close()
    return True


def edit_property_field(property_id, field, value):
    allowed_fields = ["title", "address", "price", "rooms", "area", "contact"]
    if field not in allowed_fields:
        return False
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    cursor.execute(f"UPDATE properties SET {field} = ? WHERE id = ?", (value, property_id))
    conn.commit()
    conn.close()
    return True


def init_favorites_table():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            property_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_to_favorites(user_id, property_id):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, property_id))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (user_id, property_id))
        conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect("realty.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.* FROM properties p
        JOIN favorites f ON p.id = f.property_id
        WHERE f.user_id = ? AND p.status = 'active'
        ORDER BY p.id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def remove_from_favorites(user_id, property_id):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, property_id))
    conn.commit()
    conn.close()


def get_all_properties(sort_by="new"):
    conn = sqlite3.connect("realty.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM properties WHERE status = 'active'"

    if sort_by == "price_asc":
        query += " ORDER BY price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY price DESC"
    elif sort_by == "old":
        query += " ORDER BY id ASC"
    else:
        query += " ORDER BY id DESC"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_owner_column_if_missing():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in cursor.fetchall()]
    if "owner_id" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN owner_id INTEGER")
        conn.commit()
    conn.close()


def add_property_to_db(data):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO properties (title, address, price, rooms, area, photos, contact, owner_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data["address"],
        data["price"],
        data["rooms"],
        data["area"],
        json.dumps(data["photos"]),
        data["contact"],
        data["owner_id"]
    ))
    conn.commit()
    conn.close()

def get_properties_by_owner(user_id):
    conn = sqlite3.connect("realty.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM properties WHERE status = 'active' AND owner_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

import datetime

def add_created_at_column_if_missing():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in cursor.fetchall()]
    if "created_at" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN created_at TEXT DEFAULT (datetime('now'))")
        conn.commit()
    conn.close()

def auto_archive_old_properties(days=30):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE properties
        SET status = 'archived'
        WHERE status = 'active' AND datetime(created_at) < datetime(?)
    """, (cutoff_date,))
    conn.commit()
    conn.close()

def create_subscriptions_table():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            max_price INTEGER,
            rooms INTEGER,
            area_hint TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

def subscribe_user(user_id, max_price, rooms, area_hint):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subscriptions (user_id, max_price, rooms, area_hint) VALUES (?, ?, ?, ?)",
                   (user_id, max_price, rooms, area_hint))
    conn.commit()
    conn.close()

def add_location_columns_if_missing():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in cursor.fetchall()]
    if "latitude" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN latitude REAL")
    if "longitude" not in columns:
        cursor.execute("ALTER TABLE properties ADD COLUMN longitude REAL")
    conn.commit()
    conn.close()

def add_language_column_if_missing():
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "language" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else "ru"

def set_user_language(user_id, lang):
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()
