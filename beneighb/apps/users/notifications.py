import os
import firebase_admin
import logging

from firebase_admin import messaging


logger = logging.getLogger(__name__)


def send_push_notification(recipient, body, title=''):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=recipient.fcm_token,
    )
    response = messaging.send(message)
    logger.info('Successfully sent message:', response)
