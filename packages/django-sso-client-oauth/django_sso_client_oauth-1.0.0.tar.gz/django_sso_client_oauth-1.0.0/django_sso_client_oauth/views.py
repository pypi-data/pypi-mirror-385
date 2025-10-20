from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.http import HttpRequest, HttpResponse
from requests_oauthlib import OAuth2Session
from .settings import get_sso_config
from .utils import get_or_create_user
import logging

logger = logging.getLogger(__name__)

def login(request: HttpRequest) -> HttpResponse:
    """Initiate OAuth2 Authorization Code flow by redirecting the user to the SSO provider."""
    config = get_sso_config()
    oauth = OAuth2Session(
        client_id=config["CLIENT_ID"],
        redirect_uri=config["REDIRECT_URI"],
        scope=config["SCOPE"],
    )
    authorization_url, state = oauth.authorization_url(f"{config['BASE_URL']}/o/authorize/")
    request.session["oauth_state"] = state
    return redirect(authorization_url)


def callback(request: HttpRequest) -> HttpResponse:
    """Handle the OAuth2 callback, exchange the code for tokens, and authenticate the user."""
    config = get_sso_config()
    state = request.session.get("oauth_state")
    if not state:
        return redirect(f"{config['LOGIN_ERROR_REDIRECT']}?error=missing_state")

    oauth = OAuth2Session(
        client_id=config["CLIENT_ID"],
        redirect_uri=config["REDIRECT_URI"],
        state=state,
    )
    try:
        token = oauth.fetch_token(
            f"{config['BASE_URL']}/o/token/",
            client_secret=config["CLIENT_SECRET"],
            authorization_response=request.build_absolute_uri(),
        )
        userinfo_url = config["USERINFO_ENDPOINT"]
        if not userinfo_url.startswith("http"):
            userinfo_url = f"{config['BASE_URL']}{userinfo_url}"
        resp = oauth.get(userinfo_url)
        user_info = resp.json()

        user = get_or_create_user(user_info, config)
        auth_login(request, user)
        return redirect(config["LOGIN_REDIRECT"])
    except Exception as e:
        logger.error("SSO callback failed: %s", e, exc_info=True)
        return redirect(f"{config['LOGIN_ERROR_REDIRECT']}?error=sso_failed")
