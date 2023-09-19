from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from apps.auth0.provider import GoogleProviderWithId


class GoogleOAuth2AdapterIdToken(GoogleOAuth2Adapter):
    provider_id = GoogleProviderWithId.id
