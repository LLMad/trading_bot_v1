import time
import logging
import sqlite3
from datetime import datetime, timedelta
import requests
import pandas as pd
import unittest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
API_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "BTCUSDT"
DB_NAME = "crypto_prices.db"
RATE_LIMIT = 60  # API requests per minute
RISK_PERCENTAGE = 1  # Percentage of account balance to risk per trade
ACCOUNT_BALANCE = 10000  # Example account balance in USD

# Database setup
def initialize_database():
    """Create the database and tables if not already present."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table for price data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    # Table for trading signals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            signal TEXT NOT NULL
        )
    """)
    # Table for positions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            entry_price REAL NOT NULL,
            position_size REAL NOT NULL,
            stop_loss REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Fetch price data
def fetch_price():
    """Fetch the current price of BTC/USDT from Binance."""
    try:
        response = requests.get(API_URL, params={"symbol": SYMBOL})
        response.raise_for_status()
        data = response.json()
        price = float(data["price"])
        return price
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching price data: {e}")
        return None

# Save to database
def save_to_database(table, data):
    """Save data to the specified table in the local database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if table == "price_data":
            cursor.execute("INSERT INTO price_data (timestamp, price) VALUES (?, ?)", data)
        elif table == "trading_signals":
            cursor.execute("INSERT INTO trading_signals (timestamp, signal) VALUES (?, ?)", data)
        elif table == "positions":
            cursor.execute("INSERT INTO positions (timestamp, symbol, entry_price, position_size, stop_loss, status) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving data to database: {e}")
    finally:
        conn.close()

# Calculate moving averages
def calculate_moving_averages():
    """Calculate 20-day and 50-day moving averages from the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, price FROM price_data ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        if len(rows) < 50:
            logging.warning("Not enough data for calculating moving averages.")
            return None, None

        # Convert to DataFrame for calculation
        df = pd.DataFrame(rows, columns=["timestamp", "price"])
        df["price"] = df["price"].astype(float)
        df["20_MA"] = df["price"].rolling(window=20).mean()
        df["50_MA"] = df["price"].rolling(window=50).mean()

        return df.iloc[-1]["20_MA"], df.iloc[-1]["50_MA"]
    except sqlite3.Error as e:
        logging.error(f"Error reading data from database: {e}")
        return None, None

# Position sizing and risk management
def calculate_position_size(entry_price, stop_loss):
    """Calculate position size based on account balance and risk percentage."""
    risk_per_trade = ACCOUNT_BALANCE * (RISK_PERCENTAGE / 100)
    risk_per_unit = abs(entry_price - stop_loss)
    position_size = risk_per_trade / risk_per_unit
    return round(position_size, 6)

def add_position(symbol, entry_price, stop_loss):
    """Add a new position to the database."""
    position_size = calculate_position_size(entry_price, stop_loss)
    save_to_database("positions", (datetime.utcnow().isoformat(), symbol, entry_price, position_size, stop_loss, "OPEN"))
    return position_size

# Generate trading signals and manage positions
def generate_trading_signal():
    """Generate buy/sell signals based on moving average crossover and manage positions."""
    ma_20, ma_50 = calculate_moving_averages()
    if ma_20 is None or ma_50 is None:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT signal FROM trading_signals ORDER BY timestamp DESC LIMIT 1")
    last_signal = cursor.fetchone()
    last_signal = last_signal[0] if last_signal else None
    conn.close()

    signal = None
    if ma_20 > ma_50 and last_signal != "BUY":
        signal = "BUY"
        stop_loss = ma_50  # Example: Use 50-day MA as stop-loss
        entry_price = fetch_price()
        if entry_price:
            add_position(SYMBOL, entry_price, stop_loss)
        logging.info("Generated BUY signal.")
    elif ma_20 < ma_50 and last_signal != "SELL":
        signal = "SELL"
        logging.info("Generated SELL signal.")

    if signal:
        timestamp = datetime.utcnow().isoformat()
        save_to_database("trading_signals", (timestamp, signal))

# Main trading bot logic
def run_trading_bot():
    """Run the trading bot to fetch and log price data."""
    initialize_database()
    while True:
        price = fetch_price()
        if price is not None:
            timestamp = datetime.utcnow().isoformat()
            logging.info(f"Fetched price: {price} at {timestamp}")
            save_to_database("price_data", (timestamp, price))
            generate_trading_signal()
        time.sleep(60 / RATE_LIMIT)

# Unit tests
class TestTradingBot(unittest.TestCase):
    def setUp(self):
        """Set up a temporary in-memory database for testing."""
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                signal TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                entry_price REAL NOT NULL,
                position_size REAL NOT NULL,
                stop_loss REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Close the in-memory database."""
        self.conn.close()

    def test_calculate_position_size(self):
        """Test position size calculation."""
        entry_price = 50000
        stop_loss = 49000
        position_size = calculate_position_size(entry_price, stop_loss)
        self.assertAlmostEqual(position_size, 2, places=6)

    def test_add_position(self):
        """Test adding a new position."""
        symbol = "BTCUSD"
        entry_price = 50000
        stop_loss = 49000
        position_size = calculate_position_size(entry_price, stop_loss)
        add_position(symbol, entry_price, stop_loss)
        self.cursor.execute("SELECT COUNT(*) FROM positions")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_generate_trading_signal(self):
        """Test generating trading signals and position management."""
        now = datetime.utcnow()
        for i in range(50):
            timestamp = (now - timedelta(days=i)).isoformat()
            price = 50000 + (i if i < 25 else -i)  # Simulate a crossover
            self.cursor.execute("INSERT INTO price_data (timestamp, price) VALUES (?, ?)", (timestamp, price))
        self.conn.commit()

        ma_20, ma_50 = calculate_moving_averages()
        self.assertIsNotNone(ma_20)
        self.assertIsNotNone(ma_50)
        generate_trading_signal()
        self.cursor.execute("SELECT COUNT(*) FROM positions")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0)

if __name__ == "__main__":
    run_trading_bot()
    unittest.main()
