from django.conf import settings

DEFAULTS = {
    "BASE_URL": None,
    "CLIENT_ID": None,
    "CLIENT_SECRET": None,
    "REDIRECT_URI": None,
    "SCOPE": ["openid", "read", "write"],
    "LOGIN_REDIRECT": "/",
    "LOGIN_ERROR_REDIRECT": "/login/",
    "USERINFO_ENDPOINT": "/api/auth/me/",
    "AUTO_CREATE_USER": True,
    "SYNC_PERMISSIONS": True,
}

def get_sso_config() -> dict:
    """Retrieve merged SSO configuration combining defaults with user overrides."""
    return {**DEFAULTS, **getattr(settings, "SSO_CONFIG", {})}
