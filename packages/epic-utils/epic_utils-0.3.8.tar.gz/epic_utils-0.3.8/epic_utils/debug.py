import time
import threading
from datetime import datetime

START_TIME = time.time()

class Variable():
    def __init__(self, func, name):
        self.func = func
        self.name = name
        self.lastValue = self.getValue()
        self.changes = []
    
    def getValue(self):
        return self.func()

    
class VariableLog():
    def __init__(self):
        self.variables: list[Variable] = []
        self.logging = True
        self._thread = threading.Thread(target=self._log)
        self._thread.start()

    def addVar(self, var: Variable):
        self.variables.append(var)

    def _log(self):
        while self.logging:
            for _var in self.variables:
                value = _var.getValue()
                if value != _var.lastValue:
                    _var.changes.append([time.time()-START_TIME, _var.lastValue, value])
                    _var.lastValue = value
            time.sleep(0.1)           

    def stop(self):
        self.logging = False
        self._thread.join()
    
    def print(self):
        for var in self.variables:
            print(f"Variable: {var.name}")
            print("\t  Time   |  Change")
            for change in var.changes:
                t = time.strftime("%H:%M:%S", time.gmtime(change[0]))
                print(f"\t{t} | {change[1]} -> {change[2]}")

    