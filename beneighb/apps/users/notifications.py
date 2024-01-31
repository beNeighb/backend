import logging

from firebase_admin import messaging


logger = logging.getLogger(__name__)


def send_push_notification(recipient, body, title='', data=None):
    msg_data = {
        'notification': messaging.Notification(
            title=title,
            body=body,
        ),
        'token': recipient.fcm_token,
    }

    if data:
        msg_data['data'] = data

    message = messaging.Message(**msg_data)
    response = messaging.send(message)
    logger.info('Successfully sent message:', response)
