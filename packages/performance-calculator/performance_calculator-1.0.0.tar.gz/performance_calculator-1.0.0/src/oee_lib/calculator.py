# src/oee_lib/calculator.py

"""
=============================================================
 Library PyOEE-Calc | A simple calculation of performance
=============================================================

Author:
    Sergio Oliveira - x23170981@student.ncirl.ie

Institution:
    National College of Ireland

Date:
    21 - Oct - 2025
"""

class OEECalculator:
    """
    Library - OEE (Overall Equipment Effectiveness) Calculator
    """

    def __init__(self):
        pass

    def calculate_performance_rate(self, actual_rate:float, nominal_rate:float) -> float:
        """
        Calculates the Performance Factor (P) of the OEE.
        Formula: (Real Rate / Nominal Rate)

        :param actual_rate: Production rate that the user has simulated.
        :param nominal_rate: Optimal rate read from the Product Catalog.
        :return: A decimal value (0.0 to 1.0) representing performance.
        """

        # Handle Exceptions
        if actual_rate <= 0.0 or nominal_rate <= 0.0:
            return 0.0

        performance = (actual_rate / nominal_rate) * 100.0

        return round(performance, 2)