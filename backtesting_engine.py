import pandas as pd  
import numpy as np  
from typing import Callable, Dict

class HistoricalDataSimulator:  
    """  
    Simulates trading strategies using historical market data.

    Includes performance analysis, transaction cost modeling,  
    and risk metrics calculation.  
    """

    def \_\_init\_\_(self, historical\_data: pd.DataFrame, transaction\_cost: float):  
        """  
        Initializes the simulator with historical data and transaction cost.

        Args:  
            historical\_data (pd.DataFrame): Historical market data with 'timestamp', 'price', and 'volume'.  
            transaction\_cost (float): Proportional transaction cost (e.g., 0.001 for 0.1%).  
        """  
        self.historical\_data \= historical\_data  
        self.transaction\_cost \= transaction\_cost  
        self.results \= {}

    def simulate\_strategy(self, strategy\_function: Callable) \-\> Dict\[str, float\]:  
        """  
        Simulates a trading strategy and calculates performance metrics.

        Args:  
            strategy\_function (Callable): Function defining the trading strategy.

        Returns:  
            Dict\[str, float\]: Performance metrics including profit, Sharpe ratio, and max drawdown.  
        """  
        self.historical\_data\['signal'\] \= self.historical\_data.apply(strategy\_function, axis=1)  
        self.historical\_data\['returns'\] \= self.historical\_data\['price'\].pct\_change()  
        self.historical\_data\['strategy\_returns'\] \= self.historical\_data\['signal'\].shift(1) \* self.historical\_data\['returns'\]

        \# Apply transaction costs  
        self.historical\_data\['strategy\_returns'\] \-= self.transaction\_cost \* self.historical\_data\['signal'\].diff().abs()

        cumulative\_returns \= (1 \+ self.historical\_data\['strategy\_returns'\]).cumprod()  
        self.results\['profit'\] \= cumulative\_returns.iloc\[-1\] \- 1  
        self.results\['sharpe\_ratio'\] \= self.\_calculate\_sharpe\_ratio(self.historical\_data\['strategy\_returns'\])  
        self.results\['max\_drawdown'\] \= self.\_calculate\_max\_drawdown(cumulative\_returns)

        return self.results

    def \_calculate\_sharpe\_ratio(self, returns: pd.Series, risk\_free\_rate: float \= 0.01) \-\> float:  
        """  
        Calculates the Sharpe ratio for the given returns.

        Args:  
            returns (pd.Series): Strategy returns.  
            risk\_free\_rate (float): Risk-free rate (default 0.01).

        Returns:  
            float: Sharpe ratio.  
        """  
        excess\_returns \= returns \- risk\_free\_rate / 252  
        return excess\_returns.mean() / returns.std() \* np.sqrt(252)

    def \_calculate\_max\_drawdown(self, cumulative\_returns: pd.Series) \-\> float:  
        """  
        Calculates the maximum drawdown.

        Args:  
            cumulative\_returns (pd.Series): Cumulative returns of the strategy.

        Returns:  
            float: Maximum drawdown.  
        """  
        rolling\_max \= cumulative\_returns.cummax()  
        drawdowns \= (cumulative\_returns \- rolling\_max) / rolling\_max  
        return drawdowns.min()

\# Unit tests  
def test\_simulate\_strategy():  
    """Test the simulate\_strategy function for accuracy."""  
    historical\_data \= pd.DataFrame({  
        'timestamp': pd.date\_range(start='2023-01-01', periods=100, freq='D'),  
        'price': np.linspace(100, 200, 100),  
        'volume': np.random.randint(1000, 2000, 100),  
    })

    def dummy\_strategy(row):  
        return 1 if row\['price'\] \> 150 else \-1

    simulator \= HistoricalDataSimulator(historical\_data, transaction\_cost=0.001)  
    results \= simulator.simulate\_strategy(dummy\_strategy)

    assert 'profit' in results, "Profit metric not calculated."  
    assert 'sharpe\_ratio' in results, "Sharpe ratio not calculated."  
    assert 'max\_drawdown' in results, "Max drawdown not calculated."

def test\_transaction\_costs():  
    """Test the application of transaction costs."""  
    historical\_data \= pd.DataFrame({  
        'timestamp': pd.date\_range(start='2023-01-01', periods=10, freq='D'),  
        'price': \[100, 105, 110, 100, 95, 90, 85, 80, 75, 70\],  
        'volume': np.random.randint(1000, 2000, 10),  
    })

    def dummy\_strategy(row):  
        return 1

    simulator \= HistoricalDataSimulator(historical\_data, transaction\_cost=0.01)  
    results \= simulator.simulate\_strategy(dummy\_strategy)  
    assert results\['profit'\] \< 0, "Transaction costs not correctly applied."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_simulate\_strategy()  
    test\_transaction\_costs()  
    print("All tests passed.")

