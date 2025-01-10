import pandas as pd  
import numpy as np  
from typing import Callable, Dict, Any

class HistoricalDataSimulator:  
    """Implements historical data simulation for trading strategies."""

    def \_\_init\_\_(self, data\_path: str):  
        self.data\_path \= data\_path  
        self.data \= None

    def load\_data(self) \-\> pd.DataFrame:  
        """Loads historical data from the provided file path."""  
        self.data \= pd.read\_csv(self.data\_path, parse\_dates=\['timestamp'\])  
        self.data.sort\_values('timestamp', inplace=True)  
        return self.data

    def optimize\_parameters(self, strategy\_func: Callable, param\_grid: Dict\[str, Any\]) \-\> Dict\[str, Any\]:  
        """Optimizes strategy parameters using historical data.

        Args:  
            strategy\_func (Callable): A function implementing the trading strategy.  
            param\_grid (Dict\[str, Any\]): A dictionary of parameter names and values to test.

        Returns:  
            Dict\[str, Any\]: The best parameters and associated performance.  
        """  
        best\_params \= None  
        best\_performance \= \-np.inf

        for params in self.\_generate\_param\_combinations(param\_grid):  
            performance \= self.\_evaluate\_strategy(strategy\_func, params)  
            if performance \> best\_performance:  
                best\_performance \= performance  
                best\_params \= params

        return {"params": best\_params, "performance": best\_performance}

    def analyze\_performance(self, returns: pd.Series) \-\> Dict\[str, Any\]:  
        """Analyzes the performance of the strategy.

        Args:  
            returns (pd.Series): A series of strategy returns.

        Returns:  
            Dict\[str, Any\]: Performance metrics such as Sharpe ratio and max drawdown.  
        """  
        sharpe\_ratio \= returns.mean() / returns.std() \* np.sqrt(252)  
        cumulative\_returns \= (1 \+ returns).cumprod()  
        max\_drawdown \= (cumulative\_returns / cumulative\_returns.cummax() \- 1).min()

        return {  
            "Sharpe Ratio": sharpe\_ratio,  
            "Max Drawdown": max\_drawdown,  
            "Total Return": cumulative\_returns.iloc\[-1\] \- 1,  
        }

    def \_generate\_param\_combinations(self, param\_grid: Dict\[str, Any\]):  
        """Generates all combinations of parameters from a grid."""  
        import itertools  
        keys, values \= zip(\*param\_grid.items())  
        for combination in itertools.product(\*values):  
            yield dict(zip(keys, combination))

    def \_evaluate\_strategy(self, strategy\_func: Callable, params: Dict\[str, Any\]) \-\> float:  
        """Evaluates the strategy on historical data with the given parameters."""  
        signals \= strategy\_func(self.data, \*\*params)  
        returns \= self.data\['close'\].pct\_change() \* signals.shift(1)  
        return returns.sum()

\# Example unit tests  
def test\_load\_data():  
    simulator \= HistoricalDataSimulator('test\_data.csv')  
    data \= simulator.load\_data()  
    assert not data.empty, "Data loading failed."  
    assert 'timestamp' in data.columns, "Timestamp column missing."

def test\_optimize\_parameters():  
    def dummy\_strategy(data, param1, param2):  
        return pd.Series(1, index=data.index)

    simulator \= HistoricalDataSimulator('test\_data.csv')  
    simulator.load\_data()  
    param\_grid \= {'param1': \[1, 2\], 'param2': \[0.1, 0.2\]}  
    result \= simulator.optimize\_parameters(dummy\_strategy, param\_grid)  
    assert "params" in result, "Optimization failed to return parameters."  
    assert result\["performance"\] \>= 0, "Performance calculation failed."

def test\_analyze\_performance():  
    returns \= pd.Series(\[0.01, \-0.02, 0.03, \-0.01\])  
    simulator \= HistoricalDataSimulator('test\_data.csv')  
    performance \= simulator.analyze\_performance(returns)  
    assert "Sharpe Ratio" in performance, "Performance metrics missing."  
    assert "Max Drawdown" in performance, "Performance metrics missing."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_load\_data()  
    test\_optimize\_parameters()  
    test\_analyze\_performance()  
    print("All tests passed.")

