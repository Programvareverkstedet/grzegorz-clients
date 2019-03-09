import random, os, time, shutil, sys
from threading import Timer
import remi.gui as gui
from remi import App
from .utils import Namespace, call_as_thread, seconds_to_timestamp
from . import api
from .constants import *

#globals:
WIDTH_L = 400
WIDTH_R = 512
WIDTH = WIDTH_L  + 40 + WIDTH_R

class RemiApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(__file__), 'res')
		super(RemiApp, self).__init__(*args, static_file_path=res_path)
		
	def make_gui_elements(self):#content and behaviour
		#logo:
		self.logo_image = gui.Image('/res/logo.png')
		
		#playback controls
		self.playback = Namespace()
		
		self.playback.playing = gui.Label("Now playing: None")# (TODO): update this
		
		self.playback.party = gui.Button(ICON_PARTY)
		self.playback.party.attributes["onclick"] = "document.body.classList.toggle('dancing');"
		self.playback.party.attributes["title"] = "ENABLE PARTY MODE" # hover text
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
		self.logo_image.style["width"] = f"100%"
		for i in (self.playback.previous, self.playback.play, self.playback.next, self.playback.party):
			i.style["margin"] = "3px"
			i.style["width"]  = "2.8em"
		
		# Playback:
		self.playback.party.style["background"] \
			= f"linear-gradient(40deg,{COLOR_PINK},{COLOR_TEAL})"

		self.playback.play.style["background"] \
			= f"linear-gradient(40deg,{COLOR_BLUE},{COLOR_PURPLE})"

		
		self.playback.volume_label.style["font-size"] = "0.8em"
		
		self.playback.volume_slider.style["width"] = "150px"
		self.playback.volume_slider.style["margin-left"] = "20px"
		self.playback.volume_slider.style["margin-bottom"] = "13px"
		
		self.playback.seek_slider.set_size("90%", "20px")
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
		self.input.field.style["align-self"] = "flex-start"
		
		self.input.submit.style["margin"] = "0px 5px"
		self.input.submit.style["padding"] = "0px 10px"
		
		# Containers:
		root_container = gui.HBox()
		root_container.style.update({"margin-left": "auto", "margin-right":"auto"})
		root_container.style["margin-left"] = "auto"
		root_container.style["margin-right"] = "auto"
		root_container.style["max-width"] = f"{WIDTH}px"
		root_container.style["flex-wrap"] = "wrap"
		
		# LEFT SIDE
		left_container = gui.VBox(width=WIDTH_L)
		left_container.style["margin-top"] = "0.8em"
		left_container.style["align-self"] = "flex-start"
		root_container.append(left_container)
		
		left_container.append(self.logo_image)
		
		left_container.append(self.playback.playing)
		
		playback_container = gui.HBox()
		playback_container.append(self.playback.party)
		playback_container.append(self.playback.previous)
		playback_container.append(self.playback.play)
		playback_container.append(self.playback.next)
		
		volume_container = gui.VBox()
		volume_container.append(self.playback.volume_label)
		volume_container.append(self.playback.volume_slider)
		playback_container.append(volume_container)

		left_container.append(playback_container)
		
		left_container.append(self.playback.seek_slider)
		left_container.append(self.playback.timestamp)
		
		# RIGHT SIDE
		right_container = gui.VBox(width=WIDTH_R)
		right_container.style["margin-top"] = "0.8em"
		right_container.style["align-self"] = "flex-start"
		root_container.append(right_container)
		
		self.input.add_song.style["line-height"] = "1em"
		right_container.append(self.input.add_song)
		
		input_container = gui.HBox(width="100%")
		input_container.style["margin"] = "0px"
		input_container.append(self.input.field)
		input_container.append(self.input.submit)
		right_container.append(input_container)
		
		right_container.append(self.playlist.table)
		
		playlist_button_container = gui.HBox()
		playlist_button_container.append(self.playlist.shuffle)
		playlist_button_container.append(self.playlist.clear)
		playlist_button_container.style["margin-left"] = "auto"
		playlist_button_container.style["margin-right"] = "0.25em"
		playlist_button_container.style["margin-bottom"] = "0.8em"
		right_container.append(playlist_button_container)
		
		return root_container
		
	def main(self):
		self.make_gui_elements()
		container = self.make_gui_container()
		self.mainLoop()
		return container
	def mainLoop(self):
		self.playback_update()
		self.volume_update()
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
		
	# gui updaters:
	@call_as_thread
	def playback_update(self):
		is_playing = api.is_playing()
		self.set_playing(is_playing)

		if is_playing: # update seekbar and timestamp
			try:
				playback_pos = api.get_playback_pos()
			except api.APIError:
				playback_pos = None
			
			if playback_pos:
				slider_pos = playback_pos["current"] / playback_pos["total"] * 100
				current = seconds_to_timestamp(playback_pos["current"])
				total = seconds_to_timestamp(playback_pos["total"])
				
				if self.playback.seek_slider.get_value() != slider_pos:
					self.playback.seek_slider.set_value(slider_pos)
				
				self.playback.timestamp.set_text(f"{current} - {total}")
			else:
				self.playback.timestamp.set_text("--:-- - --:--")
	@call_as_thread
	def volume_update(self):
		volume = api.get_volume()
		if volume > 100:
			volume = 100
		
		if self.playback.volume_slider.get_value() != volume:
			self.playback.volume_slider.set_value(volume)
	@call_as_thread
	def playlist_update(self):
		playlist = api.get_playlist() # json structure
		N = len(playlist)
		
		# update playlist table content:
		table = []
		for playlist_item in playlist:
			name = playlist_item["filename"]
			length = None
			
			if "data" in playlist_item:
				name = playlist_item["data"].get("title", name)
				length = playlist_item["data"].get("duration", length)
			
			table.append([
				playlist_item["index"],
				name,
				seconds_to_timestamp(length) if length else "--:--",
				ICON_UP,
				ICON_DOWN,
				ICON_TRASH,
			])

		self.playlist.table.empty(keep_title=True)
		self.playlist.table.append_from_list(table)

		# styling the new table:
		# for each row element:
		for row_key, playlist_item in zip(self.playlist.table._render_children_list[1:], playlist):
			row_widget = self.playlist.table.get_child(row_key)
			row_widget.set_on_click_listener(self.on_table_row_click, playlist_item)
			
			if playlist_item.get("current", False):
				self.playback.previous.set_enabled(playlist_item.get("index") != 0)
				self.playback.next.set_enabled(playlist_item.get("index") != N-1)
				row_widget.style["background-color"] = COLOR_LIGHT_BLUE
			else:
				row_widget.style["color"] = COLOR_GRAY_DARK
			
			
			# for each item element in this row:
			for item_index, item_key in enumerate(row_widget._render_children_list):
				item_widget = row_widget.get_child(item_key)
				
				if item_index == 1 and "failed" in playlist_item.get("data", {}):
					item_widget.style["width"] = "1.1em"
					item_widget.style["color"] = COLOR_RED
				
				if item_index >= 3:
					item_widget.style["width"] = "1.1em"
					item_widget.style["color"] = COLOR_TEAL
				
				if item_index == 3:
					item_widget.set_on_click_listener(self.on_table_item_move_click, playlist_item, False)
					if playlist_item["index"] == 0:
						item_widget.style["color"] = COLOR_GRAY_LIGHT
				if item_index == 4:
					item_widget.set_on_click_listener(self.on_table_item_move_click, playlist_item, True)
					if playlist_item["index"] == N-1:
						item_widget.style["color"] = COLOR_GRAY_LIGHT
				
				if item_index == 5:
					item_widget.style["color"] = COLOR_RED
					item_widget.set_on_click_listener(self.on_table_item_remove_click, playlist_item)
				#print(index, key, item_widget)
	def set_playing(self, is_playing:bool): # Updates GUI elements
		self.playback.play.set_text(ICON_PAUSE if is_playing else ICON_PLAY)
		self.playback.seek_slider.set_enabled(is_playing)
