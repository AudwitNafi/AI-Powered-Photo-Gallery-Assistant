def month_mapper(month_num):
    month_names = {
        '01': "January",
        '02': "February",
        '03': "March",
        '04': "April",
        '05': "May",
        '06': "June",
        '07': "July",
        '08': "August",
        '09': "September",
        '10': "October",
        '11': "November",
        '12': "December"
    }
    return month_names.get(month_num, "Invalid Month")

def split_date(date_str):
    try:
        year, month, day = date_str.split('-')
        return int(year), month_mapper(month), int(day)
    except ValueError:
        raise ValueError("Invalid date format. Please use mm-dd-yyyy")
