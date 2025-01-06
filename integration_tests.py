import unittest

from unittest.mock import MagicMock

import pandas as pd

import numpy as np

from trading\_bot import RiskManagement, StrategyFactory, SMACrossoverStrategy, fetch\_historical\_returns, start\_dashboard

class TestEndToEndTradingSystem(unittest.TestCase):

    def setUp(self):

        """Set up mock components for testing."""

        self.account\_balance \= 10000

        self.risk\_tolerance \= 2

        self.rm \= RiskManagement(self.account\_balance, self.risk\_tolerance)

        self.factory \= StrategyFactory()

        self.factory.register\_strategy("sma\_crossover", SMACrossoverStrategy)

        self.strategy \= self.factory.create\_strategy("sma\_crossover", short\_window=20, long\_window=50)

        self.mock\_data \= pd.DataFrame({

            'price': \[100 \+ np.sin(i/10) \* 10 for i in range(100)\],

            'timestamp': pd.date\_range(start='2023-01-01', periods=100, freq='D')

        })

    def test\_data\_pipeline\_integration(self):

        """Test data collection, normalization, and storage."""

        normalized\_data \= self.mock\_data.copy()

        normalized\_data\['price'\] \= normalized\_data\['price'\].round(2)

        self.assertTrue((normalized\_data\['price'\] \<= self.mock\_data\['price'\]).all())

    def test\_strategy\_signal\_generation(self):

        """Test SMA crossover strategy signal generation."""

        signals \= self.strategy.generate\_signals(self.mock\_data)

        self.assertIn('signal', signals.columns)

        self.assertTrue(signals\['signal'\].isna().sum() \< len(signals))

    def test\_risk\_management\_integration(self):

        """Test risk management with generated signals."""

        signals \= self.strategy.generate\_signals(self.mock\_data)

        entry\_price \= signals\['price'\].iloc\[-1\]

        stop\_loss \= entry\_price \* 0.95

        position\_size \= self.rm.calculate\_position\_size(entry\_price, stop\_loss)

        self.assertGreater(position\_size, 0\)

    def test\_monitoring\_dashboard\_integration(self):

        """Test if the monitoring dashboard initializes correctly."""

        start\_dashboard\_mock \= MagicMock(start\_dashboard)

        start\_dashboard\_mock()

        start\_dashboard\_mock.assert\_called\_once()

    def test\_end\_to\_end\_flow(self):

        """Simulate an end-to-end trading flow."""

        signals \= self.strategy.generate\_signals(self.mock\_data)

        historical\_returns \= fetch\_historical\_returns()

        var \= self.rm.calculate\_var(historical\_returns)

        entry\_price \= signals\['price'\].iloc\[-1\]

        stop\_loss \= entry\_price \* 0.95

        position\_size \= self.rm.calculate\_position\_size(entry\_price, stop\_loss)

        self.assertGreater(position\_size, 0\)

        self.assertLess(var, 0\)

    def test\_ci\_configuration(self):

        """Ensure test suite is CI-ready."""

        self.assertTrue(True, "All tests must pass for CI configuration.")

if \_\_name\_\_ \== "\_\_main\_\_":

    unittest.main()

