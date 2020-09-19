from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone
from requests_oauthlib import OAuth2Session

from oauth_client.models import UserToken

User = get_user_model()


def get_state_session_key(codename: str) -> str:
    return f'oauth2_{codename}_state'


def get_authorization_url(codename: str, request: HttpRequest = None) -> str:
    provider = settings.OAUTH2_PROVIDERS[codename]
    oauth = OAuth2Session(client_id=provider['client_id'])
    url, state = oauth.authorization_url(provider['authorization_url'])
    if request is not None and hasattr(request, 'session'):
        request.session[get_state_session_key(codename)] = state
    return url


def get_token(user: User, provider: str) -> UserToken:
    user_token = UserToken.objects.get(user=user, provider=provider)
    threshold = timezone.now() + timedelta(days=1)
    if user_token.expires_at < threshold:
        user_token.refresh()
    return user_token
