import os
import psycopg2
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

@app.route("/")
def scrape_and_save():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        url = "https://finance.yahoo.com/quote/AAPL/"
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # Dica: imprima o HTML se estiver em dúvida
        # print(soup.prettify())

        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})

        price = price_tag.text if price_tag else "N/A"


        # Conecta ao banco
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"]
        )
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS prices (symbol TEXT, price TEXT);")
        cur.execute("INSERT INTO prices (symbol, price) VALUES (%s, %s)", ("AAPL", price))
        conn.commit()
        cur.close()
        conn.close()

        return f"Preço AAPL: {price}"
