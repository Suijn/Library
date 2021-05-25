import datetime

def calculate_end_date(start_date):
    """Calculate the date until which the book has to be returned."""
    delta = datetime.timedelta(days=30)
    end_date = start_date + delta
    return end_date