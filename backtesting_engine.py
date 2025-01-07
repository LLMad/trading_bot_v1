import numpy as np  
import pandas as pd  
from trading\_bot import StrategyFactory, RiskManagement

class HistoricalDataSimulator:  
    """Simulates historical data for strategy testing and performance analysis."""

    def \_\_init\_\_(self, strategy\_factory: StrategyFactory, risk\_management: RiskManagement):  
        self.strategy\_factory \= strategy\_factory  
        self.risk\_management \= risk\_management

    def simulate(self, historical\_data: pd.DataFrame, strategy\_name: str, transaction\_cost=0.001):  
        """Simulates the performance of a trading strategy on historical data.

        Args:  
            historical\_data (pd.DataFrame): Historical price data with 'price' and 'timestamp'.  
            strategy\_name (str): Name of the strategy to test.  
            transaction\_cost (float): Proportional transaction cost per trade.

        Returns:  
            pd.DataFrame: Simulation results including returns, drawdowns, and metrics.  
        """  
        strategy \= self.strategy\_factory.create\_strategy(strategy\_name, short\_window=20, long\_window=50)  
        signals \= strategy.generate\_signals(historical\_data)  
        results \= historical\_data.copy()  
        results\['signal'\] \= signals\['signal'\]  
        results\['position'\] \= results\['signal'\].shift(1).fillna(0)

        \# Calculate daily returns  
        results\['daily\_return'\] \= results\['position'\] \* results\['price'\].pct\_change()

        \# Apply transaction costs  
        results\['transaction\_cost'\] \= np.abs(results\['position'\].diff().fillna(0)) \* transaction\_cost  
        results\['net\_return'\] \= results\['daily\_return'\] \- results\['transaction\_cost'\]

        \# Calculate performance metrics  
        results\['cumulative\_return'\] \= (1 \+ results\['net\_return'\]).cumprod()  
        results\['drawdown'\] \= 1 \- results\['cumulative\_return'\] / results\['cumulative\_return'\].cummax()

        return results

    def analyze\_performance(self, simulation\_results: pd.DataFrame):  
        """Analyzes the performance of the simulated strategy.

        Args:  
            simulation\_results (pd.DataFrame): Simulation results from the simulate function.

        Returns:  
            dict: Performance metrics including Sharpe ratio, max drawdown, and total return.  
        """  
        total\_return \= simulation\_results\['cumulative\_return'\].iloc\[-1\] \- 1  
        max\_drawdown \= simulation\_results\['drawdown'\].max()  
        annualized\_return \= simulation\_results\['net\_return'\].mean() \* 252  
        annualized\_volatility \= simulation\_results\['net\_return'\].std() \* np.sqrt(252)  
        sharpe\_ratio \= annualized\_return / annualized\_volatility if annualized\_volatility \!= 0 else np.nan

        return {  
            'total\_return': total\_return,  
            'max\_drawdown': max\_drawdown,  
            'sharpe\_ratio': sharpe\_ratio,  
        }

\# Unit tests  
def test\_simulation():  
    """Test historical data simulation."""  
    factory \= StrategyFactory()  
    factory.register\_strategy("sma\_crossover", lambda: SMACrossoverStrategy(20, 50))  
    risk\_mgmt \= RiskManagement(10000, 2\)  
    simulator \= HistoricalDataSimulator(factory, risk\_mgmt)

    \# Mock historical data  
    data \= pd.DataFrame({  
        'price': \[100 \+ np.sin(i/10) \* 10 for i in range(100)\],  
        'timestamp': pd.date\_range(start='2023-01-01', periods=100, freq='D')  
    })

    results \= simulator.simulate(data, "sma\_crossover")  
    assert not results\['cumulative\_return'\].isnull().all(), "Simulation failed to calculate cumulative returns."

    metrics \= simulator.analyze\_performance(results)  
    assert 'sharpe\_ratio' in metrics, "Performance analysis missing Sharpe ratio."  
    assert 'max\_drawdown' in metrics, "Performance analysis missing max drawdown."  
    assert 'total\_return' in metrics, "Performance analysis missing total return."

if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_simulation()  
    print("All tests passed.")

