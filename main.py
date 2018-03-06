#!/usr/bin/env python3
import os, sys
from remi import start
from threading import Timer
from grzegorz_clients import api, remi_ui


# config must be a object with the attributes seen in default_config.py:
def main(config):
	start_kwargs = {}
	for attr in ("address", "port", "host_name", "websocket_port",
			"username", "password", "standalone", "start_browser",
			"multiple_instance", "enable_file_cache"):
		assert hasattr(config, attr), f"Config has no attribute {attr!r}!"
		start_kwargs[attr] = getattr(config, attr)
	assert hasattr(config, "api_base"), f"Config has no attribute 'api_base'!"
	
	if config.standalone:#it's picky :(
		start_kwargs = {"standalone":config.standalone}
	
	# start the webserver:
	api.set_endpoint(config.api_base)
	start(
		remi_ui.RemiApp,
		title = "Gregorz",
		**start_kwargs
		)

if __name__ == "__main__":
	if "--no-volume" in sys.argv[1:]:
		print("Keeping volume down")
		def keep_volume_down():
			api.set_volume(0)
			Timer(5, keep_volume_down).start()
		Timer(5, keep_volume_down).start()
	
	if not os.path.exists("config.py"):
		shutil.copy("default_config.py", "config.py")
	import config

	main(config)
