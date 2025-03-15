from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask import jsonify, request
from typing import Dict, Any, Optional, Union, Tuple, Callable
import functools

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def api_response(data: Any = None, error: Optional[str] = None, status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized API response.
    
    Args:
        data: The data to return in the response
        error: An error message, if applicable
        status_code: HTTP status code
        
    Returns:
        A tuple containing the JSON response and HTTP status code
    """
    response = {
        "status": "success" if error is None else "error",
        "data": data
    }
    
    if error:
        response["error"] = error
        # If no status code was explicitly set for an error, use 400
        if status_code == 200:
            status_code = 400
            
    return jsonify(response), status_code

def is_api_request() -> bool:
    """
    Determine if the current request is an API request.
    
    Returns:
        True if the request path starts with /api/ or Accept header indicates JSON
    """
    path_is_api = request.path.startswith('/api/')
    accepts_json = request.headers.get('Accept', '').find('application/json') >= 0
    json_content_type = request.headers.get('Content-Type', '').find('application/json') >= 0
    
    return path_is_api or accepts_json or json_content_type

def api_route(f: Callable) -> Callable:
    """
    Decorator for routes that can be accessed via both API and web interface.
    For API requests, returns JSON. For web requests, returns HTML.
    
    Args:
        f: The route function to decorate
        
    Returns:
        Decorated function that handles both API and web requests
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the result from the wrapped function
        result = f(*args, **kwargs)
        
        # If it's an API request, convert the result to JSON API response
        if is_api_request():
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], dict):
                # Result is already in the format (data, status_code)
                return api_response(data=result[0], status_code=result[1])
            elif isinstance(result, dict):
                # Result is a dictionary to be converted to JSON
                return api_response(data=result)
                
        # For web requests, return the original result (usually HTML)
        return result
        
    return decorated_function
