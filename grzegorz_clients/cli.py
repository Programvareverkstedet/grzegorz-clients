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


@cli.command(help="Add one ore more items to the playlist. [--play, --now]")
def add(
    urls: list[str],
    play: bool = False,
    now: bool = False,
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)
    if now:
        pre = api.get_playlist()

    for url in urls:
        resp = api.load_path(url)
        rich.print(f"{url} : {resp!r}", file=sys.stderr)

    if now:
        post = api.get_playlist()
        current_index, = [i.get("index", -1) for i in post if i.get("current", False)][:1] or [0]
        old_indices = set(i.get("index", -1) for i in pre)
        new_indices = set(i.get("index", -1) for i in post) - old_indices
        assert all(i > current_index for i in new_indices)
        target = current_index
        if not play: target += 1
        if target not in new_indices:
            for idx in sorted(new_indices):
                api.playlist_move(idx, target)
                target += 1

    if play:
        if now: api.playlist_goto(current_index)
        api.set_playing(True)

@cli.command(name="list", help="List the current playlist")
def list_(
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)
    print_json(api.get_playlist())

@cli.command(help="Set Playing")
def play( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    # TODO: add logic to seek to start of song if at end of song AND at end of playlist?
    rich.print(api.set_playing(True), file=sys.stderr)

@cli.command(help="Unset Playing")
def pause( api_base: str = DEFAULT_API_BASE ):
    api.set_endpoint(api_base)
    rich.print(api.set_playing(False), file=sys.stderr)

@cli.command(help="Goto next item in playlist")
def next( api_base: str = DEFAULT_API_BASE ):
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
    volume: float,
    api_base: str = DEFAULT_API_BASE,
):
    api.set_endpoint(api_base)
    rich.print(api.set_volume(volume), file=sys.stderr)


if __name__ == "__main__":
	cli()
