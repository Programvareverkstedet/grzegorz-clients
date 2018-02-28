import requests, json
from urllib.parse import urlencode
from functools import wraps
import api

# This will be overwritten by config
BASE_URL = "http://localhost:8080/api"

# Exceptions:
class APIError(Exception): pass

# decorator:
def request_post(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        response = requests.post(f"{BASE_URL}/{url}", data=data)
        data = json.loads(response.text)
        if "error" not in data or data["error"] != False:
            print(data)
            raise APIError(data["error"])
        return data["success"]
    return new_func
def request_get(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url = func(*args, **kwargs)
        response = requests.get(f"{BASE_URL}/{url}")
        data = json.loads(response.text)
        if "error" not in data or data["error"] != False:
            raise APIError(data["errortext"])
        return data["value"]
    return new_func

# methods:

@request_post
def load_path(path:str):
    args = urlencode(locals())
    return f"load?{args}", None

@request_get
def is_playing():
    return f"play"

@request_post
def set_playing(play:bool):
    args = urlencode(locals())
    return f"play?{args}", None

@request_get
def get_volume():
    return f"volume"

@request_post
def set_volume(volume:int):# between 0 and 100 (you may also exceed 100)
    args = urlencode(locals())
    return f"volume?{args}", None

@request_get
def get_playlist():
    return f"playlist"

@request_post
def playlist_next():
    return f"playlist/next", None

@request_post
def playlist_previous():
    return f"playlist/previous", None

@request_get
def get_playback_pos():
    return f"time"

@request_post
def seek_absolute(pos):
    args = urlencode(locals())
    return f"time?{args}", None

@request_post
def seek_percent(percent):
    args = urlencode(locals())
    return f"time?{args}", None
