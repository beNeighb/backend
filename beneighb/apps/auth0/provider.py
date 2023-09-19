from allauth.socialaccount.providers.google.provider import GoogleProvider


class GoogleProviderWithId(GoogleProvider):
    id = 'google_with_id_instead_of_sub'
    name = "Google With ID"

    def extract_uid(self, data):
        return str(data['id'])


provider_classes = [GoogleProviderWithId]
