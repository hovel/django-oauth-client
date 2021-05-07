from django.urls import path

from oauth_client.views import OAuth2CallbackView

app_name = 'oauth_client'
urlpatterns = [
    path('oauth2_callback/<int:provider_id>/',
         OAuth2CallbackView.as_view(),
         name='oauth2_callback'),
    path('oauth2_callback/<str:provider_slug>/',
         OAuth2CallbackView.as_view(),
         name='oauth2_callback'),
    path('oauth2_callback/<str:provider_slug>/',
         OAuth2CallbackView.as_view(),
         name='oauth2_callback_part'),
]
