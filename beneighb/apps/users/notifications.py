import logging

from firebase_admin import messaging
from firebase_admin.exceptions import InvalidArgumentError


logger = logging.getLogger(__name__)


def send_push_notification(recipient, body, title='', data=None):
    if not recipient.fcm_token:
        return

    msg_data = {
        'notification': messaging.Notification(
            title=title,
            body=body,
        ),
        'token': recipient.fcm_token,
    }

    if data:
        msg_data['data'] = data

    try:
        message = messaging.Message(**msg_data)
        response = messaging.send(message)
        logger.info('Successfully sent message:', response)
    except InvalidArgumentError:
        logger.exception('Invalid FCM token: %s', recipient.fcm_token)
