from datetime import date

def get_current_date_string() -> str:
    """Returns today's date as a string in 'YYYYMMDD' format."""
    return date.today().strftime('%Y%m%d')

def get_readme_date_string() -> str:
    """Returns today's date as a string in 'YYYY-MM-DD' format."""
    return date.today().strftime('%Y-%m-%d')