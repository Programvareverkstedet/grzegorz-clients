import random, os, time, shutil, sys
from threading import Timer
import remi.gui as gui
from remi import App
from utils import Namespace, call_as_thread, get_youtube_metadata

import api

#globals:
COLOR_BLUE = "rgb(33, 150, 243)"
COLOR_BLUE_SHADOW = "rgba(33, 150, 243, 0.75)"

class MyApp(App):
	def __init__(self, *args):
		res_path = os.path.join(os.path.dirname(__file__), 'res')
		super(MyApp, self).__init__(*args, static_file_path=res_path)

	def main(self):
		container = gui.VBox(width=512)
		container.style["margin-left"] = "auto"
		container.style["margin-right"] = "auto"
		
		#logo:
		container.append(gui.Image('/res/logo.jpg', width=512))
		
		#playback controls
		playbackContainer = gui.HBox()#; container.append(playbackContainer)
		
		self.playback = Namespace()
		for i in ("previous", "play", "next"):
			button = gui.Button(i.capitalize(), margin="5px")
			setattr(self.playback, i, button)
			playbackContainer.append(button)
			button.set_on_click_listener(getattr(self,'playback_%s' % i))
		
		self.playback.playing = gui.Label("Now playing: None")
		self.playback.slider = gui.Slider(0, 0, 100, 1, width="85%", height=20, margin='10px')
		
		container.append(self.playback.playing)
		container.append(playbackContainer)
		container.append(self.playback.slider)
		
		#playlist
		self.playlist = Namespace()
		self.playlist.table = gui.Table(width="100%", margin="10px")
		self.playlist.table.append_from_list([['#', 'Name', "length"]], fill_title=True)
		
		container.append(self.playlist.table)
		
		#input
		container.append(gui.Label("Add songs:"))
		inputContainer = gui.HBox(width=512)
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
		#self.playback.slider.get_value()
		
		self.playback_update()
		self.playlist_update()
		
		
		Timer(0.7, self.mainLoop).start()

	# events:
	@call_as_thread
	def playback_previous(self, widget):
		api.playlist_previous()
	@call_as_thread
	def playback_play(self, widget):# toggle playblack
		if api.is_playing():
			self.playback.play.set_text("Play")
			api.set_playing(False)
		else:
			self.playback.play.set_text("Pause")
			api.set_playing(True)
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

	# playback steps:
	@call_as_thread
	def playback_update(self):
		play_label = "Pause" if api.is_playing() else "Play"
		playback_pos = random.randrange(0,100)
		
		#print(dir(self.playback.play))
		self.playback.play.set_text(play_label)
		self.playback.slider.set_value(playback_pos)
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
