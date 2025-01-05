import time  
import logging  
import sqlite3  
from datetime import datetime  
import requests

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s')

\# Constants  
API\_URL \= "https://api.binance.com/api/v3/ticker/price"  
SYMBOL \= "BTCUSDT"  
DB\_NAME \= "crypto\_prices.db"  
RATE\_LIMIT \= 60  \# API requests per minute

\# Database setup  
def initialize\_database():  
    """Create the database and table if not already present."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS price\_data (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            timestamp TEXT NOT NULL,  
            price REAL NOT NULL  
        )  
    """)  
    conn.commit()  
    conn.close()

\# Fetch price data  
def fetch\_price():  
    """Fetch the current price of BTC/USDT from Binance."""  
    try:  
        response \= requests.get(API\_URL, params={"symbol": SYMBOL})  
        response.raise\_for\_status()  
        data \= response.json()  
        price \= float(data\["price"\])  
        return price  
    except requests.exceptions.RequestException as e:  
        logging.error(f"Error fetching price data: {e}")  
        return None

\# Save to database  
def save\_to\_database(timestamp, price):  
    """Save the price data to the local database."""  
    try:  
        conn \= sqlite3.connect(DB\_NAME)  
        cursor \= conn.cursor()  
        cursor.execute("INSERT INTO price\_data (timestamp, price) VALUES (?, ?)", (timestamp, price))  
        conn.commit()  
    except sqlite3.Error as e:  
        logging.error(f"Error saving data to database: {e}")  
    finally:  
        conn.close()

\# Main trading bot logic  
def run\_trading\_bot():  
    """Run the trading bot to fetch and log price data."""  
    initialize\_database()  
    while True:  
        price \= fetch\_price()  
        if price is not None:  
            timestamp \= datetime.utcnow().isoformat()  
            logging.info(f"Fetched price: {price} at {timestamp}")  
            save\_to\_database(timestamp, price)  
        time.sleep(60 / RATE\_LIMIT)

if \_\_name\_\_ \== "\_\_main\_\_":  
    run\_trading\_bot()

