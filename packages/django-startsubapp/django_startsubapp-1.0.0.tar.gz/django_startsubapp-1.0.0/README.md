# django-startsubapp

A Django management command that creates Django apps inside a dedicated `apps/` folder to keep your project structure clean and organized.

## Features

- 🚀 Create Django apps directly inside the `apps/` folder
- 📦 Automatically handles app structure and configuration
- 🔧 Simple command: `python manage.py startsubapp [app_name]`
- 🛡️ Input validation to prevent errors
- ✨ Enhanced user feedback with status messages

## Installation

### Via PyPI

```bash
pip install django-startsubapp
```

### Development Installation

```bash
git clone https://github.com/Saman-naruee/django-startsubapp.git
cd django-startsubapp
pip install -e .
```

## Quick Start

### 1. Add to Django Project

Add `startsubapp` to your Django project's `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps
    'startsubapp',
]
```

### 2. Create a New Sub-App

Run the management command:

```bash
python manage.py startsubapp myapp
```

This will create:
```
myproject/
├── apps/
│   └── myapp/
│       ├── migrations/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests.py
│       ├── views.py
│       └── ...
├── manage.py
└── ...
```

### 3. Update Your Settings

Add the new app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'apps.myapp',  # Note: apps.myapp format
]
```

## Usage

### Command Syntax

```bash
python manage.py startsubapp [app_name]
```

### Example

Create an accounts app:

```bash
python manage.py startsubapp accounts
```

This creates `apps/accounts/` with all necessary Django app files.

## How It Works

1. Creates the `apps/` folder if it doesn't exist
2. Uses Django's built-in `startapp` command to create the app structure
3. Moves the app from the project root into the `apps/` folder
4. Ensures proper `__init__.py` exists in the app directory
5. Automatically configures the app's `apps.py` with the correct path

## Error Handling

The command includes validation for:

- **Invalid app names**: Prevents dots (`.`) in app names
- **Existing apps**: Checks for conflicts before creation
- **File system errors**: Handles file operations safely

Example error message:

```bash
$ python manage.py startsubapp my.app
Error: Dots not allowed in app_name. Use simple name like 'accounts'
```

## Project Structure

The package follows modern Python packaging standards:

```
django-startsubapp/
├── src/
│   └── startsubapp/
│       ├── __init__.py
│       ├── apps.py
│       └── management/
│           └── commands/
│               └── startsubapp.py
├── tests/
│   └── test_basic.py
├── pyproject.toml
├── setup.cfg
├── README.md
├── LICENSE
└── .gitignore
```

## Requirements

- Python 3.8+
- Django 3.0+

## Testing

Run tests with:

```bash
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Saman Naruee**
- Email: samannaruee@gmail.com
- GitHub: [@Saman-naruee](https://github.com/Saman-naruee)

## Support

If you encounter any issues, please open an issue on [GitHub](https://github.com/Saman-naruee/django-startsubapp/issues).

## Changelog

### v1.0.0 (Initial Release)
- Initial release of django-startsubapp
- Basic functionality for creating sub-apps in `apps/` folder
- Full validation and error handling
- PyPI publication
