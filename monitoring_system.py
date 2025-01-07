import logging  
import psutil  
import time  
from datetime import datetime  
from flask import Flask, jsonify  
from trading\_bot import StrategyFactory, RiskManagement

\# Configure logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s \- %(levelname)s \- %(message)s', filename='performance\_monitor.log')

class PerformanceTracker:  
    """Tracks real-time performance metrics and system health."""

    def \_\_init\_\_(self):  
        self.performance\_metrics \= {  
            "trades\_executed": 0,  
            "winning\_trades": 0,  
            "losing\_trades": 0,  
            "win\_rate": 0.0,  
            "average\_return": 0.0  
        }  
        self.resource\_usage \= {  
            "cpu\_usage": 0.0,  
            "memory\_usage": 0.0,  
            "disk\_usage": 0.0  
        }  
        self.alerts \= \[\]

    def update\_trade\_metrics(self, trade\_result):  
        """Update trade performance metrics."""  
        self.performance\_metrics\["trades\_executed"\] \+= 1  
        if trade\_result \> 0:  
            self.performance\_metrics\["winning\_trades"\] \+= 1  
        else:  
            self.performance\_metrics\["losing\_trades"\] \+= 1

        total\_trades \= self.performance\_metrics\["trades\_executed"\]  
        self.performance\_metrics\["win\_rate"\] \= (  
            self.performance\_metrics\["winning\_trades"\] / total\_trades  
        ) \* 100  
        logging.info(f"Updated performance metrics: {self.performance\_metrics}")

    def calculate\_system\_health(self):  
        """Track system resource usage."""  
        self.resource\_usage\["cpu\_usage"\] \= psutil.cpu\_percent()  
        self.resource\_usage\["memory\_usage"\] \= psutil.virtual\_memory().percent  
        self.resource\_usage\["disk\_usage"\] \= psutil.disk\_usage('/').percent  
        logging.info(f"System health: {self.resource\_usage}")

    def check\_alerts(self):  
        """Trigger alerts based on predefined conditions."""  
        if self.resource\_usage\["cpu\_usage"\] \> 85:  
            self.alerts.append(f"High CPU usage: {self.resource\_usage\['cpu\_usage'\]}%")  
        if self.resource\_usage\["memory\_usage"\] \> 85:  
            self.alerts.append(f"High memory usage: {self.resource\_usage\['memory\_usage'\]}%")

        if self.alerts:  
            logging.warning(f"Alerts triggered: {self.alerts}")

\# Flask app for real-time monitoring  
dashboard\_app \= Flask(\_\_name\_\_)  
performance\_tracker \= PerformanceTracker()

@dashboard\_app.route('/performance', methods=\['GET'\])  
def get\_performance():  
    return jsonify(performance\_tracker.performance\_metrics)

@dashboard\_app.route('/system\_health', methods=\['GET'\])  
def get\_system\_health():  
    performance\_tracker.calculate\_system\_health()  
    return jsonify(performance\_tracker.resource\_usage)

@dashboard\_app.route('/alerts', methods=\['GET'\])  
def get\_alerts():  
    performance\_tracker.check\_alerts()  
    return jsonify(performance\_tracker.alerts)

\# Unit tests  
def test\_performance\_tracker():  
    pt \= PerformanceTracker()  
    pt.update\_trade\_metrics(1)  
    pt.update\_trade\_metrics(-1)  
    assert pt.performance\_metrics\["trades\_executed"\] \== 2  
    assert pt.performance\_metrics\["winning\_trades"\] \== 1  
    assert pt.performance\_metrics\["losing\_trades"\] \== 1

    pt.calculate\_system\_health()  
    assert pt.resource\_usage\["cpu\_usage"\] \>= 0  
    assert pt.resource\_usage\["memory\_usage"\] \>= 0

    pt.check\_alerts()  
    assert isinstance(pt.alerts, list)

if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Run unit tests  
    test\_performance\_tracker()

    \# Start Flask app  
    dashboard\_app.run(debug=True, port=5000)

def test\_update\_trade\_metrics():  
    """Test trade performance metrics updates."""  
    pt \= PerformanceTracker()  
      
    \# Simulate a winning trade  
    pt.update\_trade\_metrics(1)  
    assert pt.performance\_metrics\["trades\_executed"\] \== 1  
    assert pt.performance\_metrics\["winning\_trades"\] \== 1  
    assert pt.performance\_metrics\["losing\_trades"\] \== 0  
    assert pt.performance\_metrics\["win\_rate"\] \== 100.0

    \# Simulate a losing trade  
    pt.update\_trade\_metrics(-1)  
    assert pt.performance\_metrics\["trades\_executed"\] \== 2  
    assert pt.performance\_metrics\["winning\_trades"\] \== 1  
    assert pt.performance\_metrics\["losing\_trades"\] \== 1  
    assert pt.performance\_metrics\["win\_rate"\] \== 50.0

def test\_check\_alerts():  
    """Test alert triggering based on system health conditions."""  
    pt \= PerformanceTracker()  
      
    \# Mock system health conditions  
    pt.resource\_usage\["cpu\_usage"\] \= 90  \# High CPU usage  
    pt.resource\_usage\["memory\_usage"\] \= 88  \# High memory usage  
      
    pt.check\_alerts()  
      
    assert len(pt.alerts) \== 2  
    assert "High CPU usage" in pt.alerts\[0\]  
    assert "High memory usage" in pt.alerts\[1\]

    \# Test no alerts when conditions are normal  
    pt.alerts.clear()  
    pt.resource\_usage\["cpu\_usage"\] \= 50  \# Normal CPU usage  
    pt.resource\_usage\["memory\_usage"\] \= 40  \# Normal memory usage  
      
    pt.check\_alerts()  
    assert len(pt.alerts) \== 0

\# Run the tests  
if \_\_name\_\_ \== "\_\_main\_\_":  
    test\_update\_trade\_metrics()  
    test\_check\_alerts()  
    print("All tests passed.")

