from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.views import View
from requests_oauthlib import OAuth2Session

from oauth_client.models import UserToken
from oauth_client.utils import get_state_session_key
from .utils import get_token_url


class OAuth2CallbackView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        codename = kwargs['codename']

        try:
            provider = settings.OAUTH2_PROVIDERS[codename]
        except KeyError:
            raise Http404()

        state = request.session.get(get_state_session_key(codename), None)

        oauth = OAuth2Session(
            client_id=provider['client_id'],
            state=state, redirect_uri=provider.get('redirect_uri'))

        authorization_response = self.request.build_absolute_uri().replace(
            'http://', 'https://')  # always use https, they said. mwahaha!

        token_url = get_token_url(provider, request)
        kwgs = provider.get('addional_requests_kwargs', {})
        token = oauth.fetch_token(
            token_url=token_url,
            client_secret=provider['client_secret'],
            authorization_response=authorization_response)

        try:
            user_token = UserToken.objects.get(user=request.user,
                                               provider=codename)
        except UserToken.DoesNotExist:
            user_token = UserToken(user=request.user, provider=codename)

        if 'endpoint' in provider:
            user_token.endpoint = provider['endpoint'](request)

        user_token.token = token
        user_token.save()

        return redirect(self.get_success_url(user_token))

    def get_success_url(self, user_token):
        success_url = user_token.get_provider()['success_url']
        if callable(success_url):
            return success_url(user_token)
        return success_url
