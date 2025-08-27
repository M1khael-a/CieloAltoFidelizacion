from flask import abort
from flask_login import current_user
from functools import wraps

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(403)
            if current_user.rol not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return wrapper
