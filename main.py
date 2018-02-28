#!/usr/bin/env python3
from remi import start
import os
import api
import gui

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
	api.BASE_URL = config.api_base
	start(
		gui.MyApp,
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
