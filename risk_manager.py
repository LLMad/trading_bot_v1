import numpy as np  
import sqlite3  
import logging  
from datetime import datetime  
from scipy.stats import norm

\# Constants  
DB\_NAME \= "crypto\_prices.db"  
RISK\_FREE\_RATE \= 0.01  \# Example risk-free rate for VaR calculations

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s', filename='trading\_bot.log')

class RiskManagement:  
    def \_\_init\_\_(self, account\_balance, risk\_tolerance):  
        self.account\_balance \= account\_balance  
        self.risk\_tolerance \= risk\_tolerance  \# Risk tolerance as a percentage

    def calculate\_position\_size(self, entry\_price, stop\_loss):  
        """Calculate position size based on risk tolerance and stop loss."""  
        risk\_per\_trade \= self.account\_balance \* (self.risk\_tolerance / 100\)  
        position\_size \= risk\_per\_trade / abs(entry\_price \- stop\_loss)  
        logging.info(f"Calculated position size: {position\_size}")  
        return position\_size

    def calculate\_var(self, historical\_returns, confidence\_level=0.95):  
        """Calculate Value at Risk (VaR) using historical returns."""  
        mean\_return \= np.mean(historical\_returns)  
        std\_dev \= np.std(historical\_returns)  
        var \= norm.ppf(1 \- confidence\_level, mean\_return, std\_dev) \* self.account\_balance  
        logging.info(f"Calculated VaR: {var}")  
        return var

    def portfolio\_allocation(self, assets, cov\_matrix, risk\_aversion=3):  
        """Perform mean-variance portfolio optimization."""  
        expected\_returns \= np.array(\[asset\['expected\_return'\] for asset in assets\])  
        weights \= np.linalg.inv(cov\_matrix).dot(expected\_returns) / risk\_aversion  
        weights /= np.sum(weights)  \# Normalize weights to sum to 1  
        logging.info(f"Calculated portfolio weights: {weights}")  
        return weights

    def enforce\_position\_limits(self, open\_positions):  
        """Ensure no position exceeds predefined limits based on account equity."""  
        max\_position\_size \= self.account\_balance \* 0.2  \# Example: 20% of account equity  
        for position in open\_positions:  
            if position\['size'\] \> max\_position\_size:  
                logging.warning(f"Position size {position\['size'\]} exceeds limit {max\_position\_size}")  
                return False  
        return True

\# Integration with database  
def fetch\_historical\_returns():  
    """Fetch historical returns from the database."""  
    conn \= sqlite3.connect(DB\_NAME)  
    cursor \= conn.cursor()  
    cursor.execute("SELECT price FROM price\_data ORDER BY timestamp DESC LIMIT 100")  
    prices \= \[row\[0\] for row in cursor.fetchall()\]  
    conn.close()  
    returns \= np.diff(np.log(prices))  
    return returns

\# Unit tests for risk management module  
def test\_risk\_management():  
    account\_balance \= 10000  \# Example account balance  
    risk\_tolerance \= 2  \# 2% risk per trade  
    rm \= RiskManagement(account\_balance, risk\_tolerance)

    \# Test position size calculation  
    entry\_price \= 20000  
    stop\_loss \= 19000  
    position\_size \= rm.calculate\_position\_size(entry\_price, stop\_loss)  
    assert position\_size \> 0, "Position size calculation failed"

    \# Test VaR calculation  
    historical\_returns \= fetch\_historical\_returns()  
    var \= rm.calculate\_var(historical\_returns)  
    assert var \< 0, "VaR calculation failed"

    \# Test portfolio allocation  
    assets \= \[{'expected\_return': 0.1}, {'expected\_return': 0.2}\]  
    cov\_matrix \= np.array(\[\[0.01, 0.002\], \[0.002, 0.02\]\])  
    weights \= rm.portfolio\_allocation(assets, cov\_matrix)  
    assert np.isclose(np.sum(weights), 1), "Portfolio allocation failed"

    \# Test position limits enforcement  
    open\_positions \= \[{'size': 1500}, {'size': 2500}\]  
    result \= rm.enforce\_position\_limits(open\_positions)  
    assert result, "Position limits enforcement failed"

if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Run unit tests  
    test\_risk\_management()

