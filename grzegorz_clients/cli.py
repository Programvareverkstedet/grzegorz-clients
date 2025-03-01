from . import api
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import os
import rich
import shutil
import subprocess
import sys
import typer

# export GRZEGORZ_DEFAULT_API_BASE="https://georg.pvv.ntnu.no/api"
# export GRZEGORZ_DEFAULT_API_BASE="https://brzeczyszczykiewicz.pvv.ntnu.no/api"
# export GRZEGORZ_DEFAULT_API_BASE="https://georg.pvv.ntnu.no/api;https://brzeczyszczykiewicz.pvv.ntnu.no/api"

DEFAULT_API_BASE = os.environ.get("GRZEGORZ_DEFAULT_API_BASE", "https://brzeczyszczykiewicz.pvv.ntnu.no/api")
if ";" in DEFAULT_API_BASE:
    if shutil.which("gum"):
        DEFAULT_API_BASE = subprocess.run([
            "gum", "choose",
            *DEFAULT_API_BASE.split(";"),
            "--header=Please select an endpoint...",
        ], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    else:
        DEFAULT_API_BASE = DEFAULT_API_BASE.split(";", 1)[0]

def print_json(obj):
    if not isinstance(obj, str):
        obj = json.dumps(obj)
    rich.print_json(obj)

cli = typer.Typer(no_args_is_help=True)

def _add(
    urls     : list[str],
    put_pre  : bool = False,
    put_post : bool = False,
    play     : bool = False,
    api_base : str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)
    if put_pre or put_post:
        pre = api.get_playlist()

    for url in urls:
        resp = api.load_path(url)
        rich.print(f"{url} : {resp!r}", file=sys.stderr)

    if put_pre or put_post:
        assert put_pre != put_post
        post = api.get_playlist()
        current_index, = [i.get("index", -1) for i in post if i.get("current", False)][:1] or [0]
        old_indices = set(i.get("index", -1) for i in pre)
        new_indices = set(i.get("index", -1) for i in post) - old_indices
        assert all(i > current_index for i in new_indices)
        target = current_index if put_pre else current_index + 1
        if target not in new_indices:
            for idx in sorted(new_indices):
                api.playlist_move(idx, target)
                target += 1

    if play:
        assert put_pre or put_post
        api.playlist_goto(current_index if put_pre else current_index + 1)
        api.set_playing(True)

@cli.command(help="Add one or more items to the playlist")
def play(
    urls: list[str],
    pre: bool = False,
    api_base: str = DEFAULT_API_BASE,
):
    _add(urls, put_post=not pre, put_pre=pre, play=True, api_base=api_base)

@cli.command(help="Add one or more items to the playlist")
def next(
    urls: list[str],
    api_base: str = DEFAULT_API_BASE,
):
    _add(urls, put_post=True, api_base=api_base)

@cli.command(help="Add one or more items to the playlist")
def queue(
    urls: list[str],
    play: bool = True,
    api_base: str = DEFAULT_API_BASE,
):
    _add(urls, api_base=api_base)
    if play:
        api.set_playing(True)

@cli.command(name="list", help="List the current playlist")
def list_(
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)
    print_json(api.get_playlist())

@cli.command(help="Set Playing to True")
def resume( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    # TODO: add logic to seek to start of song if at end of song AND at end of playlist?
    rich.print(api.set_playing(True), file=sys.stderr)

@cli.command(help="Unset Playing")
def pause( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.set_playing(False), file=sys.stderr)

@cli.command(help="Toggle playback")
def toggle(api_base: str = DEFAULT_API_BASE):
    api.set_endpoint(api_base)
    playing = api.is_playing()
    rich.print(api.set_playing(not playing), file=sys.stderr)

@cli.command(help="Goto next item in playlist")
def skip( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.playlist_next(), file=sys.stderr)

@cli.command(help="Goto previous item in playlist")
def prev( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.playlist_previous(), file=sys.stderr)

@cli.command(help="Goto a specific item in the playlist")
def goto( index: int, api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.playlist_goto(index), file=sys.stderr)

@cli.command(help="Shuffle the playlist")
def shuf( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.playlist_shuffle(), file=sys.stderr)

@cli.command(help="Clear the playlist")
def clear( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.playlist_clear(), file=sys.stderr)

@cli.command(help="Get current status")
def status(
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)

    status = dict(
        playing      = api.is_playing,
        volume       = api.get_volume,
        is_looping   = api.get_playlist_looping,
        playback_pos = api.get_playback_pos,
        current = lambda: [i for i in api.get_playlist() if i.get("current", False)][:1] or [None],
    )

    with ThreadPoolExecutor() as p:
        status = dict(zip(status.keys(), p.map(lambda x: x(), status.values())))

    print_json(status)


@cli.command(help="Set the playback volume")
def set_volume(
    volume: str,
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)

    volume = volume.removesuffix("%")

    if volume.startswith("+") or volume.startswith("-"):
        current_volume = api.get_volume()
        new_volume = max(0, min(100, current_volume + int(volume)))
        new_volume = int(new_volume)
    else:
        new_volume = int(volume)

    rich.print(api.set_volume(new_volume), file=sys.stderr)


if __name__ == "__main__":
	cli()
