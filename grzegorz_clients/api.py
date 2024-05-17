import requests, json
from urllib.parse import urlencode
from functools import wraps

# This must be set to be able to use it on remote hosts
BASE_URL = "http://localhost:8080/api"
def set_endpoint(base_url:str):
    global BASE_URL
    BASE_URL = base_url

# Exceptions:
class APIError(Exception): pass

def parse_message(method, url, status, function_name, json_text):
    prefix = f"[{function_name}] {method} /{url} -> {status}:"
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        raise APIError(f"{prefix} Expected json response, got:\n{json_text}")

    if "error" not in data:
        raise APIError(f"{prefix} Missing json data 'error', got:\n{json_text}")

    if data["error"] != False:
        raise APIError(f"{prefix} Got error {str(data['error'])}, got:\n{json_text}")

    if "success" not in data:
        raise APIError(f"{prefix} Missing json data 'error', got:\n{json_text}")

    return data

# decorator:
# (TODO): Add logging
def request_delete(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        response = requests.delete(f"{BASE_URL}/{url}", json=data)
        response.raise_for_status() # raises HTTPError, if any
        data = parse_message(
            "DELETE",
            url,
            response.status_code,
            func.__name__,
            response.text,
        )
        return data["success"]
    return new_func

def request_post(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        response = requests.post(f"{BASE_URL}/{url}", json=data)
        response.raise_for_status() # raises HTTPError, if any
        data = parse_message(
            "POST",
            url,
            response.status_code,
            func.__name__,
            response.text,
        )
        return data["success"]
    return new_func

def request_get(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url = func(*args, **kwargs)
        response = requests.get(f"{BASE_URL}/{url}")
        response.raise_for_status() # raises HTTPError, if any
        data = parse_message(
            "GET",
            url,
            response.status_code,
            func.__name__,
            response.text,
        )

        if "value" not in data:
            raise APIError(f"[{func.__name__}] Missing json data 'value', got:\n{json.dumps(data)}")

        return data["value"]
    return new_func

# methods:

@request_post
def load_path(path:str, data: dict = None):
    args = urlencode(locals())
    return f"load?{args}", data

@request_get
def is_playing():
    return "play"

@request_post
def set_playing(play: bool):
    args = urlencode(locals())
    return f"play?{args}", None

@request_get
def get_volume():
    return "volume"

@request_post
def set_volume(volume: float): # between 0 and 100 (you may also exceed 100)
    args = urlencode(locals())
    return f"volume?{args}", None

@request_get
def get_playlist():
    return "playlist"

@request_post
def playlist_next():
    return "playlist/next", None

@request_post
def playlist_goto(index: int):
    args = urlencode(locals())
    return f"playlist/goto?{args}", None

@request_post
def playlist_previous():
    return "playlist/previous", None

@request_post
def playlist_shuffle():
    return "playlist/shuffle", None

@request_delete
def playlist_clear():
    return "playlist", None

@request_delete
def playlist_remove(index: int):
    args = urlencode(locals())
    return f"playlist?{args}", None

@request_post
def playlist_move(index1: int, index2: int):
    args = urlencode(locals())
    return f"playlist/move?{args}", None

@request_get
def get_playlist_looping():
    return "playlist/loop"

@request_post
def playlist_set_looping(looping: bool):
    return f"playlist/loop?loop={str(bool(looping)).lower()}", None

@request_get
def get_playback_pos():
    return "time"

@request_post
def seek_absolute(pos: float):
    args = urlencode(locals())
    return f"time?{args}", None

@request_post
def seek_percent(percent: int):
    args = urlencode(locals())
    return f"time?{args}", None
