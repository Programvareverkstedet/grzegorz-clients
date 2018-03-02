# Gregorz webUI
<img align="right" width="250" src="grzegorz_clients/res/logo.png">

A simple webui to interface with the [Grzegorz API](https://github.com/Programvareverkstedet/grzegorz)


## How to run this

First of we need to install any needed dependencies. If you want to, you may do so in a virtual environment.

To install the needed dependencies, run this with sufficient rights (as root?):

```
pip install -r requirements.txt
```

Now, make a copy of `default_config.py` named `config.py`, and make any changes you see fit. Each field should be described there

When finished, run the server with:

```
python3 main.py
```

## License

Licensed under BSD 3 clause, see the file LICENSE for more details

This uses the library REMI by dddomodossola, which is licensed under apache2.
This license may be read [over here](https://choosealicense.com/licenses/apache-2.0/)
