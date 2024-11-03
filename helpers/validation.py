import re

def validate_email(email):
    """Validate email format using a regex pattern."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Ensure password is at least 8 characters long."""
    return len(password) >= 8

def validate_required_fields(data, required_fields):
    """Check if all required fields are present and not empty."""
    return all(data.get(field) for field in required_fields)
