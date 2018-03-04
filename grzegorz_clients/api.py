import requests, json
from urllib.parse import urlencode
from functools import wraps
from . import api

# This must be set to be able to use it on remote hosts
BASE_URL = "http://localhost:8080/api"
def set_endpoint(base_url:str):
    global BASE_URL
    BASE_URL = base_url

# Exceptions:
class APIError(Exception): pass

# decorator:
# (TODO): Add logging
def request_delete(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        if type(data) is dict: data = json.dumps(data)
        response = requests.delete(f"{BASE_URL}/{url}", data=data)
        data = json.loads(response.text)
        if "error" not in data or data["error"] != False:
            print(data)
            raise APIError(data["error"])
        return data["success"]
    return new_func
def request_post(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        if type(data) is dict: data = json.dumps(data)
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
def load_path(path:str, data:dict=None):
    args = urlencode(locals())
    return f"load?{args}", data

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

@request_delete
def playlist_clear():
    return f"playlist", None

@request_delete
def playlist_remove(index:int):
    args = urlencode(locals())
    return f"playlist?{args}", None

@request_get
def get_playback_pos():
    return f"time"

@request_post
def seek_absolute(pos:float):
    args = urlencode(locals())
    return f"time?{args}", None

@request_post
def seek_percent(percent:int):
    args = urlencode(locals())
    return f"time?{args}", None
