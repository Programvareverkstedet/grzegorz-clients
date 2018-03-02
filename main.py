#!/usr/bin/env python3
import os
from remi import start
from grzegorz_clients import api, gui


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
		gui.MyApp,
		title = "Gregorz",
		**start_kwargs
		)

if __name__ == "__main__":
	if not os.path.exists("config.py"):
		shutil.copy("default_config.py", "config.py")
	import config
	main(config)
