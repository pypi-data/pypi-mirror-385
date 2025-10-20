# django-sso-client-oauth

**django-sso-client-oauth** is a reusable Django app that simplifies the integration of Single Sign-On (SSO) functionality into your Django projects. It is designed to work seamlessly with Django-based applications and supports flexible configurations for connecting to an SSO provider.

> **Note**: This package is currently in **beta**. Features and APIs may change in future releases.

## Features

- **SSO Integration**: Easily integrate Single Sign-On functionality into your Django project.
- **Customizable Settings**: Configure the SSO client to work with your specific SSO provider.
- **Token Management**: Handle authentication tokens securely.
- **Django Compatibility**: Works with Django 3.2+.

## Installation

Install the package using pip:

```bash
pip install django-sso-client-oauth
```

Alternatively, for development purposes, you can install it in editable mode:

```bash
pip install -e .
```

To uninstall the package:

```bash
pip uninstall django-sso-client-oauth
```

## Quickstart

1. Add `django_sso_client_oauth` to your `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...,
       "django_sso_client_oauth",
   ]
   ```

2. Configure the SSO client settings in your Django project:

   ```python
   SSO_CLIENT = {
        "BASE_URL": "https://sso.example.com",
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "REDIRECT_URI": "https://your-app.com/sso/callback",
        "SCOPE": ["openid", "read", "write"],
        "LOGIN_REDIRECT": "/",
        "LOGIN_ERROR_REDIRECT": "/login/",
        "USERINFO_ENDPOINT": "/api/auth/me/",
        "AUTO_CREATE_USER": True,
        "SYNC_PERMISSIONS": True,
   }
   ```

3. Include the SSO client URLs in your `urls.py`:

   ```python
   from django.urls import path, include

   urlpatterns = [
       ...,
       path("sso/", include("django_sso_client_oauth.urls")),
   ]
   ```

4. Run your Django server:

   ```bash
   python manage.py runserver
   ```

## Usage

### Redirecting Users to the SSO Provider

To initiate the SSO flow, redirect users to the SSO provider's login page. This can be done using the utility functions provided in the `django_sso_client_oauth.utils` module.

### Handling SSO Callbacks

The app includes built-in views to handle SSO callbacks and exchange authorization codes for tokens. These views are automatically included when you add the app's URLs to your project.

### Customizing Behavior

You can customize the behavior of the SSO client by overriding the default settings or extending the provided views and utilities.

## Development

To contribute to this project:

1. Clone the repository.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Disclaimer

This package is in **beta**. Use it in production environments with caution, and report any issues you encounter.
