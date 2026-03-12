def get_day_number(day_number):
    if 1 <= day_number <= 26:
        return chr(ord('A') + day_number - 1)
    return None

_MONTHS = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]

def get_month(month):
    try:
        return _MONTHS.index(month) + 3
    except ValueError:
        return None