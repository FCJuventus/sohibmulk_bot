
def notify_subscribers(bot, new_object):
    import threading
    def run():
        conn = sqlite3.connect("realty.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id FROM subscriptions
            WHERE max_price >= ?
            AND rooms = ?
            AND (area_hint IS NULL OR area_hint = '' OR area_hint IN (?))
        """, (new_object['price'], new_object['rooms'], new_object['address']))
        users = cursor.fetchall()
        conn.close()

        text = f"🏠 <b>Новый объект:</b>\n📍 {new_object['address']}\n💰 {new_object['price']} сомони\n🛏 {new_object['rooms']} комн.\n📐 {new_object['area']} м²"
        for user in users:
            try:
                bot.send_message(user[0], text, parse_mode="HTML")
            except Exception as e:
                print("❌ Не удалось отправить:", e)
    threading.Thread(target=run).start()
