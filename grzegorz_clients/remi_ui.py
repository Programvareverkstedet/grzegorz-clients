import random, os, time, shutil, sys
from threading import Timer
import remi.gui as gui
from remi import App
from .utils import Namespace, call_as_thread, seconds_to_timestamp
from . import api
from .constants import *

#globals:
WIDTH = 512

class RemiApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(__file__), 'res')
		super(RemiApp, self).__init__(*args, static_file_path=res_path)
		
	def make_gui_elements(self):
		#logo:
		self.logo_image = gui.Image('/res/logo.png')
		
		#playback controls
		self.playback = Namespace()
		
		self.playback.playing = gui.Label("Now playing: None")# (TODO): update this
		
		self.playback.previous = gui.Button(ICON_PREV)
		self.playback.previous.set_on_click_listener(self.playback_previous)
		self.playback.play = gui.Button(ICON_PLAY)
		self.playback.play.set_on_click_listener(self.playback_play)
		self.playback.next = gui.Button(ICON_NEXT)
		self.playback.next.set_on_click_listener(self.playback_next)
		
		self.playback.volume_label = gui.Label("Volume:")
		self.playback.volume_slider = gui.Slider(100, 0, 100, 1)
		self.playback.volume_slider.set_oninput_listener(self.change_volume)
		
		self.playback.seek_slider = gui.Slider(0, 0, 100, 1)
		self.playback.seek_slider.set_oninput_listener(self.change_seek)
		
		self.playback.timestamp = gui.Label("--:-- - --:--")
		
		#playlist
		self.playlist = Namespace()
		
		self.playlist.table = gui.Table()
		self.playlist.table.append_from_list([['#', 'Name', "length", "", "", ""]], fill_title=True)
		
		self.playlist.shuffle = gui.Button("SHUFFLE")
		self.playlist.shuffle.set_on_click_listener(self.on_playlist_clear_shuffle)
		
		self.playlist.clear = gui.Button("CLEAR")
		self.playlist.clear.set_on_click_listener(self.on_playlist_clear_click)
		
		#input
		self.input = Namespace()
		self.input.add_song = gui.Label("Add song:")
		self.input.field = gui.TextInput(single_line=True)
		self.input.field.set_on_enter_listener(self.input_submit)
		self.input.submit = gui.Button("Submit!")
		self.input.submit.set_on_click_listener(self.input_submit)
	def make_gui_container(self):#placement and styling
		# Logo image:
		self.logo_image.width = WIDTH
		for i in (self.playback.previous, self.playback.play, self.playback.next):
			i.style["margin"] = "3px"
			i.style["width"]  = "2.8em"
		
		# Playback:
		self.playback.play.style["background"] \
			= f"linear-gradient(40deg,{COLOR_BLUE},{COLOR_PURPLE})"
		
		self.playback.volume_label.style["font-size"] = "0.8em"
		
		self.playback.volume_slider.style["width"] = "150px"
		self.playback.volume_slider.style["margin-left"] = "20px"
		self.playback.volume_slider.style["margin-bottom"] = "13px"
		
		self.playback.seek_slider.set_size("85%", "20px")
		self.playback.seek_slider.style["margin"] = "10px"
		
		# Playlist:
		self.playlist.table.style["width"] = "100%"
		self.playlist.table.style["margin"] = "10px"
		title_row = self.playlist.table.get_child("title")
		title_row.get_child(title_row._render_children_list[1]) \
			.style["width"] = "100%"
		
		self.playlist.clear.style["background"] \
			= f"linear-gradient(40deg,{COLOR_RED},{COLOR_ORANGE})"
		self.playlist.shuffle.style["background"] \
			= f"linear-gradient(40deg,{COLOR_TEAL},{COLOR_GREEN})"

		for i in (self.playlist.shuffle, self.playlist.clear):
			i.style["height"] = "1.8em"
			i.style["font-size"] = "0.8em"
			i.style["margin-left"] = "0.25em"
			i.style["margin-right"] = "0.25em"
		
		# Input field:
		self.input.field.style["height"] = "20px"
		self.input.field.style["margin"] = "5px"
		self.input.field.style["border"] = "1px solid %s" % COLOR_BLUE
		self.input.field.style["box-shadow"] = "0px 0px 5px 0px %s" % COLOR_BLUE_SHADOW
		
		self.input.submit.style["margin"] = "5px"
		
		# Containers:
		container = gui.VBox(width=WIDTH)
		container.style.update({"margin-left": "auto", "margin-right":"auto"})
		
		container.append(self.logo_image)
		
		container.append(self.playback.playing)
		
		playback_container = gui.HBox()
		playback_container.append(self.playback.previous)
		playback_container.append(self.playback.play)
		playback_container.append(self.playback.next)
		
		volume_container = gui.VBox()
		volume_container.append(self.playback.volume_label)
		volume_container.append(self.playback.volume_slider)
		playback_container.append(volume_container)

		container.append(playback_container)
		
		container.append(self.playback.seek_slider)
		container.append(self.playback.timestamp)
		
		container.append(self.playlist.table)
		
		playlist_button_container = gui.HBox()
		playlist_button_container.append(self.playlist.shuffle)
		playlist_button_container.append(self.playlist.clear)
		playlist_button_container.style["margin-left"] = "auto"
		playlist_button_container.style["margin-right"] = "0.25em"
		container.append(playlist_button_container)
		
		container.append(self.input.add_song)
		
		input_container = gui.HBox(width="100%")
		input_container.append(self.input.field)
		input_container.append(self.input.submit)
		container.append(input_container)
		
		return container
	def main(self):
		self.make_gui_elements()
		container = self.make_gui_container()
		self.mainLoop()
		return container
	def mainLoop(self):
		#self.playback.seek_slider.get_value()
		self.playback_update()
		self.playlist_update()
		
		Timer(1, self.mainLoop).start()

	# events:
	@call_as_thread
	def playback_previous(self, widget):
		api.playlist_previous()
	@call_as_thread
	def playback_play(self, widget):# toggle playblack
		if api.is_playing():
			api.set_playing(False)
			self.set_playing(False)
		else:
			api.set_playing(True)
			self.set_playing(True)
	@call_as_thread
	def playback_next(self, widget):
		api.playlist_next()
	@call_as_thread
	def input_submit(self, widget, value=None):
		if value is None:
			value = self.input.field.get_text()
		self.input.field.set_text("")
		
		self.input.field.set_enabled(False)
		self.input.submit.set_enabled(False)
		try:
			#data = get_youtube_metadata(value)
			data = None
		finally:
			self.input.field.set_enabled(True)
			self.input.submit.set_enabled(True)
		
		api.load_path(value, data)
	@call_as_thread
	def change_seek(self, widget, value):
		api.seek_percent(value)
	@call_as_thread
	def change_volume(self, widget, value):
		api.set_volume(value)
	@call_as_thread
	def on_table_row_click(self, row_widget, playlist_item):
		print("row", playlist_item)
	@call_as_thread
	def on_table_item_move_click(self, row_widget, playlist_item, down = True):
		index = playlist_item["index"]
		dest = index + 2 if down else index-1
		api.playlist_move(index, dest)
	@call_as_thread
	def on_table_item_remove_click(self, row_widget, playlist_item):
		api.playlist_remove(playlist_item["index"])
	@call_as_thread
	def on_playlist_clear_shuffle(self, row_widget):
		api.playlist_shuffle()
	@call_as_thread
	def on_playlist_clear_click(self, row_widget):
		api.playlist_clear()
		
	# playback steps:
	@call_as_thread
	def playback_update(self, times_called=[0]):
		is_playing = api.is_playing()
		self.set_playing(is_playing)

		if is_playing:
			try:
				playback_pos = api.get_playback_pos()
			except api.APIError:
				playback_pos = None
			if playback_pos:
				slider_pos = playback_pos["current"] / playback_pos["total"] * 100
				if self.playback.seek_slider.get_value() != slider_pos:
					self.playback.seek_slider.set_value(slider_pos)
				self.playback.timestamp.set_text(
					seconds_to_timestamp(playback_pos["current"])
					+ " - " + 
					seconds_to_timestamp(playback_pos["total"])
					)
			else:
				self.playback.timestamp.set_text("--:-- - --:--")
				
		if times_called[0] % 5 == 0:
			volume = api.get_volume()
			if volume > 100: volume = 100
			if self.playback.volume_slider.get_value() != volume:
				self.playback.volume_slider.set_value(volume)
		times_called[0] += 1
	@call_as_thread
	def volume_update(self):
		self.volume.slider.set_value(api.get_volume())
	@call_as_thread
	def playlist_update(self):
		playlist = api.get_playlist()
		
		N = len(playlist)
		table = []
		for i, playlist_item in enumerate(playlist):
			name = playlist_item["filename"]
			length = "--:--"
			if "data" in playlist_item:
				if "title" in playlist_item["data"]:
					name = playlist_item["data"]["title"]
				if "duration" in playlist_item["data"]:
					length = seconds_to_timestamp(playlist_item["data"]["duration"])
			
			if playlist_item.get("current", False):
				self.playback.previous.set_enabled(i != 0)
				self.playback.next.set_enabled(i != N-1)

			table.append([
				playlist_item["index"],
				name,
				length,
				ICON_UP,
				ICON_DOWN,
				ICON_TRASH,
			])

		self.playlist.table.empty(keep_title=True)
		self.playlist.table.append_from_list(table)
		
		for row_widget, playlist_item in zip(
				map(self.playlist.table.get_child, self.playlist.table._render_children_list[1:]),
				playlist):
			if "current" in playlist_item:
				row_widget.style["background-color"] = COLOR_LIGHT_BLUE
			else:
				row_widget.style["color"] = COLOR_GRAY_DARK
			row_widget.set_on_click_listener(self.on_table_row_click, playlist_item)
			for index, (key, item_widget) in enumerate(zip(row_widget._render_children_list,
					map(row_widget.get_child, row_widget._render_children_list))):
				if index == 1 and "failed" in playlist_item.get("data", {}):
					item_widget.style["width"] = "1.1em"
					item_widget.style["color"] = COLOR_RED
				if index >= 3:
					item_widget.style["width"] = "1.1em"
					item_widget.style["color"] = COLOR_TEAL
				if index == 3:
					item_widget.set_on_click_listener(self.on_table_item_move_click, playlist_item, False)
					if playlist_item["index"] == 0:
						item_widget.style["color"] = COLOR_GRAY_LIGHT
				if index == 4:
					item_widget.set_on_click_listener(self.on_table_item_move_click, playlist_item, True)
					if playlist_item["index"] == N-1:
						item_widget.style["color"] = COLOR_GRAY_LIGHT
				if index == 5:
					item_widget.style["color"] = COLOR_RED
					item_widget.set_on_click_listener(self.on_table_item_remove_click, playlist_item)
				#print(index, key, item_widget)

	#helpers
	def set_playing(self, is_playing:bool):
		self.playback.play.set_text(ICON_PAUSE if is_playing else ICON_PLAY)
		self.playback.seek_slider.set_enabled(is_playing)
		
