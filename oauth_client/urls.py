from django.urls import path

from oauth_client.views import OAuth2CallbackView

app_name = 'oauth_client'
urlpatterns = [
    path('oauth2_callback/<str:codename>/',
         OAuth2CallbackView.as_view(),
         name='oauth2_callback'),
    path('oauth2_callback/<str:codename>/<int:part_id>/',
         OAuth2CallbackView.as_view(),
         name='oauth2_callback_part'),
]
