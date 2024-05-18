from . import api, utils
from pathlib import Path
from datetime import timedelta
import json
import os
import rich
import shutil
import subprocess
import sys
import typer

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Button, Static, ProgressBar, DataTable

from textual.timer import Timer
from textual import on
from textual.app import App, ComposeResult
import textual.containers as c
from textual.reactive import var
import textual.widgets as w
from textual.events import Mount
from textual.widgets import DirectoryTree, Footer, Header, Static


# export GRZEGORZ_DEFAULT_API_BASE="https://brzeczyszczykiewicz.pvv.ntnu.no/api"
# export GRZEGORZ_DEFAULT_API_BASE="https://georg.pvv.ntnu.no/api"
DEFAULT_API_BASE = os.environ.get("GRZEGORZ_DEFAULT_API_BASE", "https://brzeczyszczykiewicz.pvv.ntnu.no/api")


# url input
# prev - Button
# play/pause - Button
# next - Button
# loop - Switch
# shuffle - Button
# clear - Button
# position - ProgressBar

# playlist - datatable

# waveform - Sparkline

# LoadingIndicator

class GrzegorzApp(App):
    CSS_PATH = "gzregorz.tcss"
    #DEFAULT_CSS = ""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    refresh_timer: Timer

    def compose(self) -> ComposeResult:
        yield Static("Now playing: ", id="header")
        yield Horizontal(
            ProgressBar(id="seekbar", total=0, show_percentage=False, show_eta=False),
            Static(" --:-- --:--", id="playtime"),
            classes="center"
        )
        yield Horizontal(
            ProgressBar(id="volumebar", total=100, show_eta=False),
            classes="center"
        )
        yield Horizontal(
            Button.error("Clear", id="btn-clear"),
            Button("Prev", id="btn-prev"),
            Button.success("Play", id="btn-play"),
            Button("Next", variant="primary", id="btn-next"),
            Button.warning("Shuffle", id="btn-shuffle"),
            id="controls",
        )
        yield VerticalScroll(
            DataTable(
                id="playlist",
                zebra_stripes=True,
                cursor_type="row",
            ),
        )

    def on_mount(self) -> None:
        api.set_endpoint("https://georg.pvv.ntnu.no/api")
        self.refresh_timer = self.set_interval(1 / 1, self.do_update) # threaded

        # self.log(api.get_playlist())
        playlist: DataTable = self.query_one("#playlist")
        playlist.add_columns("#", "Name", "length")

    def do_update(self):
        self.log("do_update")

        # update status
        vol  = api.get_volume()
        pos  = api.get_playback_pos() or {"current": 0, "left": 0, "total": 0}
        loop = api.get_playlist_looping()
        play = api.is_playing()
        self.log(f"""
            {vol  = }
            {pos  = }
            {loop = }
            {play = }
        """)

        # todo: sliders?
        seek_var: ProgressBar = self.query_one("#seekbar")
        seek_var.total    = pos.get("total",   0)
        seek_var.progress = pos.get("current", 0)

        playtime: Static  = self.query_one("#playtime")
        playtime.update(f" --:-- - --:--" if not play else f" {timedelta(seconds=int(pos.get('current', 0)))} - {timedelta(seconds=int(pos.get('total', 0)))}")

        vol_var: ProgressBar  = self.query_one("#volumebar")
        vol_var.progress = vol

        btn_play: Button  = self.query_one("#btn-play")
        btn_play.label = "Pause" if play else "Play"
        # btn_play.variant = "success" if play else "default"

        # update playlist
        playlist_data = api.get_playlist()
        table = [
            (
                item.get("index", -1),
                item.get("data", {}).get("title", None) or item["filename"],
                utils.seconds_to_timestamp(item["data"]["duration"]) if "duration" in item.get("data", {}) else "--:--",
            )
            for item in playlist_data
        ]
        current, = [item for item in playlist_data if item.get("current", False)][:1] or [None]
        if current is not None:
            self.query_one("#header").update("Now playing: " +
                current.get("data", {}).get("title", None) or current["filename"]
            )

        playlist: DataTable = self.query_one("#playlist")
        for r, row in enumerate(table[:playlist.row_count]):
            for c, col in enumerate(row):
                playlist.update_cell_at((r, c), col)
        if playlist.row_count < len(table): # add more rows
            playlist.add_rows(table[playlist.row_count:])
        elif playlist.row_count > len(table): # remove extra rows
            for i in range(playlist.row_count-1, len(table)-1, -1):
                playlist.remove_row(playlist._row_locations.get_key(i))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-clear":
            api.playlist_clear()
        elif event.button.id == "btn-prev":
            api.playlist_previous()
        elif event.button.id == "btn-play":
            api.set_playing(not api.is_playing())
        elif event.button.id == "btn-next":
            api.playlist_next()
        elif event.button.id == "btn-shuffle":
            api.playlist_shuffle()

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.log("spismeg")
        self.log(f"{event            = }")
        self.log(f"{event.cursor_row = }")
        self.log(f"{event.row_key    = }")
        self.log("spismeg")

def main():
    app = GrzegorzApp()
    app.run()

if __name__ == "__main__":
    main()
