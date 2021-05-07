import logging
from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.module_loading import import_string
from django.views import View
from requests_oauthlib import OAuth2Session

from .models import UserToken, Provider, Integration
from .utils import get_token_url, get_state_session_key, get_redirect_url

OAUTH_REGISTER_NEW = getattr(settings, 'OAUTH_REGISTER_NEW')

logger = logging.getLogger('oauth_client')


class OAuth2CallbackView(View):

    def get(self, request, *args, **kwargs):
        self.provider = self.get_provider()
        self.endpoint = self.get_endpoint()

        self.integration, _ = Integration.objects.get_or_create(
            endpoint=self.endpoint)

        session_key = get_state_session_key(str(self.provider.id))
        state = request.session.get(session_key, None)
        redirect_url = get_redirect_url(self.provider)
        oauth = OAuth2Session(client_id=self.provider.client_id, state=state,
                              redirect_uri=redirect_url)

        authorization_response = self.request.build_absolute_uri().replace(
            'http://', 'https://')  # always use https, they said. mwahaha!

        token_url = get_token_url(self.provider, endpoint=self.endpoint)

        token = oauth.fetch_token(
            token_url=token_url,
            client_secret=self.provider.client_secret,
            authorization_response=authorization_response)

        user = request.user
        if user.is_anonymous:
            if OAUTH_REGISTER_NEW:
                # FIXME оставлено для совместимости
                try:
                    provider_config = settings.OAUTH2_PROVIDERS[self.provider.preset]
                    username_gen = provider_config['username_gen']
                    username_gen = import_string(username_gen)
                except (KeyError, AttributeError, TypeError):
                    raise Http404()

                username = username_gen(token, self.provider, request)
                user = User.objects.filter(username=username).first()
                if not user:
                    logger.debug(f'Registering new user: {username}')
                    user = User.objects.create_user(username=username)
            else:
                raise Http404

        expires_at = token.get('expires_at', None)
        if expires_at:
            expires_at = datetime.fromtimestamp(expires_at)
        self.user_token, created = UserToken.objects.update_or_create(
            user=user,
            provider=self.provider,
            integration=self.integration,
            defaults={
                'scope': token.scope or '',
                'expires_at': expires_at,
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
            })

        request = self.set_request_user(request, user)
        assert request.user == self.request.user
        self.process()
        return self.process_response(self.integration)

    def get_provider(self) -> Provider:
        provider_id = self.kwargs.get('provider_id', '')
        if provider_id:
            return get_object_or_404(Provider, id=provider_id)
        provider_slug = self.kwargs.get('provider_slug', '')
        if provider_slug:
            return get_object_or_404(Provider, slug=provider_slug)
        raise Http404()

    def get_endpoint(self) -> str:
        endpoint = ''
        if self.provider.preset == Provider.Preset.BX24:
            endpoint = self.request.GET['DOMAIN']
        elif self.provider.preset == Provider.Preset.AMOCRM:
            endpoint = urlparse(self.request.GET['referer']).netloc
        return endpoint

    def set_request_user(self, request: HttpRequest,
                         user: User) -> HttpRequest:
        if request.user != user:
            logout(request)
        if not request.user.is_authenticated:
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
        return request

    def process(self):
        """
        Хук для запуска какой-нибудь дополнительной обработки.
        """
        pass

    def process_response(self, integration: Integration) -> HttpResponse:
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        # FIXME оставлено для совместимости
        try:
            provider_config = settings.OAUTH2_PROVIDERS[self.provider.preset]
            success_url = provider_config['success_url']
            success_url = import_string(success_url)
        except (KeyError, AttributeError, TypeError):
            raise Http404()

        success_url = success_url(self.user_token)
        return success_url
