# Gregorz Clients
<img align="right" width="250" src="grzegorz_clients/res/logo.png">

A set of simple API endpoints and ready-to-go clients to interface with the [Grzegorz API](https://github.com/Programvareverkstedet/grzegorz)

#### Working clients:
*  A webUI client made with REMI

#### Planned future clients:
* CLI client
* WebExtensions browser extension


## How to run this

First of we need to install any needed dependencies. If you want to, you may do so in a virtual environment.

To install the needed dependencies, run this with sufficient rights (as root?):

    pip install -r requirements.txt

Now, make a copy of `default_config.py` named `config.py`, and make any changes you see fit. Each field should be described in the file.

When finished, run the server with:

    python3 main.py

## Making the webui run on boot

Copy the files in the folder dist into $HOME/.config/systemd/user and run the following commands as the user intended to run the server:

	$ systemctl --user enable grzegorz_webui.service
	$ systemctl --user start grzegorz_webui.service


## Developing on this

If you plan on making changes to the code, i advice you to install [`entr`](http://entrproject.org/) and use the supplied script `dev.sh`.
It will restart the server everytime you write a change to any of the .py files in the project.


## License

Licensed under BSD 3 clause, see the file LICENSE for more details

This uses the library REMI by dddomodossola, which is licensed under apache2.
This license may be read [over here](https://choosealicense.com/licenses/apache-2.0/)
