class Calendar:
    #docstring
    """
    
    This class represents a calendar and provides methods to check if a given year is a leap year.
    
    """
    def is_leap_year(self, year):
        if year <= 0:
            return False
        elif year % 4 != 0:
            return False
        elif year % 100 != 0:
            return True
        elif year % 400 != 0:
            return False
        else:
            return True

def main():
    """
    
    Main function to test the is_leap_year method using unit testing.
    
    """
    tc = [1, 4, 100, 400, 12, 15, 27, 500, 1000, 1932, 1971, 2000, 2012, 2015, 2016, 2020, 4000]
    expected_result = [False, True, False, True, True, False, False, False, False, True, False, True, True, False, True, True, True]
    
    calendar = Calendar()
    
    for i in range(len(tc)):
        computed_result = calendar.is_leap_year(tc[i])
        print(f"Test case: {i + 1}")
        
        if computed_result == expected_result[i]:
            print("Passed")
        else:
            print(f"Failed\nExpected [{expected_result[i]}] but found [{computed_result}]")

if __name__ == "__main__":
    main()