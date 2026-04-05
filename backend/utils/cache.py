"""
Cache utilities for optimized database queries and API responses
"""
from functools import wraps
from flask import request, jsonify
from datetime import timedelta

# Cache decorator for GET endpoints
def cached(timeout=300):
    """
    Decorator to cache GET request responses
    Args:
        timeout: Cache duration in seconds (default: 5 minutes)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip caching for non-GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # Generate cache key from route + params
            cache_key = f"cache:{request.path}:{request.query_string.decode()}"
            
            # For now, call function directly
            # Ready for Redis integration
            result = f(*args, **kwargs)
            return result
        return decorated_function
    return decorator


def pagination_params():
    """
    Extract and validate pagination parameters from request
    Returns: (page, per_page) tuple
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 items per page
    
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    
    return page, per_page


def paginate_query(query, page, per_page):
    """
    Paginate a SQLAlchemy query
    Returns: (items, total_count, total_pages)
    """
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return items, total, total_pages


def paginate_response(items, page, per_page, total, total_pages):
    """
    Format paginated response
    """
    return {
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }
    }
