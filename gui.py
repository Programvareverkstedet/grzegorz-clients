import random, os, time, shutil, sys
from threading import Timer
import remi.gui as gui
from remi import App
from utils import Namespace, call_as_thread, get_youtube_metadata

import api

#globals:
COLOR_BLUE = "rgb(33, 150, 243)"
COLOR_BLUE_SHADOW = "rgba(33, 150, 243, 0.75)"
WIDTH = 512

class MyApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(__file__), 'res')
		super(MyApp, self).__init__(*args, static_file_path=res_path)

	def main(self):
		container = gui.VBox(width=WIDTH)
		container.style.update({"margin-left": "auto", "margin-right":"auto"})
		
		#logo:
		container.append(gui.Image('/res/logo.png', width=WIDTH))
		
		#playback controls
		self.playback = Namespace()
		
		self.playback.playing = gui.Label("Now playing: None")# (TODO): update this
		
		self.playback.previous, self.playback.play, self.playback.next \
			= map(lambda x: gui.Button(f'<i class="fas fa-{x}"></i>', margin="3px", width="2.8em"), 
			("step-backward", "play", "step-forward"))
		self.playback.previous.set_on_click_listener(self.playback_previous)
		self.playback.play.set_on_click_listener(self.playback_play)
		self.playback.next.set_on_click_listener(self.playback_next)
		
		self.playback.volume_label = gui.Label("Volume:")
		self.playback.volume_label.style["font-size"] = "0.8em"
		self.playback.volume_slider = gui.Slider(100, 0, 100, 1, width="150px")
		self.playback.volume_slider \
			.style.update({"margin-left": "20px", "margin-bottom":"13px"})
		self.playback.volume_slider.set_oninput_listener(self.change_volume)
		
		self.playback.seek_slider = gui.Slider(0, 0, 100, 1, width="85%", height=20, margin='10px')
		self.playback.seek_slider.set_oninput_listener(self.change_seek)
		
		container.append(self.playback.playing)
		
		playbackContainer = gui.HBox()
		playbackContainer.append(self.playback.previous)
		playbackContainer.append(self.playback.play)
		playbackContainer.append(self.playback.next)
		volume_container = gui.VBox()
		volume_container.append(self.playback.volume_label)
		volume_container.append(self.playback.volume_slider)
		playbackContainer.append(volume_container)
		container.append(playbackContainer)
		container.append(self.playback.seek_slider)
		
		#playlist
		self.playlist = Namespace()
		self.playlist.table = gui.Table(width="100%", margin="10px")
		self.playlist.table.append_from_list([['#', 'Name', "length"]], fill_title=True)
		
		container.append(self.playlist.table)
		
		#input
		container.append(gui.Label("Add songs:"))
		inputContainer = gui.HBox(width=WIDTH)
		self.input = Namespace()
		self.input.field = gui.TextInput(single_line=True, height="20px", margin="5px")
		self.input.field.style["border"]     = "1px solid %s" % COLOR_BLUE
		self.input.field.style["box-shadow"] = "0px 0px 5px 0px %s" % COLOR_BLUE_SHADOW
		self.input.submit = gui.Button("Submit!", margin="5px")
		self.input.field.set_on_enter_listener(self.input_submit)
		self.input.submit.set_on_click_listener(self.input_submit)
		
		inputContainer.append(self.input.field)
		inputContainer.append(self.input.submit)
		container.append(inputContainer)
		
		#return the container
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
		
		# (TODO):
		# title, length = utils.get_youtube_metadata(value)
		api.load_path(value)
	@call_as_thread
	def change_seek(self, widget, value):
		api.seek_percent(value)
	@call_as_thread
	def change_volume(self, widget, value):
		api.set_volume(value)

	# playback steps:
	@call_as_thread
	def playback_update(self, times_called=[0]):
		is_playing = api.is_playing()
		self.set_playing(is_playing)

		if is_playing:
			playback_pos = api.get_playback_pos()
			playback_pos = playback_pos["current"] / playback_pos["total"] * 100
			if self.playback.seek_slider.get_value() != playback_pos:
				self.playback.seek_slider.set_value(playback_pos)
		
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
		
		table = []
		for item in playlist:
			table.append([
				item["index"],
				item["filename"],
				"05:00" + ("#"*("current" in item))
			])

		self.playlist.table.empty(keep_title=True)
		self.playlist.table.append_from_list(table)
	
	#helpers
	def set_playing(self, is_playing:bool):
		self.playback.play.set_text('<i class="fas fa-pause"></i>' if is_playing else '<i class="fas fa-play"></i>')
		self.playback.seek_slider.set_enabled(is_playing)
		
