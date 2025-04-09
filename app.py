from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import datetime
import os
import json
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

orders = []
allowed_ids = [799869557, 565652402]

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = -1002622271091

PRODUCTS_FILE = "products.json"

def send_order_to_group(order):
    items = "\n".join(order["cart"])
    total = sum([int(i.split("(")[-1].split("z")[0].strip()) for i in order["cart"]])
    text = f"🛒 *Новый заказ*\n\n"            f"👤 Пользователь: @{order['username']} (ID: {order['user_id']})\n"            f"🗓 Дата: {order['timestamp']}\n"            f"📦 Товары:\n{items}\n\n"            f"💰 *Итого: {total} zł*"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": GROUP_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

@app.route("/api/cart", methods=["POST"])
def receive_cart():
    data = request.json
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["status"] = "ожидает"
    orders.append(data)
    send_order_to_group(data)
    return jsonify({ "status": "ok" })

@app.route("/admin/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)

@app.route("/admin/update_status", methods=["POST"])
def update_status():
    data = request.json
    idx = data.get("index")
    status = data.get("status")
    if idx is not None and 0 <= idx < len(orders):
        orders[idx]["status"] = status
    return jsonify({ "success": True })

@app.route("/products.json")
def get_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/admin/save_products", methods=["POST"])
def save_products():
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(request.json, f, ensure_ascii=False, indent=2)
    return jsonify({ "success": True })

@app.route("/index.html")
def serve_index():
    return send_from_directory(os.getcwd(), "index.html")

@app.route("/admin.html")
def serve_admin():
    return send_from_directory(os.getcwd(), "admin.html")

@app.route("/")
def home():
    return serve_index()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
