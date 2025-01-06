import time  
import logging  
import sqlite3  
from datetime import datetime  
import requests  
import pandas as pd  
import numpy as np  
from flask import Flask, render\_template, request, jsonify  
import threading  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s', filename='trading\_bot.log')

\# Constants  
API\_URL \= "https://api.binance.com/api/v3/ticker/price"  
SYMBOL \= "BTCUSDT"  
DB\_NAME \= "crypto\_prices.db"  
EMAIL\_ADDRESS \= "your\_email@example.com"  
EMAIL\_PASSWORD \= "your\_email\_password"  
NOTIFICATION\_RECIPIENT \= "recipient\_email@example.com"

\# Flask app setup  
app \= Flask(\_\_name\_\_)

\# Initialize database  
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

\# Error handling and recovery  
class ErrorHandler:  
    @staticmethod  
    def log\_error(error\_message):  
        """Log an error message to the log file."""  
        logging.error(error\_message)

    @staticmethod  
    def send\_notification(subject, message):  
        """Send an error notification via email."""  
        try:  
            msg \= MIMEMultipart()  
            msg\['From'\] \= EMAIL\_ADDRESS  
            msg\['To'\] \= NOTIFICATION\_RECIPIENT  
            msg\['Subject'\] \= subject

            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP('smtp.gmail.com', 587\) as server:  
                server.starttls()  
                server.login(EMAIL\_ADDRESS, EMAIL\_PASSWORD)  
                server.send\_message(msg)  
                logging.info("Notification sent successfully.")  
        except Exception as e:  
            logging.error(f"Failed to send notification: {e}")

    @staticmethod  
    def recover\_from\_error():  
        """Perform recovery actions for common errors."""  
        logging.info("Attempting to recover from error...")  
        \# Example recovery: Reconnect to the API or database  
        try:  
            initialize\_database()  
            logging.info("Recovery successful.")  
        except Exception as e:  
            logging.error(f"Recovery failed: {e}")

\# Flask routes  
@app.route('/')  
def dashboard():  
    """Render the dashboard with real-time data."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()

    \# Fetch active positions  
    cursor.execute("SELECT \* FROM positions WHERE status \= 'open'")  
    active\_positions \= cursor.fetchall()

    \# Fetch recent trading signals  
    cursor.execute("SELECT \* FROM trading\_signals ORDER BY timestamp DESC LIMIT 10")  
    recent\_signals \= cursor.fetchall()

    \# Fetch latest price data  
    cursor.execute("SELECT \* FROM price\_data ORDER BY timestamp DESC LIMIT 1")  
    latest\_price \= cursor.fetchone()

    conn.close()

    return render\_template('dashboard.html',   
                           active\_positions=active\_positions,  
                           recent\_signals=recent\_signals,  
                           latest\_price=latest\_price)

@app.route('/configure', methods=\['GET', 'POST'\])  
def configure():  
    """Handle strategy configuration adjustments."""  
    if request.method \== 'POST':  
        risk\_percentage \= request.form.get('risk\_percentage')  
        \# Save the configuration settings (to file or database)  
        with open('config.json', 'w') as f:  
            f.write(json.dumps({"risk\_percentage": risk\_percentage}))  
        return jsonify({"message": "Configuration updated successfully\!"})  
    else:  
        \# Load the current configuration  
        with open('config.json', 'r') as f:  
            config \= json.load(f)  
        return jsonify(config)

@app.route('/health')  
def health():  
    """Provide system health metrics."""  
    health\_metrics \= {  
        "api\_status": "operational",  
        "database\_status": "connected",  
        "uptime": f"{time.time() \- start\_time} seconds"  
    }  
    return jsonify(health\_metrics)

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
        ErrorHandler.log\_error(f"Error fetching price data: {e}")  
        ErrorHandler.send\_notification("API Error", f"Error fetching price data: {e}")  
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
        ErrorHandler.log\_error(f"Error saving data to database: {e}")  
        ErrorHandler.send\_notification("Database Error", f"Error saving data to database: {e}")  
    finally:  
        conn.close()

\# Start Flask app  
if \_\_name\_\_ \== "\_\_main\_\_":  
    initialize\_database()  
    start\_time \= time.time()  
    threading.Thread(target=lambda: app.run(debug=True, use\_reloader=False)).start()

