import websocket  
import json  
import sqlite3  
from typing import Dict, Any, List

class MarketDataCollector:  
    """Handles market data collection, storage, and retrieval."""

    def \_\_init\_\_(self, db\_path: str \= "market\_data.db"):  
        self.db\_path \= db\_path  
        self.\_initialize\_database()

    def \_initialize\_database(self):  
        """Initializes the SQLite database for data storage."""  
        connection \= sqlite3.connect(self.db\_path)  
        cursor \= connection.cursor()  
        cursor.execute('''CREATE TABLE IF NOT EXISTS market\_data (  
            id INTEGER PRIMARY KEY,  
            exchange TEXT,  
            symbol TEXT,  
            timestamp DATETIME DEFAULT CURRENT\_TIMESTAMP,  
            price REAL,  
            volume REAL  
        )''')  
        connection.commit()  
        connection.close()

    def store\_data(self, exchange: str, symbol: str, price: float, volume: float):  
        """Stores market data into the database."""  
        connection \= sqlite3.connect(self.db\_path)  
        cursor \= connection.cursor()  
        cursor.execute('''INSERT INTO market\_data (exchange, symbol, price, volume)   
                          VALUES (?, ?, ?, ?)''', (exchange, symbol, price, volume))  
        connection.commit()  
        connection.close()

    def fetch\_historical\_data(self, symbol: str, limit: int \= 100\) \-\> List\[Dict\[str, Any\]\]:  
        """Fetches historical data for a given symbol."""  
        connection \= sqlite3.connect(self.db\_path)  
        cursor \= connection.cursor()  
        cursor.execute('''SELECT timestamp, price, volume FROM market\_data  
                          WHERE symbol \= ? ORDER BY timestamp DESC LIMIT ?''', (symbol, limit))  
        rows \= cursor.fetchall()  
        connection.close()  
        return \[{"timestamp": row\[0\], "price": row\[1\], "volume": row\[2\]} for row in rows\]

    def normalize\_data(self, data: List\[Dict\[str, Any\]\]) \-\> List\[Dict\[str, Any\]\]:  
        """Normalizes data to a standard format."""  
        \# Example normalization logic  
        return \[{  
            "timestamp": item\["timestamp"\],  
            "price": round(item\["price"\], 2),  
            "volume": round(item\["volume"\], 4\)  
        } for item in data\]

    def stream\_data(self, exchange\_url: str, symbol: str):  
        """Streams real-time data using websockets."""  
        def on\_message(ws, message):  
            data \= json.loads(message)  
            self.store\_data(  
                exchange="example\_exchange",  
                symbol=symbol,  
                price=data\["price"\],  
                volume=data\["volume"\]  
            )

        ws \= websocket.WebSocketApp(exchange\_url, on\_message=on\_message)  
        ws.run\_forever()

\# Unit tests  
import unittest  
class TestMarketDataCollector(unittest.TestCase):

    def setUp(self):  
        self.collector \= MarketDataCollector(db\_path=":memory:")

    def test\_store\_and\_fetch\_data(self):  
        self.collector.store\_data("test\_exchange", "BTC/USD", 50000.0, 1.5)  
        data \= self.collector.fetch\_historical\_data("BTC/USD")  
        self.assertEqual(len(data), 1\)  
        self.assertEqual(data\[0\]\["price"\], 50000.0)

    def test\_data\_normalization(self):  
        raw\_data \= \[{"timestamp": "2025-01-03T00:00:00", "price": 50000.12345, "volume": 1.2345678}\]  
        normalized \= self.collector.normalize\_data(raw\_data)  
        self.assertEqual(normalized\[0\]\["price"\], 50000.12)  
        self.assertEqual(normalized\[0\]\["volume"\], 1.2346)

    def test\_stream\_data(self):  
        \# Mock websocket behavior for testing purposes  
        pass

if \_\_name\_\_ \== "\_\_main\_\_":  
    unittest.main()

