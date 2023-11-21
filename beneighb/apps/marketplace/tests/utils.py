from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def update_client_with_correct_token(user, client):
    AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'
    refresh_token = RefreshToken.for_user(user)

    AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
        token=refresh_token.access_token
    )
    client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)


def get_client_with_valid_token(user):
    client = APIClient()
    update_client_with_correct_token(user, client)
    return client
