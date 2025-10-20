# Enventory

**Enventory** is a lightweight Python utility that acts as a thin wrapper around [`python-dotenv`](https://pypi.org/project/python-dotenv/), making it easier to load and retrieve environment variables from `.env` files with optional type casting, defaults, and required flags.

---

## Features

* Wraps `python-dotenv` to simplify loading `.env` files.
* Retrieve environment variables with default values, type casting, and required checks.
* Helper functions for casting strings to booleans or lists.
* Raises clear errors when environment files or required variables are missing.
* Compatible with Python 3.8+.

---

## Installation

Once published to PyPI, you can install Enventory via pip:

```bash
pip install enventory
```

Or for local development:

```bash
git clone https://github.com/yourusername/enventory.git
cd enventory
pip install -e .
```

Note: Enventory requires `python-dotenv` as a dependency.

---

## Usage

### Load Environment Variables

```python
from enventory import loadenv

# Load the default .env file from cwd or parent paths
loadenv()

# Load a specific env file from a base directory
from pathlib import Path
loadenv(base=Path("/path/to/project"), name=".env.production")
```

### Retrieve Environment Variables

```python
from enventory import getenv, to_boolean, to_list

# Get a variable with optional default
db_host = getenv("DB_HOST", default="localhost")

# Get a required variable (raises ValueError if missing)
secret_key = getenv("SECRET_KEY", required=True)

# Cast a variable to boolean
debug_mode = getenv("DEBUG", default="False", cast=to_boolean)

# Cast a comma-separated variable to a list
allowed_hosts = getenv("ALLOWED_HOSTS", default="", cast=to_list)
```

### Helper Functions

```python
from enventory import to_boolean, to_list

to_boolean("yes")  # True
to_boolean("0")    # False

to_list("a,b,c")   # ['a', 'b', 'c']
to_list("a;b;c", separator=";")  # ['a', 'b', 'c']
```

---

## Error Handling

* `EnvNotFoundError` is raised if `loadenv` cannot find a `.env` file.
* `ValueError` is raised by `getenv` if a required environment variable is missing.

---

## Project Structure

```
enventory/
├── setup.py
├── pyproject.toml
├── README.md
└── enventory/
    ├── __init__.py  # exposes env.py
    └── env.py       # main environment utility
```

---

## Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes
4. Submit a pull request

---

## License

MIT License © Your Name

---

## Dependencies

* [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Compatibility

* Python 3.8 and above
