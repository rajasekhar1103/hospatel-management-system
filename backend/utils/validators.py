"""
Input validation utilities for API endpoints
"""
from flask import jsonify
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def validate_json(required_fields=None):
    """
    Decorator to validate required JSON fields in request body
    
    Args:
        required_fields: List of required field names
    
    Returns:
        Decorator function that validates input
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if required_fields is None:
                return f(*args, **kwargs)
                
            data = None
            try:
                data = kwargs.get('data') or {}  # For manual calls
                from flask import request
                if not data and request.is_json:
                    data = request.get_json() or {}
            except:
                return jsonify(msg="Invalid JSON format"), 400
            
            if not data:
                return jsonify(msg="Request body is required"), 400
            
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return jsonify(
                    msg=f"Missing required fields: {', '.join(missing_fields)}"
                ), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_string(value, max_length=None, strip=True):
    """
    Sanitize and validate string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        strip: Whether to strip whitespace
    
    Returns:
        Sanitized string or None
    """
    if value is None:
        return None
    
    if not isinstance(value, str):
        return None
    
    if strip:
        value = value.strip()
    
    if max_length and len(value) > max_length:
        return None
    
    return value


def validate_date_format(date_str, format_str='%Y-%m-%d'):
    """
    Validate date format and return datetime object
    
    Args:
        date_str: Date string to validate
        format_str: Expected date format
    
    Returns:
        (datetime_object, None) on success or (None, error_message) on failure
    """
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date_str, format_str).date()
        return date_obj, None
    except (ValueError, TypeError) as e:
        return None, f"Invalid date format. Expected {format_str}"


def validate_time_format(time_str, format_str='%H:%M'):
    """
    Validate time format and return time object
    
    Args:
        time_str: Time string to validate
        format_str: Expected time format
    
    Returns:
        (time_object, None) on success or (None, error_message) on failure
    """
    from datetime import datetime
    try:
        time_obj = datetime.strptime(time_str, format_str).time()
        return time_obj, None
    except (ValueError, TypeError) as e:
        return None, f"Invalid time format. Expected {format_str}"


def validate_integer(value, min_val=None, max_val=None):
    """
    Validate integer value within range
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        (integer, None) on success or (None, error_message) on failure
    """
    try:
        int_val = int(value)
        if min_val is not None and int_val < min_val:
            return None, f"Value must be >= {min_val}"
        if max_val is not None and int_val > max_val:
            return None, f"Value must be <= {max_val}"
        return int_val, None
    except (ValueError, TypeError):
        return None, "Must be a valid integer"
