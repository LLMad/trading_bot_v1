\# Module: automated\_testing\_infrastructure.py  
\# Purpose: Implements automated testing infrastructure for the trading system, including integration tests and CI configuration.

import unittest  
from unittest.mock import patch, MagicMock  
from strategy\_executor import execute\_strategy  
from monitoring\_system import health\_check, log\_trade\_execution  
from backtesting\_engine import run\_backtest  
from data\_pipeline import stream\_market\_data, store\_data

class TestTradingSystemIntegration(unittest.TestCase):  
      
    def setUp(self):  
        """Set up common test data and mocks."""  
        self.mock\_strategy \= MagicMock()  
        self.mock\_market\_data \= \[{"price": 30000, "volume": 1.5}\]  
        self.historical\_data \= \[{"price": 29000, "volume": 1.0}, {"price": 29500, "volume": 1.2}\]

    @patch("data\_pipeline.stream\_market\_data")  
    def test\_data\_pipeline\_integration(self, mock\_stream):  
        """Test if real-time data streaming integrates correctly with storage."""  
        mock\_stream.return\_value \= self.mock\_market\_data  
        result \= stream\_market\_data("Binance")  
        self.assertEqual(result, self.mock\_market\_data)

    @patch("monitoring\_system.log\_trade\_execution")  
    @patch("strategy\_executor.execute\_strategy")  
    def test\_strategy\_execution\_integration(self, mock\_execute, mock\_log):  
        """Test if strategy execution logs trades properly."""  
        mock\_execute.return\_value \= "Order executed"  
        mock\_log.return\_value \= None

        response \= execute\_strategy(self.mock\_strategy, self.mock\_market\_data)  
        self.assertEqual(response, "Order executed")  
        mock\_log.assert\_called\_with(order\_id=MagicMock(), status="Executed")

    @patch("backtesting\_engine.run\_backtest")  
    def test\_backtesting\_integration(self, mock\_backtest):  
        """Test if backtesting executes correctly and returns metrics."""  
        mock\_backtest.return\_value \= {"Sharpe Ratio": 1.5}  
        results \= run\_backtest(self.mock\_strategy, self.historical\_data)  
        self.assertEqual(results\["Sharpe Ratio"\], 1.5)

    def test\_monitoring\_health\_check(self):  
        """Test system health check functionality."""  
        health\_status \= health\_check()  
        self.assertTrue(health\_status)

\# Continuous Integration (CI) Configuration  
\# Save the following YAML as .github/workflows/ci.yml in the project repository.  
ci\_yaml \= """  
name: CI

on:  
  push:  
    branches:  
      \- main  
  pull\_request:  
    branches:  
      \- main

jobs:  
  test:  
    runs-on: ubuntu-latest

    steps:  
    \- name: Checkout code  
      uses: actions/checkout@v3

    \- name: Set up Python  
      uses: actions/setup-python@v4  
      with:  
        python-version: '3.9'

    \- name: Install dependencies  
      run: |  
        python \-m pip install \--upgrade pip  
        pip install \-r requirements.txt

    \- name: Run tests  
      run: |  
        python \-m unittest discover tests  
"""

if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Run unit tests for integration verification  
    unittest.main()

