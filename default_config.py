address = "0.0.0.0" # network interface ip
port = 8081 # http listen port

#Link to where your Grzegorz API is hosted
api_base = "http://localhost:8080/api"

# a string containing the host name or remote ip address that allows to access to your app.
host_name = None
# websocket port
websocket_port = 0 # 0 means random

# In order to limit the remote access to your interface you
# can define a username and password. It probably uses http basic-auth
username = None
password = None

# Open a PyWebView window instead of using the browser. This requires pywebview to be installed. 
# This will negate all other options
standalone = False

# Defines whether the browser should be opened automatically at startup
start_browser = True 

# Multipe instance. If True, multiple clients that connects to your script has different App instances
multiple_instance = False

# Cache files in "res" folder
enable_file_cache = True
