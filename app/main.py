import os
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", 5432),
        database=os.environ.get("DB_NAME", "financas"),
        user=os.environ.get("DB_USER", "user"),
        password=os.environ.get("DB_PASS", "pass")
    )

def create_table_if_not_exists():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id SERIAL PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    price NUMERIC(15, 4) NOT NULL,
                    scraped_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            conn.commit()

def fetch_price(symbol="AAPL"):
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
        if price_tag and price_tag.text:
            price_str = price_tag.text.replace(",", "")  # Remove vírgulas de milhares
            return float(price_str)
        else:
            logger.warning("Não encontrou o preço no HTML")
            return None
    except Exception as e:
        logger.error(f"Erro ao buscar preço: {e}")
        return None

def save_price(symbol, price):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO prices (symbol, price, scraped_at) VALUES (%s, %s, NOW())",
                (symbol, price)
            )
            conn.commit()

@app.route("/")
def scrape_and_save():
    create_table_if_not_exists()
    symbol = "AAPL"
    price = fetch_price(symbol)
    if price is None:
        return jsonify({"error": "Não foi possível obter o preço"}), 500
    save_price(symbol, price)
    return jsonify({"symbol": symbol, "price": price, "timestamp": datetime.now().isoformat()})

@app.route("/history")
def price_history():
    symbol = "AAPL"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT price, scraped_at FROM prices WHERE symbol = %s ORDER BY scraped_at DESC LIMIT 10",
                    (symbol,)
                )
                rows = cur.fetchall()
        return jsonify(rows)
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({"error": "Erro ao buscar histórico"}), 500

if __name__ == "__main__":
    app.run(debug=True)
