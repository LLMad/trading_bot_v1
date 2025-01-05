import sqlite3  
from datetime import datetime

DB\_NAME \= "crypto\_trading\_bot.db"  
RISK\_PERCENTAGE \= 1  \# Percentage of account balance to risk per trade  
ACCOUNT\_BALANCE \= 10000  \# Example account balance in USD

\# Database setup  
def initialize\_risk\_database():  
    """Create the database and tables for risk management if not already present."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
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

\# Calculate position size  
def calculate\_position\_size(entry\_price, stop\_loss):  
    """Calculate position size based on account balance and risk percentage."""  
    risk\_per\_trade \= ACCOUNT\_BALANCE \* (RISK\_PERCENTAGE / 100\)  
    risk\_per\_unit \= abs(entry\_price \- stop\_loss)  
    position\_size \= risk\_per\_trade / risk\_per\_unit  
    return round(position\_size, 6\)  \# Round to 6 decimal places for precision

\# Track open positions  
def add\_position(symbol, entry\_price, stop\_loss):  
    """Add a new position to the database."""  
    position\_size \= calculate\_position\_size(entry\_price, stop\_loss)  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("INSERT INTO positions (timestamp, symbol, entry\_price, position\_size, stop\_loss, status) VALUES (?, ?, ?, ?, ?, ?)",  
                   (datetime.utcnow().isoformat(), symbol, entry\_price, position\_size, stop\_loss, "OPEN"))  
    conn.commit()  
    conn.close()  
    return position\_size

\# Update position status  
def close\_position(position\_id):  
    """Mark a position as closed in the database."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("UPDATE positions SET status \= ? WHERE id \= ?", ("CLOSED", position\_id))  
    conn.commit()  
    conn.close()

\# Get total exposure  
def get\_total\_exposure():  
    """Calculate the total exposure of all open positions."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("SELECT SUM(entry\_price \* position\_size) FROM positions WHERE status \= ?", ("OPEN",))  
    total\_exposure \= cursor.fetchone()\[0\]  
    conn.close()  
    return total\_exposure if total\_exposure else 0

\# Unit tests  
if \_\_name\_\_ \== "\_\_main\_\_":  
    import unittest

    class TestRiskManagement(unittest.TestCase):

        def setUp(self):  
            """Set up a temporary in-memory database for testing."""  
            self.conn \= sqlite3.connect(":memory:")  
            self.cursor \= self.conn.cursor()  
            self.cursor.execute("""  
                CREATE TABLE positions (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    timestamp TEXT NOT NULL,  
                    symbol TEXT NOT NULL,  
                    entry\_price REAL NOT NULL,  
                    position\_size REAL NOT NULL,  
                    stop\_loss REAL NOT NULL,  
                    status TEXT NOT NULL  
                )  
            """)

        def tearDown(self):  
            """Close the in-memory database."""  
            self.conn.close()

        def test\_calculate\_position\_size(self):  
            """Test position size calculation."""  
            entry\_price \= 50000  
            stop\_loss \= 49000  
            position\_size \= calculate\_position\_size(entry\_price, stop\_loss)  
            self.assertAlmostEqual(position\_size, 2, places=6)

        def test\_add\_position(self):  
            """Test adding a new position."""  
            symbol \= "BTCUSD"  
            entry\_price \= 50000  
            stop\_loss \= 49000  
            position\_size \= calculate\_position\_size(entry\_price, stop\_loss)  
            add\_position(symbol, entry\_price, stop\_loss)  
            self.cursor.execute("SELECT COUNT(\*) FROM positions")  
            count \= self.cursor.fetchone()\[0\]  
            self.assertEqual(count, 1\)

        def test\_get\_total\_exposure(self):  
            """Test calculating total exposure."""  
            add\_position("BTCUSD", 50000, 49000\)  
            add\_position("ETHUSD", 4000, 3900\)  
            total\_exposure \= get\_total\_exposure()  
            self.assertGreater(total\_exposure, 0\)

    unittest.main()

