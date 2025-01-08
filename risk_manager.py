import threading  
import time  
from typing import Dict, Any

class RealTimeRiskController:  
    """Monitors positions and enforces real-time risk controls."""

    def \_\_init\_\_(self, max\_exposure: float, max\_drawdown: float):  
        self.positions \= {}  
        self.lock \= threading.Lock()  
        self.max\_exposure \= max\_exposure  
        self.max\_drawdown \= max\_drawdown  
        self.account\_equity \= 0.0  
        self.initial\_equity \= 0.0

    def update\_position(self, symbol: str, quantity: float, price: float):  
        """Updates the position for a given symbol.

        Args:  
            symbol (str): The trading symbol.  
            quantity (float): The quantity of the position.  
            price (float): The current price of the symbol.  
        """  
        with self.lock:  
            if symbol not in self.positions:  
                self.positions\[symbol\] \= {"quantity": 0.0, "value": 0.0}

            position \= self.positions\[symbol\]  
            position\["quantity"\] \+= quantity  
            position\["value"\] \= position\["quantity"\] \* price  
            self.\_evaluate\_risk()

    def calculate\_exposure(self) \-\> float:  
        """Calculates total exposure based on current positions.

        Returns:  
            float: Total exposure value.  
        """  
        with self.lock:  
            return sum(pos\["value"\] for pos in self.positions.values())

    def calculate\_drawdown(self) \-\> float:  
        """Calculates the current drawdown as a percentage.

        Returns:  
            float: Current drawdown percentage.  
        """  
        with self.lock:  
            return max(0.0, (self.initial\_equity \- self.account\_equity) / self.initial\_equity \* 100\)

    def \_evaluate\_risk(self):  
        """Evaluates current risk and enforces controls if necessary."""  
        exposure \= self.calculate\_exposure()  
        drawdown \= self.calculate\_drawdown()

        if exposure \> self.max\_exposure:  
            print("Exposure limit breached\! Initiating emergency unwinding.")  
            self.\_unwind\_positions()

        if drawdown \> self.max\_drawdown:  
            print("Drawdown limit breached\! Initiating emergency unwinding.")  
            self.\_unwind\_positions()

    def \_unwind\_positions(self):  
        """Unwinds all positions to reduce exposure."""  
        with self.lock:  
            for symbol in self.positions.keys():  
                self.positions\[symbol\]\["quantity"\] \= 0.0  
                self.positions\[symbol\]\["value"\] \= 0.0  
            print("All positions unwound.")

    def adjust\_trade(self, symbol: str, price: float, risk\_factor: float):  
        """Adjusts trade size based on risk factor.

        Args:  
            symbol (str): The trading symbol.  
            price (float): The current price of the symbol.  
            risk\_factor (float): The risk adjustment factor.  
        """  
        with self.lock:  
            position \= self.positions.get(symbol, {"quantity": 0.0})  
            adjustment \= \-position\["quantity"\] \* risk\_factor  
            print(f"Adjusting trade for {symbol} by {adjustment} units.")  
            \# Logic to send adjustment order to the market goes here

\# Unit tests  
def test\_exposure\_limit():  
    """Test exposure limit enforcement."""  
    controller \= RealTimeRiskController(max\_exposure=10000.0, max\_drawdown=10.0)  
    controller.initial\_equity \= 15000.0  
    controller.account\_equity \= 15000.0

    controller.update\_position("BTCUSD", 1.0, 11000.0)  
    assert controller.calculate\_exposure() \<= 10000.0, "Exposure limit not enforced."

def test\_drawdown\_limit():  
    """Test drawdown limit enforcement."""  
    controller \= RealTimeRiskController(max\_exposure=10000.0, max\_drawdown=10.0)  
    controller.initial\_equity \= 15000.0  
    controller.account\_equity \= 13000.0

    controller.update\_position("BTCUSD", 1.0, 9000.0)  
    assert controller.calculate\_drawdown() \<= 10.0, "Drawdown limit not enforced."

def test\_position\_unwinding():  
    """Test emergency position unwinding."""  
    controller \= RealTimeRiskController(max\_exposure=10000.0, max\_drawdown=10.0)  
    controller.initial\_equity \= 15000.0  
    controller.account\_equity \= 13000.0

    controller.update\_position("BTCUSD", 1.0, 11000.0)  
    controller.\_unwind\_positions()  
    assert sum(pos\["quantity"\] for pos in controller.positions.values()) \== 0.0, "Positions not unwound."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_exposure\_limit()  
    test\_drawdown\_limit()  
    test\_position\_unwinding()  
    print("All tests passed.")

