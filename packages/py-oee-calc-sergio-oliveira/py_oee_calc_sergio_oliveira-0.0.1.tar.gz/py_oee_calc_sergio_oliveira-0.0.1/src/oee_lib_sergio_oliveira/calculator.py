from datetime import datetime

class OEECalculator:
    """
    Library - OEE (Overall Equipment Effectiveness) Calculator
    """

    def __init__(self):
        pass

    def oee_test(self, name: str) -> str:
        timestamp = datetime.now()
        return f'Hello, {name} - {timestamp} '