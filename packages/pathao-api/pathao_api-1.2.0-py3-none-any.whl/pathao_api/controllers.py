import requests
from functools import wraps

# -------------------------------
# Decorators
# -------------------------------
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = kwargs.get("token")  # â Only look in keyword args

        if not token:
            raise ValueError("Authorization token is required as a keyword argument (token=...)")

        return func(*args, **kwargs)
    return wrapper

# -------------------------------
# Exceptions
# -------------------------------
class UnauthorizedError(Exception):
    """Custom exception for 401 responses"""
    pass

# -------------------------------
# Helper function for requests
# -------------------------------
def request_with_401_check(method, url, token=None, payload=None):
    """
    Generic request wrapper that raises UnauthorizedError on 401
    and parses JSON response.
    """
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}" if token else ""
    }

    if method.lower() == "post" and payload is not None:
        headers["Content-Type"] = "application/json"

    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, json=payload)
        else:
            raise ValueError("Unsupported HTTP method")

        if response.status_code == 401:
            raise UnauthorizedError("401 Unauthorized")

        response.raise_for_status()  # Raises HTTPError for 4xx/5xx

        try:
            return response.json()
        except ValueError:
            raise ValueError("Response is not valid JSON")

    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}") from e

# -------------------------------
# Token functions
# -------------------------------
def issue_access_token(url: str, args: dict):
    """
    Request an access token using provided credentials.
    """
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=args, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Token request failed: {e}") from e
    except ValueError:
        raise ValueError("Token response is not valid JSON")

def issue_refresh_token(url: str, args: dict):
    """
    Refresh an access token using refresh token.
    """
    try:
        response = requests.post(url, json=args)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Refresh token request failed: {e}") from e
    except ValueError:
        raise ValueError("Refresh token response is not valid JSON")

# -------------------------------
# API Controller functions
# -------------------------------
@token_required
def get_city_list(url: str, token: str):
    print(f"Token: {token}")
    return request_with_401_check("get", url, token=token)

@token_required
def get_zone_list(url: str, token: str):
    return request_with_401_check("get", url, token=token)

@token_required
def get_area_list(url: str, token: str):
    return request_with_401_check("get", url, token=token)

@token_required
def get_price_plan(url: str, payload: dict, token: str):
    return request_with_401_check("post", url, token=token, payload=payload)

@token_required
def get_stores_info(url: str, token: str):
    return request_with_401_check("get", url, token=token)

@token_required
def create_order(url: str, token: str, payload: dict):
    return request_with_401_check("post", url, token=token, payload=payload)