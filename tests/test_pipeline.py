
import unittest
from datetime import datetime

def filter_and_clean_rate(target_currency, rate):
    """Processes a raw rate row exactly like your silver layer loop."""
    exchange_rate = float(rate)
    if exchange_rate <= 0:
        return None  
    return (target_currency.upper().strip(), exchange_rate)


def generate_date_dimension_row(date_object):
    """Computes the date dimension array fields exactly like your gold layer."""
    return {
        "date": date_object,
        "year": date_object.year,
        "month": date_object.month,
        "day": date_object.day,
        "is_weekday": date_object.weekday() < 5
    }


class TestPipelineLogic(unittest.TestCase):

    ## --- SILVER LAYER TESTS ---

    def test_valid_rate_processing(self):
        """Test that normal, positive exchange rates are processed correctly."""
        result = filter_and_clean_rate("uzs", "12650.50")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "UZS")
        self.assertEqual(result[1], 12650.50)

    def test_filter_zero_and_negative_rates(self):
        """Test that invalid rates (<= 0) are correctly blocked and skipped."""

        # Test zero rate
        zero_result = filter_and_clean_rate("EUR", 0.0)
        self.assertIsNone(zero_result, "Zero rates must be skipped/returned as None")

        # Test negative rate anomaly
        negative_result = filter_and_clean_rate("RUB", -1.45)
        self.assertIsNone(negative_result, "Negative rates must be skipped/returned as None")


    ## --- GOLD LAYER TESTS ---

    def test_date_dimension_weekday(self):
        """Test that a standard weekday identifies is_weekday as True."""
        
        monday = datetime.strptime("2026-06-29", "%Y-%m-%d").date()
        dim_row = generate_date_dimension_row(monday)
        
        self.assertEqual(dim_row["year"], 2026)
        self.assertEqual(dim_row["month"], 6)
        self.assertEqual(dim_row["day"], 29)
        self.assertTrue(dim_row["is_weekday"], "Monday must be flagged as a weekday")

    def test_date_dimension_weekend(self):
        sunday = datetime.strptime("2026-06-28", "%Y-%m-%d").date()
        dim_row = generate_date_dimension_row(sunday)
        
        self.assertFalse(dim_row["is_weekday"], "Sunday must NOT be flagged as a weekday")


if __name__ == "__main__":
    unittest.main()