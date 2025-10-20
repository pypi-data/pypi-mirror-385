from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from typing import Dict, Any

def get_or_create_user(user_info: Dict[str, Any], config: Dict[str, Any]):
    """
    Create or update a Django user based on the user info payload from the SSO provider.
    """
    User = get_user_model()
    username = user_info.get("username") or user_info.get("email")
    if not username:
        raise ValueError("User info missing username/email field.")

    user, created = User.objects.get_or_create(username=username)

    for key, value in user_info.items():
        if key not in ["id", "permissions", "groups"] and hasattr(user, key):
            setattr(user, key, value)
    user.save()

    if config.get("SYNC_PERMISSIONS") and "permissions" in user_info:
        user.user_permissions.clear()
        for perm_data in user_info["permissions"]:
            codename = perm_data.get("codename") if isinstance(perm_data, dict) else perm_data
            if codename:
                perm = Permission.objects.filter(codename=codename).first()
                if perm:
                    user.user_permissions.add(perm)

    return user
