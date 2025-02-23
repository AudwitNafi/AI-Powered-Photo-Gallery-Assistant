def month_mapper(month_num):
    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    return month_names.get(month_num, "Invalid Month")

def split_date(date_str):
    try:
        month, day, year = date_str.split('-')
        return int(year), month_mapper(int(month)), int(day)
    except ValueError:
        raise ValueError("Invalid date format. Please use mm-dd-yyyy")
