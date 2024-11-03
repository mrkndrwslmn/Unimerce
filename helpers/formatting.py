from datetime import datetime

def format_date(date):
    """Convert a date object to 'YYYY-MM-DD' format."""
    return date.strftime('%Y-%m-%d') if isinstance(date, datetime) else None

def format_currency(amount):
    """Format a float amount to currency string."""
    return f"${amount:,.2f}"

def truncate_string(text, length=50):
    """Truncate a string to a specific length."""
    return text[:length] + '...' if len(text) > length else text

def time_ago(joined_date):
    now = datetime.now()
    diff = now - joined_date

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    weeks = days // 7
    months = days // 30
    years = days // 365

    if years > 0:
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
    
def currency_format(value):
    """Format a number as currency with commas and two decimal places."""
    try:
        return f"₱{value:,.2f}"
    except (ValueError, TypeError):
        return "₱0.00"
    