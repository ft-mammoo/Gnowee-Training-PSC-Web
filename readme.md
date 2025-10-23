
# Gnowee PSC Training Web

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

Lightweight Django web project used for the Gnowee PSC training exercises and demos. The Django app lives in the `psc_training_web` package and this repository contains the minimal project wrapper to run and develop locally.

## Contents

- `psc_training_web/` — Django project package (settings, urls, wsgi/asgi)
- `manage.py` — Django management script
- `LICENSE` — MIT license for the repository

## Requirements

- Python 3.10+ (use a virtual environment)
- pip
- Recommended: a virtualenv or venv

## Quick start (development)

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

If this project has a requirements file, install it. If not, install Django manually:

```bash
# if you have requirements.txt
pip install -r requirements.txt

# or, install Django (example)
pip install Django
```

3. Run migrations and start the development server

```bash
python manage.py migrate
python manage.py runserver
```

The site will be available at http://127.0.0.1:8000/ by default.

## Common tasks

- Create a new Django app:

```bash
python manage.py startapp myapp
```

- Create a superuser:

```bash
python manage.py createsuperuser
```

- Run tests:

```bash
python manage.py test
```

## Configuration

Edit settings in `psc_training_web/settings.py`. For production deployments, ensure you set `DEBUG = False`, configure `ALLOWED_HOSTS`, database settings, static files, and secret key management via environment variables.

## Contributing

Contributions are welcome. Open issues or submit pull requests. Keep changes small and focused, and include tests where applicable.

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

