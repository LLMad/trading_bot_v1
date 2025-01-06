import logging  
from abc import ABC, abstractmethod

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s', filename='trading\_bot.log')

class Strategy(ABC):  
    """Abstract base class for trading strategies."""

    @abstractmethod  
    def generate\_signals(self, market\_data):  
        pass

class SMACrossoverStrategy(Strategy):  
    """Simple Moving Average Crossover Strategy."""

    def \_\_init\_\_(self, short\_window, long\_window):  
        self.short\_window \= short\_window  
        self.long\_window \= long\_window

    def generate\_signals(self, market\_data):  
        """Generate buy/sell signals based on SMA crossover."""  
        market\_data\['short\_sma'\] \= market\_data\['price'\].rolling(window=self.short\_window).mean()  
        market\_data\['long\_sma'\] \= market\_data\['price'\].rolling(window=self.long\_window).mean()  
        market\_data\['signal'\] \= 0  
        market\_data.loc\[market\_data\['short\_sma'\] \> market\_data\['long\_sma'\], 'signal'\] \= 1  
        market\_data.loc\[market\_data\['short\_sma'\] \<= market\_data\['long\_sma'\], 'signal'\] \= \-1  
        logging.info("Generated signals using SMA Crossover Strategy.")  
        return market\_data

class StrategyFactory:  
    """Factory for creating and managing trading strategies."""

    def \_\_init\_\_(self):  
        self.\_strategies \= {}

    def register\_strategy(self, strategy\_name, strategy\_class):  
        """Register a new strategy class."""  
        self.\_strategies\[strategy\_name\] \= strategy\_class  
        logging.info(f"Registered strategy: {strategy\_name}")

    def create\_strategy(self, strategy\_name, \*args, \*\*kwargs):  
        """Create an instance of the requested strategy."""  
        strategy\_class \= self.\_strategies.get(strategy\_name)  
        if not strategy\_class:  
            logging.error(f"Strategy {strategy\_name} not found.")  
            raise ValueError(f"Strategy {strategy\_name} is not registered.")  
        return strategy\_class(\*args, \*\*kwargs)

\# Unit tests  
def test\_strategy\_factory():  
    factory \= StrategyFactory()

    \# Register and create SMA Crossover Strategy  
    factory.register\_strategy("sma\_crossover", SMACrossoverStrategy)  
    strategy \= factory.create\_strategy("sma\_crossover", short\_window=20, long\_window=50)

    \# Mock market data  
    import pandas as pd  
    market\_data \= pd.DataFrame({  
        'price': \[100 \+ i for i in range(100)\]  \# Example price data  
    })

    \# Generate signals  
    signals \= strategy.generate\_signals(market\_data)  
    assert 'signal' in signals.columns, "Signal generation failed."

    \# Test unregistered strategy error  
    try:  
        factory.create\_strategy("unknown\_strategy")  
    except ValueError as e:  
        assert str(e) \== "Strategy unknown\_strategy is not registered.", "Unregistered strategy error handling failed."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_strategy\_factory()

