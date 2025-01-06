import time  
import logging  
import sqlite3  
from datetime import datetime, timedelta  
import requests  
import pandas as pd  
import numpy as np  
import unittest

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

\# Backtesting module  
def backtest\_strategy(historical\_data):  
    """Backtest the SMA crossover strategy on historical data."""  
    historical\_data\["20\_MA"\] \= historical\_data\["price"\].rolling(window=20).mean()  
    historical\_data\["50\_MA"\] \= historical\_data\["price"\].rolling(window=50).mean()  
    historical\_data\["signal"\] \= 0  
    historical\_data.loc\[historical\_data\["20\_MA"\] \> historical\_data\["50\_MA"\], "signal"\] \= 1  
    historical\_data.loc\[historical\_data\["20\_MA"\] \< historical\_data\["50\_MA"\], "signal"\] \= \-1

    \# Simulate trades  
    positions \= \[\]  
    for i in range(1, len(historical\_data)):  
        if historical\_data.iloc\[i \- 1\]\["signal"\] \!= historical\_data.iloc\[i\]\["signal"\]:  
            positions.append({  
                "timestamp": historical\_data.index\[i\],  
                "price": historical\_data.iloc\[i\]\["price"\],  
                "signal": historical\_data.iloc\[i\]\["signal"\]  
            })

    return positions

def calculate\_performance\_metrics(trades, initial\_balance):  
    """Calculate strategy performance metrics."""  
    portfolio \= initial\_balance  
    portfolio\_values \= \[\]  
    for trade in trades:  
        if trade\["signal"\] \== 1:  
            portfolio \+= portfolio \* 0.01  \# Simulate 1% profit per trade  
        elif trade\["signal"\] \== \-1:  
            portfolio \-= portfolio \* 0.005  \# Simulate 0.5% loss per trade  
        portfolio\_values.append(portfolio)

    returns \= np.diff(portfolio\_values) / portfolio\_values\[:-1\]  
    sharpe\_ratio \= np.mean(returns) / np.std(returns)  
    max\_drawdown \= np.min(portfolio\_values) / np.max(portfolio\_values) \- 1  
    win\_rate \= sum(\[1 for trade in trades if trade\["signal"\] \== 1\]) / len(trades)

    return {  
        "Sharpe Ratio": sharpe\_ratio,  
        "Maximum Drawdown": max\_drawdown,  
        "Win Rate": win\_rate  
    }

def generate\_performance\_report(metrics):  
    """Generate a performance report."""  
    logging.info("Performance Report:")  
    for key, value in metrics.items():  
        logging.info(f"{key}: {value:.2f}")

\# Unit tests  
class TestBacktesting(unittest.TestCase):  
    def setUp(self):  
        """Set up mock historical data for testing."""  
        dates \= pd.date\_range(start="2023-01-01", periods=100)  
        prices \= \[100 \+ i \* 0.5 for i in range(100)\]  
        self.historical\_data \= pd.DataFrame({"price": prices}, index=dates)

    def test\_backtest\_strategy(self):  
        """Test the backtesting logic."""  
        trades \= backtest\_strategy(self.historical\_data)  
        self.assertGreater(len(trades), 0\)

    def test\_calculate\_performance\_metrics(self):  
        """Test the performance metrics calculation."""  
        trades \= backtest\_strategy(self.historical\_data)  
        metrics \= calculate\_performance\_metrics(trades, 10000\)  
        self.assertIn("Sharpe Ratio", metrics)  
        self.assertIn("Maximum Drawdown", metrics)  
        self.assertIn("Win Rate", metrics)

if \_\_name\_\_ \== "\_\_main\_\_":  
    unittest.main()

