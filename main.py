#!/usr/bin/env python3
from remi import start
import os
import api
import gui

# config must be a object with the attributes seen in default_config.py:
def main(config):
	start_kwargs = {}
	for attr in ("address", "port", "hostname", "websocket_port",
			"username", "password", "standalone", "start_browser",
			"multiple_instance", "enable_file_cache"):
		assert hasattr(config, attr), f"Config has no attribute {attr!r}!"
		start_kwargs[attr] = getattr(config, attr)
	assert hasattr(config, "api_base"), f"Config has no attribute 'api_base'!"
	
	if "standalone" in start_kwargs:
		#Why must the standalone client be so picky?
		for illega_attr in ("address", "port", "hostname", "websocket_port",
				"username", "password", "start_browser", "multiple_instance",
				"enable_file_cache"):
			del start_kwargs[illega_attr]
	
	
	# start the webserver:
	api.BASE_URL = config.api_base
	start(
		gui.MyApp,
		title = "Gregorz",
		**start_kwargs
		)

if __name__ == "__main__":
	if not os.path.exists("config.py"):
		shutil.copy("default_config.py", "config.py")
	import config
	main(config)
