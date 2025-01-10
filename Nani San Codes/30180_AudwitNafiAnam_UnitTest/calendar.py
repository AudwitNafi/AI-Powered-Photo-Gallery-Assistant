class Calendar:
    """
    A Calendar class that handles year-related calculations.
    
    Attributes:
        year (int): The year to perform calculations on
    """
    
    def __init__(self, year):
        """
        Initialize the Calendar with a specific year.
        
        Args:
            year: The year to set for the calendar
            
        Raises:
            ValueError: If the year is not a positive integer
        """
        self.set_year(year)
    
    def set_year(self, year):
        """
        Set the year for the calendar.
        
        Args:
            year: The year to set
            
        Raises:
            ValueError: If the year is not a positive integer
        """
        if not isinstance(year, int):
            raise ValueError("Year must be an integer")
        if year <= 0:
            raise ValueError("Year must be a positive number")
        self._year = year
    
    @property
    def year(self):
        """Get the current year."""
        return self._year
    
    def is_leap_year(self):
        """
        Determine whether the current year is a leap year.
        
        Returns:
            bool: True if the year is a leap year, False otherwise
        """
        if self._year % 4 == 0:
            if self._year % 100 == 0:
                return self._year % 400 == 0
            return True
        return False

if __name__ == '__main__':
    # Example usage
    try:
        year = int(input("Enter a year to check: "))
        calendar = Calendar(year)
        result = calendar.is_leap_year()
        print(f"{calendar.year} is{' ' if result else ' not '}a leap year")
    except ValueError as e:
        print(f"Error: {e}")