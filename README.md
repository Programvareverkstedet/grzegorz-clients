# Gregorz Clients
<img align="right" width="250" src="grzegorz_clients/res/logo.png">

A set of simple API endpoints and ready-to-go clients to interface with the [Grzegorz API](https://github.com/Programvareverkstedet/grzegorz)

#### Working clients:
*  A webUI client made with REMI
*  CLI client

#### Planned future clients:
* WebExtensions browser extension


## How to run this

    pip install --user git+https://github.com/Programvareverkstedet/grzegorz_clients.git#master

### cli

    grzegorzctl

### webui

As the user intended to run the server:

    pip install --user git+https://github.com/Programvareverkstedet/grzegorz_clients.git#master
    grzegorz-webui --host-name 0.0.0.0 --port 80

It's rather insecure and could use a reverse proxy and some whitelisting. ;)


## Making the webui run on boot

Modify and copy the files in `dist` to `$HOME/.config/systemd/user`, then run the following commands as the user intended to run the server:

	$ systemctl --user enable grzegorz_webui.service
	$ systemctl --user start grzegorz_webui.service


## Development

Setup virtual environment and running the server:

    poetry install
    grzegorz-webui --no-volume

If you also run a local instance of the Grzegorz API:

    grzegorz-webui --api-base http://localhost:8000/api

If you plan on making changes to the code, preferably install [`entr`](http://entrproject.org/) and use the supplied script `dev.sh`.
It will restart the server every time you change any of the files tracked by git.

    ./dev.sh --api-base http://localhost:8000/api


## License

Licensed under BSD 3 clause, see the file LICENSE for more details

This uses the library REMI by dddomodossola, which is licensed under apache2.
This license may be read [over here](https://choosealicense.com/licenses/apache-2.0/)
