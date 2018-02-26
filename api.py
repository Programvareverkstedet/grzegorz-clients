import requests, urllib
from functools import wraps
from pathlib import Path

# (TODO)Move to config?
BASE_URL = Path('http://bokhylle.pvv.ntnu.no:8080/api')

# Exceptions:
class APIError(Exception): pass

# decorator:
def request_post(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url, data = func(*args, **kwargs)
        response = requests.post(url, data=data)
        json = json.loads(response.text)
        if "error" not in json or json["error"] != False:
            raise APIError(json["error_msg"])
        return json["success"]
    return new_func
def request_get(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        url = func(*args, **kwargs)
        response = requests.get(url)
        json = json.loads(response.text)
        if "error" not in json or json["error"] != False:
            raise APIError(json["error_msg"])
        return json["value"]
    return new_func

# methods:

@request_post
def is_playing(path:str):
    args = urllib.urlencode(locals())
    return BASE_URL / f"play?{args}", None

@request_get
def is_playing():
    return BASE_URL / f"play"

@request_post
def set_playing(play:bool):
    args = urllib.urlencode(locals())
    return BASE_URL / f"play?{args}", None

@request_get
def get_volume():
    return BASE_URL / f"volume"

@request_post
def set_volume(volume:int):# between 0 and 100 (you may also exceed 100)
    args = urllib.urlencode(locals())
    return BASE_URL / f"volume?{args}", None

@request_get
def get_playlist():
    return BASE_URL / f"playlist"

@request_post
def playlist_next():
    return BASE_URL / f"playlist/next", None

@request_post
def playlist_previous():
    return BASE_URL / f"playlist/previous", None
