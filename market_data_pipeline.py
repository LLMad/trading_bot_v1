import asyncio

import websockets

import json

import time

from collections import deque

from typing import Dict, Any

import threading

class MarketDataProcessor:

    """Processes and stores real-time market data efficiently."""

    def \_\_init\_\_(self, buffer\_size: int \= 10000):

        self.data\_buffer \= deque(maxlen=buffer\_size)

        self.lock \= threading.Lock()

    async def connect\_to\_exchange(self, uri: str):

        """Establishes a websocket connection to an exchange.

        Args:

            uri (str): Websocket URI for the exchange.

        """

        print(f"Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:

            await self.\_handle\_messages(websocket)

    async def \_handle\_messages(self, websocket):

        """Handles incoming messages from the websocket.

        Args:

            websocket: Active websocket connection.

        """

        async for message in websocket:

            data \= json.loads(message)

            normalized\_data \= self.normalize\_data(data)

            self.store\_data(normalized\_data)

    def normalize\_data(self, data: Dict\[str, Any\]) \-\> Dict\[str, Any\]:

        """Normalizes raw data to a standard format.

        Args:

            data (Dict\[str, Any\]): Raw data from the exchange.

        Returns:

            Dict\[str, Any\]: Normalized data.

        """

        normalized \= {

            "timestamp": data.get("T", time.time()),

            "price": float(data.get("p", 0)),

            "volume": float(data.get("v", 0)),

            "symbol": data.get("s", "UNKNOWN")

        }

        return normalized

    def store\_data(self, data: Dict\[str, Any\]):

        """Stores data in the buffer with thread safety.

        Args:

            data (Dict\[str, Any\]): Normalized data to store.

        """

        with self.lock:

            self.data\_buffer.append(data)

    def get\_buffer\_snapshot(self):

        """Returns a snapshot of the current buffer.

        Returns:

            list: A list containing buffered data.

        """

        with self.lock:

            return list(self.data\_buffer)

\# Unit tests

def test\_normalize\_data():

    """Test data normalization."""

    processor \= MarketDataProcessor()

    raw\_data \= {"T": 1640995200, "p": "45000", "v": "1.5", "s": "BTCUSD"}

    normalized \= processor.normalize\_data(raw\_data)

    assert normalized\["timestamp"\] \== 1640995200, "Timestamp normalization failed."

    assert normalized\["price"\] \== 45000.0, "Price normalization failed."

    assert normalized\["volume"\] \== 1.5, "Volume normalization failed."

    assert normalized\["symbol"\] \== "BTCUSD", "Symbol normalization failed."

def test\_store\_data():

    """Test data storage in buffer."""

    processor \= MarketDataProcessor(buffer\_size=5)

    data \= {"timestamp": 1640995200, "price": 45000.0, "volume": 1.5, "symbol": "BTCUSD"}

    processor.store\_data(data)

    assert len(processor.get\_buffer\_snapshot()) \== 1, "Data was not stored in buffer."

def test\_buffer\_overflow():

    """Test buffer overflow behavior."""

    processor \= MarketDataProcessor(buffer\_size=3)

    for i in range(5):

        processor.store\_data({"timestamp": time.time(), "price": i, "volume": 1, "symbol": "BTCUSD"})

    buffer \= processor.get\_buffer\_snapshot()

    assert len(buffer) \== 3, "Buffer overflow not handled correctly."

    assert buffer\[0\]\["price"\] \== 2, "Oldest data not discarded."

if \_\_name\_\_ \== "\_\_main\_\_":

    test\_normalize\_data()

    test\_store\_data()

    test\_buffer\_overflow()

    print("All tests passed.")

