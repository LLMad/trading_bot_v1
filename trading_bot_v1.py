{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import time\
import logging\
import sqlite3\
from datetime import datetime\
import requests\
\
# Configure logging\
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')\
\
# Constants\
API_URL = "https://api.binance.com/api/v3/ticker/price"\
SYMBOL = "BTCUSDT"\
DB_NAME = "crypto_prices.db"\
RATE_LIMIT = 60  # API requests per minute\
\
# Database setup\
def initialize_database():\
    """Create the database and table if not already present."""\
    conn = sqlite3.connect(DB_NAME)\
    cursor = conn.cursor()\
    cursor.execute("""\
        CREATE TABLE IF NOT EXISTS price_data (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            timestamp TEXT NOT NULL,\
            price REAL NOT NULL\
        )\
    """)\
    conn.commit()\
    conn.close()\
\
# Fetch price data\
def fetch_price():\
    """Fetch the current price of BTC/USDT from Binance."""\
    try:\
        response = requests.get(API_URL, params=\{"symbol": SYMBOL\})\
        response.raise_for_status()\
        data = response.json()\
        price = float(data["price"])\
        return price\
    except requests.exceptions.RequestException as e:\
        logging.error(f"Error fetching price data: \{e\}")\
        return None\
\
# Save to database\
def save_to_database(timestamp, price):\
    """Save the price data to the local database."""\
    try:\
        conn = sqlite3.connect(DB_NAME)\
        cursor = conn.cursor()\
        cursor.execute("INSERT INTO price_data (timestamp, price) VALUES (?, ?)", (timestamp, price))\
        conn.commit()\
    except sqlite3.Error as e:\
        logging.error(f"Error saving data to database: \{e\}")\
    finally:\
        conn.close()\
\
# Main trading bot logic\
def run_trading_bot():\
    """Run the trading bot to fetch and log price data."""\
    initialize_database()\
    while True:\
        price = fetch_price()\
        if price is not None:\
            timestamp = datetime.utcnow().isoformat()\
            logging.info(f"Fetched price: \{price\} at \{timestamp\}")\
            save_to_database(timestamp, price)\
        time.sleep(60 / RATE_LIMIT)\
\
if __name__ == "__main__":\
    run_trading_bot()\
}