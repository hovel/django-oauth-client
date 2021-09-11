from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from requests_oauthlib import OAuth2Session
from oauth_client.exceptions import LockIntegrationError

from .models import UserToken, Provider, Integration

User = get_user_model()


def get_token_url(provider: Provider, endpoint: str = None) -> str:
    # FIXME оставлено для совместимости
    try:
        provider_config = settings.OAUTH2_PROVIDERS[provider.preset]
        token_url = provider_config['token_url']
        if callable(token_url):
            token_url = token_url(endpoint)
    except (KeyError, AttributeError, TypeError):
        token_url = provider.token_url
    return token_url


def get_redirect_url(provider: Provider) -> Optional[str]:
    # FIXME оставлено для совместимости
    try:
        provider_config = settings.OAUTH2_PROVIDERS[provider.preset]
        redirect_uri = provider_config['redirect_uri']
        return redirect_uri
    except (KeyError, AttributeError, TypeError):
        return None


def get_state_session_key(codename: str) -> str:
    return f'oauth2_{codename}_state'


def get_authorization_url(codename: str, request: HttpRequest = None) -> str:
    # FIXME оставлено для совместимости
    provider = settings.OAUTH2_PROVIDERS[codename]
    oauth = OAuth2Session(client_id=provider['client_id'])
    url, state = oauth.authorization_url(provider['authorization_url'])
    if request is not None and hasattr(request, 'session'):
        request.session[get_state_session_key(codename)] = state
    return url


def get_token(user: User, provider: str) -> UserToken:
    # FIXME оставлено для совместимости
    user_token = UserToken.objects.get(user=user, provider__preset=provider)
    threshold = timezone.now() + timedelta(days=1)
    if user_token.expires_at < threshold:
        user_token.refresh()
    return user_token


def lock_integration(integration: Integration) -> bool:
    ready = Q(install_start__isnull=True,
              install_finish__isnull=True)
    stale = Q(install_start__lt=timezone.now() - timedelta(minutes=10),
              install_finish__isnull=True)
    installed = Q(install_start__isnull=False,
                  install_finish__isnull=False)
    locked = Integration.objects \
        .filter(ready | stale | installed, id=integration.id) \
        .update(install_start=timezone.now(), install_finish=None)
    if not bool(locked):
        raise LockIntegrationError
    return bool(locked)


def unlock_integration(integration: Integration):
    Integration.objects \
        .filter(id=integration.id) \
        .update(install_finish=timezone.now())
