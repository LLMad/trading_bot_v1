import time  
import logging  
import sqlite3  
from datetime import datetime, timedelta  
import requests  
import pandas as pd  
import numpy as np  
import unittest  
from textblob import TextBlob  
import talib

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s')

\# Constants  
API\_URL \= "https://api.binance.com/api/v3/ticker/price"  
SYMBOL \= "BTCUSDT"  
DB\_NAME \= "crypto\_prices.db"  
RATE\_LIMIT \= 60  \# API requests per minute  
RISK\_PERCENTAGE \= 1  \# Percentage of account balance to risk per trade  
ACCOUNT\_BALANCE \= 10000  \# Example account balance in USD

\# Database setup  
def initialize\_database():  
    """Create the database and tables if not already present."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    \# Table for price data  
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS price\_data (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            timestamp TEXT NOT NULL,  
            price REAL NOT NULL  
        )  
    """)  
    \# Table for trading signals  
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS trading\_signals (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            timestamp TEXT NOT NULL,  
            signal TEXT NOT NULL  
        )  
    """)  
    \# Table for positions  
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS positions (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            timestamp TEXT NOT NULL,  
            symbol TEXT NOT NULL,  
            entry\_price REAL NOT NULL,  
            position\_size REAL NOT NULL,  
            stop\_loss REAL NOT NULL,  
            status TEXT NOT NULL  
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
def save\_to\_database(table, data):  
    """Save data to the specified table in the local database."""  
    try:  
        conn \= sqlite3.connect(DB\_NAME)  
        cursor \= conn.cursor()  
        if table \== "price\_data":  
            cursor.execute("INSERT INTO price\_data (timestamp, price) VALUES (?, ?)", data)  
        elif table \== "trading\_signals":  
            cursor.execute("INSERT INTO trading\_signals (timestamp, signal) VALUES (?, ?)", data)  
        elif table \== "positions":  
            cursor.execute("INSERT INTO positions (timestamp, symbol, entry\_price, position\_size, stop\_loss, status) VALUES (?, ?, ?, ?, ?, ?)", data)  
        conn.commit()  
    except sqlite3.Error as e:  
        logging.error(f"Error saving data to database: {e}")  
    finally:  
        conn.close()

\# Calculate moving averages  
def calculate\_moving\_averages():  
    """Calculate 20-day and 50-day moving averages from the database."""  
    try:  
        conn \= sqlite3.connect(DB\_NAME)  
        cursor \= conn.cursor()  
        cursor.execute("SELECT timestamp, price FROM price\_data ORDER BY timestamp DESC LIMIT 50")  
        rows \= cursor.fetchall()  
        conn.close()  
        if len(rows) \< 50:  
            logging.warning("Not enough data for calculating moving averages.")  
            return None, None

        \# Convert to DataFrame for calculation  
        df \= pd.DataFrame(rows, columns=\["timestamp", "price"\])  
        df\["price"\] \= df\["price"\].astype(float)  
        df\["20\_MA"\] \= df\["price"\].rolling(window=20).mean()  
        df\["50\_MA"\] \= df\["price"\].rolling(window=50).mean()

        return df.iloc\[-1\]\["20\_MA"\], df.iloc\[-1\]\["50\_MA"\]  
    except sqlite3.Error as e:  
        logging.error(f"Error reading data from database: {e}")  
        return None, None

\# Position sizing and risk management  
def calculate\_position\_size(account\_balance, risk\_percentage, entry\_price, stop\_loss):  
    """Calculate position size based on risk management parameters."""  
    risk\_amount \= account\_balance \* (risk\_percentage / 100\)  
    position\_size \= risk\_amount / abs(entry\_price \- stop\_loss)  
    return position\_size

\# Trading logic  
def execute\_trade(signal, price, account\_balance):  
    """Execute a trade based on the signal and manage risk."""  
    if signal \== "buy":  
        stop\_loss \= price \* 0.98  \# Example stop-loss at 2% below entry price  
        position\_size \= calculate\_position\_size(ACCOUNT\_BALANCE, RISK\_PERCENTAGE, price, stop\_loss)  
        save\_to\_database("positions", (datetime.utcnow().isoformat(), SYMBOL, price, position\_size, stop\_loss, "open"))  
        logging.info(f"Executed BUY order: Price={price}, Size={position\_size}, Stop Loss={stop\_loss}")  
    elif signal \== "sell":  
        logging.info(f"Executed SELL order at Price={price}")

\# Market analysis module  
def fetch\_sentiment():  
    """Fetch sentiment data from a social media API and analyze it."""  
    try:  
        \# Placeholder: Replace with actual social media API call  
        example\_tweets \= \[  
            "Bitcoin is skyrocketing\! 🚀",  
            "I'm bearish on BTC right now...",  
            "Great time to buy Bitcoin\!"  
        \]  
        sentiments \= \[TextBlob(tweet).sentiment.polarity for tweet in example\_tweets\]  
        avg\_sentiment \= np.mean(sentiments)  
        return avg\_sentiment  
    except Exception as e:  
        logging.error(f"Error fetching sentiment data: {e}")  
        return 0

def calculate\_technical\_indicators(data):  
    """Calculate RSI, MACD, and Bollinger Bands for the given price data."""  
    try:  
        prices \= np.array(data\["price"\], dtype=float)  
        rsi \= talib.RSI(prices, timeperiod=14)  
        macd, macdsignal, \_ \= talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)  
        upperband, middleband, lowerband \= talib.BBANDS(prices, timeperiod=20)

        return {  
            "RSI": rsi\[-1\],  
            "MACD": macd\[-1\],  
            "Signal": macdsignal\[-1\],  
            "UpperBand": upperband\[-1\],  
            "LowerBand": lowerband\[-1\]  
        }  
    except Exception as e:  
        logging.error(f"Error calculating technical indicators: {e}")  
        return {}

def generate\_trading\_signal(sentiment, indicators):  
    """Generate trading signals based on sentiment and technical indicators."""  
    try:  
        if sentiment \> 0.1 and indicators\["RSI"\] \< 30 and indicators\["MACD"\] \> indicators\["Signal"\]:  
            return "buy"  
        elif sentiment \< \-0.1 and indicators\["RSI"\] \> 70 and indicators\["MACD"\] \< indicators\["Signal"\]:  
            return "sell"  
        else:  
            return "hold"  
    except Exception as e:  
        logging.error(f"Error generating trading signal: {e}")  
        return "hold"

\# Integration and backtesting  
def integrate\_market\_analysis():  
    """Integrate market analysis into the trading workflow."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("SELECT timestamp, price FROM price\_data ORDER BY timestamp DESC LIMIT 100")  
    rows \= cursor.fetchall()  
    conn.close()

    if len(rows) \< 100:  
        logging.warning("Not enough data for market analysis.")  
        return

    df \= pd.DataFrame(rows, columns=\["timestamp", "price"\])  
    sentiment \= fetch\_sentiment()  
    indicators \= calculate\_technical\_indicators(df)  
    signal \= generate\_trading\_signal(sentiment, indicators)  
    if signal \!= "hold":  
        execute\_trade(signal, df.iloc\[-1\]\["price"\], ACCOUNT\_BALANCE)  
        save\_to\_database("trading\_signals", (datetime.utcnow().isoformat(), signal))

\# Unit tests  
class TestMarketAnalysis(unittest.TestCase):  
    def setUp(self):  
        """Set up mock data for testing."""  
        self.data \= pd.DataFrame({"price": \[100 \+ i for i in range(100)\]})

    def test\_calculate\_technical\_indicators(self):  
        """Test technical indicator calculations."""  
        indicators \= calculate\_technical\_indicators(self.data)  
        self.assertIn("RSI", indicators)  
        self.assertIn("MACD", indicators)  
        self.assertIn("Signal", indicators)

    def test\_generate\_trading\_signal(self):  
        """Test trading signal generation."""  
        indicators \= {  
            "RSI": 25,  
            "MACD": 1,  
            "Signal": 0.5,  
            "UpperBand": 120,  
            "LowerBand": 80  
        }  
        sentiment \= 0.2  
        signal \= generate\_trading\_signal(sentiment, indicators)  
        self.assertEqual(signal, "buy")

if \_\_name\_\_ \== "\_\_main\_\_":  
    initialize\_database()  
    unittest.main()

