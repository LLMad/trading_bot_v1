import logging  
import time  
from typing import Dict, Any

class LoggingAndPerformanceTracking:  
    """  
    Implements comprehensive logging and performance tracking for the trading system.  
    Includes functions for trade execution monitoring, system health checks, and performance metrics collection.  
    """

    def \_\_init\_\_(self, log\_file: str \= "trading\_system.log"):  
        self.logger \= logging.getLogger("TradingSystemLogger")  
        self.logger.setLevel(logging.INFO)  
        file\_handler \= logging.FileHandler(log\_file)  
        formatter \= logging.Formatter('%(asctime)s \- %(levelname)s \- %(message)s')  
        file\_handler.setFormatter(formatter)  
        self.logger.addHandler(file\_handler)  
        self.metrics \= {  
            "trade\_count": 0,  
            "average\_execution\_time": 0.0,  
            "system\_health\_checks": \[\]  
        }

    def log\_trade\_execution(self, trade\_id: str, details: Dict\[str, Any\]) \-\> None:  
        """  
        Logs trade execution details.

        Args:  
            trade\_id (str): Unique identifier for the trade.  
            details (Dict\[str, Any\]): Trade execution details such as symbol, price, quantity, etc.  
        """  
        self.logger.info(f"Trade Executed: {trade\_id}, Details: {details}")  
        self.metrics\["trade\_count"\] \+= 1

    def log\_system\_health(self, status: str, message: str) \-\> None:  
        """  
        Logs system health status and adds it to the health checks metrics.

        Args:  
            status (str): Status of the system (e.g., OK, WARNING, ERROR).  
            message (str): Detailed message about the health status.  
        """  
        self.logger.info(f"System Health: {status} \- {message}")  
        self.metrics\["system\_health\_checks"\].append({"status": status, "message": message})

    def track\_execution\_time(self, func):  
        """  
        Decorator for tracking and logging execution time of a function.

        Args:  
            func (callable): The function to be tracked.

        Returns:  
            callable: Wrapped function with execution time tracking.  
        """  
        def wrapper(\*args, \*\*kwargs):  
            start\_time \= time.time()  
            result \= func(\*args, \*\*kwargs)  
            execution\_time \= time.time() \- start\_time  
            self.logger.info(f"Execution Time for {func.\_\_name\_\_}: {execution\_time:.4f} seconds")  
            self.\_update\_average\_execution\_time(execution\_time)  
            return result

        return wrapper

    def \_update\_average\_execution\_time(self, execution\_time: float) \-\> None:  
        """  
        Updates the average execution time metric.

        Args:  
            execution\_time (float): Time taken for the last execution.  
        """  
        count \= self.metrics\["trade\_count"\]  
        if count \> 1:  
            previous\_avg \= self.metrics\["average\_execution\_time"\]  
            new\_avg \= (previous\_avg \* (count \- 1\) \+ execution\_time) / count  
            self.metrics\["average\_execution\_time"\] \= new\_avg  
        else:  
            self.metrics\["average\_execution\_time"\] \= execution\_time

\# Unit Tests  
import unittest

class TestLoggingAndPerformanceTracking(unittest.TestCase):  
    def setUp(self):  
        self.logger \= LoggingAndPerformanceTracking(log\_file="test\_trading\_system.log")

    def test\_log\_trade\_execution(self):  
        self.logger.log\_trade\_execution("T123", {"symbol": "BTC/USD", "price": 50000, "quantity": 1})  
        self.assertEqual(self.logger.metrics\["trade\_count"\], 1\)

    def test\_log\_system\_health(self):  
        self.logger.log\_system\_health("OK", "System running smoothly")  
        self.assertEqual(len(self.logger.metrics\["system\_health\_checks"\]), 1\)

    def test\_track\_execution\_time(self):  
        @self.logger.track\_execution\_time  
        def sample\_function():  
            time.sleep(0.1)

        sample\_function()  
        self.assertGreater(self.logger.metrics\["average\_execution\_time"\], 0\)

if \_\_name\_\_ \== "\_\_main\_\_":  
    unittest.main()

