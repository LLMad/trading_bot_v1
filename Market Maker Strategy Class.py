## **Market Maker Strategy Class**

from strategy\_framework import Strategy  
import numpy as np

class MarketMaker(Strategy):  
    def \_\_init\_\_(self, risk\_manager, volatility\_threshold=0.01, inventory\_target=100):  
        """  
        Market Maker Strategy.

        Args:  
            risk\_manager (object): Instance of the risk management system.  
            volatility\_threshold (float): Threshold for calculating bid-ask spread.  
            inventory\_target (int): Target inventory level for position sizing.  
        """  
        self.risk\_manager \= risk\_manager  
        self.volatility\_threshold \= volatility\_threshold  
        self.inventory\_target \= inventory\_target

    def generate\_signal(self, market\_data):  
        """  
        Generate bid-ask spread based on market volatility.

        Args:  
            market\_data (dict): Real-time market data containing prices and volume.

        Returns:  
            dict: Contains bid and ask prices.  
        """  
        mid\_price \= (market\_data\['bid\_price'\] \+ market\_data\['ask\_price'\]) / 2  
        volatility \= np.std(market\_data\['price\_history'\]\[-20:\])  \# Last 20 prices

        spread \= max(volatility \* self.volatility\_threshold, 0.01)  \# Ensure minimum spread  
        return {  
            'bid\_price': mid\_price \- spread / 2,  
            'ask\_price': mid\_price \+ spread / 2  
        }

    def calculate\_position\_size(self, current\_inventory):  
        """  
        Calculate position size based on inventory levels.

        Args:  
            current\_inventory (int): Current inventory level.

        Returns:  
            int: Suggested position size adjustment.  
        """  
        position\_adjustment \= self.inventory\_target \- current\_inventory  
        return position\_adjustment

    def execute\_trade(self, signal):  
        """  
        Execute trades based on the generated signal.

        Args:  
            signal (dict): Signal containing bid and ask prices.

        Returns:  
            None  
        """  
        if self.risk\_manager.check\_limits(signal):  
            print(f"Placing bid at {signal\['bid\_price'\]} and ask at {signal\['ask\_price'\]}.")  
        else:  
            print("Trade limits breached. Adjusting strategy.")

\# Unit Tests  
if \_\_name\_\_ \== "\_\_main\_\_":  
    class MockRiskManager:  
        def check\_limits(self, signal):  
            return True

    mock\_market\_data \= {  
        'bid\_price': 100,  
        'ask\_price': 102,  
        'price\_history': \[100, 101, 102, 99, 100, 101, 102, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86\]  
    }  
      
    risk\_manager \= MockRiskManager()  
    strategy \= MarketMaker(risk\_manager)

    \# Test signal generation  
    signal \= strategy.generate\_signal(mock\_market\_data)  
    print("Generated Signal:", signal)

    \# Test position sizing  
    position\_size \= strategy.calculate\_position\_size(90)  
    print("Position Adjustment:", position\_size)

    \# Test trade execution  
    strategy.execute\_trade(signal)

