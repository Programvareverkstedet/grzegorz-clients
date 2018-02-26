#!/usr/bin/env python3
import random, os, time, shutil, sys
from threading import Timer
import remi.gui as gui
from remi import start, App
from utils import Namespace

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
		
		self.playlist.queue = []#[i] = [source, name, length]
		
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
		
		
		self.playlist.table.empty(keep_title=True)
		self.playlist.table.append_from_list(self.playlist_update())
		
		Timer(0.7, self.mainLoop).start()

	# events:
	def playback_previous(self, widget): pass
	def playback_play(self, widget):# toggle playblack
		pass
	def playback_next(self, widget):
		source, name, length = self.playlist.queue.pop(0)
		
		pass
	def input_submit(self, widget, value=None):
		if not value:
			value = self.input.field.get_text()
		self.input.field.set_text("")
		
		title, length =  get_youtube_metadata(value)
		
		self.playlist.queue.append([value, title, length])
		
	# playback steps:
	def playback_update(self):
		#talk to mpv, see wether the song is being played still
		if 0:#if done:
			self.playback_next()
			self.playback.slider.set_value(0)
		else:
			self.playback.slider.set_value(100)
		
		return
	def playlist_update(self):
		#out = [['#', 'Name', "length"]]
		out = []
		for i, (source, name, length) in enumerate(self.playlist.queue):
			out.append([str(i+1), name, length])
		
		return out


# config must be a object with the attributes::
#	config.host: str
#	config.port: str
#	config.start_browser: bool
#	config.multiple_instance: bool
def main(config):
	assert hasattr(config, "host")
	assert hasattr(config, "port")
	assert hasattr(config, "start_browser")
	assert hasattr(config, "multiple_instance")
	
	# start the webserver:
	start(
		MyApp,
		title = "Gregorz",
		address = config.host,
		port = config.port,
		start_browser = config.start_browser,
		multiple_instance = config.multiple_instance,
		enable_file_cache = True
		)

if __name__ == "__main__":
	if not os.path.exists("config.py"):
		shutil.copy("default_config.py", "config.py")
	import config
	main(config)
