# edupsyadmin

edupsyadmin provides tools to help school psychologists with their
documentation

## Basic Setup

You can install the CLI using pip or
[uv](https://docs.astral.sh/uv/getting-started/installation).

Install with uv:

    $ uv tool install edupsyadmin

You may get a warning that the `bin` directory is not on your environment path.
If that is the case, copy the path from the warning and add it directory to
your **environment path** permanently or just for the current session.

Run the application:

    $ edupsyadmin --help

## Getting started

### keyring backend

edupsyadmin uses `keyring` to store the encryption credentials. `keyring` has
several backends.

- On Windows the default is the Windows Credential Manager (German:
  Anmeldeinformationsverwaltung).

- On macOS, the default is Keychain (German: Schlüsselbund)

Those default keyring backends unlock when you login to your machine. You may
want to install a backend that requires separate unlocking:
<https://keyring.readthedocs.io/en/latest/#third-party-backends>

### Modify the config file

First, you have to update the config file with your data using the config
editor TUI:

`edupsyadmin edit_config`

## The database

The information you enter, is stored in an SQLite database with the fields
described [in the documentation for
edupsyadmin](https://edupsyadmin.readthedocs.io/en/latest/clients_model.html#)

## Examples

Get information about the path to the config file and the path to the database:

    $ edupsyadmin info

Add a client interactively:

    $ edupsyadmin new_client

Add a client to the database from a Webuntis csv export:

    $ edupsyadmin new_client --csv ./path/to/your/file.csv --name "short_name_of_client"

Change values for the database entry with `client_id=42` interactively:

    $ edupsyadmin set_client 42

Change values for the database entry with `client_id=42` from the commandline:

```
$ edupsyadmin set_client 42 \
  --key_value_pairs \
  "nta_font=1" \
  "nta_zeitv_vieltext=20" \
  "nos_rs=0" \
  "lrst_diagnosis=iLst"
```

See an overview of all clients in the database:

    $ edupsyadmin get_clients

Fill a PDF form for the database entry with `client_id=42`:

    $ edupsyadmin create_documentation 42 --form_paths ./path/to/your/file.pdf

Fill all files that belong to the form_set `lrst` (as defined in the
config.yml) with the data for `client_id=42`:

    $ edupsyadmin create_documentation 42 --form_set lrst

## Development

Create the development enviroment:

    $ uv v
    $ uv pip install -e .

Run the test suite:

    $ .venv/bin/python -m pytest -v -n auto --cov=src test/

Build documentation:

    $ .venv/bin/python -m sphinx -M html docs docs/_build

## License

This project is licensed under the terms of the MIT License. Portions of this
project are derived from the python application project cookiecutter template
by Michael Klatt, which is also licensed under the MIT license. See the
LICENSE.txt file for details.
