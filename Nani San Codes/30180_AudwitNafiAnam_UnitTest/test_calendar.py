import unittest
from calendar import Calendar

class TestCalendar(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.calendar = Calendar(2024)
    
    def test_valid_initialization(self):
        """Test valid calendar initialization."""
        calendar = Calendar(2024)
        self.assertEqual(calendar.year, 2024)
    
    def test_invalid_initialization(self):
        """Test invalid calendar initialization."""
        with self.assertRaises(ValueError):
            Calendar(-2024)
        with self.assertRaises(ValueError):
            Calendar(0)
        with self.assertRaises(ValueError):
            Calendar("2024")
    
    def test_year_setter(self):
        """Test year setter with valid and invalid values."""
        self.calendar.set_year(2025)
        self.assertEqual(self.calendar.year, 2025)
        
        with self.assertRaises(ValueError):
            self.calendar.set_year(-2025)
    
    def test_typical_leap_years(self):
        """Test leap years (divisible by 4)."""
        test_years = [2024, 2020, 2016]
        for year in test_years:
            self.calendar.set_year(year)
            self.assertTrue(self.calendar.is_leap_year())
    
    def test_typical_non_leap_years(self):
        """Test non-leap years."""
        test_years = [2023, 2022, 2021]
        for year in test_years:
            self.calendar.set_year(year)
            self.assertFalse(self.calendar.is_leap_year())
    
    def test_century_years(self):
        """Test years divisible by 100 (centuries)."""
        test_years = [2000, 1600, 2400, 1200]
        for year in test_years:
            self.calendar.set_year(year)
            self.assertTrue(self.calendar.is_leap_year())
            
        non_leap_years = [2100, 1300, 2500, 1900]
        for year in non_leap_years:
            self.calendar.set_year(year)
            self.assertFalse(self.calendar.is_leap_year())
            
    def test_century_non_leap_years(self):
        """Test years divisible by 100 but not by 400."""
        test_years = [2100, 1800, 1700, 2900]
        for year in test_years:
            self.calendar.set_year(year)
            self.assertFalse(self.calendar.is_leap_year())

if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'])