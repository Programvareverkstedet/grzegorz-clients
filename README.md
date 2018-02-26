# Gregorz webUI

A simple webui to interface with the [Grzegorz API](https://github.com/Programvareverkstedet/grzegorz)

## How to run this

First of we need to install any needed dependencies. If you want to, you may do so in a virtual environment.

To install the needed dependencies, run this with sufficient rights (as root?):

```
pip install -r requirements.txt
```

Now, make a copy of `default_config.py` named `config.py`, and make any changes you see fit. Here is a description of each field:

* `host` - The interace you want to listen to
* `port` - The port to listen to
* `start_browser` - Whether to open a window in the defualt browser of the interface when starting
* `multiple_instance` - Whether to handle each client induvidually or with a single instance

When finished, start the server with:

```
python3 main.py
```

## License

Licensed under BSD 3 clause, see the file LICENSE for more details

This uses the library REMI by dddomodossola, which is licensed under apache2.
This license may be read [over here](https://choosealicense.com/licenses/apache-2.0/)
