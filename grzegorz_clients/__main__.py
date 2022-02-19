#!/usr/bin/env python3
from remi import start
from threading import Timer
import typer
from . import api, remi_ui


cli = typer.Typer()

@cli.command()
def main(
		address           : str  = "localhost", # network interface ip
		port              : int  = 8001,        # http listen port
		api_base          : str  = "https://brzeczyszczykiewicz.pvv.ntnu.no/api", #Link to where your Grzegorz API is hosted

		host_name         : str  = None, # a string containing the host name or remote ip address that allows to access to your app.
		websocket_port    : int  = 0,    # websocket port, 0 makes it random

		# In order to limit the remote access to your interface you
		# can define a username and password. It probably uses http basic-auth
		username          : str  = None,
		password          : str  = None,

		# Open a PyWebView window instead of using the browser. This requires pywebview to be installed.
		# This will negate all other options
		standalone        : bool = False,

		start_browser     : bool = False, # Defines whether the browser should be opened automatically at startup
		multiple_instance : bool = False, # Multipe instance. If True, multiple clients that connects to your script has different App instances
		enable_file_cache : bool = True,  # Cache files in "res" folder

		# set to false to force the volume to be zero.
		# Great for remote development!
		volume            : bool = True,
		):

	if not volume:
		print("Keeping volume down")
		def keep_volume_down():
			api.set_volume(0)
			Timer(5, keep_volume_down).start()
		Timer(5, keep_volume_down).start()


	api.set_endpoint(api_base)

	# start the webserver:

	if standalone: # it's picky :(
		start(
			remi_ui.RemiApp,
			title = "Gregorz",
			standalone = standalone
		)
	else:
		start(
			remi_ui.RemiApp,
			title             = "Gregorz",
			address           = address,
			port              = port,
			host_name         = host_name,
			websocket_port    = websocket_port,
			username          = username,
			password          = password,
			standalone        = standalone,
			start_browser     = start_browser,
			multiple_instance = multiple_instance,
			enable_file_cache = enable_file_cache,

		)


if __name__ == "__main__":
	cli()
